# Spend Tokens Where They Pay: What Compute Allocation Can and Cannot Buy an ARC-AGI-3 Agent

**Subtitle:** A calibrated model of how LLM agents turn generation tokens into cleared levels, a Bayesian Gittins scheduler that the model values at about six points, and a pre-registered leaderboard test that so far measures one to two.

*Nguyen Van Thanh, Loi Dinh Nhat, Le Cong Hoang (Team Talyxion). The agent is Daniel Franzen's Milestone-2 notebook, which is built on Tufa Labs' Duck harness. All credit for the agent is theirs; our work is the model, the scheduler and the measurements.*

---

## 1. Summary

Strong ARC-AGI-3 submissions run one loop: a local Qwen3.8-Flash-Next plays 110 hidden games through a Python tool on one RTX PRO 6000 for nine hours. We ask a narrower question: **which game should receive the next block of tokens?**

1. **Diagnosis.** In 282 cleared levels from 12 public runs, the agent beat the human action baseline 71% of the time, and 63% of cleared levels hit the per-level score cap. The score is bound by levels cleared, and clearing is bound by generation compute.
2. **Model.** A censored log-normal model of tokens-to-clear, with a latent difficulty per game. On 232 held-out (run, game) pairs it predicts levels cleared with correlation 0.82.
3. **Method.** An exact Bayesian Gittins index for the harness's priority gate: 161 lines, CPU-only, 0.04 ms per decision.
4. **Prediction.** A trace-calibrated simulator that hands over slots only at context trims, as the real harness does, predicts **+5.8 ± 0.4** points over Franzen's priority. The gain holds in all 14 misspecification scenarios we tried.
5. **Measurement.** On the leaderboard (Table 1) the gain is positive in direction but far smaller than predicted; we report the gap and what it teaches.

**Table 1.** Public leaderboard scores (55 hidden games).

| Configuration | Runs | Score |
|---|---|---|
| Franzen notebook, community copies (Kaggle forum, thread 745062) | hundreds | 25.77 ± 3.93 (mean ± SD) |
| Franzen notebook, our run | 1 | 25.29 |
| **Franzen + Gittins + retained-function fix (ours)** | 3 | **25.49, 28.45, 26.72** (mean 26.89, SD 1.49) |

The mean difference is +1.1 against the community copies and +1.6 against our own base run (z ≈ 0.5). With a discounted prior from the simulator, our estimate of the effect is **+1.8 ± 1.8**. One caveat: the community copies were submitted on 30 Sep–1 Oct, which overlaps a Kaggle outage that cut some runs to 2–4 hours. That control may therefore be biased low, so the measured gain is an upper bound.

## 2. Why the score is completion-bound

A cleared level scores `min(115, 100·(baseline/actions)²)`; level *i* weighs *i*; a game is capped at its cleared-weight share; the best play counts.

- **Agents are already action-efficient.** The median ratio of human to agent actions is 1.27.
- **Depth pays.** In a 7-level game the last level is worth 7× the first.
- **Replaying after a win is useless.** A post-win RESET opens a new scored play, but only 6 of 356 game runs were won outright, all already at 93–100.

Our own LLM-free June explorer was in the opposite regime: it cleared levels in 15 of 25 public games yet scored 0.22 because it wandered. Today's frontier sits in the completion-bound regime, so allocation matters more than efficiency.

## 3. A cost model of agent progress

Per level reached we record generated tokens and whether it cleared (else right-censored):

`log T = μ + β_level + α_run + u_game + ε`, with `u_game ~ N(0, σu²)` and `ε ~ N(0, σ²)`.

Censored maximum likelihood (Gauss–Hermite) on 495 attempts, 25 public games, 12 public runs gives σu = 0.77 (hardest and easiest games differ ~20×), σ = 0.95, and deeper levels costing 1.7–3.3× level 1.

Deep-level Kaplan–Meier curves match the model only when conditioned on each game's posterior difficulty: games that reach deep levels are the easy ones, which is what a scheduler can exploit.

## 4. The Gittins index

A game is a bandit arm that pays its score weight when a level clears and can be abandoned at any time. Backward induction gives the value of continuing:

`Q_λ(l,t) = h(l,t)·(R_l + V_λ(l+1,0)) + (1−h(l,t))·V_λ(l,t+q) − λq`, with `V_λ = max(0, Q_λ)`.

Here `h` is the posterior hazard of clearing level `l` in the next 4k tokens, given `t` tokens already spent. The index is the λ at which continuing breaks even (Gittins 1979; Katehakis & Veinott 1987; Weber 1992).

The posterior over `u_game` updates on every cleared level and on how long the current level has resisted. Franzen's `(A+B)·C` prices level value, continuation and a decaying completion curve, but learns nothing about the individual game.

## 5. What the simulator predicts, and why naive reallocation fails

Setup: 110 games, 19.4M tokens (9 h at 609 tokens/s), hidden-set difficulty calibrated to the community mean.

- **Main comparison (equal / Franzen / Gittins / oracle):** 25.6 / 31.6 / 37.1 / 51.3.
- **Robustness:** the gain stays positive in every misspecification we tried (difficulty shift, heavy tails, spread, noise): +3.2 to +8.4.
- **Faithful gate.** Handovers only at trims, which we measured in Franzen's logs: the first trim comes after about 68k generated tokens, so 39% of the budget is spent before any priority decision, and later trims come about every 35k. The gain is still +4.7 to +6.7.

**Ablation.** With the posterior updates removed, the index scores 29.0, below Franzen's 31.6. The gain is Bayesian learning, not the shape of the index.

**This explains a public negative result.** On the forum, Scott Le Grand reported that demoting games stuck at level 0 "did no good". Our simulator agrees: that heuristic is worth +0.0 to +0.7, because Franzen's completion factor already stops funding stuck levels.

## 6. The leaderboard test

**Design.** We pre-registered the design before seeing any score (`PREREGISTRATION.md`, with timestamped amendments). The original plan was a balanced A/B. Once the competition allowed only one submission per day, we used the community distribution of hundreds of single-run Franzen copies (forum thread 745062) as the control. This also validated our noise model: we had predicted an SD of 3.6–3.8, against the observed 3.93.

**Mechanism check.** The commit-time demo never contends for slots, so we ran a Kaggle diagnostic with 25 games, 4 slots and every pricing logged.

- The scheduler handed over 105 times.
- Its indices spanned a 5× range.
- Five games that kept clearing levels received 70% of all tokens.
- The correlation between tokens received and levels cleared was 0.91.

The gate works as designed.

**Result.** The observed +1.2 is well short of the predicted +5.8. Three candidate explanations:

1. **Noise.** Unlikely to explain it alone: the three-run mean sits about 2 standard errors below the prediction.
2. **The hidden set violates the model.** If level-1 costs on hidden games have heavier right tails, or are less predictive of later levels than on the public games, cross-level learning is worth less.
3. **Coarse decisions.** The faithful simulation argues against this one.

We report every submission until the deadline, favourable or not.

## 7. Other measured findings

| Finding | Measurement | Outcome |
|---|---|---|
| Serving is at its frontier | 2 speculative steps: −13% tokens/s. 4 steps: refused by the QSA kernel. 12 streams: +7% before steady state, then limited by KV memory | Kept Franzen's serving |
| Online MXFP8, publicly suggested as +15–28% | Frees 35% KV memory but cuts throughput 21–37% and raises tokens per cleared level about 1.5× on this W4A16 checkpoint | Rejected |
| Retained helper functions | Upstream silently dropped all of them on any tool timeout; we fixed it with a regression test | Fix shipped |
| Budget meter: 18% of tokens follow a death, mostly budget-bar deaths | A deterministic border-bar reader estimates remaining actions at 92% of steps (median error 0) on 20 public games | Under leaderboard test (`combo2`) |

## 8. Universality, progress, novelty

**Universality.** Any benchmark that splits one compute budget over many tasks of unknown difficulty (ARC-AGI-2 test-time search, agentic coding suites, proof batches) can reuse the recipe: log tokens and outcomes per attempt, fit a censored model with a task-level effect, allocate by the Bayesian index.

**Progress.** We release the level-attempt dataset, the cost model and simulator, a compute-scaling estimate (one doubling ≈ +20 points; Tufa Labs' lead ≈ 1.9× effective compute), the explanation for why naive reallocation fails, and a measured simulator-to-leaderboard gap so others can calibrate offline gains.

**Novelty.** To our knowledge this is the first survival model of LLM-agent progress on ARC-AGI-3 and the first Bayesian index scheduler for it.

**Limitations.**

- The log-normal form and a single difficulty factor per game.
- A hidden-set difficulty shift calibrated from one statistic.
- Few leaderboard runs, the dominant limitation.

## 9. Reproducibility

Repository: patches, cost-model fit, simulator, diagnostics, figures and the pre-registration **[link]**. Notebook **[link]**, submissions 56808799, 56836105 and 56864114.

**References.** Gittins (1979) *JRSS-B* 41(2); Katehakis & Veinott (1987) *Math. Oper. Res.* 12(2); Weber (1992) *Ann. Appl. Probab.* 2(4); Kaplan & Meier (1958) *JASA* 53(282); Chollet (2019) arXiv:1911.01547; Tufa Labs, Duck harness; Franzen, ARC-AGI-3 Milestone-2 solution.
