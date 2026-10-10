"""combo3 v3 hardening, applied to the built notebook by make_combo3.py.

combo3 v2 scored 0.00 in its first competition rerun (submission 57024002, Sat 2026-10-10 00:00 UTC) after five clean
commit runs: the server most likely never came up. Two cheap guards:
- JustAdev742's --input-fallback resolver remaps datasets and the competition between Kaggle's two mount layouts but
  not models; this one also tries the model layouts (no models/<owner> prefix, capitalised framework folder) and, as a
  last resort, searches /kaggle/input for the slug (5 levels) and follows the tail case-insensitively.
- ARC3_HTTP_RETRY_INITIAL_SECONDS 900 -> 2400: each game's first request waits up to 40 min for a slow server boot
  (Saturday 00:00 UTC storage ran 4-5x slow per JustAdev's log; a normal boot is ~8.5 min).
"""

RESOLVER = r'''import os as _ours_os
def _ours_input(path):
    if _ours_os.path.exists(path):
        return path
    parts = path.split('/')  # '', 'kaggle', 'input', kind, ...
    root, kind = '/'.join(parts[:3]), (parts[3] if len(parts) > 3 else '')
    cands = []
    if kind == 'datasets' and len(parts) > 5:
        cands.append('/'.join(parts[:3] + parts[5:]))
    elif kind == 'competitions' and len(parts) > 4:
        cands.append('/'.join(parts[:3] + parts[4:]))
    elif kind == 'models' and len(parts) > 5:
        rest = parts[6:]
        for r in (rest, [rest[0].capitalize()] + rest[1:] if rest else []):
            cands += ['/'.join(parts[:6] + r), '/'.join(parts[:3] + [parts[5]] + r)]
    for alt in cands:
        if _ours_os.path.exists(alt):
            print(f'ours: {path} -> {alt}')
            return alt
    slug_i = 5 if kind in ('datasets', 'models') else 4
    if len(parts) > slug_i:
        slug, tail = parts[slug_i], parts[slug_i + 1:]
        for dirpath, dirnames, _files in _ours_os.walk(root):
            if dirpath[len(root):].count('/') >= 5:
                dirnames[:] = []
                continue
            if slug not in dirnames:
                continue
            cur = dirpath.rstrip('/') + '/' + slug
            for t in tail:
                m = [d for d in _ours_os.listdir(cur) if d.lower() == t.lower()] if _ours_os.path.isdir(cur) else []
                if not m:
                    cur = None
                    break
                cur = cur + '/' + m[0]
            if cur is None and kind == 'models':  # any folder of the slug holding a config.json
                for dp, dn, fn in _ours_os.walk(dirpath.rstrip('/') + '/' + slug):
                    if 'config.json' in fn:
                        cur = dp
                        break
            if cur and _ours_os.path.exists(cur):
                print(f'ours (search): {path} -> {cur}')
                return cur
    print(f'ours: WARNING input path not found: {path}')
    return path
'''

OLD_START = "import os as _ours_os\ndef _ours_input(path):\n"
OLD_END = "# <<< ours (--input-fallback)"
GRACE_OLD = "os.environ['ARC3_HTTP_RETRY_INITIAL_SECONDS'] = '900'"
GRACE_NEW = "os.environ['ARC3_HTTP_RETRY_INITIAL_SECONDS'] = '2400'  # Talyxion v3: survive a slow model boot"


def harden(src: str) -> str:
    assert src.count(OLD_START) == 1 and src.count(OLD_END) == 1 and src.count(GRACE_OLD) == 1
    a, b = src.index(OLD_START), src.index(OLD_END)
    return src[:a] + RESOLVER + src[b:].replace(GRACE_OLD, GRACE_NEW)
