#!/bin/sh
# crshim.sh CORE_MATH_DIR OUT_DIR LIBSWMM5
#
# Builds the CORE-MATH shim for SWMM's libm calls: OUT_DIR/libcrlibm_shim.so
# from crlibm_shim.c on Linux (for LD_PRELOAD), OUT_DIR/libcrlibm_shim.dylib
# from crlibm_shim_darwin.c on macOS (for DYLD_INSERT_LIBRARIES; it interposes).
# Beside it, libcrlibm_canary.*: the same with pow wrong by 2^-20 relative, a
# planted fault a run must show, or the preload never reached libswmm5.
# Then checks that every libm function LIBSWMM5 imports is one the shim
# answers. CORE_MATH_DIR holds CORE-MATH's binary64 acos asin atan cos exp sin
# tan log log10 pow as crnumerics' core-math/ lays them out (log/, log10/ and
# pow/ with their headers), and on macOS exp10 (clang makes __exp10 of
# pow(10, x)). Every machine compiles them with the same flags, -O2
# -fno-builtin -ffp-contract=off, so the code computes as written (CORE-MATH's
# fused steps are explicit fma calls). On Linux, pinned with
# taskset to $SWMM_CPUS (default 0-3). Prints the shim's path; exit 0, or 2
# (VOID, reason on stderr) when a compile fails or an import is not answered.
# POSIX sh.
set -eu
[ $# -eq 3 ] || { sed -n '2,18p' "$0"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
CM=$1; O=$2; LIB=$3
CC=${CC:-cc}
PIN=""; command -v taskset >/dev/null 2>&1 && PIN="taskset -c ${SWMM_CPUS:-0-3}"
FLAGS="-O2 -fPIC -fno-builtin -ffp-contract=off"
void() { echo "$*" >&2; echo VOID >&2; exit 2; }
CR="acos.c asin.c atan.c cos.c exp.c sin.c tan.c log/log.c log10/log10.c pow/pow.c"
[ "$(uname -s)" = Darwin ] && CR="$CR exp10.c"
rm -rf "$O"; mkdir -p "$O/cr"
for f in $CR; do
  $PIN $CC $FLAGS -I"$CM/$(dirname $f)" -c "$CM/$f" -o "$O/cr/$(basename $f .c).o" \
    || void "compile failed: $f"
done
if [ "$(uname -s)" = Darwin ]; then
  SRC=$HERE/crlibm_shim_darwin.c; EXT=dylib; LINK=-dynamiclib
else
  SRC=$HERE/crlibm_shim.c; EXT=so; LINK=-shared
fi
$PIN $CC $FLAGS -c "$SRC" -o "$O/shim.o" || void "compile failed: $SRC"
$PIN $CC $FLAGS -DSHIM_CANARY -c "$SRC" -o "$O/canary.o" || void "compile failed: $SRC (canary)"
$PIN $CC $LINK -o "$O/libcrlibm_shim.$EXT" "$O"/cr/*.o "$O/shim.o" -lm || void "link failed"
$PIN $CC $LINK -o "$O/libcrlibm_canary.$EXT" "$O"/cr/*.o "$O/canary.o" -lm || void "link failed (canary)"

# what the shim answers, and what libswmm5 imports (Mach-O names carry a leading _)
if [ "$EXT" = dylib ]; then
  answered=$(sed -n 's/^INTERPOSE([^,]*, *\([A-Za-z_0-9]*\)).*/\1/p' "$SRC")
  imports=$(nm -u "$LIB" | sed 's/^_//')
else
  answered=$(nm -D --defined-only "$O/libcrlibm_shim.so" | awk '{print $3}')
  imports=$(nm -D --undefined-only "$LIB" | awk '{print $2}' | sed 's/@.*//')
fi
[ -n "$imports" ] || void "no imports read from $LIB"
missing=""; seen=""
for s in $imports; do
  case $s in
    sin|cos|tan|asin|acos|atan|atan2|sincos|__sincos|__sincos_stret|sinh|cosh|tanh|exp|exp2|exp10|__exp10|expm1|log|log10|log2|log1p|pow|cbrt|hypot|erf|erfc|lgamma|tgamma)
      seen="$seen $s"
      echo "$answered" | grep -qx "$s" || missing="$missing $s" ;;
  esac
done
[ -z "$missing" ] || void "libm imports not in the shim:$missing"
echo "libm imports of $(basename "$LIB"), all answered:$seen" >&2
echo "$O/libcrlibm_shim.$EXT"
