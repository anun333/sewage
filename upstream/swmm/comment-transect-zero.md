<!-- Draft, not posted. A comment for pyswmm/Stormwater-Management-Model#420, with a one-line pointer to it on #419. Checked 2026-10-30 on develop at 6c81201 (gcc -O2 -ffp-contract=off, Debian 13 aarch64, cfarm424) with checks/swmm/transect/check.sh; the SWMM 5.2 User's Manual is EPA/600/R-22/030 (2022), Appendix D.2, p. 374. If the last-transect issue is posted first, replace #NNN with its number. -->

**Comment on #420:**

Some context that may help with this and #419, from the manual, the engine and the earlier discussion on EPA's tracker.

**The behaviour in #420 is documented.** The SWMM 5.2 User's Manual, Appendix D.2 (`[TRANSECTS]`, p. 374), says the same of all three values on an NC line: "use 0 if no change from previous NC line". That follows HEC-2. On USEPA/Stormwater-Management-Model#218, the same report as this one, Mitch Heineman explained that it carries over SWMM 4 Extran's optional C2 roughness line.

**What the engine does** (`develop` at 6c81201). I ran small models with two conduits on two transects, T2 being the one in this issue:
- **T2 inherits.** With `NC 0 0 0` after T1's `NC 0.01 0.01 0.01`, T2 gives a `.out` identical to T2 with `NC 0.01 0.01 0.01`. With `NC 0.02 0.02 0.02` the `.out` differs, so T2's roughness does reach the results.
- **A zero with nothing to inherit is caught.** If the first transect has `NC 0 0 0`, the run stops with `ERROR 227: Transect T1 has no Manning's N.` So the 0.016 in #419 probably comes from the GUI, not the engine. I didn't test the GUI.
- **A zero overbank also inherits.** T1 has overbanks of 0.05 and T2 has `NC 0 0 0.02`. That gives the same `.out` as T2 with `NC 0.05 0.05 0.02`, not as `NC 0.02 0.02 0.02`. SWMM's Help text says "The overbank roughness values can be zero if no overbank exists", as LRossman quoted on USEPA/Stormwater-Management-Model#67. For a transect that follows one with overbanks, that statement and the inheritance can't both hold, so the Help text or the manual may want a line.

If the HEC-2 convention stays, these two issues may come down to documentation. If you'd rather have an error or a warning when a zero inherits, it would need to be optional, because files that rely on the convention are valid input.

While checking this, I found that the last transect in a file is never read when `[TRANSECTS]` is the file's last section; that's #NNN, with a one-line fix.

The models and the script are at https://github.com/anun333/sewage/tree/main/checks/swmm/transect.

Drafted with an AI assistant (Claude), which also ran the checks reported here; I read it before posting.

**Comment on #419:**

A comment on #420 covers this one too: what the engine does with a zero roughness, and why the first transect's zero gives ERROR 227 in the engine.

Drafted with an AI assistant (Claude); I read it before posting.
