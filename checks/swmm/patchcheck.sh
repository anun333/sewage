#!/bin/sh
# patchcheck.sh BASE_SRC PATCHED_SRC SUITE WORK REF_DIGESTS CC "CFLAGS" [REPEATS]
#
# Checks the two upstream patches in ../../upstream/swmm/ (the -ffp-contract=off
# build change and the gage.c fix) on one machine:
#  1. builds BASE_SRC and PATCHED_SRC with the same CC and CFLAGS;
#  2. runs every model in models.txt at 1 thread on the patched build and
#     compares its digests with REF_DIGESTS (board5's gcc-O2-t1, the no-FMA
#     reference): IDENTICAL means the patch removes this machine's FMA effect;
#  3. times both builds, REPEATS (default 5) interleaved repeats each, pinned to
#     one CPU ($SWMM_TIME_CPU, default 3) where taskset exists, and prints
#     timecmp.py's table.
# Pass CFLAGS that produce FMA on this machine to make the timing mean
# something: "-O3 -march=native" on x86-64; the plain default (-O2) already
# contracts on aarch64 and Apple silicon. Builds use $SWMM_JOBS jobs (default
# 4) on CPUs $SWMM_CPUS (default 0-3), as build.sh does.
set -eu
[ $# -ge 7 ] || { sed -n 2,17p "$0"; exit 2; }
BASE=$1 PATCHED=$2 SUITE=$3 WORK=$4 REF=$5 CC=$6 CFLAGS=$7 REPEATS=${8:-5}
HERE=$(cd "$(dirname "$0")" && pwd)
MODELS=$(cat "$HERE/models.txt")
case $CC in clang*) CXX=clang++ ;; gcc*) CXX=g++ ;; *) CXX=c++ ;; esac
mkdir -p "$WORK/builds" "$WORK/runs"

echo "== build: $CC $CFLAGS"
sh "$HERE/build.sh" "$BASE" "$WORK/builds/base" "$CC" "$CXX" "$CFLAGS" > "$WORK/builds/base.log" 2>&1
sh "$HERE/build.sh" "$PATCHED" "$WORK/builds/patched" "$CC" "$CXX" "$CFLAGS" > "$WORK/builds/patched.log" 2>&1

echo "== patched build against $REF"
python3 -I "$HERE/swmmrun.py" run "$WORK/builds/patched/bin/runswmm" "$SUITE" "$WORK/runs" patched-check 1 \
    --drop-out-over 50 $MODELS > "$WORK/runs/patched-check.log"
python3 -I "$HERE/swmmrun.py" digcmp "$REF" "$WORK/runs/patched-check/digests.txt" || true

echo "== timing, $REPEATS repeats each, interleaved"
CPU=${SWMM_TIME_CPU:-3}
i=1
while [ "$i" -le "$REPEATS" ]; do
    for b in base patched; do
        SWMM_CPUS=$CPU python3 -I "$HERE/swmmrun.py" run "$WORK/builds/$b/bin/runswmm" "$SUITE" "$WORK/runs" \
            "time-$b-r$i" 1 --drop-out-over 1 $MODELS > "$WORK/runs/time-$b-r$i.log"
    done
    i=$((i + 1))
done
echo "load at end: $(uptime)"
python3 -I "$HERE/timecmp.py" "$WORK/runs" time-base time-patched
