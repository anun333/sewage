#!/usr/bin/env python3
"""swmmcmp.py - compare two EPA SWMM 5.x runs bit for bit.

    python3 -I swmmcmp.py A.out B.out [--rpt A.rpt B.rpt] [--json]

Binary .out: the whole file is compared byte for byte first. If it differs,
every reported float32 value is decoded and compared, per element type and
variable: how many values differ, the largest absolute and relative
difference, the largest difference in float32 ulps, and where (element ID,
report period).

It also applies upstream's own regression rule, nrtest-swmm's
"swmm allclose" (numpy.testing.assert_allclose per element and period,
|test - ref| <= atol + rtol*|ref|), with the tolerances pyswmm's CI passes:
rtol=0.01, atol=1e-6 (ci-tools/linux/run-nrtests.sh).

.rpt: compared after masking the three lines that carry wall-clock time
("Analysis begun on", "Analysis ended on", "Total elapsed time"), the
pyswmm logo line (it carries the build date) and the "Number of Threads"
echo; the differing lines are listed. nrtest-swmm's "swmm report" rule (drop the first
and last 4 lines, all others equal) is reported too.

Verdict line, as crnumerics: IDENTICAL (exit 0), DIFFERS (exit 1),
VOID (exit 2: a file is missing or unreadable). Standard library only.
"""
import json
import math
import re
import struct
import sys

MAGIC = 516114522
RTOL, ATOL = 0.01, 1e-6

SUB_VARS = ["rainfall", "snow_depth", "evap_loss", "infil_loss", "runoff",
            "gw_outflow", "gw_elev", "soil_moist"]
NODE_VARS = ["depth", "head", "volume", "lateral_inflow", "total_inflow",
             "flooding"]
LINK_VARS = ["flow", "depth", "velocity", "volume", "capacity"]
SYS_VARS = ["air_temp", "rainfall", "snow_depth", "evap_infil", "runoff",
            "dw_inflow", "gw_inflow", "rdii_inflow", "ext_inflow",
            "total_inflow", "flooding", "outflow", "storage", "evap_rate",
            "pet"]


class OutFile:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.raw = f.read()
        r = self.raw
        if len(r) < 52:
            raise ValueError("file too short")
        (self.magic, self.version, self.flow_units, self.nsub, self.nnode,
         self.nlink, self.npoll) = struct.unpack_from("<7i", r, 0)
        (self.id_pos, self.prop_pos, self.out_pos, self.nperiods,
         self.errcode, magic2) = struct.unpack_from("<6i", r, len(r) - 24)
        if self.magic != MAGIC or magic2 != MAGIC:
            raise ValueError("bad magic number")
        pos = self.id_pos
        names = []
        for _ in range(self.nsub + self.nnode + self.nlink + self.npoll):
            (n,) = struct.unpack_from("<i", r, pos)
            names.append(r[pos + 4:pos + 4 + n].decode("latin-1"))
            pos += 4 + n
        a, b, c = self.nsub, self.nsub + self.nnode, self.nsub + self.nnode + self.nlink
        self.ids = {"subcatch": names[:a], "node": names[a:b],
                    "link": names[b:c], "system": ["system"]}
        self.polls = names[c:]
        # skip pollutant units and the property block to the variable codes
        pos += 4 * self.npoll
        (k,) = struct.unpack_from("<i", r, pos); pos += 4 + 4 * k + 4 * k * self.nsub
        (k,) = struct.unpack_from("<i", r, pos); pos += 4 + 4 * k + 4 * k * self.nnode
        (k,) = struct.unpack_from("<i", r, pos); pos += 4 + 4 * k + 4 * k * self.nlink
        nv = []
        for _ in range(4):
            (k,) = struct.unpack_from("<i", r, pos)
            nv.append(k)
            pos += 4 + 4 * k
        self.nsubv, self.nnodev, self.nlinkv, self.nsysv = nv
        self.start_date, self.report_step = struct.unpack_from("<di", r, pos)
        self.nvals = (self.nsub * self.nsubv + self.nnode * self.nnodev +
                      self.nlink * self.nlinkv + self.nsysv)
        self.period_bytes = 8 + 4 * self.nvals
        if self.out_pos + self.nperiods * self.period_bytes != len(r) - 24:
            raise ValueError("results block size does not match epilogue")

    def blocks(self):
        """(type, nelem, nvar, var names) in the order SWMM writes them."""
        pn = self.polls
        return [("subcatch", self.nsub, self.nsubv, SUB_VARS + pn),
                ("node", self.nnode, self.nnodev, NODE_VARS + pn),
                ("link", self.nlink, self.nlinkv, LINK_VARS + pn),
                ("system", 1, self.nsysv, SYS_VARS)]

    def period(self, p):
        off = self.out_pos + p * self.period_bytes
        date = struct.unpack_from("<d", self.raw, off)[0]
        u = struct.unpack_from("<%dI" % self.nvals, self.raw, off + 8)
        return date, u


def f32(u):
    return struct.unpack("<f", struct.pack("<I", u))[0]


def ordered(u):
    """float32 bit pattern -> integer that orders like the float (for ulps)."""
    return u if u < 0x80000000 else 0x80000000 - u


def compare_out(pa, pb):
    A, B = OutFile(pa), OutFile(pb)
    res = {"bytes_identical": A.raw == B.raw, "file_a": pa, "file_b": pb}
    if res["bytes_identical"]:
        return res
    shape_a = (A.nsub, A.nnode, A.nlink, A.npoll, A.nsubv, A.nnodev, A.nlinkv, A.nsysv)
    shape_b = (B.nsub, B.nnode, B.nlink, B.npoll, B.nsubv, B.nnodev, B.nlinkv, B.nsysv)
    res["same_shape"] = shape_a == shape_b
    res["nperiods"] = (A.nperiods, B.nperiods)
    res["prologue_identical"] = A.raw[:A.out_pos] == B.raw[:B.out_pos]
    res["epilogue_identical"] = A.raw[-24:] == B.raw[-24:]
    if not res["same_shape"]:
        return res
    stats = {}
    nrtest_fail = 0
    nrtest_first = None
    ndiff = 0
    ntotal = 0
    first_diff_period = None
    date_diffs = 0
    for p in range(min(A.nperiods, B.nperiods)):
        da, ua = A.period(p)
        db, ub = B.period(p)
        if da != db:
            date_diffs += 1
        if ua == ub:
            ntotal += len(ua)
            continue
        i = 0
        for typ, ne, nv, vnames in A.blocks():
            for e in range(ne):
                elem_fail = False
                for v in range(nv):
                    x, y = ua[i], ub[i]
                    i += 1
                    ntotal += 1
                    if x == y:
                        continue
                    ndiff += 1
                    if first_diff_period is None:
                        first_diff_period = p
                    fa, fb = f32(x), f32(y)
                    key = "%s.%s" % (typ, vnames[v] if v < len(vnames) else v)
                    s = stats.setdefault(key, {"n": 0, "max_abs": 0.0, "max_rel": 0.0,
                                               "max_ulp": 0, "where_abs": None,
                                               "a": None, "b": None})
                    s["n"] += 1
                    if math.isnan(fa) or math.isnan(fb):
                        s["nan"] = s.get("nan", 0) + 1
                        continue
                    d = abs(fa - fb)
                    den = max(abs(fa), abs(fb))
                    rel = d / den if den else 0.0
                    ulp = abs(ordered(x) - ordered(y))
                    if d > s["max_abs"]:
                        s.update(max_abs=d, where_abs="%s %s period %d" % (typ, A.ids[typ][e], p),
                                 a=fa, b=fb)
                    s["max_rel"] = max(s["max_rel"], rel)
                    s["max_ulp"] = max(s["max_ulp"], ulp)
                    # nrtest-swmm: assert_allclose(test=B, ref=A)
                    if not d <= ATOL + RTOL * abs(fa):
                        elem_fail = True
                if elem_fail:
                    nrtest_fail += 1
                    if nrtest_first is None:
                        nrtest_first = "%s %s period %d" % (typ, A.ids[typ][e], p)
    res.update(values_total=ntotal, values_differ=ndiff, first_diff_period=first_diff_period,
               date_diffs=date_diffs, per_var=stats,
               nrtest_allclose_pass=(nrtest_fail == 0),
               nrtest_failing_elements=nrtest_fail, nrtest_first_fail=nrtest_first)
    if stats:
        res["max_abs"] = max(s["max_abs"] for s in stats.values())
        res["max_rel"] = max(s["max_rel"] for s in stats.values())
        res["max_ulp"] = max(s["max_ulp"] for s in stats.values())
    return res


# Wall-clock lines; the pyswmm fork's logo line, which carries the build date
# (BUILD_ID, report.c report_writeLogo); and the thread count SWMM echoes in
# its options table (the run driver reads that separately).
MASK = re.compile(r"^\s*(Analysis begun on|Analysis ended on|Total elapsed time"
                  r"|PYSWMM TOOLKIT API - VERSION|Number of Threads)")


def masked_rpt_bytes(path):
    """The .rpt with the masked lines replaced, as bytes (for digests). Line
    endings are read as \\n, so a Windows report (\\r\\n) digests like a Linux one."""
    with open(path, "rb") as f:
        lines = f.read().split(b"\n")
    out = []
    for x in lines:
        x = x[:-1] if x.endswith(b"\r") else x
        s = x.decode("latin-1")
        out.append(b"<masked>" if MASK.match(s) else x)
    return b"\n".join(out)


def compare_rpt(pa, pb):
    with open(pa, encoding="latin-1") as f:
        la = f.read().splitlines()
    with open(pb, encoding="latin-1") as f:
        lb = f.read().splitlines()
    ma = [("<masked>" if MASK.match(x) else x) for x in la]
    mb = [("<masked>" if MASK.match(x) else x) for x in lb]
    diffs = [(i + 1, x, y) for i, (x, y) in enumerate(zip(ma, mb)) if x != y]
    nr_pass = all(x == y for x, y in zip(la[4:-4], lb[4:-4]))
    return {"identical_masked": ma == mb, "lines": (len(la), len(lb)),
            "differing_lines": len(diffs) + abs(len(la) - len(lb)),
            "first_diffs": diffs[:12], "nrtest_report_pass": nr_pass}


def main(argv):
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    rpt = None
    if "--rpt" in argv:
        k = argv.index("--rpt")
        rpt = argv[k + 1:k + 3]
        argv = argv[:k] + argv[k + 3:]
    if len(argv) != 2:
        print(__doc__)
        print("VOID")
        return 2
    try:
        out = compare_out(*argv)
        rr = compare_rpt(*rpt) if rpt else None
    except (OSError, ValueError, struct.error) as e:
        print("error: %s" % e)
        print("VOID")
        return 2
    same = out["bytes_identical"] and (rr is None or rr["identical_masked"])
    if as_json:
        print(json.dumps({"out": out, "rpt": rr}, default=str))
    else:
        if out["bytes_identical"]:
            print("out: byte-identical")
        else:
            print("out: DIFFERS; %s of %s values; max abs %.3g, max rel %.3g, max %s ulp; "
                  "first period %s; nrtest allclose(rtol=0.01, atol=1e-6) %s" % (
                      out.get("values_differ"), out.get("values_total"),
                      out.get("max_abs", 0), out.get("max_rel", 0), out.get("max_ulp", 0),
                      out.get("first_diff_period"),
                      "PASS" if out.get("nrtest_allclose_pass") else
                      "FAIL (%s elements, first %s)" % (out.get("nrtest_failing_elements"),
                                                         out.get("nrtest_first_fail"))))
            for k, s in sorted(out.get("per_var", {}).items(), key=lambda kv: -kv[1]["max_rel"]):
                print("  %-26s n=%-7d max_abs=%-10.3g max_rel=%-10.3g max_ulp=%-9d at %s (%r vs %r)" % (
                    k, s["n"], s["max_abs"], s["max_rel"], s["max_ulp"], s["where_abs"], s["a"], s["b"]))
        if rr is not None:
            if rr["identical_masked"]:
                print("rpt: identical (timestamps masked)")
            else:
                print("rpt: DIFFERS; %d lines; nrtest report rule %s" % (
                    rr["differing_lines"], "PASS" if rr["nrtest_report_pass"] else "FAIL"))
                for n, x, y in rr["first_diffs"]:
                    print("  line %d:\n    A: %s\n    B: %s" % (n, x.rstrip(), y.rstrip()))
    print("IDENTICAL" if same else "DIFFERS")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
