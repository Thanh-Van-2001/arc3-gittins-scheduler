"""Diagnostic notebook: does the Gittins gate actually steer slots under contention in the real harness?

Built from the submitted combo notebook. Changes (diagnostic only, never submitted):
- 25 public games for 4 slots (contention), 55 minutes per game window;
- smaller harness context window so context trims (the only handover points) happen often;
- ARC3_DIAG_CONCURRENCY=1 and a wrapper that logs every Gittins pricing to gittins_log.jsonl.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
NL = "\n"
nb = json.load(open(os.path.join(HERE, "combo", "arc3-talyxion-combo.ipynb"), encoding="utf-8"))
ALL = ["ar25", "bp35", "cd82", "cn04", "dc22", "ft09", "g50t", "ka59", "lf52", "lp85", "ls20", "m0r0", "r11l",
       "re86", "s5i5", "sb26", "sc25", "sk48", "sp80", "su15", "tn36", "tr87", "tu93", "vc33", "wa30"]


def cell_with(text):
    hits = [c for c in nb["cells"] if text in "".join(c["source"])]
    assert len(hits) == 1, (text, len(hits))
    return hits[0]


def sub(cell, old, new):
    s = "".join(cell["source"])
    assert old in s, old
    cell["source"] = s.replace(old, new, 1).splitlines(keepends=True)


env = cell_with("'ARC3_MAX_ACTIVE_STREAMS': 10,")
sub(env, "'ARC3_MAX_ACTIVE_STREAMS': 10,", "'ARC3_MAX_ACTIVE_STREAMS': 4,\n    'ARC3_DIAG_CONCURRENCY': '1',")
sub(env, "'LOCAL_ANALYZER_CONTEXT_WINDOW': (116+12)*1024,", "'LOCAL_ANALYZER_CONTEXT_WINDOW': (40+8)*1024,")
sub(env, "'LOCAL_ANALYZER_MAX_OUTPUT': 12*1024,", "'LOCAL_ANALYZER_MAX_OUTPUT': 8*1024,")
sub(env, "'ARC3_CONTEXT_DRAIN_TOKENS': 58*1024,", "'ARC3_CONTEXT_DRAIN_TOKENS': 20*1024,")

hook = cell_with("bm.solver.max_runtime_s_per_game = 48*60")
sub(hook, "DEMO_KEEP = ['sb26', 'ft09', 'lp85']  # short commit-mode demo to save GPU quota",
    "DEMO_KEEP = %r  # diagnostic: all 25 games compete for 4 slots" % ALL)
sub(hook, "bm.solver.max_runtime_s_per_game = 12*60  # short demo", "bm.solver.max_runtime_s_per_game = 55*60  # diagnostic window")
logger = NL.join([
    "",
    "# --- diagnostic: log every Gittins pricing ---",
    "import json as _json, time as _time",
    "import inference.agent.tool_agent as _ta, inference.agent.gittins_scheduler as _gs",
    "_GLOG = open('/kaggle/working/gittins_log.jsonl', 'a')",
    "_orig_gp = _gs.gittins_priority",
    "def _logged_gp(level, tokens, cleared_costs=(), total_levels=None):",
    "    p = _orig_gp(level, tokens, cleared_costs, total_levels)",
    "    _GLOG.write(_json.dumps(dict(t=_time.time(), level=int(level), tokens=float(tokens), cleared=[list(map(float, c)) for c in (cleared_costs or ())], n=total_levels, p=int(p))) + '\\n'); _GLOG.flush()",
    "    return p",
    "_ta.gittins_priority = _logged_gp",
    "print('gittins pricing logger installed; policy enabled:', _gs.gittins_enabled(), 'offset', _gs._offset())",
])
s = "".join(hook["source"]) + logger + NL
hook["source"] = s.splitlines(keepends=True)

nb["cells"].insert(0, {"cell_type": "markdown", "metadata": {}, "source": [
    "# Diagnostic (not for submission): Gittins gate under contention" + NL, NL,
    "25 public games, 4 slots, 48k harness context so trims are frequent; logs every pricing."]})
out = os.path.join(HERE, "diag")
os.makedirs(out, exist_ok=True)
name = "arc3-talyxion-diag"
json.dump(nb, open(os.path.join(out, name + ".ipynb"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
meta = json.load(open(os.path.join(HERE, "combo", "kernel-metadata.json")))
meta.update(id="thnhnguyn2001/" + name, title=name, code_file=name + ".ipynb")
json.dump(meta, open(os.path.join(out, "kernel-metadata.json"), "w"), indent=2)
code = NL.join("".join(c["source"]) for c in nb["cells"])
print("streams", re.findall(r"ARC3_MAX_ACTIVE_STREAMS': (\d+)", code), "| window", re.findall(r"CONTEXT_WINDOW': ([^,]+)", code),
      "| logger", "_logged_gp" in code, "| runtime", re.findall(r"max_runtime_s_per_game = (\d+\*60)  # diagnostic", code))
