import numpy as np, pandas as pd, itertools
from costmodel import fit
from sim import sample_world, simulate, make_equal, make_franzen, oracle_score
from gittins import GittinsTables, make_gittins
df = pd.read_csv(r"D:\arc3_paper\analysis\level_attempts.csv"); M = fit(df)
nl_pool = df.groupby("game").n_levels.first().values
fr_runs = [r for r, a in M["a"].items() if np.exp(a) < 0.35]
done = df[df.completed & (df.actions > 0) & df.run.isin(fr_runs)]
ratio_pool = (done.baseline / done.actions).values
run_eff = float(np.mean([M["a"][r] for r in fr_runs])); eff = float(np.mean(np.minimum(1.0, ratio_pool ** 2)))
G, B = 110, 19.4e6
tab = GittinsTables(M, run_eff, shift=0.6, tmax=600_000, n_levels_range=sorted(set(nl_pool)), eff=eff)
for first, lease in [(0, 0), (40000, 30000), (60000, 50000), (80000, 60000)]:
    d = []
    for sd in range(6):
        w = sample_world(np.random.default_rng(300 + sd), G, M, nl_pool, ratio_pool, run_eff, 0.6)
        f = simulate(w, B, make_franzen(), lease=lease, first_chunk=first)[0]
        g = simulate(w, B, make_gittins(tab), lease=lease, first_chunk=first)[0]
        d.append((f, g))
    d = np.array(d); diff = d[:, 1] - d[:, 0]
    print(f"first_chunk={first:6d} lease={lease:6d}  franzen {d[:,0].mean():5.1f}  gittins {d[:,1].mean():5.1f}  diff {diff.mean():+5.2f} +- {diff.std(ddof=1)/np.sqrt(len(diff)):.2f} (min {diff.min():+5.2f})", flush=True)
