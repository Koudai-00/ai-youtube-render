"""AJ・マッキー 時間分割レンダーの窓境界を安全な位置に選ぶ。
境界は「字幕(キュー)の切れ目」かつ「章/カード/ダック区間の外」に置く
→ 窓またぎでのテロップ二重表示・カード/章の再アニメ（二重アニメ）を防ぐ。
出力: "s:e" を1行1窓でstdoutへ（render scriptが読む）。
前提: 事前に full build 済みの index.html があること。
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "hyperframes" / "templates" / "shaydullaev" / "index.html").read_text(encoding="utf-8")
D = json.loads(re.search(r"const DATA = (\{.*?\});\n", HTML, re.S).group(1))
TOTAL = float(D["total"])

# 境界を置いてはいけない区間（この内側で切ると再アニメ/黒/分断が起きる）
NOCUT = []
for c in D.get("chapters", []):
    NOCUT.append((c["start"] - 0.6, c["end"] + 0.3))
for c in D.get("cards", []):
    NOCUT.append((c["start"] - 0.3, c["end"] + 0.3))
for s in D.get("bg", []):
    if s.get("duck"):
        NOCUT.append((s["start"] - 0.2, s["end"] + 0.2))

# ダックはbgのstart/endにフラグが無い場合があるので timings からも取得
TIM = json.loads((ROOT / "subtitles" / "out" / "shaydullaev" / "timings.json").read_text(encoding="utf-8"))
for dk in TIM.get("ducks", []):
    NOCUT.append((dk["start"] - 0.2, dk["end"] + 0.2))


def in_nocut(t):
    return any(a < t < b for a, b in NOCUT)

# 候補=字幕キューの境界（各キューの s と e）。ここで切れば字幕は跨がない。
cands = sorted(set([round(c["s"], 2) for c in D["caps"]] + [round(c["e"], 2) for c in D["caps"]]))
cands = [t for t in cands if 0 < t < TOTAL]

# ダック範囲(30〜33秒)。窓境界がこの中に来ると試合映像が継ぎ目で割れるので、必ず外へ退避する。
DUCKS = [(dk["start"], dk["end"]) for dk in TIM.get("ducks", [])]


def snap_out_of_duck(t):
    """境界tがダック内なら、ダック終端の直後へ退避(次窓の先頭からダック外で開始)。"""
    for ds, de in DUCKS:
        if ds - 0.2 < t < de + 0.2:
            return round(de + 0.3, 2)
    return t


TARGET, LO, HI = 45.0, 34.0, 56.0
bounds = [0.0]
while TOTAL - bounds[-1] > HI:
    last = bounds[-1]
    lo, hi, tgt = last + LO, last + HI, last + TARGET
    pool = [t for t in cands if lo <= t <= hi and not in_nocut(t)]
    if not pool:  # 安全点が無ければ制約を緩め、それでも無ければtargetで妥協
        pool = [t for t in cands if lo <= t <= hi]
    if not pool:
        nxt = round(tgt, 2)
    else:
        nxt = min(pool, key=lambda t: abs(t - tgt))
    if nxt <= last + 1:
        nxt = round(last + TARGET, 2)
    nxt = snap_out_of_duck(nxt)  # ダック内なら終端外へ(窓が最大~ダック長ぶん伸びる)
    if nxt >= TOTAL:
        break
    bounds.append(nxt)
bounds.append(round(TOTAL, 3))

# CI並列化: env WIN_FROM/WIN_TO で窓インデックスをスライス(既定=全窓)。
import os
_wins = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]
_lo = int(os.environ.get("WIN_FROM", 0) or 0)
_hi = int(os.environ.get("WIN_TO", len(_wins)) or len(_wins))
for s, e in _wins[_lo:_hi]:
    print(f"{s}:{e}")
