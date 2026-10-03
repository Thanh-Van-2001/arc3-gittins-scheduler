"""Reconcile with Scott Le Grand's report that dropping games stuck at level 0 to give L1+/L2+ games
more time did not help: simulate that heuristic next to Franzen's priority and the Bayesian index."""
import numpy as np, pandas as pd, json
from costmodel import fit
from sim import sample_world, simulate, make_franzen, franzen_priority
from gittins import GittinsTables, make_gittins
df = pd.read_csv("level_attempts.csv"); M = fit(df)
nl_pool = df.groupby("game").n_levels.first().values
fr = [r for r, a in M["a"].items() if np.exp(a) < 0.35]
dd = df[df.completed & (df.actions > 0) & df.run.isin(fr)]; rp = (dd.baseline / dd.actions).values
re_ = float(np.mean([M["a"][r] for r in fr])); eff = float(np.mean(np.minimum(1, rp ** 2)))
tab = GittinsTables(M, re_, shift=0.6, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)

def make_drop_l0(T, boost_deep=False):
    """Franzen priority, except a game still at level 0 after T tokens is demoted below everything;
    optionally games at level >= 2 get a 2x boost (the 'give L2+ more time' variant)."""
    def pol(st, world, active, frac, ps):
        tail = min(1.0, (1 - frac) / 0.2); best, bg = -1e18, None
        for g in active:
            lv = int(st.level[g]); p = franzen_priority(lv + 1, st.t[g] / 1000 * 1.5, st.t[g], int(world.n_levels[g]), tail)
            if lv == 0 and st.t[g] > T: p -= 1e6
            if boost_deep and lv >= 2: p *= 2
            if p > best: best, bg = p, g
        return bg
    return pol

pols = {"franzen": lambda: make_franzen(), "gittins": lambda: make_gittins(tab)}
for T in [50_000, 100_000, 150_000]:
    pols[f"drop_L0>{T//1000}k"] = (lambda T=T: make_drop_l0(T))
    pols[f"drop_L0>{T//1000}k+boostL2"] = (lambda T=T: make_drop_l0(T, True))
res = {k: [] for k in pols}
for sd in range(6):
    w = sample_world(np.random.default_rng(800 + sd), 110, M, nl_pool, rp, re_, 0.6)
    for k, mk in pols.items():
        res[k].append(simulate(w, 19.4e6, mk(), lease=30000, first_chunk=40000)[0])
base = np.array(res["franzen"])
for k, v in res.items():
    v = np.array(v); d = v - base
    print(f"{k:24s} {v.mean():5.1f}   vs Franzen {d.mean():+5.2f} ± {d.std(ddof=1)/np.sqrt(len(d)):.2f}")
json.dump({k: list(map(float, v)) for k, v in res.items()}, open("drop_l0.json", "w"), indent=1)
