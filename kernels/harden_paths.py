"""Make the notebooks robust to Kaggle's two input-mount layouts.

Kaggle mounts attached inputs either as /kaggle/input/datasets/<owner>/<slug> (new) or
/kaggle/input/<slug> (legacy); models and the competition data likewise. Franzen's notebook
hard-codes the new layout. We insert a resolver that keeps the original path when it exists and
otherwise falls back to the alternatives, so behaviour is identical whenever the original works.
"""
import json
import os
import sys

RESOLVER = r'''
# --- Talyxion: tolerate both Kaggle input-mount layouts (no-op when the original path exists) ---
def _resolve_input(path, must_contain=None):
    import glob as _glob
    p = Path(path)
    def ok(c):
        return c.exists() and (must_contain is None or (c / must_contain).exists())
    if ok(p):
        return str(p)
    parts = p.parts  # ('/', 'kaggle', 'input', kind, owner, slug, ...)
    cands = []
    if len(parts) > 5 and parts[3] in ('datasets', 'models'):
        slug, rest = parts[5], parts[6:]
        cands += [Path('/kaggle/input', slug, *rest), Path('/kaggle/input', slug)]
        if rest:  # model framework folder may be capitalised differently
            cands += [Path('/kaggle/input', slug, rest[0].capitalize(), *rest[1:]),
                      Path('/kaggle/input/models', parts[4], slug, rest[0].capitalize(), *rest[1:])]
    if len(parts) > 4 and parts[3] == 'competitions':
        cands += [Path('/kaggle/input', *parts[4:])]
    for c in cands:
        if ok(c):
            print(f'input path fallback: {path} -> {c}')
            return str(c)
    if must_contain:
        hits = sorted(_glob.glob(f'/kaggle/input/**/{must_contain}', recursive=True))
        slug = parts[5] if len(parts) > 5 else parts[-1]
        hits = [h for h in hits if slug in h] or hits
        if hits:
            c = Path(hits[0]).parent
            print(f'input path search: {path} -> {c}')
            return str(c)
    print(f'WARNING: input path not found: {path}')
    return str(p)

WHEELHOUSE_DIR  = _resolve_input(WHEELHOUSE_DIR)
MODEL_DIR       = _resolve_input(MODEL_DIR, 'config.json')
DRAFT_MODEL_DIR = _resolve_input(DRAFT_MODEL_DIR)
ORIG_BUNDLE_DIR = _resolve_input(ORIG_BUNDLE_DIR, 'deploy_target.pkl')
COMP_DIR        = _resolve_input('/kaggle/input/competitions/arc-prize-2026-arc-agi-3', 'arc_agi_3_wheels')
# --- end Talyxion resolver ---
'''


def harden(path):
    nb = json.load(open(path, encoding="utf-8"))
    idx = {i for i, c in enumerate(nb["cells"]) if "ORIG_BUNDLE_DIR   =" in "".join(c["source"])}
    assert len(idx) == 1, idx
    i4 = idx.pop()
    s = "".join(nb["cells"][i4]["source"])
    if "_resolve_input" not in s:
        anchor = "SERVED_MODEL_NAME = 'flashnext'\n"
        assert anchor in s
        s = s.replace(anchor, anchor + RESOLVER, 1)
        nb["cells"][i4]["source"] = s.splitlines(keepends=True)
    for c in nb["cells"]:
        src = "".join(c["source"])
        new = src.replace('"/kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels"',
                          'str(Path(COMP_DIR) / "arc_agi_3_wheels")')
        new = new.replace('Path("/kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels").parent',
                          'Path(COMP_DIR)')
        if new != src:
            c["source"] = new.splitlines(keepends=True)
    json.dump(nb, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    left = [l.strip() for c in nb["cells"] for l in "".join(c["source"]).splitlines()
            if "/kaggle/input/competitions" in l and "_resolve_input" not in l]
    print(os.path.basename(path), "remaining hard-coded competition paths:", left)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        harden(p)
