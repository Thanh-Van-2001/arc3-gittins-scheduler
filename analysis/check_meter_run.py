"""Verify a commit run of combo2: patches applied, no traceback, and budget-meter lines in prompts."""
import glob
import json
import os
import re
import sys

D = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Admin\AppData\Local\Temp\kout\combo2"
log = glob.glob(os.path.join(D, "*.log"))[0]
txt = "".join(r.get("data", "") for r in json.load(open(log, encoding="utf-8", errors="replace")))
print(re.findall(r"\w+ patch applied successfully", txt), "| traceback:", "Traceback" in txt)
for f in sorted(glob.glob(os.path.join(D, "*_p0_requests.jsonl"))):
    lines, prompts = set(), 0
    for row in open(f, encoding="utf-8"):
        for m in json.loads(row)["messages"]:
            if m.get("role") != "user":
                continue
            c = m.get("content")
            c = c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))
            prompts += 1
            lines.update(re.findall(r"Budget meter[^\n]{0,220}", c or ""))
    print(os.path.basename(f)[:4], "| user messages scanned:", prompts, "| distinct meter lines:", len(lines))
    for line in sorted(lines)[:3]:
        print("    ", line)
b = json.load(open(os.path.join(D, "benchmark.json")))
print([(g["game_id"][:4], g["levels_completed"], round(g["final_score"], 1)) for g in b["game_runs"]])
