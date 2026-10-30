# Change inventory: f96035f74f against origin/main (merge base 1ddf41f067)

Project profile: WaterTAP. 2 files changed, 24 lines added, 19 removed.
PR template: .github/PULL_REQUEST_TEMPLATE.md: Fixes/Resolves; Summary/Motivation; Changes proposed; Legal Acknowledgement.

## I. Where it sits

Control: `watertap/flowsheets/MD/MD_single_stage_continuous_recirculation.py` is placed in `flowsheets` (the profile's first layer, flowsheets).

- `watertap/flowsheets/METAB/model_evaluation.py`: flowsheets; 11 entries beside it in `watertap/flowsheets/METAB/`.
- `watertap/flowsheets/METAB/tests/test_model_evaluation.py`: flowsheets; 6 entries beside it in `watertap/flowsheets/METAB/tests/`.

## F. Functions the diff changes, and their callers two levels up

Callers are matched by name at the head, tests left out (see N). A method of a common name counts only in files that name its file or class. Check each by reading it.

- `get_ch4_fr()` in `watertap/flowsheets/METAB/model_evaluation.py`: 1 caller(s), 0 outside the diff. Control: 6 line(s) name it.
  - `watertap/flowsheets/METAB/model_evaluation.py` in `collect_results`; called from `watertap/flowsheets/METAB/model_evaluation.py`:run_model
- `get_eff_fr()` in `watertap/flowsheets/METAB/model_evaluation.py`: 1 caller(s), 0 outside the diff. Control: 6 line(s) name it.
  - `watertap/flowsheets/METAB/model_evaluation.py` in `collect_results`; called from `watertap/flowsheets/METAB/model_evaluation.py`:run_model
- `get_h2_fr()` in `watertap/flowsheets/METAB/model_evaluation.py`: 1 caller(s), 0 outside the diff. Control: 6 line(s) name it.
  - `watertap/flowsheets/METAB/model_evaluation.py` in `collect_results`; called from `watertap/flowsheets/METAB/model_evaluation.py`:run_model
- `get_mass_flowrate()` in `watertap/flowsheets/METAB/model_evaluation.py`: 1 caller(s), 0 outside the diff. Control: 9 line(s) name it.
  - `watertap/flowsheets/METAB/model_evaluation.py` in `collect_results`; called from `watertap/flowsheets/METAB/model_evaluation.py`:run_model
- `get_r1_ex_biogas_fr()` in `watertap/flowsheets/METAB/model_evaluation.py`: 1 caller(s), 0 outside the diff. Control: 6 line(s) name it.
  - `watertap/flowsheets/METAB/model_evaluation.py` in `collect_results`; called from `watertap/flowsheets/METAB/model_evaluation.py`:run_model
- `test_get_ch4_fr_w_existing_df()` in `watertap/flowsheets/METAB/tests/test_model_evaluation.py`: 0 caller(s), 0 outside the diff. Control: 1 line(s) name it.
- `test_get_eff_fr_w_existing_df()` in `watertap/flowsheets/METAB/tests/test_model_evaluation.py`: 0 caller(s), 0 outside the diff. Control: 1 line(s) name it.
- `test_get_h2_fr_w_existing_df()` in `watertap/flowsheets/METAB/tests/test_model_evaluation.py`: 0 caller(s), 0 outside the diff. Control: 1 line(s) name it.
- `test_get_mass_flowrate_w_existing_df()` in `watertap/flowsheets/METAB/tests/test_model_evaluation.py`: 0 caller(s), 0 outside the diff. Control: 1 line(s) name it.
- `test_get_r1_ex_biogas_fr_w_existing_df()` in `watertap/flowsheets/METAB/tests/test_model_evaluation.py`: 0 caller(s), 0 outside the diff. Control: 1 line(s) name it.

## T. What should change together (the project's profile)

Control: 3 rules in the profile, 2 triggered by this diff.

- the flowsheet's tests pin its results: 6 file(s) at head, 1 changed by the diff. Not changed: `watertap/flowsheets/METAB/tests/test_surrogate_model_generator.py`, `watertap/flowsheets/METAB/tests/test_performance_estimation.py`, `watertap/flowsheets/METAB/tests/test_input_space_generation.py`, `watertap/flowsheets/METAB/tests/test_METAB_ASM1_flowsheet.py` and more.
- flowsheet documentation: 18 file(s) at head, 0 changed by the diff. Not changed: `docs/technical_reference/flowsheets/seawater_RO_desalination.rst`, `docs/technical_reference/flowsheets/oaro.rst`, `docs/technical_reference/flowsheets/mvc.rst`, `docs/technical_reference/flowsheets/membrane_distillation.rst` and more.

## S. Shared state: names the diff assigns that other files use


Control: 1 names assigned in changed lines; 0 are locals of the changed C/C++ files (none), left out; 0 of the rest also used outside the diff.

## P. Parallel paths: other files sharing the change's distinctive strings and names

Control: 9 distinctive tokens searched (strings of 6+ characters and their folders, and names of 8+ in the changed and context lines); a token in more than 15 files is too common to count. Files in the change's own language come first.

- No other file shares them.

## N. Tests next door

Control: 276 test files at head; the diff changes 1 of them.

- `get_ch4_fr`: 1 test file(s): `watertap/flowsheets/METAB/tests/test_model_evaluation.py`
- `get_eff_fr`: 1 test file(s): `watertap/flowsheets/METAB/tests/test_model_evaluation.py`
- `get_h2_fr`: 1 test file(s): `watertap/flowsheets/METAB/tests/test_model_evaluation.py`
- `get_mass_flowrate`: 1 test file(s): `watertap/flowsheets/METAB/tests/test_model_evaluation.py`
- `get_r1_ex_biogas_fr`: 1 test file(s): `watertap/flowsheets/METAB/tests/test_model_evaluation.py`
- `model_evaluation`: 1 test file(s): `watertap/flowsheets/METAB/tests/test_model_evaluation.py`
- `test_get_ch4_fr_w_existing_df`: 1 test file(s): `watertap/flowsheets/METAB/tests/test_model_evaluation.py`
- `test_get_eff_fr_w_existing_df`: 1 test file(s): `watertap/flowsheets/METAB/tests/test_model_evaluation.py`
- `test_get_h2_fr_w_existing_df`: 1 test file(s): `watertap/flowsheets/METAB/tests/test_model_evaluation.py`
- `test_get_mass_flowrate_w_existing_df`: 1 test file(s): `watertap/flowsheets/METAB/tests/test_model_evaluation.py`
- `test_get_r1_ex_biogas_fr_w_existing_df`: 1 test file(s): `watertap/flowsheets/METAB/tests/test_model_evaluation.py`

## O. Other open PRs changing the same files, and the same functions

Control: 29 open PRs read.

- None changes the same files.

## L. Open issues that name the changed functions or files

Control: 7 of 7 searches answered (`get_ch4_fr`, `get_eff_fr`, `get_h2_fr`, `get_mass_flowrate`, `get_r1_ex_biogas_fr`, `test_get_ch4_fr_w_existing_df`, `model_evaluation.py`).

- None.

## M. Recent history of the changed files (365 days on the base)

Control: 1 commits on `origin/main` touched these 1 files in 365 days.

- Who: Morgan Wang (1).
- 30e75917 2026-06-25 Morgan Wang: Add METAB Integration Workflow Tutorial (#1635)

## C. Our draft's references

- `.github/workflows/watertap-metab.yml`: not found at head.
- `LICENSE.txt`: not found at head.

Control: the planted name `zz_no_such_name_qq` is not found, as it must be. 5 path references (2 not found); 18 backticked names, 1 not found at head: `Pandas4Warning`.
Names not found may be fine (a PR's new names, other projects', prose in backticks): read each.
