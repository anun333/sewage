#!/bin/sh
# cfarm-job.sh linux|darwin [threads] [dmr]
#
# One GCC Compile Farm host's share of the SWMM cross-machine phase (README,
# "cfarm"). Run it from the work folder that holds it and:
#   src/swmm          pyswmm SWMM develop at 6c81201 (git archive)
#   src/suite/public  swmm-nrtestsuite public/ at e609fdb (git archive)
#   core-math/        the CORE-MATH files crshim.sh compiles
#   ref/              board5's digests: board5-gcc-O2-t1.txt and
#                     board5-gcc-O2-nocontract-cr-t1.txt
#   build.sh swmmrun.py swmmcmp.py models.txt crshim.sh crlibm_shim.c
#   crlibm_shim_darwin.c (and dmr_geomean.py dmr_rounding.py for "dmr")
# It builds the platform's default (gcc -O2 on Linux, Apple clang -O2 on
# macOS) and the same with -ffp-contract=off; runs the models on one thread
# with each, and with the second build again with the CORE-MATH shim preloaded
# (crshim.sh), plus a canary shim that must change Example1 and user1; compares
# each run's digests to board5's (swmmrun.py digcmp); and counts the FMA
# instructions in each libswmm5. "threads" builds the -ffp-contract=off
# configuration a second time and runs it at 4 threads; "dmr" runs the two DMR
# checks. What is kept goes to results/ (summary.txt first); builds/, runs/
# and shim/ are scratch.
# Resources: SWMM_JOBS build jobs (default 4); on Linux every build and run is
# pinned with taskset to SWMM_CPUS (default 0-3). Run it under nice -n 19.
# NOTICE names the run-notice tool. SKIP_GC2=1 leaves gate_control_2 out (its
# .out is 492 MB); otherwise that .out is deleted right after hashing.
# Stops (exit 3) when /tmp/$USER-PLEASE-STOP appears. POSIX sh.
set -u
[ $# -ge 1 ] || { sed -n '2,29p' "$0"; exit 2; }
OS=$1; shift
THREADS=0; DMR=0
for x in "$@"; do case $x in threads) THREADS=1 ;; dmr) DMR=1 ;; esac; done
R=$(cd "$(dirname "$0")" && pwd)
RES=$R/results; mkdir -p "$RES"
SUM=$RES/summary.txt; : > "$SUM"
PY="python3 -I"
SUITE=$R/src/suite/public; SRC=$R/src/swmm
NOTICE=${NOTICE:?set NOTICE to the run-notice tool}
JOBS=${SWMM_JOBS:-4}; export SWMM_JOBS=$JOBS
PIN=""; command -v taskset >/dev/null 2>&1 && PIN="taskset -c ${SWMM_CPUS:-0-3}"
user=$(id -un)
note() { echo "$*"; echo "$*" >> "$SUM"; }
stop() { if [ -e "/tmp/$user-PLEASE-STOP" ]; then note "STOPPED: /tmp/$user-PLEASE-STOP exists"; exit 3; fi; }
sha256() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }

stop
"$NOTICE" start sewage-swmm --job "EPA SWMM bit-reproducibility builds and model runs" \
  --cores "$JOBS" --mem 2 --hours 1 \
  --intent "open-source wastewater model reproducibility study (sewage project)" || exit 2
trap '"$NOTICE" end sewage-swmm' EXIT
trap 'exit 1' HUP INT TERM
T0=$(date +%s)

MODELS=$(grep -v '^#' "$R/models.txt")
REF1=$R/ref/board5-gcc-O2-t1.txt; REFC=$R/ref/board5-gcc-O2-nocontract-cr-t1.txt
if [ "${SKIP_GC2:-0}" = 1 ]; then
  MODELS=$(echo "$MODELS" | grep -v gate_control_2)
  grep -v gate_control_2 "$REF1" > "$R/ref/board5-gcc-O2-t1-nogc2.txt"
  grep -v gate_control_2 "$REFC" > "$R/ref/board5-gcc-O2-nocontract-cr-t1-nogc2.txt"
  REF1=$R/ref/board5-gcc-O2-t1-nogc2.txt; REFC=$R/ref/board5-gcc-O2-nocontract-cr-t1-nogc2.txt
fi
if [ "$OS" = darwin ]; then CC=cc; CXX=c++; D=clang; else CC=gcc; CXX=g++; D=gcc; fi
export CC

{
  echo "date: $(date -u '+%Y-%m-%d %H:%M UTC')"; uname -a
  if [ "$OS" = darwin ]; then
    sw_vers; sysctl -n machdep.cpu.brand_string hw.ncpu
  else
    lscpu | grep -E 'Model name|^CPU\(s\)'; ldd --version 2>&1 | head -1; echo "debian $(cat /etc/debian_version)"
  fi
  $CC --version 2>&1 | head -2; cmake --version | head -1; python3 --version
  echo "pin: ${PIN:-none}; build jobs: $JOBS"; uptime
} > "$RES/env.txt" 2>&1

lib_of() {  # the libswmm5 a build's runswmm loads
  for f in "$R/builds/$1/src/solver/libswmm5.so" "$R/builds/$1/src/solver/libswmm5.dylib"; do
    [ -f "$f" ] && { echo "$f"; return; }
  done
}
build() {  # NAME FLAGS
  stop
  echo "== build $1: $CC $2"
  sh "$R/build.sh" "$SRC" "$R/builds/$1" "$CC" "$CXX" "$2" > "$RES/build-$1.txt" 2>&1; rc=$?
  cp "$R/builds/$1/configure.log" "$RES/configure-$1.log" 2>/dev/null
  cp "$R/builds/$1/build.log" "$RES/build-$1.log" 2>/dev/null
  [ $rc = 0 ] || { note "build $1: FAILED (VOID), see build-$1.txt"; exit 2; }
  lib=$(lib_of "$1")
  n=$(objdump -d "$lib" | awk -F'\t' '{for (i = 2; i <= NF; i++) { split($i, w, " ");
        if (w[1] ~ /^(vfn?m(add|sub)[0-9a-z]*|fn?m(add|sub)|fml[as])$/) { n++; break } } } END { print n + 0 }')
  note "build $1: $CC $2; $(basename "$lib") sha256 $(sha256 "$lib" | cut -c1-16); $n FMA instructions"
}
run() {  # TAG BUILD THREADS [--preload LIB] MODEL...
  tag=$1; b=$2; t=$3; shift 3
  stop
  echo "== run $tag"
  $PY "$R/swmmrun.py" run "$R/builds/$b/bin/runswmm" "$SUITE" "$R/runs" "$tag" "$t" \
      --drop-out-over 100 "$@" > "$RES/run-$tag.log" 2>&1; rc=$?
  cp "$R/runs/$tag/digests.txt" "$RES/digests-$tag.txt" 2>/dev/null
  [ $rc = 0 ] || note "run $tag: exit $rc (a model failed or wrote no .out: VOID)"
}
dig() {  # LABEL A B
  $PY "$R/swmmrun.py" digcmp "$2" "$3" > "$RES/digcmp-$1.txt" 2>&1
  list=$(grep ' DIFFERS ' "$RES/digcmp-$1.txt" | awk '{print $1 $3 $4}' | sed 's|^[^/]*/||; s|\.inp||' | tr '\n' ' ')
  note "digcmp $1: $(tail -1 "$RES/digcmp-$1.txt")${list:+ [$list]}"
}

# 1. the platform's default
build $D-O2 "-O2"
run $D-O2-t1 $D-O2 1 $MODELS
dig "board5-gcc-O2-t1_vs_$D-O2-t1" "$REF1" "$RES/digests-$D-O2-t1.txt"

# 2. the same with -ffp-contract=off
build $D-O2-nocontract "-O2 -ffp-contract=off"
run $D-O2-nocontract-t1 $D-O2-nocontract 1 $MODELS
dig "board5-gcc-O2-t1_vs_$D-O2-nocontract-t1" "$REF1" "$RES/digests-$D-O2-nocontract-t1.txt"
dig "$D-O2-t1_vs_$D-O2-nocontract-t1" "$RES/digests-$D-O2-t1.txt" "$RES/digests-$D-O2-nocontract-t1.txt"

# 3. (2) with SWMM's libm calls answered by CORE-MATH
stop
C=$D-O2-nocontract-cr-t1
if SHIM=$(sh "$R/crshim.sh" "$R/core-math" "$R/shim" "$(lib_of $D-O2-nocontract)" 2> "$RES/crshim.txt"); then
  note "shim: $(cat "$RES/crshim.txt")"
  run $C $D-O2-nocontract 1 --preload "$SHIM" $MODELS
  run $D-O2-nocontract-canary-t1 $D-O2-nocontract 1 --preload "$R/shim/libcrlibm_canary.${SHIM##*.}" \
      examples/Example1.inp user/user1.inp
  ok=1
  for m in examples/Example1.inp user/user1.inp; do
    a=$(grep "^$m " "$RES/digests-$C.txt" | cut -d' ' -f2)
    b=$(grep "^$m " "$RES/digests-$D-O2-nocontract-canary-t1.txt" | cut -d' ' -f2)
    { [ -n "$a" ] && [ "$a" != - ] && [ -n "$b" ] && [ "$b" != - ] && [ "$a" != "$b" ]; } || ok=0
  done
  if [ $ok = 1 ]; then note "canary (pow wrong by 2^-20): changed Example1 and user1, so the preload reaches libswmm5"
  else note "canary (pow wrong by 2^-20): did NOT change Example1 and user1: the preload missed libswmm5, shim runs VOID"; fi
  dig "board5-gcc-O2-t1_vs_$C" "$REF1" "$RES/digests-$C.txt"
  dig "board5-gcc-O2-nocontract-cr-t1_vs_$C" "$REFC" "$RES/digests-$C.txt"
  dig "$D-O2-nocontract-t1_vs_$C" "$RES/digests-$D-O2-nocontract-t1.txt" "$RES/digests-$C.txt"
else
  note "shim: VOID: $(tr '\n' ' ' < "$RES/crshim.txt")"
fi

# 4. a second build of (2), at 4 threads
if [ $THREADS = 1 ]; then
  build $D-O2-nocontract-b2 "-O2 -ffp-contract=off"
  # the files differ by SWMM's BUILD_ID (a configure-time timestamp); compare the code
  if command -v objcopy >/dev/null 2>&1; then
    objcopy -O binary --only-section=.text "$(lib_of $D-O2-nocontract)" "$R/builds/a.text"
    objcopy -O binary --only-section=.text "$(lib_of $D-O2-nocontract-b2)" "$R/builds/b.text"
    note "libswmm5 .text of the two -ffp-contract=off builds: $(cmp -s "$R/builds/a.text" "$R/builds/b.text" && echo same bytes || echo different bytes) (the files differ by the BUILD_ID timestamp)"
  fi
  run $D-O2-nocontract-b2-t4 $D-O2-nocontract-b2 4 $MODELS
  n=$(awk '!/^#/ && $4 == 4' "$RES/digests-$D-O2-nocontract-b2-t4.txt" | wc -l | tr -d ' ')
  note "threads: $n models report 4 threads used"
  dig "$D-O2-nocontract-t1_vs_$D-O2-nocontract-b2-t4" "$RES/digests-$D-O2-nocontract-t1.txt" \
      "$RES/digests-$D-O2-nocontract-b2-t4.txt"
fi

# the DMR checks: does another libm move exp(mean(log)) across the limit?
if [ $DMR = 1 ]; then
  stop
  $PIN $PY "$R/dmr_geomean.py" > "$RES/dmr_geomean.txt" 2>&1
  note "dmr_geomean: exit $?: $(tail -1 "$RES/dmr_geomean.txt")"
  $PIN $PY "$R/dmr_rounding.py" --rule half_even --trials 50000 > "$RES/dmr_rounding.txt" 2>&1
  note "dmr_rounding --rule half_even --trials 50000: exit $?: $(tail -1 "$RES/dmr_rounding.txt")"
fi
note "done in $(( $(date +%s) - T0 )) s with $JOBS build jobs; runs on 1 thread$([ $THREADS = 1 ] && echo ', and 4 for the thread run')"
