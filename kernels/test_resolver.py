"""Check the input-path resolver against both Kaggle mount layouts using a fake /kaggle tree."""
import json
import re
import shutil
import sys
from pathlib import Path

nb = json.load(open(sys.argv[1], encoding="utf-8"))
cell = next("".join(c["source"]) for c in nb["cells"] if "_resolve_input" in "".join(c["source"]))
resolver = cell[cell.index("# --- Talyxion"):cell.index("# --- end Talyxion resolver ---")]
consts = "\n".join(l for l in cell.splitlines()
                   if re.match(r"^(WHEELHOUSE_DIR|MODEL_DIR|DRAFT_MODEL_DIR|ORIG_BUNDLE_DIR)\s+=\s+'", l))
root = Path("/kaggle/input")
LAYOUTS = {
    "new": {"datasets/dfranzen/pennyroyal-v253": None,
            "models/dfranzen/intel-qwen3.8-flash-next-w4a16-autoround/transformers/default/1": "config.json",
            "models/dfranzen/albucino-qwen3-8-flash-next-drafter/transformers/default/1": None,
            "datasets/dfranzen/taaf-kaggle-source-bundle-copy": "deploy_target.pkl",
            "competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels": None},
    "legacy": {"pennyroyal-v253": None,
               "intel-qwen3.8-flash-next-w4a16-autoround/transformers/default/1": "config.json",
               "albucino-qwen3-8-flash-next-drafter/transformers/default/1": None,
               "taaf-kaggle-source-bundle-copy": "deploy_target.pkl",
               "arc-prize-2026-arc-agi-3/arc_agi_3_wheels": None},
}
failed = False
for layout, dirs in LAYOUTS.items():
    if Path("/kaggle").exists():
        shutil.rmtree("/kaggle")
    for d, f in dirs.items():
        (root / d).mkdir(parents=True, exist_ok=True)
        if f:
            (root / d / f).write_text("x")
    ns = {"Path": Path}
    exec(consts + "\n" + resolver, ns)
    vals = {k: ns[k] for k in ["WHEELHOUSE_DIR", "MODEL_DIR", "DRAFT_MODEL_DIR", "ORIG_BUNDLE_DIR", "COMP_DIR"]}
    ok = all(Path(v).exists() for v in vals.values())
    failed |= not ok
    print(layout, "ALL RESOLVED" if ok else "MISSING", {k: Path(v).as_posix() for k, v in vals.items()})
shutil.rmtree("/kaggle")
sys.exit(1 if failed else 0)
