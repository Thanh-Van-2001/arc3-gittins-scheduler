"""Faithful gate simulation: the real harness re-prices and hands over a slot ONLY at context trims.

Measured on Franzen's demo transcripts: first trim after ~68k generated tokens (52k-96k), then about
every ~35k. Games that have never trimmed sit in the 'untrimmed band' and are always admitted first,
in dispatch order. A level clear is NOT a decision point. Ten slots run in parallel; we simulate the
pooled budget with per-game trim clocks.
"""
import json

import numpy as np
import pandas as pd

from costmodel import fit
from gittins import GittinsTables
from sim import franzen_priority, game_score, sample_world

df = pd.read_csv("level_attempts.csv"); M = fit(df)
nl_pool = df.groupby("game").n_levels.first().values
fr = [r for r, a in M["a"].items() if np.exp(a) < 0.35]
dd = df[df.completed & (df.actions > 0) & df.run.isin(fr)]; rp = (dd.baseline / dd.actions).values
re_ = float(np.mean([M["a"][r] for r in fr])); eff = float(np.mean(np.minimum(1, rp ** 2)))
G, B, SLOTS, Q = 110, 19.4e6, 10, 2000.0


def run(world, policy, first_trim, trim_every, rng, tables=None):
    nl = world.n_levels
    level = np.zeros(G, int); t_level = np.zeros(G); done = np.zeros(G, bool)
    cleared = [[] for _ in range(G)]
    gen = np.zeros(G)                                   # generated tokens per game (trim clock)
    next_trim = first_trim * np.exp(rng.normal(0, 0.2, G))
    trimmed = np.zeros(G, bool)
    slots = list(range(SLOTS)); queue_fresh = list(range(SLOTS, G))   # dispatch order
    running = list(range(SLOTS))
    spent = 0.0

    def price(g, frac):
        if policy == "franzen":
            return franzen_priority(level[g] + 1, t_level[g] / 1000 * 1.5, t_level[g], int(nl[g]), min(1.0, (1 - frac) / 0.2))
        w = tables.posterior(list(enumerate(cleared[g])), int(level[g]), t_level[g])
        return tables.index(int(nl[g]), int(level[g]), t_level[g], w)

    waiting = {}                                        # trimmed games waiting for a slot -> price
    while spent < B and running:
        # advance every running game by one quantum (parallel streams share the budget)
        for g in list(running):
            if spent >= B: break
            gen[g] += Q; t_level[g] += Q; spent += Q
            if t_level[g] >= world.cost[g][level[g]]:
                cleared[g].append(world.cost[g][level[g]]); level[g] += 1; t_level[g] = 0.0
                if level[g] >= nl[g]:
                    done[g] = True; running.remove(g); continue
            if gen[g] >= next_trim[g]:                  # context trim: the only handover point
                trimmed[g] = True; next_trim[g] = gen[g] + trim_every * np.exp(rng.normal(0, 0.2))
                running.remove(g); waiting[g] = price(g, spent / B)
        # fill free slots: untrimmed band first (dispatch order), then highest price
        while len(running) < SLOTS and (queue_fresh or waiting):
            if queue_fresh:
                running.append(queue_fresh.pop(0))
            else:
                g = max(waiting, key=waiting.get); waiting.pop(g); running.append(g)
    return float(np.mean([game_score(level[g], nl[g], world.ratio[g]) for g in range(G)]))


if __name__ == "__main__":
    out = {}
    for shift in [0.85]:
        tab = GittinsTables(M, re_, shift=shift, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)
        for first, every in [(68_000, 35_000), (40_000, 30_000), (95_000, 50_000)]:
            f, g = [], []
            for sd in range(6):
                w = sample_world(np.random.default_rng(1200 + sd), G, M, nl_pool, rp, re_, shift)
                f.append(run(w, "franzen", first, every, np.random.default_rng(sd)))
                g.append(run(w, "gittins", first, every, np.random.default_rng(sd), tab))
            d = np.array(g) - np.array(f)
            out[f"{first}/{every}"] = dict(franzen=float(np.mean(f)), gittins=float(np.mean(g)), diff=float(d.mean()), se=float(d.std(ddof=1) / np.sqrt(len(d))))
            print(f"shift {shift} first_trim {first//1000}k every {every//1000}k: franzen {np.mean(f):5.1f}  gittins {np.mean(g):5.1f}  diff {d.mean():+5.2f} ± {d.std(ddof=1)/np.sqrt(len(d)):.2f}", flush=True)
    json.dump(out, open("faithful.json", "w"), indent=1)
