#!/usr/bin/env bash
# Robust scheduler: daily combo submissions with retry + verification, and the Saturday throughput batch.
# The kernel to submit is read from kernels/next_submission.txt at each slot ("slug version message"),
# so the plan can change by editing that file instead of killing this job.
set -u
cd /c/Users/Admin/AppData/Local/Temp
K="./kgl/Scripts/python.exe -m kaggle"
LOG=/d/arc3_paper/results/scheduler.log
PLAN=/d/arc3_paper/kernels/next_submission.txt
st() { $K kernels status "thnhnguyn2001/$1" 2>&1 | tail -1; }
done_k() { case "$(st "$1")" in *COMPLETE*|*ERROR*|*CANCEL*) return 0;; *) return 1;; esac; }
today_submitted() { $K competitions submissions -c arc-prize-2026-arc-agi-3 --csv 2>/dev/null | sed -n '2p' | grep -q "$1"; }

submit_slot() {  # $1 = YYYYMMDD, $2 = YYYY-MM-DD
  until [ "$(date -u +%Y%m%d%H%M)" -ge "${1}0000" ]; do sleep 30; done
  read -r SLUG VER MSG < "$PLAN"
  for i in $(seq 1 30); do
    if today_submitted "$2"; then
      echo "$(date -u +%F' '%H:%M) slot $1 OK: $($K competitions submissions -c arc-prize-2026-arc-agi-3 --csv 2>&1 | sed -n '2p')" >> $LOG
      return
    fi
    $K competitions submit -c arc-prize-2026-arc-agi-3 -k "thnhnguyn2001/$SLUG" -v "$VER" -f submission.parquet -m "$MSG (slot $1)" >> $LOG 2>&1
    sleep 60
  done
  echo "$(date -u +%F' '%H:%M) slot $1 FAILED after retries" >> $LOG
}

saturday_batch() {
  until [ "$(date -u +%Y%m%d%H%M)" -ge 202610100010 ]; do sleep 60; done
  for pair in "a30 h30" "i30 j30"; do
    for k in $pair; do
      for i in 1 2 3 4 5; do
        r=$($K kernels push -p D:/arc3_paper/kernels/tput/$k 2>&1 | tail -1); echo "$(date -u +%H:%M) push $k: $r" >> $LOG
        case "$r" in *successfully*) break;; esac; sleep 120
      done
    done
    for k in $pair; do until done_k "arc3-talyxion-tput-$k"; do sleep 120; done; echo "$(date -u +%H:%M) $k: $(st arc3-talyxion-tput-$k)" >> $LOG; done
  done
  (cd /d/arc3_paper/analysis && rm -rf ../results/tput/a30 ../results/tput/h30 ../results/tput/i30 ../results/tput/j30 && python tput.py a30 h30 i30 j30) >> $LOG 2>&1
}

saturday_batch &
submit_slot 20261010 2026-10-10
submit_slot 20261011 2026-10-11
submit_slot 20261012 2026-10-12
submit_slot 20261013 2026-10-13
submit_slot 20261014 2026-10-14
wait
echo "$(date -u +%F' '%H:%M) scheduler_v2 finished" >> $LOG
