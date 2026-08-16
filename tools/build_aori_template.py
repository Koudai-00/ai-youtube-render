"""アオリ・チロン完全解説 index.html 生成(1920x1080・評伝型・窓対応・cue同期字幕)。
字幕=timings.jsonのcue単位(1cue=1字幕・実発話と正確一致)。要素はbase_id範囲で配置。
背景=単一bg動画を窓別選択。前景=DOM(下部字幕・章タグ・PiP・規模マップ・エルス戦カード・ギブソン対戦カード・
朝倉戦ポスター(ユーザー提供)・スタッツ・出典・透かし)。SFXイベント=sfx_events.json(章=衝撃音/カード=シャキーン・金属交互)。
窓env=HF_WIN_START/END/VISUAL_ONLY/HF_OUTNAME/HF_EXPORT_BG/HF_EXPORT_SFX。"""
from __future__ import annotations
import json, html, os, re
from pathlib import Path
VISUAL_ONLY = os.environ.get("HF_VISUAL_ONLY") == "1"

ROOT = Path(__file__).resolve().parents[1]
EP = "aori"
TPL = ROOT / "hyperframes" / "templates" / EP
TIM = json.load(open(ROOT / "subtitles" / "out" / EP / "timings.json", encoding="utf-8"))
CUES = TIM["cues"]
COMP = round(TIM["total"] + 0.3, 2)
# base_id -> cue範囲
BY_BASE = {}
for c in CUES:
    BY_BASE.setdefault(c["base_id"], []).append(c)
W0 = float(os.environ.get("HF_WIN_START") or 0)
_w1 = os.environ.get("HF_WIN_END"); W1 = float(_w1) if _w1 else COMP
WIN = round(W1 - W0, 2)
OUTNAME = os.environ.get("HF_OUTNAME", "index.html")
def T(t): return round(t - W0, 3)
def OV(t0, t1): return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)
def st(b): return BY_BASE[b][0]["start"]
def en(b): return BY_BASE[b][-1]["end"]
def esc(s): return html.escape(s)

# ===== DISP: 読みかな→正式表記(長キー優先) =====
DISP = {
    "あおりちろん": "アオリ・チロン", "あさくらかい": "朝倉海", "だぶりゅーえるえふ": "WLF",
    "うーりんふぉん": "武林風", "さんだー": "散打", "さんだ": "散打", "ちゃんうぇいりー": "張偉麗",
    "いーろん": "一龍", "しーあんたいいくだいがく": "西安体育大学", "かなんえいし": "河南衛視",
    "こーでぃぎぶそん": "コーディ・ギブソン", "きゃめろんえるす": "キャメロン・エルス",
    "あいまんざはび": "アイマン・ザハビ", "らうるろさすじゅにあ": "ラウル・ロサス・ジュニア",
    "こーでぃはどん": "コーディ・ハドン", "ぎぶそん": "ギブソン",
    "ユーエフシー": "UFC", "ワン": "ONE", "ライジン": "RIZIN", "ディープ": "DEEP",
    "ケーワン": "K-1", "ノックアウト": "KO", "よんじゅうきゅう": "49", "パーセント": "%",
    "5てんよんなな": "5.47", "モンゴリアンマーダラー": "モンゴリアン・マーダラー",
}
def disp(t):
    for k in sorted(DISP, key=len, reverse=True): t = t.replace(k, DISP[k])
    return t.replace("、と、", "と、").replace("、と。", "と。")

# ===== 字幕2行分割(表示用) =====
def zwidth(s): return sum(0.55 if (c.isascii() and (c.isalnum() or c in " .,'-%")) else 1.0 for c in s)
def wrap_two(text, maxw):
    segs = [s for s in re.split("(?<=、)", text) if s]
    for i in range(1, len(segs)):
        l1 = "".join(segs[:i]); l2 = "".join(segs[i:])
        if zwidth(l1) <= maxw and zwidth(l2) <= maxw: return (l1, l2)
    if zwidth(text) <= maxw * 2:
        cut = max(1, int(len(text) * maxw / max(zwidth(text), 1))); return (text[:cut], text[cut:])
    return None
def sub_lines(text, maxw=26.0):
    if zwidth(text) <= maxw: return [text]
    w = wrap_two(text, maxw); return [w[0], w[1]] if w else [text]

# ===== 章(評伝型: 英字タグ+日本語サブ) =====
CHAP_LABEL = {
    "内モンゴルの遊牧民": ("ORIGIN", "内モンゴルの遊牧民"),
    "散打からMMAへ": ("SANDA", "散打から、MMAへ"),
    "中国の頂点 武林風": ("WLF", "中国の頂点、武林風"),
    "UFCの舞台へ": ("UFC", "UFCの舞台へ"),
    "ファイトスタイル徹底分析": ("STYLE", "ファイトスタイル徹底分析"),
    "朝倉海戦の行方": ("THE FIGHT", "朝倉海戦の、行方"),
}
CHAPS = [(c["chapter"], c["start"]) for c in CUES if c["chapter"]]

# ===== 背景プラン (t0_bid, t1_bid, ref, motion, srclabel) =====
S_UFC = "出典: UFC公式 素材"; S_RIZIN = "出典: RIZIN公式"; S_PEX = "出典: イメージ映像(Pexels)"
IMG = {"aori_fullbody.png", "aori_headshot.png", "asakura_kai.jpg", "gibson_fullbody.png", "else_fullbody.png", "HNJ048LbkAA_4Af.jpg"}
PORTRAIT = ("aori_fullbody.png", "gibson_fullbody.png", "else_fullbody.png", "asakura_kai.jpg", "HNJ048LbkAA_4Af.jpg")
BG = [
    ("h1", "h2", "aori_fullbody.png", "kb_zin", S_UFC),
    ("h2", "h3", "fists.mp4", None, S_PEX),
    ("h3", "c1_1", "grassland.mp4", None, S_PEX),
    ("c1_1", "c1_2", "nomad.mp4", None, S_PEX),
    ("c1_2", "c1_3", "grassland.mp4", None, S_PEX),
    ("c1_3", "c1_4", "nomad.mp4", None, S_PEX),
    ("c1_4", "c2_1", "gym.mp4", None, S_PEX),
    ("c2_1", "c2_2", "silhouette.mp4", None, S_PEX),
    ("c2_2", "c2_3", "training.mp4", None, S_PEX),
    ("c2_3", "c2_4", "aori_headshot.png", "kb_zin", S_UFC),
    ("c2_4", "c3_1", "stadium.mp4", None, S_PEX),
    ("c3_1", "c3_2", "cage.mp4", None, S_PEX),
    ("c3_2", "c3_3", "lantern.mp4", None, S_PEX),
    ("c3_3", "c3_4", "crowd.mp4", None, S_PEX),
    ("c3_4", "c3_6", "aerial.mp4", None, S_PEX),
    ("c3_6", "c3_7", "lantern.mp4", None, S_PEX),
    ("c3_7", "c4_1", "crowd.mp4", None, S_PEX),
    ("c4_1", "c4_2", "aori_fullbody.png", "kb_pan", S_UFC),
    ("c4_2", "c4_3", "spotlight.mp4", None, S_PEX),
    ("c4_3", "c4_4", "shanghai.mp4", None, S_PEX),
    ("c4_4", "c4_4b", "gym.mp4", None, S_PEX),            # エルス戦カード
    ("c4_4b", "c4_7", "fists.mp4", None, S_PEX),          # ギブソン対戦カード
    ("c4_7", "c4_8", "cage.mp4", None, S_PEX),            # ロサス(黒星)
    ("c4_8", "c5_1", "aori_headshot.png", "kb_zin", S_UFC),
    ("c5_1", "c5_2", "gym.mp4", None, S_PEX),
    ("c5_2", "c5_3", "silhouette.mp4", None, S_PEX),
    ("c5_3", "c5_4", "spotlight.mp4", None, S_PEX),       # スタッツ(攻撃データ)
    ("c5_4", "c5_5", "stadium.mp4", None, S_PEX),
    ("c5_5", "c6_1", "training.mp4", None, S_PEX),
    ("c6_1", "c6_2", "shanghai.mp4", None, S_PEX),
    ("c6_2", "c6_2b", "aerial.mp4", None, S_PEX),         # 朝倉PiP
    ("c6_2b", "c6_3", "asakura_kai.jpg", "kb_zin", S_RIZIN),  # 共通点(朝倉ポートレート contain)
    ("c6_3", "c6_4", "cage.mp4", None, S_PEX),
    ("c6_4", "c6_5", "shanghai.mp4", None, S_UFC),        # 提供対戦ポスターがDOMで乗る(7:06)
    ("c6_5", "c6_6", "crowd.mp4", None, S_PEX),           # スタッツ(戦績)
    ("c6_6", "c6_7", "asakura_kai.jpg", "kb_pan", S_RIZIN),  # 朝倉ポートレート contain
    ("c6_7", "c6_8", "aori_fullbody.png", "kb_zin", S_UFC),
    ("c6_8", "e1", "spotlight.mp4", None, S_PEX),
    ("e1", "END", "aori_fullbody.png", "kb_zin", S_UFC),
]
def _t(bid): return COMP if bid == "END" else st(bid)
BG_ABS = [(_t(a), _t(b), r, m, s) for (a, b, r, m, s) in BG]
BG_ABS.sort(key=lambda e: e[0])
_bg2 = []
for i, (t0, t1, r, m, s) in enumerate(BG_ABS):
    if i + 1 < len(BG_ABS): t1 = round(BG_ABS[i + 1][0] + 0.08, 3)
    _bg2.append((round(t0, 3), round(t1, 3), r, m, s))
BG_ABS = _bg2

# ===== BGプラン書き出し(bg合成用) =====
if os.environ.get("HF_EXPORT_BG") == "1":
    plan = [{"t0": t0, "t1": t1, "kind": ("img" if r in IMG else "vid"), "ref": r,
             "motion": (m or ("kb_zin" if i % 2 == 0 else "kb_pan")),
             "port": (r in PORTRAIT)}
            for i, (t0, t1, r, m, s) in enumerate(BG_ABS)]
    (TPL / "bg_plan.json").write_text(json.dumps({"total": COMP, "segments": plan}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"exported bg_plan.json ({len(plan)} segments, total {COMP})"); raise SystemExit(0)

# ===== 試合映像PiP (b0,b1,clip,label,media_start) =====
PIP = [
    ("h2", "h3", "aori_wlfko1.mp4", "武林風時代のKO", 0),
    ("c3_1", "c3_2", "aori_wlfstd1.mp4", "武林風 (アオリの試合)", 0),
    ("c3_3", "c3_4", "wlf1.mp4", "WLF 武林風 (番組)", 0),
    ("c3_6", "c3_7", "wlf2.mp4", "WLF 武林風 の試合", 0),
    ("c4_3", "c4_4", "molina.mp4", "UFC 試合映像 (対モリナ)", 0),
    ("c4_7", "c4_8", "rosas.mp4", "対ロサス Jr (判定負け)", 0),
    ("c5_2", "c5_3", "molina2.mp4", "UFC 試合映像 (対モリナ)", 0),
    ("c5_5", "c6_1", "aori_wlfko2.mp4", "武林風時代のKO", 0),
    ("c6_2", "c6_2b", "asakura_clean.mp4", "朝倉海 vs スモザーマン", 0),
]
sfx = []  # {t, kind}
_cardn = 0
def _alt():
    global _cardn; _cardn += 1; return "metal" if _cardn % 2 else "shakiin"

pip_divs, pip_tws = [], []
for k, item in enumerate(PIP):
    b0, b1, clip, lab, mstart = item
    t0 = st(b0); t1 = st(b1) if b1 in BY_BASE else en(b0)
    if OV(t0, t1):
        pid = f"pip{k}"
        ms_attr = f' data-media-start="{mstart}"' if mstart else ""
        pip_divs.append(f'<div class="pipbox" id="{pid}"><div class="pipframe">'
                        f'<video id="{pid}-v" src="assets/pip/{clip}" muted playsinline loop'
                        f'{ms_attr} data-start="{max(0.0,T(t0)):.2f}" data-duration="{(min(t1,W1)-max(t0,W0))+0.4:.2f}" data-track-index="{40+k}"></video>'
                        f'</div><div class="piplabel">{esc(lab)}</div></div>')
        if T(t0) <= 0.02:
            pip_tws.append(f"tl.set('#{pid}',{{opacity:1,scale:1}},0);")
        else:
            pip_tws.append(f"tl.fromTo('#{pid}',{{opacity:0,scale:.94}},{{opacity:1,scale:1,duration:.4,ease:'back.out(1.3)'}},{T(t0):.2f});")
        pip_tws.append(f"tl.to('#{pid}',{{opacity:0,duration:.3}},{T(t1)-0.05:.2f});")
    sfx.append({"t": round(t0 + 0.05, 2), "kind": _alt()})

# ===== 規模マップ図(ch3: c3_4..c3_6) =====
map_divs, map_tws = [], []
if OV(st("c3_4"), st("c3_6")):
    inner = ('<div class="scalemap" id="scalemap"><div class="smttl">世界の主要MMA団体 規模マップ</div>'
             '<div class="smrow"><span class="smtier">世界</span><span class="smorg big">UFC</span></div>'
             '<div class="smrow"><span class="smtier">アジア</span><span class="smorg">ONE</span></div>'
             '<div class="smrow"><span class="smtier">日本</span><span class="smorg">RIZIN</span><span class="smorg sm">DEEP</span><span class="smorg sm">パンクラス</span></div>'
             '<div class="smrow hi"><span class="smtier">中国</span><span class="smorg">WLF 武林風</span><span class="smnote">← アオリはここの王者</span></div></div>')
    map_divs.append(inner)
    map_tws.append(f"tl.fromTo('#scalemap',{{opacity:0,y:24}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.3)'}},{max(0.0,T(st('c3_4')+0.2)):.2f});")
    map_tws.append(f"tl.to('#scalemap',{{opacity:0,duration:.3}},{T(st('c3_6')-0.1):.2f});")
sfx.append({"t": round(st("c3_4") + 0.25, 2), "kind": "metal"})

# ===== エルス戦カード(c4_4) =====
else_divs, else_tws = [], []
if OV(st("c4_4"), st("c4_4b")):
    else_divs.append('<div class="fcard" id="elsecard"><div class="fcttl">2024年 ・ UFC</div>'
                     '<img class="fcimg" src="assets/img/else_fullbody.png">'
                     '<div class="fcname">キャメロン・エルス 戦</div><div class="fcres win">1R TKO 勝ち</div></div>')
    else_tws.append(f"tl.fromTo('#elsecard',{{opacity:0,scale:.95}},{{opacity:1,scale:1,duration:.45,ease:'back.out(1.2)'}},{max(0.0,T(st('c4_4')+0.15)):.2f});")
    else_tws.append(f"tl.to('#elsecard',{{opacity:0,duration:.3}},{T(st('c4_4b')-0.1):.2f});")
sfx.append({"t": round(st("c4_4") + 0.15, 2), "kind": "shakiin"})

# ===== ギブソン戦 対戦カード(公式写真 左右並置 + 21秒TKOスタンプ) c4_4b..c4_6 =====
gib_divs, gib_tws = [], []
if OV(st("c4_4b"), st("c4_7")):
    gib_divs.append(
        '<div class="gibcard" id="gibcard">'
        '<div class="gibttl">2025年10月18日 ・ UFC バンクーバー</div>'
        '<div class="gibrow">'
        '<div class="gibside"><img class="gibimg" src="assets/img/aori_fullbody.png"><div class="gibname aori">アオリ・チロン</div><div class="gibtag win">WIN</div></div>'
        '<div class="gibmid"><div class="gibvs">VS</div></div>'
        '<div class="gibside"><img class="gibimg" src="assets/img/gibson_fullbody.png"><div class="gibname gib">コーディ・ギブソン</div><div class="gibtag lose">KO負け</div></div>'
        '</div>'
        '<div class="gibstamp" id="gibstamp">21秒 TKO</div>'
        '</div>')
    gib_tws.append(f"tl.fromTo('#gibcard',{{opacity:0,scale:.96}},{{opacity:1,scale:1,duration:.5,ease:'back.out(1.2)'}},{max(0.0,T(st('c4_4b')+0.2)):.2f});")
    if OV(st("c4_6"), st("c4_7")):
        ts = T(st("c4_6") + 0.1)
        if ts <= 0.02:
            gib_tws.append("tl.set('#gibstamp',{opacity:1,scale:1,rotation:-8},0);")
        else:
            gib_tws.append("tl.set('#gibstamp',{opacity:0},0);")
            gib_tws.append(f"tl.fromTo('#gibstamp',{{opacity:0,scale:2.4,rotation:-8}},{{opacity:1,scale:1,rotation:-8,duration:.34,ease:'back.out(2)'}},{ts:.2f});")
    else:
        gib_tws.append("tl.set('#gibstamp',{opacity:1,scale:1,rotation:-8},0);")
    gib_tws.append(f"tl.to('#gibcard',{{opacity:0,duration:.3}},{T(st('c4_7')-0.1):.2f});")
sfx.append({"t": round(st("c4_4b") + 0.2, 2), "kind": "metal"})
sfx.append({"t": round(st("c4_6") + 0.1, 2), "kind": "shakiin"})

# ===== スタッツカード =====
STAT = [
    ("c5_3", "c5_4", '<div class="statttl">攻撃データ</div><div class="statrow"><b>有効打 命中率</b><span class="sv">49%</span></div><div class="statrow"><b>被弾数 / 分</b><span class="sv warn">5.47発</span></div><div class="statnote">当てる力は高いが、もらう隙も大きい</div>'),
    ("c6_5", "c6_6", '<div class="statttl">戦績</div><div class="statrow"><b>プロ通算</b><span class="sv">26勝 13敗 1NC</span></div><div class="statrow"><b>KO</b><span class="sv">9</span><b>UFC</b><span class="sv">4勝 5敗 1NC</span></div><div class="statnote">勝つも負けるも豪快なストライカー</div>'),
]
stat_divs, stat_tws = [], []
for k, (b0, b1, inner) in enumerate(STAT):
    if OV(st(b0), st(b1)):
        sid = f"stat{k}"
        stat_divs.append(f'<div class="statcard" id="{sid}">{inner}</div>')
        stat_tws.append(f"tl.fromTo('#{sid}',{{opacity:0,x:40}},{{opacity:1,x:0,duration:.5,ease:'back.out(1.3)'}},{max(0.0,T(st(b0)+0.2)):.2f});")
        stat_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{T(st(b1)-0.1):.2f});")
    sfx.append({"t": round(st(b0) + 0.2, 2), "kind": _alt()})

# ===== 朝倉戦ポスター(ユーザー提供・c6_4, 7:06) =====
pos_divs, pos_tws = [], []
if OV(st("c6_4"), st("c6_5")):
    pos_divs.append('<div class="poster" id="poster"><img src="assets/img/HNJ048LbkAA_4Af.jpg"></div>')
    pos_tws.append(f"tl.fromTo('#poster',{{opacity:0,scale:.96}},{{opacity:1,scale:1,duration:.5,ease:'back.out(1.2)'}},{max(0.0,T(st('c6_4')+0.2)):.2f});")
    pos_tws.append(f"tl.to('#poster',{{opacity:0,duration:.3}},{T(st('c6_5')-0.1):.2f});")
sfx.append({"t": round(st("c6_4") + 0.2, 2), "kind": "shakiin"})

# ===== 章タグ =====
chap_divs, chap_tws = [], []
for j, (ch, cst) in enumerate(CHAPS):
    if ch in CHAP_LABEL and OV(cst, cst + 3.8):
        en_, sub = CHAP_LABEL[ch]; cid = f"chap{j}"
        chap_divs.append(f'<div class="chaptag" id="{cid}"><div class="chnum">{esc(en_)}</div><div class="chttl">{esc(sub)}</div></div>')
        chap_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,y:40}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.6)'}},{T(cst+0.1):.2f});")
        chap_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-26,duration:.4,ease:'power1.in'}},{T(cst+3.4):.2f});")
    sfx.append({"t": round(cst + 0.1, 2), "kind": "impact"})

# ===== SFXイベント書き出し =====
if os.environ.get("HF_EXPORT_SFX") == "1":
    sfx_sorted = sorted(sfx, key=lambda e: e["t"])
    (TPL / "sfx_events.json").write_text(json.dumps(sfx_sorted, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"exported sfx_events.json ({len(sfx_sorted)} events)"); raise SystemExit(0)

# ===== 背景=窓別bg動画 =====
bg_divs, bg_tws, src_divs = [], [], []
_wi = min(8, int((W0 + 1.5) // 60)); _fstart = max(0.0, _wi * 60 - 1.5); _media = round(W0 - _fstart, 3)
_bgdur = (min(COMP, W1) - W0) + 0.6
bg_divs.append('<div class="bgseg" id="bgmain" style="z-index:1;opacity:1">'
               f'<video id="bgmain-v" src="assets/bgvid/aori_bg_w{_wi}.mp4" muted playsinline data-layout-allow-overflow '
               f'data-start="0" data-duration="{_bgdur:.2f}" data-media-start="{_media:.3f}" data-track-index="10"></video></div>')
bg_tws.append("tl.set('#bgmain',{opacity:1},0);")
for i, (t0, t1, r, m, s) in enumerate(BG_ABS):
    if not s or not OV(t0, t1): continue
    sid = f"src{i}"; vt0 = T(t0)
    src_divs.append(f'<div class="srclab" id="{sid}">{esc(s)}</div>')
    bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{max(0.0,vt0+0.3):.2f});")
    bg_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{T(t1)-0.25:.2f});")

# ===== 下部字幕(cue単位・完全同期) =====
sub_divs, sub_tws = [], []
for i, c in enumerate(CUES):
    cs, ce = c["start"], c["end"]
    if not OV(cs, ce): continue
    inner = "<br>".join(esc(l) for l in sub_lines(disp(c["text"]))); did = f"sub{i}"
    sub_divs.append(f'<div class="subt" id="{did}">{inner}</div>')
    sub_tws.append(f"tl.fromTo('#{did}',{{opacity:0}},{{opacity:1,duration:.16}},{max(0.0,T(cs)):.2f});")
    sub_tws.append(f"tl.to('#{did}',{{opacity:0,duration:.12}},{T(ce-0.03):.2f});")

# ===== 章SE(mux用・visual_onlyでは無音) =====
chap_audio = []
if not VISUAL_ONLY:
    for j, (ch, cst) in enumerate(CHAPS):
        if OV(cst, cst + 1.0):
            chap_audio.append(f'<audio id="chs{j}" src="assets/se/se_impact.mp3" data-start="{T(cst+0.1):.2f}" data-track-index="{200+j}" data-volume="0.5"></audio>')

# 窓境界cont
def _cont_fix(tws):
    out = []
    for s in tws:
        m = re.match(r"tl\.fromTo\('(#[^']+)',\{[^}]*\},\{[^}]*\},([\-0-9.]+)\);\s*$", s)
        if m and float(m.group(2)) <= 0.02:
            out.append("tl.set('%s',{opacity:1,x:0,y:0,scale:1},0);" % m.group(1))
        else: out.append(s)
    return out
for _nm in ("bg_tws", "chap_tws", "pip_tws", "map_tws", "else_tws", "gib_tws", "stat_tws", "pos_tws", "sub_tws"):
    globals()[_nm] = _cont_fix(globals()[_nm])

def J(items, ind="      "): return "\n".join(ind + x for x in items)
AUDIO_BLOCK = ("" if VISUAL_ONLY else
    '<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="60" data-volume="1"></audio>\n'
    '    <audio id="bgm" src="assets/audio/bgm.mp3" data-start="0" data-track-index="61" data-volume="0.07"></audio>')

HTML = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
  @font-face{{font-family:"Mincho";src:url("assets/fonts/GokubutoMincho.ttf");}}
  @font-face{{font-family:"JPHeavy";src:url("assets/fonts/SourceHanSansJP-Heavy.otf");}}
  @font-face{{font-family:"JPMed";src:url("assets/fonts/SourceHanSansJP-Medium.otf");}}
  :root{{--white:#fff;--yellow:#ffe23a;--red:#ff3a3a;--blue:#37c0ff;--gold:#e8b64c;--green:#37e08a;--ink:#0a0c12;
    --edge:drop-shadow(4px 0 0 var(--ink)) drop-shadow(-4px 0 0 var(--ink)) drop-shadow(0 4px 0 var(--ink)) drop-shadow(0 -4px 0 var(--ink))
           drop-shadow(3px 3px 0 var(--ink)) drop-shadow(-3px 3px 0 var(--ink)) drop-shadow(0 8px 16px rgba(0,0,0,.8));
    --edsm:drop-shadow(0 0 2px var(--ink)) drop-shadow(1px 1px 1px var(--ink)) drop-shadow(0 2px 6px rgba(0,0,0,.85));}}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  #root{{position:absolute;inset:0;overflow:hidden;background:#05060a;font-family:"JPMed";}}
  .bgseg{{position:absolute;inset:0;opacity:0;overflow:hidden;}}
  .bgseg video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform:translateZ(0);backface-visibility:hidden;}}
  .veil{{position:absolute;inset:0;z-index:30;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,.45) 0%,transparent 20%,transparent 56%,rgba(0,0,0,.5) 84%,rgba(0,0,0,.78) 100%);}}
  .wm{{position:absolute;z-index:60;left:36px;top:30px;font-family:"JPHeavy";font-size:30px;color:#fff;letter-spacing:.04em;filter:var(--edsm);opacity:.9;}}
  .srclab{{position:absolute;z-index:55;left:40px;bottom:40px;font-family:"JPMed";font-size:23px;color:#eaeaea;opacity:0;background:rgba(0,0,0,.5);border-left:4px solid var(--gold);padding:6px 14px;border-radius:3px;filter:var(--edsm);}}
  .chaptag{{position:absolute;z-index:48;left:120px;top:37%;opacity:0;}}
  .chaptag .chnum{{font-family:"JPHeavy";font-size:40px;color:var(--gold);letter-spacing:.14em;filter:var(--edge);}}
  .chaptag .chttl{{font-family:"JPHeavy";font-size:76px;color:#fff;filter:var(--edge);margin-top:6px;white-space:nowrap;}}
  .pipbox{{position:absolute;z-index:42;right:70px;top:150px;opacity:0;}}
  .pipframe{{width:1000px;height:562px;border:6px solid #fff;border-radius:10px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.7);background:#000;}}
  .pipframe video{{width:100%;height:100%;object-fit:cover;}}
  .piplabel{{position:absolute;left:0;bottom:-14px;background:var(--red);color:#fff;font-family:"JPHeavy";font-size:28px;padding:6px 20px;border-radius:6px;filter:var(--edsm);}}
  .scalemap{{position:absolute;z-index:44;left:90px;top:230px;background:rgba(8,12,22,.9);border:2px solid #2a3a5a;border-radius:18px;padding:30px 40px;opacity:0;min-width:900px;}}
  .smttl{{font-family:"JPHeavy";font-size:42px;color:#fff;filter:var(--edsm);margin-bottom:20px;}}
  .smrow{{display:flex;align-items:center;gap:22px;margin:14px 0;}}
  .smtier{{font-family:"JPHeavy";font-size:30px;color:#9fd0ff;width:120px;}}
  .smorg{{font-family:"JPHeavy";font-size:44px;color:#fff;background:rgba(40,60,90,.8);padding:6px 24px;border-radius:10px;}}
  .smorg.big{{font-size:56px;color:#0a0c12;background:var(--gold);}}
  .smorg.sm{{font-size:32px;color:#cfe;background:rgba(40,60,90,.6);}}
  .smrow.hi .smorg{{background:var(--red);color:#fff;}}
  .smnote{{font-family:"JPHeavy";font-size:30px;color:var(--yellow);filter:var(--edsm);}}
  /* エルス戦カード(単体・右) */
  .fcard{{position:absolute;z-index:45;right:150px;top:120px;display:flex;flex-direction:column;align-items:center;opacity:0;background:rgba(8,12,22,.82);border:2px solid #2a3a5a;border-radius:18px;padding:20px 34px;}}
  .fcttl{{font-family:"JPHeavy";font-size:30px;color:var(--gold);filter:var(--edsm);margin-bottom:6px;}}
  .fcimg{{height:440px;object-fit:contain;filter:drop-shadow(0 12px 26px rgba(0,0,0,.7));}}
  .fcname{{font-family:"JPHeavy";font-size:38px;color:#fff;filter:var(--edge);margin-top:8px;}}
  .fcres{{font-family:"JPHeavy";font-size:34px;padding:4px 22px;border-radius:8px;margin-top:10px;filter:var(--edsm);}}
  .fcres.win{{background:var(--green);color:#04210f;}}
  /* ギブソン戦 対戦カード */
  .gibcard{{position:absolute;z-index:45;left:0;right:0;top:88px;display:flex;flex-direction:column;align-items:center;opacity:0;}}
  .gibttl{{font-family:"JPHeavy";font-size:38px;color:var(--gold);filter:var(--edge);margin-bottom:10px;}}
  .gibrow{{display:flex;align-items:flex-end;justify-content:center;gap:40px;position:relative;}}
  .gibside{{display:flex;flex-direction:column;align-items:center;position:relative;}}
  .gibimg{{height:470px;object-fit:contain;filter:drop-shadow(0 14px 30px rgba(0,0,0,.75));}}
  .gibname{{font-family:"JPHeavy";font-size:40px;color:#fff;filter:var(--edge);margin-top:6px;}}
  .gibtag{{font-family:"JPHeavy";font-size:30px;padding:4px 20px;border-radius:8px;margin-top:10px;filter:var(--edsm);}}
  .gibtag.win{{background:var(--green);color:#04210f;}}
  .gibtag.lose{{background:rgba(60,70,90,.9);color:#dfe6f2;}}
  .gibmid{{display:flex;align-items:center;align-self:center;margin-bottom:130px;}}
  .gibvs{{font-family:"JPHeavy";font-size:82px;color:#fff;filter:var(--edge);}}
  .gibstamp{{position:absolute;top:250px;font-family:"JPHeavy";font-size:124px;color:var(--red);
    filter:drop-shadow(4px 0 0 #fff) drop-shadow(-4px 0 0 #fff) drop-shadow(0 4px 0 #fff) drop-shadow(0 -4px 0 #fff) drop-shadow(0 10px 22px rgba(0,0,0,.85));}}
  /* 提供対戦ポスター(縦) */
  .poster{{position:absolute;z-index:45;left:0;right:0;top:28px;display:flex;align-items:flex-start;justify-content:center;opacity:0;}}
  .poster img{{height:830px;object-fit:contain;border-radius:10px;box-shadow:0 22px 60px rgba(0,0,0,.85);}}
  /* スタッツカード */
  .statcard{{position:absolute;z-index:44;right:80px;top:300px;background:rgba(8,12,22,.9);border:2px solid #2a3a5a;border-radius:16px;padding:26px 34px;opacity:0;min-width:560px;}}
  .statttl{{font-family:"JPHeavy";font-size:36px;color:var(--gold);margin-bottom:16px;}}
  .statrow{{display:flex;align-items:baseline;gap:18px;font-family:"JPMed";font-size:34px;color:#fff;margin:10px 0;}}
  .statrow b{{font-family:"JPHeavy";}} .statrow .sv{{font-family:"JPHeavy";font-size:42px;color:var(--yellow);}}
  .statrow .sv.warn{{color:var(--red);}}
  .statnote{{font-family:"JPMed";font-size:26px;color:#9fd0ff;margin-top:14px;}}
  /* 下部字幕 */
  .subt{{position:absolute;z-index:50;left:0;right:0;bottom:96px;text-align:center;opacity:0;font-family:"JPHeavy";font-size:46px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;}}
</style></head><body>
  <div id="root" data-composition-id="aori" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
{J(bg_divs,"    ")}
    {AUDIO_BLOCK}
{J(chap_audio,"    ")}
    <div class="veil"></div>
    <div class="wm">格闘ニュースラボ</div>
{J(src_divs,"    ")}
{J(chap_divs,"    ")}
{J(pip_divs,"    ")}
{J(map_divs,"    ")}
{J(else_divs,"    ")}
{J(gib_divs,"    ")}
{J(pos_divs,"    ")}
{J(stat_divs,"    ")}
{J(sub_divs,"    ")}
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({{paused:true}});
{J(bg_tws)}
{J(chap_tws)}
{J(pip_tws)}
{J(map_tws)}
{J(else_tws)}
{J(gib_tws)}
{J(pos_tws)}
{J(stat_tws)}
{J(sub_tws)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['aori'] = tl;
    </script>
  </div>
</body></html>"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} bg={len(bg_divs)} pip={len(pip_divs)} subs={len(sub_divs)} cues={len(CUES)}")
