<!-- DRAFT PR for pyswmm/Stormwater-Management-Model, base develop. Patch: 0001-gage-*.patch. Not opened. -->

**Title:** gage: don't convert a one-point rain series' interval to int

A rain gage that reads a time series with a single point has no recording interval to check. The bug:

- **No interval.** `table_validate` leaves the series' `dxMin` at `BIG`, which is 1e10 days.
- **The cast.** `gage_validate` (gage.c:251) then evaluates `(int)(floor(dxMin*SECperDAY + 0.5))`, converting 8.64e14 to `int`. That is out of range. ISO C leaves the conversion undefined (C17 6.3.1.4p1). Under Annex F, which gcc and clang on glibc claim through `__STDC_IEC_559__`, it raises "invalid" and gives an unspecified value (F.4). So both CPUs below are within the standard, and the result isn't portable.
- **Different results by CPU:**
  - x86-64 (`cvttsd2si`) yields INT_MIN, so neither interval check fires.
  - aarch64 (`fcvtzs`) saturates to INT_MAX, so `rainInterval < gageInterval` holds and the report gains `WARNING 09: time series interval greater than recording interval for Rain Gage 1`.

This shows in swmm-nrtestsuite's `update_v5111/catchment_as_outfall.inp`, whose gage reads the one-point series `NORAIN`. Its report differs between x86-64 and aarch64 builds of the same commit.

**The change.** The interval stays at 0 when `dxMin*SECperDAY` doesn't fit in an `int`, so both checks are skipped as they are on x86-64 today:

```c
gageInterval = 0;
if ( Tseries[k].dxMin * SECperDAY < INT_MAX )
    gageInterval = (int)(floor(Tseries[k].dxMin*SECperDAY + 0.5));
```

**Tested:**
- **x86-64** (gcc 13.3, `-O2`): all 34 models in nrtestsuite v3.3.0 `public/` give the same `.out` and `.rpt` as before.
- **aarch64** (Neoverse-N1, gcc 14.2, and an Apple M1 with Apple clang 21): `catchment_as_outfall`'s report now matches x86-64's byte for byte. Before the fix, both had the WARNING 09 version.

EPA's v5.2.4 has the same line.
