#!/usr/bin/env python3
"""controls.py RESULT.csv INF_DRY [REPORT.txt]: plant faults and check that the checks catch them.

RESULT.csv is a steady-state result (e.g. results/ss_bsm2python.csv), INF_DRY the IWA
file Inf_dry_2006.txt, REPORT.txt the pdftotext -layout text of the BSM1 report
(optional: without it the refextract control is skipped and said so).

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
        rr = list(csv.reader(open(ref)))
        k = next(i for i, r in enumerate(rr) if r[2] == 'EQ' and r[0] == 'rain' and r[5].startswith('app4'))
        rr[k][3] = rr[k][3][:-1] + str((int(rr[k][3][-1]) + 1) % 10)
        f4 = os.path.join(tmp, 'ref_bad.csv'); write(f4, rr[0], rr[1:])
        control('refextract: reference.csv rebuilt from the report, then rain EQ last digit changed',
                run('refextract.py', report, ref), run('refextract.py', report, f4), 0, (1,), 'EQ')
    else:
        print('skipped refextract: no report text given')

    if all(out):
        print(f'IDENTICAL: {len(out)} of {len(out)} controls caught their planted fault'); sys.exit(0)
    print(f'VOID: {out.count(False)} of {len(out)} controls missed'); sys.exit(2)


if __name__ == '__main__':
    main()
