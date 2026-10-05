#!/usr/bin/env bash
# Usage: submit_slot.sh YYYYMMDD kernel-slug version "message"
set -u
SLOT="$1"; KER="$2"; VER="$3"; MSG="$4"
cd /c/Users/Admin/AppData/Local/Temp
K="./kgl/Scripts/python.exe -m kaggle"
until [ "$(date -u +%Y%m%d%H%M)" -ge "${SLOT}0000" ]; do sleep 30; done
$K competitions submit -c arc-prize-2026-arc-agi-3 -k "thnhnguyn2001/$KER" -v "$VER" -f submission.parquet -m "$MSG" 2>&1 | tail -2
$K competitions submissions -c arc-prize-2026-arc-agi-3 --csv 2>&1 | head -2
echo "$(date -u +%H:%M) submitted $KER v$VER for slot $SLOT"
