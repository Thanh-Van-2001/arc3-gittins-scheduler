"""Deterministic move-budget meter for ARC-AGI-3 frames (CPU only, no game knowledge).

Most games show the remaining move budget as a bar in the outer border that loses cells as actions
are spent and refills when the level restarts. The model reads it by eye and often miscounts; in
Franzen's demo 4 of 5 deaths were budget deaths. This meter tracks, per level attempt, the colour
counts in the border band and reports the colour that shrinks most steadily, its rate per action and
the implied number of actions left. It reports nothing unless the pattern is clear.
"""
from __future__ import annotations

import numpy as np

BORDER = 4
MIN_STEPS = 3          # actions observed in this attempt before reporting
MIN_DROP = 3           # cells the bar must have lost
MIN_START = 12         # bar length at the start of the attempt (cells)


def border_counts(grid) -> dict[int, int]:
    g = np.asarray(grid)
    mask = np.zeros(g.shape, bool)
    mask[:BORDER, :] = mask[-BORDER:, :] = mask[:, :BORDER] = mask[:, -BORDER:] = True
    vals, cnt = np.unique(g[mask], return_counts=True)
    return {int(v): int(c) for v, c in zip(vals, cnt)}


class BudgetMeter:
    def __init__(self):
        self.reset()

    def reset(self):
        """Call at the start of every level attempt (new level, death, or explicit RESET)."""
        self.series: list[dict[int, int]] = []

    def observe(self, grid) -> None:
        self.series.append(border_counts(grid))

    def estimate(self):
        """(colour, cells_left, cells_per_action, actions_left) or None if no clear bar."""
        if len(self.series) - 1 < MIN_STEPS:
            return None
        best = None
        colours = set().union(*self.series)
        for c in colours:
            seq = np.array([s.get(c, 0) for s in self.series])
            # a refill (pickup) restarts the bar: measure only the segment since the last increase
            ups = np.nonzero(np.diff(seq) > 0)[0]
            seg = seq[ups[-1] + 1:] if len(ups) else seq
            m = len(seg) - 1
            if m < MIN_STEPS:
                continue
            start, now = seg[0], seg[-1]
            if start < MIN_START or start - now < MIN_DROP:
                continue
            rate = (start - now) / m
            steps_with_drop = int((np.diff(seg) < 0).sum())
            if steps_with_drop < max(2, int(0.25 * m * min(1.0, rate))):
                continue
            score = (start - now) * steps_with_drop
            if best is None or score > best[0]:
                best = (score, c, int(now), float(rate))
        if best is None:
            return None
        _, c, now, rate = best
        return dict(colour=c, cells_left=now, cells_per_action=round(rate, 3), actions_left=int(now / rate) if rate > 0 else None)

    def describe(self) -> str:
        e = self.estimate()
        if not e or e["actions_left"] is None:
            return ""
        return (f"Budget meter (harness estimate from the border bar, colour {e['colour']}): "
                f"{e['cells_left']} cells left, losing ~{e['cells_per_action']:.2f} per action, "
                f"so roughly {e['actions_left']} actions remain in this attempt. Approximate.")
