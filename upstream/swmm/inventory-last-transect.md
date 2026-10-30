# Change inventory: ca8b177ff7 against origin/develop (merge base 6c81201589)

Project profile: EPA SWMM (pyswmm fork). 1 files changed, 6 lines added, 0 removed.
PR template: none found; CONTRIBUTORS lists contributors with a licence line.

## I. Where it sits

Control: `src/solver/input.c` is placed in `solver: input parsing` (the profile's first layer, solver: input parsing).

- `src/solver/input.c`: solver: input parsing; 80 entries beside it in `src/solver/`.

## F. Functions the diff changes, and their callers two levels up

Callers are matched by name at the head, tests left out (see N). A method of a common name counts only in files that name its file or class. Check each by reading it.

- `input_readData()` in `src/solver/input.c`: 2 caller(s), 2 outside the diff. Control: 3 line(s) name it.
  - `src/solver/funcs.h` in `(declaration)`
  - `src/solver/project.c` in `project_readInput`; called from `src/solver/swmm5.c`:swmm_open

## T. What should change together (the project's profile)

Control: 5 rules in the profile, 1 triggered by this diff.

- input sections and keywords are listed in several places: 3 file(s) at head, 0 changed by the diff. Not changed: `src/solver/text.h`, `src/solver/keywords.c`, `src/solver/enums.h`.

## S. Shared state: names the diff assigns that other files use


Control: 0 names assigned in changed lines; 0 are locals of the changed C/C++ files (none), left out; 0 of the rest also used outside the diff.

## P. Parallel paths: other files sharing the change's distinctive strings and names

Control: 6 distinctive tokens searched (strings of 6+ characters and their folders, and names of 8+ in the changed and context lines); a token in more than 15 files is too common to count. Files in the change's own language come first.

- `src/solver/keywords.c` (solver: input parsing): shares 2: `TRANSECT`, `s_TRANSECT`
- `src/solver/transect.c` (solver: hydraulics): shares 2: `TRANSECT`, `transect_validate`
- `src/solver/inputrpt.c` (solver: other): shares 1: `TRANSECT`
- `src/solver/link.c` (solver: hydraulics): shares 1: `TRANSECT`
- `src/solver/project.c` (solver: input parsing): shares 1: `TRANSECT`
- `src/solver/report.c` (solver: output and report): shares 1: `ERR_INPUT`
- `src/solver/toolkit.c` (solver: public API): shares 1: `TRANSECT`
- `src/solver/xsect.c` (solver: hydraulics): shares 1: `TRANSECT`
- `src/solver/enums.h` (solver: shared headers): shares 2: `TRANSECT`, `s_TRANSECT`
- `src/solver/error.h` (solver: shared headers): shares 2: `ERR_INPUT`, `TRANSECT`
- `src/solver/text.h` (solver: shared headers): shares 2: `TRANSECT`, `s_TRANSECT`
- `src/solver/funcs.h` (solver: shared headers): shares 1: `transect_validate`

## N. Tests next door

Control: 50 test files at head; the diff changes 0 of them.

- `input`: 1 test file(s): `tests/solver/test_canonical.cpp`
- `input_readData`: no test file names it.

## O. Other open PRs changing the same files, and the same functions

Control: 3 open PRs read.

- #407 (lrntct, updated 2025-03-16): Set the branch feature-2dflood up to date with the main branch. Same files: `src/solver/input.c`; same functions: input_readData.

## L. Open issues that name the changed functions, files or folders

Control: 2 of 2 searches answered (`input_readData`, `input.c`).

- None.

## M. Recent history of the changed files (365 days on the base)

Control: 0 commits on `origin/develop` touched these 1 files in 365 days.


## C. Our draft's references

- `explicit.inp`: not found at head.
- `input.c:213` at the base reads: `transect_validate(Nobjects[TRANSECT]-1);`
- `transects-last.inp`: not found at head.

Control: the planted name `zz_no_such_name_qq` is not found, as it must be. 3 path references (2 not found); 4 backticked names, 0 not found at head.
Names not found may be fine (a PR's new names, other projects', prose in backticks): read each.
