"""Exercise the exact code paths the Gittins patch touches on a real ToolAgent object:
level-transition cost recording -> context-trim handover -> priority gate pricing."""
import os, sys, time, threading
os.environ.update({"ARC3_PRIORITY_POLICY": "gittins", "ARC3_MAX_ACTIVE_STREAMS": "2",
                   "ARC3_PRIORITY_REFRESH_QUEUE": "1", "ARC3_PRIORITY_SCORE_NORMALIZATION": "1",
                   "ARC3_PRIORITY_TAIL_LOOKUP": "remaining", "ARC3_PRIORITY_TAIL_FADE": "1",
                   "ARC3_PRIORITY_TAIL_FADE_FRACTION": "0.2"})
sys.path.insert(0, r"D:\arc3_paper\harness\src\ARC3-Inference")
import inference.agent.tool_agent as ta

class FakeGame: number_of_levels = 7
class FakeSession:
    game = FakeGame()
    def step(self, *a, **k): pass

def make_agent(name):
    ag = object.__new__(ta.ToolAgent)
    ag.__dict__.update(dict(_context_was_trimmed=False, _actions_at_level_start=0, _tokens_at_level_start=0,
                            _session_generated_tokens=0, _progress_pace=ta.ProgressPace(), _pace_last_completed_level=0,
                            _cleared_level_costs=[], _priority_current=0, _priority_next=0, _diag_name=name,
                            _step_env_callback=FakeSession().step, _kept_functions={}, _game_elapsed_seconds=None))
    return ag

gate = ta._priority_gate()
gate.configure_clock(time.monotonic(), time.monotonic() + 3600)
easy, hard = make_agent("easy"), make_agent("hard")
for ag in (easy, hard):
    gate.acquire(ta._PRIORITY_UNTRIMMED_BASE)

def clear_level(ag, tokens, new_level):
    ag._session_generated_tokens += tokens
    ag._last_step_summary = {"level": new_level, "level_transition": True, "end_action_num": 10 * new_level}
    try:
        ag._update_summarized_knowledge_from_step_summary()
    except AttributeError as e:  # unrelated world-model bookkeeping on a bare object
        # the cost record and level-start counters are updated before that bookkeeping runs
        print("  (ignored unrelated attribute:", e, ")")
        ag._tokens_at_level_start = ag._session_generated_tokens
        ag._actions_at_level_start = 10 * new_level

clear_level(easy, 6000, 2); clear_level(easy, 9000, 3)
clear_level(hard, 160000, 2); clear_level(hard, 240000, 3)
print("easy costs", easy._cleared_level_costs, "hard costs", hard._cleared_level_costs)
assert easy._cleared_level_costs == [(1, 6000), (2, 9000)], easy._cleared_level_costs
assert hard._cleared_level_costs == [(1, 160000), (2, 240000)]

prices = {}
for ag in (easy, hard):
    ag._session_generated_tokens += 20000
    ag._last_step_summary = {"level": 3, "end_action_num": 35}
    ag._context_was_trimmed = True
    t = threading.Thread(target=ag._maybe_handover, daemon=True); t.start(); t.join(5)
    assert not t.is_alive(), "handover blocked"
    prices[ag._diag_name] = ag._priority_current
print("handover priorities", prices)
assert prices["easy"] > prices["hard"], "easy game must outrank the hard one"
assert all(1 <= p < ta._PRIORITY_BAND for p in prices.values())
print("OK")
