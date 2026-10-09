"""Gate A/B under REAP-448 + 14 streams on the 25 public games (121 min/game): Gittins (combo3-full) vs Franzen's
gate (combo3-nog-full), paired by game over results/run1..runN."""
import glob
import os
import re
import statistics as st

A, B = "combo3-full", "combo3-nog-full"


def load(d):
    g = {}
    for line in open(d + "/summary.txt"):
        m = re.search(r"^\s+(\w+)-\w+: score=([\d.]+), levels=([\d.]+)/\d+", line)
        if m:
            g[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    return g


runs = sorted(os.path.basename(p) for p in glob.glob("../results/run[0-9]*"))
R = {(r, a): load(f"../results/{r}/{a}") for r in runs for a in (A, B)}
for a in (A, B):
    means = [st.mean(x[0] for x in R[(r, a)].values()) for r in runs]
    levels = [int(sum(x[1] for x in R[(r, a)].values())) for r in runs]
    print(a, [round(m, 2) for m in means], levels, "mean %.2f" % st.mean(means))
d = [st.mean(R[(r, A)][g][0] for r in runs) - st.mean(R[(r, B)][g][0] for r in runs) for g in R[(runs[0], A)]]
print("paired per-game diff %.2f +/- %.2f (n=%d games, %d pairs)" % (st.mean(d), st.stdev(d) / len(d) ** 0.5, len(d), len(runs)))
