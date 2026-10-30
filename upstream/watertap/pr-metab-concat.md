<!-- Draft, not posted. Patch: 0001-METAB-model_evaluation-append-rows-with-pd.concat.patch, on WaterTAP main at 1ddf41f. Tested 2026-10-30 by .github/workflows/watertap-metab.yml (run 41112294912). Issue: watertap-org/watertap#1889, "METAB Test Failures" (dallan-keylogic, 2026-10-22; bug, Priority:High; assigned MarcusHolly and luohezhiming; adam-a-a asked two more developers to look on 2026-10-26; no fix proposed as of 2026-10-30, so check again just before opening). The first inventory missed it: check L searched only file and function names, and #1889 names the folder. Found 2026-10-30; check L now searches folders too. To open it: fork watertap-org/watertap to anun333, push the branch, open the PR against main. -->

**Title:** METAB model_evaluation: append rows with pd.concat, so they hold numbers (fixes CI with pandas 3.1)

## Fixes/Resolves:

Fixes #1889. Since pandas 3.1.0 came out on 2026-10-22, five tests in `watertap/flowsheets/METAB/tests/test_model_evaluation.py` fail in CI wherever pip installs it, which is Python 3.11, 3.12 and 3.13, on Linux and Windows, in PRs and on `main`. Python 3.10 gets pandas 2.3.3, where they pass:

```
FAILED watertap/flowsheets/METAB/tests/test_model_evaluation.py::test_get_eff_fr_w_existing_df - pandas.errors.Pandas4Warning: Setting an item of incompatible dtype is deprecated and will raise an error in a future version of pandas.
```

and the same for `test_get_ch4_fr_w_existing_df`, `test_get_h2_fr_w_existing_df`, `test_get_r1_ex_biogas_fr_w_existing_df` and `test_get_mass_flowrate_w_existing_df`.

## Summary/Motivation:

#1889 asks how to handle these failures. This PR fixes the helpers rather than pinning pandas or filtering the warning, because the warning points at a real bug. `get_eff_fr`, `get_ch4_fr`, `get_h2_fr`, `get_r1_ex_biogas_fr` and `get_mass_flowrate` build `fr_dict` with one-element lists (`fr_dict[name] = [value]`). That suits `pd.DataFrame(fr_dict)`, but `df.loc[len(df)] = fr_dict` stores each list itself as the new row's cell, and the columns become `object` dtype. pandas 2.3.3 does this silently; pandas 3.1 warns that it will become an error, and `filterwarnings = error` turns the warning into a failure. The tests had encoded the lists: `assert df.iloc[1]["H2O"] == [100.0]`.

`collect_results` always calls these helpers with `df=None` and accumulates with `pd.concat`, so results from `run_model` aren't affected. Only callers who pass an existing `df` get the lists.

## Changes proposed in this PR:
- `model_evaluation.py`: in the five helpers, `df.loc[len(df)] = fr_dict` becomes `df = pd.concat([df, pd.DataFrame(fr_dict)], ignore_index=True)`.
- `test_model_evaluation.py`: the five `*_w_existing_df` tests check that the appended row is `float64` (`assert (df.dtypes == "float64").all()`), and compare its values with numbers instead of lists.

Tested by running `test_model_evaluation.py` from the source tree, so `pytest.ini` applies, on Ubuntu 24.04 with Python 3.12:

| code | tests | pandas | result |
| --- | --- | --- | --- |
| `main` | `main`'s | 3.1.0 | 5 failed (`Pandas4Warning`), as in CI |
| `main` | this PR's | 2.3.3 | 5 failed: the new dtype check catches the lists without any warning |
| this PR | this PR's | 3.1.0 | 20 passed, 2 skipped |
| this PR | this PR's | 2.3.3 | 20 passed, 2 skipped |

Drafted with an AI assistant (Claude), which also ran the tests reported here; I read it before posting.

### Legal Acknowledgement

By contributing to this software project, I agree to the following terms and conditions for my contribution:

1. I agree my contributions are submitted under the license terms described in the LICENSE.txt file at the top level of this directory.
2. I represent I am authorized to make the contributions and grant the license. If my employer has rights to intellectual property that includes these contributions, I represent that I have received permission to make contributions and grant the required license on behalf of that employer.
