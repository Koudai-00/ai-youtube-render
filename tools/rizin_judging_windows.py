# -*- coding: utf-8 -*-
"""rizin_judging のCI窓分割の境界(1行1窓 "s:e")。
   約60秒窓。境界はビート開始にスナップして字幕・カードを割らない。
   env WIN_FROM/WIN_TO で並列スライス。"""
from __future__ import annotations
import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIM = json.loads((ROOT / "subtitles" / "out" / "rizin_judging" / "timings.json").read_text(encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)
starts = sorted(b["start"] for b in TIM["beats"])
step = 60.0
bounds = [0.0]
while bounds[-1] < COMP - 35:
    t = bounds[-1] + step
    cands = [s for s in starts if s > bounds[-1] + 35 and s < COMP - 12]
    if not cands:
        break
    snap = min(cands, key=lambda s: abs(s - t))
    if snap <= bounds[-1] + 1:
        break
    bounds.append(round(snap, 2))
bounds.append(COMP)
wins = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]
lo = int(os.environ.get("WIN_FROM", 0) or 0)
hi = int(os.environ.get("WIN_TO", len(wins)) or len(wins))
for s, e in wins[lo:hi]:
    print(f"{round(s,2)}:{round(e,2)}")
