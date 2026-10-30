#!/bin/sh
# crpreload-job.sh: SWMM with crmvec's crpreload in place of crlibm_shim.c (Linux).
#
# crpreload (crmvec, github.com/anun333/crmvec, since 0.9.0) answers CORE-MATH's 76
# elementary functions under their C library names; crlibm_shim.c answers the 11
# that SWMM calls. Both return correctly rounded results, which are unique, so a
# run with either must give the same bits. Run it from the work folder that holds it and:
#   src/base           pyswmm SWMM develop at 6c81201 (git archive)
#   src/patched        the same + the two patches in upstream/swmm/ (git am, git archive)
#   src/suite/public   swmm-nrtestsuite public/ at e609fdb
#   crmvec/            crmvec v0.12.2 (git archive of 953ed27)
#   ref/cr-ref.txt     digests/board5/gcc-O2-nocontract-cr-t1.txt, the shim's reference
#   build.sh swmmrun.py swmmcmp.py models.txt transect/
# 1. builds crpreload (make crpreload/libcrpreload.so) and SWMM twice: base with
#    gcc -O2 -ffp-contract=off, patched with gcc -O2 (its CMake pins contraction off);
# 2. checks that every libm function libswmm5 imports is one crpreload exports
#    (the list crshim.sh checks);
# 3. runs the models in models.txt at one thread: base without a preload (the
#    control: it must differ from the reference wherever glibc and CORE-MATH
#    disagree), base with crpreload, patched with crpreload; and Example1 once
#    under LD_DEBUG=bindings, to record which library answers each libm call;
# 4. compares each run with ref/cr-ref.txt (swmmrun.py digcmp);
# 5. runs transect/check.sh with the base build: what the engine does with a zero
#    roughness on a transect's NC line (pyswmm SWMM #419, #420).
# Kept: results/ (summary.txt first). NOTICE names the run-notice tool, NCORES the
# cores the notice states; SWMM_CPUS (default 0-3) and SWMM_JOBS as for build.sh.
# Run it under nice -n 19. POSIX sh.
set -u
R=$(cd "$(dirname "$0")" && pwd)
RES=$R/results; mkdir -p "$RES"
SUM=$RES/summary.txt; : > "$SUM"
PY="python3 -I"
SUITE=$R/src/suite/public
NOTICE=${NOTICE:?set NOTICE to the run-notice tool}
NCORES=${NCORES:?set NCORES}
MODELS=$(grep -v '^#' "$R/models.txt")
PIN="taskset -c ${SWMM_CPUS:-0-3}"
note() { echo "$*"; echo "$*" >> "$SUM"; }
sha256() { sha256sum "$1" | cut -d' ' -f1; }

"$NOTICE" start sewage-swmm-crpreload --job "EPA SWMM test models with a correctly rounded libm (crpreload)" \
  --cores "$NCORES" --mem 2 --hours 1 --nice 19 \
  --intent "checking open-source water software for the sewage project, github.com/anun333/sewage" || exit 2
trap '"$NOTICE" end sewage-swmm-crpreload' EXIT
trap 'exit 1' HUP INT TERM
T0=$(date +%s)
{
  echo "date: $(date -u '+%Y-%m-%d %H:%M UTC')"; uname -a
  lscpu | grep -E 'Model name|^CPU\(s\)|Flags' | sed 's/^\(Flags:\).*\( fma \).*/\1 ...\2.../'
  ldd --version 2>&1 | head -1; echo "debian $(cat /etc/debian_version)"
  gcc --version | head -1; cmake --version | head -1; python3 --version
  echo "SWMM_CPUS=${SWMM_CPUS:-unset} SWMM_JOBS=${SWMM_JOBS:-unset} nice=$(nice)"
  echo "models: $(echo "$MODELS" | wc -l | tr -d ' ')"
} > "$RES/env.txt" 2>&1

# 1. builds
s=0; $PIN make -C "$R/crmvec" -j "${SWMM_JOBS:-4}" crpreload/libcrpreload.so > "$RES/build-crpreload.log" 2>&1 || s=$?
CRP=$R/crmvec/crpreload/libcrpreload.so
[ "$s" = 0 ] && [ -f "$CRP" ] || { note "crpreload build failed (exit $s): VOID"; exit 2; }
note "crpreload: crmvec v0.12.2, libcrpreload.so sha256 $(sha256 "$CRP" | cut -c1-16), $(nm -D --defined-only "$CRP" | wc -l) symbols exported"
for spec in "base|-O2 -ffp-contract=off" "patched|-O2"; do
  b=${spec%%|*}; fl=${spec#*|}
  s=0; sh "$R/build.sh" "$R/src/$b" "$R/work/builds/$b" gcc g++ "$fl" > "$RES/build-$b.log" 2>&1 || s=$?
  lib=$R/work/builds/$b/src/solver/libswmm5.so
  [ "$s" = 0 ] && [ -f "$lib" ] || { note "SWMM build $b failed (exit $s): VOID"; exit 2; }
  note "build $b: gcc $fl; libswmm5.so sha256 $(sha256 "$lib" | cut -c1-16)"
done

# 2. every libm import answered
answered=$(nm -D --defined-only "$CRP" | awk '{print $3}')
for b in base patched; do
  imports=$(nm -D --undefined-only "$R/work/builds/$b/src/solver/libswmm5.so" | awk '{print $2}' | sed 's/@.*//')
  missing=""; seen=""
  for x in $imports; do
    case $x in
      sin|cos|tan|asin|acos|atan|atan2|sincos|__sincos|sinh|cosh|tanh|exp|exp2|exp10|__exp10|expm1|log|log10|log2|log1p|pow|cbrt|hypot|erf|erfc|lgamma|tgamma)
        seen="$seen $x"
        echo "$answered" | grep -qx "$x" || missing="$missing $x" ;;
    esac
  done
  [ -n "$seen" ] || { note "imports of $b: none read: VOID"; exit 2; }
  [ -z "$missing" ] || { note "imports of $b not answered by crpreload:$missing: VOID"; exit 2; }
  note "libm imports of $b's libswmm5, all answered by crpreload:$seen"
done

# 3. runs
for spec in "base-glibc-t1|base|" "base-crp-t1|base|$CRP" "patched-crp-t1|patched|$CRP"; do
  tag=${spec%%|*}; rest=${spec#*|}; b=${rest%%|*}; pre=${rest#*|}
  if [ -n "$pre" ]; then set -- --preload "$pre"; else set --; fi
  s=0; $PY "$R/swmmrun.py" run "$R/work/builds/$b/bin/runswmm" "$SUITE" "$R/work/runs" "$tag" 1 \
    --drop-out-over 50 "$@" $MODELS > "$RES/run-$tag.log" 2>&1 || s=$?
  [ "$s" = 0 ] || note "run $tag: exit $s (a model failed)"
  cp "$R/work/runs/$tag/digests.txt" "$RES/digests-$tag.txt"
  cp "$R/work/runs/$tag/meta.json" "$RES/meta-$tag.json" 2>/dev/null
done
d=$R/work/bindings; mkdir -p "$d"
LD_DEBUG=bindings LD_DEBUG_OUTPUT=$d/ld LD_PRELOAD=$CRP $PIN "$R/work/builds/base/bin/runswmm" \
  "$SUITE/examples/Example1.inp" "$d/ex1.rpt" "$d/ex1.out" > /dev/null 2>&1
cat "$d"/ld.* 2>/dev/null | grep -E "binding file [^ ]*libswmm5[^ ]* .*: normal symbol \`(sin|cos|tan|asin|acos|atan|atan2|sincos|exp|log|log10|pow)'" \
  | sed -E 's/^ *[0-9]+: *//' | sort -u > "$RES/bindings-example1.txt"
ncrp=$(grep -c 'to [^ ]*libcrpreload\.so' "$RES/bindings-example1.txt")
nall=$(wc -l < "$RES/bindings-example1.txt")
note "bindings (Example1, base + crpreload): $ncrp of $nall libm symbols libswmm5 uses bound to libcrpreload.so: $(sed -E "s/.*symbol \`([a-z0-9]+)'.*/\1/" "$RES/bindings-example1.txt" | sort -u | tr '\n' ' ')"

# 4. against the shim's reference
for tag in base-glibc-t1 base-crp-t1 patched-crp-t1; do
  $PY "$R/swmmrun.py" digcmp "$R/ref/cr-ref.txt" "$RES/digests-$tag.txt" > "$RES/digcmp-$tag.txt" 2>&1
  note "$tag vs board5 gcc-O2-nocontract-cr-t1 (the shim): $(tail -1 "$RES/digcmp-$tag.txt")$(grep ' DIFFERS ' "$RES/digcmp-$tag.txt" | awk '{print " " $1 $3 $4}' | tr -d '\n')"
done
# 5. zero roughness on a transect's NC line (pyswmm SWMM #419, #420), with the base build
s=0; sh "$R/transect/check.sh" "$R/work/builds/base/bin/runswmm" "$R/work/transect" > "$RES/transect.txt" 2>&1 || s=$?
note "transect roughness (transect/check.sh): exit $s, $(tail -1 "$RES/transect.txt")"
note "done in $(( $(date +%s) - T0 )) s"
