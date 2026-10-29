#!/usr/bin/env python3
"""run_watertap.py OUT.csv: WaterTAP's BSM1-based ASM1 flowsheet, steady state, for bsm1cmp.py.

WaterTAP has no BSM1 flowsheet with BSM1's settler. The nearest is
watertap/flowsheets/activated_sludge/ASM1_flowsheet.py: BSM1's five reactors
and flows, ASM1, and a clarifier that is a separator with fixed split
fractions, solved as one steady state by IPOPT. Three cases go to OUT.csv:

  ss_shipped   build_flowsheet() as shipped: reactor 5's oxygen fixed at
               4.49e-4 kg/m3, split fractions rounded to 5 decimals.
  ss_kla5      the same, then reactor 5 aerated with KLa = 3.5 1/h (84 1/d,
               the report's open-loop value) like reactors 3 and 4, oxygen free.
  ss_exact     ss_kla5 with the flows exact (Qe 18061, Qw 385 of 18831) and the
               particulate split to the effluent set from the report's own
               steady state (Qe*TSSe / (Qf*TSSf), TSSe 12.4969, TSSf 3269.8246;
               Appendix 4, p. 41): what WaterTAP's ASM1 reactors give when the
               settler is replaced by the answer it should reach.

WaterTAP gives no settler layers; underflow is the Sludge product, effluent
the Treated product and input_as the inlet of R1.
"""
import csv, sys
import pyomo.environ as pyo
from pyomo.environ import units as pu
from watertap.flowsheets.activated_sludge.ASM1_flowsheet import build_flowsheet
from watertap.core.solvers import get_solver
from idaes.core.util.model_statistics import degrees_of_freedom

ST = ['SI', 'SS', 'XI', 'XS', 'XBH', 'XBA', 'XP', 'SO', 'SNO', 'SNH', 'SND', 'XND', 'SALK']
WT = ['S_I', 'S_S', 'X_I', 'X_S', 'X_BH', 'X_BA', 'X_P', 'S_O', 'S_NO', 'S_NH', 'S_ND', 'X_ND']


def port_values(port_or_block, inlet=False):
    b = port_or_block
    c = b.conc_mass_comp
    out = {v: pyo.value(pu.convert(c[0, w], to_units=pu.g / pu.m ** 3)) for v, w in zip(ST, WT)}
    out['SALK'] = pyo.value(pu.convert(b.alkalinity[0], to_units=pu.mol / pu.m ** 3))
    out['Q'] = pyo.value(pu.convert(b.flow_vol[0], to_units=pu.m ** 3 / pu.day))
    return out


def collect(m, case):
    fs = m.fs
    blocks = {'input_as': fs.R1.inlet, 'reactor1': fs.R1.outlet, 'reactor2': fs.R2.outlet,
              'reactor3': fs.R3.outlet, 'reactor4': fs.R4.outlet, 'reactor5': fs.R5.outlet,
              'underflow': fs.Sludge.inlet, 'effluent': fs.Treated.inlet}
    rows = []
    for b, port in blocks.items():
        d = port_values(port)
        rows += [(case, b, v, d[v]) for v in ST]
        rows.append((case, 'flows', f'Q_{b}', d['Q']))
    return rows


def add_kla5(m, solver):
    fs = m.fs
    fs.R5.KLa = pyo.Var(initialize=3.5, units=pu.hour ** -1)

    @fs.R5.Constraint(fs.time)
    def mass_transfer_R5(self, t):
        return pu.convert(fs.R5.injection[t, 'Liq', 'S_O'], to_units=pu.kg / pu.hour) == (
            fs.R5.KLa * fs.R5.volume[t] * (fs.S_O_eq - fs.R5.outlet.conc_mass_comp[t, 'S_O']))

    fs.R5.KLa.fix(3.5)
    fs.R5.outlet.conc_mass_comp[:, 'S_O'].unfix()
    assert degrees_of_freedom(m) == 0
    res = solver.solve(m)
    pyo.assert_optimal_termination(res)


def set_exact(m, solver):
    fs = m.fs
    qe, qf, qr, qw = 18061.0, 36892.0, 18446.0, 385.0
    fx = qe * 12.4969 / (qf * 3269.8246)
    for j in ['H2O', 'S_I', 'S_S', 'S_O', 'S_NO', 'S_NH', 'S_ND', 'S_ALK']:
        fs.CL1.split_fraction[0, 'effluent', j].fix(qe / qf)
    for j in ['X_I', 'X_S', 'X_BH', 'X_BA', 'X_P', 'X_ND']:
        fs.CL1.split_fraction[0, 'effluent', j].fix(fx)
    fs.SP6.split_fraction[:, 'recycle'].fix(qr / (qr + qw))
    fs.SP5.split_fraction[:, 'underflow'].fix(0.6)
    assert degrees_of_freedom(m) == 0
    res = solver.solve(m)
    pyo.assert_optimal_termination(res)
    return fx


def main(out):
    m, res = build_flowsheet()
    pyo.assert_optimal_termination(res)
    solver = get_solver()
    rows = collect(m, 'ss_shipped')
    add_kla5(m, solver)
    rows += collect(m, 'ss_kla5')
    fx = set_exact(m, solver)
    rows += collect(m, 'ss_exact')
    with open(out, 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['case', 'block', 'var', 'value'])
        for r in rows:
            w.writerow([r[0], r[1], r[2], repr(float(r[3]))])
    print('solver options:', dict(solver.options))
    print(f'particulate split to effluent in ss_exact: {fx!r}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(2)
    main(sys.argv[1])
