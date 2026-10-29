#!/bin/sh
# job1.sh NAME CMD...: one job of cfarm-job.sh, run at nice 19 and logged to logs/NAME.log, whose last
# line is "ok SECONDS s" or "FAILED SECONDS s". Skipped when /tmp/$USER-PLEASE-STOP exists or the
# job's log already ends in ok.
n=$1; shift
if [ -e /tmp/$USER-PLEASE-STOP ]; then echo "$n: stop requested, not started" >> logs/stopped.txt; exit 0; fi
if [ -f logs/$n.log ] && tail -n 1 logs/$n.log | grep -q '^ok '; then exit 0; fi
s=$(date +%s)
if nice -n 19 "$@" > logs/$n.log 2>&1; then echo "ok $(( $(date +%s) - s )) s" >> logs/$n.log
else echo "FAILED $(( $(date +%s) - s )) s" >> logs/$n.log; fi
${NOTICE:-$HOME/bin/notice} refresh sewage-bsm1 > /dev/null 2>&1 || true
