"""How noisy is one leaderboard run? Split level-cost noise into a part fixed per (game, level) and
a part redrawn per run, then simulate repeated runs of the same policy on the same 55 games."""
import numpy as np, pandas as pd
from costmodel import fit
from sim import sample_world, simulate, make_franzen, World
from gittins import GittinsTables, make_gittins
df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv"); M = fit(df)
d = df[(df.tokens > 0) & df.completed].copy()
lv = d.level.clip(upper=6)
d["res"] = np.log(d.tokens) - (M["mu"] + M["b"][lv - 1] + d.run.map(M["a"]) + d.game.map(M["u"]))
grp = d.groupby(["game", "level"]).res
multi = d[grp.transform("size") >= 2]
within = multi.groupby(["game", "level"]).res.var(ddof=1).mean()
total = d.res.var(ddof=1)
icc = max(0.0, 1 - within / total)
print(f"completed-level residual var {total:.3f}, within (game,level) across runs {within:.3f}, ICC {icc:.2f}, pairs n={len(multi)}")
nl_pool = df.groupby("game").n_levels.first().values
fr_runs = [r for r, a in M["a"].items() if np.exp(a) < 0.35]
dd = df[df.completed & (df.actions > 0) & df.run.isin(fr_runs)]
ratio_pool = (dd.baseline / dd.actions).values
run_eff = float(np.mean([M["a"][r] for r in fr_runs])); eff = float(np.mean(np.minimum(1.0, ratio_pool ** 2)))
tab = GittinsTables(M, run_eff, shift=0.6, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)
G_all, B = 110, 19.4e6
s_fixed, s_run = M["s"] * np.sqrt(icc), M["s"] * np.sqrt(1 - icc)
rng = np.random.default_rng(7)
u = rng.normal(0.6, M["su"], G_all); nl = rng.choice(nl_pool, G_all)
fixed = [rng.normal(0, s_fixed, n) for n in nl]
ratios = [rng.choice(ratio_pool, n) for n in nl]
public = rng.choice(G_all, 55, replace=False)
out = {"franzen": [], "gittins": []}
for rep in range(8):
    r2 = np.random.default_rng(1000 + rep)
    cost = []
    for g in range(G_all):
        l = np.minimum(np.arange(1, nl[g] + 1), len(M["b"]))
        cost.append(np.exp(M["mu"] + run_eff + M["b"][l - 1] + u[g] + fixed[g] + r2.normal(0, s_run, nl[g])))
    w = World(nl, cost, ratios, u)
    for name, pol in [("franzen", make_franzen()), ("gittins", make_gittins(tab))]:
        _, st = simulate(w, B, pol, lease=30000, first_chunk=40000)
        from sim import game_score
        sc = np.array([game_score(st.level[g], nl[g], ratios[g]) for g in range(G_all)])
        out[name].append(sc[public].mean())
for k, v in out.items():
    print(k, "public-LB mean %.2f  run-to-run SD %.2f" % (np.mean(v), np.std(v, ddof=1)))
diff = np.array(out["gittins"]) - np.array(out["franzen"])
print("paired diff mean %.2f SD %.2f -> submissions per arm for 2-sigma: %.1f" % (diff.mean(), np.std(out["gittins"], ddof=1),
      max(1, (2 * np.sqrt(np.var(out["gittins"], ddof=1) + np.var(out["franzen"], ddof=1)) / max(diff.mean(), 1e-9)) ** 2)))
