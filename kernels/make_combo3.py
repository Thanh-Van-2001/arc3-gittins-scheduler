"""Build combo3: combo (Franzen M2 + Bayesian Gittins + retained-function fix) on REAP-448 + 14 streams.

The ARC FR-Spec map (--hot-tokens) is left out: built on Windows its sha256 did not match on Kaggle (v1 failed at
the map assert), and it is worth only ~2% tok/s.

Serving changes come from JustAdev742/scottmahony's Apache-2.0 tooling (scripts/build_franzen_nb.py,
scripts/sglang_reap_patch.py, kaggle/franzen/reap448_kept_experts.json, hot_tokens_64k_arc.pt); their gates measured
+14% output tok/s for REAP-448 + 14 streams (same accept length) and ~+2% for the ARC token map.

    python make_combo3.py            # arc3-talyxion-combo3      (short save run, the submission kernel)
    python make_combo3.py full       # arc3-talyxion-combo3-full (25 public games x 121 min, evaluation only)
    python make_combo3.py full nog   # arc3-talyxion-combo3-nog-full: the same without Gittins (Franzen's gate)
    python make_combo3.py [full] bundle  # arc3-talyxion-combo4[-full]: + JustAdev742's harness bundle (budget meter,
                                         # search helper, win ledger, level mem, perception; their LB draw 34.04)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

JUSTA = Path(os.environ.get("JUSTA") or (r"D:dev_toolsjusta" if os.name == "nt" else Path(os.environ["TEMP"]) / "ghscan2" / "justa"))
HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent / "harness"
full = "full" in sys.argv[1:]
nog = "nog" in sys.argv[1:]
bundle = "bundle" in sys.argv[1:]
use_map = "map" in sys.argv[1:]  # ARC FR-Spec map: build on Linux (zip create_system differs on Windows)
logs = "logs" in sys.argv[1:]  # full runs: write *_requests.jsonl (MTP draft fine-tune data)
slug = ("arc3-talyxion-combo4" if bundle else "arc3-talyxion-combo3") + ("-nog" if nog else "") + ("-full" if full else "")
out = HERE / slug.replace("arc3-talyxion-", "")
NOTE = ("Talyxion combo3: Franzen M2 + Bayesian Gittins + retained-function fix + REAP-448 + 14 streams "
        "(REAP/map tooling: JustAdev742/scottmahony, Apache-2.0)")
cmd = [sys.executable, "scripts/build_franzen_nb.py", "--out", str(out), "--slug", slug,
       "--patch", str(HARNESS / "talyxion_gittins.patch"), "--patch", str(HARNESS / "talyxion_fixes.patch"),
       "--env-add", "ARC3_PRIORITY_POLICY=gittins", "--env-add", "ARC3_GITTINS_OFFSET=-0.516",
       "--env", "ARC3_MAX_ACTIVE_STREAMS=14", "--cfg", "MAXREQ=14", "--cfg", "CUDAGRAPH_MAXBS=14", "--cfg", "MAMBA_CACHE=84",
       "--reap-kept", "kaggle/franzen/reap448_kept_experts.json",
       "--input-fallback", "--compact", "--no-apply-check", "--note", NOTE]
if full:
    cmd += ["--full25", "121", "--fail-fast"]
if use_map:
    cmd += ["--hot-tokens", "kaggle/franzen/hot_tokens_64k_arc.pt"]
if bundle:
    cmd += ["--patch", str(HARNESS / "justa_bundle.patch")]
    for flag in ("OURS_BUDGET_METER", "OURS_SEARCH_HELPER", "OURS_WIN_LEDGER", "OURS_LEVEL_MEM", "OURS_PERCEPTION"):
        cmd += ["--env-add", flag + "=1"]
    cmd[cmd.index("--note") + 1] = NOTE + " + JustAdev742 harness bundle (ours-01 time, 02, 04, 03b, 05, 08b)"
if nog:
    for flag in ("--patch", "--env-add", "--env-add"):
        i = cmd.index(flag)
        if flag == "--patch":
            assert cmd[i + 1].endswith("talyxion_gittins.patch")
        del cmd[i:i + 2]
    cmd[cmd.index("--note") + 1] = NOTE.replace("Bayesian Gittins + ", "") + " [control: Franzen's gate]"
subprocess.run(cmd, cwd=JUSTA, check=True, env=dict(os.environ, PYTHONUTF8="1"))

nb_path = out / f"{slug}.ipynb"
nb = json.loads(nb_path.read_text(encoding="utf-8"))
sys.path.insert(0, str(HERE))
from robust_input import harden  # noqa: E402  (v3: model-path fallback + 40-min first-request grace)
hits = [c for c in nb["cells"] if "def _ours_input(path):" in "".join(c["source"])]
assert len(hits) == 1
hits[0]["source"] = harden("".join(hits[0]["source"])).splitlines(keepends=True)
if logs:
    anchor = "bm.solver.max_runtime_s_per_game = 121.0*60  # ours (--full25)"
    hits = [c for c in nb["cells"] if anchor in "".join(c["source"])]
    assert full and len(hits) == 1
    hits[0]["source"] = "".join(hits[0]["source"]).replace(
        anchor, anchor + "\n        bm.solver.save_request_logs = True  # Talyxion: request logs for the MTP fine-tune"
    ).splitlines(keepends=True)
first = "".join(nb["cells"][0]["source"])
assert "**Our arm (scottmahony, built by " in first
nb["cells"][0]["source"] = first.replace("**Our arm (scottmahony, built by ", "**Talyxion arm (built with JustAdev742's ").splitlines(keepends=True)
nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
meta_path = out / "kernel-metadata.json"
meta = json.loads(meta_path.read_text())
meta.update(id=f"thnhnguyn2001/{slug}", title=slug)
meta_path.write_text(json.dumps(meta, indent=1))
print("wrote", nb_path, meta["id"])
