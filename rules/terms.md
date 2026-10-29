# C. Licences, contribution rules and platform terms

Checked 2026-10-29. Each project's files were read with `gh api` at its default branch
that day (the commit is in the URL); web pages were fetched the same day. Where a page
refused automated reading, the row says so and nothing was worked around. This is a
reading of published terms, not legal advice.

## What changes what we do

1. **`checks/bsm1/simulink200.csv` carries bsm2-python's numbers without bsm2-python's
   licence notice.** BSD-3-Clause asks redistributions to "retain the above copyright
   notice, this list of conditions and the following disclaimer"
   ([LICENSE](https://github.com/fau-evt/bsm2-python/blob/73caa8bde193c0dd8a8803dfcd67b546501c950e/LICENSE)).
   Our README says "(BSD-3)" but the notice is nowhere in the repo. The 24 values are
   simulation results and probably facts, so the obligation may not attach. Adding the
   notice costs one file, so add it ([below](#recommended-changes-to-our-repo)).
   Checked 2026-10-29.
2. **Our WaterTAP numbers came from HSL code, and HSL's acknowledgement is missing.**
   The cfarm421 run log says "This is Ipopt version 3.13.2, running with linear solver
   ma27". idaes-ext's licence file says "All technical papers, sales and publicity
   material resulting from use of the HSL codes within IPOPT must contain the following
   acknowledgement: HSL, a collection of Fortran codes for large-scale scientific
   computation. See http://www.hsl.rl.ac.uk."
   ([license.txt](https://github.com/IDAES/idaes-ext/blob/cee874d/license.txt)).
   Add that sentence to `checks/bsm1/README.md`. Checked 2026-10-29.
3. **Two projects make AI disclosure a condition of a PR, and we have disclosed nothing
   so far.**
   - **WNTR's** PR template has an "AI Disclosure" section. Its acknowledgement adds: "If
     code was generated using AI tools, I have disclosed the use of AI and reviewed all
     code for quality assurance, correctness, security, and licensing"
     ([template](https://github.com/USEPA/WNTR/blob/11eec7d/.github/PULL_REQUEST_TEMPLATE.md)).
   - **IDAES** says "Contributors must disclose whether and how AI tools were used". Its
     form asks whether AI output was rewritten, reviewed and verified, or committed as is
     ([template](https://github.com/IDAES/idaes-pse/blob/48db990/.github/PULL_REQUEST_TEMPLATE.md)).
   - **QSDsan** welcomes Claude Code and Codex and says "You remain responsible for
     every line you contribute"
     ([guide](https://github.com/QSD-Group/QSDsan/blob/bac88d8/docs/source/faq/ai_assisted_coding.rst)).
   - **PHES-ODM** keeps an AGENTS.md "for AI coding agents ... and human contributors".
   - **The three repos we reviewed have no AI policy (confirmed):** USEPA SWMM, OWA
     EPANET and bsm2-python. None of their READMEs, CONTRIBUTING files, codes of
     conduct, issue templates or wikis mentions AI.
   - **Our record so far:** six reviews, posted 2026-10-29 12:56 UTC, with no AI
     disclosure in any of them. Nothing required one.

   From now on, put one line in every review, issue and PR, and fill in WNTR's and
   IDAES's sections in full. Checked 2026-10-29.
4. **Offer our SWMM changes under CC0 as well as MIT, so both SWMM lines can take them.**
   The repos differ:
   - **USEPA's repo** has no LICENSE file and no contribution terms, only a README saying
     SWMM is "released in the Public Domain". EPA's own guidance requires a LICENSE.md
     and a CONTRIBUTING.md in every public EPA repo, and this repo has neither
     ([EPA](https://www.epa.gov/developers/open-source-software-and-code-repositories)).
   - **The pyswmm fork** releases contributors' material under MIT "unless otherwise
     noted". Its CONTRIBUTORS file records each contributor's licence as "MIT License"
     or "Public Domain". Its wiki says accepted changes "will be eligible for USEPA
     review"
     ([LICENSE](https://github.com/pyswmm/Stormwater-Management-Model/blob/6c81201/LICENSE),
     [workflow](https://github.com/pyswmm/Stormwater-Management-Model/wiki/GitHub-Branching-Workflow)).
   - **Our README** names SWMM's licence but not the licence on our own changes, which
     default to our MIT.

   A CC0 dedication lets the fork and EPA each take the changes without carrying our
   notice. Checked 2026-10-29.
5. **ECHO_modules contradicts itself on its licence.** Its LICENSE file is GPL-3.0
   (added 2021). Its README says "the 3-Clause BSD License" and links to a different
   repository's LICENSE
   ([README](https://github.com/edgi-govdata-archiving/ECHO_modules/blob/fc2ddd9/README.md)).
   The landscape lists it as GPL-3.0. Before N2 sends code there, say which licence our
   contribution carries: BSD-3-Clause fits under either reading. Ask EDGI in the first
   issue which one they mean. Checked 2026-10-29.
6. **mWater's ShareAlike licence blocks one plan in U4.** U4 plans a Brick extension
   "built from mWater's vocabulary". mWater's standard is CC BY-SA 4.0, and so is every
   contribution to it. Brick is BSD-3-Clause. mWater's definitions and descriptions
   can't go into Brick under BSD-3-Clause.
   - **What still works:** use only the type and attribute names and codes, with
     definitions we write ourselves; or ask mWater; or publish the extension separately
     under CC BY-SA 4.0.
   - **mWater's process:** it asks for an issue before any change to what a standard
     means. Its repo has received no issue or PR since it was created on 2026-09-01
     ([CONTRIBUTING](https://github.com/mWater/asset-standards/blob/c676752/CONTRIBUTING.md),
     [NOTICE](https://github.com/mWater/asset-standards/blob/c676752/NOTICE)).

   Checked 2026-10-29.
7. **NASSCO wants a licence even for tools that only emit PACP codes.** NASSCO calls
   PACP's codes "the proprietary intellectual property of NASSCO, Inc.". It requires
   licensing of Automated Defect Recognition products "so they may legally use PACP,
   LACP and MACP codes" ([NASSCO](https://nassco.org/education-and-training/pacp-lacp-macp/pacp-software/)).
   The exchange database and data dictionary come only after a signed agreement and a
   yearly fee per product
   ([Policy 15](https://nassco.org/wp-content/uploads/2023/08/Policy-15-Import-and-Export-Software-Testing-v7.0-Final-24July2020.pdf)).
   A defect classifier of ours that outputs PACP codes falls under this. EN 13508-2
   stays the open target. Checked 2026-10-29.
8. **bsm2-python may not take contributions on GitHub at all.** Its CONTRIBUTING walks
   contributors through FAU's own GitLab (gitlab.rrze.fau.de). On GitHub it has merged
   four PRs ever, the last on 2025-07-20. Issue #7 and PR #8 (2026-10-06) have no
   maintainer reply. Ask where contributions go before drafting U6's fix for it.
   Checked 2026-10-29.
9. **Make the BSM1 inputs impossible to commit.**
   - **What:** the commands download Lund's report (no licence), its `pdftotext` output,
     and IWA's influent and sensor-noise files (no terms stated).
   - **Where they land:** working directories.
   - **What guards them:** nothing in `.gitignore` covers any of them.

   Lund's portal reserves "all rights ... including those for text and data mining, AI
   training, and similar technologies"
   ([record](https://portal.research.lu.se/en/publications/benchmark-simulation-model-no-1-bsm1/)).
   Add ignore patterns. Checked 2026-10-29.

## Projects: licences and contribution terms

### At a glance (checked 2026-10-29)

None of these projects asks for a CLA, a DCO sign-off or a copyright assignment. No
`dco.yml`, CLA bot or sign-off check was found in any repo's `.github/`. "Outside" means
GitHub's `author_association` is not OWNER, MEMBER or COLLABORATOR. Members who hide
their membership count as outside, which inflates the count for WaterTAP, IDAES and
CDC.

| Project | Licence (SPDX, file) | Terms on contributing | AI policy | Code of conduct | Security policy | Last merged PR | Outside PRs, last 100 closed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| USEPA SWMM | none; README says public domain | none (no CONTRIBUTING) | **none** | none | private vulnerability reporting on; no SECURITY.md | 2023-10-12 | 30 merged, 21 not; 11 of 12 open PRs are outside |
| pyswmm SWMM fork (OWA's old URL redirects here) | MIT plus public domain (`LICENSE`) | CONTRIBUTORS file records each contributor's licence; wiki covers git workflow | none | Contributor Covenant 1.4 (wiki) | none | 2026-07-15 | 44 merged, 17 not |
| pyswmm | BSD-2-Clause (`LICENSE.txt`) | wiki checklist: issue first, tests, update AUTHORS | none | Contributor Covenant (wiki) | none | 2026-10-01 | 42 merged, 7 not |
| swmm-python (swmm-toolkit) | CC0-1.0 plus US government work (`swmm-toolkit/LICENSE.md`) | none | none | none | none | 2026-04-29 | 5 merged, 3 not |
| swmm-nrtestsuite | CC-BY-4.0 plus US government work (`LICENSE.md`) | none | none | none | none | 2021-09-15 | 2 merged |
| OWA EPANET | MIT (`LICENSE`) | README: issue first, PR to `dev` | **none** | Contributor Covenant 1.4 | none | 2026-10-26 | 17 merged, 10 not |
| WNTR (USEPA/Sandia) | BSD-3-Clause, "Revised BSD" (`LICENSE.md`) | PR checkbox: contributions under Revised BSD; authorised by employer | **disclosure required** | none | none | 2026-07-01 | 23 merged, 12 not |
| QSDsan | NCSA (`LICENSE.txt`) | credit at module level; copied code must be permissive, "not copy-left"; tests must pass | **AI welcomed; contributor responsible** (guide plus AGENTS.md) | none (EXPOsan's applies) | none | 2026-10-12 | 12 merged, 3 not |
| EXPOsan | NCSA (`LICENSE.txt`) | refers to QSDsan's | AGENTS.md | Contributor Covenant | none | 2026-10-08 | 8 merged, 3 not |
| WaterTAP | BSD-3-Clause-LBNL (`LICENSE.md`) | PR "Legal Acknowledgement": under the licence, authorised by employer | none | none | none | 2026-10-01 | not separable; 32 open |
| IDAES (idaes-pse) | BSD-3-Clause-LBNL (`LICENSE.md`) | the same acknowledgement | **disclosure required** | none | none | 2026-10-19 | not separable; 25 open |
| idaes-ext (binaries we ran) | IDAES BSD plus bundled EPL-2.0, EPL-1.0, LGPL and HSL terms (`license.txt`) | n/a | none | none | none | n/a | n/a |
| bsm2-python | BSD-3-Clause (`LICENSE`, "Copyright (c) 2025, FAU-EVT") | CONTRIBUTING points to FAU's GitLab | **none** | PSF's, "as a reference" | none | 2025-07-20 | 1 merged ever |
| SWMManywhere | BSD-3-Clause (`LICENSE`); bundles netcomp (MIT) | issue first for new functions and metrics; PR checklist | none | Contributor Covenant | none | 2026-10-26 | 2 merged (rest team and bots) |
| ECHO_modules (EDGI) | **GPL-3.0 (`LICENSE`) but README says BSD-3-Clause** | EDGI: chat or issue first; review "within about 3 days" | none | EDGI's | none | 2025-12-17 | 4 merged |
| CORE-MATH | MIT (`LICENSE`; each source file carries it) | none in README | none | none | none | GitLab, not assessed | n/a |
| mWater asset standards | CC-BY-SA-4.0 (`LICENSE`, `NOTICE`) | contributions under CC BY-SA 4.0; issue before any change in meaning | none | own, short | none | no PR ever | none |
| PHES-ODM | **CC-BY-SA-4.0 (`LICENSE`), but README says CC BY 4.0** and the LICENSE's first line reads `cc-by-4.0` | PR to `main`, validated by CI | AGENTS.md for agents and humans | Contributor Covenant | org SECURITY.md; private reporting on | 2026-09-17 | 39 merged; last outside 2023-03-31 |
| Brick | BSD-3-Clause (`LICENSE`) | focused PRs | none | none | none | 2026-10-16 | 28 merged, 5 not |
| Freyja | BSD-2-Clause (`LICENSE`) | none | none | none | none | 2026-10-22 | 14 merged, 4 not |
| CDC wwinference | **Apache-2.0 (`LICENSE`), but README also says contributions are CC0** | README: PRs are a CC0 waiver *and* an Apache-2.0 licence; submissions "may be archived" under the Federal Records Act | none | CDC template's (the repo's own link is broken) | vulnerability PR template | 2026-07-26 | not separable |

### What each requires of us (checked 2026-10-29)

| Project | Licence or terms | What it requires of us | What we should consider or do | URL | Downloaded |
| --- | --- | --- | --- | --- | --- |
| USEPA SWMM | Public domain (README); EPA disclaimer | Nothing written for contributors. GitHub's "inbound = outbound" rule needs "notice of a license", and this repo has only a README sentence | Any PR should say: "dedicated to the public domain under CC0 1.0". It has merged nothing since 2023-10-12, so our four reviews (#226, #234, #237, #239) may go unread. GitHub's Copilot reviewer bot has already reviewed #234 and #237. No reply to ours yet | https://github.com/USEPA/Stormwater-Management-Model | yes |
| pyswmm SWMM fork | MIT for contributors' material, public domain for EPA's and US government material | Under MIT, keep the copyright notice; contributors are listed in CONTRIBUTORS (fields N, E, L, D) | Offer `upstream/swmm/` changes under CC0 and ask for a CONTRIBUTORS line with `L: Public Domain`. Its LICENSE names OpenMP as a third-party library with no text | https://github.com/pyswmm/Stormwater-Management-Model | yes |
| pyswmm | BSD-2-Clause | Keep the notice; the wiki asks contributors to update AUTHORS | Follow the checklist: issue first, tests, AUTHORS | https://github.com/pyswmm/pyswmm | yes |
| swmm-toolkit | CC0 1.0 plus 17 USC 105 | None | Nothing; we install its wheels | https://github.com/pyswmm/swmm-python | yes |
| swmm-nrtestsuite | CC BY 4.0 plus US government work | Attribution and a licence link if we share the models or adaptations | We share only digests of outputs and a list of file names, which need nothing. Credit it in THIRD_PARTY.md anyway | https://github.com/pyswmm/swmm-nrtestsuite | yes |
| OWA EPANET | MIT | Keep the notice | Issue first for code; our #916 review awaits a reply | https://github.com/OpenWaterAnalytics/EPANET | yes |
| WNTR | Revised BSD (NTESS) | PR checkboxes: Revised BSD, authority, **AI disclosure** | Fill in the AI section truthfully | https://github.com/USEPA/WNTR | yes |
| QSDsan, EXPOsan | NCSA | Tests pass; credit in the module docstring; no copyleft code | Note AI assistance; keep "Allow edits from maintainers" on | https://github.com/QSD-Group/QSDsan | yes |
| WaterTAP | BSD-3-Clause-LBNL | PR acknowledgement. The licence also grants LBNL a licence to any "Enhancements" we publish "without imposing a separate written license agreement" | Our MIT licence is probably such a separate written licence, so publishing fixes here likely does not trigger that clause. Disclose AI use on the reactor-5 oxygen fix even though the template doesn't ask; the sibling IDAES template does | https://github.com/watertap-org/watertap | yes |
| IDAES, idaes-ext | BSD-3-Clause-LBNL; bundled solver licences | PR acknowledgement and **AI disclosure**. HSL's acknowledgement in anything resulting from HSL use | Add HSL's sentence to `checks/bsm1/` | https://github.com/IDAES/idaes-pse | yes |
| bsm2-python | BSD-3-Clause; its copyright page also credits Lund University's IEA (2006–2024) for the ported model files | Keep the notice on anything copied | Add the notice for `simulink200.csv`. Ask where contributions go | https://github.com/fau-evt/bsm2-python | yes |
| SWMManywhere | BSD-3-Clause | Issue first for new functions | Nothing planned | https://github.com/ImperialCollegeLondon/SWMManywhere | yes |
| ECHO_modules | GPL-3.0 or BSD-3-Clause (conflict) | Unclear | Offer N2's code under BSD-3-Clause and ask which licence they mean | https://github.com/edgi-govdata-archiving/ECHO_modules | yes |
| CORE-MATH | MIT | The notice in "all copies or substantial portions" | Our repo holds no CORE-MATH file ([below](#our-own-repository)) | https://gitlab.inria.fr/core-math/core-math | yes (via GitLab API; the site's pages are bot-checked) |
| mWater asset standards | CC BY-SA 4.0 | Attribution, changes marked, ShareAlike; no hint of endorsement (`NOTICE`, citing §2(a)(6)) | Review errata as issues, which raises no licence question. Keep mWater's text out of Brick | https://github.com/mWater/asset-standards | yes |
| PHES-ODM | CC BY-SA 4.0 by LICENSE (CC BY 4.0 by README) | Treat as BY-SA, the stricter | In the U5 issue, cite their 2022 decision for BY-SA (#179, closed) and the stale badge and first line | https://github.com/PHES-ODM/PHES-ODM | yes |
| Brick | BSD-3-Clause | Keep the notice | See item 6 | https://github.com/BrickSchema/Brick | yes |
| Freyja | BSD-2-Clause | Keep the notice | Nothing planned | https://github.com/andersen-lab/Freyja | yes |
| CDC wwinference | Apache-2.0, or CC0 by README | A PR is both a CC0 waiver and an Apache-2.0 grant; it may be archived as a federal record | Nothing planned. If ever, accept both, which CC0 already covers | https://github.com/CDCgov/ww-inference-model | yes |

## US government repositories (checked 2026-10-29)

- **EPA's rules for its own repos.** Each public repo needs a LICENSE.md, a README with
  the standard disclaimer, and a CONTRIBUTING.md. EPA "usually recommends the use of
  the MIT license". Repo administrators review outside code and may "reject the
  submission". Contributors "should contact the repo administrator early in the
  development process"
  ([EPA, updated 2026-03-10](https://www.epa.gov/developers/open-source-software-and-code-repositories)).
  USEPA SWMM carries the disclaimer, but has neither the licence file nor the
  contributing file. WNTR has both.
- **No EPA-wide contributor terms exist.** No page says that outside contributions to an
  EPA repo become public domain or CC0. EPA's disclaimers page has a comment licence
  ("irrevocable permission to copy, distribute, make derivatives") only for its *social
  media* accounts ([EPA disclaimers, updated 2026-09-21](https://www.epa.gov/web-policies-and-procedures/epa-disclaimers)).
- **Public domain covers the government's own work, not ours.** 17 USC 105 denies
  copyright only to "any work of the United States Government"
  ([govinfo](https://www.govinfo.gov/content/pkg/USCODE-2023-title17/html/USCODE-2023-title17-chap1-sec105.htm)).
  A contribution from us stays ours and is licensed however the repo's terms or our PR
  say. That's why federal repos that want public domain ask for a CC0 waiver, as CDC's
  template does, and why swmm-toolkit uses CC0 to cover rights outside the US.
- **EPA's data** is "by default in the public domain" under 17 USC 105, "no warranty
  expressed or implied" ([EPA data licence](https://edg.epa.gov/epa_data_license.html)).
  Separately, the disclaimers page says EPA documents "may be freely distributed and
  used for non-commercial, scientific and educational purposes" and that individual
  documents may differ.
- **CDC's template.** Submissions "may be subject to ... the Federal Records Act, and
  may be archived" ([wwinference README](https://github.com/CDCgov/ww-inference-model/blob/3e92fea/README.md)).

## Data and documents we copy or plan to copy (checked 2026-10-29)

| Item | Licence or terms | What it requires of us | What we should consider or do | URL | Downloaded |
| --- | --- | --- | --- | --- | --- |
| BSM1 report (Lund, 2008) | No licence in the PDF. Lund's portal: "All rights are reserved, including those for text and data mining, AI training, and similar technologies". The PDF's host (www2.iea.lth.se) states no terms | Don't redistribute the PDF or its text | Keep copying numbers only, each with its page, in our own layout (`reference.csv`). Ignore `*.pdf` and `bsm1.txt` | https://portal.research.lu.se/en/publications/benchmark-simulation-model-no-1-bsm1/ | record yes; PDF no (not needed) |
| BSM1 2018 version (IWA page) | "Copyright © 2018" the nine named authors; DRAFT watermark | The same | The same | https://iwa-mia.org/benchmarking/ | page yes |
| IWA influent and sensor-noise files | IWA's benchmarking page states no terms; its footer is the theme's unedited placeholder. IWA's site-wide terms page renders only with JavaScript and gave no text | Unknown | Keep not copying them; record sha256 values only, as now | https://iwa-mia.org/benchmarking/ | page yes; site terms no |
| bsm2-python test data → `simulink200.csv` | BSD-3-Clause | The notice, conditions and disclaimer, if the values are protectable | Add them (exact text below) | https://github.com/fau-evt/bsm2-python/blob/73caa8bde193c0dd8a8803dfcd67b546501c950e/tests/bsm1_ol_test.py | yes |
| EPA ECHO / ICIS-NPDES | Public domain (17 USC 105); "for informational purposes only. No warranty" | No attribution needed; don't imply EPA endorsement or use EPA's seal | Cite ECHO and the download date. No rate limit is published, so pace the REST calls | https://echo.epa.gov/resources/echo-data/about-the-data | yes |
| Sewer-ML | Dataset CC BY-NC-SA 4.0, through a Google Form; code MIT (Bitbucket) | Non-commercial; attribution; share-alike | Research only, as U5 says. The form may add terms: unread, because filling it in is agreeing | https://bitbucket.org/aauvap/sewer-ml | yes (README, LICENSE, page) |
| NASSCO PACP | Registered copyright in the PACP Manual; codes, forms and grading claimed as NASSCO's IP; licence per product, yearly fee July to June | A signed licence before the exchange database or dictionary, and for any ADR tool | Don't build PACP output without it | https://nassco.org/education-and-training/pacp-lacp-macp/pacp-software/ | yes (page, Policy 15, blank agreement) |
| Semantic Scholar API | API Licence Agreement (updated 2023-05-17), accepted by use | Don't share the API key beyond authorised users. Data stays under its own licences (CC BY-NC or ODC-BY). Credit "Semantic Scholar"; cite "The Semantic Scholar Open Data Platform" in scientific publications. Respect rate limits; don't redistribute the API | Neither the key nor any Semantic Scholar output appears in our repo or its history. If a literature list goes public, add the credit, and publish metadata (titles, DOIs), not abstracts | https://www.semanticscholar.org/product/api/license | yes |
| CORE-MATH | MIT | The notice with copies | Nothing to add to our repo (see below) | https://core-math.gitlabpages.inria.fr/ | yes |

### Facts and expression

- **United States.** "Facts are not copyrightable", and a compilation is protected only
  in its original selection and arrangement (*Feist v. Rural*, 499 U.S. 340 (1991),
  [US Reports](https://tile.loc.gov/storage-services/service/ll/usrep/usrep499/usrep499340/usrep499340.pdf)).
  Copyright never extends to "any idea, procedure, process, system, method of
  operation" (17 USC 102(b),
  [govinfo](https://www.govinfo.gov/content/pkg/USCODE-2023-title17/html/USCODE-2023-title17-chap1-sec102.htm)).
  - **What follows for us:** a model's printed results are facts. `reference.csv`
    takes the numbers into our own layout with page references, not the report's
    tables.
  - **What would change that:** reproducing a table as the report lays it out, or
    quoting its text at length.
- **European Union.** The database right protects "a substantial investment in either
  the obtaining, verification or presentation of the contents" (Directive 96/9/EC
  Art. 7, [Publications Office](http://publications.europa.eu/resource/cellar/b48976b5-b31a-4dba-a052-87133e17d65e.0008.05/DOC_1)).
  Three things weaken it here:
  - **What counts as investment.** The Court of Justice held that resources used "to
    create" data don't count (*BHB v William Hill*, C-203/02, 2004,
    [Publications Office](http://publications.europa.eu/resource/cellar/51970810-9a78-49d2-bdef-bc8178bba308.0002.03/DOC_1)).
    Simulation results are created data.
  - **The term.** The right lasts fifteen years from 1 January after publication (Art.
    10), so a database published in 2008 lost it on 2023-12-31.
  - **Small extracts.** Insubstantial parts are always free to take (Art. 8).
- **Text and data mining.** The EU's general exception lets rightholders opt out
  (Directive 2019/790 Art. 4,
  [Publications Office](http://publications.europa.eu/resource/cellar/214471fe-786e-11e9-9f05-01aa75ed71a1.0006.01/DOC_1)).
  Lund's footer is such an opt-out for its portal. Our `refextract.py` mines the PDF
  for numbers. Under US law that copies facts; the opt-out governs mining done in the
  EU. The risk is low as long as only numbers are published.
- **AI-drafted text.** The US Copyright Office says copyright "does not extend to purely
  AI-generated material". It does protect human selection, arrangement and
  modification ([Part 2, January 2025](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf)).
  Anthropic assigns users "all of our right, title, and interest—if any—in Outputs"
  ([consumer terms](https://www.anthropic.com/legal/consumer-terms) §4; the
  [commercial terms](https://www.anthropic.com/legal/commercial-terms) say the same).
  So we can make the "authorised to grant the license" statements that WNTR, WaterTAP
  and IDAES ask for, as long as a person reviews and edits the work and the AI use is
  disclosed.

## Platforms and services (checked 2026-10-29)

| Service | Terms | What it requires of us | What we should consider or do | URL | Downloaded |
| --- | --- | --- | --- | --- | --- |
| GitHub | Terms of Service (effective 2026-04-27) and Acceptable Use Policies; CC0 | **D.6:** content added to a repo with a licence notice is licensed "under the same terms" ("inbound=outbound"). **D.4:** GitHub may use content to train AI. **H:** "Abuse or excessively frequent requests ... via the API" can suspend access. **AUP §4:** no "automated excessive bulk activity" or "inauthentic interactions". **AUP §7:** research use of public data only if publications are open access. **Disrupting others:** no "nonsensical or irrelevant code reviews", empty PRs, or "excessive notifications" | Nothing bars AI-written content; the AI page bans only CSAM, extremist and non-consensual imagery tools. Keep each review on-topic and approved, as now. Space postings: our six went out within one minute. Sleep between API calls: this check hit the code-search limit once | https://github.com/github/site-policy | yes |
| PyPI | Terms of Service (effective 2025-02-25); Acceptable Use Policy; CC0 | Mostly binds uploaders. API abuse can mean suspension. Each package keeps its own licence | Nothing beyond the packages' own licences | https://github.com/psf/policies/tree/main/docs/pypi.org | yes |
| GCC Compile Farm (cfarm) | Account page: "should be used only for free software development". Usage rules are on the GCC wiki | Free-software use only | Our use (SWMM, EPANET, BSM1 implementations, CORE-MATH, all open) fits. The wiki page blocked automated reading with a bot check, which we did not get around, so its rules are unread here. Keep following what the admins told us (nice 19, at most half the cores, run notices, clean up) | https://portal.cfarm.net/users/new/ ; https://gcc.gnu.org/wiki/CompileFarm | account page yes; wiki no |
| IWA | Site terms render only with JavaScript; a search snippet says UK copyright, with consent needed beyond permitted use *(snippet)* | Unknown | Keep linking, not copying | https://www.iwa-network.org/terms-and-conditions/ | no |
| Lund University portal | Footer: all rights reserved, including TDM and AI training | Don't copy portal content | Copy numbers only (as now) | https://portal.research.lu.se/ | yes (record page) |
| EPA web and ECHO | Disclaimers (updated 2026-09-21): no endorsement; "Commercial use ... may be protected"; seal and logo not to imply endorsement. Privacy notice | Don't imply EPA endorsement; no EPA logo | Nothing to change | https://www.epa.gov/web-policies-and-procedures/epa-disclaimers | yes |
| Anthropic (the AI assistant used) | Consumer and commercial terms assign Output rights to the user | Review outputs before use | Which terms apply depends on the account; both assign Outputs | https://www.anthropic.com/legal/consumer-terms | yes |

## Our own repository

Scanned 2026-10-29: every tracked file, plus the uncommitted BSM1 closed-loop work.

- **Copied third-party content.** Only `checks/bsm1/simulink200.csv` (24 values from
  bsm2-python, BSD-3-Clause), and it lacks the notice.
- **Numbers cited with sources.** `checks/bsm1/reference.csv` holds the Lund report's
  numbers, page by page, with no text or table layout. The constants in the run
  scripts (Table 5 influent, volumes, KLa values) are facts.
- **Derived, not copied.** `checks/swmm/digests/` are SHA-256 digests of SWMM outputs
  computed from swmm-nrtestsuite's models (CC BY 4.0); `models.txt` lists file names.
  Neither redistributes the models.
- **CORE-MATH is not in the repo.**
  - `crlibm_shim.c` and `crlibm_shim_darwin.c` are our code; they only declare and
    call CORE-MATH's `cr_*` functions.
  - `crshim.sh` compiles CORE-MATH sources from a directory given on its command line
    (crnumerics' copy, where every file carries its MIT header).
  - The built libraries stay in ignored directories.

  MIT's notice condition applies to "copies or substantial portions", and the repo
  holds none, so it is met. The tarballs sent to cfarm included those source files
  with their headers intact.
- **Runtime only, not distributed.** `run_qsdsan.py` rewrites EXPOsan's `_asm1.tsv`
  into a temporary file at runtime.
- **AI output.** `thread/2026-10-27-initial.md` is verbatim AI output, labelled as a
  chat answer. Purely AI-generated text likely carries no copyright (above), so MIT
  adds little to it. That's harmless, but say plainly that it is AI output.
- **Patches.** `upstream/swmm/` holds two patches whose context lines come from SWMM:
  public domain (EPA's original code, and the build system by the fork's LICENSE) or
  MIT (the fork's later additions). Our added lines are ours, under MIT by default.
- **Secrets.** No API key or Semantic Scholar output appears in the tree or its history.
- **Answers to the brief:**
  - **The README's licence line** names SWMM's licence but not the licence on our
    changes.
  - **A NOTICE file** isn't needed: MIT doesn't use one, and nothing we copy is Apache.
    A short `THIRD_PARTY.md` covers what is owed.

### Recommended changes to our repo

**Applied 2026-10-29:** 1 (`THIRD_PARTY.md`, without the CC0 and AI-assistance
sections, which wait on a decision), 2 (the README's licence paragraph, without those
two sentences), 3 and 4. **Waiting on a decision:** the CC0 dedication (1, 2 and 5) and
the AI-assistance disclosure (1, 2, 5 and 6).

**1. Add `THIRD_PARTY.md`** at the root:

```markdown
# Third-party material

Everything in this repository is MIT licensed ([LICENSE](LICENSE)) except as listed
here. Checked 2026-10-29.

## Copied into this repository

### checks/bsm1/simulink200.csv

Its 24 values are copied from bsm2-python, `tests/bsm1_ol_test.py` lines 62-114 at
commit 73caa8bde193c0dd8a8803dfcd67b546501c950e
(https://github.com/fau-evt/bsm2-python): the BSM2 group's Simulink results for BSM1
open loop after 200 days. bsm2-python is distributed under this licence:

    BSD 3-Clause License

    Copyright (c) 2025, FAU-EVT

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    3. Neither the name of the copyright holder nor the names of its
       contributors may be used to endorse or promote products derived from
       this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### checks/bsm1/reference.csv

Numbers from IWA Task Group on Benchmarking of Control Strategies for WWTPs,
*Benchmark Simulation Model no. 1 (BSM1)*, Lund University, 2008,
LUTEDX/(TEIE-7229), each with its page. The report states no licence and is not
included here; only the printed numbers are copied, not its text, tables or figures.

## Derived from, not included

- **swmm-nrtestsuite v3.3.0** (https://github.com/pyswmm/swmm-nrtestsuite, CC BY 4.0,
  copyright its contributors, with US government material in the public domain):
  `checks/swmm/digests/` holds SHA-256 digests of SWMM outputs computed from its
  models, and `checks/swmm/models.txt` lists their names. The models are not included.
- **HSL.** The WaterTAP results in `checks/bsm1/` were computed with IPOPT 3.13.2 from
  idaes-ext 3.4.2, using the HSL linear solver MA27. HSL, a collection of Fortran codes
  for large-scale scientific computation. See http://www.hsl.rl.ac.uk.
- **CORE-MATH** (https://core-math.gitlabpages.inria.fr/, MIT). `checks/swmm/crshim.sh`
  compiles CORE-MATH sources from a checkout given on its command line;
  `checks/swmm/crlibm_shim*.c` only call CORE-MATH's `cr_*` functions. No CORE-MATH
  file is in this repository. Anyone who distributes a built shim must include
  CORE-MATH's copyright notices and licence.
- **BSM1 inputs.** IWA's influent and sensor-noise files (http://iwa-mia.org/benchmarking/,
  no terms stated) are downloaded by the commands in `checks/bsm1/README.md` and are
  not included; their SHA-256 values are recorded there.

## upstream/swmm/

The patches change SWMM: public domain (US EPA), with MIT-licensed additions by the
pyswmm fork's contributors. The unchanged context lines remain under SWMM's terms. Our
changes in them are also dedicated to the public domain under CC0 1.0
(https://creativecommons.org/publicdomain/zero/1.0/), so the pyswmm fork and US EPA
can each take them on their own terms.

## AI assistance

Much of the text, code and analysis here was drafted with an AI assistant (Claude, by
Anthropic) and was read, run and approved by the maintainer before publication.
`thread/2026-10-27-initial.md` is an AI assistant's answer, kept verbatim and unchecked.
```

**2. In `README.md`, replace the last paragraph** ("MIT licensed ([LICENSE](LICENSE)).
The patches in `upstream/swmm/` change SWMM, ...") with:

```markdown
MIT licensed ([LICENSE](LICENSE)), except the material listed in
[THIRD_PARTY.md](THIRD_PARTY.md): 24 values copied from bsm2-python (BSD-3-Clause,
notice included there) and numbers cited from the BSM1 report. The patches in
`upstream/swmm/` change SWMM, which is public domain (EPA) with MIT additions (the
pyswmm fork); our changes in them are also dedicated to the public domain under CC0 1.0,
so either line can take them. Text and code here were drafted with an AI assistant and
read, run and approved by the maintainer before publication.
```

**3. In `checks/bsm1/README.md`, end the "A converged Simulink answer" bullet** with:

```markdown
  Its licence notice (BSD-3-Clause, Copyright (c) 2025, FAU-EVT) is in
  [THIRD_PARTY.md](../../THIRD_PARTY.md).
```

Then, at the end of the WaterTAP row's notes in the versions table, add:

```markdown
IPOPT ran with HSL's MA27 linear solver. HSL, a collection of Fortran codes for large-scale scientific computation. See http://www.hsl.rl.ac.uk.
```

**4. Append to `.gitignore`:**

```gitignore
# Third-party inputs that must never be committed: the BSM1 report (no licence; Lund
# reserves all rights), its extracted text, and IWA's influent and sensor-noise files
# (no terms stated). See THIRD_PARTY.md.
*.pdf
bsm1.txt
Inf_*_2006.txt
sennoise*
```

**5. In `upstream/swmm/pr-build.md` and `pr-gage.md`, before posting**, add:

```markdown
I dedicate my changes in this PR to the public domain under CC0 1.0, so they can go to
USEPA's repository unchanged; take them under this repository's MIT terms if you
prefer. If you keep CONTRIBUTORS current, the entry would be `N: anun333`,
`L: Public Domain`, `D: <one line>`. Drafted with an AI assistant; I ran every build
and test reported here.
```

**6. A standard disclosure line for reviews, issues and PRs** (replace the bracketed
part with what was actually done):

```markdown
Drafted with an AI assistant (Claude); I read it, [ran every command and checked each number] before posting.
```

On WNTR and IDAES, fill in their template sections in full instead.

## Not checked, or uncertain

- **The GCC wiki's CompileFarm rules** (bot check), **IWA's site terms** (JavaScript
  only) and **Sewer-ML's request form**: unread for the reasons given above.
- **Whether `simulink200.csv`'s values are protectable at all.** The recommendation adds
  the notice either way.
- **Which Anthropic terms govern the account.** Both sets assign Outputs to the user.
- **GitHub's `author_association` counts.** They understate members who hide their
  membership, so "outside" counts for WaterTAP, IDAES and CDC mean little.
- **Contribution practice on Inria's GitLab (CORE-MATH) and FAU's GitLab
  (bsm2-python):** not assessed.
- **Whether swmm-toolkit's wheels ship an OpenMP runtime, and under what licence:** not
  checked. We only install them.
