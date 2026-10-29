#!/bin/sh
# setup-envs.sh: three Python environments under ~/sewage-bsm1/env (qsd, bsm2, wt), from the git-archive
# sources in src/ and PyPI; every cache kept inside ~/sewage-bsm1.
set -eu
W=$HOME/sewage-bsm1
export PIP_CACHE_DIR=$W/cache/pip XDG_CACHE_HOME=$W/cache MPLCONFIGDIR=$W/cache/mpl
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 MAKEFLAGS=-j16
cd $W
mk() { python3 -m venv env/$1 && env/$1/bin/pip install -q --upgrade pip; }
case "${1:-all}" in
qsd|all)
  mk qsd
  env/qsd/bin/pip install -q ./src/qsdsan openpyxl
  env/qsd/bin/pip install -q --no-deps ./src/exposan        # EXPOsan main pins qsdsan==1.5.3; QSDsan main is 1.6.0
  env/qsd/bin/pip freeze > logs/freeze-qsd.txt ;;
esac
case "${1:-all}" in
bsm2|all)
  mk bsm2
  SETUPTOOLS_SCM_PRETEND_VERSION=0.0.16+g73caa8b env/bsm2/bin/pip install -q ./src/bsm2-python
  env/bsm2/bin/pip freeze > logs/freeze-bsm2.txt ;;
esac
case "${1:-all}" in
wt|all)
  mk wt
  env/wt/bin/pip install -q ./src/watertap
  env/wt/bin/pip freeze > logs/freeze-wt.txt ;;
esac
