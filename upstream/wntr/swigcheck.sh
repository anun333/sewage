#!/bin/sh
# swigcheck.sh WORK [TREE]: after fixcheck.sh, regenerate the evaluator's SWIG wrapper with
# SWIG 4.0.2, the version that generated the committed evaluator_wrap.cpp.
#
# fixcheck.sh's step 3 used the host's SWIG 4.3.0, whose SWIG_Python_AppendOutput
# takes a third argument that WNTR's numpy.i does not pass, so no 4.3 wrapper builds,
# with or without the fix. Here, in WORK (fixcheck.sh's, with venv/, src-base/ and
# src-TREE/ built; TREE defaults to 585):
#   1. pip installs swig==4.0.2 into WORK/venv-swig;
#   2. regenerates evaluator_wrap.cpp and evaluator.py (-c++ -python -builtin, as
#      setup.py's use_swig does) from base's and from TREE's sources;
#   3. diffs base's regenerated wrapper with the committed one (the same generator
#      and options should give the same file), and TREE's with base's (only the new
#      `serial` members should appear);
#   4. builds a copy of TREE with its regenerated wrapper and runs test_aml.py on it.
# Writes WORK/results/swig402-*. Run it under nice -n 19. POSIX sh.
set -u
[ $# -ge 1 ] || { sed -n '2,16p' "$0"; exit 2; }
W=$(cd "$1" && pwd); T=${2:-585}; R=$W/results; PIN="taskset -c ${CPUS:-0-3}"
rc() { echo "$1 $2" >> "$R/rc.txt"; }
s=0
[ -x "$W/venv-swig/bin/swig" ] || { python3 -m venv "$W/venv-swig" && \
  PIP_CACHE_DIR=$W/pipcache "$W/venv-swig/bin/python" -m pip install -q swig==4.0.2; } > "$R/swig402-pip.log" 2>&1 || s=$?
rc swig402-install "$s"
SW=$W/venv-swig/bin/swig
"$SW" -version > "$R/swig402-version.txt" 2>&1
for t in base "$T"; do
  d=$W/swig402-$t; rm -rf "$d"; mkdir -p "$d"
  cp "$W/src-$t/wntr/sim/aml/"*.i "$W/src-$t/wntr/sim/aml/"*.hpp "$d/"
  s=0; (cd "$d" && "$SW" -c++ -python -builtin -o evaluator_wrap.cpp evaluator.i) > "$R/swig402-$t.log" 2>&1 || s=$?
  rc "swig402-$t" "$s"
done
diff "$W/src-base/wntr/sim/aml/evaluator_wrap.cpp" "$W/swig402-base/evaluator_wrap.cpp" > "$R/swig402-committed-vs-base.diff"; rc swig402-committed-vs-base-diff $?
diff "$W/src-base/wntr/sim/aml/evaluator.py" "$W/swig402-base/evaluator.py" > "$R/swig402-committed-py-vs-base.diff"; rc swig402-committed-py-vs-base-diff $?
diff "$W/swig402-base/evaluator_wrap.cpp" "$W/swig402-$T/evaluator_wrap.cpp" > "$R/swig402-base-vs-$T.diff"; rc "swig402-base-vs-$T-diff" $?
diff "$W/swig402-base/evaluator.py" "$W/swig402-$T/evaluator.py" > "$R/swig402-base-vs-$T-py.diff"; rc "swig402-base-vs-$T-py-diff" $?
rm -rf "$W/src-swig402"; mkdir -p "$W/x" && tar -xf "$W/src-$T.tar" -C "$W/x" && mv "$W/x/src-$T" "$W/src-swig402" && rmdir "$W/x"
cp "$W/swig402-$T/evaluator_wrap.cpp" "$W/swig402-$T/evaluator.py" "$W/src-swig402/wntr/sim/aml/"
s=0; (cd "$W/src-swig402" && env -i PATH="$W/venv/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 \
  $PIN "$W/venv/bin/python" setup.py build_ext --inplace) > "$R/swig402-build-$T.log" 2>&1 || s=$?
rc "swig402-build-$T" "$s"
s=0; (cd "$W/src-swig402" && env -i PATH="$W/venv/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 \
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$W/src-swig402" $PIN "$W/venv/bin/python" -m pytest \
  -p no:cacheprovider -q -rfE wntr/tests/test_aml.py) > "$R/swig402-pytest-$T-aml.log" 2>&1 || s=$?
rc "swig402-pytest-$T-aml" "$s"
echo "swig402 finished" >> "$R/rc.txt"
