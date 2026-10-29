#!/usr/bin/env python3
"""wntrcmp.py - compare wntrrun.py outputs from two runs, e.g. two machines.

  python3 -I wntrcmp.py digcmp DIGESTS_A DIGESTS_B [--sim epanet|wntr]
  python3 -I wntrcmp.py cmp RUN_A RUN_B [--sim epanet|wntr] [--rtol R] [--atol A]
  python3 -I wntrcmp.py spread RUN_A1 [RUN_A2...] -- RUN_B1 [RUN_B2...] [--sim S]
  python3 -I wntrcmp.py probe NET SIM VAR:ELEMENT:SECONDS... -- RUN...

digcmp: compares two digests.txt files network by network and simulator by
simulator (every item: inp, bin, index, error_code, node.*, link.*). A network
or simulator that is in one file only, or that raised on either side, is VOID.

cmp: decodes the float64 files of two run directories (RUNS/TAG). For each
variable that differs it prints how many values differ, the largest absolute
and relative difference (|a - b| / max(|a|, |b|)) with the element, time and
both values, the largest distance in ulps, and the allclose test that
EPANET's and SWMM's nrtest regression suites use, with B as the reference:
|a - b| <= atol + rtol * |b|, rtol 0.01 and atol 1e-6 by default (applied here
to WNTR's SI values).

spread: for repeat runs of two configurations (e.g. the same install run several
times on each machine), prints for each variable that is not the same in all
runs: how many distinct results each group has, and the largest differences
and allclose failures within group A (every pair), within group B, and across
(every A run against every B run). DIFFERS if any variable is not the same in
all runs.

probe: prints one value per run for each VAR:ELEMENT:SECONDS given, e.g.
node.pressure:JUNCTION-1100:86400 (no verdict; exit 2 if a value is missing).

--sim limits each command to one simulator. Each prints a verdict line:
IDENTICAL (exit 0), DIFFERS (exit 1), VOID (exit 2: a file is missing, a
simulator failed, or nothing was compared). Python 3 standard library only.
"""
import json
import os
import struct
import sys

sys.dont_write_bytecode = True


def read_digests(path):
    d = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            net, sim, item, digest = line.split()[:4]
            d.setdefault((net, sim), {})[item] = digest
    return d


def digcmp(pa, pb, sim=None):
    try:
        a, b = read_digests(pa), read_digests(pb)
    except (OSError, ValueError) as e:
        print("error: %s" % e)
        print("VOID")
        return 2
    keys = sorted(k for k in set(a) | set(b) if sim is None or k[1] == sim)
    void = not keys
    differ = 0
    for k in keys:
        name = "%s %s" % k
        if k not in a or k not in b:
            print("%-22s VOID (in one file only)" % name)
            void = True
            continue
        fa = [s for s, x in (("A", a[k]), ("B", b[k])) if "error" in x]
        if fa:
            print("%-22s VOID (raised on %s)" % (name, " and ".join(fa)))
            void = True
            continue
        items = sorted(set(a[k]) | set(b[k]))
        bad = [i for i in items if a[k].get(i) != b[k].get(i)]
        missing = [i for i in items if i not in a[k] or i not in b[k]]
        if missing:
            print("%-22s VOID (items in one file only: %s)" % (name, ", ".join(missing)))
            void = True
        elif bad:
            differ += 1
            print("%-22s DIFFERS (%s)" % (name, ", ".join(bad)))
        else:
            print("%-22s IDENTICAL (%d items)" % (name, len(items)))
    if void:
        print("VOID")
        return 2
    print("DIFFERS" if differ else "IDENTICAL")
    return 1 if differ else 0


def read_f64(path):
    with open(path, "rb") as f:
        b = f.read()
    if len(b) % 8:
        raise ValueError("%s: %d bytes is not a whole number of float64" % (path, len(b)))
    return b


def unpack(b):
    n = len(b) // 8
    return struct.unpack("<%dd" % n, b), struct.unpack("<%dQ" % n, b)


def ordered(u):
    """float64 bits -> an integer that orders like the float (for ulp distance)."""
    return u if u < (1 << 63) else (1 << 63) - u


def cmp_var(pa, pb, times, names, rtol, atol):
    ba, bb = read_f64(pa), read_f64(pb)
    if len(ba) != len(bb) or len(ba) != 8 * len(times) * len(names):
        raise ValueError("shapes differ: %d, %d values for %dx%d" % (
            len(ba) // 8, len(bb) // 8, len(times), len(names)))
    r = {"n": len(ba) // 8, "differ": 0, "max_abs": 0.0, "max_rel": 0.0, "max_ulp": 0,
         "at_abs": None, "at_rel": None, "fail": 0, "fail_elems": set(), "worst_fail": None}
    if ba == bb:
        return r
    (fa, ua), (fb, ub) = unpack(ba), unpack(bb)
    worst = -1.0
    m = len(names)
    for i in range(len(fa)):
        if ua[i] == ub[i]:
            continue
        r["differ"] += 1
        x, y = fa[i], fb[i]
        where = (names[i % m], times[i // m], x, y)
        d = abs(x - y)
        if d != d:  # a NaN on one side
            d = float("inf")
        den = max(abs(x), abs(y))
        rel = d / den if den else 0.0
        if d > r["max_abs"] or r["at_abs"] is None:
            r["max_abs"], r["at_abs"] = d, where
        if rel > r["max_rel"] or r["at_rel"] is None:
            r["max_rel"], r["at_rel"] = rel, where
        r["max_ulp"] = max(r["max_ulp"], abs(ordered(ua[i]) - ordered(ub[i])))
        lim = atol + rtol * abs(y)
        if not d <= lim:
            r["fail"] += 1
            r["fail_elems"].add(names[i % m])
            excess = d / lim if lim else float("inf")
            if excess > worst:
                worst, r["worst_fail"] = excess, where
    return r


def fmt_where(w):
    return "%s t=%gs (%.10g vs %.10g)" % w


def cmp(ra, rb, sim=None, rtol=0.01, atol=1e-6):
    try:
        da = read_digests(os.path.join(ra, "digests.txt"))
        db = read_digests(os.path.join(rb, "digests.txt"))
    except (OSError, ValueError) as e:
        print("error: %s" % e)
        print("VOID")
        return 2
    keys = sorted(k for k in set(da) | set(db) if sim is None or k[1] == sim)
    void = not keys
    differ = 0
    out = []
    for k in keys:
        net, s = k
        name = "%s %s" % k
        if k not in da or k not in db or "error" in da[k] or "error" in db[k]:
            print("%-22s VOID (no results on one side)" % name)
            void = True
            continue
        d_a = os.path.join(ra, net.replace("/", "-"), s)
        d_b = os.path.join(rb, net.replace("/", "-"), s)
        try:
            with open(os.path.join(d_a, "index.json")) as f:
                ia = json.load(f)
            with open(os.path.join(d_b, "index.json")) as f:
                ib = json.load(f)
        except (OSError, ValueError) as e:
            print("%-22s VOID (%s)" % (name, e))
            void = True
            continue
        if ia != ib:
            print("%-22s DIFFERS (time index or element names)" % name)
            differ += 1
            continue
        items = sorted(i for i in set(da[k]) | set(db[k]) if i.startswith(("node.", "link.")))
        same_k = True
        for item in items:
            kind = item.split(".")[0]
            try:
                r = cmp_var(os.path.join(d_a, item + ".f64"), os.path.join(d_b, item + ".f64"),
                            ia["times"], ia[kind], rtol, atol)
            except (OSError, ValueError) as e:
                print("%-22s %-22s VOID (%s)" % (name, item, e))
                void = True
                continue
            if not r["differ"]:
                continue
            same_k = False
            line = "%-22s %-22s DIFFERS %d/%d values; max_abs %.3g at %s; max_rel %.3g at %s; max_ulp %d; allclose(rtol=%g, atol=%g) %s" % (
                name, item, r["differ"], r["n"], r["max_abs"], fmt_where(r["at_abs"]),
                r["max_rel"], fmt_where(r["at_rel"]), r["max_ulp"], rtol, atol,
                "PASS" if not r["fail"] else "FAIL on %d values, %d elements; worst %s" % (
                    r["fail"], len(r["fail_elems"]), fmt_where(r["worst_fail"])))
            print(line)
            r["fail_elems"] = sorted(r["fail_elems"])
            out.append(dict(r, net=net, sim=s, item=item))
        if same_k:
            print("%-22s IDENTICAL (%d variables)" % (name, len(items)))
        else:
            differ += 1
    with open(os.path.join(rb, "cmp_%s__%s.json" % (os.path.basename(os.path.normpath(ra)),
                                                    os.path.basename(os.path.normpath(rb)))), "w") as f:
        json.dump(out, f, indent=1, default=str)
    if void:
        print("VOID")
        return 2
    print("DIFFERS" if differ else "IDENTICAL")
    return 1 if differ else 0


def pair_stats(ra, rb, net, sim, item, digests, rtol, atol, cache):
    """cmp_var for one variable of two runs; None when their digests match."""
    if digests[ra][(net, sim)][item] == digests[rb][(net, sim)][item]:
        return None
    key = (ra, rb, net, sim, item)
    if key not in cache:
        d_a = os.path.join(ra, net.replace("/", "-"), sim)
        d_b = os.path.join(rb, net.replace("/", "-"), sim)
        with open(os.path.join(d_a, "index.json")) as f:
            ia = json.load(f)
        with open(os.path.join(d_b, "index.json")) as f:
            if json.load(f) != ia:
                raise ValueError("%s %s: index differs between %s and %s" % (net, sim, ra, rb))
        cache[key] = cmp_var(os.path.join(d_a, item + ".f64"), os.path.join(d_b, item + ".f64"),
                             ia["times"], ia[item.split(".")[0]], rtol, atol)
    return cache[key]


def summarize(stats):
    """max_abs, max_rel and allclose failures over a list of pair results (None = identical)."""
    diff = [s for s in stats if s is not None and s["differ"]]
    if not diff:
        return "0/%d pairs differ" % len(stats)
    worst = max(diff, key=lambda s: (s["fail"], s["max_abs"]))
    return "%d/%d pairs differ, max_abs %.3g, max_rel %.3g, %d/%d pairs fail allclose (up to %d values, %d elements%s)" % (
        len(diff), len(stats), max(s["max_abs"] for s in diff), max(s["max_rel"] for s in diff),
        sum(1 for s in diff if s["fail"]), len(stats), worst["fail"], len(worst["fail_elems"]),
        "; worst " + fmt_where(worst["worst_fail"]) if worst["fail"] else "")


def spread(group_a, group_b, sim=None, rtol=0.01, atol=1e-6):
    """Within-group variation of repeat runs (every run against every other in its
    group) next to the variation across the groups (every A run against every B run)."""
    runs = group_a + group_b
    try:
        digests = {r: read_digests(os.path.join(r, "digests.txt")) for r in runs}
    except (OSError, ValueError) as e:
        print("error: %s" % e)
        print("VOID")
        return 2
    keys = sorted(set.union(*(set(d) for d in digests.values())))
    keys = [k for k in keys if sim is None or k[1] == sim]
    void = not keys or len(group_a) < 1 or len(group_b) < 1
    differ = 0
    cache = {}
    pairs_a = [(x, y) for i, x in enumerate(group_a) for y in group_a[i + 1:]]
    pairs_b = [(x, y) for i, x in enumerate(group_b) for y in group_b[i + 1:]]
    pairs_x = [(x, y) for x in group_a for y in group_b]
    for k in keys:
        name = "%s %s" % k
        if any(k not in digests[r] or "error" in digests[r][k] for r in runs):
            print("%-22s VOID (missing or raised in %s)" % (name, ", ".join(
                os.path.basename(os.path.normpath(r)) for r in runs
                if k not in digests[r] or "error" in digests[r][k])))
            void = True
            continue
        items = sorted(i for i in digests[runs[0]][k] if i.startswith(("node.", "link.")))
        all_same = True
        for item in items:
            if len({digests[r][k].get(item) for r in runs}) == 1:
                continue
            all_same = False
            try:
                sa = [pair_stats(x, y, k[0], k[1], item, digests, rtol, atol, cache) for x, y in pairs_a]
                sb = [pair_stats(x, y, k[0], k[1], item, digests, rtol, atol, cache) for x, y in pairs_b]
                sx = [pair_stats(x, y, k[0], k[1], item, digests, rtol, atol, cache) for x, y in pairs_x]
            except (OSError, ValueError, KeyError) as e:
                print("%-22s %-20s VOID (%s)" % (name, item, e))
                void = True
                continue
            print("%-22s %-20s distinct A %d/%d, B %d/%d" % (
                name, item, len({digests[r][k][item] for r in group_a}), len(group_a),
                len({digests[r][k][item] for r in group_b}), len(group_b)))
            print("    within A: %s" % summarize(sa))
            print("    within B: %s" % summarize(sb))
            print("    A vs B:   %s" % summarize(sx))
        if all_same:
            print("%-22s IDENTICAL in all %d runs (%d variables)" % (name, len(runs), len(items)))
        else:
            differ += 1
    if void:
        print("VOID")
        return 2
    print("DIFFERS" if differ else "IDENTICAL")
    return 1 if differ else 0


def probe(net, sim, specs, runs):
    """One value per run for each VAR:ELEMENT:SECONDS, e.g. node.pressure:JUNCTION-1100:86400."""
    print("run " + " ".join(specs))
    void = not runs
    for run in runs:
        d = os.path.join(run, net.replace("/", "-"), sim)
        vals = []
        try:
            with open(os.path.join(d, "index.json")) as f:
                ix = json.load(f)
            for s in specs:
                var, el, t = s.rsplit(":", 2)
                names = ix[var.split(".")[0]]
                i = ix["times"].index(float(t)) * len(names) + names.index(el)
                with open(os.path.join(d, var + ".f64"), "rb") as f:
                    f.seek(8 * i)
                    vals.append("%.10g" % struct.unpack("<d", f.read(8))[0])
        except (OSError, ValueError, KeyError) as e:
            print("%s VOID (%s)" % (run, e))
            void = True
            continue
        print("%s %s" % (os.path.basename(os.path.normpath(run)), " ".join(vals)))
    return 2 if void else 0


def main(a):
    opts = {}
    for o in ("--sim", "--rtol", "--atol"):
        if o in a:
            k = a.index(o)
            opts[o] = a[k + 1]
            a = a[:k] + a[k + 2:]
    sim = opts.get("--sim")
    if a[:1] == ["digcmp"] and len(a) == 3:
        return digcmp(a[1], a[2], sim)
    if a[:1] == ["cmp"] and len(a) == 3:
        return cmp(a[1], a[2], sim, float(opts.get("--rtol", 0.01)), float(opts.get("--atol", 1e-6)))
    if a[:1] == ["probe"] and "--" in a and a.index("--") >= 4:
        k = a.index("--")
        return probe(a[1], a[2], a[3:k], a[k + 1:])
    if a[:1] == ["spread"] and "--" in a:
        k = a.index("--")
        return spread(a[1:k], a[k + 1:], sim, float(opts.get("--rtol", 0.01)),
                      float(opts.get("--atol", 1e-6)))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
