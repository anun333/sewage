#!/bin/sh
# fixcheck.sh WORK CHECKS: test the two WNTR fixes against WNTR main, on one Linux host.
#
# WORK holds src-base.tar, src-585.tar and src-584.tar (git archive of WNTR main and of
# the two fix branches, each with prefix src-NAME/) and nets/ (the networks that
# CHECKS/networks.txt lists). CHECKS is sewage's checks/wntr (wntrrun.py, wntrcmp.py,
# controls.sh, networks.txt, constraints.txt). Everything is written under WORK:
#   results/   what is kept: logs, test reports, digests, comparisons, timings
#   venv/      one environment for all three trees (pip cache in WORK/pipcache)
#   src-*/     the trees, each built in place (setup.py build_ext --inplace)
#   runs/      wntrrun.py output (float64 files, about 26 MB a run)
# Steps:
#   1. venv: WNTR's dependencies, its optional and test extras, pinned with
#      constraints.txt where it pins them; pip freeze to results/.
#   2. Build each tree in place. Compile evaluator.cpp alone with g++ and clang++,
#      -Wall -Wextra, as C++98 and C++17, for base and 585 (new warnings?).
#   3. SWIG: regenerate evaluator_wrap.cpp (-c++ -python -builtin, as setup.py's
#      use_swig does) for base and for 585, build 585 with its regenerated wrapper and
#      run test_aml.py on it; diff the two regenerated wrappers.
#   4. pytest in each tree: SUITE=full is CI's core selection (-m "not extensions"),
#      SUITE=quick its quick test (-m "not time_consuming and not extensions"), both
#      with --doctest-modules --doctest-glob="*.rst". Controls: base with the two new
#      test files, which must fail there.
#   5. wntrrun.py on every network: base and 585 three times each with string hashing
#      and address randomisation on (a fresh process each, as a user gets), and once
#      with PYTHONHASHSEED=4242, randomisation off and a longer environment (another
#      layout); 584 once. Then wntrcmp.py: spread base runs against 585 runs, digcmp
#      within each, cmp base against 585, and digcmp base against 584 for EPANET;
#      controls.sh on one run.
#   6. PERF=1: Net6 under WNTRSimulator, base and 585 alternately, three times each,
#      one process at a time on one CPU.
# Each step's exit status goes to results/rc.txt. On a shared host run this under
# nice -n 19; CPUS (default 0-3) is the taskset list and NPAR (default 4) how many
# jobs run at once. Solvers run on one thread. POSIX sh plus GNU xargs, util-linux,
# python3 with venv, g++, clang++ and swig.
set -eu
[ $# -eq 2 ] || { sed -n '2,36p' "$0"; exit 2; }
W=$(cd "$1" && pwd); C=$(cd "$2" && pwd)
CPUS=${CPUS:-0-3}; NPAR=${NPAR:-4}; SUITE=${SUITE:-quick}; PERF=${PERF:-0}
R=$W/results; mkdir -p "$R" "$W/runs" "$W/piptmp"
PIN="taskset -c $CPUS"
V=$W/venv; PY=$V/bin/python
rc() { echo "$1 $2" >> "$R/rc.txt"; }
# a clean environment for every Python run; PYTHONPATH picks the tree
penv() {  # penv TREE CMD...
  t=$1; shift
  env -i PATH="$V/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 MPLBACKEND=Agg \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="$W/$t" "$@"
}

{
  echo "host $(uname -srm)"; echo "cpu $(grep -m1 -E 'model name|^CPU part' /proc/cpuinfo | sed 's/.*: //')"
  echo "libc $(ldd --version 2>&1 | head -1)"; echo "python $(python3 --version 2>&1)"
  echo "g++ $(g++ --version | head -1)"; echo "clang++ $(clang++ --version | head -1)"
  echo "swig $(swig -version | sed -n 2p)"; echo "SUITE=$SUITE PERF=$PERF CPUS=$CPUS NPAR=$NPAR"
  for t in base 585 584; do echo "src-$t.tar sha256 $(sha256sum "$W/src-$t.tar" | cut -d' ' -f1)"; done
} > "$R/host.txt"

# 1. environment
if [ ! -x "$PY" ]; then
  python3 -m venv "$V"
  s=0
  PIP_CACHE_DIR=$W/pipcache TMPDIR=$W/piptmp $PIN "$PY" -m pip install -q -c "$C/constraints.txt" \
    numpy scipy networkx pandas matplotlib setuptools \
    pytest nbformat nbconvert ipykernel coverage \
    'plotly<6.0' folium utm openpyxl geopandas rasterio rtree > "$R/pip.log" 2>&1 || s=$?
  rc pip-install "$s"
  if [ "$s" != 0 ]; then  # without the optional extra; tests that need it then skip or fail
    s=0
    PIP_CACHE_DIR=$W/pipcache TMPDIR=$W/piptmp $PIN "$PY" -m pip install -q -c "$C/constraints.txt" \
      numpy scipy networkx pandas matplotlib setuptools \
      pytest nbformat nbconvert ipykernel coverage > "$R/pip-noopt.log" 2>&1 || s=$?
    rc pip-install-without-optional "$s"
  fi
  "$PY" -m pip freeze > "$R/pip-freeze.txt"
fi

# 2. builds, and evaluator.cpp alone under two compilers and two standards
for t in base 585 584; do
  if [ ! -d "$W/src-$t" ]; then tar -xf "$W/src-$t.tar" -C "$W"; fi
  s=0; (cd "$W/src-$t" && penv "src-$t" $PIN "$PY" setup.py build_ext --inplace) > "$R/build-$t.log" 2>&1 || s=$?
  rc "build-$t" "$s"
done
for t in base 585; do
  for cc in g++ clang++; do
    for std in c++98 c++17; do
      s=0; $cc -std=$std -Wall -Wextra -fsyntax-only "$W/src-$t/wntr/sim/aml/evaluator.cpp" \
        > "$R/warn-$t-$cc-$std.txt" 2>&1 || s=$?
      rc "warn-$t-$cc-$std" "$s"
    done
  done
done

# 3. SWIG: regenerated wrappers, and 585 built and tested with its own
for t in base 585; do
  d=$W/swig-$t; rm -rf "$d"; mkdir -p "$d"; cp "$W/src-$t/wntr/sim/aml/"*.i "$W/src-$t/wntr/sim/aml/"*.hpp "$d/"
  s=0; (cd "$d" && swig -c++ -python -builtin -o evaluator_wrap.cpp evaluator.i) > "$R/swig-$t.log" 2>&1 || s=$?
  rc "swig-$t" "$s"
done
diff "$W/swig-base/evaluator_wrap.cpp" "$W/swig-585/evaluator_wrap.cpp" > "$R/swig-wrap-base-vs-585.diff" || true
if [ ! -d "$W/src-585swig" ]; then
  mkdir -p "$W/x" && tar -xf "$W/src-585.tar" -C "$W/x" && mv "$W/x/src-585" "$W/src-585swig" && rmdir "$W/x"
  cp "$W/swig-585/evaluator_wrap.cpp" "$W/swig-585/evaluator.py" "$W/src-585swig/wntr/sim/aml/"
fi
s=0; (cd "$W/src-585swig" && penv src-585swig $PIN "$PY" setup.py build_ext --inplace) > "$R/build-585swig.log" 2>&1 || s=$?
rc build-585swig "$s"
s=0; (cd "$W/src-585swig" && penv src-585swig $PIN "$PY" -m pytest -p no:cacheprovider -q -rfE \
  wntr/tests/test_aml.py) > "$R/pytest-585swig-aml.log" 2>&1 || s=$?
rc pytest-585swig-aml "$s"

# 4. test suites, and the controls (the new tests on base must fail)
if [ ! -d "$W/src-basectl" ]; then
  mkdir -p "$W/x" && tar -xf "$W/src-base.tar" -C "$W/x" && mv "$W/x/src-base" "$W/src-basectl" && rmdir "$W/x"
  cp "$W/src-585/wntr/tests/test_aml.py" "$W/src-basectl/wntr/tests/test_aml.py"
  cp "$W/src-584/wntr/tests/test_epanet_toolkit.py" "$W/src-basectl/wntr/tests/test_epanet_toolkit.py"
fi
s=0; (cd "$W/src-basectl" && penv src-basectl $PIN "$PY" setup.py build_ext --inplace) > "$R/build-basectl.log" 2>&1 || s=$?
rc build-basectl "$s"
if [ "$SUITE" = full ]; then SEL="not extensions"; else SEL="not time_consuming and not extensions"; fi
cat > "$W/job4.sh" <<EOF
#!/bin/sh
# job4.sh TREE: one pytest run, as step 4 of fixcheck.sh
t=\$1; cd "$W/src-\$t"
s=0
env -i PATH="$V/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 MPLBACKEND=Agg OMP_NUM_THREADS=1 \\
  OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$W/src-\$t" \\
  $PIN "$PY" -m pytest -p no:cacheprovider -q -rfEs -m "$SEL" --ignore=wntr/extensions \\
  --doctest-modules --doctest-glob="*.rst" --junitxml="$R/pytest-\$t.xml" wntr > "$R/pytest-\$t.log" 2>&1 || s=\$?
echo "pytest-\$t \$s" >> "$R/rc.txt"
EOF
cat > "$W/jobctl.sh" <<EOF
#!/bin/sh
# jobctl.sh: the new tests on base, which must fail
cd "$W/src-basectl"
s=0
env -i PATH="$V/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 MPLBACKEND=Agg OMP_NUM_THREADS=1 \\
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$W/src-basectl" \\
  $PIN "$PY" -m pytest -p no:cacheprovider -q -rfE \\
  "wntr/tests/test_aml.py::TestStructureOrder" "wntr/tests/test_epanet_toolkit.py::TestLinuxMachine" \\
  > "$R/pytest-control-base-newtests.log" 2>&1 || s=\$?
echo "pytest-control-base-newtests \$s" >> "$R/rc.txt"
EOF
chmod +x "$W/job4.sh" "$W/jobctl.sh"
printf '%s\n' "$W/job4.sh base" "$W/job4.sh 585" "$W/job4.sh 584" "$W/jobctl.sh" \
  | xargs -P "$NPAR" -I CMD sh -c CMD

# 5. repeat runs of every network
LONG=$(printf '%04000d' 0)
cat > "$W/job5.sh" <<EOF
#!/bin/sh
# job5.sh TREE TAG [layout]: one wntrrun.py run, as step 5 of fixcheck.sh
t=\$1; tag=\$2; s=0
if [ "\${3:-}" = layout ]; then
  env -i PATH="$V/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 MPLBACKEND=Agg OMP_NUM_THREADS=1 \\
    OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$W/src-\$t" \\
    PYTHONHASHSEED=4242 PADDING="$LONG" $PIN setarch "\$(uname -m)" -R \\
    "$PY" -s "$C/wntrrun.py" run "$W/nets" "$W/runs" "\$tag" "$C/networks.txt" > "$R/run-\$tag.log" 2>&1 || s=\$?
else
  env -i PATH="$V/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 MPLBACKEND=Agg OMP_NUM_THREADS=1 \\
    OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$W/src-\$t" \\
    $PIN "$PY" -s "$C/wntrrun.py" run "$W/nets" "$W/runs" "\$tag" "$C/networks.txt" > "$R/run-\$tag.log" 2>&1 || s=\$?
fi
echo "run-\$tag \$s" >> "$R/rc.txt"
EOF
chmod +x "$W/job5.sh"
printf '%s\n' "$W/job5.sh base base-r1" "$W/job5.sh 585 585-r1" "$W/job5.sh base base-r2" \
  "$W/job5.sh 585 585-r2" "$W/job5.sh base base-r3" "$W/job5.sh 585 585-r3" \
  "$W/job5.sh base base-lay layout" "$W/job5.sh 585 585-lay layout" "$W/job5.sh 584 584-r1" \
  | xargs -P "$NPAR" -I CMD sh -c CMD
for tag in base-r1 base-r2 base-r3 base-lay 585-r1 585-r2 585-r3 585-lay 584-r1; do
  for f in digests.txt times.txt meta.json; do
    [ -f "$W/runs/$tag/$f" ] && cp "$W/runs/$tag/$f" "$R/runs-$tag-$f"
  done
done
cmpx() {  # cmpx NAME ARGS...: one wntrcmp.py comparison, kept in results/
  n=$1; shift; s=0
  python3 -I "$C/wntrcmp.py" "$@" > "$R/cmp-$n.txt" 2>&1 || s=$?
  rc "cmp-$n" "$s"
}
cmpx spread-wntr spread "$W/runs/base-r1" "$W/runs/base-r2" "$W/runs/base-r3" "$W/runs/base-lay" -- \
  "$W/runs/585-r1" "$W/runs/585-r2" "$W/runs/585-r3" "$W/runs/585-lay" --sim wntr
for k in r2 r3 lay; do
  cmpx "dig-585-r1-vs-$k" digcmp "$W/runs/585-r1/digests.txt" "$W/runs/585-$k/digests.txt" --sim wntr
  cmpx "dig-base-r1-vs-$k" digcmp "$W/runs/base-r1/digests.txt" "$W/runs/base-$k/digests.txt" --sim wntr
done
cmpx base-vs-585-wntr cmp "$W/runs/base-r1" "$W/runs/585-r1" --sim wntr
cmpx dig-585-vs-base-epanet digcmp "$W/runs/base-r1/digests.txt" "$W/runs/585-r1/digests.txt" --sim epanet
cmpx dig-584-vs-base-epanet digcmp "$W/runs/base-r1/digests.txt" "$W/runs/584-r1/digests.txt" --sim epanet
s=0; sh "$C/controls.sh" "$W/runs/585-r1" "$W/ctl" > "$R/controls.txt" 2>&1 || s=$?
rc controls "$s"

# 6. timing
if [ "$PERF" = 1 ]; then
  P1=$(echo "$CPUS" | cut -d- -f1 | cut -d, -f1)
  : > "$R/perf-net6.txt"
  for i in 1 2 3; do
    for t in base 585; do
      penv "src-$t" taskset -c "$P1" "$PY" -s -c 'import sys, time, wntr
wn = wntr.network.WaterNetworkModel(sys.argv[1])
t0 = time.perf_counter(); wntr.sim.WNTRSimulator(wn).run_sim()
print("%s %d %.2f" % (sys.argv[2], int(sys.argv[3]), time.perf_counter() - t0))' \
        "$W/nets/wntr/Net6.inp" "$t" "$i" >> "$R/perf-net6.txt" 2>> "$R/perf-net6.err" || rc "perf-$t-$i" $?
    done
  done
fi
echo "finished" >> "$R/rc.txt"
