import numpy as np, pandas as pd, time, sys
from costmodel import fit
from sim import sample_world, simulate, make_equal, make_franzen, oracle_score
from gittins import GittinsTables, make_gittins

df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv")
M = fit(df)
nl_pool = df.groupby("game").n_levels.first().values
fr_runs = [r for r, a in M["a"].items() if np.exp(a) < 0.35]
done = df[df.completed & (df.actions > 0) & df.run.isin(fr_runs)]
ratio_pool = (done.baseline / done.actions).values
run_eff = float(np.mean([M["a"][r] for r in fr_runs]))
eff = float(np.mean(np.minimum(1.0, ratio_pool ** 2)))
G, B = 110, 19.4e6
shift = float(sys.argv[1]) if len(sys.argv) > 1 else 0.6
t0 = time.time()
tab = GittinsTables(M, run_eff, shift=shift, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)
print("tables built in", round(time.time() - t0, 1), "s; eff", round(eff, 3), flush=True)
res = {k: [] for k in ["equal", "franzen", "gittins", "oracle"]}
for sd in range(4):
    rng = np.random.default_rng(100 + sd)
    w = sample_world(rng, G, M, nl_pool, ratio_pool, run_eff, shift)
    res["equal"].append(simulate(w, B, make_equal(G, B))[0])
    res["franzen"].append(simulate(w, B, make_franzen())[0])
    t1 = time.time(); res["gittins"].append(simulate(w, B, make_gittins(tab))[0])
    res["oracle"].append(oracle_score(w, B))
    print(sd, {k: round(v[-1], 2) for k, v in res.items()}, "gittins sim s", round(time.time() - t1, 1), flush=True)
print("MEAN", {k: round(float(np.mean(v)), 2) for k, v in res.items()})
print("paired gittins - franzen:", np.round(np.array(res["gittins"]) - np.array(res["franzen"]), 2))
