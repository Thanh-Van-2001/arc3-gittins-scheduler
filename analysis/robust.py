import numpy as np, pandas as pd, sys, json, itertools
from costmodel import fit
from sim import sample_world, simulate, make_equal, make_franzen, oracle_score
from gittins import GittinsTables, make_gittins
df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv")
M = fit(df)
nl_pool = df.groupby("game").n_levels.first().values
fr_runs = [r for r, a in M["a"].items() if np.exp(a) < 0.35]
done = df[df.completed & (df.actions > 0) & df.run.isin(fr_runs)]
ratio_pool = (done.baseline / done.actions).values
run_eff = float(np.mean([M["a"][r] for r in fr_runs]))
eff = float(np.mean(np.minimum(1.0, ratio_pool ** 2)))
G, B = 110, 19.4e6
tab = GittinsTables(M, run_eff, shift=0.6, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)
scen = [
  ("matched", dict(shift=0.6)),
  ("world easier (shift 0.0)", dict(shift=0.0)),
  ("world harder (shift 1.2)", dict(shift=1.2)),
  ("heavy tails t3", dict(shift=0.6, t_df=3)),
  ("more game spread x1.4", dict(shift=0.6, su_scale=1.4)),
  ("less game spread x0.5", dict(shift=0.6, su_scale=0.5)),
  ("more level noise x1.3", dict(shift=0.6, s_scale=1.3)),
]
leases = [0.0, 30000.0]
for (name, kw), lease in itertools.product(scen, leases):
    d = []
    for sd in range(4):
        w = sample_world(np.random.default_rng(200 + sd), G, M, nl_pool, ratio_pool, run_eff, **kw)
        f = simulate(w, B, make_franzen(), lease=lease)[0]
        g = simulate(w, B, make_gittins(tab), lease=lease)[0]
        e = simulate(w, B, make_equal(G, B))[0]
        o = oracle_score(w, B)
        d.append((e, f, g, o))
    d = np.array(d)
    print(f"{name:28s} lease={int(lease):6d} equal {d[:,0].mean():5.1f} franzen {d[:,1].mean():5.1f} gittins {d[:,2].mean():5.1f} oracle {d[:,3].mean():5.1f} | G-F {np.mean(d[:,2]-d[:,1]):+5.2f} (min {np.min(d[:,2]-d[:,1]):+5.2f})", flush=True)
