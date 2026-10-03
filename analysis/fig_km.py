import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
from costmodel import fit, GH_X, GH_W
SURF, INK, INK2, GRID, BLUE, ORANGE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6", "#eb6834"
df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv"); df = df[df.tokens > 0]; M = fit(df)
df["norm"] = df.tokens / np.exp(df.run.map(M["a"]))  # tokens in reference-run units
def km(t, e):
    o = np.argsort(t); t, e = t[o], e[o]; n = len(t); S = 1.0; xs, ys = [0], [1.0]
    for i in range(n):
        if e[i]: S *= 1 - 1 / (n - i)
        xs.append(t[i]); ys.append(S)
    return np.array(xs), np.array(ys)
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, axs = plt.subplots(1, 4, figsize=(13, 3.6), sharey=True)
grid = np.geomspace(1e3, 3e6, 200)
for k, ax in enumerate(axs, start=1):
    sub = df[df.level == k] if k < 4 else df[df.level >= 4]
    x, y = km(sub.norm.values, sub.completed.values.astype(bool))
    ax.step(x, y, where="post", color=BLUE, lw=2, label="Kaplan–Meier (data)")
    # model survival for the SAME attempts: each uses its own level offset and its game's posterior
    # difficulty (games that reach deep levels are the easier ones - a selection effect)
    lvl = np.minimum(sub.level.values, len(M["b"]))
    m = M["mu"] + M["b"][lvl - 1] + sub.game.map(M["u"]).values
    S = stats.norm.sf((np.log(grid)[:, None] - m[None, :]) / M["s"]).mean(1)
    S0 = (stats.norm.sf((np.log(grid)[:, None] - M["mu"] - M["b"][min(k, len(M["b"])) - 1] - M["su"] * GH_X[None, :]) / M["s"]) * GH_W).sum(1)
    ax.plot(grid, S, color=ORANGE, lw=2, ls="--", label="model, same games")
    ax.plot(grid, S0, color=INK2, lw=1, ls=":", label="model, all games (prior)")
    ax.set_xscale("log"); ax.set_xlim(2e3, 3e6); ax.grid(color=GRID)
    ax.set_title(f"level {k}" + ("+" if k == 4 else "") + f"  (n={len(sub)}, cleared {sub.completed.mean():.0%})", color=INK, fontsize=11, loc="left")
    ax.set_xlabel("generated tokens (reference-run units)", color=INK2, fontsize=10)
axs[0].set_ylabel("P(level not yet cleared)", color=INK2)
h, l = axs[0].get_legend_handles_labels(); fig.legend(h, l, loc="upper center", ncol=3, frameon=False, fontsize=10)
fig.tight_layout(); fig.savefig(r"D:\arc3_paper\figs\fig_km.png", dpi=180); print("ok")
