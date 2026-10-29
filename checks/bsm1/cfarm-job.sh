#!/bin/sh
# cfarm-job.sh [JOBS]: run the BSM1 cross-check on one host, at most $NCORES single-threaded processes at once.
#
# Expects, in the current directory (the work folder):
#   env/qsd, env/bsm2, env/wt   Python environments (setup-envs.sh): QSDsan+EXPOsan, bsm2-python, WaterTAP
#   idaes/                      IDAES solvers (IDAES_DATA), for WaterTAP
#   inputs/Inf_{dry,rain,strm}_2006.txt   the IWA influent files
#   run_qsdsan.py run_bsm2python.py run_watertap.py bsm1kpi.py job1.sh
# Writes results/ (steady states, 15-minute series, performance indices) and logs/.
# JOBS (default: all) is a file of "name<TAB>command" lines; a name whose log ends in "ok" is skipped,
# so the script can be rerun after a failure. Every process runs at nice 19 with one thread; a run
# notice is posted for the whole job and removed on exit; /tmp/$USER-PLEASE-STOP stops new processes.
set -eu
NCORES=${NCORES:-16}
NOTICE=${NOTICE:-$HOME/bin/notice}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1
export MPLCONFIGDIR=$PWD/cache/mpl XDG_CACHE_HOME=$PWD/cache NUMBA_CACHE_DIR=$PWD/cache/numba IDAES_DATA=$PWD/idaes
mkdir -p results logs cache
$NOTICE start sewage-bsm1 --job "BSM1 cross-check: QSDsan, WaterTAP, bsm2-python ($NCORES single-threaded runs)" \
    --cores "$NCORES" --mem 16 --hours 3 --nice 19 \
    --intent "open-source wastewater model reproducibility study (sewage project)"
trap '$NOTICE end sewage-bsm1' EXIT
trap 'exit 1' INT TERM

J=${1:-}
if [ -z "$J" ]; then
  J=logs/jobs.txt; : > $J
  printf 'ss_qsdsan\tenv/qsd/bin/python -I run_qsdsan.py ss results/ss_qsdsan.csv 1000 1e-8\n' >> $J
  printf 'ss_bsm2python\tenv/bsm2/bin/python -I run_bsm2python.py ss results/ss_bsm2python.csv 1000\n' >> $J
  printf 'ss_watertap\tenv/wt/bin/python -I run_watertap.py results/ss_watertap.csv\n' >> $J
  printf 'ss_qsdsan_bsm1coef\tenv/qsd/bin/python -I run_qsdsan.py ss results/ss_qsdsan_bsm1coef.csv 1000 1e-8 bsm1\n' >> $J
  for w in dry rain storm; do
    for i in cubic linear linear-fixqa; do
      printf 'dyn_qsdsan_%s_%s\tenv/qsd/bin/python -I run_qsdsan.py dyn inputs %s %s diluted results/dyn_qsdsan_%s_%s.csv 1e-6\n' $i $w $w $i $i $w >> $J
    done
    for i in zoh linear; do
      printf 'dyn_bsm2python_%s_%s\tenv/bsm2/bin/python -I run_bsm2python.py dyn inputs %s %s diluted results/dyn_bsm2python_%s_%s.csv results/own_bsm2python_%s_%s.csv\n' $i $w $w $i $i $w $i $w >> $J
    done
  done
  # step check: bsm2-python again at 30- and 15-second steps
  for w in dry rain storm; do
    for st in 05:0.5 025:0.25; do
      printf 'dyn_bsm2python_linear_%s_step%s\tenv/bsm2/bin/python -I run_bsm2python.py dyn inputs %s linear diluted results/dyn_bsm2python_linear_%s_step%s.csv results/own_bsm2python_linear_%s_step%s.csv %s\n' \
        $w ${st%%:*} $w $w ${st%%:*} $w ${st%%:*} ${st#*:} >> $J
    done
  done
  # tolerance check: one QSDsan case again at rtol = atol = 1e-8
  printf 'dyn_qsdsan_linear-fixqa_dry_tol8\tenv/qsd/bin/python -I run_qsdsan.py dyn inputs dry linear-fixqa diluted results/dyn_qsdsan_linear-fixqa_dry_tol8.csv 1e-8\n' >> $J
  for w in rain storm; do
    printf 'dyn_bsm2python_linear_%s_hosted\tenv/bsm2/bin/python -I run_bsm2python.py dyn inputs %s linear hosted results/dyn_bsm2python_linear_%s_hosted.csv\n' $w $w $w >> $J
  done
fi

date -u +"start %FT%TZ" > logs/job-times.txt
export NOTICE
tr '\t' ' ' < $J | xargs -P "$NCORES" -L 1 sh job1.sh
date -u +"end %FT%TZ" >> logs/job-times.txt

# performance indices of each dynamic series: days 7-14 of the weather file are t = 21..28
for f in results/dyn_*.csv; do
  b=$(basename $f .csv); w=$(echo $b | sed 's/.*_\(dry\|rain\|storm\)\(_hosted\|_tol8\|_step[0-9]*\)\?$/\1/')
  python3 -I bsm1kpi.py $f $w 21 results/kpi_${b#dyn_}.csv || echo "kpi $b: VOID" >> logs/kpi.txt
done
grep -h '^ok \|^FAILED' logs/*.log | sort | uniq -c
