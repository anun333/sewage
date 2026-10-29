<!-- DRAFT for USEPA/WNTR (bug-report template). Not posted; reviewed before posting. -->

**Title:** Linux aarch64: `pip install wntr` succeeds, but EpanetSimulator fails because the x86-64 libepanet22.so is loaded on every Linux

**Summary**

On aarch64 Linux (ARM servers, Raspberry Pi, AWS Graviton and the like), WNTR 1.5.0 installs without a warning, but `EpanetSimulator` can't run.

- **The install.** PyPI has wheels for manylinux x86_64, macOS arm64 and x86_64, and win_amd64 only, so on aarch64 Linux pip builds the sdist. That build compiles WNTR's two C++ extensions (`wntr.sim.aml._evaluator` and `_network_isolation`) and nothing else; EPANET comes only as the bundled prebuilt libraries. conda-forge has no aarch64 Linux build either.
- **The failure.** `wntr/epanet/toolkit.py` (lines 22-30 at 1.5.0) picks `libepanet/linux-x64/libepanet22.so` for every platform that is not Windows or macOS. On aarch64 that is the wrong architecture, and the first EPANET run fails:

  ```
  OSError: .../site-packages/wntr/epanet/libepanet/linux-x64/libepanet22.so: cannot open shared object file: No such file or directory
  ```

  The file is there; it just isn't loadable on this CPU, so the message is misleading.
- **Not the same as #471 and #474,** though the message is the same: there, the 1.3.0 wheels had no EPANET binaries at all.
- **`WNTRSimulator` works on aarch64** (see below).

**Expected behaviour:** either `EpanetSimulator` works on aarch64 Linux, or the user is told it isn't supported. Some options:
- check `platform.machine()` in `toolkit.py` and raise a clear error naming the platform when no matching library exists;
- build EPANET from source in the sdist on platforms without a bundled library;
- ship a `linux-aarch64` library, or an aarch64 manylinux wheel.

**Example**

On any aarch64 Linux machine:

```sh
python3 -m venv v && v/bin/pip install wntr==1.5.0      # builds the sdist, succeeds
v/bin/python - <<'PY'
import wntr
wn = wntr.network.WaterNetworkModel("Net3.inp")   # examples/networks/Net3.inp
wntr.sim.EpanetSimulator(wn).run_sim()            # OSError: ...linux-x64/libepanet22.so: cannot open shared object file
PY
```

**Environment**
 - Operating system: Debian 13, aarch64 (Arm Neoverse-N1), gcc 14.2
 - Python version: 3.13.5
 - WNTR version: 1.5.0, built from the sdist by pip

**Additional context**

- On the same machine, `WNTRSimulator` ran the example networks, except ky10, which doesn't converge on x86-64 either.
- The x86-64 wheel works as expected on x86-64 Linux.
- I didn't test the macOS arm64 wheel, which ships `darwin-arm/libepanet2.dylib`.
- The full record (install logs, the libraries' checksums, the runs) is at https://github.com/anun333/sewage/tree/main/checks/wntr.

Drafted with an AI assistant (Claude), which also ran the builds and checks reported here; I read it before posting.
