# Change inventory: d3fc35476b against origin/main (merge base 3edc06c7c4)

Project profile: WNTR. 4 files changed, 41 lines added, 1 removed.
PR template: .github/PULL_REQUEST_TEMPLATE.md: Summary; Tests and Documentation; AI Disclosure (checkboxes); Acknowledgement (Revised BSD; AI-generated code reviewed).

## I. Where it sits

Control: `wntr/sim/aml/__init__.py` is placed in `simulation: algebraic modelling (C++ and SWIG)` (the profile's first layer, simulation: algebraic modelling (C++ and SWIG)).

- `documentation/installation.rst`: documentation; 54 entries beside it in `documentation/`.
- `wntr/epanet/msx/toolkit.py`: EPANET toolkit and I/O; 5 entries beside it in `wntr/epanet/msx/`.
- `wntr/epanet/toolkit.py`: EPANET toolkit and I/O; 7 entries beside it in `wntr/epanet/`.
- `wntr/tests/test_epanet_toolkit.py`: tests; 52 entries beside it in `wntr/tests/`.

## F. Functions the diff changes, and their callers two levels up

Callers are matched by name at the head, tests left out (see N). A method of a common name counts only in files that name its file or class. Check each by reading it.

- `ENepanet.__init__()` in `wntr/epanet/toolkit.py`: 2 caller(s), 1 outside the diff. Control: 162 line(s) name it.
  - `wntr/epanet/toolkit.py` in `runepanet`
  - `wntr/sim/epanet.py` in `EpanetSimulator.run_sim`; called from `examples/fire_flow.py`:(file scope), `examples/getting_started.py`:(file scope), `examples/pipe_criticality.py`:(file scope), `examples/stochastic_simulation.py`:(file scope), `wntr/morph/skel.py`:_Skeletonize.__init__
- `MSXepanet.__init__()` in `wntr/epanet/msx/toolkit.py`: 1 caller(s), 1 outside the diff. Control: 156 line(s) name it.
  - `wntr/sim/epanet.py` in `EpanetSimulator.run_sim`; called from `examples/fire_flow.py`:(file scope), `examples/getting_started.py`:(file scope), `examples/pipe_criticality.py`:(file scope), `examples/stochastic_simulation.py`:(file scope), `wntr/morph/skel.py`:_Skeletonize.__init__
- `TestLinuxMachine.test_non_x86_64_raises()` in `wntr/tests/test_epanet_toolkit.py`: 0 caller(s), 0 outside the diff. Control: 1 line(s) name it.
- `_check_linux_machine()` in `wntr/epanet/toolkit.py`: 2 caller(s), 0 outside the diff. Control: 4 line(s) name it.
  - `wntr/epanet/msx/toolkit.py` in `MSXepanet.__init__`; called from `wntr/sim/epanet.py`:EpanetSimulator.run_sim
  - `wntr/epanet/toolkit.py` in `ENepanet.__init__`; called from `wntr/epanet/toolkit.py`:runepanet, `wntr/sim/epanet.py`:EpanetSimulator.run_sim

## T. What should change together (the project's profile)

Control: 5 rules in the profile, 2 triggered by this diff.

- the MSX toolkit loads EPANET libraries the same way: 1 file(s) at head, 1 changed by the diff.
- release notes, written at release by the maintainers: 26 file(s) at head, 0 changed by the diff. Not changed: `documentation/whatsnew/v1.5.0.rst`, `documentation/whatsnew/v1.4.0.rst`, `documentation/whatsnew/v1.3.2.rst`, `documentation/whatsnew/v1.3.1.rst` and more.

## S. Shared state: names the diff assigns that other files use


Control: 2 names assigned in changed lines; 0 are locals of the changed C/C++ files (none), left out; 0 of the rest also used outside the diff.

## P. Parallel paths: other files sharing the change's distinctive strings and names

Control: 38 distinctive tokens searched (strings of 6+ characters and their folders, and names of 8+ in the changed and context lines); a token in more than 15 files is too common to count. Files in the change's own language come first.

- `wntr/epanet/msx/exceptions.py` (EPANET toolkit and I/O): shares 4: `EpanetMsxException`, `MSXKeyError`, `MSXValueError`, `MSX_ERROR_CODES`
- `wntr/epanet/msx/enums.py` (EPANET toolkit and I/O): shares 2: `TkObjectType`, `TkSourceType`
- `wntr/epanet/msx/io.py` (EPANET toolkit and I/O): shares 2: `EpanetMsxException`, `MSXValueError`
- `wntr/epanet/io.py` (EPANET toolkit and I/O): shares 1: `darwin`
- `wntr/epanet/msx/__init__.py` (EPANET toolkit and I/O): shares 1: `MSXepanet`
- `wntr/metrics/economic.py` (metrics): shares 1: `NotImplementedError`
- `wntr/msx/base.py` (other): shares 1: `NotImplementedError`
- `wntr/network/controls.py` (network model): shares 1: `NotImplementedError`
- `wntr/sim/aml/expr.py` (simulation: algebraic modelling (C++ and SWIG)): shares 1: `NotImplementedError`
- `wntr/sim/epanet.py` (simulation: Python): shares 1: `MSXepanet`
- `wntr/sim/hydraulics.py` (simulation: Python): shares 1: `NotImplementedError`
- `MANIFEST.in` (build and packaging): shares 3: `darwin`, `libepanet/linux-x64`, `libepanet/windows-x64`

## N. Tests next door

Control: 113 test files at head; the diff changes 1 of them.

- `ENepanet`: 1 test file(s): `wntr/tests/test_epanet_toolkit.py`
- `MSXepanet`: 2 test file(s): `wntr/tests/test_epanet_msx_tooklit.py`, `wntr/tests/test_epanet_toolkit.py`
- `TestLinuxMachine`: 1 test file(s): `wntr/tests/test_epanet_toolkit.py`
- `_check_linux_machine`: 1 test file(s): `wntr/tests/test_epanet_toolkit.py`
- `test_non_x86_64_raises`: 1 test file(s): `wntr/tests/test_epanet_toolkit.py`
- `toolkit`: 2 test file(s): `wntr/tests/test_epanet_msx_tooklit.py`, `wntr/tests/test_epanet_toolkit.py`

## O. Other open PRs changing the same files, and the same functions

Control: 8 open PRs read.

- #558 (dbhart, updated 2026-05-15): Update: add enums to toolkit to enable clean error messages. Same files: `wntr/epanet/toolkit.py`, `wntr/tests/test_epanet_toolkit.py`; same functions: none seen.

## L. Open issues that name the changed functions, files or folders

Control: 6 of 6 searches answered (`_check_linux_machine`, `test_non_x86_64_raises`, `installation.rst`, `toolkit.py`, `epanet`, `msx`).

Folders too common to count (more than 10 open issues and PRs name them): `epanet`.

- #75: GPV Setting
- #501: Issue with MSXepanet class
- #584: Linux aarch64: `pip install wntr` succeeds, but EpanetSimulator fails because the x86-64 libepanet22

## M. Recent history of the changed files (365 days on the base)

Control: 6 commits on `origin/main` touched these 3 files in 365 days.

- Who: David Hart (3), Kirk Bonney (2), Katherine Klise (1).
- 3edc06c7 2026-10-30 Katherine Klise: Fix documentation print statement (#587)
- 10b734d4 2026-06-08 Kirk Bonney: Release workflows & cleanup (#560)
- f78bf99c 2026-03-13 Kirk Bonney: Fix pkg_resources deprecation and CI build failures (#552)
- aa358024 2025-11-21 David Hart: Eliminate relative paths in msx library
- e562f05d 2025-11-12 David Hart: Fix pkg_resources deprecation (#544)
- 19cbc014 2025-11-07 David Hart: Update pkg_resources to new mechanism

## C. Our draft's references


Control: the planted name `zz_no_such_name_qq` is not found, as it must be. 5 path references (0 not found); 12 backticked names, 1 not found at head: `OSError`.
Names not found may be fine (a PR's new names, other projects', prose in backticks): read each.
