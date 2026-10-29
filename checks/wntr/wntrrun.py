#!/usr/bin/env python3
"""wntrrun.py - run water networks through WNTR's two simulators and digest the results.

  python -I wntrrun.py run NETS RUNS TAG NETLIST
  python -I wntrrun.py libcheck

Runs with the Python of a venv that has wntr installed (wntrjob.sh makes one).

run: NETLIST is networks.txt, one "PATH BLOB" per line; PATH is under NETS and
BLOB is the file's git blob sha1, which is checked before anything runs (a
mismatch is VOID). Each network runs twice, each run in its own directory
RUNS/TAG/<net>/<sim>/:
  epanet  wntr.sim.EpanetSimulator: EPANET 2.2 through the library WNTR bundles,
          hydraulics plus water quality when the .inp sets one. file_prefix is
          relative to the run directory, so the .bin records only relative names.
  wntr    wntr.sim.WNTRSimulator: WNTR's own hydraulic solver (no quality).
Every result DataFrame (node: demand, head, pressure, quality, ...; link:
flowrate, velocity, ...) is written as little-endian float64 bytes, rows = the
time index, columns = element names sorted, to <kind>.<var>.f64, with the times
and names in index.json. EPANET's results are float32 in the .bin; widening to
float64 is exact.
Writes RUNS/TAG/digests.txt, one line per item: NET SIM ITEM SHA256 SHAPE, where
ITEM is
  inp          WNTR's written .inp without its "; Filename:" and "; Created:" lines
  bin          EPANET's binary output
  index        index.json (times and sorted names)
  error_code   the results object's error_code (as text, not hashed)
  node.VAR / link.VAR   the float64 bytes above
A simulator that raises gets one line, ITEM "error", digest "-", and its
message in meta.json. Run times go to RUNS/TAG/times.txt.

libcheck: prints which EPANET library WNTR's toolkit loads, and EPANET's version
from ENgetversion, or the error the load raised.

Exit 0 when every run finished, 2 otherwise (crnumerics' VOID).
"""
import ctypes
import hashlib
import json
import os
import platform
import sys
import time

sys.dont_write_bytecode = True


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def git_blob_sha1(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def masked_inp(path):
    with open(path, "rb") as f:
        lines = f.read().splitlines(keepends=True)
    return b"".join(x for x in lines if not x.startswith((b"; Filename:", b"; Created:")))


def read_netlist(path):
    rows = []
    with open(path) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                p, blob = line.split()[:2]
                rows.append((p, blob))
    return rows


def frames(results):
    """(kind, var, DataFrame) for every result table, in a fixed order."""
    out = []
    for kind in ("node", "link"):
        tables = getattr(results, kind)
        for var in sorted(tables):
            out.append((kind, var, tables[var]))
    return out


def dump(results, d, emit):
    import numpy as np
    index = {"times": None, "node": None, "link": None}
    for kind, var, df in frames(results):
        cols = sorted(str(c) for c in df.columns)
        df = df.copy()
        df.columns = [str(c) for c in df.columns]
        df = df[cols]
        times = [float(t) for t in df.index.to_numpy(dtype=np.float64)]
        if index["times"] is None:
            index["times"] = times
        elif index["times"] != times:
            raise ValueError("%s.%s has a different time index" % (kind, var))
        if index[kind] is None:
            index[kind] = cols
        elif index[kind] != cols:
            raise ValueError("%s.%s has different element names" % (kind, var))
        a = np.ascontiguousarray(df.to_numpy(dtype=np.float64)).astype("<f8", copy=False)
        b = a.tobytes()
        with open(os.path.join(d, "%s.%s.f64" % (kind, var)), "wb") as f:
            f.write(b)
        emit("%s.%s" % (kind, var), sha256_bytes(b), "%dx%d" % a.shape)
    ib = json.dumps(index, sort_keys=True, separators=(",", ":")).encode()
    with open(os.path.join(d, "index.json"), "wb") as f:
        f.write(ib)
    emit("index", sha256_bytes(ib), "%dx%d+%d" % (len(index["times"] or []), len(index["node"] or []),
                                                    len(index["link"] or [])))
    emit("error_code", str(getattr(results, "error_code", None)).replace(" ", "_"), "-")


def run(nets, runs, tag, netlist):
    import wntr
    rows = read_netlist(netlist)
    tagdir = os.path.abspath(os.path.join(runs, tag))
    os.makedirs(tagdir, exist_ok=True)
    lines, times, meta_rows = [], [], []
    void = not rows
    if void:
        print("VOID: %s lists no networks" % netlist)
    for rel, blob in rows:
        src = os.path.abspath(os.path.join(nets, rel))
        net = rel[:-4] if rel.endswith(".inp") else rel
        with open(src, "rb") as f:
            got = git_blob_sha1(f.read())
        if got != blob:
            print("%-14s VOID: git blob %s, networks.txt says %s" % (net, got, blob))
            lines.append("%s - error - blob-mismatch" % net)
            void = True
            continue
        for sim in ("epanet", "wntr"):
            d = os.path.join(tagdir, net.replace("/", "-"), sim)
            os.makedirs(d, exist_ok=True)
            for x in os.listdir(d):
                os.remove(os.path.join(d, x))

            def emit(item, digest, shape, _net=net, _sim=sim):
                lines.append("%s %s %s %s %s" % (_net, _sim, item, digest, shape))

            prefix = os.path.basename(net)
            cwd = os.getcwd()
            t0 = time.time()
            err = wn = None
            try:
                os.chdir(d)
                wn = wntr.network.WaterNetworkModel(src)
                if sim == "epanet":
                    res = wntr.sim.EpanetSimulator(wn).run_sim(file_prefix=prefix)
                else:
                    res = wntr.sim.WNTRSimulator(wn).run_sim()
                secs = time.time() - t0
                if sim == "epanet":
                    emit("inp", sha256_bytes(masked_inp(prefix + ".inp")), "-")
                    with open(prefix + ".bin", "rb") as f:
                        emit("bin", sha256_bytes(f.read()), "-")
                dump(res, d, emit)
            except Exception as e:  # recorded, not fatal: one simulator may not load on a platform
                secs = time.time() - t0
                err = "%s: %s" % (type(e).__name__, str(e).replace(sys.prefix, "VENV"))
                emit("error", "-", type(e).__name__)
                void = True
            finally:
                os.chdir(cwd)
            quality = None
            try:
                quality = wn.options.quality.parameter
            except Exception:
                pass
            times.append("%s %s %.3f" % (net, sim, secs))
            meta_rows.append({"net": net, "sim": sim, "secs": round(secs, 3), "error": err,
                              "quality": quality})
            print("%-14s %-6s %8.2fs %s" % (net, sim, secs, "ok" if err is None else err[:160]),
                  flush=True)
    vers = {}
    for m in ("wntr", "numpy", "scipy", "pandas", "networkx"):
        try:
            vers[m] = __import__(m).__version__
        except Exception:
            vers[m] = None
    layout = layout_state()
    head = "# tag=%s machine=%s python=%s %s %s\n# net sim item sha256 shape\n" % (
        tag, platform.machine(), platform.python_version(),
        " ".join("%s=%s" % kv for kv in sorted(vers.items())), layout)
    with open(os.path.join(tagdir, "digests.txt"), "w") as f:
        f.write(head + "\n".join(lines) + "\n")
    with open(os.path.join(tagdir, "times.txt"), "w") as f:
        f.write("# net sim seconds (wall clock, model load included)\n" + "\n".join(times) + "\n")
    with open(os.path.join(tagdir, "meta.json"), "w") as f:
        json.dump({"tag": tag, "machine": platform.machine(), "system": platform.platform(),
                   "python": platform.python_version(), "versions": vers, "layout": layout,
                   "rows": meta_rows}, f, indent=1)
    return 2 if void else 0


def layout_state():
    """What decides heap layout, which WNTRSimulator's results depend on (see README):
    string hash randomisation and address-space randomisation (ADDR_NO_RANDOMIZE)."""
    seed = os.environ.get("PYTHONHASHSEED") if not sys.flags.ignore_environment else None
    hs = "random" if sys.flags.hash_randomization and not seed else "fixed(%s)" % seed
    aslr = "?"
    try:
        with open("/proc/self/personality") as f:
            aslr = "off" if int(f.read(), 16) & 0x0040000 else "on"
    except (OSError, ValueError):
        pass
    return "hashseed=%s aslr=%s" % (hs, aslr)


def libcheck():
    try:
        from wntr.epanet import toolkit
        print("epanet library %s" % toolkit.libepanet)
        e = toolkit.ENepanet()
        v = ctypes.c_int()
        e.ENlib.ENgetversion(ctypes.byref(v))
        print("epanet ENgetversion %d" % v.value)
        return 0
    except Exception as e:
        print("epanet load failed: %s: %s" % (type(e).__name__, str(e).replace(sys.prefix, "VENV")))
        return 2


def main(a):
    if a[:1] == ["run"] and len(a) == 5:
        return run(*a[1:])
    if a == ["libcheck"]:
        return libcheck()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
