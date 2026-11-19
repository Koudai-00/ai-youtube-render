# -*- coding: utf-8 -*-
"""japan03v3: index.html ビルダ(窓分割対応) — DESIGN03_v3.md たっくー技法密度版
技法: 行積み上げ/名札+吹き出し線画人物/ソースラベル/特大数値+赤丸/質問カード/
画面隅キャプション/ハードカット輪番/伏字/章扉。HF_WIN_START/HF_WIN_END で窓ビルド。
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "japan03v3"
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


def telop(eid, lid, html, hold=0.6, serif=False):
    """下部テロップ (キーワード色分け必須)。serif=True で明朝"""
    st = N[lid]["start"] - 0.05
    en = N[lid]["start"] + N[lid]["dur"] + hold
    cls = "telop ts" if serif else "telop"
    el_div(eid, st, en, "telopw", f'<div class="{cls}" id="{eid}i">{html}</div>')
    fromto(st + 0.02, f"#{eid}i", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.3, "power2.out")
    tw(en - 0.25, f'tl.to("#{eid}i", {{opacity: 0, duration: 0.22}}, %T%);')


# 線画SVG (白ストローク)
def svg_person(kind="stand", h=104):
    if kind == "runner":
        body = ('<circle cx="40" cy="13" r="11"/>'
                '<path d="M38 24 L30 56 L36 60"/>'
                '<path d="M34 34 L14 44"/><path d="M34 34 L52 26"/>'
                '<path d="M30 56 L10 72 L6 94"/><path d="M32 58 L50 74 L46 98"/>')
        return f'<svg viewBox="0 0 60 104" style="height:{h}px" class="sg">{body}</svg>'
    if kind == "elder":
        body = ('<circle cx="32" cy="14" r="11"/>'
                '<path d="M32 25 Q28 48 28 70"/>'
                '<path d="M31 38 L14 56"/><path d="M31 38 L48 52 L48 70"/>'
                '<path d="M28 70 L18 100"/><path d="M28 70 L38 100"/>'
                '<path d="M48 56 L48 100"/>')
        return f'<svg viewBox="0 0 60 104" style="height:{h}px" class="sg">{body}</svg>'
    if kind == "kid":
        body = ('<circle cx="30" cy="20" r="12"/>'
                '<path d="M30 32 L30 66"/>'
                '<path d="M30 42 L14 56"/><path d="M30 42 L46 56"/>'
                '<path d="M30 66 L20 96"/><path d="M30 66 L40 96"/>')
        return f'<svg viewBox="0 0 60 104" style="height:{int(h*0.72)}px" class="sg">{body}</svg>'
    body = ('<circle cx="30" cy="13" r="11"/>'
            '<path d="M30 24 L30 64"/>'
            '<path d="M30 36 L12 56"/><path d="M30 36 L48 56"/>'
            '<path d="M30 64 L16 100"/><path d="M30 64 L44 100"/>')
    return f'<svg viewBox="0 0 60 104" style="height:{h}px" class="sg">{body}</svg>'


# ============================================================ s_cold: q_ms1 肉声
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
    '<div class="qcap" id="msc1">地面には、散った桜の花びらだけ。<br>ほかのゴミが、<span class="gd">ほとんど無い</span>——</div>'
    '<div class="qcap qbig" id="msc2">「なんで、こんなに<span class="gd">きれい</span>なんだ?」</div>'
    '<div class="qcap" id="msc3">その一言に、思わず、足を緩めた</div>'))
sp = t0 + qi["lead"]
fromto(t0 + 0.3, "#msp", "x: -16, opacity: 0", "x: 0, opacity: 1", 0.4, "power2.out")
fromto(sp + 0.2, "#msc1", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
setv(sp + 6.8, "#msc1", "opacity: 0")
fromto(sp + 6.95, "#msc2", 'scale: 1.25, opacity: 0, filter: "blur(5px)"',
       'scale: 1, opacity: 1, filter: "blur(0px)"', 0.35, "back.out(1.6)")
setv(sp + 9.6, "#msc2", "opacity: 0")
fromto(sp + 9.75, "#msc3", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")

# ============================================================ s_think: 桜+線画+吹き出し
scene_bg("s_think")
sc = SC["s_think"]
telop("tp01", "n01", '観光客の<span class="gd">ひと言</span>が、彼を立ち止まらせた', serif=True)
ft = N["n01"]["start"] + 1.1
el_div("thf", ft - 0.15, sc["end"] + 0.1, "figwrap", (
    f'<div class="fig figR" id="thfg">{svg_person("runner", 215)}</div>'
    '<div class="bubble bubR" id="thbb">走りながら、<br>考え込んでしまった——</div>'))
fromto(ft, "#thfg", "y: 24, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
fromto(ft + 1.5, "#thbb", "scale: 0.4, opacity: 0", "scale: 1, opacity: 1", 0.4, "back.out(2.2)")

# ============================================================ s_title
scene_bg("s_title", cut=True)
sc = SC["s_title"]
tt = sc["start"] + 0.15
el_div("ttl", sc["start"], sc["end"] + 0.1, "twrap", (
    '<div class="tdark" id="tdk"></div>'
    '<div class="tlabel" id="tlb">ある在日中国人の「違和感」から始まる話</div>'
    '<div class="ttitle" id="tti">中国とは、<span class="trd">違いすぎた</span></div>'
    '<div class="tline" id="tln"></div>'
    '<div class="tsub" id="tsb">909万人が気づいた、日中の決定的な差</div>'))
fromto(tt, "#tdk", "opacity: 0", "opacity: 0.66", 0.3, "power1.in")
fromto(tt + 0.1, "#tlb", "opacity: 0, y: -12", "opacity: 1, y: 0", 0.4, "power2.out")
fromto(tt + 0.55, "#tti", 'opacity: 0, scale: 1.18, filter: "blur(10px)"',
       'opacity: 1, scale: 1, filter: "blur(0px)"', 0.5, "power3.out")
fromto(tt + 1.05, "#tln", "scaleX: 0", "scaleX: 1", 0.45, "power2.inOut")
fromto(tt + 1.3, "#tsb", "opacity: 0", "opacity: 1", 0.4, "power2.out")

# ============================================================ s_data1: srclabel+特大数値+赤丸
scene_bg("s_data1")
sc = SC["s_data1"]
el_div("sl1", sc["start"] + 0.2, SC["s_data2"]["end"] + 0.1, "srcw",
       '<div class="srclabel" id="sl1i">JNTO 訪日外客統計によると</div>')
fromto(sc["start"] + 0.3, "#sl1i", "x: -14, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")
d1 = N["n02"]["start"]
el_div("bn1", sc["start"] + 0.2, sc["end"] + 0.1, "bnwrap", (
    '<div class="bnlabel" id="bnl">2025年に日本を訪れた中国人</div>'
    '<div class="bignum" id="bnn"><span id="dnv">0</span><span class="bnunit">万人</span></div>'
    '<svg class="bncirc" id="bnc" viewBox="0 0 560 240"><ellipse cx="280" cy="120" rx="262" ry="104"/></svg>'
    '<div class="bnrow" id="bnr1">前年比 <span class="gd">+30.3%</span> — 過去最多ペース</div>'))
fromto(d1 - 0.1, "#bnl", "y: 20, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
fromto(d1 + 0.7, "#bnn", "opacity: 0, y: 24", "opacity: 1, y: 0", 0.3, "power2.out")
tw(d1 + 0.9, 'tl.fromTo(CNT, {v: 0}, {v: 909, duration: 1.15, ease: "power2.out", '
             'onUpdate: () => { const el = document.getElementById("dnv"); '
             'if (el) el.textContent = Math.round(CNT.v); }}, %T%);')
fromto(d1 + 2.2, "#bnc", "scale: 1.3, opacity: 0", "scale: 1, opacity: 1", 0.35, "back.out(1.8)")
fromto(d1 + 2.9, "#bnr1", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.35, "power2.out")

# ============================================================ s_data2: 行積み上げ
scene_bg("s_data2", cut=True)
sc = SC["s_data2"]
el_div("lb2", sc["start"] + 0.1, sc["end"] + 0.1, "lbwrap", (
    '<div class="lbrow" id="lr1">2025年8月 ⇒ ひと月で<span class="gd">100万人</span>を突破</div>'
    '<div class="lbrow" id="lr2">国・地域別の訪日客数 ⇒ <span class="rd">最多</span>に</div>'))
d2 = N["n03"]["start"]
fromto(d2 - 0.05, "#lr1", "x: -22, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")
fromto(d2 + 2.0, "#lr2", "x: -22, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")

# ============================================================ s_cn: 3ハードカット+隅キャプション
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
    '<div class="cnrow" id="cnr1">夜は、東京より<span class="gd">明るい</span></div>'
    '<div class="cnrow" id="cnr2">高鉄は、時速<span class="bl">350キロ</span></div>'
    '<div class="cnrow" id="cnr3">財布は、<span class="rd">持ち歩かない</span></div>'))
fromto(n4 + 3.4, "#cnr1", "x: 26, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")
fromto(n4 + 5.9, "#cnr2", "x: 26, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")
fromto(n4 + 8.9, "#cnr3", "x: 26, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")

# ============================================================ s_why: 質問カード
scene_bg("s_why", cut=True)
sc = SC["s_why"]
el_div("why", sc["start"], sc["end"] + 0.1, "qcwrap", (
    '<div class="qcdark" id="qcd"></div>'
    '<div class="qctext" id="qct">なぜ、<span class="rd">909万人</span>は<br>日本へ?</div>'
    '<div class="qcsub" id="qcs">— 何もかも、進んでいるはずなのに</div>'))
w0t = N["n05"]["start"] - 0.15
fromto(w0t, "#qcd", "opacity: 0", "opacity: 0.78", 0.4, "power1.in")
fromto(w0t + 0.25, "#qct", 'opacity: 0, scale: 1.12, filter: "blur(7px)"',
       'opacity: 1, scale: 1, filter: "blur(0px)"', 0.5, "power2.out")
fromto(w0t + 1.6, "#qcs", "opacity: 0", "opacity: 1", 0.45, "power2.out")

# ============================================================ s_fam: 線画ファミリー+名札+吹き出し
scene_bg("s_fam")
sc = SC["s_fam"]
telop("tp06", "n06", 'マレーシアの中華系ファミリー・<span class="gd">6人</span>の記録', hold=0.5)
figs = "".join(
    f'<div class="fig6" id="ff{i}">{svg_person(k, h)}</div>'
    for i, (k, h) in enumerate((("stand", 205), ("stand", 196), ("elder", 190),
                                ("elder", 186), ("kid", 205), ("kid", 190))))
el_div("fam", sc["start"] + 0.3, sc["end"] + 0.1, "figwrap", (
    '<div class="nplate npfam" id="fmp"><div class="ntag">家族6人・初めての日本</div>'
    '<div class="ncredit">引用: Nicaboo</div></div>'
    f'<div class="figrow" id="fgr">{figs}</div>'
    '<div class="bubble bubF" id="fmb">家族旅行が、<br>こんなことになるなんて</div>'))
f0 = N["n06"]["start"] + 0.8
fromto(f0 - 0.5, "#fmp", "x: -16, opacity: 0", "x: 0, opacity: 1", 0.4, "power2.out")
for i in range(6):
    fromto(f0 + 0.42 * i, f"#ff{i}", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.32, "back.out(1.5)")
fromto(f0 + 3.2, "#fmb", "scale: 0.4, opacity: 0", "scale: 1, opacity: 1", 0.4, "back.out(2.2)")

# ============================================================ s_noodle: テキスト引用
scene_bg("s_noodle")
sc = SC["s_noodle"]
el_div("ncc", sc["start"] + 0.2, sc["end"] + 0.1, "ccwrap ccTL",
       '<div class="ccap" id="ncci">到着初日・最初の一杯</div>')
fromto(sc["start"] + 0.35, "#ncci", "x: -12, opacity: 0", "x: 0, opacity: 1", 0.3, "power2.out")
qt = N["n07"]["start"] + N["n07"]["dur"] + 0.25
el_div("tq", qt - 0.1, sc["end"] + 0.1, "tqwrap", (
    '<div class="tquote" id="tqt">「コシがあって、柔らかい。<br>この味、<span class="gd">好き</span>」</div>'
    '<div class="tqsrc" id="tqs">— 家族の動画より(引用: Nicaboo)</div>'))
fromto(qt, "#tqt", 'opacity: 0, y: 20, filter: "blur(6px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.55, "power2.out")
fromto(qt + 0.7, "#tqs", "opacity: 0", "opacity: 1", 0.4, "power2.out")

# ============================================================ s_coldlead
scene_bg("s_coldlead", cut=True)
telop("tp08", "n08", 'ただし、日本の冬を<span class="rd">なめてはいけない</span>', hold=0.3, serif=True)

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
fromto(sp + 4.0, "#ncc2", 'scale: 1.2, opacity: 0', 'scale: 1, opacity: 1', 0.35, "back.out(1.6)")

# ============================================================ s_pivot (伏字)
scene_bg("s_pivot")
sc = SC["s_pivot"]
telop("tp09", "n09", '彼らの心を動かしたのは、<span class="gd">別のもの</span>', hold=0.1)
kt = N["n09"]["start"] + N["n09"]["dur"] + 0.3
el_div("kx", kt - 0.1, sc["end"] + 0.1, "kwrap", (
    '<div class="kdark"></div>'
    '<div class="kick" id="kk">本当の驚きは、<span class="fsslot">'
    '<span class="fsw fsa" id="fsa">●●●</span><span class="fsw fsb" id="fsb">気配り</span>'
    '</span>だった</div>'))
fromto(kt, "#kk", 'opacity: 0, y: 20', 'opacity: 1, y: 0', 0.5, "power2.out")
setv(kt, "#fsb", "opacity: 0, xPercent: -50")
ft = kt + 1.75
tw(ft, 'tl.to("#fsa", {opacity: 0, filter: "blur(8px)", duration: 0.2}, %T%);')
fromto(ft + 0.1, "#fsb", 'opacity: 0, xPercent: -50, scale: 1.35, filter: "blur(6px)"',
       'opacity: 1, xPercent: -50, scale: 1, filter: "blur(0px)"', 0.4, "power3.out")

# ============================================================ s_ch1 (章扉)
scene_bg("s_ch1", last=True)
sc = SC["s_ch1"]
el_div("c1o", sc["start"], COMP, "qov", (
    '<div class="cdark"></div>'
    '<div class="cwrap"><div class="cno" id="cn1">第 1 章</div>'
    '<div class="cline" id="cl1"></div>'
    '<div class="ctitle" id="ct1">丁寧さの、正体</div>'
    '<div class="csub" id="cs1">— ある中国人が、日本で通報された話</div></div>'))
t0 = sc["start"]
setv(t0 - 0.45, "#dip", "opacity: 0")
tw(t0 - 0.45, 'tl.to("#dip", {opacity: 1, duration: 0.35, ease: "power1.in"}, %T%);')
tw(t0 + 0.05, 'tl.to("#dip", {opacity: 0, duration: 0.5, ease: "power1.out"}, %T%);')
fromto(t0 + 0.35, "#cn1", "y: -16, opacity: 0", "y: 0, opacity: 1", 0.5, "power3.out")
fromto(t0 + 0.6, "#cl1", "scaleX: 0", "scaleX: 1", 0.45, "power2.inOut")
fromto(t0 + 0.8, "#ct1", 'opacity: 0, y: 24, filter: "blur(9px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.65, "power2.out")
fromto(t0 + 1.5, "#cs1", "opacity: 0", "opacity: 1", 0.45, "power2.out")
tw(COMP - 1.15, 'tl.to("#stage", {opacity: 0, duration: 1.0, ease: "power1.in"}, %T%);')

# ============================================================ assemble html
CSS = """
@font-face { font-family:'NotoB'; src:url('assets/fonts/NotoSansJP-Black.otf') format('opentype'); }
@font-face { font-family:'NotoBd'; src:url('assets/fonts/NotoSansJP-Bold.otf') format('opentype'); }
@font-face { font-family:'ShipA'; src:url('assets/fonts/ShipporiMinchoB1-ExtraBold.ttf') format('truetype'); }
@font-face { font-family:'Dela'; src:url('assets/fonts/DelaGothicOne-Regular.ttf') format('truetype'); }
@font-face { font-family:'ZenK'; src:url('assets/fonts/ZenKakuGothicNew-Black.ttf') format('truetype'); }
@font-face { font-family:'ZenB'; src:url('assets/fonts/ZenKakuGothicNew-Bold.ttf') format('truetype'); }
@font-face { font-family:'MPR'; src:url('assets/fonts/MPLUSRounded1c-ExtraBold.ttf') format('truetype'); }
@font-face { font-family:'Yusei'; src:url('assets/fonts/YuseiMagic-Regular.ttf') format('truetype'); }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { background:#000; }
#root { position:relative; width:1920px; height:1080px; overflow:hidden;
  background:#0a0d14; font-family:'NotoBd',sans-serif; color:#f2f4f8; }
#stage { position:absolute; inset:0; }
.clip { position:absolute; inset:0; width:100%; height:100%; }
.bgw { position:absolute; inset:0; opacity:0; will-change:transform,opacity; }
video.bgv { position:absolute; inset:0; width:100%; height:100%; object-fit:cover;
  transform:translateZ(0); backface-visibility:hidden; }
.gd { color:#e8c872; } .rd { color:#ff6a55; } .bl { color:#7db8e8; } .gr { color:#7ec87e; }
#scrim { position:absolute; inset:0; z-index:28; pointer-events:none;
  background:linear-gradient(0deg, rgba(5,7,12,.70) 0%, rgba(5,7,12,.16) 15%, rgba(5,7,12,0) 30%); }
#barT, #barB { position:absolute; left:0; right:0; height:64px; background:#000; z-index:40; }
#barT { top:0; } #barB { bottom:0; }
#dip { position:absolute; inset:0; background:#000; z-index:38; opacity:0; pointer-events:none; }
/* テロップ */
.telopw { z-index:33; pointer-events:none; display:flex; align-items:flex-end;
  justify-content:center; padding-bottom:90px; }
.telop { font-family:'NotoB'; font-size:46px; letter-spacing:.04em; text-align:center;
  max-width:1680px; color:#f2f4f8; opacity:0;
  text-shadow:0 0 6px rgba(0,0,0,.95), 0 3px 18px rgba(0,0,0,.9); }
.telop.ts { font-family:'ShipA'; font-size:50px; letter-spacing:.05em; }
/* 名札 + 引用字幕 */
.qov { z-index:34; pointer-events:none; }
.nplate { position:absolute; left:56px; top:92px; opacity:0; }
.nplate .ntag { display:inline-block; background:#c2342a; color:#fff; font-family:'ZenK';
  font-size:30px; letter-spacing:.06em; padding:10px 20px;
  box-shadow:0 3px 14px rgba(0,0,0,.5); }
.nplate .ncredit { display:block; margin-top:6px; background:rgba(5,8,14,.72); color:#cdd6e2;
  font-family:'ZenB'; font-size:20px; padding:5px 12px; width:max-content; }
.qcap { position:absolute; left:60px; right:60px; bottom:176px; text-align:center; font-size:50px;
  font-family:'ShipA'; color:#f6f3ea; letter-spacing:.02em; opacity:0;
  text-shadow:0 0 6px rgba(0,0,0,.95), 0 3px 18px rgba(0,0,0,.9); }
.qcap.qbig { font-size:64px; bottom:166px; }
/* 線画 + 吹き出し */
.figwrap { z-index:33; pointer-events:none; }
.sg { fill:none; stroke:#f2f4f8; stroke-width:6.5; stroke-linecap:round; stroke-linejoin:round; }
.fig { position:absolute; opacity:0;
  filter:drop-shadow(0 4px 14px rgba(0,0,0,.6)); }
.figR { right:170px; bottom:200px; }
.bubble { position:absolute; background:#fdfdf8; color:#15181f; font-family:'MPR';
  font-size:33px; line-height:1.45; padding:20px 28px; border-radius:20px; opacity:0;
  box-shadow:0 6px 24px rgba(0,0,0,.45); }
.bubble:after { content:""; position:absolute; bottom:-16px; left:70%; border:10px solid transparent;
  border-top-color:#fdfdf8; border-left-width:6px; border-right-width:6px; }
.bubR { right:150px; bottom:450px; transform-origin:70% 100%; }
.bubF { right:230px; bottom:540px; transform-origin:60% 100%; }
/* タイトル */
.twrap { z-index:35; pointer-events:none; }
.tdark { position:absolute; inset:0; background:#06080e; opacity:0; }
.tlabel { position:absolute; left:0; right:0; top:296px; text-align:center; font-family:'ZenB';
  font-size:31px; letter-spacing:.3em; color:#cfd8e4; opacity:0; }
.ttitle { position:absolute; left:0; right:0; top:372px; text-align:center; font-family:'Dela';
  font-size:118px; color:#f5f6f8; opacity:0; letter-spacing:.01em;
  text-shadow:0 6px 36px rgba(0,0,0,.85); }
.trd { color:#ff5a44; }
.tline { position:absolute; left:50%; top:596px; width:560px; margin-left:-280px; height:3px;
  transform-origin:center; transform:scaleX(0);
  background:linear-gradient(90deg, rgba(232,200,114,0), #e8c872 30%, #ff6a55 70%, rgba(255,106,85,0)); }
.tsub { position:absolute; left:0; right:0; top:640px; text-align:center; font-family:'ShipA';
  font-size:37px; color:#e3d9c4; opacity:0; }
/* ソースラベル */
.srcw { z-index:34; pointer-events:none; }
.srclabel { position:absolute; left:56px; top:96px; border:2px solid rgba(242,244,248,.85);
  background:rgba(5,8,14,.55); color:#f2f4f8; font-family:'ZenK'; font-size:26px;
  letter-spacing:.08em; padding:8px 18px; opacity:0; }
/* 特大数値 */
.bnwrap { z-index:33; pointer-events:none; }
.bnlabel { position:absolute; left:0; right:0; top:300px; text-align:center; font-family:'ShipA';
  font-size:42px; color:#f2ecdc; opacity:0; text-shadow:0 2px 14px rgba(0,0,0,.9); }
.bignum { position:absolute; left:0; right:0; top:368px; text-align:center; font-family:'Dela';
  font-size:190px; color:#e8c872; opacity:0; font-variant-numeric:tabular-nums;
  text-shadow:0 6px 36px rgba(0,0,0,.9); }
.bignum .bnunit { font-size:70px; color:#f2f4f8; margin-left:10px; }
.bncirc { position:absolute; left:50%; top:340px; width:560px; height:240px; margin-left:-280px;
  opacity:0; }
.bncirc ellipse { fill:none; stroke:#ff5a44; stroke-width:7; }
.bnrow { position:absolute; left:0; right:0; top:648px; text-align:center; font-family:'NotoB';
  font-size:38px; color:#e8edf4; opacity:0; text-shadow:0 2px 14px rgba(0,0,0,.9); }
/* 行積み上げ */
.lbwrap { z-index:33; pointer-events:none; }
.lbrow { position:absolute; left:140px; font-family:'ShipA'; font-size:48px; color:#f2ecdc;
  opacity:0; background:rgba(5,8,14,.55); padding:12px 26px;
  text-shadow:0 2px 12px rgba(0,0,0,.8); }
#lr1 { top:380px; } #lr2 { top:490px; }
/* 中国3カット */
.cnlines { z-index:33; pointer-events:none; }
.cnrow { position:absolute; right:130px; text-align:right; font-family:'ShipA'; font-size:50px;
  color:#f6f3ea; opacity:0; background:rgba(5,8,14,.5); padding:10px 24px;
  text-shadow:0 2px 12px rgba(0,0,0,.85); }
#cnr1 { top:330px; } #cnr2 { top:440px; } #cnr3 { top:550px; }
.ccwrap { z-index:34; pointer-events:none; }
.ccap { position:absolute; background:#c2342a; color:#fff; font-family:'ZenK'; font-size:27px;
  letter-spacing:.06em; padding:8px 18px; opacity:0; box-shadow:0 3px 14px rgba(0,0,0,.5); }
.ccTL .ccap { left:56px; top:96px; }
.ccBR .ccap { right:56px; bottom:110px; }
/* 質問カード */
.qcwrap { z-index:35; pointer-events:none; }
.qcdark { position:absolute; inset:0; opacity:0;
  background:radial-gradient(ellipse at center, rgba(26,6,8,.82) 0%, rgba(8,3,5,.96) 75%); }
.qctext { position:absolute; left:0; right:0; top:360px; text-align:center; font-family:'ShipA';
  font-size:88px; line-height:1.4; color:#f0e9dc; opacity:0;
  text-shadow:0 4px 30px rgba(0,0,0,.95); }
.qcsub { position:absolute; left:0; right:0; top:660px; text-align:center; font-family:'Yusei';
  font-size:38px; color:#d8c9b4; opacity:0; }
/* 線画ファミリー */
.figrow { position:absolute; left:0; right:0; bottom:280px; display:flex; gap:64px;
  justify-content:center; align-items:flex-end; }
.fig6 { opacity:0; filter:drop-shadow(0 4px 14px rgba(0,0,0,.6)); }
.npfam { left:56px; top:92px; }
/* テキスト引用 */
.tqwrap { z-index:35; pointer-events:none; }
.tquote { position:absolute; left:0; right:0; top:300px; text-align:center; font-family:'ShipA';
  font-size:76px; line-height:1.5; color:#f5f6f8; opacity:0;
  text-shadow:0 4px 28px rgba(0,0,0,.9); }
.tqsrc { position:absolute; left:0; right:0; top:570px; text-align:center; font-family:'ZenB';
  font-size:30px; color:#cfd8e4; opacity:0; text-shadow:0 2px 12px rgba(0,0,0,.85); }
/* 伏字 */
.kwrap { z-index:35; pointer-events:none; }
.kdark { position:absolute; inset:0; background:rgba(4,6,10,.55); }
.kick { position:absolute; left:0; right:0; top:450px; text-align:center; font-family:'ShipA';
  font-size:88px; color:#f5f6f8; opacity:0;
  text-shadow:0 4px 30px rgba(0,0,0,.9); }
.fsslot { position:relative; display:inline-block; min-width:300px; }
.fsw { display:inline-block; }
.fsa { color:#aab6c8; }
.fsb { position:absolute; left:50%; top:0; color:#ff5a44; white-space:nowrap; }
/* 章扉 */
.cdark { position:absolute; inset:0; background:rgba(4,6,10,.62); }
.cwrap { position:absolute; inset:0; }
.cno { position:absolute; left:0; right:0; top:330px; text-align:center; font-family:'Dela';
  font-size:44px; letter-spacing:.42em; color:#e8c872; opacity:0; }
.cline { position:absolute; left:50%; top:418px; width:420px; margin-left:-210px; height:3px;
  transform-origin:center; transform:scaleX(0); background:rgba(232,200,114,.75); }
.ctitle { position:absolute; left:0; right:0; top:452px; text-align:center; font-family:'ShipA';
  font-size:108px; color:#f5f6f8; opacity:0;
  text-shadow:0 4px 30px rgba(0,0,0,.85); }
.csub { position:absolute; left:0; right:0; top:640px; text-align:center; font-family:'ZenB';
  font-size:34px; color:#cfd8e4; opacity:0; }
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
<div id="scrim"></div>
<div id="dip"></div>
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
