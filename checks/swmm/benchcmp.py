#!/usr/bin/env python3
"""benchcmp.py DIR_A DIR_B : compare every <name>.out / <name>.rpt found
under DIR_A with the file of the same name under DIR_B (nrtest benchmark
trees or swmmrun.py run trees). One line per model, then a verdict."""
import os, sys
sys.dont_write_bytecode = True  # no __pycache__ beside the scripts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swmmcmp as C
def index(root):
    d = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith('.out'):
                d[f[:-4]] = os.path.join(dp, f[:-4])
    return d
A, B = index(sys.argv[1]), index(sys.argv[2])
n_diff = 0; void = False
for name in sorted(set(A) & set(B)):
    try:
        o = C.compare_out(A[name] + '.out', B[name] + '.out')
        r = C.compare_rpt(A[name] + '.rpt', B[name] + '.rpt')
    except Exception as e:
        print('%-22s VOID (%s)' % (name, e)); void = True; continue
    if o['bytes_identical'] and r['identical_masked']:
        print('%-22s IDENTICAL' % name); continue
    n_diff += 1
    s = 'out:same' if o['bytes_identical'] else 'out:%s/%s vals max_abs=%.3g max_rel=%.3g nperiods=%s nrtest=%s' % (
        o.get('values_differ'), o.get('values_total'), o.get('max_abs', 0), o.get('max_rel', 0),
        o.get('nperiods'), 'PASS' if o.get('nrtest_allclose_pass') else 'FAIL(%s)' % o.get('nrtest_failing_elements'))
    s += ' rpt:%s' % ('same' if r['identical_masked'] else '%d lines nrtest=%s' % (
        r['differing_lines'], 'PASS' if r['nrtest_report_pass'] else 'FAIL'))
    print('%-22s DIFFERS %s' % (name, s))
print('only in one tree:', sorted(set(A) ^ set(B)))
print('VOID' if void else ('DIFFERS' if n_diff else 'IDENTICAL'))
