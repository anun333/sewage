# swmm: does EPA SWMM give the same bits everywhere? (ideas U1)

Run on board5 on 2026-10-27: AMD Ryzen 5 PRO 5650U (x86-64 with FMA and AVX2),
Ubuntu 24.04, glibc 2.39, gcc 13.3.0, clang 18.1.3, cmake 3.28. **CPU limit:**
every build and run used at most 4 of the 12 hardware threads, pinned with
`taskset -c 0-3`, with builds at `-j 4` and nothing running at the same time.
The scripts do the same on Linux (`SWMM_CPUS` changes the set). Reruns should
keep that limit.

Verdicts follow crnumerics: `IDENTICAL` (exit 0), `DIFFERS` (exit 1), `VOID`
(exit 2: a run failed, a file was missing, or a control did not fail).

## What was built and run

| what | where | commit |
| --- | --- | --- |
| SWMM, the active line | github.com/pyswmm/Stormwater-Management-Model, `develop` | `6c8120158957c8a5a5c9e39f435f0a31f63b5b8a` (2026-07-15) |
| SWMM, official, for comparison | github.com/USEPA/Stormwater-Management-Model, tag `v5.2.4` | `7952ca837988b1c32f791812eccc9fd64547e093` |
| test models | github.com/pyswmm/swmm-nrtestsuite, tag `v3.3.0` (the tag CI uses), directory `public/` | `e609fdbb47db410ee95a8c0353f21e4a7d890b58` (same commit as tag `v3.0.0`) |
| official benchmarks | release assets of swmm-nrtestsuite `v3.3.0`: `benchmark-linux.tar.gz` (built from SWMM `c82ba0c`), `benchmark-darwin.tar.gz` (`fe7defc`), `benchmark-win64.zip` (`19f1649`) | |
| EPANET | github.com/OpenWaterAnalytics/EPANET, `dev` | `57d8bd8ad60e89b57f2a1ac591f05c8e13589866`; models `example-networks/Net1.inp`, `Net2.inp`, `Net3.inp` |

**Models.** These are the 34 `.inp` files in [models.txt](models.txt), which are
every model in `public/` that has a test JSON: `examples/` (Example1-6),
`extran/` (extran1-10), `routing/` (test1-5), `update_v5111/` (7 files) and
`user/` (user1-5). `update_v5111/ncdc_format.inp` is left out: it has no test
JSON and stops with ERROR 156 anyway. The runs also need the data files
beside the models:
`examples/Example2.dat`, `extran/extran8b.hsf`, `update_v5111/events_example.dat`,
`update_v5111/ncdc_format_{old,new}.dat`, and the `examples/*.txt` files.
`swmmrun.py` copies every non-`.inp`, non-`.json` file in a model's directory
into its run directory. To ship the set elsewhere, tar `public/` at that commit.

Dynamic-wave models run with OpenMP only when they have at least 4 links per
thread (`project.c:277`). So at 2 threads, 23 models really split the work,
and at 4 and 8 threads 8 do (Example3, gate_control_2/3, user1-5). Each run
reads its actual thread count back from the report.

## Results

| A vs B | verdict | what differs |
| --- | --- | --- |
| gcc -O2: THREADS 1 vs 2, 4 and 8 (8 oversubscribed on 4 CPUs) | **IDENTICAL**, 34/34 | |
| gcc -O2: 4 threads x3 and 8 threads x2, repeated | **IDENTICAL** | run to run deterministic |
| gcc -O2: THREADS 0 with OMP_NUM_THREADS=4 | **IDENTICAL** | |
| clang -O2 (LLVM libomp): 1 vs 4 vs 8 threads | **IDENTICAL** | |
| gcc -O3 -march=native: 1 vs 4 threads | **IDENTICAL** | |
| gcc -O2 vs -O0, -O3, -O2 -ffp-contract=off | **IDENTICAL** | |
| gcc -O2 vs clang -O2 | **IDENTICAL** | |
| gcc -O2 vs gcc -O2/-O3 -march=native (FMA contraction) | **DIFFERS**, 9 models | user5: max abs 1.88e3 (link volume, ft3), link flow 400.6 vs 450.9 cfs (LIB_2, period 32), max rel 1.97; user1 rel 0.21; Example1 (runoff and quality, no OpenMP) rel 0.015. Fails upstream's own `allclose` on Example1, user1, user5, and its report rule on Example1, Example3, Example4, user1, user5 |
| gcc -O2 vs clang -O3 -march=native | **DIFFERS**, 9 models | as above |
| gcc -O2 vs gcc/clang -O3 -march=native -ffp-contract=off | **IDENTICAL** | FMA is the whole effect |
| gcc -O3 -march=native vs clang -O3 -march=native | **DIFFERS**, 5 models | the two compilers fuse different operations |
| one gcc -O2 binary: glibc's FMA vs non-FMA libm (`GLIBC_TUNABLES`, or qemu `-cpu Nehalem`) | **DIFFERS** on 3 of 4 | Example1: 9 values, rel 4e-6, and the report's flow-routing continuity error reads 0.103% vs 0.109%. user3: 1 value, 1 ulp. user5: 36087 values, max abs 1.73e3, rel 0.22, which fails `allclose` on 277 elements. Report rule fails on Example1 and user5. user1 unchanged |
| the same, with SWMM's 11 libm imports answered by CORE-MATH (`crlibm_shim.c`) | **IDENTICAL**, 4/4 | correct rounding removes the libm part |
| local gcc -O0 / -O2 (`6c81201`) vs official benchmark-linux (`c82ba0c`, built 2023 on GitHub's runner) | **IDENTICAL**, 33/33 | without FMA the bits match across machines and three years of commits. 33 because gate_control_2's 492 MB `.out` was left out of every benchmark comparison |
| official benchmark-linux vs benchmark-darwin | **DIFFERS**, 10 models | fails `allclose` on Example1, user1, user5. The same signature as local FMA builds, which match darwin on 26 of 33 (non-FMA builds: 23 of 33) |
| official benchmark-linux vs benchmark-win64 | **DIFFERS**, 13 models | fails `allclose` on user1, user3 (rel 1.97), user5. MSVC Release builds use `/fp:fast` (`src/solver/CMakeLists.txt:70`) |
| EPANET gcc -O2 vs repeat, clang -O2, -O3 -march=native -ffp-contract=off | **IDENTICAL** (Net1-3) | EPANET has no OpenMP |
| EPANET gcc -O2 vs -O3 -march=native | **DIFFERS** | .out: 31 of 4208, 2656 of 27059 and 2843 of 36173 float32 words; Net3 report "Final Mass" 4.70231e+06 vs 4.70230e+06 |

**Where the differences come from.** At a fixed build and machine, SWMM is
deterministic and independent of the thread count. Its OpenMP loops
(`dynwave.c:387`, `:609`) are per link and per node, with no reductions. Two
things change the bits:
- **FMA contraction**: gcc and clang with `-march=native` on x86-64, and by
  default on aarch64 and Apple silicon.
- **The C library's math**: glibc picks FMA or non-FMA `exp`/`log`/`pow`/`sin`
  by CPU at run time.

A last-bit change does not stay small. user5's `LIB_*` links oscillate,
with flows changing sign, and a 1-ulp difference grows to about 1-7% of the
largest flow in the system for the rest of the run. In user1 and Example1
the differences peak near the storm peak (about 1% of the flow), then die
out to the same bits. A changed iteration count or time step is the likely
path, but that was not traced.

**crnumerics' tools.**
- `repro-scan` rates every `libswmm5.so` **CLEAN**. As info it lists the
  causes: 574 FMAs (gcc -march=native), 1129 (clang), 425 in an aarch64
  -O2 cross build (built, not run); 11 libm call sites; 1 OpenMP region.
  `--strict` makes it FLAGGED.
- On `compile_commands.json` it flags `-march=native` and notes
  "contraction not pinned off" for every build without
  `-ffp-contract=off`. Both are right here.
- `repro-diff` (repeat, threads 1/4, ftz, cpu=Nehalem) on user1 and
  events_example: **IDENTICAL**. On Example1 and user3: **DIFFERS**, under
  `cpu` only.
- **Since then** (crnumerics
  [`beeb69d`](https://github.com/anun333/crnumerics/commit/beeb69d), 2026-10-29),
  `repro-scan` flags x86-64 calls into glibc maths that picks FMA or
  non-FMA code by CPU (`libm-cpu`), and a CLEAN verdict names the fused
  multiply-adds it found. On swmm-toolkit 0.17.0's published wheels (see
  [Published wheels](#published-wheels-2026-10-29)) it prints **FLAGGED**
  for the x86-64 wheel, for 11 such calls in `libswmm5.so`. It prints
  **CLEAN** for the aarch64 wheel, naming its 555 fused multiply-adds (552 in
  `libswmm5.so`, 3 in `libswmm-output.so`). Its
  [tools/README.md](https://github.com/anun333/crnumerics/blob/beeb69d/tools/README.md)
  has the output. The from-source builds above were not rescanned.

## Upstream's guard

- pyswmm CI (`.github/workflows/build-test.yml`) runs nrtest against a
  separate benchmark per platform, with `OMP_NUM_THREADS: 1` (line 76).
  The Linux and macOS jobs are `experimental: true`, so their failures don't
  fail the build.
- `ci-tools/linux/run-nrtests.sh:68-69` (pyswmm/ci-tools `7a17fd1`):
  `RTOL_VALUE='0.01'`, `ATOL_VALUE='1.E-6'`.
- nrtest-swmm (`pyswmm/swmm-python`, `nrtest-swmm/nrtest_swmm/__init__.py`):
  - `.out` files go through `np.testing.assert_allclose` per element and
    period.
  - `.rpt` files must match exactly after dropping the first and last 4
    lines.
  - Both comparisons `zip` the two files, so a shorter test file passes
    (read in the code, not tested).
- `ci-tools/linux/make.sh` configures with no `CMAKE_BUILD_TYPE` under Unix
  Makefiles, so its `--config Release` does nothing. Linux CI therefore tests
  an unoptimized build, where gcc never fuses.

## Commands

`$CRNUMERICS` below is a checkout of https://github.com/anun333/crnumerics (its
`core-math/` and `tools/`).

```sh
# clones, each into its own empty directory
git clone --depth 1 https://github.com/pyswmm/Stormwater-Management-Model.git src/swmm
git clone --depth 1 --branch v3.3.0 https://github.com/pyswmm/swmm-nrtestsuite.git src/suite
SUITE=$PWD/src/suite/public

# the build and thread matrix (configs.txt); 13.5 minutes on board5's 4 CPUs
sh checks/swmm/matrix.sh $PWD/src/swmm $SUITE $PWD/work          # IDENTICAL/DIFFERS per line, summary.txt

# one configuration by hand (any compiler, flags, thread count)
sh checks/swmm/build.sh $PWD/src/swmm work/builds/x cc c++ "-O2"
python3 -I checks/swmm/swmmrun.py run work/builds/x/bin/runswmm $SUITE work/runs x-t4 4 $(cat checks/swmm/models.txt)
python3 -I checks/swmm/swmmrun.py digcmp work/runs/a-t1/digests.txt work/runs/x-t4/digests.txt
python3 -I checks/swmm/swmmrun.py cmp work/runs a-t1 x-t4 --skip-missing $(cat checks/swmm/models.txt)
python3 -I checks/swmm/swmmcmp.py A.out B.out --rpt A.rpt B.rpt  # one pair, decoded
python3 -I checks/swmm/profile.py A.out B.out                    # link-flow difference over time

# glibc libm dispatch, and the CORE-MATH fix (Linux, glibc, x86-64 with FMA); 6 minutes
sh checks/swmm/libm-dispatch.sh work/builds/gcc-O2 $PWD/src/swmm $SUITE work/libm $CRNUMERICS/core-math

# crnumerics' tools on a build
$CRNUMERICS/tools/repro-scan work/builds/gcc-O2/src/solver/libswmm5.so work/builds/gcc-O2/compile_commands.json
cc -O2 -Isrc/swmm/src/solver/include -o swmmquiet checks/swmm/swmmquiet.c -Lwork/builds/gcc-O2/src/solver -lswmm5 -Wl,-rpath,$PWD/work/builds/gcc-O2/src/solver
taskset -c 0-3 $CRNUMERICS/tools/repro-diff --threads 4 --output /abs/dir/x.out -- ./swmmquiet /abs/dir/Example1.inp /abs/dir/x.rpt /abs/dir/x.out
#   (use a copy of the .inp with THREADS 0, so OMP_NUM_THREADS decides)

# the official benchmarks, each archive in its own empty directory
gh release download v3.3.0 --repo pyswmm/swmm-nrtestsuite --pattern 'benchmark-linux.tar.gz'   # and -darwin, -win64.zip

# the official per-platform benchmarks (each archive in its own directory)
python3 -I checks/swmm/benchcmp.py bench-linux/x bench-darwin/x
python3 -I checks/swmm/benchcmp.py work/runs/gcc-O2-t1 bench-linux/x

# EPANET: EPANET's .out records the input and report paths, so run each build
# in the same directory before comparing
python3 -I checks/swmm/epanetcmp.py A.out B.out
```

`digests.txt` (one per run directory; board5's are in [digests/board5/](digests/board5/))
has the sha256 of each `.out` and of each `.rpt` with its volatile lines
masked:
- the wall-clock lines;
- the pyswmm logo line, which carries the build date;
- the "Number of Threads" echo.

Digests from different machines compare with `swmmrun.py digcmp`, with no
`.out` files moved.

**Notes for other machines.**
- Pass input paths as absolute paths (`swmmrun.py` does). Given a relative
  path, `swmm_open` calls `realpath()` into a 260-byte buffer
  (`swmm5.c:1647`, `InpDir[MAXFNAME+1]`). gcc builds with `_FORTIFY_SOURCE`
  (Ubuntu's default from -O1 up) then abort with `buffer overflow detected`.
  This is already reported in USEPA PR #237 (open).
- On macOS, SWMM's CMake downloads and builds LLVM OpenMP 17.0.1
  (`cmake/openmp.cmake`), so the build needs network access.
- Without `taskset` the scripts run unpinned.
- `gate_control_2`'s `.out` is 492 MB, and the scripts delete it after
  hashing.

## Controls

- **`swmmcmp.py`** caught three planted faults:
  - one float32 in user1's `.out` with its lowest bit flipped: DIFFERS,
    located at link 41, period 0, 1 ulp;
  - one report line changed: DIFFERS;
  - a missing file: VOID.
- **`swmmrun.py digcmp`** caught three planted faults:
  - one digest changed: DIFFERS;
  - one model removed: VOID;
  - a run with no output: VOID.
- **`libm-dispatch.sh`** carries its own control. glibc's two code paths
  must differ on at least one model, or the verdict is VOID. They differed
  on 3 of 4.
- **The shim's coverage check** fails (VOID) if libswmm5 imports a libm
  function the shim lacks. An early shim without `sincos` left Example1
  differing. That coverage check was not itself tested with a planted
  fault.

## cfarm: x86-64, aarch64 and macOS (2026-10-27)

Run on the GCC Compile Farm on 2026-10-27, 18:19-18:31 UTC. Each host was limited to 4 cores (2 on cfarm104), ran under
`nice -n 19` with one job at a time, and had a run notice posted while it
worked. The question: do `-ffp-contract=off`, alone or with the CORE-MATH
shim, give board5's bits, and what does each platform's default build give?

| host | CPU | OS | compiler | C library | Python |
| --- | --- | --- | --- | --- | --- |
| board5 (reference) | AMD Ryzen 5 PRO 5650U (Zen 3, FMA) | Ubuntu 24.04 | gcc 13.3.0 | glibc 2.39 | 3.12.3 |
| cfarm421 | AMD EPYC 7773X (Zen 3, FMA) | Debian 13.7 | gcc 14.2.0 | glibc 2.41 | 3.13.5 |
| cfarm424 | Neoverse-N1 (aarch64) | Debian 13.7 | gcc 14.2.0 | glibc 2.41 | 3.13.5 |
| cfarm104 | Apple M1 | macOS 26.5.2 | Apple clang 21.0.0 (clang-2100.1.1.101), cmake 4.4.4 | libSystem | 3.9.6 |

The same sources ran everywhere: `git archive` of SWMM `6c81201` and of the
suite's `public/` at `e609fdb`. Every host ran the 34 models at 1 thread,
except cfarm104, which left out gate_control_2 (its disk is 87% full). Each
host ran three configurations:
1. The platform's default build: gcc `-O2`, or Apple clang `-O2` on macOS.
2. The same build with `-ffp-contract=off`.
3. Build (2) with SWMM's libm calls answered by CORE-MATH. Linux used
   `crlibm_shim.c` through `LD_PRELOAD`. macOS used `crlibm_shim_darwin.c`, a
   dylib with `__DATA,__interpose` entries, through `DYLD_INSERT_LIBRARIES`.

**A second board5 reference.** CORE-MATH and glibc disagree on some calls,
so (3) can't equal gcc-O2-t1 anywhere. Its reference is board5's
gcc-O2-nocontract build with the same shim:
[digests/board5/gcc-O2-nocontract-cr-t1.txt](digests/board5/gcc-O2-nocontract-cr-t1.txt).
Against gcc-O2-t1 that reference **DIFFERS** on 6 models:
- user5: max abs 1.17e3 (rel 0.13), and `allclose` fails on 164 elements;
- Example1: rel 4.9e-4;
- user3: 2 ulp;
- user4: 1 ulp;
- Example3: the `.rpt` only;
- gate_control_2: the `.out` (not decoded).

| host, configuration (FMA instructions in libswmm5) | vs board5 gcc-O2-t1 | vs board5 gcc-O2-nocontract-cr-t1 |
| --- | --- | --- |
| cfarm421 gcc -O2 (0) | **IDENTICAL**, 34/34 | |
| cfarm421 gcc -O2 -ffp-contract=off (0) | **IDENTICAL**, 34/34 | |
| cfarm421 the same + CORE-MATH | DIFFERS, the 6 above | **IDENTICAL**, 34/34 |
| cfarm424 gcc -O2 (429) | **DIFFERS**, 10 models: user5 max abs 1.88e3, rel 1.97 (`allclose` fails on 2344 elements); user1 abs 0.80, rel 0.21; Example1 abs 1.25, rel 0.015; user3 rel 1.2e-3 (abs 1.8e-12); bioretention and porous_pavement below 7e-18 on values near zero; gate_control_2 (not decoded); `.rpt` only: Example3 (times of maxima), Example4 (0.96 vs 0.97), catchment_as_outfall. `allclose` fails on Example1, user1 and user5 | |
| cfarm424 gcc -O2 -ffp-contract=off (0) | **DIFFERS**, 1 model: catchment_as_outfall's `.rpt`. **All 34 `.out` files identical** | |
| cfarm424 the same + CORE-MATH | DIFFERS, 7 models (the 6 above + catchment_as_outfall) | **DIFFERS**, 1 model: catchment_as_outfall's `.rpt`. **All 34 `.out` files identical** |
| cfarm424 a second -ffp-contract=off build at 4 threads, vs the first at 1 | **IDENTICAL**, 34/34. 8 models used 4 threads; both builds have the same `.text` bytes | |
| cfarm104 Apple clang -O2 (460) | **DIFFERS**, 10 of 33: user5 abs 1.74e3, rel 1.79 (`allclose` fails on 2342 elements); user1 abs 0.61, rel 0.13; Example1 abs 1.28, rel 0.011; user3 and events_example 1 ulp; bioretention and porous_pavement below 7e-18; `.rpt` only: Example3, Example4, catchment_as_outfall. `allclose` fails on Example1, user1 and user5 | |
| cfarm104 Apple clang -O2 -ffp-contract=off (0) | **DIFFERS**, 5 of 33. This is macOS's libm alone: user5 abs 2.12e3, rel 0.84 (`allclose` fails on 214 elements); Example1 abs 0.78, rel 0.0073 (`allclose` passes, report rule fails); user3 1 ulp; `.rpt` only: Example3, catchment_as_outfall | |
| cfarm104 the same + CORE-MATH | DIFFERS, 6 of 33 | **DIFFERS**, 1 of 33: catchment_as_outfall's `.rpt`. **All 33 `.out` files identical** |

The default FMA builds don't agree with each other either. cfarm424 gcc -O2
and cfarm104 clang -O2 differ on 6 models, and neither matches any of
board5's `-march=native` builds.

**Why catchment_as_outfall's report differs: undefined behaviour, not
rounding.** Its rain gage `1` reads the one-point series `NORAIN`. With no
interval to measure, `table_validate` leaves `dxMin` at `BIG`, which is 1e10
days (`table.c:294`, `consts.h:33`). Then `gage.c:251` evaluates
`(int)(floor(dxMin*SECperDAY + 0.5))`, which is 8.64e14 converted to `int`:
out of range, so undefined behaviour in C. The two ISAs answer differently:
- x86-64's `cvttsd2si` returns INT_MIN, so no warning;
- aarch64's `fcvtzs`, on Linux and macOS alike, saturates to INT_MAX, so
  `rainInterval < gageInterval` holds and the report gains
  `WARNING 09: time series interval greater than recording interval for Rain Gage 1`.

The `.out` is unaffected, but the line fails nrtest's report rule, and no
floating-point setting removes it.

**macOS specifics.**
- SWMM's CMake fetched LLVM OpenMP 17.0.1 and built it in each build. The
  network allowed it, so OpenMP stayed on.
- Apple clang turns a sin/cos pair into `__sincos_stret` and `pow(10, x)`
  into `__exp10(x)`. The macOS shim interposes both. Both answers are
  correctly rounded, so `cr_exp10(x)` gives the same bits as
  `cr_pow(10, x)`.
- The first attempt came back VOID: crshim.sh's import check caught
  `__exp10` missing from the shim. The rerun is the one in the table. The
  first attempt's other runs had the same digests as the rerun.
- `DYLD_*` variables are stripped when a SIP-protected binary such as
  `/usr/bin/python3` starts. So `swmmrun.py --preload` sets the variable on
  runswmm's own environment, never on the shell's.

**Controls.**
- **The canary.** `-DSHIM_CANARY` makes `pow` wrong by 2^-20. On every host
  it changed Example1 and user1, so the preload or insertion did reach
  libswmm5.
- **The import check** (`crshim.sh`) caught the real `__exp10` gap above.
- **A board5 dry run.** `cfarm-job.sh` was run on board5 first, and it
  reproduced board5's verdicts.

**DMR checks** (`python3 -I`, cfarm424 and cfarm104):
- **cfarm424** prints board5's numbers exactly:
  - `dmr_geomean.py`: limit 126 lands on the limit 1277/1277; 200 gives 103
    above and 878 below; 941 gives 8 above and 3 below; 1000 gives 32 above
    and 1436 below.
  - `dmr_rounding.py --rule half_even --trials 50000`: 5101 of 12676 ties
    round differently at n=4, and 693 of 1700 at n=30.
- **cfarm104** prints other numbers:
  - geomean: 126 gives 4 below; 200 gives 189 above and 792 below; 1000
    gives 50 above and 1418 below.
  - rounding: 5244 ties at n=4 and 768 at n=30.
- **The cause is Python, not libm.** CPython 3.12 made `sum()` of floats
  Neumaier-compensated; 3.9 adds left to right.
  `dmr_sumcheck.py` swapped the scripts' `sum` (not kept; the checks now add left to
  right themselves). The swap went both ways:
  - board5's glibc with a plain sum prints cfarm104's numbers exactly;
  - cfarm104's libm with the Neumaier sum prints board5's exactly.

  So macOS's `log` and `exp` move no count here; the Python version does.
  Every verdict is still **DIFFERS**.

**Files.**
- New scripts:
  - [cfarm-job.sh](cfarm-job.sh): one host's share, as listed above;
  - [crshim.sh](crshim.sh): builds the shim and canary for Linux or macOS,
    and checks the imports;
  - [crlibm_shim_darwin.c](crlibm_shim_darwin.c).
- Changes to existing scripts:
  - `swmmrun.py run --preload LIB`;
  - `SWMM_JOBS` in build.sh;
  - `SHIM_CANARY` in crlibm_shim.c.
- Digests: [digests/cfarm421/](digests/cfarm421/),
  [digests/cfarm424/](digests/cfarm424/) and
  [digests/cfarm104/](digests/cfarm104/), each with the host's
  `summary.txt`.
- Each host's full logs were archived privately; the digests here are what the
  verdicts rest on.

```sh
# board5: the CORE-MATH reference (board5's -ffp-contract=off build)
sh checks/swmm/crshim.sh $CRNUMERICS/core-math work/shim work/builds/gcc-O2-nocontract/src/solver/libswmm5.so
python3 -I checks/swmm/swmmrun.py run work/builds/gcc-O2-nocontract/bin/runswmm $SUITE work/runs \
    gcc-O2-nocontract-cr-t1 1 --drop-out-over 100 --preload work/shim/libcrlibm_shim.so $(cat checks/swmm/models.txt)

# each host: ~/sewage-swmm holds the bundle cfarm-job.sh's header lists
#   (src/swmm, src/suite/public, core-math/, ref/, the scripts)
NOTICE=~/bin/notice SWMM_CPUS=9-12 nice -n 19 sh cfarm-job.sh linux > results/job.log 2>&1              # cfarm421
NOTICE=~/bin/notice SWMM_CPUS=12-15 nice -n 19 sh cfarm-job.sh linux threads dmr > results/job.log 2>&1  # cfarm424
PATH=$PATH:/opt/homebrew/bin NOTICE=~/bin/notice SWMM_JOBS=2 SKIP_GC2=1 nice -n 19 sh cfarm-job.sh darwin dmr > results/job.log 2>&1  # cfarm104

# decoding: copy only the differing models' .out/.rpt home, then
python3 -I checks/swmm/swmmcmp.py board5/user5.out host/user5.out --rpt board5/user5.rpt host/user5.rpt
```

## Patches (2026-10-27)

The two draft upstream patches are in `upstream/swmm/`:
- `0001-gage`: guards the out-of-range cast at `gage.c:251`;
- `0002-build`: adds a top-level `add_compile_options(-ffp-contract=off)`
  for GNU, Clang and AppleClang, and switches MSVC Release from `/fp:fast` to
  `/fp:precise`.

They are on branch `repro-fp` (`f30b92c`), on top of `6c81201`.
[patchcheck.sh](patchcheck.sh) builds the base and the patched tree with the
same compiler and flags. It checks the patched build's digests against a
reference, then times both builds over 5 interleaved repeats at 1 thread
([timecmp.py](timecmp.py)).

**board5 (x86-64)** ran on 2026-10-27, 13:43-13:55 CDT, pinned to CPUs 0-3 with
timing on CPU 3:
- `patchcheck.sh` with gcc `-O3 -march=native` and 5 repeats;
- with clang `-O3 -march=native` and with gcc `-O2`, correctness only.

| configuration | against | verdict |
| --- | --- | --- |
| patched gcc -O3 -march=native | board5 gcc-O2-t1 | **IDENTICAL**, 34/34 (unpatched: 9 models differ) |
| patched clang -O3 -march=native | board5 gcc-O2-t1 | **IDENTICAL**, 34/34 |
| patched gcc -O2 | board5 gcc-O2-t1 | **IDENTICAL**, 34/34: the gage fix changes nothing on x86-64 |

**Timing:** [digests/board5/timing-gcc-O3-native.txt](digests/board5/timing-gcc-O3-native.txt).
- The sums of the per-model medians were 26.14 s unpatched and 25.71 s patched (ratio
  0.984). Every model's ratio lies between 0.91 and 1.05.
- The noise was large. Board5's load average rose from about 1.4 to 6.8 during the runs,
  from other work, and per-model spread was 34-60%. One unpatched repeat totalled 35.5 s
  against about 26 for the others.
- So: no cost visible at this noise, not a measured zero.

**cfarm424 and cfarm104** ran on 2026-10-27 between 18:55 and 19:04 UTC.
Each ran under `nice -n 19` with a run notice posted, on the same hosts and
software as the "cfarm" section above. Each host ran `patch-job.sh`, which
does two things:
- runs `patchcheck.sh` at the platform's default `-O2`, which contracts on
  both hosts, so the timing pits FMA against no FMA;
- runs the patched build with the CORE-MATH shim and its canary.

cfarm424 used CPUs 48-51 and timed on CPU 49. cfarm104 ran 2 build jobs,
unpinned, with gate_control_2 left out.

| host, configuration (FMA instructions in libswmm5: base → patched) | against | verdict |
| --- | --- | --- |
| cfarm424 patched gcc -O2 (429 → 0) | board5 gcc-O2-t1 | **IDENTICAL**, 34/34, `.rpt` included |
| cfarm424 the same + CORE-MATH | board5 gcc-O2-nocontract-cr-t1 | **IDENTICAL**, 34/34, `.rpt` included |
| cfarm104 patched Apple clang -O2 (460 → 0) | cfarm104 clang-O2-nocontract-t1 (its own no-FMA run, above) | **DIFFERS**, 1 of 33: catchment_as_outfall's `.rpt`, which is the gage fix |
| cfarm104 the same + CORE-MATH | board5 gcc-O2-nocontract-cr-t1 | **IDENTICAL**, 33/33, `.rpt` included |

- **The gage fix.** With the patch, catchment_as_outfall's masked `.rpt`
  on both ARM hosts is board5's x86-64 report byte for byte (digest
  `029db7ce…`). The earlier no-FMA runs on both hosts gave `8a9ff63f…`, the
  report with WARNING 09. So the `.rpt` gap in "What these do not show" is
  closed for these two hosts.
- **The build change.** In the patched tree, gage.c's compile line reads
  `-O2 … -ffp-contract=off`. The option follows `CMAKE_C_FLAGS`, so it
  overrides the target's default.
- **What is left on macOS** is libm. Without the shim, cfarm104's patched
  build still differs from board5 gcc-O2-t1 on 4 of 33 models: Example1,
  Example3 (`.rpt` only), user3 and user5. These are the earlier
  `-ffp-contract=off` differences minus catchment_as_outfall.
- **Sanity.**
  - The base builds reproduced the earlier phase's default-build digests
    exactly: 34/34 on cfarm424 and 33/33 on cfarm104.
  - All 5 timing repeats of each build gave identical digests, and the
    patched repeats equal the check run.
  - cfarm424's patched digests equal board5's
    [patched-gcc-O2-t1.txt](digests/board5/patched-gcc-O2-t1.txt).
  - On both hosts the canary changed Example1 and user1.

**Timing.** The table shows the median of 5 interleaved repeats in seconds
for models whose base median is at least 0.2 s. Totals cover every model
(34 on cfarm424, 33 on cfarm104).

| model | cfarm424 base | patched | ratio | cfarm104 base | patched | ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Example3 | 0.87 | 0.88 | 1.011 | 0.40 | 0.40 | 1.000 |
| events_example | 1.37 | 1.41 | 1.029 | 0.65 | 0.66 | 1.015 |
| gate_control_2 | 7.08 | 7.19 | 1.016 | | | |
| gate_control_3 | 1.90 | 1.91 | 1.005 | 0.75 | 0.76 | 1.013 |
| user1 | 0.39 | 0.43 | 1.103 | 0.21 | 0.22 | 1.048 |
| user2 | 2.19 | 2.23 | 1.018 | 1.05 | 1.06 | 1.010 |
| user3 | 6.28 | 6.34 | 1.010 | 2.99 | 3.02 | 1.010 |
| user4 | 4.28 | 4.32 | 1.009 | 2.24 | 2.26 | 1.009 |
| user5 | 13.40 | 13.57 | 1.013 | 7.52 | 7.58 | 1.008 |
| **total of medians** | 38.53 | 39.09 | **1.015** | 16.20 | 16.35 | **1.009** |

- **Spread**, as (max-min)/median per model:
  - cfarm424: 1-11% (user4's base 11%, user1 about 10%, gate_control_2's
    base 9%). Each repeat's total, patched over base (paired): 1.016, 1.015,
    1.016, 1.019 and 0.974. The last pair came from one slow base pass
    (40.0 s against 38.5-38.7 s).
  - cfarm104: 0-28% (gate_control_3's base 28%, the rest at most 9%). Each
    repeat's total ratio: 1.034, 1.028, 0.994, 1.009 and 1.037.
  - user1's 1.10 and 1.05 are within its own spread. The long models agree
    on 1-1.5% (cfarm424) and about 1% (cfarm104).
- **Load.**
  - cfarm424: load average 31.6 before and 34.3 after. Another user's GCC
    testsuite at nice 10 kept every CPU about 45% busy, so no CPU was idle,
    and the nice-19 runs pinned to CPU 49 shared it. CPU 49 was 44% busy in
    the 10 s before the job and 29% after.
  - cfarm104: load average 5.5 before and 4.6 after, on 8 cores, from
    another user's three single-threaded processes.
  - macOS can't pin, so runs could land on the M1's performance or
    efficiency cores. The interleaving keeps that fair between the builds,
    but not quiet.
- **Files.**
  - Digests: [digests/cfarm424/](digests/cfarm424/) and
    [digests/cfarm104/](digests/cfarm104/), in `patched-*.txt` (check, shim,
    canary and the job summary) and `timing-*.txt` (both tables).
  - Logs and per-repeat `meta.json` were archived privately.
  - [patch-job.sh](patch-job.sh) is one host's share of the patch check.

```sh
# each host: ~/sewage-swmm-patch holds src/base (git archive 6c81201), src/patched (git archive f30b92c),
#   src/suite/public (e609fdb), core-math/, ref/patchcheck-ref.txt, ref/cr-ref.txt and the scripts
NOTICE=~/bin/notice NCORES=4 SWMM_CPUS=48-51 SWMM_TIME_CPU=49 SWMM_JOBS=4 nice -n 19 sh patch-job.sh linux > results/job.log 2>&1  # cfarm424
PATH=$PATH:/opt/homebrew/bin NOTICE=~/bin/notice NCORES=2 SWMM_JOBS=2 nice -n 19 sh patch-job.sh darwin > results/job.log 2>&1  # cfarm104, models.txt without gate_control_2
```

## Published wheels (2026-10-29)

Everything above built SWMM from source. pyswmm users don't: `pip install pyswmm`
brings in swmm-toolkit's prebuilt wheel. swmm-toolkit 0.17.0 (PyPI, 2026-02-26)
ships the fork's SWMM at `ebbce382`, 10 commits before `6c81201`. Its wheels are
built natively by cibuildwheel on `ubuntu-24.04`, `ubuntu-24.04-arm`,
`windows-2025`, `macos-15-intel` and `macos-15` (`.github/workflows/build_wheel.yml`), and nothing
in swmm-toolkit's CMake or `pyproject.toml` turns contraction off.

[wheeljob.sh](wheeljob.sh) installs a wheel from PyPI into a venv, records its
sha256, counts the FMA instructions in the libraries it ships, and runs the 34
models at one thread through the wheel's own solver (`swmm.toolkit.solver.swmm_run`).
board5 ran it with the x86-64 wheel, under the same 4-CPU lock as everything else.
cfarm424 ran it with the aarch64 wheel on 2026-10-29, 11:53-11:54Z, nice 19, one
process, with a run notice. As a reference, board5 also built `ebbce382` from
source with gcc `-O2 -ffp-contract=off`.

| | x86-64 wheel | aarch64 wheel |
| --- | --- | --- |
| wheel sha256 | `28737dd5...` | `f0d5026a...` |
| FMA instructions in `libswmm5.so` | 0 | 552 |
| against `ebbce382` from source, `-ffp-contract=off` | **IDENTICAL**, all 34 (`.out` and `.rpt`) | 10 models differ |

The aarch64 wheel against the x86-64 one:
- **`.out` differs on 7 models**; 3 fail nrtest-swmm's `allclose` (rtol 0.01,
  atol 1e-6):
  - **user5:** 2,344 elements. LIB_2's flow at period 32 is 400.57 cfs on x86-64
    and 450.88 on aarch64, the same pair the from-source builds gave. Link 647
    holds 22,226 against 24,101 ft³ at period 176.
  - **user1:** 17 elements; node 05yD77's depth at period 88 is 1.011 against
    0.981 ft.
  - **Example1:** 3 elements; link 15's flow at period 5 is 3.526 against 3.502.
  - bioretention, porous_pavement and user3 differ within the tolerance (the
    first two only in values below 1e-17).
  - gate_control_2 differs too; its 492 MB `.out` was deleted after hashing, so
    it wasn't decoded.
- **`.rpt` differs on 6 models**, which fail nrtest's exact report comparison:
  Example1, Example3, Example4, catchment_as_outfall (the `gage.c` warning),
  user1 and user5.

So a pyswmm user's results on user5 depend on whether they run on x86-64 or on
ARM Linux, by 50 cfs (13%) in that flow, with nothing to tell them. The x86-64 wheel gives
the answer of a build without contraction. The aarch64 wheel gives the answer this
README measured for aarch64's default build.

**The fix reaches the wheels.** swmm-toolkit builds the solver with
`add_subdirectory(swmm-solver)`, which reads the solver's top-level
`CMakeLists.txt`. So `0002-build`'s top-level `add_compile_options` would apply to
the wheel builds once swmm-toolkit updates its submodule. That is read from the
CMake files and was not built. On aarch64, `-ffp-contract=off` gave x86-64's
`.out` bits for `6c81201` ([Patches](#patches-2026-10-27)); the same build of
`ebbce382` was not run.

- **Not run:** the macOS wheels (cfarm104 didn't answer ssh or ping on
  2026-10-29), the Windows wheel, and the musllinux wheels (a different C library's
  maths).
- **Files.**
  - Digests and each wheel's record are in [digests/wheels/](digests/wheels/).
  - cfarm424's log was archived privately.

```sh
# WORK/src/suite/public is swmm-nrtestsuite public/ at e609fdb
nice -n 19 sh wheeljob.sh WORK 0.17.0       # writes WORK/runs/wheel-0.17.0-PLATFORM/{digests.txt,wheel.txt}
python3 -I swmmrun.py digcmp digests/wheels/board5-wheel-0.17.0-x86_64.txt digests/wheels/cfarm424-wheel-0.17.0-aarch64.txt
# decoding: both runs' folders under one RUNS directory, then
python3 -I swmmrun.py cmp RUNS wheel-0.17.0-manylinux2014_x86_64 wheel-0.17.0-manylinux2014_aarch64 --skip-missing MODEL...
```

## crpreload in place of the shim (2026-10-30)

`crlibm_shim.c` answers the 11 libm functions SWMM calls. crmvec's crpreload
([github.com/anun333/crmvec](https://github.com/anun333/crmvec), since 0.9.0 on x86-64
and 0.11.0 on aarch64) answers CORE-MATH's 76 under their C library names, and is
maintained and checked against CORE-MATH on its own. Both return correctly rounded
results, and a correctly rounded result is unique, so SWMM must give the same bits with
either. [crpreload-job.sh](crpreload-job.sh) checks that with crmvec v0.12.2:
- it builds crpreload and SWMM `6c81201` twice (`-O2 -ffp-contract=off`; patched `-O2`);
- every libm function `libswmm5` imports (`acos asin atan cos exp log log10 pow sin
  sincos tan`) is one crpreload exports, and `LD_DEBUG=bindings` shows Example1's eight
  bound to `libcrpreload.so`;
- it compares every run with board5's shim reference,
  [gcc-O2-nocontract-cr-t1](digests/board5/gcc-O2-nocontract-cr-t1.txt).

| host | no preload (the control) | + crpreload | patched + crpreload |
| --- | --- | --- | --- |
| cfarm421 (x86-64) | DIFFERS, the 6 models glibc and CORE-MATH disagree on | **IDENTICAL**, 34/34 | **IDENTICAL**, 34/34 |
| cfarm424 (aarch64) | DIFFERS, those 6 + catchment_as_outfall's `.rpt` | DIFFERS, catchment_as_outfall's `.rpt` only (the `gage.c` cast); all 34 `.out` identical | **IDENTICAL**, 34/34 |

This is the shim's own result, with every run predicted before it ran. So on Linux,
crpreload can stand in for the shim: `--preload libcrpreload.so` in place of
`crshim.sh`'s library. macOS still needs the darwin shim until crpreload's macOS port
has run on a Mac (cfarm104 was unreachable). The shim stays for that, and as the
reference. Digests:
[digests/cfarm421/](digests/cfarm421/) and [digests/cfarm424/](digests/cfarm424/),
`crp-*.txt`.

```sh
# a work folder holding src/base, src/patched (git archive), src/suite/public, crmvec/ (v0.12.2),
# ref/cr-ref.txt (= digests/board5/gcc-O2-nocontract-cr-t1.txt), build.sh swmmrun.py swmmcmp.py models.txt transect/
NOTICE=true NCORES=4 SWMM_CPUS=0-3 nice -n 19 sh crpreload-job.sh
```

## What these do not show

- **Windows.** MSVC was not run. The `/fp:fast` explanation for win64's
  differences is a hypothesis, and code changes between the benchmarks'
  commits are mixed in with platform effects.
- **CORE-MATH on Windows.** It made glibc on x86-64 and aarch64 and macOS's
  libm agree in every `.out` (cfarm). MSVC's CRT was not tried.
- **The report on aarch64.** The catchment_as_outfall warning above differs
  on aarch64 whatever the floating-point settings. Only a source change
  (clamping `gageInterval`) would make `.rpt` files match across ISAs.
- **Other ARM cores and compilers.** One Neoverse-N1 with gcc 14 and one M1
  with Apple clang 21 were run. Linux clang on aarch64 and gcc on macOS were
  not.
- **The mechanism that amplifies a 1-ulp change.** Iteration counts and time
  steps were not traced.
