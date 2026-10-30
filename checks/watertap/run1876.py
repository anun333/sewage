#!/usr/bin/env python3
"""run1876.py - run WaterTAP's BSM2 electroNP (no bio-P) flowsheet in fresh processes.

  python run1876.py OUT SEED...

watertap-org/watertap#1876: test_BSM2_electroNP_no_bioP failed at random on Windows
(Python 3.12 and 3.13), and is skipped since #1877. Each failure in their CI logs ends
the same way: IPOPT 3.13.2 (ma27) stops after 3000 iterations with overall NLP error
3.2791577558896899e-09 scaled and 9.9785802011532694e+07 unscaled, so the failing path
is deterministic and something discrete picks it. This runs the flowsheet's main()
once per SEED, each in a new process with PYTHONHASHSEED=SEED (a seed may repeat, to
test whether one seed always gives the same result), and writes:
  OUT/SEED-N.log      everything the run printed (IPOPT's logs included)
  OUT/runs.jsonl      one line per run: seed, outcome (ok, or the exception), seconds,
                      the closing solve's iterations, EXIT line and overall NLP error,
                      the values test_results checks, and a sha256 of every variable's
                      value (sorted by name; ok runs only)
  OUT/machine.json    platform, CPU, Python, and the versions of watertap, idaes-pse
                      and pyomo
Exit 0 when every run finished (failed solves included), 2 if a run produced no record.
"""
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time

CHILD = r'''
import hashlib, json, sys, time
t0 = time.time()
rec = {}
try:
    from pyomo.environ import value, Var
    from watertap.flowsheets.electroNP.BSM2_electroNP_no_bioP import main
    m, results = main(has_electroNP=True)
    rec["outcome"] = "ok"
    t = m.fs.electroNP.treated
    rec["values"] = {"flow_vol": value(t.flow_vol[0])}
    for c in ("S_A", "S_F", "S_I", "S_NH4", "S_PO4", "S_K", "S_Mg", "S_IC", "X_I", "X_S"):
        rec["values"][c] = value(t.conc_mass_comp[0, c])
    h = hashlib.sha256()
    for v in sorted(m.component_data_objects(Var, descend_into=True), key=lambda v: v.name):
        h.update(("%s=%r\n" % (v.name, v.value)).encode())
    rec["vars_sha256"] = h.hexdigest()
except Exception as e:
    rec["outcome"] = "%s: %s" % (type(e).__name__, str(e)[:200])
rec["seconds"] = round(time.time() - t0, 1)
print("RUN1876-RECORD " + json.dumps(rec))
'''


def closing_solve(log):
    """The last IPOPT run in the log: iterations, EXIT line, overall NLP error."""
    blocks = log.split("This is Ipopt version")
    if len(blocks) < 2:
        return {}
    b = blocks[-1]
    out = {"ipopt": b.split("\n", 1)[0].strip()}
    for key, pat in (("iterations", r"Number of Iterations\.+:\s*(\d+)"),
                     ("exit", r"EXIT:\s*(.*)"),
                     ("nlp_error", r"Overall NLP error\.+:\s*(\S+)\s+(\S+)")):
        mm = re.search(pat, b)
        if mm:
            out[key] = mm.group(1) if key != "nlp_error" else [mm.group(1), mm.group(2)]
    return out


def cpu():
    if sys.platform == "win32":
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "(Get-CimInstance Win32_Processor).Name"], capture_output=True, text=True)
        return r.stdout.strip()
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor()


def main(a):
    if len(a) < 2:
        print(__doc__)
        return 2
    out, seeds = a[0], a[1:]
    os.makedirs(out, exist_ok=True)
    vers = {}
    for mod in ("watertap", "idaes", "pyomo", "numpy", "scipy"):
        try:
            vers[mod] = __import__(mod).__version__
        except Exception as e:
            vers[mod] = "?: %s" % e
    with open(os.path.join(out, "machine.json"), "w") as f:
        json.dump({"platform": platform.platform(), "machine": platform.machine(), "cpu": cpu(),
                   "python": sys.version.split()[0], "versions": vers}, f, indent=1)
    void = False
    seen = {}
    with open(os.path.join(out, "runs.jsonl"), "w") as jf:
        for s in seeds:
            seen[s] = seen.get(s, 0) + 1
            env = dict(os.environ, PYTHONHASHSEED=str(s))
            t0 = time.time()
            r = subprocess.run([sys.executable, "-c", CHILD], env=env, capture_output=True, text=True)
            log = r.stdout + "\n--- stderr ---\n" + r.stderr
            with open(os.path.join(out, "%s-%d.log" % (s, seen[s])), "w", encoding="utf-8") as f:
                f.write(log)
            mm = re.search(r"^RUN1876-RECORD (.*)$", r.stdout, re.M)
            rec = json.loads(mm.group(1)) if mm else {"outcome": "no record (exit %d)" % r.returncode}
            void = void or not mm
            rec = dict({"seed": s, "rep": seen[s], "wall": round(time.time() - t0, 1)}, **rec)
            rec["closing_solve"] = closing_solve(r.stdout)
            jf.write(json.dumps(rec) + "\n")
            jf.flush()
            print("seed %s rep %d: %s, %s iterations, %s" % (s, seen[s], rec["outcome"][:60],
                  rec["closing_solve"].get("iterations"), rec["closing_solve"].get("exit")), flush=True)
    return 2 if void else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
