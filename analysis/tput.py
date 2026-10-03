"""Compare serving configurations from their commit-mode benchmark runs.

Harness-side throughput = generated tokens summed over all games / wall-clock span of the run
(the quantity the cost model's budget is measured in). Server-side: mean decode throughput while
the gate is saturated, and the share of prompt tokens served from the prefix cache.
"""
import glob
import json
import os
import re
import subprocess
import sys

import numpy as np

KAGGLE = [r"C:\Users\Admin\AppData\Local\Temp\kgl\Scripts\python.exe", "-m", "kaggle"]
OUT = r"D:\arc3_paper\results\tput"


def fetch(key):
    d = os.path.join(OUT, key)
    os.makedirs(d, exist_ok=True)
    if not os.path.exists(os.path.join(d, "benchmark.json")):
        subprocess.run(KAGGLE + ["kernels", "output", "thnhnguyn2001/arc3-talyxion-tput-" + key, "-p", d,
                                 "--file-pattern", r"(benchmark\.json|serve\.log)$"], capture_output=True)
    return d


def analyse(d):
    b = json.load(open(os.path.join(d, "benchmark.json"), encoding="utf-8"))
    tok = 0
    t_end = 0.0
    levels = 0
    for g in b["game_runs"]:
        hist = g.get("history") or []
        tok += sum(h.get("generated_tokens") or 0 for h in hist)
        if hist:
            t_end = max(t_end, hist[-1]["wallclock_seconds"])
        levels += int(g.get("levels_completed") or 0)
    log = open(os.path.join(d, "serve.log"), encoding="utf-8", errors="replace").read()
    dec = [(int(r), float(t)) for r, t in re.findall(r"Decode batch, #running-req: (\d+).*?gen throughput \(token/s\): ([0-9.]+)", log)]
    full = [t for r, t in dec if r >= 8]
    acc = [float(x) for x in re.findall(r"accept len: ([0-9.]+)", log)]
    new = sum(int(x) for x in re.findall(r"#new-token: (\d+)", log))
    cached = sum(int(x) for x in re.findall(r"#cached-token: (\d+)", log))
    kv = re.findall(r"max_total_num_tokens=(\d+)", log)
    exc = len(re.findall(r"Scheduler hit an exception|Traceback", log))
    return dict(kv_pool=int(kv[-1]) if kv else None, server_errors=exc, games=len(b["game_runs"]), gen_tokens=tok, span_s=round(t_end), harness_tok_s=round(tok / max(t_end, 1)),
                decode_tok_s_saturated=round(float(np.mean(full))) if full else None,
                mean_running=round(float(np.mean([r for r, _ in dec])), 1) if dec else None,
                accept_len=round(float(np.mean(acc)), 2) if acc else None,
                prefix_cache_share=round(cached / max(1, cached + new), 3), levels=levels)


if __name__ == "__main__":
    keys = sys.argv[1:] or ["a", "b", "c", "d"]
    rows = {}
    for k in keys:
        d = fetch(k)
        try:
            rows[k] = analyse(d)
        except Exception as e:
            rows[k] = {"error": repr(e)}
        print(k, rows[k])
    json.dump(rows, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
