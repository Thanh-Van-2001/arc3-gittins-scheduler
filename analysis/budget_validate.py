"""Validate the budget meter offline: random play on the 25 public games with the real engine.
For every attempt that ends in a death, compare the meter's 'actions left' at each step with the
true number of actions remaining before that death. Also measure false alarms on attempts that do
not end in death (meter predicts death within k actions but none happens)."""
import json
import random

import numpy as np

import arc_agi
from arcengine import GameAction, GameState
from budget_meter import BudgetMeter
from budget_probe import ENV_DIR, frame_of


def run(game_id, steps=400, seed=0):
    rng = random.Random(seed)
    arcade = arc_agi.Arcade(operation_mode=arc_agi.OperationMode.OFFLINE, environments_dir=ENV_DIR)
    env = arcade.make(game_id)
    obs = env.step(GameAction.RESET)
    meter = BudgetMeter(); meter.observe(frame_of(obs))
    attempts, cur, level = [], [], obs.levels_completed
    for t in range(steps):
        acts = [a for a in (obs.available_actions or []) if a != 0]
        if not acts:
            break
        a = GameAction.from_id(rng.choice(acts))
        obs = env.step(a, data={"x": rng.randrange(64), "y": rng.randrange(64)} if a.value == 6 else {})
        meter.observe(frame_of(obs))
        cur.append(meter.estimate())
        died = obs.state == GameState.GAME_OVER
        if died or obs.levels_completed != level:
            attempts.append(dict(estimates=cur, died=died))
            cur = []
            level = obs.levels_completed
            if died:
                obs = env.step(GameAction.RESET)
            meter.reset(); meter.observe(frame_of(obs))
    if cur:
        attempts.append(dict(estimates=cur, died=False))
    return attempts


if __name__ == "__main__":
    arcade = arc_agi.Arcade(operation_mode=arc_agi.OperationMode.OFFLINE, environments_dir=ENV_DIR)
    errs, rel, coverage, false_alarm, games_with_deaths, hazard_deaths = [], [], [], [], 0, []
    per_game = {}
    for gid in sorted(e.game_id for e in arcade.available_environments):
        ge, gn = [], 0
        for seed in range(2):
            try:
                atts = run(gid, seed=seed)
            except Exception as ex:
                print(gid[:4], "ERROR", repr(ex)[:120]); break
            for a in atts:
                est = a["estimates"]
                last = est[-1] if est else None
                budget_death = bool(a["died"] and last and last["cells_left"] <= max(2, 3 * last["cells_per_action"]))
                if a["died"] and not budget_death:
                    hazard_deaths.append(gid[:4])
                if budget_death and len(est) >= 5:
                    gn += 1
                    for i, e in enumerate(est):
                        true_left = len(est) - 1 - i
                        coverage.append(e is not None)
                        if e is not None and e["actions_left"] is not None:
                            errs.append(e["actions_left"] - true_left); ge.append(abs(e["actions_left"] - true_left))
                            rel.append(abs(e["actions_left"] - true_left) / max(5, true_left))
                elif not a["died"]:
                    for i, e in enumerate(est):
                        if e is not None and e["actions_left"] is not None and i + 10 < len(est):
                            false_alarm.append(e["actions_left"] <= 3)
        per_game[gid[:4]] = dict(deaths=gn, median_abs_err=float(np.median(ge)) if ge else None)
        games_with_deaths += gn > 0
    errs = np.array(errs)
    print("hazard (non-budget) deaths excluded:", len(hazard_deaths))
    print("games with budget deaths:", games_with_deaths, "| meter coverage on budget-death attempts: %.0f%%" % (100 * np.mean(coverage)))
    print("actions-left error: median %.1f, MAE %.1f, median relative %.0f%%" % (np.median(errs), np.mean(np.abs(errs)), 100 * np.median(rel)))
    print("false 'death within 3' alarms on surviving attempts: %.1f%%" % (100 * np.mean(false_alarm) if false_alarm else 0))
    print(per_game)
    json.dump(per_game, open(r"D:\arc3_paper\results\budget_validate.json", "w"), indent=1)
