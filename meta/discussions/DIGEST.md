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
