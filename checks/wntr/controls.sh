#!/bin/sh
# controls.sh RUN SCRATCH
#
# Planted faults that wntrcmp.py must catch. RUN is one finished wntrrun.py run
# directory (RUNS/TAG); SCRATCH is an empty or absent directory that receives two
# copies of it, A and B. B gets each fault in turn, then is restored from A:
#   1. no fault: cmp and digcmp IDENTICAL (the baseline)
#   2. the lowest bit of one float64 flipped (wntr/Net3, WNTRSimulator, node
#      pressure, value 100): cmp DIFFERS, located, 1 ulp
#   3. one character of one digest changed: digcmp DIFFERS
#   4. one value file deleted: cmp VOID
#   5. one digest line deleted: digcmp VOID
#   6. a simulator that raised (an "error" line): digcmp VOID
# Prints each verdict and "controls: N of 6 caught"; exit 0 only if all 6 were.
set -eu
[ $# -eq 2 ] || { sed -n '2,15p' "$0"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$1" && pwd); S=$2
mkdir -p "$S"; S=$(cd "$S" && pwd)
A=$S/A; B=$S/B; rm -rf "$A" "$B"; cp -r "$R" "$A"
fresh() { rm -rf "$B"; cp -r "$A" "$B"; }
ok=0
check() {  # check N WANT CMD... : run wntrcmp, compare its last line with WANT
  n=$1; want=$2; shift 2
  out=$(python3 -I "$HERE/wntrcmp.py" "$@" 2>&1) || true
  got=$(printf '%s\n' "$out" | tail -1)
  if [ "$got" = "$want" ]; then ok=$((ok + 1)); r=caught; else r=MISSED; fi
  echo "control $n: want $want, got $got: $r"
  printf '%s\n' "$out" | grep -v -E 'IDENTICAL \(' | sed -n '1,3p' | sed 's/^/    /'
}
fresh
c1a=$(python3 -I "$HERE/wntrcmp.py" cmp "$A" "$B" | tail -1) || true
check 1 IDENTICAL digcmp "$A/digests.txt" "$B/digests.txt"
[ "$c1a" = IDENTICAL ] || { echo "control 1: cmp of two copies said $c1a"; ok=$((ok - 1)); }

python3 -I -c 'import sys
p = sys.argv[1]; b = bytearray(open(p, "rb").read()); b[8 * 100] ^= 1; open(p, "wb").write(b)' \
  "$B/wntr-Net3/wntr/node.pressure.f64"
check 2 DIFFERS cmp "$A" "$B" --sim wntr

fresh
awk '!/^#/ && !done && $3 == "node.head" { $4 = (substr($4, 1, 1) == "0" ? "1" : "0") substr($4, 2); done = 1 } { print }' \
  "$A/digests.txt" > "$B/digests.txt"
check 3 DIFFERS digcmp "$A/digests.txt" "$B/digests.txt"

fresh
rm "$B/wntr-Net1/wntr/link.flowrate.f64"
check 4 VOID cmp "$A" "$B"

fresh
awk '!/^#/ && $3 == "node.demand" && !done { done = 1; next } { print }' "$A/digests.txt" > "$B/digests.txt"
check 5 VOID digcmp "$A/digests.txt" "$B/digests.txt"

fresh
awk '!/^#/ && $1 == "wntr/Net1" && $2 == "wntr" { if (!done) print $1, $2, "error", "-", "OSError"; done = 1; next } { print }' \
  "$A/digests.txt" > "$B/digests.txt"
check 6 VOID digcmp "$A/digests.txt" "$B/digests.txt"

rm -rf "$A" "$B"
echo "controls: $ok of 6 caught"
[ "$ok" = 6 ]
