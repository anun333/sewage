# Change inventory: 7b2e666a7a against origin/develop (merge base 6c81201589)

Project profile: EPA SWMM (pyswmm fork). 3 files changed, 12 lines added, 2 removed.
PR template: none found; CONTRIBUTORS lists contributors with a licence line.

## I. Where it sits

Control: `src/solver/input.c` is placed in `solver: input parsing` (the profile's first layer, solver: input parsing).

- `CMakeLists.txt`: build; 15 entries beside it in `./`.
- `src/solver/CMakeLists.txt`: solver: other; 80 entries beside it in `src/solver/`.
- `src/solver/gage.c`: solver: hydrology; 80 entries beside it in `src/solver/`.

## F. Functions the diff changes, and their callers two levels up

Callers are matched by name at the head, tests left out (see N). A method of a common name counts only in files that name its file or class. Check each by reading it.

- `gage_validate()` in `src/solver/gage.c`: 2 caller(s), 2 outside the diff. Control: 3 line(s) name it.
  - `src/solver/funcs.h` in `(declaration)`
  - `src/solver/project.c` in `project_validate`; called from `src/solver/swmm5.c`:swmm_open

## T. What should change together (the project's profile)

Control: 5 rules in the profile, 1 triggered by this diff.

- build settings live in the top-level and per-target files: 8 file(s) at head, 0 changed by the diff. Not changed: `tests/solver/CMakeLists.txt`, `tests/shared/CMakeLists.txt`, `tests/outfile/CMakeLists.txt`, `tests/CMakeLists.txt` and more.

## S. Shared state: names the diff assigns that other files use


Control: 1 names assigned in changed lines; 1 are locals of the changed C/C++ files (gageInterval), left out; 0 of the rest also used outside the diff.

## P. Parallel paths: other files sharing the change's distinctive strings and names

Control: 16 distinctive tokens searched (strings of 6+ characters and their folders, and names of 8+ in the changed and context lines); a token in more than 15 files is too common to count. Files in the change's own language come first.

- `src/solver/rdii.c` (solver: hydrology): shares 3: `SECperDAY`, `gageInterval`, `rainInterval`
- `src/solver/inputrpt.c` (solver: other): shares 2: `SECperDAY`, `rainInterval`
- `src/solver/report.c` (solver: output and report): shares 2: `SECperDAY`, `rainInterval`
- `src/solver/infil.c` (solver: hydrology): shares 1: `SECperDAY`
- `src/solver/landuse.c` (solver: quality and treatment): shares 1: `SECperDAY`
- `src/solver/lid.c` (solver: hydrology): shares 1: `SECperDAY`
- `src/solver/lidproc.c` (solver: hydrology): shares 1: `SECperDAY`
- `src/solver/node.c` (solver: hydraulics): shares 1: `SECperDAY`
- `src/solver/project.c` (solver: input parsing): shares 1: `SECperDAY`
- `src/solver/rain.c` (solver: other): shares 1: `rainInterval`
- `src/solver/routing.c` (solver: hydraulics): shares 1: `SECperDAY`
- `src/solver/swmm5.c` (solver: public API): shares 1: `SECperDAY`

## N. Tests next door

Control: 50 test files at head; the diff changes 0 of them.

- `gage`: 1 test file(s): `tests/solver/test_gage.cpp`
- `gage_validate`: no test file names it.

## O. Other open PRs changing the same files, and the same functions

Control: 3 open PRs read.

- #407 (lrntct, updated 2025-03-16): Set the branch feature-2dflood up to date with the main branch. Same files: `CMakeLists.txt`, `src/solver/CMakeLists.txt`, `src/solver/gage.c`; same functions: none seen.

## L. Open issues that name the changed functions or files

Control: 4 of 4 searches answered (`gage_validate`, `CMakeLists.txt`, `CMakeLists.txt`, `gage.c`).

- #431: Results change with FMA contraction and the C library's maths; a build flag makes them reproducible

## M. Recent history of the changed files (365 days on the base)

Control: 1 commits on `origin/develop` touched these 3 files in 365 days.

- Who: michaeltryby (1).
- 813aab6 2026-01-07 michaeltryby: Fussing

## C. Our draft's references

- `gage.c:251` at the base reads: `gageInterval = (int)(floor(Tseries[k].dxMin*SECperDAY + 0.5));`
- `update_v5111/catchment_as_outfall.inp`: not found at head.

Control: the planted name `zz_no_such_name_qq` is not found, as it must be. 3 path references (1 not found); 8 backticked names, 5 not found at head: `NORAIN`, `__STDC_IEC_559__`, `catchment_as_outfall`, `cvttsd2si`, `fcvtzs`.
Names not found may be fine (a PR's new names, other projects', prose in backticks): read each.
