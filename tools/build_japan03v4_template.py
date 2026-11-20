# -*- coding: utf-8 -*-
"""japan03v4: index.html ビルダ(窓分割対応) — ref4(dLVgVtuQAOY)分析反映版
v3からの改修点 (ユーザー指摘対応):
 - 背景: 解説シーンは紙/紺グランジテクスチャ、実写は角丸カード内 or ビネット+グレイン
 - テキスト: 多層縁取り(text-shadow輪)+グラデ充填2層(stk)+インライン色分け+下線
 - 人物: pictogram2.com ベクター素材 (グレースケール統一・currentColor)
 - 吹き出し: 発言者の頭上に尻尾付きで正確に接続 (px計算)
HF_WIN_START/HF_WIN_END で窓ビルド。
"""
import json
import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "japan03v4"
TPL = ROOT / "hyperframes" / "templates" / EP
TIM = json.loads((ROOT / "subtitles" / "out" / EP / "timings.json").read_text(encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)

W0 = float(os.environ.get("HF_WIN_START") or 0)
W1 = float(os.environ.get("HF_WIN_END") or COMP)
WDUR = round(W1 - W0, 3)


def T(t):
    return round(t - W0, 3)


def OV(t0, t1):
    return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)


SC = {s["id"]: s for s in TIM["scenes"]}
N = TIM["narr"]
Q = TIM["quotes"]

ELS = []
TWEENS = []
_track = [0]


def track():
    _track[0] += 1
    return _track[0]


def el_div(eid, t0, t1, cls, inner, style=""):
    if not OV(t0, t1):
        return
    s = max(t0, W0)
    d = round(min(t1, W1 + 0.2) - s, 3)
    ELS.append(
        f'<div id="{eid}" class="clip {cls}" data-start="{T(s)}" data-duration="{d}" '
        f'data-track-index="{track()}" style="{style}">{inner}</div>')


def el_bg(wid, t0, t1, src, ms, z):
    if not OV(t0, t1):
        return
    s = max(t0, W0)
    d = round(min(t1, W1 + 0.2) - s, 3)
    ms_eff = round(ms + (s - t0), 3)
    ELS.append(
        f'<div class="bgw" id="w_{wid}" style="z-index:{z}">'
        f'<video class="clip bgv" data-start="{T(s)}" data-duration="{d}" '
        f'data-media-start="{ms_eff}" data-track-index="{track()}" '
        f'src="assets/bg/{src}" muted playsinline></video></div>')


def el_tex(wid, t0, t1, tex, z):
    """テクスチャ背景 (静的img)"""
    if not OV(t0, t1):
        return
    ELS.append(
        f'<div class="bgw" id="w_{wid}" style="z-index:{z}">'
        f'<img class="texbg" src="assets/tex/{tex}"></div>')


def tw(t, js):
    TWEENS.append(js.replace("%T%", str(round(t, 3))))


def fromto(t, sel, frm, to, dur, ease):
    tw(t, f'tl.fromTo("{sel}", {{{frm}}}, {{{to}, duration: {dur}, ease: "{ease}", immediateRender: false}}, %T%);')


def setv(t, sel, vars_):
    tw(t, f'tl.set("{sel}", {{{vars_}}}, %T%);')


ZBG = [0]


def zbg():
    ZBG[0] += 1
    return ZBG[0]


def xfade(wid, t0, dur_total, z1=1.05, z0=1.0):
    fromto(t0, f"#w_{wid}", "opacity: 0", "opacity: 1", 0.45, "power1.inOut")
    tw(t0, f'tl.fromTo("#w_{wid}", {{scale: {z0}}}, {{scale: {z1}, duration: {round(dur_total, 2)}, '
           f'ease: "none", immediateRender: false}}, %T%);')


def hardcut(wid, t0, dur_total, z1=1.06):
    setv(t0, f"#w_{wid}", "opacity: 1")
    tw(t0, f'tl.fromTo("#w_{wid}", {{scale: 1.0}}, {{scale: {z1}, duration: {round(dur_total, 2)}, '
           f'ease: "none", immediateRender: false}}, %T%);')


def scene_bg(sid, last=False, cut=False):
    sc = SC[sid]
    t0 = sc["start"]
    t1 = COMP if last else sc["end"] + 0.55
    z = zbg()
    el_bg(sid, t0, t1, f"bg_{sid}.mp4", 0.0, z)
    if cut:
        hardcut(sid, t0, t1 - t0)
    else:
        xfade(sid, t0, t1 - t0)


def scene_tex(sid, tex, last=False, cut=True):
    sc = SC[sid]
    t0 = sc["start"]
    t1 = COMP if last else sc["end"] + 0.55
    z = zbg()
    el_tex(sid, t0, t1, tex, z)
    if cut:
        hardcut(sid, t0, t1 - t0, z1=1.035)
    else:
        xfade(sid, t0, t1 - t0, z1=1.035)


# ---- pictogram (ベクター, currentColor)
PICTO_DIR = TPL / "assets" / "picto"
_PC = {}


def picto(name, h, cls=""):
    """SVG挿入。返り値 (html, 実px幅)"""
    if name not in _PC:
        _PC[name] = (PICTO_DIR / f"{name}.svg").read_text(encoding="utf-8")
    svg = _PC[name]
    vb = re.search(r'viewBox="([-\d. ]+)"', svg).group(1).split()
    w = float(vb[2]) * h / float(vb[3])
    html = svg.replace('<svg ', f'<svg class="pic {cls}" style="height:{h}px" ', 1)
    return html, round(w)


def bubble(bid, text, left, bottom, tail_x, w=None, cls=""):
    """吹き出し: tail_x = 吹き出し左端からの尻尾中心px (発言者の頭上に合わせる)"""
    ws = f"width:{w}px;" if w else ""
    return (f'<div class="bubble {cls}" id="{bid}" style="left:{left}px; bottom:{bottom}px; {ws}">'
            f'{text}<svg class="btail" style="left:{tail_x - 15}px" viewBox="0 0 30 24">'
            f'<path d="M1 2 L29 2 L13 23 Z"/></svg></div>')


def stk(text, fill, w=12, color="#17120d"):
    """2層ストローク文字 (縁取り+グラデ充填)。textはプレーン文字列のみ"""
    return (f'<span class="stkw"><span class="stkl" style="-webkit-text-stroke:{w}px {color}">{text}</span>'
            f'<span class="stkf {fill}">{text}</span></span>')


def ring(px, color, n=16):
    parts = [f"{px * math.cos(2 * math.pi * i / n):.1f}px {px * math.sin(2 * math.pi * i / n):.1f}px 0 {color}"
             for i in range(n)]
    return ", ".join(parts)


OLK = ring(5, "#0b0d12") + ", 0 6px 22px rgba(0,0,0,.6)"       # 黒縁 (白文字用)
OLK7 = ring(7, "#0b0d12") + ", 0 8px 28px rgba(0,0,0,.65)"     # 黒縁太
OLW = ring(5, "#f4efe2") + ", 0 4px 16px rgba(70,58,34,.28)"   # 白縁 (紙上の濃文字用)


def telop(eid, lid, html, hold=0.6, serif=False, paper=False):
    st = N[lid]["start"] - 0.05
    en = N[lid]["start"] + N[lid]["dur"] + hold
    cls = "telop ts" if serif else "telop"
    if paper:
        cls += " tpp"
    el_div(eid, st, en, "telopw", f'<div class="{cls}" id="{eid}i">{html}</div>')
    fromto(st + 0.02, f"#{eid}i", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.3, "power2.out")
    tw(en - 0.25, f'tl.to("#{eid}i", {{opacity: 0, duration: 0.22}}, %T%);')


# ============================================================ s_cold: q_ms1 肉声 (全面引用+字幕強化)
qi = Q["q_ms1"]
t0 = qi["beat_start"]
t1 = t0 + qi["dur"]
z = zbg()
if OV(t0, t1 + 0.3):
    s = max(t0, W0)
    d = round(min(t1 + 0.3, W1 + 0.2) - s, 3)
    ms_eff = round(qi["media_start"] + (s - t0), 3)
    ELS.append(
        f'<div class="bgw" id="w_s_cold" style="z-index:{z}">'
        f'<video class="clip bgv" data-start="{T(s)}" data-duration="{d}" '
        f'data-media-start="{ms_eff}" data-track-index="{track()}" '
        f'src="assets/bg/{qi["clip"]}" muted playsinline></video></div>')
fromto(t0, "#w_s_cold", "opacity: 0", "opacity: 1", 0.5, "power1.inOut")
tw(t0, f'tl.fromTo("#w_s_cold", {{scale: 1.04}}, {{scale: 1.0, duration: {round(t1 - t0, 2)}, '
       f'ease: "none", immediateRender: false}}, %T%);')
el_div("msq", t0, t1 + 0.1, "qov", (
    '<div class="nplate" id="msp"><div class="ntag">在日中国人クリエイターの記録</div>'
    '<div class="ncredit">引用: 有話銘說(大阪)</div></div>'
    '<div class="qcap" id="msc1">地面には、散った桜の花びらだけ。<br>ほかのゴミが、<span class="gd ulg">ほとんど無い</span>——</div>'
    '<div class="qcap qbig" id="msc2">「なんで、こんなに<span class="gd">きれい</span>なんだ?」</div>'
    '<div class="qcap" id="msc3">その一言に、思わず、足を緩めた</div>'))
sp = t0 + qi["lead"]
fromto(t0 + 0.3, "#msp", "x: -16, opacity: 0", "x: 0, opacity: 1", 0.4, "power2.out")
fromto(sp + 0.2, "#msc1", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
setv(sp + 6.8, "#msc1", "opacity: 0")
fromto(sp + 6.95, "#msc2", 'scale: 1.3, opacity: 0, rotation: -2, filter: "blur(5px)"',
       'scale: 1, opacity: 1, rotation: 0, filter: "blur(0px)"', 0.35, "back.out(1.7)")
setv(sp + 9.6, "#msc2", "opacity: 0")
fromto(sp + 9.75, "#msc3", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")

# ============================================================ s_think: 紙+走る人ピクト+吹き出し+桜カード
scene_tex("s_think", "paper_light.png", cut=True)
sc = SC["s_think"]
telop("tp01", "n01", '観光客の<span class="rdp ulr">ひと言</span>が、彼を立ち止まらせた', serif=True, paper=True)
ft = N["n01"]["start"] + 0.9
run_svg, run_w = picto("run", 330, "ink")
# 走者: left 420px, bottom 300px → 頭中心 ≈ left+run_w*0.55
run_left, run_bottom = 400, 310
head_x = run_left + int(run_w * 0.55)
bub_left = head_x - 320
el_div("thf", ft - 0.15, sc["end"] + 0.1, "figwrap", (
    f'<div class="ccap pcapTL" id="thcap">大阪・桜の季節</div>'
    f'<svg class="spdl" id="thsp" viewBox="0 0 120 90" style="left:{run_left - 215}px; bottom:{run_bottom + 80}px">'
    '<path d="M8 10 H78"/><path d="M22 42 H112"/><path d="M8 74 H64"/></svg>'
    f'<div class="fig" id="thfg" style="left:{run_left}px; bottom:{run_bottom}px">{run_svg}</div>'
    + bubble("thbb", "走りながら、<br>考え込んでしまった——", bub_left, run_bottom + 345,
             head_x - bub_left, cls="bink")))
fromto(ft, "#thfg", "x: -60, opacity: 0", "x: 0, opacity: 1", 0.45, "power3.out")
fromto(ft + 0.05, "#thsp", "x: -40, opacity: 0", "x: 0, opacity: 0.5", 0.45, "power3.out")
fromto(ft - 0.3, "#thcap", "x: -14, opacity: 0", "x: 0, opacity: 1", 0.3, "power2.out")
fromto(ft + 1.3, "#thbb", "scale: 0.4, opacity: 0, rotation: -4", "scale: 1, opacity: 1, rotation: 0",
       0.42, "back.out(2.0)")
# 桜実写カード (右上・白枠・傾き)
if OV(sc["start"] + 0.3, sc["end"] + 0.1):
    s = max(sc["start"] + 0.3, W0)
    d = round(min(sc["end"] + 0.1, W1 + 0.2) - s, 3)
    ms_eff = round(0.0 + (s - (sc["start"] + 0.3)), 3)
    ELS.append(
        '<div class="fcard" id="thcard" style="right:120px; top:150px; width:560px; height:315px; '
        'transform:rotate(2.2deg)">'
        f'<video class="clip cardv" data-start="{T(s)}" data-duration="{d}" data-media-start="{ms_eff}" '
        f'data-track-index="{track()}" src="assets/bg/bg_s_think.mp4" muted playsinline></video>'
        '<div class="fclabel">大阪城公園</div></div>')
fromto(sc["start"] + 0.55, "#thcard", "y: -26, opacity: 0, rotation: 4", "y: 0, opacity: 1, rotation: 2.2",
       0.45, "power2.out")
tw(sc["end"] - 0.12, 'tl.to("#thcard", {opacity: 0, duration: 0.18}, %T%);')

# ============================================================ s_title: グラデ+ストローク+フラッシュ
scene_bg("s_title", cut=True)
sc = SC["s_title"]
tt = sc["start"] + 0.15
el_div("ttl", sc["start"], sc["end"] + 0.1, "twrap", (
    '<div class="tdark" id="tdk"></div>'
    '<div class="tlabel" id="tlb">ある在日中国人の「違和感」から始まる話</div>'
    f'<div class="ttitle" id="tti">{stk("中国とは、", "gfw", 14)}{stk("違いすぎた", "gfr", 14)}</div>'
    '<div class="tline" id="tln"></div>'
    '<div class="tsub" id="tsb">909万人が気づいた、日中の決定的な差</div>'))
fromto(tt, "#tdk", "opacity: 0", "opacity: 0.72", 0.3, "power1.in")
fromto(tt + 0.1, "#tlb", "opacity: 0, y: -12", "opacity: 1, y: 0", 0.4, "power2.out")
fromto(tt + 0.55, "#tti", 'opacity: 0, scale: 1.45, rotation: -2.5, filter: "blur(10px)"',
       'opacity: 1, scale: 1, rotation: 0, filter: "blur(0px)"', 0.42, "power3.out")
setv(tt + 0.9, "#flash", "opacity: 0.75")
tw(tt + 0.95, 'tl.to("#flash", {opacity: 0, duration: 0.3, ease: "power2.out"}, %T%);')
fromto(tt + 1.05, "#tln", "scaleX: 0", "scaleX: 1", 0.45, "power2.inOut")
fromto(tt + 1.3, "#tsb", "opacity: 0", "opacity: 1", 0.4, "power2.out")

# ============================================================ s_data1: 紙+特大数値+JALカード+歩行ピクト列
scene_tex("s_data1", "paper_light.png", cut=True)
sc = SC["s_data1"]
el_div("sl1", sc["start"] + 0.2, sc["end"] + 0.1, "srcw",
       '<div class="srclabel" id="sl1i">JNTO 訪日外客統計<span class="srcsub">2025</span></div>')
fromto(sc["start"] + 0.3, "#sl1i", "x: -14, opacity: 0, rotation: -2", "x: 0, opacity: 1, rotation: -1.2",
       0.35, "power2.out")
d1 = N["n02"]["start"]
walk_svg, walk_w = picto("walk", 76, "ink")
walkrow = "".join(f'<div class="wk" id="wk{i}">{walk_svg}</div>' for i in range(5))
el_div("bn1", sc["start"] + 0.2, sc["end"] + 0.1, "bnwrap", (
    '<div class="bnlabel" id="bnl">2025年に日本を訪れた中国人</div>'
    '<div class="bignum" id="bnn"><span class="stkw"><span class="stkl bnd" id="dnvl">0</span>'
    '<span class="stkf gfg bnd" id="dnv">0</span></span><span class="bnunit">万人</span></div>'
    '<svg class="bncirc" id="bnc" viewBox="0 0 560 240"><ellipse cx="280" cy="120" rx="262" ry="104"/></svg>'
    '<div class="bnrow" id="bnr1">前年比 <span class="rdp ulr">+30.3%</span> — 過去最多ペース</div>'
    f'<div class="walkrow" id="wkr">{walkrow}</div>'))
fromto(d1 - 0.1, "#bnl", "y: 20, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
fromto(d1 + 0.7, "#bnn", "opacity: 0, y: 24", "opacity: 1, y: 0", 0.3, "power2.out")
tw(d1 + 0.9, 'tl.fromTo(CNT, {v: 0}, {v: 909, duration: 1.15, ease: "power2.out", '
             'onUpdate: () => { const a = document.getElementById("dnv"); '
             'const b = document.getElementById("dnvl"); const s = String(Math.round(CNT.v)); '
             'if (a) a.textContent = s; if (b) b.textContent = s; }}, %T%);')
fromto(d1 + 2.2, "#bnc", "scale: 1.3, opacity: 0", "scale: 1, opacity: 1", 0.35, "back.out(1.8)")
fromto(d1 + 2.9, "#bnr1", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.35, "power2.out")
for i in range(5):
    fromto(d1 + 1.0 + 0.16 * i, f"#wk{i}", "x: -30, opacity: 0", "x: 0, opacity: 1", 0.3, "power2.out")
# JAL実写カード (左下・モノクロ)
if OV(sc["start"] + 0.4, sc["end"] + 0.1):
    s = max(sc["start"] + 0.4, W0)
    d = round(min(sc["end"] + 0.1, W1 + 0.2) - s, 3)
    ms_eff = round(0.0 + (s - (sc["start"] + 0.4)), 3)
    ELS.append(
        '<div class="fcard mono" id="d1card" style="left:110px; bottom:150px; width:470px; height:264px; '
        'transform:rotate(-2deg)">'
        f'<video class="clip cardv" data-start="{T(s)}" data-duration="{d}" data-media-start="{ms_eff}" '
        f'data-track-index="{track()}" src="assets/bg/bg_s_data1.mp4" muted playsinline></video>'
        '<div class="fclabel">羽田空港</div></div>')
fromto(sc["start"] + 0.65, "#d1card", "y: 26, opacity: 0, rotation: -4", "y: 0, opacity: 1, rotation: -2",
       0.45, "power2.out")
tw(sc["end"] - 0.12, 'tl.to("#d1card", {opacity: 0, duration: 0.18}, %T%);')

# ============================================================ s_data2: 紺パネル+行積み上げ
scene_tex("s_data2", "panel_navy.png", cut=True)
sc = SC["s_data2"]
el_div("lb2", sc["start"] + 0.1, sc["end"] + 0.1, "lbwrap", (
    '<div class="lbrow" id="lr1"><span class="lbar"></span>2025年8月 ⇒ ひと月で<span class="gd ulg">100万人</span>を突破</div>'
    '<div class="lbrow" id="lr2"><span class="lbar"></span>国・地域別の訪日客数 ⇒ <span class="rd ulr">最多</span>に</div>'))
d2 = N["n03"]["start"]
fromto(d2 - 0.05, "#lr1", "x: -26, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")
fromto(d2 + 2.0, "#lr2", "x: -26, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")
# 空港実写カード (右下・モノクロ)
if OV(sc["start"] + 0.3, sc["end"] + 0.1):
    s = max(sc["start"] + 0.3, W0)
    d = round(min(sc["end"] + 0.1, W1 + 0.2) - s, 3)
    ms_eff = round(0.0 + (s - (sc["start"] + 0.3)), 3)
    ELS.append(
        '<div class="fcard mono" id="d2card" style="right:130px; bottom:170px; width:470px; height:264px; '
        'transform:rotate(2deg)">'
        f'<video class="clip cardv" data-start="{T(s)}" data-duration="{d}" data-media-start="{ms_eff}" '
        f'data-track-index="{track()}" src="assets/bg/bg_s_data2.mp4" muted playsinline></video>'
        '<div class="fclabel">到着ロビー</div></div>')
fromto(sc["start"] + 0.5, "#d2card", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.45, "power2.out")
tw(sc["end"] - 0.12, 'tl.to("#d2card", {opacity: 0, duration: 0.18}, %T%);')

# ============================================================ s_cn: 3ハードカット+隅キャプション (ビネット+行)
sc = SC["s_cn"]
cn0 = sc["start"]
cn_end = sc["end"] + 0.55
seg = (sc["end"] - sc["start"]) / 3
cuts = [cn0, cn0 + seg, cn0 + 2 * seg]
for i, (wid, src) in enumerate((("cn_a", "bg_cn_a.mp4"), ("cn_b", "bg_cn_b.mp4"), ("cn_c", "bg_cn_c.mp4"))):
    t_s = cuts[i]
    t_e = (cuts[i + 1] + 0.1) if i < 2 else cn_end
    z = zbg()
    el_bg(wid, t_s, t_e, src, 0.0, z)
    hardcut(wid, t_s, t_e - t_s)
caps = [("cc1", "中国・上海", "ccTL"), ("cc2", "高速鉄道 350km/h", "ccBR"), ("cc3", "中国・深圳", "ccTL")]
for i, (cid, label, pos) in enumerate(caps):
    t_s = cuts[i]
    t_e = (cuts[i + 1] + 0.05) if i < 2 else sc["end"]
    el_div(cid, t_s, t_e, f"ccwrap {pos}", f'<div class="ccap" id="{cid}i">{label}</div>')
    fromto(t_s + 0.15, f"#{cid}i", "x: -12, opacity: 0", "x: 0, opacity: 1", 0.3, "power2.out")
n4 = N["n04"]["start"]
el_div("cnl", cn0, sc["end"] + 0.1, "cnlines", (
    '<div class="cnrow" id="cnr1">夜は、東京より<span class="gd ulg">明るい</span></div>'
    '<div class="cnrow" id="cnr2">高鉄は、時速<span class="bl">350キロ</span></div>'
    '<div class="cnrow" id="cnr3">財布は、<span class="rd ulr">持ち歩かない</span></div>'))
fromto(n4 + 3.4, "#cnr1", "x: 26, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")
fromto(n4 + 5.9, "#cnr2", "x: 26, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")
fromto(n4 + 8.9, "#cnr3", "x: 26, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")

# ============================================================ s_why: 紺+赤ラジアル+質問カード
scene_tex("s_why", "panel_navy.png", cut=True)
sc = SC["s_why"]
el_div("why", sc["start"], sc["end"] + 0.1, "qcwrap", (
    '<div class="qcdark" id="qcd"></div>'
    f'<div class="qctext" id="qct">なぜ、<span class="rd">909万人</span>は<br>日本へ?</div>'
    '<div class="qcsub" id="qcs">— 何もかも、進んでいるはずなのに</div>'))
w0t = N["n05"]["start"] - 0.15
fromto(w0t, "#qcd", "opacity: 0", "opacity: 0.85", 0.4, "power1.in")
fromto(w0t + 0.25, "#qct", 'opacity: 0, scale: 1.12, filter: "blur(7px)"',
       'opacity: 1, scale: 1, filter: "blur(0px)"', 0.5, "power2.out")
fromto(w0t + 1.6, "#qcs", "opacity: 0", "opacity: 1", 0.45, "power2.out")

# ============================================================ s_fam: 実写+家族ピクト+接続吹き出し
scene_bg("s_fam")
sc = SC["s_fam"]
telop("tp06", "n06", 'マレーシアの中華系ファミリー・<span class="gd ulg">6人</span>の記録', hold=0.5)
f2_svg, f2_w = picto("family2", 300, "wt")
f3_svg, f3_w = picto("family3", 285, "wt")
# 配置: family2(父中心) + family3 = 6人 (名札の人数と一致させる)
g1_left = 430
g2_left = g1_left + f2_w + 130
fam_bottom = 210
# family2 の父=グループ左側 ≈ left + f2_w*0.22 (吹き出し接続先)
dad_x = g1_left + int(f2_w * 0.22)
bubf_left = max(120, dad_x - 300)
el_div("fam", sc["start"] + 0.3, sc["end"] + 0.1, "figwrap", (
    '<div class="nplate npfam" id="fmp"><div class="ntag">家族6人・初めての日本</div>'
    '<div class="ncredit">引用: Nicaboo</div></div>'
    f'<div class="fig" id="fg1" style="left:{g1_left}px; bottom:{fam_bottom}px">{f2_svg}</div>'
    f'<div class="fig" id="fg2" style="left:{g2_left}px; bottom:{fam_bottom}px">{f3_svg}</div>'
    + bubble("fmb", "家族旅行が、<br>こんなことになるなんて", bubf_left, fam_bottom + 315,
             dad_x - bubf_left, cls="bwt")))
f0 = N["n06"]["start"] + 0.8
fromto(f0 - 0.5, "#fmp", "x: -16, opacity: 0", "x: 0, opacity: 1", 0.4, "power2.out")
for i, g in enumerate(("#fg1", "#fg2")):
    fromto(f0 + 0.42 * i, g, "y: 30, opacity: 0", "y: 0, opacity: 1", 0.34, "back.out(1.5)")
fromto(f0 + 3.2, "#fmb", "scale: 0.4, opacity: 0, rotation: -3", "scale: 1, opacity: 1, rotation: 0",
       0.4, "back.out(2.0)")

# ============================================================ s_noodle: 実写+引用ボックス+食事ピクト
scene_bg("s_noodle")
sc = SC["s_noodle"]
el_div("ncc", sc["start"] + 0.2, sc["end"] + 0.1, "ccwrap ccTL",
       '<div class="ccap" id="ncci">到着初日・最初の一杯</div>')
fromto(sc["start"] + 0.35, "#ncci", "x: -12, opacity: 0", "x: 0, opacity: 1", 0.3, "power2.out")
qt = N["n07"]["start"] + N["n07"]["dur"] + 0.25
eat_svg, eat_w = picto("eat", 250, "wt")
el_div("tq", qt - 0.1, sc["end"] + 0.1, "tqwrap", (
    '<div class="qbox" id="tqt">「コシがあって、柔らかい。<br>この味、<span class="gd ulg">好き</span>」'
    '<div class="tqsrc">— 家族の記録より(引用: Nicaboo)</div>'
    '<svg class="btail bt-box" viewBox="0 0 30 24"><path d="M1 2 L29 2 L13 23 Z"/></svg></div>'
    f'<div class="fig" id="tqf" style="left:380px; bottom:180px">{eat_svg}</div>'))
fromto(qt, "#tqt", 'opacity: 0, y: 20, filter: "blur(6px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.5, "power2.out")
fromto(qt + 0.35, "#tqf", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.35, "back.out(1.6)")

# ============================================================ s_coldlead
scene_bg("s_coldlead", cut=True)
telop("tp08", "n08", 'ただし、日本の冬を<span class="rd ulr">なめてはいけない</span>', hold=0.3, serif=True)

# ============================================================ s_coldq: n_cold 肉声
qi = Q["n_cold"]
t0 = qi["beat_start"]
t1 = t0 + qi["dur"]
z = zbg()
if OV(t0, t1 + 0.3):
    s = max(t0, W0)
    d = round(min(t1 + 0.3, W1 + 0.2) - s, 3)
    ms_eff = round(qi["media_start"] + (s - t0), 3)
    ELS.append(
        f'<div class="bgw" id="w_s_coldq" style="z-index:{z}">'
        f'<video class="clip bgv" data-start="{T(s)}" data-duration="{d}" '
        f'data-media-start="{ms_eff}" data-track-index="{track()}" '
        f'src="assets/bg/{qi["clip"]}" muted playsinline></video></div>')
fromto(t0, "#w_s_coldq", "opacity: 0", "opacity: 1", 0.45, "power1.inOut")
el_div("nco", t0, t1 + 0.1, "qov", (
    '<div class="nplate" id="ncp"><div class="ntag">東京の夜 — 家族の記録</div>'
    '<div class="ncredit">引用: Nicaboo</div></div>'
    '<div class="qcap" id="ncc1">「こんなに寒いと 思わなかった…」</div>'
    '<div class="qcap qbig" id="ncc2">「いま ちょっと<span class="rd">後悔</span>してます(笑)」</div>'))
sp = t0 + qi["lead"]
fromto(t0 + 0.25, "#ncp", "x: -16, opacity: 0", "x: 0, opacity: 1", 0.4, "power2.out")
fromto(sp + 0.15, "#ncc1", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
setv(sp + 3.9, "#ncc1", "opacity: 0")
fromto(sp + 4.0, "#ncc2", 'scale: 1.25, opacity: 0, rotation: -1.5', 'scale: 1, opacity: 1, rotation: 0',
       0.35, "back.out(1.6)")

# ============================================================ s_pivot: 紺+お辞儀ピクト+伏字
scene_tex("s_pivot", "panel_navy.png", cut=True)
sc = SC["s_pivot"]
telop("tp09", "n09", '彼らの心を動かしたのは、<span class="gd ulg">別のもの</span>', hold=0.1)
pv_items = [("trash", "ゴミは、持ち帰る"), ("clean", "通る場所を、汚さない"), ("bow", "そっと、頭を下げる")]
panels = []
for i, (pname, plabel) in enumerate(pv_items):
    psvg, _ = picto(pname, 185, "wt")
    panels.append(
        f'<div class="pvpanel" id="pvp{i}" style="left:{330 + i * 440}px">'
        f'<div class="pvpic">{psvg}</div><div class="pvlabel">{plabel}</div></div>')
el_div("pvf", sc["start"] + 0.4, sc["end"] + 0.1, "figwrap", "".join(panels))
p0 = N["n09"]["start"] + 0.6
for i in range(3):
    fromto(p0 + 1.0 * i, f"#pvp{i}", "y: 30, opacity: 0, scale: 1.12", "y: 0, opacity: 1, scale: 1",
           0.38, "back.out(1.6)")
kt = N["n09"]["start"] + N["n09"]["dur"] + 0.3
el_div("kx", kt - 0.1, sc["end"] + 0.1, "kwrap", (
    '<div class="kdark"></div>'
    '<div class="kick" id="kk">本当の驚きは、<span class="fsslot">'
    '<span class="fsw fsa" id="fsa">●●●</span><span class="fsw fsb" id="fsb">気配り</span>'
    '<span class="fsul" id="fsu"></span>'
    '</span>だった</div>'))
fromto(kt, "#kk", 'opacity: 0, y: 20', 'opacity: 1, y: 0', 0.5, "power2.out")
setv(kt, "#fsb", "opacity: 0, xPercent: -50")
ft = kt + 1.75
tw(ft, 'tl.to("#fsa", {opacity: 0, filter: "blur(8px)", duration: 0.2}, %T%);')
fromto(ft + 0.1, "#fsb", 'opacity: 0, xPercent: -50, scale: 1.4, filter: "blur(6px)"',
       'opacity: 1, xPercent: -50, scale: 1, filter: "blur(0px)"', 0.4, "power3.out")
fromto(ft + 0.5, "#fsu", "scaleX: 0", "scaleX: 1", 0.3, "power2.inOut")

# ============================================================ s_ch1 (章扉)
scene_bg("s_ch1", last=True)
sc = SC["s_ch1"]
el_div("c1o", sc["start"], COMP, "qov", (
    '<div class="cdark"></div>'
    '<div class="cframe" id="cf1"></div>'
    '<div class="cwrap"><div class="cno" id="cn1">第 1 章</div>'
    '<div class="cline" id="cl1"></div>'
    f'<div class="ctitle" id="ct1">{stk("丁寧さの、正体", "gfw", 10)}</div>'
    '<div class="csub" id="cs1">— ある中国人が、日本で通報された話</div></div>'))
t0 = sc["start"]
setv(t0 - 0.45, "#dip", "opacity: 0")
tw(t0 - 0.45, 'tl.to("#dip", {opacity: 1, duration: 0.35, ease: "power1.in"}, %T%);')
tw(t0 + 0.05, 'tl.to("#dip", {opacity: 0, duration: 0.5, ease: "power1.out"}, %T%);')
fromto(t0 + 0.3, "#cf1", "opacity: 0, scale: 1.04", "opacity: 1, scale: 1", 0.55, "power2.out")
fromto(t0 + 0.35, "#cn1", "y: -16, opacity: 0", "y: 0, opacity: 1", 0.5, "power3.out")
fromto(t0 + 0.6, "#cl1", "scaleX: 0", "scaleX: 1", 0.45, "power2.inOut")
fromto(t0 + 0.8, "#ct1", 'opacity: 0, y: 24, filter: "blur(9px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.65, "power2.out")
fromto(t0 + 1.5, "#cs1", "opacity: 0", "opacity: 1", 0.45, "power2.out")
tw(COMP - 1.15, 'tl.to("#stage", {opacity: 0, duration: 1.0, ease: "power1.in"}, %T%);')

# ============================================================ assemble html
CSS = f"""
@font-face {{ font-family:'NotoB'; src:url('assets/fonts/NotoSansJP-Black.otf') format('opentype'); }}
@font-face {{ font-family:'NotoBd'; src:url('assets/fonts/NotoSansJP-Bold.otf') format('opentype'); }}
@font-face {{ font-family:'ShipA'; src:url('assets/fonts/ShipporiMinchoB1-ExtraBold.ttf') format('truetype'); }}
@font-face {{ font-family:'Dela'; src:url('assets/fonts/DelaGothicOne-Regular.ttf') format('truetype'); }}
@font-face {{ font-family:'ZenK'; src:url('assets/fonts/ZenKakuGothicNew-Black.ttf') format('truetype'); }}
@font-face {{ font-family:'ZenB'; src:url('assets/fonts/ZenKakuGothicNew-Bold.ttf') format('truetype'); }}
@font-face {{ font-family:'MPR'; src:url('assets/fonts/MPLUSRounded1c-ExtraBold.ttf') format('truetype'); }}
@font-face {{ font-family:'Yusei'; src:url('assets/fonts/YuseiMagic-Regular.ttf') format('truetype'); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ background:#000; }}
#root {{ position:relative; width:1920px; height:1080px; overflow:hidden;
  background:#0a0d14; font-family:'NotoBd',sans-serif; color:#f2f4f8; }}
#stage {{ position:absolute; inset:0; }}
.clip {{ position:absolute; inset:0; width:100%; height:100%; }}
.bgw {{ position:absolute; inset:0; opacity:0; will-change:transform,opacity; }}
video.bgv {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover;
  transform:translateZ(0); backface-visibility:hidden; }}
img.texbg {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
/* カラー/強調 */
.gd {{ color:#e8c872; }} .rd {{ color:#ff6a55; }} .bl {{ color:#7db8e8; }} .gr {{ color:#7ec87e; }}
.rdp {{ color:#c2342a; }}
.ulg {{ background:linear-gradient(transparent 84%, rgba(232,200,114,.95) 84%); padding:0 2px 3px; }}
.ulr {{ background:linear-gradient(transparent 84%, rgba(255,90,68,.95) 84%); padding:0 2px 3px; }}
.tpp .ulr, .bnrow .ulr {{ background:linear-gradient(transparent 84%, rgba(194,52,42,.9) 84%); }}
/* オーバーレイ */
#vig {{ position:absolute; inset:0; z-index:27; pointer-events:none;
  background:radial-gradient(ellipse at center, rgba(0,0,0,0) 52%, rgba(0,0,0,.40) 100%); }}
#grainov {{ position:absolute; inset:0; z-index:28; pointer-events:none; opacity:.07;
  background:url('assets/tex/grain.png'); mix-blend-mode:overlay; }}
#scrim {{ position:absolute; inset:0; z-index:29; pointer-events:none;
  background:linear-gradient(0deg, rgba(5,7,12,.62) 0%, rgba(5,7,12,.12) 15%, rgba(5,7,12,0) 30%); }}
#barT, #barB {{ position:absolute; left:0; right:0; height:56px; background:#000; z-index:40; }}
#barT {{ top:0; }} #barB {{ bottom:0; }}
#dip {{ position:absolute; inset:0; background:#000; z-index:38; opacity:0; pointer-events:none; }}
#flash {{ position:absolute; inset:0; background:#fff; z-index:37; opacity:0; pointer-events:none; }}
/* 2層ストローク文字 */
.stkw {{ position:relative; display:inline-block;
  filter:drop-shadow(0 6px 20px rgba(0,0,0,.55)); }}
.stkl {{ position:absolute; left:0; top:0; color:transparent; z-index:0; }}
.stkf {{ position:relative; z-index:1; }}
.gfw {{ background:linear-gradient(180deg,#ffffff 12%,#e9edf5 55%,#b9c4d6 92%);
  -webkit-background-clip:text; background-clip:text; color:transparent; }}
.gfr {{ background:linear-gradient(180deg,#ffd9d0 6%,#ff6a50 48%,#c21f12 94%);
  -webkit-background-clip:text; background-clip:text; color:transparent; }}
.gfg {{ background:linear-gradient(180deg,#fffdf2 8%,#ffe9a8 46%,#dfa23e 92%);
  -webkit-background-clip:text; background-clip:text; color:transparent; }}
/* テロップ */
.telopw {{ z-index:33; pointer-events:none; display:flex; align-items:flex-end;
  justify-content:center; padding-bottom:86px; }}
.telop {{ font-family:'NotoB'; font-size:47px; letter-spacing:.04em; text-align:center;
  max-width:1680px; color:#f6f7fa; opacity:0; text-shadow:{OLK}; }}
.telop.ts {{ font-family:'ShipA'; font-size:51px; letter-spacing:.05em; }}
.telop.tpp {{ color:#262230; text-shadow:{OLW}; }}
/* 名札 + 引用字幕 */
.qov {{ z-index:34; pointer-events:none; }}
.nplate {{ position:absolute; left:56px; top:84px; opacity:0; transform:rotate(-1.2deg); }}
.nplate .ntag {{ display:inline-block; background:#c2342a; color:#fff; font-family:'ZenK';
  font-size:31px; letter-spacing:.06em; padding:10px 22px;
  border:3px solid rgba(255,255,255,.92); box-shadow:0 5px 18px rgba(0,0,0,.55); }}
.nplate .ncredit {{ display:block; margin-top:7px; background:rgba(5,8,14,.78); color:#d7dfe9;
  font-family:'ZenB'; font-size:20px; padding:5px 12px; width:max-content; }}
.qcap {{ position:absolute; left:60px; right:60px; bottom:172px; text-align:center; font-size:51px;
  font-family:'ShipA'; color:#f6f3ea; letter-spacing:.02em; opacity:0; text-shadow:{OLK}; }}
.qcap.qbig {{ font-size:66px; bottom:162px; text-shadow:{OLK7}; }}
/* ピクトグラム + 吹き出し */
.figwrap {{ z-index:33; pointer-events:none; }}
.pic {{ display:block; }}
.ink {{ color:#2a2733; filter:drop-shadow(0 5px 12px rgba(70,58,34,.30)); }}
.wt {{ color:#f4f6f9; filter:drop-shadow(0 6px 16px rgba(0,0,0,.55)); }}
.fig {{ position:absolute; opacity:0; }}
.spdl {{ position:absolute; width:190px; opacity:0; }}
.spdl path {{ stroke:#2a2733; stroke-width:11; stroke-linecap:round; fill:none; }}
.bubble {{ position:absolute; background:#fffdf6; color:#1a1d26; font-family:'MPR';
  font-size:34px; line-height:1.45; padding:18px 28px; border-radius:18px; opacity:0;
  border:3.5px solid #14161c; box-shadow:0 8px 26px rgba(0,0,0,.35);
  transform-origin:60% 100%; }}
.btail {{ position:absolute; bottom:-22px; width:30px; height:24px; }}
.btail path {{ fill:#fffdf6; stroke:#14161c; stroke-width:3; }}
.bubble.bwt {{ background:#ffffff; }}
/* 実写カード */
.fcard {{ position:absolute; border:5px solid rgba(255,255,255,.94); border-radius:14px;
  overflow:hidden; opacity:0; box-shadow:0 14px 40px rgba(20,14,8,.45); z-index:32; }}
.fcard video.cardv {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.fcard.mono video.cardv {{ filter:grayscale(1) contrast(1.06) brightness(1.02); }}
.fclabel {{ position:absolute; left:0; bottom:0; background:rgba(8,10,14,.82); color:#e8ebf0;
  font-family:'ZenB'; font-size:21px; padding:5px 14px; border-top-right-radius:10px; }}
/* タイトル */
.twrap {{ z-index:35; pointer-events:none; }}
.tdark {{ position:absolute; inset:0; background:#06080e; opacity:0; }}
.tlabel {{ position:absolute; left:0; right:0; top:286px; text-align:center; font-family:'ZenB';
  font-size:30px; letter-spacing:.3em; color:#dfe5ee; opacity:0; text-shadow:{OLK}; }}
.ttitle {{ position:absolute; left:0; right:0; top:352px; text-align:center; font-family:'Dela';
  font-size:128px; opacity:0; letter-spacing:.01em; }}
.ttitle .stkw {{ margin:0 -2px; }}
.tline {{ position:absolute; left:50%; top:604px; width:620px; margin-left:-310px; height:4px;
  transform-origin:center; transform:scaleX(0);
  background:linear-gradient(90deg, rgba(232,200,114,0), #e8c872 30%, #ff6a55 70%, rgba(255,106,85,0)); }}
.tsub {{ position:absolute; left:0; right:0; top:648px; text-align:center; font-family:'ShipA';
  font-size:38px; color:#efe6d2; opacity:0; text-shadow:{OLK}; }}
/* ソースラベル (紙上) */
.srcw {{ z-index:34; pointer-events:none; }}
.srclabel {{ position:absolute; left:64px; top:92px; background:#fdfcf7; color:#232029;
  font-family:'ZenK'; font-size:27px; letter-spacing:.07em; padding:10px 20px;
  border-left:10px solid #c2342a; box-shadow:0 6px 18px rgba(70,58,34,.3); opacity:0; }}
.srclabel .srcsub {{ margin-left:12px; font-size:20px; color:#8a8376; }}
/* 特大数値 (紙上) */
.bnwrap {{ z-index:33; pointer-events:none; }}
.bnlabel {{ position:absolute; left:0; right:0; top:264px; text-align:center; font-family:'ShipA';
  font-size:44px; color:#262230; opacity:0; text-shadow:{OLW}; }}
.bignum {{ position:absolute; left:0; right:0; top:330px; text-align:center; font-family:'Dela';
  opacity:0; font-variant-numeric:tabular-nums; }}
.bignum .bnd {{ font-size:206px; }}
.bignum .stkl {{ -webkit-text-stroke:13px #1d1812; }}
.bignum .bnunit {{ font-size:72px; color:#262230; margin-left:12px; font-family:'Dela'; }}
.bncirc {{ position:absolute; left:50%; top:310px; width:590px; height:250px; margin-left:-295px;
  opacity:0; }}
.bncirc ellipse {{ fill:none; stroke:#c2342a; stroke-width:9; stroke-dasharray:1120 240;
  stroke-linecap:round; }}
.bnrow {{ position:absolute; left:0; right:0; top:630px; text-align:center; font-family:'NotoB';
  font-size:40px; color:#262230; opacity:0; text-shadow:{OLW}; }}
.walkrow {{ position:absolute; left:0; right:0; top:716px; display:flex; gap:46px; justify-content:center; }}
.walkrow .wk {{ opacity:0; }}
/* 行積み上げ (紺上) */
.lbwrap {{ z-index:33; pointer-events:none; }}
.lbrow {{ position:absolute; left:150px; font-family:'ShipA'; font-size:52px; color:#f4f2ea;
  opacity:0; text-shadow:{OLK}; padding-left:34px; }}
.lbrow .lbar {{ position:absolute; left:0; top:8px; bottom:8px; width:12px; background:#c2342a; }}
#lr1 {{ top:330px; }} #lr2 {{ top:446px; }}
/* 中国3カット */
.cnlines {{ z-index:33; pointer-events:none; }}
.cnrow {{ position:absolute; right:130px; text-align:right; font-family:'ShipA'; font-size:52px;
  color:#f6f3ea; opacity:0; text-shadow:{OLK}; }}
#cnr1 {{ top:330px; }} #cnr2 {{ top:440px; }} #cnr3 {{ top:550px; }}
.ccwrap {{ z-index:34; pointer-events:none; }}
.ccap {{ position:absolute; background:#c2342a; color:#fff; font-family:'ZenK'; font-size:28px;
  letter-spacing:.06em; padding:9px 20px; opacity:0; border:3px solid rgba(255,255,255,.92);
  box-shadow:0 4px 16px rgba(0,0,0,.45); }}
.ccTL .ccap {{ left:56px; top:88px; }}
.ccBR .ccap {{ right:56px; bottom:104px; }}
.pcapTL {{ left:64px; top:88px; }}
/* 質問カード */
.qcwrap {{ z-index:35; pointer-events:none; }}
.qcdark {{ position:absolute; inset:0; opacity:0;
  background:radial-gradient(ellipse at center, rgba(42,8,10,.80) 0%, rgba(8,3,5,.96) 76%); }}
.qctext {{ position:absolute; left:0; right:0; top:342px; text-align:center; font-family:'ShipA';
  font-size:96px; line-height:1.38; color:#f0e9dc; opacity:0; text-shadow:{OLK7}; }}
.qcsub {{ position:absolute; left:0; right:0; top:668px; text-align:center; font-family:'Yusei';
  font-size:40px; color:#e3cf9e; opacity:0; text-shadow:{OLK}; }}
/* 引用ボックス (ref4: 白枠カード) */
.tqwrap {{ z-index:35; pointer-events:none; }}
.qbox {{ position:absolute; left:50%; top:300px; transform:translateX(-50%); width:1180px;
  text-align:center; font-family:'ShipA'; font-size:66px; line-height:1.5; color:#f6f4ec;
  background:rgba(6,8,13,.52); border:3.5px solid rgba(246,244,236,.9); padding:40px 50px 30px;
  opacity:0; text-shadow:{OLK}; }}
.qbox .tqsrc {{ margin-top:16px; font-family:'ZenB'; font-size:28px; color:#cfd8e4; }}
.bt-box {{ left:118px; }}
.bt-box path {{ fill:rgba(6,8,13,.9); stroke:rgba(246,244,236,.9); stroke-width:3; }}
/* 気配り3連パネル */
.pvpanel {{ position:absolute; bottom:300px; width:380px; height:350px; opacity:0;
  border:3px solid rgba(244,246,249,.85); background:rgba(10,14,22,.38);
  box-shadow:0 10px 30px rgba(0,0,0,.4); }}
.pvpanel .pvpic {{ display:flex; justify-content:center; align-items:center; height:255px; }}
.pvpanel .pvlabel {{ text-align:center; font-family:'ZenK'; font-size:29px; color:#f4f6f9;
  letter-spacing:.04em; text-shadow:{OLK}; }}
/* 伏字 */
.kwrap {{ z-index:35; pointer-events:none; }}
.kdark {{ position:absolute; inset:0; background:rgba(4,6,10,.62); }}
.kick {{ position:absolute; left:0; right:0; top:430px; text-align:center; font-family:'ShipA';
  font-size:92px; color:#f5f6f8; opacity:0; text-shadow:{OLK7}; }}
.fsslot {{ position:relative; display:inline-block; min-width:320px; }}
.fsw {{ display:inline-block; }}
.fsa {{ color:#aab6c8; }}
.fsb {{ position:absolute; left:50%; top:0; color:#ff5a44; white-space:nowrap; }}
.fsul {{ position:absolute; left:6%; right:6%; bottom:-10px; height:9px; background:#c2342a;
  border-radius:5px; transform:scaleX(0); transform-origin:left center; }}
/* 章扉 */
.cdark {{ position:absolute; inset:0; background:rgba(4,6,10,.66); }}
.cframe {{ position:absolute; inset:90px 150px; border:2px solid rgba(232,200,114,.5);
  outline:2px solid rgba(232,200,114,.22); outline-offset:9px; opacity:0; }}
.cwrap {{ position:absolute; inset:0; }}
.cno {{ position:absolute; left:0; right:0; top:318px; text-align:center; font-family:'Dela';
  font-size:46px; letter-spacing:.42em; color:#e8c872; opacity:0; text-shadow:{OLK}; }}
.cline {{ position:absolute; left:50%; top:410px; width:430px; margin-left:-215px; height:3px;
  transform-origin:center; transform:scaleX(0); background:rgba(232,200,114,.75); }}
.ctitle {{ position:absolute; left:0; right:0; top:442px; text-align:center; font-family:'ShipA';
  font-size:112px; opacity:0; }}
.csub {{ position:absolute; left:0; right:0; top:644px; text-align:center; font-family:'ZenB';
  font-size:35px; color:#d6dde7; opacity:0; text-shadow:{OLK}; }}
"""

html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="root" data-width="1920" data-height="1080" data-start="0" data-duration="{WDUR}">
<div id="stage">
{chr(10).join(ELS)}
<div id="vig"></div>
<div id="grainov"></div>
<div id="scrim"></div>
<div id="dip"></div>
<div id="flash"></div>
<div id="barT"></div>
<div id="barB"></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>
window.__timelines = window.__timelines || {{}};
const CNT = {{ v: 0 }};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(TWEENS)}
const root = gsap.timeline({{ paused: true }});
tl.time({W0});
root.fromTo(tl, {{ time: {W0} }}, {{ time: {W1}, duration: {WDUR}, ease: "none" }}, 0);
window.__timelines["root"] = root;
</script>
</div>
</body>
</html>
"""

TPL.mkdir(parents=True, exist_ok=True)
(TPL / "index.html").write_text(html, encoding="utf-8", newline="\n")
print(f"built index.html window {W0}-{W1} ({WDUR}s) els={len(ELS)} tweens={len(TWEENS)}")
