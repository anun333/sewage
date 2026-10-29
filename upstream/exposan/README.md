# upstream/exposan: drafts for QSD-Group/EXPOsan (and QSDsan)

Each draft is read and approved in full before it goes out.

| File | What |
| --- | --- |
| [issue.md](issue.md) | **Posted 2026-10-29 as [#80](https://github.com/QSD-Group/EXPOsan/issues/80).** `exposan.bsm1`'s steady state stands up to 0.7% from BSM1, from the exact constants 20/7 and 32/7 and the exact alkalinity weights. With BSM1's 2.86 and 4.57 it matches bsm2-python to 1e-8, all but alkalinity, whose remaining shift the weights predict exactly. Two dynamic-only differences are also noted: the recycle follows the influent, and the clarifier holds solubles in one volume |

The evidence is in [checks/bsm1/](../../checks/bsm1/README.md).

## Before a PR

- **QSDsan's AI guide** (docs/source/faq/ai_assisted_coding.rst) welcomes Claude Code
  and Codex, and says "You remain responsible for every line you contribute." Disclose,
  and be ready to explain every change.
- **QSDsan's rules:** tests pass, credit goes in the module docstring, no copyleft code,
  and "allow edits from maintainers" stays on ([rules/terms.md](../../rules/terms.md)).
- **The fix is a design choice for the maintainers:** a `bsm1` stoichiometry option, or
  documenting the gap. So the issue goes first.
