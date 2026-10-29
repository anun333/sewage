# bsm1: do the open implementations of BSM1 give the published answer? (ideas U6)

Benchmark Simulation Model No. 1 is the IWA task group's activated-sludge plant
with a published reference answer: five reactors (two anoxic, three aerated),
ASM1, a ten-layer settler, fixed flows and aeration in open loop. In closed loop,
two PI controllers set the oxygen in reactor 5 and the nitrate in reactor 2. This
check runs the open loop in three open implementations and the closed loop in the
one that has it (bsm2-python), and compares them with the report and with each
other.

The open loop ran on cfarm421 (AMD EPYC 7773X, Debian 13.7, glibc 2.41, Python
3.13.5) on 2026-10-29 between 01:51 and 04:40 UTC. **CPU limit:** at most 16
single-threaded processes at once (`OMP_NUM_THREADS=1` and the like), all at
`nice -n 19`, with a run notice posted while they ran. The closed loop ran later
that day on board5; see [its section](#results-closed-loop-bsm2-python).
The comparison scripts are standard-library Python and run anywhere.

Verdicts follow crnumerics: `IDENTICAL` (exit 0), `DIFFERS` (exit 1), `VOID`
(exit 2: a row was missing or not a number, or a control did not fail).

## The reference

- **The report.** J. Alex, L. Benedetti, J. Copp, K.V. Gernaey, U. Jeppsson,
  I. Nopens, M.-N. Pons, L. Rieger, C. Rosen, J.P. Steyer, P. Vanrolleghem,
  S. Winkler, *Benchmark Simulation Model no. 1 (BSM1)*, Lund University, 2008,
  CODEN LUTEDX/(TEIE-7229)/1-62/(2008), 62 pages.
  - It is a free download, with no registration, at
    https://www2.iea.lth.se/publications/Reports/LTH-IEA-7229.pdf (sha256
    `30828bc11496fb6d9801c1b53c4c62cb27b2274f831938fee4087c14b00e901a`). The address on Lund's research portal,
    `www.iea.lth.se/...`, returned 404 on 2026-10-28; the `www2` host works.
  - **Terms:** the report states no licence. Lund's portal record gives none
    either, under a site-wide "All rights reserved". So the PDF is not copied
    here. Only the numbers are, each with its page.
- **A second copy.** IWA's benchmarking page (http://iwa-mia.org/benchmarking/,
  where www.benchmarkwwtp.org now redirects) hosts a 2018 version,
  `BSM_TG_Tech_Report_no_1_BSM1_General_Description.pdf`. It has 58 pages,
  "Copyright © 2018" the nine named authors, and a "DRAFT" watermark. Its Tables
  6 to 8 print the same numbers as the 2008 report, and so does Appendix 4's
  open loop, all 361 of its numbers. That 2018 version is what WaterTAP and
  bsm2-python cite as "Alex et al. (2018)".
- **[reference.csv](reference.csv)**, 694 rows (`case, block, var, printed,
  unit, source`). `printed` is the number as printed, so its last digit is the
  precision every verdict uses:
  - steady state, open loop, Tables 6 to 8 (pp. 15-16, three digits) and
    Appendix 4 (pp. 39-41, five or six digits; Matlab/Simulink, 27 March 2008):
    the five reactors, the inlet of reactor 1, the settler's underflow,
    effluent and ten layers, and the sludge ages and thickening factors;
  - dynamic, open loop, Appendix 4 (pp. 43-48): days 7-14 of the dry, rain and
    storm files, after 150 days at constant influent and 14 days of dry weather:
    flow-weighted effluent averages, loads, IQ, EQ, sludge production, AE, PE,
    ME, OCI, 95th percentiles and limit violations;
  - Appendix 2 (pp. 33-34): the same dry-weather summary from the FORTRAN
    implementation, to three or four digits. That makes a second published answer;
  - dynamic, closed loop, Appendix 5 (pp. 53-61; Matlab/Simulink, 28 March 2008),
    cases `cl_dry`, `cl_rain` and `cl_storm`: days 7-14 of each file after 150
    days at constant influent and 14 days of dry weather, with the same
    performance rows as the open loop (block `perf`, plus TSS violations where
    printed) and the controllers' indices (block `ctrl`, 24 per case): for each
    loop the error's mean, mean absolute value, IAE, ISE, largest value, std and
    variance, and for its manipulated variable the range, the largest change in
    one sample, the mean, and the std and variance of the changes (see
    [below](#two-findings-about-the-report)). Appendix 5's closed-loop steady
    state (pp. 49-52) is not extracted.

  [refextract.py](refextract.py) rebuilds the file from `pdftotext -layout` of
  the 2008 PDF and gives IDENTICAL.
- **A converged Simulink answer.** bsm2-python's own test,
  `tests/bsm1_ol_test.py` lines 62-114 (BSD-3), holds the BSM2 group's Simulink
  BSM1 open loop after 200 days at constant influent (`bsm1_test_ol.slx`), at full
  precision: the effluent and the ten settler layers.
  [simulink200.csv](simulink200.csv) copies them. Its licence notice (BSD-3-Clause, Copyright (c) 2025, FAU-EVT)
  is in [THIRD_PARTY.md](../../THIRD_PARTY.md).
- **Influent files.** The same IWA page hosts the three weather files, with no
  terms stated, at `http://iwa-mia.org/wp-content/uploads/2019/04/` + file name.
  They are not copied here. Their sha256 values:
  - `Inf_dry_2006.txt`: `2a3776651012d004835870dde73857acec36202efb86ba69f589d6b4fb7601e0`;
  - `Inf_rain_2006.txt`: `c84a4e49d8c0f9bea27a427f528cd00344575c19900c8813eeffb66b0d1f5dd7`;
  - `Inf_strm_2006.txt`: `8e600c737710767da0116283bab5ba567c9b5114c5859faeb7383ed962b72c65`;
  - for the closed loop, the sensor noise `sennoise.zip`:
    `17abad7e4047cb9f269378447c7978174b976d9854616c43d5f66d9d02b047d1`. It holds
    `sennoise.asc` (`227f9cb43df8bf5dd4062fd9e63c32bb35e68b1ed254a925d84999012e14a609`):
    time and 25 noise columns, every minute for 14 days, as the report's
    section 7.3 describes.

  QSDsan ships the dry file as `qsdsan/data/sanunit_data/_inf_dry_2006.tsv`. It
  equals IWA's except one value in the last row (XND 11.814 against 11.81402).
  bsm2-python's `data/dryinfluent.csv` equals it to 1e-8 in time and lacks the
  final row (t = 14).

### What the reference itself gets wrong

1. **Rain and storm SI.** In the IWA-hosted rain and storm files, every
   component is diluted by the extra flow (C_rain = C_dry·Q_dry/Q_rain to
   1.3e-6) except soluble inert COD, which stays at 30 g/m3. The published
   results need SI diluted too:
   - **IQ** depends on the influent only. Over days 7-14 it gives the report's
     52081.3952 for dry weather (every printed digit). With SI = 30·Q_dry/Q it
     gives 52081.3951 for rain (printed 52081.3952; the report's IQ is
     identical for dry and rain, as a pure dilution must be) and 54061.4969 for
     storm (printed 54061.497). The files as hosted give 52253.8005 (+0.33%)
     and 54139.4000 (+0.14%).
   - **Effluent SI**, which only flow and mixing move, comes out at 22.838 and
     26.297 with diluted SI (bsm2-python at 15-second steps). The printed
     values are 22.8388 and 26.2999. The hosted files give 30.000 for both, and
     EQ rises 1.9% (rain) and 0.95% (storm).
   - bsm2-python's `raininfluent.csv` does have SI diluted (= 30·Q_dry/Q to
     its 2 decimals), but the file is broken in other ways; see below.

   Every rain and storm run below uses SI = 30·Q_dry/Q. The other columns are
   as hosted.
2. **Appendix 4's steady state is not steady.** XI is inert: at steady state,
   its inflow Q0·XI0 = 944435.2 g/d must equal its outflow Qe·XIe + Qw·XIu.
   - With Appendix 4's own numbers, the outflow is 944429.43, short by
     6.1e-6. Balancing it with the printed TSS gives XI = 1149.1253 in every
     reactor, against the printed 1149.1182/1149.1183.
   - The Simulink 200-day values close the same balance to 4e-10.
   - Every converged implementation below sits at the balanced value. It
     differs from Appendix 4 by 1e-6 to 1.3e-5 (relative) in the particulates
     (XI, XP, XBA, XBH, TSS) and by under one printed unit in a few solubles
     (for example effluent SNH 1.73333 against 1.7334).
   - The report calls these the values "after 100 days" and does not say where
     the 100 days started. With a slowest time constant near the specific
     sludge age (9.1 days, so exp(-100/9.14) = 1.8e-5), a residual of 6e-6 at
     day 100 fits a start about 30% from steady state. That is an inference, not
     checked.
3. **Small slips.**
   - Table 6 prints reactor 2's TSS as 3282, where Appendix 4's 3282.5339
     rounds to 3283.
   - Table 8 labels the effluent nitrate SNO,u and gives oxygen in g COD/m3.
   - Appendix 2's FORTRAN column gives an effluent flow of 18055.2 against
     Matlab's 18061.33. The flow is Q0 - Qw, so the FORTRAN figures were
     averaged differently.
   - Section 5.1 limits KLa5 to 0-10 1/h (240 1/d), but Appendix 5's
     dry-weather KLa5 spans 242.2831 1/d, which a KLa5 held within 0-240
     cannot do. bsm2-python's limit is 360 1/d (`KLA5_MAX`).
   - Appendix 3 gives the nitrate controller's Tt as 1.015 d, where Appendix 5
     gives 0.015 d. bsm2-python uses 0.015.

## What was run

| implementation | source | how it reaches the answer |
| --- | --- | --- |
| QSDsan + EXPOsan | github.com/QSD-Group/QSDsan `main` `bac88d8fca9d86a01dbfc5694cd4c0fe23f9a259` (2026-10-12, version 1.6.0); github.com/QSD-Group/EXPOsan `main` `84d50344abc089a07bebd38786a833d4fd235cc4` (2026-10-22, 1.6.0; installed with `--no-deps`, since it pins qsdsan==1.5.3); biosteam 2.54.0, thermosteam 0.54.2, scipy 1.18.1, numpy 2.5.4, numba 0.68.1 | `exposan.bsm1` as shipped: ASM1, five CSTRs, `FlatBottomCircularClarifier`. Integrated in time with scipy's BDF. Steady state: 1000 days at rtol = atol = 1e-8 from EXPOsan's default initial state. Dynamic: 300 days at constant influent, then 14 days dry and 14 days of the weather at rtol = atol = 1e-6 (one case again at 1e-8); variants with linear influent and with the internal recycle held constant (`-fixqa`, see below) |
| WaterTAP | github.com/watertap-org/watertap `main` `5909a60409d25944f73d5b9293abf3a6adf21def` (2026-10-01, version 1.9.0.dev0, after the 1.8.0 release); idaes-pse 2.13.0, pyomo 6.10.1, IPOPT 3.13.2 from idaes-ext 3.4.2 (ubuntu2204 build; checksums matched); IPOPT used HSL's MA27 linear solver. HSL, a collection of Fortran codes for large-scale scientific computation. See http://www.hsl.rl.ac.uk | WaterTAP has no BSM1 flowsheet with BSM1's settler. `watertap/flowsheets/activated_sludge/ASM1_flowsheet.py` is BSM1's reactors and flows with a separator for the clarifier (WaterTAP's `Clarifier` is a separator too, with no layers), solved as one steady state by IPOPT (watertap-solvers defaults: tol and constr_viol_tol 1e-8). Its BSM2 flowsheets have a different plant (other volumes, a primary clarifier, a digester) and were not run. No dynamic case |
| bsm2-python | github.com/fau-evt/bsm2-python `main` `73caa8bde193c0dd8a8803dfcd67b546501c950e` (2025-07-20; newer than PyPI's 0.0.16); numba 0.68.1, scipy 1.18.1 | `BSM1OL`: each step integrates every unit separately with scipy's `odeint` (default tolerances) over a fixed step, with the inputs held from the previous step. Steady state: 15-minute steps (as upstream's own steady-state test) for 1000 days from its default initial state. Dynamic: 1-minute steps (upstream's recommendation), 150 days at constant influent, 14 days dry, 14 days of the weather; again at 30- and 15-second steps |

Every source went to the host as a `git archive` tarball and was installed with pip
into its own venv. The stabilization influent is the report's Table 5 (Q 18446,
SS 69.5, XBH 28.17, XS 202.32, XI 51.2, SNH 31.56, SI 30, SND 6.95, XND 10.59,
SALK 7, the rest 0). The KLa values are 240, 240 and 84 1/d in reactors 3-5, Qa
55338, Qr 18446 and Qw 385 m3/d.

The influent goes in two ways, because the implementations differ here:
- **zoh / cubic** is each one's own behaviour. bsm2-python holds each 15-minute
  sample until the next (`bsm1_base.py:215`). QSDsan's `DynamicInfluent` fits a
  periodic cubic spline through them (`unit_operations/dynamic/_influent.py:99`).
- **linear** interpolates between samples. The BSM2 group's Simulink test model
  in bsm2-python, `tests/simulink_files/bsm1_test_ol.slx`, reads its influent
  with `FromWorkspace` blocks whose `Interpolate` is left at its default, on.
  The 2008 Simulink model itself is not public. For bsm2-python, linear means
  feeding the interpolated values at every 1-minute step.

The scripts:
- [run_qsdsan.py](run_qsdsan.py), [run_watertap.py](run_watertap.py) and
  [run_bsm2python.py](run_bsm2python.py) write steady states as `case, block, var,
  value` rows and dynamic runs as 15-minute series;
- [run_bsm2python_cl.py](run_bsm2python_cl.py) does the same for bsm2-python's
  closed loop, with the controllers' signals as extra columns;
- [bsm1kpi.py](bsm1kpi.py) turns a series into the report's indices for days
  7-14 of the weather, and [bsm1clkpi.py](bsm1clkpi.py) adds the closed loop's
  (aeration from the logged KLa values, and the controllers' indices);
- [bsm1cmp.py](bsm1cmp.py) compares with the report or between results;
- [kpitable.py](kpitable.py) tabulates indices;
- [controls.py](controls.py) runs the planted faults;
- [cfarm-job.sh](cfarm-job.sh) and [job1.sh](job1.sh) are the host's job,
  and [setup-envs.sh](setup-envs.sh) built the environments.

The steady states and performance indices are in [results/](results/). The
15-minute series (about 2.5 MB each, 3 MB in closed loop) are not in the repo.
The open-loop ones were archived privately with the logs.

## Results: steady state

Each run against the report to its printed digits: rows AGREE when the result
rounds to the printed value. "Simulink 200 d" is the largest relative difference
from simulink200.csv (effluent and settler, full precision).

| run | Tables 6-8 (3 digits) | Appendix 4 (5-6 digits) | Simulink 200 d |
| --- | --- | --- | --- |
| bsm2-python, 1000 d | 107 of 108 agree | 77 of 126 agree | 1.0e-8 |
| QSDsan as shipped, 1000 d | 86 of 108 | 21 of 126 | 2.7e-3 (effluent SNO) |
| QSDsan with the report's 2.86 and 4.57 | 104 of 108 | 69 of 126 | 2.9e-4 (SALK) |
| WaterTAP as shipped | 35 of 98 | 9 of 115 | 8.5e-2 (SO) |
| WaterTAP, reactor 5 held at 0.491 g/m3 (board5, 2026-10-29) | 86 of 98 | 20 of 115 | 8.4e-4 (effluent XP) |
| WaterTAP, reactor 5 at KLa 3.5 1/h | 87 of 98 | 16 of 115 | 8.4e-4 (effluent XP) |
| WaterTAP, KLa 3.5 1/h, exact flows and the report's settler split | 97 of 98 | 73 of 115 | 1.9e-7 |

- **The row no converged run can match** in Tables 6-8 is Table 6's reactor 2
  TSS, printed 3282 where the answer is 3282.546.
- **What every converged run misses** in Appendix 4 is the reference's own
  shortfall (above): XI, XP, XBA, XBH and TSS, by 1e-6 to 1.3e-5, and a few
  solubles by under one printed unit.
- **WaterTAP** has fewer rows because it has no settler layers.
- **Day 100** changes little. bsm2-python's state at day 100, from its own
  initial state, agrees on 76 of 126 rows of Appendix 4. QSDsan's agrees on 27,
  WaterTAP has no time. The report's initial state is not given, so day 100
  can't be reproduced.

Between runs at full precision (`bsm1cmp.py pair`), the largest relative
difference:

| A vs B | rows | largest difference |
| --- | --- | --- |
| bsm2-python vs WaterTAP (exact flows, report's split) | 115 | 1.8e-7 (effluent XBH; the split carries the report's six printed digits) |
| bsm2-python vs QSDsan as shipped | 126 | 7.0e-3 (reactor 2 SNO 3.6620 vs 3.6362) |
| bsm2-python vs QSDsan with 2.86 and 4.57 | 126 | 2.9e-4 (SALK, 8 rows); every other row within 1.1e-8 |
| bsm2-python 1000 d vs its day 100 | 126 | 1.9e-6 (reactor 5 SNH): converged long before day 1000 |

The solvers agree with each other far better than with the printed reference:
- bsm2-python steps `odeint`;
- QSDsan integrates with BDF;
- WaterTAP solves the steady state directly with IPOPT.

Once the model differences below are removed, they meet within 1e-7.

### Why each differs

- **bsm2-python**: nothing to explain. Its converged state is Simulink's to
  1e-8. It uses BSM2's temperature-dependent ASM1 (`bsm2/asm1_bsm2.py`), which
  at the 15 °C of every BSM1 input reduces to BSM1's constants; its oxygen
  saturation evaluates to 8.0000000000066.
- **QSDsan** differs from BSM1's equations in two places. With the first
  removed, every row except alkalinity matches bsm2-python to 1.1e-8; the
  second accounts for the alkalinity rows (computed below, not run):
  1. **Stoichiometric constants.** EXPOsan's `exposan/bsm1/data/_asm1.tsv`
     line 3 uses `7/20*(Y_H-1)/Y_H` for nitrate in anoxic growth (20/7 =
     2.857, where the report's equation has 2.86). Line 4 uses
     `(Y_A-32/7)/Y_A` for oxygen in autotrophic growth (32/7 = 4.571, report
     4.57). QSDsan's own `qsdsan/data/process_data/_asm1.tsv` has the same.
     These are the exact values, chosen so that COD balances. But BSM1
     specifies the rounded ones, and they move effluent nitrate by -0.27%,
     oxygen by -0.15%, ammonia by +0.16% and reactor 2's nitrate by -0.70%.
     `run_qsdsan.py ss ... bsm1` swaps them, and every row except SALK then
     matches.
  2. **Alkalinity.** QSDsan derives the alkalinity coefficients from a charge
     balance, so they are not written in the table. It uses exact atomic
     weights: S_ALK is HCO3- at 1/12.0107 charge per g C, and nitrate and
     ammonium are 1/14.0067 per g N. BSM1's equations divide by 14, and its
     inputs (EXPOsan writes 7 mol/m3 as 7*12 = 84 g C/m3) use 12. So every
     alkalinity change is 14/14.0067 · 12.0107/12 = 1.000413 times BSM1's.
     That gives effluent SALK 4.12439 against 4.12558. The predicted shift,
     (7 - 4.12558)(f - 1) = 0.0011868 with f = 1.000413, is the observed
     0.0011868 to every digit shown.

  QSDsan's clarifier also keeps solubles in one mixed volume
  (`qsdsan/unit_operations/dynamic/_clarifier.py:553`) where BSM1 has ten
  layers. That doesn't change a steady state.
- **WaterTAP**'s `ASM1_flowsheet.py` is not BSM1's open loop, in three ways:
  1. **Reactor 5's oxygen is fixed** at 4.49e-4 kg/m3 (line 216). That is
     0.449 g/m3, where the report's open loop has KLa 3.5 1/h, which gives
     0.491.
     - The fix is deliberate: line 312 says "S_O concentration is controlled
       in R5". But 0.449 is not the closed loop's setpoint either, which is
       2 g/m3 (the report's Appendix 4, "DOsetpoint=2mg/l").
     - Reactors 3 and 4 start at 1.72e-3 and 2.43e-3 (lines 214-215), the
       report's Table 6 values, before lines 313-316 switch them to KLa
       10 1/h.
     - Where 0.449 comes from isn't stated. It is not a transposition of 0.491;
       an earlier version of this README guessed that, wrongly. The same four
       lines, R5 at 4.49e-4 included, appear in WaterTAP's BSM2, METAB-BSM1 and
       ASM2d flowsheets (checked 2026-10-29).
     - Fixing R5 at 4.91e-4 instead (`run_watertap.py` case `ss_r5fix`, run on
       board5 2026-10-29) agrees with Tables 6-8 on 86 of 98 rows, against 87
       for KLa 3.5 1/h and 35 as shipped.

     The test file accepts the result: `test_asm1_flowsheet.py` lines 79-89 and
     123-133 accept S_O 0.449 ("slightly off, but probably due to differences
     in injection rates"), SNO 10.14 and SNH 1.86 ("slightly off in last
     significant digit") at rel 1e-2. The report has 10.4 and 1.73, which are
     -2.6% and +7.3% away. Aerating reactor 5 with KLa 3.5 1/h, like reactors
     3 and 4, brings SO to 0.49095, SNO to 10.4149 and SNH to 1.7345.
  2. **The clarifier is a separator** with split fractions rounded to five
     decimals: lines 223-236 give 0.48956 and 0.00187, and line 239 gives
     0.97955 for the recycle.
     The wastage then comes out at 385.1 instead of 385. With exact flows and
     the split the report's own settler reaches, it matches the converged
     answer to 1.8e-7.
  3. The flowsheet runs at 298.15 K, which changes nothing: its ASM1
     parameters carry no temperature dependence.

  That the clarifier is a placeholder is said in the code: line 104, "TODO:
  Replace with more detailed model when available", and line 222, "TODO: Update
  once more detailed model available".

## Results: dynamic open loop (days 7-14)

Each run: 150 days (bsm2-python) or 300 days (QSDsan) at constant influent,
14 days of dry weather, then 14 days of the weather file. The indices cover days
7-14 of the last file, from 15-minute samples.

Against the report's printed digits almost nothing agrees, in any run. IQ, AE,
PE and ME do, because they follow from the inputs alone. bsm2-python agrees on
5 to 12 of 58 rows, and QSDsan's one finished run on 6. So the comparison is in
relative differences.

The two published implementations already disagree at this level. For dry
weather, Appendix 2's FORTRAN differs from Appendix 4's Matlab by +0.74% in
effluent ammonia, +0.15% in EQ, +0.40% in the ammonia 95th percentile, and its
violation time is 0.5761 against 0.57292 days.

Only one QSDsan dynamic run finished: linear influent, constant recycle, dry
weather, 1 h 41 min of BDF at rtol 1e-6. The other nine were stopped
unfinished, so QSDsan's rain, storm, cubic and proportional-recycle cases are
not reported. The tables below come from `kpitable.py` over
[results/](results/).

**Dry weather.** bsm2-python with linear influent at three steps and with each sample held (its default), and QSDsan's one finished run. Each cell is the value and its relative difference from Appendix 4.

| index | report (Matlab) | report (FORTRAN) | bsm2-python 1 min | 30 s | 15 s | 1 min, held | QSDsan, fixed Qa |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EQ | 6690.1066 | 6700 | 6719.59 (+4.4e-03) | 6705.51 (+2.3e-03) | 6698.48 (+1.3e-03) | 6732.56 (+6.3e-03) | 6738.95 (+7.3e-03) |
| IQ | 52081.3952 | 52100 | 52081.4 (-8.8e-10) | 52081.4 (-8.8e-10) | 52081.4 (-8.8e-10) | 52081.4 (-8.8e-10) | 52081.4 (-8.8e-10) |
| SNH_e | 4.7589 | 4.794 | 4.82074 (+1.3e-02) | 4.79116 (+6.8e-03) | 4.77637 (+3.7e-03) | 4.84057 (+1.7e-02) | 4.84993 (+1.9e-02) |
| TN_e | 15.5686 | 15.58 | 15.609 (+2.6e-03) | 15.5897 (+1.4e-03) | 15.58 (+7.3e-04) | 15.6282 (+3.8e-03) | 15.6638 (+6.1e-03) |
| TSS_e | 12.9917 | 12.99 | 12.9841 (-5.8e-04) | 12.988 (-2.8e-04) | 12.99 (-1.3e-04) | 13.0059 (+1.1e-03) | 12.9918 (+4.2e-06) |
| COD_e | 48.2958 | 48.30 | 48.2882 (-1.6e-04) | 48.2922 (-7.5e-05) | 48.2942 (-3.3e-05) | 48.3177 (+4.5e-04) | 48.2919 (-8.1e-05) |
| SI_e | 30 | 30. | 30 (-5.2e-14) | 30 (-8.1e-14) | 30 (-1.3e-13) | 30 (-5.2e-14) | 30 (+1.2e-16) |
| SP_disposal | 2435.6901 | 2436 | 2432.77 (-1.2e-03) | 2434.57 (-4.6e-04) | 2435.47 (-8.9e-05) | 2433.32 (-9.7e-04) | 2436.24 (+2.3e-04) |
| OCI | 16148.0073 | 16150 | 16133.4 (-9.0e-04) | 16142.4 (-3.5e-04) | 16146.9 (-6.7e-05) | 16136.2 (-7.3e-04) | 16150.8 (+1.7e-04) |
| SNH_e95 | 8.8818 | 8.9175 | 8.98665 (+1.2e-02) | 8.92638 (+5.0e-03) | 8.90609 (+2.7e-03) | 9.01076 (+1.5e-02) | 7.8094 (-1.2e-01) |
| TN_e95 | 18.5332 | 18.535 | 18.6063 (+3.9e-03) | 18.581 (+2.6e-03) | 18.5591 (+1.4e-03) | 18.6203 (+4.7e-03) | 17.672 (-4.6e-02) |
| TSS_e95 | 15.7415 | 15.8 | 15.708 (-2.1e-03) | 15.7281 (-8.5e-04) | 15.7382 (-2.1e-04) | 15.7045 (-2.4e-03) | 15.7477 (+3.9e-04) |
| SNH_viol_days | 4.375 | 4.403 | 4.375 (+0.0e+00) | 4.375 (+0.0e+00) | 4.375 (+0.0e+00) | 4.39583 (+4.8e-03) | 4.04167 (-7.6e-02) |
| TN_viol_days | 0.57292 | 0.5761 | 0.59375 (+3.6e-02) | 0.583333 (+1.8e-02) | 0.572917 (-5.8e-06) | 0.604167 (+5.5e-02) | 0.0625 (-8.9e-01) |

**Rain**, bsm2-python only, with SI diluted except in the "hosted SI" column.

| index | report (Matlab) | 1 min | 30 s | 15 s | 1 min, held | 1 min, hosted SI |
| --- | --- | --- | --- | --- | --- | --- |
| EQ | 8951.3288 | 8981.08 (+3.3e-03) | 8959.16 (+8.7e-04) | 8948.23 (-3.5e-04) | 8997.04 (+5.1e-03) | 9151.66 (+2.2e-02) |
| IQ | 52081.3952 | 52081.4 (-1.1e-09) | 52081.4 (-1.1e-09) | 52081.4 (-1.1e-09) | 52081.4 (-1.1e-09) | 52253.8 (+3.3e-03) |
| SNH_e | 5.0085 | 5.05649 (+9.6e-03) | 5.02078 (+2.5e-03) | 5.00297 (-1.1e-03) | 5.07621 (+1.4e-02) | 5.05649 (+9.6e-03) |
| TN_e | 14.3394 | 14.3701 (+2.1e-03) | 14.3476 (+5.7e-04) | 14.3364 (-2.1e-04) | 14.3854 (+3.2e-03) | 14.3701 (+2.1e-03) |
| TSS_e | 16.1579 | 16.1473 (-6.5e-04) | 16.1553 (-1.6e-04) | 16.1593 (+8.4e-05) | 16.1683 (+6.4e-04) | 16.1473 (-6.5e-04) |
| COD_e | 45.5175 | 45.5038 (-3.0e-04) | 45.514 (-7.8e-05) | 45.5191 (+3.5e-05) | 45.5245 (+1.5e-04) | 52.6683 (+1.6e-01) |
| SI_e | 22.8388 | 22.8354 (-1.5e-04) | 22.8371 (-7.5e-05) | 22.8379 (-3.8e-05) | 22.827 (-5.2e-04) | 30 (+3.1e-01) |
| SP_disposal | 2353.0104 | 2346.33 (-2.8e-03) | 2349.74 (-1.4e-03) | 2351.45 (-6.6e-04) | 2346.85 (-2.6e-03) | 2346.33 (-2.8e-03) |
| OCI | 15734.6089 | 15701.2 (-2.1e-03) | 15718.2 (-1.0e-03) | 15726.8 (-4.9e-04) | 15703.8 (-2.0e-03) | 15701.2 (-2.1e-03) |
| SNH_e95 | 9.4978 | 9.59882 (+1.1e-02) | 9.53506 (+3.9e-03) | 9.503 (+5.5e-04) | 9.62502 (+1.3e-02) | 9.59882 (+1.1e-02) |
| TN_e95 | 17.8121 | 17.8394 (+1.5e-03) | 17.8188 (+3.8e-04) | 17.8056 (-3.7e-04) | 17.9523 (+7.9e-03) | 17.8394 (+1.5e-03) |
| TSS_e95 | 21.6824 | 21.6599 (-1.0e-03) | 21.6746 (-3.6e-04) | 21.6821 (-1.4e-05) | 21.7549 (+3.3e-03) | 21.6599 (-1.0e-03) |
| SNH_viol_days | 4.4375 | 4.47917 (+9.4e-03) | 4.44792 (+2.3e-03) | 4.4375 (+0.0e+00) | 4.46875 (+7.0e-03) | 4.47917 (+9.4e-03) |
| TN_viol_days | 0.32292 | 0.333333 (+3.2e-02) | 0.333333 (+3.2e-02) | 0.333333 (+3.2e-02) | 0.322917 (-1.0e-05) | 0.333333 (+3.2e-02) |

**Storm**, bsm2-python only, with SI diluted except in the "hosted SI" column.

| index | report (Matlab) | 1 min | 30 s | 15 s | 1 min, held | 1 min, hosted SI |
| --- | --- | --- | --- | --- | --- | --- |
| EQ | 8197.7197 | 8064.52 (-1.6e-02) | 8044.19 (-1.9e-02) | 8034.06 (-2.0e-02) | 8071.9 (-1.5e-02) | 8141.22 (-6.9e-03) |
| IQ | 54061.497 | 54061.5 (-1.4e-09) | 54061.5 (-1.4e-09) | 54061.5 (-1.4e-09) | 54061.5 (-1.4e-09) | 54139.4 (+1.4e-03) |
| SNH_e | 5.681 | 5.42903 (-4.4e-02) | 5.39107 (-5.1e-02) | 5.37212 (-5.4e-02) | 5.43838 (-4.3e-02) | 5.42903 (-4.4e-02) |
| TN_e | 15.326 | 15.1595 (-1.1e-02) | 15.1345 (-1.2e-02) | 15.122 (-1.3e-02) | 15.1641 (-1.1e-02) | 15.1595 (-1.1e-02) |
| TSS_e | 15.1739 | 15.2391 (+4.3e-03) | 15.2478 (+4.9e-03) | 15.2524 (+5.2e-03) | 15.2625 (+5.8e-03) | 15.2391 (+4.3e-03) |
| COD_e | 47.6511 | 47.7239 (+1.5e-03) | 47.7394 (+1.9e-03) | 47.7474 (+2.0e-03) | 47.7247 (+1.5e-03) | 51.4368 (+7.9e-02) |
| SI_e | 26.2999 | 26.2871 (-4.9e-04) | 26.2934 (-2.5e-04) | 26.2966 (-1.3e-04) | 26.2548 (-1.7e-03) | 30 (+1.4e-01) |
| SP_disposal | 2607.4907 | 2587.06 (-7.8e-03) | 2593.49 (-5.4e-03) | 2596.74 (-4.1e-03) | 2588.29 (-7.4e-03) | 2587.06 (-7.8e-03) |
| OCI | 17007.0104 | 16904.9 (-6.0e-03) | 16937 (-4.1e-03) | 16953.2 (-3.2e-03) | 16911 (-5.6e-03) | 16904.9 (-6.0e-03) |
| SNH_e95 | 10.1872 | 9.89165 (-2.9e-02) | 9.83688 (-3.4e-02) | 9.81197 (-3.7e-02) | 9.91902 (-2.6e-02) | 9.89165 (-2.9e-02) |
| TN_e95 | 18.9449 | 18.7825 (-8.6e-03) | 18.7438 (-1.1e-02) | 18.7325 (-1.1e-02) | 18.8362 (-5.7e-03) | 18.7825 (-8.6e-03) |
| TSS_e95 | 20.7485 | 20.7775 (+1.4e-03) | 20.7816 (+1.6e-03) | 20.7837 (+1.7e-03) | 20.7489 (+1.7e-05) | 20.7775 (+1.4e-03) |
| SNH_viol_days | 4.625 | 4.55208 (-1.6e-02) | 4.53125 (-2.0e-02) | 4.52083 (-2.3e-02) | 4.54167 (-1.8e-02) | 4.55208 (-1.6e-02) |
| TN_viol_days | 0.64583 | 0.604167 (-6.5e-02) | 0.59375 (-8.1e-02) | 0.59375 (-8.1e-02) | 0.614583 (-4.8e-02) | 0.604167 (-6.5e-02) |

### Why they differ

- **bsm2-python's step is not converged.** `BSM1OL` integrates each unit
  separately over the step and feeds each the others' outputs from the step
  before (`bsm1_base.py` `step()`). That is first order in the step:
  - every index's distance from its zero-step limit halves when the step halves
    (the ratio of successive differences is 2.00 for EQ, effluent ammonia, TN,
    TSS and sludge production, at 1 min, 30 s and 15 s);
  - at the documented 1-minute step, dry-weather EQ is 0.44% above the report
    and effluent ammonia 1.3%;
  - extrapolated to zero step, dry weather lands within 2e-4 of Matlab: EQ
    6691.44 against 6690.1066, ammonia 4.7616 against 4.7589, TSS 12.9920
    against 12.9917, sludge 2436.38 against 2435.6901.
  - The steady state is unaffected (a fixed point), which is why it matches
    Simulink to 1e-8.
- **Rain and storm keep a gap after that.**
  - Extrapolated to zero step, rain is -0.16% in EQ and -0.47% in effluent
    ammonia; its sludge production (+0.007%) and OCI agree.
  - Storm is -2.1% in EQ and -5.8% in ammonia, and halving the step moves it
    further from the report.
  - Effluent SI, which only flow and mixing move, converges to the report in
    both (to 4e-5 at 15 s). So the hydraulics and the SI correction are
    right.
  - The gap is in the nitrogen during high flows. IQ cannot see an exchange
    between SNH and SND in the influent (both count as Kjeldahl nitrogen), so
    a difference of that kind between the hosted files and the report's would
    pass the IQ check. That is a guess, not shown.
- **Influent interpolation.** In bsm2-python, holding each sample (its default)
  instead of interpolating raises dry-weather EQ by 0.19% and effluent
  ammonia by 0.41%; for storm the shift is 0.09%.
- **QSDsan (the one finished run, dry, linear influent, recycle held at 55338).**
  - Flow-weighted averages are close to the report: EQ +0.73%, effluent
    ammonia +1.9%, TSS +4e-6, sludge +2.3e-4.
  - The peaks are not. The ammonia 95th percentile is 7.81 against 8.88, TN's
    is 17.67 against 18.53, and the TN violation time is 0.06 against 0.57
    days.
  - Settler and effluent solids track bsm2-python's to about 0.1%. The
    effluent solubles do not: ammonia ranges 0.66-8.33 against 0.38-9.81.
  - The likely cause is QSDsan keeping the clarifier's solubles in one mixed
    volume (`_clarifier.py:553`), which damps the daily cycle more than BSM1's
    ten layers do. That is inferred from the series, not isolated by a run.
- **QSDsan's internal recycle** follows the influent flow: `CSTR.split` is
  normalized to fractions (`_bioreactor.py:267`), so EXPOsan's
  `split=[Q_intr, Q+Q_ras]` (`exposan/bsm1/system.py:274`) gives Qa = 1.5(Q0 +
  Qr) instead of a constant 55338. `run_qsdsan.py` `fixed_recycle` holds it
  constant. The runs measuring its effect did not finish.

## Results: closed loop (bsm2-python)

Appendix 5 gives the closed loop. One PI controller holds reactor 5's oxygen at
2 g/m3 by moving KLa5, and another holds reactor 2's nitrate at 1 g N/m3 by
moving the internal recycle (Qintr, the Qa above). Each reads its tank through a
sensor model with noise. The protocol is the open loop's: 150 days at constant
influent, 14 days of dry weather and 14 days of the weather file, with indices
over days 7-14 from 15-minute samples. Of the three implementations, only
bsm2-python has this closed loop (`BSM1CL`). EXPOsan's `exposan/bsm1/README.rst`
offers only an idealized oxygen target and lists PI control as future work, and
WaterTAP has no dynamic BSM1 (both at the commits above).

This part comes from our review of bsm2-python's pull request #8, "Preserve PI
integral and anti-windup state between controller steps", which fixes its issue
#7. The review is posted:
https://github.com/fau-evt/bsm2-python/pull/8#pullrequestreview-5698022419.

**What was run.** `BSM1CL` from `main` (`73caa8bde193c0dd8a8803dfcd67b546501c950e`,
as in the open loop) and from the pull request's head
(`e929c48d747539594eb8f6f59a4c07ec97572396`), with
[run_bsm2python_cl.py](run_bsm2python_cl.py) at 1-minute steps, in two
configurations:
- **The report's** (`report`, the class `ReportCL`), for dry, rain and storm.
  It keeps BSM1CL's own sensor, PID and actuator classes, gains, limits and
  order of operations, and changes three settings to the report's:
  - KLa3 = KLa4 = 240 1/d;
  - the nitrate sensor's range is 0-20 g N/m3;
  - the noise comes from columns 1 (oxygen) and 2 (nitrate) of `sennoise.asc`,
    restarted with each 14-day file and off during the 150 days.

  The influent is interpolated linearly, with SI diluted for rain and storm, as
  in the open loop's linear runs.
- **As shipped** (`shipped`), dry weather only: BSM1CL unchanged, each influent
  sample held.

The runs were made on board5 (AMD Ryzen 5 PRO 5650U, x86-64, Ubuntu 24.04,
Python 3.12.3; packages in [results/versions.txt](results/versions.txt))
on 2026-10-29 between 11:12 and 12:22 UTC. One single-threaded process ran at a
time, on at most 4 of the machine's 12 threads. A 178-day run (256,321 steps)
took 324-423 s in the report's configuration and 782-1014 s as shipped
([results/runs_bsm2python_cl.txt](results/runs_bsm2python_cl.txt) has each
run's line).

Those eight runs were made with the review's own driver, which
run_bsm2python_cl.py replaces. The script reproduces them byte for byte:
- two were rerun at full length, the report's configuration (dry, the pull
  request; 486 s) and as shipped (dry, main; 769 s), side by side;
- so were five runs at 15-minute steps: the three [below](#15-minute-steps),
  and both branches as shipped (14-19 s each).

Each new series was identical to the original. The indices are
[bsm1clkpi.py](bsm1clkpi.py)'s, in [results/](results/) as
`kpi_bsm2python_cl_<configuration>_<weather>_<branch>.csv` (`pr8` is the pull
request). The tables come from `kpitable.py`.

Against Appendix 5's printed digits almost nothing agrees, as in the open loop:
2 to 6 of 82 rows (85 for storm). So each cell is the value and its relative
difference from Appendix 5.

**Dry weather**, in the report's configuration and as shipped.

| index | report (Matlab) | main | PR #8 | shipped, main | shipped, PR #8 |
| --- | --- | --- | --- | --- | --- |
| SO5_IAE | 0.58831 | 5.52429 (+8.4e+00) | 0.5612 (-4.6e-02) | 5.49319 (+8.3e+00) | 0.542834 (-7.7e-02) |
| SO5_ISE | 0.083975 | 6.00686 (+7.1e+01) | 0.0757918 (-9.7e-02) | 5.43309 (+6.4e+01) | 0.0712613 (-1.5e-01) |
| SO5_err_max | 0.39631 | 1.89016 (+3.8e+00) | 0.361805 (-8.7e-02) | 1.80252 (+3.5e+00) | 0.392568 (-9.4e-03) |
| SO5_err_std | 0.10953 | 0.917953 (+7.4e+00) | 0.104053 (-5.0e-02) | 0.873414 (+7.0e+00) | 0.100895 (-7.9e-02) |
| KLa5_mean | 144.1219 | 139.852 (-3.0e-02) | 144.306 (+1.3e-03) | 147.604 (+2.4e-02) | 160.099 (+1.1e-01) |
| KLa5_dstd | 9.5682 | 6.70863 (-3.0e-01) | 11.7854 (+2.3e-01) | 6.55955 (-3.1e-01) | 11.6626 (+2.2e-01) |
| SNO2_IAE | 1.4348 | 3.81622 (+1.7e+00) | 1.50406 (+4.8e-02) | 3.93284 (+1.7e+00) | 1.43921 (+3.1e-03) |
| SNO2_ISE | 0.56897 | 2.87715 (+4.1e+00) | 0.598415 (+5.2e-02) | 2.79991 (+3.9e+00) | 0.593032 (+4.2e-02) |
| SNO2_err_max | 0.91782 | 1.3589 (+4.8e-01) | 0.92096 (+3.4e-03) | 1.20572 (+3.1e-01) | 0.88998 (-3.0e-02) |
| SNO2_err_std | 0.28509 | 0.63704 (+1.2e+00) | 0.292268 (+2.5e-02) | 0.625335 (+1.2e+00) | 0.29106 (+2.1e-02) |
| Qintr_mean | 18610.0822 | 17476.8 (-6.1e-02) | 18575.8 (-1.8e-03) | 19343.9 (+3.9e-02) | 22348.9 (+2.0e-01) |
| Qintr_dstd | 4078.4756 | 4064.07 (-3.5e-03) | 4258.44 (+4.4e-02) | 2323.82 (-4.3e-01) | 2611.92 (-3.6e-01) |
| EQ | 6123.0182 | 6214.06 (+1.5e-02) | 6150.61 (+4.5e-03) | 6535.61 (+6.7e-02) | 6358.26 (+3.8e-02) |
| SNH_e | 2.5392 | 2.65303 (+4.5e-02) | 2.55268 (+5.3e-03) | 3.58425 (+4.1e-01) | 3.27556 (+2.9e-01) |
| TN_e | 16.9245 | 17.0936 (+1.0e-02) | 16.9337 (+5.4e-04) | 16.8995 (-1.5e-03) | 16.5429 (-2.3e-02) |
| TSS_e | 13.0038 | 13.0044 (+4.4e-05) | 13.0105 (+5.2e-04) | 13.0301 (+2.0e-03) | 13.0384 (+2.7e-03) |
| SP_disposal | 2440.6057 | 2441.28 (+2.8e-04) | 2446.64 (+2.5e-03) | 2440.32 (-1.2e-04) | 2447.44 (+2.8e-03) |
| AE | 3698.3438 | 3672.28 (-7.0e-03) | 3698.67 (+8.7e-05) | 3259.67 (-1.2e-01) | 3333.69 (-9.9e-02) |
| PE | 241.0305 | 236.725 (-1.8e-02) | 241.121 (+3.8e-04) | 244.194 (+1.3e-02) | 256.213 (+6.3e-02) |
| OCI | 16382.4027 | 16355.4 (-1.6e-03) | 16413 (+1.9e-03) | 15945.4 (-2.7e-02) | 16067.1 (-1.9e-02) |
| SNH_e95 | 7.3902 | 7.25785 (-1.8e-02) | 7.38143 (-1.2e-03) | 8.34749 (+1.3e-01) | 8.32771 (+1.3e-01) |
| TN_e95 | 20.2693 | 20.4619 (+9.5e-03) | 20.256 (-6.6e-04) | 20.2636 (-2.8e-04) | 19.9216 (-1.7e-02) |
| SNH_viol_days | 1.1979 | 1.38542 (+1.6e-01) | 1.20833 (+8.7e-03) | 2.91667 (+1.4e+00) | 2.07292 (+7.3e-01) |
| TN_viol_days | 1.2813 | 1.33333 (+4.1e-02) | 1.26042 (-1.6e-02) | 1.10417 (-1.4e-01) | 0.96875 (-2.4e-01) |

**Rain**, in the report's configuration.

| index | report (Matlab) | main | PR #8 |
| --- | --- | --- | --- |
| SO5_IAE | 0.55672 | 4.73702 (+7.5e+00) | 0.531321 (-4.6e-02) |
| SO5_ISE | 0.074733 | 4.92277 (+6.5e+01) | 0.0676463 (-9.5e-02) |
| SO5_err_max | 0.38505 | 1.89016 (+3.9e+00) | 0.357173 (-7.2e-02) |
| SO5_err_std | 0.10332 | 0.82759 (+7.0e+00) | 0.0983014 (-4.9e-02) |
| KLa5_mean | 139.5768 | 139.482 (-6.8e-04) | 139.717 (+1.0e-03) |
| KLa5_dstd | 9.2235 | 6.51566 (-2.9e-01) | 11.1153 (+2.1e-01) |
| SNO2_IAE | 1.7349 | 4.2307 (+1.4e+00) | 1.79819 (+3.6e-02) |
| SNO2_ISE | 0.79436 | 3.4239 (+3.3e+00) | 0.827644 (+4.2e-02) |
| SNO2_err_max | 0.92134 | 1.38749 (+5.1e-01) | 0.926389 (+5.5e-03) |
| SNO2_err_std | 0.33686 | 0.688616 (+1.0e+00) | 0.343853 (+2.1e-02) |
| Qintr_mean | 29608.9372 | 19189.5 (-3.5e-01) | 29584.5 (-8.2e-04) |
| Qintr_dstd | 4110.5486 | 3836.12 (-6.7e-02) | 4309.51 (+4.8e-02) |
| EQ | 8184.7263 | 8405.36 (+2.7e-02) | 8222.68 (+4.6e-03) |
| SNH_e | 3.226 | 3.294 (+2.1e-02) | 3.25779 (+9.9e-03) |
| TN_e | 14.7465 | 15.42 (+4.6e-02) | 14.7718 (+1.7e-03) |
| TSS_e | 16.1768 | 16.1566 (-1.2e-03) | 16.1674 (-5.8e-04) |
| SP_disposal | 2357.5863 | 2356.73 (-3.6e-04) | 2367.66 (+4.3e-03) |
| AE | 3671.3519 | 3670.09 (-3.4e-04) | 3671.48 (+3.4e-05) |
| PE | 285.264 | 243.576 (-1.5e-01) | 285.156 (-3.8e-04) |
| OCI | 15984.5473 | 15937.3 (-3.0e-03) | 16034.9 (+3.2e-03) |
| SNH_e95 | 8.0395 | 7.91748 (-1.5e-02) | 8.07162 (+4.0e-03) |
| TN_e95 | 19.1429 | 19.601 (+2.4e-02) | 19.1684 (+1.3e-03) |
| SNH_viol_days | 1.8958 | 2.02083 (+6.6e-02) | 1.91667 (+1.1e-02) |
| TN_viol_days | 0.77083 | 1.14583 (+4.9e-01) | 0.78125 (+1.4e-02) |

**Storm**, in the report's configuration.

| index | report (Matlab) | main | PR #8 |
| --- | --- | --- | --- |
| SO5_IAE | 0.56598 | 5.25856 (+8.3e+00) | 0.541671 (-4.3e-02) |
| SO5_ISE | 0.078876 | 5.44305 (+6.8e+01) | 0.0716272 (-9.2e-02) |
| SO5_err_max | 0.37924 | 1.89016 (+4.0e+00) | 0.358189 (-5.6e-02) |
| SO5_err_std | 0.10615 | 0.880275 (+7.3e+00) | 0.101153 (-4.7e-02) |
| KLa5_mean | 147.9338 | 142.296 (-3.8e-02) | 148.096 (+1.1e-03) |
| KLa5_dstd | 9.3809 | 6.59016 (-3.0e-01) | 11.5873 (+2.4e-01) |
| SNO2_IAE | 1.6785 | 3.99748 (+1.4e+00) | 1.73403 (+3.3e-02) |
| SNO2_ISE | 0.78797 | 3.01996 (+2.8e+00) | 0.81081 (+2.9e-02) |
| SNO2_err_max | 1.2014 | 1.33948 (+1.1e-01) | 1.18149 (-1.7e-02) |
| SNO2_err_std | 0.33547 | 0.651953 (+9.4e-01) | 0.340327 (+1.4e-02) |
| Qintr_mean | 24623.036 | 18880.1 (-2.3e-01) | 24544.9 (-3.2e-03) |
| Qintr_dstd | 4141.7466 | 3908.32 (-5.6e-02) | 4330.23 (+4.6e-02) |
| EQ | 7220.7241 | 7407.53 (+2.6e-02) | 7260.99 (+5.6e-03) |
| SNH_e | 3.0622 | 3.22529 (+5.3e-02) | 3.09025 (+9.2e-03) |
| TN_e | 15.8676 | 16.3437 (+3.0e-02) | 15.8832 (+9.8e-04) |
| TSS_e | 15.2737 | 15.2728 (-5.8e-05) | 15.2666 (-4.7e-04) |
| SP_disposal | 2605.4902 | 2596.47 (-3.5e-03) | 2614 (+3.3e-03) |
| AE | 3720.9173 | 3686.76 (-9.2e-03) | 3721.12 (+5.4e-05) |
| PE | 265.1984 | 242.338 (-8.6e-02) | 264.998 (-7.6e-04) |
| OCI | 17253.5665 | 17151.4 (-5.9e-03) | 17296.1 (+2.5e-03) |
| SNH_e95 | 7.8033 | 7.73958 (-8.2e-03) | 7.86416 (+7.8e-03) |
| TN_e95 | 20.1257 | 20.6124 (+2.4e-02) | 20.1494 (+1.2e-03) |
| SNH_viol_days | 1.8854 | 2.07292 (+9.9e-02) | 1.88542 (+8.8e-06) |
| TN_viol_days | 1.0938 | 1.32292 (+2.1e-01) | 1.125 (+2.9e-02) |

### What the tables show

- **On main the controllers are proportional only.** `PID.output` sets the
  integral to one step's increment instead of adding it
  (`bsm2/aerationcontrol.py:124`), so nothing accumulates. In the report's
  configuration:
  - the oxygen ISE is 72, 66 and 69 times the report's (dry, rain, storm), and
    the oxygen sits 0.05 to 0.14 g/m3 above its setpoint on average
    (`SO5_err_mean`);
  - the nitrate IAE is 2.7, 2.4 and 2.4 times the report's;
  - the recycle doesn't follow wet weather. Mean Qintr is 19190 and 18880 m3/d
    against the report's 29609 and 24623 for rain and storm, so PE is 15% and
    8.6% low;
  - EQ is 1.5%, 2.7% and 2.6% high.
- **With the pull request**, the error indices of both loops (mean absolute
  error, IAE, ISE, largest error, std and variance) are within 10% of Appendix 5
  in all three weathers. The farthest are the oxygen ISE and variance, at -9.2%
  to -9.7%. The mean errors are below 0.01 g/m3 in both, so their ratios mean
  little. Mean KLa5 and mean Qintr are within 0.32%.
  - EQ is +0.45%, +0.46% and +0.56%. AE and PE are within 0.08%, and OCI within
    0.32%.
  - The dry-weather EQ, +0.45%, is close to the open loop's +0.44% at the same
    1-minute step, which converges to the report as the step shrinks (above).
    The closed loop was not run at shorter steps, so that reading is likely but
    not shown.
  - Two things stay apart. The oxygen loop's errors are 4% to 10% smaller than
    the report's. And KLa5 changes 21% to 24% more from sample to sample (the
    std of its changes; Qintr's is 4.4% to 4.8% higher). Candidates, none
    isolated:
    - the 1-minute step;
    - bsm2-python's first-order filter on Qintr (time constant 0.001 d,
      `QINTRT`), where Appendix 5 names an actuator model only for KLa5;
    - the sensor models during stabilization, where the report's 150 days use
      ideal sensors.

### BSM1CL as shipped

Three of BSM1CL's settings differ from the report's closed loop, on main and on
the pull request alike:
- **KLa3 and KLa4 are 201.30 1/d** (`bsm1_cl.py:166-167`, `KLA3_INIT` and
  `KLA4_INIT` in `bsm2/init/aerationcontrolinit_bsm1.py`), where the report has
  240.
- **Both sensors read one noise column** (`bsm1_cl.py:201,208`). It is the
  package's `data/sensornoise.csv`, which is column 1 of `sennoise.asc` repeated
  every 14 days, looked up at the simulation time (`bsm1_cl.py:198`). The report
  uses columns 1 and 2, restarted with each file.
- **The nitrate sensor's range is 0-10 g N/m3** (`aerationcontrolinit_bsm1.py:42`),
  where section 5.1 and Table 14 have 0-20. The noise scales with the range, so
  it is 0.25 g N/m3 instead of 0.5.

It also holds each influent sample, as BSM1OL does.

With the pull request the loops still come close to the report's indices
(oxygen IAE -7.7%, nitrate IAE +0.3%), but the plant doesn't:
- effluent ammonia is 3.28 against 2.54 g N/m3 (+29%), and the ammonia limit is
  exceeded for 2.07 days against 1.20;
- AE is 9.9% low. That gap is the arithmetic of KLa3 and KLa4: 2 × 1333 m3 ×
  (240 - 201.30) 1/d × 8/1800 is 459 kWh/d less. KLa5 runs higher (mean 160.1
  against 144.3 in the report's configuration), which gives 94 kWh/d back;
- mean Qintr is 22349 m3/d (+20%).

The higher ammonia fits the weaker aeration in reactors 3 and 4. But the three
settings were not changed one at a time, so that part is not shown.

The shipped runs took about twice as long. BSM1CL searches its 876,961-row
noise table with `np.where` at every step (`bsm1_cl.py:198`). That is the likely
reason; it was not profiled.

### Two findings about the report

1. **Its error indices leave out the sensor noise.** Section 5.2 defines the
   error as e = Z_setpoint - Z_meas, the measured value, which is what the
   controllers act on.
   - With the pull request, the indices from the logged sensor signal are 1.9
     to 6.4 times the report's. From the true concentration in the tank, they
     are within 10% (the tables above). Dry weather, the report's configuration:

     | index | report (Matlab) | main | PR #8 |
     | --- | --- | --- | --- |
     | SO5_IAE, sensor signal | 0.58831 | 5.65804 (+8.6e+00) | 1.5686 (+1.7e+00) |
     | SO5_ISE, sensor signal | 0.083975 | 6.57729 (+7.7e+01) | 0.537257 (+5.4e+00) |
     | SO5_err_max, sensor signal | 0.39631 | 2.30665 (+4.8e+00) | 0.862671 (+1.2e+00) |
     | SO5_err_std, sensor signal | 0.10953 | 0.960773 (+7.8e+00) | 0.277 (+1.5e+00) |
     | SNO2_IAE, sensor signal | 1.4348 | 4.48752 (+2.1e+00) | 3.21326 (+1.2e+00) |
     | SNO2_ISE, sensor signal | 0.56897 | 4.41795 (+6.8e+00) | 2.27677 (+3.0e+00) |
     | SNO2_err_max, sensor signal | 0.91782 | 2.37698 (+1.6e+00) | 1.71123 (+8.6e-01) |
     | SNO2_err_std, sensor signal | 0.28509 | 0.787612 (+1.8e+00) | 0.569557 (+1.0e+00) |
     | KLa5: std of u, not of du | 9.5682 | 30.8976 (+2.2e+00) | 60.6044 (+5.3e+00) |
     | Qintr: std of u, not of du | 4078.4756 | 6814.31 (+6.7e-01) | 10590.9 (+1.6e+00) |

   - Rain and storm are the same (`SO5_meas_*` and `SNO2_meas_*` in the results
     files). With the pull request, the oxygen ISE from the signal is 0.528 and
     0.533, against the report's 0.0747 and 0.0789.
   - Our runs log only the true concentration and the noisy signal. A rough
     rebuild of a noise-free but delayed sensor reading (the signal less the
     known noise) lands about as close to the report as the true concentration
     does. So which of the two the report's code used is open; leaving out the
     noise is what matters. bsm1clkpi.py uses the true concentration.
2. **Its "standard deviation of MV" is the std of the changes.** Appendix 5
   labels the figure std(Qintr) and std(KLa5). But section 5.2 defines the index
   as the variance of the manipulated variable's variations, Δu = u(t + dt) -
   u(t).
   - The numbers agree with section 5.2. In the table above, the std of u itself
     is 1.7 to 6.3 times the report's. With the pull request, the std of Δu is
     +4.4% (Qintr) and +23% (KLa5).
   - reference.csv names these rows `Qintr_dstd`, `Qintr_dvar`, `KLa5_dstd` and
     `KLa5_dvar`.

The variances are also the population form. Each printed variance of an error
equals ISE/7 - mean(e)² to its printed digits, in all six loops. For dry
nitrate, that is 0.0812769 against the printed 0.081276; the n - 1 form gives
0.081398. bsm1clkpi.py uses the population form for errors and changes alike,
and a control holds it to that.

### 15-minute steps

BSM1CL warns that steps longer than a minute will "most probably fail". These
runs used the report's configuration and dry weather at 15-minute steps, with 1
day of stabilization instead of 150 to keep them short:
- **The pull request's head gives NaN.** The oxygen controller's integral
  overflows to -inf at t = 2.26 d, 3.26 days into the run, and KLa5 is NaN from
  the next sample, t = 2.27 d
  ([results/kpi_bsm2python_cl_report_dry_pr8_step15.txt](results/kpi_bsm2python_cl_report_dry_pr8_step15.txt)).
  - The tracking term adds (u - v)·dt/Tt to the integral at each step,
    explicitly. The oxygen loop's Tt is 0.001 d (1.44 min), so at 15 minutes
    dt/Tt is 10.4.
  - So each step overshoots the limit 9.4 times as far as the last, the other
    way, and the integral grows without bound.
  - This update is stable only for dt < 2·Tt: 2.88 minutes for the oxygen loop
    and 43.2 for the nitrate loop (Tt 0.015 d).
- **main stays finite**, because its integral starts again each step. But the
  loop chatters between its limits: over days 21-28 KLa5 spans 359.995 of its
  0-360 1/d, and the oxygen IAE is 14.9 against the report's 0.588.
- **The guard our review suggested** keeps the integral bounded at any step. It
  changes nothing while dt ≤ Tt (at 1-minute steps dt/Tt is 0.69 for the oxygen
  loop). It replaces line 128 of `bsm2/aerationcontrol.py` at the pull request's
  head:

  ```diff
  -            self.aw = (self.prev_lim - self.prev_signal) / self.t_t * (dt_arr[1] - dt_arr[0])
  +            self.aw = (self.prev_lim - self.prev_signal) * min((dt_arr[1] - dt_arr[0]) / self.t_t, 1.0)
  ```

  With it the same run stays finite, but chatters like main's: KLa5 spans
  359.998 and the oxygen IAE is 14.2. Fifteen-minute steps are too coarse for
  these loops either way, and the guard only removes the NaN.

The two finite runs' indices are
[results/kpi_bsm2python_cl_report_dry_main_step15.csv](results/kpi_bsm2python_cl_report_dry_main_step15.csv)
and
[results/kpi_bsm2python_cl_report_dry_pr8guard_step15.csv](results/kpi_bsm2python_cl_report_dry_pr8guard_step15.csv).

### What the closed loop does not show

- **Steps under a minute.** None were run, so how much of what remains with the
  pull request is step error is not known.
- **The shipped settings one at a time**, and rain and storm as shipped.
- **15-minute steps after 150 days** of stabilization: only 1 day was run.
- **Appendix 5's closed-loop steady state** (pp. 49-52).
- **bsm2-python's other controlled plants** (BSM1PS, BSM2CL), and the pull
  request's own tests. The review covers them; they are not part of this check.

## Candidates for upstream

Only our review of bsm2-python's pull request #8 has been posted (see the
closed loop). Each of these would need its text agreed first.

- **WaterTAP** (an issue, then a small PR):
  - `ASM1_flowsheet.py` holds reactor 5's oxygen at 4.49e-4 kg/m3 as
    "controlled" (line 312). That value is neither BSM1's open loop (KLa
    3.5 1/h, giving 0.491 g/m3) nor its closed-loop setpoint (2 g/m3), and
    its source isn't stated. Its test accepts
    effluent nitrate and ammonia 2.6% and 7.3% from the report as "slightly off
    in last significant digit".
  - Which fix is right is the maintainers' call. Either add the KLa constraint
    to R5 as R3 and R4 have it, which was run here (`run_watertap.py`
    `add_kla5` is the whole change), or keep R5 controlled at 4.91e-4, which
    was not run. Either way the test can then be tightened to the report's
    values.
  - The rounded split fractions could also carry more digits (18061/36892 and
    18446/18831).
  - No open issue covers it: a search for BSM1 and the ASM1 flowsheet found
    only #934 (BSM2) and closed PRs. #1851 and #1876 are about BSM2.
- **EXPOsan** (an issue; the fix is a choice for the maintainers):
  - `exposan/bsm1` reproduces BSM1 only to about 3e-3. The cause is the exact
    constants 20/7 and 32/7 in its `_asm1.tsv`, and the exact atomic weights in
    the alkalinity charge balance.
  - A BSM1 module could carry BSM1's own 2.86 and 4.57 and a 14 and 12
    convention for alkalinity, or the README could say how far it stands from
    the reference.
  - The dynamic differences (internal recycle, the soluble clarifier; see the
    dynamic section) belong in the same issue. No open issue in QSDsan or EXPOsan
    covers any of this.
- **bsm2-python** (an issue, possibly with a fixed file):
  - `src/bsm2_python/data/raininfluent.csv` does not load. Rows 998, 1000 and
    1001 hold `30.044.50`, `27.446.67` and `26.880.33`.
  - The whole flow column is in thousands (21.477 for 21477), every value
    including time is rounded to 2 decimals, and nothing in the package reads
    the file.
  - The repository also has no storm file.
  - Separately, influent is held constant between samples, while Simulink
    interpolates. Over days 7-14 that moves EQ by 0.2% and effluent ammonia by
    0.4% (dry weather).
  - The only open issue (#7) is the PID bug that pull request #8 fixes; our
    review of that pull request is posted.
  - `BSM1CL` differs from the report's closed loop in three settings: KLa3 and
    KLa4 at 201.30, one noise column for both sensors, and a nitrate sensor
    range of 0-10 (see the closed loop). The review offered to open an issue
    for them.
  - The 15-minute guard was suggested in the review, as not blocking.
- **The IWA task group** (no public tracker; a note to the BSM authors):
  - the hosted rain and storm files keep SI at 30 where the published results
    need it diluted;
  - Appendix 4's steady state misses the XI balance by 6e-6.

  Both are shown here with numbers anyone can recompute.

## Commands

```sh
# the reference: the report's text and the IWA influent files, each in its own empty directory
curl -sSLO https://www2.iea.lth.se/publications/Reports/LTH-IEA-7229.pdf && pdftotext -layout LTH-IEA-7229.pdf bsm1.txt
for f in Inf_dry_2006.txt Inf_rain_2006.txt Inf_strm_2006.txt sennoise.zip; do curl -sSLO http://iwa-mia.org/wp-content/uploads/2019/04/$f; done
unzip sennoise.zip                                # sennoise.asc, for the closed loop
python3 -I checks/bsm1/refextract.py bsm1.txt checks/bsm1/reference.csv     # IDENTICAL

# on a host: sources as git archive tarballs under src/, influent files under inputs/
sh setup-envs.sh                                  # env/qsd, env/bsm2, env/wt (about 2.5 GB)
IDAES_DATA=$PWD/idaes env/wt/bin/idaes get-extensions --distro ubuntu2204   # or unpack idaes-ext 3.4.2 by hand
NCORES=16 nice -n 19 sh cfarm-job.sh > logs/job.log 2>&1

# one run by hand
env/bsm2/bin/python -I run_bsm2python.py ss results/ss_bsm2python.csv 1000
env/qsd/bin/python -I run_qsdsan.py ss results/ss_qsdsan_bsm1coef.csv 1000 1e-8 bsm1
env/qsd/bin/python -I run_qsdsan.py dyn inputs storm linear-fixqa diluted results/dyn_qsdsan_linear-fixqa_storm.csv 1e-6
env/wt/bin/python -I run_watertap.py results/ss_watertap.csv
python3 -I bsm1kpi.py results/dyn_bsm2python_linear_dry.csv dry 21 results/kpi_bsm2python_linear_dry.csv

# closed loop: env/bsm2 has main installed; --src imports a checkout instead, here the pull
# request's head (git fetch https://github.com/fau-evt/bsm2-python pull/8/head); inputs/ also holds sennoise.asc
env/bsm2/bin/python -I run_bsm2python_cl.py report inputs dry results/dyn_bsm2python_cl_report_dry_pr8.csv - --src bsm2-python-pr8/src
env/bsm2/bin/python -I run_bsm2python_cl.py shipped inputs dry results/dyn_bsm2python_cl_shipped_dry_main.csv -
env/bsm2/bin/python -I run_bsm2python_cl.py report inputs dry results/dyn_bsm2python_cl_report_dry_main_step15.csv - 15 1
python3 -I bsm1clkpi.py results/dyn_bsm2python_cl_report_dry_pr8.csv cl_dry 21 results/kpi_bsm2python_cl_report_dry_pr8.csv

# comparisons (standard library only)
python3 -I bsm1cmp.py ref reference.csv results/ss_bsm2python.csv                 # Appendix 4
python3 -I bsm1cmp.py ref reference.csv results/ss_bsm2python.csv --source t      # Tables 6-8
python3 -I bsm1cmp.py ref reference.csv results/ss_watertap.csv --rcase ss_exact --common
python3 -I bsm1cmp.py ref reference.csv results/kpi_bsm2python_linear_dry.csv --case dry
python3 -I bsm1cmp.py pair results/ss_bsm2python.csv results/ss_qsdsan_bsm1coef.csv --rtol 1e-7
python3 -I bsm1cmp.py pair simulink200.csv results/ss_bsm2python.csv --common
python3 -I kpitable.py dry linear=results/kpi_bsm2python_linear_dry.csv
python3 -I bsm1cmp.py ref reference.csv results/kpi_bsm2python_cl_report_dry_pr8.csv --case cl_dry --source app5
python3 -I kpitable.py cl_dry main=results/kpi_bsm2python_cl_report_dry_main.csv "PR #8=results/kpi_bsm2python_cl_report_dry_pr8.csv"
python3 -I kpitable.py cl_dry --alt "PR #8=results/kpi_bsm2python_cl_report_dry_pr8.csv"   # sensor signal, std of u
python3 -I controls.py results/ss_bsm2python.csv Inf_dry_2006.txt bsm1.txt         # the planted faults
```

## Controls

[controls.py](controls.py) plants one fault per check and passes only if the
clean run gives its expected verdict and the planted run is caught, naming the
row where the check names rows. All 9 were caught (IDENTICAL):

- `bsm1cmp.py ref` with the report's own Appendix 4 values as a result:
  - clean, IDENTICAL;
  - with reactor 3's SNO raised one printed unit, DIFFERS, naming that row;
  - with one row removed, VOID.
- `bsm1cmp.py pair` of a result with itself:
  - clean, IDENTICAL;
  - with effluent SNH times (1 + 1e-10), DIFFERS, naming it.

  At `--rtol 1e-9` that planted change passes, and at 1e-11 it is caught.
- `bsm1kpi.py` on the dry influent alone:
  - its IQ for days 7-14 is the report's 52081.3952, an answer the code did not
    make;
  - with one SNH sample raised by 1 g/m3, DIFFERS.
- `refextract.py`:
  - reference.csv rebuilt from the report, IDENTICAL;
  - with the last digit of rain EQ changed, DIFFERS;
  - with the last digit of the closed loop's dry-weather oxygen ISE changed,
    DIFFERS.
- `bsm1cmp.py ref` for the closed loop, with Appendix 5's own dry-weather
  rows as a result:
  - clean, IDENTICAL;
  - with the oxygen IAE raised one printed unit, DIFFERS, naming that row.
- `bsm1clkpi.py` on a series whose indices were worked out by hand: the oxygen
  alternating 2 ∓ 0.1 and the nitrate 1 ∓ 0.2, KLa5 and Qintr as ramps, KLa3 and
  KLa4 at 240.
  - The answers are IAE 0.7, ISE 0.07 and std 0.1 for oxygen (and 1.4, 0.28,
    0.2 for nitrate), a std of the changes of 0 for both ramps, and AE
    3933.0905556. All are IDENTICAL. The n - 1 std would give 0.1000745, and
    a copy of bsm1clkpi.py changed to n - 1 fails this control.
  - With one oxygen sample moved by 0.5, DIFFERS, naming the IAE.

Two more checks against answers the code did not make:
- IQ for rain and storm, with diluted SI, gives the report's figures to the
  last printed digit.
- The steady-state rebuild of the derived rows, sludge ages and thickening
  factors, from Appendix 4's own states agrees with its printed values.

## What these do not show

- **The 2008 Simulink model itself.** It is not public, so how it interpolated
  the influent, its solver and its tolerances, and where its 100 days started,
  are inferred, not read.
- **Closed loop outside bsm2-python.** QSDsan and WaterTAP were not run in
  closed loop. For bsm2-python's, see
  [what the closed loop does not show](#what-the-closed-loop-does-not-show).
- **WaterTAP's dynamics.** It has no dynamic BSM1 and no layered settler.
  Its BSM2 flowsheets were not compared.
- **bsm2-python's BSM2.** Its BSM2 was not run, and neither was QSDsan's
  ASM2d or PFR variant of `exposan.bsm1`.
- **A QSDsan restart oddity, not explained.** Splitting a QSDsan steady-state
  run into legs, calling `System.simulate` again without resetting the state,
  gave states 1% away from a single run after 2 days. The runs here are single
  calls.
