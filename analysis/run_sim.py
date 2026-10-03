import numpy as np, pandas as pd, sys, json
from costmodel import fit
from sim import sample_world, simulate, make_equal, make_franzen, oracle_score

df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv")
M = fit(df)
nl_pool = df.groupby("game").n_levels.first().values
fr_runs = [r for r, a in M["a"].items() if np.exp(a) < 0.35]
done = df[df.completed & (df.actions > 0) & df.run.isin(fr_runs)]
ratio_pool = (done.baseline / done.actions).values
run_eff = float(np.mean([M["a"][r] for r in fr_runs]))
print("franzen-like runs:", fr_runs, "run effect x", round(np.exp(run_eff), 3), "ratio pool", len(ratio_pool))
G, B = 110, 19.4e6

def evaluate(shift, seeds=range(6), budget=B, policies=("equal", "franzen", "oracle")):
    out = {p: [] for p in policies}
    for sd in seeds:
        rng = np.random.default_rng(sd)
        w = sample_world(rng, G, M, nl_pool, ratio_pool, run_eff, shift)
        if "equal" in policies: out["equal"].append(simulate(w, budget, make_equal(G, budget))[0])
        if "franzen" in policies: out["franzen"].append(simulate(w, budget, make_franzen())[0])
        if "oracle" in policies: out["oracle"].append(oracle_score(w, budget))
    return {p: (round(np.mean(v), 2), round(np.std(v), 2)) for p, v in out.items()}

for shift in [0.0, 0.5, 1.0, 1.5]:
    print("shift", shift, evaluate(shift, seeds=range(3)), flush=True)
