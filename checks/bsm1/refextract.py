#!/usr/bin/env python3
"""refextract.py TEXT [CSV]: rebuild reference.csv from the BSM1 technical report.

TEXT is `pdftotext -layout LTH-IEA-7229.pdf` (Alex et al., "Benchmark Simulation
Model no. 1 (BSM1)", Lund University, 2008, 62 pages). The report is not copied
here; its numbers are. Without CSV the rows are printed; with CSV they are checked
against that file and the verdict is IDENTICAL (exit 0), DIFFERS (1) or VOID (2).

Rows: case, block, var, printed, unit, source. `printed` is the number exactly as
the report prints it, so its last digit is the precision the verdicts use.
- case ss, source app4-p39..p41: Appendix 4, steady state, open loop (Matlab/Simulink,
  27 March 2008), five or six digits.
- case ss, source t6-p15, t7-p15, t8-p16: Tables 6 to 8, the same steady state to
  three digits. Table 7 numbers settler layers from the bottom; here TSS1 is the top
  layer in every source, as in Appendix 4.
- case dry, rain, storm, source app4-p43..p48: Appendix 4, open loop, days 7 to 14 of
  each weather file after 150 days at constant influent and 14 days of dry weather.
- case dry, source app2-p33, app2-p34: Appendix 2, the same dry-weather summary from
  the FORTRAN implementation, to fewer digits: a second published answer.
- case cl_dry, cl_rain, cl_storm, source app5-p53..p61: Appendix 5, closed loop (Matlab/
  Simulink, 28 March 2008), days 7 to 14 of each weather file after 150 days at constant
  influent and 14 days of dry weather. Block perf as for the open loop, plus TSS
  violations where printed; block ctrl, the controller indices: SNO2_* and Qintr_* for the
  nitrate loop (tank 2, manipulated variable Qintr), SO5_* and KLa5_* for the oxygen loop
  (tank 5). Qintr_dstd and Qintr_dvar (likewise KLa5) are what Appendix 5 labels std(Qintr)
  and var(Qintr); section 5.2 defines them on the changes du (see README).
"""
import csv, re, sys

VARS13 = ['SI', 'SS', 'XI', 'XS', 'XBH', 'XBA', 'XP', 'SO', 'SNO', 'SNH', 'SND', 'XND', 'SALK']
UNIT = {'SI': 'g COD/m3', 'SS': 'g COD/m3', 'XI': 'g COD/m3', 'XS': 'g COD/m3', 'XBH': 'g COD/m3',
        'XBA': 'g COD/m3', 'XP': 'g COD/m3', 'SO': 'g O2/m3', 'SNO': 'g N/m3', 'SNH': 'g N/m3',
        'SND': 'g N/m3', 'XND': 'g N/m3', 'SALK': 'mol/m3', 'TSS': 'g SS/m3'}
NUM = r'(-?[0-9]+\.?[0-9]*(?:e[-+]?[0-9]+)?)'


def page_of(lines, i):
    """Appendix 4 prints bare page numbers at the foot of each page: the first one after line i."""
    for j in range(i, len(lines)):
        s = lines[j].strip()
        if re.fullmatch(r'[0-9]{2}', s):
            return int(s)
    return None


def steady(lines, rows):
    a = next(i for i, l in enumerate(lines) if 'STEADY STATE RESULTS FOR OPENLOOP' in l)
    b = next(i for i, l in enumerate(lines) if 'DYNAMIC RESULTS FOR OPENLOOP' in l)
    blocks = {'Input to AS': 'input_as', 'Reactor 1': 'reactor1', 'Reactor 2': 'reactor2',
              'Reactor 3': 'reactor3', 'Reactor 4': 'reactor4', 'Reactor 5': 'reactor5',
              'Settler underflow': 'underflow', 'Settler effluent': 'effluent'}
    cur = None
    for i in range(a, b):
        s = lines[i].strip()
        if s in blocks:
            cur = blocks[s]; continue
        if s.startswith('Settler internal'):
            cur = 'settler'; continue
        if s.startswith('Other variables') or s.startswith('Influent char') or s.startswith('Flow cond') \
                or s.startswith('Dimensions'):
            cur = s.split()[0].lower(); continue
        m = re.fullmatch(r'([A-Z]+[0-9]*) = ' + NUM + r' (.*)', s)
        if m and cur in blocks.values():
            v = m.group(1)
            if v in VARS13 or v == 'TSS':
                rows.append(('ss', cur, v, m.group(2), UNIT[v], f'app4-p{page_of(lines, i)}'))
        elif m and cur == 'settler':
            rows.append(('ss', 'settler', m.group(1), m.group(2), UNIT['TSS'], f'app4-p{page_of(lines, i)}'))
        elif cur == 'other':
            for pat, var, unit in ((r'Trad\. sludge age .* = ' + NUM, 'trad_sludge_age', 'd'),
                                   (r'Spec\. sludge age .* = ' + NUM, 'spec_sludge_age', 'd'),
                                   (r'Thickening factor .* = ' + NUM, 'thickening', '-'),
                                   (r'Thinning factor .* = ' + NUM, 'thinning', '-')):
                m = re.fullmatch(pat + r'(?: days)?', s)
                if m:
                    rows.append(('ss', 'derived', var, m.group(1), unit, f'app4-p{page_of(lines, i)}'))


def tables(lines, rows):
    """Tables 6 to 8 (pages 15 and 16), three digits."""
    t6 = next(i for i, l in enumerate(lines) if 'Table 6: Biological reactor steady-state' in l)
    sym = {'SI': 'SI', 'SS': 'SS', 'XI': 'XI', 'XS': 'XS', 'X B,H': 'XBH', 'XB,A': 'XBA', 'XP': 'XP',
           'SO': 'SO', 'SNO': 'SNO', 'SNH': 'SNH', 'SND': 'SND', 'XND': 'XND', 'SALK': 'SALK'}
    for i in range(t6 - 20, t6):
        s = lines[i]
        m = re.match(r'\s*(X B,H|XB,A|[A-Z]+),stab\s+\S+\s+(?:X B,H|XB,A|[A-Z]+),i\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', s)
        if m:
            v = sym[m.group(1)]
            for k in range(5):
                rows.append(('ss', f'reactor{k + 1}', v, m.group(k + 2), UNIT[v], 't6-p15'))
        m = re.match(r'\s*Xstab\s+Xi\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', s)
        if m:
            for k in range(5):
                rows.append(('ss', f'reactor{k + 1}', 'TSS', m.group(k + 1), UNIT['TSS'], 't6-p15'))
    t7 = next(i for i, l in enumerate(lines) if 'Table 7: Settler steady-state' in l)
    for i in range(t7 - 12, t7):
        m = re.match(r'\s*([0-9]+)\s+(\S+)\s+30\s', lines[i])
        if m:
            k = int(m.group(1))                     # 1 = bottom in Table 7
            rows.append(('ss', 'settler', f'TSS{11 - k}', m.group(2), UNIT['TSS'], 't7-p15'))
    t8 = next(i for i, l in enumerate(lines) if 'Table 8: Settler steady-state' in l)
    for i in range(t8 - 18, t8):
        m = re.match(r'\s*(X B,H|XB,A|[A-Z]+),u\s+(\S+)\s+(X B,H|XB,A|[A-Z]+),[eu]\s+(\S+)', lines[i])
        if m:
            v = sym[m.group(1)]
            rows.append(('ss', 'underflow', v, m.group(2), UNIT[v], 't8-p16'))
            rows.append(('ss', 'effluent', sym[m.group(3)], m.group(4), UNIT[v], 't8-p16'))
        m = re.match(r'\s*Xu\s+(\S+)\s+Xe\s+(\S+)', lines[i])
        if m:
            rows.append(('ss', 'underflow', 'TSS', m.group(1), UNIT['TSS'], 't8-p16'))
            rows.append(('ss', 'effluent', 'TSS', m.group(2), UNIT['TSS'], 't8-p16'))


DYN = [  # (regex on one line, var, unit)
    (r'Effluent average flow rate = ' + NUM, 'Qe', 'm3/d'),
    *[(rf'Effluent average {v} conc = ' + NUM, f'{v}_e', UNIT[v]) for v in VARS13 + ['TSS']],
    (r'Effluent average Kjeldahl N conc = ' + NUM, 'TKN_e', 'g N/m3'),
    (r'Effluent average total N conc = ' + NUM, 'TN_e', 'g N/m3'),
    (r'Effluent average total COD conc = ' + NUM, 'COD_e', 'g COD/m3'),
    (r'Effluent average BOD5 conc = ' + NUM, 'BOD5_e', 'g/m3'),
    *[(rf'Effluent average {v} load = ' + NUM, f'{v}_load', 'kg/d (kmol/d for SALK)') for v in VARS13 + ['TSS']],
    (r'Effluent average Kjeldahl N load = ' + NUM, 'TKN_load', 'kg N/d'),
    (r'Effluent average total N load = ' + NUM, 'TN_load', 'kg N/d'),
    (r'Effluent average total COD load = ' + NUM, 'COD_load', 'kg COD/d'),
    (r'Effluent average BOD5 load = ' + NUM, 'BOD5_load', 'kg/d'),
    (r'Influent Quality \(I\.Q\.\) index = ' + NUM, 'IQ', 'kg PU/d'),
    (r'Effluent Quality \(E\.Q\.\) index = ' + NUM, 'EQ', 'kg PU/d'),
    (r'Sludge production for disposal = ' + NUM, 'SP_disposal_total', 'kg SS'),
    (r'Average sludge production for disposal per day = ' + NUM, 'SP_disposal', 'kg SS/d'),
    (r'Sludge production released into effluent = ' + NUM, 'SP_effluent_total', 'kg SS'),
    (r'Average sludge production released into effluent per day = ' + NUM, 'SP_effluent', 'kg SS/d'),
    (r'Total sludge production = ' + NUM, 'SP_total_total', 'kg SS'),
    (r'Total average sludge production per day = ' + NUM, 'SP_total', 'kg SS/d'),
    (r'Average aeration energy per day = ' + NUM, 'AE', 'kWh/d'),
    (r'Average pumping energy per day \(for Qintr, Qr and Qw\) = ' + NUM, 'PE', 'kWh/d'),
    (r'Average mixing energy per day = ' + NUM, 'ME', 'kWh/d'),
    (r'Total Operational Cost Index \(OCI\) = ' + NUM, 'OCI', '-'),
    (r'95% percentile for effluent SNH \(Ammonia95\) = ' + NUM, 'SNH_e95', 'g N/m3'),
    (r'95% percentile for effluent TN \(TN95\) = ' + NUM, 'TN_e95', 'g N/m3'),
    (r'95% percentile for effluent TSS \(TSS95\) = ' + NUM, 'TSS_e95', 'g SS/m3'),
]


# Appendix 5's controller indices: (regex on one line, var suffix, unit as a format of the variable's unit)
CTRL = [
    (r'Average value of error \(mean\(e\)\) = ' + NUM, 'err_mean', '{}'),
    (r'Average value of absolute error \(mean\(\|e\|\)\) = ' + NUM, 'err_absmean', '{}'),
    (r'Integral of absolute error \(IAE\) = ' + NUM, 'IAE', '({})*d'),
    (r'Integral of square error \(ISE\) = ' + NUM, 'ISE', '({})^2*d'),
    (r'Maximum absolute deviation from (?:nitrate|oxygen) setpoint \(max\(e\)\) = ' + NUM, 'err_max', '{}'),
    (r'Standard deviation of error \(std\(e\)\) = ' + NUM, 'err_std', '{}'),
    (r'Variance of error \(var\(e\)\) = ' + NUM, 'err_var', '({})^2'),
]
MV = [
    (r'Maximum absolute variation of MV \(max-min\) = ' + NUM, 'range', '{}'),
    (r'Maximum absolute variation of MV in one sample \(max delta\) = ' + NUM, 'maxdelta', '{}'),
    (r'Average value of MV \(mean\((\w+)\)\) = ' + NUM, 'mean', '{}'),
    (r'Standard deviation of MV \(std\((\w+)\)\) = ' + NUM, 'dstd', '{}'),
    (r'Variance of MV \(var\((\w+)\)\) = ' + NUM, 'dvar', '({})^2'),
]
LOOPS = {'Nitrate controller for second anoxic reactor': ('SNO2', 'g N/m3', 'Qintr', 'm3/d'),
         'Oxygen controller for last aerobic reactor': ('SO5', 'g (-COD)/m3', 'KLa5', '1/d')}


def dynamic(lines, rows, closed=False):
    """Appendix 4 (open loop) or, with closed, Appendix 5's dynamic results and controller indices."""
    if not closed:
        a = next(i for i, l in enumerate(lines) if 'DYNAMIC RESULTS FOR OPENLOOP' in l)
        b = next(i for i, l in enumerate(lines) if i > a and 'CLOSEDLOOP' in l.replace(' ', '').upper()
                 and 'RESULTS' in l)
    else:
        a = next(i for i, l in enumerate(lines) if 'DYNAMIC RESULTS FOR CLOSEDLOOP' in l)
        b = len(lines)
    pre, app = ('cl_', 'app5') if closed else ('', 'app4')
    case = None
    lim = None
    loop = None
    for i in range(a, b):
        s = lines[i].strip()
        for w, c in (('DRYWEATHER FILE', 'dry'), ('RAINWEATHER FILE', 'rain'), ('STORMWEATHER FILE', 'storm')):
            if w in s and s.startswith('*'):
                case = pre + c
                loop = None
        if case is None:
            continue
        src = f'{app}-p{page_of(lines, i)}'
        for pat, var, unit in DYN:
            m = re.match(pat, s)
            if m:
                rows.append((case, 'perf', var, m.group(1), unit, src))
        m = re.match(r'The maximum effluent (total nitrogen|ammonia nitrogen|total suspended solids) level', s)
        if m:
            lim = {'total nitrogen': 'TN', 'ammonia nitrogen': 'SNH', 'total suspended solids': 'TSS'}[m.group(1)]
        m = re.match(r'during ' + NUM + r' days, i\.e\. ' + NUM + r'% of the operating time', s)
        if m and lim:
            rows.append((case, 'perf', f'{lim}_viol_days', m.group(1), 'd', src))
            rows.append((case, 'perf', f'{lim}_viol_pct', m.group(2), '%', src))
        m = re.match(r'The limit was violated at ([0-9]+) different occasions', s)
        if m and lim:
            rows.append((case, 'perf', f'{lim}_viol_count', m.group(1), '-', src))
            lim = None
        if not closed:
            continue
        if s in LOOPS:
            loop = LOOPS[s]
        if loop is None:
            continue
        cv, ucv, mv, umv = loop
        for pat, suf, unit in CTRL:
            m = re.match(pat, s)
            if m:
                rows.append((case, 'ctrl', f'{cv}_{suf}', m.group(1), unit.format(ucv), src))
        for pat, suf, unit in MV:
            m = re.match(pat, s)
            if m and (m.lastindex == 1 or m.group(1) == mv):
                rows.append((case, 'ctrl', f'{mv}_{suf}', m.group(m.lastindex), unit.format(umv), src))


def app2(lines, rows):
    """Appendix 2 (pages 33-34): the FORTRAN implementation's open-loop dry-weather summary."""
    a = next(i for i, l in enumerate(lines) if 'Appendix 2: Open-loop performance (summary)' in l and i > 200)
    b = next(i for i, l in enumerate(lines) if 'Appendix 3: Closed-loop performance (summary)' in l and i > a)
    pats = [(r'Effluent average flow rate\s+\S+\s+' + NUM + r'$', 'Qe', 'm3/d'),
            *[(rf'Effluent average {v} concentration.*\s{NUM}$', f'{v}_e', UNIT[v]) for v in VARS13 + ['TSS']],
            (r'Effluent average Kjeldahl N concentration\s.*\s' + NUM + '$', 'TKN_e', 'g N/m3'),
            (r'Effluent average BOD5 concentration.*\s' + NUM + '$', 'BOD5_e', 'g/m3'),
            (r'Influent quality \(IQ\) index\s.*\s' + NUM + '$', 'IQ', 'kg PU/d'),
            (r'Effluent quality \(EQ\) index\s.*\s' + NUM + '$', 'EQ', 'kg PU/d'),
            (r'Average sludge production for disposal per day\s.*\s' + NUM + '$', 'SP_disposal', 'kg SS/d'),
            (r'Average sludge production released into effluent per day\s.*\s' + NUM + '$', 'SP_effluent', 'kg SS/d'),
            (r'Total average sludge production per day\s.*\s' + NUM + '$', 'SP_total', 'kg SS/d'),
            (r'Average aeration energy\s.*\s' + NUM + '$', 'AE', 'kWh/d'),
            (r'Average pumping energy\s.*\s' + NUM + '$', 'PE', 'kWh/d'),
            (r'Average mixing energy\s.*\s' + NUM + '$', 'ME', 'kWh/d'),
            (r'Total Operational Cost Index \(OCI\)\s.*\s' + NUM + '$', 'OCI', '-'),
            (r'95% percentile of effluent SNH .*\s' + NUM + '$', 'SNH_e95', 'g N/m3'),
            (r'95% percentile of effluent TSS .*\s' + NUM + '$', 'TSS_e95', 'g SS/m3')]
    lim = None
    for i in range(a, b):
        s = lines[i].strip()
        src = 'app2-p33' if i < next(j for j in range(a, b) if 'Page 33' in lines[j]) else 'app2-p34'
        for pat, var, unit in pats:
            m = re.match(pat, s)
            if m and not (var.endswith('_e') and 'load' in s):
                rows.append(('dry', 'perf', var, m.group(1), unit, src))
        nxt = lines[i + 1].strip() if i + 1 < b else ''
        for lab, var, unit in (('total N concentration', 'TN_e', 'g N/m3'),
                               ('total COD concentration', 'COD_e', 'g COD/m3')):
            if s == f'Effluent average {lab}':
                m = re.match(r'\(limit.*\)\s.*\s' + NUM + '$', nxt)
                if m:
                    rows.append(('dry', 'perf', var, m.group(1), unit, src))
        if s.startswith('95% percentile of effluent total N'):
            m = re.match(r'BSM1\s+' + NUM + '$', nxt)
            if m:
                rows.append(('dry', 'perf', 'TN_e95', m.group(1), 'g N/m3', src))
        m = re.match(r'Maximum effluent total (N|ammonia) limit', s)
        if m:
            lim = 'TN' if m.group(1) == 'N' else 'SNH'
        elif s.startswith('Maximum effluent'):
            lim = None
        if lim:
            for pat, suf, unit in ((r'during:\s+d\s+' + NUM + '$', 'viol_days', 'd'),
                                   (r'% of total evaluation time:\s+%\s+' + NUM + '$', 'viol_pct', '%'),
                                   (r'number of violations:\s+' + NUM + '$', 'viol_count', '-')):
                m = re.match(pat, s)
                if m:
                    rows.append(('dry', 'perf', f'{lim}_{suf}', m.group(1), unit, src))


def main():
    if len(sys.argv) not in (2, 3):
        print(__doc__); sys.exit(2)
    lines = open(sys.argv[1], encoding='utf-8', errors='replace').read().split('\n')
    rows = []
    try:
        tables(lines, rows); steady(lines, rows); dynamic(lines, rows); app2(lines, rows)
        dynamic(lines, rows, closed=True)
    except StopIteration:
        print('VOID: a section of the report was not found'); sys.exit(2)
    head = ('case', 'block', 'var', 'printed', 'unit', 'source')
    if len(sys.argv) == 2:
        w = csv.writer(sys.stdout, lineterminator='\n'); w.writerow(head); w.writerows(rows); return
    with open(sys.argv[2], newline='') as f:
        old = [tuple(r) for r in csv.reader(f)][1:]
    if not rows:
        print('VOID: nothing extracted'); sys.exit(2)
    if old == rows:
        print(f'IDENTICAL: {len(rows)} rows of {sys.argv[2]} rebuilt from the report text'); sys.exit(0)
    a, b = set(old), set(rows)
    for r in sorted(a - b)[:10]: print('  only in csv:   ', r)
    for r in sorted(b - a)[:10]: print('  only in report:', r)
    print(f'DIFFERS: {len(a - b)} rows only in the csv, {len(b - a)} only in the report text'); sys.exit(1)


if __name__ == '__main__':
    main()
