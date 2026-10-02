"""那須川天心 vs 井上拓真2 採点検証まとめ index.html 生成（1920x1080・窓分割対応）。

前景の核＝「全12ラウンド × ジャッジ3人」の採点グリッド。公開された 4R/8R の採点・最終スコア・
公式採点表の内訳を突き合わせて復元したもので、競合（ニュース系チャンネル）がやっていない。
背景＝ビート別 bgvid を1本に連結したパート（<video>要素を40未満に保つ）。
env: HF_WIN_START / HF_WIN_END / HF_VISUAL_ONLY / HF_OUTNAME
"""
from __future__ import annotations
import json, html, os, re as _re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "tenshin_takuma2"
TPL = ROOT / "hyperframes" / "templates" / EP
TIM = json.load(open(ROOT / "subtitles" / "out" / EP / "timings.json", encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)
BEATS = TIM["beats"]
CHAPS = TIM["chapters"]

W0 = float(os.environ.get("HF_WIN_START") or 0)
_w1 = os.environ.get("HF_WIN_END")
W1 = float(_w1) if _w1 else COMP
VISUAL_ONLY = os.environ.get("HF_VISUAL_ONLY") == "1"
WIN = round(W1 - W0, 2)
OUTNAME = os.environ.get("HF_OUTNAME", "index.html")
def T(t): return round(t - W0, 3)
def OV(t0, t1): return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)
def esc(s): return html.escape(s)
BS = {b["id"]: b["start"] for b in BEATS}
BE = {b["id"]: b["end"] for b in BEATS}
def bs(bid): return BS[bid]
def be(bid): return BE[bid]

# ---- 字幕表示置換（読みかな→算用数字/英字/正式表記）------------------------
# ★長いキーを先に置換する（disp() が長さ順にソートして適用）
DISP = {
    # スコア
    "ひゃくじゅうよんたいひゃくじゅうさん": "114-113",
    "ひゃくじゅうろくたいひゃくじゅういち": "116-111",
    "ひゃくじゅうろくたいひゃくじゅうに": "116-112",
    "ひゃくじゅうななたいひゃくじゅういち": "117-111",
    "ひゃくじゅうごたいひゃくじゅうに": "115-112",
    "ななじゅうななたいななじゅうよん": "77-74",
    "ななじゅうろくたいななじゅうご": "76-75",
    "さんじゅうきゅうたいさんじゅうなな": "39-37",
    "さんじゅうはちたいさんじゅうはち": "38-38",
    "よんじゅうたいさんじゅうろく": "40-36",
    "はちはつたいはちはつ": "8発対8発",
    "じゅうごはつたいごはつ": "15発対5発",
    "じゅうきゅうはつたいじゅっぱつ": "19発対10発",
    "ごはつたいじゅうはちはつ": "5発対18発",
    "じゅうたいはち": "10-8",
    "さんたいゼロ": "3-0",
    # ラウンド
    "じゅうにラウンド": "12ラウンド", "じゅういちラウンド": "11ラウンド",
    "じゅうラウンド": "10ラウンド", "きゅうラウンド": "9ラウンド", "はちラウンド": "8ラウンド",
    "ななラウンド": "7ラウンド", "ろくラウンド": "6ラウンド", "ごラウンド": "5ラウンド",
    "よんラウンド": "4ラウンド", "さんラウンド": "3ラウンド", "にラウンド": "2ラウンド",
    "いちラウンド": "1ラウンド",
    # 日付・年
    "にせん にじゅうろくねんくがつにじゅうななにち": "2026年9月27日",
    "にせん にじゅうごねんじゅういちがつにじゅうよっか": "2025年11月24日",
    "二千二十六年五月二日": "2026年5月2日",
    "さんびゃくななにち": "307日", "やくさんじゅうねん": "約30年", "やくにじゅうびょう": "約20秒",
    # 数値
    "よんひゃくきゅうじゅうはっぱつ": "498発", "よんひゃくにじゅっぱつ": "420発",
    "ひゃくにじゅういっぱつ": "121発", "きゅうじゅうきゅうはつ": "99発",
    "ななじゅうはっぱつ": "78発", "さんじゅうろっぱつ": "36発", "はちじゅうななはつ": "87発",
    "にじゅうごはつ": "25発", "ひゃくいっぱつ": "101発",
    "じゅうにはつ": "12発", "じゅっぱつ": "10発", "ななはつ": "7発", "はちはつ": "8発",
    "にはつ": "2発", "ごはつ": "5発", "いっぱつ": "1発", "じゅうきゅうはつ": "19発",
    "にじゅうはちてんはちパーセント": "28.8%", "じゅうきゅうてんきゅうパーセント": "19.9%",
    "じゅうポイントマスト": "10ポイントマスト", "じゅうポイント": "10ポイント",
    "きゅうポイント": "9ポイント", "はちポイント": "8ポイント",
    "ごポイント": "5ポイント", "よんポイント": "4ポイント", "さんポイント": "3ポイント",
    "にポイント": "2ポイント", "いちポイント": "1ポイント",
    "じゅうさんど": "13度", "ごかいきゅうせいは": "5階級制覇", "にかいきゅうせいは": "2階級制覇",
    "さんぷん": "3分", "にばい": "2倍", "いちい": "1位", "にどめ": "2度目",
    "だいいっせん": "第1戦", "さんにん": "3人", "ふたり": "2人", "ひとり": "1人",
    "よっつ": "4つ", "みっつ": "3つ", "ろくつ": "6つ", "ごつ": "5つ", "ふたつ": "2つ", "ひとつ": "1つ",
}
def disp(t):
    for k in sorted(DISP, key=len, reverse=True):
        t = t.replace(k, DISP[k])
    return t

# ---- 出典ラベル（bg_segments.json をそのまま使い、素材と表示のズレを防ぐ）----
_SEG = json.load(open(TPL / "assets" / "bg_segments.json", encoding="utf-8"))
SRC = {x["beat"]: x["label"] for x in _SEG}

# =============================================================================
# ★全12ラウンド × ジャッジ3人の採点グリッド（復元値）
#   公開情報: 4R=40-36/39-37/38-38, 8R=77-74×2/76-75(天心), 最終=114-113/116-111×2,
#             各ラウンドの内訳(3-0 or 2-1) → 3人のカードは一意に定まる。
#   T=井上拓真 / N=那須川天心
# =============================================================================
CARD = {       # round: (judgeA 114-113, judgeB 116-111, judgeC 116-111), CompuBox 拓真:天心
    1:  ("T", "T", "T", "2", "2"),
    2:  ("N", "N", "T", "7", "8"),
    3:  ("T", "T", "T", "11", "5"),
    4:  ("N", "T", "T", "7", "4"),
    5:  ("T", "T", "T", "15", "5"),
    6:  ("N", "T", "N", "10", "12"),
    7:  ("N", "N", "N", "5", "18"),
    8:  ("T", "T", "T", "18", "9"),
    9:  ("T", "T", "T", "9", "6"),
    10: ("T", "N", "T", "10", "12"),
    11: ("T", "T", "T", "19", "10"),
    12: ("N", "T", "N", "8", "8"),
}
UNANI_T = [1, 3, 5, 8, 9, 11]      # 3人とも井上拓真
UNANI_N = [7]                      # 3人とも那須川天心（ダウンの7R）
SPLIT = [2, 4, 6, 10, 12]          # 割れたラウンド

GRID_TOP, TTL_H, HEAD_H, ROW_H, BRD = 62, 52, 56, 44, 1
ROW_PITCH = ROW_H + BRD
ROW0_TOP = GRID_TOP + 2 + TTL_H + HEAD_H          # .grid の border2px + タイトル + ヘッダ行


def grid_html(gid, mark_t=False, mark_n=False, mark_split=False, show_cb=False, judge_a=False):
    """採点グリッド1枚。mark_* で色を付ける状態違いを作る（opacityだけで切り替える）。"""
    cols = ['<div class="gc gr">R</div>',
            f'<div class="gc {"gj on" if judge_a else "gj"}">ジャッジA<span>114-113</span></div>',
            '<div class="gc gj">ジャッジB<span>116-111</span></div>',
            '<div class="gc gj">ジャッジC<span>116-111</span></div>']
    if show_cb:
        cols.append('<div class="gc gb">CompuBox<span>拓真 : 天心</span></div>')
    rows = [f'<div class="grow ghead">{"".join(cols)}</div>']
    for r in range(1, 13):
        a, b, c, ht, hn = CARD[r]
        cls = ""
        if mark_t and r in UNANI_T: cls = " mt"
        if mark_n and r in UNANI_N: cls = " mn"
        if mark_split and r in SPLIT: cls = " ms"
        cells = [f'<div class="gc gr">{r}</div>']
        for k, v in enumerate((a, b, c)):
            jc = "jt" if v == "T" else "jn"
            extra = " dim" if (judge_a and k > 0) else ""
            nm = "拓真" if v == "T" else "天心"
            if r == 7:
                nm += " 10-8"
            cells.append(f'<div class="gc {jc}{extra}">{nm}</div>')
        if show_cb:
            w = "cbn" if (hn != "—" and ht != "—" and int(hn) > int(ht)) else ("cbe" if ht == hn else "cbt")
            cells.append(f'<div class="gc gb {w}">{ht} : {hn}</div>')
        rows.append(f'<div class="grow{cls}">{"".join(cells)}</div>')
    w = 1000 if show_cb else 820
    return (f'<div class="grid{" wide" if show_cb else ""}" id="{gid}" style="width:{w}px">'
            f'<div class="gttl">全12ラウンド　ジャッジ3人の採点</div>{"".join(rows)}</div>')


# 表示状態（beat_from, beat_to, パラメータ）
GRIDS = [
    ("gA", "5_cards05", "5_cards07", dict(mark_t=True)),
    ("gB", "5_cards08", "5_cards09", dict(mark_t=True, mark_n=True)),
    ("gC", "5_cards10", "5_cards11", dict(mark_t=True, mark_n=True, mark_split=True)),
    ("gD", "5_cards12", "5_cards27", dict(mark_t=True, mark_n=True, mark_split=True, show_cb=True)),
    ("gE", "7_last403", "7_last409", dict(mark_n=True, mark_split=True, judge_a=True)),
    ("gF", "9_end02", "9_end04", dict(mark_t=True, mark_n=True, mark_split=True)),
]
# gD の中で、ナレが触れているラウンドを1行だけ光らせる（opacityのみのオーバーレイ）
ROWHI = [
    ("5_cards12", 1), ("5_cards13", 1), ("5_cards14", 2), ("5_cards15", 2),
    ("5_cards16", 6), ("5_cards17", 10), ("5_cards18", 12),
    ("5_cards22", 11), ("5_cards24", 7),
]

# =============================================================================
# パネル（カード）: (beat_from, beat_to, pid, pos, html)
# =============================================================================
def panel_score(ttl, rows, note=""):
    r = "".join(f'<div class="prow"><span class="pk">{esc(k)}</span>'
                f'<span class="pv">{esc(v)}</span></div>' for k, v in rows)
    n = f'<div class="pnote">{esc(note)}</div>' if note else ""
    return f'<div class="pttl">{esc(ttl)}</div>{r}{n}'


def panel_quote(who, body, meta=""):
    m = f'<div class="qmeta">{esc(meta)}</div>' if meta else ""
    fs = 40 if len(body) <= 48 else 35 if len(body) <= 86 else 30
    return (f'<div class="qwho">{esc(who)}</div>'
            f'<div class="qbody" style="font-size:{fs}px">{esc(body)}</div>{m}')


def panel_big(lines):
    return "".join(f'<div class="bl{i}">{esc(t)}</div>' for i, t in enumerate(lines))


PANELS = [
    # --- 冒頭 ---
    ("0_intro01", "0_intro02", "p_off", "cen", panel_score("公式採点（3-0 井上拓真）", [
        ("サザーランド", "114 - 113"), ("パーマー", "116 - 111"), ("ペラヨ", "116 - 111")],
        "那須川天心は7ラウンドにダウンを奪っている")),
    ("0_intro03", "0_intro04", "p_op8", "cen", panel_score("8ラウンド終了時点の公開採点", [
        ("ジャッジ2人", "77 - 74　井上拓真"), ("ジャッジ1人", "76 - 75　那須川天心")],
        "1人のカードでは、挑戦者が1ポイント上にいた")),
    ("0_intro06", "0_intro06", "p_title", "title", panel_big(
        ["採点は", "なぜ割れたのか", "那須川天心 vs 井上拓真2　全12ラウンド検証"])),
    # --- 第1戦/第2戦の結果 ---
    ("1_what04", "1_what05", "p_f1", "rt", panel_score("第1戦　2025年11月24日", [
        ("ジャッジ2人", "116 - 112"), ("ジャッジ1人", "117 - 111")],
        "WBC世界バンタム級王座決定戦／井上拓真 3-0")),
    ("1_what13", "1_what13", "p_f2", "rt", panel_score("第2戦　2026年9月27日", [
        ("最終スコア", "114-113 / 116-111 ×2")], "井上拓真 3-0　2度目の防衛成功")),
    ("1_what14", "1_what15", "p_q1", "rt", panel_quote(
        "那須川天心", "本当にボクシングで負けた感じ。ポイントゲーム。負けた気していないんですよ", "試合後の会見より")),
    # --- オープンスコアリング ---
    ("2_open04", "2_open07", "p_op4", "cen", panel_score("4ラウンド終了時点の公開採点", [
        ("ジャッジC", "40 - 36　フルマーク"), ("ジャッジB", "39 - 37"), ("ジャッジA", "38 - 38　ドロー")],
        "同じ4ラウンドで、3人が3通りに分かれた")),
    ("2_open09", "2_open10", "p_q2", "rt", panel_quote(
        "浜田剛史", "4ラウンドの採点を聞いて、取られているのかと。那須川天心のこのやり方では"
                   "ポイントがつかないことに焦りがあったのは事実です", "帝拳プロモーション代表／一夜明け会見")),
    ("2_open12", "2_open13", "p_q3", "rt", panel_quote(
        "木村悠", "ジャッジにどう見えているかを考えさせてしまう。試合の流れそのものが変わる",
        "元WBC世界ライトフライ級王者")),
    # --- s6 採点基準 / CompuBox ---
    ("6_criteria05", "6_criteria07", "p_cri", "cen", panel_score("JBCが示す採点の4基準", [
        ("1", "有効打（クリーンヒット）"), ("2", "攻撃性（アグレッシブネス）"),
        ("3", "リングジェネラルシップ"), ("4", "ディフェンス")],
        "手数の多さは、この中に入っていない")),
    ("6_criteria08", "6_criteria16", "p_cb", "rt", panel_score("CompuBox（全12ラウンド）", [
        ("総パンチ", "井上 420　/　那須川 498"),
        ("ヒット", "井上 121　/　那須川 99"),
        ("的中率", "井上 28.8% / 那須川 19.9%"),
        ("パワーパンチ", "井上 101　/　那須川 87"),
        ("ボディ", "井上 25　/　那須川 36")],
        "打ったのは那須川、当てたのは井上、ボディは那須川")),
    ("6_criteria18", "6_criteria19", "p_q4", "rt", panel_quote(
        "浜田剛史", "採点基準は約30年になりますけど、ボクシング関係者の間でも真っ二つに分かれることがある",
        "帝拳プロモーション代表")),
    # --- s7 勝敗が決まった3分 ---
    ("7_last400", "7_last402", "p_op8b", "cen", panel_score("8ラウンド終了時点の公開採点", [
        ("ジャッジB・C", "77 - 74　井上拓真"), ("ジャッジA", "76 - 75　那須川天心")],
        "この時点では、1人が挑戦者を上に置いていた")),
    ("7_last410", "7_last412", "p_11r", "rt", panel_score("11ラウンドのヒット数", [
        ("井上拓真", "19発"), ("那須川天心", "10発")], "3人のジャッジが全員、井上拓真につけた")),
    # --- s9 ---
    ("9_end05", "9_end07", "p_q5", "rt", panel_quote(
        "那須川天心", "難しすぎます。倒すだけがボクシングじゃないんだなと。経験、実力不足です",
        "試合後の会見より")),
]

CHAP_SUB = {}   # timings 側の title/sub をそのまま使う

# ---- 字幕分割（≤2行・各≤27全角）------------------------------------------
PUNCT = set("、。，．！？")
def zwidth(s):
    w = 0
    for ch in s:
        w += 0.55 if (ch.isascii() and (ch.isalnum() or ch in " .,'-〜!?%:")) else 1.0
    return w
def wrap_two(text, maxw):
    segs = [s for s in _re.split("(?<=、)", text) if s]
    best = None
    for i in range(1, len(segs)):
        l1 = "".join(segs[:i]); l2 = "".join(segs[i:])
        if zwidth(l1) <= maxw and zwidth(l2) <= maxw:
            if best is None or abs(zwidth(l1) - zwidth(l2)) < best[0]:
                best = (abs(zwidth(l1) - zwidth(l2)), l1, l2)
    if best:
        return (best[1], best[2])
    if zwidth(text) <= maxw * 2:
        target = int(len(text) * maxw / max(zwidth(text), 1))
        KATA = _re.compile(r'[ァ-ヴーｦ-ﾟA-Za-z0-9・%]')
        def inside_word(c):
            return 0 < c < len(text) and bool(KATA.match(text[c-1])) and bool(KATA.match(text[c]))
        def ok(c):
            lim = min(maxw + 4.5, 27.0)
            return (0 < c < len(text) and not inside_word(c) and text[c] not in PUNCT
                    and zwidth(text[:c]) <= lim and zwidth(text[c:]) <= lim)
        # 句読点の直後を最優先、次に助詞の直後、それ以外は最後
        PART = set("はがをにへとでものやねよも")
        cands = []
        for c in range(1, len(text)):
            if not ok(c):
                continue
            p = 0 if text[c-1] in PUNCT else (6 if text[c-1] in PART else 10)
            cands.append((p + abs(c - target), c))
        if cands:
            return (text[:min(cands)[1]], text[min(cands)[1]:])
        c2 = max(1, min(len(text) - 1, target))
        while c2 > 1 and zwidth(text[:c2]) > 27.0:
            c2 -= 1
        return (text[:c2], text[c2:])
    return None
def fits_two(text, maxw):
    return zwidth(text) <= maxw or wrap_two(text, maxw) is not None
def split_two_lines(text, maxw=23.0):
    parts = [p for p in _re.split("(?<=[、。])", text) if p]
    cues, cur = [], ""
    for p in parts:
        cand = cur + p
        if fits_two(cand, maxw):
            cur = cand
        else:
            if cur: cues.append(cur)
            cur = p
    if cur:
        # 末尾の極小断片は直前へ吸収する
        if cues and zwidth(cur) <= 6.0 and fits_two(cues[-1] + cur, maxw):
            cues[-1] += cur
        else:
            cues.append(cur)
    return cues or [text]
def sub_lines(text, maxw=23.0):
    if zwidth(text) <= maxw:
        return [text]
    w = wrap_two(text, maxw)
    return [w[0], w[1]] if w else [text]

# ---- 背景（連結済みパート）--------------------------------------------------
BG = [(b["start"], b["end"], b["id"], SRC.get(b["id"], "")) for b in BEATS]
BG.sort(key=lambda e: e[0])
_bg2 = []
for i, (t0, t1, fn, sl) in enumerate(BG):
    if i + 1 < len(BG):
        t1 = round(BG[i + 1][0] + 0.08, 3)
    _bg2.append((round(t0, 3), round(t1, 3), fn, sl))
BG = _bg2
BG[-1] = (BG[-1][0], COMP, BG[-1][2], BG[-1][3])

bg_divs, bg_tws, src_divs = [], [], []
PARTS = json.load(open(TPL / "assets" / "bgvid_full" / "parts.json", encoding="utf-8"))
for k, pt in enumerate(PARTS):
    pt0, pt1 = pt["t0"], pt["t1"]
    if not OV(pt0, pt1):
        continue
    bid = f"bgp{k}"
    ds = max(0.0, T(pt0))
    ms = max(0.0, W0 - pt0)
    dur = min(pt["media_len"] - ms, (W1 - max(pt0, W0)) + 0.6)
    if dur <= 0.05:
        continue
    bg_divs.append(
        f'<div class="bgseg" id="{bid}" style="z-index:{k + 1};opacity:1">'
        f'<video id="{bid}-v" src="assets/bgvid_full/{pt["file"]}" muted playsinline '
        f'data-layout-allow-overflow data-start="{ds:.2f}" data-duration="{dur:.2f}" '
        f'data-media-start="{ms:.2f}" data-track-index="{10 + k}"></video></div>')
    bg_tws.append(f"tl.set('#{bid}',{{opacity:1}},0);")

for i, (t0, t1, fn, srcl) in enumerate(BG):
    if not OV(t0, t1) or not srcl:
        continue
    if (min(t1, W1) - max(t0, W0)) <= 0.6:
        continue
    vt0, vt1 = T(t0), T(t1)
    sid = f"src{i}"
    src_divs.append(f'<div class="srclab" id="{sid}">{esc(srcl)}</div>')
    if vt0 + 0.3 < 0:
        bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:1}},{{opacity:1,duration:.01}},0.00);")
    else:
        bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{vt0 + 0.3:.2f});")
    bg_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{vt1 - 0.25:.2f});")

# ---- 章タグ ----
chap_divs, chap_tws, chap_audio = [], [], []
for j, c in enumerate(CHAPS):
    st = c["start"]
    if not OV(st, st + 4.2):
        continue
    cid = f"chap{j}"
    sub = f'<div class="chttl">{esc(c["sub"])}</div>' if c.get("sub") else ""
    chap_divs.append(f'<div class="chaptag" id="{cid}"><div class="chnum">{esc(c["title"])}</div>{sub}</div>')
    chap_tws.append(f"tl.fromTo('#{cid}',{{opacity:0}},{{opacity:1,duration:.45}},{T(st + 0.1):.2f});")
    chap_tws.append(f"tl.to('#{cid}',{{opacity:0,duration:.4}},{T(st + 3.8):.2f});")
    if not VISUAL_ONLY:
        chap_audio.append(f'<audio id="chs{j}" src="assets/se/chapter.wav" '
                          f'data-start="{T(st + 0.1):.2f}" data-track-index="{200 + j}" data-volume="0.5"></audio>')

# ---- 採点グリッド ----
grid_divs, grid_tws = [], []
for gid, b0, b1, kw in GRIDS:
    t0, t1 = bs(b0) - 0.25, be(b1) + 0.15
    if not OV(t0, t1):
        continue
    cont = T(t0) <= 0.02
    op = ' style="opacity:1"' if cont else ''
    gh = grid_html(gid, **kw)
    if cont:
        gh = gh.replace(f'id="{gid}" style="width:', f'id="{gid}" data-cont="1" style="opacity:1;width:')
    grid_divs.append(gh)
    if cont:
        grid_tws.append(f"tl.fromTo('#{gid}',{{opacity:1}},{{opacity:1,duration:.01}},0);")
    else:
        grid_tws.append(f"tl.fromTo('#{gid}',{{opacity:0}},{{opacity:1,duration:.35}},{T(t0):.2f});")
    grid_tws.append(f"tl.to('#{gid}',{{opacity:0,duration:.3}},{T(t1):.2f});")

for n, (bid, r) in enumerate(ROWHI):
    t0, t1 = bs(bid) + 0.1, be(bid) - 0.05
    if not OV(t0, t1):
        continue
    hid = f"rh{n}"
    top = ROW0_TOP + (r - 1) * ROW_PITCH
    cont = T(t0) <= 0.02
    _op = "opacity:1;" if cont else ""
    grid_divs.append(f'<div class="rowhi" id="{hid}" style="{_op}top:{top}px"></div>')
    if cont:
        grid_tws.append(f"tl.fromTo('#{hid}',{{opacity:1}},{{opacity:1,duration:.01}},0);")
    else:
        grid_tws.append(f"tl.fromTo('#{hid}',{{opacity:0}},{{opacity:1,duration:.22}},{T(t0):.2f});")
    grid_tws.append(f"tl.to('#{hid}',{{opacity:0,duration:.2}},{T(t1):.2f});")

# ---- パネル ----
pan_divs, pan_tws = [], []
for b0, b1, pid, pos, inner in PANELS:
    t0, t1 = bs(b0) + 0.15, be(b1) - 0.1
    if not OV(t0, t1):
        continue
    cont = T(t0) <= 0.02
    op = ' style="opacity:1"' if cont else ''
    pan_divs.append(f'<div class="panel {pos}" id="{pid}"{op}>{inner}</div>')
    if cont:
        pan_tws.append(f"tl.fromTo('#{pid}',{{opacity:1}},{{opacity:1,duration:.01}},0);")
    else:
        pan_tws.append(f"tl.fromTo('#{pid}',{{opacity:0}},{{opacity:1,duration:.4}},{T(t0):.2f});")
    pan_tws.append(f"tl.to('#{pid}',{{opacity:0,duration:.3}},{T(t1):.2f});")

# ---- プロの採点リスト（s3 で1行ずつ積み上がる）------------------------------
SCORELIST = [
    ("3_pros01", "具志堅用高", "天心 2ポイント勝ち", "n"),
    ("3_pros03", "内藤大助", "4R 38-38", "e"),
    ("3_pros05", "赤穂亮", "4R 39-37", "t"),
    ("3_pros06", "椎野大輝", "4R 38-38 〜 39-37", "e"),
    ("3_pros09", "内山高志", "115-112 拓真", "t"),
    ("3_pros10", "川尻達也", "115-112 拓真", "t"),
    ("3_pros11", "亀田大毅", "114-113 拓真", "t"),
    ("3_pros12", "京口紘人", "116-111 拓真", "t"),
    ("3_pros13", "渡嘉敷・竹原・畑山", "3ポイント差 拓真", "t"),
]
sl_divs, sl_tws = [], []
SL_END = be("3_pros17") - 0.2
for n, (bid, who, sc, side) in enumerate(SCORELIST):
    t0 = bs(bid) + 0.6
    if not OV(t0, SL_END):
        continue
    sid = f"sl{n}"
    cont = T(t0) <= 0.02
    _op = "opacity:1;" if cont else ""
    sl_divs.append(f'<div class="slrow {side}" id="{sid}" style="{_op}top:{40 + n * 62}px">'
                   f'<span class="slw">{esc(who)}</span><span class="sls">{esc(sc)}</span></div>')
    if cont:
        sl_tws.append(f"tl.fromTo('#{sid}',{{opacity:1}},{{opacity:1,duration:.01}},0);")
    else:
        sl_tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.3}},{T(t0):.2f});")
    sl_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{T(SL_END):.2f});")

# ---- 字幕 ----
sub_divs, sub_tws = [], []
sidx = 0
for b in BEATS:
    if not b.get("text", "").strip():
        continue
    text = disp(b["text"])
    cues = split_two_lines(text)
    dur = b["end"] - b["start"]
    wsum = sum(zwidth(c) for c in cues) or 1.0
    acc = 0.0
    for cue in cues:
        cs = b["start"] + dur * acc / wsum
        acc += zwidth(cue)
        ce = b["start"] + dur * acc / wsum
        if not OV(cs, ce):
            continue
        lines = sub_lines(cue)
        inner = "<br>".join(esc(l) for l in lines)
        did = f"sub{sidx}"; sidx += 1
        sub_divs.append(f'<div class="subt" id="{did}">{inner}</div>')
        if T(cs) < 0:
            sub_tws.append(f"tl.fromTo('#{did}',{{opacity:1}},{{opacity:1,duration:.01}},0);")
        else:
            sub_tws.append(f"tl.fromTo('#{did}',{{opacity:0}},{{opacity:1,duration:.18}},{T(cs):.2f});")
        sub_tws.append(f"tl.to('#{did}',{{opacity:0,duration:.14}},{T(ce - 0.05):.2f});")

def J(items, ind="      "):
    return "\n".join(ind + x for x in items)

AUDIO_BLOCK = ("" if VISUAL_ONLY else
    '<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="60" data-volume="1"></audio>\n'
    '    <audio id="bgm" src="assets/audio/bgm.m4a" data-start="0" data-track-index="61" data-volume="0.045"></audio>')


# ---- 幅検算（セーフ幅超過でビルドを止める）----------------------------------
def _w(t, px):
    return sum(px * 0.55 if (ch.isascii() and ch != "　") else px for ch in t)
def _audit_widths(html_text):
    import html as _H
    lim = [("pv", 38, 504), ("pk", 27, 250), ("pttl", 31, 776), ("pnote", 25, 776),
           ("slw", 30, 360), ("sls", 30, 400), ("bl0", 72, 1400), ("bl1", 118, 1400),
           ("bl2", 34, 1400), ("gttl", 26, 980), ("chnum", 86, 1760), ("chttl", 36, 1760)]
    bad = []
    for cls, px, mx in lim:
        for t in _re.findall(rf'class="{cls}"[^>]*>(.*?)<', html_text):
            t = _H.unescape(t)
            if _w(t, px) > mx:
                bad.append(f"{cls}: {int(_w(t,px))}px > {mx}px  {t[:40]}")
    if bad:
        raise SystemExit("幅オーバー:\n  " + "\n  ".join(bad))

HTML = f"""<!doctype html>
<!-- 那須川天心 vs 井上拓真2 採点検証まとめ 1920x1080 -->
<html>
<head>
<meta charset="utf-8">
<style>
  @font-face{{font-family:"Mincho";src:url("assets/fonts/GokubutoMincho.ttf");}}
  @font-face{{font-family:"JPHeavy";src:url("assets/fonts/SourceHanSansJP-Heavy.otf");}}
  @font-face{{font-family:"JPMed";src:url("assets/fonts/SourceHanSansJP-Medium.otf");}}
  :root{{
    --white:#fff; --yellow:#ffd93a; --red:#ff4545; --blue:#4fb9ff; --ink:#07090f;
    --edge:drop-shadow(3px 0 0 var(--ink)) drop-shadow(-3px 0 0 var(--ink)) drop-shadow(0 3px 0 var(--ink))
           drop-shadow(0 -3px 0 var(--ink)) drop-shadow(0 6px 14px rgba(0,0,0,.8));
    --edge-sm:drop-shadow(0 0 2px var(--ink)) drop-shadow(1px 1px 1px var(--ink)) drop-shadow(0 2px 6px rgba(0,0,0,.85));
  }}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  #root{{position:absolute;inset:0;overflow:hidden;background:#05060a;font-family:"JPMed";}}
  .bgseg{{position:absolute;inset:0;opacity:0;overflow:hidden;}}
  .bgseg video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform:translateZ(0);backface-visibility:hidden;}}
  .veil{{position:absolute;inset:0;z-index:300;pointer-events:none;
        background:linear-gradient(180deg,rgba(0,0,0,.52) 0%,transparent 15%,transparent 56%,rgba(0,0,0,.58) 82%,rgba(0,0,0,.84) 100%);}}
  .wm{{position:absolute;z-index:360;left:36px;top:28px;font-family:"JPHeavy";font-size:28px;color:#fff;
      letter-spacing:.04em;filter:var(--edge-sm);opacity:.88;}}
  .srclab{{position:absolute;z-index:340;left:40px;bottom:22px;font-family:"JPMed";font-size:22px;color:#eaeaea;opacity:0;
        background:rgba(0,0,0,.55);border-left:4px solid var(--yellow);padding:6px 14px;border-radius:3px;filter:var(--edge-sm);}}
  .subt{{position:absolute;z-index:350;left:0;right:0;bottom:118px;text-align:center;opacity:0;
        font-family:"JPHeavy";font-size:45px;line-height:1.34;color:#fff;filter:var(--edge);
        letter-spacing:.01em;white-space:pre-line;padding:0 90px;}}

  /* 章タグ */
  .chaptag{{position:absolute;z-index:320;left:0;right:0;top:34%;text-align:center;opacity:0;}}
  .chaptag .chnum{{font-family:"Mincho";font-size:86px;color:#fff;letter-spacing:.06em;
        text-shadow:0 0 0 #000,4px 0 0 #07090f,-4px 0 0 #07090f,0 4px 0 #07090f,0 -4px 0 #07090f,
                    3px 3px 0 #07090f,-3px 3px 0 #07090f,3px -3px 0 #07090f,-3px -3px 0 #07090f,0 10px 28px rgba(0,0,0,.85);}}
  .chaptag .chttl{{font-family:"JPHeavy";font-size:36px;color:var(--yellow);margin-top:18px;letter-spacing:.04em;
        text-shadow:2px 2px 0 #07090f,-2px 2px 0 #07090f,2px -2px 0 #07090f,-2px -2px 0 #07090f,0 6px 18px rgba(0,0,0,.85);}}

  /* 採点グリッド */
  .grid{{position:absolute;z-index:332;right:62px;top:{GRID_TOP}px;opacity:0;
        background:rgba(8,11,18,.82);border:2px solid rgba(255,255,255,.16);border-radius:14px;
        padding:0 0 10px;box-shadow:0 20px 60px rgba(0,0,0,.7);overflow:hidden;}}
  .grid .gttl{{font-family:"JPHeavy";font-size:26px;color:#fff;background:rgba(255,255,255,.08);
        height:{TTL_H}px;line-height:{TTL_H}px;text-align:center;letter-spacing:.06em;}}
  .grow{{display:flex;align-items:stretch;height:{ROW_H}px;border-top:{BRD}px solid rgba(255,255,255,.09);}}
  .grow.ghead{{height:{HEAD_H}px;border-top:none;}}
  .gc{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
       font-family:"JPMed";font-size:25px;color:#e9edf4;line-height:1.15;}}
  .gc.gr{{flex:0 0 68px;font-family:"JPHeavy";color:#9fb0c8;font-size:25px;}}
  .ghead .gc{{font-family:"JPHeavy";font-size:22px;color:#cfe0f5;}}
  .ghead .gc span{{font-size:17px;color:#8fa4bd;font-family:"JPMed";margin-top:2px;}}
  .ghead .gc.on{{color:var(--yellow);}}
  .gc.jt{{color:#bcd4ea;}} .gc.jn{{color:#ffe07a;font-family:"JPHeavy";}}
  .gc.dim{{opacity:.28;}}
  .gc.gb{{flex:0 0 190px;font-family:"JPHeavy";font-size:25px;color:#cdd7e4;}}
  .gc.gb.cbn{{color:#ffd166;}} .gc.gb.cbe{{color:#9fe8c9;}}
  .grow.mt{{background:rgba(79,185,255,.16);}}
  .grow.mn{{background:rgba(255,69,69,.22);}}
  .grow.ms{{background:rgba(255,217,58,.17);}}
  .rowhi{{position:absolute;z-index:334;right:62px;width:1000px;height:{ROW_H}px;opacity:0;
        border:3px solid var(--yellow);border-radius:5px;box-shadow:0 0 22px rgba(255,217,58,.6);
        background:rgba(255,217,58,.10);}}

  /* パネル */
  .panel{{position:absolute;z-index:333;opacity:0;background:rgba(8,11,18,.86);
        border:2px solid rgba(255,255,255,.16);border-radius:16px;padding:26px 32px 24px;
        box-shadow:0 20px 56px rgba(0,0,0,.7);}}
  .panel.rt{{right:66px;top:120px;width:840px;}}
  .panel.cen{{left:50%;transform:translateX(-50%);top:150px;width:1060px;}}
  .panel .pttl{{font-family:"JPHeavy";font-size:31px;color:var(--yellow);margin-bottom:18px;letter-spacing:.04em;}}
  .panel .prow{{display:flex;align-items:baseline;gap:22px;padding:10px 0;border-top:1px solid rgba(255,255,255,.1);}}
  .panel .prow:first-of-type{{border-top:none;}}
  .panel .pk{{flex:0 0 250px;font-family:"JPMed";font-size:27px;color:#b9c7da;}}
  .panel .pv{{flex:1;font-family:"JPHeavy";font-size:38px;color:#fff;letter-spacing:.02em;}}
  .panel .pnote{{margin-top:18px;padding-top:14px;border-top:1px solid rgba(255,255,255,.12);
        font-size:25px;color:#ffd93a;font-family:"JPMed";}}
  .panel .qwho{{font-family:"JPHeavy";font-size:30px;color:#fff;background:#c62828;display:inline-block;
        padding:5px 18px;border-radius:6px;margin-bottom:16px;}}
  .panel .qbody{{font-family:"JPHeavy";color:#fff;line-height:1.5;}}
  .panel .qmeta{{margin-top:16px;padding-top:12px;border-top:1px solid rgba(255,255,255,.12);
        font-size:23px;color:#9fb0c8;}}
  /* 冒頭タイトル（大型文字は text-shadow で縁取り: filter の積層はCIで固まる） */
  .panel.title{{left:96px;top:300px;width:1400px;background:none;border:none;box-shadow:none;padding:0;}}
  .panel.title .bl0{{font-family:"Mincho";font-size:72px;color:#fff;letter-spacing:.08em;
        text-shadow:4px 0 0 #07090f,-4px 0 0 #07090f,0 4px 0 #07090f,0 -4px 0 #07090f,
                    3px 3px 0 #07090f,-3px 3px 0 #07090f,3px -3px 0 #07090f,-3px -3px 0 #07090f,0 12px 30px rgba(0,0,0,.9);}}
  .panel.title .bl1{{font-family:"Mincho";font-size:112px;color:var(--yellow);letter-spacing:.06em;margin-top:2px;
        text-shadow:5px 0 0 #07090f,-5px 0 0 #07090f,0 5px 0 #07090f,0 -5px 0 #07090f,
                    4px 4px 0 #07090f,-4px 4px 0 #07090f,4px -4px 0 #07090f,-4px -4px 0 #07090f,0 14px 34px rgba(0,0,0,.9);}}
  .panel.title .bl2{{font-family:"JPHeavy";font-size:34px;color:#fff;margin-top:22px;letter-spacing:.05em;
        text-shadow:2px 2px 0 #07090f,-2px 2px 0 #07090f,2px -2px 0 #07090f,-2px -2px 0 #07090f,0 6px 18px rgba(0,0,0,.9);}}

  /* プロの採点リスト */
  .slrow{{position:absolute;z-index:333;right:66px;width:820px;opacity:0;display:flex;align-items:center;gap:20px;
        background:rgba(8,11,18,.82);border-left:7px solid #7f8ca0;border-radius:8px;padding:12px 20px;
        box-shadow:0 10px 30px rgba(0,0,0,.55);}}
  .slrow.n{{border-left-color:var(--red);}} .slrow.t{{border-left-color:var(--blue);}}
  .slrow.e{{border-left-color:var(--yellow);}}
  .slrow .slw{{flex:0 0 360px;font-family:"JPHeavy";font-size:30px;color:#fff;}}
  .slrow .sls{{flex:1;font-family:"JPHeavy";font-size:30px;color:#ffe07a;text-align:right;}}
</style>
</head>
<body>
  <div id="root" data-composition-id="{EP}" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
{J(bg_divs,"    ")}

    {AUDIO_BLOCK}
{J(chap_audio,"    ")}

    <div class="veil"></div>
    <div class="wm">格闘ニュースラボ</div>
{J(src_divs,"    ")}
{J(grid_divs,"    ")}
{J(pan_divs,"    ")}
{J(sl_divs,"    ")}
{J(chap_divs,"    ")}
{J(sub_divs,"    ")}

    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({{paused:true}});
{J(bg_tws)}
{J(grid_tws)}
{J(pan_tws)}
{J(sl_tws)}
{J(chap_tws)}
{J(sub_tws)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['{EP}'] = tl;
    </script>
  </div>
</body>
</html>
"""
_audit_widths(HTML)
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} "
      f"bg={len(bg_divs)} grid={len(grid_divs)} panel={len(pan_divs)} slist={len(sl_divs)} subs={len(sub_divs)}")
