#!/bin/sh
# check.sh RUNSWMM OUT: what SWMM's engine does with zero roughness on a transect's NC
# line (pyswmm/Stormwater-Management-Model#419 and #420), and with [TRANSECTS] as an
# input file's last section.
#
# The SWMM 5.2 User's Manual ([TRANSECTS]) says of Nleft, Nright and Nchanl: "use 0 if
# no change from previous NC line", as in HEC-2. Every model has two conduits on two
# transects, T1 then T2 (T2 is #420's), and runs for 6 hours. In OUT:
#   inherit            T2's NC is 0 0 0 after T1's 0.01 0.01 0.01
#   explicit           T2's NC is 0.01 0.01 0.01
#   control            T2's NC is 0.02 0.02 0.02 (must differ from explicit: T2's
#                      roughness reaches the results)
#   first-zero         T1's NC is 0 0 0: nothing to inherit
#   overbank-inherit   T1's overbanks 0.05; T2's NC is 0 0 0.02
#   overbank-explicit  T1's overbanks 0.05; T2's NC is 0.05 0.05 0.02
#   overbank-none      T1's overbanks 0.05; T2's NC is 0.02 0.02 0.02 (must differ from
#                      overbank-explicit)
#   transects-last     explicit with [TRANSECTS] moved to the end of the file
# Prints each run's .out sha256 and report ERROR lines, then one line per question:
#   inherit is explicit?                    (#420: does a zero take the previous value?)
#   first-zero has ERROR 227?               (#419: is a zero with nothing to inherit caught?)
#   overbank-inherit is overbank-explicit?  (does a zero overbank take the previous one,
#                                           or mean "no overbank"?)
#   transects-last is explicit?             (is the last transect read when nothing follows?)
# Exit 0 when every run that should run did and both controls differ; 2 (VOID) otherwise.
# POSIX sh.
set -u
[ $# -eq 2 ] || { sed -n '2,29p' "$0"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd); RUN=$1; O=$2; mkdir -p "$O"
sha() { if [ -s "$1" ]; then sha256sum "$1" | cut -c1-16; else echo -; fi; }
errs() { grep -h 'ERROR' "$O/$1.rpt" 2>/dev/null | tr -s ' ' | sed 's/^ //' | tr '\n' ';'; }
for m in inherit explicit control first-zero overbank-inherit overbank-explicit overbank-none transects-last; do
  rm -f "$O/$m.rpt" "$O/$m.out"
  "$RUN" "$HERE/$m.inp" "$O/$m.rpt" "$O/$m.out" > "$O/$m.log" 2>&1
  echo "$m: exit $? .out $(sha "$O/$m.out") errors: $(errs "$m")"
done
for m in inherit explicit control overbank-inherit overbank-explicit overbank-none; do
  if [ "$(sha "$O/$m.out")" = - ] || [ -n "$(errs "$m")" ]; then echo "VOID: $m did not run cleanly"; exit 2; fi
done
same() { [ "$(sha "$O/$1.out")" = "$(sha "$O/$2.out")" ]; }
same explicit control && { echo "VOID: control is identical to explicit"; exit 2; }
same overbank-explicit overbank-none && { echo "VOID: overbank-none is identical to overbank-explicit"; exit 2; }
echo "controls: control differs from explicit, overbank-none differs from overbank-explicit"
if same inherit explicit; then echo "inherit is explicit: yes (T2 took T1's 0.01)"; else echo "inherit is explicit: no"; fi
if grep -q 'ERROR 227' "$O/first-zero.rpt"; then echo "first-zero has ERROR 227: yes"; else echo "first-zero has ERROR 227: no"; fi
if same overbank-inherit overbank-explicit; then
  echo "overbank-inherit is overbank-explicit: yes (T2's zero overbanks took T1's 0.05)"
elif same overbank-inherit overbank-none; then
  echo "overbank-inherit is overbank-explicit: no; it is overbank-none (a zero overbank meant no overbank)"
else
  echo "overbank-inherit is overbank-explicit: no, nor overbank-none"
fi
if same transects-last explicit; then echo "transects-last is explicit: yes"
else echo "transects-last is explicit: no; errors: $(errs transects-last)"; fi
exit 0
