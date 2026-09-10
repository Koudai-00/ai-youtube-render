# -*- coding: utf-8 -*-
"""keramov_charlie_short の CI窓分割の境界(1行1窓 "s:e")。
   71秒の短尺なので約36秒×2窓。境界はナレのビート開始にスナップして字幕を割らない。
   env WIN_FROM/WIN_TO で並列スライス。"""
from __future__ import annotations
import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIM = json.loads((ROOT / "subtitles" / "out" / "keramov_charlie_short" / "timings.json").read_text(encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)
starts = sorted(b["start"] for b in TIM["beats"])
target = COMP / 2
snap = min((s for s in starts if 12 < s < COMP - 12), key=lambda s: abs(s - target))
wins = [(0.0, round(snap, 2)), (round(snap, 2), COMP)]
lo = int(os.environ.get("WIN_FROM", 0) or 0)
hi = int(os.environ.get("WIN_TO", len(wins)) or len(wins))
for s, e in wins[lo:hi]:
    print(f"{round(s,2)}:{round(e,2)}")
