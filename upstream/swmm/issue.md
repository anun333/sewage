<!-- Posted 2026-10-29 as https://github.com/pyswmm/Stormwater-Management-Model/issues/431 after the maintainer read and approved this text. -->

**Title:** Results change with FMA contraction and the C library's maths; a build flag makes them reproducible

I checked whether SWMM gives the same results on different machines. The set-up:

- **Code:** `develop` at 6c81201.
- **Models:** the 34 in swmm-nrtestsuite v3.3.0 `public/`, the tag CI uses.
- **What I varied:** thread count, compiler, flags, CPU and operating system.
- **How I compared:** the `.out` files bit for bit, and the `.rpt` files after masking the timing and version lines.

**Thread count doesn't change anything.** I ran 1, 2, 4 and 8 threads, with repeats, under both gcc's OpenMP and LLVM's, and every run was bit-identical. The loops in `dynwave.c` work per link and per node with no reductions, so that's expected, but it's good to have it confirmed.

**Two things do change results, by more than nrtest-swmm allows:**

1. **Fused multiply-adds.** gcc and clang turn `a*b + c` into one FMA instruction wherever the target has it. That happens by default on aarch64 and Apple silicon, and on x86-64 with `-march=native`. The FMA rounds once where the separate multiply and add round twice, and on some models that last-bit difference grows. Against a build without FMA:
   - **Bits change on 9 of the 34 models.**
   - **user5, user1 and Example1 fail `allclose` (rtol 0.01).** On user5, for example, LIB_2's flow at period 32 reads 400.6 against 450.9 cfs.
   - **The report comparison fails on five models.**
2. **The C library's maths.** glibc picks an FMA or a non-FMA version of `exp`, `log` and `pow` depending on the CPU it runs on. So one binary gives different user5 results on a CPU with FMA than on one without, and fails `allclose` on 277 elements. Apple's libm differs from glibc's again.

This looks like what #203 ran into in 2018. A rebuild there failed the regression tests on Example1, Example3, test5, user1 and user5, and the issue was closed without a cause. The suite's own benchmarks show it today: the Linux, macOS and Windows benchmarks of v3.3.0 fail against each other on the same models.

**Per platform, `.out` files against an x86-64 gcc -O2 build:**

| | x86-64 Linux | aarch64 Linux | macOS (M1) |
| --- | --- | --- | --- |
| default build | same bits (gcc emits no FMA for baseline x86-64) | 10 models differ; 3 fail `allclose` | 10 models differ; 3 fail `allclose` |
| `-ffp-contract=off` | same bits | same bits | 5 differ: 4 from Apple's libm, 1 from the `gage.c` bug below |
| `-ffp-contract=off`, maths calls answered by a correctly rounded libm (CORE-MATH) | same bits | same bits | same bits |

The FMA builds disagree with each other too: aarch64 gcc and Apple clang differ on 6 models. So there isn't one "ARM answer" to keep as a benchmark.

**This reaches pyswmm users through the published wheels.**
- The aarch64 wheel of swmm-toolkit 0.17.0 has 552 FMA instructions in `libswmm5.so`; the x86-64 wheel has none.
- Run on the 34 models, the two wheels disagree on 10, and 3 fail `allclose`. On user5, LIB_2's flow at period 32 is again 400.6 cfs on x86-64 against 450.9 on ARM Linux.
- The x86-64 wheel matches a `-ffp-contract=off` build of the same commit (`ebbce382`) bit for bit.

swmm-toolkit builds the solver through its top-level CMakeLists (`add_subdirectory(swmm-solver)`), so the build change below would reach the wheels once the submodule is updated.

**What I'd propose: two small PRs, which I can open if you want them.**

- **A build change.** Add `-ffp-contract=off` for gcc and clang, via `add_compile_options` in the top-level CMakeLists, so it reaches every target. Change MSVC Release's `/fp:fast` to `/fp:precise`; since Visual Studio 2022, `/fp:precise` generates no contractions by default.
  - With it, gcc and clang builds on x86-64 at `-O0` to `-O3`, with or without `-march=native`, all write the same `.out` bits, and gcc `-O2` on aarch64 Linux writes those bits too.
  - Those bits are also the suite's existing 2023 Linux benchmark, on 33 of 33 models compared.
  - It costs about 1% in run time: 1.5% on aarch64 and 0.9% on an M1, over every model at one thread, and nothing visible on x86-64 with `-march=native`. All of these were measured on shared machines, within their noise.
- **A fix for an out-of-range conversion in `gage.c`**, the one difference the flag doesn't remove. A rain gage reading a one-point time series has no interval, so `dxMin` stays at `BIG`. `gage_validate` then converts `dxMin*SECperDAY` (8.64e14) to `int`, at line 251. That is out of range: undefined in ISO C (C17 6.3.1.4p1), and under Annex F, which gcc and clang on glibc advertise through `__STDC_IEC_559__`, the "invalid" exception with an unspecified value (F.4). Either way the result isn't portable:
  - x86-64 yields INT_MIN, so there's no warning;
  - aarch64 saturates to INT_MAX, so `catchment_as_outfall`'s report gains WARNING 09.

  The fix leaves the interval at 0 when it doesn't fit, which keeps x86-64's output. EPA's v5.2.4 has the same line.

**What remains after both.** macOS's libm still gives different bits. I'm not proposing a new dependency for that, only noting that a correctly rounded libm closes the gap: an `LD_PRELOAD`/`DYLD_INSERT_LIBRARIES` shim routing SWMM's 11 maths imports to CORE-MATH made all three platforms identical. With the flag in place, the Linux CI jobs could share one benchmark and might not need to be `experimental`.

**What I didn't test:** MSVC and Windows, including whether `/fp:precise` makes Windows match Linux.

The scripts, digests and commands are at https://github.com/anun333/sewage/tree/main/checks/swmm. They are plain Python and POSIX sh. They build, run and compare digests, with controls: planted bit flips and missing files must be caught.

Related: #203; pyswmm/swmm-python#47 (a more forgiving comparison); USEPA/Stormwater-Management-Model#143 (the arm64 build).

Drafted with an AI assistant (Claude), which also ran the builds and checks reported here; I read it before posting.
