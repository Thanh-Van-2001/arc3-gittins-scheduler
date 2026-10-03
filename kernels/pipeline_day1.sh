#!/usr/bin/env bash
# 1) wait for throughput configs C,D to finish (2-GPU-session limit)
# 2) push path-hardened v2 of both A/B arms
# 3) wait for the gittins commit, then submit it at 00:05 UTC (fallback: version 1)
set -u
K="/c/Users/Admin/AppData/Local/Temp/kgl/Scripts/python.exe -m kaggle"
st() { $K kernels status "thnhnguyn2001/$1" 2>&1 | tail -1; }
terminal() { case "$(st "$1")" in *COMPLETE*|*ERROR*|*CANCEL*) return 0;; *) return 1;; esac; }

until terminal arc3-talyxion-tput-c && terminal arc3-talyxion-tput-d; do sleep 120; done
echo "$(date -u +%H:%M) C,D done"
for k in base gittins; do $K kernels push -p "D:/arc3_paper/kernels/$k" 2>&1 | tail -1; done
until terminal arc3-talyxion-gittins; do sleep 120; done
G=$(st arc3-talyxion-gittins); echo "$(date -u +%H:%M) gittins v2: $G"
VER=2; case "$G" in *COMPLETE*) ;; *) VER=1;; esac
until [ "$(date -u +%Y%m%d%H%M)" -ge 202610040005 ]; do sleep 120; done
$K competitions submit -c arc-prize-2026-arc-agi-3 -k thnhnguyn2001/arc3-talyxion-gittins -v $VER -f submission.parquet \
   -m "A/B gittins #1 (Franzen M2 + Bayesian Gittins scheduler, v$VER)" 2>&1 | tail -2
$K competitions submissions -c arc-prize-2026-arc-agi-3 --csv 2>&1 | head -3
echo "$(date -u +%H:%M) submitted gittins v$VER"
