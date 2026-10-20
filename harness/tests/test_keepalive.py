"""The startup keepalive resets the warmup game while /health fails and stops once it answers."""
import http.server
import os
import sys
import threading
import time

root = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Admin\AppData\Local\Temp\c3chk\t2"
sys.path[:0] = [os.path.join(root, "ARC3-Inference"), os.path.join(root, "tufa-arc-agi-framework")]
try:
    import taaf.game  # noqa: F401  (the TAAF framework ships in Franzen's bundle dataset, not in this tree)
except ImportError:
    import types

    for name in ("taaf", "taaf.game", "taaf.solver"):
        sys.modules[name] = types.ModuleType(name)
    sys.modules["taaf.solver"].Solver = object
    sys.modules["taaf.game"].Game = object
    sys.modules["taaf"].game, sys.modules["taaf"].solver = sys.modules["taaf.game"], sys.modules["taaf.solver"]
import inference.framework.solver as solver  # noqa: E402

healthy = {"ok": False}


class Health(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if healthy["ok"] and self.path == "/health" else 503)
        self.end_headers()

    def log_message(self, *a):
        pass


srv = http.server.HTTPServer(("127.0.0.1", 0), Health)
threading.Thread(target=srv.serve_forever, daemon=True).start()
os.environ["LOCAL_ANALYZER_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}/v1"
assert solver._analyzer_healthy() is False


class FakeGameSolver:
    resets = 0

    def should_stop(self):
        return False

    def _execute_auto_reset(self):
        FakeGameSolver.resets += 1


solver.KEEPALIVE_SECONDS = 0.2
g = FakeGameSolver()
solver._start_startup_keepalive(g)
time.sleep(1.1)
assert g.resets >= 3, g.resets
healthy["ok"] = True
assert solver._analyzer_healthy() is True
time.sleep(0.6)
n = g.resets
time.sleep(0.8)
assert g.resets == n, (n, g.resets)
print("resets while down:", n, "-> stopped once healthy; OK")
