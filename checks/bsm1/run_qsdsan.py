#!/usr/bin/env python3
"""run_qsdsan.py: BSM1 open loop in QSDsan through EXPOsan's bsm1 module, for bsm1cmp.py and bsm1kpi.py.

  run_qsdsan.py ss OUT.csv [DAYS] [RTOL] [COEF]
      exposan.bsm1 as shipped (ASM1, CSTRs, KLa 240/240/84 1/d, its default
      initial conditions), constant influent, integrated with scipy's BDF
      (rtol = atol = RTOL, default 1e-8) for DAYS days (default 1000). Writes the
      states at day 100 (case ss100) and at the end (case ss). COEF bsm1 swaps
      in the report's rounded stoichiometric constants (bsm1_coefficients).
  run_qsdsan.py dyn INPUTS WEATHER INTERP SI OUT.csv [RTOL]
      The same plant with QSDsan's DynamicInfluent in front, started from the
      steady state (300 days of constant influent), then 14 days of dry weather
      and 14 days of WEATHER (dry, rain or storm). INTERP: cubic is
      DynamicInfluent's default (a periodic cubic spline through the 15-minute
      samples); linear is its first-order spline; a suffix -fixqa holds the
      internal recycle at 55338 m3/d (see fixed_recycle). SI as in
      run_bsm2python.py. The Qa column is the internal recycle that results:
      shipped, 0.6 of reactor 5's outflow, so 1.5*(Qin + Qr) at every instant.
      Writes 15-minute samples of the 28 days. RTOL default 1e-6.

Values are read from solve_ivp's dense output at the requested times
(System.scope.sol.sol). biosteam's System.simulate keeps t_eval for its own
export and calls solve_ivp without it, so sol.t holds every internal step.
"""
import csv, os, sys, tempfile, time
import numpy as np
import qsdsan as qs
from qsdsan import processes as pc, sanunits as su, System
from exposan import bsm1
from exposan.bsm1 import system as bs

ST = ['SI', 'SS', 'XI', 'XS', 'XBH', 'XBA', 'XP', 'SO', 'SNO', 'SNH', 'SND', 'XND', 'SALK']
QS = ['S_I', 'S_S', 'X_I', 'X_S', 'X_BH', 'X_BA', 'X_P', 'S_O', 'S_NO', 'S_NH', 'S_ND', 'X_ND', 'S_ALK']
SCALE = [1.0] * 12 + [1 / 12]                    # S_ALK is kept as mg C/L; BSM1 uses mol HCO3/m3
CONST = [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 18446]
Q0, QA, QR, QW = 18446.0, 55338.0, 18446.0, 385.0


def read_iwa(path):
    rows = [[float(x) for x in l.split()] for i, l in enumerate(open(path)) if i > 0 and l.strip()]
    for k, r in enumerate(rows):
        assert abs(r[0] - k / 96) < 1e-6
    return rows


def influent(inputs, weather, si):
    dry = read_iwa(f'{inputs}/Inf_dry_2006.txt')
    w = read_iwa(f'{inputs}/Inf_{"strm" if weather == "storm" else weather}_2006.txt')
    if si == 'diluted':
        w = [[r[0], 30 * d[14] / r[14]] + r[2:] for r, d in zip(w, dry)]
    return [r[1:] for r in dry[:-1]] + [r[1:] for r in w]


def bsm(conc, ids):
    """QSDsan concentration vector (mg/L, in ids order) -> the 13 BSM1 states."""
    ix = {c: i for i, c in enumerate(ids)}
    return [conc[ix[c]] * s for c, s in zip(QS, SCALE)]


def tss(c):
    return 0.75 * (c[2] + c[3] + c[4] + c[5] + c[6])


def blocks_at(sysm, y, inf=None):
    """BSM1 blocks from a system state vector y (solve_ivp's layout, System._state_idx).

    The clarifier's outlets are rebuilt as QSDsan builds them (FlatBottomCircularClarifier
    _update_state): solubles of the clarifier plus the layer's TSS times the particulate
    composition of its feed, reactor 5."""
    idx = sysm._state_idx
    st = {n: y[a:b] for n, (a, b) in idx.items()}
    cmps = sysm.flowsheet.unit.A1.components
    ids, x, imass = cmps.IDs, np.asarray(cmps.x, float), np.asarray(cmps.i_mass, float)
    m = len(ids)
    R = [st[n][:m] for n in ('A1', 'A2', 'O1', 'O2', 'O3')]
    c1 = st['C1']
    n = sysm.flowsheet.unit.C1._N_layer
    Z, layers = c1[:m] * (1 - x), c1[-n:]
    xc = R[4] * x / np.sum(R[4] * imass * x)
    out = {f'reactor{i + 1}': bsm(R[i], ids) for i in range(5)}
    out['underflow'] = bsm(Z + layers[-1] * xc, ids)
    out['effluent'] = bsm(Z + layers[0] * xc, ids)
    if inf is not None:   # A1's inlet: influent, internal recycle (reactor 5) and returned sludge
        out['input_as'] = [(Q0 * a + QA * b + QR * c) / (Q0 + QA + QR)
                           for a, b, c in zip(inf, out['reactor5'], out['underflow'])]
    return out, list(layers)


def rows_of(blocks, layers):
    rows = []
    for b, c in blocks.items():
        rows += [(b, v, x) for v, x in zip(ST, c)]
        rows.append((b, 'TSS', tss(c)))
    rows += [('settler', f'TSS{j + 1}', x) for j, x in enumerate(layers)]
    return rows


def fixed_recycle(O3, qa):
    """Make O3's first outlet (the internal recycle) a constant flow qa, as BSM1 has it.

    Shipped, CSTR.split is a fraction (0.6 of O3's outflow), so the recycle follows
    the influent flow. This replaces O3's two state updates (CSTR._update_state and
    _update_dstate, qsdsan/unit_operations/dynamic/_bioreactor.py) before the ODE
    is compiled."""
    import types

    def upd(self):
        arr = self._state
        arr[arr < 1e-16] = 0.
        arr[-1] = sum(ws.state[-1] for ws in self.ins)
        rww, tr = self._outs
        y = arr.copy(); y[-1] = qa; rww.state = y
        y = arr.copy(); y[-1] = arr[-1] - qa; tr.state = y

    def dupd(self):
        arr = self._dstate
        rww, tr = self._outs
        y = arr.copy(); y[-1] = 0.; rww.dstate = y
        tr.dstate = arr.copy()
    O3._update_state = types.MethodType(upd, O3)
    O3._update_dstate = types.MethodType(dupd, O3)


def bsm1_coefficients(folder):
    """A copy of EXPOsan's exposan/bsm1/data/_asm1.tsv with the report's rounded constants:
    2.86 for 20/7 (anoxic growth, S_NO and S_N2) and 4.57 for 32/7 (autotrophic growth, S_O)."""
    src = os.path.join(bsm1.data_path, '_asm1.tsv')
    txt = open(src).read()
    new = (txt.replace('7/20*(Y_H-1)/Y_H', '(Y_H-1)/(2.86*Y_H)').replace('7/20*(1-Y_H)/Y_H', '(1-Y_H)/(2.86*Y_H)')
              .replace('(Y_A-32/7)/Y_A', '(Y_A-4.57)/Y_A'))
    assert new.count('2.86') == 2 and new.count('4.57') == 1, 'unexpected _asm1.tsv'
    fd, path = tempfile.mkstemp(suffix='.tsv', dir=folder)
    with os.fdopen(fd, 'w') as f:
        f.write(new)
    return path


def steady(rtol, days, at=(), asm_path=None):
    """exposan.bsm1 as shipped, constant influent, from its default initial state, in one
    solve_ivp call from 0 to days; the system state at each time in at (from the dense
    output) and at days. No trackers: they keep every right-hand-side call, which over
    hundreds of days is gigabytes. (Splitting the run into legs, restarting simulate()
    without a reset, gave states 1% away from the one-shot run after 2 days; the legs
    were dropped, not explained.)"""
    kw = {}
    if asm_path:
        kw['asm_kwargs'] = dict(bs.default_asm_kwargs['asm1'], path=asm_path)
    bsm1.load(reload=True, **kw)
    sysm = bsm1.sys
    sysm.set_dynamic_tracker()
    t0 = time.time()
    sysm.simulate(state_reset_hook='reset_cache', t_span=(0.0, days), method='BDF', rtol=rtol, atol=rtol,
                  timeout=None, dense_output=bool(at))
    sol = sysm.scope.sol
    assert sol.status == 0, sol.message
    out = [sol.sol(t) for t in at] + [sol.y[:, -1].copy()]
    return sysm, out, time.time() - t0


def ss(out, days=1000.0, rtol=1e-8, coef='shipped'):
    days, rtol = float(days), float(rtol)
    path = bsm1_coefficients(os.path.dirname(os.path.abspath(out))) if coef == 'bsm1' else None
    sysm, ys, el = steady(rtol, days, at=(100.0, days - 1.0), asm_path=path)
    if path:
        os.remove(path)
    inf = CONST[:13]
    snap = [rows_of(*blocks_at(sysm, y, inf)) for y in ys]
    rows = [('ss100',) + r for r in snap[0]] + [('ss',) + r for r in snap[2]]
    a = np.array([r[2] for r in snap[1]]); b = np.array([r[2] for r in snap[2]])
    change = np.max(np.abs(b - a) / np.maximum(np.abs(a), 1e-300))
    with open(out, 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['case', 'block', 'var', 'value'])
        for r in rows:
            w.writerow([r[0], r[1], r[2], repr(float(r[3]))])
    print(f'qsdsan ss: BDF rtol=atol={rtol:g} to t = {days:g} d, {el:.0f} s, {sysm.scope.sol.nfev} RHS calls; '
          f'largest relative change over the last day {change:.3e}')


def dyn(inputs, weather, interp, si, out, rtol=1e-6):
    rtol = float(rtol)
    # 1. steady state of the shipped system, as initial conditions
    sysm, ys, el0 = steady(1e-8, 300.0)
    u = sysm.flowsheet.unit
    ids = u.A1.components.IDs
    y = ys[-1]
    st = {n: y[a:b] for n, (a, b) in sysm._state_idx.items()}
    init = {n: dict(zip(ids, st[n][:-1])) for n in ('A1', 'A2', 'O1', 'O2', 'O3')}
    m = len(ids)
    sol = dict(zip(ids, st['C1'][:m]))
    tss_layers = list(st['C1'][-u.C1._N_layer:])
    x = np.asarray(u.A1.components.x, float)
    ras = dict(zip(ids, st['O3'][:m] * x))           # particulate composition of the feed
    # 2. influent file for DynamicInfluent: t, component IDs (mg/L, S_ALK in mg C/L), Q (m3/d)
    inf = influent(inputs, weather, si)
    fd, path = tempfile.mkstemp(suffix='.tsv', dir=os.path.dirname(os.path.abspath(out)))
    with os.fdopen(fd, 'w') as f:
        f.write('\t'.join(['t'] + QS + ['Q']) + '\n')
        for k, c in enumerate(inf):
            vals = [x / s for x, s in zip(c[:13], SCALE)] + [c[13]]
            f.write('\t'.join([repr(k / 96)] + [repr(x) for x in vals]) + '\n')
    # 3. the same plant as exposan.bsm1.create_system (ASM1, CSTR), fed by DynamicInfluent
    qs.main_flowsheet.set_flowsheet(qs.Flowsheet(f'bsm1dyn_{weather}_{interp}'))
    pc.create_asm1_cmps()
    asm = pc.ASM1(**bs.default_asm_kwargs['asm1'])
    base, _, fix = interp.partition('-')
    kw = {} if base == 'cubic' else {'interpolator': 1}
    INF = su.DynamicInfluent('INF', data_file=path, **kw)
    aer1 = aer2 = pc.DiffusedAeration('aer1', 'S_O', KLa=240, DOsat=8.0, V=bs.V_ae)
    aer3 = pc.DiffusedAeration('aer3', 'S_O', KLa=84, DOsat=8.0, V=bs.V_ae)
    an = dict(V_max=bs.V_an, aeration=None, suspended_growth_model=asm)
    ae = dict(V_max=bs.V_ae, DO_ID='S_O', suspended_growth_model=asm)
    A1 = su.CSTR('A1', ins=[INF - 0, 'RWW', 'RAS'], **an)
    A2 = su.CSTR('A2', A1 - 0, **an)
    O1 = su.CSTR('O1', A2 - 0, aeration=aer1, **ae)
    O2 = su.CSTR('O2', O1 - 0, aeration=aer2, **ae)
    O3 = su.CSTR('O3', O2 - 0, [1 - A1, 'treated'], split=[bs.Q_intr, bs.Q + bs.Q_ras], aeration=aer3, **ae)
    C1 = su.FlatBottomCircularClarifier('C1', O3 - 1, ['effluent', 2 - A1, 'WAS'], **bs.default_c1_kwargs)
    if fix == 'fixqa':
        fixed_recycle(O3, bs.Q_intr)
    dsys = System('bsm1_dyn', path=(INF, A1, A2, O1, O2, O3, C1), recycle=(O3 - 0, C1 - 1))
    dsys.set_tolerance(rmol=1e-6)
    for n, unit in (('A1', A1), ('A2', A2), ('O1', O1), ('O2', O2), ('O3', O3)):
        unit.set_init_conc(**init[n])
    C1.set_init_solubles(**{k: v for k, v in sol.items() if v > 0})
    C1.set_init_sludge_solids(**{k: v for k, v in ras.items() if v > 0})
    C1.set_init_TSS(tss_layers)
    dsys.set_dynamic_tracker()
    t_eval = np.arange(len(inf)) / 96
    t0 = time.time()
    dsys.simulate(state_reset_hook='reset_cache', t_span=(0, t_eval[-1]), t_eval=t_eval, method='BDF',
                  rtol=rtol, atol=rtol, timeout=None, dense_output=True)
    assert dsys.scope.sol.status == 0, dsys.scope.sol.message
    el = time.time() - t0
    os.remove(path)
    ids = A1.components.IDs
    head = ['t', 'Qin'] + [v + '_in' for v in ST] + ['Qe'] + [v + '_e' for v in ST] + ['Qw'] + \
        [v + '_u' for v in ST] + [f'TSS_r{k}' for k in range(1, 6)] + [f'TSS_s{j}' for j in range(1, 11)] + ['Qa']
    qs_ = bs.Q_was
    with open(out, 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(head)
        sol = dsys.scope.sol
        for t in t_eval:
            yi = INF.interpolant(t)                         # component IDs + Q
            ci = bsm(yi[:-1], ids)
            blk, layers = blocks_at(dsys, sol.sol(t))
            qin = yi[-1]
            qe = qin - qs_                                  # clarifier: (Qin + Qr) in, Qr + Qw out below
            qa = QA if fix == 'fixqa' else O3.split[0] * (qin + bs.Q_ras) / (1 - O3.split[0])
            r = [t, qin, *ci, qe, *blk['effluent'], qs_, *blk['underflow'],
                 *[tss(blk[f'reactor{i}']) for i in range(1, 6)], *layers, qa]
            w.writerow([repr(float(v)) for v in r])
    qin = INF.interpolant(t_eval[-1])[-1]
    print(f'internal recycle at t = 28: stream {O3.outs[0].state[-1]:.3f} m3/d, Qa column '
          f'{QA if fix == "fixqa" else 1.5 * (qin + bs.Q_ras):.3f}')
    print(f'qsdsan dyn {weather} {interp} SI {si}: steady state {el0:.0f} s, BDF rtol=atol={rtol:g} '
          f'over {t_eval[-1]:g} d {el:.0f} s, {dsys.scope.sol.nfev} RHS calls')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'ss' and len(a) in (2, 3, 4, 5):
        ss(*a[1:])
    elif a and a[0] == 'dyn' and len(a) in (6, 7):
        dyn(*a[1:])
    else:
        print(__doc__); sys.exit(2)
