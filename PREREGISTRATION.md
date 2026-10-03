# Pre-registered leaderboard A/B (written 2026-10-03, before any leaderboard result)

**Hypothesis.** Replacing Franzen's `(A+B)·C` admission priority with the Bayesian Gittins index
(`ARC3_PRIORITY_POLICY=gittins`, everything else byte-identical) raises the public ARC-AGI-3 score.

**Prediction (from the calibrated simulator, `analysis/noise.py`).** Public-LB difference ≈ +5 to +6
points; run-to-run SD of a single submission ≈ 3.6–3.8 points.

**Design.** Two private notebooks, `thnhnguyn2001/arc3-talyxion-base` (Franzen M2 notebook, only the
commit-mode demo shortened) and `thnhnguyn2001/arc3-talyxion-gittins` (+ `harness/talyxion_gittins.patch`).
Target 3 scored submissions per arm, interleaved in time. Errored/timeout submissions are reported,
not dropped silently.

**Analysis.** Report every scored submission. Primary statistic: difference of arm means with a
Welch t-interval; secondary: one-sided permutation test over all submissions. No submissions are
excluded after seeing scores.

**Amendment (2026-10-03 14:00 +07, before any score):** the competition now allows **1 submission per
UTC day** (Kaggle: "0 submissions remaining today" after the first). Schedule: one submission per day,
alternating arms starting base, gittins, gittins, base, base, gittins (ABBAAB to balance any drift in
queue/hardware conditions over time). Submission refs are logged in `results/lb_submissions.csv`.

**Exploratory arm (declared 2026-10-04, outside the confirmatory A/B):** after the six A/B submissions,
2–3 submissions of `kernels/combo` (Gittins + 12 serving streams, +7% throughput in the sweep). Reported
separately as exploratory; it does not enter the A/B analysis.

**Amendment 2 (2026-10-04 05:40 +07, before any Gittins score):** the competition allows
`maxDailySubmissions = 1` (confirmed via the Kaggle API) and the team wants every remaining slot spent
on the configuration with the highest expected score. The base arm is therefore **not resubmitted**.
Design becomes: Gittins arm × 3 (then the exploratory combo arm), compared against the base reference
set = our base #1 (25.29) plus the independently reported scores of the identical Franzen notebook
(27.89 in his write-up, 31.47 best public). This is weaker than a balanced A/B and is reported as such.
