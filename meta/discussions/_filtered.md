## [732854] What are your agents scoring on the 25 public games? — ataraxian 2026-09-16
started:   2026-09-14 23:08:10
ended:     2026-09-15 01:21:58
duration:  2h 13m 48s
mean score:    9.91
median score:  4.76

then LB 6.23, I don't know if it's sheer luck.

The notebook is based on the public flash-next one, but I did make significant changes to the harness structure. The original runs from 6 to 12 on the local 25 set, while my modified version runs from around from 9 to 14 (can't afford too many seeds). I've also noticed that the original runs from 1.96 to 4.33 on the public LB (see  but my version has been running  a stable 4.0+ for a while.

Hope this helps everyone understand the variance better, or worse, I have no idea. I don't think this aligns well with the local-lb consistency pattern of the others.



## [732854] What are your agents scoring on the 25 public games? — nicholaspellegrin 2026-09-18
Recently:
Public 7.6%   (solving 35 levels total) -> 3.35% Private LB,
Public 10.2% (solving 44 levels total) -> 3.05% Private LB,
Public 7.7%   (solving 37 levels total) -> 4.42% Private LB

It almost feels like doing better on the public set (even without any game-specific stuff) correlates to weaker private scores.

Also all those above scores were different harness variations. It feels almost impossible to experiment because you need to submit at least like 5 times to get a good feel for how a notebook version scores (to account for the variation), but with only 1 submission a day the progress is so slow.

## [735243] Qwen 3.8 release — scottlegrand 2026-08-17
The most I ever saw locally before 3.8 was 5 level 3s reached in 130 minutes and a couple miracles that made it to level 5 (crazy outlier single run top local RHAE 3.6 or so, but rarely over 2, LB 1.5). 3.8 has taken things to 3.8 locally, regularly >2, and 50% >3. And yep, they have absolutely cracked 3.8 secret sauce here. I went from 40 to 102 in the past few hours.

## [735590] ARC-AGI-3 run went backwards on the leaderboard. What are we missing? — pengyipeng1 2026-08-17
Hi everyone 👋

Small team here with 3 submissions so far, and we need a reality check. Our journey:

| Date   | Submission                                | Public score |
|--------|-------------------------------------------|--------------|
| 08-12  | naive graph-explorer MVP                  | 0.25         |
| 08-15  | PAGI-001 (offline eval +121% vs baseline)  | 0.74         |
| 08-16  | PAGI-002 (offline eval +21.6% over 001)    | 0.28 😭      |

Yes — our most "improved" submission scored the *worst* of the three publicly.
Our frozen offline validation keeps going up, and the public leaderboard keeps
laughing at us. We're sitting around rank #744 / 2362 while the leader is at
2.70, so there is clearly a huge amount we don't understand yet.

We would genuinely love your advice on:

1. **Local vs public gap**: how do you make offline evaluation actually predict
   the public score? (more seeds? per-environment reporting? agent variance?)
2. **Where the points live** at this level: exploration breadth, action
   efficiency, memory / state tracking, or planning quality? What gave you the
   single biggest jump?
3. **One strong agent or a family?** We see top teams iterating with dozens of
   submissions — do you polish one agent, or run a portfolio?
4. What is the most common trap you see teams fall into around the 0.3-0.8
   range?

Feel free to roast us — we clearly deserve it 😅. Any suggestion is welcome;
we'll read everything. Thank you in advance to everyone who shares, and good
luck to all! 🍀

## [735590] ARC-AGI-3 run went backwards on the leaderboard. What are we missing? — chiakazirim 2026-08-17
If your local test runs are using the game's source code to make a deepcopy for offline explorations, I don't think the source code is available for the test set used for the public leaderboard scoring.

If that's the case, your agent will make very random explorations and waste real actions during live play before eventually solving a level, and that would give zero scores for most levels completed.

## [738599] GPT-OSS-120B works on the RTX Pro 6000 — offline vLLM 0.19 config + a  — rngrng 2026-09-01
Ran openai/gpt-oss-120b end-to-end as an agent analyzer on the competition GPU today. Sharing the config that works and one vLLM bug you will hit, since most public setups here are Qwen-centric.

## Attachments (all public)

- **Model**: `danielhanchen/gpt-oss-120b` Kaggle Model (Transformers layout, MXFP4, 15 safetensors). Weights load at **65.96 GiB** — fits the RTX Pro 6000 with room for KV cache.
- **Wheelhouse**: `driessmit1/arc3-vllm-h100-wheelhouse-v3` (vllm 0.19.0 + torch 2.10.0 + flashinfer 0.6.6 — from Tufa Labs' open-sourced milestone release; the versions are known-good together, don't mix wheel sets).
- **Tiktoken encodings**: notebook output `philipvonderlind/vllm-deps`. gpt-oss is a harmony model and `openai-harmony` tries to *download* its tiktoken encodings at import — offline you must attach them and set:

```
TIKTOKEN_ENCODINGS_BASE=/kaggle/input/vllm-deps/tiktoken_encodings   # o200k_base + cl100k_base
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
```

## Serve flags — the diffs vs. a Qwen setup

```
--tool-call-parser openai        # reads tool calls from the harmony commentary channel
--kv-cache-dtype fp8             # keeps 64k context in budget
--max-model-len 65536
--enable-prefix-caching
```

Two things to *remove* from a Qwen config:

- **No `--reasoning-parser`.** gpt-oss goes through vLLM's native harmony path (`openai_gptoss` is engaged automatically). Pointing `qwen3` at it fails — the vocab has no `<think>` token.
- **No `--default-chat-template-kwargs '{"preserve_thinking": true}'`** — harmony handles reasoning channels itself. Also note vLLM prints: *"For gpt-oss, we ignore --enable-auto-tool-choice and always enable tool use."*

Healthy numbers for reference: model load ~74 s, KV cache 15.86 GiB = **462k tokens** at fp8, sustained **~830 tok/s** generation with 25 concurrent requests, ~90% prefix-cache hit rate in an agent loop.

## The bug: 8.1% of requests 500

vLLM 0.19.0's harmony output parser (`vllm/entrypoints/openai/parser/harmony_utils.py`, `parse_output_into_messages`) has **no error handling**. gpt-oss occasionally emits a malformed harmony continuation — an `<|end|>` not followed by `<|start|>`, or a hallucinated `<|start|>functions.python` tool-result turn — and `StreamableParser` raises `HarmonyError` straight out of the request handler. The client gets a 500 and your agent loses the whole turn. Measured **91 of 1,127 requests (8.1%)** on a 25-game run.

Since the wheelhouse installs into a writable `--target` dir

## [738600] Offline vLLM on Kaggle: the wheelhouse pattern, mount-path gotchas, an — rngrng 2026-09-01
Competition kernels run with no internet, and a working local-LLM setup is table stakes here. This is the checklist I wish I'd had — everything below was learned by burning GPU hours.

## 1. The wheelhouse pattern

`pip install vllm` is dead offline. Attach a dataset full of wheels plus a lock file, and install with the resolver fenced off the network:

```bash
python -m pip install \
  --no-index --find-links /kaggle/input/<your-wheelhouse> \
  --requirement /kaggle/input/<your-wheelhouse>/requirements.lock \
  --target /kaggle/working/vllm-site-packages \
  --only-binary :all: --no-compile --ignore-installed --no-warn-conflicts
```

Details that matter:

- `--target` into `/kaggle/working` keeps the base environment untouched (the harness and its deps keep working). Export `PYTHONPATH=/kaggle/working/vllm-site-packages` to every child process that needs vLLM.
- `--only-binary :all:` means a missing wheel fails in seconds instead of attempting a source build that dies after minutes.
- **Pin a known-good trio and don't mix wheel sets.** `vllm==0.19.0 + torch==2.10.0 + flashinfer==0.6.6` work together (that's the combination in the public `driessmit1/arc3-vllm-h100-wheelhouse-v3`, from Tufa Labs' open-sourced milestone setup). I tried combining wheels from two different public wheelhouses and got resolver conflicts — versions across wheelhouses are not interchangeable.
- Write a **stamp file** after a successful install (contents = the pinned versions) and check it plus a `python -c "import vllm, torch"` before reinstalling. In interactive sessions this turns every restart from a several-minute reinstall into a no-op.

## 2. Mount paths are not where you think

The same attachment can appear at different paths depending on how it was attached and when the kernel was created. Resolve all candidates instead of hardcoding one:

- Datasets: `/kaggle/input/<slug>` **or** `/kaggle/input/datasets/<owner>/<slug>`
- Notebook outputs: `/kaggle/input/<slug>` **or** `/kaggle/usr/lib/notebooks/<owner>/<slug>`
- Kaggle Models: `/kaggle/input/models/<owner>/<slug>/<framework>/<variation>/<version>`

Print an audit of what actually mounted as your first cell. A missing attachment found at second 5 costs nothing; found after the model loaded, it costs half an hour.

## 3. Verify the model attachment before installing anything

A Kaggle Model can attach partially or in an unexpected layout. Check the cheap invariants first — `config.json`, `tokenizer.json`, the safetensors i

## [738602] Fail fast or lose hours: guard cells that protect your GPU quota — rngrng 2026-09-01
With weekly GPU quota and long agent runs, the expensive failure isn't the crash — it's the crash that happens **late**. A run that dies at minute 3 costs nothing; the same root cause surfacing at minute 90 costs a real slice of your week. Everything below is a guard that moved a failure from "late and opaque" to "immediate and named", from runs on this competition.

## 1. Assert the GPU you think you have

Kaggle once provisioned a Tesla P100 for a notebook configured for the RTX Pro 6000. The visible symptom was an unrelated-looking subprocess failure minutes later. Worse outcomes exist: on a smaller GPU a big model can get through minutes of loading before OOM. First cell:

```python
import subprocess
names = subprocess.run(
    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
    capture_output=True, text=True).stdout.split("\n")
names = [n.strip() for n in names if n.strip()]
assert names and all("rtx pro 6000" in n.lower() for n in names), f"wrong GPU: {names}"
```

Adjust the expected substring per accelerator choice. Seconds to fail, and the error names the actual problem.

## 2. Audit every attachment before any expensive step

Attachments mount at different paths depending on type and how they were attached (`/kaggle/input/<slug>` vs `/kaggle/input/datasets/<owner>/<slug>`, models under `/kaggle/input/models/.../<version>`). Print what actually mounted, then assert the cheap invariants of each input: the wheelhouse's lock file exists, the model dir has `config.json` + `tokenizer.json` + the exact expected safetensors shard count. A partially-attached model that passes a naive `path.exists()` check will happily waste a full install-and-load cycle before failing.

## 3. Smoke-test the model server before the agent touches it

After starting vLLM: poll `/v1/models` with a hard timeout, and on timeout print the **tail of the server log** in the exception — the alternative is a run that "hangs" with the actual error buried in a file nobody looks at. Then one tiny completion request. Wrong parser/template flags produce a server that comes up healthy and fails on first use; catch that in a 5-second request, not inside the run.

## 4. Leave before the wall clock throws you out

If the kernel hits the hard runtime limit, it is killed and you lose the outputs — scorecards, transcripts, everything you'd use to debug. Compute a soft deadline at start (`hard_limit - buffer`, I use 10 minutes) and have the loop exit cleanly when it's reached. A par

## [738766] Is the exploration phase burning score? — viktorkorsun 2026-09-01
TDLR: is it possible to score 100% in this scenario:
1. exploration, a few unsuccessful attempts
2. game reset
3. perfect completion

Backgrouind: on the 24'th of August my submission that explores the game until a working hypothesis is built, then resets the game, and then uses that hypothesis to solve the level optimally - scored 0.25.

A resubmission of a byte-to-byte identical solution scored only 0.09 on August 26'th. I have a hypothesis that the scorer was changed to count the exploration phase, and a game reset does not reset the scorer, so that all previous steps are counted against the new attempt.

Am I tripping?

## [739047] Open-sourcing winning-trajectory datasets + a LoRA for the duck harnes — justforgags 2026-09-02
Hey all — sharing some artifacts that might help others fine-tune agents on ARC-AGI-3.

We ran the open duck harness (TAAF, MIT) with Qwen3.6-27B, kept only the games the agent won (reached a level), and LoRA-SFT'd on those winning trajectories (STaR / reject-sampling). Behavior-cloning the agent's own successes gave us a real, measurable lift on the leaderboard.

Three CC0 datasets:
- [arc3-sft-trajectories]( — full level-completing trajectories in chat-JSONL (system → reasoning → Python tool-calls → results). Drop-in SFT data.
- [arc3-duck-lora-sft]( — the pilot LoRA adapter (Qwen3.6, qwen3_5).
- [duck-eval-results]( — per-game offline benchmark logs.

A few gotchas that might save you time:
- Train assistant-tokens-only; the tool-calls are OpenAI-format, flatten before templating.
- It's a multimodal arch — merge/serve as Qwen3_5ForConditionalGeneration (a text-only save gets rejected by vLLM), and copy the processor configs into the merged checkpoint.
- Offline levels don't predict the leaderboard — only submit to measure.

Hope it helps someone climb. Happy to answer questions. 🦆

## [739047] Open-sourcing winning-trajectory datasets + a LoRA for the duck harnes — justforgags 2026-09-03
A useful distinction here is what you fine-tune on.

Chollet's caution is about the demonstration set as data — training a model to solve those 25 specific games. That absolutely overfits: the private eval is different and harder, so memorizing the demo games buys you nothing there.

But "LoRA" isn't one thing. What gave us a modest lift wasn't training on game solutions — it was behavior-cloning the harness's own winning trajectories (STaR / rejection sampling): keep only the runs where the agent actually cleared levels, and SFT on the process — how it wrote probes, used the segmentation, structured its reasoning and tool calls. You're teaching agentic skill, not the answer key.

Why we half-trust it: the gain showed up on the leaderboard (semi-private) score, not on the local demo games — base model vs. the same model with a trajectory-LoRA, same harness. So at least in our case it wasn't demo-set overfitting.

Big caveats, and they line up with your experience:

1. High variance — same recipe, different runs, scores swung a lot. Very easy to read noise as signal.
2. Naively scaling the data hurt — more trajectories at the same recipe made it worse. Curation > quantity.
3. Base-model-specific — an adapter that helps one model won't necessarily help a different/stronger one, so as the meta shifts to new bases, old adapters can stop paying off entirely.

So: training on demo solutions → yes, backfires. Behavior-cloning winning process → can help, but it's finicky, model-specific, and only the private/semi-private score can confirm it's real.

## [739047] Open-sourcing winning-trajectory datasets + a LoRA for the duck harnes — justforgags 2026-09-03
Hi Nick, yes it was a big jump went from 1.25 to 1.94 fine tuning on qwen. At that time it took me from 300~ rank to 133~ . Now the leaderboard is already 7~ lol.

## [739801] MULTIMODAL_UPSCALE: the writeup says 4 is best, the popular forks all  — asanashirov 2026-09-06
Two published claims about the same knob point in opposite directions, and I
can't find anyone who has tested it. Posting my measurements in case they help,
and because I'd rather not burn a 9h submission finding out what someone already
knows.

## The contradiction

The Duck harness writeup ([discussion 717133](
says the authors tuned this and settled on 4x:

> a 4x upscaled image of the board is injected into its context at the beginning
> of every turn ... we found that this upscaling gives the model the best visual
> understanding of the scene

Meanwhile the widely-forked Qwen3.8 submission notebooks run `MULTIMODAL_UPSCALE
= 8`, and the change from 4 to 8 is documented there as the arm that moved the
score. I inherited 8 without questioning it.

Both can be true — the writeup tuned against Qwen 3.6, the forks run 3.8, and a
different vision encoder could prefer a different scale. But I can't find a
single posted A/B, and it isn't a cheap thing to test: more visual tokens per
frame means fewer actions inside the same per-game cap, so it trades perception
against depth rather than being a free win.

**Has anyone run 4 against 8 on the same model?** Even a rough public-set
comparison would be useful, with the caveat below.

## Why I'm asking instead of measuring

Because I no longer trust the instrument, and I'd rather say so than let someone
else repeat the detour.

I ran the same notebook twice over the 25 public games in a single job (50 runs,
two waves, 4h25m):

| | mean score over the 25 games |
|---|---|
| pass 0 | 2.85 |
| pass 1 | 4.75 |

**A spread of 1.90 on identical configuration.** Every prompt-level arm I have
tried moves the public score by well under a point, so all of my arm rankings
were inside the noise and none of them meant anything. The authors report the
same thing from their side — 1.6002 +/- 0.4475 over 25 games x 20 tries — and
Jeroen has said the leaderboard itself ranges 0.7 to 1.3 on unmodified reruns.

Two consequences I'd suggest to anyone else optimising here:

- **Cross-team comparison on the public set doesn't work.** My runs land at 3.48
  and 4.57; the public figures I can read out of other teams' kernel outputs are
  3.77 and 3.79. Those cannot order us, even where the leaderboard separates the
  same notebooks by 3x.
- **A single submission is evidence, not proof.** At ~9h per rerun against a 30h
  weekly quota, that's a brutal exchange rate, and it's why I'd rather ask.

(One useful side effect: pass 1 scoring *high

## [739938] What Have You Tried So Far? — phuongncn 2026-09-07
Let's share some short but useful experiences—what worked, what didn't, and what we learned along the way. Hopefully, we can learn from each other, avoid repeating the same mistakes, and save some valuable time.

Of course, I understand that this is a competition, and everyone has the right to keep their own edge or secret sauce. But personally, I see this as a learning journey: **the more you give, the more you get back. Winning is just a consequence.** ^^

For example, look at **Team Tufa**. They shared an excellent solution during the Progress round, then got overtaken by quite a large margin afterward—and now they're back at the top of the leaderboard!

So, here's what I've tried and failed at so far. **What about you?**

### 1. Gemma 4 31B

It seems to be better than Qwen 3.6 27B at image recognition and understanding visual content, but it falls far behind when it comes to logic and coding.

### 2. Using a system decoder to simplify everything happening in the game

For example, automatically identifying objects, figuring out which objects can move, etc.

This makes it possible for smaller models like GPT-OSS 120B/20B to understand and play the game. However, they tend to fail by taking overly roundabout approaches, and the decoder can also introduce strong game-specific biases.

### 3. Splitting the LLM into different roles

I tried assigning different roles to different LLM calls:

* Observer
* Theory Generator
* Action Taker
* Advisor

They can critique and challenge each other, and the overall reasoning quality seems to improve. However, the downside is obvious: **5× the LLM calls and a lot more tokens burned.** 😅

### 4. Trying different model configurations

I experimented with different Qwen distilled models, Qwen Thinking Cap, and turning thinking on/off.

The results didn't change that much.

With thinking **off**, the model is much faster but tends to be careless. With thinking **on**, the code quality is better, but it becomes significantly slower.

### 5. Experimenting with different concurrency levels

I tried 8, 16, 24, etc.

It seems that going beyond **16 concurrent requests** hits a saturation point. Increasing concurrency doesn't really make things faster and sometimes even makes the overall system slower.

My guess is that the KV cache becomes heavy, while prefill and decode start interfering with each other.

### 6. Playing all the games myself and creating training data

I tried playing all the games manually (and won all 100%, o

## [739938] What Have You Tried So Far? — rakbidb 2026-09-08
Hi @phuongncn, thanks for sharing this! Many of your findings are surprisingly consistent with my experiments.

I started from a relatively simple Duck + Qwen setup with a public LB around 1.65. One of the more reproducible submissions later reached 2.86 (now its 3.48 after around 3x resubmit, not reproducible as I thought, I guess😅). Here are the main things I tried and learned.

### 1. Reproducible serving mattered more than expected

Before changing the agent logic, I worked on making the inference stack deterministic and auditable:

- exact model and runtime profile;
- pinned serving configuration;
- MTP and concurrency configuration;
- startup validation;
- real tool-call preflight;
- fail-closed behavior when the wrong model or parser is loaded.

This produced a more reliable improvement than several complicated prompting experiments. A sophisticated agent is difficult to evaluate when serving behavior changes between runs.

### 2. Unconditional recovery usually made things worse

My earlier recovery agents were too eager to intervene. They often:

- retried actions that had already failed;
- changed hypotheses too frequently;
- entered long loops;
- consumed many tokens without producing level progress.

More recovery was not automatically better recovery.

What worked better was single-step verified recovery:

1. propose only one recovery action;
2. execute it;
3. observe the actual state transition;
4. continue only when there is evidence that the action helped;
5. otherwise apply a cooldown and return control to the normal policy.

I later added route gating so recovery is triggered by observable symptoms such as repeated no-op transitions, persistent stagnation, or a failed action pattern—not merely because the model says it is uncertain.

### 3. Memory helped only when it stored verified facts

Free-form summaries can preserve an incorrect theory for a very long time.

I changed the memory system to prefer verified transition facts such as:

- action X changed object Y;
- action X was a no-op in state Z;
- progress occurred after a particular interaction;
- a hypothesis was contradicted by the next observation.

Memory is scoped by game/level and can be invalidated. I use retrieved strategies as hypotheses, not instructions.

This reduced some repeated mistakes, although memory contamination is still a real risk.

### 4. Multi-role reasoning was useful only when gated

I also experimented with separating planning, verification, recovery, and ac

## [739938] What Have You Tried So Far? — phuongncn 2026-09-08
Thanks for sharing so enthusiastically and for all the great ideas! Regarding your questions:

1. I tried playing the perfect-win games, recording every step, and then training a kind of reward model to encourage the agent to follow the right approach in each situation. However, it ended up learning by imitation and could only play that specific game.

2. For the different roles, to save tokens I only pass the information that each role actually needs. For example, one role receives the image, while another has access to the history of previous steps. At one point, I had a 5-role flow that managed to win a few public games using reasoning only (no coding agent like Tufa), one step at a time. But it couldn't run on Kaggle because it made too many LLM calls and ran out of the time budget :))

Right now, I'm focusing on optimizing the time spent on LLM calls. Token is money, and it seems that using fewer tokens per step is actually more effective.

And you're absolutely right that it's very difficult to reproduce the Tufa-family notebooks because they run games in parallel, while the noise is almost random. I'm also looking for ways to reduce that randomness. Do you have any ideas on how we could tackle this?

## [739938] What Have You Tried So Far? — rakbidb 2026-09-08
Yeah, I’ve been thinking about this too. My current suspicion is that a lot of the variance may come from request scheduling + continuous batching, not just sampling.

When games run in parallel, tiny timing differences can change which requests are batched together. In an interactive setting like ARC-AGI-3, even one slightly different token/action can change the next observation, and then the entire trajectory can diverge.

A few things I want to test:

1. Per-request deterministic seeds.
   Derive the seed from something like "(base_seed, game_id, level_id, step_id)" so concurrency does not change RNG consumption order.

2. Replay the exact same prompts at different concurrency levels.
   For example: "1, 4, 8, 16".
   If concurrency=1 is stable but higher concurrency starts diverging, that would strongly suggest the randomness is coming from the serving/batching layer.

3. Fixed or synchronized micro-batches.
   Instead of fully asynchronous execution, maybe process small groups of games in a stable order. It could be a useful trade-off between throughput and reproducibility.

4. Ablate MTP / speculative decoding.
   Just to isolate whether they contribute additional variance.

5. Measure variance, not only mean score.
   I’m starting to think the practical objective should be closer to:

$$
E[\text{score}] - \lambda \cdot \mathrm{Std}[\text{score}
]$$

because a slightly weaker but stable agent may be better than one that occasionally scores high but is very noisy.

So my working hypothesis is:

Parallelism may not be only an engineering optimization here. It can effectively change the policy trajectory.

I’ll probably start with the exact-prompt replay × concurrency experiment first. If identical prompts only diverge when batching changes, that would give us a much clearer direction for reducing the randomness.

Would be interesting to compare results if you try something similar 😅

## [742148] Long Queue for RTX Pro 6000 (8 hours) partially due to abusive used fo — chewkokwahibrainai 2026-09-20
The Long Queue for RTX Pro 6000 usage has been getting serious day by day especially between 2 am UTC to 9 am UTC. Beside legitimate usage, the problem is partly made serious by abusive used of RTX Pro 6000 GPU for non ARC AGI-3 tasks.

I propose 2 methods below to mitigate the problems: @herbison 

1. Decrease the number of allowed concurrent GPU usage for RTX Pro 6000 from 2 to 1 per user. This will limit the abusive usage for Training of non ARC-AGI-3 tasks while free up resources for iteration. (At least 50% can be free up)

2. Make a clear warning pop-up when user chose RTX Pro 6000 as the GPU, currently there is no warning, some novice user might not read the rules and use it ignorantly for non ARC-AGI-3 tasks.

Other participants can also propose better way to mitigate if you had any ideas.

Some example of abuse:  
  
       
       


## [742477] About ACTION 7. — hvanphucs112 2026-09-22
What exactly is ACTION7?

The ARC-AGI-3 overview describes it as UNDO, but most agents forked from Duck seem to encounter an index error when they query or try to use this action.

Should we actually keep ACTION7 enabled and treat it as UNDO, or would it be safer to remove/disable it? Is there any evidence that ACTION7 has another role or behavior beyond simply undoing the previous action?

## [742788] Can a New Model Reach the Top? — sonphamorg 2026-09-23
I tried it, the token efficiency just was that great for Deep Seek Flash

To fit it in RTX 6000 PRO, you have to do a lot of shenanigans like quantization and pruning of experts, and by theh end of it, the token efficiency just wasn't equal to Flash Next.

But I would not be surprised if top teams figured out that there are better models that can make this token speed / reasoning quality trade off though

## [742801] We will not be open-sourcing for the second milestone prize — huikang 2026-09-23
Thanks for sharing your intention early!

I also want to ask regarding the [rules](

> Notebooks must be made public under an open source license by the corresponding milestone dates to qualify for these prizes.

Based on precedent (Milestone 1), it seems that

- Top teams will publish their notebook (together with all the dependencies needed to run the notebook) one or two hours before the deadline
- Other teams that simply clone and submit the notebook will not be able to get the full score within the one or two hours
- The ranking priority is based on the snapshot at the deadline (submissions that are in progress will not be considered)
- If a fine-tuned model is used, the model has to be published before the deadline (because it is part of the dependency to the notebook)

There is something I want to clarify

- If you fine-tune a model, to be considered for the milestone prize, do you need to publish (1) the dataset and (2) the fine-tuning script?

## [742801] We will not be open-sourcing for the second milestone prize — scottlegrand 2026-09-28
I tried a bunch of ways to drop L0 games to give L1+ and L2+ games more time and I thought it would be quite a lever myself, but no dice for me at least. But you're right that solving more higher levels is a win. But it's also a lottery as to whether the method does as well on the validation hidden vs the hidden hidden given the huge variance of independent attempts with the same approach.

My one attempt at fine-tuning with a LORA got me +2 on the public games, but it was a paltry effort compared to what someone could do with a DGX with 8 GPUs. Also, that was right around the time flash-nvfp4 was released and that's too big for that approach on my RTX 6000.

## [742835] Finetuning a model (SFT or RL) on the RTX 6000 Pro? — nicholaspellegrin 2026-09-23
I've been toying with the idea of finetuning a model (either through SFT or some form of RL), but I haven't decided on a recipe yet. Part of the reason I've been holding off on trying this is because I'm not sure how realistic it is to fine tune Qwen 3.8 Next Flash NVFP4 on an RTX 6000 Pro.

I know that the RTX Pro is more than capable of finetuning Qwen 3.8 27B, but the gap in capability between 27B and flash next is quite large in my experiments (And I don't want to spend too much time finetuning 27B just for it to reach parity with base flash-next).

Has anyone had success training Flash-Next on their RTX 6000 Pro, or is the only option if I want to pursue finetuning to switch back to a smaller model and hope I can push it past the base performance of flash-next? Or if teams have found success training Qwen Flash Next, did you need to rent out more compute from somewhere else, and would that have an impact on the eligibility on winning the competition (if the hosts find excessive external compute not being "fair" to other participants)?

Any advice would be appreciated, and I don't expect anyone to share their "secret sauce" training recipe, especially so close to Milestone #2 and competition end.

## [743060] P3.1: Perception-Augmented Duck — What Prompt Engineering Can and Cann — gedouluhui 2026-09-24
**Milestone #2 technical write-up · September 2026**
**Authors:** gedouluhui (Kaggle)
**Base harness:** [The Duck]( by Tufa Labs (Milestone #1 winner), used unmodified except where stated
**Model:** Qwen3.8-27B FP8 (Kaggle Models mirror: `foysalemonshanto/qwen3-8-27b-fp8-repacked-v1`)
**Hidden-set score:** **1.43** (single-play competition evaluation)

---

## 1. What this is

The Duck harness (Tufa Labs) won Milestone #1 and was open-sourced with an invitation: "The harness can still benefit from many improvements, especially in context management and perception. With this, we are inviting the community to improve on our work."

We took that invitation literally. This submission keeps the Duck harness architecture intact — REPL coding agent, ephemeral `python` tool, image + text grid perception, automatic context eviction — and changes exactly four things, each validated or rejected by a controlled experiment on the 25 public games:

| Change | Verdict | Evidence |
|---|---|---|
| Model: Qwen3.6-27B FP8 → **Qwen3.8-27B FP8** | kept | hidden 1.12 (P1) with zero other changes |
| **Perception hints** (deterministic connected-component click candidates) | kept | public EV 2.81 (P2.1) |
| **Prompt patch**: true scoring formula + remaining-time budget line | kept | hidden 1.43 (P3.1), +28% over P1 |
| Context 32k → 64k + output cap | **rejected** | 1.20 — throughput collapse (§5.1) |
| Temperature 0.6 → 0.3 | **rejected** | 0.95 — exploration collapse (§5.2) |
| Archetype playbook in system prompt | **rejected** | 1.54 — below pre-registered line (§5.3) |

Everything below documents the measurements, including the failures. We believe the negative results are the most useful part for the community.

## 2. The scoring rule, reverse-engineered (transfers to every competitor)

The competition page does not publish the exact scoring formula. We reconstructed it from the harness source (`tufa-arc-agi-framework`) and confirmed it against per-level telemetry across four full runs:

- **Level score** = `min(115, (baseline_actions / your_actions)² × 100)`. Every action — ACTION1–7 and in-level RESET — costs +1. A solution twice as long as the human baseline scores ~4× less; brute force asymptotes to zero.
- **Game score** = `Σ (level_index × level_score) / Σ (level_index)` over all levels, i.e. later levels are worth more, and an unfinished game caps out at the completed fraction. For a 6-level game, level 1 alone is worth at most 100/21 ≈ 4.76; for a 9-level game, 100

## [743319] Partial-reasoning supervision made our agent stop acting: "no tool cal — wkdrbwnd1 2026-09-25
We fine-tuned a small adapter on our own agent trajectories so the model would keep its tool-use habits with a shorter system prompt. We tried a few ways of deciding which assistant tokens get loss, and one of them failed in a way we did not expect. Sharing in case it saves someone a run.

**Setup (kept general)**
- Training data: 31 agent trajectories from 20 public games (thinking + python tool calls).
- Evaluation: 5 public games that were NOT in the training data (lp85, r11l, sc25, sp80, su15), all run in parallel. Same harness and prompt for every variant. 1 run per config.
- Two supervision recipes compared here:
  - **weighted**: tool-call tokens at weight 1.0, every reasoning token at 0.3.
  - **labeled**: we read the reasoning and labeled each sentence as (a) about using the tool interface, (b) generic problem-solving method, or (c) game-specific commentary, with weights 1.0 / 0.3 / 0.1. Tool calls stay at 1.0. The idea was to keep the "how to use the tools" signal and drop game-specific memorization. In practice about 92% of reasoning tokens were game-specific, so most of the reasoning ended up at 0.1.

**Results, 7-hour budget per game**

| | lp85 | r11l | sc25 | sp80 | su15 | avg |
|---|---|---|---|---|---|---|
| weighted | 82.1 | 27.0 | 5.6 | 0.6 | 10.1 | 25.07 |
| labeled | 10.3 | 4.8 | 7.4 | 0.2 | 2.2 | 4.99 |

With a 1-hour budget (and a slightly different prompt), labeled was actually a bit ahead (10.83 vs 8.88). The two runs disagree on which recipe is better, which says a lot about single-run noise. The failure below, though, showed up in both.

**What went wrong with labeled**

It was not code errors. Tool errors were 2.8% of turns for labeled vs 4.9% for weighted. The difference was turns that ended without any tool call:

| 7h runs | turns | turns with no tool call | degenerate-reasoning turns* |
|---|---|---|---|
| weighted | 3,668 | 132 | 148 |
| labeled | 4,767 | 1,474 | 624 |

\*A line repeated 4+ times inside one reasoning block, or "Hmm" more than 25 times per 1,000 chars.

The clearest case is lp85 (labeled):
1. Turns 0–293 are normal. The model clears 3 levels, and every turn ends in a tool call.
2. At turn 294 (level 4), reasoning grows to ~14K chars and hits the generation length limit, so no tool call comes out.
3. From then on, every remaining turn (1,231 in a row, until the 7h budget ran out) is ~2K chars of reasoning followed by a normal `stop`, with an empty answer and no tool call.
4. Our harness answered each empty tu

## [743723] Harness or model? Notes from a week of controlled harness experiments — sergueimakarov 2026-09-26
**Setting.** Over the past week we ran a series of controlled experiments on a public Duck-based harness. The model, the serving stack and the time budget stayed fixed. Each change was added as a single isolated layer and compared against the same baseline on the public games. We deliberately avoided stacking changes: when several layers ship together, a gain from one can hide a loss from another, and the combined result says little about either.

**Measurement.**The first result concerns the metric itself. Repeated runs of an identical build produce a wide spread of scores. The per-game outcome is close to bimodal: a game is either understood early or yields almost nothing. A single lucky or unlucky game can therefore move the aggregate noticeably. As a consequence, one run resolves only large effects. Reliable comparison requires the mean of several baseline runs, and many single-run "improvements" fall within the noise. We also found it useful to read the verdict on all games together and separately on the subset of games whose outcome is most stable. A change that only moves the volatile games is much harder to trust.

**Harness layers.** Almost every added layer scored at or below the baseline: consensus between sampled answers, a reasoning-discipline block, higher-resolution board images, and an executable world model with replay validation and search-based planning. Before reading any score, we checked that each layer had actually been active: its markers in the logs, and its traces in the model's tool calls. This step turned out to matter. The world-model scaffold is the clearest example: the model largely ignored it, so that run measured the presence of an unused instruction rather than the method. Offline, the model rarely produced a simulator that predicted unseen transitions better than a trivial "nothing changes" baseline. The comparison against that trivial baseline was important too: several simulators that looked exact on the observed transitions were no better than it on new ones.

**Where runs fail.**The most informative analysis compared stuck runs with successful runs of the same game. Replaying recorded runs on the local engine makes it possible to align them state by state. Both pass through the same states and diverge within the first few moves of a level. At most of these forks, the stuck run had already tried the action type that later proved decisive. The failure is therefore neither memory nor coverage of the action space. It is 

## [743723] Harness or model? Notes from a week of controlled harness experiments — scottlegrand 2026-09-26
That and sb26. But 10 to 15 on the public is about what I'd expect from this notebook. That translates to three to five on the hidden. You should be able to hit at least 40 levels on the public and my record was 52.

## [743723] Harness or model? Notes from a week of controlled harness experiments — sergueimakarov 2026-09-27
A short follow-up with two numbers behind the claims in the post, since a few people asked how large the effects actually are.

Noise. Two runs of an identical build, one right after the other on the same server, with a 30-minute cap per game: 2.60 and 1.45, with the first level cleared in 15 games vs 9. Nothing differed between them except sampling. Over full-length runs of the same build we have seen a spread of roughly 4.5 to 9.4 on the public games. So a single run of a harness change tells you almost nothing unless the effect is very large. We now compare against the mean of several control runs, and we look at mechanism counters (requests per game, moves per request, calls that only inspect the board) before we look at the score.

The early fork. Aligning stuck runs with successful runs of the same game state by state, in 83% of the forks the stuck run had already tried the action type that later turned out to be decisive. It had the evidence; it drew the wrong conclusion about the goal and kept defending it. That is why we read the remaining gap as a judgement problem rather than an exploration or memory problem.

## [744365] Hill-climbing on the LB happens in groups? — grigoriyzatravkin 2026-09-29
I think that there are some sort of stepwise function in the competition per design. As soon as your agent starts understand level 2 of the game, its very likely its going to be able to solve level 3,4, 5 and so on. So basically every improvemnt can result in bigger and bigger increase of the score. And more points you have, more points you gain from every imporvment. I saw several times in my public runs that when agent starts to understand the game (passes level 2) then suddenly he also gets all next levels, sometimes up to 100 points. 

So I wouldnt be very surprised if 100 points will be achieved on the competition.

## [744365] Hill-climbing on the LB happens in groups? — kriztianrubin 2026-09-30
Hill-climbing on the leaderboard & the Astra unlock
"Serguei Makarov nailed it: nobody needs a secret cabal when the leaderboard itself serves as the ultimate high-signal diagnostic. Seeing a top score shift from a 0.12 or single-digit plateau up to a structural tier tells everyone that the bottleneck isn't the base model's raw capacity—it's the harness architecture.
Looking closely at what OpenAI’s Astra pulled off on the benchmark (jumping from 62.7% on the standard harness up to 99.9% with the Provider Adapter harness), the real unlock isn't brute-force token generation. It's how the scaffolding forces the model to transition from passive reactive guessing into building an explicit, on-the-fly symbolic world model. When an agent compresses raw grid pixels into compact algebraic shorthands—tracking object coordinates, rotation indexes, and causal sequence lengths natively—its action efficiency skyrockets. Higher reasoning effort actually cuts down execution costs because the model stops wasting steps wandering through blind exploration loops.
For the rest of us stuck in the trenches moving past baseline scores, the takeaway is clear: stop polishing prompt strings and go back to the foundational feedback loop. The teams cracking the next milestones are the ones engineering strict epistemic-to-pragmatic phase controllers that map environment failure boundaries before getting choked out by the RHAE power-law penalty. The leaderboard is moving because everyone is finally building real causal machinery instead of hoping heuristics will carry them across the finish line."

## [744545] Can some teams regret not sharing for 2nd milestone prize? — huikang 2026-10-01
I am quite surprised by your regret.

I thought your advantage has been a significantly better finetuned model, given your experience in dataset construction and finetuning. Maybe also did some inference engineering.

Sharing the finetuned model might for the milestone prize might still make sense if you can tune a much better model anyway. I thought you were confused with the complexity of the progress as much as I am.

For my case, I am quite relieved that I no longer eligible to make a decision. I still appreciate the very short period of time I am at the top of the leaderboard.

## [744792] Comparing the Milestone 2 winning solutions — huikang 2026-10-01
Congratulations to the winners (tentative, to be confirmed by the organizers) of the Milestone Prize 2!

All three run Tufa Labs' Duck harness on the Tufa ARC-AGI Framework (TAAF) and serve Qwen3.8-Flash-Next.

Here is a comparison ~

| | dfranzen | lordhansolo | sirikilohit |
|---|---|---|---|
| Public LB score | 27.89 | 23.84 | 22.53 |
| Kaggle | [notebook]( | [notebook]( | [notebook]( |
| GitHub | [github]( | not linked | [github]( |
| Write-up | [writeup]( | not published | [writeup]( |
| Model and quant | [Intel/Qwen3.8-Flash-Next-W4A16-AutoRound]( [uploaded]( (AutoRound W4A16 + BF16 PLE)<br><br>draft: [albucino/Qwen3.8-Flash-Next-W4A16-FP8PLE]( [uploaded]( (INT4 MTP) | [primitive-ai/Qwen3.8-Flash-Next-mixed-NVFP4-FP8]( [uploaded]( (NVFP4 + FP8 mixed + BF16 PLE, NVFP4 MTP head built in) | [Intel/Qwen3.8-Flash-Next-W4A16-AutoRound]( [uploaded]( (AutoRound W4A16 + RadixArk FP8 PLE)<br><br>draft: [RadixArk/Qwen3.8-Flash-Next-NVFP4]( [uploaded]( (NVFP4 MTP) |
| Speculative | 3 draft [tokens]( INT4 MTP [draft]( FR-Spec hot [tokens]( | 3 draft [tokens]( MTP [head]( draft [vocab]( | 3 draft [tokens]( MTP [draft]( |
| Model weights on GPU | 73.64 GB<br><br>69.85 GB target<br>3.79 GB draft | 71.94 GB<br><br>target incl. MTP head | 73.57 GB<br><br>69.78 GB target<br>3.79 GB draft |
| KV + Mamba cache on GPU | 15.94 GB<br><br>11.58 GB target KV<br>0.96 GB draft KV<br>3.40 GB Mamba | 19.69 GB | 16.97 GB<br><br>11.50 GB target KV<br>0.96 GB draft KV<br>4.51 GB Mamba |
| CUDA graphs on GPU | 1.14 GB<br><br>0.48 GB target verify<br>0.37 GB draft decode<br>0.29 GB draft extend | 0.46 GB | 1.59 GB<br><br>0.65 GB target verify<br>0.61 GB draft decode<br>0.33 GB draft extend |
| GPU memory left free | 4.25 GB | 1.90 GB | 3.17 GB |
| Offloaded memory | 95.37 GB<br><br>95.37 GB BF16 PLE | 96.55 GB<br><br>95.37 GB BF16 PLE [table]( GB BF16 embed_tokens [table]( | 95.68 GB<br><br>47.68 GB FP8 PLE<br>48 GB hierarchical KV + Mamba [cache]( |
| Server | [SGLang Pennyroyal v2.5.3]( | [vLLM 0.29.1rc1 nightly e975732]( | [SGLang Pennyroyal v2.5.0]( |
| MoE backend | [auto]( (Marlin for W4A16) | [auto]( (flashinfer_cutlass for NVFP4) | auto (Marlin for W4A16), draft on [flashinfer_cutlass]( |
| Linear-attention backend | [flashinfer]( | flashinfer prefill (auto), triton [decode]( | [flashinfer]( |
| KV dtype | fp8_e4m3 | fp8_e4m3 | fp8_e4m3 |
| Pool sizing | mem fraction 0.96 | gpu util 0.98, profiled | mem fraction 0.97 + 48 GB host tier |
| KV pool (tokens) | 1,011,264 | 1,417,1

## [744792] Comparing the Milestone 2 winning solutions — xiaoz259 2026-10-01
I am curious about fp8 kv choice. I ablated it a while ago and found very little NLL penalty to use nvfp4 kv and had been using it since. On the other hand, I just ran a token matched level completions against the milestone solutions and found mine to be less action-efficient for some reason. I am wondering if this has to do with the kv quant or just the harness prompts.

## [744932] ARC Paper Track: Metamorphic Core Reasoning via Dynamic Graph Restruct — angelsonawane 2026-10-01
# ARC Paper Track Proposal: Dynamic Meta-Graph Structuring for Abstract Spatial Induction

**Author:** Angel Sonawane  
**Target:** Theoretical Framework for Fluid Intelligence Core Architecture  

---

## 1. Abstract
The primary limitation preventing modern large language models from achieving fluid intelligence on the Abstraction and Reasoning Corpus (ARC) benchmark is their reliance on fixed positional pixel embeddings and static computational logic. ARC puzzles demand that an artificial intelligence adapt to entirely novel spatial tasks using fewer than five context examples. This paper introduces the Metamorphic Core Reasoning (MCR) framework. Instead of processing grid colors as linear coordinate arrays, MCR abstracts spatial objects into highly dynamic graph networks. Each distinct visual shape on the grid becomes an interconnected logical node. By altering the layout structure dynamically according to topological logic changes rather than static rules, our framework allows lightweight systems to achieve fluid reasoning without requiring extensive cloud training compute.

---

## 2. Core Problem: The Memory-Bias Failure in Spatial Logic
Standard multi-modal architectures handle ARC tasks by treating grids as visual matrices or direct text strings. This paradigm suffers from two major logic bottlenecks:
1. Syntactic Rigidity: A model trained on 3x3 scaling logic fails to generalize when a task demands a 9x9 transformation matrix.
2. Inability to Conceptualize Novel Rules: Because models rely heavily on memory patterns learned during training, they struggle with abstract operations (such as color inversion or rotation alignments) when applied to symbols they have never seen before.

---

## 3. Methodology: Metamorphic Core Reasoning Framework
The MCR architecture bypasses static rule strings entirely, dividing the puzzle interface into three adaptive operational layers:

* **Layer 1: Structural Object Graph Extraction:** Grids are converted into independent spatial nodes based on boundary similarities. If a green block is inside a black border, the layout is treated as a parent-child logic node.
* **Layer 2: Relational Topology Testing:** The framework runs the sample transformation tasks through an abstraction test engine. Instead of asking "which pixel moves?", it evaluates "how did the connection structure between the objects change?"
* **Layer 3: Generative Matrix Reconstruction:** Once the underlying topological alteration pattern is uncovered, t

## [745062] Incredible notebook performance variation (Daniel Franzen's copies dat — sonphamorg 2026-10-02
Immediately after Daniel Franzen's submission, hundreds of participants copied the notebook and made the submission, creating a large distribution around 20 to 34 score. Since the notebook was released just 24 hours ago, each participant only had one chance of making this submission. This means the score currently in the leaderboard is a true performance sampling distribution of the notebook, and not after each notebook has been submitted multiple times and we only take the higher score. 

This allows us a rare window into the true extent of variation in ARC-AGI-3 performance.



* Mean: 25.77 points
* Standard deviation: 3.93 points
* Median: 26.19 points

This means that to be 90% sure that you make improvements you need to be at least 8 points above. It also means that Tufa and Yi-Chia can be comfortable not sharing the notebook as their lead was big enough to survive the Franzen's copies onslaught.

## [745654] After the 1 October image update (Python 3.13): which Docker image doe — justnoone2026 2026-10-03
Hi ARC Prize team (@gregkamradt) and Kaggle staff,

On 1 October the default notebook images changed. Both gcr.io/kaggle-gpu-images/python:latest and gcr.io/kaggle-images/python:latest are now built on 2026-10-01 (Ubuntu 24.04, with python3 = Python 3.13). Until 30 September the default was the image built on 2026-06-29 (Ubuntu 22.04, Python 3.12).

Many notebooks in this competition install offline wheels that were built for Python 3.12 (for example a vLLM or SGLang wheelhouse), so they depend on the image their notebook version was created in. The documentation says that every notebook version is associated with a specific Docker image version, but it does not say which image the scored rerun uses.

Question: when a notebook version is submitted to this competition, is the scored rerun on the hidden games executed in the Docker image of that notebook version (the pinned, original environment), or in the current default image?

A short confirmation would tell everyone whether a pinned Python 3.12 environment is safe for the final submissions, or whether wheels have to be rebuilt for Python 3.13. Thank you!

## [745654] After the 1 October image update (Python 3.13): which Docker image doe — kriztianrubin 2026-10-03
Kaggle executes scored competition reruns using the pinned Docker image version associated with the specific submitted notebook version, not the latest default image.
Key Technical Details
 * Docker Image Pinning Contract: When you commit and submit a notebook version, Kaggle records the exact container image digest used during that commit. The hidden test evaluation rerun executes inside that identical pinned environment, preserving the original Python version (e.g., Python 3.12.13).
 * ARC-AGI-3 Offline Wheel Dependencies: The competition offline wheel dataset (/kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels) explicitly contains C-extension binaries compiled for CPython 3.12 (cp312), such as pillow-12.2.0-cp312-cp312-...whl and numpy-2.4.4-cp312-...whl. Because ABI bindings for cp312 wheels are incompatible with Python 3.13 (cp313), forced image upgrades would break offline installation steps.
 * New Submissions Post-October 1: Any new notebook created after the October 1 image default shift will default to Python 3.13 (Ubuntu 24.04). If your offline pipeline relies on cp312 wheels, you must explicitly set the notebook environment setting to "Pin to original environment" or select an older pinned image version in the notebook sidebar before committing.
Verification Guardrail Code
Add this runtime check at the top of your submission notebook prior to running pip install to ensure environment safety:
import sys

# Verify Python runtime compatibility before offline wheel installation
print(f"Execution Runtime Python Version: {sys.version}")
assert sys.version_info[:2] == (3, 12), (
    f"Environment Mismatch: Expected Python 3.12 for cp312 wheels, "
    f"but detected Python {sys.version_info.major}.{sys.version_info.minor}. "
    f"Please set Notebook Environment to 'Pin to original environment'."
)