"""Censored log-normal model of the generated-token cost of clearing an ARC-AGI-3 level.

    log T[r,g,l] = mu + b_level[l] + a_run[r] + u_game[g] + eps,   eps ~ N(0, s^2)
    u_game ~ N(0, su^2)   (shared by every level of a game, across runs)

T is the number of generated tokens the agent spends on level l before clearing it. Attempts the
run abandoned (time ran out) are right-censored at the tokens already spent. The game effect is
integrated out with Gauss-Hermite quadrature; runs are fixed effects (different models/configs).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize, stats

GH_X, GH_W = np.polynomial.hermite_e.hermegauss(40)  # probabilists' Hermite: weight exp(-x^2/2)
GH_W = GH_W / GH_W.sum()
MAX_LEVEL = 6  # levels >= MAX_LEVEL share one coefficient (few observations)


def design(df: pd.DataFrame):
    d = df[df.tokens > 0].copy()
    d["lv"] = d.level.clip(upper=MAX_LEVEL)
    runs = sorted(d.run.unique())
    games = sorted(d.game.unique())
    d["ri"] = d.run.map({r: i for i, r in enumerate(runs)})
    d["gi"] = d.game.map({g: i for i, g in enumerate(games)})
    return d, runs, games


def unpack(theta, n_runs):
    mu = theta[0]
    b = np.concatenate([[0.0], theta[1:MAX_LEVEL]])          # level 1 is the reference
    a = np.concatenate([[0.0], theta[MAX_LEVEL:MAX_LEVEL + n_runs - 1]])  # run 0 is the reference
    log_s, log_su = theta[-2], theta[-1]
    return mu, b, a, np.exp(log_s), np.exp(log_su)


def negloglik(theta, d, n_runs, n_games):
    mu, b, a, s, su = unpack(theta, n_runs)
    y = np.log(d.tokens.values)
    m = mu + b[d.lv.values - 1] + a[d.ri.values]
    done = d.completed.values.astype(bool)
    # per-observation log-likelihood at each quadrature node (obs x nodes)
    z = (y[:, None] - m[:, None] - su * GH_X[None, :]) / s
    ll = np.where(done[:, None], stats.norm.logpdf(z) - np.log(s) - y[:, None], stats.norm.logsf(z))
    # sum within game, then integrate over the game effect
    G = np.zeros((n_games, len(GH_X)))
    np.add.at(G, d.gi.values, ll)
    mx = G.max(axis=1, keepdims=True)
    return -(mx[:, 0] + np.log((np.exp(G - mx) * GH_W[None, :]).sum(axis=1))).sum()


def fit(df: pd.DataFrame):
    d, runs, games = design(df)
    n_runs, n_games = len(runs), len(games)
    theta0 = np.zeros(1 + (MAX_LEVEL - 1) + (n_runs - 1) + 2)
    theta0[0] = np.log(d.tokens.median())
    theta0[-2], theta0[-1] = np.log(1.0), np.log(0.5)
    res = optimize.minimize(negloglik, theta0, args=(d, n_runs, n_games), method="L-BFGS-B")
    mu, b, a, s, su = unpack(res.x, n_runs)
    # posterior mean of each game's effect (for diagnostics / difficulty ranking)
    y = np.log(d.tokens.values)
    m = mu + b[d.lv.values - 1] + a[d.ri.values]
    done = d.completed.values.astype(bool)
    z = (y[:, None] - m[:, None] - su * GH_X[None, :]) / s
    ll = np.where(done[:, None], stats.norm.logpdf(z), stats.norm.logsf(z))
    G = np.zeros((n_games, len(GH_X)))
    np.add.at(G, d.gi.values, ll)
    post = np.exp(G - G.max(axis=1, keepdims=True)) * GH_W[None, :]
    post /= post.sum(axis=1, keepdims=True)
    u_hat = (post * (su * GH_X)[None, :]).sum(axis=1)
    return dict(mu=mu, b=b, a=dict(zip(runs, a)), s=s, su=su, u=dict(zip(games, u_hat)),
                nll=res.fun, converged=bool(res.success), n=len(d), n_runs=n_runs, n_games=n_games)


if __name__ == "__main__":
    df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv")
    f = fit(df)
    print({k: (np.round(v, 3) if isinstance(v, (float, np.ndarray)) else v) for k, v in f.items() if k not in ("a", "u")})
    print("median tokens to clear L1 (reference run, average game):", round(float(np.exp(f["mu"]))))
    print("level multipliers:", np.round(np.exp(f["b"]), 2))
    print("run effects (x):", {k[:40]: round(float(np.exp(v)), 2) for k, v in f["a"].items()})
    print("game effects (x):", {k: round(float(np.exp(v)), 2) for k, v in sorted(f["u"].items(), key=lambda kv: kv[1])})
