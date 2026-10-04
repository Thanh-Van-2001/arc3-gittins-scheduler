#!/usr/bin/env bash
# Submit the combo arm in the next UTC slot (argument: YYYYMMDD of the slot). Edit/stop if the plan changes.
set -u
SLOT="$1"
cd /c/Users/Admin/AppData/Local/Temp
K="./kgl/Scripts/python.exe -m kaggle"
until [ "$(date -u +%Y%m%d%H%M)" -ge "${SLOT}0000" ]; do sleep 30; done
$K competitions submit -c arc-prize-2026-arc-agi-3 -k thnhnguyn2001/arc3-talyxion-combo -v 1 -f submission.parquet \
   -m "Final #${2:-n}: Franzen M2 + Bayesian Gittins (offset 0.85) + retained-function fix" 2>&1 | tail -2
$K competitions submissions -c arc-prize-2026-arc-agi-3 --csv 2>&1 | head -2
echo "$(date -u +%H:%M) submitted combo for slot $SLOT"
