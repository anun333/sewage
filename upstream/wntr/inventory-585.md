# Change inventory: 726780eee8 against main (merge base 11eec7d5bf)

Project profile: WNTR. 3 files changed, 98 lines added, 20 removed.
PR template: .github/PULL_REQUEST_TEMPLATE.md: Summary; Tests and Documentation; AI Disclosure (checkboxes); Acknowledgement (Revised BSD; AI-generated code reviewed).

## I. Where it sits

Control: `wntr/sim/aml/__init__.py` is placed in `simulation: algebraic modelling (C++ and SWIG)` (the profile's first layer, simulation: algebraic modelling (C++ and SWIG)).

- `wntr/sim/aml/evaluator.cpp`: simulation: algebraic modelling (C++ and SWIG); 9 entries beside it in `wntr/sim/aml/`.
- `wntr/sim/aml/evaluator.hpp`: simulation: algebraic modelling (C++ and SWIG); 9 entries beside it in `wntr/sim/aml/`.
- `wntr/tests/test_aml.py`: tests; 52 entries beside it in `wntr/tests/`.

## F. Functions the diff changes, and their callers two levels up

Callers are matched by name at the head, tests left out (see N). A method of a common name counts only in files that name its file or class. Check each by reading it.

- `Evaluator.add_constraint()` in `wntr/sim/aml/evaluator.cpp`: 3 caller(s), 2 outside the diff. Control: 4 line(s) name it.
  - `wntr/sim/aml/aml.py` in `Model._register_constraint`; called from `wntr/sim/aml/aml.py`:Model.__setattr__, `wntr/sim/aml/aml.py`:ConstraintDict.__setitem__
  - `wntr/sim/aml/evaluator.hpp` in `(declaration)`
  - `wntr/sim/aml/evaluator_wrap.cpp` in `_wrap_Evaluator_add_constraint`
- `Evaluator.add_if_else_constraint()` in `wntr/sim/aml/evaluator.cpp`: 3 caller(s), 2 outside the diff. Control: 4 line(s) name it.
  - `wntr/sim/aml/aml.py` in `Model._register_conditional_constraint`; called from `wntr/sim/aml/aml.py`:Model._register_constraint
  - `wntr/sim/aml/evaluator.hpp` in `(declaration)`
  - `wntr/sim/aml/evaluator_wrap.cpp` in `_wrap_Evaluator_add_if_else_constraint`
- `Evaluator.add_var()` in `wntr/sim/aml/evaluator.cpp`: 3 caller(s), 2 outside the diff. Control: 4 line(s) name it.
  - `wntr/sim/aml/aml.py` in `Model._increment_var`; called from `wntr/sim/aml/aml.py`:Model._register_conditional_constraint, `wntr/sim/aml/aml.py`:Model._register_constraint
  - `wntr/sim/aml/evaluator.hpp` in `(declaration)`
  - `wntr/sim/aml/evaluator_wrap.cpp` in `_wrap_Evaluator_add_var`
- `Evaluator.set_structure()` in `wntr/sim/aml/evaluator.cpp`: 9 caller(s), 4 outside the diff. Control: 19 line(s) name it.
  - `wntr/sim/aml/aml.py` in `Model.set_structure`; called from `wntr/sim/aml/aml.py`:Model.set_structure, `wntr/sim/aml/evaluator.cpp`:Evaluator.evaluate, `wntr/sim/aml/evaluator.cpp`:Evaluator.evaluate_csr_jacobian, `wntr/sim/aml/evaluator.cpp`:Evaluator.get_x, `wntr/sim/aml/evaluator.cpp`:Evaluator.load_var_values_from_x
  - `wntr/sim/aml/evaluator.cpp` in `Evaluator.evaluate`; called from `wntr/sim/aml/aml.py`:Constraint.evaluate, `wntr/sim/aml/aml.py`:Model.evaluate_residuals, `wntr/sim/aml/evaluator.cpp`:_evaluate, `wntr/sim/aml/evaluator.cpp`:Evaluator.evaluate, `wntr/sim/aml/evaluator.cpp`:Evaluator.evaluate_csr_jacobian
  - `wntr/sim/aml/evaluator.cpp` in `Evaluator.evaluate_csr_jacobian`; called from `wntr/sim/aml/aml.py`:Model.evaluate_jacobian, `wntr/sim/aml/evaluator.cpp`:Evaluator.evaluate_csr_jacobian, `wntr/sim/aml/evaluator_wrap.cpp`:_wrap_Evaluator_evaluate_csr_jacobian
  - `wntr/sim/aml/evaluator.cpp` in `Evaluator.get_x`; called from `wntr/sim/aml/aml.py`:Model.get_x, `wntr/sim/aml/evaluator.cpp`:Evaluator.get_x, `wntr/sim/aml/evaluator_wrap.cpp`:_wrap_Evaluator_get_x, `wntr/sim/core.py`:_solver_helper, `wntr/sim/solvers.py`:NewtonSolver.solve
  - `wntr/sim/aml/evaluator.cpp` in `Evaluator.load_var_values_from_x`; called from `wntr/sim/aml/aml.py`:Model.evaluate_jacobian, `wntr/sim/aml/aml.py`:Model.evaluate_residuals, `wntr/sim/aml/aml.py`:Model.load_var_values_from_x, `wntr/sim/aml/evaluator.cpp`:Evaluator.load_var_values_from_x, `wntr/sim/aml/evaluator_wrap.cpp`:_wrap_Evaluator_load_var_values_from_x
  - `wntr/sim/aml/evaluator.hpp` in `(declaration)`
  - `wntr/sim/aml/evaluator_wrap.cpp` in `_wrap_Evaluator_set_structure`
  - `wntr/sim/core.py` in `_solver_helper`; called from `wntr/sim/core.py`:WNTRSimulator.run_sim
- `Evaluator.~Evaluator()` in `wntr/sim/aml/evaluator.cpp`: 1 caller(s), 0 outside the diff. Control: 0 line(s) name it.
  - `wntr/sim/aml/evaluator.hpp` in `(declaration)`
- `TestStructureOrder.test_creation_order()` in `wntr/tests/test_aml.py`: 0 caller(s), 0 outside the diff. Control: 1 line(s) name it.
- `column_less()` in `wntr/sim/aml/evaluator.cpp`: 0 caller(s), 0 outside the diff. Control: 1 line(s) name it.

## T. What should change together (the project's profile)

Control: 5 rules in the profile, 2 triggered by this diff.

- the SWIG interface, its generated wrapper and proxy module come from evaluator.hpp: 3 file(s) at head, 0 changed by the diff. Not changed: `wntr/sim/aml/evaluator_wrap.cpp`, `wntr/sim/aml/evaluator.py`, `wntr/sim/aml/evaluator.i`.
- release notes, written at release by the maintainers: 26 file(s) at head, 0 changed by the diff. Not changed: `documentation/whatsnew/v1.5.0.rst`, `documentation/whatsnew/v1.4.0.rst`, `documentation/whatsnew/v1.3.2.rst`, `documentation/whatsnew/v1.3.1.rst` and more.

## S. Shared state: names the diff assigns that other files use

- `term`: 8 other file(s): `wntr/epanet/msx/enums.py`, `wntr/epanet/msx/exceptions.py`, `wntr/epanet/msx/io.py`, `wntr/msx/base.py`, `wntr/msx/elements.py`, `wntr/msx/model.py` and more

Control: 6 names assigned in changed lines; 4 are locals of the changed C/C++ files (is_structure_set, jac_rpn_iter, max_rpn_size, next_serial), left out; 1 of the rest also used outside the diff.

## P. Parallel paths: other files sharing the change's distinctive strings and names

Control: 36 distinctive tokens searched (strings of 6+ characters and their folders, and names of 8+ in the changed and context lines); a token in more than 15 files is too common to count. Files in the change's own language come first.

- `wntr/sim/aml/evaluator_wrap.cpp` (simulation: algebraic modelling (C++ and SWIG)): shares 6: `IfElseConstraint`, `StructureException`, `add_leaf`, `condition_rpn`, `evaluator.hpp`
- `wntr/sim/aml/aml.py` (simulation: algebraic modelling (C++ and SWIG)): shares 3: `add_leaf`, `condition_rpn`, `evaluate_jacobian`
- `wntr/sim/core.py` (simulation: Python): shares 1: `evaluate_jacobian`
- `wntr/sim/solvers.py` (simulation: Python): shares 1: `evaluate_jacobian`
- `wntr/sim/aml/evaluator.i` (simulation: algebraic modelling (C++ and SWIG)): shares 2: `StructureException`, `evaluator.hpp`
- `documentation/advancedsim.rst` (documentation): shares 1: `evaluate_jacobian`

## N. Tests next door

Control: 113 test files at head; the diff changes 1 of them.

- `Evaluator`: no test file names it.
- `TestStructureOrder`: 1 test file(s): `wntr/tests/test_aml.py`
- `add_constraint`: no test file names it.
- `add_if_else_constraint`: no test file names it.
- `add_var`: no test file names it.
- `column_less`: no test file names it.
- `evaluator`: no test file names it.
- `set_structure`: 1 test file(s): `wntr/tests/test_aml.py`
- `test_creation_order`: 1 test file(s): `wntr/tests/test_aml.py`
- `~Evaluator`: no test file names it.

## O. Other open PRs changing the same files, and the same functions

Control: 9 open PRs read.

- #586 (monocongo, updated 2026-10-30): fix: order AML evaluator variables and constraints by creation serial. Same files: `wntr/sim/aml/evaluator.cpp`, `wntr/sim/aml/evaluator.hpp`, `wntr/tests/test_aml.py`; same functions: none seen.
- #582 (marekl11, updated 2026-10-27): Fix two crashes: unknown AT keyword in INP controls and zero line-sear. Same files: `wntr/tests/test_aml.py`; same functions: none seen.

## L. Open issues that name the changed functions, files or folders

Control: 9 of 9 searches answered (`add_constraint`, `add_if_else_constraint`, `add_var`, `column_less`, `set_structure`, `test_creation_order`, `evaluator.cpp`, `evaluator.hpp`, `aml`).

- #439: Tank Leak Hydraulic Solver Bug
- #584: Linux aarch64: `pip install wntr` succeeds, but EpanetSimulator fails because the x86-64 libepanet22
- #585: WNTRSimulator results change from run to run: the evaluator orders variables and constraints by memo

## M. Recent history of the changed files (365 days on the base)

Control: 0 commits on `main` touched these 2 files in 365 days.


## C. Our draft's references

- `pr-585.md`: not found at head.
- `upstream/inventory.py`: not found at head.

Control: the planted name `zz_no_such_name_qq` is not found, as it must be. 8 path references (2 not found); 16 backticked names, 1 not found at head: `PYTHONHASHSEED`.
Names not found may be fine (a PR's new names, other projects', prose in backticks): read each.
