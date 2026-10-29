#!/usr/bin/env python3
"""kpitable.py CASE LABEL=KPI.csv...: a Markdown table of performance indices for one weather case.

Rows are the main indices; columns are the report (Appendix 4, Matlab; and for dry
weather Appendix 2, FORTRAN) and then each LABEL=file given, as written by bsm1kpi.py.
Each result cell shows the value and its relative difference from Appendix 4.
"""
import csv, os, sys

VARS = ['EQ', 'IQ', 'SNH_e', 'TN_e', 'TSS_e', 'COD_e', 'SI_e', 'SP_disposal', 'OCI',
        'SNH_e95', 'TN_e95', 'TSS_e95', 'SNH_viol_days', 'TN_viol_days']


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    case = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    ref = {(r['source'][:4], r['var']): r['printed'] for r in csv.DictReader(open(os.path.join(here, 'reference.csv')))
           if r['case'] == case and r['block'] == 'perf'}
    cols = [a.split('=', 1) for a in sys.argv[2:]]
    data = [{r['var']: float(r['value']) for r in csv.DictReader(open(f))} for _, f in cols]
    head = ['index', 'report (Matlab)'] + (['report (FORTRAN)'] if case == 'dry' else []) + [c for c, _ in cols]
    print('| ' + ' | '.join(head) + ' |')
    print('|' + ' --- |' * len(head))
    for v in VARS:
        p = ref.get(('app4', v))
        if p is None:
            continue
        row = [v, p] + ([ref.get(('app2', v), '')] if case == 'dry' else [])
        for d in data:
            x = d.get(v)
            row.append('' if x is None else f'{x:.6g} ({(x - float(p)) / float(p):+.1e})' if float(p) else f'{x:.6g}')
        print('| ' + ' | '.join(row) + ' |')


if __name__ == '__main__':
    main()
