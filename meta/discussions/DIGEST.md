# Kaggle ARC-AGI-3 discussion digest (read 2026-10-04)

Source: competition forum 10403401, fetched via the public web API (`meta/kaggle_discussions.py`);
raw threads saved as `<topic_id>.md`. URLs: https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/<id>

## Evidence relevant to our paper

| Topic | Claim / number | Use |
|---|---|---|
| 745062 (Son Pham) | Hundreds of single submissions of Franzen's notebook copies: **mean 25.77, SD 3.93, median 26.19** | External control distribution for the Franzen arm; validates our noise model (predicted SD 3.6–3.8) |
| 744792 (Tong Hui Kang) | Side-by-side of the three M2 winners: Franzen 27.89 (10 streams, 128k ctx, KV pool 1.01M), Lord Han Solo 23.84 (vLLM, 14 streams, KV pool 1.42M), Lohit Siriki 22.53 (16 streams, 69k ctx, 48 GB host KV tier) | Context vs concurrency trade-off; KV capacity is the binding resource |
| 744792 (rellik13 = Lohit Siriki) | Spending freed memory on longer history (trims 37k→27k ⇒ 57k→45k) took his score **14.5 → 22.5** | Long context matters; do not trade it for streams |
| 744792 (xz) | NVFP4 KV cache: "very little NLL penalty", half the memory of FP8 | Possible route to 12–14 streams at full context |
| 744792 (Son Pham) | REAP expert-pruned Qwen3.8 for higher TPS: "an entire untapped area" | Throughput lever (unvalidated) |
| 743723 (Sergei Makarov) | Controlled single-layer experiments: almost every harness layer ≤ baseline; failures are early goal misjudgement (83% of forks had already tried the decisive action type); identical builds spread 4.5–9.4 on public games | Harness changes are low-value; noise is large |
| 742801 (Scott Le Grand) | Tried dropping L0 games to give L1+/L2+ more time: "no dice" (best-of-3 evaluation) | Counter-evidence for heuristic reallocation — our A/B must check |
| 739938 (Fususu) | "Adaptive compute allocation looks more promising than a fixed action budget"; shadow-mode allocator: ~13.6% counterfactual action savings | Supports allocation as a lever |
| 734369 (Jakob Brüggen) | "Tokens are the real currency, not actions"; every run hits the wall-clock cap | Supports completion/compute-bound regime |
| 739047 (manas joshi) | STaR LoRA on own winning trajectories: LB 1.25 → 1.94 (Qwen3.6-27B era); finicky, model-specific | Training lever; infeasible for us on Flash-Next now |
| 732854 | Public-game scores correlate poorly (even negatively) with LB | Don't tune on the 25 public games |
| 742801 (Jeroen Cottaar, Tufa) | Tufa will not open-source until the end; CPMP (NVIDIA) likewise | Top approaches unavailable before deadline |
| 744995 | Some runs end after 2–4 h (infra outage) | Watch for truncated submissions |

## Second pass (all 155 topics, 1,020 messages; read 2026-10-04)

| Source | Claim | Use |
|---|---|---|
| JustAdev742 notes (GitHub) + forum | Tufa forked an RL post-training stack (slime/miles/verl + Megatron) on Sep 3–9; evaluates on B200 SLURM (20 passes × 25 games); team bios = RL/self-play; Tufa paper on on-policy self-distillation from world feedback | Top-1 gap most likely from post-training, not harness |
| JustAdev742 notes | Yi-Chia Chen (LB 48) previously shipped own SGLang build, self-trained DFlash drafter (8 draft tokens), on-policy-distilled W4A16 model on the same GPU; "complexity of the process" | Top-2 gap: trained drafter/model + inference engineering |
| jeroencottaar 687655 (Apr) | `baseline_actions` were visible for the 110 test games during submission | TAAF later treats them as hidden; would give a difficulty prior (our corr 0.42) — not relied on |
| jeroencottaar 743952 | Hidden-set (private) numbers usually revealed for all submissions at the end | Final evidence for the paper |
| sirikilohit 744792 | Helpful harness changes were "not misleading the agent": UNDO instead of ACTION7, "level restarted" instead of "game over", removing lines telling it to ignore the budget bar | Already in Franzen's prompts |
| rakbidb 739938 | Run-to-run variance plausibly from continuous batching: one different token diverges the trajectory | Explains SD ≈ 3.9 |
| viktorkorsun 738766 | Explore → level reset → perfect replay still pays for exploration actions | Consistent with our scorer reading (only post-WIN reset opens a new play) |
| asanashirov 739801 | Image upscale 4× (Tufa) vs 8–10× (forks/Franzen): untested contradiction; identical configs spread 2.85 vs 4.75 | Keep Franzen's 10× |
| chewkokwahibrainai 742148 | RTX PRO 6000 queue worst 02:00–09:00 UTC | Schedule commits outside that window |
