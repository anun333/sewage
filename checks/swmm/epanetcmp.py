#!/usr/bin/env python3
"""epanetcmp.py A.out B.out : EPANET binary outputs are made of 4-byte
fields (ints, float32 and 4-byte-multiple strings), so compare them word by
word and report how many float32 words differ and the largest abs/rel
difference. Verdict IDENTICAL / DIFFERS / VOID."""
import struct, sys
try:
    a = open(sys.argv[1], 'rb').read(); b = open(sys.argv[2], 'rb').read()
except (OSError, IndexError) as e:
    print(e); print('VOID'); sys.exit(2)
if a == b:
    print('IDENTICAL'); sys.exit(0)
if len(a) != len(b) or len(a) % 4:
    print('sizes %d %d' % (len(a), len(b))); print('DIFFERS'); sys.exit(1)
n = len(a) // 4
fa = struct.unpack('<%df' % n, a); fb = struct.unpack('<%df' % n, b)
ua = struct.unpack('<%dI' % n, a); ub = struct.unpack('<%dI' % n, b)
nd = 0; mabs = 0.0; mrel = 0.0; where = None
for i in range(n):
    if ua[i] != ub[i]:
        nd += 1
        d = abs(fa[i] - fb[i]); den = max(abs(fa[i]), abs(fb[i]))
        r = d / den if den else 0.0
        if r > mrel: mrel = r; where = (i * 4, fa[i], fb[i])
        mabs = max(mabs, d)
print('%d of %d words differ; max abs %.3g; max rel %.3g at byte %s (%r vs %r)' % ((nd, n, mabs, mrel) + where))
print('DIFFERS'); sys.exit(1)
