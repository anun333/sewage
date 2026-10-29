# Rules that bear on this work, part A: laws and regulations

Checked 2026-10-29. Every item was read that day from the official source it links: the
eCFR (current to 2026-10-27), govinfo (the 2024 edition of the US Code, the Federal
Register, public laws), federalregister.gov's API, epa.gov, echo.epa.gov, osha.gov,
whitehouse.gov, state rule sites and the EU Publications Office. Quotes are from those
texts. A claim marked *(search)* came from a search result or a page summary and wasn't
read in the original. Technical standards (ISO, ASTM, Standard Methods and the like) are
in part B, and licences and platform terms in part C.

**Who is bound.** Most of what follows binds permittees, states or EPA, not us. Where a
rule binds an agency only, the item says so. This is a reading of public texts, not legal
advice.

## What changes what we do

Checked 2026-10-29; sources are in the sections below.

1. **The federal reproducibility standard applies to EPA, and our SWMM finding fits it
   ([U1](ideas.md#u1)).**
   - **The standard.** OMB's Information Quality Act guidelines define reproducibility
     as "capable of being substantially reproduced, subject to an acceptable degree of
     imprecision". The tolerated imprecision is smaller for information with more
     important impacts (67 FR 8452, 2002).
   - **Code and models.** OMB's M-19-15 (2019) says that computer code used for
     influential analyses "should be made available to the public". Executive Order 14303
     (2025) tells agencies to publish "the models and analyses (including, as applicable,
     the source code for such models)" behind influential information. It also tells
     them to document "how uncertainty propagates throughout any models".
   - **What to do.** All of these bind EPA, not us, and none names SWMM. In the U1 issue,
     state the platform drift against EPA's own nrtest tolerance and leave the question of
     what is acceptable to the maintainers. Don't file an information-quality Request for
     Correction: the fix belongs upstream.
2. **SWMM output becomes regulatory numbers in two places.**
   - **The CSO Control Policy** (1994). CWA §402(q) requires every permit, order or
     decree for a combined sewer issued after 2000-12-21 to conform to it. Its
     "presumption approach" counts overflow events (an average of four a year) or percent
     capture by volume (85%). Models "should include appropriate calibration and
     verification with field measurements".
   - **40 CFR 122.38.** Great Lakes Basin CSO permittees publish each overflow's
     "measured or estimated volume" every year. A permittee that uses a model must
     describe its calibration. Permittees serving 75,000 or more must reassess it at least
     every 5 years.
   - **What to do.** Report U1's differences in those terms: overflow events per year,
     percent capture and volume per event, as well as maximum relative difference. The
     Great Lakes annual notices are public, so they are a test case that needs no utility.
3. **The ECHO screen ([N2](ideas.md#n2)) has a written definition to implement.**
   - **The rule.** 40 CFR 123.45 Appendix A defines Category I effluent violations: a
     monthly average that "exceed[s] or equal[s]" 1.4 times the limit (Group I
     pollutants) or 1.2 times (Group II) in two or more months of six, or any exceedance
     in four or more months of six. A DMR is a reporting violation when it isn't
     submitted "within 30 days" of its due date.
   - **The tie trap.** The comparison at the tie must be done in decimal. A check here
     over limits from 0.01 to 20.00, in steps of 0.01, at both TRCs found that a value
     exactly equal to TRC × limit is judged *below* the threshold in binary floating point
     in 92 of 4,000 cases: for a limit of 4.11, 1.4 × 4.11 comes out as
     5.7540000000000004.
   - **The definitions disagree.** EPA's 1996 SNC design, which ECHO still cites, says
     "40% exceedance" and "30 or more days late". ECHO's own page says "more than 30 days
     late". Pretreatment SNC (40 CFR 403.8) is a different test again.
   - **Timing.** From 2026-12-21, EPA must build its public noncompliance reports from
     facility-submitted phase-2 data as well (123.45). Read what those reports already
     publish before building a duplicate.
4. **DMR arithmetic has more rule fields than our table lists ([N1](ideas.md#n1)).**
   - **Per day or per sample.** The federal monthly average is a mean of *daily
     discharges*, each day averaged first (122.2). Tennessee's "monthly average
     concentration" is "the arithmetic mean of all samples" in the month (0400-40-05-.02
     (52)). The two differ whenever a day has more than one sample.
   - **Extra samples count.** Results from monitoring done more often than the permit
     requires must go into the DMR calculation (122.41(l)(4)(ii)).
   - **Percent removal** comes from the 30-day *average* influent and effluent, not from
     an average of daily removals (133.101(j)).
   - **Tennessee's own geometric-mean definition** names both forms, the nth root of the
     product and "the antilog of the arithmetic mean of the logarithms" (definition 35).
     The second is the float formula our check caught landing above a limit.
   - **What to do.** Add per-day or per-sample averaging, the treatment of extra samples
     and the percent-removal method to N1's profile fields.
5. **The person who signs a DMR certifies it "under penalty of law"** (40 CFR 122.22(d)),
   and a knowingly false statement is a crime (CWA §309(c)(4)). Any citizen may sue over
   a violation after 60 days' notice (§505).
   - **For N1.** Stay a calculator that shows its rule profile, inputs and arithmetic.
     It must never submit, and never word its output as a finding of compliance.
   - **For N2.** Call results "reported exceedances" and "screens", not violations.
6. **Effluent data are public by law, and some neighbouring data are not.**
   - **Public.** CWA §308(b) makes effluent data available to the public, and 40 CFR
     122.7 denies any confidentiality claim for permits, applications and effluent data.
     Republishing ECHO-derived DMR screens is therefore on firm ground.
   - **Not public.**
     - Drinking-water risk and resilience assessments under SDWA §1433 stay with the
       utility: only a certification goes to EPA.
     - Department of Defense NPDES data may be withheld as critical infrastructure
       information (40 CFR 127.1(c)).
   - **What to do.** Don't ask a utility for its assessment, or for anything else it
     treats as security information.
7. **Wet wells, lift stations and sewers are permit-required confined spaces**
   (29 CFR 1910.146, and 1926.1201, which names "lift stations" and "sewers").
   - **Who is covered.** Federal OSHA doesn't cover state or local government workers
     (29 USC 652(5)). Municipal sewer crews have OSHA-standard protection only through a
     State Plan, of which there are 29 (osha.gov).
   - **For the parked lift-station watch ([O1](ideas.md#o1)).** It must never present a
     level or alarm reading as fitness for entry, which is decided by atmospheric testing
     under the employer's permit program. Installing any sensor in a wet well is itself an
     entry.
8. **The EU's recast Urban Wastewater Treatment Directive (EU) 2024/3019** creates legal
   demand for what several of the projects do. Member states must transpose it by
   2027-07-31. It requires:
   - storm-water overflow monitoring whose results may feed models (Art. 21), and a list
     of the agglomerations where overflows exceed 2% of the collected load (Art. 5);
   - integrated plans for the drainage areas of agglomerations of 100,000 p.e. and above,
     by 2033;
   - a national system for wastewater surveillance (SARS-CoV-2, poliovirus, influenza,
     emerging pathogens), with antimicrobial resistance monitored in agglomerations of
     100,000 p.e. and above;
   - quaternary treatment for micropollutants at plants of 150,000 p.e. and above, by
     2045;
   - energy audits, and energy neutrality at national level by 2045.

   bsm2-python, QSDsan's energy accounting and Freyja-type surveillance tools now have
   users with legal deadlines in Europe.

Also worth knowing:
- **No regulation names our tools or ideas.** No section of the CFR contains "SWMM",
  "Storm Water Management Model", "EPANET", "Benchmark Simulation Model", "wastewater
  surveillance", "fiscal sustainability plan" or "capacity, management, operation" (eCFR
  full-text search, 2026-10-29; as a control, "geometric mean" returns 158 sections and
  "combined sewer overflow" 26).
- **Their regulatory weight is indirect.** It comes through permits, decrees, policies
  and the statute's text.

## Federal water law

### The Clean Water Act

The CWA is issued by Congress, free, and was read in the 2024 edition of 33 USC chapter 26
([govinfo PDF](https://www.govinfo.gov/content/pkg/USCODE-2024-title33/pdf/USCODE-2024-title33-chap26.pdf),
downloaded). Checked 2026-10-29.

| Section (33 USC) | What it governs | Touches | What we should consider or do |
| --- | --- | --- | --- |
| §301 (1311) | Effluent limitations; POTWs must meet secondary treatment (301(b)(1)(B)); marine waivers (301(h)) | N1, N2 | Background. The numbers come through 40 CFR 133 and 125 |
| §304 (1314) | 304(d) defines secondary treatment; 304(h) test procedures; 304(a) criteria | N1, N3 | Background for 40 CFR 133 and 136 |
| §307 (1317) | Toxic and pretreatment standards | N2 | Industrial users have their own SNC test (40 CFR 403.8). Keep it apart from NPDES SNC |
| §308 (1318) | Records, reports, inspections; 308(b) makes effluent data public | N2 | The legal footing for publishing screens of DMR data |
| §309 (1319) | Enforcement; 309(c)(4) makes a knowingly false material statement or tampering a crime | N1 | N1 prepares numbers and a person signs them. Its output must let the signer see every step. Civil maximum $68,445 per day per violation for penalties assessed from 2025-01-08 (40 CFR 19.4) |
| §402 (1342) | NPDES permits; 402(b) state programs; 402(p) stormwater and MS4s; **402(q)** makes permits and decrees for combined sewers "conform to" the 1994 CSO Control Policy; 402(s) integrated plans (2012 framework) | U1, N2 | 402(q) is why the CSO policy's modelling expectations bind. See the policy below |
| §405 (1345) | Sewage sludge use and disposal | O2 | The standards are 40 CFR 503 |
| §505 (1365) | Citizen suits after 60 days' notice to EPA, the state and the violator | N2 | Screens can feed litigation. Label them as screens of reported data, with ECHO's caveats |
| §603(d)(1)(E) (1383) | A CWSRF borrower repairing, replacing or expanding a treatment works must "develop and implement a fiscal sustainability plan" with the four elements, **or "certify"** that it has one | O7 | The statute itself allows self-certification, which supports O7's caution. The plan appears in no regulation (eCFR search above) |
| §109 (1259) | Training grants for operators | — | The CWA funds operator training but has no operator-certification requirement. Wastewater certification is state law (below) |

### Regulations (40 CFR)

These are issued by EPA, free and public domain, and were downloaded from the
eCFR's point-in-time API as of 2026-10-27 (an editorial compilation; the annual CFR is the
official edition). Checked 2026-10-29.

- **Part 122, NPDES** ([eCFR](https://www.ecfr.gov/current/title-40/part-122)).
  - **Governs:** permits and their standard conditions.
  - **Touches:** N1, N2, N3 and U1.
  - **Consider or do:**
    - **122.2.** Average weekly and monthly limits are means of "daily discharges" over
      the *calendar* week and month. A daily discharge is the day's average for
      concentration and the day's total for mass. N1's default should average within the
      day first.
    - **122.7.** Effluent data can't be claimed confidential.
    - **122.22(d).** The certification text the signer makes "under penalty of law"
      (lesson 5).
    - **122.26 and 122.34, stormwater and MS4s.** A large or medium MS4's application
      must include "estimates of the annual pollutant load" and "event mean
      concentration" at its outfalls (122.26(d)(2)(iii)(B)). This is model territory, but
      no model is required by name.
    - **122.38, Great Lakes CSO notification (2018, effective 2018-02-07).**
      Permittees give notice within 4 hours and supplemental notice within 7 days, and
      publish an annual notice by May 1. The modelling clause is quoted in lesson 2. Use
      these notices as public test cases for U1.
    - **122.41(j).** Records rules, already in [landscape](landscape.md#the-numbers-on-a-dmr-and-why-they-differ-between-plants).
    - **122.41(l)(4)(ii)–(iii).** Extra samples count, and averages are arithmetic
      unless the permit says otherwise.
    - **122.41(l)(6)–(7).** The 24-hour and 5-day reports. Since phase 2, reports of
      sewer overflows and bypasses carry the data in Part 127's Appendix A.
    - **122.41(m) and (n).** Bypass and upset. An upset defence needs "properly signed,
      contemporaneous operating logs", which is what N3's append-only log would produce.
    - **122.44(i)(1)(iv).** The sufficiently sensitive methods rule (below).
    - **122.45(d).** POTW limits are weekly and monthly averages.
- **Part 123, state program requirements** ([eCFR](https://www.ecfr.gov/current/title-40/part-123)).
  - **Governs:** what an authorized state must have, and EPA's noncompliance reports.
  - **Touches:** N2.
  - **Consider or do:**
    - **123.25.** Lists which Part 122 provisions every state program must carry, so
      state rules can be stricter but not weaker.
    - **123.45 and its Appendix A.** These are the definitions to implement in N2
      (lesson 3). Since 2022-12-21, EPA must publish quarterly and annual noncompliance
      reports online from DMR data, and from 2026-12-21 it must add facility-submitted
      phase-2 data.
- **Part 124, procedures** ([eCFR](https://www.ecfr.gov/current/title-40/part-124)).
  - **Governs:** draft permits, public notice and comment.
  - **Touches:** nothing yet.
  - **Note:** draft permits get at least 30 days of public comment, and "any interested
    person may submit written comments" (124.10, 124.11). We have no plan to comment on
    permits. Doing so would be outward-facing and would need review first.
- **Part 125, criteria and standards** ([eCFR](https://www.ecfr.gov/current/title-40/part-125)).
  - **Governs:** technology-based limits (subpart A) and 301(h) marine waivers for POTWs
    (subpart G).
  - **Touches:** N2.
  - **Note:** a POTW with a 301(h) waiver has limits below secondary treatment. Flag such
    plants in the screen rather than scoring them against Part 133 (how many hold one was
    not checked).
- **Part 127, NPDES electronic reporting** ([eCFR](https://www.ecfr.gov/current/title-40/part-127)).
  - **Governs:** which reports are electronic, and since when.
  - **Touches:** N2.
  - **Consider or do:**
    - **Dates.** DMRs have been electronic since 2016-12-21. Sewer overflow and bypass
      reports, MS4 reports, pretreatment annual reports and state-program biosolids
      reports were due 2025-12-21.
    - **Gaps.** EPA may approve alternative deadlines "in no event beyond December 21,
      2028" (127.24(e)–(f)), so overflow event data in ECHO may be missing for some
      states until then. Check EPA's list of approved alternative deadlines before
      reading an absence as zero overflows *(the list itself was not read)*.
- **Part 130 and Part 131, water quality planning and standards** ([130](https://www.ecfr.gov/current/title-40/part-130),
  [131](https://www.ecfr.gov/current/title-40/part-131)).
  - **Governs:** TMDLs (130.7) and water quality standards.
  - **Touches:** U1, and the geometric-mean check.
  - **TMDLs.** They are often built with watershed and sewer models, but the rules name
    none.
  - **131.41.** It promulgates bacteria criteria for coastal recreation waters in states
    that didn't adopt their own: E. coli 126 per 100 ml as a geometric mean, plus single
    sample maxima.
  - **The footnote and the table disagree.** The footnote prints the formula as "geometric
    mean * 10 + (confidence level factor * log standard deviation)". The exponent is lost
    in both the eCFR and the 2025 annual CFR: in the official PDF, "10", "+" and the
    bracket sit on one baseline. Recomputing GM × 10^(factor × SD) with the stated
    factors gives 235.7, 299.5, 409.6 and 575.9 for E. coli, and 104.7, 159.2, 275.5 and
    500.1 for marine enterococci. The table prints 235, 298, 409, 575 and 104, 158, 276,
    501. No single rounding rule reproduces them all.
  - **What to do.** This is a small, checkable note in the spirit of
    [checks/](checks/README.md). Check the 2004 rule (69 FR 67242, the source the eCFR
    gives for 131.41) and the 1986 criteria document before raising it anywhere *(neither
    was read)*.
- **Part 133, secondary treatment** ([eCFR](https://www.ecfr.gov/current/title-40/part-133)).
  - **Governs:** BOD5, SS and pH floors for POTWs.
  - **Touches:** N1.
  - **Consider or do:**
    - **Windows.** "7 consecutive days" and "30 consecutive days" windows (133.101(a)–(b)),
      against Part 122's calendar windows. This is already noted in landscape.
    - **Percent removal** comes from 30-day averages (133.101(j)).
    - **"Consistently achievable"** is the 95th percentile of 30-day averages over at least
      two years, with the 7-day value 1.5 times that (133.101(f)). That is a statistic N1
      could compute for permit renewals, but it is out of scope for now.
- **Part 136, test procedures** ([eCFR](https://www.ecfr.gov/current/title-40/part-136)).
  - **Governs:** approved methods, Table II holding times, method detection limits
    (Appendix B, Revision 2) and laboratory QA/QC (136.7).
  - **Touches:** N1, N3.
  - **Consider or do:**
    - **Table II footnote 2.** When compositing would compromise a sample, the grabs
      "must be analyzed separately and the concentrations averaged". That is another
      arithmetic mean for N1 and N3.
    - **136.7.** For methods without QA/QC of their own, labs must document twelve QC
      elements, "control charts" among them. N3 should record the batch and QC links, not
      just the result.
    - **Methods updates.** The last final update was the 2024 Methods Update Rule
      (89 FR 27288, effective 2024-06-17). Methods Update Rule 22 (PFAS and PCB
      congeners) was proposed 2025-01-21 (90 FR 6967) and had no final rule in the Federal
      Register on 2026-10-29.
- **The sufficiently sensitive methods rule** (79 FR 49001, 2014-08-19, effective
  2014-09-18; [govinfo](https://www.govinfo.gov/content/pkg/FR-2014-08-19/pdf/2014-19265.pdf),
  downloaded).
  - **Governs:** permittees must use a Part 136 method whose minimum level is at or below
    the limit, or the most sensitive approved method (122.44(i)(1)(iv)).
  - **Touches:** N1.
  - **What to do.** How often a result is a non-detect *near a limit* depends on this
    rule. N1's non-detect handling should record the minimum level used, not only "<".
- **Part 403, pretreatment** ([eCFR](https://www.ecfr.gov/current/title-40/part-403)).
  - **Governs:** POTW pretreatment programs and industrial users.
  - **Touches:** N2.
  - **Consider or do:**
    - **SNC for industrial users is a different test.** It is chronic when 66% or more
      of a parameter's measurements over 6 months exceed the limit. It is technical when
      33% or more "equal or exceed" TRC × limit, with a TRC of 1.4 for BOD, TSS and fats,
      oil and grease and 1.2 for everything else except pH (403.8(f)(2)(viii)).
    - **Annual notice.** The POTW must publish its SNC industrial users at least once a
      year in a newspaper.
    - **Keep the tests apart.** Don't let N2 conflate this with NPDES Category I.
- **Part 503, biosolids** ([eCFR](https://www.ecfr.gov/current/title-40/part-503)).
  - **Governs:** land application, surface disposal and incineration of sewage sludge.
  - **Touches:** O2, and the geometric-mean check.
  - **Consider or do:**
    - **A strict-inequality geometric mean.** Class B Alternative 1 needs seven samples
      whose fecal coliform "geometric mean … shall be less than" 2,000,000 MPN or CFU per
      gram of total solids (503.32(b)(2)). That makes a second federal geometric mean,
      with a *strict* inequality, for the geometric-mean test set.
    - **Records and reports.** Records are kept 5 years (503.17). POTWs of 1 MGD or
      more, or serving 10,000 or more, report each February 19 (503.18).
    - **Who the permitting authority is.** Only nine states hold EPA's biosolids
      authorization: AZ, ID, MI, OH, OK, SD, TX, UT and WI, with MI and OH only in part.
      Elsewhere EPA remains the biosolids permitting authority (EPA authorization table,
      below).
- **Part 3, CROMERR** ([eCFR](https://www.ecfr.gov/current/title-40/part-3)).
  - **Governs:** electronic reporting to EPA (subpart B) and state systems (subpart D).
    Subpart C is "[Reserved]".
  - **Touches:** N1, N3.
  - **Note:** confirms landscape. A plant's own electronic records fall under 122.41(j),
    not CROMERR, and N1 is not a submission system.
- **Part 35 subpart K, CWSRF** ([eCFR](https://www.ecfr.gov/current/title-40/part-35/subpart-K)).
  - **Governs:** state revolving fund administration (1990, last amended 2014).
  - **Touches:** O7.
  - **Note:** it has no text on fiscal sustainability plans. The requirement lives only in
    §603(d)(1)(E) and EPA guidance.

### Policies that act like rules

Checked 2026-10-29.

- **The Combined Sewer Overflow Control Policy** (EPA, 1994; FR Doc 94-9295, 59 FR 18688;
  [govinfo](https://www.govinfo.gov/content/pkg/FR-1994-04-19/html/94-9295.htm), free,
  downloaded).
  - **Governs:** the nine minimum controls, and the long-term control plan with its
    characterization, monitoring and modelling.
  - **Touches:** U1.
  - **Key text:**
    - "Use of models should include appropriate calibration and verification with field
      measurements".
    - The presumption approach: "no more than an average of four overflow events per
      year" (the permitting authority may allow two more), or capture of "no less than
      85% by volume", or an equivalent mass removal.
    - At the permitting authority's discretion, jurisdictions under 75,000 people "may
      not need to complete each of the formal steps", modelling among them.
  - **What to do.** See lesson 2. A difference of a few percent in a model's overflow
    volume can move an event across the count or a system across 85%.
- **Sanitary sewer overflows and CMOM: no rule exists.**
  - **The 2001 proposal.** EPA's 2010 notice says the 2001 proposed rule "was never
    formally released to the public or sent to the Federal Register for publication, but
    instead was withdrawn in January 2001 for further review" (75 FR 30395,
    [govinfo](https://www.govinfo.gov/content/pkg/FR-2010-06-01/pdf/2010-13098.pdf),
    downloaded). There is no official text to download.
  - **A conflict.** A utility association's archive says EPA "signed and released" it on
    2001-01-05 *(search)*. The official notice wins.
  - **EPA's position now.** SSOs reaching waters of the US "are prohibited unless
    authorized by a NPDES permit" ([EPA's SSO page](https://www.epa.gov/npdes/sanitary-sewer-overflows-ssos),
    updated 2026-04-13, not downloaded).
  - **The CMOM guide.** EPA's *Guide for Evaluating CMOM Programs* (EPA 305-B-05-002,
    2005; [epa.gov](https://www.epa.gov/sites/default/files/2015-10/documents/cmom_guide_for_collection_systems.pdf),
    downloaded) is guidance for inspectors. Its pump-station checks are alarm
    verification, wet-well level settings, telemetry and inspection frequency. It also
    tells inspectors to "refrain from entering confined spaces".
  - **What to do.** For O1, that guide is the closest thing to a federal specification
    for what a lift-station monitor should show. CMOM duties reach utilities through
    consent decrees and state permits, not a federal rule.
- **NPDES significant noncompliance as ECHO computes it.**
  - **The basis.** ECHO says SNC follows EPA's *General Design for SNC Redefinition
    Enhancement in PCS* (1996-12-16; [echo.epa.gov](https://echo.epa.gov/system/files/EPA_1572.pdf),
    scanned, downloaded) and the codes in its data dictionary
    ([echo.epa.gov](https://echo.epa.gov/help/reports/dfr-data-dictionary), downloaded).
  - **Touches:** N2.
  - **What to do.** Implement the regulation's text (123.45 Appendix A) and record where
    the 1996 design and ECHO's page differ (lesson 3). Report suspected ECHO errors
    through ECHO's "Report Data Error" link, the channel EPA provides, not through an
    information-quality complaint.

## Federal rules about data, models and code

Checked 2026-10-29 against the linked texts.

| Item | Issued by | What it requires, and of whom | Touches | What we should consider or do | Link (all free, all downloaded) |
| --- | --- | --- | --- | --- | --- |
| **Information Quality Act**, §515 of Pub. L. 106-554 (2000), a note to 44 USC 3516 | Congress | OMB must issue guidelines. Each agency must issue its own and set up a way for "affected persons" to "seek and obtain correction" of information it disseminates. **Binds agencies only** | U1, N2 | The correction route exists, but our route is upstream issues. See EPA's guidelines below | [govinfo](https://www.govinfo.gov/link/uscode/44/3516?link-type=pdf) |
| **OMB IQA guidelines**, 67 FR 8452 (2002-02-22, effective 2002-01-03) | OMB | Defines "influential" information ("clear and substantial impact"). For influential analytic results, agencies must give "sufficient transparency about data and methods that an independent reanalysis could be undertaken by a qualified member of the public". Reproducibility is "subject to an acceptable degree of imprecision", tighter for more important information. **Binds agencies** | U1, U6 | Gives the vocabulary for U1: same inputs, same code, different platform, results outside EPA's own tolerance. Don't claim SWMM "violates" anything. Whether a model release is "information" EPA "disseminates" isn't settled in these texts | [govinfo](https://www.govinfo.gov/content/pkg/FR-2002-02-22/pdf/R2-59.pdf) |
| **OMB M-19-15**, *Improving Implementation of the IQA* (April 2019) | OMB | Code behind an analysis "should be made available to the public for further analysis". For model results, "reproducibility requires, at minimum, transparency about the specific methods, design parameters, equations or algorithms, parameters, and assumptions". Complex models under economically significant rules get peer review. **Binds agencies** | U1, U6 | Supports asking EPA to document SWMM's floating-point assumptions (FMA, libm) as part of "methods" | [whitehouse.gov](https://www.whitehouse.gov/wp-content/uploads/2019/04/M-19-15.pdf) |
| **OMB Peer Review Bulletin**, 70 FR 2664 (2005-01-14) | OMB | Influential scientific information, which by definition includes "models", gets peer review. Assessments with over $500 million a year of impact, or that are novel or controversial, get more. **Binds agencies** | U1 | Applies to EPA's own work, not to a city's long-term control plan model | [govinfo](https://www.govinfo.gov/content/pkg/FR-2005-01-14/pdf/05-769.pdf) |
| **EPA Information Quality Guidelines**, EPA/260R-02-008 (October 2002, with addenda) | EPA | Covers "any communication or representation of knowledge … in any medium". Excludes research a researcher publishes on their own account. The guidelines say they are "not a regulation" and are "non-binding". Requests for correction: the complainant carries the burden, and EPA's page wants requesters to be directly affected | U1, N2 | We are probably not "affected persons" for SWMM. Use upstream issues and ECHO's error link. Keep the IQG in mind only if EPA publishes model results we can show are wrong | [epa.gov](https://www.epa.gov/sites/default/files/2020-02/documents/epa-info-quality-guidelines_pdf_version.pdf) |
| **Executive Order 14303**, *Restoring Gold Standard Science*, 90 FR 22601 (signed 2025-05-23) | President | Agencies must publish the data, analyses and "models and analyses (including, as applicable, the source code for such models)" behind influential scientific information (§4(b)). Employees must document "how uncertainty propagates throughout any models" (§4(c)). Enforcement risk models are excepted. **Binds agencies** | U1 | The strongest current federal statement that EPA model code should be public and its uncertainty stated. EPA's 2026 implementation report doesn't mention models' source code or SWMM (searched). Cite it in U1 as context only | [govinfo](https://www.govinfo.gov/content/pkg/FR-2025-05-29/pdf/2025-09802.pdf); [EPA 2026 report](https://www.epa.gov/system/files/documents/2026-09/gold-standard-science-2026-report_0.pdf) |
| **EPA, *Guidance on the Development, Evaluation, and Application of Environmental Models*** (EPA/100/K-09/003, 2009) | EPA, Council for Regulatory Environmental Modeling | Code verification "tests whether the code performs according to its design specifications". "Independent testing of the code … can be useful". "It does not impose legally binding requirements" | U1, U6 | Our checks are what this guidance calls independent code testing. Quote it in the U1 and U6 write-ups | [epa.gov](https://www.epa.gov/sites/default/files/2015-04/documents/cred_guidance_0309.pdf) |
| **EPA "transparency" rule** (40 CFR part 30), 86 FR 469 (2021-01-06), removed by 86 FR 29515 (effective 2021-05-28) | EPA | Would have weighted the science behind significant rules by public availability of data and models. Removal "effectuates the vacatur … ordered by the United States District Court for the District of Montana". No successor rule in the Federal Register on 2026-10-29 | — | Nothing binding now. Don't cite it as current | [govinfo](https://www.govinfo.gov/content/pkg/FR-2021-06-02/pdf/2021-11317.pdf) |
| **Evidence Act, Title II (OPEN Government Data Act)**, Pub. L. 115-435 (2019-01-14), and **OMB M-25-05** (2025-01-15) | Congress; OMB | Agency data assets are open by default: machine-readable, open format, open licence, listed in a comprehensive data inventory. M-25-05 replaces M-13-13. **Binds agencies** | N2 | ECHO's bulk files are open government data assets. Our derived tables can carry the same openness. No obligation falls on us | [Act](https://www.govinfo.gov/content/pkg/PLAW-115publ435/pdf/PLAW-115publ435.pdf); [M-25-05](https://www.whitehouse.gov/wp-content/uploads/2025/01/M-25-05-Phase-2-Implementation-of-the-Foundations-for-Evidence-Based-Policymaking-Act-of-2018-Open-Government-Data-Access-and-Management-Guidance.pdf) |
| **Federal Source Code Policy, OMB M-16-21** (2016-08-08) | OMB | Custom code must be available for government-wide reuse and inventoried on code.gov. A three-year pilot required releasing at least 20% of new custom code as open source. It encourages federal staff to contribute "to existing OSS projects". No rescission found *(search)* | U1, U2 | Explains why EPA publishes on GitHub. It doesn't oblige EPA to merge outside work, which fits upstream-first to the pyswmm fork | [archives](https://obamawhitehouse.archives.gov/sites/default/files/omb/memoranda/2016/m_16_21.pdf) |
| **SHARE IT Act**, Pub. L. 118-187 (2024-12-23) | Congress | Within 210 days, agencies must store custom-developed code in a public or private repository that federal employees can access, and make its metadata public. It requires sharing across government, **not open-source release** | U1, U6 | Little direct effect on us. New EPA code should at least have public metadata | [govinfo](https://www.govinfo.gov/content/pkg/PLAW-118publ187/pdf/PLAW-118publ187.pdf) |
| **EPA, *Open Source Software and Code Repositories*** (developer page, updated 2026-03-10) | EPA | Cites M-16-21 and EPA's System Life Cycle Management procedure. Public repositories need a LICENSE.md, a README and the EPA disclaimer ("as is"; "EPA has relinquished control of the information"). EPA "usually recommends the use of the MIT license". Repository administrators review submissions | U1, U2 | The disclaimer means EPA takes no responsibility for released code, so a fix lands only if someone merges it. Licence questions are in part C | [epa.gov](https://www.epa.gov/developers/open-source-software-and-code-repositories) |
| **17 USC 105** | Congress | No copyright in "any work of the United States Government" | U1 | Why SWMM is public domain. Shared with part C | [govinfo](https://www.govinfo.gov/link/uscode/17/105?link-type=pdf) |

## Drinking water, for EPANET (briefly)

Checked 2026-10-29.

- **SDWA §1433 as rewritten by AWIA 2018 §2013** (42 USC 300i-2; Congress; free;
  [govinfo](https://www.govinfo.gov/link/uscode/42/300i-2?link-type=pdf), downloaded).
  - **Governs:** community water systems serving more than 3,300 people must assess risk
    and resilience. That covers "the pipes and constructed conveyances", monitoring and
    "electronic, computer, or other automated systems". They must certify to EPA by
    2020-03-31, 2020-12-31 or 2021-06-30 by size, review the assessment every 5 years
    and keep an emergency response plan.
  - **Who sees it.** Only the certification goes to EPA. No state or local law may demand
    the assessment because of it.
  - **Touches:** EPANET and WNTR.
  - **Consider or do:** reproducible hydraulic models matter here, but the assessments are
    private. Don't ask for them.
- **SDWA §1419, operator certification** (42 USC 300g-8;
  [govinfo](https://www.govinfo.gov/link/uscode/42/300g-8?link-type=pdf), downloaded).
  - **Governs:** EPA guidelines set minimum standards for certifying drinking-water
    operators, and states run the programs.
  - **Note:** the CWA has no counterpart for wastewater (above).

## Worker safety

Checked 2026-10-29.

- **OSH Act definitions and state plans** (29 USC 652(5) and 667; Congress; free;
  [652](https://www.govinfo.gov/link/uscode/29/652?link-type=pdf),
  [667](https://www.govinfo.gov/link/uscode/29/667?link-type=pdf), downloaded).
  - **Who is covered.** "Employer" excludes "any State or political subdivision of a
    State". A State Plan must cover "all employees of public agencies of the State and its
    political subdivisions".
  - **The count.** osha.gov lists 22 State Plans covering private and public workers and 7
    covering public workers only. Tennessee's covers "all state and local government
    workers". In Pennsylvania, Texas and Florida, "State and local government workers are
    not covered by federal OSHA" ([osha.gov](https://www.osha.gov/stateplans), downloaded).
- **29 CFR 1910.146, permit-required confined spaces, general industry** (OSHA; free;
  [eCFR](https://www.ecfr.gov/current/title-29/section-1910.146), downloaded).
  - **Governs:** a permit space has a hazardous atmosphere, engulfment, entrapment or
    another serious hazard. In "a continuous system (such as a sewer)", entry conditions
    are "continuously monitored". Appendix C's first worked example is sewer entry.
  - **Touches:** O1.
  - **Consider or do:** see lesson 7.
- **29 CFR 1926 subpart AA, confined spaces in construction** (OSHA, 2015; free;
  [eCFR](https://www.ecfr.gov/current/title-29/subtitle-B/chapter-XVII/part-1926/subpart-AA),
  downloaded).
  - **Governs:** the note to 1926.1201 lists "manholes (such as sewer, storm drain …)",
    "sewers", "digesters" and "lift stations".
  - **Touches:** O1, U3, and any field installation.
  - **Consider or do:** the same as 1910.146. Anything that involves installing a flume
    sensor or level probe is construction or maintenance work under one of these rules.

## States

Checked 2026-10-29.

**How state NPDES programs work.**
- **Authorization.** CWA §402(b) and 40 CFR 123 let EPA authorize a state to run NPDES.
  EPA's table ([epa.gov](https://www.epa.gov/npdes/npdes-state-program-authority),
  updated 2026-08-17, downloaded) shows every state authorized except Massachusetts, New
  Hampshire and New Mexico. EPA also permits in DC, American Samoa, Guam, the Northern
  Mariana Islands and Puerto Rico, and in almost all Indian country.
- **Partial authority.** Authority comes in parts: permits, federal facilities,
  pretreatment, general permits and biosolids. Only nine states hold the biosolids part.
  Tennessee's permit program dates from 1977-12-28 and it has no biosolids authority.
- **Definitions.** A state's definitions (weeks, averages, geometric means) live in its own
  rules and in each permit's Part I. That is why N1 needs profiles.

**Operator certification is state law** for wastewater (the CWA only funds training,
33 USC 1259). Example: Tennessee's Board of Water and Wastewater Operator Certification
classes treatment plants as Biological/Natural or Grades I–IV by a point scheme, with
separate collection-system classes (0400-49-01-.08;
[TN SOS](https://publications.tnsosfiles.com/rules/0400/0400-49/0400-49-01.20210711.pdf),
free, downloaded).

**State DMR definitions, from official sources.** These confirm the landscape table and
add to it.

| State and source | Checked 2026-10-29 | What changes for N1 |
| --- | --- | --- |
| **Tennessee**, rule 0400-40-05-.02, chapter as revised March 2024 ([TN SOS](https://publications.tnsosfiles.com/rules/0400/0400-40/0400-40-05.20240319.pdf), downloaded) | **Confirmed.** (35): geometric mean is the nth root of the product, "equivalent to the antilog of the arithmetic mean of the logarithms"; zero counts as one. (62): week is Sunday–Saturday; a week spanning two months "shall be considered part of the latter month". (52): monthly average concentration is "the arithmetic mean of all samples collected in a one calendar-month period … other than bacteria". (97): weekly likewise. No rounding rule in the chapter | Per-sample, not per-day, averaging is a Tennessee profile field. The rule's own second definition of the geometric mean is the float-unsafe one |
| **Pennsylvania**, *Instructions for Completing DMRs*, 3800-FM-BPNPSM0463 (3/2012) ([DEP](https://files.dep.state.pa.us/water/BPNPSM/WastewaterManagement/DMR/3800-FM-BPNPSM0463.pdf), downloaded) | **Confirmed.** Round statistics to the limit's decimal places. With no limit, use the data's places; mass with no limit goes to a whole number, or one significant figure below 1. "If the number you are rounding is followed by 5, 6, 7, 8, or 9, round the number up" (half up). Geometric mean substitutes 1 for 0. A censored example reports "> 158" | Rounding precision comes from the *limit*, not a fixed digit. Censored geometric means carry a qualifier |
| **Montana**, *DMR Guidance and FAQs* (updated October 2025) ([DEQ](https://deq.mt.gov/files/Water/WQInfo/Documents/DMR%20Compliance%20Guide/Compliance-Guidance-Final-October-2025.pdf), downloaded) | **Confirmed.** Week is Sunday–Saturday; a split week's average goes to "the month with 4 or more days", while monthly averages use only that month's samples. TNTC uses the lab's ">" value, or >20,000 per 100 ml if none. No rounding rule found | A split week can contribute samples to one month's weekly value and not its monthly one |

A third state wasn't added: no other official DMR instructions turned up quickly enough
to be worth the time.

## International (briefly)

Checked 2026-10-29.

- **Directive (EU) 2024/3019, recast Urban Wastewater Treatment Directive** (European
  Parliament and Council, 2024-11-27; OJ L 2024/3019; free; downloaded as the
  Publications Office's English XHTML, because EUR-Lex served a bot check;
  [EUR-Lex](https://eur-lex.europa.eu/eli/dir/2024/3019/oj)).
  - **Dates.** It entered into force 20 days after publication, and member states
    transpose most of it by 2027-07-31 (Art. 33). Directive 91/271/EEC is repealed from
    2027-08-01 (Art. 32).
  - **What it requires:**
    - **Integrated plans** (Art. 5): by 2033 for drainage areas of 100,000 p.e. and
      above, and by 2039 for listed areas of 10,000–100,000. Listing uses "historic data,
      modelling and state-of-the-art climate projections", with a 2% storm-water-overflow
      threshold.
    - **Quaternary treatment** (Art. 8): plants of 150,000 p.e. and above, 20% of them by
      2033, 60% by 2039 and all by 2045.
    - **Producer responsibility** (Art. 9): by 2028-12-31, producers of the listed
      products cover at least 80% of the cost of quaternary treatment and of
      micropollutant monitoring.
    - **Energy** (Art. 11): energy audits every four years, the first by 2028 or 2032 by
      size. National renewable energy from plants of 10,000 p.e. and above must reach 20%,
      40%, 70% and 100% of their use by 2030, 2035, 2040 and 2045.
    - **Surveillance** (Art. 17): a national system linking health and wastewater
      authorities, and antimicrobial resistance monitoring at agglomerations of 100,000
      p.e. and above.
    - **Monitoring** (Art. 21): includes greenhouse gases "by means of analysis,
      calculations or modelling", and storm-water overflows, with results usable "for the
      purposes of modelling".
    - **Public information** (Art. 24): online information for each agglomeration over
      1,000 p.e.
  - **Touches:** U1 (overflow modelling), U6 (energy and greenhouse-gas modelling in BSM
    tools), the surveillance ideas, and the European projects.
  - **Consider or do:** when proposing a change to bsm2-python or QSDsan's energy and
    greenhouse-gas accounting, say which article it serves. Don't claim the directive
    requires any particular tool; it doesn't.
- **Regulation (EU) 2024/2847, Cyber Resilience Act** (free;
  [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/2847/oj), downloaded as XHTML).
  - **Dates.** It applies from 2027-12-11, with Article 14 reporting from 2026-09-11.
  - **Scope.** It "does not apply to natural or legal persons who contribute with source
    code to products with digital elements qualifying as free and open-source software
    that are not under their responsibility" (recital 18). Open-source "stewards" have
    light duties (Art. 24).
  - **Touches:** U1–U6.
  - **Consider or do:** nothing for our contributions. It matters if anyone ever *sells*
    a product built on this work in the EU, such as a lift-station box.

## Not covered

- **States.** All states other than Tennessee, Pennsylvania and Montana; California's
  statewide sanitary sewer order and other state SSO rules; state operator-certification
  rules other than Tennessee's.
- **Other countries' national law.** Germany's Abwasserverordnung, including how it
  judges compliance samples *(unchecked)* (bsm2-python is German); UK and Swiss law.
- **Case law.** No court decisions were read, on DMRs, models or citizen suits.
- **EPA guidance not listed above.** The NPDES Permit Writers' Manual (already cited in
  landscape), the 1991 Technical Support Document's statistics for setting limits, the
  2012 recreational water quality criteria, and the 2004 report to Congress on CSOs and
  SSOs.
- **Part 136 and SDWA regulations.** The Part 136 methods themselves, and 40 CFR 141 and
  142.
- **EPA's approved list of alternative phase-2 deadlines**, the 2004 BEACH Act rule text
  behind 131.41, and the 1986 bacteria criteria document.
