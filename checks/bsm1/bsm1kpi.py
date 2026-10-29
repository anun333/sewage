#!/usr/bin/env python3
"""bsm1kpi.py SERIES.csv CASE T0 [OUT.csv]: BSM1 open-loop performance indices from a time series.

SERIES.csv holds 15-minute samples written by the run_*.py drivers, with the
columns t, Qin, <state>_in, Qe, <state>_e, Qw, <state>_u (13 ASM1 states each:
SI SS XI XS XBH XBA XP SO SNO SNH SND XND SALK), TSS_r1..TSS_r5 (reactors) and
TSS_s1..TSS_s10 (settler layers). The evaluation window is [T0, T0+7) days.

Every index follows the BSM1 report (section 6 and Appendix 4): averages are
flow-weighted, integrals are rectangles of 15 minutes taking the value at the
start of each interval, the 95th percentiles use Matlab's prctile convention
(midpoint plotting positions, linear interpolation), a violation is a sample
above the limit, and the number of violations counts upward crossings (a
window that starts above the limit counts one). AE, PE and ME follow from the
fixed open-loop settings (KLa 240, 240, 84 1/d; Qa 55338, Qr 18446, Qw 385),
except that PE uses the series' Qa column when it has one.

Writes rows case, block (perf), var, value, with the variable names of
reference.csv, to OUT.csv or stdout. Prints VOID and exits 2 when the window
is not covered by whole 15-minute samples.
"""
import csv, math, sys

ST = ['SI', 'SS', 'XI', 'XS', 'XBH', 'XBA', 'XP', 'SO', 'SNO', 'SNH', 'SND', 'XND', 'SALK']
IXB, IXP, FP = 0.08, 0.06, 0.08
V = [1000.0, 1000.0, 1333.0, 1333.0, 1333.0]
A, Z = 1500.0, 0.4
KLA = [0.0, 0.0, 240.0, 240.0, 84.0]
QA, QR, QW = 55338.0, 18446.0, 385.0
DT = 1.0 / 96


def tss(r, s):
    return 0.75 * (r['XS' + s] + r['XI' + s] + r['XBH' + s] + r['XBA' + s] + r['XP' + s])


def tkn(r, s):
    return (r['SNH' + s] + r['SND' + s] + r['XND' + s] + IXB * (r['XBH' + s] + r['XBA' + s])
            + IXP * (r['XP' + s] + r['XI' + s]))


def cod(r, s):
    return r['SS' + s] + r['SI' + s] + r['XS' + s] + r['XI' + s] + r['XBH' + s] + r['XBA' + s] + r['XP' + s]


def bod5(r, s, f):
    return f * (r['SS' + s] + r['XS' + s] + (1 - FP) * (r['XBH' + s] + r['XBA' + s]))


def prctile(x, p):
    """Matlab's prctile: sorted values sit at 100*(i-0.5)/n, linear in between, clamped."""
    x = sorted(x); n = len(x)
    pos = p / 100 * n + 0.5          # 1-based position
    if pos <= 1: return x[0]
    if pos >= n: return x[-1]
    i = int(math.floor(pos)); f = pos - i
    return x[i - 1] + f * (x[i] - x[i - 1])


def violations(x, lim):
    above = [v > lim for v in x]
    count = sum(1 for i, a in enumerate(above) if a and (i == 0 or not above[i - 1]))
    days = sum(above) * DT
    return days, days / (len(x) * DT) * 100, count


def inventory(r):
    """kg of solids in reactors and settler at one sample."""
    return (sum(v * r[f'TSS_r{k}'] for k, v in enumerate(V, 1)) + Z * A * sum(r[f'TSS_s{j}'] for j in range(1, 11))) / 1000


def kpi(rows, t0):
    k0 = [i for i, r in enumerate(rows) if abs(r['t'] - t0) < 1e-6]
    k1 = [i for i, r in enumerate(rows) if abs(r['t'] - (t0 + 7)) < 1e-6]
    if not k0 or not k1 or k1[0] - k0[0] != 672:
        return None
    w = rows[k0[0]:k1[0]]                        # 672 samples, t0 .. t0+7-dt
    T = 7.0
    qe = [r['Qe'] for r in w]
    sq = sum(qe) * DT
    out = {'Qe': sq / T}
    der = {'TSS': lambda r: tss(r, '_e'), 'TKN': lambda r: tkn(r, '_e'), 'COD': lambda r: cod(r, '_e'),
           'BOD5': lambda r: bod5(r, '_e', 0.25)}
    for v in ST:
        out[f'{v}_e'] = sum(r['Qe'] * r[v + '_e'] for r in w) * DT / sq
    for v, f in der.items():
        out[f'{v}_e'] = sum(r['Qe'] * f(r) for r in w) * DT / sq
    out['TN_e'] = out['TKN_e'] + out['SNO_e']
    for v in ST + list(der):
        out[f'{v}_load'] = out[f'{v}_e'] * out['Qe'] / 1000
    out['TN_load'] = out['TKN_load'] + out['SNO_load']
    eq = lambda r, s, fb, q: (2 * tss(r, s) + cod(r, s) + 30 * tkn(r, s) + 10 * r['SNO' + s] + 2 * bod5(r, s, fb)) * r[q]
    out['EQ'] = sum(eq(r, '_e', 0.25, 'Qe') for r in w) * DT / (T * 1000)
    out['IQ'] = sum(eq(r, '_in', 0.65, 'Qin') for r in w) * DT / (T * 1000)
    was = sum(tss(r, '_u') * r['Qw'] for r in w) * DT / 1000
    sp = inventory(rows[k1[0]]) - inventory(rows[k0[0]]) + was
    out['SP_disposal_total'] = sp; out['SP_disposal'] = sp / T
    spe = sum(tss(r, '_e') * r['Qe'] for r in w) * DT / 1000
    out['SP_effluent_total'] = spe; out['SP_effluent'] = spe / T
    out['SP_total_total'] = sp + spe; out['SP_total'] = (sp + spe) / T
    out['AE'] = 8.0 / (1.8 * 1000) * sum(v * k for v, k in zip(V, KLA))
    qa = sum(r['Qa'] for r in w) / len(w) if 'Qa' in w[0] else QA      # a driver may log a varying Qa
    out['PE'] = 0.004 * qa + 0.008 * QR + 0.05 * QW
    out['ME'] = 24 * 0.005 * sum(v for v, k in zip(V, KLA) if k < 20)
    out['OCI'] = out['AE'] + out['PE'] + 5 * out['SP_disposal'] + out['ME']
    snh = [r['SNH_e'] for r in w]
    tn = [tkn(r, '_e') + r['SNO_e'] for r in w]
    ts = [tss(r, '_e') for r in w]
    out['SNH_e95'], out['TN_e95'], out['TSS_e95'] = prctile(snh, 95), prctile(tn, 95), prctile(ts, 95)
    for name, x, lim in (('TN', tn, 18.0), ('SNH', snh, 4.0)):
        out[f'{name}_viol_days'], out[f'{name}_viol_pct'], out[f'{name}_viol_count'] = violations(x, lim)
    return out


def main():
    if len(sys.argv) not in (4, 5):
        print(__doc__); sys.exit(2)
    with open(sys.argv[1], newline='') as f:
        rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]
    case, t0 = sys.argv[2], float(sys.argv[3])
    out = kpi(rows, t0)
    if out is None or any(not math.isfinite(v) for v in out.values()):
        print(f'VOID: {sys.argv[1]} does not cover [{t0}, {t0 + 7}) in 15-minute samples'); sys.exit(2)
    f = open(sys.argv[4], 'w', newline='') if len(sys.argv) == 5 else sys.stdout
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['case', 'block', 'var', 'value'])
    for k, v in out.items():
        w.writerow([case, 'perf', k, repr(v)])


if __name__ == '__main__':
    main()
