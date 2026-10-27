#!/bin/sh
# patch-job.sh linux|darwin
#
# One GCC Compile Farm host's share of the SWMM patch check (sewage
# checks/swmm/README.md, "Patches"). Run it from the work folder that holds it and:
#   src/base                 pyswmm SWMM develop at 6c81201 (git archive)
#   src/patched              the same + the two draft patches, f30b92c (git archive)
#   src/suite/public         swmm-nrtestsuite public/ at e609fdb (tar)
#   core-math/               the CORE-MATH files crshim.sh compiles
#   ref/patchcheck-ref.txt   digests the patched default build is checked against
#   ref/cr-ref.txt           digests the patched build + CORE-MATH shim is checked against
#   patchcheck.sh timecmp.py build.sh swmmrun.py swmmcmp.py models.txt crshim.sh
#   crlibm_shim.c crlibm_shim_darwin.c
# 1. patchcheck.sh: builds base and patched with the platform's default (gcc -O2,
#    or Apple clang -O2), checks the patched build against ref/patchcheck-ref.txt,
#    and times both, REPEATS (default 5) interleaved repeats each, pinned to
#    SWMM_TIME_CPU on Linux (macOS can't pin);
# 2. counts the FMA instructions in each libswmm5;
# 3. runs the patched build with the CORE-MATH shim preloaded, and with a canary
#    shim that must change Example1 and user1, and checks it against ref/cr-ref.txt.
# Kept: results/ (summary.txt first, load.txt before and after); work/ is scratch.
# NOTICE names the run-notice tool, NCORES the cores the notice states.
# Stops (exit 3) when /tmp/$USER-PLEASE-STOP appears, checked every 5 s while
# patchcheck runs and between steps. Run it under nice -n 19. POSIX sh.
set -u
OS=${1:?linux or darwin}
R=$(cd "$(dirname "$0")" && pwd)
RES=$R/results; mkdir -p "$RES"
SUM=$RES/summary.txt; : > "$SUM"
PY="python3 -I"
SUITE=$R/src/suite/public
NOTICE=${NOTICE:?set NOTICE to the run-notice tool}
NCORES=${NCORES:?set NCORES}
REPEATS=${REPEATS:-5}
MODELS=$(grep -v '^#' "$R/models.txt")
user=$(id -un)
note() { echo "$*"; echo "$*" >> "$SUM"; }
stopped() { [ -e "/tmp/$user-PLEASE-STOP" ]; }
stop() { if stopped; then note "STOPPED: /tmp/$user-PLEASE-STOP exists"; exit 3; fi; }
killtree() { for c in $(pgrep -P "$1"); do killtree "$c"; done; kill -TERM "$1" 2>/dev/null; }
sha256() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }
load() {  # LABEL: the load average, and per-CPU busy % (Linux) or the CPU split (macOS) over 10 s
  { echo "== $1: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"; uptime
    if [ "$OS" = darwin ]; then top -l 2 -n 0 -s 10 | grep -E '^(Load Avg|CPU usage)' | tail -2
    else mpstat -P ALL 10 1 | awk '/^Average/ && $2 ~ /^[0-9]+$/ {printf "%s:%d ", $2, 100 - $NF} END {print ""}'; fi
  } >> "$RES/load.txt" 2>&1
}

stop
"$NOTICE" start sewage-swmm-patch --job "EPA SWMM patch check and timing" --cores "$NCORES" --mem 2 --hours 1 \
  --intent "open-source wastewater model reproducibility study (sewage project)" || exit 2
trap '"$NOTICE" end sewage-swmm-patch' EXIT
trap 'exit 1' HUP INT TERM
T0=$(date +%s)
if [ "$OS" = darwin ]; then CC=cc; else CC=gcc; fi
export CC
{
  echo "date: $(date -u '+%Y-%m-%d %H:%M UTC')"; uname -a
  if [ "$OS" = darwin ]; then sw_vers; sysctl -n machdep.cpu.brand_string hw.ncpu
  else lscpu | grep -E 'Model name|^CPU\(s\)'; ldd --version 2>&1 | head -1; echo "debian $(cat /etc/debian_version)"; fi
  $CC --version 2>&1 | head -2; cmake --version | head -1; python3 --version
  echo "SWMM_CPUS=${SWMM_CPUS:-unset} SWMM_TIME_CPU=${SWMM_TIME_CPU:-unset} SWMM_JOBS=${SWMM_JOBS:-unset} nice=$(nice) repeats=$REPEATS"
  echo "models: $(echo "$MODELS" | wc -l | tr -d ' ')"
} > "$RES/env.txt" 2>&1
load before

# 1. patchcheck, watched for the stop file
sh "$R/patchcheck.sh" "$R/src/base" "$R/src/patched" "$SUITE" "$R/work" "$R/ref/patchcheck-ref.txt" \
   "$CC" "-O2" "$REPEATS" > "$RES/patchcheck.txt" 2>&1 &
pc=$!
while kill -0 "$pc" 2>/dev/null; do
  if stopped; then killtree "$pc"; wait "$pc"; note "STOPPED during patchcheck: /tmp/$user-PLEASE-STOP exists"; exit 3; fi
  sleep 5
done
wait "$pc"; rc=$?
note "patchcheck: exit $rc; patched -O2 vs ref/patchcheck-ref.txt: $(grep -E '^(IDENTICAL|DIFFERS|VOID)$' "$RES/patchcheck.txt" | head -1)$(grep ' DIFFERS ' "$RES/patchcheck.txt" | awk '{print " " $1 $3 $4}' | tr -d '\n')"
for b in base patched; do
  cp "$R/work/builds/$b/configure.log" "$RES/configure-$b.log" 2>/dev/null
  cp "$R/work/builds/$b/build.log" "$RES/build-$b.log" 2>/dev/null
done
for d in "$R"/work/runs/patched-check "$R"/work/runs/time-*; do
  [ -d "$d" ] || continue
  t=$(basename "$d")
  cp "$d/digests.txt" "$RES/digests-$t.txt"; cp "$d/meta.json" "$RES/meta-$t.json"
done
[ "$rc" = 0 ] || { note "patchcheck failed: VOID"; load after; exit 2; }

# 2. FMA instructions, and gage.c's compile command
lib_of() {
  for f in "$R/work/builds/$1/src/solver/libswmm5.so" "$R/work/builds/$1/src/solver/libswmm5.dylib"; do
    [ -f "$f" ] && { echo "$f"; return; }
  done
}
for b in base patched; do
  lib=$(lib_of $b)
  n=$(objdump -d "$lib" | awk -F'\t' '{for (i = 2; i <= NF; i++) { split($i, w, " ");
        if (w[1] ~ /^(vfn?m(add|sub)[0-9a-z]*|fn?m(add|sub)|fml[as])$/) { n++; break } } } END { print n + 0 }')
  note "build $b: $CC -O2; $(basename "$lib") sha256 $(sha256 "$lib" | cut -c1-16); $n FMA instructions"
  grep '"command".*gage\.c' "$R/work/builds/$b/compile_commands.json" > "$RES/cc-gage-$b.txt" 2>/dev/null
done

# 3. the patched build with the CORE-MATH shim
stop
if SHIM=$(sh "$R/crshim.sh" "$R/core-math" "$R/work/shim" "$(lib_of patched)" 2> "$RES/crshim.txt"); then
  note "shim: $(cat "$RES/crshim.txt")"
  for spec in "patched-cr-t1 $SHIM" "patched-canary-t1 $R/work/shim/libcrlibm_canary.${SHIM##*.}"; do
    set -- $spec; tag=$1; lib=$2
    stop
    if [ "$tag" = patched-cr-t1 ]; then ms=$MODELS; else ms="examples/Example1.inp user/user1.inp"; fi
    $PY "$R/swmmrun.py" run "$R/work/builds/patched/bin/runswmm" "$SUITE" "$R/work/runs" "$tag" 1 \
        --drop-out-over 50 --preload "$lib" $ms > "$RES/run-$tag.log" 2>&1 || note "run $tag: a model failed (VOID)"
    cp "$R/work/runs/$tag/digests.txt" "$RES/digests-$tag.txt"
  done
  ok=1
  for m in examples/Example1.inp user/user1.inp; do
    a=$(grep "^$m " "$RES/digests-patched-cr-t1.txt" | cut -d' ' -f2)
    b=$(grep "^$m " "$RES/digests-patched-canary-t1.txt" | cut -d' ' -f2)
    { [ -n "$a" ] && [ "$a" != - ] && [ -n "$b" ] && [ "$b" != - ] && [ "$a" != "$b" ]; } || ok=0
  done
  if [ $ok = 1 ]; then note "canary (pow wrong by 2^-20): changed Example1 and user1, so the preload reaches libswmm5"
  else note "canary (pow wrong by 2^-20): did NOT change Example1 and user1: the shim run is VOID"; fi
  $PY "$R/swmmrun.py" digcmp "$R/ref/cr-ref.txt" "$RES/digests-patched-cr-t1.txt" > "$RES/digcmp-cr.txt" 2>&1
  note "patched + CORE-MATH vs ref/cr-ref.txt: $(tail -1 "$RES/digcmp-cr.txt")$(grep ' DIFFERS ' "$RES/digcmp-cr.txt" | awk '{print " " $1 $3 $4}' | tr -d '\n')"
else
  note "shim: VOID: $(tr '\n' ' ' < "$RES/crshim.txt")"
fi
load after
note "done in $(( $(date +%s) - T0 )) s"
