"""今週ニュース(weekly0814) CI窓分割の境界を出力(1行1窓 "s:e")。
単一bg動画＋DOM前景方式なので固定60秒窓で安全(前景はcontで境界継続=再アニメ無し)。"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIM = json.loads((ROOT / "subtitles" / "out" / "weekly0814" / "timings.json").read_text(encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)
step = 60.0
t = 0.0
while t < COMP - 0.01:
    e = min(t + step, COMP)
    print(f"{round(t,2)}:{round(e,2)}")
    t = e
