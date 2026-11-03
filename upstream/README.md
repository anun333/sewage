# upstream

What has gone to other projects, and what is ready but not sent. Each text was read in
full and approved by the maintainer before it went out, and each carries a line saying an
AI assistant drafted it.

## Before anything goes out: the change's context

[inventory.py](inventory.py) lists the context of one intended change, so that it's proposed
with all of it in view, with a control on each check so that a "none" is a real none. Per-project
settings are in [inventory-profiles.json](inventory-profiles.json):
- **I:** where the changed files sit in the project;
- **F:** the functions changed, and their callers two levels up, across C, C++, SWIG and Python;
- **T:** what the project changes together;
- **S:** shared state other files use;
- **P:** parallel paths, the same strings and names elsewhere;
- **N:** tests next door;
- **O:** other open PRs on the same files and functions;
- **L:** open issues that name them, or the folder they sit in;
- **M:** recent history and its authors;
- **C:** whether our draft's `file:line` references and names exist where it says.

The output for each ready change is saved beside its draft (`inventory-*.md`).

```sh
python3 -I upstream/inventory.py CLONE BRANCH --base origin/main --gh OWNER/REPO --draft upstream/PROJECT/DRAFT.md
```

It has changed three plans:
- **#585.** Its check O found that someone else opened the same fix as USEPA/WNTR#586 on
  2026-10-30, so we review that PR instead of opening our own.
- **#584.** It found #558, a maintainer's PR on the same file. The two merge cleanly
  there, and the PR text now says so.
- **METAB.** Its first version missed WaterTAP's own issue for these failures, #1889,
  which names only the folder ("the METAB flowsheet"). Check L now searches the changed
  files' folders too, and checks L and O say when GitHub didn't answer, so an empty list
  can't be mistaken for a clean one. The PR text now says "Fixes #1889".

Its check P reproduces, unaided, the gap first found by hand in #584 (the MSX loader beside
`toolkit.py`).

## Issues

| Thread | Posted | Subject | State (checked 2026-10-30) |
| --- | --- | --- | --- |
| [pyswmm/Stormwater-Management-Model#431](https://github.com/pyswmm/Stormwater-Management-Model/issues/431) | 2026-10-29 | Results change with FMA contraction and the C library's maths ([swmm/](swmm/README.md)) | No reply |
| [pyswmm/Stormwater-Management-Model#432](https://github.com/pyswmm/Stormwater-Management-Model/issues/432) | 2026-10-29 | The `.out` header's start date is one report step early ([swmm/](swmm/README.md)) | No reply |
| [watertap-org/watertap#1892](https://github.com/watertap-org/watertap/issues/1892) | 2026-10-29 | Reactor 5's oxygen is fixed at 0.449 g/m³ ([watertap/](watertap/README.md)) | Triaged 2026-10-29: three developers assigned, labelled Priority:Normal; no comment yet |
| [QSD-Group/EXPOsan#80](https://github.com/QSD-Group/EXPOsan/issues/80) | 2026-10-29 | BSM1 steady state off by up to 0.7% from exact constants and atomic weights ([exposan/](exposan/README.md)) | No reply |
| [USEPA/WNTR#584](https://github.com/USEPA/WNTR/issues/584) | 2026-10-29 | aarch64 Linux loads the x86-64 EPANET library ([wntr/](wntr/README.md)) | No reply; our offer to build the fix is the one comment |
| [USEPA/WNTR#585](https://github.com/USEPA/WNTR/issues/585) | 2026-10-29 | `WNTRSimulator` results change from run to run ([wntr/](wntr/README.md)) | No reply; our offer to build the fix is the one comment |
| [PHES-ODM/PHES-ODM#296](https://github.com/PHES-ODM/PHES-ODM/issues/296) | 2026-10-29 | LICENSE file against README ([phes-odm/](phes-odm/README.md)) | No reply |
| [edgi-govdata-archiving/ECHO_modules#140](https://github.com/edgi-govdata-archiving/ECHO_modules/issues/140) | 2026-10-29 | LICENSE (GPL-3.0) against README (BSD-3) ([echo-modules/](echo-modules/README.md)) | **Answered** 2026-10-29 by a maintainer: GPL v3 is the licence, and a README fix is welcome |
| [pyswmm/Stormwater-Management-Model#433](https://github.com/pyswmm/Stormwater-Management-Model/issues/433) | 2026-10-31 | The last transect is never read when `[TRANSECTS]` is the file's last section; a one-line fix ([swmm/](swmm/README.md)) | Posted |
| [fau-evt/bsm2-python#9](https://github.com/fau-evt/bsm2-python/issues/9) | 2026-10-31 | `data/raininfluent.csv` doesn't load, and its flows are written with thousands separators ([bsm2-python/](bsm2-python/README.md)) | Posted |
| [mWater/asset-standards#1](https://github.com/mWater/asset-standards/issues/1) | 2026-10-31 | Three more points for the Table 2 units erratum, with exact values ([mwater/](mwater/README.md)) | Posted |

## Reviews

Posted 2026-10-29 as review comments, not as approvals or change requests. The six
reviews of 2026-10-29 left out the AI disclosure line, so each got a short comment about
an hour later: "For transparency, since the review above doesn't say so: it was drafted
with an AI assistant (Claude), which also ran the builds and checks it reports. I read it
before posting." The review of #586 carries the line itself.

| PR | Recommends |
| --- | --- |
| [USEPA/Stormwater-Management-Model#239](https://github.com/USEPA/Stormwater-Management-Model/pull/239) | Merge |
| [USEPA/Stormwater-Management-Model#234](https://github.com/USEPA/Stormwater-Management-Model/pull/234) | Merge |
| [USEPA/Stormwater-Management-Model#237](https://github.com/USEPA/Stormwater-Management-Model/pull/237) | Merge |
| [USEPA/Stormwater-Management-Model#226](https://github.com/USEPA/Stormwater-Management-Model/pull/226) | Changes |
| [OpenWaterAnalytics/EPANET#916](https://github.com/OpenWaterAnalytics/EPANET/pull/916) | Changes, after building and running it. **The author took up every point on 2026-11-02** (head `c242c61`, on `dev` `57d8bd8`) and asked for another look. Re-checked 2026-11-03 on cfarm421 with GCC 14.2 and Clang 19.1: with the option on, all 59 sources get `-fsanitize=undefined`, and the library's 27 also get `-fno-sanitize-recover=all`; the 6 tests pass and `runepanet` reports nothing on 14 `.inp` files. A planted overflow in `EN_createproject()` now fails `test_net_builder`, `test_toolkit` and `test_reent` under both compilers. With the option off, the library gets no `-fsanitize` or `-g`. **Follow-up posted 2026-11-03** ([review](https://github.com/OpenWaterAnalytics/EPANET/pull/916#pullrequestreview-5750496681)), saying so and that we'd be glad to see it merged |
| [fau-evt/bsm2-python#8](https://github.com/fau-evt/bsm2-python/pull/8) | Merge |
| [USEPA/WNTR#586](https://github.com/USEPA/WNTR/pull/586#pullrequestreview-5719468594) (posted 2026-10-30) | Confirms the fix (the one we offered on #585) on x86-64 and aarch64, with one suggestion |

## Comments

| Thread | Posted | Says | State |
| --- | --- | --- | --- |
| [watertap-org/watertap#1876](https://github.com/watertap-org/watertap/issues/1876#issuecomment-6545228017) | 2026-10-31 | Its "random" Windows failures follow the runner's CPU: Intel fails and AMD passes, every time, since `865012cd7`; the solution has nitrifiers washed out, so the solve has no margin ([watertap/comment-1876.md](watertap/comment-1876.md)) | Posted |
| [pyswmm/Stormwater-Management-Model#431](https://github.com/pyswmm/Stormwater-Management-Model/issues/431#issuecomment-6550507709) | 2026-10-31 | The Windows follow-up: `/fp:fast` alone moves 14 models; with CORE-MATH, Windows matches Linux in all 34 files ([swmm/comment-431-windows.md](swmm/comment-431-windows.md)) | Posted |
| [pyswmm/Stormwater-Management-Model#420](https://github.com/pyswmm/Stormwater-Management-Model/issues/420#issuecomment-6550507409), with a pointer on [#419](https://github.com/pyswmm/Stormwater-Management-Model/issues/419#issuecomment-6550507542) | 2026-10-31 | The zero roughness they report is documented HEC-2 behaviour; what the engine does; the overbank case where the Help text disagrees ([swmm/comment-transect-zero.md](swmm/comment-transect-zero.md)). It cites USEPA #218 and #67, which now show a cross-reference | Posted |

## Pull requests

| PR | Opened | Change | State |
| --- | --- | --- | --- |
| [watertap-org/watertap#1893](https://github.com/watertap-org/watertap/pull/1893) | 2026-10-31 | Fixes #1889: the METAB `model_evaluation` helpers append rows with `pd.concat`, so they hold numbers, which ends five CI failures under pandas 3.1 ([watertap/pr-metab-concat.md](watertap/pr-metab-concat.md)) | Open; its CI waits for a maintainer to approve the run (first PR from this account) |
| [edgi-govdata-archiving/ECHO_modules#141](https://github.com/edgi-govdata-archiving/ECHO_modules/pull/141) | 2026-10-31 | Closes #140, as its maintainer invited: the README's licence paragraph says GPL v3 in EDGI's own wording and links to this repository's LICENSE ([echo-modules/pr-readme.md](echo-modules/pr-readme.md)) | **Merged 2026-11-02** by its maintainer, who approved it; #140 closed with it |
| [USEPA/WNTR#589](https://github.com/USEPA/WNTR/pull/589) | 2026-10-31 | Fixes #584: on Linux on anything but x86-64, a `NotImplementedError` naming the CPU instead of a misleading `OSError`, tested on x86-64 and aarch64 ([wntr/pr-584.md](wntr/pr-584.md)) | Open. CI was approved on 2026-11-02 and every job failed, the docs included, on `ModuleNotFoundError: No module named 'six'`. python-dateutil 4.0.0 (2026-11-01) no longer installs `six`, which WNTR imported without declaring; WNTR #590 removed it from main that evening. Our runs tested the merge into the old main `3edc06c`, and re-runs reuse that merge. **2026-11-03:** main merged into the branch (head `91e67c9`, the same change; a rebase's force-push was blocked) and a [comment](https://github.com/USEPA/WNTR/pull/589#issuecomment-6601069831) saying why; the new runs wait for a maintainer's approval |

## Email

- **The BSM1 authors:** a note on the reference's two faults and five smaller slips, sent to
  Ulf Jeppsson, whom IWA-MIA's benchmarking page names as its contact (reported sent
  2026-11-01; [bsm/note-to-authors.md](bsm/note-to-authors.md)).

## Also on upstream timelines

Six of this repo's commit messages named upstream threads as `owner/repo#N`, so GitHub put
"anun333 referenced this" entries, linking here, on WNTR #584 and #586, WaterTAP #1876
and #1892, SWMM #431 (pyswmm) and EXPOsan #80 (2026-10-29 and 30). They can't be removed
without rewriting history. Since 2026-10-30, commit messages write "WNTR PR 586" instead.

## Ready, not sent

- **SWMM:** two patches, the build flag and the `gage.c` fix, with PR texts
  ([swmm/](swmm/README.md)). They go up if the fork's maintainers want them after #431.
  The build patch's MSVC half is now tested on Windows. The #431 follow-up, the #419 and
  #420 comments and #433 have gone out (above).
- **WaterTAP:** a one-line fix for #1892 with its test values, tested; it goes up if the
  maintainers choose that fix ([watertap/](watertap/README.md)). The #1876 comment and the
  METAB fix (#1893) have gone out (above).
