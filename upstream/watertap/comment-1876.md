<!-- Draft, not posted. A comment on watertap-org/watertap#1876. Evidence: checks/watertap/README.md "#1876"; workflows watertap-1876*.yml in anun333/sewage, runs 41111593097, 41112937032, 41114515417, 41119049846, 41119769250, 41120600926, 41121805857, 41122509497, 41123021921 (2026-10-30). -->

**Comment on #1876:**

I looked into this. The failures aren't random: on Windows the test fails on Intel runners and passes on AMD runners. GitHub's `windows-2022` pool mixes the two, so it looked random.

**The CI failures.** Between 21 and 25 September the test failed six times, all on `win64` with Python 3.12 or 3.13. Every one ends in the same state: an `InitializationError` at the closing recycle solve, IPOPT 3.13.2 (MA27) after 3000 iterations, with overall NLP error `3.2791577558896899e-09` scaled and `9.9785802011532694e+07` unscaled. At `b5c7ce154` the same Python failed in the user-mode job and passed in the Tests job.

**Reproduced, by CPU.** I ran the flowsheet's `main(has_electroNP=True)` on GitHub runners at `1ddf41f`:

| runners | result |
| --- | --- |
| Windows, Intel Xeon Platinum 8573C and 8370C (9 runners) | all fail exactly as in CI: 3000 iterations, the same NLP error to the last digit |
| Windows, AMD EPYC 7763, 9V45 and 9V74 (44 runners) | all pass, but only "Solved To Acceptable Level", after 410 iterations; all bit-identical |
| Linux, AMD and Intel (18 runners, 3 of them Intel) | all "Optimal Solution Found" in 650 iterations; all bit-identical |

On a given runner the result doesn't depend on `PYTHONHASHSEED` (ten seeds, bit-identical) or the Python version (3.12, 3.13). On AMD runners the test passed both alone and in the full user-mode session at `b5c7ce154`, so earlier tests don't change it. So it's the arithmetic in the Windows build of the solvers (`ipopt.exe` links `msvcrt.dll`, MinGW's runtime and reference BLAS), which differs between Intel and AMD here.

**Where the margin went.** At the parent of `865012cd7` (2026-09-03, "Update operating conditions": feed `X_PAO` from 500 to 51.5262 g/m³), the closing solve is "Optimal Solution Found" in 200 iterations on Windows, Intel and AMD alike, bit-identical (28 runners, 2 of them Intel). Since that change it reaches only "acceptable" on AMD, and fails on Intel.

**Why it's fragile.** On the Intel runners the equations end up met (constraint violation 3e-9), but dual infeasibility (3.3e3 scaled) and complementarity (25) stay large: the iterates are against variable bounds. IDAES's `DiagnosticsToolbox` on the solution (Linux and AMD Windows) and the last iterate (Intel) shows the same thing in each case:
- 244 variables at or near bounds, including `S_NO3` and `X_AUT` at about zero in all 55 state blocks, so autotrophs and nitrate are washed out of the plant;
- a Jacobian condition number of 3.4e13.

This was already so before `865012cd7`. A square solve that has to land on so many zero bounds leaves IPOPT little margin, and small arithmetic differences decide it.

I don't know whether nitrifier washout is intended for this configuration; you'd know better. If it isn't, that may be the thing to fix. Two smaller suggestions:
- Printing the runner's CPU in the CI environment summary would make failures like this easy to recognise.
- On Windows, a failing case can be reproduced on demand by checking for an Intel runner.

The scripts and all run records are at https://github.com/anun333/sewage/tree/main/checks/watertap.

Drafted with an AI assistant (Claude), which also ran the checks reported here; I read it before posting.
