"""combo5 v2 hardening of JustAdev742's --draft cell (applied by make_combo3.py).

combo5 v1's first competition rerun (57502585, 2026-10-22) scored 0.00 after clean commit runs. The --draft cell looks
for the session-A kernel output at two fixed mount paths and raises after 600 s, and the build drops the albucino
draft from the inputs, so a different mount path in the rerun ends the run (and a 10-minute wait also risks the
15-minute no-move rule). Here the cell searches /kaggle/input for the draft manifest, waits at most 120 s, and falls
back to the albucino draft (kept as a model source) instead of raising, so the worst case is combo4.
"""

ALBUCINO_MODEL = "dfranzen/albucino-qwen3-8-flash-next-drafter/Transformers/default/1"
ALBUCINO_PATH = "/kaggle/input/models/dfranzen/albucino-qwen3-8-flash-next-drafter/transformers/default/1"

OLD_LOOP = (
    "    while not (found := [p for p in candidates if os.path.isfile(os.path.join(p, 'arc3-draft-manifest.json'))]):\n"
    "        if time.time() - t0 > timeout_s:\n"
    "            raise RuntimeError(f'MTP draft not mounted after {timeout_s:g} s: {candidates}')\n"
    "        time.sleep(5)\n"
)
NEW_LOOP = (
    "    import glob as _g\n"
    "    def _look():\n"
    "        hits = [p for p in candidates if os.path.isfile(os.path.join(p, 'arc3-draft-manifest.json'))]\n"
    "        for depth in range(1, 6):  # Talyxion v2: any mount layout\n"
    "            hits += sorted(os.path.dirname(m) for m in _g.glob('/kaggle/input/' + '*/' * depth + 'arc3-draft-manifest.json'))\n"
    "        return hits\n"
    "    while not (found := _look()):\n"
    "        if time.time() - t0 > timeout_s:\n"
    "            print(f'ours: WARNING MTP draft not mounted after {timeout_s:g} s; falling back to albucino')\n"
    "            return None\n"
    "        time.sleep(5)\n"
)


def harden_draft(src: str) -> str:
    assert src.count(OLD_LOOP) == 1, "draft wait loop not found"
    src = src.replace(OLD_LOOP, NEW_LOOP)
    src = src.replace("timeout_s=600.0", "timeout_s=120.0")
    # sha mismatches also fall back instead of raising
    src = src.replace("        raise RuntimeError(f'MTP draft {path}: manifest sha256",
                      "        print('ours: WARNING draft manifest mismatch; falling back to albucino'); return None\n"
                      "        raise RuntimeError(f'MTP draft {path}: manifest sha256")
    src = src.replace("        raise RuntimeError(f'MTP draft {path}: mtp",
                      "        print('ours: WARNING draft dense mismatch; falling back to albucino'); return None\n"
                      "        raise RuntimeError(f'MTP draft {path}: mtp")
    line_start = src.index("DRAFT_MODEL_DIR   = _ours_draft_dir(")
    line_end = src.index("\n", line_start)
    call = src[line_start:line_end]
    src = src[:line_start] + call + f" or _ours_input({ALBUCINO_PATH!r})" + src[line_end:]
    return src
