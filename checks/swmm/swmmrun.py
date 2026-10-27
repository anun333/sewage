#!/usr/bin/env python3
"""swmmrun.py - run SWMM models under one configuration; compare runs.

  python3 -I swmmrun.py run RUNSWMM SUITE RUNS TAG THREADS [--omp N]
                            [--drop-out-over MB] [--preload LIB] MODEL...
  python3 -I swmmrun.py cmp RUNS TAG_A TAG_B [--skip-missing] MODEL...
  python3 -I swmmrun.py digcmp DIGESTS_A DIGESTS_B

run: copies each MODEL (a path relative to SUITE, e.g. user/user4.inp) and
the data files beside it into RUNS/TAG/<model>/, sets THREADS in [OPTIONS]
(THREADS "-" leaves the file alone) and runs RUNSWMM there, with
OMP_NUM_THREADS = --omp (default: THREADS). On Linux each run is pinned with
`taskset -c $SWMM_CPUS` (default 0-3: the limit used on board5 was 4 of its 12
hardware threads); without taskset (macOS) it runs unpinned. The input is
passed by absolute path: given a relative path, swmm_open calls realpath()
into a 260-byte buffer, which _FORTIFY_SOURCE builds abort on. The thread
count SWMM actually used is read back from the report.
Writes RUNS/TAG/digests.txt: one line per model with the sha256 of the .out
and of the masked .rpt (see swmmcmp.MASK), so runs on different machines can
be compared without moving the .out files. --drop-out-over deletes any .out
larger than MB megabytes after digesting it (gate_control_2's is 492 MB).
--preload LIB loads LIB into each SWMM run only (LD_PRELOAD on Linux,
DYLD_INSERT_LIBRARIES on macOS), e.g. the CORE-MATH shim (crshim.sh). It is
set on the child's environment because macOS strips DYLD_* variables when it
starts a system binary such as /usr/bin/python3.

cmp: swmmcmp on each model's .out and .rpt (decoded differences);
--skip-missing passes over models whose .out was dropped.
digcmp: compares two digests.txt files model by model.

Each prints a verdict line: IDENTICAL (exit 0), DIFFERS (exit 1),
VOID (exit 2: a run failed, a file is missing, or nothing was compared).
Python 3 standard library only.
"""
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True  # no __pycache__ beside the scripts
sys.path.insert(0, HERE)
import swmmcmp  # noqa: E402

THREADS_RE = re.compile(r"^(\s*THREADS\s+)\S+", re.I | re.M)


def set_threads(text, n):
    if THREADS_RE.search(text):
        return THREADS_RE.sub(lambda m: m.group(1) + str(n), text, count=1)
    return re.sub(r"(?im)^(\[OPTIONS\][^\n]*\n)", r"\g<1>THREADS              %d\n" % n,
                  text, count=1)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(runswmm, suite, runs, tag, threads, omp, drop_mb, models, preload=None):
    runswmm = os.path.abspath(runswmm)
    rows = []
    pin = []
    if shutil.which("taskset"):
        pin = ["taskset", "-c", os.environ.get("SWMM_CPUS", "0-3")]
    tagdir = os.path.join(runs, tag)
    os.makedirs(tagdir, exist_ok=True)
    for m in models:
        src = os.path.join(suite, m)
        name = os.path.splitext(os.path.basename(m))[0]
        d = os.path.abspath(os.path.join(tagdir, name))
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        for f in os.listdir(os.path.dirname(src)):
            p = os.path.join(os.path.dirname(src), f)
            if os.path.isfile(p) and not f.endswith((".inp", ".json")):
                shutil.copy(p, d)
        with open(src, encoding="latin-1") as f:
            text = f.read()
        if threads is not None:
            text = set_threads(text, threads)
        inp = os.path.join(d, name + ".inp")
        rpt = os.path.join(d, name + ".rpt")
        out = os.path.join(d, name + ".out")
        with open(inp, "w", encoding="latin-1") as f:
            f.write(text)
        env = dict(os.environ)
        if omp is not None:
            env["OMP_NUM_THREADS"] = str(omp)
        if preload:
            env["DYLD_INSERT_LIBRARIES" if sys.platform == "darwin" else "LD_PRELOAD"] = preload
        t0 = time.time()
        # cwd = run dir: LID report files named in the .inp are opened
        # relative to the working directory, as nrtest runs them.
        r = subprocess.run(pin + [runswmm, inp, rpt, out], env=env, cwd=d,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        dt = time.time() - t0
        used, h_out, h_rpt = None, "-", "-"
        if os.path.exists(rpt):
            with open(rpt, encoding="latin-1") as f:
                mm = re.search(r"Number of Threads \.+ (\d+)", f.read())
                used = int(mm.group(1)) if mm else None
            h_rpt = hashlib.sha256(swmmcmp.masked_rpt_bytes(rpt)).hexdigest()
        if os.path.exists(out):
            h_out = sha256_file(out)
            if drop_mb is not None and os.path.getsize(out) > drop_mb * 1e6:
                os.remove(out)
        ok = r.returncode == 0 and h_out != "-"
        rows.append({"model": m, "exit": r.returncode, "secs": round(dt, 2),
                     "threads_used": used, "sha256_out": h_out, "sha256_rpt": h_rpt})
        print("%-38s exit=%d %7.2fs threads_used=%s%s" % (
            m, r.returncode, dt, used, "" if ok else "  (no .out)"), flush=True)
    meta = {"runswmm": runswmm, "threads": threads, "omp": omp, "pin": pin, "preload": preload,
            "machine": platform.machine(), "system": platform.platform(), "rows": rows}
    with open(os.path.join(tagdir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    with open(os.path.join(tagdir, "digests.txt"), "w") as f:
        f.write("# tag=%s threads=%s omp=%s machine=%s system=%s%s\n" % (
            tag, threads, omp, platform.machine(), platform.platform(),
            " preload=%s" % os.path.basename(preload) if preload else ""))
        f.write("# model sha256(.out) sha256(masked .rpt) threads_used\n")
        for r in rows:
            f.write("%s %s %s %s\n" % (r["model"], r["sha256_out"], r["sha256_rpt"],
                                       r["threads_used"]))
    return 0 if all(r["exit"] == 0 and r["sha256_out"] != "-" for r in rows) else 2


def cmp(runs, ta, tb, models, skip_missing=False):
    summary = []
    void = False
    for m in models:
        name = os.path.splitext(os.path.basename(m))[0]
        a = os.path.join(runs, ta, name, name)
        b = os.path.join(runs, tb, name, name)
        if skip_missing and not (os.path.exists(a + ".out") and os.path.exists(b + ".out")):
            print("%-38s not decoded (.out dropped after digesting; see digcmp)" % m)
            continue
        try:
            o = swmmcmp.compare_out(a + ".out", b + ".out")
            r = swmmcmp.compare_rpt(a + ".rpt", b + ".rpt")
        except Exception as e:  # missing or unreadable output
            print("%-38s VOID (%s)" % (m, e))
            void = True
            continue
        same = o["bytes_identical"] and r["identical_masked"]
        if same:
            line = "IDENTICAL"
        else:
            line = "DIFFERS out:%s" % ("same" if o["bytes_identical"] else
                                       "%s/%s vals, max_abs=%.3g max_rel=%.3g max_ulp=%s nrtest=%s" % (
                                           o.get("values_differ"), o.get("values_total"),
                                           o.get("max_abs", 0), o.get("max_rel", 0), o.get("max_ulp"),
                                           "PASS" if o.get("nrtest_allclose_pass") else
                                           "FAIL(%s)" % o.get("nrtest_failing_elements")))
            line += " rpt:%s" % ("same" if r["identical_masked"] else
                                 "%d lines, nrtest=%s" % (r["differing_lines"],
                                                          "PASS" if r["nrtest_report_pass"] else "FAIL"))
        print("%-38s %s" % (m, line))
        summary.append({"model": m, "same": same, "out": o, "rpt": r})
    with open(os.path.join(runs, "cmp_%s__%s.json" % (ta, tb)), "w") as f:
        json.dump(summary, f, default=str, indent=1)
    if void or not summary:
        print("VOID")
        return 2
    ok = all(s["same"] for s in summary)
    print("IDENTICAL" if ok else "DIFFERS")
    return 0 if ok else 1


def read_digests(path):
    d = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            model, h_out, h_rpt = line.split()[:3]
            d[model] = (h_out, h_rpt)
    return d


def digcmp(pa, pb):
    try:
        a, b = read_digests(pa), read_digests(pb)
    except (OSError, ValueError) as e:
        print("error: %s" % e)
        print("VOID")
        return 2
    common = sorted(set(a) & set(b))
    void = not common or set(a) != set(b)
    differ = 0
    for m in common:
        if "-" in a[m] + b[m]:
            void = True
            print("%-38s VOID (a run produced no output)" % m)
            continue
        so, sr = a[m][0] == b[m][0], a[m][1] == b[m][1]
        if so and sr:
            print("%-38s IDENTICAL" % m)
        else:
            differ += 1
            print("%-38s DIFFERS (%s)" % (m, ", ".join(
                x for x, s in ((".out", so), (".rpt", sr)) if not s)))
    for m in sorted(set(a) ^ set(b)):
        print("%-38s VOID (in one file only)" % m)
    if void:
        print("VOID")
        return 2
    print("DIFFERS" if differ else "IDENTICAL")
    return 1 if differ else 0


def main(a):
    if a[:1] == ["run"]:
        omp = drop = preload = None
        if "--preload" in a:
            k = a.index("--preload"); preload = os.path.abspath(a[k + 1]); a = a[:k] + a[k + 2:]
        if "--omp" in a:
            k = a.index("--omp"); omp = int(a[k + 1]); a = a[:k] + a[k + 2:]
        if "--drop-out-over" in a:
            k = a.index("--drop-out-over"); drop = float(a[k + 1]); a = a[:k] + a[k + 2:]
        runswmm, suite, runs, tag, threads = a[1:6]
        threads = None if threads == "-" else int(threads)
        if omp is None and threads is not None:
            omp = threads
        return run(runswmm, suite, runs, tag, threads, omp, drop, a[6:], preload)
    if a[:1] == ["cmp"] and len(a) >= 5:
        skip = "--skip-missing" in a
        a = [x for x in a if x != "--skip-missing"]
        return cmp(a[1], a[2], a[3], a[4:], skip)
    if a[:1] == ["digcmp"] and len(a) == 3:
        return digcmp(a[1], a[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
