#!/usr/bin/env python3
"""Does averaging lab results in binary floating point flip a DMR's rounding?

A DMR reports averages of lab values that were written down in decimal (12.3 mg/L). When
the exact decimal average lands on a rounding tie (21.95, reported to one decimal), the
reported value depends on how the average was computed:

* exact decimal arithmetic, then round half up: the answer the rule intends (22.0);
* a binary64 mean, then round half up on the binary value: 21.95 is stored as
  21.94999..., so it reports 21.9. repr() still prints "21.95", so nobody sees why;
* a binary64 mean shown at 15 significant digits first (as spreadsheets display it),
  then rounded: recovers 21.95, so it reports 22.0.

Which rounding rule applies is the permit's to say, and they differ: EPA's example permit
language rounds half to even (1.05 -> 1.0, 1.15 -> 1.2), Pennsylvania's DMR instructions
round half up. `--rule` picks one; this measures what binary arithmetic does to it. EPA's
two worked examples are checked first: binary64 holds 1.05 a little above the tie and
1.15 a little below, so rounding the binary value gets 1.15 wrong under either rule, and
1.05 wrong as well under EPA's half-even.

Verdicts, as crnumerics' checks print them: IDENTICAL (exit 0) when the method under test
agrees with exact decimal on every tie, DIFFERS (exit 1) when it does not, VOID (exit 2)
when the control fails or no ties were sampled.

    python3 checks/dmr_rounding.py            # the binary-value method, half up, n = 4 and 30
    python3 checks/dmr_rounding.py --rule half_even
    python3 checks/dmr_rounding.py --method sig15
"""
import argparse
import random
import sys
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from fractions import Fraction

STEP = Decimal("0.1")
RULES = {"half_up": ROUND_HALF_UP, "half_even": ROUND_HALF_EVEN}
RULE = ROUND_HALF_UP

# EPA's worked examples (2020 DMR webinar, round half to even), and the same values half up
WORKED = [("half_even", "1.05", "1.0"), ("half_even", "1.15", "1.2"),
          ("half_up", "1.05", "1.1"), ("half_up", "1.15", "1.2")]


def naive_sum(xs):
    """Left to right, as hand-written code adds. Python 3.12's sum() compensates, so the
    float methods use this to give the same counts on every Python version."""
    total = 0.0
    for x in xs:
        total += x
    return total


def exact_round(xs):
    mean = sum(Fraction(str(x)) for x in xs) / len(xs)
    return (Decimal(mean.numerator) / Decimal(mean.denominator)).quantize(STEP, RULE)


METHODS = {
    # round the binary64 value itself (what most hand-written code does)
    "binary": lambda xs: Decimal(naive_sum(xs) / len(xs)).quantize(STEP, RULE),
    # show at 15 significant digits first, as a spreadsheet does, then round
    "sig15": lambda xs: Decimal(format(naive_sum(xs) / len(xs), ".15g")).quantize(STEP, RULE),
    # the control: exact decimal, which must never differ from itself
    "decimal": exact_round,
}


def is_tie(xs):
    mean = sum(Fraction(str(x)) for x in xs) / len(xs)
    hundredths = mean * 100
    return hundredths.denominator == 1 and hundredths % 10 == 5


def run(method, n, trials, rng):
    ties = flips = 0
    example = None
    for _ in range(trials):
        xs = [rng.randint(10, 400) / 10 for _ in range(n)]  # 1.0 to 40.0 mg/L, one decimal
        if not is_tie(xs):
            continue
        ties += 1
        if METHODS[method](xs) != exact_round(xs):
            flips += 1
            example = example or (xs, repr(naive_sum(xs) / n), exact_round(xs), METHODS[method](xs))
    return ties, flips, example


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--method", choices=sorted(METHODS), default="binary")
    ap.add_argument("--rule", choices=sorted(RULES), default="half_up")
    ap.add_argument("--trials", type=int, default=200_000)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    global RULE
    RULE = RULES[args.rule]
    for rule, value, want in WORKED:
        if rule != args.rule:
            continue
        got = METHODS[args.method]([float(value)])
        mark = "ok" if str(got) == want else "WRONG"
        print(f"worked example {value} -> {want} ({rule}): method gives {got}  {mark}")

    rng = random.Random(args.seed)
    _, control_flips, _ = run("decimal", 4, 20_000, rng)
    if control_flips:
        print("VOID: the exact-decimal control disagreed with itself")
        return 2

    any_ties = any_flips = False
    for n in (4, 30):  # a week of four samples; a month of daily samples
        ties, flips, example = run(args.method, n, args.trials, rng)
        any_ties |= ties > 0
        any_flips |= flips > 0
        share = f"{flips / ties:.0%}" if ties else "n/a"
        print(f"n={n:2d}  ties {ties:6d}/{args.trials}  rounded differently {flips:6d} ({share})")
        if example:
            xs, shown, want, got = example
            print(f"      e.g. mean shows as {shown}, exact rounds to {want}, method gives {got}")
    if not any_ties:
        print("VOID: no ties sampled")
        return 2
    print("DIFFERS" if any_flips else "IDENTICAL",
          f"(method {args.method}, rule {args.rule}, against exact decimal)")
    return 1 if any_flips else 0


if __name__ == "__main__":
    sys.exit(main())
