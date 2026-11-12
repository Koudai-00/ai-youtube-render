"""weekly1113 CI窓分割の境界(1行1窓 "s:e")。"""
import json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
T = json.loads((ROOT / "subtitles/out/weekly1113/timings.json").read_text(encoding="utf-8"))
COMP = T["total"]; st = [b["start"] for b in T["beats"]]; b = [0.0]
while b[-1] < COMP - 26:
    t = b[-1] + 50; c = [s for s in st if b[-1] + 26 < s < COMP - 8]
    if not c: break
    v = min(c, key=lambda s: abs(s - t))
    if v <= b[-1] + 1: break
    b.append(round(v, 2))
b.append(COMP); w = list(zip(b, b[1:]))
lo = int(os.environ.get("WIN_FROM", 0)); hi = int(os.environ.get("WIN_TO", len(w)))
for s, e in w[lo:hi]: print(f"{round(s, 2)}:{round(e, 2)}")
