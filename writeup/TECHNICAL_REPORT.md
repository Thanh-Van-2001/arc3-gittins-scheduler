# Spend Tokens Where They Pay — Technical Report

*Nguyen Van Thanh, Loi Dinh Nhat, Le Cong Hoang (Team Talyxion).*

*Companion to the ARC Prize 2026 Paper Track write-up. Every number in this report
is produced by a script in this repository; the script is named next to the number.*

## 0. Scope and credit

The ARC-AGI-3 agent we evaluate is Daniel Franzen's Milestone-2 notebook, which is itself built on
Tufa Labs' Duck harness (Jeroen Cottaar et al.). The agent, prompts, perception aids, serving stack
and priority gate are theirs. Our contribution is (i) an empirical model of how such agents convert
generation tokens into cleared levels, (ii) a Bayesian Gittins-index policy for the gate, and
(iii) the evidence for it: simulation, ablations, robustness, and a leaderboard A/B.

## 1. The scoring function and what it implies

The official `arc_agi` scorecard (v0.9.9, `scorecard.py`) scores a cleared level as
`min(115, 100·(b/a)²)`, where `b` is the human baseline and `a` the agent's actions. It weights
level *i* of an *N*-level game by *i*, takes the weighted mean, caps it at the cleared-weight share
`Σ_{i≤L} i / Σ_{i≤N} i · 100`, and keeps each game's best play (`EnvironmentScoreList.score = max`).

**Efficiency is mostly capped.** In 282 cleared levels from 12 public runs, the median `b/a` is
1.27 and 63% of levels reach the 115 cap (`analysis/level_attempts.py`). With the game-level cap, a
game's score is approximately its cleared-weight share.

**Depth dominates.** Level weights grow linearly, so the last of seven levels is worth 7× the first.

**Replay after a win is legal but nearly worthless.** In `arcengine` 0.9.3, `handle_reset` performs a
full reset when the state is `WIN` even if `ONLY_RESET_LEVELS` is set, and the competition gateway
intercepts full resets only when the level's action count is zero. A RESET after winning a game
therefore opens a new play, and the best play counts. For near-capped LLM agents the gain is about
7 points on a single game in Franzen's demo, so we did not pursue it.

**Two regimes.** Our June LLM-free graph explorer cleared at least one level in 15 of 25 public games,
yet scored 0.22. It wandered, so its levels were nowhere near the cap. LLM agents sit in the opposite
regime, where completion binds. This explains why efficiency tricks moved the old frontier and
allocation moves the current one.

## 2. Data

`meta/collect.py` lists the public notebooks of the competition and downloads `benchmark.json` from
each one's latest output. Twelve contain per-game histories from Duck-family agents playing the 25
public demo games offline. `analysis/level_attempts.py` turns each reached level into one row:
generated tokens spent there, actions, whether it was cleared, and the human baseline. Identical
outputs re-published by forks are de-duplicated by content hash. The result is 495 attempts, 282 of
them cleared.

## 3. Cost model (`analysis/costmodel.py`)

`log T_{r,g,l} = μ + β_{min(l,6)} + α_r + u_g + ε`, with `u_g ~ N(0, σ_u²)` and `ε ~ N(0, σ²)`.

`T` is the generated tokens needed to clear level `l`. Unfinished attempts contribute the survival
term `P(T > t)`. We integrate `u_g` out with 40-point Gauss–Hermite quadrature and maximise the
likelihood with L-BFGS-B. Run effects absorb differences in model, quantisation and prompts.

| Parameter | Estimate |
|---|---|
| median level-1 cost, reference run | 53.7k tokens |
| level multipliers β (levels 1–6+) | 1, 2.06, 1.74, 2.38, 3.34, 3.25 |
| σ (level noise, log) | 0.95 |
| σ_u (game difficulty, log) | 0.77 |
| Franzen-config runs, relative cost | 0.24–0.29 |

**Validation.** We refit without each run and predict levels cleared per (run, game) from the tokens
actually spent there (`analysis/loro.py`). Correlation is 0.82, MAE 0.66 levels, n = 232, and the
mean is unbiased (1.22 actual vs 1.20 predicted). For held-out Franzen-config runs: correlation 0.66,
MAE 1.13.

**Selection.** Pooled Kaplan–Meier curves for levels ≥ 2 look much cheaper than the population model
predicts. Conditioning on the posterior difficulty of the games that reached those levels makes the
two coincide (`figs/fig_km.png`). Games that reach deep levels are the easy ones. This selection effect
is exactly the information a scheduler can exploit.

## 4. The allocation problem and the index (`analysis/gittins.py`, `harness/.../gittins_scheduler.py`)

**Decision.** At every context-trim handover, the gate admits the waiting game with the highest
priority. Non-trimmed games run first in dispatch order (the "untrimmed band"). A game keeps its slot
between trims so that prefix caching keeps working.

**Value of continuing.** For reward rate λ, game-score points per generated token:

```
Q_λ(l,t) = h(l,t)·(R_l + V_λ(l+1,0)) + (1−h(l,t))·V_λ(l,t+q) − λq,   V_λ = max(0, Q_λ)
```

- `R_l = l/(N(N+1)/2) · 100 · ē`, where `ē = E[min(1,(b/a)²)] = 0.94` on Franzen-config runs.
- `h(l,t)` is the probability of clearing within the next `q = 4000` tokens, given `t` tokens already
  spent. It comes from the log-normal survival with the game's difficulty.
- Each posterior particle `u_k` (41 particles over ±3.5σ_u) gets its own backward induction, up to
  `t = 600k` tokens per level.
- The root value under the posterior is `Σ_k w_k Q_λ^k(l,t)`. The index is the λ where this crosses
  zero, interpolated on a log grid of 80 λ values.

Continuation treats `u` as known, a QMDP-style approximation. At the root, the posterior combines the
costs of cleared levels with survival of the current level.

**Why an index.** Arms evolve only when played, rewards arrive on transitions, and abandoning is
free. This is the classical setting in which a dynamic-allocation index is optimal for discounted
rewards (Gittins 1979; Weber 1992); `Q_λ` is the restart-in-state / calibration form (Katehakis &
Veinott 1987). Our budget is finite and not discounted, so we use the index as a principled
heuristic and test it by simulation.

**Implementation.** Tables for a level count build in about 0.2 s and are cached. A decision costs
0.04 ms. The module matches the analysis implementation to 1e-15, and integer priorities preserve
the index order. Hook test: `harness/tests/test_gittins_hook.py`.

## 5. Simulator (`analysis/sim.py`)

- 110 games, with level counts drawn from the public games.
- Level costs drawn from the fitted model, with the run effect of Franzen-config runs and a
  hidden-set shift of +0.6 in log cost.
- Per-level efficiency ratios drawn from Franzen-config runs.
- Budget: 19.4M generated tokens. That is 532 minutes at the 609 tokens/s harness-side throughput
  Franzen reports.
- Policies: equal split; Franzen's priority ported verbatim, including tail lookup "remaining", score
  normalisation and the 20% tail fade; the Gittins index; and a clairvoyant oracle, which is a
  precedence-constrained knapsack over each game's concave hull of cumulative cost and score.
- Optional gate mechanics: an initial forced chunk per game, and leases between handovers.

## 6. Results

**Main comparison**, at 1× budget with a 40k first chunk and 30k leases, over 5 seeds
(`analysis/ablate_scale.py`):

| Policy | Score |
|---|---|
| Equal | 25.6 |
| Franzen | 31.6 |
| Gittins | 37.1 |
| Oracle | 51.3 |

**Robustness** (`analysis/robust.py`, 4 seeds × 2 lease settings each). Gittins minus Franzen: matched
+6.3/+5.1; hidden set easier +6.3/+7.8; harder +4.2/+3.8; Student-t₃ costs +8.4/+7.3; game spread ×1.4
+6.8/+6.6; ×0.5 +4.9/+3.5; level noise ×1.3 +3.3/+3.2. The minimum over individual seeds was positive
in every cell.

**Gate mechanics** (`analysis/realistic.py`, 6 seeds). First chunk / lease of 0/0: +5.4 ± 0.5;
40k/30k: +5.1 ± 0.5; 60k/50k: +4.1 ± 0.3; 80k/60k: +5.1 ± 0.5.

**Ablation.** Prior-only index 29.0; without cross-level learning 33.8; full posterior 37.1.

**Extensions that did not help** (`analysis/extras.py`). Endgame-myopic tables over the last 15%:
−0.8 to +0.7. Tables matched to the true hidden-set shift: −0.5 to +1.1.

**Mechanism** (`analysis/fig_alloc.py`, 6 worlds). Both policies clear the same number of levels
(3.13 vs 3.12 per game). Gittins moves tokens away from the hardest 40% of games (34.5% → 28.7% of
the budget) and into easy games, where it clears deeper and more valuable levels.

**Compute scaling.** Equal / Franzen / Gittins / Oracle scores:

| Budget | Equal | Franzen | Gittins | Oracle |
|---|---|---|---|---|
| 0.25× | 5.4 | 7.0 | 9.0 | 22.9 |
| 0.5× | 11.6 | 17.5 | 19.7 | 34.7 |
| 1× | 25.6 | 31.6 | 37.1 | 51.3 |
| 2× | 47.3 | 55.0 | 59.0 | 71.4 |
| 4× | 70.5 | 85.3 | 86.4 | 91.6 |

At 1×, Gittins equals Franzen at about 1.2× compute. Tufa Labs' 52.5 lies at about 1.9× on Franzen's
curve.

**Why naive reallocation does not help** (`analysis/drop_l0.py`, 6 seeds, same worlds, realistic gate).
On the Kaggle forum, Scott Le Grand reported that demoting games stuck at level 0 to give L1+/L2+ games
more time "did no good". The simulator reproduces this:

| Policy | vs Franzen |
|---|---|
| Franzen priority + demote games still at level 0 after 50k / 100k / 150k tokens | +0.2 / +0.0 / +0.0 |
| Same, plus a 2× boost for games at level ≥ 2 | +0.7 |
| Bayesian Gittins index | **+4.5 ± 0.7** |

Franzen's completion factor C already decays to near zero for long-stuck levels, so explicit
demotion is redundant. The gain requires inferring each game's difficulty from the levels it has
already cleared. This matches the ablation, where the prior-only index falls below Franzen.

**Where the tokens go after a death** (public runs, `results/budget_*`).
- 23% of level attempts contain at least one death, and 18.4% of all generated tokens are spent after the first death in a level.
- In Franzen's demo, the model itself diagnoses 4 of 5 deaths as move-budget deaths: it reads the border bar by eye and miscounts.
- Random play on the 25 public games with the real engine shows that 23 games have a border bar (about 63 cells, losing 0.5–1.3 cells per action).
- A deterministic CPU meter tracks each border colour per level attempt and restarts its measurement after refills (`analysis/budget_meter.py`). On attempts that end in a budget death in 20 games, it gives an estimate at 96% of steps. The actions-left error has median 0, MAE 8.5 and 4% median relative error, with no false "≤3 actions left" alarms on surviving attempts.
- Three games remain inaccurate (ls20, lf52, ft09).

**Serving configuration is near its frontier** (`analysis/tput.py`, commit-mode runs, 20 games × 12 min,
gate saturated). Harness-side generation throughput: Franzen's 10 streams with 3 speculative steps,
624 tokens/s (94.2% of prompt tokens served from cache); 2 speculative steps, 545 (−13%);
4 speculative steps, fails at start-up because Qwen3.8's QSA attention caps draft tokens at 4;
12 streams, 669 (+7%, cache 93.6%). The 12-stream gain is measured before contexts reach their
steady-state size (58k–128k tokens). At steady state, 12 streams need about 1.1M KV tokens against a
1.01M pool, so the gain is likely to shrink. We therefore kept Franzen's serving configuration. Pennyroyal's online MXFP8 (`SGLANG_SM120_ONLINE_MXFP8`), suggested by public notes as worth +15–28% decode, does free memory (KV pool 1.01M → 1.36M tokens), but on Franzen's W4A16 AutoRound checkpoint it **cut** generation throughput: 395 tokens/s at 10 streams (−37%) and 494 at 12 streams (−21%). The published gain was measured on an NVFP4 checkpoint and does not transfer.

**Leaderboard noise** (`analysis/noise.py`). Splitting level noise into a part fixed per (game, level)
and a part redrawn per run (ICC 0.46) gives a single-submission SD of about 3.7 points on 55 games.
About three submissions per arm are needed to resolve a 5-point effect at 2σ.

## 7. Leaderboard A/B (pre-registered in `PREREGISTRATION.md`)

Arms: `thnhnguyn2001/arc3-talyxion-base` (Franzen's notebook, only the commit-time demo shortened)
and `thnhnguyn2001/arc3-talyxion-gittins` (+ `talyxion_gittins.patch`, `ARC3_PRIORITY_POLICY=gittins`).
The competition allows one submission per UTC day; the schedule is ABBAAB.

**[Results table: ref, date, arm, public score; arm means; Welch interval; permutation p.]**

## 8. Limitations

- **Model form.** Log-normal with a single difficulty factor per game. Heavy tails did not change the
  ranking, but structured effects could, for example a game whose late levels are much harder than
  its early ones.
- **Hidden-set shift.** One number, calibrated on the leaderboard band of Franzen's notebook.
  Misspecifying it by ±0.6 did not reverse the ranking.
- **Simulator abstractions.** Throughput is treated as fixed, and the cost of switching games beyond
  the lease mechanics is ignored.
- **Data mix.** The public runs mix models and configurations; run effects absorb the mean, not
  interactions.

## 9. Reproduction

```
python meta/collect.py                      # public benchmark.json files
cd analysis
python level_attempts.py && python costmodel.py && python loro.py
python robust.py && python realistic.py && python ablate_scale.py && python extras.py && python noise.py
python figs.py && python fig_km.py && python fig_alloc.py && python cover.py
```

The Kaggle notebooks are in `kernels/`. The patch applies with
`git apply --include=ARC3-Inference/*` on top of Franzen's patch over Duck commit `7652836`.

## References

- Gittins, J. C. (1979). Bandit processes and dynamic allocation indices. *JRSS-B* 41(2):148–164. doi:10.1111/j.2517-6161.1979.tb01068.x
- Katehakis, M. N. & Veinott, A. F. (1987). The multi-armed bandit problem: decomposition and computation. *Math. Oper. Res.* 12(2):262–268. doi:10.1287/moor.12.2.262
- Weber, R. (1992). On the Gittins index for multiarmed bandits. *Ann. Appl. Probab.* 2(4). doi:10.1214/aoap/1177005588
- Kaplan, E. L. & Meier, P. (1958). Nonparametric estimation from incomplete observations. *JASA* 53(282):457–481. doi:10.1080/01621459.1958.10501452
- Chollet, F. (2019). On the Measure of Intelligence. arXiv:1911.01547.
- Tufa Labs. Duck harness. https://github.com/Tufalabs/duck-harness
- Franzen, D. ARC-AGI-3 Milestone 2 solution and write-up. https://github.com/da-fr/arc-agi-3-solution
