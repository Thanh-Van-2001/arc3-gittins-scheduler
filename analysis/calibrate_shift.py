"""Recalibrate the hidden-set difficulty shift against the community distribution of single
submissions of Franzen's notebook (mean 25.77, SD 3.93, n in the hundreds; forum topic 745062)."""
import numpy as np, pandas as pd, json
from costmodel import fit
from sim import sample_world, simulate, make_franzen
from gittins import GittinsTables, make_gittins
df = pd.read_csv("level_attempts.csv"); M = fit(df)
nl_pool = df.groupby("game").n_levels.first().values
fr = [r for r, a in M["a"].items() if np.exp(a) < 0.35]
dd = df[df.completed & (df.actions > 0) & df.run.isin(fr)]; rp = (dd.baseline / dd.actions).values
re_ = float(np.mean([M["a"][r] for r in fr])); eff = float(np.mean(np.minimum(1, rp ** 2)))
out = {}
for shift in [0.6, 0.75, 0.9, 1.05]:
    tab_fixed = GittinsTables(M, re_, shift=0.6, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)
    tab_match = GittinsTables(M, re_, shift=shift, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)
    f, g06, gm = [], [], []
    for sd in range(5):
        w = sample_world(np.random.default_rng(900 + sd), 110, M, nl_pool, rp, re_, shift)
        kw = dict(lease=30000, first_chunk=40000)
        f.append(simulate(w, 19.4e6, make_franzen(), **kw)[0])
        g06.append(simulate(w, 19.4e6, make_gittins(tab_fixed), **kw)[0])
        gm.append(simulate(w, 19.4e6, make_gittins(tab_match), **kw)[0])
    out[shift] = dict(franzen=float(np.mean(f)), gittins_tables06=float(np.mean(g06)), gittins_matched=float(np.mean(gm)))
    print(f"shift {shift:.2f}: franzen {np.mean(f):5.1f} | gittins(0.6 tables) {np.mean(g06):5.1f} (+{np.mean(np.array(g06)-f):.1f}) | gittins(matched) {np.mean(gm):5.1f} (+{np.mean(np.array(gm)-f):.1f})", flush=True)
json.dump(out, open("calibrate_shift.json", "w"), indent=1)
