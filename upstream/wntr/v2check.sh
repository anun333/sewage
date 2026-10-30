#!/bin/sh
# v2check.sh WORK TREE REF CPUS: after fixcheck.sh, check a revised fix tree the same way.
# In WORK (fixcheck.sh's), with src-TREE/ built: CI's core pytest selection on TREE, and one
# wntrrun.py run of every network compared with REF's first run (runs/REF-r1), which must
# be bit-identical when TREE only restructures REF. Writes results/v2-*. Run it under
# nice -n 19. POSIX sh.
set -u
[ $# -eq 4 ] || { sed -n '2,6p' "$0"; exit 2; }
W=$(cd "$1" && pwd); T=$2; REF=$3; CPUS=$4; R=$W/results; C=$W/checks; V=$W/venv
s=0; (cd "$W/src-$T" && env -i PATH="$V/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 MPLBACKEND=Agg \
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$W/src-$T" \
  taskset -c "$CPUS" "$V/bin/python" -m pytest -p no:cacheprovider -q -rfEs -m "not extensions" \
  --ignore=wntr/extensions --doctest-modules --doctest-glob="*.rst" --junitxml="$R/v2-pytest-$T.xml" wntr) \
  > "$R/v2-pytest-$T.log" 2>&1 || s=$?
echo "v2-pytest-$T $s" >> "$R/rc.txt"
s=0; env -i PATH="$V/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 MPLBACKEND=Agg OMP_NUM_THREADS=1 \
  OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$W/src-$T" \
  taskset -c "$CPUS" "$V/bin/python" -s "$C/wntrrun.py" run "$W/nets" "$W/runs" "$T-r1" "$C/networks.txt" \
  > "$R/v2-run-$T-r1.log" 2>&1 || s=$?
echo "v2-run-$T-r1 $s" >> "$R/rc.txt"
cp "$W/runs/$T-r1/digests.txt" "$R/runs-$T-r1-digests.txt"
s=0; python3 -I "$C/wntrcmp.py" digcmp "$W/runs/$REF-r1/digests.txt" "$W/runs/$T-r1/digests.txt" \
  > "$R/v2-dig-$REF-vs-$T.txt" 2>&1 || s=$?
echo "v2-dig-$REF-vs-$T $s" >> "$R/rc.txt"
echo "v2 finished" >> "$R/rc.txt"
