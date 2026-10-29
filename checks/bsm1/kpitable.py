#!/usr/bin/env python3
"""kpitable.py CASE [--alt] LABEL=KPI.csv...: a Markdown table of performance indices for one weather case.

Rows are the main indices; columns are the report (Appendix 4, Matlab; and for dry
weather Appendix 2, FORTRAN) and then each LABEL=file given, as written by bsm1kpi.py.
Each result cell shows the value and its relative difference from Appendix 4.

A closed-loop CASE (cl_dry, cl_rain, cl_storm) takes files written by bsm1clkpi.py
and compares with Appendix 5: the controller indices first, then the plant's. With
--alt it shows the other readings of the controller indices instead: from the
sensor signal rather than the true concentration, and the std of the manipulated
variable itself rather than of its changes, each against the report's figure.
"""
import csv, os, sys

VARS = ['EQ', 'IQ', 'SNH_e', 'TN_e', 'TSS_e', 'COD_e', 'SI_e', 'SP_disposal', 'OCI',
        'SNH_e95', 'TN_e95', 'TSS_e95', 'SNH_viol_days', 'TN_viol_days']
VARS_CL = ['SO5_IAE', 'SO5_ISE', 'SO5_err_max', 'SO5_err_std', 'KLa5_mean', 'KLa5_dstd',
           'SNO2_IAE', 'SNO2_ISE', 'SNO2_err_max', 'SNO2_err_std', 'Qintr_mean', 'Qintr_dstd',
           'EQ', 'SNH_e', 'TN_e', 'TSS_e', 'SP_disposal', 'AE', 'PE', 'OCI',
           'SNH_e95', 'TN_e95', 'SNH_viol_days', 'TN_viol_days']
# --alt: (report's variable, the result's variable, row label)
ALT = [(f'{cv}_{k}', f'{cv}_meas_{k}', f'{cv}_{k}, sensor signal') for cv in ('SO5', 'SNO2')
       for k in ('IAE', 'ISE', 'err_max', 'err_std')] + \
      [(f'{mv}_dstd', f'{mv}_std', f'{mv}: std of u, not of du') for mv in ('KLa5', 'Qintr')]


def main():
    args = [a for a in sys.argv[1:] if a != '--alt']
    alt = '--alt' in sys.argv
    if len(args) < 2:
        print(__doc__); sys.exit(2)
    case = args[0]
    cl = case.startswith('cl_')
    app = 'app5' if cl else 'app4'
    here = os.path.dirname(os.path.abspath(__file__))
    ref = {(r['source'][:4], r['var']): r['printed'] for r in csv.DictReader(open(os.path.join(here, 'reference.csv')))
           if r['case'] == case and r['block'] in ('perf', 'ctrl')}
    cols = [a.split('=', 1) for a in args[1:]]
    data = [{r['var']: float(r['value']) for r in csv.DictReader(open(f))} for _, f in cols]
    head = ['index', 'report (Matlab)'] + (['report (FORTRAN)'] if case == 'dry' else []) + [c for c, _ in cols]
    print('| ' + ' | '.join(head) + ' |')
    print('|' + ' --- |' * len(head))
    rows = ALT if alt else [(v, v, v) for v in (VARS_CL if cl else VARS)]
    for v, rv, label in rows:
        p = ref.get((app, v))
        if p is None:
            continue
        row = [label, p] + ([ref.get(('app2', v), '')] if case == 'dry' else [])
        for d in data:
            x = d.get(rv)
            row.append('' if x is None else f'{x:.6g} ({(x - float(p)) / float(p):+.1e})' if float(p) else f'{x:.6g}')
        print('| ' + ' | '.join(row) + ' |')


if __name__ == '__main__':
    main()
