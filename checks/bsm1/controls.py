#!/usr/bin/env python3
"""controls.py RESULT.csv INF_DRY [REPORT.txt]: plant faults and check that the checks catch them.

RESULT.csv is a steady-state result (e.g. results/ss_bsm2python.csv), INF_DRY the IWA
file Inf_dry_2006.txt, REPORT.txt the pdftotext -layout text of the BSM1 report
(optional: without it the refextract controls are skipped and said so).

Each control runs a check twice, clean and with one planted fault, and passes only
if the clean run gives the expected verdict and the planted run is caught (DIFFERS
or VOID, naming the planted row where the check names rows). The last line is
IDENTICAL (exit 0) when every control passes, VOID (exit 2) otherwise.
"""
import csv, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PY = [sys.executable, '-I']


def run(*args):
    p = subprocess.run(PY + [os.path.join(HERE, args[0])] + list(args[1:]), capture_output=True, text=True)
    return p.returncode, p.stdout


def write(path, header, rows):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(header); w.writerows(rows)


def main():
    if len(sys.argv) not in (3, 4):
        print(__doc__); sys.exit(2)
    result, infdry = sys.argv[1], sys.argv[2]
    report = sys.argv[3] if len(sys.argv) == 4 else None
    ref = os.path.join(HERE, 'reference.csv')
    tmp = tempfile.mkdtemp(prefix='bsm1ctl')
    out = []

    def control(name, clean, planted, expect_clean, catch, needle=None):
        ok = clean[0] == expect_clean and planted[0] in catch and (needle is None or needle in planted[1])
        out.append(ok)
        print(f'{"caught" if ok else "MISSED"}  {name}: clean exit {clean[0]}, planted exit {planted[0]}'
              + (f', names "{needle}"' if needle and needle in planted[1] else ''))

    # 1. bsm1cmp ref: the report's own printed steady state as a result
    rows = [r for r in csv.DictReader(open(ref)) if r['case'] == 'ss' and r['source'].startswith('app4')
            and r['block'] != 'derived']
    own = [['ss', r['block'], r['var'], r['printed']] for r in rows]
    f0 = os.path.join(tmp, 'own.csv'); write(f0, ['case', 'block', 'var', 'value'], own)
    bad = [list(r) for r in own]
    k = next(i for i, r in enumerate(bad) if r[1] == 'reactor3' and r[2] == 'SNO')
    bad[k][3] = repr(float(bad[k][3]) + 0.0001)                  # one printed unit
    f1 = os.path.join(tmp, 'own_bad.csv'); write(f1, ['case', 'block', 'var', 'value'], bad)
    control('ref: report vs itself, then reactor3 SNO + 1 printed unit',
            run('bsm1cmp.py', 'ref', ref, f0, '--quiet'), run('bsm1cmp.py', 'ref', ref, f1, '--quiet'),
            0, (1,), 'reactor3   SNO')
    f2 = os.path.join(tmp, 'own_short.csv'); write(f2, ['case', 'block', 'var', 'value'], own[:-1])
    control('ref: one row removed', run('bsm1cmp.py', 'ref', ref, f0, '--quiet'),
            run('bsm1cmp.py', 'ref', ref, f2, '--quiet'), 0, (2,), 'MISSING')

    # 2. bsm1cmp pair: a result vs itself, then one value changed in its 10th digit
    res = list(csv.reader(open(result)))
    head, body = res[0], res[1:]
    bad = [list(r) for r in body]
    k = next(i for i, r in enumerate(bad) if r[0] == 'ss' and r[1] == 'effluent' and r[2] == 'SNH')
    bad[k][3] = repr(float(bad[k][3]) * (1 + 1e-10))
    f3 = os.path.join(tmp, 'res_bad.csv'); write(f3, head, bad)
    control('pair: result vs itself, then effluent SNH * (1 + 1e-10)',
            run('bsm1cmp.py', 'pair', result, result), run('bsm1cmp.py', 'pair', result, f3), 0, (1,),
            'effluent   SNH')
    control('pair at rtol 1e-9 lets that planted change through, at rtol 1e-11 does not',
            run('bsm1cmp.py', 'pair', result, f3, '--rtol', '1e-9'),
            run('bsm1cmp.py', 'pair', result, f3, '--rtol', '1e-11'), 0, (1,))

    # 3. bsm1kpi: IQ of the dry weather file must be the report's 52081.3952; then one sample changed
    st = ['SI', 'SS', 'XI', 'XS', 'XBH', 'XBA', 'XP', 'SO', 'SNO', 'SNH', 'SND', 'XND', 'SALK']
    dry = [[float(x) for x in l.split()] for i, l in enumerate(open(infdry)) if i > 0 and l.strip()]
    head = ['t', 'Qin'] + [v + '_in' for v in st] + ['Qe'] + [v + '_e' for v in st] + ['Qw'] + \
        [v + '_u' for v in st] + [f'TSS_r{j}' for j in range(1, 6)] + [f'TSS_s{j}' for j in range(1, 11)]

    def series(path, plant):
        rows = []
        for k, r in enumerate(dry):
            ins = r[1:14]
            if plant and k == 960:                                 # day 10, inside the window
                ins = ins[:9] + [ins[9] + 1.0] + ins[10:]          # SNH + 1 g/m3
            rows.append([k / 96, r[14], *ins, 1.0, *([1.0] * 13), 385.0, *([1.0] * 13), *([1.0] * 15)])
        write(path, head, rows)
    s0, s1 = os.path.join(tmp, 'inf.csv'), os.path.join(tmp, 'inf_bad.csv')
    series(s0, False); series(s1, True)
    k0, k1 = os.path.join(tmp, 'kpi.csv'), os.path.join(tmp, 'kpi_bad.csv')
    run('bsm1kpi.py', s0, 'dry', '7', k0); run('bsm1kpi.py', s1, 'dry', '7', k1)

    def iq_only(path, dst):
        rows = [r for r in csv.reader(open(path))]
        write(dst, rows[0], [r for r in rows[1:] if r[2] == 'IQ'])
        return dst
    rq = os.path.join(tmp, 'ref_iq.csv')
    write(rq, ['case', 'block', 'var', 'printed', 'unit', 'source'],
          [[r['case'], r['block'], r['var'], r['printed'], r['unit'], r['source']]
           for r in csv.DictReader(open(ref)) if r['case'] == 'dry' and r['var'] == 'IQ'
           and r['source'].startswith('app4')])
    control('kpi: IQ of Inf_dry_2006.txt days 7-14 is the report\'s 52081.3952; then one SNH sample + 1',
            run('bsm1cmp.py', 'ref', rq, iq_only(k0, k0 + '.iq'), '--case', 'dry', '--quiet'),
            run('bsm1cmp.py', 'ref', rq, iq_only(k1, k1 + '.iq'), '--case', 'dry', '--quiet'), 0, (1,), 'IQ')

    # 4. refextract: rebuilding reference.csv from the report, then with one printed value changed
    if report:
        for case, var, name in (('rain', 'EQ', 'rain EQ'), ('cl_dry', 'SO5_ISE', 'closed-loop dry SO5_ISE')):
            rr = list(csv.reader(open(ref)))
            k = next(i for i, r in enumerate(rr) if r[2] == var and r[0] == case and r[5].startswith('app'))
            rr[k][3] = rr[k][3][:-1] + str((int(rr[k][3][-1]) + 1) % 10)
            f4 = os.path.join(tmp, f'ref_bad_{case}.csv'); write(f4, rr[0], rr[1:])
            control(f'refextract: reference.csv rebuilt from the report, then {name} last digit changed',
                    run('refextract.py', report, ref), run('refextract.py', report, f4), 0, (1,), var)
    else:
        print('skipped refextract: no report text given')

    # 5. bsm1cmp ref, closed loop: Appendix 5's own dry-weather rows as a result
    rows = [r for r in csv.DictReader(open(ref)) if r['case'] == 'cl_dry']
    own = [['cl_dry', r['block'], r['var'], r['printed']] for r in rows]
    f5 = os.path.join(tmp, 'cl_own.csv'); write(f5, ['case', 'block', 'var', 'value'], own)
    bad = [list(r) for r in own]
    k = next(i for i, r in enumerate(bad) if r[1] == 'ctrl' and r[2] == 'SO5_IAE')
    bad[k][3] = repr(float(bad[k][3]) + 0.00001)                 # one printed unit
    f6 = os.path.join(tmp, 'cl_own_bad.csv'); write(f6, ['case', 'block', 'var', 'value'], bad)
    control('ref, closed loop: Appendix 5 dry vs itself, then SO5_IAE + 1 printed unit',
            run('bsm1cmp.py', 'ref', ref, f5, '--case', 'cl_dry', '--source', 'app5', '--quiet'),
            run('bsm1cmp.py', 'ref', ref, f6, '--case', 'cl_dry', '--source', 'app5', '--quiet'), 0, (1,),
            'ctrl       SO5_IAE')

    # 6. bsm1clkpi: controller indices of a series whose answers are worked out by hand. In the window
    # (samples 672..1343, an even start) SO5 = 2 -/+ 0.1 alternately, so e = -/+0.1: IAE 0.1*7, ISE 0.01*7,
    # std 0.1 with section 5.2's variance (n-1 would give 0.1000745). SNO2 = 1 -/+ 0.2 likewise. KLa5 and
    # Qa are ramps (du = 0.25 and 4 exactly, so their std of du is 0); KLa3 = KLa4 = 240 makes
    # AE = 8/1800 * 1333 * (480 + mean KLa5) = 3933.0905556. Then one SO5 sample moved by 0.5.
    def clseries(path, plant):
        rows = []
        for k, r in enumerate(dry):
            sg = 1 if k % 2 else -1
            so5, sno2 = 2 + 0.1 * sg, 1 + 0.2 * sg
            if plant and k == 960:
                so5 += 0.5
            rows.append([k / 96, r[14], *r[1:14], 1.0, *([1.0] * 13), 385.0, *([1.0] * 13), *([1.0] * 15),
                         20000 + 4 * (k - 672), 240.0, 240.0, 100 + 0.25 * (k - 672), so5, so5, sno2, sno2])
        write(path, head + ['Qa', 'KLa3', 'KLa4', 'KLa5', 'SO5_true', 'SO5_meas', 'SNO2_true', 'SNO2_meas'], rows)
    c0, c1 = os.path.join(tmp, 'cl.csv'), os.path.join(tmp, 'cl_bad.csv')
    clseries(c0, False); clseries(c1, True)
    q0, q1 = os.path.join(tmp, 'clkpi.csv'), os.path.join(tmp, 'clkpi_bad.csv')
    run('bsm1clkpi.py', c0, 'cl_ctl', '7', q0); run('bsm1clkpi.py', c1, 'cl_ctl', '7', q1)
    known = [('ctrl', 'SO5_IAE', '0.7000000000'), ('ctrl', 'SO5_ISE', '0.07000000000'),
             ('ctrl', 'SO5_err_max', '0.1000000000'), ('ctrl', 'SO5_err_std', '0.1000000000'),
             ('ctrl', 'SO5_err_var', '0.01000000000'), ('ctrl', 'SO5_err_mean', '0.0000000000'),
             ('ctrl', 'SNO2_IAE', '1.400000000'), ('ctrl', 'SNO2_ISE', '0.2800000000'),
             ('ctrl', 'SNO2_err_std', '0.2000000000'), ('ctrl', 'KLa5_mean', '183.8750000'),
             ('ctrl', 'KLa5_range', '167.7500000'), ('ctrl', 'KLa5_maxdelta', '0.2500000000'),
             ('ctrl', 'KLa5_dstd', '0.0000000000'), ('ctrl', 'Qintr_mean', '21342.00000'),
             ('ctrl', 'Qintr_maxdelta', '4.000000000'), ('ctrl', 'Qintr_dstd', '0.0000000000'),
             ('perf', 'AE', '3933.0905556'), ('perf', 'ME', '240.0000000')]
    rk = os.path.join(tmp, 'ref_cl_known.csv')
    write(rk, ['case', 'block', 'var', 'printed', 'unit', 'source'], [['cl_ctl', b, v, p, '', 'ctl'] for b, v, p in known])
    control('clkpi: controller indices worked out by hand; then one SO5 sample + 0.5',
            run('bsm1cmp.py', 'ref', rk, q0, '--case', 'cl_ctl', '--source', 'ctl', '--quiet'),
            run('bsm1cmp.py', 'ref', rk, q1, '--case', 'cl_ctl', '--source', 'ctl', '--quiet'), 0, (1,), 'SO5_IAE')

    if all(out):
        print(f'IDENTICAL: {len(out)} of {len(out)} controls caught their planted fault'); sys.exit(0)
    print(f'VOID: {out.count(False)} of {len(out)} controls missed'); sys.exit(2)


if __name__ == '__main__':
    main()
