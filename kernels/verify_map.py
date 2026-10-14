"""Execute the notebook's FR-Spec map writer cell into a temp dir and compare its sha256 with TOKEN_MAP_SHA (cell 12)."""
import hashlib
import json
import os
import re
import sys
import tempfile

nb = json.load(open(sys.argv[1], encoding="utf-8"))
cells = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
writer = [s for s in cells if "/kaggle/arc3-hot-tokens.pt" in s and "TOKEN_MAP_SHA" not in s]
launcher = [s for s in cells if "TOKEN_MAP_SHA" in s and "args" in s]
assert len(writer) == 1 and launcher, (len(writer), len(launcher))
want = re.findall(r"TOKEN_MAP_SHA\s*=\s*['\"]([0-9a-f]{64})['\"]", launcher[0])
tmp = tempfile.mkdtemp()
src = writer[0].replace("/kaggle/arc3-hot-tokens.pt", os.path.join(tmp, "map.pt"))
exec(compile(src, "writer", "exec"), {"__name__": "__main__"})
got = hashlib.sha256(open(os.path.join(tmp, "map.pt"), "rb").read()).hexdigest()
print("TOKEN_MAP_SHA", want, "written", got, "MATCH" if want and want[-1] == got else "MISMATCH")
