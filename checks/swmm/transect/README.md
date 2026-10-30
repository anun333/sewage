# checks/swmm/transect: zero roughness on a transect, and the last transect

What EPA SWMM's engine does with a zero on a transect's NC line, asked in
pyswmm/Stormwater-Management-Model#419 and #420 (and EPA's #217 and #218). Also a bug
found along the way. Run 2026-10-30 on cfarm424 (Debian 13, aarch64, gcc 14.2), with
the pyswmm fork's `develop` at 6c81201 built `-O2 -ffp-contract=off`.

**What the manual says.** The SWMM 5.2 User's Manual, Appendix D.2 (`[TRANSECTS]`,
p. 374), says of Nleft, Nright and Nchanl: "use 0 if no change from previous NC line",
as in HEC-2. Its Nleft entry says "right overbank", a slip for left. Error 227's
description covers only a missing NC line.

**Results** ([check.sh](check.sh); every model has two conduits on two transects, T2
being #420's):

| Question | Models | Result |
| --- | --- | --- |
| Does a zero take the previous transect's value? (#420) | `inherit` against `explicit` | **Yes.** The `.out` files are identical. `control` (T2 at 0.02) differs, so T2's roughness reaches the results |
| Is a zero with nothing to inherit caught? (#419) | `first-zero` | **Yes**, `ERROR 227: Transect T1 has no Manning's N.` The 0.016 in #419 isn't the engine's; perhaps the GUI's (not tested) |
| Does a zero overbank mean "no overbank"? | `overbank-inherit` against `overbank-explicit` and `overbank-none` | **No.** It takes the previous transect's overbank (0.05): identical to `overbank-explicit`, unlike `overbank-none`. SWMM's Help says "The overbank roughness values can be zero if no overbank exists" (quoted by LRossman on EPA's #67), which the engine doesn't do for a transect after one with overbanks |
| Is the last transect read when `[TRANSECTS]` ends the file? | `transects-last` against `explicit` (the same model, sections reordered) | **No.** `ERROR 113: invalid roughness for Conduit C2` and `ERROR 119: invalid cross section for Link C2`. `input_readData()` finishes the last transect only when the next section heading arrives |

**The last-transect fix** ([fixcheck.sh](fixcheck.sh),
[upstream/swmm/0003-*.patch](../../../upstream/swmm/0003-input-read-the-last-transect-when-TRANSECTS-is-the-fi.patch)):
validate the last transect once more after the read loop. With it, `transects-last`
gives `explicit`'s `.out`, and all 34 suite models give the same `.out` and `.rpt`
as without it. Four of them have transects, and all four end with `[LABELS]`.

```sh
sh checks/swmm/transect/check.sh BUILD/bin/runswmm OUTDIR      # any SWMM build
sh checks/swmm/transect/fixcheck.sh WORK                        # after crpreload-job.sh in WORK
```

The drafts for the fork, a comment on #420 and an issue for the last transect, are in
[upstream/swmm/](../../../upstream/swmm/README.md).
