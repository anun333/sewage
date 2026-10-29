# sewage

Open-source software for sewers and wastewater: what exists, what was claimed about it
and what checking found, and where our own work
([fieldmesh](https://github.com/anun333/fieldmesh),
[crnumerics](https://github.com/anun333/crnumerics)) could help, upstream or in a repo of
our own.

Started 2026-10-27 from a chat answer about open-source wastewater software. That answer
is kept verbatim, unchecked, in [thread/2026-10-27-initial.md](thread/2026-10-27-initial.md).

| | |
| --- | --- |
| [landscape.md](landscape.md) | The projects, checked against their own repos and papers on 2026-10-27, each claim in the thread with a verdict, and what the thread missed |
| [ideas.md](ideas.md) | Ways to contribute, upstream and in our repos, each with what it rests on, what would prove it wrong, and the first step |
| [checks/](checks/) | Measurements behind the ideas, rerunnable, with verdict lines |
| [upstream/](upstream/swmm/README.md) | Drafts for other projects, not yet posted: two issues and two patches for SWMM ([swmm/](upstream/swmm/README.md); the first issue posted as pyswmm/Stormwater-Management-Model#431), an issue for WaterTAP ([watertap/](upstream/watertap/README.md), posted as watertap-org/watertap#1892), an issue for EXPOsan ([exposan/](upstream/exposan/README.md), posted as QSD-Group/EXPOsan#80), and two issues for WNTR ([wntr/](upstream/wntr/README.md)) |
| [rules/](rules/README.md) | The laws, standards and terms that bear on this work, checked 2026-10-29, with what each changes |
| [thread/](thread/) | The conversations this started from, verbatim |

## What is here, and what is not

- **Nothing has been built yet.** This is a survey and a list of ideas. The direction,
  as of 2026-10-27, is to contribute to existing projects first, with no idea depending
  on a pilot utility ([ideas.md](ideas.md#the-short-version)).
- **Two measurements**, run 2026-10-27 ([checks/](checks/README.md)):
  - **Rounding.** When an average of decimal lab values lands exactly on a rounding tie,
    rounding the binary64 value reports the wrong digit in 41–46% of ties. That
    includes EPA's own worked example 1.15 → 1.2, which comes out 1.1.
  - **Geometric means.** A geometric mean computed as `exp(mean(log))` can land a few
    ulps above an exact bacteria limit: `[4, 10000]` against 200 gives
    `200.0000000000001`.
  - **The fix.** Exact decimal and integer arithmetic get both right.
- **One experiment, run on board5 2026-10-27:** does EPA SWMM give the same bits
  everywhere ([checks/swmm/](checks/swmm/README.md), [ideas U1](ideas.md#u1))?
  - Thread count doesn't change its results.
  - FMA contraction and glibc's choice of maths code path do, by up to several percent,
    past upstream's own tolerance.
  - `-ffp-contract=off` plus CORE-MATH gives the same `.out` bits on x86-64 Linux,
    aarch64 Linux and macOS (run on cfarm).
  - One report line differs on ARM, because of undefined behaviour in SWMM's C code.
- **A second, run on cfarm 2026-10-29:** do the open implementations of the BSM1
  treatment benchmark give its published answer
  ([checks/bsm1/](checks/bsm1/README.md), [ideas U6](ideas.md#u6))?
  - At steady state they agree with each other within 2e-7, once each
    implementation's departures from BSM1's equations are removed. Those departures
    are candidate fixes upstream.
  - The reference itself has two faults, both shown with numbers.
  - In closed loop, bsm2-python's controllers didn't integrate. With the fix in its PR
    #8, they reproduce the report's controller results within 10%.
- **Statements about other projects** carry the date they were checked. Anything without
  a date is from memory and should be checked before anyone relies on it.

MIT licensed ([LICENSE](LICENSE)), except the material listed in
[THIRD_PARTY.md](THIRD_PARTY.md): 24 values copied from bsm2-python (BSD-3-Clause,
notice included there) and numbers cited from the BSM1 report. The patches in
`upstream/swmm/` change SWMM, which is public domain (EPA) with MIT additions (the
pyswmm fork); our changes in them are also dedicated to the public domain under CC0 1.0,
so either line can take them. Text, code and analysis here were produced with an AI
assistant (Claude), which also ran the builds and checks; the maintainer reads and
approves what is published.
