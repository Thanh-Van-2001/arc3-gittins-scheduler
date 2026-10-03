#!/usr/bin/env bash
# Submit the final combo (Gittins calibrated + retained-function fix) in the 2026-10-04 UTC slot.
# Fallback to the validated Gittins v2 if the combo commit fails its checks or is not ready by 01:30 UTC.
set -u
cd /c/Users/Admin/AppData/Local/Temp
K="./kgl/Scripts/python.exe -m kaggle"
st() { $K kernels status "thnhnguyn2001/$1" 2>&1 | tail -1; }

until [ "$(date -u +%Y%m%d%H%M)" -ge 202610040000 ]; do sleep 30; done
echo "$(date -u +%H:%M) slot open"

CHOICE=""
while [ -z "$CHOICE" ]; do
  S=$(st arc3-talyxion-combo)
  case "$S" in
    *COMPLETE*)
      rm -rf kout/combo && mkdir -p kout/combo
      $K kernels output thnhnguyn2001/arc3-talyxion-combo -p kout/combo --file-pattern 'submission\.parquet$' >/dev/null 2>&1
      OK=$(python - <<'EOF'
import json
rows = json.load(open('kout/combo/arc3-talyxion-combo.log', encoding='utf-8', errors='replace'))
txt = ''.join(r.get('data', '') for r in rows)
need = ['harness patch applied successfully', 'gittins patch applied successfully', 'fixes patch applied successfully']
ok = all(n in txt for n in need) and 'Traceback' not in txt
print('OK' if ok else 'BAD ' + ' '.join(str(n in txt) for n in need) + ' traceback=' + str('Traceback' in txt))
EOF
)
      echo "$(date -u +%H:%M) combo commit check: $OK"
      if [ "$OK" = "OK" ] && [ -f kout/combo/submission.parquet ]; then CHOICE="combo"; else CHOICE="gittins"; fi ;;
    *ERROR*|*CANCEL*) echo "$(date -u +%H:%M) combo commit $S"; CHOICE="gittins" ;;
    *)
      if [ "$(date -u +%Y%m%d%H%M)" -ge 202610040130 ]; then echo "combo not ready by 01:30 UTC ($S)"; CHOICE="gittins"; else sleep 60; fi ;;
  esac
done

if [ "$CHOICE" = "combo" ]; then
  $K competitions submit -c arc-prize-2026-arc-agi-3 -k thnhnguyn2001/arc3-talyxion-combo -v 1 -f submission.parquet \
     -m "Final #1: Franzen M2 + Bayesian Gittins (offset 0.85) + retained-function fix" 2>&1 | tail -2
else
  $K competitions submit -c arc-prize-2026-arc-agi-3 -k thnhnguyn2001/arc3-talyxion-gittins -v 2 -f submission.parquet \
     -m "Gittins #1 (Franzen M2 + Bayesian Gittins, v2) [fallback]" 2>&1 | tail -2
fi
$K competitions submissions -c arc-prize-2026-arc-agi-3 --csv 2>&1 | head -3
echo "$(date -u +%H:%M) submitted $CHOICE"
