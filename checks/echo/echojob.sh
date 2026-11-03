#!/bin/sh
# Run echo_screen.py on cfarm421 under a run notice. The data folder holds EPA's
# downloads, fetched beforehand (see README.md): the state's DMR zips for each fiscal
# year, its EFF_VIOLATIONS zip, npdes_downloads.zip and REF_STATISTICAL_BASE.csv.
# NOTICE names the run-notice tool.
#   sh echojob.sh WORKDIR STATE FY0 FY1
set -u
W=$1 ST=$2 FY0=$3 FY1=$4
NOTICE=${NOTICE:-$HOME/bin/notice}
cd "$W" || exit 2
$NOTICE start sewage-n2 --job "ECHO screen of $ST sewage plants, FY$FY0-FY$FY1 (Python, one process)" \
    --cores 1 --mem 4 --hours 0.5 --nice 19 \
    --intent "screening EPA's public discharge-monitoring data (sewage project)"
trap '$NOTICE end sewage-n2' EXIT
trap 'exit 1' INT TERM
mkdir -p results
nice -n 19 python3 -I echo_screen.py --data data --state "$ST" --fy "$FY0" "$FY1" \
    --tsv "results/plants-$ST-FY$FY0-FY$FY1.tsv" --flags "results/flags-$ST-FY$FY0-FY$FY1.tsv" > "results/screen-$ST-FY$FY0-FY$FY1.md" 2> results/stderr.txt
echo "exit $?" >> "results/screen-$ST-FY$FY0-FY$FY1.md"
cp data/SHA256SUMS data/FETCHED results/
