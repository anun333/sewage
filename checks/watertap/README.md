# checks/watertap: two things in WaterTAP's own CI

Both were found while looking at WaterTAP's BSM2 issues ([ideas U5](../../ideas.md#u5)).
Everything ran on GitHub's runners, from this repository's workflows, started by hand.

## #1876: the BSM2 electroNP (no bio-P) flowsheet failing "at random" on Windows

[watertap-org/watertap#1876](https://github.com/watertap-org/watertap/issues/1876)
reports `test_BSM2_electroNP_no_bioP` failing at random on Windows, Python 3.12 and
3.13. It has been skipped since #1877 (2026-09-25). #1851, the other BSM2 issue, has a
fix in progress from WaterTAP's developers (#1872), so it was left alone.

**WaterTAP's failing CI logs** (every failed Checks run from 2026-09-20 to 2026-10-29,
about 126 MB):
- **Six failures,** 21 to 25 September, all `win64`, Python 3.12 and 3.13. Each is an
  `InitializationError` at the "closing recycle" solve.
- **Every one ends identically:** IPOPT 3.13.2 with MA27 stops after 3000 iterations at
  overall NLP error `3.2791577558896899e-09` scaled and `9.9785802011532694e+07`
  unscaled, to the last digit. So the failing path is deterministic, and something
  discrete chooses it.
- **The same commit and Python can go either way.** At `b5c7ce154` (`main`, 25
  September), "Tests (py3.13/win64)" passed and "pytest (user mode) (py3.13/win64)"
  failed. Both had idaes-pse 2.13.0, Pyomo 6.10.1, numpy 2.5.3 and IDAES's solvers
  3.4.2. They differ in which tests run before this one.

**Our runs** ([run1876.py](run1876.py): the flowsheet's `main()` in fresh processes),
at WaterTAP `1ddf41f` (2026-10-30):

| | Linux (ubuntu-22.04) | Windows (windows-2022) |
| --- | --- | --- |
| closing solve | 650 iterations, "Optimal Solution Found" | 410 iterations, only "Solved To Acceptable Level" |
| PYTHONHASHSEED 0-9, and 0 and 1 again | all 12 runs bit-identical | all 12 runs bit-identical |
| Python 3.12 against 3.13 | identical | identical |
| ten runners (AMD EPYC 7763, 9V45, 9V74) | | all identical |
| `OPENBLAS_CORETYPE` forced to five kernels | | no effect: `ipopt.exe` links reference `libblas.dll`, not OpenBLAS |

So in a fresh process the flowsheet doesn't depend on the hash seed, the Python version or
those AMD CPUs.

**The cause: the CPU vendor, on Windows only.** Sampling more runners at `1ddf41f`
([watertap-1876-cpu.yml](../../.github/workflows/watertap-1876-cpu.yml)):

| runners | closing solve |
| --- | --- |
| Windows, Intel Xeon Platinum 8573C and 8370C (9) | fails exactly as in WaterTAP's CI: 3000 iterations, NLP error `3.2791577558896899e-09` / `9.9785802011532694e+07` to the last digit |
| Windows, AMD EPYC 7763, 9V45 and 9V74 (44) | passes, "Solved To Acceptable Level" after 410 iterations, all bit-identical |
| Linux, AMD (15) and Intel (3) | "Optimal Solution Found" in 650 iterations, all bit-identical |

- **Leftover state from earlier tests is ruled out.** At the failing commit `b5c7ce154`,
  with that CI job's own package versions (`constraints-1876-sep25.txt`), the test passed
  alone, fresh and in the full user-mode session on four AMD runners
  ([watertap-1876-session.yml](../../.github/workflows/watertap-1876-session.yml)).
- **The image doesn't decide it either:** WaterTAP's failures shared an image version
  with a pass.
- **So it is the Windows build of the solvers.** `ipopt.exe` links `msvcrt.dll`, MinGW's
  runtime and reference BLAS, and gives different arithmetic on Intel than on AMD here.
  Which function, exactly, was not traced.

**Where the margin went.** At the parent of `865012cd7` (2026-09-03, "Update operating
conditions": feed `X_PAO` 500 to 51.5262 g/m³), all 28 Windows runners, 2 of them Intel,
give "Optimal Solution Found" in 200 iterations, bit-identical. Since that commit, AMD
reaches only "acceptable" and Intel fails. On Linux the solve was optimal before (632
iterations) and after (650).

**Why it's fragile** ([diag1876.py](diag1876.py), IDAES's DiagnosticsToolbox;
[watertap-1876-diag.yml](../../.github/workflows/watertap-1876-diag.yml),
[watertap-1876-history.yml](../../.github/workflows/watertap-1876-history.yml)):
- **At the Intel failure,** the equations are met (violation 3e-9), but dual infeasibility
  (3.3e3 scaled) and complementarity (25) stay large: the iterates sit against bounds.
- **In every solution, before and after `865012cd7`,** about 244 variables are at or near
  their bounds. They include `S_NO3` and `X_AUT` at about zero in all 55 state blocks
  (nitrifiers washed out), and the Jacobian condition number is about 3.4e13.

A comment for #1876 is drafted in
[upstream/watertap/comment-1876.md](../../upstream/watertap/comment-1876.md).

## METAB `model_evaluation`: appended rows hold lists

Since 2026-10-22, five tests in
`watertap/flowsheets/METAB/tests/test_model_evaluation.py` fail WaterTAP's CI wherever
pip installs pandas 3.1.0. That's Python 3.11 to 3.13, on Linux and Windows, in PRs and
on `main`: 114 of the 116 failed test jobs on those versions show it. Python 3.10 gets
pandas 2.3.3. WaterTAP tracks the failures as
[#1889](https://github.com/watertap-org/watertap/issues/1889).

The cause is a real bug, which pandas 3.1 now warns about.
- **Where.** The helpers build `fr_dict` with one-element lists. `df.loc[len(df)] =
  fr_dict` then stores each list as a cell, and the columns become `object`.
- **Checked** with pandas 2.3.3 (silent) and 3.1.0 (`Pandas4Warning`) on cfarm421.
- **Who it reaches.** Only callers who pass an existing `df`; `collect_results` doesn't.

[upstream/watertap/0001-*.patch](../../upstream/watertap/0001-METAB-model_evaluation-append-rows-with-pd.concat.patch)
appends with `pd.concat` and checks the dtype in the tests.
[watertap-metab.yml](../../.github/workflows/watertap-metab.yml) tests it:

| code | tests | pandas | result |
| --- | --- | --- | --- |
| `main` | `main`'s | 3.1.0 | 5 failed (`Pandas4Warning`), as in WaterTAP's CI |
| `main` | the patch's | 2.3.3 | 5 failed on the new dtype check, with no warning |
| patched | the patch's | 3.1.0 | 20 passed |
| patched | the patch's | 2.3.3 | 20 passed |
