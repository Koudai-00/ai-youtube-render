"""RIZIN.54 勝敗予想まとめ 横テンプレ(1920x1080)生成【ニュースまとめ型・中立】。
背景=画像(予想者サムネ/公式カード/パネリスト)＋動画(クレベル実写/Pexels)混在・Ken Burns。
オーバーレイ: 予想者ラベル(名前+予想)、パネリストカットアウト、Xカード(本人=実/一般=匿名)、集計カード、章5、DOM字幕、出典。
時間分割レンダー対応(HF_WIN_START/END, cont/cont_end)。中立=単一BGM。
"""
from __future__ import annotations
import json, os, sys, subprocess
from collections import Counter
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=None)
def clip_dur(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "hyperframes" / "templates" / "rizin54-yosou"
TIM = json.loads((ROOT / "subtitles" / "out" / "rizin54_yosou" / "timings.json").read_text(encoding="utf-8"))
BEATS = TIM["beats"]
SECS = {s["sec"]: s for s in TIM["sections"]}
SECORDER = [s["sec"] for s in TIM["sections"]]
TOTAL = TIM["total"]
DUR = round(TOTAL + 0.6, 2)
FADE = 0.5

WIN_START = float(os.environ.get("HF_WIN_START", "0") or "0")
WIN_END = float(os.environ.get("HF_WIN_END", "0") or "0")
WINDOWED = "HF_WIN_START" in os.environ or "HF_WIN_END" in os.environ
if not WINDOWED:
    WIN_START, WIN_END = 0.0, DUR


def _norm(s: str) -> str:
    return s.replace("、", "").replace("。", "").replace(" ", "").replace("　", "")


def beats_of(sec: str):
    return [b for b in BEATS if b["sec"] == sec]


def beat_at(sub: str):
    nsub = _norm(sub)
    for b in BEATS:
        if nsub in _norm(b["text"]):
            return b
    raise SystemExit(f"BEAT NOT FOUND: {sub}")


# ============ 背景レジストリ (img / vid) ============
TALK = ["talk_aoki", "talk_strasser", "talk_saito", "talk_kawajiri", "talk_jobin", "talk_izawa",
        "talk_ougikubo", "talk_matsushima", "talk_motoya", "talk_kanehara", "talk_ishiwatari",
        "talk_saeki", "talk_takagi", "talk_horiguchi"]
VID = {"kleber_face", "kleber_action", "px_cage", "px_ring", "px_crowd", "px_stage", *TALK}


def is_vid(name: str) -> bool:
    return name in VID


# 出典ラベル
SRC_OF = {
    "px_cage": "映像: Pexels", "px_ring": "映像: Pexels", "px_crowd": "映像: Pexels", "px_stage": "映像: Pexels",
    "kleber_face": "試合映像: RIZIN", "kleber_action": "試合映像: RIZIN",
}
for c in ["card_main_kleber_akimoto", "card_sato_mix", "card_ito_gaja", "card_majima_takeda",
          "card_goto_temirov", "card_hiramoto_jolly", "card_sudario_sakai",
          "panel_titlecard", "pred_official", "cut_seiya", "cut_ota", "cut_izawa", "cut_hinotori"]:
    SRC_OF[c] = "画像: RIZIN FF公式"
PRED_SRC = {
    "pred_aoki": "出典: YouTube「青木真也」", "pred_aoki_satomix": "出典: YouTube「青木真也」",
    "pred_strasser": "出典: YouTube「ストロング金子/ストチャンネル」", "pred_saito": "出典: YouTube「斎藤裕」",
    "pred_kawajiri": "出典: YouTube「川尻達也のじりラジオ」", "pred_jobin": "出典: YouTube「ジョビンチャンネル」",
    "pred_izawa_th": "出典: YouTube「伊澤星花」", "pred_ougikubo": "出典: YouTube「おぎちゃんねる」",
    "pred_ougikubo_zenhan": "出典: YouTube「おぎちゃんねる」", "pred_matsushima": "出典: YouTube「松嶋こよみ」",
    "pred_motoya": "出典: YouTube「元谷友貴」", "pred_kanehara": "出典: YouTube「kinchanTV/金原正徳」",
    "pred_ishiwatari": "出典: YouTube「石渡伸太郎」", "pred_akimoto_honnin": "出典: YouTube「秋元強真」",
    "pred_satoshi": "出典: YouTube「U-NEXT格闘技公式」", "pred_suzuki": "出典: YouTube「U-NEXT格闘技公式」",
    "panel_unext": "出典: YouTube「U-NEXT格闘技公式」",
    "card_ueda_edoporo": "画像: RIZIN FF公式",
}
SRC_OF.update(PRED_SRC)
# 発言クリップの出典
TALK_SRC = {
    "talk_aoki": "出典: YouTube「青木真也」", "talk_strasser": "出典: YouTube「ストロング金子/ストチャンネル」",
    "talk_saito": "出典: YouTube「斎藤裕」", "talk_kawajiri": "出典: YouTube「ジョビンチャンネル(川尻達也)」",
    "talk_jobin": "出典: YouTube「ジョビンチャンネル」", "talk_izawa": "出典: YouTube「伊澤星花」",
    "talk_ougikubo": "出典: YouTube「おぎちゃんねる(扇久保博正)」", "talk_matsushima": "出典: YouTube「松嶋こよみ」",
    "talk_motoya": "出典: YouTube「元谷友貴」", "talk_kanehara": "出典: YouTube「kinchanTV(金原正徳)」",
    "talk_ishiwatari": "出典: YouTube「石渡伸太郎」", "talk_saeki": "出典: YouTube「ジョビンチャンネル(佐伯繁)」",
    "talk_takagi": "出典: YouTube「高木凌」", "talk_horiguchi": "出典: YouTube「堀口恭司」",
}
SRC_OF.update(TALK_SRC)


def src_of(name: str) -> str:
    return SRC_OF.get(name, "画像: RIZIN FF公式")


# ============ セクション別・ビート順の背景 ============
SECTION_BG = {
    "s0_intro":  ["px_cage", "card_main_kleber_akimoto", "talk_aoki", "card_sato_mix", "pred_ougikubo_zenhan"],
    "s1_card":   ["card_main_kleber_akimoto", "kleber_action", "akimoto_solo", "kleber_face", "talk_horiguchi", "px_crowd"],
    "s2_akimoto":["talk_aoki", "talk_strasser", "talk_saito", "talk_kawajiri", "talk_jobin", "talk_izawa",
                  "panel_titlecard", "panel_titlecard", "talk_kanehara", "talk_ishiwatari", "talk_saeki", "talk_takagi"],
    "s3_kleber": ["kleber_face", "talk_ougikubo", "talk_matsushima", "talk_motoya", "pred_satoshi", "pred_suzuki"],
    "s4_even":   ["panel_titlecard", "pred_akimoto_honnin", "px_ring", "px_crowd"],
    "s5_semi":   ["pred_ougikubo_zenhan", "card_sato_mix", "card_sato_mix"],
    "s6_other":  ["card_hiramoto_jolly", "pred_official", "card_goto_temirov", "card_ito_gaja",
                  "card_majima_takeda", "talk_ishiwatari", "card_ueda_edoporo", "talk_ougikubo"],
    "s7_end":    ["panel_titlecard", "kleber_action", "px_stage", "card_main_kleber_akimoto", "px_ring"],
}

# ============ 予想者ラベル (名前 + 予想 + 色) ============
# 色: 秋元=青 #4ea1ff / クレベル=赤 #ff5a4d / 五分=灰 #cfcfcf
AK, KL, EV = "#5aa8ff", "#ff5f52", "#d8d8d8"
def PL(anchor, name, pick, color):
    return {"anchor": anchor, "name": name, "pick": pick, "color": color}
PLABELS = [
    # s1 堀口コメント
    PL("元ベラトール世界王者の堀口恭司さんも", "堀口 恭司", "注目の一戦", "#ffd76a"),
    # s2 秋元有利論
    PL("青木真也さんは、秋元の1ラウンド", "青木 真也", "秋元 1〜2R KO", AK),
    PL("ストラッサー起一さんも、忖度なしで秋元", "ストラッサー起一", "秋元 2R KO", AK),
    PL("斎藤裕さんは、戦前の予想はやはり秋元有利", "斎藤 裕", "秋元 有利", AK),
    PL("川尻達也さんは、みんなが思うほど差は大きくない", "川尻 達也", "秋元(僅差)", AK),
    PL("ジョビンさんも秋元", "ジョビン", "秋元", AK),
    PL("女子スーパーアトム級王者の伊澤星花さん", "伊澤 星花", "秋元", AK),
    PL("征矢貴さんも、秋元のKO勝ち", "征矢 貴", "秋元 KO", AK),
    PL("火の鳥さんは、秋元がタックルを切って", "火の鳥", "秋元 1R KO", AK),
    PL("金原正徳さんは、U-NEXTの公式予想番組で秋元の3ラウンドTKO", "金原 正徳", "秋元 3R TKO", AK),
    PL("石渡伸太郎さんは、秋元を知れば知るほど怪物", "石渡 伸太郎", "秋元(圧倒)", AK),
    PL("DEEP代表の佐伯繁さんも、距離感が良すぎて", "佐伯 繁", "秋元(差あり)", AK),
    PL("RIZINフェザー級の高木凌さんも、クレベルは組みつけない", "高木 凌", "秋元", AK),
    # s3 クレベル逆転論
    PL("扇久保博正さんは、クレベルがラストチャンス", "扇久保 博正", "クレベル 判定", KL),
    PL("松嶋こよみさんは、クレベルの一本勝ち", "松嶋 こよみ", "クレベル 一本(三角)", KL),
    PL("そして、過去に秋元から勝利を挙げている元谷友貴さん", "元谷 友貴", "クレベル 寄り", KL),
    PL("柔術家のホベルト・サトシ・ソウザさんは", "サトシ・ソウザ", "クレベル 2R一本", KL),
    PL("そして、クレベルに打撃を指導する鈴木博昭さんも", "鈴木 博昭", "クレベル", KL),
    # s4 五分
    PL("太田忍さんは、どちらが勝ってもおかしくない", "太田 忍", "どっちもあり", EV),
    # s5 セミ
    PL("セミファイナルは、佐藤将光対パッチー・ミックス", "青木真也ら", "ミックス 優勢", "#ffd76a"),
    # s6 その他(発言者強調)
    PL("水野新太対リー・カイウェンは、ほぼ全員が水野", "石渡・金原ら", "水野 有利", "#ffd76a"),
    PL("上田幹雄対エドポロ・キングは、上田の蹴りとスピード", "扇久保選手の予想", "上田 KO", "#ffd76a"),
    PL("直樹対細川一颯は、総合力の直樹か", "石渡・扇久保の予想", "直樹 / 細川で割れ", "#ffd76a"),
]

# ============ パネリスト・カットアウト (bg=pred_official/panel の上に人物) ============
PCUTS = [
    {"anchor": "征矢貴さんも、秋元のKO勝ち", "file": "cut_seiya.jpg"},
    {"anchor": "火の鳥さんは、秋元がタックルを切って", "file": "cut_hinotori.jpg"},
    {"anchor": "太田忍さんは、どちらが勝ってもおかしくない", "file": "cut_ota.jpg"},
]

# ============ 集計カード (秋元8/クレベル3/五分2) ============
TALLY_ANCHOR = "集計の結果は、秋元が12人"

# ============ Xカード ============
# 本人(公人・当事者)=実名/実アイコン。 一般ファン=匿名(仮名+イニシャル丸)。
XCARDS = [
    {"anchor": "本人は、練習で触られることがほとんどない",
     "author": "秋元 強真", "handle": "@Kyoma_mma", "verified": True, "avatar": "xav_akimoto.jpg",
     "text": "10試合目メイン💪 まじ必ず勝つから #RIZIN54", "likes": "5,497", "anon": False, "big": True},
    {"anchor": "ファンの応援は秋元寄りが目立ちますが",
     "author": "格闘技ファン", "handle": "@mma_fan", "verified": False, "initial": "R", "color": "#3b7fd4",
     "text": "秋元応援だけど、まだクレベル一本かコントロールされる気もする。パッチー戦みたいに触れさせずKOしたらもう昇天", "likes": "758", "anon": True, "pos": "left"},
    {"anchor": "ファンの応援は秋元寄りが目立ちますが",
     "author": "格闘技ファン", "handle": "@rizin_love", "verified": False, "initial": "K", "color": "#c0417a",
     "text": "クレベル秋元って秋元有利って言われてんのか。俺、全然クレベル勝つと思う", "likes": "420", "anon": True, "pos": "right"},
    {"anchor": "秋元を組める距離に入れさせないか",
     "author": "格闘技ファン", "handle": "@yosou_daily", "verified": False, "initial": "S", "color": "#4d8a5a",
     "text": "未だに悩んでる、まじでどっちもある。触らせない展開なら秋元、組んだらクレベル。一発は秋元…", "likes": "—", "anon": True, "pos": "center"},
]

CHANNEL = "格闘ニュースラボ"

SECTION_TAGS = {
    "s0_intro": "", "s1_card": "メインカード", "s2_akimoto": "秋元 有利論",
    "s3_kleber": "クレベル 逆転論", "s4_even": "五分・本人", "s5_semi": "後半カード",
    "s6_other": "後半カード", "s7_end": "まとめ",
}

# ============ 背景セグメント生成 (img/vid) ============
# 長尺ビートの後半を別素材に差し替え(単調回避・ナレ一致): (anchor, 2nd_asset, frac)
SPLITS = [
    ("そして、過去に秋元から勝利を挙げている元谷友貴さん", "kleber_action", 0.55),  # 元谷がクレベルの強みを語る後半→クレベル映像
    ("平本丈対ジョリーは、1ラウンド勝負", "talk_saito", 0.55),                      # 斎藤が平本予想→斎藤の発言クリップ
]


# Ken Burns 変種(scale, xPercent, yPercent の from→to)。窓分割でも連続させるため
# 「セグメント全体に対する進行度」で from/to を補間する(ピース境界でリセットしない)。
KB_VARIANTS = [
    ((1.02, -2.5, -1.2), (1.10, 2.5, 1.2)),
    ((1.10, 2.5, 1.0), (1.02, -2.5, -0.6)),
    ((1.03, 3.0, -0.8), (1.11, -3.0, 1.0)),
    ((1.11, -2.8, 1.2), (1.03, 2.8, -1.0)),
]


def kb_for(kb_idx, seg_start, seg_end, vis_start, vis_end):
    (s0, x0, y0), (s1, x1, y1) = KB_VARIANTS[kb_idx % 4]
    basis = max(0.1, (seg_end - seg_start) + FADE)  # フルレンダーのKB基準尺と一致

    def lerp(p):
        p = min(1.0, max(0.0, p))
        return {"scale": round(s0 + (s1 - s0) * p, 4),
                "x": round(x0 + (x1 - x0) * p, 3),
                "y": round(y0 + (y1 - y0) * p, 3)}
    return lerp((vis_start - seg_start) / basis), lerp((vis_end - seg_start) / basis)


def build_bg_segments():
    used = Counter()
    beat_rows = []
    for sid in SECORDER:
        lst = SECTION_BG[sid]
        bts = beats_of(sid)
        if len(bts) != len(lst):
            raise SystemExit(f"SECTION_BG mismatch {sid}: beats={len(bts)} bg={len(lst)}")
        for b, asset in zip(bts, lst):
            beat_rows.append([b, asset, sid])
    segs = []
    for b, asset, sid in beat_rows:
        if segs and segs[-1]["name"] == asset and segs[-1]["sec"] == sid and (b["end"] - segs[-1]["start"]) <= 11.0:
            segs[-1]["end"] = b["end"]
        else:
            segs.append({"start": b["start"], "end": b["end"], "name": asset, "sec": sid})
    for i in range(len(segs) - 1):
        segs[i]["end"] = segs[i + 1]["start"]
    segs[0]["start"] = 0.0
    segs[-1]["end"] = TOTAL
    # 長尺ビート分割
    for anchor, asset2, frac in SPLITS:
        b = beat_at(anchor)
        for i, s in enumerate(segs):
            if s["start"] <= b["start"] < s["end"] and s["end"] - s["start"] > 9.0:
                cut = round(s["start"] + (s["end"] - s["start"]) * frac, 3)
                new = {"start": cut, "end": s["end"], "name": asset2, "sec": s["sec"]}
                s["end"] = cut
                segs.insert(i + 1, new)
                break
    vi = 0
    for s in segs:
        nm = s["name"]
        s["video"] = is_vid(nm)
        ext = "mp4" if s["video"] else "jpg"
        sub = "bgvid" if s["video"] else "img"
        p = TPL / "assets" / sub / f"{nm}.{ext}"
        if not p.exists():
            raise SystemExit(f"MISSING BG: {p}")
        s["src"] = src_of(nm)
        s["asset"] = f"{sub}/{nm}.{ext}"
        s["id"] = f"bg{vi}"
        s["track"] = 40 + (vi % 12)
        s["kb"] = vi % 4  # Ken Burns 方向を交互に(単調回避)
        f, t = kb_for(s["kb"], s["start"], s["end"], s["start"], s["end"])  # フル(非窓)の既定
        s["kb_from"], s["kb_to"] = f, t
        if s["video"]:
            cd = clip_dur(str(p))
            seglen = (s["end"] - s["start"]) + FADE
            s["mstart"] = 0.0
            s["mdur"] = round(min(seglen + 0.15, cd - 0.05), 3)
            if s["mdur"] < seglen - 0.3:
                # ループ延長: 短尺クリップは2周目を許容(seglenに満たない分)
                s["loop"] = True
                s["mdur"] = round(cd - 0.05, 3)
        vi += 1
        used[nm] += 1
    for s in segs:
        s["start"] = round(s["start"], 3); s["end"] = round(s["end"], 3)
    return segs, used


# ============ 字幕 ============
DISP = [
    ("RIZIN.54", "RIZIN.54"),
]
def disp(text: str) -> str:
    for k, v in DISP:
        text = text.replace(k, v)
    return text


CAP_LINE_MAX = 23.0
CAP_BREAK_AFTER = set("、。，・！？」』）】")
CAP_PARTICLE = set("はがをにでとへものやか")


def build_caps():
    def width(s):
        return sum(0.5 if ch.isascii() else 1.0 for ch in s)

    def wrap_lines(s):
        lines, cur = [], ""
        i = 0
        while i < len(s):
            cur += s[i]
            if width(cur) >= CAP_LINE_MAX and i < len(s) - 1:
                cut = len(cur)
                for j in range(len(cur) - 1, max(0, len(cur) - 10), -1):
                    ch = cur[j - 1]
                    def _kata(c): return "゠" <= c <= "ヿ" or c == "ー"
                    if _kata(ch) and j < len(cur) and _kata(cur[j]):
                        continue
                    if ch.isascii() and ch.isalnum() and j < len(cur) and cur[j].isascii() and cur[j].isalnum():
                        continue
                    if ch in CAP_BREAK_AFTER or ch in CAP_PARTICLE:
                        cut = j; break
                lines.append(cur[:cut]); cur = cur[cut:]
            i += 1
        if cur:
            lines.append(cur)
        return [ln for ln in lines if ln]

    caps = []
    for i, b in enumerate(BEATS):
        start = b["start"]
        nxt = BEATS[i + 1]["start"] if i + 1 < len(BEATS) else b["end"] + 0.4
        end = min(b["end"] + 0.30, nxt - 0.05)
        if end <= start:
            end = max(b["end"], start + 0.4)
        txt = disp(b["text"].replace("「", "").replace("」", ""))
        lines = wrap_lines(txt)
        groups = [lines[k:k + 2] for k in range(0, len(lines), 2)]
        wsum = sum(width("".join(g)) for g in groups) or 1
        t = start
        for gi, g in enumerate(groups):
            frac = width("".join(g)) / wsum
            gend = end if gi == len(groups) - 1 else min(end - 0.05, t + (end - start) * frac)
            if gend <= t:
                gend = t + 0.4
            caps.append({"s": round(t, 2), "e": round(gend, 2), "lines": g})
            t = round(gend, 2)
    for k in range(len(caps) - 1):
        if caps[k]["e"] > caps[k + 1]["s"]:
            caps[k]["e"] = round(caps[k + 1]["s"] - 0.02, 2)
    return caps


def anchored(items):
    """anchor(サブ文字列)を beat の時刻へ解決し start/end を付与。"""
    out = []
    for it in items:
        b = beat_at(it["anchor"])
        d = dict(it)
        d["start"] = round(b["start"] + 0.25, 2)
        d["end"] = round(b["end"] + 0.10, 2)
        out.append(d)
    return out


def _src_windows(segs):
    out = []
    for s in segs:
        txt = s.get("src", "")
        if out and out[-1]["text"] == txt and abs(out[-1]["end"] - s["start"]) < 0.05:
            out[-1]["end"] = s["end"]
        else:
            out.append({"start": s["start"], "end": s["end"], "text": txt})
    return out


bg_segs, used = build_bg_segments()
DATA = {
    "total": DUR,
    "bg": bg_segs,
    "tags": [{"start": SECS[s]["start"], "end": SECS[s]["end"], "label": SECTION_TAGS.get(s, "")} for s in SECORDER],
    "plabels": anchored(PLABELS),
    "pcuts": anchored(PCUTS),
    "xcards": anchored(XCARDS),
    "tally": [{"start": round(beat_at(TALLY_ANCHOR)["start"] + 0.3, 2), "end": round(beat_at(TALLY_ANCHOR)["end"] + 0.2, 2)}],
    "srcs": _src_windows(bg_segs),
    "caps": build_caps(),
    "chapters": TIM.get("chapters", []),
    "channel": CHANNEL,
}

# ============ 窓分割 ============
if WINDOWED:
    off, wdur = WIN_START, round(WIN_END - WIN_START, 3)
    def _win_timed(items, ks="start", ke="end"):
        out = []
        for it in items:
            ns, ne = it[ks] - off, it[ke] - off
            if ne <= 0.001 or ns >= wdur - 0.001:
                continue
            it = dict(it); it["cont"] = ns < 0.05; it["cont_end"] = ne > wdur - 0.05
            it[ks] = round(max(0.0, ns), 3); it[ke] = round(min(wdur, ne), 3)
            out.append(it)
        return out
    def _win_bg(items):
        out = []
        for it in items:
            it = dict(it)
            ns, ne = it["start"] - off, it["end"] - off
            if ne <= 0.001 or ns >= wdur - 0.001:
                continue
            it["cont"] = ns < 0.05
            it["cont_end"] = ne > wdur - 0.05
            # KenBurnsをピースまたぎで連続させる: セグメント全体に対する可視区間の進行度でfrom/toを補間
            vis0 = max(it["start"], off)
            vis1 = min(it["end"], off + wdur)
            f, t = kb_for(it.get("kb", 0), it["start"], it["end"], vis0, vis1)
            it["kb_from"], it["kb_to"] = f, t
            if it["video"]:
                ms = it.get("mstart", 0.0)
                if ns < 0:
                    ms = round(ms - ns, 3)
                d = it.get("mdur", ne - max(0.0, ns))
                st = max(0.0, ns)
                dd = min(d, wdur - st) if it["cont_end"] else min(d, (min(wdur, ne) - st) + FADE)
                it["mstart"] = ms; it["mdur"] = round(max(0.3, dd), 3)
            it["start"] = round(max(0.0, ns), 3); it["end"] = round(min(wdur, ne), 3)
            out.append(it)
        return out
    DATA["bg"] = _win_bg(bg_segs)
    for k in ("plabels", "pcuts", "xcards", "tally", "tags", "srcs", "chapters"):
        DATA[k] = _win_timed(DATA[k])
    DATA["caps"] = _win_timed(DATA["caps"], "s", "e")
    DUR = wdur; DATA["total"] = wdur
    bg_segs = DATA["bg"]

# ============ メディア要素 ============
media = []
for s in bg_segs:
    if s["video"]:
        media.append(
            f'<div class="bg" id="{s["id"]}"><div class="bgfill" style="background-image:url(assets/{s["asset"]})"></div>'
            f'<video class="bgv" id="{s["id"]}-v" src="assets/{s["asset"]}" muted playsinline '
            f'data-start="{s["start"]}" data-duration="{s.get("mdur",1)}" data-media-start="{s.get("mstart",0)}" data-track-index="{s["track"]}"></video></div>')
    else:
        media.append(
            f'<div class="bg" id="{s["id"]}"><div class="bgfill" style="background-image:url(assets/{s["asset"]})"></div>'
            f'<div class="bgmain" style="background-image:url(assets/{s["asset"]})"></div></div>')
media.append('<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="70" data-volume="1"></audio>')
media.append('<audio id="bgm" src="assets/audio/bgm.m4a" data-start="0" data-duration="__DUR__" data-track-index="71" data-volume="0.075"></audio>')
MEDIA = "\n    ".join(media)

LIB = ROOT / "hyperframes" / "_lib" / "textfx"
TEXTFX_CSS = (LIB / "textfx.css").read_text(encoding="utf-8")
TEXTFX_JS = (LIB / "textfx.js").read_text(encoding="utf-8")

TEMPLATE = r"""<!doctype html>
<!-- RIZIN.54 勝敗予想まとめ 1920x1080【ニュースまとめ・中立】 -->
<html>
<head>
<meta charset="utf-8" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script>__TEXTFX_JS__</script>
<style>
__TEXTFX_CSS__
  @font-face { font-family:"Mincho"; src:url("assets/fonts/GokubutoMincho.ttf") format("truetype"); font-weight:900; font-display:block; }
  @font-face { font-family:"JPHeavy"; src:url("assets/fonts/SourceHanSansJP-Heavy.otf") format("opentype"); font-weight:900; font-display:block; }
  @font-face { font-family:"JPMed"; src:url("assets/fonts/SourceHanSansJP-Medium.otf") format("opentype"); font-weight:500; font-display:block; }
  * { box-sizing:border-box; margin:0; padding:0; }
  html,body { width:100%; height:100%; background:#000; overflow:hidden; }
  #root { position:relative; width:1920px; height:1080px; overflow:hidden; background:#05070c; font-family:"JPHeavy","Noto Sans JP",sans-serif; color:#fff; }

  .bg { position:absolute; inset:0; z-index:1; opacity:0; overflow:hidden; will-change:opacity; }
  .bgfill { position:absolute; inset:-4%; background-size:cover; background-position:center; filter:blur(22px) brightness(.4) saturate(.9); transform:scale(1.1); }
  .bgmain { position:absolute; inset:0; background-size:contain; background-position:center; background-repeat:no-repeat; will-change:transform; }
  .bg .bgv { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; transform:translateZ(0); backface-visibility:hidden; }

  .veil { position:absolute; inset:0; z-index:5; pointer-events:none; background:linear-gradient(180deg, rgba(0,0,0,.34) 0%, rgba(0,0,0,.02) 20%, rgba(0,0,0,.02) 52%, rgba(0,0,0,.42) 82%, rgba(0,0,0,.78) 100%); }
  .vignette { position:absolute; inset:0; z-index:6; pointer-events:none; background:radial-gradient(ellipse at 50% 46%, transparent 0 58%, rgba(0,0,0,.44) 100%); }

  .tag { position:absolute; z-index:20; left:56px; top:52px; padding:8px 22px 8px 18px; background:rgba(8,9,12,.6); border-left:5px solid #e7b94a; border-radius:2px; font-family:"Mincho",serif; font-size:34px; font-weight:900; letter-spacing:.05em; color:#fff; text-shadow:0 0 2px #000,0 2px 8px rgba(0,0,0,.9); white-space:nowrap; opacity:0; -webkit-backdrop-filter:blur(6px); backdrop-filter:blur(6px); }
  .badge { position:absolute; z-index:20; right:56px; top:54px; padding:9px 22px; background:rgba(8,8,10,.82); border:2px solid rgba(255,213,74,.85); border-radius:40px; font-family:"JPHeavy"; font-size:26px; color:#ffe89a; letter-spacing:.03em; text-shadow:0 1px 3px rgba(0,0,0,.9); }
  .src { position:absolute; z-index:20; left:40px; bottom:24px; padding:3px 11px; background:rgba(0,0,0,.62); border-left:3px solid rgba(255,213,74,.85); border-radius:2px; font-family:"JPMed"; font-size:18px; color:#e2e2e2; letter-spacing:.01em; text-shadow:0 1px 2px rgba(0,0,0,.9); opacity:0; }

  /* 予想者ラベル(上部・字幕と非干渉) */
  #plLayer { position:absolute; inset:0; z-index:19; pointer-events:none; }
  .pl { position:absolute; left:50%; top:132px; transform:translateX(-50%); text-align:center; opacity:0; white-space:nowrap; }
  .pl .plname { display:inline-block; padding:.12em .5em; font-family:"JPHeavy"; font-size:60px; letter-spacing:.02em; color:#fff; paint-order:stroke fill; -webkit-text-stroke:1px rgba(0,0,0,.2); text-shadow:0 0 3px #000,3px 0 2px #000,-3px 0 2px #000,0 3px 2px #000,0 6px 16px rgba(0,0,0,.9); }
  .pl .plpick { display:block; margin-top:12px; }
  .pl .plpick span { display:inline-block; padding:.16em .8em; background:rgba(6,8,12,.72); border-radius:8px; font-family:"JPHeavy"; font-size:40px; letter-spacing:.02em; border:2px solid rgba(255,255,255,.14); text-shadow:0 2px 6px rgba(0,0,0,.9); }
  .pl .plpre { color:#cfd6e0; font-size:26px; margin-right:.4em; }

  /* パネリスト・カットアウト(右) */
  #pcLayer { position:absolute; inset:0; z-index:16; pointer-events:none; }
  .pc { position:absolute; right:70px; bottom:0; height:86%; opacity:0; }
  .pc img { height:100%; width:auto; filter:drop-shadow(0 6px 20px rgba(0,0,0,.75)); }

  /* Xカード */
  #xLayer { position:absolute; inset:0; z-index:19; pointer-events:none; }
  .xc { position:absolute; opacity:0; width:760px; background:rgba(21,24,30,.97); border:1px solid rgba(255,255,255,.14); border-radius:20px; padding:26px 30px; box-shadow:0 16px 44px rgba(0,0,0,.6); font-family:"JPMed"; }
  .xc.big { width:900px; }
  .xc .xhead { display:flex; align-items:center; gap:16px; margin-bottom:14px; }
  .xc .xav { width:64px; height:64px; border-radius:50%; object-fit:cover; flex:none; }
  .xc .xavi { width:64px; height:64px; border-radius:50%; flex:none; display:flex; align-items:center; justify-content:center; font-family:"JPHeavy"; font-size:30px; color:#fff; }
  .xc .xname { font-family:"JPHeavy"; font-size:31px; color:#fff; display:flex; align-items:center; gap:8px; }
  .xc .xver { width:26px; height:26px; }
  .xc .xhandle { font-size:23px; color:#8b98a5; margin-top:2px; }
  .xc .xtext { font-size:33px; line-height:1.5; color:#f2f5f8; }
  .xc.big .xtext { font-size:37px; }
  .xc .xmeta { margin-top:16px; font-size:22px; color:#8b98a5; }
  .xc .xmeta b { color:#e2555f; font-family:"JPHeavy"; }

  /* 集計カード */
  #tallyLayer { position:absolute; inset:0; z-index:19; pointer-events:none; }
  .tally { position:absolute; left:50%; top:52%; transform:translate(-50%,-50%); opacity:0; text-align:center; }
  .tally .thead { font-family:"Mincho",serif; font-size:44px; color:#ffce2e; letter-spacing:.08em; margin-bottom:26px; text-shadow:0 2px 10px rgba(0,0,0,.9); }
  .tally .trow { display:flex; gap:34px; justify-content:center; }
  .tally .tcell { min-width:300px; padding:28px 20px; background:rgba(8,10,14,.78); border-radius:16px; border-top:6px solid #666; }
  .tally .tcell .tlabel { font-family:"JPHeavy"; font-size:38px; color:#fff; margin-bottom:10px; }
  .tally .tcell .tnum { font-family:"Mincho",serif; font-size:104px; line-height:.9; }
  .tally .tcell .tnum em { font-style:normal; font-size:40px; }
  .tally .ak { border-top-color:#5aa8ff; } .tally .ak .tnum { color:#5aa8ff; }
  .tally .kl { border-top-color:#ff5f52; } .tally .kl .tnum { color:#ff5f52; }
  .tally .ev { border-top-color:#d8d8d8; } .tally .ev .tnum { color:#d8d8d8; }

  #chapLayer { position:absolute; inset:0; z-index:25; pointer-events:none; }
  .chap { position:absolute; inset:0; opacity:0; }
  .chap .cfull { position:absolute; inset:0; -webkit-backdrop-filter:blur(22px) brightness(.4) saturate(.85); backdrop-filter:blur(22px) brightness(.4) saturate(.85); background:rgba(4,6,10,.34); }
  .chap .cinner { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); text-align:center; }
  .chap .csub2 { font-family:"Mincho",serif; font-weight:900; font-size:56px; letter-spacing:.1em; color:#ffce2e; text-shadow:0 0 2px #000,2px 2px 1px #000,0 4px 14px rgba(0,0,0,.92); margin-bottom:.18em; white-space:nowrap; }
  .chap .ctitle { font-family:"Mincho",serif; font-weight:900; font-size:150px; line-height:1.0; letter-spacing:.04em; color:#fff; white-space:nowrap; text-shadow:0 0 2px #000,3px 0 2px #000,-3px 0 2px #000,0 3px 2px #000,0 0 16px rgba(0,0,0,.95),0 9px 30px rgba(0,0,0,.9); }
  .chap .cline { width:0; height:5px; margin:26px auto 0; background:linear-gradient(90deg,transparent,#ffce2e 25%,#ffce2e 75%,transparent); border-radius:3px; }

  #capLayer { position:absolute; inset:0; z-index:17; pointer-events:none; }
  .cap { position:absolute; left:50%; bottom:96px; transform:translateX(-50%); width:1760px; text-align:center; opacity:0; }
  .cap .cl { display:inline-block; max-width:1760px; font-family:"JPHeavy"; font-weight:900; font-size:46px; line-height:1.32; color:#fff; white-space:nowrap; letter-spacing:.005em; paint-order:stroke fill; -webkit-text-stroke:5.5px #000; text-shadow:0 3px 7px rgba(0,0,0,.92); }
</style>
</head>
<body>
  <div id="root" data-composition-id="rizin54-yosou" data-start="0" data-duration="__DUR__" data-width="1920" data-height="1080">
    __MEDIA__
    <div class="veil"></div>
    <div class="vignette"></div>
    <div id="pcLayer"></div>
    <div id="capLayer"></div>
    <div id="plLayer"></div>
    <div id="xLayer"></div>
    <div id="tallyLayer"></div>
    <div id="ovLayer"></div>
    <div id="chapLayer"></div>
  </div>
<script>
  const DATA = __DATA__;
  const ovLayer = document.getElementById('ovLayer');
  const FADE = 0.5;
  const tl = gsap.timeline({paused:true});
  const VER = "<svg class='xver' viewBox='0 0 24 24' fill='#1d9bf0'><path d='M22.25 12c0-1.43-.88-2.67-2.19-3.34.46-1.39.2-2.9-.81-3.91s-2.52-1.27-3.91-.81c-.66-1.31-1.91-2.19-3.34-2.19s-2.67.88-3.33 2.19c-1.4-.46-2.91-.2-3.92.81s-1.26 2.52-.8 3.91c-1.31.67-2.2 1.91-2.2 3.34s.89 2.67 2.2 3.34c-.46 1.39-.21 2.9.8 3.91s2.52 1.26 3.91.81c.67 1.31 1.91 2.19 3.34 2.19s2.68-.88 3.34-2.19c1.39.45 2.9.2 3.91-.81s1.27-2.52.81-3.91c1.31-.67 2.19-1.91 2.19-3.34zm-11.71 4.2L6.8 12.46l1.41-1.42 2.26 2.26 4.8-5.23 1.47 1.36-6.2 6.77z'></path></svg>";

  DATA.bg.forEach((s) => {
    const el = document.getElementById(s.id);
    const kb = el.querySelector('.bgmain') || el.querySelector('.bgv');
    const dur = Math.max(0.6, s.end - s.start);
    // Ken Burns: 窓分割でも連続(ビルダーがセグメント進行度で from/to を補間済み)。ease:none で線形＝ピース境界で速度連続。
    const kf = s.kb_from || {scale:1.02,x:0,y:0}, kt = s.kb_to || {scale:1.08,x:0,y:0};
    if (kb) tl.fromTo(kb,
      {scale:kf.scale, xPercent:kf.x, yPercent:kf.y},
      {scale:kt.scale, xPercent:kt.x, yPercent:kt.y, duration:dur, ease:'none'}, s.start);
    if (s.cont) tl.set(el, {opacity:1}, s.start);
    else tl.fromTo(el, {opacity:0}, {opacity:1, duration:FADE, ease:'power1.out'}, s.start);
    if (!s.cont_end) tl.to(el, {opacity:0, duration:FADE, ease:'power1.in'}, s.end);
  });

  DATA.tags.forEach((t) => {
    if (!t.label) return;
    const el = document.createElement('div'); el.className='tag'; el.textContent=t.label; ovLayer.appendChild(el);
    if (t.cont) tl.set(el,{opacity:1,x:0},t.start);
    else tl.fromTo(el,{opacity:0,x:-22},{opacity:1,x:0,duration:.4,ease:'back.out(1.4)'}, t.start);
    if (!t.cont_end) tl.to(el,{opacity:0,duration:.35,ease:'power1.in'}, t.end-.35);
  });
  const badge = document.createElement('div'); badge.className='badge'; badge.textContent=DATA.channel; ovLayer.appendChild(badge);
  DATA.srcs.forEach((s) => {
    if (!s.text) return;
    const el = document.createElement('div'); el.className='src'; el.textContent=s.text; ovLayer.appendChild(el);
    if (s.cont) tl.set(el,{opacity:1},s.start); else tl.to(el,{opacity:1,duration:.4}, s.start);
    if (!s.cont_end) tl.to(el,{opacity:0,duration:.4}, s.end-.4);
  });

  const FX = window.TextFX;
  // 予想者ラベル
  const plLayer = document.getElementById('plLayer');
  DATA.plabels.forEach((p) => {
    const el = document.createElement('div'); el.className='pl';
    el.innerHTML = "<div class='plname'>"+p.name+"</div><div class='plpick'><span style='color:"+p.color+"'><span class='plpre'>予想</span>"+p.pick+"</span></div>";
    plLayer.appendChild(el);
    if (p.cont) tl.set(el,{opacity:1,y:0},p.start);
    else { tl.fromTo(el,{opacity:0,y:-18},{opacity:1,y:0,duration:.4,ease:'power3.out'}, p.start); }
    if (!p.cont_end) tl.to(el,{opacity:0,duration:.3,ease:'power1.in'}, p.end-.3);
  });

  // パネリスト・カットアウト
  const pcLayer = document.getElementById('pcLayer');
  DATA.pcuts.forEach((p) => {
    const el = document.createElement('div'); el.className='pc';
    el.innerHTML = "<img src='assets/img/"+p.file+"'>";
    pcLayer.appendChild(el);
    if (p.cont) tl.set(el,{opacity:1,x:0},p.start);
    else tl.fromTo(el,{opacity:0,x:40},{opacity:1,x:0,duration:.5,ease:'power3.out'}, p.start);
    if (!p.cont_end) tl.to(el,{opacity:0,duration:.35,ease:'power1.in'}, p.end-.35);
  });

  // Xカード
  const xLayer = document.getElementById('xLayer');
  DATA.xcards.forEach((c) => {
    const el = document.createElement('div'); el.className='xc'+(c.big?' big':'');
    if (c.big) { el.style.left='50%'; el.style.top='40%'; el.style.transform='translate(-50%,-50%)'; }
    else if (c.pos==='left') { el.style.left='70px'; el.style.top='30%'; }
    else if (c.pos==='right') { el.style.right='70px'; el.style.top='52%'; }
    else { el.style.left='50%'; el.style.top='40%'; el.style.transform='translateX(-50%)'; }
    const av = c.anon
      ? "<div class='xavi' style='background:"+(c.color||'#3b7fd4')+"'>"+(c.initial||'?')+"</div>"
      : "<img class='xav' src='assets/img/"+c.avatar+"'>";
    el.innerHTML = "<div class='xhead'>"+av+"<div><div class='xname'>"+c.author+(c.verified?VER:"")+"</div><div class='xhandle'>"+c.handle+"</div></div></div>"
      + "<div class='xtext'>"+c.text+"</div><div class='xmeta'>♡ <b>"+c.likes+"</b>  ・ X(旧Twitter)より</div>";
    xLayer.appendChild(el);
    const tf = el.style.transform || '';
    if (c.cont) tl.set(el,{opacity:1},c.start);
    else tl.fromTo(el,{opacity:0,y:16},{opacity:1,y:0,duration:.4,ease:'power3.out'}, c.start);
    if (!c.cont_end) tl.to(el,{opacity:0,duration:.3,ease:'power1.in'}, c.end-.3);
  });

  // 集計カード
  const tallyLayer = document.getElementById('tallyLayer');
  DATA.tally.forEach((t) => {
    const el = document.createElement('div'); el.className='tally';
    el.innerHTML = "<div class='thead'>予想者18人の内訳</div><div class='trow'>"
      + "<div class='tcell ak'><div class='tlabel'>秋元</div><div class='tnum'>12<em>人</em></div></div>"
      + "<div class='tcell kl'><div class='tlabel'>クレベル</div><div class='tnum'>5<em>人</em></div></div>"
      + "<div class='tcell ev'><div class='tlabel'>五分</div><div class='tnum'>1<em>人</em></div></div></div>";
    tallyLayer.appendChild(el);
    const cells = el.querySelectorAll('.tcell');
    if (t.cont) { tl.set(el,{opacity:1},t.start); tl.set(cells,{opacity:1,y:0},t.start); }
    else {
      tl.fromTo(el,{opacity:0},{opacity:1,duration:.3}, t.start);
      tl.fromTo(cells,{opacity:0,y:26},{opacity:1,y:0,duration:.45,stagger:.12,ease:'back.out(1.3)'}, t.start+.1);
    }
    if (!t.cont_end) tl.to(el,{opacity:0,duration:.3,ease:'power1.in'}, t.end-.3);
  });

  const capLayer = document.getElementById('capLayer');
  (DATA.caps||[]).forEach((c) => {
    const el = document.createElement('div'); el.className='cap';
    el.innerHTML = c.lines.map((l)=>"<div class='cl'>"+l+"</div>").join('');
    capLayer.appendChild(el);
    if (c.cont) tl.set(el,{opacity:1,y:0},c.s);
    else tl.fromTo(el,{opacity:0,y:8},{opacity:1,y:0,duration:.14,ease:'power1.out'}, c.s);
    if (!c.cont_end) tl.to(el,{opacity:0,duration:.1,ease:'power1.in'}, c.e);
  });

  const chapLayer = document.getElementById('chapLayer');
  (DATA.chapters||[]).forEach((ch)=>{
    const el=document.createElement('div'); el.className='chap';
    el.innerHTML="<div class='cfull'></div><div class='cinner'><div class='csub2'>"+ch.sub+"</div><div class='ctitle'>"+ch.title+"</div><div class='cline'></div></div>";
    chapLayer.appendChild(el);
    const inner=el.querySelector('.cinner'), ttl=el.querySelector('.ctitle'), line=el.querySelector('.cline');
    if (ch.cont) { tl.set(el,{opacity:1},0); tl.set(inner,{scale:1.0},0); tl.set(ttl,{letterSpacing:'0.04em',opacity:1},0); tl.set(line,{width:560},0); }
    else {
      tl.fromTo(el,{opacity:0},{opacity:1,duration:.2,ease:'power1.out'}, ch.start);
      tl.fromTo(inner,{scale:1.1},{scale:1.0,duration:.55,ease:'power3.out'}, ch.start);
      tl.fromTo(ttl,{letterSpacing:'0.2em',opacity:0},{letterSpacing:'0.04em',opacity:1,duration:.5,ease:'power2.out'}, ch.start+0.04);
      tl.fromTo(line,{width:0},{width:560,duration:.55,ease:'power2.out'}, ch.start+0.18);
    }
    if (!ch.cont_end) tl.to(el,{opacity:0,duration:.3,ease:'power1.in'}, ch.end-0.3);
  });

  window.__timelines = window.__timelines || {};
  window.__timelines['rizin54-yosou'] = tl;
</script>
</body>
</html>
"""

HTML = (TEMPLATE.replace("__TEXTFX_CSS__", TEXTFX_CSS)
                .replace("__TEXTFX_JS__", TEXTFX_JS)
                .replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
                .replace("__MEDIA__", MEDIA)
                .replace("__DUR__", str(DUR)))
(TPL / "index.html").write_text(HTML, encoding="utf-8")

over = {a: n for a, n in used.items() if n >= 3}
vid_time = sum(s["end"] - s["start"] for s in bg_segs if s.get("video"))
print(f"-> {TPL / 'index.html'}")
print(f"bg segs:{len(bg_segs)} plabels:{len(DATA['plabels'])} pcuts:{len(DATA['pcuts'])} xcards:{len(DATA['xcards'])} chapters:{len(DATA['chapters'])} total:{DUR}s")
print(f"背景セグメント最大尺: {max(s['end']-s['start'] for s in bg_segs):.1f}s (目標<11s)")
print(f"★背景の【映像】比率: {100*vid_time/max(1,DUR):.0f}%")
print(f"3回以上使用: {over if over else 'なし'}")
print("使用回数:", dict(used))
