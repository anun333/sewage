#!/bin/sh
# libm-dispatch.sh BUILD_DIR SRC SUITE WORK CORE_MATH_DIR
#
# Linux, glibc, x86-64 with FMA only. One SWMM binary, two CPUs' worth of
# libm: glibc picks FMA or non-FMA code for exp, log, pow, sin, cos, ... at
# run time, and GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX2,-FMA makes it pick the
# non-FMA code here, as on a CPU without FMA (it gives the same .out as
# qemu-x86_64 -cpu Nehalem). The models run four ways:
#   glibc          glibc, FMA code      | the control: these two must differ
#   glibc-nofma    glibc, non-FMA code  | on at least one model, or VOID
#   cr             every libm function libswmm5 imports answered by CORE-MATH
#   cr-nofma       (correctly rounded) through LD_PRELOAD, under both hwcaps
# Verdict: IDENTICAL when cr and cr-nofma agree on every model (exit 0),
# DIFFERS when they don't (1), VOID when the control does not differ, a libm
# import is missing from the shim, or a run fails (2).
#
# BUILD_DIR: a build.sh tree (libswmm5 at src/solver); SRC: the SWMM clone
# (for swmm5.h); SUITE: swmm-nrtestsuite's public/; CORE_MATH_DIR: CORE-MATH
# binary64 sources laid out as crnumerics' core-math/ (acos.c ... pow/pow.c).
# Pinned with taskset to $SWMM_CPUS (default 0-3), one run at a time.
set -eu
[ $# -eq 5 ] || { sed -n '2,24p' "$0"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
B=$1; SRC=$2; SUITE=$3; W=$4; CM=$5
MODELS=${MODELS:-"examples/Example1.inp user/user1.inp user/user3.inp user/user5.inp"}
PIN=""; command -v taskset >/dev/null 2>&1 && PIN="taskset -c ${SWMM_CPUS:-0-3}"
CC=${CC:-cc}
NOFMA="glibc.cpu.hwcaps=-AVX2,-FMA"
LIB="$B/src/solver/libswmm5.so"
mkdir -p "$W/shim"

$PIN $CC -O2 -I"$SRC/src/solver/include" -o "$W/swmmquiet" "$HERE/swmmquiet.c" \
    -L"$B/src/solver" -lswmm5 -Wl,-rpath,"$B/src/solver"
for f in acos.c asin.c atan.c cos.c exp.c sin.c tan.c log/log.c log10/log10.c pow/pow.c; do
  $PIN $CC -O2 -fPIC -fno-builtin -I"$CM/$(dirname $f)" -c "$CM/$f" -o "$W/shim/$(basename $f .c).o"
done
$PIN $CC -O2 -fPIC -fno-builtin -c "$HERE/crlibm_shim.c" -o "$W/shim/shim.o"
$PIN $CC -shared -o "$W/libcrlibm_shim.so" "$W"/shim/*.o -lm
SHIM="$W/libcrlibm_shim.so"

# every libm function libswmm5 imports must be in the shim (sincos included:
# gcc makes it from a sin/cos pair, and missing it once left a difference)
missing=""
for s in $(nm -D --undefined-only "$LIB" | awk '{print $2}' | sed 's/@.*//'); do
  case $s in
    sin|cos|tan|asin|acos|atan|atan2|sincos|sinh|cosh|tanh|exp|exp2|expm1|log|log10|log2|log1p|pow|cbrt|hypot|erf|erfc|lgamma|tgamma)
      nm -D --defined-only "$SHIM" | awk '{print $3}' | grep -qx "$s" || missing="$missing $s" ;;
  esac
done
if [ -n "$missing" ]; then echo "libm imports not in the shim:$missing"; echo VOID; exit 2; fi

control=0; fix=0; void=0
for m in $MODELS; do
  n=$(basename "$m" .inp); d="$W/$n"; rm -rf "$d"; mkdir -p "$d"
  cp "$SUITE/$m" "$d/"
  for f in "$(dirname "$SUITE/$m")"/*; do
    case $f in *.inp|*.json) ;; *) [ -f "$f" ] && cp "$f" "$d/" ;; esac
  done
  ( cd "$d"
    $PIN "$W/swmmquiet" "$d/$n.inp" "$d/glibc.rpt" "$d/glibc.out" >/dev/null
    GLIBC_TUNABLES=$NOFMA $PIN "$W/swmmquiet" "$d/$n.inp" "$d/glibc-nofma.rpt" "$d/glibc-nofma.out" >/dev/null
    LD_PRELOAD=$SHIM $PIN "$W/swmmquiet" "$d/$n.inp" "$d/cr.rpt" "$d/cr.out" >/dev/null
    GLIBC_TUNABLES=$NOFMA LD_PRELOAD=$SHIM $PIN "$W/swmmquiet" "$d/$n.inp" "$d/cr-nofma.rpt" "$d/cr-nofma.out" >/dev/null
  ) || { echo "$m: a run failed"; void=1; continue; }
  if python3 -I "$HERE/swmmcmp.py" "$d/glibc.out" "$d/glibc-nofma.out" --rpt "$d/glibc.rpt" "$d/glibc-nofma.rpt" > "$d/control.txt"; then
    c=IDENTICAL; else c=DIFFERS; control=1; fi
  if python3 -I "$HERE/swmmcmp.py" "$d/cr.out" "$d/cr-nofma.out" --rpt "$d/cr.rpt" "$d/cr-nofma.rpt" > "$d/fix.txt"; then
    x=IDENTICAL; else x=DIFFERS; fix=1; fi
  echo "$m: glibc FMA vs non-FMA libm: $c ($(head -1 "$d/control.txt" | cut -c1-90)); CORE-MATH: $x"
done
if [ $void = 1 ] || [ $control = 0 ]; then
  [ $control = 0 ] && echo "control did not differ: glibc's dispatch changed nothing here"
  echo VOID; exit 2
fi
if [ $fix = 1 ]; then echo DIFFERS; exit 1; fi
echo IDENTICAL
