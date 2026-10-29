<!-- Posted 2026-10-29 as https://github.com/watertap-org/watertap/issues/1892 after the maintainer read and approved this text. -->

**Title:** ASM1_flowsheet: reactor 5's oxygen is fixed at 0.449 g/m³; BSM1's open loop gives 0.491, and effluent N moves 2.6-7%

### Description

`watertap/flowsheets/activated_sludge/ASM1_flowsheet.py` (on `main`, 5909a60) is based on BSM1 (Alex et al., cited in its docstring). It sets the aerobic reactors' oxygen like this:

- R3 and R4 start fixed at 1.72e-3 and 2.43e-3 kg/m³ (lines 214-215). Those are BSM1's Table 6 values, 1.72 and 2.43 g/m³. Lines 313-316 then switch both to KLa = 10 1/h, which is BSM1's 240 1/d.
- R5 stays fixed at 4.49e-4 kg/m³ (line 216). The comment at line 312 says "S_O concentration is controlled in R5".

BSM1 has neither 0.449 g/m³:
- In open loop, R5 is aerated with KLa = 84 1/d (3.5 1/h), giving S_O = 0.491 g/m³ (Table 6; Appendix 4 has 0.49094).
- In closed loop, R5's oxygen is controlled to a setpoint of 2 g/m³.

The lower oxygen shifts nitrogen in the effluent, and the test accepts the shift. `tests/test_asm1_flowsheet.py` pins these at rel=1e-2, with the comments "S_O is slightly off" and "Slightly off in last significant digit":
- effluent S_NO at 10.14e-3;
- S_NH at 1.86e-3;
- S_O at 4.49e-4.

Against the report, S_NO is −2.6% and S_NH +7.3%. That is more than the last digit.

### Expected Behavior

The flowsheet should reproduce BSM1's open-loop steady state (Tables 6-8) to the printed digits, apart from what the separator-for-a-settler simplification changes. Steady states solved here (IPOPT, same solver options):

| | BSM1 Table 6/8 | App. 4 | as shipped | R5 fixed at 4.91e-4 | R5 at KLa 3.5 1/h |
| --- | ---: | ---: | ---: | ---: | ---: |
| R5 S_O (g/m³) | 0.491 | 0.49094 | 0.449 | 0.491 | 0.49095 |
| effluent S_NO (g N/m³) | 10.4 | 10.4152 | 10.148 | 10.415 | 10.415 |
| effluent S_NH (g N/m³) | 1.73 | 1.7334 | 1.8597 | 1.7344 | 1.7345 |
| R2 S_NO (g N/m³) | 3.66 | 3.6619 | 3.4486 | 3.6621 | 3.6619 |
| effluent alkalinity (mol/m³) | 4.13 | 4.1256 | 4.1537 | 4.1257 | 4.1257 |
| values matching Tables 6-8 to the printed digits | | | 35 of 98 | 86 of 98 | 87 of 98 |

Most of the remaining misses come from the separator's split fractions, which are rounded to five decimals (lines 223-239: 0.48956, 0.00187, 0.97955; the wastage comes out 385.1 m³/d rather than 385). With the exact flow splits (18061/36892 = 0.489564..., 18446/18831 = 0.979555...) and a particulate split matching the report's settler, 97 of 98 values match. The remaining one is a rounding slip in the report itself (R2 TSS printed 3282; Appendix 4's 3282.53 rounds to 3283). The result is then within 1.8e-7 of bsm2-python's converged BSM1, which matches the BSM group's Simulink to 1e-8.

### Steps to Reproduce

```python
import pyomo.environ as pyo
from watertap.flowsheets.activated_sludge.ASM1_flowsheet import build_flowsheet
from watertap.core.solvers import get_solver

m, res = build_flowsheet()
def show(tag):
    c = lambda b, j: 1000 * pyo.value(b.conc_mass_comp[0, j])   # kg/m3 -> g/m3
    print(tag, "R5 S_O", round(c(m.fs.R5.outlet, "S_O"), 4),
          "| effluent S_NO", round(c(m.fs.Treated, "S_NO"), 4),
          "S_NH", round(c(m.fs.Treated, "S_NH"), 4))
show("as shipped:")                                          # 0.449 | 10.1476 1.8597
m.fs.R5.outlet.conc_mass_comp[:, "S_O"].fix(4.91e-4)         # BSM1 open loop, Table 6
pyo.assert_optimal_termination(get_solver().solve(m))
show("R5 at 0.491:")                                         # 0.491 | 10.4152 1.7344
```

### Environment

- WaterTAP `main` at 5909a60 (1.9.0.dev0), idaes-pse 2.13.0, Pyomo 6.10.1, IPOPT 3.13.2 (idaes-ext 3.4.2), Python 3.12 and 3.13.
- Run on Ubuntu 24.04 x86-64 and on Debian 13 x86-64. The results were bit-identical on both machines.

### Anything Else?

**Two possible fixes:**
- **One line:** `fix(4.91e-4)` at line 216, which keeps R5 as an oxygen-fixed reactor, as the line-312 comment intends.
- **Aerate R5 with KLa = 3.5 1/h** through a `mass_transfer_R5` constraint like R3's and R4's. That matches BSM1's open loop structurally.

They give the same numbers to about 1e-4. Either way, the test's expected values could move to the report's: S_O 4.91e-4, S_NO 10.4e-3, S_NH 1.73e-3, alkalinity 4.13e-3. I'm happy to open a PR for whichever you prefer. I haven't yet run WaterTAP's test suite with either change.

**The same lines appear elsewhere.** R3/R4/R5 oxygen fixed at 1.72e-3, 2.43e-3 and 4.49e-4 also appears in:
- `full_water_resource_recovery_facility/BSM2.py` (lines 338-340);
- `METAB/METAB_BSM1_flowsheet.py` (lines 295-297);
- `activated_sludge/ASM2D_flowsheet_noPHA.py` (lines 203-205; R3 there is 2.72e-3).

I haven't checked those against their own references. In BSM2, for instance, the activated-sludge volumes and aeration differ, so the right values may differ too.

The full comparison (BSM1 open loop in QSDsan, WaterTAP and bsm2-python against the 2008 report, with scripts, results and controls) is at https://github.com/anun333/sewage/tree/main/checks/bsm1. The case above is `run_watertap.py`'s `ss_r5fix`.

Drafted with an AI assistant (Claude), which also ran the builds and checks reported here; I read it before posting.
