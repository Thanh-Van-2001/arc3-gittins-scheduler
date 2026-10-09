"""Build combo3: combo (Franzen M2 + Bayesian Gittins + retained-function fix) on REAP-448 + 14 streams.

The ARC FR-Spec map (--hot-tokens) is left out: built on Windows its sha256 did not match on Kaggle (v1 failed at
the map assert), and it is worth only ~2% tok/s.

Serving changes come from JustAdev742/scottmahony's Apache-2.0 tooling (scripts/build_franzen_nb.py,
scripts/sglang_reap_patch.py, kaggle/franzen/reap448_kept_experts.json, hot_tokens_64k_arc.pt); their gates measured
+14% output tok/s for REAP-448 + 14 streams (same accept length) and ~+2% for the ARC token map.

    python make_combo3.py            # arc3-talyxion-combo3      (short save run, the submission kernel)
    python make_combo3.py full       # arc3-talyxion-combo3-full (25 public games x 121 min, evaluation only)
    python make_combo3.py full nog   # arc3-talyxion-combo3-nog-full: the same without Gittins (Franzen's gate)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

JUSTA = Path(os.environ["TEMP"]) / "ghscan2" / "justa"
HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent / "harness"
full = "full" in sys.argv[1:]
nog = "nog" in sys.argv[1:]
slug = "arc3-talyxion-combo3" + ("-nog" if nog else "") + ("-full" if full else "")
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
first = "".join(nb["cells"][0]["source"])
assert "**Our arm (scottmahony, built by " in first
nb["cells"][0]["source"] = first.replace("**Our arm (scottmahony, built by ", "**Talyxion arm (built with JustAdev742's ").splitlines(keepends=True)
nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
meta_path = out / "kernel-metadata.json"
meta = json.loads(meta_path.read_text())
meta.update(id=f"thnhnguyn2001/{slug}", title=slug)
meta_path.write_text(json.dumps(meta, indent=1))
print("wrote", nb_path, meta["id"])
