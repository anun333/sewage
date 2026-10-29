#!/usr/bin/env python3
"""bsm1cmp.py: compare BSM1 results with the reference report and with each other.

  bsm1cmp.py ref REFERENCE.csv RESULT.csv [--case C] [--rcase RC] [--source S] [--common] [--quiet]
      Every reference row of case C (default ss) whose source starts with S
      (default app4) against RESULT: AGREES when the result rounds to the
      printed value (|x - printed| <= half a unit in its last printed digit;
      an integer without a decimal point does not count trailing zeros),
      else DIFFERS with the difference, relative and in printed units.
  bsm1cmp.py pair A.csv B.csv [--case C] [--rtol R] [--common] [--quiet]
      Two results at full precision: abs and rel difference per variable and
      the largest per block. Equal means |a - b| <= R*max(|a|,|b|) (R = 0:
      bit for bit).

  bsm1cmp.py series A.csv B.csv [--from T] [--rtol R]
      Two 15-minute series (run_*.py dyn) column by column from day T: the
      largest difference relative to the column's largest value.

RESULT files have the columns case, block, var, value (value at full
precision). For case ss, derived rows (TSS, sludge ages, thickening and
thinning factors) are computed from the states when the file lacks them,
with the formulas of the report's Appendix 4.

Verdicts as in crnumerics: IDENTICAL (exit 0: every row agrees or is equal),
DIFFERS (exit 1), VOID (exit 2: a needed row is missing or not a number, or
nothing was compared). --common restricts the comparison to rows both files
have and lists the rest, instead of VOID (WaterTAP has no settler layers).
"""
import csv, math, sys
from decimal import Decimal

V = [1000.0, 1000.0, 1333.0, 1333.0, 1333.0]   # reactor volumes, m3
A, Z, QE, QW = 1500.0, 0.4, 18061.0, 385.0     # settler area and layer height, effluent and wastage flows
XCOD = ('XS', 'XP', 'XI', 'XBH', 'XBA')


def read(path, case=None, source=None):
    out = {}
    with open(path, newline='') as f:
        for r in csv.DictReader(f):
            if case and r['case'] != case:
                continue
            if source and not r['source'].startswith(source):
                continue
            out[(r['case'], r['block'], r['var'])] = r
    return out


def recase(res, case):
    """Treat a result's rows of another case name (e.g. ss100, ss_kla5) as case."""
    return {(case, k[1], k[2]): dict(r, case=case) for k, r in res.items()}


def num(s):
    try:
        x = float(s)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def derive(res, case='ss'):
    """Fill derived rows from states, where the result lacks them."""
    g = lambda b, v: num(res.get((case, b, v), {}).get('value'))
    put = lambda b, v, x: res.setdefault((case, b, v), {'case': case, 'block': b, 'var': v, 'value': repr(x), 'derived': 1})
    blocks = ['input_as'] + [f'reactor{k}' for k in range(1, 6)] + ['underflow', 'effluent']
    for b in blocks:
        xs = [g(b, v) for v in XCOD]
        if None not in xs:
            put(b, 'TSS', 0.75 * sum(xs))
    try:
        xr = [sum(g(f'reactor{k}', v) for v in XCOD) for k in range(1, 6)]
        xe, xu = (sum(g(b, v) for v in XCOD) for b in ('effluent', 'underflow'))
        put('derived', 'trad_sludge_age', sum(v * x for v, x in zip(V, xr)) / (QE * xe + QW * xu))
        tss5 = g('reactor5', 'TSS') or 0.75 * xr[4]
        put('derived', 'thickening', g('underflow', 'TSS') / tss5)
        put('derived', 'thinning', g('effluent', 'TSS') / tss5)
        bio = lambda b: g(b, 'XBH') + g(b, 'XBA')
        frac = bio('reactor5') / tss5
        layers = sum(g('settler', f'TSS{j}') for j in range(1, 11))
        put('derived', 'spec_sludge_age',
            (sum(v * bio(f'reactor{k}') for k, v in zip(range(1, 6), V)) + Z * A * frac * layers)
            / (QE * bio('effluent') + QW * bio('underflow')))
    except (TypeError, ZeroDivisionError):
        pass
    return res


def ulp_of(printed):
    """One unit in the last printed digit. An integer printed without a decimal point
    does not count its trailing zeros (Appendix 2's 52100 is three digits; 6394. is four)."""
    d = Decimal(printed)
    e = d.as_tuple().exponent
    if e == 0 and '.' not in printed and printed.strip('-') != '0':
        e = len(printed) - len(printed.rstrip('0'))
    return float(Decimal(1).scaleb(e))


def cmd_ref(argv):
    ref, resf = argv[0], argv[1]
    case = opt(argv, '--case', 'ss'); src = opt(argv, '--source', 'app4'); quiet = '--quiet' in argv
    R = read(ref, case, src)
    res = recase(read(resf, opt(argv, '--rcase', case)), case)
    if case == 'ss':
        derive(res, case)
    if not R:
        print(f'VOID: no reference rows for case {case}, source {src}'); return 2
    missing, agree, differ = [], 0, []
    for k, r in R.items():
        x = num(res.get(k, {}).get('value'))
        if x is None:
            missing.append(k); continue
        p = float(r['printed']); u = ulp_of(r['printed'])
        d = x - p
        ok = abs(d) <= 0.5 * u * (1 + 1e-9) + 1e-300
        tag = ' (derived here)' if res[k].get('derived') else ''
        if ok:
            agree += 1
            if not quiet:
                print(f'AGREES   {k[1]:10s} {k[2]:16s} printed {r["printed"]:>12s}  result {x:.10g}{tag}')
        else:
            rel = d / p if p else float('inf')
            differ.append(k)
            print(f'DIFFERS  {k[1]:10s} {k[2]:16s} printed {r["printed"]:>12s}  result {x:.10g}  '
                  f'diff {d:+.4g} (rel {rel:+.2e}, {d / u:+.1f} printed units){tag}')
    common = '--common' in argv
    if common and missing:
        print(f'not in the result, not compared: {len(missing)} rows ({", ".join(sorted({k[1] for k in missing}))})')
    else:
        for k in missing:
            print(f'MISSING  {k[1]:10s} {k[2]}')
    n = agree + len(differ)
    tail = f'{resf} vs {ref} [{case}, {src}]: {agree} of {n} agree'
    if (missing and not common) or n == 0:
        print(f'VOID: {tail}; {len(missing)} reference rows missing from the result'); return 2
    if differ:
        print(f'DIFFERS: {tail}, {len(differ)} differ'); return 1
    print(f'IDENTICAL: {tail}'); return 0


def cmd_pair(argv):
    fa, fb = argv[0], argv[1]
    case = opt(argv, '--case', 'ss'); rtol = float(opt(argv, '--rtol', '0')); quiet = '--quiet' in argv
    ca, cb = opt(argv, '--cases', f'{case},{case}').split(',')
    a, b = recase(read(fa, ca), case), recase(read(fb, cb), case)
    if case == 'ss':
        derive(a, case); derive(b, case)
    keys = sorted(set(a) | set(b))
    only = [k for k in keys if (k in a) != (k in b)]
    common = [k for k in keys if k in a and k in b]
    if only and '--common' not in argv:
        for k in only[:20]:
            print(f'MISSING  {k[1]} {k[2]} only in {fa if k in a else fb}')
        print(f'VOID: {len(only)} rows in one file only (use --common to compare the rest)'); return 2
    worst, ndiff, bad = {}, 0, []
    for k in common:
        x, y = num(a[k]['value']), num(b[k]['value'])
        if x is None or y is None:
            bad.append(k); continue
        d = abs(x - y); s = max(abs(x), abs(y))
        rel = d / s if s else 0.0
        eq = d <= rtol * s
        ndiff += not eq
        w = worst.get(k[1])
        if w is None or rel > w[1]:
            worst[k[1]] = (d, rel, k[2], x, y)
        if not quiet and not eq:
            print(f'  {k[1]:10s} {k[2]:16s} {x:.12g}  {y:.12g}  abs {d:.3e}  rel {rel:.3e}')
    print(f'largest relative difference per block ({fa} vs {fb}):')
    for blk, (d, rel, v, x, y) in sorted(worst.items(), key=lambda t: -t[1][1]):
        print(f'  {blk:10s} {v:16s} abs {d:.3e}  rel {rel:.3e}  ({x:.10g} vs {y:.10g})')
    if only:
        print(f'  ({len(only)} rows in one file only, not compared: '
              f'{", ".join(sorted({k[1] for k in only}))})')
    if bad or not common:
        print(f'VOID: {len(bad)} rows not a number, {len(common)} compared'); return 2
    tol = 'bit for bit' if rtol == 0 else f'rtol {rtol:g}'
    if ndiff:
        print(f'DIFFERS: {ndiff} of {len(common)} rows differ ({tol})'); return 1
    print(f'IDENTICAL: {len(common)} rows equal ({tol})'); return 0


def cmd_series(argv):
    """Two 15-minute series column by column, from --from T (default 0): the largest
    difference relative to the column's largest magnitude."""
    fa, fb = argv[0], argv[1]
    t0 = float(opt(argv, '--from', '0')); rtol = float(opt(argv, '--rtol', '0'))
    def load(f):
        with open(f, newline='') as h:
            return {round(float(r['t']) * 96): r for r in csv.DictReader(h) if float(r['t']) >= t0 - 1e-9}
    a, b = load(fa), load(fb)
    ks = sorted(set(a) & set(b))
    cols = [c for c in (next(iter(a.values())) if a else {}) if c != 't' and b and c in next(iter(b.values()))]
    if not ks or not cols or len(ks) != len(a) or len(ks) != len(b):
        print(f'VOID: the series do not share their sample times ({len(a)}, {len(b)}, {len(ks)} common)'); return 2
    out, ndiff = [], 0
    for c in cols:
        xa = [num(a[k][c]) for k in ks]; xb = [num(b[k][c]) for k in ks]
        if None in xa or None in xb:
            print(f'VOID: column {c} is not a number'); return 2
        scale = max(max(abs(x) for x in xa), max(abs(x) for x in xb))
        d = max(abs(x - y) for x, y in zip(xa, xb))
        rel = d / scale if scale else 0.0
        ndiff += rel > rtol
        out.append((rel, c, d))
    print(f'largest difference per column relative to its largest value, t >= {t0:g} ({fa} vs {fb}):')
    for rel, c, d in sorted(out, reverse=True)[:12]:
        print(f'  {c:8s} abs {d:.3e}  rel {rel:.3e}')
    tol = 'bit for bit' if rtol == 0 else f'rtol {rtol:g}'
    if ndiff:
        print(f'DIFFERS: {ndiff} of {len(cols)} columns differ ({tol}) over {len(ks)} samples'); return 1
    print(f'IDENTICAL: {len(cols)} columns over {len(ks)} samples ({tol})'); return 0


def opt(argv, name, default):
    return argv[argv.index(name) + 1] if name in argv else default


if __name__ == '__main__':
    if len(sys.argv) < 4 or sys.argv[1] not in ('ref', 'pair', 'series'):
        print(__doc__); sys.exit(2)
    sys.exit({'ref': cmd_ref, 'pair': cmd_pair, 'series': cmd_series}[sys.argv[1]](sys.argv[2:]))
