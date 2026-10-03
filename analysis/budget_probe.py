"""Probe the 25 public games for a move-budget bar: play random valid actions offline and look for a
colour whose cell count in the outer border shrinks steadily with actions and refills on death/reset."""
import json
import os
import random
import sys

import numpy as np

import arc_agi
from arcengine import GameAction, GameState

ENV_DIR = r"D:\arc3_paper\data\comp\environment_files"
BORDER = 4


def frame_of(obs):
    arr = np.array(obs.frame)
    return arr[-1] if arr.ndim == 3 else arr


def border_counts(grid):
    h, w = grid.shape
    mask = np.zeros_like(grid, bool)
    mask[:BORDER, :] = mask[-BORDER:, :] = mask[:, :BORDER] = mask[:, -BORDER:] = True
    vals, cnt = np.unique(grid[mask], return_counts=True)
    return dict(zip(vals.tolist(), cnt.tolist()))


def play(game_id, steps=150, seed=0):
    rng = random.Random(seed)
    arcade = arc_agi.Arcade(operation_mode=arc_agi.OperationMode.OFFLINE, environments_dir=ENV_DIR)
    env = arcade.make(game_id)
    obs = env.step(GameAction.RESET)
    trace = []
    for t in range(steps):
        acts = [a for a in (obs.available_actions or []) if a not in (0,)]
        if not acts:
            break
        a = GameAction.from_id(rng.choice(acts)) if hasattr(GameAction, "from_id") else GameAction(rng.choice(acts))
        data = {"x": rng.randrange(64), "y": rng.randrange(64)} if a.value == 6 else {}
        obs = env.step(a, data=data)
        g = frame_of(obs)
        trace.append(dict(t=t, state=str(obs.state), level=obs.levels_completed, border=border_counts(g)))
        if obs.state in (GameState.GAME_OVER,):
            trace[-1]["death"] = True
            obs = env.step(GameAction.RESET)
    return trace


def bar_candidates(trace):
    """Colours whose border count moves monotonically down between deaths for >= 8 steps."""
    out = {}
    colours = set().union(*[set(x["border"]) for x in trace]) if trace else set()
    for c in colours:
        seq = [x["border"].get(c, 0) for x in trace]
        deaths = [i for i, x in enumerate(trace) if x.get("death")]
        seg_start = 0
        best = None
        for end in deaths + [len(seq)]:
            s = seq[seg_start:end]
            if len(s) >= 8:
                d = np.diff(s)
                if (d <= 0).all() and s[0] - s[-1] >= 4:
                    rate = (s[0] - s[-1]) / len(s)
                    best = dict(start=s[0], end=s[-1], steps=len(s), cells_per_action=round(rate, 2))
            seg_start = end + 1
        if best:
            out[c] = best
    return out


if __name__ == "__main__":
    arcade = arc_agi.Arcade(operation_mode=arc_agi.OperationMode.OFFLINE, environments_dir=ENV_DIR)
    ids = [e.game_id for e in arcade.available_environments]
    res = {}
    for gid in sorted(ids):
        try:
            tr = play(gid)
            cands = bar_candidates(tr)
            deaths = sum(1 for x in tr if x.get("death"))
            res[gid] = dict(deaths=deaths, steps=len(tr), bars=cands)
            print(gid[:4], "deaths", deaths, "steps", len(tr), "bar candidates", cands)
        except Exception as e:
            print(gid[:4], "ERROR", repr(e)[:150])
    json.dump(res, open(r"D:\arc3_paper\results\budget_probe.json", "w"), indent=1)
