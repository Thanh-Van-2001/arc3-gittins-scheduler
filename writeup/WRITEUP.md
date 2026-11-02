# Spend Tokens Where They Pay: What Scheduling, Throughput and Reliability Buy an ARC-AGI-3 Agent

**Subtitle:** A calibrated cost model and Bayesian Gittins scheduler for LLM game agents, measured against a simulator, paired offline runs and 31 leaderboard submissions.

*Nguyen Van Thanh, Loi Dinh Nhat, Le Cong Hoang (Team Talyxion). The agent is Daniel Franzen's Milestone-2 notebook, built on Tufa Labs' Duck harness. The REAP pruning, notebook builder, harness bundle and MTP fine-tuning pipeline we reuse are JustAdev742's (Apache-2.0). Our contributions are the cost model, the scheduler, the reliability fixes and the measurements.*

---

## 1. Summary

Strong ARC-AGI-3 submissions run one loop: a local Qwen3.8-Flash-Next plays 110 hidden games through a Python tool on one RTX PRO 6000 for nine hours. The score is bound by levels cleared, and clearing is bound by generation compute. We asked which game should get the next block of tokens, and then measured everything else that changes how many useful tokens a run produces.

1. **Model.** A censored log-normal model of tokens-to-clear with a latent difficulty per game. On 232 held-out (run, game) pairs it predicts levels cleared with correlation 0.82.
2. **Method.** An exact Bayesian Gittins index for the harness's priority gate: 161 lines, CPU-only, 0.04 ms per decision.
3. **Three measurements of the same scheduler, from easiest to hardest.** The simulator predicts **+5.8 ± 0.4**. Four paired full runs on the public games measure **+3.2 ± 2.5**. On the leaderboard the effect is too small to see.
4. **Throughput and reliability.** These moved the leaderboard mean more than scheduling did. Stacking REAP-448 with 14 streams, a harness bundle, a fine-tuned MTP draft and four reliability fixes raised our mean from 25.5 to 28.8. Our best run scored **35.73** (rank 71 of 5,059).

**Table 1.** Public leaderboard (55 hidden games). Means exclude zero and error runs, which are counted separately.

| Configuration | Valid runs | Mean ± SD | Zero/error runs |
|---|---|---|---|
| Stock Franzen copies (community tally, tantan0327) | 76 | 26.8 ± 3.6 | – |
| + Gittins + retained-function fix (10 streams) | 4 | 25.5 ± 3.1 | 0 |
| … + budget-meter prompt line | 2 | 21.8 ± 3.9 | 0 |
| … + REAP-448, 14 streams, keepalive | 7 | 26.8 ± 1.8 | 1 |
| … + JustAdev742 harness bundle + ARC token map | 6 | 28.3 ± 2.5 | 1 |
| … + fine-tuned MTP draft | 7 | **28.8 ± 3.6** | 1 |

## 2. Why the score is completion-bound

A cleared level scores `min(115, 100·(baseline/actions)²)`. Level *i* weighs *i*, a game is capped at its cleared-weight share, and the best play counts. In 282 cleared levels from 12 public runs the agent beat the human action baseline 71% of the time, and 63% of cleared levels hit the cap. Once agents are this action-efficient, deeper levels decide the score: in a 7-level game the last level is worth 7× the first. Allocation and throughput matter more than efficiency.

## 3. A cost model of agent progress

For each level reached we record the generated tokens and whether the level cleared; uncleared attempts are right-censored:

`log T = μ + β_level + α_run + u_game + ε`, with `u_game ~ N(0, σu²)` and `ε ~ N(0, σ²)`.

Censored maximum likelihood (Gauss–Hermite) on 495 attempts gives σu = 0.77, σ = 0.95, and deeper levels costing 1.7–3.3× level 1. With σu = 0.77, the hardest and easiest games differ about 20× in cost. Deep-level Kaplan–Meier curves match the model only when conditioned on each game's posterior difficulty. The games that reach deep levels are the easy ones, and that is what a scheduler can exploit.

## 4. The Gittins index

Each game is a bandit arm that pays its score weight when a level clears and can be abandoned at any time:

`Q_λ(l,t) = h(l,t)·(R_l + V_λ(l+1,0)) + (1−h(l,t))·V_λ(l,t+q) − λq`, with `V_λ = max(0, Q_λ)`.

Here `h` is the posterior hazard of clearing level `l` in the next 4k tokens, given `t` tokens already spent. The index is the λ at which continuing breaks even (Gittins 1979; Katehakis & Veinott 1987; Weber 1992). The posterior over `u_game` updates on every cleared level and on how long the current level has resisted. Franzen's `(A+B)·C` priority prices level value, continuation and a decaying completion curve, but learns nothing about the individual game. In the simulator, removing the posterior updates drops the index below Franzen's priority, so the gain comes from Bayesian learning.

## 5. Three measurements of one scheduler

**Simulator.** The simulator runs 110 games on 19.4M tokens and hands over slots only at context trims, as the harness does. It predicts +5.8 ± 0.4 over Franzen's gate, and the gain stays positive (+3.2 to +8.4) in all 14 misspecification scenarios we tried. It also explains a public negative result: demoting games stuck at level 0 is worth +0.0 to +0.7, because Franzen's completion factor already stops funding them.

**Paired offline runs.** We ran four pairs under REAP-448 and 14 streams, 25 public games at 121 minutes each, identical except for the gate. Gittins scored 50.20, 45.63, 50.23 and 55.87; Franzen's gate scored 43.62, 52.81, 42.00 and 50.53. The paired per-game difference is **+3.24 ± 2.47**, and Gittins cleared 110.5 levels against 105.3. A Kaggle diagnostic with 25 games, 4 slots and every pricing logged confirmed the mechanism. The gate handed over 105 times, and five games that kept clearing levels received 70% of the tokens.

**Leaderboard.** Per-run noise is SD ≈ 3–3.6. Against that, a 2-point effect needs about twenty runs per arm to detect, and one submission per day did not allow it. Our Gittins arms never trailed stock copies. The leaderboard neither confirms nor refutes the offline +3. We report this as a calibrated **sim-to-real gap**: the simulator's +5.8 shrank to about +3 on real games and is unmeasurable at leaderboard sample sizes.

## 6. Throughput levers

| Lever | Measurement | Outcome |
|---|---|---|
| REAP-448 load-time expert pruning + 14 streams | KV pool 1.01M → 1.48M tokens, peak use 0.94, no OOM; +14% output tokens/s (JustAdev742's same-conditions gate) | Adopted |
| ARC FR-Spec token map | Draft acceptance +1–2% | Adopted |
| MTP draft fine-tuned on our own request logs (72 GPU-minutes) | Held-out acceptance 2.725 → 2.965; served 2.71 → 2.88–2.92, lossless | Adopted |
| Relaxed acceptance 0.5 | Accept 3.35, full run 50.76, no gain over lossless | Rejected |
| Online MXFP8 | −21% to −37% throughput on this W4A16 checkpoint | Rejected |
| Budget-meter line in the prompt | 24.54 and 19.08 vs 25.5 without it | Rejected |

## 7. Reliability: the cheapest points

Three of our 31 submissions returned zero or an error, and community threads report the same failures. Each cause we could identify had a fix of under 30 lines:

1. **15-minute no-move rule.** A run with no game action for 15 minutes ends early. When the 125B model loaded slowly, the single warmup RESET was not enough. Fix: a keepalive thread resets the warmup game every 9 minutes until the server's `/health` answers.
2. **Slow storage.** At peak hours model loads took 36–48 minutes instead of about 8, and every game's first request gave up after 15 minutes. Fix: a 90-minute first-request grace and submissions moved off the 00:00–09:00 UTC rush.
3. **Mounts.** Kaggle-output mounts failed at setup on some days, and model paths varied between mount layouts. Fix: serve the draft from a dataset, use a resolver that searches every layout, and fall back to the stock draft if ours is missing.
4. **Rerun detection.** A scored rerun can miss `KAGGLE_IS_COMPETITION_RERUN` and take the offline branch. Fix: also treat the run as scored when the competition gateway's host resolves.

Once all four fixes were in (from 24 October), 10 submissions produced one error and no zeros.

## 8. Universality, progress, novelty

**Universality.** The recipe applies to any benchmark that splits one compute budget over many tasks of unknown difficulty, such as ARC-AGI-2 test-time search, agentic coding suites and proof batches. Log tokens and outcomes per attempt, fit a censored model with a task-level effect, and allocate by the Bayesian index.

**Progress.** We release the level-attempt dataset, the cost model and simulator, the paired-run protocol, and a three-level measurement (simulator, offline, leaderboard) of the same method, so others can discount offline gains. We also release a reliability checklist that removes most zero-score runs.

**Novelty.** To our knowledge this is the first survival model of LLM-agent progress on ARC-AGI-3, the first Bayesian index scheduler for it, and the first fine-tuned speculative draft for this agent trained from the agent's own traffic.

**Limitations.**

- The log-normal form assumes a single difficulty factor per game.
- The hidden-set shift is calibrated from one statistic.
- With about seven runs per arm, the leaderboard cannot resolve effects under about 3.5 points.
- Most throughput levers and the harness bundle reuse JustAdev742's work. We measured them; we did not invent them.

## 9. Reproducibility

Repository with patches, builders, cost model, simulator, paired-run results (`results/run1–4`), submission log (`results/lb_submissions.csv`) and pre-registration: **github.com/Thanh-Van-2001/arc3-gittins-scheduler**. Notebook: **kaggle.com/code/thnhnguyn2001/arc3-talyxion-combo5** (best run, submission 57838033).

**References.** Gittins (1979) *JRSS-B* 41(2); Katehakis & Veinott (1987) *Math. Oper. Res.* 12(2); Weber (1992) *Ann. Appl. Probab.* 2(4); Kaplan & Meier (1958) *JASA* 53(282); Chollet (2019) arXiv:1911.01547; Lasby et al. (2026) REAP, ICLR, arXiv:2510.13999; tantan0327, arc-agi-3-agent (leaderboard tally); Tufa Labs, Duck harness; Franzen, ARC-AGI-3 Milestone-2 solution; JustAdev742, Arc-Agi-3-Kaggle-comp.
