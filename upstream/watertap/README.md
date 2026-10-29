# upstream/watertap: drafts for watertap-org/watertap

Not posted. Each draft is read and approved in full before it goes out.

| File | What |
| --- | --- |
| [issue.md](issue.md) | `ASM1_flowsheet.py` holds reactor 5's oxygen at 0.449 g/m³ where BSM1's open loop gives 0.491. Effluent nitrate and ammonia move 2.6% and 7.3%, and the test accepts it. Two fixes, both measured |

The evidence is in [checks/bsm1/](../../checks/bsm1/README.md): `run_watertap.py`, its
four cases, and `results/ss_watertap.csv`.

## Before a PR

- **WaterTAP's PR template has a "Legal Acknowledgement".** The contribution is under
  WaterTAP's licence (BSD-3-Clause-LBNL), and the contributor is authorised to make it,
  with the employer's permission if an employer holds rights to it. See
  [rules/terms.md](../../rules/terms.md).
- **AI disclosure.** WaterTAP's template doesn't ask, but IDAES's does, and we disclose
  everywhere anyway.
- **Run WaterTAP's own test.** `tests/test_asm1_flowsheet.py` pins the shipped values
  (S_O 4.49e-4, S_NO 10.14e-3, S_NH 1.86e-3, at rel 1e-2). A fix has to update them, and
  the suite should pass with the change before the PR is opened. That hasn't been run
  yet.
- **Open the issue first** and let the maintainers choose between the two fixes: one
  line, or a KLa constraint like R3's and R4's.

## Questions to expect

- **Is 0.449 deliberate?** Line 312 calls R5 "controlled", but BSM1's closed-loop
  setpoint is 2 g/m³, not 0.449. Where 0.449 comes from isn't stated. The same block
  appears in their BSM2, METAB-BSM1 and ASM2d flowsheets.
- **Why not leave it, since this is only an example?** Because the test then certifies
  results that are 7% off as correct to the last digit, and other flowsheets copy the
  block.
- **What about the clarifier?** It is a separator, which their TODO comments already
  say. With exact splits, the reactors match the report and bsm2-python to 1.8e-7, so
  the oxygen is the only modelling difference left.
