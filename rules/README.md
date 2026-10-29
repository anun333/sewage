# rules: laws, standards and terms that bear on this work

Checked 2026-10-29, from official sources. This is an inventory for our own work, not
legal advice.

| | |
| --- | --- |
| [laws.md](laws.md) | US federal statutes and regulations (Clean Water Act; 40 CFR 3, 122, 123, 127, 133, 136, 403 and 503), the CSO Control Policy, information-quality and open-source policy, OSHA confined spaces, the SDWA for EPANET, three states' DMR definitions, and the EU's recast Urban Wastewater Treatment Directive (2024/3019) |
| [standards.md](standards.md) | ISO C and IEEE 754 on contraction and conversions, OpenMP, glibc's libm accuracy, EPA's modelling QA guidance, the SWMM, EPANET and BSM specifications, design and condition standards (Ten States, EN 752, EN 13508-2, PACP), data formats (ICIS-NPDES, ECHO, SensorThings, WaterML, NWSS, PHES-ODM, Brick), lab methods, and OT security and safety |
| [terms.md](terms.md) | The licences and contribution rules of the 22 projects we use or contribute to, USEPA's GitHub terms, the terms on data we copy, the platforms we use (GitHub, PyPI, cfarm), and what our own repository owes |
| [manifests/](manifests/) | Every document downloaded: source URL, date, SHA-256 and terms (275 files, 149 MB). The files themselves are kept out of the repository; the manifests are enough to fetch and verify them again |

Paid and registration-only standards are listed with how to get them, not downloaded.

## What changes what we do

**The SWMM work ([U1](../ideas.md#u1)):**
- **The `gage.c` cast is out of range, which is not simply "undefined".** ISO C leaves it
  undefined (C17 6.3.1.4p1). gcc and clang on glibc advertise Annex F
  (`__STDC_IEC_559__`), and there F.4 makes the conversion raise "invalid" and return an
  unspecified value. So x86-64's INT_MIN and aarch64's INT_MAX are both allowed. The
  drafts in `upstream/swmm/` now say this ([standards.md](standards.md)).
- **FMA contraction and libm differences are within the C standard.**
  - Contraction is allowed and implementation-defined (C17 6.5p8, 7.12.2, F.7).
  - `<math.h>` accuracy is implementation-defined, and glibc doesn't aim for correct
    rounding.
  - So `-ffp-contract=off` is a project choice, and the only portable one, not a bug fix.
  - Digests should record the glibc version they were made with.
- **OpenMP gives no bitwise guarantee for reductions** (6.0 §7.6.7). SWMM's routing
  loops have none, which is why the thread count changed nothing.
- **EPA's own modelling QA guidance applies.** QA/G-5M (2002, still current) treats
  hardware and operating system as part of the model and asks for testing on several
  platforms. Its worked example accepts differences "usually less than ±0.1%"; user5
  differs by 13% between the published wheels.
- **The likely amplifier is SWMM's own convergence test.** Its head tolerance is 0.005 ft
  over at most 8 trials. Tracing trials per step on user5 is the next measurement.
- **Information-quality rules bind EPA, not us.** OMB's guidelines (67 FR 8452) call for
  results "capable of being substantially reproduced", M-19-15 asks for the code behind
  influential analyses, and EO 14303 asks for model code and uncertainty. So the
  issue argues against nrtest's own tolerance, and we file no Request for Correction
  ([laws.md](laws.md)).
- **Where SWMM output becomes regulatory numbers.**
  - Under the CSO Control Policy (CWA §402(q)), compliance is measured in overflow
    events per year and percent capture.
  - Under 40 CFR 122.38, Great Lakes CSO permittees publish modelled overflow volumes
    every year.
  - So report U1's differences in those units. The annual notices are public test cases
    that need no utility.

**The DMR work ([N1](../ideas.md#n1), [N2](../ideas.md#n2)):**
- **Significant noncompliance has an exact definition, and its ties need decimal
  arithmetic.** Under 40 CFR 123.45 Appendix A, a monthly average that "exceeds or
  equals" 1.4 or 1.2 times the limit counts. In binary floating point, 1.4 × 4.11 is
  5.7540000000000004, so an average of exactly 5.754 tests as below the threshold when
  it equals it. The regulation, EPA's 1996 design and ECHO's own page word the test
  differently ([laws.md](laws.md)).
- **The averages are defined differently.**
  - The federal monthly average averages each day first (122.2).
  - Tennessee averages all samples in the month.
  - Extra monitoring must be included (122.41(l)(4)(ii)).
  - Percent removal comes from 30-day averages (133.101(j)).
  - N1's state profiles need fields for each of these.
- **ICIS-NPDES stores values as `xsd:decimal`,** and ECHO distinguishes 186 statistical
  base codes. N1 should emit decimal strings that validate against the schema, round
  once, and key its profiles on the statistical base code ([standards.md](standards.md)).
- **A DMR is signed under penalty of law** (122.22(d); CWA §309(c)(4)). N1 stays a
  calculator that never submits, and N2 calls its output a screen of reported
  exceedances. Effluent data are public by law (CWA §308(b), 40 CFR 122.7), so
  publishing screens is fine.

**Contributing ([terms.md](terms.md)):**
- **No project we use requires a CLA, a DCO sign-off or copyright assignment.**
- **AI disclosure.**
  - WNTR's and IDAES's PR templates require an AI-use disclosure.
  - QSDsan accepts AI-assisted work but holds the contributor responsible for every
    line.
  - USEPA SWMM, EPANET and bsm2-python have no policy.
  - We now disclose on everything we post (see below).
- **USEPA's SWMM repo has no licence file or contribution terms.** The pyswmm fork
  records each contributor as MIT or Public Domain. Our patches are offered under CC0
  as well as MIT.
- **bsm2-python's contribution guide still points to FAU's GitLab, which is retired.**
  The GitLab repo says it moved to GitHub in 2025, and FAU's GitLab takes no outside
  sign-ups. GitHub is the place, but it has merged four PRs ever.
- **EDGI's ECHO_modules says GPL-3.0 in LICENSE and BSD-3 in its README.** Code for N2
  should be offered under BSD-3, which fits either, and we should ask which they mean.
- **mWater's asset standard is CC BY-SA 4.0 and Brick is BSD-3,** so a Brick extension
  can use mWater's names and codes but not its text.
- **NASSCO requires a licence even for tools that only output PACP codes.**

**This repository:**
- **Applied 2026-10-29:**
  - `THIRD_PARTY.md`, with bsm2-python's BSD-3 notice for the 24 values in
    `simulink200.csv`;
  - the HSL acknowledgement for the WaterTAP run;
  - `.gitignore` lines so the BSM1 report and IWA's files can't be committed.
- **Also applied, with the maintainer's agreement:**
  - the CC0 dedication for our SWMM changes;
  - an AI-assistance statement in the README and `THIRD_PARTY.md`;
  - a standard disclosure line on everything we post: "Drafted with an AI assistant
    (Claude), which also ran the builds and checks reported here; I read it before
    posting."

**Parked work:**
- **Lift stations are permit-required confined spaces** (29 CFR 1910.146; 1926.1201
  names them). Federal OSHA doesn't cover municipal workers; only the 29 State Plans do.
  A lift-station watch ([O1](../ideas.md#o1)) must never present its readings as
  fitness for entry.
- **Alarms must meet Ten States Standards §46.** Its 2026 edition is current, paid, and
  not read here.
- **The EU's recast directive (2024/3019) sets legal deadlines** for overflow
  monitoring, wastewater surveillance, quaternary treatment (2033, 2039 and 2045) and
  energy neutrality (2045). Transposition is due 2027-07-31.

## Not settled

- **Which C23 clause numbers apply.** N3220 and the later N3550 number them differently,
  and the published C23 wasn't read.
- **IEEE 754's clauses 10.4 and 11** are cited from memory; the standard is paid.
- **The 2001 SSO proposal.** Sources disagree on whether it was ever released.
- **40 CFR 131.41's bacteria formula** is printed without its exponent in both the eCFR
  and the annual CFR.
- **Pages that couldn't be read.** The cfarm rules page, IWA's site terms and parts of
  CDC's NWSS pages blocked automated reading.
