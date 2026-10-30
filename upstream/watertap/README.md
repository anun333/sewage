# upstream/watertap: drafts for watertap-org/watertap

Each draft is read and approved in full before it goes out.

| File | What |
| --- | --- |
| [comment-1876.md](comment-1876.md) | #1876's "random" Windows failures: Intel runners fail and AMD runners pass, every time, since `865012cd7` (2026-09-03); before it both gave the same optimal solution. The solution has nitrifiers washed out (many variables at zero bounds, condition number 3.4e13), so the solve has no margin. Not posted |
| [pr-metab-concat.md](pr-metab-concat.md), [0001-METAB-*.patch](0001-METAB-model_evaluation-append-rows-with-pd.concat.patch) | Since pandas 3.1, five METAB `model_evaluation` tests fail WaterTAP's CI on Python 3.11-3.13 (PRs and `main`). The cause is a real bug: appended rows hold one-element lists. A `pd.concat` fix with dtype checks in the tests, tested with pandas 3.1.0 and 2.3.3, controls both ways ([.github/workflows/watertap-metab.yml](../../.github/workflows/watertap-metab.yml)). Not posted |
| [issue.md](issue.md) | **Posted 2026-10-29 as [#1892](https://github.com/watertap-org/watertap/issues/1892).** `ASM1_flowsheet.py` holds reactor 5's oxygen at 0.449 g/m³ where BSM1's open loop gives 0.491. Effluent nitrate and ammonia move 2.6% and 7.3%, and the test accepts it. Two fixes, both measured |

The evidence is in [checks/bsm1/](../../checks/bsm1/README.md): `run_watertap.py`, its
four cases, and `results/ss_watertap.csv`.

## Before a PR

- **WaterTAP's PR template has a "Legal Acknowledgement".** The contribution is under
  WaterTAP's licence (BSD-3-Clause-LBNL), and the contributor is authorised to make it,
  with the employer's permission if an employer holds rights to it. See
  [rules/terms.md](../../rules/terms.md).
- **AI disclosure.** WaterTAP's template doesn't ask, but IDAES's does, and we disclose
  everywhere anyway.
- **Run WaterTAP's own test: done 2026-10-29 for the one-line fix.** This was on
  board5, at 5909a60, with idaes-pse 2.13.0, Pyomo 6.10.1 and IPOPT 3.13.2.
  - As shipped, `tests/test_asm1_flowsheet.py` passes (2 tests). It pins S_O 4.49e-4,
    S_NO 10.14e-3 and S_NH 1.86e-3 at rel 1e-2.
  - The candidate PR changes:
    - line 216 to `fix(4.91e-4)`;
    - the test's Treated and Sludge expectations to BSM1's Tables 6 and 8 (S_O 4.91e-4,
      S_NO 10.4e-3, S_NH 1.73e-3, rel 1e-2, with the "slightly off" comments replaced
      by the reference);
    - the doc table in `docs/technical_reference/flowsheets/ASM1.rst`. It lists the
      three fixed oxygen values in g/m³ but gives kilogram figures, and R5's is also
      off by ten (0.00449). They become 1.72, 2.43 and 0.491.
  - With the change, the test passes. With the new test on the old code, it fails, which
    is the control. All 12 tests in `flowsheets/activated_sludge/` pass, and black
    26.3.1 (their pin) is clean.
  - The diff (3 files, +12/-14) is kept out of this repository, because its context
    lines are WaterTAP's BSD-3-Clause-LBNL code. It goes up from a fork.
  - Not run: the KLa variant through their test suite, and the docs build.
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
