#!/bin/sh
# build.sh SRC BUILD_DIR CC CXX "CFLAGS" [extra cmake args...]
#
# Configures SWMM with an empty CMAKE_BUILD_TYPE, so CFLAGS are the only
# optimisation flags, and builds runswmm and libswmm5 with $SWMM_JOBS jobs
# (default 4).
# On Linux it pins itself to CPUs $SWMM_CPUS (default 0-3) with taskset:
# the limit used on board5, the development machine, was 4 of its 12 threads. Where taskset is
# missing (macOS) it runs unpinned. POSIX sh; needs cmake >= 3.23.
set -eu
[ $# -ge 5 ] || { echo "usage: $0 SRC BUILD_DIR CC CXX CFLAGS [cmake args]"; exit 2; }
SRC=$1; BLD=$2; CC=$3; CXX=$4; CFLAGS=$5; shift 5
PIN=""
if command -v taskset >/dev/null 2>&1; then PIN="taskset -c ${SWMM_CPUS:-0-3}"; fi
rm -rf "$BLD"
mkdir -p "$BLD"
$PIN cmake -S "$SRC" -B "$BLD" \
  -DCMAKE_BUILD_TYPE= \
  -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX" \
  -DCMAKE_C_FLAGS="$CFLAGS" -DCMAKE_CXX_FLAGS="$CFLAGS" \
  -DBUILD_TESTS=OFF -DCMAKE_EXPORT_COMPILE_COMMANDS=ON "$@" >"$BLD/configure.log" 2>&1 \
  || { tail -30 "$BLD/configure.log"; exit 1; }
$PIN cmake --build "$BLD" -j "${SWMM_JOBS:-4}" >"$BLD/build.log" 2>&1 \
  || { tail -30 "$BLD/build.log"; exit 1; }
ls "$BLD/bin/runswmm"
