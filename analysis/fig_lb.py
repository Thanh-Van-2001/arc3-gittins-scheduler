"""Simulated vs measured: predicted gain of the Gittins scheduler vs leaderboard runs."""
import csv, json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
C = {"gittins": "#2a78d6", "franzen": "#eb6834"}
rows = list(csv.DictReader(open(r"D:\arc3_paper\results\lb_submissions.csv")))
combo = [float(r["public_score"]) for r in rows if r["arm"] == "combo" and r["public_score"]]
base = [float(r["public_score"]) for r in rows if r["arm"] == "base" and r["public_score"]]
F = json.load(open(r"D:\arc3_paper\analysis\faithful.json"))["68000/35000"]
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(8, 4.6))
ref = 25.77
# simulated prediction, anchored at the community Franzen mean
ax.errorbar([0], [ref], yerr=[[3.93], [3.93]], fmt="o", color=C["franzen"], ms=8, capsize=6, lw=2)
ax.errorbar([1], [ref + F["diff"]], yerr=[[F["se"] * 1.96], [F["se"] * 1.96]], fmt="D", color=C["gittins"], ms=8, capsize=6, lw=2, mfc=SURF, mew=2)
ax.scatter([2] * len(base), base, color=C["franzen"], s=46, zorder=3)
ax.scatter([3] * len(combo), combo, color=C["gittins"], s=46, zorder=3)
ax.hlines(np.mean(combo), 2.75, 3.25, color=C["gittins"], lw=2)
for x, lab in [(0, f"Franzen notebook\ncommunity copies\n{ref} ± 3.93 (SD)"), (1, f"Gittins, simulated\n(+{F['diff']:.1f} ± {1.96*F['se']:.1f})"),
               (2, "Franzen notebook\nour run"), (3, f"Gittins + fix\nour runs (mean {np.mean(combo):.2f})")]:
    ax.text(x, 17.6, lab, ha="center", va="top", fontsize=9.5, color=INK2)
ax.set_xticks([]); ax.set_xlim(-0.6, 3.6); ax.set_ylim(17.8, 37); ax.grid(axis="y", color=GRID)
ax.set_ylabel("public leaderboard score", color=INK2)
ax.set_title("Predicted vs measured: the scheduler helps, by less than the simulator says", loc="left", color=INK, fontsize=12)
fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig(r"D:\arc3_paper\figs\fig_lb.png", dpi=180); print("ok", combo, base)
