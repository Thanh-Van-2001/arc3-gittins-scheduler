"""Diff public ARC-AGI-3 notebooks against Franzen's M2 notebook: models, server config, harness env,
solver overrides, and whether they ship their own harness patch."""
import json
import re
import sys
from pathlib import Path

REF = Path(r"D:\arc3_paper\kernels\base\arc3-talyxion-base.ipynb")
KEYS_ENV = re.compile(r"""['"]((?:ARC3|LOCAL_ANALYZER|EXPOSE|MULTIMODAL|OPENROUTER|INFERENCE)_[A-Z0-9_]+)['"]\s*:\s*([^,\n]+)""")
KEYS_CFG = re.compile(r"\n\s*([A-Z][A-Z0-9_]{2,})=([^,\n]+),")
KEYS_SOLVER = re.compile(r"(bm\.solver\.[a-z_]+|bm\.n_passes)\s*=\s*([^\n#]+)")


def extract(path):
    nb = json.load(open(path, encoding="utf-8"))
    code = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    meta = {}
    mp = Path(path).with_name("kernel-metadata.json")
    if mp.exists():
        m = json.load(open(mp))
        meta = dict(models=m.get("model_sources"), datasets=m.get("dataset_sources"), shape=m.get("machine_shape"))
    env = {k: v.strip().strip("'\"") for k, v in KEYS_ENV.findall(code)}
    cfg = {k: v.strip() for k, v in KEYS_CFG.findall(code)}
    solver = {k: v.strip() for k, v in KEYS_SOLVER.findall(code)}
    patch_bytes = sum(len("".join(c["source"])) for c in nb["cells"] if "".join(c["source"]).startswith("%%writefile") and ".patch" in "".join(c["source"])[:200])
    engine = "sglang" if "sglang" in code.lower() else ("vllm" if "vllm" in code.lower() else "?")
    return dict(meta=meta, env=env, cfg=cfg, solver=solver, patch_bytes=patch_bytes, engine=engine, cells=len(nb["cells"]))


def diff(a, b):
    out = {}
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            out[k] = (a.get(k), b.get(k))
    return out


if __name__ == "__main__":
    ref = extract(REF)
    for p in sys.argv[1:]:
        x = extract(p)
        print("=" * 100)
        print(Path(p).parent.name, "| engine", x["engine"], "| own patch bytes", x["patch_bytes"], "| cells", x["cells"])
        print("  models:", x["meta"].get("models"))
        print("  datasets:", x["meta"].get("datasets"))
        for name in ("env", "cfg", "solver"):
            d = diff(ref[name], x[name])
            if d:
                print(f"  {name} differences (franzen -> this):")
                for k, (va, vb) in d.items():
                    print(f"     {k}: {va} -> {vb}")
