# The landscape: open-source software for sewers and wastewater

Checked 2026-10-27. GitHub facts (license, last commit, releases, open issues) were read
with `gh api` that day; everything else came from the project's own pages, the papers, the
eCFR and state rules. A claim marked *(snippet)* came only from a search-engine snippet of
a page that refused direct reading. Anything marked *(unchecked)* is from memory.

## The thread's claims, one by one

The thread is in [thread/2026-10-27-initial.md](thread/2026-10-27-initial.md).

| Claim | Verdict | What is true |
| --- | --- | --- |
| SWMM is public-domain EPA software for storm, sanitary and combined sewers | **Confirmed** | The USEPA repo's README says "released in the Public Domain". EPA's page lists 5.2.4 (2023-08-07) as current ([epa.gov](https://www.epa.gov/water-research/storm-water-management-model-swmm)) |
| Open Water Analytics maintains a version on GitHub, coordinating with EPA | **Corrected** | The OWA repo was transferred to **[pyswmm/Stormwater-Management-Model](https://github.com/pyswmm/Stormwater-Management-Model)** (MIT on top of public domain; last merge #430, 2026-07-15). [USEPA/Stormwater-Management-Model](https://github.com/USEPA/Stormwater-Management-Model) has merged no PR since October 2023; "PR for 5.3.0 release" (#179) has been open since April 2025. No documented coordination: fixes land in the fork first (fork #430 fixed the storage Newton-solver bug later filed against EPA as #227) |
| PySWMM reads and changes parameters and controls infrastructure while a simulation runs | **Confirmed** | Nearly the words of Tryby et al., *Environmental Modelling & Software* 179 (2024), [doi:10.1016/j.envsoft.2024.106114](https://doi.org/10.1016/j.envsoft.2024.106114). BSD-2, v2.2.0 released 2026-10-01 |
| It helped Cincinnati and Columbus cut tens of millions of gallons of CSO a year | **Corrected** | The sentence is from that 2024 EPA–Xylem paper. The control running in Cincinnati is **Xylem's commercial system**, which Xylem says cut 247 million gallons a year ([xylem.com](https://www.xylem.com/en-uk/making-waves/water-utilities-news/xylem-cincinnati-reduced-sewer-overflows/)). PySWMM was used to design and evaluate the control, not to run it. Per-city figures are behind Elsevier's paywall, unread |
| Open Storm: hardware, cloud platform, how-to guide at open-storm.org | **Corrected: dormant** | Its description is accurate as history (Bartos, Wong & Kerkez 2018, [doi:10.1039/C7EW00374A](https://doi.org/10.1039/C7EW00374A)). The open-storm GitHub org's last pushes were 2017–2021; open-storm.org now opens the U-M Digital Water Lab's build page. The lab is active under [kLabUM](https://github.com/kLabUM) |
| pystorms: a benchmark sandbox of control scenarios | **Confirmed, reviving** | Rimer et al. 2023, [doi:10.1016/j.envsoft.2023.105635](https://doi.org/10.1016/j.envsoft.2023.105635). GPL-3.0. PyPI still serves 1.0.0 (2022); branch `release/2.0.0` is 14 commits ahead of master as of 2026-09-13 |
| TEKSI wastewater (ex-QGEP): pipe attributes, plans, statistics; PostGIS model edited in QGIS; Swiss standards | **Confirmed** | [teksi/wastewater](https://github.com/teksi/wastewater), GPL-3.0, release 2026.1.1 (2026-10-02), committed today. Targets VSA-DSS 2020.1 and SIA405 |
| Development is moving from QGEP to TEKSI | **Confirmed, the move is done** | QGEP says it "is currently being replaced by TEKSI"; no QGEP commits since 2024-04; migration in [teksi/QGEP2TWW](https://github.com/teksi/QGEP2TWW). No US or German deployment found, and no effort to generalise the data model |
| QWAT is the drinking-water sibling | **Corrected** | Branded "TEKSI Water module (project QWAT)" but still in [github.com/qwat](https://github.com/qwat/QWAT) (GPL-2.0). 1.5.0.rc1 out for testing (2026-08-14). A French RAEPA extension exists |
| Sewer-ML: 1.3 million images, professional inspectors, three utilities, nine years | **Confirmed** | 1,300,201 images from 75,618 videos, 17 defect classes, three Danish utilities ([arXiv:2103.10895](https://arxiv.org/abs/2103.10895)) |
| Code, models and dataset are all public | **Corrected** | Code MIT (Bitbucket, dormant since 2021-12). The **dataset is CC BY-NC-SA 4.0** (non-commercial, share-alike) and comes through a request form. Whether the weights download was not checked |
| The benchmark left a lot of room | **Confirmed** | The paper's F2-CIW was 55.11%. CT-GNN (WACV 2022) added about 5 points; Hu et al. (IEEE TIM 2023) about 8; a 2026 preprint (Sewer-Transformer-ML, arXiv 2609.11375, not peer reviewed) claims 65.68%. The CodaLab leaderboard was not checked |
| QSDsan: sanitation and resource recovery design; BSM1; non-sewered sanitation | **Confirmed** | [QSD-Group/QSDsan](https://github.com/QSD-Group/QSDsan), UIUC/NCSA licence, v1.5.3. ASM1, ASM2d, mASM2d, ADM1, mADM1. BSM1 and BSM2 live in its sibling EXPOsan, which also carries the non-sewered systems. Takes outside PRs (an ASM2d fix merged 2026-10-12) |
| WaterTAP: DOE/NAWI, leans desalination, has biological wastewater models | **Confirmed, and more** | [watertap-org/watertap](https://github.com/watertap-org/watertap), BSD-3-style, 1.8.0 (2026-09-29). ASM1, ASM2d, ASM3, ADM1 and modified forms; a full BSM2 flowsheet. Open wastewater bugs: #1851 (BSM2 digester makes no methane), #1876 (BSM2 flowsheet unstable) |
| OpenPLC, FUXA and Rapid SCADA get used at pump stations and small plants | **Unverified** | No utility-documented use found for OpenPLC or FUXA. Rapid SCADA's own project list has one US landfill pumping to sewage treatment. **OpenPLC v3 is archived and end-of-life**; [Runtime v4](https://github.com/Autonomy-Logic/openplc-runtime) (MIT) and [Editor v4](https://github.com/Autonomy-Logic/openplc-editor) (GPL-3.0) replace it |
| The operator side is mostly proprietary | **Confirmed** | See [the operator side](#the-operator-side), below |

**Security, which the thread left out.** Water utilities are a CISA priority sector.
OpenPLC v3 has about 24 NVD CVEs, several from 2026, and, being end-of-life, will likely
leave them unfixed ([ICSA-25-273-05](https://www.cisa.gov/news-events/ics-advisories/icsa-25-273-05)).
The v4 repos have no SECURITY.md. FUXA published 23 GitHub advisories in 2026 alone, many of
them unauthenticated remote code execution, fixed between 1.2.10 and 1.3.3
([advisories](https://github.com/frangoteam/FUXA/security/advisories)). Rapid SCADA 5.x has
11 CVEs, and CISA recorded that the vendor "did not respond to CISA's attempts at
coordination" ([ICSA-24-011-03](https://www.cisa.gov/news-events/ics-advisories/icsa-24-011-03)).
None is a tool to put on a utility network without its own hardening.

## What the thread missed

### Collection and stormwater

| Project | Licence | Last activity | What it is |
| --- | --- | --- | --- |
| **[Giswater](https://github.com/giswater/plugin)** | GPL-3.0 | v4.17.6, 2026-10-07 | QGIS + PostGIS asset management for water and sewer networks, exporting to EPANET and SWMM (Giswater Association: BGEO and UPC Barcelona). The biggest omission: TEKSI's maintained peer, not tied to Swiss standards |
| [OWA EPANET](https://github.com/OpenWaterAnalytics/EPANET) | MIT | v2.3.5, committed 2026-10-26 | The drinking-water engine, same community as SWMM |
| [WNTR](https://github.com/USEPA/WNTR) | BSD-style | v1.5.0, 2026-07 | EPA/Sandia resilience analysis on EPANET models |
| [swmmio](https://github.com/pyswmm/swmmio) | MIT | PyPI 0.8.6, 2026-09 | SWMM files through pandas. GitHub Releases stuck at v0.6.0 |
| [swmm-toolkit](https://github.com/pyswmm/swmm-python) | CC0 + MIT/Apache | PyPI 0.17.0, 2026-02 | The compiled engine PySWMM sits on |
| [swmm_api](https://gitlab.com/markuspichler/swmm_api) | MIT | 0.4.74, 2026-06 | TU Graz's SWMM reader, writer and runner |
| **[SWMManywhere](https://github.com/ImperialCollegeLondon/SWMManywhere)** | BSD-3 | v0.2.4, 2026-10-01 | Builds a synthetic sewer network and SWMM model for any place from open data (Imperial College). 92 open issues |
| [generate_swmm_inp](https://github.com/Jannik-Schilling/generate_swmm_inp) | GPL-2.0 | 2026-06 | QGIS layers to and from SWMM |
| [Itzï](https://github.com/ItziModel/itzi) | GPL-2.0 | v26.6, 2026-07 | 2D flood model in GRASS, coupled to SWMM through pyswmm |
| [pipedream](https://github.com/mdbartos/pipedream) | GPL-3.0 | 2024-05 | Interactive hydrodynamic solver for pipe networks (from the Open Storm lineage) |
| [mikeio1d](https://github.com/DHI/mikeio1d) | MIT | v1.4.0, 2026-10 | Reads DHI MIKE+ results, a bridge out of proprietary models |
| [EPA SSOAP](https://github.com/USEPA/ssoap-toolbox) | EPA EULA, not open | README says **deprecated** | RDII (rain-derived infiltration and inflow) toolbox. EPA says its functions will move into a new SWMM GUI; no public repo yet. **No maintained open RDII tool exists** |

USACE's HEC-HMS and HEC-RAS are free executables without public source; only
[HEC-DSS](https://github.com/HydrologicEngineeringCenter/hec-dss) (MIT) is open.

### Inspection and condition

- **NASSCO PACP, the US defect-coding standard, is license-gated.** The exchange database
  and data dictionary go only to vendors who sign a licence, pay yearly and pass
  certification. An open "PACP-compatible" tool needs that licence. The European
  **EN 13508-2** is the practical open target: [kwb.en13508.2](https://github.com/KWB-R/kwb.en13508.2)
  (R, MIT, KWB Berlin) reads and writes it, and [QITV](https://github.com/cazitouni/QITV)
  (GPL-2.0) brings WinCan XML into QGIS. Nothing equivalent exists in Python.
- **Other image sets:** QV-Pipe and CCTV-Pipe ([videopipe.github.io](https://videopipe.github.io),
  licence unclear) and WRc's Ofwat-funded library of 27,262 images over 72 MSCC-linked defect
  codes, announced as free to download, licence not found.

### Treatment process models and the activated-sludge microbiome

| Project | Licence | Last activity | What it is |
| --- | --- | --- | --- |
| [bsm2-python](https://github.com/fau-evt/bsm2-python) | BSD-3 | 2025-07 | BSM1 and BSM2 in Python (FAU Erlangen) |
| [wwtmodels/Activated-Sludge-Models](https://github.com/wwtmodels/Activated-Sludge-Models) | **no licence file** | v3, 2025-02 | Lund/DTU reference ASM1, ASM2d, ASM3 in MATLAB |
| [PooPyLab](https://github.com/toogad/PooPyLab_Project) | GPL-3.0 | 2025-09 | ASM1 simulator, one developer |
| [ADM1F](https://github.com/lanl/ADM1F) | BSD-3 | 2024-07 | LANL's ADM1 in Fortran/PETSc |
| [MiDAS](https://midasfieldguide.org) | site CC BY-SA 4.0; database terms unchecked | MiDAS 5 (2024) | 16S reference database and field guide for activated sludge and digesters (Aalborg) |

The ifak Modelica WasteWater library has been archived since 2015; OpenWasteWater
(OpenModelica, CC0) went quiet in 2023.

### Field sensing and loggers

- **EnviroDIY** (Stroud Water Research Center): [ModularSensors](https://github.com/EnviroDIY/ModularSensors)
  (BSD-3, 69 open), the [Mayfly](https://github.com/EnviroDIY/EnviroDIY_Mayfly_Logger) open-hardware
  logger, and [Monitor My Watershed](https://github.com/WikiWatershed/monitor-my-watershed)
  (BSD-3, built on ODM2). The main maintained open logger stack for water.
- **No maintained open library turns a flume or weir level into flow** (Parshall flumes,
  V-notch weirs, ISO 9826 / ASTM D1941), though nearly every small plant measures flow that way.

### Data standards

| Standard | State | Note |
| --- | --- | --- |
| OGC SensorThings ([FROST-Server](https://github.com/FraunhoferIOSB/FROST-Server), LGPL-3.0, v2.8.2) | 1.1 current; 2.0's public comment closed 2026-01-18 | fieldmesh speaks 1.1 and noted that the 2.0 draft drops `resultQuality` |
| **[PHES-ODM](https://github.com/PHES-ODM/PHES-ODM)** | v3.0.1, 2026-09-17; **entered "long-term maintenance" in September 2026** | The open data model for wastewater surveillance. Its README says CC BY 4.0 and its LICENSE is CC BY-SA 4.0: they conflict |
| **[mWater Asset Standards](https://github.com/mWater/asset-standards)** | sanitation standard v1.0 issued 2026-08-21 | The first open, machine-readable vocabulary for sewer assets: 27 types (manhole, pump, tank, outfall, meter, ...), 211 attributes, JSON Schema, CC BY-SA 4.0. Its REVIEW-NEEDED.md lists open errata |
| [Brick](https://github.com/BrickSchema/Brick) 1.4.4 | active | **No sewer or wastewater classes**, only generic pumps, a check valve, a collection-basin level sensor and a grease interceptor. ASHRAE 223P leaves water out of scope |
| EPA WQX 3.0 | beta beside 2.0 | Water-quality exchange; [dataretrieval-python](https://github.com/DOI-USGS/dataretrieval-python) reads it |
| ODM2 | dormant since 2020 | Still the schema under Monitor My Watershed |

### Wastewater-based epidemiology

CDC's weekly wastewater data (data.cdc.gov `j9g8-acpt`, public domain, updated 2026-10-23);
[Freyja](https://github.com/andersen-lab/Freyja) (BSD-2, v2.0.7) for lineage mixtures, with
open issues on norovirus and RSV barcodes; CDC's [wwinference](https://github.com/CDCgov/ww-inference-model)
(Apache-2.0); ETH Zurich's V-pipe, COJAC and LolliPop; [EpiSewer](https://github.com/adrian-lison/EpiSewer)
(MIT). WastewaterSCAN's data is CC BY-NC 4.0.

### Global and non-sewered sanitation

The SFD (Shit Flow Diagram) generator has no public source. [Akvo Flow](https://github.com/akvo/akvo-flow)
(AGPL-3.0) is in maintenance. mWater is about 70% open by its own account, with the server
closed. Eawag's [Santiago.jl](https://github.com/santiago-sanitation-systems/Santiago.jl)
(AGPL-3.0) is quiet. ETH Zurich's [openwashdata](https://github.com/openwashdata) publishes
CC BY 4.0 data packages, faecal-sludge data among them.

### Telemetry at pump stations

[open62541](https://github.com/open62541/open62541) (OPC UA in C, MPL-2.0),
[Eclipse Milo](https://github.com/eclipse-milo/milo) (EPL-2.0), [Apache PLC4X](https://github.com/apache/plc4x)
(1.0.0 in 2026-09), Node-RED, [Scada-LTS](https://github.com/SCADA-LTS/Scada-LTS) and
Meshtastic are all active. **No utility-written deployment of Node-RED or Meshtastic at a
lift station was found**, only vendor marketing.

## The operator side

The thread's closing claim holds, and is sharper than it said.

**What exists in the open.** Nothing like a WIMS (Hach's water information management
system), no DMR calculator, no bench-sheet tool: GitHub turns up dead scrapers
([dssg/dmr2pgsql](https://github.com/dssg/dmr2pgsql), [potash/il-dmr](https://github.com/potash/il-dmr))
and one unlicensed [netdmr](https://github.com/phrac/netdmr). **The incumbent is the
spreadsheet.** Memphis's wastewater division publishes
[copy-n-launch-xlsx](https://github.com/City-of-Memphis-Wastewater/copy-n-launch-xlsx), "stable
spreadsheet copy, renaming, and dating, for municipal wastewater operator daily data entry".
Kentucky hands out a 14-sheet Excel workbook for monthly operating reports. General open
tools exist and nobody has fitted them to wastewater: [SENAITE](https://github.com/senaite/senaite.core)
for the lab (GPL-2.0), [Atlas CMMS](https://github.com/Grashjs/cmms) (AGPL-3.0) and openMAINT
for maintenance.

**What utilities buy.** Hach WIMS (descended from OPS SQL; run by Aquatic Informatics since
2021), AllMax Operator10, Klir Comply, AVEVA PI and Rockwell historians, Aquatic Informatics
AQUARIUS. None publishes a price. For lift stations, Mission Communications: one Florida
utility paid $23,446.80 for 42 stations for a year, about $47 a station a month (2015–16,
[FL PSC filing](https://www.floridapsc.com/library/FILINGS/2016/07551-2016/07551-2016.pdf), *(snippet)*).

### The numbers on a DMR, and why they differ between plants

- **Records.** 40 CFR 122.41(j): monitoring records for 3 years (sludge 5), each with date,
  place and time of sampling, who sampled, analysis dates, who analysed, the method and the
  result. Averages are arithmetic "unless otherwise specified by the Director in the permit"
  (122.41(l)(4)(iii)).
- **Holding times.** 40 CFR 136 Table II: coliform and E. coli 8 hours, BOD 48 hours, TSS 7
  days, cooled to 6 °C or less.
- **Two federal windows.** 122.2 defines weekly and monthly averages over the **calendar**
  week and month; 133.101 defines secondary treatment over **"7 consecutive days" and "30
  consecutive days"**. EPA's Permit Writers' Manual §5.1.3.2 only recommends writing calendar
  limits.
- **The states disagree on everything else.**

| | Week | Split week goes to | Non-detect counts as | Zero in a geometric mean | Rounding |
| --- | --- | --- | --- | --- | --- |
| EPA example permit language ([2020 webinar](https://19january2021snapshot.epa.gov/sites/static/files/2020-09/documents/dmrwebinar-slides.pdf)) | Sun–Sat | the month holding the Saturday | zero (below PQL) | — | **half to even** (1.05 → 1.0, 1.15 → 1.2) |
| **Tennessee** ([0400-40-05-.02](https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-0400-40-05-.02), read 2026-10-27) | Sun–Sat (62) | **the latter month** (62) | not said | **one** (35) | not said in the rule |
| Pennsylvania ([instructions](https://files.dep.state.pa.us/water/BPNPSM/WastewaterManagement/DMR/3800-FM-BPNPSM0463.pdf)) | — | the month with most of its days | the reporting limit, keeping "<" | one | **half up** |
| Montana ([2025 guide](https://deq.mt.gov/files/Water/WQInfo/Documents/DMR%20Compliance%20Guide/Compliance-Guidance-Final-October-2025.pdf)) | — | the month with 4 or more of its days | the reporting limit, keeping "<"; bacteria 1; TNTC > 20,000 | — | — |
| Oregon (per a Hach WIMS template) | — | — | 0 in arithmetic means; ½ DL in geometric; DL for bacteria | — | — |

Hach WIMS ships about 23 numbered definitions of a "week"
([Q10530](https://www.opssys.com/InstantKB/Article.aspx?id=10530)). No court dispute over any of
this was found: the divergence lives in permits and software settings.

**Binary arithmetic adds its own error on top** (measured here, [checks/](checks/README.md)):
rounding the binary64 value of an average gets EPA's own worked example 1.15 wrong under
either rule, and 1.05 wrong under EPA's half-even. Python's `round(1.15, 1)` and JavaScript's
`(1.15).toFixed(1)` both give 1.1. Against EPA's example copper limit of 1.1 mg/L, the rule
says violation and naive code says compliance. A geometric mean computed as
`exp(mean(log))` lands a few ulps above an exact limit for some sets
(`[4, 10000]` against 200 gives `200.0000000000001`).

### Electronic reporting and public data

- **40 CFR 127** makes DMRs electronic; phase 2 (due 2025-12-21) adds sewer overflow and
  bypass event reports. Tennessee requires NetDMR (over 99% of permittees, 2025 *(snippet)*).
- **The DMR schema is public** ([ICIS v5.15 XSDs](https://www.exchangenetwork.net/schema/ICIS/5/ICIS_Schema_v5.15.zip),
  January 2026). It carries **only the computed statistics, never the daily values**: the
  averaging happens in plant spreadsheets, and the only audit trail is the plant's own records.
- **CROMERR (40 CFR 3)** governs the state's or EPA's receiving system; its subpart on a
  plant's own electronic records is reserved, so 122.41(j) is what governs those.
- **EPA ECHO** serves every facility's DMR history: per-state, per-year files for FY2009–FY2026
  and a REST call per permit (`echodata.epa.gov/echo/eff_rest_services.download_effluent_chart?p_id=TN0024988`,
  64 columns with limits, statistical base, qualifiers and violation codes). An open tool can
  screen exceedances across every plant; it cannot recompute an average, because the daily
  values are not there. EPA's 2023 advisory calls late or faulty DMRs "the single largest
  source of SNC nationwide" ([npdesdmr.pdf](https://www.epa.gov/system/files/documents/2023-06/npdesdmr.pdf)).

### Money, scale and people

- **17,544 POTWs** serve 270.4 million people. Communities of 10,000 or fewer make up over
  60% of submissions but 12% of the population, and EPA says their needs are likely
  undercounted ([2022 CWNS](https://www.epa.gov/system/files/documents/2024-05/2022-cwns-report-to-congress.pdf)).
  The wastewater need is $345.7 billion, $47.1 billion of it in small communities.
- **About 8,000 lagoons** (2011), over 4,500 of them discharging without advanced treatment,
  often in towns under 3,000 ([Lagoon Action Plan](https://www.epa.gov/system/files/documents/2022-10/Lagoon%20Action_Plan_FINAL.pdf)).
- **Fiscal sustainability plans.** CWA §603(d)(1)(E) requires a Clean Water SRF borrower
  repairing, replacing or expanding a POTW to have or certify a plan with an inventory of
  critical assets, their condition, a water and energy conservation check, and a funded plan
  for maintenance and replacement ([33 USC 1383](https://www.law.cornell.edu/uscode/text/33/1383)).
  GAO found only 9 of 25 small utilities knew rehabilitation-versus-replacement costs for all
  their assets ([GAO-16-237](https://www.gao.gov/products/gao-16-237)). **EPA's free small-system
  tool, CUPSS, is abandoned**: legacy, no longer downloadable, built for Windows XP.
- **Operators.** Small utilities struggle to hire certified operators ([GAO-18-102](https://www.gao.gov/products/gao-18-102));
  the much-cited "30–50% retirement-eligible" figure is hard to trace.

### Tennessee

- Operator certification by plant grade (I–IV by points), a separate Biological/Natural
  Systems class for lagoons and wetlands, and collection Grades I and II (0400-49-01-.08, -.09).
- Secondary treatment's weekly BOD5 average is 40 mg/L, tighter than the federal 45. Lagoons
  have their own limits: 45/50/65 mg/L and 65% removal (0400-40-05-.09).
- Overflows are prohibited; a sewer overflow or unanticipated bypass is reported within 24
  hours and in writing within 5 days, with volume, duration, location and receiving water,
  through myTDEC Forms (0400-40-05-.07). Since 2022 a daily-maximum violation also triggers
  the 24-hour report.
- ECHO lists 384 Tennessee facilities typed as POTWs. One small plant (Alamo, TN0024988) shows
  156 limit violations over 2023–26, mostly ammonia and chlorine: a treatment problem, not a
  reporting one.
- **Not found:** TDEC's own DMR calculation instructions, or a Tennessee permit's Part I
  definitions, which is where rounding and non-detects would be settled.

## Not checked

- Per-city figures in the 2024 PySWMM paper (paywalled); the Sewer-ML leaderboard and weights.
- Licences: the WRc image library, QV-Pipe, MiDAS's database, the Mayfly hardware.
- Whether SensorThings 2.0 or ASHRAE 223P has been adopted since the spring.
- Whether Excel's `ROUND` and `GEOMEAN` behave like the checks' "15 significant digits"
  method. That method is a stand-in, not Excel.
- Any utility-documented use of OpenPLC, FUXA, Node-RED or Meshtastic.
- Whether EPA SWMM gives the same bits across thread counts and compilers: proposed, not run
  ([ideas.md](ideas.md#u1)).
