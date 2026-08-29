"""今週ニュース(ufcsh0829) CI窓分割の境界を出力(1行1窓 "s:e")。
per-segment背景方式。窓は概ね48秒(render_windows.sh 側で PIECE_SEC=12 に分割描画されるため
1描画あたりの背景動画数は数本に収まり、multi-video ハングを回避)。前景はcontで境界継続=再アニメ無し。
WIN_FROM/WIN_TO 環境変数で窓範囲をスライス(2並列レンダー用)。"""
from __future__ import annotations
import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIM = json.loads((ROOT / "subtitles" / "out" / "ufcsh0829" / "timings.json").read_text(encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)
# 窓境界はビート開始にスナップ(継続の自然な切れ目)
starts = [b["start"] for b in TIM["beats"]]
step = 48.0
bounds = [0.0]
while bounds[-1] < COMP - 24:
    t = bounds[-1] + step
    cands = [s for s in starts if s > bounds[-1] + 24 and s < COMP - 8]
    if not cands:
        break
    snap = min(cands, key=lambda s: abs(s - t))
    if snap <= bounds[-1] + 1:
        break
    bounds.append(round(snap, 2))
bounds.append(COMP)
wins = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]

lo = int(os.environ.get("WIN_FROM", 0))
hi = int(os.environ.get("WIN_TO", len(wins)))
for s, e in wins[lo:hi]:
    print(f"{round(s,2)}:{round(e,2)}")
