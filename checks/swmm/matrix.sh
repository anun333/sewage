#!/bin/sh
# matrix.sh SRC SUITE WORK [CONFIGS]
#
# Builds SWMM (SRC: a clone of pyswmm/Stormwater-Management-Model) once per
# line of CONFIGS (default configs.txt here), runs the models in models.txt
# (paths under SUITE: swmm-nrtestsuite's public/ directory) at each thread
# count the line names, and writes WORK/digests/<config>-t<N>.txt. Then:
#   - per configuration: each thread count, and REPEATS (default 2) more runs
#     at the highest one, against its own 1-thread run (digcmp);
#   - per configuration: its 1-thread run against the first configuration's
#     (digcmp for the verdict, then cmp for decoded differences).
# Prints one verdict line per comparison and writes WORK/summary.txt.
#
# CPU limit: on Linux every build and run is pinned with taskset to
# $SWMM_CPUS (default 0-3): the limit used on board5 was 4 of its 12 hardware
# threads. Builds use 4 jobs; nothing runs concurrently. Thread counts above
# the CPUs given are oversubscribed, which still tests how OpenMP splits the
# work. Without taskset (macOS) runs are unpinned.
# POSIX sh and python3 (standard library) only; needs cmake >= 3.23.
set -eu
[ $# -ge 3 ] || { sed -n '2,20p' "$0"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$1; SUITE=$2; WORK=$3; CONFIGS=${4:-$HERE/configs.txt}
REPEATS=${REPEATS:-2}
PY="python3 -I"
MODELS=$(grep -v '^#' "$HERE/models.txt")
mkdir -p "$WORK/builds" "$WORK/runs" "$WORK/digests"
SUM="$WORK/summary.txt"
: > "$SUM"
note() { echo "$*"; echo "$*" >> "$SUM"; }
verdict() { tail -1 "$1"; }

grep -v '^#' "$CONFIGS" | while IFS='|' read -r name cc cxx cflags threads; do
  [ -n "$name" ] || continue
  B="$WORK/builds/$name"
  echo "== build $name: $cc $cflags"
  sh "$HERE/build.sh" "$SRC" "$B" "$cc" "$cxx" "$cflags" </dev/null >/dev/null
  top=1
  for t in $threads; do
    # keep the 1-thread .out files (except gate_control_2's 492 MB) for decoding
    if [ "$t" = 1 ]; then keep=100; else keep=0; fi
    $PY "$HERE/swmmrun.py" run "$B/bin/runswmm" "$SUITE" "$WORK/runs" "$name-t$t" "$t" \
        --drop-out-over $keep $MODELS </dev/null > "$WORK/runs/$name-t$t.log" || true
    cp "$WORK/runs/$name-t$t/digests.txt" "$WORK/digests/$name-t$t.txt"
    top=$t
  done
  i=1
  while [ "$top" != 1 ] && [ $i -le "$REPEATS" ]; do
    tag="$name-t$top-rep$i"
    $PY "$HERE/swmmrun.py" run "$B/bin/runswmm" "$SUITE" "$WORK/runs" "$tag" "$top" \
        --drop-out-over 0 $MODELS </dev/null > "$WORK/runs/$tag.log" || true
    cp "$WORK/runs/$tag/digests.txt" "$WORK/digests/$tag.txt"
    i=$((i + 1))
  done
  for f in "$WORK/digests/$name"-t*.txt; do
    tag=$(basename "$f" .txt)
    [ "$tag" = "$name-t1" ] && continue
    $PY "$HERE/swmmrun.py" digcmp "$WORK/digests/$name-t1.txt" "$f" </dev/null > "$WORK/runs/dig_$tag.txt" || true
    note "threads  $name-t1 vs $tag: $(verdict "$WORK/runs/dig_$tag.txt")"
  done
  first=$(grep -v '^#' "$CONFIGS" | head -1 | cut -d'|' -f1)
  if [ "$name" != "$first" ]; then
    $PY "$HERE/swmmrun.py" digcmp "$WORK/digests/$first-t1.txt" "$WORK/digests/$name-t1.txt" </dev/null \
        > "$WORK/runs/dig_$first-vs-$name.txt" || true
    $PY "$HERE/swmmrun.py" cmp "$WORK/runs" "$first-t1" "$name-t1" --skip-missing $MODELS </dev/null \
        > "$WORK/runs/cmp_$first-vs-$name.txt" || true
    n=$(grep -c 'DIFFERS ' "$WORK/runs/cmp_$first-vs-$name.txt" || true)
    note "build    $first vs $name: $(verdict "$WORK/runs/dig_$first-vs-$name.txt") ($n models decoded as differing; $WORK/runs/cmp_$first-vs-$name.txt)"
  fi
done
echo "summary: $SUM"
if grep -q 'VOID' "$SUM"; then echo VOID; exit 2; fi
if grep -q 'DIFFERS' "$SUM"; then echo DIFFERS; exit 1; fi
echo IDENTICAL
