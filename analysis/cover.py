import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
C = {"gittins": "#2a78d6", "franzen": "#eb6834", "equal": "#1baf7a"}
S = json.load(open(r"D:\arc3_paper\analysis\scale_ablation.json"))
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "font.size": 13, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
fig = plt.figure(figsize=(12, 6))
fig.text(0.04, 0.90, "Spend tokens where they pay", fontsize=26, color=INK, weight="bold")
fig.text(0.04, 0.83, "Bayesian Gittins scheduling for ARC-AGI-3 agents", fontsize=17, color=INK2)
ax = fig.add_axes([0.07, 0.12, 0.40, 0.6])
x = np.array([0.25, 0.5, 1.0, 2.0, 4.0])
for k, lab in [("gittins", "Bayesian Gittins (ours)"), ("franzen", "Franzen priority"), ("equal", "Equal split")]:
    ax.plot(x, [S[str(v)][k] for v in x], marker="o", ms=7, lw=2.2, color=C[k], label=lab)
ax.plot(x, [S[str(v)]["oracle"] for v in x], ls="--", color=INK2, lw=1.5, label="Clairvoyant oracle")
ax.set_xscale("log", base=2); ax.set_xticks(x); ax.set_xticklabels([f"{v:g}×" for v in x]); ax.set_ylim(0, 100)
ax.axvline(1, color=INK2, ls=":", lw=1); ax.grid(color=GRID); ax.legend(frameon=False, fontsize=11, loc="upper left")
ax.set_xlabel("compute budget (1× = one 9-h run)", color=INK2); ax.set_ylabel("simulated score", color=INK2)
ax2 = fig.add_axes([0.62, 0.12, 0.34, 0.6])
m = S["1.0"]
bars = [("Equal", m["equal"], C["equal"]), ("Franzen", m["franzen"], C["franzen"]), ("Gittins", m["gittins"], C["gittins"]), ("Oracle", m["oracle"], "#c3c2b7")]
for i, (lab, v, col) in enumerate(bars):
    ax2.bar(i, v, width=0.62, color=col)
    ax2.text(i, v + 1.2, f"{v:.1f}", ha="center", color=INK, fontsize=13)
ax2.set_xticks(range(len(bars))); ax2.set_xticklabels([b[0] for b in bars]); ax2.set_ylim(0, 60); ax2.grid(axis="y", color=GRID)
ax2.set_title("score at the competition budget", color=INK2, fontsize=13, loc="left")
fig.savefig(r"D:\arc3_paper\figs\cover.png", dpi=150); print("ok")
