"""RIZIN.54 全選手紹介まとめ 時間分割レンダーの窓境界を安全な位置に選ぶ。
境界は「字幕(キュー)の切れ目」かつ「章/STATカード/ダック(試合映像20秒)の外」に置く。
ダック内で窓を切ると試合映像に継ぎ目が出るため、ダックは必ず1窓内に収める(NOCUT)。
出力: "s:e" を1行1窓でstdoutへ。前提: 事前に full build 済みの index.html。
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "hyperframes" / "templates" / "rizin54-fighters" / "index.html").read_text(encoding="utf-8")
D = json.loads(re.search(r"const DATA = (\{.*?\});\s*\n\s*const ovLayer", HTML, re.S).group(1))
TOTAL = float(D["total"])

NOCUT = []
for c in D.get("chapters", []):
    NOCUT.append((c["start"] - 0.6, c["end"] + 0.3))
for c in D.get("stats", []):
    NOCUT.append((c["start"] - 0.3, c["end"] + 0.3))
for c in D.get("ducks", []):
    NOCUT.append((c["start"] - 1.2, c["end"] + 1.2))


def in_nocut(t):
    return any(a < t < b for a, b in NOCUT)


cands = sorted(set([round(c["s"], 2) for c in D["caps"]] + [round(c["e"], 2) for c in D["caps"]]))
cands = [t for t in cands if 0 < t < TOTAL]

TARGET, LO, HI = 46.0, 34.0, 56.0
bounds = [0.0]
while TOTAL - bounds[-1] > HI:
    last = bounds[-1]
    lo, hi, tgt = last + LO, last + HI, last + TARGET
    pool = [t for t in cands if lo <= t <= hi and not in_nocut(t)]
    if not pool:
        pool = [t for t in cands if lo <= t <= hi and not in_nocut(t + 0.01)]
    if not pool:
        pool = [t for t in cands if lo <= t <= hi]
    nxt = round(tgt, 2) if not pool else min(pool, key=lambda t: abs(t - tgt))
    if nxt <= last + 1:
        nxt = round(last + TARGET, 2)
    bounds.append(nxt)
bounds.append(round(TOTAL, 3))

for i in range(len(bounds) - 1):
    print(f"{bounds[i]}:{bounds[i+1]}")
