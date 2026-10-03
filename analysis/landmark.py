"""Does within-level activity (actions taken so far) predict clearing, beyond tokens spent,
level depth and the game's estimated difficulty? Landmark analysis on per-action histories."""
import glob, hashlib, json, os
import numpy as np, pandas as pd
from scipy import stats
from costmodel import fit
from level_attempts import ROOTS
df = pd.read_csv('level_attempts.csv'); M = fit(df)
rows, seen = [], set()
for root in ROOTS:
    for p in glob.glob(os.path.join(root, '**', 'benchmark.json'), recursive=True):
        h = hashlib.md5(open(p, 'rb').read()).hexdigest()
        if h in seen: continue
        seen.add(h)
        run = os.path.basename(os.path.dirname(p))
        b = json.load(open(p, encoding='utf-8'))
        for g in b.get('game_runs', []):
            hist, apl = g.get('history') or [], g.get('actions_per_level') or []
            L = int(g.get('levels_completed') or 0); idx = 0
            for lv in range(min(L + 1, len(apl))):
                seg = hist[idx: idx + apl[lv]]; idx += apl[lv]
                if not seg: continue
                cum = np.cumsum([x.get('generated_tokens') or 0 for x in seg])
                rows.append(dict(run=run, game=g['game_id'][:4], level=lv + 1, done=lv < L, cum=cum, total=cum[-1]))
A = pd.DataFrame(rows)
A = A[A.run.isin(M['a'].keys())]
for land, horizon in [(20000, 60000), (40000, 80000), (80000, 120000)]:
    sub = []
    for _, r in A.iterrows():
        if r.total <= land: continue          # cleared or abandoned before the landmark
        a_by = int((r.cum <= land).sum())     # actions taken by the landmark
        cleared_next = bool(r.done and r.total <= land + horizon)
        censored = (not r.done) and r.total < land + horizon  # run ended before the horizon
        if censored: continue
        lv = min(r.level, len(M['b']))
        sub.append(dict(y=cleared_next, log_actions=np.log1p(a_by), level=lv,
                        prior=M['mu'] + M['b'][lv - 1] + M['a'][r.run] + M['u'].get(r.game, 0.0)))
    S = pd.DataFrame(sub)
    X = np.column_stack([np.ones(len(S)), S.log_actions.values, S.prior.values]); y = S.y.values.astype(float)
    beta = np.zeros(3)
    for _ in range(50):  # Newton-Raphson logistic regression
        p = 1 / (1 + np.exp(-X @ beta)); W = p * (1 - p)
        H = X.T @ (X * W[:, None]); beta += np.linalg.solve(H, X.T @ (y - p))
    se = np.sqrt(np.diag(np.linalg.inv(H))); pv = 2 * stats.norm.sf(np.abs(beta / se))
    print(f"landmark {land//1000}k, horizon +{horizon//1000}k: n={len(S)} cleared={y.mean():.2f} | "
          f"log_actions coef {beta[1]:+.2f} (p={pv[1]:.3f}), prior coef {beta[2]:+.2f} (p={pv[2]:.3f})")
