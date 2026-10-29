#!/bin/sh
# wntrjob.sh WORK MODE TAG [REPS]
#
# Installs WNTR the way users get it from PyPI and runs the networks in networks.txt
# through both of its simulators (wntrrun.py). MODE wheel: the wheel for this Python and
# machine (PyPI has Linux wheels for x86-64 only). MODE sdist: the source tarball, built
# by pip, which is what `pip install wntr` does on aarch64 Linux. CFLAGS and CXXFLAGS in
# the environment reach the sdist build (the -ffp-contract=off control). Setting them
# replaces Python's default flags for the C++ files, -O2 included, so pass the whole set
# (see the README's control). fetch.py saves the file in WORK/dl-TAG, its own
# directory, after checking PyPI's sha256. pip installs it
# into WORK/venv-TAG with constraints.txt, no cache and TMPDIR=WORK/piptmp, so no build is
# reused. WORK/runs/TAG/install.txt records the artifact, host and compiler, the build's
# compile lines, each shared library under wntr/ (sha256, ELF machine, compiler, FMA
# instruction count), the EPANET library WNTR loads and pip freeze, with WORK, HOME,
# venv and build-environment (BUILDENV) paths replaced. A venv that already has its
# install.txt is reused, not rebuilt.
# Then wntrrun.py runs REPS more times (default 1). Each run is named by the next free
# name: TAG, TAG-rep2, TAG-rep3, ... These runs use python -I, so string hashing and
# addresses are randomised per process, as for a user. With WNTR_LAYOUT=fixed the runs
# are TAG-fixed1, TAG-fixed2, ... instead, started with a cleared environment,
# PYTHONHASHSEED=0 and address randomisation off (setarch -R). WNTRSimulator's equation
# order follows the heap layout, and this makes it repeat, but only for the same command
# line: a run under another TAG or path gets another order (see README).
# WORK/nets must hold the files networks.txt lists. On Linux every step is pinned with
# taskset to WNTR_CPUS (default 0-3); on a shared host run it under nice -n 19. Solvers
# run on one thread (OMP/OPENBLAS/MKL_NUM_THREADS=1). POSIX sh; needs python3 with venv,
# a C++ compiler for MODE sdist, binutils, util-linux, and network access to PyPI.
set -eu
[ $# -ge 3 ] || { sed -n '2,28p' "$0"; exit 2; }
W=$(cd "$1" && pwd); MODE=$2; TAG=$3; REPS=${4:-1}; V=${WNTR_VERSION:-1.5.0}
HERE=$(cd "$(dirname "$0")" && pwd)
PIN=; command -v taskset >/dev/null 2>&1 && PIN="taskset -c ${WNTR_CPUS:-0-3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PIP_DISABLE_PIP_VERSION_CHECK=1
sha256() { sha256sum "$1" | cut -d' ' -f1; }
clean() { sed -e "s|$W/piptmp/pip-build-env-[A-Za-z0-9_]*|BUILDENV|g" -e "s|$W|WORK|g" -e "s|$HOME|HOME|g"; }
R=$W/runs/$TAG; VE=$W/venv-$TAG; VP=$VE/bin/python
mkdir -p "$R" "$W/piptmp"

runs() {
  i=1; n=0
  while [ "$n" -lt "$REPS" ]; do
    if [ "${WNTR_LAYOUT:-}" = fixed ]; then T=$TAG-fixed$i
    elif [ "$i" = 1 ]; then T=$TAG
    else T=$TAG-rep$i; fi
    i=$((i + 1))
    [ -f "$W/runs/$T/digests.txt" ] && continue
    n=$((n + 1))
    if [ "${WNTR_LAYOUT:-}" = fixed ]; then
      $PIN env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
        MKL_NUM_THREADS=1 PYTHONHASHSEED=0 setarch "$(uname -m)" -R \
        "$VP" -s -P "$HERE/wntrrun.py" run "$W/nets" "$W/runs" "$T" "$HERE/networks.txt" || echo "wntrrun exit $? ($T)"
    else
      $PIN "$VP" -I "$HERE/wntrrun.py" run "$W/nets" "$W/runs" "$T" "$HERE/networks.txt" || echo "wntrrun exit $? ($T)"
    fi
  done
}
if [ -x "$VP" ] && [ -f "$R/install.txt" ]; then
  echo "reusing $VE (install.txt exists)"
  runs
  exit 0
fi

A=$(python3 -I "$HERE/fetch.py" "$MODE" "$V" "$W/dl-$TAG")
python3 -m venv "$VE"
t0=$(date +%s); rc=0
TMPDIR=$W/piptmp $PIN "$VP" -I -m pip install -v --no-cache-dir -c "$HERE/constraints.txt" "$A" \
  > "$R/install.log" 2>&1 || rc=$?
t1=$(date +%s)

{
  echo "artifact $(basename "$A") sha256 $(sha256 "$A")"
  echo "install exit $rc in $((t1 - t0)) s"
  echo "python $("$VP" -I -c 'import platform; print(platform.python_version())')"
  echo "host $(uname -srm)"
  echo "libc $(ldd --version 2>&1 | head -1)"
  echo "cpu $(grep -m1 -E 'model name|^CPU part' /proc/cpuinfo | sed 's/.*: //')"
  echo "cpu has fma: $(grep -m1 -c -w -E 'fma|asimd' /proc/cpuinfo)"
  echo "CFLAGS='${CFLAGS-}' CXXFLAGS='${CXXFLAGS-}'"
  if [ "$MODE" = sdist ]; then
    echo "c++ $(${CXX:-c++} --version 2>&1 | head -1)"
    grep -E '^ *Successfully installed' "$R/install.log" | sed 's/^ */pip: /' | clean
    grep -E -- ' -c [^ ]*\.cpp' "$R/install.log" | sed 's/^ */compile: /' | clean
  fi
  for lib in $(find "$VE" -path '*/site-packages/wntr/*' -name '*.so*' | sort); do
    mach=$(readelf -h "$lib" 2>/dev/null | sed -n 's/^ *Machine: *//p')
    comp=$(readelf -p .comment "$lib" 2>/dev/null | sed -n 's/^ *\[ *0\] *//p' | head -1)
    # n/a when this objdump cannot disassemble the file (another ISA): no instructions seen
    n=$(objdump -d "$lib" 2>/dev/null | awk -F'\t' 'NF >= 3 { ins++ } { for (i = 2; i <= NF; i++) { split($i, w, " ");
          if (w[1] ~ /^(vfn?m(add|sub)[0-9a-z]*|fn?m(add|sub)|fml[as])$/) { n++; break } } }
          END { if (ins) print n + 0; else print "n/a" }')
    # the machine code alone: -g puts the compile flags into the file, so file hashes of two builds always differ
    text=n/a
    if objcopy -O binary --only-section=.text "$lib" "$W/text.bin" 2>/dev/null && [ -s "$W/text.bin" ]; then
      text=$(sha256 "$W/text.bin" | cut -c1-16); fi
    rm -f "$W/text.bin"
    echo "lib ${lib#"$VE"/lib/*/site-packages/} sha256 $(sha256 "$lib" | cut -c1-16) text $text fma $n machine '$mach' compiler '$comp'"
  done
  "$VP" -I "$HERE/wntrrun.py" libcheck 2>&1 | clean || true
  "$VP" -I -m pip freeze 2>&1 | clean
} > "$R/install.txt"
cat "$R/install.txt"
[ "$rc" = 0 ] || { echo "VOID: pip install failed (see $R/install.log)"; exit 2; }
runs
