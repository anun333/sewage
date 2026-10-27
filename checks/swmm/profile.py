#!/usr/bin/env python3
"""profile.py A.out B.out [var=link.flow] : per report period, how many link
flows differ and the largest |diff| relative to the largest flow in the
system at that period (to tell persistent drift from transient spikes)."""
import os, sys, struct
sys.dont_write_bytecode = True  # no __pycache__ beside the scripts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swmmcmp as C
A, B = C.OutFile(sys.argv[1]), C.OutFile(sys.argv[2])
off = A.nsub * A.nsubv + A.nnode * A.nnodev
nl, nv = A.nlink, A.nlinkv
rows = []
for p in range(A.nperiods):
    _, ua = A.period(p); _, ub = B.period(p)
    fa = [C.f32(ua[off + e * nv]) for e in range(nl)]
    fb = [C.f32(ub[off + e * nv]) for e in range(nl)]
    d = [abs(x - y) for x, y in zip(fa, fb)]
    big = max(abs(x) for x in fa) or 1.0
    nd = sum(1 for x in d if x)
    k = max(range(nl), key=lambda e: d[e])
    rows.append((p, nd, d[k], d[k] / big, A.ids['link'][k], fa[k], fb[k]))
step = max(1, A.nperiods // 40)
print("period  links_differing  max|dQ|   max|dQ|/max|Q|  link  A  B")
for r in rows[::step]:
    print("%5d %8d %12.4g %12.3g  %s  %.6g  %.6g" % r)
w = max(rows, key=lambda r: r[3])
print("worst:", "%5d %8d %12.4g %12.3g  %s  %.6g  %.6g" % w)
print("last :", "%5d %8d %12.4g %12.3g  %s  %.6g  %.6g" % rows[-1])
