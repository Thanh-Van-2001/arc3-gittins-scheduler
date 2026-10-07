#!/usr/bin/env bash
# Daily combo submissions (slots 2026-10-09 .. 2026-10-14) and the Saturday throughput batch.
# Stop this task to change the plan; per-slot output goes to results/scheduler.log.
set -u
cd /c/Users/Admin/AppData/Local/Temp
K="./kgl/Scripts/python.exe -m kaggle"
LOG=/d/arc3_paper/results/scheduler.log
st() { $K kernels status "thnhnguyn2001/$1" 2>&1 | tail -1; }
done_k() { case "$(st "$1")" in *COMPLETE*|*ERROR*|*CANCEL*) return 0;; *) return 1;; esac; }

submit_slot() {  # $1 = YYYYMMDD
  until [ "$(date -u +%Y%m%d%H%M)" -ge "${1}0000" ]; do sleep 30; done
  $K competitions submit -c arc-prize-2026-arc-agi-3 -k thnhnguyn2001/arc3-talyxion-combo -v 1 -f submission.parquet \
     -m "Final: Franzen M2 + Bayesian Gittins (offset 0.85) + retained-function fix (slot $1)" >> $LOG 2>&1
  echo "$(date -u +%F' '%H:%M) submitted combo for slot $1: $($K competitions submissions -c arc-prize-2026-arc-agi-3 --csv 2>&1 | sed -n '2p')" >> $LOG
}

saturday_batch() {
  until [ "$(date -u +%Y%m%d%H%M)" -ge 202610100010 ]; do sleep 60; done
  for pair in "a30 h30" "i30 j30"; do
    for k in $pair; do echo "$(date -u +%H:%M) push $k: $($K kernels push -p D:/arc3_paper/kernels/tput/$k 2>&1 | tail -1)" >> $LOG; done
    for k in $pair; do until done_k "arc3-talyxion-tput-$k"; do sleep 120; done; echo "$(date -u +%H:%M) $k: $(st arc3-talyxion-tput-$k)" >> $LOG; done
  done
  (cd /d/arc3_paper/analysis && rm -rf ../results/tput/a30 ../results/tput/h30 ../results/tput/i30 ../results/tput/j30 && python tput.py a30 h30 i30 j30) >> $LOG 2>&1
}

for d in 20261009 20261010; do submit_slot $d; done
saturday_batch &
for d in 20261011 20261012 20261013 20261014; do submit_slot $d; done
wait
echo "$(date -u +%F' '%H:%M) scheduler finished" >> $LOG
