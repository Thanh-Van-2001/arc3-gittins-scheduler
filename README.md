# Spend tokens where they pay — Bayesian Gittins scheduling for ARC-AGI-3 agents

Team Talyxion, ARC Prize 2026 Paper Track. Built on Tufa Labs' Duck harness (MIT) and
Daniel Franzen's Milestone-2 solution (Apache-2.0).

| Path | What it is |
|---|---|
| `harness/talyxion_gittins.patch` | The whole contribution as a patch on top of Franzen's harness: `inference/agent/gittins_scheduler.py` + priority-gate hook. Enable with `ARC3_PRIORITY_POLICY=gittins`. |
| `harness/franzen.patch` | Franzen's harness patch (from his public notebook), applied to Duck commit `7652836`. |
| `kernels/base`, `kernels/gittins` | The two Kaggle notebooks used for the leaderboard A/B (identical except for the patch + env var). |
| `meta/collect.py` | Downloads `benchmark.json` from public competition notebooks. |
| `analysis/level_attempts.py` | Flattens those runs into one row per level attempt → `level_attempts.csv`. |
| `analysis/costmodel.py` | Censored log-normal cost model with a game random effect. |
| `analysis/loro.py` | Leave-one-run-out validation. |
| `analysis/sim.py`, `gittins.py` | Simulator, policies (equal, Franzen, Gittins, oracle). |
| `analysis/robust.py`, `realistic.py`, `ablate_scale.py`, `extras.py` | Experiments behind every table/figure. |
| `analysis/figs.py`, `cover.py` | Figures. |
| `writeup/WRITEUP.md` | Kaggle writeup (≤1500 words). |

Reproduce: `python meta/collect.py && cd analysis && python level_attempts.py && python costmodel.py && python robust.py && python ablate_scale.py && python figs.py`.
