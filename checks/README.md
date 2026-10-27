# checks

Measurements behind [../ideas.md](../ideas.md). Each ends in a verdict line, the way
crnumerics' checks do: `IDENTICAL` (exit 0), `DIFFERS` (exit 1), `VOID` (exit 2: a
control failed or nothing was tested). Standard library only.

| Check | Question | Result (board5, cfarm424 and cfarm104 agree, 2026-10-27) |
| --- | --- | --- |
| [dmr_rounding.py](dmr_rounding.py) | When an average of decimal lab values lands on a rounding tie, does rounding the binary64 value give the rule's answer? | **DIFFERS** for the binary value: 41–46% of ties round wrong, under half up and half even alike. EPA's worked example 1.15 → 1.2 comes out 1.1 under either rule, and 1.05 → 1.0 comes out 1.1 under half even. **IDENTICAL** for rounding at 15 significant digits and for exact decimal (the control) |
| [dmr_geomean.py](dmr_geomean.py) | When counts' exact geometric mean equals a limit, which side does `exp(mean(log))` land on? | **DIFFERS**: limit 126 gives 4 sets below it; 200 gives 189 above and 792 below; 941 gives 8 above and 3 below; 1,000 gives 50 above and 1,418 below. `[4, 10000]` gives `200.0000000000001` |
| [swmm/](swmm/README.md) | Does EPA SWMM give the same bits across threads, compilers, flags, CPUs and operating systems? | See its README. Threads change nothing. FMA contraction and the C library's maths move results past upstream's tolerance. `-ffp-contract=off` plus CORE-MATH gives the same `.out` bits on x86-64 Linux, aarch64 Linux and macOS |

```sh
python3 checks/dmr_rounding.py --rule half_even
python3 checks/dmr_rounding.py --method sig15
python3 checks/dmr_geomean.py
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
- **Whether Excel's ROUND and GEOMEAN behave like `sig15`,** which is a stand-in for
  rounding at 15 significant digits, not Excel itself. Nor how Excel adds.
