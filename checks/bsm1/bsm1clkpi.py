#!/usr/bin/env python3
"""bsm1clkpi.py SERIES.csv CASE T0 [OUT.csv]: BSM1 closed-loop indices from a time series.

SERIES.csv is a run_bsm2python_cl.py series: the columns bsm1kpi.py reads, plus Qa,
KLa3, KLa4, KLa5 (the values applied from each sample on), SO5_true, SO5_meas,
SNO2_true and SNO2_meas (the reactor's concentration and the sensor signal the
controller saw at that sample). The window is [T0, T0+7) days, 672 samples.

- block perf: bsm1kpi.py's indices, except that AE and ME follow the logged KLa
  values (PE already follows the logged Qa), and OCI with them. Also TSS_viol_*
  (limit 30 g SS/m3), which Appendix 5 prints where the limit was violated.
- block ctrl: the controller indices of the report's section 5.2 and Appendix 5,
  for the nitrate loop (SNO2 in tank 2, setpoint 1 g N/m3, manipulated variable
  Qintr = Qa) and the oxygen loop (SO5 in tank 5, setpoint 2 g/m3, KLa5):
    <cv>_err_mean, _err_absmean, _IAE, _ISE, _err_max (largest |e|), _err_std and
    _err_var, with e = setpoint - the true concentration. Section 5.2 writes the
    measured one; Appendix 5's figures match the true one (see README). The same
    from the sensor signal are <cv>_meas_*. Integrals are 15-minute rectangles,
    and mean and variance are those integrals over T, as section 5.2 defines them:
    var = mean(e^2) - mean(e)^2, with no n-1 (the report's printed variances are
    ISE/7 - mean(e)^2).
    <mv>_range (max - min), _maxdelta (largest |du| between samples), _mean, and
    _dstd and _dvar, the std and variance of du = u(t+dt) - u(t) over the window's
    671 changes: section 5.2's variance of the manipulated variable's variations,
    which Appendix 5 labels std(Qintr) and var(Qintr). <mv>_std is the std of u.

Writes rows case, block, var, value to OUT.csv or stdout. Prints VOID and exits 2
when the window is not covered by whole 15-minute samples, or when any value in the
series is not a finite number (naming where each column first is not).
"""
import csv, math, os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bsm1kpi  # noqa: E402

V, DT = bsm1kpi.V, bsm1kpi.DT
LOOPS = (('SNO2', 1.0, 'Qintr', 'Qa'), ('SO5', 2.0, 'KLa5', 'KLa5'))   # cv, setpoint, mv, its column


def pstats(x):
    """Mean and variance over T: the 15-minute rectangle integrals divided by T."""
    m = sum(x) / len(x)
    return m, sum((v - m) ** 2 for v in x) / len(x)


def err_idx(e, p):
    m, var = pstats(e)
    return {f'{p}_err_mean': m, f'{p}_err_absmean': sum(abs(x) for x in e) / len(e),
            f'{p}_IAE': sum(abs(x) for x in e) * DT, f'{p}_ISE': sum(x * x for x in e) * DT,
            f'{p}_err_max': max(abs(x) for x in e), f'{p}_err_std': math.sqrt(var), f'{p}_err_var': var}


def mv_idx(u, p):
    du = [b - a for a, b in zip(u, u[1:])]
    dvar = pstats(du)[1]
    return {f'{p}_range': max(u) - min(u), f'{p}_maxdelta': max(abs(x) for x in du), f'{p}_mean': sum(u) / len(u),
            f'{p}_dstd': math.sqrt(dvar), f'{p}_dvar': dvar, f'{p}_std': math.sqrt(pstats(u)[1])}


def clkpi(rows, t0):
    perf = bsm1kpi.kpi(rows, t0)
    if perf is None:
        return None, None
    i0 = next(i for i, r in enumerate(rows) if abs(r['t'] - t0) < 1e-6)
    w = rows[i0:i0 + 672]
    kla = [[0.0, 0.0, r['KLa3'], r['KLa4'], r['KLa5']] for r in w]
    perf['AE'] = 8.0 / (1.8 * 1000) * sum(sum(v * k for v, k in zip(V, ks)) for ks in kla) / len(w)
    perf['ME'] = 24 * 0.005 * sum(sum(v for v, k in zip(V, ks) if k < 20) for ks in kla) / len(w)
    perf['OCI'] = perf['AE'] + perf['PE'] + 5 * perf['SP_disposal'] + perf['ME']
    tss = [bsm1kpi.tss(r, '_e') for r in w]
    perf['TSS_viol_days'], perf['TSS_viol_pct'], perf['TSS_viol_count'] = bsm1kpi.violations(tss, 30.0)
    ctrl = {}
    for cv, sp, mv, col in LOOPS:
        ctrl.update(err_idx([sp - r[cv + '_true'] for r in w], cv))
        ctrl.update(mv_idx([r[col] for r in w], mv))
    for cv, sp, mv, col in LOOPS:
        ctrl.update(err_idx([sp - r[cv + '_meas'] for r in w], cv + '_meas'))
    return perf, ctrl


def main():
    if len(sys.argv) not in (4, 5):
        print(__doc__); sys.exit(2)
    with open(sys.argv[1], newline='') as f:
        rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]
    case, t0 = sys.argv[2], float(sys.argv[3])
    first = {}                                   # column -> first t where it is not a finite number
    for r in rows:
        for k, v in r.items():
            if k not in first and not math.isfinite(v):
                first[k] = r['t']
    if first:
        cols = sorted(first.items(), key=lambda kv: kv[1])
        print(f'VOID: {sys.argv[1]}: not a finite number from ' + ', '.join(f'{k} t = {t:.6g}' for k, t in cols[:8])
              + (f' and {len(cols) - 8} more columns' if len(cols) > 8 else '')); sys.exit(2)
    perf, ctrl = clkpi(rows, t0)
    if perf is None:
        print(f'VOID: {sys.argv[1]} does not cover [{t0}, {t0 + 7}) in 15-minute samples'); sys.exit(2)
    f = open(sys.argv[4], 'w', newline='') if len(sys.argv) == 5 else sys.stdout
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['case', 'block', 'var', 'value'])
    for blk, d in (('perf', perf), ('ctrl', ctrl)):
        for k, v in d.items():
            w.writerow([case, blk, k, repr(v)])


if __name__ == '__main__':
    main()
