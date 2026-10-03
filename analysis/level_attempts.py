"""Turn benchmark.json files from public Duck-family runs into a flat table of level attempts.

One row per (run, game, level) that the agent reached: actions spent, generated tokens spent,
wall-clock spent, whether the level was completed, and the human baseline action count.
Unfinished attempts are right-censored (the run ended before completion).
"""
import json, glob, os, sys, hashlib
import pandas as pd

ROOTS = [r"D:\arc3_paper\meta\runs", r"C:\Users\Admin\AppData\Local\Temp\out"]

def attempts_from_benchmark(path):
    b = json.load(open(path, encoding="utf-8"))
    run = os.path.basename(os.path.dirname(path))
    rows = []
    for g in b.get("game_runs", []):
        hist = g.get("history") or []
        apl = g.get("actions_per_level") or []
        base = g.get("base_actions_per_level") or []
        L = int(g.get("levels_completed") or 0)
        n_levels = int(g.get("number_of_levels") or len(base) or 0)
        idx = 0
        t_prev = 0.0
        for lv in range(min(L + 1, n_levels)):
            n = apl[lv] if lv < len(apl) else 0
            seg = hist[idx: idx + n]
            idx += n
            tok = sum(h.get("generated_tokens") or 0 for h in seg)
            t_end = seg[-1]["wallclock_seconds"] if seg else t_prev
            rows.append(dict(run=run, game=g["game_id"][:4], level=lv + 1, n_levels=n_levels,
                             completed=lv < L, actions=n, tokens=tok, seconds=max(0.0, t_end - t_prev),
                             baseline=base[lv] if lv < len(base) else None,
                             final_score=g.get("final_score"), state=g.get("state")))
            t_prev = t_end
    return rows

def load_all():
    rows, seen = [], set()
    for root in ROOTS:
        for p in glob.glob(os.path.join(root, "**", "benchmark.json"), recursive=True):
            h = hashlib.md5(open(p, "rb").read()).hexdigest()
            if h in seen:  # forks often re-publish identical outputs
                continue
            seen.add(h)
            try:
                rows += attempts_from_benchmark(p)
            except Exception as e:
                print("skip", p, repr(e), file=sys.stderr)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = load_all()
    out = r"D:\arc3_paper\analysis\level_attempts.csv"
    df.to_csv(out, index=False)
    print(df.shape, "runs:", df.run.nunique(), "games:", df.game.nunique())
    done = df[df.completed & (df.actions > 0)]
    r = (done.baseline / done.actions)
    print("completed level attempts:", len(done))
    print("baseline/actions quantiles:", r.quantile([.1, .25, .5, .75, .9]).round(2).to_dict())
    print("share of completed levels at score cap (ratio>=sqrt(1.15)=1.072):", round((r >= 1.0724).mean(), 3))
    print("share with ratio < 1 (score < 100):", round((r < 1).mean(), 3))
