# -*- coding: utf-8 -*-
"""japan03v7: index.html ビルダ(窓分割対応) — v6の人物置換+配置改善版
ユーザー指摘対応: 棒人間ピクト→写真由来フィギュア (ポスタライズ切り抜きPNG+実写シルエットSVG)。
全フィギュアは画面下端アンカー・バストアップ大型化。会話は左右2者構図。群衆前景帯。
HF_WIN_START/HF_WIN_END で窓ビルド。
"""
import json
import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "japan03v7"
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


def flash(t, peak=0.45, dur=0.28):
    setv(t, "#flash", f"opacity: {peak}")
    tw(t + 0.04, f'tl.to("#flash", {{opacity: 0, duration: {dur}, ease: "power2.out"}}, %T%);')


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


def scene_bg(sid, last=False, cut=False, src=None, wid=None, t1=None):
    sc = SC[sid]
    t0 = sc["start"]
    if t1 is None:
        t1 = COMP if last else sc["end"] + 0.55
    wid = wid or sid
    z = zbg()
    el_bg(wid, t0, t1, src or f"bg_{sid}.mp4", 0.0, z)
    if cut:
        hardcut(wid, t0, t1 - t0)
    else:
        xfade(wid, t0, t1 - t0)


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


PICTO_DIR = TPL / "assets" / "picto"
SIL_DIR = ROOT / "src" / "photo_sil"
_PC = {}


def _svg_fig(path, h, cls):
    key = str(path)
    if key not in _PC:
        _PC[key] = path.read_text(encoding="utf-8")
    svg = _PC[key]
    vb = re.search(r'viewBox="([-\d. ]+)"', svg).group(1).split()
    w = float(vb[2]) * h / float(vb[3])
    html = svg.replace('<svg ', f'<svg class="pic {cls}" style="height:{h}px" ', 1)
    return html, round(w)


def picto(name, h, cls=""):
    return _svg_fig(PICTO_DIR / f"{name}.svg", h, cls)


def sil(name, h, cls=""):
    """写真由来シルエット (src/photo_sil, ビルド時インライン)"""
    return _svg_fig(SIL_DIR / f"{name}.svg", h, cls)


def pfig(name, h):
    """ポスタライズ切り抜きPNG (assets/photo)"""
    return f'<img class="pimg" src="assets/photo/{name}.png" style="height:{h}px">'


def bubble(bid, text, left, bottom, tail_x, w=None, cls=""):
    ws = f"width:{w}px;" if w else ""
    return (f'<div class="bubble {cls}" id="{bid}" style="left:{left}px; bottom:{bottom}px; {ws}">'
            f'{text}<svg class="btail" style="left:{tail_x - 17}px" viewBox="0 0 34 27">'
            f'<path d="M1 2 L33 2 L15 26 Z"/></svg></div>')


def stk(text, fill, w=12, color="#17120d"):
    return (f'<span class="stkw"><span class="stkl" style="-webkit-text-stroke:{w}px {color}">{text}</span>'
            f'<span class="stkf {fill}">{text}</span></span>')


def ring(px, color, n=16):
    parts = [f"{px * math.cos(2 * math.pi * i / n):.1f}px {px * math.sin(2 * math.pi * i / n):.1f}px 0 {color}"
             for i in range(n)]
    return ", ".join(parts)


OLK = ring(5, "#0b0d12") + ", 0 6px 22px rgba(0,0,0,.6)"
OLK7 = ring(7, "#0b0d12") + ", 0 8px 28px rgba(0,0,0,.65)"
OLW = ring(5, "#f4efe2") + ", 0 4px 16px rgba(70,58,34,.28)"

SKYLINE = (
    '<svg class="skyline" viewBox="0 0 1920 150" preserveAspectRatio="none">'
    '<path d="M0 150 V96 H70 V58 H150 V96 H210 V34 H268 V96 H330 V72 H420 V110 H480 V48 H540 V110 '
    'H600 V20 L640 6 L680 20 V110 H760 V64 H840 V96 H920 V40 H1010 V96 H1080 V78 H1170 V110 '
    'H1230 V30 H1300 V110 H1380 V58 H1470 V96 H1540 V44 H1620 V96 H1700 V70 H1790 V110 H1850 V88 H1920 V150 Z"/>'
    '</svg>')


def wmk(text, dark=True, right=90, top=140, size=330):
    cls = "wmk wmkd" if dark else "wmk wmkp"
    return f'<div class="{cls}" style="right:{right}px; top:{top}px; font-size:{size}px">{text}</div>'


def telop(eid, lid, html, hold=0.6, serif=False, paper=False):
    st = N[lid]["start"] - 0.05
    en = N[lid]["start"] + N[lid]["dur"] + hold
    cls = "telop ts" if serif else "telop"
    if paper:
        cls += " tpp"
    el_div(eid, st, en, "telopw", f'<div class="{cls}" id="{eid}i">{html}</div>')
    fromto(st + 0.02, f"#{eid}i", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.3, "power2.out")
    tw(en - 0.25, f'tl.to("#{eid}i", {{opacity: 0, duration: 0.22}}, %T%);')


# ============================================================ s_h1+s_h2: オフィス実写bg (連続)
# 左=彼 (男性シルエット) / 右=同僚 (ポスタライズ写真) の対面構図。両シーン通し。
scene_bg("s_h1", cut=True, src="bg_h12.mp4", wid="h12", t1=SC["s_h2"]["end"] + 0.55)
sc = SC["s_h1"]
telop("tp01", "n01", '日本で働く、ひとりの<span class="gd ulg">中国人男性</span>', serif=True, hold=0.3)
telop("tp02", "n02", '毎日、<span class="gd">笑顔</span>で、<span class="gd">お辞儀</span>。困っていれば、助けてくれる', hold=0.4)
man_svg, man_w = sil("f_walk3", 680, "wt")
MAN_L = 170
MAN_HEAD_X = MAN_L + int(man_w * 0.5)
el_div("h12f", sc["start"] + 0.1, SC["s_h2"]["end"] + 0.1, "figwrap", (
    wmk("実話", True, 70, 120, 340)
    + f'<div class="fig figbot" id="hman" style="left:{MAN_L}px">{man_svg}</div>'
    f'<div class="hfig" id="hcow" style="right:104px; height:950px">{pfig("f_cowork", 950)}</div>'
    '<div class="wstamp" id="ws1" style="left:620px; top:230px; transform:rotate(-2.5deg)">笑顔</div>'
    '<div class="wstamp" id="ws2" style="left:860px; top:430px; transform:rotate(1.8deg)">お辞儀</div>'
    '<div class="wstamp" id="ws3" style="left:600px; top:630px; transform:rotate(-1.4deg)">親切</div>'))
el_div("h1c", sc["start"] + 0.2, sc["end"], "figwrap",
       '<div class="ccap pcapTL" id="h1cap">ある職場の、実話</div>')
fromto(sc["start"] + 0.35, "#h1cap", "x: -14, opacity: 0", "x: 0, opacity: 1", 0.3, "power2.out")
fromto(sc["start"] + 0.25, "#hman", "x: -60, opacity: 0", "x: 0, opacity: 1", 0.45, "power2.out")
fromto(N["n01"]["start"] + 0.4, "#hcow", "y: 60, opacity: 0", "y: 0, opacity: 1", 0.5, "power2.out")
n2 = N["n02"]["start"]
for i, dt in enumerate((2.3, 4.6, 7.0)):
    fromto(n2 + dt, f"#ws{i+1}", "scale: 1.7, opacity: 0", "scale: 1, opacity: 1", 0.28, "power3.out")

# ============================================================ s_h2: 吹き出し (bg・人物継続+ミニフラッシュ)
sc = SC["s_h2"]
flash(sc["start"], 0.3, 0.24)
telop("tp03", "n03", 'だから、彼は、思った——', serif=True, hold=1.6)
bub_left = 140
el_div("h2f", sc["start"] + 0.05, sc["end"] + 0.1, "figwrap",
       bubble("h2bb", 'この人とは、<br><span class="rdp">友達になれる</span>', bub_left, 756,
              MAN_HEAD_X - bub_left, cls="bwt"))
fromto(N["n03"]["start"] + N["n03"]["dur"] + 0.25, "#h2bb",
       "scale: 0.4, opacity: 0, rotation: -4", "scale: 1, opacity: 1, rotation: 0", 0.42, "back.out(2.0)")

# ============================================================ s_h3: スマホ実写bg+メッセージ
scene_bg("s_h3", cut=True, src="bg_h3.mp4")
sc = SC["s_h3"]
flash(sc["start"], 0.35, 0.24)
telop("tp04", "n04", 'SNSで、<span class="gd ulg">何度も</span>、食事に誘った', hold=0.3)
ph_svg, ph_w = sil("f_phonest", 880, "wt")
msgs = ["今度、食事に行きませんか?", "来週なら、どうですか?", "また、誘ってもいいですか?"]
msg_html = "".join(
    f'<div class="msgb" id="mg{i}" style="left:{800 + i * 56}px; top:{200 + i * 158}px">{m}</div>'
    for i, m in enumerate(msgs))
el_div("h3f", sc["start"] + 0.1, sc["end"] + 0.1, "figwrap", (
    wmk("友情", True, 80, 150, 300)
    + '<div class="ccap pcapTL" id="h3cap">再現イメージ</div>'
    f'<div class="fig figbot" id="h3fg" style="left:180px">{ph_svg}</div>' + msg_html))
fromto(sc["start"] + 0.25, "#h3cap", "x: -14, opacity: 0", "x: 0, opacity: 1", 0.3, "power2.out")
fromto(sc["start"] + 0.3, "#h3fg", "y: 44, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
n4 = N["n04"]["start"]
for i, dt in enumerate((1.7, 2.6, 3.5)):
    fromto(n4 + dt, f"#mg{i}", "x: 44, opacity: 0, scale: 0.9", "x: 0, opacity: 1, scale: 1", 0.3, "back.out(1.5)")

# ============================================================ s_h4: パトランプ実写bg+通報 (彼=影/警官=白 対峙)
scene_bg("s_h4", cut=True, src="bg_h4.mp4")
sc = SC["s_h4"]
man2_svg, man2_w = sil("f_walk3", 780, "drk")
po_svg, po_w = sil("f_police2", 820, "wt")
el_div("h4x", sc["start"], sc["end"] + 0.1, "kwrap", (
    '<div class="h4dark"></div>'
    f'<div class="fig figbot" id="h4m" style="left:150px">{man2_svg}</div>'
    f'<div class="fig figbot" id="h4fg" style="right:160px">{po_svg}</div>'
    '<div class="h4sub" id="h4s">ハラスメントとして——</div>'
    f'<div class="h4big" id="h4b">{stk("通報", "gfr", 18)}</div>'))
n5 = N["n05"]["start"]
fromto(sc["start"] + 0.15, "#h4m", "x: -60, opacity: 0", "x: 0, opacity: 0.92", 0.4, "power2.out")
fromto(n5 - 0.1, "#h4s", "opacity: 0, y: -10", "opacity: 1, y: 0", 0.3, "power2.out")
fromto(n5 + 0.75, "#h4b", 'opacity: 0, scale: 1.9, rotation: -3, filter: "blur(8px)"',
       'opacity: 1, scale: 1, rotation: 0, filter: "blur(0px)"', 0.32, "power3.out")
flash(n5 + 1.0, 0.6, 0.3)
fromto(n5 + 1.35, "#h4fg", "x: 70, opacity: 0", "x: 0, opacity: 1", 0.35, "power3.out")

# ============================================================ s_h5: 交差点実写bg+群衆前景+質問カード
scene_bg("s_h5", cut=True, src="bg_h5.mp4")
sc = SC["s_h5"]
cr_svg, cr_w = sil("f_crowd", 400, "blk")
cr2_svg, _ = sil("f_crowd", 440, "blk")
el_div("h5q", sc["start"], sc["end"] + 0.1, "qcwrap", (
    '<div class="qcdark" id="qcd"></div>'
    f'<div class="crowdrow" id="crd">'
    f'<div class="crp" style="left:-60px; bottom:-16px">{cr2_svg}</div>'
    f'<div class="crp" style="left:860px; bottom:-10px; transform:scaleX(-1)">{cr_svg}</div>'
    f'<div class="crp" style="left:1560px; bottom:-20px">{cr2_svg}</div></div>'
    '<div class="qctext" id="qct">なぜ、"親切"が<br><span class="rd">事件</span>になったのか?</div>'
    '<div class="qcsub" id="qcs">— 丁寧さと、友好は、別のもの</div>'))
fromto(sc["start"] + 0.1, "#crd", "y: 50, opacity: 0", "y: 0, opacity: 1", 0.5, "power2.out")
w0t = N["n06"]["start"] - 0.15
fromto(w0t, "#qcd", "opacity: 0", "opacity: 0.8", 0.4, "power1.in")
fromto(w0t + 0.3, "#qct", 'opacity: 0, scale: 1.12, filter: "blur(7px)"',
       'opacity: 1, scale: 1, filter: "blur(0px)"', 0.5, "power2.out")
fromto(w0t + 3.0, "#qcs", "opacity: 0", "opacity: 1", 0.45, "power2.out")

# ============================================================ s_title
scene_bg("s_title", cut=True)
sc = SC["s_title"]
tt = sc["start"] + 0.15
el_div("ttl", sc["start"], sc["end"] + 0.1, "twrap", (
    '<div class="tdark" id="tdk"></div>'
    '<div class="tlabel" id="tlb">ある中国人の実話から始まる、日中比較</div>'
    f'<div class="ttitle" id="tti">{stk("丁寧さの、", "gfw", 15)}{stk("正体", "gfr", 15)}</div>'
    '<div class="tline" id="tln"></div>'
    '<div class="tsub" id="tsb">— 日本で通報された、中国人の話</div>'))
fromto(tt, "#tdk", "opacity: 0", "opacity: 0.72", 0.3, "power1.in")
fromto(tt + 0.1, "#tlb", "opacity: 0, y: -12", "opacity: 1, y: 0", 0.4, "power2.out")
fromto(tt + 0.55, "#tti", 'opacity: 0, scale: 1.45, rotation: -2.5, filter: "blur(10px)"',
       'opacity: 1, scale: 1, rotation: 0, filter: "blur(0px)"', 0.42, "power3.out")
flash(tt + 0.9, 0.75, 0.3)
fromto(tt + 1.05, "#tln", "scaleX: 0", "scaleX: 1", 0.45, "power2.inOut")
fromto(tt + 1.3, "#tsb", "opacity: 0", "opacity: 1", 0.4, "power2.out")

# ============================================================ s_data: 紙+スカイライン+909+実写シルエット群
scene_tex("s_data", "paper_light.png", cut=True)
sc = SC["s_data"]
flash(sc["start"], 0.4, 0.26)
el_div("sl1", sc["start"] + 0.2, sc["end"] + 0.1, "srcw",
       '<div class="srclabel" id="sl1i">JNTO 訪日外客統計<span class="srcsub">2025</span></div>')
fromto(sc["start"] + 0.3, "#sl1i", "x: -14, opacity: 0, rotation: -2", "x: 0, opacity: 1, rotation: -1.2",
       0.35, "power2.out")
d1 = N["n07"]["start"]
n8 = N["n08"]["start"]
WK = [("f_walk1", 205), ("f_walk2", 235), ("f_phonest", 215), ("f_walk3", 228), ("f_present", 210)]
walkrow = "".join(f'<div class="wk" id="wk{i}">{sil(n, h, "ink")[0]}</div>' for i, (n, h) in enumerate(WK))
el_div("bn1", sc["start"] + 0.2, sc["end"] + 0.1, "bnwrap", (
    SKYLINE
    + '<div class="bnlabel" id="bnl">2025年・日本を最も多く訪れた外国人</div>'
    '<div class="bignum" id="bnn"><span class="stkw"><span class="stkl bnd" id="dnvl">0</span>'
    '<span class="stkf gfg bnd" id="dnv">0</span></span><span class="bnunit">万人</span></div>'
    '<svg class="bncirc" id="bnc" viewBox="0 0 560 240"><ellipse cx="280" cy="120" rx="262" ry="104"/></svg>'
    f'<div class="walkrow" id="wkr">{walkrow}</div>'
    '<div class="bnrow" id="bnr1">増えていくのは——文化の<span class="rdp ulr">"すれ違い"</span></div>'))
fromto(d1 + 0.3, "#bnl", "y: 20, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
fromto(d1 + 3.9, "#bnn", "opacity: 0, y: 24", "opacity: 1, y: 0", 0.3, "power2.out")
tw(d1 + 4.1, 'tl.fromTo(CNT, {v: 0}, {v: 909, duration: 1.15, ease: "power2.out", '
             'onUpdate: () => { const a = document.getElementById("dnv"); '
             'const b = document.getElementById("dnvl"); const s = String(Math.round(CNT.v)); '
             'if (a) a.textContent = s; if (b) b.textContent = s; }}, %T%);')
fromto(d1 + 5.4, "#bnc", "scale: 1.3, opacity: 0", "scale: 1, opacity: 1", 0.35, "back.out(1.8)")
for i in range(len(WK)):
    fromto(d1 + 4.3 + 0.15 * i, f"#wk{i}", "x: -34, opacity: 0", "x: 0, opacity: 1", 0.3, "power2.out")
fromto(n8 + 2.3, "#bnr1", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.35, "power2.out")
if OV(sc["start"] + 0.4, sc["end"] + 0.1):
    s = max(sc["start"] + 0.4, W0)
    d = round(min(sc["end"] + 0.1, W1 + 0.2) - s, 3)
    ms_eff = round(0.0 + (s - (sc["start"] + 0.4)), 3)
    ELS.append(
        '<div class="fcard mono" id="dcard" style="left:90px; bottom:200px; width:560px; height:315px; '
        'transform:rotate(-2deg)">'
        f'<video class="clip cardv" data-start="{T(s)}" data-duration="{d}" data-media-start="{ms_eff}" '
        f'data-track-index="{track()}" src="assets/bg/card_air.mp4" muted playsinline></video>'
        '<div class="fclabel">羽田空港</div></div>')
fromto(sc["start"] + 0.65, "#dcard", "y: 30, opacity: 0, rotation: -4", "y: 0, opacity: 1, rotation: -2",
       0.45, "power2.out")
tw(sc["end"] - 0.12, 'tl.to("#dcard", {opacity: 0, duration: 0.18}, %T%);')

# ============================================================ s_road: 2分割予告カード (シルエット+写真)
scene_tex("s_road", "paper_light.png", cut=True)
sc = SC["s_road"]
flash(sc["start"], 0.35, 0.24)
sp1_svg, _ = sil("f_walk3", 240, "wt")
el_div("road", sc["start"] + 0.1, sc["end"] + 0.1, "figwrap", (
    SKYLINE
    + '<div class="rohead" id="roh">今日、深掘りする「ふたつの実話」</div>'
    '<div class="splitcard" id="spc1" style="left:110px">'
    '<div class="spno">第1部</div><div class="sptitle">通報された、<br>中国人</div>'
    f'<div class="sppic">{sp1_svg}</div></div>'
    '<div class="splitcard" id="spc2" style="left:990px">'
    '<div class="spno">第2部</div><div class="sptitle">大阪で受けた、<br>"人生最悪"の接客</div>'
    f'<div class="sppic">{pfig("f_shock", 250)}</div></div>'))
n9 = N["n09"]["start"]
fromto(n9 + 0.3, "#roh", "y: -16, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
fromto(n9 + 1.3, "#spc1", "y: 40, opacity: 0, scale: 1.08, rotation: -1.5",
       "y: 0, opacity: 1, scale: 1, rotation: 0", 0.4, "back.out(1.5)")
fromto(n9 + 2.7, "#spc2", "y: 40, opacity: 0, scale: 1.08, rotation: 1.5",
       "y: 0, opacity: 1, scale: 1, rotation: 0", 0.4, "back.out(1.5)")

# ============================================================ s_p1: 第1部扉
scene_tex("s_p1", "panel_navy.png", cut=True)
sc = SC["s_p1"]
el_div("p1o", sc["start"], sc["end"] + 0.1, "qov", (
    '<div class="cframe" id="cf1"></div>'
    '<div class="cwrap"><div class="cno" id="cn1">第 1 部</div>'
    '<div class="cline" id="cl1"></div>'
    f'<div class="ctitle" id="ct1">{stk("通報された、中国人", "gfw", 11)}</div>'
    '<div class="csub" id="cs1">— 丁寧は、友好では、ない</div></div>'))
t0 = sc["start"]
setv(t0 - 0.4, "#dip", "opacity: 0")
tw(t0 - 0.4, 'tl.to("#dip", {opacity: 1, duration: 0.3, ease: "power1.in"}, %T%);')
tw(t0 + 0.05, 'tl.to("#dip", {opacity: 0, duration: 0.45, ease: "power1.out"}, %T%);')
fromto(t0 + 0.25, "#cf1", "opacity: 0, scale: 1.04", "opacity: 1, scale: 1", 0.5, "power2.out")
fromto(t0 + 0.3, "#cn1", "y: -16, opacity: 0", "y: 0, opacity: 1", 0.45, "power3.out")
fromto(t0 + 0.5, "#cl1", "scaleX: 0", "scaleX: 1", 0.4, "power2.inOut")
fromto(t0 + 0.65, "#ct1", 'opacity: 0, y: 22, filter: "blur(9px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.55, "power2.out")
fromto(t0 + 1.35, "#cs1", "opacity: 0", "opacity: 1", 0.4, "power2.out")

# ============================================================ s_zhen: 紙+プロフィール (語り手シルエット)
scene_tex("s_zhen", "paper_light.png", cut=True)
sc = SC["s_zhen"]
telop("tp11", "n11", 'あの職場で、何が起きていたのか——<span class="rdp ulr">順番に</span>見ていく', serif=True, paper=True, hold=0.4)
pr_svg, pr_w = sil("f_present", 840, "ink")
el_div("zh", sc["start"] + 0.1, sc["end"] + 0.1, "figwrap", (
    SKYLINE
    + '<div class="nplate npz" id="zhp"><div class="ntag">語り手: Zhen Into Chinese さん</div>'
    '<div class="ncredit">日中の文化を分析するクリエイター</div></div>'
    f'<div class="fig figbotp" id="zhfg" style="left:300px">{pr_svg}</div>'
    '<div class="profrow" id="pr1" style="top:300px"><span class="pbar"></span>中国で、生まれ育つ</div>'
    '<div class="profrow" id="pr2" style="top:428px"><span class="pbar"></span>日本で、暮らした経験</div>'
    '<div class="profrow" id="pr3" style="top:556px"><span class="pbar"></span>ヨーロッパでも、数年</div>'))
n10 = N["n10"]["start"]
fromto(n10 + 0.3, "#zhp", "x: -16, opacity: 0", "x: 0, opacity: 1", 0.4, "power2.out")
fromto(n10 + 0.9, "#zhfg", "y: 44, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
for i, dt in enumerate((2.2, 4.6, 6.6)):
    fromto(n10 + dt, f"#pr{i+1}", "x: -30, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")

# ============================================================ s_p1a: オフィス実写bg+チェック行 (同僚写真=右)
scene_bg("s_p1a", cut=True, src="bg_p1a.mp4")
sc = SC["s_p1a"]
flash(sc["start"], 0.35, 0.24)
el_div("pa", sc["start"] + 0.1, sc["end"] + 0.1, "figwrap", (
    wmk("理想", True, 640, 110, 300)
    + '<div class="ccap pcapTL" id="pacap">再現・理想の職場</div>'
    f'<div class="hfig" id="pafg" style="right:104px; height:880px">{pfig("f_cowork", 880)}</div>'
    '<div class="chkrow onv ckl" id="ck1" style="top:280px"><span class="ckm">✓</span>毎朝の、あいさつ</div>'
    '<div class="chkrow onv ckl" id="ck2" style="top:408px"><span class="ckm">✓</span>きれいな、お辞儀</div>'
    '<div class="chkrow onv ckl" id="ck3" style="top:536px"><span class="ckm">✓</span>困ったら、助けてくれる</div>'
    '<div class="chkrow ckr" id="ck4" style="top:700px">= <span class="rd">「友達になりたい」のサイン</span>?</div>'))
n12 = N["n12"]["start"]
n13 = N["n13"]["start"]
fromto(sc["start"] + 0.3, "#pacap", "x: -14, opacity: 0", "x: 0, opacity: 1", 0.3, "power2.out")
fromto(n12 + 0.5, "#pafg", "y: 60, opacity: 0", "y: 0, opacity: 1", 0.45, "power2.out")
for i, dt in enumerate((2.4, 4.6, 6.6)):
    fromto(n12 + dt, f"#ck{i+1}", "x: -30, opacity: 0", "x: 0, opacity: 1", 0.33, "power2.out")
fromto(n13 + 3.1, "#ck4", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.35, "power2.out")

# ============================================================ s_p1b: スマホ実写bg+誘い連打→暗転
scene_bg("s_p1b", last=True, cut=True, src="bg_p1b.mp4")
sc = SC["s_p1b"]
flash(sc["start"], 0.35, 0.24)
ph2_svg, _ = sil("f_phonest", 840, "wt")
msgs2 = ["一度", "二度", "三度"]
msg2_html = "".join(
    f'<div class="msgb mgs" id="mh{i}" style="left:{820 + i * 250}px; top:{300 + (i % 2) * 70}px">{m}</div>'
    for i, m in enumerate(msgs2))
el_div("pb", sc["start"] + 0.1, COMP, "figwrap", (
    f'<div class="fig figbot" id="pbfg" style="left:220px">{ph2_svg}</div>' + msg2_html
    + '<div class="pbdark" id="pbd"></div>'
    '<div class="pbline" id="pbl">しかし、相手に見えていたのは——<span class="rd">別の景色</span></div>'))
n14 = N["n14"]["start"]
n15 = N["n15"]["start"]
fromto(sc["start"] + 0.3, "#pbfg", "y: 44, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
for i, dt in enumerate((4.35, 5.05, 5.75)):
    fromto(n14 + dt, f"#mh{i}", "scale: 1.6, opacity: 0", "scale: 1, opacity: 1", 0.25, "power3.out")
fromto(n15 + 0.2, "#pbd", "opacity: 0", "opacity: 0.74", 0.8, "power1.in")
fromto(n15 + 0.9, "#pbl", 'opacity: 0, y: 18, filter: "blur(6px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.55, "power2.out")
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
.gd {{ color:#e8c872; }} .rd {{ color:#ff6a55; }} .bl {{ color:#7db8e8; }} .gr {{ color:#7ec87e; }}
.rdp {{ color:#c2342a; }}
.ulg {{ background:linear-gradient(transparent 84%, rgba(232,200,114,.95) 84%); padding:0 2px 3px; }}
.ulr {{ background:linear-gradient(transparent 84%, rgba(255,90,68,.95) 84%); padding:0 2px 3px; }}
.tpp .ulr {{ background:linear-gradient(transparent 84%, rgba(194,52,42,.9) 84%); }}
#vig {{ position:absolute; inset:0; z-index:27; pointer-events:none;
  background:radial-gradient(ellipse at center, rgba(0,0,0,0) 50%, rgba(0,0,0,.42) 100%); }}
#grainov {{ position:absolute; inset:0; z-index:28; pointer-events:none; opacity:.07;
  background:url('assets/tex/grain.png'); mix-blend-mode:overlay; }}
#scrim {{ position:absolute; inset:0; z-index:29; pointer-events:none;
  background:linear-gradient(0deg, rgba(5,7,12,.62) 0%, rgba(5,7,12,.12) 15%, rgba(5,7,12,0) 30%); }}
#barT, #barB {{ position:absolute; left:0; right:0; height:56px; background:#000; z-index:40; }}
#barT {{ top:0; }} #barB {{ bottom:0; }}
#dip {{ position:absolute; inset:0; background:#000; z-index:38; opacity:0; pointer-events:none; }}
#flash {{ position:absolute; inset:0; background:#fff; z-index:37; opacity:0; pointer-events:none; }}
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
.telopw {{ z-index:36; pointer-events:none; display:flex; align-items:flex-end;
  justify-content:center; padding-bottom:78px; }}
.telop {{ font-family:'NotoB'; font-size:57px; letter-spacing:.04em; text-align:center;
  max-width:1740px; color:#f6f7fa; opacity:0; text-shadow:{OLK}; }}
.telop.ts {{ font-family:'ShipA'; font-size:61px; letter-spacing:.05em; }}
.telop.tpp {{ color:#262230; text-shadow:{OLW}; }}
.qov {{ z-index:34; pointer-events:none; }}
.nplate {{ position:absolute; left:56px; top:80px; opacity:0; transform:rotate(-1.2deg); }}
.nplate .ntag {{ display:inline-block; background:#c2342a; color:#fff; font-family:'ZenK';
  font-size:35px; letter-spacing:.06em; padding:12px 26px;
  border:3px solid rgba(255,255,255,.92); box-shadow:0 5px 18px rgba(0,0,0,.55); }}
.nplate .ncredit {{ display:block; margin-top:8px; background:rgba(5,8,14,.78); color:#d7dfe9;
  font-family:'ZenB'; font-size:24px; padding:6px 14px; width:max-content; }}
.npz .ncredit {{ background:rgba(40,34,28,.85); }}
.figwrap {{ z-index:33; pointer-events:none; }}
.pic {{ display:block; }}
.ink {{ color:#2a2733; filter:drop-shadow(0 5px 12px rgba(70,58,34,.30)); }}
.wt {{ color:#f4f6f9; filter:drop-shadow(0 7px 18px rgba(0,0,0,.6)); }}
.drk {{ color:#19090b; filter:drop-shadow(0 0 30px rgba(255,64,44,.4)); }}
.blk {{ color:#05060a; filter:drop-shadow(0 -4px 22px rgba(255,88,64,.34)); }}
.fig {{ position:absolute; opacity:0; }}
.figbot {{ bottom:56px; }}
.figbotp {{ bottom:56px; }}
.hfig {{ position:absolute; bottom:56px; opacity:0;
  filter:drop-shadow(0 18px 44px rgba(0,0,0,.55)); }}
.hfig .pimg {{ display:block; height:100%; }}
.sppic .pimg {{ display:inline-block; }}
.crowdrow {{ position:absolute; inset:0; opacity:0; z-index:1; }}
.crp {{ position:absolute; }}
/* 透かし大字 */
.wmk {{ position:absolute; font-family:'ShipA'; line-height:1; pointer-events:none; }}
.wmkd {{ color:rgba(255,255,255,.065); }}
.wmkp {{ color:rgba(42,39,51,.06); }}
/* スカイライン帯 (紙シーン下部) */
.skyline {{ position:absolute; left:0; right:0; bottom:56px; width:100%; height:150px; }}
.skyline path {{ fill:rgba(42,39,51,.14); }}
.bubble {{ position:absolute; background:#fffdf6; color:#1a1d26; font-family:'MPR';
  font-size:46px; line-height:1.45; padding:26px 38px; border-radius:22px; opacity:0;
  border:4px solid #14161c; box-shadow:0 10px 30px rgba(0,0,0,.4);
  transform-origin:40% 100%; }}
.btail {{ position:absolute; bottom:-25px; width:34px; height:27px; }}
.btail path {{ fill:#fffdf6; stroke:#14161c; stroke-width:3; }}
.bubble.bwt {{ background:#ffffff; }}
.ccap {{ position:absolute; background:#c2342a; color:#fff; font-family:'ZenK'; font-size:33px;
  letter-spacing:.06em; padding:11px 24px; opacity:0; border:3px solid rgba(255,255,255,.92);
  box-shadow:0 4px 16px rgba(0,0,0,.45); }}
.pcapTL {{ left:64px; top:86px; }}
.wstamp {{ position:absolute; background:#c2342a; color:#fff; font-family:'ZenK'; font-size:76px;
  letter-spacing:.08em; padding:22px 46px; opacity:0; border:4px solid rgba(255,255,255,.92);
  box-shadow:0 10px 30px rgba(0,0,0,.55); }}
.msgb {{ position:absolute; background:#ffffff; color:#1a1d26; font-family:'MPR'; font-size:46px;
  padding:24px 38px; border-radius:26px 26px 5px 26px; opacity:0;
  border:3.5px solid #14161c; box-shadow:0 9px 26px rgba(0,0,0,.45); }}
.msgb.mgs {{ font-size:64px; font-family:'ZenK'; }}
.fcard {{ position:absolute; border:6px solid rgba(255,255,255,.94); border-radius:16px;
  overflow:hidden; opacity:0; box-shadow:0 16px 44px rgba(20,14,8,.45); z-index:32; }}
.fcard video.cardv {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.fcard.mono video.cardv {{ filter:grayscale(1) contrast(1.06) brightness(1.02); }}
.fclabel {{ position:absolute; left:0; bottom:0; background:rgba(8,10,14,.82); color:#e8ebf0;
  font-family:'ZenB'; font-size:25px; padding:6px 16px; border-top-right-radius:10px; }}
.twrap {{ z-index:35; pointer-events:none; }}
.tdark {{ position:absolute; inset:0; background:#06080e; opacity:0; }}
.tlabel {{ position:absolute; left:0; right:0; top:266px; text-align:center; font-family:'ZenB';
  font-size:34px; letter-spacing:.28em; color:#dfe5ee; opacity:0; text-shadow:{OLK}; }}
.ttitle {{ position:absolute; left:0; right:0; top:336px; text-align:center; font-family:'Dela';
  font-size:150px; opacity:0; letter-spacing:.01em; }}
.ttitle .stkw {{ margin:0 -2px; }}
.tline {{ position:absolute; left:50%; top:630px; width:700px; margin-left:-350px; height:5px;
  transform-origin:center; transform:scaleX(0);
  background:linear-gradient(90deg, rgba(232,200,114,0), #e8c872 30%, #ff6a55 70%, rgba(255,106,85,0)); }}
.tsub {{ position:absolute; left:0; right:0; top:676px; text-align:center; font-family:'ShipA';
  font-size:44px; color:#efe6d2; opacity:0; text-shadow:{OLK}; }}
.srcw {{ z-index:34; pointer-events:none; }}
.srclabel {{ position:absolute; left:64px; top:88px; background:#fdfcf7; color:#232029;
  font-family:'ZenK'; font-size:31px; letter-spacing:.07em; padding:12px 24px;
  border-left:12px solid #c2342a; box-shadow:0 6px 18px rgba(70,58,34,.3); opacity:0; }}
.srclabel .srcsub {{ margin-left:12px; font-size:22px; color:#8a8376; }}
.bnwrap {{ z-index:33; pointer-events:none; }}
.bnlabel {{ position:absolute; left:0; right:0; top:218px; text-align:center; font-family:'ShipA';
  font-size:54px; color:#262230; opacity:0; text-shadow:{OLW}; }}
.bignum {{ position:absolute; left:0; right:0; top:296px; text-align:center; font-family:'Dela';
  opacity:0; font-variant-numeric:tabular-nums; }}
.bignum .bnd {{ font-size:250px; }}
.bignum .stkl {{ -webkit-text-stroke:15px #1d1812; }}
.bignum .bnunit {{ font-size:86px; color:#262230; margin-left:14px; font-family:'Dela'; }}
.bncirc {{ position:absolute; left:50%; top:276px; width:700px; height:300px; margin-left:-350px;
  opacity:0; }}
.bncirc ellipse {{ fill:none; stroke:#c2342a; stroke-width:10; stroke-dasharray:1120 240;
  stroke-linecap:round; }}
.bnrow {{ position:absolute; left:0; right:0; top:772px; text-align:center; font-family:'NotoB';
  font-size:52px; color:#262230; opacity:0; text-shadow:{OLW}; }}
.walkrow {{ position:absolute; left:0; right:0; top:620px; display:flex; gap:66px;
  justify-content:center; align-items:flex-end; }}
.walkrow .wk {{ opacity:0; }}
.rohead {{ position:absolute; left:0; right:0; top:140px; text-align:center; font-family:'ShipA';
  font-size:56px; color:#262230; opacity:0; text-shadow:{OLW}; }}
.splitcard {{ position:absolute; top:272px; width:820px; height:582px; opacity:0;
  background:#1a2130; border:5px solid rgba(244,246,249,.9);
  box-shadow:0 18px 48px rgba(40,30,16,.42); text-align:center; }}
.splitcard .spno {{ margin-top:38px; font-family:'Dela'; font-size:40px; color:#e8c872;
  letter-spacing:.3em; }}
.splitcard .sptitle {{ margin-top:20px; font-family:'ShipA'; font-size:58px; line-height:1.38;
  color:#f4f2ea; text-shadow:{OLK}; }}
.splitcard .sppic {{ margin-top:22px; display:flex; justify-content:center; }}
.cframe {{ position:absolute; inset:80px 130px; border:2px solid rgba(232,200,114,.5);
  outline:2px solid rgba(232,200,114,.22); outline-offset:10px; opacity:0; }}
.cwrap {{ position:absolute; inset:0; }}
.cno {{ position:absolute; left:0; right:0; top:296px; text-align:center; font-family:'Dela';
  font-size:54px; letter-spacing:.42em; color:#e8c872; opacity:0; text-shadow:{OLK}; }}
.cline {{ position:absolute; left:50%; top:398px; width:480px; margin-left:-240px; height:4px;
  transform-origin:center; transform:scaleX(0); background:rgba(232,200,114,.75); }}
.ctitle {{ position:absolute; left:0; right:0; top:432px; text-align:center; font-family:'ShipA';
  font-size:124px; opacity:0; }}
.csub {{ position:absolute; left:0; right:0; top:656px; text-align:center; font-family:'ZenB';
  font-size:41px; color:#d6dde7; opacity:0; text-shadow:{OLK}; }}
.kwrap {{ z-index:35; pointer-events:none; }}
.h4dark {{ position:absolute; inset:0;
  background:radial-gradient(ellipse at center, rgba(52,8,8,.62) 0%, rgba(8,3,4,.9) 80%); }}
.h4sub {{ position:absolute; left:0; right:0; top:238px; text-align:center; font-family:'ZenK';
  font-size:54px; color:#f2b9ae; opacity:0; letter-spacing:.14em; text-shadow:{OLK}; }}
.h4big {{ position:absolute; left:0; right:0; top:330px; text-align:center; font-family:'Dela';
  font-size:300px; opacity:0; }}
.qcwrap {{ z-index:35; pointer-events:none; }}
.qcdark {{ position:absolute; inset:0; opacity:0;
  background:radial-gradient(ellipse at center, rgba(42,8,10,.78) 0%, rgba(8,3,5,.94) 78%); }}
.qctext {{ position:absolute; left:0; right:0; top:296px; text-align:center; font-family:'ShipA';
  font-size:114px; line-height:1.36; color:#f0e9dc; opacity:0; text-shadow:{OLK7}; z-index:2; }}
.qcsub {{ position:absolute; left:0; right:0; top:672px; text-align:center; font-family:'Yusei';
  font-size:47px; color:#e3cf9e; opacity:0; text-shadow:{OLK}; z-index:2; }}
.profrow, .chkrow {{ position:absolute; left:900px; font-family:'ShipA'; font-size:63px;
  color:#262230; opacity:0; text-shadow:{OLW}; padding-left:40px; }}
.profrow .pbar {{ position:absolute; left:0; top:9px; bottom:9px; width:14px; background:#c2342a; }}
.chkrow {{ left:850px; }}
.chkrow.ckl {{ left:120px; }}
.chkrow .ckm {{ color:#b98a2e; margin-right:16px; font-family:'NotoB'; }}
.chkrow.onv {{ color:#f4f2ea; text-shadow:{OLK}; }}
.chkrow.onv .ckm {{ color:#e8c872; }}
.chkrow.ckr {{ left:0; right:0; text-align:center; padding-left:0; font-size:64px; }}
.pbdark {{ position:absolute; inset:0; opacity:0; background:#04050a; }}
.pbline {{ position:absolute; left:0; right:0; top:450px; text-align:center; font-family:'ShipA';
  font-size:82px; color:#f0ece0; opacity:0; text-shadow:{OLK7}; z-index:2; }}
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
