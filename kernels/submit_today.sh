#!/usr/bin/env bash
# One daily competition submission, run by Windows Task Scheduler ("ARC3 daily submit"; survives Claude sessions).
# Idempotent: exits if today's UTC slot is already used. Submits what kernels/next_submission.txt names
# ("slug version message"). On Saturdays it waits until 02:00 UTC: the weekly quota reset at 00:00 UTC slowed
# /kaggle/input 4-5x (JustAdev742's log) and combo3 #1 submitted then scored 0.00.
set -u
cd /d/dev_tools || exit 1
K="./kaggle_venv/Scripts/python.exe -m kaggle"  # %TEMP%kgl was broken by a Temp cleanup on 10-11
LOG=/d/arc3_paper/results/scheduler.log
PLAN=/d/arc3_paper/kernels/next_submission.txt
[ "$(date -u +%Y%m%d)" -gt 20261102 ] && exit 0
if [ "$(date -u +%u)" = 6 ]; then
  until [ "$(date -u +%H%M)" -ge 0200 ]; do sleep 60; done
fi
D=$(date -u +%F); DD=$(date -u +%Y%m%d)
latest() { $K competitions submissions -c arc-prize-2026-arc-agi-3 --csv 2>/dev/null | grep -E '^[0-9]+,' | head -1; }  # skip CLI warning lines
if latest | grep -q "$D"; then
  echo "$(date -u +%F' '%H:%M) slot $DD already used (task run)" >> $LOG
  exit 0
fi
# several plan lines = alternate by UTC day (line = day number mod N)
N=$(grep -c . "$PLAN"); IDX=$(( $(date -u +%s) / 86400 % N + 1 ))
read -r SLUG VER MSG <<< "$(grep . "$PLAN" | sed -n "${IDX}p")"
for i in $(seq 1 20); do
  $K competitions submit -c arc-prize-2026-arc-agi-3 -k "thnhnguyn2001/$SLUG" -v "$VER" -f submission.parquet \
     -m "$MSG (slot $DD)" >> $LOG 2>&1
  sleep 60
  if latest | grep -q "$D"; then
    echo "$(date -u +%F' '%H:%M) slot $DD OK: $(latest)" >> $LOG
    exit 0
  fi
done
echo "$(date -u +%F' '%H:%M) slot $DD FAILED after retries" >> $LOG
