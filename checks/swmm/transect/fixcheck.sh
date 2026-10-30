#!/bin/sh
# fixcheck.sh WORK: the last-transect fix (upstream/swmm/0003-*.patch), on a host where
# crpreload-job.sh has run in WORK.
# Builds WORK/src/lasttransect (develop at 6c81201 + the fix) with gcc -O2
# -ffp-contract=off, as crpreload-job.sh built base, then:
#   1. runs the suite's models with it and compares them with base's
#      (results/digests-base-glibc-t1.txt): the fix must change none of them, since
#      no model there ends with [TRANSECTS];
#   2. runs transect/check.sh with it: transects-last must now equal explicit.
# Writes WORK/results/lasttransect-*. SWMM_CPUS and SWMM_JOBS as for build.sh. Run it
# under nice -n 19. POSIX sh.
set -u
[ $# -eq 1 ] || { sed -n '2,12p' "$0"; exit 2; }
R=$(cd "$1" && pwd); RES=$R/results
s=0; sh "$R/build.sh" "$R/src/lasttransect" "$R/work/builds/lasttransect" gcc g++ "-O2 -ffp-contract=off" \
  > "$RES/lasttransect-build.log" 2>&1 || s=$?
echo "build: exit $s" > "$RES/lasttransect-summary.txt"
# shellcheck disable=SC2046  # one argument per model; model paths have no spaces
python3 -I "$R/swmmrun.py" run "$R/work/builds/lasttransect/bin/runswmm" "$R/src/suite/public" "$R/work/runs" \
  lasttransect-t1 1 --drop-out-over 50 $(grep -v '^#' "$R/models.txt") > "$RES/lasttransect-run.log" 2>&1
cp "$R/work/runs/lasttransect-t1/digests.txt" "$RES/lasttransect-digests.txt"
python3 -I "$R/swmmrun.py" digcmp "$RES/digests-base-glibc-t1.txt" "$RES/lasttransect-digests.txt" \
  > "$RES/lasttransect-digcmp.txt" 2>&1
echo "suite vs base (same flags, no fix): $(tail -1 "$RES/lasttransect-digcmp.txt")" >> "$RES/lasttransect-summary.txt"
sh "$R/transect/check.sh" "$R/work/builds/lasttransect/bin/runswmm" "$R/work/transect-fixed" \
  > "$RES/lasttransect-transect.txt" 2>&1
echo "transect/check.sh: $(grep 'transects-last is' "$RES/lasttransect-transect.txt")" >> "$RES/lasttransect-summary.txt"
cat "$RES/lasttransect-summary.txt"
