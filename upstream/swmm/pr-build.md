<!-- DRAFT PR for pyswmm/Stormwater-Management-Model, base develop. Patch: 0002-build-*.patch. Not opened. -->

**Title:** build: no fused multiply-adds, and /fp:precise instead of /fp:fast

See #ISSUE for the measurements.

gcc and clang contract `a*b + c` into a single fused multiply-add wherever the target has the instruction: by default on aarch64 and Apple silicon, and on x86-64 with `-march=native`. MSVC's `/fp:fast` allows contraction and more. An FMA rounds once where a multiply and an add round twice, and on some models the difference grows. On swmm-nrtestsuite v3.3.0:
- builds with FMA fail nrtest-swmm's `allclose` (rtol 0.01) on Example1, user1 and user5 against a build without;
- they fail the report comparison on five models;
- the suite's own Linux, macOS and Windows benchmarks fail against each other in the same way.

**The change** is two lines:
- `add_compile_options($<$<C_COMPILER_ID:GNU,Clang,AppleClang>:-ffp-contract=off>)` in the top-level CMakeLists, before the subdirectories, so it reaches `swmm5`, `shared_objs`, the output library and `runswmm`;
- `/fp:fast` → `/fp:precise` for MSVC Release builds. Since Visual Studio 2022, `/fp:precise` generates no contractions by default; Microsoft's docs say earlier versions could. Without `/arch:AVX2`, x64 MSVC has no FMA to emit anyway.

**Tested** on the 34 models in `public/`, comparing `.out` files bit for bit and `.rpt` files with their timing and version lines masked:

| | before | after |
| --- | --- | --- |
| x86-64, gcc 13.3 and clang 18, `-O3 -march=native` | 9 models differ from `-O2` | all 34 identical to `-O2` |
| aarch64 Linux (Neoverse-N1), gcc 14.2, default `-O2` | 10 models differ from x86-64 | all 34 identical to x86-64, `.rpt` included (with the gage.c PR) |
| macOS (M1), Apple clang 21, default `-O2` | 10 models differ | 4 differ: Apple's libm, which no flag changes |
| Windows x64, MSVC 19.44 (VS 2022), Release | 14 models differ from `/fp:precise`; against Linux `-O2`, `allclose` fails on user1, user3 and user5 | 28 of 34 identical to Linux `-O2`; the other 6 are the C runtime's maths, and user3 passes |

The patch takes `libswmm5`'s FMA instructions from 429 to 0 on aarch64 and from 460 to 0 on macOS. The option lands after the user's own flags on the compile line, so it wins over an explicit `-ffp-contract=fast`.

**Speed** (5 interleaved runs of every model, single thread, median per model, total of medians):

| | without the patch | with | ratio |
| --- | --: | --: | --: |
| aarch64 Linux, gcc `-O2` | 38.5 s | 39.1 s | 1.015 |
| macOS M1, Apple clang `-O2` | 16.2 s | 16.4 s | 1.009 |
| x86-64, gcc `-O3 -march=native` | 26.1 s | 25.7 s | 0.98 |

These are shared machines, and the per-model spread was larger than the differences, so read this as "about 1%, at most". On x86-64 without `-march`, gcc emits no FMA, and the patch changes no instruction that matters.

**Windows** was tested on GitHub's runners (Windows Server 2022, three runs on three CPUs, the same bits each time). The 6 models that still differ at `/fp:precise` are the ones where results depend on the C runtime's maths functions: they differ the same way on Linux between glibc and a correctly rounded libm. With those calls answered by CORE-MATH, a correctly rounded libm linked into `swmm5.dll`, all 34 `.out` and `.rpt` files are identical to Linux's with CORE-MATH. That's not part of this PR, but it shows nothing else in the Windows build moves the results. The workflow: https://github.com/anun333/sewage/blob/main/.github/workflows/swmm-windows.yml.

I dedicate my changes in this PR to the public domain under CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/), so they can go on to USEPA's repository unchanged; you can also take them under this repository's MIT terms. For CONTRIBUTORS: `N: anun333`, `L: Public Domain`, `D: build flags for reproducible results`.

Drafted with an AI assistant (Claude), which also ran the builds and checks reported here; I read it before posting.
