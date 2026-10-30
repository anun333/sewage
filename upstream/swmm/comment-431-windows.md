<!-- Draft, not posted. A follow-up comment on pyswmm/Stormwater-Management-Model#431, which said Windows wasn't tested. Evidence: checks/swmm/README.md "Windows (2026-10-30)", checks/swmm/digests/windows/, GitHub Actions runs 41107977753, 41108732626 and 41109294719 of anun333/sewage. -->

**Comment on #431:**

A follow-up on Windows, which the issue left untested. I ran it on GitHub's runners: `develop` at 6c81201, Visual Studio 2022 (MSVC 19.44), x64 Release as your CI builds it, and the 34 models in swmm-nrtestsuite `public/` at one thread. A Linux `gcc -O2` job in the same workflow matched my earlier Linux reference bit for bit.

| Windows build | against Linux `gcc -O2` |
| --- | --- |
| `develop` as it is (Release: `/fp:fast`) | 14 models differ; `allclose` fails on user1, user3 (226 elements) and user5 |
| with `/fp:precise` (and the gage.c change) | 6 models differ, the ones that depend on the C runtime's maths; user3 passes; `allclose` still fails on Example1, user1 and user5 |
| `/fp:precise`, with SWMM's maths calls answered by CORE-MATH (correctly rounded, linked into `swmm5.dll`) | identical, all 34 `.out` and `.rpt` files, to Linux with CORE-MATH |

So on Windows, `/fp:fast` is a cause of its own: it alone moves 14 models, and user3's failure entirely. What's left at `/fp:precise` is the C runtime's maths, as with glibc's on Linux and Apple's libm on macOS. With a correctly rounded libm, Windows, x86-64 Linux, aarch64 Linux and macOS give the same bits. Three runs on three different CPUs gave the same results each time.

The workflow and the digests are at https://github.com/anun333/sewage/tree/main/checks/swmm (section "Windows").

Drafted with an AI assistant (Claude), which also ran the builds and checks reported here; I read it before posting.
