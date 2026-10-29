#!/usr/bin/env python3
"""run_bsm2python.py: BSM1 open loop in bsm2-python (BSM1OL), for bsm1cmp.py and bsm1kpi.py.

  run_bsm2python.py ss OUT.csv [DAYS]
      Constant influent (the report's Table 5 averages, 15 degC), 15-minute steps
      as in upstream's own steady-state test, for DAYS days (default 1000). Writes
      the states at day 100 (case ss100) and at the end (case ss).
  run_bsm2python.py dyn INPUTS WEATHER INTERP SI OUT.csv [OWN.csv] [STEP_MIN]
      150 days at constant influent, 14 days of dry weather, 14 days of WEATHER
      (dry, rain or storm), 1-minute steps (upstream's recommendation). INPUTS is
      the folder with the IWA files Inf_{dry,rain,strm}_2006.txt. INTERP: zoh
      feeds the 15-minute samples, which bsm2-python holds constant until the next
      one (its own behaviour); linear feeds the samples interpolated to every
      step. SI: hosted keeps the files' SI; diluted sets SI = 30*Qdry/Q, the
      influent the report's figures need (see README). Writes 15-minute samples
      of days 150-178 as t = 0..28, and bsm2-python's own IQ, EQ, AE, PE and ME
      over days 171-178 to OWN.csv. STEP_MIN (default 1) sets the step in minutes.
"""
import csv, sys, time
import numpy as np
from bsm2_python.bsm1_ol import BSM1OL

ST = ['SI', 'SS', 'XI', 'XS', 'XBH', 'XBA', 'XP', 'SO', 'SNO', 'SNH', 'SND', 'XND', 'SALK']
CONST = [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 18446]   # Table 5, then Q
IQ_, ITSS, IT = 14, 13, 15                                                          # bsm2-python indices
STAB = 150.0                                     # days at constant influent before the dry-weather file


def read_iwa(path):
    rows = [[float(x) for x in l.split()] for i, l in enumerate(open(path)) if i > 0 and l.strip()]
    for k, r in enumerate(rows):            # the files round t; the samples are every 15 minutes
        assert abs(r[0] - k / 96) < 1e-6
    return rows


def influent(inputs, weather, si):
    dry = read_iwa(f'{inputs}/Inf_dry_2006.txt')
    w = read_iwa(f'{inputs}/Inf_{"strm" if weather == "storm" else weather}_2006.txt')
    if si == 'diluted':
        w = [[r[0], 30 * d[14] / r[14]] + r[2:] for r, d in zip(w, dry)]
    return [r[1:] for r in dry[:-1]] + [r[1:] for r in w]        # 2689 samples, 0..28 d, [13 states, Q]


def row21(c):
    """13 states + Q -> bsm2-python's 21 (TSS, Q, T = 15, five dummy states)."""
    y = np.zeros(21)
    y[:13] = c[:13]
    y[ITSS] = 0.75 * (c[2] + c[3] + c[4] + c[5] + c[6])
    y[IQ_] = c[13]
    y[IT] = 15.0
    return y


def states(m):
    out = {'input_as': m.y_in1, 'reactor1': m.y_out1, 'reactor2': m.y_out2, 'reactor3': m.y_out3,
           'reactor4': m.y_out4, 'reactor5': m.y_out5, 'underflow': m.ys_out, 'effluent': m.ys_eff}
    rows = []
    for b, y in out.items():
        rows += [(b, v, y[i]) for i, v in enumerate(ST)]
        rows.append((b, 'TSS', y[ITSS]))
    rows += [('settler', f'TSS{j + 1}', x) for j, x in enumerate(m.ys_tss_internal)]
    return rows


def ss(out, days=1000.0):
    c = row21(CONST)
    data = np.array([np.r_[0.0, c], np.r_[days + 0.1, c]])
    dt = 15 / (60 * 24)
    m = BSM1OL(data_in=data, timestep=dt, endtime=days, tempmodel=False, activate=False)
    n = len(m.simtime)
    i100 = int(round(100 / dt)) - 1          # after step i the states are at simtime[i] + dt
    res, prev, t0 = [], None, time.time()
    for i in range(n):
        m.step(i)
        if i == i100:
            res += [('ss100',) + r for r in states(m)]
        if i == n - 1 - 96:
            prev = np.array([r[2] for r in states(m)])
    last = states(m)
    res += [('ss',) + r for r in last]
    change = np.max(np.abs(np.array([r[2] for r in last]) - prev) / np.maximum(np.abs(prev), 1e-300))
    with open(out, 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['case', 'block', 'var', 'value'])
        for r in res:
            w.writerow([r[0], r[1], r[2], repr(float(r[3]))])
    print(f'bsm2-python ss: {n} steps of {dt * 1440:g} min to t = {m.simtime[-1] + dt:g} d, '
          f'{time.time() - t0:.0f} s; largest relative change over the last day {change:.3e}')


def dyn(inputs, weather, interp, si, out, own=None, step_min=1.0):
    step_min = float(step_min)
    spm = int(round(15 / step_min))                         # steps per 15-minute sample
    dt = step_min / 1440
    inf = np.array(influent(inputs, weather, si))           # (2689, 14)
    T0 = STAB
    T1 = T0 + (len(inf) - 1) / 96                           # 178 d
    grid = np.arange(0, T1 + dt / 2, dt)                   # the same floats BSMBase's arange gives
    k0 = int(round(T0 / dt))
    samp = grid[k0::spm][:len(inf)]                         # 15-minute samples, as simtime values
    if interp == 'zoh':
        rows = [np.r_[0.0, row21(CONST)]] + [np.r_[t, row21(c)] for t, c in zip(samp, inf)]
    else:                                                    # linear between samples, at every step
        tt = (grid[k0:] - T0)
        lin = np.column_stack([np.interp(tt, np.arange(len(inf)) / 96, inf[:, j]) for j in range(14)])
        rows = [np.r_[0.0, row21(CONST)]] + [np.r_[t, row21(c)] for t, c in zip(grid[k0:], lin)]
    rows.append(np.r_[T1 + 1.0, rows[-1][1:]])            # BSMBase needs data past the end time
    data = np.array(rows)
    last = np.arange(0, T1 + 1.0, dt)
    last = last[last <= T1][-1]                             # BSMBase's last simtime
    m = BSM1OL(data_in=data, timestep=dt, endtime=T1, evaltime=np.array([T1 - 7.0, last]),
               tempmodel=False, activate=False)
    n = len(m.simtime)
    head = ['t', 'Qin'] + [v + '_in' for v in ST] + ['Qe'] + [v + '_e' for v in ST] + ['Qw'] + \
        [v + '_u' for v in ST] + [f'TSS_r{k}' for k in range(1, 6)] + [f'TSS_s{j}' for j in range(1, 11)]
    f = open(out, 'w', newline=''); w = csv.writer(f, lineterminator='\n'); w.writerow(head)
    t0 = time.time()
    for i in range(n):
        m.step(i)
        j = i + 1                                             # states now at grid[j]
        if j >= k0 and (j - k0) % spm == 0 and j < len(grid):
            t = grid[j]
            yin = data[np.where(m.data_time <= t)[0][-1], 1:]  # what the next step will use
            qw = min(385.0, m.ys_in[IQ_] - 18446.0)
            r = [(j - k0) / (96 * spm), yin[IQ_], *yin[:13], m.ys_eff[IQ_], *m.ys_eff[:13], qw, *m.ys_out[:13],
                 m.y_out1[ITSS], m.y_out2[ITSS], m.y_out3[ITSS], m.y_out4[ITSS], m.y_out5[ITSS],
                 *m.ys_tss_internal]
            w.writerow([repr(float(x)) for x in r])
    f.close()
    iqi, eqi, me, pe, ae = m.get_final_performance()
    if own:
        with open(own, 'w', newline='') as g:
            ww = csv.writer(g, lineterminator='\n'); ww.writerow(['case', 'block', 'var', 'value'])
            for k, v in (('IQ', iqi), ('EQ', eqi), ('ME', me), ('PE', pe), ('AE', ae)):
                ww.writerow([weather, 'own', k, repr(float(v))])
    print(f'bsm2-python dyn {weather} {interp} SI {si}: {n} steps, {time.time() - t0:.0f} s; '
          f'own IQ {iqi:.4f} EQ {eqi:.4f}')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'ss' and len(a) in (2, 3):
        ss(a[1], *(float(x) for x in a[2:]))
    elif a and a[0] == 'dyn' and len(a) in (6, 7, 8):
        dyn(*a[1:])
    else:
        print(__doc__); sys.exit(2)
