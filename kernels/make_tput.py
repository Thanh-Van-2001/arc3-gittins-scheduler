"""Generate throughput-benchmark copies of the Franzen M2 notebook (one server/harness config each)."""
import copy
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(HERE, "base", "arc3-talyxion-base.ipynb"), encoding="utf-8"))
meta = json.load(open(os.path.join(HERE, "base", "kernel-metadata.json")))

CONFIGS = {
    "a": dict(desc="control: 10 streams, spec 3", streams=10, cfg={}),
    "b": dict(desc="spec 4", streams=10, cfg={"SPEC_STEPS": 4}),
    "c": dict(desc="spec 2", streams=10, cfg={"SPEC_STEPS": 2}),
    "d": dict(desc="12 streams", streams=12, cfg={"MAXREQ": 12, "CUDAGRAPH_MAXBS": 12, "MAMBA_CACHE": 72}),
}
# 20 demo games so the 10-12 slot gate stays saturated for the whole window
KEEP = ["ar25", "bp35", "cd82", "cn04", "dc22", "ft09", "g50t", "ka59", "lf52", "lp85",
        "ls20", "m0r0", "r11l", "re86", "s5i5", "sb26", "sc25", "sk48", "sp80", "tu93"]


def edit(cell, fn):
    src = "".join(cell["source"])
    cell["source"] = fn(src).splitlines(keepends=True)


for key, c in CONFIGS.items():
    nb = copy.deepcopy(base)

    def server(src, c=c):
        for name, val in c["cfg"].items():
            pat = re.compile(r"(\n\s*" + name + r"=)([^,\n]+)(,)")
            assert pat.search(src), name
            src = pat.sub(lambda m: m.group(1) + str(val) + m.group(3), src, count=1)
        return src

    def harness(src, c=c):
        old = "'ARC3_MAX_ACTIVE_STREAMS': 10,"
        assert old in src
        return src.replace(old, "'ARC3_MAX_ACTIVE_STREAMS': %d," % c["streams"])

    def demo(src):
        old = "DEMO_KEEP = ['sb26', 'ft09', 'lp85']  # short commit-mode demo to save GPU quota"
        assert old in src
        return src.replace(old, "DEMO_KEEP = %r  # throughput benchmark: saturate the gate" % KEEP)

    edit(nb["cells"][12], server)
    edit(nb["cells"][4], harness)
    edit(nb["cells"][16], demo)
    nb["cells"].insert(0, {"cell_type": "markdown", "metadata": {}, "source": [
        "# Throughput benchmark config %s: %s\n" % (key.upper(), c["desc"]), "\n",
        "Private benchmarking copy of the Franzen M2 notebook (Apache-2.0). Not for submission."]})
    out = os.path.join(HERE, "tput", key)
    os.makedirs(out, exist_ok=True)
    name = "arc3-talyxion-tput-%s" % key
    json.dump(nb, open(os.path.join(out, name + ".ipynb"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    m = dict(meta)
    m.update(id="thnhnguyn2001/" + name, title=name, code_file=name + ".ipynb")
    json.dump(m, open(os.path.join(out, "kernel-metadata.json"), "w"), indent=2)
    s13 = "".join(nb["cells"][13]["source"])
    s5 = "".join(nb["cells"][5]["source"])
    print(key, c["desc"], re.findall(r"\n\s*(MAXREQ|SPEC_STEPS|CUDAGRAPH_MAXBS|MAMBA_CACHE)=(\w+)", s13),
          re.findall(r"ARC3_MAX_ACTIVE_STREAMS': (\d+)", s5))
