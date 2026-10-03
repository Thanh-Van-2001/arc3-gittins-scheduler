import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = r"D:\arc3_paper\figs"
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
C = {"gittins": "#2a78d6", "franzen": "#eb6834", "equal": "#1baf7a"}
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "font.size": 12, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "lines.linewidth": 2})

# Fig 1: compute scaling of score under each scheduler
S = json.load(open(r"D:\arc3_paper\analysis\scale_ablation.json"))
x = np.array(sorted(float(k) for k in S))
fig, ax = plt.subplots(figsize=(8, 5))
for k, lab in [("gittins", "Bayesian Gittins (ours)"), ("franzen", "Franzen priority (A+B)·C"), ("equal", "Equal split")]:
    y = [S[str(v) if str(v) in S else repr(v)][k] for v in x]
    ax.plot(x, y, marker="o", ms=8, color=C[k], label=lab)
yo = [S[str(v)]["oracle"] for v in x]
ax.plot(x, yo, ls="--", color=INK2, lw=1.5, label="Clairvoyant oracle")
ax.axvline(1.0, color=INK2, lw=1, ls=":")
ax.text(1.03, 3, "competition budget\n(9 h, ~19M tokens)", color=INK2, fontsize=10)
ax.set_xscale("log", base=2); ax.set_xticks(x); ax.set_xticklabels([f"{v:g}×" for v in x])
ax.set_xlabel("Generation budget relative to one 9-hour RTX PRO 6000 run"); ax.set_ylabel("Simulated score (110 games)")
ax.set_xlim(0.2, 5.5); ax.set_ylim(0, 100)
ax.legend(loc="upper left", frameon=False, labelcolor=INK)
ax.set_title("Score vs compute: allocation is worth ~20% extra compute", loc="left", color=INK, fontsize=13)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_scaling.png", dpi=200); plt.close(fig)

# Fig 2: ablation at 1x
m = S["1.0"]
bars = [("Equal split", m["equal"], C["equal"]), ("Franzen priority", m["franzen"], C["franzen"]),
        ("Gittins, prior only", m["gittins_prior_only"], "#86b6ef"), ("Gittins, no cross-level\nlearning", m["gittins_nolearn"], "#5598e7"),
        ("Gittins, full posterior", m["gittins"], C["gittins"]), ("Clairvoyant oracle", m["oracle"], "#c3c2b7")]
fig, ax = plt.subplots(figsize=(8, 4.6))
ys = np.arange(len(bars))[::-1]
for yy, (lab, v, col) in zip(ys, bars):
    ax.barh(yy, v, height=0.62, color=col)
    ax.text(v + 0.8, yy, f"{v:.1f}", va="center", color=INK, fontsize=11)
ax.set_yticks(ys); ax.set_yticklabels([b[0] for b in bars]); ax.set_xlim(0, 60); ax.grid(axis="y", visible=False)
ax.set_xlabel("Simulated score at the competition budget")
ax.set_title("Where the gain comes from: learning each game's difficulty", loc="left", color=INK, fontsize=13)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_ablation.png", dpi=200); plt.close(fig)

# Fig 3: efficiency ratio of cleared levels (LLM agents rarely bind on efficiency)
df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv")
d = df[df.completed & (df.actions > 0)]
r = np.log2(d.baseline / d.actions)
fig, ax = plt.subplots(figsize=(8, 4.4))
bins = np.arange(-4, 4.01, 0.25)
ax.hist(r.clip(-4, 4), bins=bins, color=C["gittins"], edgecolor=SURF, linewidth=2)
ax.axvline(np.log2(np.sqrt(1.15)), color=INK, lw=1.5, ls="--")
cap_share = (d.baseline / d.actions >= np.sqrt(1.15)).mean()
ax.annotate("level score capped to the right of the line\n" + f"({cap_share:.0%} of cleared levels)", xy=(np.log2(np.sqrt(1.15)), 30), xytext=(2.2, 30), color=INK, fontsize=10, va="center", bbox=dict(boxstyle="round,pad=0.3", fc=SURF, ec=GRID), arrowprops=dict(arrowstyle="-", color=INK2, lw=1))
ax.set_xticks(range(-4, 5)); ax.set_xticklabels([f"{2**v:g}×" if v >= 0 else f"1/{2**-v:g}" for v in range(-4, 5)])
ax.set_xlabel("Human baseline actions ÷ agent actions, per cleared level"); ax.set_ylabel("Cleared levels")
ax.set_title(f"LLM agents are action-efficient: score is completion-bound (n={len(d)})", loc="left", color=INK, fontsize=13)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_efficiency.png", dpi=200); plt.close(fig)
print("ok")
