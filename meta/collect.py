"""Collect benchmark.json outputs from public ARC-AGI-3 notebooks (offline demo runs)."""
import subprocess, json, os, sys, re, time
K = [r"C:\Users\Admin\AppData\Local\Temp\kgl\Scripts\python.exe", "-m", "kaggle"]
OUT = r"D:\arc3_paper\meta\runs"
os.makedirs(OUT, exist_ok=True)
refs = []
for sort in ["voteCount", "scoreDescending", "dateRun", "hotness"]:
    for page in range(1, 6):
        r = subprocess.run(K + ["kernels", "list", "--competition", "arc-prize-2026-arc-agi-3", "--sort-by", sort,
                                "--page-size", "100", "--page", str(page), "--csv"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        lines = [l for l in r.stdout.splitlines()[1:] if "/" in l.split(",")[0]]
        if not lines: break
        refs += [l.split(",")[0] for l in lines]
refs = list(dict.fromkeys(refs))
print("kernels:", len(refs), flush=True)
json.dump(refs, open(os.path.join(OUT, "_refs.json"), "w"))
got = 0
for i, ref in enumerate(refs):
    d = os.path.join(OUT, ref.replace("/", "__"))
    if os.path.exists(os.path.join(d, "benchmark.json")) or os.path.exists(os.path.join(d, "_none")):
        continue
    os.makedirs(d, exist_ok=True)
    r = subprocess.run(K + ["kernels", "output", ref, "-p", d, "-q", "--file-pattern", r"^(benchmark\.json|evaluation\.json)$"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    if os.path.exists(os.path.join(d, "benchmark.json")):
        got += 1
    else:
        open(os.path.join(d, "_none"), "w").write(r.stdout[-500:] + r.stderr[-500:])
    # the CLI also downloads the kernel log; drop it to save space
    for f in os.listdir(d):
        if f.endswith(".log"): os.remove(os.path.join(d, f))
    if i % 20 == 0: print(i, ref, "got", got, flush=True)
print("DONE got", got, flush=True)
