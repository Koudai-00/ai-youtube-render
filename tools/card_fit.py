"""大型テロップ/カード/タイトルの描画幅をビルド時に検算して見切れ・語中改行を防ぐ共有ヘルパー。

使い方（各動画のテンプレビルダーで、レンダー前に必ず呼ぶ）:
    from tools.card_fit import check_card_widths
    # font_px は実際にレンダーされるフォントpx(CSS既定 or 上書き)と一致させること
    check_card_widths(CARDS, FONT_PX)   # 超過があれば SystemExit でビルド停止

CARDS: [(start, end, type, data_dict), ...]
FONT_PX: {type: {field: px}}  例 {"title":{"l1":120,"l2":66}, "card":{"sub":44,"main":104}, ...}
"""
from __future__ import annotations

SAFE_W = 1760  # 画面幅1920 − 左右マージン目安。これを超える行は見切れ/CJK語中改行の原因。


def est_width(text: str, px: int) -> float:
    """描画幅の概算。全角(かな/漢字/カナ/全角記号)≈フォントpx、半角(英数記号空白)≈px×0.55。"""
    return sum((px * 0.55) if ch.isascii() else float(px) for ch in text)


def check_card_widths(cards, font_px, safe_w: int = SAFE_W) -> None:
    """各カード行が safe_w 以内か検算。超過があれば一覧を出して SystemExit。"""
    problems = []
    for entry in cards:
        typ = entry[2]; data = entry[3]
        for key, px in font_px.get(typ, {}).items():
            txt = data.get(key)
            if not txt:
                continue
            w = est_width(str(txt), px)
            if w > safe_w:
                problems.append(f"{typ}.{key} @{entry[0]}s 「{txt}」 ≈{w:.0f}px > {safe_w}px")
    if problems:
        raise SystemExit(
            "【カード幅超過】見切れ/語中改行の原因。文言短縮かフォント縮小か明示改行で修正:\n  "
            + "\n  ".join(problems)
        )
    print(f"カード幅検算: OK (全{sum(len(c[3]) for c in cards)}項目, 各行 <= {safe_w}px)")
