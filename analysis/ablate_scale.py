import numpy as np, pandas as pd, json
from costmodel import fit
from sim import sample_world, simulate, make_equal, make_franzen, oracle_score
from gittins import GittinsTables, make_gittins
df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv"); M = fit(df)
nl_pool = df.groupby("game").n_levels.first().values
fr_runs = [r for r, a in M["a"].items() if np.exp(a) < 0.35]
done = df[df.completed & (df.actions > 0) & df.run.isin(fr_runs)]
ratio_pool = (done.baseline / done.actions).values
run_eff = float(np.mean([M["a"][r] for r in fr_runs])); eff = float(np.mean(np.minimum(1.0, ratio_pool ** 2)))
G, B = 110, 19.4e6
tab = GittinsTables(M, run_eff, shift=0.6, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)

class NoLearn:  # ablation: ignore costs of cleared levels (no cross-level difficulty learning)
    def __init__(s, t): s.t = t
    def posterior(s, cleared, level, t): return s.t.posterior([], level, t)
    def index(s, *a): return s.t.index(*a)
class NoUpdate:  # ablation: prior only (no learning at all) -> index depends on (level, t) via hazard only
    def __init__(s, t): s.t = t
    def posterior(s, cleared, level, t):
        from gittins import PRIOR; return PRIOR
    def index(s, *a): return s.t.index(*a)

res = {}
for mult in [0.25, 0.5, 1.0, 2.0, 4.0]:
    rows = []
    for sd in range(5):
        w = sample_world(np.random.default_rng(400 + sd), G, M, nl_pool, ratio_pool, run_eff, 0.6)
        b = B * mult
        r = dict(equal=simulate(w, b, make_equal(G, b))[0], franzen=simulate(w, b, make_franzen(), lease=30000, first_chunk=40000)[0],
                 gittins=simulate(w, b, make_gittins(tab), lease=30000, first_chunk=40000)[0], oracle=oracle_score(w, b))
        if mult == 1.0:
            r["gittins_nolearn"] = simulate(w, b, make_gittins(NoLearn(tab)), lease=30000, first_chunk=40000)[0]
            r["gittins_prior_only"] = simulate(w, b, make_gittins(NoUpdate(tab)), lease=30000, first_chunk=40000)[0]
        rows.append(r)
    m = pd.DataFrame(rows).mean().round(2).to_dict(); res[mult] = m
    print("budget x", mult, m, flush=True)
json.dump({str(k): v for k, v in res.items()}, open("scale_ablation.json", "w"), indent=1)
