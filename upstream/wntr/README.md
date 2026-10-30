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

Both offers were taken up as builds before any reply, on the maintainer's go. Neither
is posted; each PR text is ready for review.

| File | What |
| --- | --- |
| [pr-585.md](pr-585.md), [585-0001-*.patch](585-0001-Order-the-evaluator-s-variables-and-constraints-by-c.patch) | Variables and constraints numbered by creation, each Jacobian row sorted by column. With it, four runs of every network are bit-identical on x86-64 and aarch64 (on `main`, all 41 result variables vary). Test suite: 471 passed against `main`'s 470 (the new test, which fails on `main`). `set_structure()` costs 16% more per call, about 0.25% of a run; Net3, where both take the same path, runs in the same time. SWIG 4.0.2 reproduces the committed wrapper from `main`, and from the fix adds only `serial` accessors |
| [pr-584.md](pr-584.md), [584-0001-*.patch](584-0001-Name-the-CPU-when-the-Linux-EPANET-library-cannot-lo.patch) | On Linux, a `NotImplementedError` naming the CPU before an EPANET library is loaded on anything but x86-64. On aarch64, all 71 EPANET test failures now say why; x86-64 is unchanged (EPANET results bit-identical, 471 tests passed). One sentence in the installation requirements |

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

## Before a PR

- **WNTR's PR template requires an AI disclosure section.** It covers the tools used
  and how, plus "I have … reviewed all code for quality assurance, correctness,
  security, and licensing". There are also checkboxes for the Revised BSD licence and
  for authority from an employer ([rules/terms.md](../../rules/terms.md)).
- **The issue templates don't ask about AI;** our disclosure line is on both drafts.
- **For the ordering fix,** the evaluator's sets and `jac_rpn` maps need a stable key,
  such as a creation serial number. That touches WNTR's C++ extension, so the issue
  goes first and the design is theirs to choose.
