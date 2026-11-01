<!-- POSTED 2026-10-31 as pyswmm/Stormwater-Management-Model#433 (https://github.com/pyswmm/Stormwater-Management-Model/issues/433), after the full text was approved; title and body read back identical. Was: Draft, not posted. Found 2026-10-30 while checking #419/#420; fix and evidence: upstream/swmm/0003-input-read-the-last-transect-when-TRANSECTS-is-the-fi.patch, checks/swmm/transect/ (check.sh, fixcheck.sh), run on cfarm424 (Debian 13 aarch64, gcc 14.2). Rechecked 2026-10-31: develop still 6c81201, input.c:213 unchanged and the patch's context (line 242) intact; USEPA develop (07c371f8a0) has the same code; no issue on transects since #419/#420 in either repo; swmm-nrtestsuite still e609fdb. -->

**Title:** The last transect is never read when `[TRANSECTS]` is the input file's last section (ERROR 113 and 119 on its conduit)

**Summary**

`input_readData()` finishes each transect when it reaches the next NC line, and the last one when it reaches the next section heading (`input.c:213` on `develop`):

```c
// --- SPECIAL CASE FOR TRANSECTS
//     finish processing the last set of transect data
if ( sect == s_TRANSECT )
    transect_validate(Nobjects[TRANSECT]-1);
```

When `[TRANSECTS]` is the last section of a file, no heading follows it, so `transect_validate()` never runs for the last transect. Its roughness and geometry tables stay empty, and the conduit that uses it fails:

```
ERROR 113: invalid roughness for Conduit C2.
ERROR 119: invalid cross section for Link C2.
```

Both errors point at the conduit, not the transect. Files written by the GUI have more sections after `[TRANSECTS]`, so they aren't affected; the four suite models with transects all end with `[LABELS]`. Hand-written and script-generated files can be.

**Example**

Two models that differ only in section order:
- `explicit.inp`, with `[REPORT]` after `[TRANSECTS]`, runs.
- `transects-last.inp`, the same model with `[TRANSECTS]` moved to the end, stops with the two errors above.

Both are at https://github.com/anun333/sewage/tree/main/checks/swmm/transect.

**A fix:** run the same check once more after the read loop:

```diff
     }   /* End of while */
 
+    // --- SPECIAL CASE FOR TRANSECTS
+    //     finish processing the last set of transect data
+    //     when [TRANSECTS] is the file's last section
+    if ( sect == s_TRANSECT )
+        transect_validate(Nobjects[TRANSECT]-1);
+
     // --- check for errors
     if (errsum > 0)  ErrorCode = ERR_INPUT;
```

With it, `transects-last.inp` gives a `.out` identical to `explicit.inp`'s. All 34 models in swmm-nrtestsuite give identical `.out` and `.rpt` files to the build without it; four of them have transects, and all four end with `[LABELS]`. I'd be glad to open this as a PR if it's useful.

**Environment**
- `develop` at 6c81201, built with gcc 14.2 (`-O2 -ffp-contract=off`), Debian 13 on aarch64. USEPA's `develop` has the same code (`input.c:213`).

Drafted with an AI assistant (Claude), which also ran the checks reported here; I read it before posting.
