#!/usr/bin/env bash
# Wait for a kernel to finish, then fetch its logs (not the large artefacts) into results/<name>.
cd /d/dev_tools
K="./kaggle_venv/Scripts/python.exe -m kaggle"  # %TEMP%kgl was broken by a Temp cleanup on 10-11
k=$1
while :; do
  s=$($K kernels status thnhnguyn2001/arc3-talyxion-$k 2>&1 | tail -1)
  case "$s" in *COMPLETE*|*ERROR*|*CANCEL*) break;; esac
  sleep 180
done
echo "$(date -u +%F' '%H:%M) $k: $s" >> /d/arc3_paper/results/scheduler.log
mkdir -p /d/arc3_paper/results/$k
$K kernels output thnhnguyn2001/arc3-talyxion-$k -p D:/arc3_paper/results/$k --file-pattern '.*(\.log|summary\.txt|benchmark\.json|\.txt)$' -o -q 2>&1 | tail -2
echo "$k: $s"; ls /d/arc3_paper/results/$k | head -30
