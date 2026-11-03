#!/usr/bin/env python3
"""echo_screen.py: what kind of trouble do one state's sewage plants report to EPA?

N2 in ../../ideas.md. It reads EPA's ECHO downloads straight from their zip files:

  {ST}_FY{YYYY}_NPDES_DMRS_LIMITS.zip  every DMR value with its limit and violation code
  npdes_downloads.zip                  permits, facilities, the quarterly noncompliance
                                       history and single-event violations
  {ST}_NPDES_EFF_VIOLATIONS.zip        DMR violations, used only to cross-check

and sorts each POTW's problems by kind, over the fiscal years asked:

  effluent  E90 values (a limit exceeded), by parameter group
  missing   D80 and D90 values (a required value not received)
  snc       quarters whose HLRNC code marks significant noncompliance, by kind
  events    single-event violations (overflows, bypasses and the like), by description

Then it looks for reported values that contradict their own arithmetic, which is
what N1 (exact DMR arithmetic) would fix:

  avg>max   a monthly average or monthly geometric mean above the daily (or instantaneous)
            maximum for the same parameter, outfall, period and unit, or a minimum above
            a maximum. Rolling, quarterly and annual averages span other months, so they
            are left out
  load      a monthly-average loading (lb/d) that differs from the monthly-average
            concentration (mg/L) x flow (MGD) x 8.34 by a unit factor: 8.34, 3.785 or a
            power of ten, either way

and two signals that are not contradictions, reported for what they suggest:

  rounding  E90s whose value, rounded to the limit's decimals, no longer exceeds the
            limit; ties (exactly half a unit over) are counted apart. ECHO strips trailing
            zeros (a permit's 2.0 is stored as 2), so the stated decimals are unknown: the
            count at the stored decimals is an upper bound, and the count with one more
            decimal is shown beside it
  outlier   values at least 100 times the median of the same series (plant, outfall,
            parameter, statistical base and unit), a common sign of a unit slip

Verdicts as in crnumerics: IDENTICAL (exit 0) when no reported value contradicts its
own definition (avg>max), DIFFERS (exit 1) when some do, VOID (exit 2) when a control
fails or no plant was read. The loading test is reported but left out of the verdict,
since a ratio near a unit factor can also arise by chance; its matches beyond the
larger decoy are the estimate it gives. The controls are synthetic rows run through the
same tests: an average above its maximum, a loading computed without the 8.34, an E90
at 126.4 against a limit of 126 and a hundredfold value must each be flagged, and a
clean twin of each must not. A fifth control is real: the E90, D80 and D90 counted
from the DMR files must equal those in the violations file for the same plants and
window. For the loading test, each unit factor's matches are printed beside those of
decoys 15% either side of it, which no unit slip produces; a factor whose count does
not stand above its decoys' is no evidence of a slip.

  --flags FILE  every flagged value with its context, as TSV

  python3 -I echo_screen.py --data DIR [--state TN] [--fy 2023 2025] [--tsv FILE]
Standard library only.
"""
import argparse
import collections
import csv
import io
import math
import os
import statistics
import sys
import zipfile
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN

csv.field_size_limit(1 << 24)

GROUPS = [  # (group, substrings of PARAMETER_DESC, lower case), first match wins
    ("overflow", ["sso,", "overflow", "bypass"]),   # Tennessee reports SSOs as DMR parameters
    ("ammonia", ["ammonia"]),
    ("bod", ["bod", "biochemical oxygen", "carbonaceous"]),
    ("tss", ["solids, total suspended", "suspended solids"]),
    ("settleable", ["settleable"]),
    ("bacteria", ["coli", "coliform", "enterococ"]),
    ("chlorine", ["chlorine"]),
    ("ph", ["ph"]),
    ("oxygen", ["oxygen, dissolved", "dissolved oxygen"]),
    ("phosphorus", ["phosphorus"]),
    ("nitrogen", ["nitrogen", "nitrate", "nitrite", "kjeldahl"]),
    ("toxicity", ["toxicity", "lc50", "ic25", "noec", "ceriodaphnia", "pimephales"]),
    ("metals", ["copper", "zinc", "lead", "mercury", "cadmium", "nickel", "silver",
                "chromium", "arsenic", "selenium", "cyanide", "aluminum", "iron"]),
    ("flow", ["flow"]),
    ("removal", ["removal"]),
]
SIZE_BINS = [(0.1, "<0.1 MGD"), (1.0, "0.1-1 MGD"), (10.0, "1-10 MGD"),
             (math.inf, ">=10 MGD")]
SNC_KINDS = {"E": "effluent", "X": "effluent", "D": "missing DMR", "W": "missing DMR",
             "S": "schedule", "T": "schedule"}
UNIT_FACTORS = [8.34, 1 / 8.34, 3.785, 1 / 3.785, 10.0, 0.1, 100.0, 0.01, 1000.0, 0.001]
CEILINGS = {"2419.6", "24196", "241960", "200.5", "2005"}  # Quanti-Tray/2000 and 51-well tops, x1 and x10
FACTOR_TOL = 0.03          # relative distance from a unit factor that counts as a match
OUTLIER_X = 100.0
OUTLIER_MIN_N = 6


def group_of(desc):
    d = desc.lower()
    for g, keys in GROUPS:
        if g == "ph":
            if d == "ph" or d.startswith("ph,") or d.startswith("ph "):
                return g
            continue
        if any(k in d for k in keys):
            return g
    return "other"


def size_bin(mgd):
    if mgd is None:
        return "unknown"
    for top, name in SIZE_BINS:
        if mgd < top:
            return name
    return SIZE_BINS[-1][1]


def num(s):
    try:
        return float(s) if s.strip() != "" else None
    except ValueError:
        return None


def mdy(s):
    try:
        m, d, y = s.split("/")
        return date(int(y), int(m), int(d))
    except (ValueError, AttributeError):
        return None


def reader(zpath, member=None):
    zf = zipfile.ZipFile(zpath)
    name = member or next(n for n in zf.namelist() if n.lower().endswith(".csv"))
    f = io.TextIOWrapper(zf.open(name), encoding="latin-1", newline="")
    return csv.DictReader(f)


# ---------------------------------------------------------------- the four signals

AVG_DESCS = {"Monthly Average", "Monthly Geometric Mean"}
DAILY_MAX_DESCS = {"Daily Maximum", "Instantaneous Maximum"}
MAX_DESCS = DAILY_MAX_DESCS | {"Maximum"}
MIN_DESCS = {"Daily Minimum", "Instantaneous Minimum", "Minimum"}


def avg_above_max(groups, sets):
    """groups: key -> list of (stat_code, value); sets: name -> statistical base codes.
    Returns (key, kind, value, maximum) for each contradiction."""
    out = []
    for key, vals in groups.items():
        dmax = [v for c, v in vals if c in sets["daily_max"]]
        amax = [v for c, v in vals if c in sets["max"]]
        avgs = [v for c, v in vals if c in sets["avg"]]
        mins = [v for c, v in vals if c in sets["min"]]
        if dmax and avgs and max(avgs) > max(dmax) * (1 + 1e-9) + 1e-12:
            out.append((key, "avg>max", max(avgs), max(dmax)))
        if amax and mins and max(mins) > max(amax) * (1 + 1e-9) + 1e-12:
            out.append((key, "min>max", max(mins), max(amax)))
    return out


def load_check(conc, load, flow):
    """conc, load: key (permit, feature, location, parameter, period, stat code) -> value;
    flow: (permit, feature, period, stat code) -> value. Returns ratios and flags."""
    ratios, flags = [], []
    for k, c in conc.items():
        if k not in load:
            continue
        fk = (k[0], k[1], k[4], k[5])
        q = flow.get(fk)
        if q is None or c <= 0 or q <= 0 or load[k] <= 0:
            continue
        r = load[k] / (c * q * 8.34)
        ratios.append(r)
        for f in UNIT_FACTORS:
            if abs(r / f - 1) <= FACTOR_TOL:
                flags.append((k, r, f, c, q, load[k]))
                break
    return ratios, flags


def decimals_of(text):
    t = text.strip()
    return len(t.split(".", 1)[1]) if "." in t else 0


def rounding_edge(value_text, limit_text, stat_type, extra=0, rule=ROUND_HALF_EVEN):
    """For an E90: 'clears' if the value rounded to the limit's decimals (plus `extra`) no
    longer violates, 'tie' if it sits exactly half a unit beyond, else 'stands'."""
    try:
        v, lim = Decimal(value_text.strip()), Decimal(limit_text.strip())
    except InvalidOperation:
        return None
    q = Decimal(1).scaleb(-(decimals_of(limit_text) + extra))
    half = q / 2
    if stat_type == "MIN":
        if v == lim - half:
            return "tie"
        return "clears" if v.quantize(q, rounding=rule) >= lim else "stands"
    if v == lim + half:
        return "tie"
    return "clears" if v.quantize(q, rounding=rule) <= lim else "stands"


def outliers(series):
    """series: key -> list of (value, row detail). Values >= OUTLIER_X x the series median."""
    out = []
    for key, vals in series.items():
        xs = [v for v, _ in vals if v > 0]
        if len(xs) < OUTLIER_MIN_N:
            continue
        med = statistics.median(xs)
        if med <= 0:
            continue
        for v, det in vals:
            if v >= OUTLIER_X * med:
                out.append((key, v, med, det))
    return out


def tot_codes(plant, key):
    return sum(c[key] for c in plant.values())


def decoy_counts(ratios, f, tol=FACTOR_TOL):
    near = lambda g: sum(abs(r / g - 1) <= tol for r in ratios)
    return near(f / 1.15), near(f), near(f * 1.15)


def controls(sets):
    """Synthetic rows through the same tests; returns a list of failures."""
    fails = []
    dm, av = sorted(sets["daily_max"])[0], sorted(sets["avg"])[0]
    g = {("P1", "001", "1", "00310", "01/31/2025", "mg/L"): [(av, 30.0), (dm, 25.0)],
         ("P2", "001", "1", "00310", "01/31/2025", "mg/L"): [(av, 20.0), (dm, 25.0)]}
    hit = {k[0] for k, kind, _, _ in avg_above_max(g, sets)}
    if hit != {"P1"}:
        fails.append(f"avg>max control: flagged {sorted(hit)}, expected ['P1']")
    k1 = ("P1", "001", "1", "00310", "01/31/2025", "MK")
    k2 = ("P2", "001", "1", "00310", "01/31/2025", "MK")
    conc = {k1: 20.0, k2: 20.0}
    load = {k1: 20.0 * 1.0, k2: 20.0 * 1.0 * 8.34}     # P1 left out the 8.34
    flow = {("P1", "001", "01/31/2025", "MK"): 1.0, ("P2", "001", "01/31/2025", "MK"): 1.0}
    _, fl = load_check(conc, load, flow)
    hit = {k[0] for k, *_ in fl}
    if hit != {"P1"}:
        fails.append(f"load control: flagged {sorted(hit)}, expected ['P1']")
    got = (rounding_edge("126.4", "126", "MAX"), rounding_edge("127", "126", "MAX"),
           rounding_edge("126.5", "126", "MAX"), rounding_edge("5.96", "6.0", "MIN"),
           rounding_edge("5.95", "6.0", "MIN"), rounding_edge("126.4", "126", "MAX", extra=1))
    want = ("clears", "stands", "tie", "clears", "tie", "stands")
    if got != want:
        fails.append(f"rounding control: got {got}, expected {want}")
    s = {"A": [(1.0, "a")] * 6 + [(150.0, "slip")], "B": [(1.0, "b")] * 6 + [(50.0, "real")]}
    hit = {d for _, _, _, d in outliers(s)}
    if hit != {"slip"}:
        fails.append(f"outlier control: flagged {sorted(hit)}, expected ['slip']")
    return fails


# ---------------------------------------------------------------- reading ECHO

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", required=True)
    ap.add_argument("--state", default="TN")
    ap.add_argument("--fy", type=int, nargs=2, default=[2023, 2025])
    ap.add_argument("--tsv")
    ap.add_argument("--flags")
    ap.add_argument("--examples", type=int, default=8)
    a = ap.parse_args()
    st, fy0, fy1 = a.state.upper(), a.fy[0], a.fy[1]
    start, end = date(fy0 - 1, 10, 1), date(fy1, 9, 30)
    D = lambda n: os.path.join(a.data, n)

    # statistical bases, chosen by their descriptions in EPA's reference table
    sets = {"avg": set(), "daily_max": set(), "max": set(), "min": set()}
    with open(D("REF_STATISTICAL_BASE.csv"), encoding="latin-1", newline="") as f:
        for r in csv.DictReader(f):
            code, desc = r["STATISTICAL_BASE_CODE"].strip(), r["STATISTICAL_BASE_LONG_DESC"].strip()
            for name, descs in (("avg", AVG_DESCS), ("daily_max", DAILY_MAX_DESCS),
                                ("max", MAX_DESCS), ("min", MIN_DESCS)):
                if desc in descs:
                    sets[name].add(code)
    print(f"# ECHO screen: {st} POTWs, FY{fy0}-FY{fy1} ({start} to {end})\n")
    print("Statistical bases compared: " + "; ".join(f"{n} {', '.join(sorted(s))}" for n, s in sets.items()) + "\n")

    fails = controls(sets) if all(sets.values()) else [f"missing statistical bases: {sets}"]

    # permits: latest version of each in the state
    permits = {}
    for r in reader(D("npdes_downloads.zip"), "ICIS_PERMITS.csv"):
        p = r["EXTERNAL_PERMIT_NMBR"]
        if not p.startswith(st):
            continue
        v = int(r["VERSION_NMBR"] or 0)
        if p not in permits or v > permits[p]["v"]:
            permits[p] = {"v": v, "type": r["FACILITY_TYPE_INDICATOR"].strip(),
                          "ptype": r["PERMIT_TYPE_CODE"], "mm": r["MAJOR_MINOR_STATUS_FLAG"],
                          "status": r["PERMIT_STATUS_CODE"],
                          "flow": num(r["TOTAL_DESIGN_FLOW_NMBR"]), "name": r["PERMIT_NAME"]}
    potw = {p for p, d in permits.items() if d["type"] == "POTW"}
    fac = {}
    for r in reader(D("npdes_downloads.zip"), "ICIS_FACILITIES.csv"):
        if r["NPDES_ID"] in potw:
            fac[r["NPDES_ID"]] = (r["FACILITY_NAME"], r["CITY"])

    # DMR values
    plant = collections.defaultdict(lambda: collections.Counter())
    seen_viol = set()
    groups = collections.defaultdict(list)
    conc, load, flow = {}, {}, {}
    series = collections.defaultdict(list)
    rounding = collections.Counter()
    round_ex = collections.defaultdict(list)
    e90_by_group = collections.Counter()
    other_desc = collections.Counter()
    desc_of = {}
    censored = collections.Counter()
    n_rows = n_potw_rows = 0
    for fy in range(fy0, fy1 + 1):
        z = D(f"{st}_FY{fy}_NPDES_DMRS_LIMITS.zip")
        for r in reader(z, f"{st}_FY{fy}_NPDES_DMRS.csv"):
            n_rows += 1
            p = r["EXTERNAL_PERMIT_NMBR"]
            if p not in potw:
                continue
            when = mdy(r["MONITORING_PERIOD_END_DATE"])
            if when is None or not (start <= when <= end):
                continue
            n_potw_rows += 1
            c = plant[p]
            c["values"] += 1
            vc = r["VIOLATION_CODE"].strip()
            vid = r["NPDES_VIOLATION_ID"].strip()
            if vc and (not vid or vid not in seen_viol):
                if vid:
                    seen_viol.add(vid)
                if vc == "E90":
                    g = group_of(r["PARAMETER_DESC"])
                    c["E90"] += 1
                    c["E90:" + g] += 1
                    e90_by_group[g] += 1
                    if g == "other":
                        other_desc[r["PARAMETER_DESC"]] += 1
                elif vc in ("D80", "D90"):
                    c[vc] += 1
            val_t = r["DMR_VALUE_NMBR"].strip()
            qual = r["DMR_VALUE_QUALIFIER_CODE"].strip()
            desc_of[r["PARAMETER_CODE"]] = r["PARAMETER_DESC"]
            if val_t in CEILINGS and group_of(r["PARAMETER_DESC"]) == "bacteria":
                censored[(val_t, qual or "=", "E90" if vc == "E90" else "")] += 1
            if not val_t or qual in ("<", ">", "<=", ">=") or r["NODI_CODE"].strip():
                continue
            v = num(val_t)
            if v is None:
                continue
            feat, loc, par = r["PERM_FEATURE_NMBR"], r["MONITORING_LOCATION_CODE"], r["PARAMETER_CODE"]
            per, code = r["MONITORING_PERIOD_END_DATE"], r["STATISTICAL_BASE_CODE"]
            typ = r["STATISTICAL_BASE_TYPE_CODE"].strip().upper()
            unit = r["DMR_UNIT_DESC"].strip()
            groups[(p, feat, loc, par, per, unit)].append((code, v))
            series[(p, feat, loc, par, code, unit)].append((v, (per, r["PARAMETER_DESC"], vc)))
            if code in sets["avg"] and code == "MK":
                if par == "50050" and unit == "MGD":
                    fk = (p, feat, per, code)
                    if fk not in flow:
                        flow[fk] = v
                    elif flow[fk] is not None and abs(flow[fk] - v) > 1e-9 * max(1.0, v):
                        flow[fk] = None          # two different flows: ambiguous, skip
                elif unit == "mg/L":
                    conc[(p, feat, loc, par, per, code)] = v
                elif unit == "lb/d":
                    load[(p, feat, loc, par, per, code)] = v
            if vc == "E90" and r["LIMIT_VALUE_NMBR"].strip() and \
                    r["LIMIT_UNIT_CODE"].strip() == r["DMR_UNIT_CODE"].strip():
                k = rounding_edge(val_t, r["LIMIT_VALUE_NMBR"], typ)
                k1 = rounding_edge(val_t, r["LIMIT_VALUE_NMBR"], typ, extra=1)
                if k1:
                    rounding["+1 " + k1] += 1
                if k:
                    rounding[k] += 1
                    if k != "stands" and len(round_ex[k]) < a.examples:
                        round_ex[k].append((p, per, r["PARAMETER_DESC"], code, val_t,
                                            r["LIMIT_VALUE_NMBR"].strip(), unit))
    flow = {k: v for k, v in flow.items() if v is not None}
    universe = [p for p in plant if plant[p]["values"]]

    # quarterly noncompliance history and single events
    q0, q1 = fy0 * 10 + 1, fy1 * 10 + 4
    for r in reader(D("npdes_downloads.zip"), "NPDES_QNCR_HISTORY.csv"):
        p = r["NPDES_ID"]
        if p in plant:
            try:
                yq = int(r["YEARQTR"])
            except ValueError:
                continue
            if q0 <= yq <= q1:
                h = r["HLRNC"].strip()
                plant[p]["quarters"] += 1
                if h in SNC_KINDS:
                    plant[p]["SNC:" + SNC_KINDS[h]] += 1
                    plant[p]["SNC quarters"] += 1
    events = collections.Counter()
    for r in reader(D("npdes_downloads.zip"), "NPDES_SE_VIOLATIONS.csv"):
        p = r["NPDES_ID"]
        if p in plant:
            when = mdy(r["SINGLE_EVENT_VIOLATION_DATE"])
            if when and start <= when <= end:
                plant[p]["events"] += 1
                events[r["VIOLATION_DESC"].strip() or r["VIOLATION_CODE"]] += 1

    # cross-check: E90 in the violations file for the same plants and window
    eff = collections.Counter()
    eff_ids = set()
    for r in reader(D(f"{st}_NPDES_EFF_VIOLATIONS.zip")):
        if r["NPDES_ID"] in plant and r["VIOLATION_CODE"] in ("E90", "D80", "D90"):
            when = mdy(r["MONITORING_PERIOD_END_DATE"])
            vid = r["NPDES_VIOLATION_ID"]
            if when and start <= when <= end and vid not in eff_ids:
                eff_ids.add(vid)
                eff[r["VIOLATION_CODE"]] += 1

    for vc in ("E90", "D80", "D90"):
        if eff[vc] != tot_codes(plant, vc):
            fails.append(f"cross-check: {vc} {tot_codes(plant, vc):,} from the DMR files, {eff[vc]:,} in the violations file")
    aam = avg_above_max(groups, sets)
    ratios, lflags = load_check(conc, load, flow)
    outl = outliers(series)
    for key, kind, *_ in aam:
        plant[key[0]][kind] += 1
    for k, *_ in lflags:
        plant[k[0]]["load factor"] += 1
    for key, *_ in outl:
        plant[key[0]]["outlier"] += 1

    # ---------------------------------------------------------------- report
    tot = collections.Counter()
    for p in universe:
        tot.update(plant[p])
    by_size = collections.defaultdict(collections.Counter)
    for p in universe:
        d = permits[p]
        b = size_bin(d["flow"])
        by_size[b]["plants"] += 1
        by_size[b]["major"] += d["mm"] == "M"
        for k in ("values", "E90", "D80", "D90", "SNC quarters", "events", "quarters"):
            by_size[b][k] += plant[p][k]
        by_size[b]["plants with E90"] += plant[p]["E90"] > 0
        by_size[b]["plants with D80/D90"] += (plant[p]["D80"] + plant[p]["D90"]) > 0
        by_size[b]["plants with SNC"] += plant[p]["SNC quarters"] > 0

    print(f"DMR rows read: {n_rows:,}; POTW rows in the window: {n_potw_rows:,}")
    print(f"POTW permits in {st} (latest version): {len(potw):,}; with DMR values in the window: {len(universe):,}\n")
    print("## By design flow\n")
    print("| Size | Plants | Major | DMR values | E90 | Plants with E90 | D80+D90 | Plants with D80/D90 | SNC quarters | Plants with SNC | Single events |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for _, b in SIZE_BINS + [(None, "unknown")]:
        s = by_size.get(b)
        if not s:
            continue
        print(f"| {b} | {s['plants']} | {s['major']} | {s['values']:,} | {s['E90']:,} | {s['plants with E90']} | "
              f"{s['D80'] + s['D90']:,} | {s['plants with D80/D90']} | {s['SNC quarters']} | {s['plants with SNC']} | {s['events']} |")
    print(f"\nTotals: E90 {tot['E90']:,}; D80 {tot['D80']:,}; D90 {tot['D90']:,}; "
          f"SNC quarters {tot['SNC quarters']} of {tot['quarters']:,} plant-quarters; single events {tot['events']:,}")
    print(f"Cross-check, the violations file for the same plants and window: E90 {eff['E90']:,}, "
          f"D80 {eff['D80']:,}, D90 {eff['D90']:,}\n")
    print("## Effluent violations (E90) by parameter group\n")
    for g, n in e90_by_group.most_common():
        print(f"- {g}: {n:,}")
    print("\n| Group | " + " | ".join(b for _, b in SIZE_BINS) + " |")
    print("| --- |" + " --- |" * len(SIZE_BINS))
    for g, _ in e90_by_group.most_common():
        cells = [sum(plant[p]["E90:" + g] for p in universe if size_bin(permits[p]["flow"]) == b)
                 for _, b in SIZE_BINS]
        print(f"| {g} | " + " | ".join(f"{c:,}" for c in cells) + " |")
    print("\n  The largest in 'other':", "; ".join(f"{d} {n}" for d, n in other_desc.most_common(10)))
    print("\n## SNC quarters by kind\n")
    for k in ("effluent", "missing DMR", "schedule"):
        print(f"- {k}: {tot['SNC:' + k]}")
    print("\n## Single-event violations by description\n")
    for d, n in events.most_common(12):
        print(f"- {d}: {n:,}")

    print("\n## Values that contradict their own arithmetic\n")
    kinds = collections.Counter(kind for _, kind, *_ in aam)
    print(f"- average above the daily maximum: {kinds['avg>max']:,}; minimum above the maximum: {kinds['min>max']:,} "
          f"(of {len(groups):,} parameter-periods)")
    by_g = collections.Counter((kind, group_of(desc_of.get(key[3], ""))) for key, kind, *_ in aam)
    print("  - by parameter group: " + "; ".join(f"{k} {g} {n}" for (k, g), n in by_g.most_common(12)))
    by_p = collections.Counter(key[0] for key, *_ in aam)
    bs = collections.Counter(size_bin(permits[p]["flow"]) for key, *_ in aam for p in [key[0]])
    print("  - by size: " + "; ".join(f"{b} {bs[b]}" for _, b in SIZE_BINS))
    print(f"  - plants: {len(by_p)}; the most: " + ", ".join(f"{p} {n}" for p, n in by_p.most_common(6)))
    for key, kind, bad, mx in aam[:a.examples]:
        print(f"  - {key[0]} {key[4]} outfall {key[1]} param {key[3]} ({key[5]}): {kind} {bad:g} > {mx:g}")
    fc = collections.Counter(round(f, 4) for _, _, f, *_ in lflags)
    print(f"- loading against concentration x flow x 8.34: {len(ratios):,} pairs compared; "
          f"{len(lflags):,} off by a unit factor ({', '.join(f'x{f:g}: {n}' for f, n in sorted(fc.items()))})")
    if ratios:
        lr = sorted(math.log10(r) for r in ratios)
        within = sum(abs(x) <= math.log10(1.25) for x in lr)
        far = sum(abs(x) > 0.5 for x in lr)
        print(f"  - within 25% of 1: {within:,}; more than 3.16 times off either way: {far:,}; "
              f"median ratio {10 ** statistics.median(lr):.4f}")
        print("  - matches at each factor beside decoys 15% either side (below / at / above):")
        excess = 0
        for f in UNIT_FACTORS:
            lo, at, hi = decoy_counts(ratios, f)
            excess += max(0, at - max(lo, hi))
            print(f"    - x{f:.4g}: {lo} / {at} / {hi}")
        print(f"  - matches beyond the larger decoy, summed over the factors: {excess}")
    for k, r, f, c, q, ld in lflags[:a.examples]:
        print(f"  - {k[0]} {k[4]} outfall {k[1]} param {k[3]}: {ld:g} lb/d vs {c:g} mg/L x {q:g} MGD x 8.34 "
              f"= {c * q * 8.34:.4g}; ratio {r:.4f} (x{f:g})")
    print("\n## Signals that are not contradictions\n")
    print(f"- E90s at the rounding edge, value rounded half-even to the limit's stored decimals "
          f"(an upper bound, since ECHO strips trailing zeros): clears {rounding['clears']:,}, "
          f"tie {rounding['tie']:,}, stands {rounding['stands']:,}")
    print(f"  - with one more decimal than stored: clears {rounding['+1 clears']:,}, "
          f"tie {rounding['+1 tie']:,}, stands {rounding['+1 stands']:,}")
    for k in ("clears", "tie"):
        for ex in round_ex[k]:
            print(f"  - {k}: {ex[0]} {ex[1]} {ex[2]} [{ex[3]}] value {ex[4]} limit {ex[5]} {ex[6]}")
    print("- bacteria values at the top of a Quanti-Tray range (value, qualifier, E90): " +
          "; ".join(f"{v} {q} {e or '-'}: {n}" for (v, q, e), n in sorted(censored.items())))
    print(f"- values at least {OUTLIER_X:g} times their series median: {len(outl):,} "
          f"(of which E90: {sum(1 for *_, d in outl if d[2] == 'E90'):,}); "
          f"apart from Quanti-Tray tops: {sum(1 for _, v, _, _ in outl if f'{v:g}' not in CEILINGS):,}")
    for key, v, med, det in outl[:a.examples]:
        print(f"  - {key[0]} {det[0]} {det[1]} [{key[4]}] {v:g} {key[5]} vs median {med:g}")

    if a.flags:
        with open(a.flags, "w", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["kind", "permit", "outfall", "location", "parameter", "description", "period",
                        "unit_or_code", "value", "against", "all_values"])
            for key, kind, bad, mx in aam:
                w.writerow([kind, key[0], key[1], key[2], key[3], desc_of.get(key[3], ""), key[4], key[5],
                            bad, mx, " ".join(f"{c}={v:g}" for c, v in groups[key])])
            for k, r, fac_, c, q, ld in lflags:
                w.writerow([f"load x{fac_:.4g}", k[0], k[1], k[2], k[3], desc_of.get(k[3], ""), k[4], k[5],
                            ld, round(c * q * 8.34, 6), f"conc={c:g} flow={q:g} ratio={r:.5f}"])
            for key, v, med, det in outl:
                w.writerow(["outlier", key[0], key[1], key[2], key[3], det[1], det[0], f"{key[4]} {key[5]}",
                            v, med, det[2]])

    if a.tsv:
        cols = ["values", "E90", "D80", "D90", "SNC quarters", "SNC:effluent", "SNC:missing DMR",
                "SNC:schedule", "events", "avg>max", "min>max", "load factor", "outlier"] + \
               [f"E90:{g}" for g, _ in GROUPS] + ["E90:other"]
        with open(a.tsv, "w", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["permit", "facility", "city", "major_minor", "design_flow_mgd", "size"] + cols)
            for p in sorted(universe):
                d = permits[p]
                name, city = fac.get(p, (d["name"], ""))
                w.writerow([p, name, city, d["mm"], "" if d["flow"] is None else d["flow"],
                            size_bin(d["flow"])] + [plant[p][c] for c in cols])

    print()
    if fails:
        for x in fails:
            print("control failed:", x)
        print("VOID")
        return 2
    if not universe:
        print("VOID (no plant read)")
        return 2
    n = kinds["avg>max"] + kinds["min>max"]
    print("Controls: all four planted cases flagged, their clean twins not; the DMR files' "
          "E90, D80 and D90 counts equal the violations file's.")
    if n:
        print(f"DIFFERS: {n:,} reported statistics contradict their own definitions "
              f"(an average or minimum above the maximum), at {len(by_p)} of {len(universe)} plants")
        return 1
    print("IDENTICAL: no reported statistic contradicts its own definition")
    return 0


if __name__ == "__main__":
    sys.exit(main())
