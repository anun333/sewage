# checks/echo: what kind of trouble do Tennessee's sewage plants report to EPA?

[N2](../../ideas.md#n2). [echo_screen.py](echo_screen.py) reads EPA's ECHO downloads
straight from their zip files and sorts each POTW's problems by kind. It also looks for
reported statistics that contradict their own definitions, which is the question
behind [N1](../../ideas.md#n1). Standard library only.

One run, on cfarm421 (Debian 13, Python 3.13.5), on 2026-11-03: Tennessee, FY2023–FY2025
(October 2022 to September 2025), with EPA's files of 2026-11-01. The run took a few
minutes on one core. Its report is
[results/screen-TN-FY2023-FY2025.md](results/screen-TN-FY2023-FY2025.md).

**Verdict: DIFFERS.**
- **The contradictions:** 529 reported statistics contradict their own definitions, at
  157 of the 308 plants:
  - 500 monthly averages or monthly geometric means above the same month's daily
    maximum;
  - 29 pH minima above the maximum.
- **The controls all pass:**
  - Four planted cases are each flagged, and their clean twins are not.
  - The E90, D80 and D90 counted from the DMR files equal those in EPA's violations file,
    to the unit: 7,667, 760 and 1,249.

## What it found

308 of Tennessee's 383 POTW permits reported DMR values in the window.

| Size | Plants | Major | DMR values | E90 | Plants with E90 | D80+D90 | Plants with D80/D90 | SNC quarters | Plants with SNC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <0.1 MGD | 71 | 0 | 34,243 | 638 | 48 | 196 | 17 | 44 | 17 |
| 0.1–1 MGD | 120 | 0 | 162,322 | 3,428 | 113 | 1,230 | 48 | 76 | 28 |
| 1–10 MGD | 90 | 90 | 139,292 | 2,261 | 86 | 416 | 41 | 31 | 15 |
| ≥10 MGD | 27 | 27 | 51,831 | 1,340 | 27 | 167 | 11 | 27 | 8 |

E90 is a limit exceeded. D80 and D90 are required values not received.

1. **Plants fail mostly on treatment.**
   - **Overall:** there were 7,667 limit exceedances against 2,009 values not received.
     The exceedances by parameter:
     - BOD 1,653;
     - overflows 1,564;
     - ammonia 1,410;
     - TSS 946;
     - bacteria 765.
   - **Small plants** (under 1 MGD, 191 plants): 4,066 exceedances against 1,426 values not
     received. BOD (1,121) and ammonia (845) lead.
   - **Significant noncompliance:** 178 of 2,314 plant-quarters were SNC. Of those, 161
     were for effluent, 16 for missing DMRs and 1 for a schedule.
2. **A fifth of the exceedances are sewer overflows.**
   - **How they're reported:** Tennessee reports sanitary sewer overflows as DMR
     parameters, "SSO, Wet Weather" (863) and "SSO, Dry Weather" (701). Each one counts as
     an E90.
   - **Which plants:** almost all at plants of 0.1 MGD and up. This is the collection
     system, not the plant, and it ties to [U5](../../ideas.md#u5)'s RDII.
   - **Single-event violations,** where overflows might be expected, hold almost none: 1
     unauthorized discharge out of 75. The rest are pretreatment-programme failures (58)
     and analyses not done (15).
3. **Self-contradicting statistics are rare per value, but common across plants.**
   - **How many:** 529 in 182,497 parameter-periods (0.29%), at 157 plants (51%). 338 of
     them are at plants under 1 MGD.
   - **By parameter:** flow 202, BOD 81, TSS 79, bacteria 44, phosphorus 44, ammonia 33,
     and pH (minimum above maximum) 29.
   - **They aren't rounding.** Most are far off: 312 of the 500 averages are more than
     twice the maximum. They look like values in the wrong box:
     - one small plant's monthly average flow is 1,744 MGD against a daily maximum of
       0.22;
     - one plant reports a pH minimum of 7.2 with a maximum of 6.3;
     - one plant's monthly average flow is 4 to 15 times its daily maximum, month after
       month.
   - **Concentrated:** three plants account for 34, 32 and 26.
4. **Loadings are mostly consistent.**
   - **The comparison:** 16,382 monthly loadings could be set against concentration × flow
     × 8.34. 13,111 are within 25% of it, and the median ratio is 0.9997.
   - **Unit factors:** 45 ratios fall near one. Decoys 15% either side of each factor
     catch about as many for 8.34, 3.785 and their inverses, so those are chance.
   - **Real slips:**
     - ×0.001, a microgram/milligram slip, clearly stands out: 8 cases against 0 for
       each decoy;
     - ×0.1 and ×10 stand out mildly (9 against 4 and 4; 5 against 2 and 2);
     - about 18 matches in all lie beyond the decoys.
5. **Rounding at the limit's precision decides few violations.**
   - **The precision is lost.** ECHO strips trailing zeros. In FY2025, none of the
     38,346 limits written with a decimal point ends in 0, and 20,803 are written like
     `.5`. So a permit's stated decimals can't be recovered.
   - **The range:** of 7,469 E90s with a value in the limit's unit, at most 219 (2.9%)
     drop below the limit when rounded half-even to the stored decimals, and 56 more are
     exact ties. With one more decimal than stored, 6 clear and 4 tie. Ties like pH 9.5
     against a stored "9" are surely violations of a permit's 9.0.
6. **Censored bacteria counts are reported as exact.**
   - 87 E. coli E90s report exactly 2419.6 with no qualifier. That is the top of the
     Quanti-Tray/2000 range, where the true count is higher.
   - 72 carry the ">" that marks it.
   - 6 carry "<", which points the wrong way.

## What it means for N1

N1's falsifier was: "Tennessee's small plants fail mostly on treatment … or on DMRs never
sent …, with nothing pointing at wrong arithmetic." The answer comes in three parts:
- **Treatment:** met. Small plants exceed limits about three times as often as they fail
  to report.
- **Rounding,** N1's first premise ([dmr_rounding.py](../dmr_rounding.py)): it decides at
  most 3.7% of violations, and maybe almost none.
- **Contradictions:** not met. Half the plants reported at least one statistic that
  contradicts its own definition, and small plants have most of them. A tool that
  computes each month's statistics from the daily values, and refuses an average above
  the maximum, would prevent those.

So N1 as "round exactly" has little behind it in this data. N1 as "compute and check the
DMR from the daily values" does.

## What this does not show

- **Which of two contradicting values is wrong.** ECHO holds only the monthly
  statistics, not the daily values. For the same reason, it can't show whether a
  consistent-looking value was computed right.
- **Whether NetDMR or Tennessee's own system checks that an average is at most the
  maximum.** Not checked.
- **Lagoons.** Nothing in these files marks a lagoon.
- **Anything beyond Tennessee** and these three years.
- **Findings against a plant.** The plant names and values in `results/` are as reported
  to EPA by 2026-11-01, and some may have been corrected since. A flagged value is a
  reason to look closer.
- **Exact parameter groups.** They come from matching parameter names.

## Files and rerun

- [echo_screen.py](echo_screen.py): the screen. Its docstring lists the tests and
  controls.
- [echojob.sh](echojob.sh): the cfarm wrapper, with a run notice.
- `results/`:
  - the report;
  - [plants](results/plants-TN-FY2023-FY2025.tsv): one row per plant, with counts by kind
    and parameter group;
  - [flags](results/flags-TN-FY2023-FY2025.tsv): every flagged value with the other
    values in its group;
  - `SHA256SUMS` of the inputs and the fetch time.

EPA's files, from `https://echo.epa.gov/files/echodownloads/`:
- `NPDES_by_state_year/TN_FY{2023,2024,2025}_NPDES_DMRS_LIMITS.zip`;
- `NPDES_by_state_year/TN_NPDES_EFF_VIOLATIONS.zip`;
- `npdes_downloads.zip` (359 MB);
- `ref_tables/REF_STATISTICAL_BASE.csv`.

EPA refreshes them weekly, so a rerun later reads newer data.

```sh
python3 -I checks/echo/echo_screen.py --data DATA --state TN --fy 2023 2025 \
    --tsv plants.tsv --flags flags.tsv
```
