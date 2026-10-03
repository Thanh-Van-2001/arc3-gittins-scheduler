import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from costmodel import fit
from sim import sample_world, simulate, make_franzen
from gittins import GittinsTables, make_gittins
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
C = {"gittins": "#2a78d6", "franzen": "#eb6834"}
df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv"); M = fit(df)
nl_pool = df.groupby("game").n_levels.first().values
fr = [r for r, a in M["a"].items() if np.exp(a) < 0.35]
dd = df[df.completed & (df.actions > 0) & df.run.isin(fr)]; rp = (dd.baseline / dd.actions).values
re_ = float(np.mean([M["a"][r] for r in fr])); eff = float(np.mean(np.minimum(1, rp ** 2)))
tab = GittinsTables(M, re_, shift=0.6, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)
w = sample_world(np.random.default_rng(42), 110, M, nl_pool, rp, re_, 0.6)
res = {}
for name, pol in [("franzen", make_franzen()), ("gittins", make_gittins(tab))]:
    score, st = simulate(w, 19.4e6, pol, lease=30000, first_chunk=40000)
    # tokens actually spent per game: cleared-level costs plus progress on the current level
    spent = np.array([sum(st.cleared_costs[g]) + st.t[g] for g in range(110)])
    res[name] = (spent, st.level.copy(), score)
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, axs = plt.subplots(1, 2, figsize=(12, 4.4))
for name, lab in [("franzen", "Franzen priority"), ("gittins", "Bayesian Gittins")]:
    sp, lv, sc = res[name]
    axs[0].scatter(np.exp(w.u), sp / 1e3, s=22, color=C[name], alpha=0.75, label=f"{lab} (score {sc:.1f})", edgecolor=SURF, linewidth=0.6)
axs[0].set_xscale("log"); axs[0].set_xlabel("true game difficulty (cost multiplier, hidden from both policies)", color=INK2)
axs[0].set_ylabel("generated tokens allocated (k)", color=INK2); axs[0].grid(color=GRID); axs[0].legend(frameon=False)
axs[0].set_title("Tokens per game vs hidden difficulty (one world)", loc="left", color=INK, fontsize=12)
# right panel: average over several worlds so the difficulty-quintile pattern is not one draw's noise
rows = []
for sd in range(6):
    ww = sample_world(np.random.default_rng(600 + sd), 110, M, nl_pool, rp, re_, 0.6)
    qq = pd.qcut(np.exp(ww.u), 5, labels=False)
    for name, pol in [("franzen", make_franzen()), ("gittins", make_gittins(tab))]:
        _, st = simulate(ww, 19.4e6, pol, lease=30000, first_chunk=40000)
        sp = np.array([sum(st.cleared_costs[g]) + st.t[g] for g in range(110)])
        for k in range(5):
            m = qq == k
            rows.append(dict(policy=name, q=k, levels=st.level[m].mean(), share=sp[m].sum() / sp.sum()))
R = pd.DataFrame(rows).groupby(["policy", "q"]).mean().reset_index()
print(R.round(3).to_string())
x = np.arange(5)
for i2, (name, lab) in enumerate([("franzen", "Franzen"), ("gittins", "Gittins")]):
    v = R[R.policy == name].sort_values("q")
    axs[1].bar(x + (i2 - 0.5) * 0.38, v.levels.values, width=0.36, color=C[name], label=lab)
    for xx, (lv_, sh) in zip(x, zip(v.levels.values, v.share.values)):
        axs[1].text(xx + (i2 - 0.5) * 0.38, lv_ + 0.08, f"{sh:.0%}", ha="center", fontsize=8, color=INK2)
axs[1].set_xticks(x); axs[1].set_xticklabels(["easiest 20%", "2nd", "3rd", "4th", "hardest 20%"])
axs[1].set_ylabel("mean levels cleared (6 worlds)", color=INK2); axs[1].grid(axis="y", color=GRID); axs[1].legend(frameon=False)
axs[1].set_title("Same number of levels, but deeper ones (labels: token share)", loc="left", color=INK, fontsize=12)
fig.tight_layout(); fig.savefig(r"D:\arc3_paper\figs\fig_alloc.png", dpi=180)
for name in res:
    sp, lv, sc = res[name]
    hard = np.exp(w.u) > np.quantile(np.exp(w.u), 0.8)
    print(name, "score %.1f" % sc, "share of tokens on hardest 20%%: %.0f%%" % (100 * sp[hard].sum() / sp.sum()))
