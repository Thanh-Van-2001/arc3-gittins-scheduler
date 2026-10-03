# Spend Tokens Where They Pay: Bayesian Gittins Scheduling for ARC-AGI-3 Agents

**Subtitle:** A calibrated model of how LLM agents progress through ARC-AGI-3 shows the score is bound by levels cleared, not by actions; allocating the fixed 9-hour budget with a Bayesian Gittins index is worth about 20% more compute.

*Nguyen Van Thanh, Loi Dinh Nhat, Le Cong Hoang (Team Talyxion). Built on Tufa Labs' Duck harness and Daniel Franzen's Milestone-2 solution; all credit for the agent itself is theirs.*

---

## 1. Summary

Every strong ARC-AGI-3 submission now runs the same loop: a local LLM plays 110 hidden games through a Python tool on one RTX PRO 6000 for nine hours. The open question is no longer *how* the agent plays a level but *which* game should get the next thousand tokens. We answer it in four steps:

1. **What limits the score.** In 282 cleared levels from 12 public runs, the agent used fewer actions than the human baseline 71% of the time, and 63% of cleared levels already sit at the per-level score cap. The score is therefore set by how many (and how deep) levels are cleared, and clearing is limited by generation compute.
2. **A cost model.** We fit a censored log-normal model of the generated tokens needed to clear a level, with a latent difficulty shared by all levels of a game. Validated leave-one-run-out, it predicts levels cleared per game with correlation 0.82 (mean absolute error 0.66 levels, n = 232).
3. **An optimal allocation rule.** Treating games as bandit arms with a stopping option gives a Gittins index. We compute it exactly over a Bayesian posterior of each game's difficulty, which updates on every cleared level and on how long the current level has resisted.
4. **Evidence.** In a simulator calibrated to Franzen's public score, the index scores **37.1** against 31.6 for Franzen's heuristic priority, 25.6 for an equal split and 51.3 for a clairvoyant oracle. The gain survives every misspecification we tried. On the leaderboard: **[LB A/B: base X ± s (n), Gittins Y ± s (n)]**.

The change is a 161-line module and a 26-line hook, CPU-only, and runs in 0.04 ms per decision.

## 2. Why the score is completion-bound

The official scorecard gives a cleared level `min(115, 100·(baseline/actions)²)`, weights level *i* by *i*, caps a game at its cleared-weight share, and takes the best of a game's plays. Three consequences follow, and the public runs confirm each of them:

- **Efficiency rarely binds for LLM agents.** The median ratio of human to agent actions on cleared levels is 1.27 (Fig. 2). Agents deliberate in tokens, then act sparingly. Our own LLM-free graph-exploration agent from June showed the opposite regime: 15 of 25 public games cleared, but wandering kept its score at 0.22. The scoring has two regimes, and today's frontier is in the completion regime.
- **Depth is worth more than breadth.** In a 7-level game the last level carries 25% of the game's score and the first carries 3.6%.
- **Replaying is worthless.** A RESET after winning a whole game does open a new play, and the best play counts (`arcengine` 0.9.3). But a near-capped agent gains almost nothing from it: about 7 points on one game in Franzen's demo.

So the agent converts generation tokens into cleared levels, and the scheduler decides where those tokens go.

## 3. A cost model of agent progress

For each level an agent reached, we record the generated tokens it spent there and whether it cleared the level. Unfinished attempts are right-censored, because the run stopped first. The model is

`log T = μ + β_level + α_run + u_game + ε`, with `u_game ~ N(0, σu²)` and `ε ~ N(0, σ²)`.

We fit it by maximum likelihood, integrating `u_game` out by Gauss–Hermite quadrature. The data are 495 attempts on all 25 public games across 12 public runs. The estimates:

- Game difficulty spreads widely: σu = 0.77, so the easiest and hardest public games differ about twentyfold.
- Level-to-level noise is just as large: σ = 0.95.
- Deeper levels cost 1.7–3.3× level 1.
- Franzen's configuration runs at 0.26× the cost of the original June Duck runs, which shows how much better models helped.

One quantity cannot be measured on the public games: how much harder the hidden set is. We calibrate it once, so that Franzen's policy lands in the 28–33 band that his notebook and its unmodified forks score on the leaderboard. This gives a shift of +0.6 in log cost, and we keep it fixed in every comparison below.

## 4. The Gittins index for compute allocation

Games compete for slots in the priority gate. Working on a game is a bandit arm that yields score when a level clears and can be abandoned at any time. For a reward rate λ, in game-score points per token, backward induction gives the value of continuing:

`Q_λ(l,t) = h(l,t)·(R_l + V_λ(l+1,0)) + (1−h(l,t))·V_λ(l,t+q) − λq`, with `V_λ = max(0, Q_λ)`.

Here `h` is the posterior hazard of clearing level `l` within the next `q` = 4k tokens, given `t` tokens already spent, and `R_l` is the level's score weight. A game's index is the λ at which continuing breaks even, that is, the highest reward rate it can sustain. Admitting the game with the highest index is the Gittins rule (Gittins 1979; Katehakis & Veinott 1987; Weber 1992).

Two Bayesian updates drive the decisions:

- **Cross-level learning.** A game whose early levels were cheap is probably easy, so its next level is priced accordingly.
- **Survival learning.** A level that has resisted 150k tokens is evidence of a hard game, and its index decays at the rate the posterior implies, not at a hand-tuned rate.

Franzen's priority `(A+B)·C` already combines level value, continuation value and a decaying completion curve. It learns nothing about the individual game, and that is the gap we close.

## 5. Results in a calibrated simulator

Setup: 110 games with costs drawn from the fitted model, and a budget of 19.4M generated tokens (nine hours at Franzen's measured 609 tokens/s). Every policy sees the same worlds. Fig. 1 and the table below report means over paired seeds.

| Scenario (4–6 seeds each) | Equal | Franzen | **Gittins** | Oracle | Gittins − Franzen |
|---|---|---|---|---|---|
| Matched model | 25.9 | 30.8 | **37.1** | 51.0 | +6.3 (min +4.1) |
| Hidden set easier (shift 0) | 43.6 | 50.6 | **56.8** | 68.9 | +6.3 |
| Hidden set harder (shift 1.2) | 14.1 | 17.8 | **21.9** | 36.5 | +4.2 |
| Heavy-tailed costs (t₃) | 29.2 | 34.4 | **42.8** | 54.2 | +8.4 |
| Game spread ×0.5 | 21.5 | 25.0 | **29.9** | 46.3 | +4.9 |
| Level noise ×1.3 | 23.0 | 27.0 | **30.3** | 47.2 | +3.3 |
| Harness gate: first 40k tokens per game, then switch only at context trims | — | 32.8 | **37.8** | — | +5.1 ± 0.5 |

**Ablation (Fig. 3).** Removing the posterior updates drops the index to 29.0, below Franzen's 31.6. Removing only cross-level learning gives 33.8. The gain therefore comes from learning each game's difficulty, not from the form of the index. Two extensions changed nothing beyond noise (±1 point): an endgame-aware variant, and tables matched to the true hidden-set shift.

**Compute scaling.** Doubling the budget raises the score by about 20 points at today's operating point (Fig. 1). The Gittins index at 1× matches Franzen's priority at roughly 1.2× compute. Read through the same curve, Tufa Labs' 52.5 corresponds to about 1.9× Franzen's effective compute, whether that comes from throughput, token efficiency or a better model.

## 6. Leaderboard validation

Two private notebooks differ only in `ARC3_PRIORITY_POLICY=gittins`: Franzen's notebook unchanged, and the same notebook with our patch. **[Fill in: submission IDs, public scores, run-to-run spread, paired difference.]**

## 7. Universality

Nothing here is specific to ARC-AGI-3. Any benchmark in which one compute budget is split across many independent tasks of unknown difficulty has the same structure. That includes ARC-AGI-2 test-time search, agentic coding suites and theorem-proving batches. The recipe carries over directly:

1. Log the tokens spent and the outcome per attempt.
2. Fit a censored cost model with a task-level random effect.
3. Allocate by the Bayesian Gittins index.

The module depends only on four fitted constants.

## 8. Novelty, limitations, honesty

As far as we know, this is the first calibrated survival model of LLM-agent progress on ARC-AGI-3, and the first Bayesian index scheduler for the competition. The agent, the prompts, the serving stack and the priority gate are Tufa Labs' and Franzen's work, which we reuse unchanged.

Limitations:

- The simulator inherits the log-normal form, although heavy tails did not hurt.
- The hidden-set shift is one calibrated number.
- The public runs mix models and configurations; we absorb this with run effects.
- Real slot handovers happen only at context trims; we simulate this explicitly.

## 9. Reproducibility

Code: patch, cost-model fit, simulator, figures, and the raw level-attempt table extracted from public notebook outputs: **[repo link]**. Notebook: **[link]**, submission **[ID]**.

**References.** Gittins, J. C. (1979). Bandit processes and dynamic allocation indices. *JRSS-B* 41(2):148–164. · Katehakis, M. N. & Veinott, A. F. (1987). The multi-armed bandit problem: decomposition and computation. *Math. Oper. Res.* 12(2):262–268. · Weber, R. (1992). On the Gittins index for multiarmed bandits. *Ann. Appl. Probab.* 2(4). · Kaplan, E. L. & Meier, P. (1958). Nonparametric estimation from incomplete observations. *JASA* 53(282):457–481. · Chollet, F. (2019). On the Measure of Intelligence. arXiv:1911.01547. · Tufa Labs, Duck harness (github.com/Tufalabs/duck-harness). · Franzen, D., ARC-AGI-3 Milestone 2 solution and write-up (github.com/da-fr/arc-agi-3-solution).
