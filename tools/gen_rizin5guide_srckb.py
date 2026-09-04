# -*- coding: utf-8 -*-
"""rizin5_guide の src_kb.json(出典ラベル + KenBurns対象)を PLAN から自動生成する。
   出典は「実際に使っている素材」から機械的に決まるので、PLAN変更時のラベルずれを防げる。"""
from __future__ import annotations
import importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bg", ROOT / "tools" / "build_rizin5guide_bg.py")
bg = importlib.util.module_from_spec(spec)
sys.modules["bg"] = bg
spec.loader.exec_module(bg)

# 素材ファイル名 → 出典ラベル（実素材の配信元）
SRC_OF_CLIP = {
    # RIZIN公式の試合
    "shaydullaev_kleber": "出典: RIZIN (試合映像)", "shaydullaev_asakura": "出典: RIZIN (試合映像)",
    "shaydullaev_kubo": "出典: RIZIN (試合映像)", "kelamov_asakura": "出典: RIZIN (試合映像)",
    "satoshi_musaev": "出典: RIZIN (試合映像)", "satoshi_kelamov": "出典: RIZIN (試合映像)",
    "nomura_patricky": "出典: RIZIN (試合映像)", "dautbek_hagiwara": "出典: RIZIN (試合映像)",
    "yaman_asakura": "出典: RIZIN (試合映像)", "hiramoto_asakura": "出典: RIZIN (試合映像)",
    "saito_asakura": "出典: RIZIN (試合映像)", "takagi_hagiwara": "出典: RIZIN (試合映像)",
    "rena_debut": "出典: RIZIN (試合映像)", "rena_izawa": "出典: RIZIN (試合映像)",
    "takagi_kaiwen": "出典: RIZIN (試合映像)", "hiramoto_koji": "出典: RIZIN (試合映像)",
    "beynoah_recent": "出典: RIZIN (試合映像)", "ajmckee_satoshi": "出典: RIZIN (試合映像)",
    "aoki_highlight": "出典: RIZIN (試合映像)",
    "rena_intro": "出典: RIZIN (試合映像)", "kuzi_fight": "出典: RIZIN (試合映像)",
    "rena_other": "出典: RIZIN (試合映像)", "takagi_other": "出典: RIZIN (試合映像)",
    "saito_other": "出典: RIZIN (試合映像)", "yaman_other": "出典: RIZIN (試合映像)",
    "saito_intro": "出典: RIZIN (試合映像)", "dautbek_other": "出典: RIZIN (試合映像)",
    "dautbek_intro": "出典: RIZIN (試合映像)", "hiramoto_other": "出典: RIZIN (試合映像)",
    "hiramoto_intro": "出典: RIZIN (試合映像)", "satoshi_other": "出典: RIZIN (試合映像)",
    "nomura_other": "出典: RIZIN (試合映像)", "aoki_other": "出典: RIZIN (試合映像)",
    "usami_intro2": "出典: RIZIN (番組映像)", "ajmckee_pfl": "出典: PFL (試合映像)",
    "ajmckee_b263": "出典: Bellator (試合映像)",
    # 他団体
    "beynoah_highkick": "出典: RISE (試合映像)", "usami_peemai": "出典: RISE (試合映像)",
    "aoki_hansen": "出典: DREAM (試合映像)", "ajmckee_bellator": "出典: Bellator (試合映像)",
    # 提供(会見/練習/OP)
    "openworkout": "出典: RIZIN公式 公開練習", "opening": "出典: RIZIN公式 大会映像",
    "presser1": "出典: RIZIN公式 記者会見", "presser2": "出典: RIZIN公式 記者会見",
    "presser3": "出典: RIZIN公式 記者会見",
}
CARD_LABEL = "出典: RIZIN公式 対戦カード"

src, kb = {}, []
for bid, spec_ in bg.PLAN.items():
    if spec_ and spec_[0] == "SPLIT":
        names = [Path(spec_[1][0]).stem, Path(spec_[2][0]).stem]
        labels = []
        for n in names:
            L = SRC_OF_CLIP.get(n, "出典: RIZIN (試合映像)")
            if L not in labels: labels.append(L)
        # 2素材の出典をまとめて表示(重複は1つに)
        src[bid] = labels[0] if len(labels) == 1 else " / ".join(l.replace("出典: ", "") for l in labels)
        if len(labels) > 1: src[bid] = "出典: " + src[bid]
        continue
    p, ms, filt, kbf = spec_
    stem = Path(p).stem
    if stem.startswith("card_"):
        src[bid] = CARD_LABEL
        kb.append(bid)                      # 静止画カードはKenBurns対象
    else:
        src[bid] = SRC_OF_CLIP.get(stem, "出典: RIZIN (試合映像)")

out = ROOT / "hyperframes" / "templates" / "rizin5_guide" / "src_kb.json"
json.dump({"src": src, "kb": kb}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"wrote {out}  src={len(src)} kb={len(kb)}")
