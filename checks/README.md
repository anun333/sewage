# checks

Measurements behind [../ideas.md](../ideas.md). Each ends in a verdict line, the way
crnumerics' checks do: `IDENTICAL` (exit 0), `DIFFERS` (exit 1), `VOID` (exit 2: a
control failed or nothing was tested). Standard library only.

| Check | Question | Result (board5, cfarm424 and cfarm104 agree, 2026-10-27) |
| --- | --- | --- |
| [dmr_rounding.py](dmr_rounding.py) | When an average of decimal lab values lands on a rounding tie, does rounding the binary64 value give the rule's answer? | **DIFFERS** for the binary value: 41–46% of ties round wrong, under half up and half even alike. EPA's worked example 1.15 → 1.2 comes out 1.1 under either rule, and 1.05 → 1.0 comes out 1.1 under half even. **IDENTICAL** for rounding at 15 significant digits and for exact decimal (the control) |
| [dmr_geomean.py](dmr_geomean.py) | When counts' exact geometric mean equals a limit, which side does `exp(mean(log))` land on? | **DIFFERS**: limit 126 gives 4 sets below it; 200 gives 189 above and 792 below; 941 gives 8 above and 3 below; 1,000 gives 50 above and 1,418 below. `[4, 10000]` gives `200.0000000000001` |
| [dmr_calc.py](dmr_calc.py) | Does a spreadsheet get the same cases right? (LibreOffice Calc 24.2.7, board5, 2026-10-29) | **IDENTICAL against half-up; half-even differs.** `ROUND(AVERAGE(...);1)` gives exact half-up on all 1,500 ties. But Calc's `ROUND` rounds half away from zero, so it differs from EPA's half-even examples on 743 of the 1,500. `GEOMEAN` lands a few ulps off the limit internally, as Python does (`RAWSUBTRACT`: 103 sets above 200, 878 below), but Calc's comparisons forgive differences that small, so all 3,737 sets test equal to the limit and none above it |
| [swmm/](swmm/README.md) | Does EPA SWMM give the same bits across threads, compilers, flags, CPUs and operating systems? | See its README. Threads change nothing. FMA contraction and the C library's maths move results past upstream's tolerance. `-ffp-contract=off` plus CORE-MATH gives the same `.out` bits on x86-64 Linux, aarch64 Linux and macOS. crmvec's crpreload gives the shim's bits exactly, so it can replace the shim on Linux (2026-10-30) |
| [wntr/](wntr/README.md) | Does WNTR give the same results on x86-64 and aarch64 Linux? (board5 and cfarm424, 2026-10-29) | See its README. On aarch64 Linux, `pip install wntr` succeeds, but `EpanetSimulator` can't run: WNTR loads its x86-64 EPANET library on every Linux. `WNTRSimulator` isn't repeatable even on one machine, because its equations are ordered by memory address. Net6 fails nrtest's tolerance between runs, so no ISA effect can be seen behind it |
| [bsm1/](bsm1/README.md) | Do QSDsan, WaterTAP and bsm2-python give BSM1's published answer? (cfarm421, 2026-10-29) | See its README. Steady state: bsm2-python matches converged Simulink to 1e-8. QSDsan and WaterTAP depart from BSM1's equations, and once those departures are removed the three meet within 2e-7. The report's own steady state misses a mass balance by 6e-6, and its hosted rain and storm files keep SI undiluted. Dynamic: bsm2-python is first order in its step; QSDsan has one run. Closed loop (bsm2-python): with its PI fix (PR #8), every controller index comes within 10% of the report; without it, the oxygen ISE is 66-72 times the report's |

```sh
python3 checks/dmr_rounding.py --rule half_even
python3 checks/dmr_rounding.py --method sig15
python3 checks/dmr_geomean.py
python3 -I checks/dmr_calc.py            # needs LibreOffice; --plant runs the control
```

**The counts used to depend on the Python version.** Python 3.12's `sum()` uses
compensated summation, and 3.9's adds left to right. The first versions of both checks
used `sum()`, so board5 (Python 3.12) and cfarm104 (3.9) printed different counts. The
cfarm phase found this, and swapping the summation reproduced each machine's numbers on
the other. Both checks now add left to right explicitly, as hand-written code does, and
print the same counts on every Python. Across glibc on x86-64 and aarch64 and macOS's
libm, the geometric-mean counts didn't change: the summation was the only cause.

What these do not show:
- **How often real lab data hits a tie, or an exact limit.** ECHO holds only monthly
  statistics, not daily values, so it can't say.
- **Excel.** `dmr_calc.py` tests LibreOffice Calc, not Excel. Excel's ROUND also rounds
  half away from zero, but its subtraction and comparisons have their own rules, and
  they were not tested.
- **What operators actually type.** A plant's spreadsheet may round with a hand-built
  formula, or not round at all. Calc's half-up `ROUND` is a hazard only where the
  permit or state follows EPA's half-even examples. Which states do is a question for
  [N1](../ideas.md#n1).
