# bsm1: do the open implementations of BSM1 give the published answer? (ideas U6)

Benchmark Simulation Model No. 1 is the IWA task group's activated-sludge plant
with a published reference answer: five reactors (two anoxic, three aerated),
ASM1, a ten-layer settler, fixed flows and aeration in open loop. This check runs
it in three open implementations and compares them with the report and with each
other.

Run on cfarm421 (AMD EPYC 7773X, Debian 13.7, glibc 2.41, Python 3.13.5) on
2026-10-29 between 01:51 and 04:40 UTC. **CPU limit:** at most 16 single-threaded
processes at once (`OMP_NUM_THREADS=1` and the like), all at `nice -n 19`, with a
run notice posted while they ran. The comparison scripts are standard-library
Python and run anywhere.

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
- **[reference.csv](reference.csv)**, 445 rows (`case, block, var, printed,
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
    implementation, to three or four digits. That makes a second published answer.

  [refextract.py](refextract.py) rebuilds the file from `pdftotext -layout` of
  the 2008 PDF and gives IDENTICAL.
- **A converged Simulink answer.** bsm2-python's own test,
  `tests/bsm1_ol_test.py` lines 62-114 (BSD-3), holds the BSM2 group's Simulink
  BSM1 open loop after 200 days at constant influent (`bsm1_test_ol.slx`), at full
  precision: the effluent and the ten settler layers.
  [simulink200.csv](simulink200.csv) copies them.
- **Influent files.** The same IWA page hosts the three weather files, with no
  terms stated, at `http://iwa-mia.org/wp-content/uploads/2019/04/` + file name.
  They are not copied here. Their sha256 values:
  - `Inf_dry_2006.txt`: `2a3776651012d004835870dde73857acec36202efb86ba69f589d6b4fb7601e0`;
  - `Inf_rain_2006.txt`: `c84a4e49d8c0f9bea27a427f528cd00344575c19900c8813eeffb66b0d1f5dd7`;
  - `Inf_strm_2006.txt`: `8e600c737710767da0116283bab5ba567c9b5114c5859faeb7383ed962b72c65`.

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

## What was run

| implementation | source | how it reaches the answer |
| --- | --- | --- |
| QSDsan + EXPOsan | github.com/QSD-Group/QSDsan `main` `bac88d8fca9d86a01dbfc5694cd4c0fe23f9a259` (2026-10-12, version 1.6.0); github.com/QSD-Group/EXPOsan `main` `84d50344abc089a07bebd38786a833d4fd235cc4` (2026-10-22, 1.6.0; installed with `--no-deps`, since it pins qsdsan==1.5.3); biosteam 2.54.0, thermosteam 0.54.2, scipy 1.18.1, numpy 2.5.4, numba 0.68.1 | `exposan.bsm1` as shipped: ASM1, five CSTRs, `FlatBottomCircularClarifier`. Integrated in time with scipy's BDF. Steady state: 1000 days at rtol = atol = 1e-8 from EXPOsan's default initial state. Dynamic: 300 days at constant influent, then 14 days dry and 14 days of the weather at rtol = atol = 1e-6 (one case again at 1e-8); variants with linear influent and with the internal recycle held constant (`-fixqa`, see below) |
| WaterTAP | github.com/watertap-org/watertap `main` `5909a60409d25944f73d5b9293abf3a6adf21def` (2026-10-01, version 1.9.0.dev0, after the 1.8.0 release); idaes-pse 2.13.0, pyomo 6.10.1, IPOPT 3.13.2 from idaes-ext 3.4.2 (ubuntu2204 build; checksums matched) | WaterTAP has no BSM1 flowsheet with BSM1's settler. `watertap/flowsheets/activated_sludge/ASM1_flowsheet.py` is BSM1's reactors and flows with a separator for the clarifier (WaterTAP's `Clarifier` is a separator too, with no layers), solved as one steady state by IPOPT (watertap-solvers defaults: tol and constr_viol_tol 1e-8). Its BSM2 flowsheets have a different plant (other volumes, a primary clarifier, a digester) and were not run. No dynamic case |
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
- [bsm1kpi.py](bsm1kpi.py) turns a series into the report's indices for days
  7-14 of the weather;
- [bsm1cmp.py](bsm1cmp.py) compares with the report or between results;
- [kpitable.py](kpitable.py) tabulates indices;
- [controls.py](controls.py) runs the planted faults;
- [cfarm-job.sh](cfarm-job.sh) and [job1.sh](job1.sh) are the host's job,
  and [setup-envs.sh](setup-envs.sh) built the environments.

The steady states and performance indices are in [results/](results/). The
15-minute series (about 2.5 MB each) were archived privately with the logs.

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
     That gives effluent SALK 4.12439 against 4.12558: the predicted shift,
     0.0011866, is the observed 0.0011868.

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
       10 1/h. So 0.449 looks like Table 6's 0.491 with two digits swapped.
       That is a guess; fixing R5 at 4.91e-4 instead was not run.

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

## Candidates for upstream

Nothing has been posted. Each of these would need its text agreed first.

- **WaterTAP** (an issue, then a small PR):
  - `ASM1_flowsheet.py` holds reactor 5's oxygen at 4.49e-4 kg/m3 as
    "controlled" (line 312). That value is neither BSM1's open loop (KLa
    3.5 1/h, giving 0.491 g/m3) nor its closed-loop setpoint (2 g/m3), and
    looks like the report's 0.491 with two digits swapped. Its test accepts
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
  - The only open issue (#7) is about the PID controller.
- **The IWA task group** (no public tracker; a note to the BSM authors):
  - the hosted rain and storm files keep SI at 30 where the published results
    need it diluted;
  - Appendix 4's steady state misses the XI balance by 6e-6.

  Both are shown here with numbers anyone can recompute.

## Commands

```sh
# the reference: the report's text and the IWA influent files, each in its own empty directory
curl -sSLO https://www2.iea.lth.se/publications/Reports/LTH-IEA-7229.pdf && pdftotext -layout LTH-IEA-7229.pdf bsm1.txt
for f in Inf_dry_2006.txt Inf_rain_2006.txt Inf_strm_2006.txt; do curl -sSLO http://iwa-mia.org/wp-content/uploads/2019/04/$f; done
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

# comparisons (standard library only)
python3 -I bsm1cmp.py ref reference.csv results/ss_bsm2python.csv                 # Appendix 4
python3 -I bsm1cmp.py ref reference.csv results/ss_bsm2python.csv --source t      # Tables 6-8
python3 -I bsm1cmp.py ref reference.csv results/ss_watertap.csv --rcase ss_exact --common
python3 -I bsm1cmp.py ref reference.csv results/kpi_bsm2python_linear_dry.csv --case dry
python3 -I bsm1cmp.py pair results/ss_bsm2python.csv results/ss_qsdsan_bsm1coef.csv --rtol 1e-7
python3 -I bsm1cmp.py pair simulink200.csv results/ss_bsm2python.csv --common
python3 -I kpitable.py dry linear=results/kpi_bsm2python_linear_dry.csv
python3 -I controls.py results/ss_bsm2python.csv Inf_dry_2006.txt bsm1.txt         # the planted faults
```

## Controls

[controls.py](controls.py) plants one fault per check and passes only if the
clean run gives its expected verdict and the planted run is caught, naming the
row where the check names rows. All 6 were caught (IDENTICAL):

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
  - with the last digit of rain EQ changed, DIFFERS.

Two more checks against answers the code did not make:
- IQ for rain and storm, with diluted SI, gives the report's figures to the
  last printed digit.
- The steady-state rebuild of the derived rows, sludge ages and thickening
  factors, from Appendix 4's own states agrees with its printed values.

## What these do not show

- **The 2008 Simulink model itself.** It is not public, so how it interpolated
  the influent, its solver and its tolerances, and where its 100 days started,
  are inferred, not read.
- **Closed loop.** The report's PI controllers, sensors and noise were not run.
- **WaterTAP's dynamics.** It has no dynamic BSM1 and no layered settler.
  Its BSM2 flowsheets were not compared.
- **bsm2-python's BSM2.** Its BSM2 and closed-loop BSM1 were not run, and
  neither was QSDsan's ASM2d or PFR variant of `exposan.bsm1`.
- **A QSDsan restart oddity, not explained.** Splitting a QSDsan steady-state
  run into legs, calling `System.simulate` again without resetting the state,
  gave states 1% away from a single run after 2 days. The runs here are single
  calls.
