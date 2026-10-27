#!/usr/bin/env python3
"""timecmp.py - how much slower is one SWMM build than another?

  python3 -I timecmp.py RUNS TAG_A TAG_B

Reads RUNS/TAG_A-r*/meta.json and RUNS/TAG_B-r*/meta.json, written by
`swmmrun.py run` (one directory per repeat), and prints each model's median
wall time under A and B, their ratio, and the ratio of the summed medians.
Models that take under 0.2 s under A are left out of the per-model table
(process start-up dominates them) but counted in the totals.

Run the repeats interleaved (A, B, A, B, ...), pinned to one CPU, on as idle a
machine as you can, and say what the load was: the medians resist noise, they
don't remove it.
"""
import glob
import json
import os
import statistics
import sys


def load(runs, tag):
    secs = {}
    dirs = sorted(d for d in glob.glob(os.path.join(runs, tag + "-r*")) if os.path.isdir(d))
    for d in dirs:
        with open(os.path.join(d, "meta.json")) as f:
            for row in json.load(f)["rows"]:
                if row["exit"] == 0:
                    secs.setdefault(row["model"], []).append(row["secs"])
    return secs, len(dirs)


def main(a):
    if len(a) != 3:
        print(__doc__)
        return 2
    runs, ta, tb = a
    sa, na = load(runs, ta)
    sb, nb = load(runs, tb)
    models = sorted(set(sa) & set(sb))
    if not models or na < 3 or nb < 3:
        print("VOID: need at least 3 repeats of each and models in common (got %d and %d)" % (na, nb))
        return 2
    print("%-38s %9s %9s %7s  (median of %d and %d repeats)" % ("model", ta, tb, "B/A", na, nb))
    tot_a = tot_b = 0.0
    for m in models:
        ma, mb = statistics.median(sa[m]), statistics.median(sb[m])
        tot_a += ma
        tot_b += mb
        if ma >= 0.2:
            spread = (max(sa[m]) - min(sa[m])) / ma if ma else 0
            print("%-38s %8.2fs %8.2fs %7.3f  (A's spread %.0f%%)" % (m, ma, mb, mb / ma, 100 * spread))
    print("%-38s %8.2fs %8.2fs %7.3f" % ("total of medians", tot_a, tot_b, tot_b / tot_a))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
