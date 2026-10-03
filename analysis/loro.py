"""Leave-one-run-out check: fit the cost model without a run, then predict how many levels that
run cleared in each game given the generated tokens it actually spent there."""
import numpy as np, pandas as pd, json
from costmodel import fit
df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv")
df = df[df.tokens > 0]
tot = df.groupby(["run", "game"]).agg(tokens=("tokens", "sum"), levels=("completed", "sum"), n=("n_levels", "first")).reset_index()
fr = ["dfranzen__arc-agi-3-milestone-2-solution", "skarin__arc3-franzen-m2-exact-10-game-validation", "matterhorn3838__arc-ak47-3-agi"]
rows = []
for held in df.run.unique():
    M = fit(df[df.run != held])
    others = [r for r in fr if r != held and r in M["a"]]
    a = float(np.mean([M["a"][r] for r in others])) if held in fr else float(np.median(list(M["a"].values())))
    rng = np.random.default_rng(0)
    for _, g in tot[tot.run == held].iterrows():
        u = M["u"].get(g.game, 0.0)
        sims = []
        for _ in range(2000):
            lv = np.minimum(np.arange(1, g.n + 1), len(M["b"]))
            c = np.exp(M["mu"] + a + M["b"][lv - 1] + u + rng.normal(0, M["s"], g.n))
            sims.append(int((np.cumsum(c) <= g.tokens).sum()))
        rows.append(dict(run=held, game=g.game, actual=int(g.levels), pred=float(np.mean(sims)), franzen_like=held in fr))
R = pd.DataFrame(rows); R.to_csv("loro.csv", index=False)
for k, sub in [("all runs", R), ("franzen-like held out", R[R.franzen_like])]:
    print(k, "n=%d" % len(sub), "corr %.2f" % np.corrcoef(sub.actual, sub.pred)[0, 1],
          "MAE %.2f levels" % np.mean(np.abs(sub.actual - sub.pred)), "mean actual %.2f pred %.2f" % (sub.actual.mean(), sub.pred.mean()))
