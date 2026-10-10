"""Exercise the v3 resolver against fake /kaggle/input trees (both known layouts + variants seen or feared)."""
import os
import tempfile

from robust_input import RESOLVER

INPUTS = {
    "wheel": "/kaggle/input/datasets/dfranzen/pennyroyal-v253",
    "model": "/kaggle/input/models/dfranzen/intel-qwen3.8-flash-next-w4a16-autoround/transformers/default/1",
    "draft": "/kaggle/input/models/dfranzen/albucino-qwen3-8-flash-next-drafter/transformers/default/1",
    "bundle": "/kaggle/input/datasets/dfranzen/taaf-kaggle-source-bundle-copy",
    "comp": "/kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels",
}
LAYOUTS = {
    "new": {k: v for k, v in INPUTS.items()},
    "old": {"wheel": "/kaggle/input/pennyroyal-v253",
            "model": "/kaggle/input/models/dfranzen/intel-qwen3.8-flash-next-w4a16-autoround/transformers/default/1",
            "draft": "/kaggle/input/models/dfranzen/albucino-qwen3-8-flash-next-drafter/transformers/default/1",
            "bundle": "/kaggle/input/taaf-kaggle-source-bundle-copy",
            "comp": "/kaggle/input/arc-prize-2026-arc-agi-3/arc_agi_3_wheels"},
    "flat-models": {"wheel": "/kaggle/input/pennyroyal-v253",
                    "model": "/kaggle/input/intel-qwen3.8-flash-next-w4a16-autoround/transformers/default/1",
                    "draft": "/kaggle/input/albucino-qwen3-8-flash-next-drafter/transformers/default/1",
                    "bundle": "/kaggle/input/taaf-kaggle-source-bundle-copy",
                    "comp": "/kaggle/input/arc-prize-2026-arc-agi-3/arc_agi_3_wheels"},
    "capitalised": {"wheel": "/kaggle/input/datasets/dfranzen/pennyroyal-v253",
                    "model": "/kaggle/input/models/dfranzen/intel-qwen3.8-flash-next-w4a16-autoround/Transformers/default/1",
                    "draft": "/kaggle/input/models/dfranzen/albucino-qwen3-8-flash-next-drafter/Transformers/default/1",
                    "bundle": "/kaggle/input/datasets/dfranzen/taaf-kaggle-source-bundle-copy",
                    "comp": "/kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels"},
    "other-version": {"wheel": "/kaggle/input/datasets/dfranzen/pennyroyal-v253",
                      "model": "/kaggle/input/models/dfranzen/intel-qwen3.8-flash-next-w4a16-autoround/transformers/default/2",
                      "draft": "/kaggle/input/models/dfranzen/albucino-qwen3-8-flash-next-drafter/transformers/default/2",
                      "bundle": "/kaggle/input/datasets/dfranzen/taaf-kaggle-source-bundle-copy",
                      "comp": "/kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels"},
}


class FakeOS:
    """os stand-in that maps /kaggle/input onto a temp dir (and back, for walk results)."""

    def __init__(self, base):
        self.base, self.path = base, self

    def _m(self, p):
        return p.replace("/kaggle/input", self.base, 1)

    def exists(self, p):
        return os.path.exists(self._m(p))

    def isdir(self, p):
        return os.path.isdir(self._m(p))

    def listdir(self, p):
        return os.listdir(self._m(p))

    def walk(self, p):
        for dp, dn, fn in os.walk(self._m(p)):
            yield dp.replace(self.base, "/kaggle/input", 1).replace("\\", "/"), dn, fn


for name, layout in LAYOUTS.items():
    with tempfile.TemporaryDirectory() as base:
        for key, p in layout.items():
            d = p.replace("/kaggle/input", base, 1)
            os.makedirs(d)
            if key in ("model", "draft"):
                open(os.path.join(d, "config.json"), "w").close()
        ns = {}
        exec(RESOLVER, ns)
        ns["_ours_os"] = FakeOS(base)
        for key, p in INPUTS.items():
            got = ns["_ours_input"](p)
            same = got == layout[key] or (os.name == "nt" and got.lower() == layout[key].lower())  # NTFS ignores case
            assert same, (name, key, got, layout[key])
    print("layout", name, "OK")
print("all OK")
