"""Upper bound for an online empirical-Bayes scheduler: in worlds whose cost structure differs from the
public-set fit, compare Gittins with public-set parameters vs Gittins with the true world parameters."""
import copy, numpy as np, pandas as pd
from costmodel import fit
from gittins import GittinsTables
from faithful import run, nl_pool, rp, re_, eff
from sim import sample_world
df = pd.read_csv("level_attempts.csv"); M = fit(df)
worlds = {
  "as fitted":                      dict(),
  "less game spread (su x0.5)":     dict(su=0.5),
  "more level noise (s x1.4)":      dict(s=1.4),
  "flat level costs (b x0.3)":      dict(b=0.3),
  "steep level costs (b x1.7)":     dict(b=1.7),
  "noise up, spread down":          dict(su=0.5, s=1.4),
}
for name, mod in worlds.items():
    W = copy.deepcopy(M)
    W["su"] = M["su"] * mod.get("su", 1); W["s"] = M["s"] * mod.get("s", 1); W["b"] = np.asarray(M["b"]) * mod.get("b", 1)
    tab_pub = GittinsTables(M, re_, shift=0.85, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)
    tab_true = GittinsTables(W, re_, shift=0.85, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)
    f, gp, gt = [], [], []
    for sd in range(5):
        w = sample_world(np.random.default_rng(1500 + sd), 110, W, nl_pool, rp, re_, 0.85)
        f.append(run(w, "franzen", 68000, 35000, np.random.default_rng(sd)))
        gp.append(run(w, "gittins", 68000, 35000, np.random.default_rng(sd), tab_pub))
        gt.append(run(w, "gittins", 68000, 35000, np.random.default_rng(sd), tab_true))
    print(f"{name:32s} franzen {np.mean(f):5.1f} | gittins(public params) {np.mean(gp):5.1f} ({np.mean(np.array(gp)-f):+.1f}) | gittins(true params) {np.mean(gt):5.1f} ({np.mean(np.array(gt)-f):+.1f})", flush=True)
