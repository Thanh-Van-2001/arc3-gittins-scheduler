"""combo2 = combo (Franzen + Gittins calibrated + retained-function fix) + budget meter (ARC3_BUDGET_METER=1)."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
NL = "\n"
nb = json.load(open(os.path.join(HERE, "combo", "arc3-talyxion-combo.ipynb"), encoding="utf-8"))
METER = open(os.path.join(HERE, "..", "harness", "talyxion_meter.patch"), encoding="utf-8", newline="").read()

fi = next(i for i, c in enumerate(nb["cells"]) if "".join(c["source"]).startswith("%%writefile /kaggle/talyxion-fixes.patch"))
nb["cells"].insert(fi + 1, {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                            "source": ("%%writefile /kaggle/talyxion-meter.patch" + NL + METER).splitlines(keepends=True)})
c = next(c for c in nb["cells"] if "print('fixes patch applied successfully')" in "".join(c["source"]))
s = "".join(c["source"])
s = s.replace("print('fixes patch applied successfully')", NL.join([
    "print('fixes patch applied successfully')",
    'subprocess.run(["git", "apply", "--include=ARC3-Inference/*", "-v", "/kaggle/talyxion-meter.patch"], '
    'cwd=f"{BUNDLE_DIR}/src", check=True)',
    "print('meter patch applied successfully')",
    "os.environ['ARC3_BUDGET_METER'] = '1'  # deterministic border-bar budget meter in the user prompt",
]), 1)
c["source"] = s.splitlines(keepends=True)
nb["cells"][0]["source"] = [
    "# Talyxion combo2: Franzen M2 + Bayesian Gittins + retained-function fix + budget meter" + NL, NL,
    "Built on Daniel Franzen's Milestone-2 notebook (Apache-2.0) and Tufa Labs' Duck harness (MIT). ",
    "Adds `talyxion-meter.patch` (ARC3_BUDGET_METER=1) on top of the combo notebook."]
out = os.path.join(HERE, "combo2")
os.makedirs(out, exist_ok=True)
name = "arc3-talyxion-combo2"
json.dump(nb, open(os.path.join(out, name + ".ipynb"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
meta = json.load(open(os.path.join(HERE, "combo", "kernel-metadata.json")))
meta.update(id="thnhnguyn2001/" + name, title=name, code_file=name + ".ipynb")
json.dump(meta, open(os.path.join(out, "kernel-metadata.json"), "w"), indent=2)
code = NL.join("".join(c["source"]) for c in nb["cells"])
print("patches:", re.findall(r"%%writefile /kaggle/([\w-]+\.patch)", code),
      "| meter env:", "ARC3_BUDGET_METER'] = '1'" in code, "| offset:", re.findall(r"ARC3_GITTINS_OFFSET'\] = '([-0-9.]+)'", code))
