"""Bayesian Gittins-style index for allocating generation tokens across ARC-AGI-3 games.

Model (costmodel.py): the tokens needed to clear level l of game g are log-normal with a latent
game difficulty u_g shared by all its levels. The index of a game is the reward rate lambda* at which
continuing to work on it (with the option to stop at any time) breaks even:

    Q_lambda(l, t) = h(l,t) * (R_l + V_lambda(l+1, 0)) + (1 - h(l,t)) * V_lambda(l, t+q) - lambda * q
    V_lambda       = max(0, Q_lambda)

computed by backward induction for each particle u_k of the game-difficulty posterior (the
continuation assumes u is known, a QMDP-style approximation); the index is the lambda at which the
posterior-weighted root value sum_k w_k Q_lambda^k(l, t) crosses zero. The posterior w_k combines
the prior on u with the costs of levels already cleared and survival of the current level.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

K = 41
X = np.linspace(-3.5, 3.5, K)
PRIOR = stats.norm.pdf(X)
PRIOR /= PRIOR.sum()


class GittinsTables:
    def __init__(self, model, run_effect, shift=0.0, q=4000.0, tmax=800_000.0,
                 lambdas=None, n_levels_range=range(1, 11), eff=0.85, horizon_levels=None):
        self.m = model
        self.mu = model["mu"] + run_effect + shift
        self.b = np.asarray(model["b"])
        self.s, self.su = model["s"], model["su"]
        self.q = q
        self.T = int(tmax // q)
        self.lambdas = np.geomspace(1e-7, 1e-2, 80) if lambdas is None else lambdas
        self.eff = eff
        self.u = self.su * X  # particle difficulties
        self.Q = {}  # n_levels -> array (L, K, n_level, T)
        for n in n_levels_range:
            self.Q[n] = self._solve(n)

    def logc_mean(self, level_idx):
        lv = min(level_idx + 1, len(self.b))
        return self.mu + self.b[lv - 1] + self.u  # (K,)

    def _hazards(self, n):
        t = np.arange(self.T + 1) * self.q
        logt = np.log(np.maximum(t, 1.0))
        H = np.zeros((n, K, self.T))
        for l in range(n):
            m = self.logc_mean(l)[:, None]
            S = stats.norm.sf((logt[None, :] - m) / self.s)
            S[:, 0] = 1.0
            H[l] = np.clip((S[:, :-1] - S[:, 1:]) / np.maximum(S[:, :-1], 1e-300), 0.0, 1.0)
        return H

    def _solve(self, n):
        H = self._hazards(n)
        R = np.arange(1, n + 1) / (n * (n + 1) / 2) * 100.0 * self.eff  # game-score points per level
        Lm = len(self.lambdas)
        Q = np.zeros((Lm, K, n, self.T), dtype=np.float32)
        V_next0 = np.zeros((Lm, K))  # V(l+1, 0)
        for l in range(n - 1, -1, -1):
            V = np.zeros((Lm, K))  # V(l, T) = 0: give up past tmax
            gain = R[l] + V_next0  # (Lm, K)
            for i in range(self.T - 1, -1, -1):
                h = H[l, :, i][None, :]
                qv = h * gain + (1 - h) * V - self.lambdas[:, None] * self.q
                Q[:, :, l, i] = qv
                V = np.maximum(0.0, qv)
            V_next0 = V
        return Q

    def posterior(self, cleared, level, t):
        """cleared: list of (level_idx, cost); level: current level idx; t: tokens on it."""
        logw = np.log(PRIOR)
        for l, c in cleared:
            logw += stats.norm.logpdf((np.log(c) - self.logc_mean(l)) / self.s)
        if t > 0:
            logw += stats.norm.logsf((np.log(t) - self.logc_mean(level)) / self.s)
        w = np.exp(logw - logw.max())
        return w / w.sum()

    def index(self, n, level, t, w):
        i = min(int(t // self.q), self.T - 1)
        qroot = self.Q[n][:, :, level, i] @ w  # (Lm,) decreasing in lambda
        pos = np.where(qroot > 0)[0]
        if len(pos) == 0:
            return 0.0
        j = pos[-1]
        if j + 1 >= len(self.lambdas):
            return float(self.lambdas[-1])
        # linear interpolation of the zero crossing in log-lambda
        a, b = qroot[j], qroot[j + 1]
        la, lb = np.log(self.lambdas[j]), np.log(self.lambdas[j + 1])
        return float(np.exp(la + (lb - la) * a / (a - b)))


def make_gittins(tables: GittinsTables):
    cache = {}  # game -> (level, t, index); only the game just worked on changes state

    def pol(st, world, active, frac, ps):
        best, bg = -1.0, None
        for g in active:
            lv, t = int(st.level[g]), float(st.t[g])
            hit = cache.get(g)
            if hit is None or hit[0] != lv or hit[1] != t:
                n = int(world.n_levels[g])
                w = tables.posterior(list(enumerate(st.cleared_costs[g])), lv, t)
                cache[g] = (lv, t, tables.index(n, lv, t, w))
            idx = cache[g][2]
            if idx > best:
                best, bg = idx, g
        return bg
    return pol
