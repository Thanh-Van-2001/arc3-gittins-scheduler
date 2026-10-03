"""Build the final 'combo' notebook: Franzen M2 + Bayesian Gittins scheduler + retained-function fix.

Serving stays exactly Franzen's: the throughput sweep found it at its frontier (12 streams are
KV-limited; Pennyroyal's online MXFP8 is 21-37% slower on this W4A16 checkpoint). The Gittins offset
is recalibrated to the community distribution of Franzen-notebook scores (hidden-set shift 0.85).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
NL = "\n"
nb = json.load(open(os.path.join(HERE, "gittins", "arc3-talyxion-gittins.ipynb"), encoding="utf-8"))
OFFSET = "-0.516"  # -1.366 (Franzen-config run effect) + 0.85 (hidden-set shift, analysis/calibrate_shift.py)


def cell_with(text):
    hits = [c for c in nb["cells"] if text in "".join(c["source"])]
    assert len(hits) == 1, (text, len(hits))
    return hits[0]


# 1) second patch: keep retained functions when a tool call times out
FIX = open(os.path.join(HERE, "..", "harness", "talyxion_fixes.patch"), encoding="utf-8", newline="").read()
gi = next(i for i, c in enumerate(nb["cells"])
          if "".join(c["source"]).startswith("%%writefile /kaggle/talyxion-gittins.patch"))
nb["cells"].insert(gi + 1, {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                            "source": ("%%writefile /kaggle/talyxion-fixes.patch" + NL + FIX).splitlines(keepends=True)})

# 2) apply it right after the Gittins patch, and set the calibrated offset
c = cell_with("print('gittins patch applied successfully')")
s = "".join(c["source"])
extra = NL.join([
    "print('gittins patch applied successfully')",
    'subprocess.run(["git", "apply", "--include=ARC3-Inference/*", "-v", "/kaggle/talyxion-fixes.patch"], '
    'cwd=f"{BUNDLE_DIR}/src", check=True)',
    "print('fixes patch applied successfully')",
    "os.environ['ARC3_GITTINS_OFFSET'] = '%s'  # hidden-set shift recalibrated to 0.85" % OFFSET,
])
s = s.replace("print('gittins patch applied successfully')", extra, 1)
c["source"] = s.splitlines(keepends=True)

nb["cells"].insert(0, {"cell_type": "markdown", "metadata": {}, "source": [
    "# Talyxion final: Franzen M2 + Bayesian Gittins scheduler + retained-function fix" + NL, NL,
    "Built on Daniel Franzen's Milestone-2 notebook (Apache-2.0) and Tufa Labs' Duck harness (MIT). ",
    "Changes: `talyxion-gittins.patch` (`ARC3_PRIORITY_POLICY=gittins`, offset recalibrated), ",
    "`talyxion-fixes.patch` (keep retained functions when a tool call times out), input-path hardening. ",
    "Serving configuration unchanged."]})

out = os.path.join(HERE, "combo")
os.makedirs(out, exist_ok=True)
name = "arc3-talyxion-combo"
json.dump(nb, open(os.path.join(out, name + ".ipynb"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
meta = json.load(open(os.path.join(HERE, "gittins", "kernel-metadata.json")))
meta.update(id="thnhnguyn2001/" + name, title=name, code_file=name + ".ipynb")
json.dump(meta, open(os.path.join(out, "kernel-metadata.json"), "w"), indent=2)

code = NL.join("".join(c["source"]) for c in nb["cells"])
print("fixes patch cell:", "%%writefile /kaggle/talyxion-fixes.patch" in code,
      "| applied:", "/kaggle/talyxion-fixes.patch\"], cwd" in code,
      "| offset:", re.findall(r"ARC3_GITTINS_OFFSET'\] = '([-0-9.]+)'", code),
      "| streams:", re.findall(r"ARC3_MAX_ACTIVE_STREAMS': (\d+)", code),
      "| server:", re.findall(r"\n\s*(MAXREQ|SPEC_STEPS)=(\w+)", code),
      "| gittins:", "ARC3_PRIORITY_POLICY'] = 'gittins'" in code,
      "| resolver:", "_resolve_input" in code,
      "| short demo:", "DEMO_KEEP = ['sb26', 'ft09', 'lp85']" in code)
