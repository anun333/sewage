# upstream/bsm2-python: drafts for fau-evt/bsm2-python

Our review of its PI-controller fix ([#8](https://github.com/fau-evt/bsm2-python/pull/8)) was posted 2026-10-29. Each draft is read and approved in full before it goes out.

| File | What |
| --- | --- |
| [issue-rain-influent.md](issue-rain-influent.md) | `data/raininfluent.csv` doesn't load: its flow column is written with thousands separators, so three values have two dots and the rest would load 1000 times too small. Not posted |
