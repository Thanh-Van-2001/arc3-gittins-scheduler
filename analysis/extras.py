import numpy as np, pandas as pd
from costmodel import fit
from sim import sample_world, simulate, make_franzen
from gittins import GittinsTables, make_gittins
df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv"); M = fit(df)
nl_pool = df.groupby("game").n_levels.first().values
fr_runs = [r for r, a in M["a"].items() if np.exp(a) < 0.35]
done = df[df.completed & (df.actions > 0) & df.run.isin(fr_runs)]
ratio_pool = (done.baseline / done.actions).values
run_eff = float(np.mean([M["a"][r] for r in fr_runs])); eff = float(np.mean(np.minimum(1.0, ratio_pool ** 2)))
G, B = 110, 19.4e6; NL = sorted(set(nl_pool))
tabs = {sh: GittinsTables(M, run_eff, shift=sh, tmax=600_000, n_levels_range=NL, eff=eff) for sh in [0.0, 0.3, 0.6, 0.9, 1.2]}
# myopic tables (no continuation value) for the endgame
class Myopic(GittinsTables):
    def _solve(self, n):
        H = self._hazards(n); R = np.arange(1, n + 1) / (n * (n + 1) / 2) * 100.0 * self.eff
        Q = np.zeros((len(self.lambdas), 41, n, self.T), dtype=np.float32)
        for l in range(n):
            V = np.zeros((len(self.lambdas), 41))
            for i in range(self.T - 1, -1, -1):
                h = H[l, :, i][None, :]
                q = h * R[l] + (1 - h) * V - self.lambdas[:, None] * self.q
                Q[:, :, l, i] = q; V = np.maximum(0.0, q)
        return Q
myo = Myopic(M, run_eff, shift=0.6, tmax=600_000, n_levels_range=NL, eff=eff)
def make_endgame(tab, myo, start=0.85):
    g1, g2 = make_gittins(tab), make_gittins(myo)
    return lambda st, w, a, frac, ps: (g2 if frac >= start else g1)(st, w, a, frac, ps)
def make_online_shift(tabs):
    # pick the table whose shift best explains all cleared levels so far (pooled across games)
    pols = {sh: make_gittins(t) for sh, t in tabs.items()}
    def pol(st, w, active, frac, ps):
        obs = [(l, c, st) for g in range(len(w.n_levels)) for l, c in enumerate(st.cleared_costs[g])]
        if len(obs) < 15: return pols[0.6](st, w, active, frac, ps)
        best, bsh = -1e18, 0.6
        for sh, t in tabs.items():
            ll = 0.0
            for g in range(len(w.n_levels)):
                wpost = t.posterior(list(enumerate(st.cleared_costs[g])), int(st.level[g]), st.t[g]) if False else None
            # marginal likelihood under each shift, game effects integrated (prior weights)
            from gittins import PRIOR
            for g in range(len(w.n_levels)):
                lw = np.log(PRIOR).copy()
                for l, c in enumerate(st.cleared_costs[g]):
                    lw += -0.5 * ((np.log(c) - t.logc_mean(l)) / t.s) ** 2
                if st.t[g] > 0:
                    from scipy import stats
                    lw += stats.norm.logsf((np.log(st.t[g]) - t.logc_mean(int(min(st.level[g], w.n_levels[g]-1)))) / t.s)
                mx = lw.max(); ll += mx + np.log(np.exp(lw - mx).sum())
            if ll > best: best, bsh = ll, sh
        return pols[bsh](st, w, active, frac, ps)
    return pol
for world_shift in [0.0, 0.6, 1.2]:
    rows = []
    for sd in range(4):
        w = sample_world(np.random.default_rng(500 + sd), G, M, nl_pool, ratio_pool, run_eff, world_shift)
        kw = dict(lease=30000, first_chunk=40000)
        r = dict(franzen=simulate(w, B, make_franzen(), **kw)[0], gittins06=simulate(w, B, make_gittins(tabs[0.6]), **kw)[0],
                 gittins_matched=simulate(w, B, make_gittins(tabs[world_shift]), **kw)[0],
                 gittins_endgame=simulate(w, B, make_endgame(tabs[0.6], myo), **kw)[0])
        rows.append(r)
    print("world shift", world_shift, pd.DataFrame(rows).mean().round(2).to_dict(), flush=True)
