## [684724] Intended compute budget — jeroencottaar 2026-03-25
Currently, submissions for this competition cannot use GPUs outside the standard P100 / 2xT4. However, the competition overview mentions: "Upgraded accelerators will be added to this competition in the near future, stay tuned for more details."

Is there any indication what accelerators these will be exactly? This information is important to know where to target our solutions.

## [684852] Do we run on public and private test set? — jeroencottaar 2026-03-26
When we make a submission, does it immediately run on all 110 problems in the full test set? Or does to run on only the 55 problems in the public test set, with reruns on the private test set performed at the end of the competition?

## [684969]  Kaggle Error displayed after submission. — jeroencottaar 2026-03-27
From some testing of my own, I think this error may be triggered if the arcade is not interacted with for 20 minutes.

## [686155] Is it possible to develop and test my code for this competition locally? Any wor — jeroencottaar 2026-03-31
I've released this notebook showing how to run the training set of 25 games, with brief instructions on how to do this also outside the Kaggle environment.

https://www.kaggle.com/code/jeroencottaar/simplified-submission-approach/

## [686416] Simplified submission framework — jeroencottaar 2026-03-31
The official notebooks show how to submit your agents to run on ARC-AGI3, but they're pretty complicated. Also, they do nothing if you're not actually submitting - they don't actually run on the 25 training games then.

We've made this notebook that shows a more straightforward way to interact with the ARC-AGI3 environments. It will run on the 25 training games when not submitting (including diagonstics), and on the 110 test games when submitting.

Good luck!

https://www.kaggle.com/code/jeroencottaar/simplified-submission-approach/

## [687655] Human scores visible to agents — jeroencottaar 2026-04-03
From some submission probing, I believe that the scores of the second-best human used for scoring (i.e. `environment_info.baseline_actions`) are available to us for the 110 test games during submission. Is this intentional, and are we indeed free to use this information?

## [687950] Is Offline BFS "Cheating the Spirit" of ARC-AGI-3? — jeroencottaar 2026-04-04
It's definitely cheating. But I'm not convinced that's what these notebooks are actually doing - they certainly do it offline on the 25 games (which is completely legitimate), but during submission they should not be able to find the game files. Not entirely clear to me if they succeed at finding these files - if they do, this definitely needs fixing.

## [695046] Better containers — infinitecreativity 2026-04-29
I think this is one hand a good idea, on another, not really possible.

The way the scoring is setup, there is a gateway that captures HTTP requests on the Arcade actions to create the scorecard. They effectively run this gateway to see what you are doing. If you submit a container you would have to do finicky things with the network traffic.

On the other hand I agree, I am trying to reverse-engineer the container too, so it would be nice to know more / have more freedom.

## [696615] H100s effectively unavailable — jeroencottaar 2026-05-03
We've been running into heavy queuing issues for H100s. Even now on Sunday morning, it's effectively impossible to get an interactive session going. Submitted notebooks are also spending >10 hours in the queue (when we gave up).

Are there any known issues with the infrastructure? Is it possible the H100 capacity is being abused for other purposes?

@addisonhoward

## [699208] Submissions not running 9 hours — jeroencottaar 2026-05-13
The maximum submission time should have been increased from 6 to 9 hours. However, we have been unable to get any submission running for more than 6 hours. This includes simple test submissions, such as a random solver playing only one move per minute.

Is it possible something is misconfigured? Perhaps the notebook runtime is 9 hours, but something in the ARC-AGI specific competition code is still limiting us to 6 hours.

Has anyone else been able to run a 9 hour submission?

## [699208] Submissions not running 9 hours — jeroencottaar 2026-05-18
@addisonhoward @gregkamradt Could you have a look at this? It does not seem possible to run submissions above 6 hours now - perhaps a soft timeout in the ARC3 specific submission management code?

## [699208] Submissions not running 9 hours — jeroencottaar 2026-05-23
Thanks for looking into this; we can confirm our submissions are now running for 9 hours.

## [699208] Submissions not running 9 hours — jakobbrggen 2026-05-28
@inversion It is still the same for our team. Our submissions only run around 3 hours even though we don't limit the time our notebook should run to 3h.

## [703056] Milestone 1 - Evaluation — jakobbrggen 2026-05-28
I just wanted to ask whether the first Milestone will be evaluated using the public or the private leaderboard?

## [703416] How I fixed the "Kaggle error" in ARC-AGI-3 submissions — jeroencottaar 2026-05-31
Congratulations on fixing the issue. 

If I read your notebook correctly, it doesn't play any games if not actually being submitted. You might want to consider hooking it up to the 25 public games when not submitting; this will allow you to debug directly, with full access to logs. An example of how to do this is shown here: https://www.kaggle.com/code/jeroencottaar/simplified-submission-approach

## [705022] How is the 1.30 on the LB possible? — jeroencottaar 2026-06-08
We have 1.30%.

## [705022] How is the 1.30 on the LB possible? — jeroencottaar 2026-06-08
It's a percentage. The maximum possible score is 100. (Not 115 - you can score 1.15x human baseline on a single level, but it gets capped to 100 per game.)

## [705022] How is the 1.30 on the LB possible? — jeroencottaar 2026-06-08
Yeah, correct.

## [705043] Exact timing of milestone prize — jeroencottaar 2026-06-08
@gregkamradt 

I'd like to check what the exact timing around the milestone prize is going to be. Note that as soon as we open source our notebook, we'll drop several hundred places because thousands of copies will be submitted to the leader board, and there is quite some variance. So we actually have a small window in which to open source. What's the exact time the milestone ranking is determined?

A note: other competitions such as AIMO had one point in time at which the milestone ranking would be frozen, then a separate deadline a few days later to actually open source and claim the prize. This means people don't have to guess their ranking ahead of time to make the decision whether to open source.

## [705043] Exact timing of milestone prize — jeroencottaar 2026-06-19
Would be great to see this clarified.

Regardless of the answer to the last question, we currently intend to share our best solution if we're still in first place on June 30.

## [705043] Exact timing of milestone prize — jeroencottaar 2026-06-27
Don't worry, we won't publish it at a time where it can be resubmitted for a decent score.

## [716696] Code for milestone 1st place open sourced - writeup tomorrow — jeroencottaar 2026-06-30
We've open-sourced our code for the purpose of the milestone. You can find it here: https://www.kaggle.com/code/jeroencottaar/taaf-duck-harness-kaggle

A more shareable verison (that didn't get the same lucky score) is here, we highly recommend working from this one: https://www.kaggle.com/code/jeroencottaar/taaf-duck-harness-kaggle-share

Tomorrow at 3 PM CEST we'll share a detailed technical writeup and several supporting materials, so stay tuned.

## [716696] Code for milestone 1st place open sourced - writeup tomorrow — jeroencottaar 2026-07-01
The high score is 100, not 1.

## [716696] Code for milestone 1st place open sourced - writeup tomorrow — jeroencottaar 2026-07-01
No, it's very unstable, ranging from 0.7 to 1.3.

## [717133] Tufa Labs’ Winning Solution for ARC-AGI-3 Milestone 1 — infinitecreativity 2026-07-01
*Authors (alphabetical order): Harold Bessis, Jeroen Cottaar, Isaiah Pressman, Dries Smit, Michal Tešnar, and Stefano Viel.*

This technical write-up describes our winning solution for the first milestone prize in the [ARC-AGI-3 Kaggle competition](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3). We present the Duck, the successor to [Stochastic Goose](https://medium.com/@dries.epos/1st-place-in-the-arc-agi-3-agent-preview-competition-49263f6287db) authored by Dries Smit, which won the ARC-AGI-3 agent preview competition. Our solution consists of an inference harness leveraging [Qwen 3.6 27B FP8](https://huggingface.co/vrfai/Qwen3.6-27B-FP8) as its base model and takes heavy inspiration from the [RGB Agent](https://blog.alexisfox.dev/arcagi3) and [Symbolica](https://www.symbolica.ai/blog/arc-agi-3) solutions. The harness uses a Python tool to interact with a game and continuously evicts past messages from its context to keep playing indefinitely. We make the code freely available on [GitHub](https://github.com/Tufalabs/duck-harness). Disclaimer: the code was developed with the help of coding assistants.

We discuss our solution and compare it to other approaches in our [blog post](https://tufalabs.ai/research/duck-harness), and showcase is in an episode of [Machine Learning Street Talk](https://x.com/MLStreetTalk/status/2072326433922297975?s=20). We discuss the progress on the benchmark in more depth in [another episode of MLST](https://www.youtube.com/watch?v=Vg6FBKTlfOw).

Alongside this write-up, we are publishing [the notebook](https://www.kaggle.com/code/jeroencottaar/taaf-duck-harness-kaggle-share) corresponding to our best submission score of 1.21% on the Kaggle leaderboard and 1.6% on the public train set, respectively. This submission initially scored 1.30%, but that result was retracted by Kaggle, leaving 1.21% as the official leaderboard score ([result here](https://www.kaggle.com/code/jeroencottaar/taaf-duck-harness-kaggle)). We observed a large variance in scores for the same submission, our best submission got scores as low as 0.77% on Kaggle and on the public games we observe standard deviations of up to 0.4. Our notebooks represent only the infrastructure and metrics; the agent code is attached as a dataset.

We release this harness with the hope of lowering the barrier to entry and inspire innovation from the community. Next, we will present the harness design, explain how the agent behaves, and show results on the public train set. 

> 📝 The text in this post is fully human written, but figures are produced with coding assistance. Refer to the submissions notebook and the repository as the ground truth.

# Design Principles

We are developing under the constraints of the Kaggle competition, which provides a RTX Pro 6000 GPU with 96 GB of VRAM and 9 hours of runtime to play 110 games in any order. Therefore, we aim for:

1. open-source models that fit the VRAM constraint, mainly Qwen 3.6 27B FP8;
2. generic ARC-AGI-3 problem solving: we do not directly encode any information about the training games into the harness to make it generalize over all games;
3. a lightweight harness, that still attempts to utilize the underlying model's capabilities as much as possible. This keeps the model in the driver seat, while future-proofing our solution to be applicable when stronger models arrive eventually.

### Related Works

Our solution takes inspiration from previously published works. [Symbolica’s solution](https://www.symbolica.ai/blog/arc-agi-3), called ARCgentica, achieved a score of 36% the day after the release of the public official games. It was developed for frontier models and uses an orchestration system, which allows the model to call itself recursively — similar to [Recursive Language Models](https://arxiv.org/abs/2512.24601), — to solve a game and execute a limited number of actions in each sub-agent. This solution shows that the models are naturally good at problem solving using code, similar to the [CodeAct](https://arxiv.org/pdf/2402.01030) method.

Alternatively to an ARC-AGI-3-specific harness, one could wrap a generic coding harness around the model. This is what the [RGB Agent](https://blog.alexisfox.dev/arcagi3) does using [OpenCode](https://opencode.ai/). Their solution was the first to show near-human action efficiency on the 3 preview games. The full game history is stored in one log file, which the agent then uses via grep, file reads, or executing Python commands. This allows the agent to first analyze observations, generate hypotheses, and then queue up a limited number of actions; a pattern that limits wasteful moves.

Our harness builds on these ideas, where the agent interacts with the game state and history using a Python Read-Eval-Print Loop (REPL).

### Harness Architecture

The Duck harness exposes the game to the agent as Python variables and allows the agent to interact with these variables in whichever way it prefers, letting it lean on its pre-trained patterns:

- All game observations are encoded as Python variables;
- The agent can interact with these variables using the Python tool, call pre-built helper functions, and take actions in the environment;
- The actions are executed in the ARC-AGI-3 environment, which then updates the Python sandbox with new variables;
- The LLM freely iterates between reasoning, tool use, and taking actions, until the game is solved or times out;
- Whenever we reach the maximum context length, we evict the oldest non-system-prompt context to enable the model to play indefinitely;
- We also leverage Qwen 3's multimodal image input to allow the model to directly observe the latest frame. To inspect specific parts of a frame, it can process the ASCII grid or use a segmentation tool.



In the subsequent paragraphs, we explain the harness design in more detail, provide additional documentation of how the game is exposed to the LLM, and explain how we construct the agent context. We also discuss the LLM perception, both using pre-built tools and the model’s image input, and provide a short summary of the harness performance on the official public games.

# Implementation Details

## Python Interface

The game state is exposed to the LLM as Python variables inside a REPL environment, which includes a few standard libraries. The agent interacts with the environment by calling a python tool, which allows for code execution up to a maximum time limit of 30 seconds and maximum output size of 4096 characters. This allows the agent to produce code to inspect the grid, search for action sequences that achieve a specific goal, and take actions directly, as shown below. The REPL environment is reset between every toolcall. This gives the model flexibility to combine action execution with environment observation.

<table>
<tr>
<td width="50%"><img src="https://www.googleapis.com/download/storage/v1/b/kaggle-forum-message-attachments/o/inbox%2F9182647%2F6f89acc63701f4b6b677fc0ae7ca9928%2Fviewer_thinking_figure.png?generation=1782916452312529&alt=media" width="100%"></td>
<td width="50%"><img src="https://www.googleapis.com/download/storage/v1/b/kaggle-forum-message-attachments/o/inbox%2F9182647%2F0cdc19408309afc5b4f0f4447b73f1fa%2Fviewer_action_figure.png?generation=1782916448951127&alt=media" width="100%"></td>
</tr>
</table>

> ⚠️ The REPL is not fully isolated. Running this harness can lead to arbitrary code execution. Run the code at your own risk.

### Pre-loaded Variables

The REPL is pre-loaded with variables, which represent the state of the environment. The variable `current_frame` stores the latest board state and exposes the attribute `.ascii`, which provides the game board in ASCII code, along with other variables such as the current level and step. Additionally, `.segmentation` provides segmentation of the board into connected components (discussed in detail later). Similarly, `previous_frame` stores the previous game frame. The `history` variable lets the model inspect its previous moves by pairing `.action` and `.frame`. Additionally, `transitions` list exposes state-action-state. Each action produces a `result` object, which stores variables about the game state, like the number of previous actions, current level, reward, state, which actions are valid, and so on. As the model usually needs to learn about the most immediate state of the game, we provide it the latest variables `last_transition`, `last_action`, and `last_action_result`.

### Actions

The model is informed about the possible actions through the `valid_actions` variable. It can execute one or multiple of actions using the `action` function. This gives it the ability to execute actions programmatically, e.g., in the loop or while tracking an object. The actions are given natural names (`UP`, `DOWN`, `LEFT`, `RIGHT`, `SPACE`, `MOUSE` and `RESET`). The `UNDO` action is not provided to the model as the model fails to use it efficiently: it undoes big batches of actions that wastes energy.

### World Model

We prompt the agent to produce a simple world model using a note that is carried over multiple turns. This helps it form and store important facts it learns over turns and levels. It can use tags like `World model:` in its response, which enables it to copy important notes into the next user message, until it decides to overwrite it. This helps the model keep a mental note of what it is trying to achieve.

## Context Construction

We always include the full system prompt in the context. The assistant generates a response per turn, which usually consists of some reasoning and a python tool call that is executed inside the REPL. If actions are executed inside the REPL, a new user message is appended to the context, including the updated information about the game state, e.g., level transitions, valid actions, and whether a level reset occured. We cap the agent's maximum context to 64k tokens to allow the agent to act over longer timespans with reasonably high token throughput. The harness attempts to maintain an input context of 32k tokens by evicting the oldest user message and subsequent assistant turns, whenever it surpass this limit. We illustrate this in the figure below, where we remove the reasoning blocks to simplify the visualization. We also provide a [GitHub repository](https://github.com/Tufalabs/duck-harness), which includes a viewer that can be used to inspect the agent context. We currently do not optimally use prefix caching on the vLLM engine.

<p align="center"><img src="https://www.googleapis.com/download/storage/v1/b/kaggle-forum-message-attachments/o/inbox%2F9182647%2Ff1bf72a9c4ed830a81694fd924d6d764%2Fcontext_eviction.gif?generation=1782916501244379&alt=media" width="50%"></p>

### System Prompt Construction

The system prompt contains many ARC-3-specific hints that are generally useful over ARC games, without providing game-specific hints. We provide information around the game setup, possible actions, and the general goal of completing as many levels as possible in an action-effecient manner. Additionally, we describe the REPL environment, with all its variables and provide recommendations on how to best leverage them. If multi-modal inputs are used, the model is instructed on how to use them as well, e.g., how to interpret the scene, the existence of a time bar, and that minimizing the bar is not the goal of the game. Finally, the model is also informed about the interface of the Python tool.

### User Response Construction

When an action is executed, in addition to the normal REPL response, a new user message is produced. This provides extra context to the model on how the environment has changed. We also repeat the state of the game and what the valid actions are to the agent, as well as a reminder on how it should use the Python tool. Lastly, we also repeat the world model instructions and provide the world model if it was defined; an the model is reminded that it should collect evidence on what happened before acting.

## Multimodality & Segmentation

To give the model a basic understanding of the current game state, a 4× upscaled image of the board is injected into its context at the beginning of every turn. Qwen's encoder processes images in 16×16 pixel patches and we found that this upscaling gives the model the best visual understanding of the scene. The model can roughly identify the objects and can perform more detailed analysis using Python code. We also tried injecting more frames or video animations, but we noticed that small models struggle with extracting details and acting on them. This also means that the model does not see animation feedback, which can be crucial, e.g., in official games such as `sb26` and `tn36`.

A common failure mode of the agent is that it tries to print the whole grid directly, which pollutes its context. To help it analyze the structure of the grid, we provide it with a segmentation tool that helps the model locate the 4-connected components in pixel space, denoting adjacency and child-parent relationship between the nodes. This tool significantly helps in games where connected components are meaningful syntactic units. The example below illustrates the segmentation tool on the first frame of `ls20`.

![segmentation_decomposition.png](https://www.googleapis.com/download/storage/v1/b/kaggle-forum-message-attachments/o/inbox%2F9182647%2F8b5ece64809e4f2b49f6aa837b6ce579%2Fsegmentation_decomposition.png?generation=1782916513869763&alt=media)

# Results

The harness was developed for [Qwen 3.6 27B FP8](https://huggingface.co/vrfai/Qwen3.6-27B-FP8), which we deploy using a [vLLM](https://vllm.ai/) server. The harness can also be used with API keys using OpenRouter or OpenAI. To evaluate the harness, we run it on the 25 public games with 20 tries each. We include the result [directory on GitHub](https://github.com/Tufalabs/duck-harness/tree/main/example-run), so that the outputs can be verified and analyzed. The mean score we achieve is `1.6002 (+/- 0.4475)`. The heatmap below shows the performance of the model across games and tries with attempts on the x-axis and games on the y-axis. The performance is rather uneven, with some games being solved consistently for over 40% of the levels, while for some not even the first level is solved. The number of attempts that reach a given ARC score is plotted on the right, showing a sharply declining distribution.

<table>
<tr>
<td width="50%"><img src="https://www.googleapis.com/download/storage/v1/b/kaggle-forum-message-attachments/o/inbox%2F9182647%2F954239d783fc760d40791d7c107d7e2e%2Ffig1_heatmap_levels.png?generation=1782916506319916&alt=media" width="100%"></td>
<td width="50%"><img src="https://www.googleapis.com/download/storage/v1/b/kaggle-forum-message-attachments/o/inbox%2F9182647%2F58ea39fdd681d4bb6d5ac79761985885%2Ffig3_cumulative_score.png?generation=1782916509571699&alt=media" width="100%"></td>
</tr>
</table>

For a discussion about the performance of frontier models in our Duck harness, please refer to our [blog post](https://tufalabs.ai/research/duck-harness/). The results directory on GitHub also includes an automatically generated [`diagnostics.html`](https://github.com/Tufalabs/duck-harness/blob/main/example-run/diagnostics.html), which visualize and compare the runs in more detail. You can browse this file directly in the [shared notebook](https://www.kaggle.com/code/jeroencottaar/taaf-duck-harness-kaggle-share). 

# Discussion

The Duck harness shows how small coding models can be used to solve ARC-AGI-3 games by leaning into the post-trained capabilities of the models. It shows good first signs of life and we expect this approach to scale with better small models and additional post-training. The harness was mainly built by understanding the strengths and weaknesses of various open-source LLMs, while trying to maximize the score we achieve on the public games. However, it has not been scrutinized and ablated over many design decisions. The main driver of improvement throughout our harness development came from better base models and introducing multi-modality. Against our intuition, hand-crafting specific tools for the model did not help, as it seems to hinder the creative abilities of the model.

To enable the agent to perform well, we had to encode a lot of specific knowledge into the prompts. This includes steering its goal setting, e.g., keeping it from treating the energy bar as the objective or inventing nonsensical goals like moving a block to a fixed position. The prompts were also carefully tuned to prevent the model from using incorrect formatting and misinterpretation variables and attributes. The model is steered away from over-interpreting a frame, as it would often hallucinate classical game sprites, like robots, or try to solve it as a classical pixels-based game, such as Atari. The models have a hard time identifying, which features of the environment are interesting, thus they dump full boards into the context that dilutes their attention. Although coding models are great at general reasoning, they need to be extensively adapted to fare well in the domain of games.

We believe the Duck can benefit from many improvements. The context management could be improved by compaction or adding memory to help the model carry curated context across multiple turns. The perception can also be improved, as coding models are not trained to reason over crops of ASCII grids, but rather abstract descriptions. Generally, transmitting abstract visual information in a useful format is a big challenge, however a first step in this direction is the segmentation tool we provide in the Duck harness.

With this, we are inviting the community to collaborate and improve on our work and are looking forward to seeing your contributions!

## [707862] Is the public game bp35 broken? — jeroencottaar 2026-07-02
(Answer formulated by Claude)

`get_pixels()` isn't part of the player-facing API — it's a method on the engine's `BaseGame` class, intended for game code to inspect its own scene. It calls `camera._raw_render()`, which renders at the level's native viewport resolution (8×8 for bp35), *before* the upscale-and-letterbox step that produces the 64×64 player frame. So it's not clipping or dropping anything; it was just never meant as an observation function. The actual protocol is `env.reset()` / `env.step(action)` returning the 64×64 frame — which is also all that exists over the HTTP API, where the game object isn't reachable at all. So `env.step(...).frame` is the right (and only) way to observe the game.

## [717133] Tufa Labs’ Winning Solution for ARC-AGI-3 Milestone 1 — jakobbrggen 2026-07-02
Thanks for this detailed explanation. It really helps to comprehend your solution and iterate it further.

## [717133] Tufa Labs’ Winning Solution for ARC-AGI-3 Milestone 1 — jeroencottaar 2026-07-03
Yes, but due to cost we've only done a few games. See here: https://tufalabs.ai/research/duck-harness

## [724890] About using GPU RTX PRO 6000 — jakobbrggen 2026-07-14
No, I do not.

## [726367] How long do you think it'll take until we reach AGI? — jakobbrggen 2026-07-15
Curious to hear the community's take: given the progress on ARC-AGI-3 and current AI systems, what's your honest timeline estimate for AGI? A few years, a decade, longer? What milestones would convince you we're close?

## [734369] Write Up: Taaf Anim Agent — jakobbrggen 2026-08-11
Link to code: https://www.kaggle.com/code/jakobbrggen/taaf-anim-arc-agi-3-solver
Link to the original TAAF write-up: https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133

## Idea

Our experiments over the last months showed mixed results. On the one hand the agent is very token efficient and the model cooperates better than we expected — when we give it a tool, it actually reaches for it on its own. On the other hand, because of its size and its limited reasoning capability compared to frontier models, it needs a lot of guidance, and it makes avoidable mistakes that cost actions.

So we focused on two things at once: giving the agent **more tools**, and adding **fixed restrictions** that keep it from burning actions on moves we already know are useless. Up to this point only two of our experiments really worked, which is why this write-up is short. We still have plenty of ideas left, and we will keep the comment section and the notebook updated whenever we find something that might move the community forward.

## Key elements

**1. A hard no-op guard.** The harness tracks every `(level, board state, action)` combination that has already been executed without changing the board. If the model tries the exact same action in the exact same state again, the harness blocks it before it reaches the environment and tells the model that this action was already proven ineffective here. The blocked action costs no action budget — only one LLM turn.

This one is small, and honestly our own measurements of it are weaker than we first thought. It looked like a solid ~12–20 % reduction in actions used, but we later realised that our runs are bound by the **wallclock limit**, not by the action budget: every run hits the time cap. Under a time cap, "fewer actions" can simply mean "each turn got more expensive", and a blocked action still costs a full LLM turn. So take that number with a grain of salt — we did.

**2. Giving the agent access to the animation frames between board states.** This is the bigger change and the one we think matters. Details below.

## Animation access

This was one of the experiments we had planned ever since Tufa Labs pointed out that their agent cannot perceive multi-frame animations. It turns out this isn't a limitation of the environment at all — the information is already there and simply gets dropped.

The ARC-AGI-3 API returns `frame` as an **array**, not a single grid. The docs are explicit about it: *"Multiple frames may be returned if the environment advances internally (e.g., animations) before settling."* On the engine side, `arcengine`'s `perform_action()` renders a frame after every internal `step()` and returns the whole list. TAAF even wraps it nicely — `GameState` exposes `frame` (the last one), `animation_frames` (everything except the last) and `all_frames`.

The catch: `animation_frames` and `all_frames` are **never called anywhere** in the harness. The only path a grid takes into the agent is `state.frame`, which is `raw.frame[-1]`. Everything in between is thrown away.

How much is "everything in between"? On the 25 public games, **13 produce multi-frame responses**. Two concrete examples:

- **sp80** — this is the clearest case. The build phase is single-frame, but `ACTION5` starts the pouring phase, and that returns **22 frames, all different, with 624 pixels that only ever exist mid-animation**.
- **bp35** — every single action returns an animation and some movements can not be understood without the animations.

Since this pattern shows up in over half the public games, we assumed it would show up in the private ones too.

### What we implemented

Three stages, all behind one feature flag:

1. **Compact metadata on every action, always on.** Each action result now carries an `animation` field: how many frames came back, how many of them were distinct, whether the final board is identical to the board before the action, and how many pixels were transient plus their bounding box. This costs a few dozen tokens and needs no cooperation from the model at all.
2. **An `animation()` tool the model can call.** It returns a compact diff timeline — one entry per distinct frame with the changed cells, identical consecutive frames collapsed. `animation(frame=k)` reads a single frame cropped to the transient region, `animation(action_num=n)` looks back at an earlier action. Full 64×64 frames are never returned; one alone would blow the tool response budget. Calling it costs no in-game action.
3. **A proactive hint.** When the model is stuck in a level and the animations there are diff-heavy, the harness suggests calling the tool.

Point 1 is the important one, because it is executive rather than advisory. Points 2 and 3 depend on the model playing along — which, to our surprise, it partly does.

### But there are downsides too

We want to be honest about these, because they are the reason our public-set A/B did **not** show a significant improvement (+1.4 % mean score, p = 0.92 over 6 games × 4 passes), even though the private set went well.

- **Tokens are the real currency, not actions.** Every run in both arms hits the 132-minute wallclock cap. Nothing ends because of an action limit and nothing ends in a win. That means any change that makes a turn more expensive directly buys you fewer moves. Our animation arm went from 384 to **449 tokens per action (+17 %)**, and the effect was mechanical: in every single game, more tokens per action meant fewer actions, and fewer tokens per action meant more. On one game we lost 54 % of our actions and gained 129 % token cost per action. If you add information to the context, budget for it in moves.
- **The model calls the tool, but mostly at the wrong moments.** It used the tool unprompted in 21 out of 24 runs, so the willingness is there. But of 181 calls across all games, only **2 landed on a genuinely informative animation**. Out of 96 large animation events in the data, it inspected 2.1 %. Two calls went to animations that had *zero* transient pixels — where the metadata already said there was nothing to see. Most calls cluster in the first few analysis steps, which looks like exploring a new tool rather than using it when needed.
- **Watch your sandbox timeout.** Our single most informative tool call of the whole run died in a 30-second Python timeout and returned nothing.
- **It does not help everywhere.** In games where the animation is pure movement interpolation, the in-between frames contain no information that isn't in the final frame, and you pay full price for them. Picking the right games matters more than we assumed — and measuring which games those are with a random-walk script does *not* predict what happens under a real agent. We were off by a factor of ten on one game in both directions.

## Conclusion and outlook

So this is a short write-up, and you might wonder why we bothered. The reason is that with the TAAF agent and the attached dataset it can be genuinely difficult to tell what a given variation changed, if anything at all — so we would rather say it out loud, including the parts that didn't work.

We also want to encourage everyone to share their thoughts and ideas even though this is a competition. At least in this Kaggle competition, we are nowhere near 100 % and the grand prize, so there is a lot more to gain from comparing notes than from sitting on them. We will keep the comments updated on what we try next — at least as long as we don't think we are going to win with it ;)

Feel free to ask anything in the comments.

## [717133] Tufa Labs’ Winning Solution for ARC-AGI-3 Milestone 1 — jeroencottaar 2026-08-20
Hey, the licenses are included in the metadata of the kernel and notebook. The notebook is under Apache 2.0 license (the only one possible on Kaggle), the underlying code dataset on MIT license.

## [737617] Sudden increase in top 3 teams? — jakobbrggen 2026-08-26
I also noticed this score increase recently. Though I can't tell for sure of course, I suspect that it has to be through a public new harness or idea which performs very well. This is the only explanation I have for three teams achieving a much better score almost simultaneously. I couldn't find a specific paper or release which was published recently and brought a significant score increase with small open source models (else i would have implemented it already and be up there as well) but I found a couple of interesting ideas mainly on the community leaderboard: https://arcprize.org/leaderboard/community. The one that stands out to me is the Polyphony Agent - ARC (Ruiyang Yu et al.) because it also uses a 27b model under relatively similar circumstances. However this harness was already  presented in the beginning of July, so it might also have nothing to do with the score increase. Hope this helps and if you or anyone else finds anything else which could be the cause i would love to hear about it too.

## [739674] How long do you have to wait to run the notebook? — drpatrickchan 2026-09-07
Our notebook is also being queued for more than a day and still queuing.,,,,

## [740262] Anyone experiencing long queue time? — sirikilohit 2026-09-09
Facing the same issue. Queue times have been pretty long the past couple of days, my notebooks have been in queue for 2 hours now

## [737617] Sudden increase in top 3 teams? — sirikilohit 2026-09-11
Same and also am struggling to decide if any of my enhancements have any effect cuz of this heavy variance. Everything falls inside the variance.

## [741608] Version 29 submission fails with generic "Kaggle Error" despite successful noteb — jeroencottaar 2026-09-16
In general, a Kaggle error in this competition means that your submission runs into an error before starting the games.

## [732854] What are your agents scoring on the 25 public games? — sirikilohit 2026-09-20
It is a good idea tho, isnt it basically the core of this competition? To see how well we can make a model can generalize on unseen tasks, given limited resources? And anyways, competitions like these are how we can actually evaluate how good a model does, ppl have been benchmaxxing a lot.

## [741839] Anyone using Claude Code for this competition? What is your experience? — sirikilohit 2026-09-20
True, claude has been good with the grunt work of checking logs, comparing runs, testing code, etc but has been really bad with coming up with new ideas and performing web searches, giving up at times. But so far it has been good with the grunt work so i use claude.

## [742801] We will not be open-sourcing for the second milestone prize — jeroencottaar 2026-09-23
**TLDR**: We, Tufa Labs, will not be sharing our solution on September 30 for the second milestone prize, since we worry it may not be possible to beat the best of 4000 copies of that solution. We still plan to release our final solution when the competition ends. We encourage other top teams to share their intentions ahead of the milestone as well.

On June 30, we open-sourced our duck harness, claiming the first ARC-AGI3 milestone prize. Apart from the prize itself, part of our motivation was that we believed this would increase the quality of the competition by providing everyone with a good baseline to build on. This has worked out well, with all high-scoring public notebooks now building on this harness. We were not worried that further improvement wasn't possible; we knew that our harness was just the beginning.

With the second milestone on September 30 coming up, we are faced with a similar choice. This time, however, it is not so obvious that big improvements are still possible in the limited time that remains. We worry that if we (or another top ranked team) share our solution there will be 4000 submissions copying this solution, with the winner simply being the luckiest. Minor improvements would not help you; your score would need to beat the best of 4000, and variance is high. This has happened before, such as in this year's AIMO competition.

So we've come to the conclusion that we will not be participating in the second milestone prize, and so will not open-source our solution. We remain fully committed to sharing our final solution when the competition ends.

We understand that other top teams may choose differently. Either way, we'd like to encourage all top teams to clarify their plans; this also helps lower-ranked teams to know whether to share or not.

## [742801] We will not be open-sourcing for the second milestone prize — lordhansolo 2026-09-26
Thanks for letting us know.

I’ll share my solution publicly if I make the top 3 in Milestone 2 among participants who have indicated their willingness to share their solutions.

## [742801] We will not be open-sourcing for the second milestone prize — lordhansolo 2026-09-26
It looks like Tufa Labs just found a big improvement ;)

## [742935]  Who will open-sourcing for the second milestone prize? — lordhansolo 2026-09-26
I’ll share my solution publicly if I make the top 3 in Milestone 2 among participants who have indicated their willingness to share their solutions.

## [742935]  Who will open-sourcing for the second milestone prize? — dfranzen 2026-09-27
Hi y’all!

After my unexpected jump to second place today, I thought I’d share my intentions on publishing too.

[Sep 27, 19:10 CEST] If I finish Milestone 2 in first place among teams willing to open-source their solution, I’ll definitely share mine. If I’m second or third among those teams, I probably will too. Otherwise, I’ll wait until the end of the competition.

[Sep 29, 10:30 CEST] To keep you updated, my plan has not changed. I will definitely open-source if I manage to stay at first place among those who wish to publish. If I end up at 2nd or 3rd place - not sure yet, but probably too.

[Sep 30, 00:50 CEST] I just published my solution for milestone 2. Here it is:

Write-up: https://www.kaggle.com/writeups/dfranzen/arc-agi-3-milestone-2

Notebook: https://www.kaggle.com/code/dfranzen/arc-agi-3-milestone-2-solution

(I had to cut the demo run short to 25 minutes because I had no kaggle compute left. I will do a full rerun of the notebook on the 25 public games next week.

## [742801] We will not be open-sourcing for the second milestone prize — jeroencottaar 2026-09-28
No, we'd just hope their solution is very different from ours, and that we can learn from it...

I guess we could look at their solution, then choose to open-source if it's similar to ours. But we won't.

## [742935]  Who will open-sourcing for the second milestone prize? — threerabbits 2026-09-28
I haven’t decided yet whether I’ll open-source my solution for the second milestone, but I’ll let everyone know my final decision here by September 29, 23:59 Taiwan time (UTC+8).

Update: Given the complexity of the process, I’ve decided not to open-source my solution for the second milestone.

## [743952] unpopular opinion — jeroencottaar 2026-09-28
The hidden set numbers are usually revealed for *all* submissions at the end of the competition.

## [742935]  Who will open-sourcing for the second milestone prize? — threerabbits 2026-09-29
Looking forward to seeing what interesting things others share!

## [744545] Can some teams regret not sharing for 2nd milestone prize? — threerabbits 2026-10-01
I regret it so much 🫠

## [744792] Comparing the Milestone 2 winning solutions — threerabbits 2026-10-01
I'm excited to see how high a score people can achieve by combining these three winning notebooks!

## [744792] Comparing the Milestone 2 winning solutions — jeroencottaar 2026-10-01
Great overview, thanks for putting this together! Saves us all a bunch of tokens...

## [744792] Comparing the Milestone 2 winning solutions — sirikilohit 2026-10-01
Thanks a lot for putting this together, saves me a lot of time. 
Looks like I took a wrong turn with the context vs concurrency tradeoff. For the most part, I thought the decode throughput was the bottleneck, so I kept the concurrency high. The logs showed me that the kv pool sat somewhere between 91-97% full and requests queued for cache space, so the memory was the actual limit but I realized this a bit too late. Also, the fp8 kv was implemented yesterday and i spent the free memory on history (the trims moved from 37k->27k to 57k->45k). I guess this alone took the score from 14.5 to 22.5.

## [744792] Comparing the Milestone 2 winning solutions — sirikilohit 2026-10-01
I didnt really compare the kv formats. fp8 was what pennyroyal's flash next receipe uses, and it halved the memory vs bf16, which i needed for longer history. I havent tried nvfp4 kv. For the nll check: at short contexts, it might not show what happens at 60k-100k tokens where we actually run. A token-matched run with only kv dtype changed would settle it. Also, my cleared levels used a median of around 0.8x the baseline actions (64% at or under the baseline). Some harness changes that helped were simply to not mislead the agent. (For ex: UNDO instead of ACTION7, "level restarted" instead of "game over",  removing lines that tell the agent to ignore the budget bar, etc etc,.)

## [744843] Vibe coding(using frontier models via api)= cheating? — sirikilohit 2026-10-01
I guess that depends on the licensing terms of the frontier model you wish to distil from. It's good to clear it up with the competition hosts before doing that.

## [744995] Run completed in 4 hours — sirikilohit 2026-10-02
Same here. I just submitted a notebook. It ran for 2 hours and completed the run.

## [744995] Run completed in 4 hours — sirikilohit 2026-10-02
Im guessing that its the same thing. 7 hours up, but my gemma competition notebook has been running fine though.