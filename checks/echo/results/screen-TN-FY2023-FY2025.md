# ECHO screen: TN POTWs, FY2023-FY2025 (2022-10-01 to 2025-09-30)

Statistical bases compared: avg MK, MM; daily_max DD, IA; max DD, IA, MB; min DC, IB, ME

DMR rows read: 917,638; POTW rows in the window: 387,688
POTW permits in TN (latest version): 383; with DMR values in the window: 308

## By design flow

| Size | Plants | Major | DMR values | E90 | Plants with E90 | D80+D90 | Plants with D80/D90 | SNC quarters | Plants with SNC | Single events |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <0.1 MGD | 71 | 0 | 34,243 | 638 | 48 | 196 | 17 | 44 | 17 | 0 |
| 0.1-1 MGD | 120 | 0 | 162,322 | 3,428 | 113 | 1,230 | 48 | 76 | 28 | 24 |
| 1-10 MGD | 90 | 90 | 139,292 | 2,261 | 86 | 416 | 41 | 31 | 15 | 41 |
| >=10 MGD | 27 | 27 | 51,831 | 1,340 | 27 | 167 | 11 | 27 | 8 | 10 |

Totals: E90 7,667; D80 760; D90 1,249; SNC quarters 178 of 2,314 plant-quarters; single events 75
Cross-check, the violations file for the same plants and window: E90 7,667, D80 760, D90 1,249

## Effluent violations (E90) by parameter group

- bod: 1,653
- overflow: 1,564
- ammonia: 1,410
- tss: 946
- bacteria: 765
- removal: 352
- chlorine: 207
- nitrogen: 158
- phosphorus: 146
- settleable: 134
- oxygen: 128
- ph: 116
- toxicity: 80
- metals: 7
- other: 1

| Group | <0.1 MGD | 0.1-1 MGD | 1-10 MGD | >=10 MGD |
| --- | --- | --- | --- | --- |
| bod | 103 | 1,018 | 233 | 299 |
| overflow | 2 | 467 | 630 | 465 |
| ammonia | 243 | 602 | 518 | 47 |
| tss | 49 | 394 | 258 | 245 |
| bacteria | 138 | 377 | 164 | 86 |
| removal | 17 | 151 | 116 | 68 |
| chlorine | 14 | 121 | 53 | 19 |
| nitrogen | 0 | 56 | 80 | 22 |
| phosphorus | 0 | 86 | 60 | 0 |
| settleable | 2 | 42 | 43 | 47 |
| oxygen | 22 | 47 | 29 | 30 |
| ph | 48 | 37 | 25 | 6 |
| toxicity | 0 | 27 | 48 | 5 |
| metals | 0 | 3 | 4 | 0 |
| other | 0 | 0 | 0 | 1 |

  The largest in 'other': Discharge event observation [Visual Monitoring] 1

## SNC quarters by kind

- effluent: 161
- missing DMR: 16
- schedule: 1

## Single-event violations by description

- Pretreatment - Failure to Enforce Against I/U: 25
- Pretreatment - Failure to submit required report (non-DMR): 17
- Monitoring Violations - Analysis not Conducted: 15
- Pretreatment - Failure to Meet Inspection and Sampling Plan for SIUs: 8
- Pretreatment - Failure to Conduct Inspections: 7
- Permit Violations - Violation Specified in Comment: 1
- Effluent Violations - Unauthorized Discharge: 1
- Pretreatment - Failure to Develop/Enforce Standards: 1

## Values that contradict their own arithmetic

- average above the daily maximum: 500; minimum above the maximum: 29 (of 182,497 parameter-periods)
  - by parameter group: avg>max flow 202; avg>max bod 81; avg>max tss 79; avg>max bacteria 44; avg>max phosphorus 44; avg>max ammonia 33; min>max ph 29; avg>max chlorine 9; avg>max nitrogen 7; avg>max metals 1
  - by size: <0.1 MGD 149; 0.1-1 MGD 189; 1-10 MGD 163; >=10 MGD 28
  - plants: 157; the most: TN0059480 34, TN0068187 32, TN0077917 26, TN0024058 15, TN0023680 14, TN0023698 14
  - TN0020729 10/31/2022 outfall 001 param 51040 (CFU/100mL): avg>max 3.89855e+07 > 5.1988
  - TN0020729 07/31/2023 outfall 001 param 51040 (CFU/100mL): avg>max 808950 > 1.1636
  - TN0021563 04/30/2023 outfall 001 param 51040 (#/100mL): avg>max 103 > 10.1
  - TN0021652 03/31/2023 outfall 001 param 51040 (#/100mL): avg>max 28.2 > 0.866
  - TN0021938 09/30/2023 outfall 001 param 51040 (#/100mL): avg>max 12 > 1
  - TN0024155 11/30/2022 outfall 001 param 51040 (#/100mL): avg>max 1.52 > 0.35
  - TN0025020 01/31/2023 outfall 001 param 51040 (#/100mL): avg>max 13 > 12.6
  - TN0057291 07/31/2023 outfall 001 param 51040 (#/100mL): avg>max 11.5 > 8.5
- loading against concentration x flow x 8.34: 16,382 pairs compared; 45 off by a unit factor (x0.001: 8, x0.1: 9, x0.1199: 6, x0.2642: 2, x3.785: 14, x8.34: 1, x10: 5)
  - within 25% of 1: 13,111; more than 3.16 times off either way: 409; median ratio 0.9997
  - matches at each factor beside decoys 15% either side (below / at / above):
    - x8.34: 1 / 1 / 4
    - x0.1199: 4 / 6 / 4
    - x3.785: 17 / 14 / 14
    - x0.2642: 5 / 2 / 13
    - x10: 2 / 5 / 2
    - x0.1: 4 / 9 / 4
    - x100: 0 / 0 / 0
    - x0.01: 0 / 0 / 0
    - x1000: 0 / 0 / 1
    - x0.001: 0 / 8 / 0
  - matches beyond the larger decoy, summed over the factors: 18
  - TN0057908 02/28/2023 outfall 001 param 80082: 1.68 lb/d vs 4.5 mg/L x 0.45 MGD x 8.34 = 16.89; ratio 0.0995 (x0.1)
  - TN0020711 07/31/2023 outfall 001 param 00310: 243000 lb/d vs 33.5 mg/L x 84.7 MGD x 8.34 = 2.366e+04; ratio 10.2686 (x10)
  - TN0062138 06/30/2023 outfall 001 param 00310: 19 lb/d vs 10 mg/L x 0.061 MGD x 8.34 = 5.087; ratio 3.7347 (x3.785)
  - TN0062201 11/30/2022 outfall 001 param 00310: 22.7 lb/d vs 9 mg/L x 0.082 MGD x 8.34 = 6.155; ratio 3.6881 (x3.785)
  - TN0062227 09/30/2023 outfall 001 param 00665: 4.25 lb/d vs 1.84 mg/L x 0.034 MGD x 8.34 = 0.5218; ratio 8.1457 (x8.34)
  - TN0028622 01/31/2023 outfall 001 param 00530: 6.8 lb/d vs 0.3 mg/L x 0.7 MGD x 8.34 = 1.751; ratio 3.8826 (x3.785)
  - TN0057908 02/28/2023 outfall 001 param 00530: 1.21 lb/d vs 3.2 mg/L x 0.45 MGD x 8.34 = 12.01; ratio 0.1008 (x0.1)
  - TN0057908 09/30/2023 outfall 001 param 00530: 0.6 lb/d vs 4.7 mg/L x 0.15 MGD x 8.34 = 5.88; ratio 0.1020 (x0.1)

## Signals that are not contradictions

- E90s at the rounding edge, value rounded half-even to the limit's stored decimals (an upper bound, since ECHO strips trailing zeros): clears 219, tie 56, stands 7,194
  - with one more decimal than stored: clears 6, tie 4, stands 7,459
  - clears: TN0020541 02/28/2023 Chlorine, total residual [DC] value .7 limit 1 mg/L
  - clears: TN0020672 05/31/2023 Chlorine, total residual [DD] value 2.18 limit 2 mg/L
  - clears: TN0020702 11/30/2022 Chlorine, total residual [DD] value .31 limit .3 mg/L
  - clears: TN0021211 12/31/2022 Chlorine, total residual [DD] value 2.09 limit 2 mg/L
  - clears: TN0028827 07/31/2023 Chlorine, total residual [DC] value .8 limit 1 mg/L
  - clears: TN0054585 12/31/2022 Chlorine, total residual [DD] value 2.1 limit 2 mg/L
  - clears: TN0059790 12/31/2022 Chlorine, total residual [DD] value 1.01 limit 1 mg/L
  - clears: TN0059790 08/31/2023 Chlorine, total residual [DD] value 1.3 limit 1 mg/L
  - tie: TN0020541 01/31/2023 Chlorine, total residual [DC] value .5 limit 1 mg/L
  - tie: TN0026174 10/31/2022 Chlorine, total residual [DD] value .75 limit .7 mg/L
  - tie: TN0028827 12/31/2022 Chlorine, total residual [DC] value .5 limit 1 mg/L
  - tie: TN0062642 02/28/2023 BOD, carbonaceous [5 day, 20 C] [MK] value 20.5 limit 20 mg/L
  - tie: TN0064670 04/30/2023 BOD, 5-day, percent removal [MJ] value 64.5 limit 65 %
  - tie: TN0062499 04/30/2023 BOD, 5-day, 20 deg. C [MK] value 34.5 limit 34 mg/L
  - tie: TN0062138 10/31/2022 pH [MB] value 9.5 limit 9 SU
  - tie: TN0062138 05/31/2023 pH [MB] value 9.5 limit 9 SU
- bacteria values at the top of a Quanti-Tray range (value, qualifier, E90): 200.5 = -: 2; 2419.6 < E90: 6; 2419.6 = -: 1; 2419.6 = E90: 87; 2419.6 > -: 5; 2419.6 > E90: 72; 24196 = -: 6
- values at least 100 times their series median: 314 (of which E90: 128); apart from Quanti-Tray tops: 302
  - TN0020079 02/28/2023 E. coli [DD] 2419.6 #/100mL vs median 20.1
  - TN0020079 02/28/2023 E. coli [MK] 2419.6 #/100mL vs median 1.5
  - TN0020079 03/31/2023 E. coli [MK] 2419.6 #/100mL vs median 1.5
  - TN0020079 02/28/2023 E. coli [DD] 2419.6 #/100mL vs median 7.3
  - TN0020079 03/31/2023 E. coli [DD] 2419.6 #/100mL vs median 7.3
  - TN0020079 08/31/2025 E. coli [DD] 1119.9 #/100mL vs median 7.3
  - TN0020541 01/31/2024 E. coli [DD] 1986.3 #/100mL vs median 12
  - TN0020575 08/31/2025 E. coli [MM] 205 MPN/100mL vs median 2

Controls: all four planted cases flagged, their clean twins not; the DMR files' E90, D80 and D90 counts equal the violations file's.
DIFFERS: 529 reported statistics contradict their own definitions (an average or minimum above the maximum), at 157 of 308 plants
exit 1
