#!/bin/sh
# perfcheck.sh WORK CPU ROUNDS TREE...: WNTRSimulator's run time for each TREE, interleaved.
#
# In WORK (fixcheck.sh's, with venv/ and nets/), each TREE is src-TREE/, built in place
# here from src-TREE.tar if it isn't already. For each of ROUNDS rounds, every TREE runs
# each network in NETS (default "Net6 ky4") in turn, one process at a time, pinned to CPU. Each run prints:
#   TREE NET ROUND seconds set_structure_seconds set_structure_calls pressure_sha256
# (set_structure is timed by wrapping wntr.sim.aml.Model.set_structure; the hash is of
# node pressure, columns sorted, as float64 bytes). Appends to WORK/results/perf.txt.
# Trees that order the equations the same way must print the same hash. Run it under
# nice -n 19. POSIX sh.
set -u
[ $# -ge 4 ] || { sed -n '2,11p' "$0"; exit 2; }
W=$(cd "$1" && pwd); CPU=$2; N=$3; shift 3
R=$W/results; V=$W/venv/bin/python; mkdir -p "$R"
for t in "$@"; do
  if [ ! -d "$W/src-$t" ]; then
    tar -xf "$W/src-$t.tar" -C "$W"
    s=0; (cd "$W/src-$t" && env -i PATH="$W/venv/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 \
      taskset -c "$CPU" "$V" setup.py build_ext --inplace) > "$R/build-$t.log" 2>&1 || s=$?
    echo "build-$t $s" >> "$R/rc.txt"
  fi
done
i=1
while [ "$i" -le "$N" ]; do
  for t in "$@"; do
    for net in ${NETS:-Net6 ky4}; do
      env -i PATH="$W/venv/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 OMP_NUM_THREADS=1 \
        OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$W/src-$t" \
        taskset -c "$CPU" "$V" -s -c 'import sys, time, hashlib
import numpy as np, wntr
from wntr.sim.aml import aml
acc = [0.0, 0]
orig = aml.Model.set_structure
def timed(self):
    t = time.perf_counter(); orig(self); acc[0] += time.perf_counter() - t; acc[1] += 1
aml.Model.set_structure = timed
wn = wntr.network.WaterNetworkModel(sys.argv[1])
t0 = time.perf_counter(); r = wntr.sim.WNTRSimulator(wn).run_sim(); el = time.perf_counter() - t0
p = r.node["pressure"]; p = p[sorted(p.columns)]
h = hashlib.sha256(np.ascontiguousarray(p.values).astype("<f8").tobytes()).hexdigest()[:16]
print("%s %s %s %.2f %.2f %d %s" % (sys.argv[2], sys.argv[3], sys.argv[4], el, acc[0], acc[1], h))' \
        "$W/nets/wntr/$net.inp" "$t" "$net" "$i" >> "$R/perf.txt" 2>> "$R/perf.err" || echo "perf-$t-$net-$i $?" >> "$R/rc.txt"
    done
  done
  i=$((i + 1))
done
echo "perf finished" >> "$R/rc.txt"
