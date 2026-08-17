"""アオリ CI窓分割の境界を出力(1行1窓 "s:e")。単一bg動画+DOM前景=固定60秒窓で安全(contで境界継続)。
CIを2並列に分けるため env WIN_FROM/WIN_TO で窓のスライスを出力できる(既定=全窓)。"""
import json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TIM = json.loads((ROOT / "subtitles" / "out" / "aori" / "timings.json").read_text(encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)
wins = []
t = 0.0
while t < COMP - 0.01:
    e = min(t + 60.0, COMP); wins.append((round(t, 2), round(e, 2))); t = e
lo = int(os.environ.get("WIN_FROM", 0) or 0)
hi = int(os.environ.get("WIN_TO", len(wins)) or len(wins))
for s, e in wins[lo:hi]:
    print(f"{s}:{e}")
