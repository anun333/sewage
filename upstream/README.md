# upstream

What has gone to other projects, and what is ready but not sent. Each text was read in
full and approved by the maintainer before it went out, and each carries a line saying an
AI assistant drafted it.

## Issues

| Thread | Posted | Subject | State (checked 2026-10-30) |
| --- | --- | --- | --- |
| [pyswmm/Stormwater-Management-Model#431](https://github.com/pyswmm/Stormwater-Management-Model/issues/431) | 2026-10-29 | Results change with FMA contraction and the C library's maths ([swmm/](swmm/README.md)) | No reply |
| [pyswmm/Stormwater-Management-Model#432](https://github.com/pyswmm/Stormwater-Management-Model/issues/432) | 2026-10-29 | The `.out` header's start date is one report step early ([swmm/](swmm/README.md)) | No reply |
| [watertap-org/watertap#1892](https://github.com/watertap-org/watertap/issues/1892) | 2026-10-29 | Reactor 5's oxygen is fixed at 0.449 g/m³ ([watertap/](watertap/README.md)) | No reply |
| [QSD-Group/EXPOsan#80](https://github.com/QSD-Group/EXPOsan/issues/80) | 2026-10-29 | BSM1 steady state off by up to 0.7% from exact constants and atomic weights ([exposan/](exposan/README.md)) | No reply |
| [USEPA/WNTR#584](https://github.com/USEPA/WNTR/issues/584) | 2026-10-29 | aarch64 Linux loads the x86-64 EPANET library ([wntr/](wntr/README.md)) | No reply; our offer to build the fix is the one comment |
| [USEPA/WNTR#585](https://github.com/USEPA/WNTR/issues/585) | 2026-10-29 | `WNTRSimulator` results change from run to run ([wntr/](wntr/README.md)) | No reply; our offer to build the fix is the one comment |
| [PHES-ODM/PHES-ODM#296](https://github.com/PHES-ODM/PHES-ODM/issues/296) | 2026-10-29 | LICENSE file against README ([phes-odm/](phes-odm/README.md)) | No reply |
| [edgi-govdata-archiving/ECHO_modules#140](https://github.com/edgi-govdata-archiving/ECHO_modules/issues/140) | 2026-10-29 | LICENSE (GPL-3.0) against README (BSD-3) ([echo-modules/](echo-modules/README.md)) | **Answered** 2026-10-29 by a maintainer: GPL v3 is the licence, and a README fix is welcome |

## Reviews

Posted 2026-10-29 as review comments, not as approvals or change requests.

| PR | Recommends |
| --- | --- |
| [USEPA/Stormwater-Management-Model#239](https://github.com/USEPA/Stormwater-Management-Model/pull/239) | Merge |
| [USEPA/Stormwater-Management-Model#234](https://github.com/USEPA/Stormwater-Management-Model/pull/234) | Merge |
| [USEPA/Stormwater-Management-Model#237](https://github.com/USEPA/Stormwater-Management-Model/pull/237) | Merge |
| [USEPA/Stormwater-Management-Model#226](https://github.com/USEPA/Stormwater-Management-Model/pull/226) | Changes |
| [OpenWaterAnalytics/EPANET#916](https://github.com/OpenWaterAnalytics/EPANET/pull/916) | Changes, after building and running it |
| [fau-evt/bsm2-python#8](https://github.com/fau-evt/bsm2-python/pull/8) | Merge |

## Ready, not sent

- **ECHO_modules:** the README fix its maintainer invited in #140
  ([echo-modules/pr-readme.md](echo-modules/pr-readme.md)).
- **bsm2-python:** an issue about its BSM1 rain influent file, which doesn't load
  ([bsm2-python/issue-rain-influent.md](bsm2-python/issue-rain-influent.md)).
- **mWater asset standards:** three additions to the unit errata mWater is considering,
  with exact values ([mwater/issue-units.md](mwater/issue-units.md)).
- **The BSM1 authors:** a note on the reference's two faults and five smaller slips
  ([bsm/note-to-authors.md](bsm/note-to-authors.md)); no recipient chosen yet.
- **WNTR:** both fixes we offered on #584 and #585, built and tested on x86-64 and
  aarch64, with PR texts ([wntr/pr-584.md](wntr/pr-584.md), [wntr/pr-585.md](wntr/pr-585.md)).
- **SWMM:** two patches, the build flag and the `gage.c` fix, with PR texts
  ([swmm/](swmm/README.md)). They go up if the fork's maintainers want them after #431.
  The build patch's MSVC half is now tested on Windows, with a follow-up comment for
  #431 ([swmm/comment-431-windows.md](swmm/comment-431-windows.md)). Also a comment for #419 and #420 (the zero roughness they report is documented
  behaviour) and an issue for a bug found while checking them, with a tested one-line
  fix ([swmm/issue-last-transect.md](swmm/issue-last-transect.md)).
- **WaterTAP:** a one-line fix for #1892 with its test values, tested; it goes up if the
  maintainers choose that fix ([watertap/](watertap/README.md)).
