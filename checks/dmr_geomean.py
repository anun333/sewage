#!/usr/bin/env python3
"""Does a floating-point geometric mean land on the wrong side of a bacteria limit?

Bacteria limits (fecal coliform 200/100 mL, E. coli 126 or 941) are judged on a
geometric mean, which Tennessee defines as "the n th root of the product of the individual
values ... values of zero shall be considered to be one" (Tenn. Comp. R. & Regs.
0400-40-05-.02(35)). Code usually computes it as exp(mean(log(x))). When the exact mean
equals the limit, say [4, 10000] against 200, that formula can land a few ulps above
the limit, and a plain `> limit` comparison then reports a violation that is not there.
Which side it lands on depends on the C library's log and exp, so two machines can
disagree.

The exact answer needs no floating point: the counts are integers, so their product is
exact, and whether the n-th root exceeds L is whether the product exceeds L**n.

This takes every set of two or three integer counts whose exact geometric mean is the
limit (sets of three are capped) and counts how often exp(mean(log)) falls above, below
or on it. Verdicts as in crnumerics: IDENTICAL (exit 0) when the float formula is exactly
on the limit every time, DIFFERS (exit 1) when it is not, VOID (exit 2) when the exact
control fails.

    python3 checks/dmr_geomean.py
    python3 checks/dmr_geomean.py --limits 200 126
"""
import argparse
import itertools
import math
import platform
import sys


def float_geomean(xs):
    # the logs are added left to right, as hand-written code does: Python 3.12's sum()
    # compensates, which changed these counts between Python versions
    total = 0.0
    for x in xs:
        total += math.log(x)
    return math.exp(total / len(xs))


def exceeds_exactly(xs, limit):
    """Whether the geometric mean of integer counts exceeds `limit`, with no rounding."""
    return math.prod(xs) > limit ** len(xs)


def sets_on_limit(limit, cap=40):
    square, cube = limit ** 2, limit ** 3
    divisors = [d for d in range(1, square + 1) if square % d == 0]
    for a in divisors:
        yield [a, square // a]
    for a, b in itertools.product(divisors[:cap], repeat=2):
        if cube % (a * b) == 0:
            yield [a, b, cube // (a * b)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--limits", type=int, nargs="+", default=[126, 200, 941, 1000])
    args = ap.parse_args()

    print(f"libm: {platform.libc_ver()} on {platform.machine()}, Python {platform.python_version()}")
    any_off = False
    for limit in args.limits:
        above = below = on = 0
        example = None
        for xs in sets_on_limit(limit):
            if exceeds_exactly(xs, limit):
                print(f"VOID: the exact control says {xs} exceeds {limit}")
                return 2
            g = float_geomean(xs)
            if g > limit:
                above += 1
                example = example or (xs, repr(g))
            elif g < limit:
                below += 1
            else:
                on += 1
        any_off |= above + below > 0
        line = f"limit {limit:5d}: sets {above + below + on:5d}, float above {above:4d}, below {below:4d}, on {on:4d}"
        if example:
            line += f"; e.g. {example[0]} gives {example[1]}, a false exceedance under '> {limit}'"
        print(line)
    print("DIFFERS" if any_off else "IDENTICAL", "(exp(mean(log)) against the exact geometric mean)")
    return 1 if any_off else 0


if __name__ == "__main__":
    sys.exit(main())
