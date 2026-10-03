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
