#!/usr/bin/env python3
"""dmr_calc.py: does a spreadsheet get DMR rounding ties and geometric-mean limits right?

The two checks beside this file measure Python's binary64 arithmetic.
Small plants keep their DMR arithmetic in spreadsheets, so this puts the same
cases into a LibreOffice Calc sheet and reads back what Calc computes:

  rounding  monthly averages of one-decimal lab values whose exact mean lands on
            a rounding tie (x.x5). Each row is checked with =ROUND(AVERAGE(...);1),
            against the exact mean rounded half up (Calc's ROUND rounds half away
            from zero) and half even (EPA's worked examples).
  geomean   sets of integer counts whose exact geometric mean equals a bacteria
            limit (dmr_geomean.py's sets). Each row is checked with =GEOMEAN(...),
            =GEOMEAN(...)>limit and =GEOMEAN(...)=limit. Exactly, it does not
            exceed the limit and is equal to it.

The sheet is written as flat ODF (.fods) with formulas and no cached results.
`soffice --headless` loads it, computes it and saves it as CSV. A throwaway
profile is used, so the user's own LibreOffice settings are neither read nor
changed.

Verdicts as in crnumerics: IDENTICAL (exit 0) when every row gives the exact
answer, DIFFERS (exit 1), VOID (exit 2: Calc did not run or a row is missing).
The control: rows whose exact mean is not a tie must all agree, and a planted
wrong expectation (--plant) must make the check DIFFER.

  python3 -I dmr_calc.py [--ties N] [--seed S] [--soffice PATH] [--plant]
Standard library only, plus a LibreOffice install.
"""
import argparse
import csv
import itertools
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from fractions import Fraction
from xml.sax.saxutils import escape

STEP = Decimal("0.1")
LIMITS = [126, 200, 941, 1000]


def exact_mean(xs):
    return sum(Fraction(str(x)) for x in xs) / len(xs)


def rounded(mean, rule):
    return (Decimal(mean.numerator) / Decimal(mean.denominator)).quantize(STEP, rule)


def is_tie(mean):
    h = mean * 100
    return h.denominator == 1 and h % 10 == 5


def rounding_cases(n_ties, seed):
    """n_ties tie rows and as many non-tie rows (the control), for 4, 10 and 30 samples."""
    rng = random.Random(seed)
    rows = []
    for n in (4, 10, 30):
        ties = others = 0
        while ties < n_ties or others < n_ties:
            xs = [rng.randint(10, 400) / 10 for _ in range(n)]
            m = exact_mean(xs)
            if is_tie(m) and ties < n_ties:
                ties += 1
                rows.append(("tie", xs, m))
            elif not is_tie(m) and others < n_ties:
                others += 1
                rows.append(("other", xs, m))
    return rows


def sets_on_limit(limit, cap=40):
    """As in dmr_geomean.py: two and three counts whose product is limit**2 or limit**3."""
    square, cube = limit ** 2, limit ** 3
    divisors = [d for d in range(1, square + 1) if square % d == 0]
    for a in divisors:
        yield [a, square // a]
    for a, b in itertools.product(divisors[:cap], repeat=2):
        if cube % (a * b) == 0:
            yield [a, b, cube // (a * b)]


def col(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def fods(rows):
    """rows: lists of cells, each ('v', number), ('e', None) or ('f', formula without '=')."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
           'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
           'xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" '
           'office:version="1.2" office:mimetype="application/vnd.oasis.opendocument.spreadsheet">',
           '<office:body><office:spreadsheet><table:table table:name="t">']
    for r in rows:
        out.append('<table:table-row>')
        for kind, x in r:
            if kind == 'v':
                out.append(f'<table:table-cell office:value-type="float" office:value="{x!r}"/>')
            elif kind == 'e':
                out.append('<table:table-cell/>')
            else:
                out.append(f'<table:table-cell table:formula="of:={escape(x)}"/>')
        out.append('</table:table-row>')
    out.append('</table:table></office:spreadsheet></office:body></office:document>')
    return "\n".join(out)


def calc(rows, soffice, work):
    """Have Calc compute the sheet; return its CSV rows (unformatted values)."""
    src = os.path.join(work, "sheet.fods")
    with open(src, "w", encoding="utf-8") as f:
        f.write(fods(rows))
    profile = "file://" + os.path.join(work, "profile")
    # 44 comma, 34 quote, 76 UTF-8, 1 first line; token 9 false: values, not "as shown"
    flt = "csv:Text - txt - csv (StarCalc):44,34,76,1,,0,false,false,false,false,false"
    r = subprocess.run([soffice, f"-env:UserInstallation={profile}", "--headless",
                        "--convert-to", flt, "--outdir", work, src],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
    out = os.path.join(work, "sheet.csv")
    if r.returncode != 0 or not os.path.exists(out):
        print(r.stdout.decode(errors="replace")[-2000:])
        return None
    with open(out, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ties", type=int, default=500, help="tie rows per sample size")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--soffice", default=shutil.which("soffice") or "soffice")
    ap.add_argument("--plant", action="store_true", help="control: plant one wrong expectation")
    a = ap.parse_args()

    rcases = rounding_cases(a.ties, a.seed)
    gcases = [(limit, xs) for limit in LIMITS for xs in sets_on_limit(limit)]
    width = 30
    rows = []
    for _, xs, _ in rcases:
        r = len(rows) + 1
        cells = [('v', x) for x in xs] + [('e', None)] * (width - len(xs))
        cells += [('f', f"ROUND(AVERAGE([.A{r}:.{col(len(xs) - 1)}{r}]);1)")]
        rows.append(cells)
    g0 = len(rows)
    for limit, xs in gcases:
        r = len(rows) + 1
        ref = f"[.A{r}:.{col(len(xs) - 1)}{r}]"
        cells = [('v', x) for x in xs] + [('e', None)] * (width - len(xs))
        cells += [('f', f"GEOMEAN({ref})"), ('f', f"GEOMEAN({ref})>{limit}"),
                  ('f', f"GEOMEAN({ref})={limit}"), ('f', f"GEOMEAN({ref})-{limit}"),
                  ('f', f"ORG.LIBREOFFICE.RAWSUBTRACT(GEOMEAN({ref});{limit})")]
        rows.append(cells)

    with tempfile.TemporaryDirectory() as work:
        out = calc(rows, a.soffice, work)
        version = subprocess.run([a.soffice, "--version"], stdout=subprocess.PIPE).stdout.decode().strip()
    if out is None or len(out) != len(rows):
        print(f"VOID: Calc returned {0 if out is None else len(out)} rows, expected {len(rows)}")
        return 2
    print(f"# {version}")

    # rounding
    stats = {"tie": [0, 0, 0], "other": [0, 0, 0]}   # rows, != half-up, != half-even
    example = None
    for i, (kind, xs, m) in enumerate(rcases):
        got = Decimal(out[i][width])
        up, even = rounded(m, ROUND_HALF_UP), rounded(m, ROUND_HALF_EVEN)
        if a.plant and i == 0:
            up = up + STEP
        s = stats[kind]
        s[0] += 1
        s[1] += got != up
        s[2] += got != even
        if kind == "tie" and got != even and example is None:
            example = (xs, m, got, even)
    for kind, (n, d_up, d_even) in stats.items():
        print(f"rounding, {kind:5}: {n} rows; ROUND(AVERAGE()) differs from exact half-up in {d_up}, "
              f"from exact half-even in {d_even}")
    if example:
        xs, m, got, even = example
        print(f"  e.g. {xs} (exact mean {float(m)!r}): Calc {got}, half-even {even}")

    # geometric means
    by = {}
    for j, (limit, xs) in enumerate(gcases):
        row = out[g0 + j]
        gt, eq = row[width + 1].upper(), row[width + 2].upper()
        diff, raw = float(row[width + 3]), float(row[width + 4])
        b = by.setdefault(limit, [0, 0, 0, 0, 0, 0, None])
        b[0] += 1
        b[1] += gt == "TRUE"
        b[2] += eq == "TRUE"
        b[3] += diff != 0.0
        b[4] += raw > 0
        b[5] += raw < 0
        if raw != 0.0 and b[6] is None:
            b[6] = (xs, raw)
    for limit, (n, gt, eq, nz, rpos, rneg, ex) in by.items():
        print(f"geomean, limit {limit}: {n} sets; GEOMEAN()>limit TRUE in {gt}, =limit TRUE in {eq}, "
              f"GEOMEAN()-limit nonzero in {nz}; RAWSUBTRACT(GEOMEAN(),limit) above 0 in {rpos}, below 0 in {rneg}"
              + (f"; e.g. {ex[0]}: {ex[1]!r}" if ex else ""))

    other_bad = stats["other"][1]
    ties_bad = stats["tie"][1]
    geo_bad = sum(b[1] for b in by.values()) + sum(b[0] - b[2] for b in by.values())
    if a.plant:
        if stats["other"][1] + ties_bad == 0:
            print("VOID: the planted expectation was not caught")
            return 2
        print("DIFFERS: the planted wrong expectation (row 1) was caught, as it must be")
        return 1
    if other_bad and not a.plant:
        print("VOID: the control (non-tie rows) disagrees with exact rounding")
        return 2
    if ties_bad or geo_bad or a.plant:
        print(f"DIFFERS: {ties_bad} rounding ties against half-up, {geo_bad} geometric-mean verdicts wrong")
        return 1
    print("IDENTICAL: every ROUND agrees with exact half-up, and every GEOMEAN equals its limit "
          "(half-even, EPA's rule, is reported above; Calc has no half-even ROUND)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
