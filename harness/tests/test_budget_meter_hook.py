"""The budget-meter hook reads the current level attempt from the real HistoryEntry/Frame types."""
import os
import sys

os.environ["ARC3_BUDGET_METER"] = "1"
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else r"D:\arc3_paper\harness\src\ARC3-Inference")
import inference.agent.tool_agent as ta  # noqa: E402
from inference.agent.runtime_state import Frame, HistoryEntry  # noqa: E402


def grid(bar_len, blob_at):
    g = [[0] * 64 for _ in range(64)]
    for c in range(bar_len):          # budget bar along the top edge, colour 9
        g[0][c] = 9
    g[30][blob_at] = 5                # a moving sprite in the interior
    return tuple(tuple(r) for r in g)


hist = []
# previous level, should be ignored
hist.append(HistoryEntry(action="UP", frame=Frame(grid=grid(64, 3), step=1, level=1)))
# current level 2 attempt: bar 64 -> 56, 2 cells per action
for i in range(8):
    hist.append(HistoryEntry(action="RIGHT", frame=Frame(grid=grid(64 - 2 * i, 10 + i), step=2 + i, level=2)))
cur = hist[-1].frame
line = ta._budget_meter_line(hist, cur)
print(line)
assert "roughly 25 actions remain" in line and "last 7 actions" in line, line

# after a RESET the attempt restarts: too few observations -> no claim
hist.append(HistoryEntry(action="RESET", frame=Frame(grid=grid(64, 10), step=8, level=2)))
assert ta._budget_meter_line(hist, hist[-1].frame) == ""
print("OK")
