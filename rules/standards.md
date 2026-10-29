# B. Technical standards and specifications

Checked 2026-10-29. This part covers the standards and specifications the project's work rests on or will meet. That is the numerics and language standards behind the SWMM findings, the model and benchmark specifications, design and condition standards, data and reporting formats, lab methods, and, for the parked lift-station idea, operational-technology and safety standards. Laws and regulations, including the Information Quality Act and the CFR text, are in part A. Licences and platform terms are in part C.

Each item was read on the issuer's own site on 2026-10-29, unless it says otherwise. A claim marked *(snippet)* came only from a search-engine result, because the page refused direct reading. A claim marked *(unchecked)* is from memory. Free documents from official sources were downloaded into a local reference set, which is not in this repo; its manifest records the URL, retrieval time, sha256, size and terms of each file. Paid standards, and free ones that need an account or click-through acceptance, were listed and not fetched. Prices marked "EVS" are from the Estonian national standards body's shop, which shows CEN, ISO and IEC prices openly, in euros including VAT. Other national bodies' prices differ, often by several times *(snippet)*.

## What changes what we do

1. **The gage.c cast should cite both C's undefined behaviour and Annex F.**
   - **ISO C.** Converting an out-of-range floating value to an integer type is undefined behaviour. That is clause 6.3.1.4p1, "Real floating and integer", in C11 and in the free C23 working text N3220. The later WG14 draft N3550 numbers it 6.3.2.4, and so does GCC's manual when it cites C23.
   - **Annex F.** gcc and clang on glibc define `__STDC_IEC_559__`, which claims Annex F. That was checked locally with gcc 13.3 for x86-64, a gcc cross-compiler for aarch64, and clang 18. Under Annex F the same conversion raises "invalid" and returns an unspecified value (F.4, the same number in every draft). So both x86-64's INT_MIN and aarch64's INT_MAX are allowed.
   - **Do.** The gage PR now cites "C11 6.3.1.4" alone. It should say the conversion is undefined in ISO C (C17 6.3.1.4p1), and unspecified, with an "invalid" exception, under Annex F (F.4), which glibc platforms claim. Either way it is not portable. Don't write "C23 6.3.1.4" until the published text's numbering has been seen.
2. **FMA builds are conforming C, so the build PR makes a choice rather than fixing a bug.**
   - **What C allows.** C permits contraction: 6.5p8 in C11 and C17, 6.5.1p8 in N3220. Whether and how expressions are contracted is implementation-defined (J.3.7), and so is the default state of the `FP_CONTRACT` pragma (7.12.2). Annex F only asks that a contracted expression be rounded once (F.7).
   - **What the compilers do.**
     - Clang's manual says fusion across statements is not compliant with the C standard and needs `-ffp-contract=fast`. Clang's default, `on`, fuses within a statement.
     - GCC defaults to `fast` in its GNU dialects and to `off` under `-std=c11`. GCC does not implement the pragma.
     - MSVC: since Visual Studio 2022, `/fp:precise` generates no contractions by default.
   - **Do.** The PR and issue should say that the standard leaves contraction to each compiler, so reproducibility is a choice the project makes. They should also say why the PR uses an explicit `-ffp-contract=off`: the pragma does nothing in GCC, and clang contracts by default even in ISO mode.
3. **libm differences conform to C too, and correct rounding is the only portable fix.**
   - **What C requires.** C makes the accuracy of `<math.h>` implementation-defined, and lets an implementation say it is unknown. That is 5.2.4.2.2 in C11 (p6 in N1570) and 5.2.5.3.3p20 in N3220.
   - **What GCC and glibc document.** GCC documents: "The accuracy is unknown". glibc's manual says it does not aim for correctly rounded results, apart from functions such as `sqrt`, `fma` and `rint`, and that its testsuite flags errors only above 9 ulp.
   - **IEEE 754 and C.** IEEE 754 recommends correctly rounded functions, but C does not require them (F.3p20 and F.10p16 in N3220). C reserves `cr_` names for correctly rounded versions (7.33.8p4).
   - **glibc's progress.** glibc 2.43 takes seven binary64 functions from CORE-MATH, but none is `exp`, `log` or `pow`.
   - **Do.**
     - The issue's "what remains" paragraph should cite these clauses.
     - checks/swmm should record the glibc version behind each digest, since a glibc that adopts correctly rounded `exp`, `log` or `pow` will change the reference bits.
4. **OpenMP explains the thread-count result, and its limit.**
   - **What the spec says.** In a reduction, the order in which values are combined is unspecified, so results need not be bitwise identical, "even if the number of threads used is the same" (OpenMP 6.0 §7.6.7, p. 250; 5.2 §5.5.6).
   - **Why SWMM is unaffected.** SWMM's loops have no reductions, which is why the thread count changed nothing.
   - **Do.** The issue should say that thread invariance depends on SWMM having no reduction clauses, and that a future `reduction` in `dynwave.c` would lose it.
5. **EPA's guidance on modeling quality assurance asks for exactly this check.**
   - **What it asks.** QA/G-5M (2002) calls the modeling framework "the model and its supporting hardware and operating system" (§4.2.3.2). It asks for beta testing "on a wide variety of different platforms", and for code verification so that "sources of error, such as rounding, are minimal" (§4.4.1).
   - **Its worked example** accepts a difference of "no more than a rounding error (usually less than ±0.1%)" (§5.3.4).
   - **Still current.** EPA still lists G-5M as guidance under its 2024 QAPP Standard and its 2025 QAPP Guidance.
   - **The gap.** On user5, SWMM's platform difference is 13% (400.6 against 450.9 cfs).
   - **Do.**
     - Cite G-5M in the issue as the reason a user working under a QAPP should care.
     - Add a line to checks/swmm naming the build flags and libm that give the reference bits, for anyone writing a QAPP.
6. **SWMM's own convergence test is the likely amplifier.**
   - **What the manuals specify.** Dynamic-wave routing iterates until each node's head changes by less than `HEAD_TOLERANCE`, 0.005 ft, in at most `MAX_TRIALS`, 8 (Reference Manual Vol. II p. 47; User's Manual 5.2 p. 334). They say nothing about how the floating-point arithmetic is evaluated.
   - **The mechanism.** A last-bit change can move a node across that test and change the trial count.
   - **Do.** Trace the trials per time step on user5. This is the open item "the mechanism that amplifies a 1-ulp change".
   - **The manual's sanity check misses it.** The User's Manual (§8.5) treats continuity errors over 10% as suspect, so Example1's 0.103% against 0.109% passes it.
   - **EPA has seen this kind of case before.** Its own 2006 QA report (EPA/600/R-06/097) traced differences on user-supplied models with "oscillatory flows" to numerical instability (in SWMM 4). user5's `LIB_*` links oscillate too.
7. **The DMR schema is decimal, so N1 must emit decimal strings and key its profiles on ECHO's statistical base codes.**
   - **The schema.** In the ICIS-NPDES schema v5.15, a DMR `NumericReport` value is `xsd:decimal`, with at most 8 fraction digits and 9 digits in all. It goes in one of the slots Q1, Q2 or C1-C3, with a qualifier.
   - **ECHO's dictionary.**
     - Qualifiers are <, <=, >, >=, =, T (too numerous to count) and E (estimated).
     - It lists 186 statistical base codes. For example, "High 7 Day Average" (HA) is separate from "High Weekly Average" (HB), and several geometric means have their own codes.
   - **Rounding.** EPA Method 1603.1 says "rounding should only occur after the final calculation".
   - **Do.** In N1:
     - key profiles on the statistical base code;
     - validate output strings against the XSD;
     - round once, at the end;
     - define non-detects against the MDL procedure (Revision 2).
8. **Ten States Standards §46 is the requirement a lift-station watch has to meet, and a new edition came out this year.**
   - **The 2014 edition** (free, archived) requires an alarm system with backup power. It must go off on power failure, high wet-well level, pump failure and unauthorized entry, and transmit to a facility staffed 24 hours a day.
   - **The 2026 edition** is current and unread. The download costs $14.95 and "cannot be copied, printed, or shared".
   - **Do.** Before O1 comes off the shelf, buy the 2026 edition and cite the edition the target state adopts.

## 1. Numerics and languages

**IEEE 754-2019, Standard for Floating-Point Arithmetic** (IEEE), and its ISO adoption **ISO/IEC 60559:2020**
- **What it specifies.** Binary and decimal floating-point formats, operations and exceptions.
  - It defines fused multiply-add as a basic operation (Microsoft's `/fp` documentation says so). C's Annex F binds 754's `fusedMultiplyAdd` to `fma` (N3220, F.3 table).
  - Clause 9 recommends correctly rounded elementary functions. A language may adopt each function, and may require correct rounding or not. The 754 working group's public "conformance and options" note says so, and so does C's F.3p20.
  - The 754 working group's background page lists the 2019 changes, mostly new recommended operations such as augmented arithmetic and new min/max.
  - Clause 10.4 (value-changing optimizations, including synthesising an FMA) and clause 11 (reproducible results) bear directly on our claims *(unchecked: clause contents from memory; the text is paid)*.
- **Touches.** The SWMM findings, the CORE-MATH argument and the DMR rounding checks.
- **Do.**
  - Don't cite clause 10 or 11 text without reading it.
  - For "IEEE 754 recommends correct rounding", cite C's F.10p16 and the working group note, both free.
  - If the issue's argument comes to rest on 754's reproducibility clause, buy the standard.
- **Status.** Active. It expires in 2029, and the working group calls the next revision "754-2029".
- **Access.** Paid.
  - IEEE SA shows no price, only "Purchase" (IEEE store) and subscription.
  - ISO/IEC 60559:2020 costs €272.12 (EVS). The CORE-MATH FAQ calls IEC 60559 "the direct translation of IEEE 754".
- **URLs.** https://standards.ieee.org/ieee/754/6210/, https://grouper.ieee.org/groups/msc/ANSI_IEEE-Std-754-2019/
- **Downloaded:** the working group's public background notes only (3 files). Checked 2026-10-29.

**ISO/IEC 9899, Programming languages: C.** The published editions are C11, C17 (ISO/IEC 9899:2018) and C23 (ISO/IEC 9899:2024). The free drafts used here are WG14's N1570, N2310, N3096, N3220 and N3550.
- **What it specifies.** The C language and library. The clauses that matter here:

  | Topic | C11 (N1570) | N3220 (C23 text) | N3550 (C2y draft, 2025) |
  | --- | --- | --- | --- |
  | Out-of-range float-to-int conversion is undefined | 6.3.1.4p1 | 6.3.1.4p1 | 6.3.2.4p1 |
  | The same under Annex F: "invalid", unspecified value | F.4 | F.4 | F.4 |
  | Contraction allowed, implementation-defined | 6.5p8 | 6.5.1p8 (footnotes 86-87) | 6.5.1p10 |
  | `FP_CONTRACT` pragma, default implementation-defined | 7.12.2 | 7.12.2 | 7.12.3 |
  | A contracted expression is rounded once | F.7 | F.7 | F.7 |
  | Accuracy of operations and `<math.h>` is implementation-defined, may be "unknown" | 5.2.4.2.2p6 | 5.2.5.3.3p20 | 5.3.5.3.3 |
  | Implementation-defined floating-point behaviour listed | J.3.6 | J.3.7 | — |
  | Correct rounding not required of the math functions; `cr_` names reserved | — | F.3p20, F.10p16, 7.33.8p4 | F.3p20, 7.35.9p4 |

  - **Footnote 87 in N3220.** It says contraction is allowed "to exploit fast machine instructions", and adds that "as contractions potentially undermine predictability... their use needs to be well-defined and clearly documented".
  - **The drafts.**
    - N2310 (November 2018) is the first C2x draft, with diff marks against C17.
    - N2176, the C17 ballot text, is on open-std.org but password-protected, so C17's paragraph numbers were read from N1570 and N2310.
    - N3220 is headed "ISO/IEC 9899:2024" and is the first C2y draft. Its cover lists the changes made since C23.
- **Touches.** U1: the gage.c PR, the build PR and the issue.
- **Do.**
  - Cite C17 by number, where the free drafts agree.
  - For C23, cite clause titles alongside numbers, or check the published text. Its numbering is uncertain: GCC's manual cites "C23 6.3.2.4" and "C23 7.12.3", which matches N3550 rather than N3220 *(the published C23 text was not read)*.
- **Access.**
  - The drafts are free on open-std.org.
  - ISO/IEC 9899:2024 costs €302.80 (EVS).
- **URL.** https://www.open-std.org/jtc1/sc22/wg14/www/docs/ (n1570.pdf, n2176.pdf, n2310.pdf, n3096.pdf, n3220.pdf, n3550.pdf)
- **Downloaded:** yes, all six. Checked 2026-10-29.

**ISO/IEC TS 18661, Floating-point extensions for C** (parts 1-5; part 4 revised in 2025)
- **What it specifies.** C bindings for the rest of IEEE 754: decimal types, interchange types, and supplementary functions in Part 4, where the correctly rounded `cr_` functions come from. Part 1's binary features went into C23 *(unchecked)*.
- **Touches.** The CORE-MATH argument, only as background.
- **Do.** Nothing now. Read Part 4 only if we propose `cr_` names to SWMM.
- **Access.** Paid.
  - TS 18661-4:2025 costs €133.39 and TS 18661-3:2015 costs €272.12 (EVS).
  - WG14 drafts exist on open-std.org but were not fetched.
- **Downloaded:** no. Checked 2026-10-29.

**OpenMP Application Programming Interface 6.0** (November 2024) **and 5.2** (OpenMP Architecture Review Board)
- **What it specifies.** Directives and runtime for shared-memory parallelism.
  - In a reduction, "the order in which values are combined [is] unspecified". So "when comparing one parallel execution to another (even if the number of threads used is the same), bitwise-identical results are not guaranteed" (6.0 §7.6.7, p. 250; 5.2 §5.5.6, pp. 132-133).
  - The static schedule's assignment of iterations to threads has been deterministic since 3.0 (6.0 change log).
- **Touches.** The thread-count half of U1.
- **Do.** State in the issue that SWMM's `dynwave.c` loops have no reductions, which is why the bits don't move with thread count, and that a future reduction would forfeit that.
- **Access.** Free. The ARB permits copying with its notice.
- **URL.** https://www.openmp.org/specifications/
- **Downloaded:** yes (6.0 and 5.2). Checked 2026-10-29.

**The GNU C Library manual, §19.7 "Errors in Math Functions"** (current online manual)
- **What it says.**
  - glibc "does not aim for correctly rounded results for functions in the math library", except functions such as `sqrt`, `fma` and `rint` that IEEE 754 fully specifies.
  - The goal is a result within "a few ulp". The testsuite flags only errors over 9 ulp.
  - It may later add correctly rounded functions under `cr` names.
  - Per-function accuracy lives in an outside study, *Accuracy of Mathematical Functions in Single, Double, Double Extended, and Quadruple Precision* (HAL hal-03141101), which covers x86-64 only.
- **Touches.** U1's libm finding: glibc picks FMA or non-FMA `exp`, `log` and `pow` by CPU.
- **Do.**
  - Cite this manual section in the issue as glibc's own statement that results may differ.
  - Note that the outside study measures x86-64 only, so it says nothing about aarch64 or macOS.
- **Access.** Free (GNU FDL).
  - glibc's NEWS file sits behind a bot check on sourceware's git web, and HAL's PDF behind another, so neither was fetched.
- **URL.** https://sourceware.org/glibc/manual/latest/html_node/Errors-in-Math-Functions.html
- **Downloaded:** yes (the manual page). Checked 2026-10-29.

**CORE-MATH** (project pages, Inria)
- **What it provides.** Correctly rounded math functions, MIT-licensed. The project claims correct rounding in all IEEE rounding modes.
  - For univariate binary32 functions this is checked exhaustively. For bivariate or wider formats, `pow` in binary64 among them, it is checked "only with respect to known hard-to-round cases".
  - The functions are tested on x86-64 Linux with and without FMA. They don't necessarily handle NaN, infinities, exceptions or the inexact flag.
  - glibc has taken in seven binary64 functions since 2.43 (`acosh`, `asinh`, `atanh`, `erf`, `erfc`, `lgamma`, `tgamma`) and many binary32 functions since 2.42.
- **Touches.** U1's fix for libm differences, through the shim in checks/swmm.
- **Do.**
  - Say in the issue that CORE-MATH's binary64 `pow` is correct only as far as known hard cases go, not proven.
  - Pin the CORE-MATH commit in checks/swmm.
- **Access.** Free. The licence is in part C.
- **URLs.** https://core-math.gitlabpages.inria.fr/ and its FAQ.
- **Downloaded:** yes (2 pages). Checked 2026-10-29.

**Compiler documentation: GCC, Clang and MSVC** (each project's current manual)
- **GCC.**
  - `-ffp-contract=fast` is the default except in standards-compliant C modes such as `-std=c11`, where it is `off`.
  - `-ffp-contract=on` contracts "within one expression, but not across different statements".
  - Its implementation-defined behaviour page says, of `<math.h>` accuracy, "The accuracy is unknown". It also says the `FP_CONTRACT` pragma "is not implemented".
- **Clang.** `on` is the default for C. "Fusion across statements is not compliant with the C and C++ standards", and needs `fast`.
- **MSVC.** "Floating-point contractions aren't generated by default under `/fp:precise`. This behavior is new in Visual Studio 2022". `/fp:fast` may contract and reorder.
- **Touches.** U1's build PR and issue.
- **Do.**
  - Quote these lines in the build PR. They are why the flag is set explicitly for each compiler.
  - Windows remains untested.
- **Access.** Free.
- **URLs.**
  - https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html
  - https://gcc.gnu.org/onlinedocs/gcc/Floating-point-implementation.html
  - https://clang.llvm.org/docs/UsersManual.html
  - https://learn.microsoft.com/en-us/cpp/build/reference/fp-specify-floating-point-behavior
- **Downloaded:** yes (5 pages). Checked 2026-10-29.

## 2. Model quality and model specifications

**Guidance on the Development, Evaluation, and Application of Environmental Models** (EPA Council for Regulatory Environmental Modeling, EPA/100/K-09/003, March 2009)
- **What it says.** It is non-binding guidance on developing, evaluating and applying models in EPA decisions.
  - §3.3.2 asks for code verification: the code "has no inherent numerical problems with obtaining a solution". It also suggests independent testing.
  - Appendix C, Box C2, asks that "sources of error, such as rounding, are minimal".
  - It defines precision as "the quality of being reproducible in outcome or performance".
- **Touches.** U1 and U6, as the federal frame for model QA.
- **Do.** Cite §3.3.2 beside G-5M when explaining why cross-platform bits matter to regulatory users.
- **Access.** Free. US government work.
- **URL.** https://www.epa.gov/sites/default/files/2015-04/documents/cred_guidance_0309.pdf
- **Downloaded:** yes. Checked 2026-10-29.

**EPA QA/G-5M, Guidance for Quality Assurance Project Plans for Modeling** (EPA/240/R-02/007, December 2002)
- **What it says.**
  - §4.2.3.2 (element B10b): the framework is "the model and its supporting hardware and operating system", and installation needs beta testing on "a wide variety of different platforms".
  - §4.3: regression tests.
  - §4.4.1 (D1): code verification, "sources of error, such as rounding, are minimal".
  - §5.3.4, a worked example: values "can differ by no more than a rounding error (usually less than ±0.1%)".
- **Status.** Not superseded. EPA's directives page lists it as current guidance, and both the 2024 QAPP Standard (§7) and the 2025 QAPP Guidance (§7) list it under related guidance.
- **Touches.** U1 and U6.
- **Do.** Use it as the reason, in the issue and the README, why a 13% platform difference matters to users working under a QAPP.
- **Access.** Free.
- **URL.** https://www.epa.gov/quality/guidance-quality-assurance-project-plans-modeling-epa-qag-5m
- **Downloaded:** yes. Checked 2026-10-29.

**EPA's quality directives:**
- Environmental Information Quality Policy (CIO 2105.4, 2024-03-20).
- Environmental Information Quality Procedure (CIO 2105-P-01.4).
- Quality Assurance Project Plan Standard (CIO 2105-S-02.1, 2024-04-03). It replaced QA/R-5 for contracts issued from 2023-07-18 and for new grant awards from 2023-08-31.
- Quality Assurance Project Plan Guidance (2025-10-01). It replaces QA/G-5 (2002).

What they say and what we do:
- **What they say.**
  - The QAPP Standard covers "information provided by models" and "development of environmental software, tools, models".
  - For models, QC "include[s], but [is] not limited to model calibration and model validation (sensitivity analyses)".
  - The 2025 Guidance asks a modeling QAPP to "describe the criteria for code verification" (D2). It also asks for the software and hardware configuration (B7).
- **Touches.** Anyone running pyswmm, WaterTAP or QSDsan in EPA-funded work.
- **Do.** Nothing binds us. The "for QAPP writers" line in checks/swmm is enough.
- **Access.** Free.
- **URL.** https://www.epa.gov/quality/quality-program-directives
- **Downloaded:** yes (4 files). Checked 2026-10-29.

**SWMM's reference documents** (EPA Office of Research and Development):

| Document | Number and date |
| --- | --- |
| Reference Manual Vol. I, Hydrology | EPA/600/R-15/162A, January 2016 |
| Reference Manual Vol. II, Hydraulics | EPA/600/R-17/111, May 2017, with an addendum dated 2022-02-10 |
| Reference Manual Vol. III, Water Quality | EPA/600/R-16/093, July 2016 |
| Reference manuals' errata | 2022 |
| User's Manual, version 5.2 | EPA/600/R-22/030, revised February 2022 |
| Quality Assurance Report: Dynamic Wave Flow Routing | EPA/600/R-06/097, September 2006 |

- **What they specify.** The model's equations and numerical methods. This is the specification that nrtest's benchmarks stand in for.
  - **Vol. II** gives dynamic wave's iteration: relaxation 0.5, convergence 0.005 ft, 8 trials (§3.2-3.3, p. 47). It also gives the root-finding tolerances, for example 0.01% of full area.
  - **The User's Manual** defines `HEAD_TOLERANCE`, `MAX_TRIALS` and `THREADS` (default 1), on p. 334. §8.5 calls continuity errors over 10% questionable.
  - **The 2006 QA report** compared SWMM 5.0.006 with SWMM 4.4h on 20 tests: 10 Extran manual examples, 5 "challenge" cases and 5 user-supplied systems. Flows "for the most part" matched closely. Where they didn't, the report blamed "numerical instabilities" in SWMM 4, in cases with "oscillatory flows due to significant inertial effects". The suite's `extran/`, `routing/` and `user/` directories hold 10, 5 and 5 models, which looks like the same 20 *(inference, not checked against the report's data)*.
- **Touches.** U1, U2 and the issue.
- **Do.**
  - Trace the trial counts against `HEAD_TOLERANCE` on user5.
  - Cite Vol. II p. 47 for the convergence test in the issue.
  - Note that no SWMM document specifies floating-point evaluation or a numerical tolerance between builds. nrtest-swmm's `rtol 0.01` is a CI choice, not part of the model.
- **Access.** Free. The manuals are PDFs on NEPIS, linked from EPA's SWMM page.
- **URL.** https://www.epa.gov/water-research/storm-water-management-model-swmm
- **Downloaded:** yes (7 files; the QA report is inside a zip that was listed, not extracted). Checked 2026-10-29.

**EPANET 2.2 User Manual** (EPA/600/R-20/133)
- **What it specifies.** The EPANET model and its input format. `ACCURACY` (default 0.001) is the convergence test: the sum of flow changes divided by total flow.
- **Touches.** U1's EPANET result: Net3's "Final Mass" changes under FMA.
- **Do.** If the EPANET finding goes upstream to OWA, cite the `ACCURACY` criterion in the same way.
- **Access.** Free.
  - EPA's own PDF is the Spanish edition.
  - The English PDF is in the USEPA/EPANET2.2 repository, and the online manual is at usepa.github.io/EPANET2.2.
- **URL.** https://www.epa.gov/water-research/epanet
- **Downloaded:** yes (English PDF). Checked 2026-10-29.

**Benchmark Simulation Model No. 1 and No. 2** (IWA Task Group on Benchmarking of Control Strategies):
- *BSM1* report, Lund University, 2008, LUTEDX/(TEIE-7229)/1-62/(2008). The sha256 matches the copy in checks/bsm1.
- 2018 draft, BSM Technical Report No. 1.
- BSM Technical Report No. 3, *BSM2 General Description*.
- The ADM1 report written for BSM2 (2006).

What they specify and what we do:
- **What they specify.** Each benchmark's plant, models, influent, procedures and evaluation criteria.
  - BSM1 §4: users "verify their implementations" against the open-loop steady state and first day.
  - BSM2 Appendix 3 prints two answers: FORTRAN (Runge-Kutta 4, step 0.005 h) and Simulink (ode45, absolute tolerance 1e-8, relative 1e-5). They differ in the third or fourth significant digit, for example effluent SNH 7.203620 against 7.2028.
- **Touches.** U6.
- **Do.**
  - Keep judging implementations to the printed digits, as checks/bsm1 does.
  - If U6 moves to BSM2, compare against both columns, and expect agreement only to the digits where the two agree.
  - Describe each implementation's influent interpolation in WaterML 2.0's terms (see section 4).
- **Access.** Free, with no registration. No licence is stated, so the files stay out of the repo, as checks/bsm1 already does.
- **URLs.** https://www2.iea.lth.se/publications/Reports/LTH-IEA-7229.pdf, http://iwa-mia.org/benchmarking/
- **Downloaded:** yes (4 files). Checked 2026-10-29.

**IWA Scientific and Technical Reports No. 9, *Activated Sludge Models ASM1, ASM2, ASM2d and ASM3*** (2000), **and No. 22, *Guidelines for Using Activated Sludge Models*** (Good Modelling Practice, 2012)
- **What they specify.**
  - STR 9 holds the defining text and parameter sets of the ASM family.
  - STR 22 sets out a protocol for quality control of simulation studies.
- **Touches.** U6.
  - BSM1 fixes its own ASM1 parameters, so BSM1 is the specification for the benchmark checks.
  - STR 9 matters only if a proposed fix depends on ASM1's original text.
- **Do.** Nothing now. Borrow before buying.
- **Access.** Paid.
  - Neither is open access, as far as a search shows *(snippet)*.
  - IWA Publishing's site served an expired certificate on 2026-10-29, and iwaponline.com a bot check, so the publisher's prices were not read.
  - Retailers list STR 9's PDF at €93.95-126.99 *(snippet)*.
- **Downloaded:** no. Checked 2026-10-29.

**nrtest and the SWMM and EPANET test suites** (Open Water Analytics; pyswmm)
- **nrtest.**
  - Its built-in comparison is "default", equivalent to `diff`, or "null".
  - Tolerant comparisons are plugins, with `(path_test, path_ref, rtol, atol)` set on the command line.
  - The project was last pushed in 2017.
- **The suites.**
  - swmm-nrtestsuite's README says only "Numerical regression test suite". Its conventions live in the CI scripts and in nrtest-swmm (see checks/swmm).
  - EPANET's example-networks repo lists the steps for adding a test and its benchmark.
- **Touches.** U1 and U2.
- **Do.** In the issue, point out that nrtest's own default is exact comparison. With contraction off, Linux builds already match the 2023 benchmark bit for bit, so the Linux CI jobs could use an exact or near-exact comparison. macOS would also need a correctly rounded libm.
- **Access.** Free (MIT).
- **URLs.**
  - https://github.com/OpenWaterAnalytics/nrtest
  - https://github.com/pyswmm/swmm-nrtestsuite
  - https://github.com/OpenWaterAnalytics/epanet-example-networks
- **Downloaded:** yes (7 small files). Checked 2026-10-29.

## 3. Design and condition standards

**Recommended Standards for Wastewater Facilities ("Ten States Standards")** (Great Lakes - Upper Mississippi River Board, Wastewater Committee). Editions 2014 and 2026.
- **What it specifies.** Design policy for collection and treatment works.
  - In 2014, Chapter 30 covers sewers: capacity, details, manholes, siphons and crossings.
  - Chapter 40 covers pumping stations. §46, "Alarm Systems", is quoted in the lead list above. §47 covers emergency operation and §49 force mains.
- **Touches.** O1 (lift-station watch). Indirectly, synthetic sewer networks such as SWMManywhere.
- **Do.** Cite §46 for O1's requirements. Buy the 2026 edition, which is current, before relying on it.
- **Access.**
  - The 2014 edition is a free archived PDF on the Minnesota Department of Health's page.
  - The 2026 edition is $14.95 to download, $24.15 as a book and $27.95 for both, sold through Minnesota's publications store. "Downloads cannot be copied, printed, or shared."
- **URL.** https://www.health.mn.gov/communities/environment/water/tenstates/standards.html
- **Downloaded:** yes (2014 only). Checked 2026-10-29.

**TR-16, Guides for the Design of Wastewater Treatment Works** (NEIWPCC), 2026 edition
- **What it specifies.** Design guidance for wastewater treatment works. The 2026 edition replaces the 2016 version and adds climate resilience, PFAS and microplastics.
- **Touches.** Background only.
- **Do.** Nothing.
- **Access.** Paid.
  - $150 bound, $95 PDF, $200 both.
  - The PDF is "licensed to the individual purchaser... External distribution, sharing, or redistribution is not permitted".
- **URL.** https://payments.neiwpcc.org/product/tr-16-guides-for-the-design-of-wastewater-treatment-works-2026-edition/
- **Downloaded:** no. Checked 2026-10-29.

**Gravity Sanitary Sewer Design and Construction** (ASCE Manual of Practice No. 60 / WEF MOP FD-5, 2nd edition, 2007)
- **What it specifies.** Practice for designing and building gravity sewers.
- **Touches.** Background for any sewer-design use of SWMM.
- **Do.** Nothing.
- **Access.** Paid. ASCE's price was not found.
- **Downloaded:** no. Checked 2026-10-29.

**EN 752:2017, Drain and sewer systems outside buildings: Sewer system management** (CEN)
- **What it specifies.** Objectives and the management process for sewer systems. A draft amendment, prA1, is listed.
- **Touches.** Background for European tools such as TEKSI.
- **Do.** Nothing.
- **Access.** Paid, €39.68 (EVS).
- **Downloaded:** no. Checked 2026-10-29.

**EN 13508-2:2003+A1:2011, Investigation and assessment of drain and sewer systems outside buildings, Part 2: Visual inspection coding system** (CEN)
- **What it specifies.** The defect-coding system for CCTV sewer inspection. It is the open alternative to PACP named in the landscape.
- **Touches.** The parked condition-coding idea, and any Python port of `kwb.en13508.2`.
- **Do.** Buy it (€47.12 at EVS) before writing a parser. Don't work from a reader package alone.
- **Access.** Paid, €47.12 (EVS).
- **Downloaded:** no. Checked 2026-10-29.

**EN 16323:2014, Glossary of wastewater engineering terms** (CEN)
- **What it specifies.** Standard terms.
- **Touches.** Vocabulary, for example for mWater or Brick proposals.
- **Do.** Nothing now.
- **Access.** Paid, €39.68 (EVS).
- **Downloaded:** no. Checked 2026-10-29.

**PACP, LACP and MACP** (NASSCO), version 8
- **What they specify.** The US coding for pipe, lateral and manhole condition.
- **How access works.**
  - **For individuals.** A training course leads to certification: $1,270 for initial certification (PACP alone, or all three), manual included. Certification lasts three years. Replacement manuals cost $155 and are "available to certified individuals only".
  - **For software.** Vendors must "request and be granted a licensing agreement", and certified software is tested against the version 8 exchange database. NASSCO moved that database from Access to SQLite in version 8 *(snippet)*. No fees are shown.
- **Touches.** The parked condition-coding idea.
- **Do.** Nothing that claims PACP compatibility without a licence. EN 13508-2 stays the open target.
- **URL.** https://nassco.org/education-and-training/pacp-lacp-macp/
- **Downloaded:** no. Checked 2026-10-29.

**ISO 24510:2024, 24511:2024 and 24512:2024, Activities relating to drinking water and wastewater services** (ISO/TC 224)
- **What they specify.** Guidelines for assessing service to users (24510), for managing wastewater utilities and assessing their services (24511), and the same for drinking water (24512). They give example performance indicators, without targets *(snippet, for 24511's scope)*.
- **Touches.** N2's sorting of plants, at most.
- **Do.** Nothing.
- **Access.** Paid, from EVS: 24510 costs €241.44, 24511 €272.12 and 24512 €272.12.
- **Downloaded:** no. Checked 2026-10-29.

## 4. Data and reporting

**ICIS-NPDES data exchange, schema v5.15** (EPA, on the Exchange Network)
- **What it specifies.** The XML that states and permittees use to send ICIS-NPDES data, DMRs among it.
  - In `ICIS_DischargeMonitoringReport_v5.15.xsd`, a `NumericReport` holds a code (Q1, Q2, C1, C2 or C3), a received date, a no-discharge indicator, a quantity, an adjusted quantity and a qualifier.
  - Quantities are `Decimal8FloatingType`: `xsd:decimal`, 0 to 8 fraction digits and 9 digits in all, or an asterisk.
  - There is nothing for daily values.
  - The release includes a flow configuration document (v5.0), a change log, a data exchange template, a batch user guide and an example instance.
- **Touches.** N1 and N2.
- **Do.**
  - N1 emits decimal strings that validate against this XSD, and never a binary float's repr.
  - The conformance suite should include the XSD check.
- **Access.** Free.
- **URL.** https://www.exchangenetwork.net/data-exchange/icis-npdes/
- **Downloaded:** yes (6 files; the zip was read, not extracted). Checked 2026-10-29.

**NetDMR data exchange, schema v1.0** (EPA, on the Exchange Network)
- **What it specifies.** NetDMR's own exchange. Its change log starts with a 2007 draft.
- **Touches.** N1, as background.
- **Do.** Nothing. N1 stays out of submission, as ideas.md already says.
- **Access.** Free.
- **URL.** https://www.exchangenetwork.net/data-exchange/netdmr/
- **Downloaded:** yes (6 files). Checked 2026-10-29.

**ECHO's ICIS-NPDES data dictionaries and reference tables** (EPA)
- **What they specify.** The DMR, limit and download-summary dictionaries define every column of ECHO's bulk files.
  - Examples: `DMR_VALUE_NMBR`, `DMR_VALUE_STANDARD_UNITS` ("as calculated by the system"), `NODI_CODE` and `EXCEEDANCE_PCT`.
  - Qualifier codes: <, <=, >, >=, =, T (too numerous to count), E (estimated).
  - The statistical base table lists 186 codes, with separate codes for 7-day and calendar-week averages and for several geometric means.
  - The effluent-charts web service page documents the per-permit REST call.
- **Touches.** N2 directly, and N1's profiles.
- **Do.** Key N1's rule profiles and N2's screen on `STATISTICAL_BASE_CODE`. Treat ECHO's standard-unit values as derived, not reported.
- **Access.** Free.
- **URL.** https://echo.epa.gov/tools/data-downloads/icis-npdes-dmr-and-limit-data-set
- **Downloaded:** yes (6 files). Checked 2026-10-29.

**OGC SensorThings API Part 1: Sensing, version 1.1** (OGC 18-088; approved 2020-11-26, published 2021-08-04)
- **What it specifies.** A REST and MQTT API for observations. An Observation's `resultQuality` is zero or more `DQ_Element`.
- **Status.** OGC's standard page still lists 1.1 as the latest Part 1, alongside Tasking 1.0, STAplus 1.0 and the WebSub extension 1.0. 2.0 is not among the adopted documents. This settles one item in the landscape's "Not checked".
- **Touches.** O1, N3 and fieldmesh.
- **Do.** Keep fieldmesh on 1.1.
- **Access.** Free, under OGC's document notice.
- **URL.** https://www.ogc.org/standards/sensorthings/
- **Downloaded:** yes (1.1). Checked 2026-10-29.

**OGC WaterML 2.0: Part 1, Timeseries, version 2.0.1** (OGC 10-126r4, corrigendum, published 2014-02-24)
- **What it specifies.** An encoding for hydrological time series. Its `interpolationType` vocabulary includes `Continuous`, `ConstPrec`, `ConstSucc` and `AveragePrec`.
- **Touches.** U6, where the BSM1 implementations differ in how they interpolate influent samples. Also the averages behind N1's daily values.
- **Do.** In U6's write-up and any upstream issue, name each implementation's influent behaviour in these terms: holding each sample is `ConstSucc`, and linear interpolation is `Continuous`.
- **Access.** Free.
- **URL.** https://www.ogc.org/standards/waterml/
- **Downloaded:** yes. Checked 2026-10-29.

**CDC NWSS data dictionary and submission format** (CDC National Wastewater Surveillance System)
- **What it specifies.** The format in which health departments submit wastewater data through CDC's DCIPHER portal.
  - The current dictionary appears to be v6.3.0 (2026-05-19). It is listed among the forms of OMB collection 0920-1422, whose revision went to OMB on 2026-10-06 (reginfo.gov). The file name came only from a search snippet of a Federal Register notice *(snippet)*.
- **Touches.** The parked wastewater-surveillance ideas.
- **Do.** Nothing until that idea is active. Then fetch the dictionary from CDC, not from a state mirror. A California copy is v5.2.2.
- **Access.** The dictionary itself is free, but it could not be reached: CDC's reporting page returned 404 to one reader and 403 to another on 2026-10-29.
- **URLs.** https://www.cdc.gov/nwss/reporting.html; https://www.reginfo.gov/public/do/PRAViewICR?ref_nbr=202609-0920-006
- **Downloaded:** no. Checked 2026-10-29.

**PHES-ODM, the Public Health Environmental Surveillance Open Data Model** (v3.0.1, 2026-09-17)
- **What it specifies.** A data model for wastewater and environmental surveillance: a dictionary of 2,344 parts, with LinkML, SQL and CSV forms.
  - Detection limits are explicit: `lod`, `loq`, `beLOD`, and a `reportable` flag.
  - It entered "a long-term maintenance phase as of September, 2026".
  - Its LICENSE file begins "cc-by-4.0" and then gives the CC BY-SA 4.0 text. That is a third wording beside the README's CC BY 4.0 (the licence question is part C's).
- **Touches.** U5 and the parked surveillance ideas.
- **Do.** U5's licence report should quote the LICENSE file's own first line.
- **Access.** Free.
- **URL.** https://github.com/PHES-ODM/PHES-ODM (tag v3.0.1)
- **Downloaded:** yes (4 files). Checked 2026-10-29.

**Brick schema** (v1.4.4 released 2025-05-02; v1.5.0-rc2, 2026-10-07)
- **What it specifies.** An RDF ontology for building systems.
  - Neither version has sewer, wastewater or lift-station classes, only `Grease_Interceptor` and the cooling-tower `Collection_Basin_Water_*` points.
- **Touches.** U4 ("take sewers to Brick").
- **Do.** A proposal would target the release after 1.5, which is already at release-candidate stage.
- **Access.** Free (BSD-3-Clause).
- **URL.** https://github.com/BrickSchema/Brick/releases
- **Downloaded:** yes (both `Brick.ttl` files). Checked 2026-10-29.

**mWater Asset Standards: sanitation and water standards, version 1.0** (mWater; repository at commit `c676752`)
- **What it specifies.** Asset types, attributes, choices and units, as CSV and JSON.
  - Its REVIEW-NEEDED.md lists errata.
    - Several flow-rate conversion factors contradict the standards' own conversion rule, and the two standards disagree on gallons per minute and per day.
    - The acre-foot is published as 1223.489 where the correct figure is 1233.48 m3.
- **Touches.** U4.
- **Do.** Start U4's review from that file. Check `units.csv`'s factors with exact decimal arithmetic.
- **Access.** Free (CC BY-SA 4.0).
- **URL.** https://github.com/mWater/asset-standards
- **Downloaded:** yes (5 files). Checked 2026-10-29.

## 5. Lab methods

**Standard Methods for the Examination of Water and Wastewater**, 24th edition (2023; APHA, AWWA and WEF)
- **What it specifies.** Laboratory methods, among them the ones most permits use for BOD (5210 B) and TSS (2540 D) *(method numbers unchecked)*.
- **Touches.** N1 and N3, through the methods a DMR's numbers come from.
- **Do.** Nothing. The methods' arithmetic matters less than the permit's.
- **Access.** Paid.
  - Print $460, or $322 for members, at AWWA's store *(snippet)*.
  - The online subscription price was not found, and standardmethods.org refused the reader.
- **Downloaded:** no. Checked 2026-10-29.

**EPA methods approved in 40 CFR 136, and the MDL procedure** (EPA Office of Water)
- **Method 1603.1, *E. coli* by membrane filtration** (EPA-821-R-23-008, September 2023).
  - It says, "Generally, rounding should only occur after the final calculation" (§14).
  - Results are reported as "E. coli CFU per 100 mL" (§13.3).
- **Method 350.1, ammonia** (Rev. 2.0, 1993).
- ***Definition and Procedure for the Determination of the Method Detection Limit, Revision 2*** (EPA 821-R-16-006, December 2016). This is 40 CFR 136 Appendix B as a stand-alone document. The MDL is "the minimum measured concentration... that can be reported with 99% confidence" to be distinguishable from blanks.
- **Touches.** N1 (rounding, non-detects) and N3 (bench sheets).
- **Do.** N1 rounds only at the end, as 1603.1 says. Its non-detect profiles cite the MDL definition and the permit's own reporting limit.
- **Access.** Free.
- **URL.** https://www.epa.gov/cwa-methods
- **Downloaded:** yes (3 files). Checked 2026-10-29.

**ISO/IEC 17025:2017, General requirements for the competence of testing and calibration laboratories** (ISO and IEC)
- **What it specifies.** The accreditation standard for labs.
- **Touches.** N3, if a pilot lab is accredited.
- **Do.** Nothing until N3 is active.
- **Access.** Paid, €238.77 (EVS).
- **Downloaded:** no. Checked 2026-10-29.

**TNI Standard, Volumes 1-4, 2016** (The NELAC Institute)
- **What it specifies.** Accreditation requirements for US environmental labs.
- **How access works.** The 2016 Volume 1 costs $320 for a single-use non-member licence, covering one computer. The 2003 NELAC standard is a free PDF. Which edition applies is up to each accreditation body.
- **Touches.** N3.
- **Do.** Nothing now.
- **URL.** https://nelac-institute.org/content/CSDP/standards.php
- **Downloaded:** no. Checked 2026-10-29.

## 6. Operational technology and safety (for the parked lift-station watch)

**NFPA 820, Standard for Fire Protection in Wastewater Treatment and Collection Facilities** (NFPA; 2024 edition *(snippet)*)
- **What it specifies.** Hazard classification and protection for wastewater spaces, including pump-station wet wells *(unchecked)*.
- **Touches.** O1: any sensor or radio near a wet well.
- **Do.** Before O1 leaves the shelf, read the wet-well classification. Keep electronics outside classified spaces or use listed equipment.
- **Access.** Paid. Resellers list it at $165-220 *(snippet)*. NFPA's free read-only access needs an account *(snippet)*, so it was not used.
- **Downloaded:** no. Checked 2026-10-29.

**NFPA 70, National Electrical Code** (NFPA, 2026 edition): Articles 500 and 501 (hazardous locations) and 430 (motors)
- **What it specifies.** US electrical installation rules.
- **Touches.** O1's hardware.
- **Do.** Same as NFPA 820.
- **Access.** Paid. Free read-only access needs an NFPA account *(snippet)*, so it was not used.
- **Downloaded:** no. Checked 2026-10-29.

**IEC 62443, Security for industrial automation and control systems** (IEC)
- **The parts priced here:**
  - 2-1:2024, the asset owner's security program;
  - 3-3:2013, system requirements and security levels;
  - 4-2:2019, component requirements;
  - TS 1-1:2009, concepts.
  - Part 4-1 (secure development lifecycle) is the one that would apply to us as a supplier *(unchecked)*.
- **Touches.** O1, fieldmesh, and any SCADA tool in the landscape.
- **Do.** Read 4-1 and 4-2 before O1 ships anything to a utility.
- **Access.** Paid, from EVS: 2-1 costs €540.23, 3-3 €506.89, 4-2 €540.23 and TS 1-1 €506.89.
- **Downloaded:** no. Checked 2026-10-29.

**NIST Cybersecurity Framework 2.0** (NIST CSWP 29, 2024-02-26) **and NIST SP 800-82 Rev. 3, *Guide to Operational Technology (OT) Security*** (September 2023)
- **What they specify.**
  - CSF 2.0 organises outcomes under six functions: Govern, Identify, Protect, Detect, Respond and Recover.
  - SP 800-82r3 is NIST's OT security guide.
- **Touches.** O1.
- **Do.** Map O1's design to CSF 2.0's outcomes, and check its network design against SP 800-82r3.
- **Access.** Free.
- **URL.** https://nvlpubs.nist.gov/
- **Downloaded:** yes (both). Checked 2026-10-29.

**EPA, CISA and FBI water-sector cybersecurity guidance**
- **The documents:**
  - *Top Cyber Actions for Securing Water Systems* (February 2024). Its eight actions: reduce exposure to the public internet; regular assessments; change default passwords; inventory OT/IT assets; incident response and recovery plans; backups; reduce exposure to vulnerabilities; awareness training.
  - *Incident Response Guide: Water and Wastewater Sector* (January 2024; CISA has an October 2024 version).
  - EPA's *Cybersecurity Incident Action Checklist* (2024).
  - *Foundations for OT Cybersecurity: Asset Inventory Guidance* (2025-08-13, a joint guide by six countries' agencies).
  - EPA's small-wastewater-system case study.
  - EPA's *Cybersecurity Procurement Evaluation Checklist* (2026).
- **Touches.** O1, and the landscape's security notes on OpenPLC, FUXA and Rapid SCADA.
- **Do.**
  - Write O1 so it passes the procurement checklist a utility would apply to it.
  - Make "no exposure to the public internet" a design rule.
- **Access.** Free. TLP:CLEAR.
  - cisa.gov refused automated download, so EPA's copies were used. That means the January 2024 edition of the incident response guide, not CISA's October 2024 one.
- **URL.** https://www.epa.gov/waterresilience/cybersecurity-planning
- **Downloaded:** yes (6 files; the October 2024 guide was not). Checked 2026-10-29.

## Not checked

- **The published C23's clause numbers.** GCC's manual and N3550 say 6.3.2.4 and 7.12.3, where N3220 says 6.3.1.4 and 7.12.2.
- **IEEE 754-2019's own text,** clauses 9.2, 10.4 and 11 among them.
- **The price pages** of IEEE, ASCE, IWA Publishing and NFPA, and the online price of Standard Methods.
- **Whether macOS's compiler and libm define `__STDC_IEC_559__`.** Only Linux with glibc was checked.
- **CDC's current NWSS dictionary file.**
- **The 2026 Ten States and TR-16 editions' contents.**
