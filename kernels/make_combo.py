"""Build the 'combo' notebook: Franzen M2 + Bayesian Gittins scheduler + 12 serving streams.

Starts from the (path-hardened) Gittins arm and applies the only community/throughput change with a
measurement behind it: 12 concurrent streams (+7% generation throughput in the 20-game sweep).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
src_nb = os.path.join(HERE, "gittins", "arc3-talyxion-gittins.ipynb")
nb = json.load(open(src_nb, encoding="utf-8"))
SERVER = {"MAXREQ": 12, "CUDAGRAPH_MAXBS": 12, "MAMBA_CACHE": 72}


def cell_with(text):
    hits = [c for c in nb["cells"] if text in "".join(c["source"])]
    assert len(hits) == 1, (text, len(hits))
    return hits[0]


c = cell_with("CFG = dict(")
s = "".join(c["source"])
for name, val in SERVER.items():
    pat = re.compile(r"(\n\s*" + name + r"=)([^,\n]+)(,)")
    assert pat.search(s), name
    s = pat.sub(lambda m: m.group(1) + str(val) + m.group(3), s, count=1)
c["source"] = s.splitlines(keepends=True)

c = cell_with("'ARC3_MAX_ACTIVE_STREAMS': 10,")
s = "".join(c["source"]).replace("'ARC3_MAX_ACTIVE_STREAMS': 10,", "'ARC3_MAX_ACTIVE_STREAMS': 12,")
c["source"] = s.splitlines(keepends=True)

nb["cells"].insert(0, {"cell_type": "markdown", "metadata": {}, "source": [
    "# Talyxion combo: Franzen M2 + Bayesian Gittins scheduler + 12 streams\n", "\n",
    "Built on Daniel Franzen's Milestone-2 notebook (Apache-2.0) and Tufa Labs' Duck harness (MIT). ",
    "Changes: `talyxion-gittins.patch` (`ARC3_PRIORITY_POLICY=gittins`), input-path hardening, ",
    "and 12 concurrent serving streams (SGLang max-running-requests 12, Mamba cache 72)."]})

out = os.path.join(HERE, "combo")
os.makedirs(out, exist_ok=True)
name = "arc3-talyxion-combo"
json.dump(nb, open(os.path.join(out, name + ".ipynb"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
meta = json.load(open(os.path.join(HERE, "gittins", "kernel-metadata.json")))
meta.update(id="thnhnguyn2001/" + name, title=name, code_file=name + ".ipynb")
json.dump(meta, open(os.path.join(out, "kernel-metadata.json"), "w"), indent=2)

code = "\n".join("".join(c["source"]) for c in nb["cells"])
print("streams:", re.findall(r"ARC3_MAX_ACTIVE_STREAMS': (\d+)", code),
      "server:", re.findall(r"\n\s*(MAXREQ|CUDAGRAPH_MAXBS|MAMBA_CACHE|SPEC_STEPS)=(\w+)", code),
      "gittins env:", "ARC3_PRIORITY_POLICY'] = 'gittins'" in code,
      "resolver:", "_resolve_input" in code,
      "short demo:", "DEMO_KEEP = ['sb26', 'ft09', 'lp85']" in code)
