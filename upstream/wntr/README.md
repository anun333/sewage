# upstream/wntr: drafts for USEPA/WNTR

Both issues are posted (2026-10-29). Each draft is read and approved in full before it goes out.

| File | What |
| --- | --- |
| [issue-aarch64.md](issue-aarch64.md) | **Posted as [#584](https://github.com/USEPA/WNTR/issues/584).** On aarch64 Linux, `pip install wntr` succeeds, but `EpanetSimulator` fails: `toolkit.py` loads the x86-64 `libepanet22.so` on every Linux. Same message as #471, different cause |
| [issue-ordering.md](issue-ordering.md) | **Posted as [#585](https://github.com/USEPA/WNTR/issues/585).** `WNTRSimulator` results change from run to run, because the evaluator orders variables and constraints by memory address. On Net6, pump status and metres of pressure change between runs |

The evidence is in [checks/wntr/](../../checks/wntr/README.md).

**Offers to build the fixes**, posted 2026-10-29 after approval:
- [#584](https://github.com/USEPA/WNTR/issues/584#issuecomment-6502234562): a clear
  error from `toolkit.py` when no bundled EPANET matches the platform, or EPANET built
  from source in the sdist;
- [#585](https://github.com/USEPA/WNTR/issues/585#issuecomment-6502235336): evaluator
  ordering by a creation serial number, checked by repeated runs and their test suite.

## The fixes, built and tested (2026-10-30)

Both offers were taken up as builds before any reply, on the maintainer's go. #585's
went in as a review of #586, which makes the same change; #584's is open as #589.

| File | What |
| --- | --- |
| [review-586.md](review-586.md) | **#585's fix was opened by someone else as [#586](https://github.com/USEPA/WNTR/pull/586) on 2026-10-30, the same design.** A review of it instead of our PR: independent x86-64 and aarch64 confirmation, the per-row allocation cost and its fix, the SWIG 4.0.2 check, and why its CI failures are unrelated. **Posted 2026-10-30** ([review](https://github.com/USEPA/WNTR/pull/586#pullrequestreview-5719468594)). (Each of the ten failed jobs read: nine fail the `gis.rst` doctest under pandas 3.1.0, which [#587](https://github.com/USEPA/WNTR/pull/587), opened by a maintainer the same day and merged that evening, fixes; one aborted in a threaded `EpanetSimulator` doctest that passed in #587's run.) **Updated by its author 2026-10-31** (four commits, head `85a54a75b7`): the AML change and its test are byte-identical to the head we reviewed, so the row-vector suggestion isn't taken up. `EN_open` now runs under a lock, after the author traced the threaded doctest's abort to the bundled parser's process-global `strtok` state in `hour()`. The threaded tests now compare results at the solver's 1e-6 tolerance instead of timing, which removes the Windows timing failure; the commit message says Net6 solves differ by several times 1e-8 before the ordering fix. Main (with #587) is merged in. CI on the new head awaits a maintainer's approval. |
| [pr-585.md](pr-585.md), [585-0001-*.patch](585-0001-Order-the-evaluator-s-variables-and-constraints-by-c.patch) | Variables and constraints numbered by creation, each Jacobian row sorted by column. With it, four runs of every network are bit-identical on x86-64 and aarch64 (on `main`, all 41 result variables vary). Test suite: 471 passed against `main`'s 470 (the new test, which fails on `main`). `set_structure()` costs 16% more per call, about 0.25% of a run; Net3, where both take the same path, runs in the same time. SWIG 4.0.2 reproduces the committed wrapper from `main`, and from the fix adds only `serial` accessors. **Superseded:** #586 (someone else's, 2026-10-30) makes the same change, so we reviewed it instead; not to be opened |
| [pr-584.md](pr-584.md), [584-0001-*.patch](584-0001-Name-the-CPU-when-the-Linux-EPANET-library-cannot-lo.patch) | On Linux, a `NotImplementedError` naming the CPU before an EPANET library is loaded on anything but x86-64. On aarch64, all 71 EPANET test failures now say why; x86-64 is unchanged (EPANET results bit-identical, 471 tests passed). Two sentences in the installation requirements. Rebuilt 2026-10-30 on main after #587 (Python files byte-identical to the tested commit). **Posted 2026-10-31 as [#589](https://github.com/USEPA/WNTR/pull/589)**. Its CI was approved on 2026-11-02 and every job failed on `ModuleNotFoundError: No module named 'six'`: python-dateutil 4.0.0 (2026-11-01) stopped installing `six`, which WNTR imported without declaring. [#590](https://github.com/USEPA/WNTR/pull/590) (someone else's) removed `six` from main that evening, but our runs tested the merge into the old main `3edc06c`, and re-runs reuse it. On 2026-11-03 main was merged into the branch (head `91e67c9`, the same patch) and a [comment](https://github.com/USEPA/WNTR/pull/589#issuecomment-6601069831) posted saying why; the new runs await approval. Since #586's update the same day, the two conflict on one line, the imports at the top of `test_epanet_toolkit.py`: #586 adds `from unittest.mock import Mock, patch`, ours `from unittest import mock`, and keeping both resolves it. `toolkit.py` merges cleanly. With both merged, #586's new `test_ENopen_parser_lock` would hit our `NotImplementedError` on aarch64 Linux, where it mocks the library load; WNTR's CI doesn't run there |

The scripts, run on cfarm421 (x86-64) and cfarm424 (aarch64), all Debian 13:
- [fixcheck.sh](fixcheck.sh): builds `main` and both branches, compilers and C++
  standards, CI's test selection, the controls, repeat runs of every network and the
  comparisons (with [checks/wntr/](../../checks/wntr/README.md)'s `wntrrun.py` and
  `wntrcmp.py`);
- [perfcheck.sh](perfcheck.sh): run time and `set_structure()` time, trees alternating
  on one core;
- [swigcheck.sh](swigcheck.sh): the wrapper regenerated with SWIG 4.0.2;
- [v2check.sh](v2check.sh): the same tests for a revised branch, compared with the
  first.

## Seen, not drafted

- **The threaded `EpanetSimulator` doctest can abort.** In #586's quick test (2026-10-30,
  job 124248739600), `advancedsim.rst`'s threaded runs ended in `Fatal Python error:
  Aborted` with three threads inside EPANET at once (`ENopen`, `ENsolveH` and the INP
  writer). The same doctest passed in #587's run that day. No open issue covers it
  (searched 2026-10-30; #431, closed 2024, is about parallel runs). Not reproduced here.
  **#586's author fixed it there on 2026-10-31** (commit `63eb8bb919`): the bundled
  `hour()` parses with `strtok`, whose state is process-global, so `EN_open` now runs
  under a lock while solves stay concurrent. The commit reports the doctest passing 100
  isolated runs and a five-thread reproducer passing 1000.
  [#588](https://github.com/USEPA/WNTR/issues/588), opened 2026-10-31 by someone else, reports
  the case of several processes: `run_sim()`'s default file prefix is `temp`, so processes
  in one directory share `temp.inp`, `.rpt`, `.bin` and `.hyd`, and EPANET fails. The abort
  above was threads in one process; whether `advancedsim.rst`'s threads share a prefix
  isn't checked.

## Before a PR

- **WNTR's PR template requires an AI disclosure section.** It covers the tools used
  and how, plus "I have … reviewed all code for quality assurance, correctness,
  security, and licensing". There are also checkboxes for the Revised BSD licence and
  for authority from an employer ([rules/terms.md](../../rules/terms.md)).
- **The issue templates don't ask about AI;** our disclosure line is on both drafts.
- **For the ordering fix,** the evaluator's sets and `jac_rpn` maps need a stable key,
  such as a creation serial number. That touches WNTR's C++ extension, so the issue
  goes first and the design is theirs to choose.
