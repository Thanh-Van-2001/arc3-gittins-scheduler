"""A timed-out tool call must not drop functions retained from earlier calls (talyxion_fixes.patch)."""
import os
import sys

os.environ.update({"ARC3_PERSISTENT_FUNCTIONS": "1", "ARC3_PERSISTENT_FUNCTIONS_SCOPE": "game"})
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else r"D:\arc3_paper\harness\src\ARC3-Inference")
import inference.agent.tool_agent as ta  # noqa: E402

ag = object.__new__(ta.ToolAgent)
src = "def helper(x):\n    return x + 1\n"
ag._kept_functions = {}

payload = {}
ag._record_retained_functions({"stdout": "", "keepable_functions": [{"name": "helper", "source": src}]}, payload)
assert list(ag._kept_functions) == ["helper"], ag._kept_functions

payload = {}
ag._record_retained_functions({"error": "Tool timed out after 30s", "stdout": "", "action_results": []}, payload)
assert list(ag._kept_functions) == ["helper"], "timeout dropped retained functions"
print("timeout keeps functions:", payload.get("function_retention"))

payload = {}
ag._record_retained_functions({"stdout": "", "keepable_functions": []}, payload)
assert ag._kept_functions == {}, "a completed call that keeps nothing still clears (upstream semantics)"
print("OK")
