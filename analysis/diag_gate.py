"""Analyse the contention diagnostic: is the Gittins gate actually steering slots?"""
import json
import os
import re
import subprocess

import numpy as np

KAGGLE = [r"C:\Users\Admin\AppData\Local\Temp\kgl\Scripts\python.exe", "-m", "kaggle"]
D = r"D:\arc3_paper\results\diag"
os.makedirs(D, exist_ok=True)
subprocess.run(KAGGLE + ["kernels", "output", "thnhnguyn2001/arc3-talyxion-diag", "-p", D,
                         "--file-pattern", r"(benchmark\.json|gittins_log\.jsonl|serve\.log)$"], capture_output=True)
logtxt = "".join(r.get("data", "") for r in json.load(open(os.path.join(D, "arc3-talyxion-diag.log"), encoding="utf-8", errors="replace")))
print("logger installed:", "gittins pricing logger installed" in logtxt, "|", re.findall(r"policy enabled: \w+ offset [-0-9.]+", logtxt)[:1])
diag = re.findall(r"gate: (\d+) handovers, (\d+) blocked, (\d+)ms blocked", logtxt)
if diag:
    print("gate handovers (last DIAG line):", diag[-1])
G = [json.loads(l) for l in open(os.path.join(D, "gittins_log.jsonl"))] if os.path.exists(os.path.join(D, "gittins_log.jsonl")) else []
print("gittins pricings:", len(G))
if G:
    p = np.array([g["p"] for g in G])
    print("priority quantiles:", np.quantile(p, [0, .1, .5, .9, 1]).round(0).tolist(), "| distinct values:", len(set(p.tolist())))
    with_clear = [g for g in G if g["cleared"]]
    if with_clear:
        mean_cost = np.array([np.mean([c[1] for c in g["cleared"]]) for g in with_clear])
        pr = np.array([g["p"] for g in with_clear])
        print("pricings with cleared levels:", len(with_clear), "| corr(priority, -log mean cleared cost) = %.2f" % np.corrcoef(pr, -np.log(mean_cost))[0, 1])
    stuck = [g for g in G if not g["cleared"]]
    if stuck:
        t = np.array([g["tokens"] for g in stuck]); pr = np.array([g["p"] for g in stuck])
        print("level-1 pricings:", len(stuck), "| corr(priority, tokens on level) = %.2f (expect negative)" % np.corrcoef(pr, t)[0, 1])
b = json.load(open(os.path.join(D, "benchmark.json")))
rows = []
for g in b["game_runs"]:
    tok = sum(h.get("generated_tokens") or 0 for h in g["history"])
    rows.append((g["game_id"][:4], int(g["levels_completed"]), tok, round(g["final_score"], 1)))
rows.sort(key=lambda r: -r[2])
print("tokens per game (desc):", rows)
tok = np.array([r[2] for r in rows]); lv = np.array([r[1] for r in rows])
print("total tokens %d | corr(tokens, levels) = %.2f | mean score %.2f" % (tok.sum(), np.corrcoef(tok, lv)[0, 1], np.mean([r[3] for r in rows])))
