# wntr: does WNTR give the same results on x86-64 and aarch64 Linux?

WNTR (github.com/USEPA/WNTR) is EPA's and Sandia's Python package for water
distribution networks. It has two simulators. `EpanetSimulator` runs EPANET 2.2
through a shared library that WNTR bundles. `WNTRSimulator` is WNTR's own
hydraulic solver: Newton's method in Python, with residuals and Jacobian from a
small compiled extension and the linear solves in scipy. This check installs
WNTR 1.5.0 the way `pip install wntr` does on each platform, runs nine networks
through both simulators, and compares the results bit for bit and against
nrtest's tolerance.

Run on 2026-10-29 on board5 (x86-64) and on cfarm424 (aarch64), 14:45-15:42 UTC on
cfarm424. **CPU limits:** board5 used at most 4 of its 12 hardware threads, pinned
with `taskset -c 0-3` and serialised with a lock, as in [../swmm/](../swmm/README.md).
cfarm424 used 2 of its 64 cores (`taskset`), all at `nice -n 19`, with a run
notice posted while it worked. The solvers ran on one thread
(`OMP_NUM_THREADS=1` and the like).

Verdicts follow crnumerics: `IDENTICAL` (exit 0), `DIFFERS` (exit 1), `VOID`
(exit 2: a run failed, a file was missing, or nothing was compared).

## The short version

- **On aarch64 Linux, `pip install wntr` gives a WNTR whose `EpanetSimulator`
  cannot run.** PyPI has no aarch64 Linux wheel, so pip builds the sdist. That
  build compiles only WNTR's two small C++ extensions. EPANET comes as prebuilt
  binaries for x86-64 Linux, x86-64 and arm64 macOS and x86-64 Windows, and WNTR
  loads the x86-64 Linux one on every Linux. The install succeeds without a
  warning. The first EPANET run fails with `OSError: ...linux-x64/libepanet22.so:
  cannot open shared object file: No such file or directory`, although the file
  is there: it is an x86-64 library. So there is no EPANET result to compare
  across the two ISAs.
- **`WNTRSimulator` is not reproducible on one machine.** Its compiled evaluator
  keeps variables and constraints in `std::set`s of pointers, so the order of the
  Jacobian's rows and columns follows heap addresses. Address-space randomisation
  and Python's string-hash seed change that order in every process, and with it
  the rounding in scipy's sparse LU solve. Two runs of the same install on the
  same machine gave different bits on all 8 networks that `WNTRSimulator` solves.
  On seven of them the differences are at most 3e-8 relative and pass nrtest's
  `allclose` (rtol 0.01, atol 1e-6). On Net6, a 96-hour network with pumps,
  valves and tanks, they switch pumps and valves at different times and move
  pressures by metres: `allclose` fails between two runs on one x86-64 machine.
- **Between x86-64 and aarch64, `WNTRSimulator`'s differences are the same size
  as within each machine.** Five default runs were made on each.
  - On the seven small networks, every pair differs (x86-64 with x86-64, aarch64
    with aarch64, and across), by at most 3e-8 relative, and every pair passes
    `allclose`.
  - On Net6, `allclose` fails in 10 of 10 pairs within x86-64, 10 of 10 within
    aarch64 and 24 of 25 across.
  - The largest difference across, JUNCTION-3322's pressure at 82 hours, is
    229.79 m on one x86-64 run against 209.28 m on all five aarch64 runs. It is
    also the largest within x86-64, where the other four runs gave 209.28-209.29 m.
- **FMA plays no part in WNTR's own code.** Every library in the x86-64 wheel has
  0 FMA instructions, and so do the two extensions pip compiles on aarch64 at
  gcc's default contraction. The evaluator is a stack machine that applies one
  operation at a time, so the compiler has no `a*b + c` to fuse. A build with
  `-ffp-contract=off` (and `-O2`) produced the same machine code as the default
  aarch64 build, byte for byte, so it cannot bring aarch64's results to
  x86-64's. Its run fell inside the same spread.

## What `pip install wntr` gets

WNTR 1.5.0 went to PyPI on 2026-07-01 (tag `1.5.0`, commit `388958845c`). It
has wheels for CPython 3.10 to 3.13 on `manylinux2014_x86_64`,
`macosx_14_0_arm64`, `macosx_15_0_x86_64` and `win_amd64`, plus an sdist
(`wntr-1.5.0.tar.gz`, sha256 `244c53bedc11ac24...`). The wheels are built by
cibuildwheel on GitHub's `ubuntu-latest`, `windows-latest`, `macos-15-intel` and
`macos-latest` runners (`.github/workflows/build_test_wheels.yml`). There is no
ARM Linux runner, the repair step is skipped, and the Linux wheels are renamed
`linux` to `manylinux2014`. conda-forge's `wntr` 1.5.0 exists for linux-64,
osx-64 and win-64 only.

**The sdist build.** `setup.py` declares two C++ extensions and nothing else to
compile:
- `wntr.sim.aml._evaluator` (`evaluator.cpp` and its SWIG wrapper), which
  evaluates `WNTRSimulator`'s residuals and Jacobian;
- `wntr.sim.network_isolation._network_isolation`.

Both have `extra_compile_args=[]`, so they get Python's own flags. On both
hosts that was `-fno-strict-overflow -Wsign-compare -DNDEBUG -g -O2 -Wall
-fPIC`, with gcc 14.2.0 (Debian) on cfarm424 and gcc 13.3.0 (Ubuntu) on board5.
pip's isolated build used numpy 2.5.4 and setuptools 84.2.1. The sdist
contains no EPANET source.

**EPANET.** It ships prebuilt, in the sdist and in every wheel:
`wntr/epanet/libepanet/{linux-x64,darwin-x64,darwin-arm,windows-x64}/`
(`MANIFEST.in`). `wntr/epanet/toolkit.py:22-30` chooses
`windows-x64/epanet22.dll` on Windows, `darwin-arm/libepanet2.dylib` or
`darwin-x64/libepanet22.dylib` on macOS, and `linux-x64/libepanet22.so`
on anything else, aarch64 Linux included. The library is EPANET 2.2.0
(`ENgetversion` returns 20200), built with GCC 7.4.0 on Ubuntu 18.04 according
to its `.comment` section. The file has been at that path, unchanged, since
WNTR PR #462 (2025-01-10).

| file (under `wntr/`) | x86-64 wheel (cp312) | aarch64, sdist built by pip (cp313) |
| --- | --- | --- |
| `epanet/libepanet/linux-x64/libepanet22.so` (what `EpanetSimulator` loads) | `3a49fa2eb1aecdf4`, x86-64, GCC 7.4.0, **0 FMA** | the same file. It is x86-64 and fails to load |
| `epanet/libepanet/linux-x64/libepanet20.so` (EPANET 2.0, `version=2.0`) | `f33bafb7b01f09f9`, GCC 4.4.7, 0 FMA | the same file |
| `epanet/libepanet/linux-x64/libepanet2.so`, `libepanetmsx.so` (EPANET-MSX) | `7dcd417ed3898cf6`, `9518e2c9d98f567c`, GCC 13.3.0, 0 FMA | the same files |
| `sim/aml/_evaluator.*.so` | `76a6dc6e131be69c`, GCC 14.2.1 (manylinux_2_28), **0 FMA** | `74d8fd642b391a15`, gcc 14.2.0, **0 FMA** |
| `sim/network_isolation/_network_isolation.*.so` | `cd8a97b8d0164c52`, GCC 14.2.1, 0 FMA | `308727ef95e82a33`, gcc 14.2.0, 0 FMA |

sha256 prefixes. FMA instructions were counted with the `objdump` and `awk`
from [../swmm/wheeljob.sh](../swmm/wheeljob.sh); the x86-64 libraries were
counted on board5, since cfarm424's `objdump` does not disassemble x86-64. The
x86-64 wheel's sha256 is `2e941cd1641da48a...`. The x86-64 Linux wheel also
carries the macOS and Windows binaries.

WNTRSimulator's linear solves are in scipy's SuperLU, and that is where the order
of its equations enters the arithmetic (below). It has 0 FMA instructions on
x86-64 (`_superlu.cpython-312-x86_64-linux-gnu.so`) and 0 on aarch64
(`_superlu.cpython-313-aarch64-linux-gnu.so`). The OpenBLAS libraries in the
numpy and scipy wheels have many: 55,388 and 60,053 on x86-64, in
runtime-dispatched kernels, and 663,048 and 720,736 on aarch64
([digests/cfarm424/scipy-fma.txt](digests/cfarm424/scipy-fma.txt)). Whether
SuperLU's calls reach those kernels was not traced.

## What was run

| network | from | elements (nodes + links) | steps | quality |
| --- | --- | --- | --- | --- |
| `wntr/Net1` | WNTR `examples/networks/` at tag 1.5.0 | 11 + 13 | 25 (24 h) | chlorine |
| `wntr/Net2` | " | 36 + 40 | 56 (55 h) | chlorine |
| `wntr/Net3` | " | 97 + 119 | 169 (168 h) | trace |
| `wntr/Net6` | " | 3356 + 3892 | 97 (96 h) | chemical |
| `wntr/ky4` | " | 964 + 1158 | 1 (steady state) | trace |
| `wntr/ky10` | " | 935 + 1061 | 1 (steady state) | age |
| `epanet/Net1`, `Net2`, `Net3` | EPANET `example-networks/` at `57d8bd8` (`dev`) | the same elements as WNTR's copies, which WNTR re-saved (Net3 there runs 168 h, not 24 h) | 25, 56, 25 | chlorine, chlorine, trace |

[networks.txt](networks.txt) lists each file with its git blob hash, and
`wntrrun.py` refuses a file whose hash differs. Every network ran through:
- **`EpanetSimulator`**, hydraulics plus the network's water quality, with a
  relative `file_prefix` so that EPANET's binary `.bin` is kept and records no
  absolute path;
- **`WNTRSimulator`**, hydraulics only. It has no water quality.

**Digests.** `digests.txt` has one line per item:
- the sha256 of the `.inp` WNTR writes for EPANET, without its `; Filename:` and
  `; Created:` lines;
- the sha256 of the `.bin`;
- the sha256 of each result table's float64 bytes. Rows are the time index,
  columns are the element names sorted, and the time index and names are hashed
  separately. EPANET's float32 values are widened to float64, which is exact.

The tables are, for nodes, demand, head, pressure, quality and (WNTR) leak
demand; for links, flowrate, velocity, status, setting and, from EPANET,
headloss, friction factor, reaction rate and quality.

**Dependencies** were pinned to what `pip install wntr==1.5.0` resolved on
board5 that day ([constraints.txt](constraints.txt): numpy 2.5.4, scipy 1.18.1,
pandas 3.1.0, networkx 3.7), on both hosts. The Pythons differ: 3.12.3 on board5
(Ubuntu 24.04, glibc 2.39, AMD Ryzen 5 PRO 5650U) and 3.13.5 on cfarm424 (Debian
13, glibc 2.41, Neoverse-N1).

**Run conditions.**
- **Default runs** use `python -I`. String hashing and address-space layout
  are then random in each process, as they are for a user.
- **Fixed-layout runs** (`WNTR_LAYOUT=fixed`) use a cleared environment,
  `PYTHONHASHSEED=0` and `setarch -R` (no address randomisation).

Each run's header records which one applied. The first runs on each host
(board5's `wheel-1.5.0-x86_64`, `-rep2` and `sdist-1.5.0-x86_64`; cfarm424's
`sdist-1.5.0-aarch64`, `-rep2` and `-nocontract`) were made before the header
had that field. They are default runs.

## Results: `EpanetSimulator`

| | verdict |
| --- | --- |
| board5, 12 runs of all nine networks (wheel and x86-64 sdist build; default and fixed layout) | **IDENTICAL**: the same `.inp`, `.bin` and tables in every run |
| cfarm424, every run | **VOID**: every network raises `OSError` at `ENepanet()`, after WNTR writes the `.inp` and before EPANET runs |
| x86-64 against aarch64 | **VOID**: nothing to compare |

The aarch64 error, from `wntr/epanet/toolkit.py:118`:

```
OSError: VENV/lib/python3.13/site-packages/wntr/epanet/libepanet/linux-x64/libepanet22.so:
cannot open shared object file: No such file or directory
```

The file exists (the install record lists it, ELF machine `Advanced Micro
Devices X86-64`). glibc's loader reports a library for another ISA this way.
`wntr.epanet.toolkit` imports without error, so the failure comes only when a
simulation starts.

## Results: `WNTRSimulator` on one machine

**Rechecked separately** on board5 the same day, with the x86-64 wheel and a
five-line script that hashes the pressure and flow tables:
- three runs of Net3, `PYTHONHASHSEED` 1, 2 and 3, gave three different results,
  differing by up to 4e-14 relative;
- three runs of Net6 run side by side on single CPUs: run 1 differs from runs 2
  and 3 by 0.84 m of pressure (40.60 against 39.76 m at hour 96), which fails
  `allclose`, while runs 2 and 3 agree to 1e-13.

The code citations below were also read at the 1.5.0 tag.

**Why it varies.** `wntr/sim/aml/evaluator.hpp:161-165` keeps the model in
`std::set<Var*>`, `std::set<Constraint*>` and three more sets of pointers.
`Evaluator::set_structure()` (`evaluator.cpp:412-446`) numbers variables and
constraints by walking those sets, so the Jacobian's columns and rows come out
in the order of the objects' addresses. Within a constraint, the Jacobian
entries come from a `std::map<Var*, ...>` in the same order. The Newton step
is `scipy.sparse.linalg.spsolve(J, r, permc_spec="COLAMD")`
(`wntr/sim/solvers.py:178`), and COLAMD's ordering, and so the rounding of the
LU factors, depends on the order it is given. The rest of the Newton step
doesn't depend on order. The residuals are evaluated one constraint at a time,
the update is elementwise, and the convergence test is `max(abs(r))`. The
Python side keeps its own collections in insertion order (`OrderedSet`).

The order was read back from the evaluator for ky4 (2,117 variables):

| process | order of the 2,117 variables |
| --- | --- |
| `python -I`, three processes | three different orders |
| `PYTHONHASHSEED=0` and `setarch -R`, two processes | the same order |

And the results follow it:
- **Default runs (`python -I`): five runs of the x86-64 wheel gave five
  different results on all 8 networks that `WNTRSimulator` solves.** ky10
  returns no time steps, so its tables are empty and trivially equal.
- **Fixed layout:** two identical command lines gave **IDENTICAL** results,
  all nine networks and both simulators (board5, the wheel's `fixed1` run
  repeated with the same paths). But fixed layout fixes the order only for
  that exact process. With wntr/Net1 alone, two runs whose run names differed
  in one character (`tagA1`, `tagA2`, the same length) gave different bits.
  So did the wheel's `fixed1` and `fixed2` runs, on all 8 networks. With ky4
  alone and ASLR off, `PYTHONHASHSEED` 0 and 1 gave different bits. With seed 0
  and ASLR on, two processes gave two results.

**How large.** Five default runs of the x86-64 wheel against each other (10
pairs). The largest relative difference over all of a network's variables:

| network | largest relative difference | `allclose` (rtol 0.01, atol 1e-6) |
| --- | --- | --- |
| wntr/Net1, epanet/Net1 | 9.2e-13 | passes |
| wntr/Net2, epanet/Net2 | 1.5e-10 | passes |
| wntr/Net3, epanet/Net3 | 7.7e-10 | passes |
| wntr/ky4 | 1.7e-8 | passes |
| **wntr/Net6** | 2 (a flow that reverses) | **fails in all 10 pairs**, on up to 2,282 pressure values at 1,142 nodes |

Head and pressure differ by at most 1.1e-13 m on the seven small networks. The
large relative differences are in flows near zero: ky4's P-144 carries
1.08e-6 m³/s.

**Net6.** Net6 runs 96 hours, with pumps, valves and tanks under controls. A
rounding difference moves a tank level or a pressure across a control
threshold at a different step. The pump then switches at another time, and
the rest of the run follows a different path. Some values, from runs on both
hosts (`wntrcmp.py probe`):

| run | JUNCTION-1100 pressure, 24 h (m) | PUMP-3863, 24 h | VALVE-3890, 25 h | JUNCTION-3322 pressure, 82 h (m) | LINK-3453 flow, 72 h (m³/s) |
| --- | --- | --- | --- | --- | --- |
| x86-64 wheel, run 1 | **8.655** | closed | closed | 209.29 | **+0.193** |
| x86-64 wheel, run 2 | 1.019 | open | active | 209.28 | -0.0119 |
| x86-64 wheel, run 3 | **8.655** | closed | closed | **229.79** | **+0.191** |
| x86-64 wheel, run 4 | 1.019 | open | active | 209.28 | -0.0119 |
| x86-64 wheel, run 5 | 1.019 | open | closed | 209.29 | +0.0102 |
| x86-64 sdist build, runs 1-3 | 1.019 | open | active | 209.27-209.28 | -0.190, -0.0119, -0.0172 |
| aarch64 sdist build, 5 default and 2 fixed-layout runs | 1.019 | open | active | 209.28 | -0.0119 in all seven |
| aarch64, the `-O0` build | 1.019 | open | active | 209.27 | +0.0498 |
| aarch64, the `-O2 -ffp-contract=off` build (fixed layout) | 1.019 | open | active | 209.24 | +0.123 |

All 26 runs are in [digests/probe-net6.txt](digests/probe-net6.txt), with
10 significant digits. One outcome came up most often: the pump open at 24 h,
JUNCTION-3322 at 209.2824654 m and LINK-3453 at -0.01192717572 m³/s, equal to 10
digits at these points, though the bits differ elsewhere. All seven runs of the
default aarch64 build gave it, and so did 6 of the 17 x86-64 runs (11 full
runs and 6 runs of Net6 alone). The aarch64 control build, with the same
machine code, did not. So this is not a property of aarch64's code, and five or
seven runs cannot say whether aarch64 lands on it more often.

The largest difference between two of the five default wheel runs is
JUNCTION-3322's pressure at 82 hours: **209.28-209.29 m in four runs, 229.79 m
in the fifth** (rep3), 20.5 m apart. A self-built x86-64 sdist install (gcc 13.3, no
FMA) behaves the same way. Its three runs against the wheel's five fall
inside the same spread, network by network
([digests/board5-spread-wheel-vs-sdist.txt](digests/board5-spread-wheel-vs-sdist.txt)).

## Results: x86-64 against aarch64

Five default runs of the x86-64 wheel on board5 (A) were compared with five
default runs of pip's aarch64 build on cfarm424 (B): every pair within A, every
pair within B, and all 25 pairs across. `wntrcmp.py spread`, full output in
[digests/spread-x86-64-wheel-vs-aarch64-sdist.txt](digests/spread-x86-64-wheel-vs-aarch64-sdist.txt).
The table gives the largest relative difference over each network's variables,
and how many pairs fail `allclose` (rtol 0.01, atol 1e-6) on any variable.

| network | within x86-64 (10 pairs) | within aarch64 (10 pairs) | x86-64 against aarch64 (25 pairs) |
| --- | --- | --- | --- |
| wntr/Net1 | 7.9e-13 | 9.3e-13 | 8.7e-13 |
| epanet/Net1 | 9.2e-13 | 9.2e-13 | 1.1e-12 |
| wntr/Net2 | 1.3e-10 | 1.6e-10 | 1.6e-10 |
| epanet/Net2 | 1.5e-10 | 1.8e-10 | 2.3e-10 |
| wntr/Net3 | 7.7e-10 | 7.2e-10 | 8.0e-10 |
| epanet/Net3 | 2.4e-11 | 3.3e-11 | 3.3e-11 |
| wntr/ky4 | 1.7e-8 | 2.6e-8 | 2.6e-8 |
| **wntr/Net6** | 2; **10 of 10 fail** | 2; **10 of 10 fail** | 2; **24 of 25 fail** |
| wntr/ky10 | no results | no results | no results |

Every pair differed in its bits on every network but ky10, and on all but
Net6 every pair passes `allclose`. On Net6:
- **Pressure** fails `allclose` in 10 of 10 pairs within x86-64 (up to 2,282
  values at 1,142 nodes), 7 of 10 within aarch64 (up to 57 values at 37 nodes)
  and 21 of 25 across (up to 2,282 values at 1,142 nodes). The largest
  differences, within x86-64 and across alike, are JUNCTION-3322 at 82 h (20.5 m,
  above) and JUNCTION-1100 at 24 h (8.655 against 1.019 m, 7.64 m). There
  PUMP-3863 is closed in two of the five x86-64 runs and open in all five
  aarch64 runs. Within aarch64 the largest was 0.85 m.
- **Head** passes `allclose` within aarch64 and fails in 9 of 10 pairs within
  x86-64 and in 15 of 25 across.
- **Link status** differs on up to 32 values (10 links) within x86-64, 2 values
  (1 pump) within aarch64, and 32 across.

So the worst x86-64-against-aarch64 values are x86-64 runs that differ just as
much from other x86-64 runs. In five runs each, aarch64's spread on Net6 was
smaller. But the control build, with the same machine code, landed elsewhere
(the table above). Nothing here separates an ISA effect from the
run-to-run one.

**At fixed layout,** each host's runs repeat only for the same command line
(above). Across hosts the command lines can't be the same: the venv paths,
the Python versions and the extension modules all differ. So a fixed-layout
run on one host has no bitwise counterpart on the other. The fixed-layout
digests are kept anyway (`*-fixed*.txt`).

## The `-ffp-contract=off` control

`EpanetSimulator` has no aarch64 build, so the control could only apply to
WNTR's own extensions, which pip compiles there.
- **The first attempt was not a control.** With `CFLAGS` and `CXXFLAGS` both
  set to `-ffp-contract=off`, the compile lines became `aarch64-linux-gnu-g++
  -ffp-contract=off -fPIC ...`. Setting them replaced Python's flags for the
  C++ files instead of adding to them, so that build had no `-O2`. Its `_evaluator` `.text` is 180,884 bytes against the
  default's 80,888. Its one run is in [digests/cfarm424/](digests/cfarm424/)
  as `sdist-1.5.0-aarch64-nocontract` (an `-O0` build).
- **The control.** `CFLAGS` and `CXXFLAGS` set to Python's flags plus
  `-ffp-contract=off` (`-fno-strict-overflow -Wsign-compare -DNDEBUG -g -O2
  -Wall -ffp-contract=off`). The `.text` sections of both extensions are
  **byte for byte the same as the default build's**: `_evaluator`
  `23c8adc0dfb7dccc` (80,888 bytes), `_network_isolation` `5ae245023aea5ea7`
  (13,392 bytes). The files differ only because `-g` records the flags.

So `-ffp-contract=off` changes nothing in what WNTR compiles on aarch64. There
is nothing in it to contract, and it cannot bring aarch64's results to x86-64's.
What keeps them apart is the equation order, which changes from run to run on
either ISA.

## Run times

| | board5 (4 CPUs) | cfarm424 (1 core per process, nice 19, host load 35-48) |
| --- | --- | --- |
| install: x86-64 wheel / sdist build | 19 s / 30 s | - / 38-67 s |
| one run of the nine networks, both simulators (sum of the per-network times) | 144-170 s | 294-720 s, slower as the host's load rose |
| of which `WNTRSimulator` on Net6 | 119-165 s | 266-637 s |
| of which `EpanetSimulator`, all nine | 3.4-4.0 s | (fails at once) |
| whole job | about 55 min of builds and runs, under the lock | 14:45:58-15:41:53 UTC, two phases |

## Controls

- **`controls.sh`** plants six faults in a copy of a finished run, and
  `wntrcmp.py` caught all 6, before and after the last changes to `wntrcmp.py`
  ([digests/controls.txt](digests/controls.txt)):
  1. two copies of one run compare `IDENTICAL` (`cmp` and `digcmp`);
  2. the lowest bit of one float64 flipped (Net3, `WNTRSimulator`, pressure):
     `DIFFERS`, located at node 103, t=3600 s, 1 ulp;
  3. one character of one digest changed: `DIFFERS`;
  4. one value file deleted: `VOID`;
  5. one digest line deleted: `VOID`;
  6. a simulator that raised: `VOID`.
- **`wntrrun.py`** refuses a network whose git blob hash is not the one in
  `networks.txt`, and a network list with no networks (`VOID`). That second
  check was added after a run with an empty list exited 0.
- **The FMA count** prints `n/a`, not 0, when `objdump` sees no instructions,
  which happens with a library for another ISA.
- **EpanetSimulator's determinism** is its own control for the method: its
  digests (`.inp`, `.bin` and all tables) matched in every board5 run, default
  and fixed layout, wheel and sdist build alike.

## Files

- `digests/board5/` and `digests/cfarm424/` hold each run's `digests.txt`, one
  file per run named by its tag, plus each build's install record
  (`*-install.txt`) and the per-network times (`times.txt`). cfarm424 also has:
  - `text-hashes.txt`, the `.text` hashes of the three aarch64 builds;
  - `scipy-fma.txt`;
  - `wheel-1.5.0-aarch64-fetch.txt`, the wheel route's "no wheel" answer;
  - `rc.txt`, the job's exit codes and times.
- `digests/board5-net6-only/` holds the six board5 runs of Net6 alone:
  `PYTHONHASHSEED` 0, 1 and 2 at fixed layout (`wheel-s*`), two default runs
  (`wheel-r*`), and the x86-64 sdist build at seed 0.
- The text outputs behind the tables are the `spread-*.txt`,
  `board5-spread-*.txt`, `probe-net6.txt`, `board5-fixed1-repeated.txt` and
  `controls.txt` files.
- The float64 value files are not committed (about 26 MB per run). So `cmp`,
  `spread` and `probe` need the runs themselves, while `digcmp` works from the
  digests here. Rerunning gives other bits, which is the finding.
- cfarm424's logs were archived privately.

## Commands

```sh
# WORK/nets holds wntr/*.inp and epanet/*.inp as networks.txt lists them
# (WNTR examples/networks at 1.5.0, EPANET example-networks at 57d8bd8)
sh wntrjob.sh WORK wheel wheel-1.5.0-x86_64 5          # x86-64: install the wheel, 5 default runs
WNTR_LAYOUT=fixed sh wntrjob.sh WORK wheel wheel-1.5.0-x86_64 2   # reuses the venv: 2 fixed-layout runs
nice -n 19 sh wntrjob.sh WORK sdist sdist-1.5.0-aarch64 5   # aarch64: what pip does there
F="-fno-strict-overflow -Wsign-compare -DNDEBUG -g -O2 -Wall -ffp-contract=off"
CFLAGS="$F" CXXFLAGS="$F" WNTR_LAYOUT=fixed sh wntrjob.sh WORK sdist sdist-1.5.0-aarch64-nocontract-O2 1

python3 -I wntrcmp.py digcmp A/digests.txt B/digests.txt [--sim wntr]
python3 -I wntrcmp.py cmp RUNS/A RUNS/B --sim wntr
python3 -I wntrcmp.py spread RUNS/A1 RUNS/A2 ... -- RUNS/B1 RUNS/B2 ... --sim wntr
sh controls.sh RUNS/A SCRATCH
```

`wntrjob.sh` downloads WNTR with [fetch.py](fetch.py), which picks the file from
PyPI's JSON API and checks its sha256. pip is not used for this, because `pip
download` of an sdist runs its `setup.py` to read the metadata.

After the runs, `wntrjob.sh` was changed only in how it names things. pip's
temporary folder is now `WORK/piptmp` (it was `WORK/tmp`), and paths into pip's
build environment are written as `BUILDENV`. The committed install records were
edited to match.

## What this does not show

- **macOS on Apple silicon.** That wheel loads `darwin-arm/libepanet2.dylib`,
  another EPANET build from x86-64 Linux's `libepanet22.so`, and it is the one ARM
  platform where WNTR's `EpanetSimulator` works. It was not run: cfarm104, the
  macOS arm64 host, did not answer on 2026-10-29. Windows and the macOS x86-64
  wheel were not run either.
- **EPANET on aarch64 Linux under any other route.** A user could build EPANET
  2.2 and put it where WNTR looks. Nothing in WNTR's documentation says to, and
  that build was not tried here. EPANET's own FMA effect, between source builds,
  is in [../swmm/](../swmm/README.md#results).
- **An ISA effect inside `WNTRSimulator`.** The equation order changes in every
  process, and the x86-64 and aarch64 runs differ by no more than that. A smaller
  difference due to the ISA, from scipy's or OpenBLAS's builds or from glibc's
  maths, would be hidden under it. Fixing the order would take a change to
  WNTR's evaluator, which this check does not make.
- **Same-Python runs.** board5 ran Python 3.12.3 and cfarm424 3.13.5, with
  different glibc versions (2.39 and 2.41). The dependencies were pinned to the
  same versions.
- **Other networks and options.** Nine example networks, WNTR's default solver
  settings and demand model (DDA) only. No pressure-dependent demand, leaks,
  MSX, or `version=2.0`.
- **Why ky10 fails in `WNTRSimulator`.** It stops at t=0 after 2,999 Newton
  iterations and returns empty tables with `error_code` 0
  (`ResultsStatus.error`), with only a warning. EPANET solves it. Its
  "identical" verdicts compare empty tables.
