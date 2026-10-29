# upstream/wntr: drafts for USEPA/WNTR

Both issues are posted (2026-10-29). Each draft is read and approved in full before it goes out.

| File | What |
| --- | --- |
| [issue-aarch64.md](issue-aarch64.md) | **Posted as [#584](https://github.com/USEPA/WNTR/issues/584).** On aarch64 Linux, `pip install wntr` succeeds, but `EpanetSimulator` fails: `toolkit.py` loads the x86-64 `libepanet22.so` on every Linux. Same message as #471, different cause |
| [issue-ordering.md](issue-ordering.md) | **Posted as [#585](https://github.com/USEPA/WNTR/issues/585).** `WNTRSimulator` results change from run to run, because the evaluator orders variables and constraints by memory address. On Net6, pump status and metres of pressure change between runs |

The evidence is in [checks/wntr/](../../checks/wntr/README.md).

## Before a PR

- **WNTR's PR template requires an AI disclosure section.** It covers the tools used
  and how, plus "I have … reviewed all code for quality assurance, correctness,
  security, and licensing". There are also checkboxes for the Revised BSD licence and
  for authority from an employer ([rules/terms.md](../../rules/terms.md)).
- **The issue templates don't ask about AI;** our disclosure line is on both drafts.
- **For the ordering fix,** the evaluator's sets and `jac_rpn` maps need a stable key,
  such as a creation serial number. That touches WNTR's C++ extension, so the issue
  goes first and the design is theirs to choose.
