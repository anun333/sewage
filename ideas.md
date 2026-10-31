# Ideas: where we could help

Each idea says what it rests on (a link into [landscape.md](landscape.md) or a check), what
would prove it wrong, and the first step. **N** ideas are new work of our own, **U** are
contributions to other people's projects, and **O** extend our own repos. Nothing
outward-facing (an issue, a PR, a review, an email) goes out until the maintainer has read
its full text. What has gone out is listed under each idea and in
[upstream/](upstream/README.md).

## The short version

**Direction, 2026-10-27:** contribute to existing projects first; nothing needs to
be Tennessee-specific; there is no route to a utility, so nothing here may depend on a
pilot.

1. **[U1](#u1): does SWMM give the same bits everywhere? Done 2026-10-27, on board5 and
   cfarm.**
   - Thread count changes nothing.
   - FMA contraction and the C library's maths move results past upstream's own
     tolerance, by up to several percent on some models. Upstream has never named the
     cause.
   - **`-ffp-contract=off` plus a correctly rounded libm (CORE-MATH) gives the same
     `.out` bits on x86-64 Linux, aarch64 Linux and macOS** for every model.
   - One report line still differs on ARM, from undefined behaviour in SWMM's C code.
   - **It reaches users (2026-10-29).** pyswmm's published aarch64 wheel (swmm-toolkit
     0.17.0) is built with FMA and disagrees with the x86-64 wheel on 10 of 34 models.
     The difference is past tolerance on 3: user5's 400.6 against 450.9 cfs again.
   - **Posted 2026-10-29:** pyswmm/Stormwater-Management-Model#431 (these results)
     and #432 (the `.out` header's start date is one report step early in about a
     third of runs whose report start falls on a step).
   - **Ready, not posted:** two patches in [upstream/swmm/](upstream/swmm/README.md),
     the build flag (about 1% slower) and the `gage.c` fix. Both were tested on all
     three platforms, and with them every file matches, reports included (macOS needs
     CORE-MATH as well). They go up as PRs if the fork's maintainers want them.
2. **[U6](#u6): BSM1 checked across its open implementations. Steady state done
   2026-10-29 ([checks/bsm1/](checks/bsm1/README.md)).**
   - Once each implementation's departures from BSM1's equations are removed, all
     three converged answers agree within 2e-7.
   - Each departure is a candidate fix:
     - WaterTAP holds reactor 5's oxygen at 0.449 g/m3, where BSM1's open loop gives 0.491;
     - EXPOsan uses exact constants where BSM1 specifies rounded ones;
     - bsm2-python's rain file doesn't load.
   - The reference has faults of its own: the hosted rain and storm files keep SI
     undiluted, and Appendix 4's steady state isn't quite steady.
   - Dynamic runs are done for bsm2-python and one QSDsan case.
   - **Closed loop (bsm2-python):** its PI controller didn't integrate. With the fix in
     PR #8, every controller index comes within 10% of the report and EQ within 0.6%.
     Our review there is posted (2026-10-29).
   - **Posted 2026-10-29:** WaterTAP's reactor-5 oxygen
     (watertap-org/watertap#1892; a one-line fix is tested and ready if they want it)
     and EXPOsan's constants and atomic weights (QSD-Group/EXPOsan#80).
   - **Drafted, not posted:** bsm2-python's rain file, which doesn't load
     ([upstream/bsm2-python/](upstream/bsm2-python/README.md)), and a note to the
     BSM authors about the reference's two faults ([upstream/bsm/](upstream/bsm/README.md)).
3. **WNTR on two ISAs, checked 2026-10-29 ([checks/wntr/](checks/wntr/README.md)).**
   - On aarch64 Linux, `pip install wntr` succeeds but `EpanetSimulator` can't run:
     WNTR loads its x86-64 EPANET library on every Linux.
   - `WNTRSimulator` isn't repeatable even on one machine, because its equations are
     ordered by memory address. On Net6 runs differ by metres of pressure.
   - **Posted 2026-10-29** as USEPA/WNTR#584 and #585, each with an offer to build the fix.
4. **Reviews of open PRs, posted 2026-10-29** as review comments. They recommend
   merging USEPA SWMM #239, #234 and #237 and bsm2-python #8, and recommend changes to
   USEPA SWMM #226 and EPANET #916 (the latter after building and running it).
5. **Small contributions to learn each community:** a review of the unit errata in
   [mWater's new sanitation asset standard](#u4) is drafted (three points its own
   verification missed). In the [pyswmm ecosystem](#u2), the transect-roughness
   reports turn out to describe documented HEC-2 behaviour, which calls for a comment
   rather than a fix; checking them found a real bug with the last transect, and a
   tested one-line fix. The licence questions are posted:
   PHES-ODM/PHES-ODM#296 ([U5](#u5)) and edgi-govdata-archiving/ECHO_modules#140 ([N2](#n2)).
6. **[N2](#n2): screen plants in EPA's public data, contributed to EDGI's ECHO tools.**
   This is any state or the whole country, not one. It says whether plants fail on
   arithmetic, paperwork or treatment, which decides whether [N1](#n1), DMR statistics
   with every state's rules written down, is worth building. ECHO_modules answered #140
   on 2026-10-29: it is GPL v3, like the rest of EDGI's software, so a screen
   contributed there is GPL v3.
7. **Parked for want of a pilot:** the [lift-station watch](#o1), [bench sheets](#n3)
   and the [fiscal sustainability plan builder](#o7). Each needs a utility willing to
   run it.

## Phase 2: builds (from 2026-10-30)

Phase 1 found faults and reported them. Phase 2 builds: fixes for other projects
first, then tools that carry one project's method into another. The rules don't
change: compute runs on cfarm, every build has a control that must fail, and nothing
goes out until the maintainer has read it.

- **Fixes built and tested, ready to offer as PRs** ([upstream/](upstream/README.md)):
  - WNTR [#585](https://github.com/USEPA/WNTR/issues/585) (the evaluator numbered by
    creation, so runs repeat) and [#584](https://github.com/USEPA/WNTR/issues/584) (an
    error that names the CPU), tested on x86-64 and aarch64;
  - SWMM's build flag and `gage.c` fix (tested 2026-10-27);
  - WaterTAP's reactor-5 oxygen (#1892);
  - ECHO_modules' README licence paragraph, which its maintainer invited.
- **Methods carried across projects:**
  - crnumerics' `repro-scan` and `repro-diff` on each project's own build, as a CI
    step a project could keep. SWMM and WNTR come first, since both showed the effects.
    This waits until a maintainer wants it.
  - The BSM1 comparison ([checks/bsm1/](checks/bsm1/README.md)) as a regression test
    across implementations: each one's steady state against the report, with its
    known departures written down. It would go to whichever project wants it.
  - crmvec's crpreload in place of our own CORE-MATH shim in
    [checks/swmm/](checks/swmm/README.md).
- **Our own libraries, once something needs them:** [N1](#n1)'s exact DMR
  arithmetic, [U3](#u3)'s level-to-flow tables and [U5](#u5)'s RDII fit.

## Lessons carried in from our own repos

- **An earlier sanitation project of ours:** the binding constraint on safe reuse was
  financing and institutions, not knowledge or software, and a premise about a partner fell
  apart once the partner's own materials were read. Here the same risks are real. The
  nation's wastewater need is $345.7 billion of capital, small plants can't hire certified
  operators, and the incumbent tool is a free spreadsheet. Each idea below says which
  constraint it touches.
- **fieldmesh:** no pilot farm means no field claims, and seasons don't reschedule. Every
  operator-side idea needs a utility that will run it, so the ideas that need no pilot
  come first.
- **crnumerics:** every check ends in a verdict, has a control, and is trusted only after
  it catches a planted bug. That method transfers here better than the libraries do (see
  [O6](#o6)).

## New work of our own

<a id="n2"></a>
### N2. Screen plants in ECHO, and contribute the screen to EDGI

- **What.** Read ECHO's DMR and limit files and sort each POTW's violations by kind:
  effluent exceedances (and of what), DMRs not received, reporting errors, and SNC
  (significant noncompliance) episodes. Then sort by plant size and type, with lagoons
  apart. Do one state first, then all of them. Tennessee needs no special place, beyond
  being the one state whose rule text has been read.
- **Size.** The national DMR file is about 0.65 GB zipped per fiscal year (FY2023–FY2025
  measured 2026-10-27). Read the CSVs straight from the zip, without unpacking, and keep
  them on a data disk, not the system disk.
- **Rests on.** ECHO serves every permit's history with violation codes and statistical
  bases ([landscape](landscape.md#electronic-reporting-and-public-data)). EPA calls late or
  faulty DMRs "the single largest source of SNC". Alamo's 156 violations were ammonia and
  chlorine, a treatment problem.
- **What would prove N1 not worth building.** Tennessee's small plants fail mostly on
  treatment (no tool fixes that; capital does) or on DMRs never sent (a people problem),
  with nothing pointing at wrong arithmetic.
- **First step.** Read [EDGI's ECHO_modules](https://github.com/edgi-govdata-archiving/ECHO_modules)
  (GPL-3.0, confirmed by its maintainer in #140) and its open issues. The screen
  should be a contribution there if it fits, and our own script only if it doesn't.

<a id="n1"></a>
### N1. DMR statistics with the rules written down

- **What.** A small library and command (Python, standard library, `decimal` and
  `fractions`) that turns daily lab values into DMR statistics under a named rule
  profile. Each profile is data, and each field in it cites the rule it came from:
  - the week, and which month a split week goes to;
  - what a non-detect counts as;
  - zero and TNTC (too numerous to count) in geometric means;
  - the rounding rule;
  - calendar or consecutive windows.

  Beside it goes a conformance suite: input days, the profile, the expected DMR line, and
  the citation. Any calculator can be run against it, a spreadsheet's export included.
  It ends in a verdict line.
- **Rests on.** The rules really differ ([table](landscape.md#the-numbers-on-a-dmr-and-why-they-differ-between-plants)).
  The public DMR schema carries only the computed statistics, so nobody downstream can
  catch a wrong average. Naive binary arithmetic gets EPA's own worked examples wrong
  ([checks/dmr_rounding.py](checks/dmr_rounding.py)). A float geometric mean can land on
  the wrong side of a limit ([checks/dmr_geomean.py](checks/dmr_geomean.py)).
- **What it must never be:** a submission channel. NetDMR and CROMERR own submission. The
  library prepares numbers and a person files them. It also can't settle a rule the
  permit leaves open; it can only show where profiles disagree.
- **What would prove it wrong.** N2 finds no arithmetic trouble. Or operators say the
  spreadsheet already gets these right, and nobody will change tools for edge cases.
  **Partly answered 2026-10-29 for LibreOffice Calc** ([checks/dmr_calc.py](checks/dmr_calc.py)):
  - its floating point does behave: `ROUND` gets every tie right half-up, and its
    comparisons call every on-limit geometric mean equal to the limit;
  - its `ROUND` is half away from zero, so wherever a permit follows EPA's half-even
    examples, half of all ties print the wrong digit. The risk is in the rule, not the
    arithmetic, which is exactly what N1's profiles are for.
  
  Excel is still unchecked.
- **First step.** Write the EPA example profile and the one state whose rule text has
  been read (Tennessee, 0400-40-05-.02), then Pennsylvania's and Montana's from their
  published instructions. Then write the first twenty test vectors, EPA's worked examples
  among them. A permit's own Part I definitions, which are public in ECHO, settle what a
  state rule leaves open.

<a id="n3"></a>
### N3. Bench sheets on an append-only log *(parked: needs a pilot plant)*

- **What.** Lab entry for BOD, TSS and bacteria. It records the six fields 40 CFR
  122.41(j)(3) requires, and a missed 40 CFR 136 holding time (8 h bacteria, 48 h BOD)
  becomes a quality assertion with provenance. It keeps three years in a verified export
  and feeds N1. Built on fieldmesh's SDK (Apache-2.0), whose observations, quality
  assertions and exports were made for this shape of problem.
- **What would prove it wrong.** Operators won't leave Memphis-style spreadsheets for
  it. It needs a pilot plant, so it comes after N1 and N2.

## Upstream

<a id="u1"></a>
### U1. Does SWMM give the same bits everywhere? *(done 2026-10-27, on board5 and cfarm)*

**Result on board5** (details, commands and controls are in
[checks/swmm/README.md](checks/swmm/README.md)). The build tested was the pyswmm fork
`develop` at `6c81201`, on the 34 models in nrtestsuite v3.3.0.

- **Identical:** every thread count, run-to-run repeat, optimisation level, and gcc
  against clang. SWMM's OpenMP loops have no reductions.
- **What changes the bits:**
  - **FMA contraction** (`-march=native` on x86-64; the default on aarch64 and Apple
    silicon). This takes 9 of the 34 models apart; on user5 a link flow reads 400.6
    against 450.9 cfs.
  - **glibc choosing its FMA or non-FMA `exp`, `log` and `pow` by CPU.** This changes 3
    of the 4 models tried. On Example1 the reported continuity error reads 0.103%
    against 0.109%.
- **Past upstream's tolerance.** Both effects fail nrtest's `rtol 0.01`. Upstream's own
  Linux, macOS and Windows benchmarks fail against each other the same way.
- **The fix.** `-ffp-contract=off` made every x86-64 compiler and flag combination
  identical, and CORE-MATH answering SWMM's 11 maths calls removed the glibc effect.
  Non-FMA builds match upstream's 2023 Linux benchmark on all 33 models compared.
- **Upstream** saw the symptom in pyswmm#203 (2018–2022, closed with no cause found)
  and has never named FMA or libm as the cause.
- **For crnumerics:** `repro-scan` rated every `libswmm5.so` CLEAN and listed the FMAs
  only as info. That's worth feeding back, since the results move by percent.
  Fed back: since crnumerics `beeb69d` (2026-10-29) it flags glibc's CPU-dependent
  maths on x86-64 and names the FMAs in a CLEAN verdict
  ([checks/swmm](checks/swmm/README.md)).

**On cfarm** (cfarm421 EPYC 7773X Debian 13; cfarm424 Neoverse-N1 Debian 13; cfarm104
M1 macOS 26.5; about 0.5 core-hours, every host cleaned afterwards):

| | x86-64 Linux | aarch64 Linux | macOS |
| --- | --- | --- | --- |
| default build | IDENTICAL to board5 (gcc emits no FMA for baseline x86-64) | DIFFERS on 10 models; user5, user1 and Example1 fail upstream's `allclose` | DIFFERS on 10 of 33; the same three fail |
| `-ffp-contract=off` | IDENTICAL | `.out` IDENTICAL on all 34 | DIFFERS on 5; Apple's libm still moves user5 (rel 0.84) |
| `-ffp-contract=off` + CORE-MATH | IDENTICAL to board5's CORE-MATH run | `.out` IDENTICAL on all 34 | `.out` IDENTICAL on all 33 |

- **The FMA builds disagree with each other.** aarch64's and macOS's default builds
  differ on 6 models, so "the macOS answer" and "the Linux answer" aren't two fixed
  references: each compiler fuses differently.
- **The one difference no floating-point setting removes.** catchment_as_outfall's report
  gains a warning on ARM. Its rain gage's series has one point, so its interval stays at
  `BIG` = 1e10 days. `gage.c:251` then casts `floor(8.64e14 + 0.5)` to `int`, which is
  undefined behaviour in C: x86-64 yields INT_MIN, while aarch64 saturates to INT_MAX
  and trips WARNING 09. The fix is a one-line source change.
- **Threads on aarch64** are bit-identical too (1 against 4).
- **Controls.** A planted `pow` error changed results on every host, proving the CORE-MATH
  shim reached SWMM. On macOS, Apple clang turns `pow(10, x)` into `__exp10`, which the
  shim's import check caught (VOID) until it was interposed too.

**Still open:** Windows (`/fp:fast` in Release builds), which wasn't run, and whether
upstream wants bit-reproducibility or only a tolerance that holds. The patches' speed cost
was measured: about 1% ([upstream/swmm/](upstream/swmm/README.md)).

**Where findings go:** the pyswmm fork, which merges. USEPA has merged nothing since 2023.

<a id="u2"></a>
### U2. A first contribution in the pyswmm ecosystem

Most scripted SWMM work runs through pyswmm, swmm-toolkit and swmmio, which are active
and merge outside PRs within days. Approachable open issues as of 2026-10-27:

- **pyswmm:** #606 (expose the LID control type), #258 (document node and conduit
  stats), #279 (warn before overwriting files).
- **The SWMM fork:** #419 and #420 (zero roughness in transects raises no error; a small
  C fix).
- **swmm-python:** #70 (unicode filenames) and #86 (make it citable).

Before opening a PR, run `pr-toolbox landing` and `check` on it, which never comment.

**Checked 2026-10-30: the SWMM fork's #419 and #420.** They aren't the small C fix
they looked like. A zero on a transect's NC line means "no change from previous NC
line", as the SWMM 5.2 manual documents (HEC-2 practice), and the engine does that;
a zero with nothing to inherit already gives Error 227. So a comment fits better than
a fix. The check did turn up a real bug: the last transect is never read when
`[TRANSECTS]` ends the file. A one-line fix is tested and leaves the suite unchanged
([checks/swmm/transect/](checks/swmm/transect/README.md),
[upstream/swmm/](upstream/swmm/README.md)). Both are drafted, not posted.

<a id="u3"></a>
### U3. Level to flow for flumes and weirs

- **The gap.** No maintained open library turns a Parshall flume or V-notch weir level
  into flow, though most small plants measure flow that way.
- **What.** A small library with the published tables, and the uncertainty a level
  error carries into flow and into the monthly flow total.
- **Rests on.** The ISO 9826 and ASTM D1941 standards are paywalled. The USBR *Water
  Measurement Manual* is a US-government work and may carry the tables (unchecked).
- **Where it could also live.** As a computed variable in EnviroDIY's ModularSensors.

<a id="u4"></a>
### U4. Review mWater's sanitation asset standard, then take sewers to Brick

- **mWater.** The [standard](https://github.com/mWater/asset-standards) (CC BY-SA 4.0,
  issued 2026-08-21) is the first open, machine-readable vocabulary for sewer assets.
  Its REVIEW-NEEDED.md lists errata, among them unit-conversion factors that contradict
  the standard's own rule. Checking conversion factors exactly is crnumerics' kind of
  work, and the standard is new enough for a review to matter.
- **Brick.** Brick 1.4.4 has no sewer or wastewater classes, so a Brick extension built
  from mWater's vocabulary (wet well, lift station, force main, manhole) would let
  building and campus models that speak Brick describe their own lift stations.
- **First step.** Read REVIEW-NEEDED.md and check each erratum. Propose nothing until
  the check is done.
- **Checked 2026-10-30.** mWater's own verification report already lists most unit
  defects (S6-S11). Three more, against NIST SP 811 and exact arithmetic: the metric
  water-column units carry conventional values under a 4 °C label; the acre-foot's
  correct value is 1233.482 with the international foot the tables use, not the
  survey-foot 1233.489 the report gives; `hp` = 746 is the electric horsepower. An
  issue is drafted in [upstream/mwater/](upstream/mwater/README.md).

<a id="u6"></a>
### U6. BSM1 across its open implementations

- **What.** Benchmark Simulation Model No. 1 is the treatment model with a published
  reference answer. Run its steady-state and dynamic cases in each open implementation:
  - QSDsan's (through EXPOsan);
  - WaterTAP's;
  - bsm2-python's.

  Compare each against the IWA task group's reference values and against each other.
  This is crnumerics' method: answers the code did not make, controls, and a verdict line.
- **Rests on.** All three are open and active, or were recently (bsm2-python went quiet
  in mid-2025). QSDsan merges outside fixes; an ASM2d fix landed 2026-10-12. WaterTAP has
  two open BSM2 bugs (#1851, #1876).
- **Checked 2026-10-29** ([checks/bsm1/](checks/bsm1/README.md)). The report is a free
  download with no licence stated, so only its numbers are copied. bsm2-python
  matches converged Simulink to 1e-8. QSDsan and WaterTAP match it once their
  departures from BSM1 are removed (constants and alkalinity; reactor 5's oxygen
  and the separator's split). The dynamic comparison is complete for bsm2-python
  (first order in its step) and covers one run for QSDsan.
- **Posted 2026-10-29:** watertap-org/watertap#1892 and QSD-Group/EXPOsan#80, and a
  review of bsm2-python's PI fix (#8). Drafted: bsm2-python's rain file and a note to the
  BSM authors.
- **What would prove it pointless.** All three agree with the reference to the stated
  tolerance. Then the result is a short note to each project saying so, which is worth
  having too.
- **Size.** About 3 GB of Python environments; WaterTAP brings IDAES and its solvers.

<a id="u5"></a>
### U5. Smaller upstream items

- **PHES-ODM's licence conflict.** Its README says CC BY 4.0 while its LICENSE is CC
  BY-SA 4.0. It entered long-term maintenance in September 2026, so a clear issue
  saves them time. Posted 2026-10-29 as PHES-ODM/PHES-ODM#296.
- **WaterTAP's BSM2 bugs.** #1851 (the digester makes no methane) and #1876 (the
  flowsheet is unstable) are numerics problems in the most-used open treatment model.
  They're hard, but they matter. **Checked 2026-10-30
  ([checks/watertap/](checks/watertap/README.md)):**
  - **#1851** has a fix in progress from WaterTAP's developers (#1872), so it was left
    alone.
  - **#1876 is diagnosed.** On Windows, Intel runners fail and AMD runners pass, every
    time, since `865012cd7` changed the feed. The solution washes out the nitrifiers,
    which leaves the solve no margin. A comment is drafted.
  - **Found along the way:** pandas 3.1 has failed five METAB tests in WaterTAP's CI
    since 2026-10-22, from a real bug. WaterTAP tracks it as #1889; our tested fix
    is open as #1893 (2026-10-31).
- **Open RDII analysis.** EPA's SSOAP is deprecated and nothing open replaces it. An
  RTK unit-hydrograph fit on pyswmm and swmmio would fill it. It's medium-sized and
  ties to [O1](#o1)'s inflow from wet-well cycles.
- **Giswater over TEKSI for anything US-facing.** TEKSI is bound to Swiss standards, and
  Giswater isn't (it exports to EPANET and SWMM). Pick Giswater as the base for any US
  asset inventory ([O7](#o7)).
- **Sewer-ML.** The dataset is non-commercial (CC BY-NC-SA), so benchmark work is
  research only. Skip unless a research partner asks.

## Our own repos

<a id="o1"></a>
### O1. A lift-station watch on fieldmesh's SDK *(parked: needs a pilot utility)*

fieldmesh's livestock water monitor already judges a tank's level. A wet well is a tank
that must not fill:

| fieldmesh `water` says | a lift station needs |
| --- | --- |
| **empty**, **low** | **high level**, **high-high** (overflow coming) |
| **not refilling** (float stuck, supply off) | **not pumping down**: pump failed, ragged or air-locked; wet well rising while "running" |
| **unseen** (no reading for half an hour) | the same, and it matters more: no news from a lift station is not good news |
| **untrusted** (a flagged reading) | float switches and the level transducer disagree, the way two soil probes check each other |

What else carries over unchanged:
- **notify** is the on-call callout utilities buy. It escalates through tiers until
  someone answers "on it", by push or by SMS through the plant's own modem.
- **The log's record of who was told, when, and who took it** is the evidence Tennessee's
  24-hour overflow report needs. The 5-day written report's fields (volume, duration,
  location, receiving water) can be prefilled for a person to file through myTDEC.
- **Wet-well cycles are a flow meter.** The fill rate is inflow, and drawdown is pump rate
  less inflow. Logged over months, that gives pump wear and ragging, plus inflow's response
  to rain (RDII). That pairs with [U5](#u5)'s RDII fit and with pump, motor and VFD fault
  diagnostics.
- **The price to beat** is about $47 a station a month (Mission Communications, 2015–16).

**Where it lives.** As a sibling built on fieldmesh's SDK (Apache-2.0), not inside
fieldmesh. fieldmesh is a farm stack, and its governance froze new modules until a pilot
asks for one.

**What would prove it wrong.** Utilities pay the vendor for 24/7 support and cellular
reliability rather than software, or the liability of a missed alarm is more than a small
utility will take on from an open project. Ask a pilot, not the simulator.

**Shares fieldmesh's blocker.** Fieldmesh's build step 7, a real radio and a real driver,
waits on hardware for both projects.

<a id="o2"></a>
### O2. fieldmesh: biosolids and septage on farmland, as an open question

40 CFR 503.32(b)(5) (read from the eCFR's 2026-10-22 issue) sets the waiting periods after
sewage sludge goes on land. Under 503.32(c) the same restrictions cover **domestic septage
spread on farms**:

- 14 months before harvesting crops whose harvested parts touch the soil;
- 20 or 38 months for crops harvested below ground, depending on how long the sludge
  stayed on the surface before it was worked in;
- 30 days for food, feed and fibre crops;
- 30 days before grazing;
- a year of restricted public access on high-exposure land.

fieldmesh already has most of this. `InputApplication` carries `preharvest_interval_days` and
`reentry_interval_h`, and `harvest_problems()` flags a harvest inside an interval, reading
conflicting values cautiously. What it lacks:
- intervals that depend on the crop class and on when the sludge was incorporated;
- a **grazing** interval for paddocks;
- a lifetime **cumulative pollutant loading** per field (503.13). An append-only log is
  the right store for that.

Per fieldmesh's governance this goes in as a numbered open question in
`docs/spec/open-questions.md` for the pilot farm to answer, not as code.

<a id="o4"></a>
### O4. A home for N1 and N3

Both belong in this folder as code once N2 says they are worth it. Use Apache-2.0 for the
library, so a vendor can embed it the way fieldmesh's SDK can be embedded. Use AGPL for
any hosted service, by fieldmesh's reasoning.

<a id="o6"></a>
### O6. crnumerics: where it fits and where it doesn't

| Place | Fit | Why |
| --- | --- | --- |
| DMR averages and rounding | **The method, not the libraries** | The inputs are decimal, so the cure is decimal arithmetic (Python's `decimal`). crsum would give the correctly rounded sum of the binary approximations, which is the wrong quantity. The verdicts, controls and planted bugs are what N1's suite needs |
| Geometric means at a limit | **Its thesis, not its code** | The float formula's side of the limit depends on the C library's `log` and `exp`, so two machines can disagree: crnumerics' subject exactly. The cure is exact integer arithmetic. Run on aarch64 glibc and macOS: the counts depended on Python's summation, not the libm ([checks/](checks/README.md)) |
| SWMM and EPANET | **Yes, measured** | CORE-MATH removed glibc's dispatch effect on SWMM's results (U1). `repro-diff` caught that effect under its older-CPU condition. `repro-scan` rated the libraries CLEAN while their results moved by percent, a finding for crnumerics itself. It now flags glibc's CPU-dependent maths and names FMAs in a CLEAN verdict (`beeb69d`) |
| Sensor nodes | **Speculative** | If fieldmesh's Q20 lets a node send a flow total it computed during an outage, crfix's integer-only, same-bits arithmetic would let the gateway reproduce that total exactly |
| Monte Carlo on SWMM or RDII | **Speculative** | crdist's same-draws-everywhere sampling, if anyone runs uncertainty studies and needs them reproducible |
| crlin, ival | **No fit found** | EPANET's solve is sparse, not dense, and flow from head is monotone, so its enclosure is just the two endpoints |

<a id="o7"></a>
### O7. A fiscal sustainability plan builder *(parked: needs a utility's or SRF office's view)*

The Clean Water SRF's money comes with a fiscal sustainability plan:
- an asset inventory;
- the assets' condition;
- a water and energy conservation check;
- a funded plan for maintenance and replacement.

GAO says small utilities lack the inventories, and EPA's free tool (CUPSS) is abandoned. An
open plan builder on Giswater and mWater's vocabulary could replace it. **But check the
constraint first:** the plan is often a self-certification (Illinois sets no
deadline; Indiana wants it before the last loan payment), so it may be a paperwork step
that blocks nobody. Ask TDEC's SRF office how small borrowers actually meet it before
building anything.

## Where software is not the answer

From [the operator side](landscape.md#the-operator-side):
- **Capital.** $345.7 billion of need. Alamo's ammonia violations need treatment
  upgrades, not a tool.
- **Certified people.** Tennessee requires the person in charge to hold the plant's grade.
- **The rules' authors.** A permit says how to average, and a library can only show where
  permits differ.
- **The spreadsheet.** It is free and already open on the operator's screen. Anything new
  must cost less effort than Excel.

## Decisions

- **2026-10-27:** contribute to existing projects first. Nothing needs to be
  Tennessee-specific. No relationships with utilities, so nothing may depend on a pilot.
- **2026-10-27:** the repo is public, after a scan for names, emails and private paths.
