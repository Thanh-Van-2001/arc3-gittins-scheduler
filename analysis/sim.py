"""Trace-calibrated simulator for allocating a fixed generation budget across ARC-AGI-3 games.

Each simulated game has n levels with token costs drawn from the fitted censored log-normal model
(costmodel.py). A policy repeatedly picks which game receives the next quantum of generated
tokens. A level clears once its accumulated tokens reach its (hidden) cost. Scoring follows the
official arc_agi scorecard: per-level min(115, 100 * ratio^2), weighted by level index, capped at
the completed-weight share, averaged over games.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

# Franzen's open-sourced scheduler (Apache-2.0), ported verbatim for comparison.
TAIL_REMAINING = {n: (8.0,) * (n - 3) + (7.0, 5.0, 0.0) for n in range(6, 11)}


def franzen_priority(level, actions, tokens, total_levels, tail_fraction):
    level = max(1, level)
    n = min(10, max(6, total_levels))
    efficiency = (25.0 / (25.0 + actions)) ** 2
    current = level * efficiency * 55.0 / (n * (n + 1) / 2)
    tail = TAIL_REMAINING[n][min(n, level) - 1] * min(1.0, max(0.0, tail_fraction))
    chance = 0.25 * 0.5 ** ((actions / 115.0) ** 2) + 0.75 * 0.5 ** ((tokens / 62000.0) ** 2)
    return (current + tail) * chance


@dataclass
class World:
    n_levels: np.ndarray           # (G,)
    cost: list                     # per game: array of level costs (tokens)
    ratio: list                    # per game: array of baseline/actions ratios if cleared
    u: np.ndarray                  # true game effects (log scale)


def sample_world(rng, G, model, n_levels_pool, ratio_pool, run_effect, shift=0.0, t_df=None, su_scale=1.0, s_scale=1.0):
    mu, b, s, su = model["mu"], model["b"], model["s"] * s_scale, model["su"] * su_scale
    u = rng.normal(shift, su, size=G)
    nl = rng.choice(n_levels_pool, size=G)
    cost, ratio = [], []
    for g in range(G):
        lv = np.minimum(np.arange(1, nl[g] + 1), len(b))
        noise = (rng.standard_t(t_df, size=nl[g]) * np.sqrt((t_df - 2) / t_df) if t_df else rng.normal(0, 1, size=nl[g])) * s
        logc = mu + run_effect + b[lv - 1] + u[g] + noise
        cost.append(np.exp(logc))
        ratio.append(rng.choice(ratio_pool, size=nl[g]))
    return World(nl, cost, ratio, u)


def game_score(levels_done, n, ratios):
    w = np.arange(1, n + 1, dtype=float)
    s = np.zeros(n)
    s[:levels_done] = np.minimum(115.0, 100.0 * ratios[:levels_done] ** 2)
    score = (w * s).sum() / w.sum()
    cap = w[:levels_done].sum() / w.sum() * 100.0
    return min(score, cap)


@dataclass
class State:
    level: np.ndarray       # 0-based current level index (== levels cleared)
    t: np.ndarray           # tokens spent on the current level
    done: np.ndarray        # game fully cleared
    cleared_costs: list = field(default_factory=list)


def simulate(world, budget, policy, quantum=4000.0, actions_per_ktok=1.5, rng=None, policy_state=None, lease=0.0, first_chunk=0.0):
    """lease: tokens a game keeps its slot after admission (harness hands over only at context
    trims); first_chunk: every game first runs this many tokens in dispatch order (the harness's
    untrimmed band) before any priority-based admission."""
    G = len(world.n_levels)
    st = State(np.zeros(G, int), np.zeros(G), np.zeros(G, bool), [[] for _ in range(G)])
    spent = 0.0
    held, held_left = None, 0.0
    first_left = np.full(G, first_chunk)
    while spent < budget:
        active = np.where(~st.done)[0]
        if len(active) == 0:
            break
        fresh = [g for g in active if first_left[g] > 0]
        if fresh:
            g = fresh[0]
            first_left[g] -= quantum
        elif held is not None and held_left > 0 and not st.done[held]:
            g = held
        else:
            g = policy(st, world, active, spent / budget, policy_state)
            held, held_left = g, lease
        if g is None:
            break
        held_left -= quantum
        q = min(quantum, budget - spent)
        st.t[g] += q
        spent += q
        lv = st.level[g]
        c = world.cost[g][lv]
        if st.t[g] >= c:
            st.cleared_costs[g].append(c)
            st.level[g] += 1
            st.t[g] = 0.0  # leftover of the quantum is lost (small)
            held_left = 0.0  # a level clear is a natural point to re-decide
            first_left[g] = min(first_left[g], 0.0)
            if st.level[g] >= world.n_levels[g]:
                st.done[g] = True
    scores = [game_score(st.level[g], world.n_levels[g], world.ratio[g]) for g in range(G)]
    return float(np.mean(scores)), st


# ---------------- policies ----------------

def make_equal(G, budget):
    quota = budget / G
    used = np.zeros(G)

    def pol(st, world, active, frac, ps):
        # round-robin over games that still have quota
        cand = [g for g in active if used[g] < quota]
        if not cand:
            return None
        g = min(cand, key=lambda g: used[g])
        used[g] += 4000.0
        return g
    return pol


def make_franzen(actions_per_ktok=1.5, fade=0.2):
    def pol(st, world, active, frac, ps):
        remaining = 1.0 - frac
        tail_fraction = min(1.0, remaining / fade)
        best, bg = -1.0, None
        for g in active:
            a = st.t[g] / 1000.0 * actions_per_ktok
            p = franzen_priority(st.level[g] + 1, a, st.t[g], int(world.n_levels[g]), tail_fraction)
            if p > best:
                best, bg = p, g
        return bg
    return pol


def oracle_score(world, budget):
    """Clairvoyant upper bound: knows every level cost. Precedence-constrained knapsack solved by
    greedy on the upper concave hull of each game's (cumulative cost, cumulative value) curve —
    exact up to the last fractional item."""
    G = len(world.n_levels)
    items = []  # (ratio, cost, game, depth)
    for g in range(G):
        n = world.n_levels[g]
        cc = np.concatenate([[0.0], np.cumsum(world.cost[g])])
        vals = [game_score(d, n, world.ratio[g]) / G for d in range(n + 1)]
        # upper concave hull over depths
        hull = [0]
        for d in range(1, n + 1):
            while len(hull) >= 2:
                d1, d2 = hull[-2], hull[-1]
                if (vals[d2] - vals[d1]) * (cc[d] - cc[d1]) <= (vals[d] - vals[d1]) * (cc[d2] - cc[d1]):
                    hull.pop()
                else:
                    break
            hull.append(d)
        for d1, d2 in zip(hull[:-1], hull[1:]):
            dc, dv = cc[d2] - cc[d1], vals[d2] - vals[d1]
            if dv > 0:
                items.append((dv / dc, dc, dv))
    items.sort(reverse=True)
    left, total = budget, 0.0
    for r, dc, dv in items:
        if dc <= left:
            left -= dc
            total += dv
        else:
            break
    return total
