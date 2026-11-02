"""Cover image for the Paper Track writeup (v3): the leaderboard ladder and the three measurements of the scheduler.

Numbers: results/lb_submissions.csv (ladder; means exclude zero/error runs), community tally (tantan0327, 76 stock
Franzen copies), analysis/gate_ab.py over results/run1..run4 (paired offline +3.24 +/- 2.47), simulator (+5.8 +/- 0.4).
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
ACCENT, BASE = "#2a78d6", "#b9b8b1"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "font.size": 13, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.spines.left": False, "axes.edgecolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})

fig = plt.figure(figsize=(12, 6))
fig.text(0.04, 0.905, "Spend tokens where they pay", fontsize=27, color=INK, weight="bold")
fig.text(0.04, 0.835, "What scheduling, throughput and reliability buy an ARC-AGI-3 agent", fontsize=16, color=INK2)
fig.text(0.04, 0.012, "Team Talyxion · built on Franzen's Milestone-2 notebook, Tufa Labs' Duck harness and JustAdev742's tooling",
         fontsize=10.5, color=MUTED)

# left: leaderboard ladder (mean +/- SD of valid runs)
ladder = [("Stock Franzen copies", 26.8, 3.6, 76, False),
          ("+ Gittins scheduler + fix", 25.5, 3.1, 4, False),
          ("+ REAP-448, 14 streams", 26.8, 1.8, 7, False),
          ("+ harness bundle, token map", 28.3, 2.5, 6, False),
          ("+ fine-tuned MTP draft", 28.8, 3.6, 7, True)]
ax = fig.add_axes([0.255, 0.16, 0.30, 0.57])
for i, (lab, m, sd, n, hi) in enumerate(ladder):
    y = len(ladder) - 1 - i
    col = ACCENT if hi else BASE
    ax.plot([m - sd, m + sd], [y, y], color=col, lw=2, solid_capstyle="round")
    ax.plot(m, y, "o", ms=9, color=col, markeredgecolor=SURF, markeredgewidth=2)
    ax.text(m, y + 0.3, f"{m:.1f}  (n={n})", ha="center", va="bottom", fontsize=11.5, color=INK)
    ax.text(17.6, y, lab, va="center", ha="right", fontsize=12, color=INK if hi else INK2)
ax.plot(35.73, 0, "D", ms=8, color=ACCENT, markeredgecolor=SURF, markeredgewidth=1.5)
ax.text(35.73, 0.3, "best run\n35.73", ha="center", va="bottom", fontsize=10.5, color=INK)
ax.set_xlim(18, 38)
ax.set_ylim(-0.5, len(ladder) - 0.25)
ax.set_yticks([])
ax.grid(axis="x", color=GRID)
ax.set_xlabel("public leaderboard score (mean ± SD)", color=INK2)
ax.set_title("Leaderboard, 31 submissions", color=INK2, fontsize=13, loc="left", x=-0.82)

# right: one scheduler, three measurements (gain over Franzen's gate)
ax2 = fig.add_axes([0.70, 0.16, 0.27, 0.57])
floor = 3.5  # 2 SE of a difference of means at ~7 runs per arm, SD ~3.3
ax2.axhspan(-floor, floor, xmin=0.78, xmax=0.98, color=GRID)
pts = [(0, 5.8, 0.4, "Simulator"), (1, 3.24, 2.47, "Paired runs\n(4 pairs, ±1 SE)")]
for x, m, e, lab in pts:
    ax2.plot([x, x], [m - e, m + e], color=ACCENT, lw=2, solid_capstyle="round")
    ax2.plot(x, m, "o", ms=9, color=ACCENT, markeredgecolor=SURF, markeredgewidth=2)
    ax2.text(x + 0.12, m, f"+{m:.1f}", va="center", fontsize=12, color=INK)
ax2.text(2, 0, "noise\nfloor\n±3.5", ha="center", va="center", fontsize=11, color=INK2)
ax2.axhline(0, color=INK2, lw=1)
ax2.set_xticks([0, 1, 2])
ax2.set_xticklabels(["Simulator", "Paired\noffline runs", "Leader-\nboard"], fontsize=11.5)
ax2.set_xlim(-0.5, 2.6)
ax2.set_ylim(-4.5, 8)
ax2.grid(axis="y", color=GRID)
ax2.spines["left"].set_visible(True)
ax2.set_ylabel("gain over Franzen's gate (points)", color=INK2)
ax2.set_title("One scheduler, three measurements", color=INK2, fontsize=13, loc="left")

fig.savefig(r"D:\arc3_paper\figs\cover.png", dpi=150)
print("ok")
