# -*- coding: utf-8 -*-
"""japan02 長尺・冒頭1分: index.html ビルダ(窓分割対応)
HF_WIN_START / HF_WIN_END env で窓ビルド。全tweenは fromTo(immediateRender:false) 絶対時刻
→ 窓外tweenは出力されず、要素はCSSの最終状態で表示される(=cont対応)。
"""
import json
import os
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "japan02"
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


B = {b["id"]: (b["start"], b["end"]) for b in TIM["beats"]}
N = TIM["narr"]
Q = TIM["quotes"]

ELS = []     # html strings (timed elements)
TWEENS = []  # js lines
_track = [0]


def track():
    _track[0] += 1
    return _track[0]


def el_div(eid, t0, t1, cls, inner, style=""):
    if not OV(t0, t1):
        return
    s = max(t0, W0)
    d = round(t1 - s, 3)
    ELS.append(
        f'<div id="{eid}" class="clip {cls}" data-start="{T(s)}" data-duration="{d}" '
        f'data-track-index="{track()}" style="{style}">{inner}</div>')


def el_video(eid, t0, t1, src, ms, cls=""):
    if not OV(t0, t1):
        return
    s = max(t0, W0)
    d = round(t1 - s, 3)
    ms_eff = round(ms + (s - t0), 3)
    ELS.append(
        f'<video id="{eid}" class="clip bgv {cls}" data-start="{T(s)}" data-duration="{d}" '
        f'data-media-start="{ms_eff}" data-track-index="{track()}" '
        f'src="assets/bg/{src}" muted playsinline></video>')


def tw(t, js):
    # 実績方式: tweenは絶対時刻のまま。登録タイムラインが tl を W0→W1 でスクラブする。
    TWEENS.append(js.replace("%T%", str(round(t, 3))))


def fromto(t, sel, frm, to, dur, ease):
    tw(t, f'tl.fromTo("{sel}", {{{frm}}}, {{{to}, duration: {dur}, ease: "{ease}", immediateRender: false}}, %T%);')


def setv(t, sel, vars_):
    tw(t, f'tl.set("{sel}", {{{vars_}}}, %T%);')


rng = random.Random(7)


def glitch(t, strength=1.0):
    """称賛トーン: 暖色の光ブルームでつなぐ(グリッチ禁止)"""
    setv(t, "#flash", f'opacity: {0.42*strength:.2f}')
    tw(t + 0.04, f'tl.to("#flash", {{opacity: 0, duration: {0.55+0.15*strength:.2f}, ease: "power2.out"}}, %T%);')


# ============================================================ quote beats
QCAP = {
    "qthd": {"credit": "引用: Those Happy Days",
             "cap": '「衝撃を受けるぞ」と<em>警告</em>されていた', "sub": "— でもそれは、想像とは真逆の衝撃だった"},
    "qtak": {"credit": "引用: TAKASHii",
             "cap": '朝4時の東京を <em>ひとりで</em>歩ける', "sub": None},
    "qchani": {"credit": "引用: Chani Japan",
               "cap": '喪失を抱えた私に 日本は<em>平穏</em>をくれた', "sub": None},
    "qkalani": {"credit": "引用: Kalani James Lenehan", "cap": None, "sub": None},
}

for q in ["qthd", "qtak", "qchani", "qkalani"]:
    qi = Q[q]
    t0 = qi["beat_start"]
    t1 = t0 + qi["dur"]
    el_video(f"{q}v", t0, t1, qi["clip"], qi["media_start"])
    c = QCAP[q]
    if q == "qkalani":
        inner = ('<div class="qscrim"></div>'
                 f'<div class="credit">{c["credit"]}</div>'
                 '<div class="qcap" id="qkalani-c1">美しすぎて 何度も<em>泣いた</em></div>'
                 '<div class="qcap qcap2" id="qkalani-c2">人生で<em>最高</em>の旅だった</div>')
    else:
        sub = f'<div class="qsub" id="{q}-s">{c["sub"]}</div>' if c["sub"] else ""
        inner = ('<div class="qscrim"></div>'
                 f'<div class="credit">{c["credit"]}</div>'
                 f'<div class="qcap" id="{q}-c">{c["cap"]}</div>' + sub)
    el_div(f"{q}o", t0, t1, "qov", inner)
    fromto(t0 + 0.05, f"#{q}v", "scale: 1.05", "scale: 1", 2.2, "power2.out")

# caption entrances (speech開始に同期)
for q in ["qthd", "qtak", "qchani"]:
    sp = Q[q]["beat_start"] + Q[q]["lead"]
    fromto(sp + 0.05, f"#{q}-c", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.35, "power3.out")
    if QCAP[q]["sub"]:
        fromto(sp + 1.0, f"#{q}-s", "opacity: 0", "opacity: 1", 0.4, "power2.out")
qa0 = Q["qkalani"]["beat_start"]
fromto(qa0 + 0.5, "#qkalani-c1", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.35, "power3.out")
fromto(qa0 + 3.3, "#qkalani-c2", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.35, "power3.out")

# boundary blooms
glitch(B["qthd"][0], 0.9)
glitch(B["qtak"][0], 1.0)
glitch(B["qchani"][0], 1.0)
glitch(B["n01"][0], 0.8)
glitch(B["qkalani"][0], 1.0)

# ============================================================ n01 statement over bright street
t0, t1 = B["n01"]
el_video("n01v", t0, t1, "stmt.mp4", 0.0)
el_div("n01o", t0, t1, "qov", (
    '<div class="qscrim"></div>'
    '<div class="credit">引用: Kalani James Lenehan</div>'
    '<div class="stm" id="stm1">いま 世界中の外国人が</div>'
    '<div class="stm stm2" id="stm2">日本に<em>人生を変えられて</em>いる<div class="uline" id="ul1"></div></div>'))
fromto(N["n01"]["start"] + 0.1, "#stm1", "y: 24, opacity: 0", "y: 0, opacity: 1", 0.35, "power3.out")
fromto(N["n01"]["start"] + 1.6, "#stm2", "y: 24, opacity: 0", "y: 0, opacity: 1", 0.35, "power3.out")
fromto(N["n01"]["start"] + 3.3, "#ul1", "scaleX: 0", "scaleX: 1", 0.45, "power2.inOut")

# ============================================================ n02 kalani profile
t0, t1 = B["n02"]
el_video("n02v", t0, t1, "profile.mp4", 0.0)
chips = "".join(f'<div class="chip" id="chip{i}">{c}</div>'
                for i, c in enumerate(["初めてのひとり旅", "ほぼ無計画", "そして、涙"], 1))
el_div("n02o", t0, t1, "qov", (
    '<div class="qscrim"></div>'
    '<div class="credit">引用: Kalani James Lenehan</div>'
    '<div class="lt" id="lt1"><div class="ltbar"></div>'
    '<div class="ltbody"><div class="ltname">初めて日本を訪れた 20代の男性</div>'
    '<div class="ltrole">Kalani James Lenehan — 人生が変わった旅</div></div></div>'
    f'<div class="chips">{chips}</div>'))
glitch(t0, 0.7)
fromto(t0 + 0.05, "#n02v", "scale: 1.04", "scale: 1", 2.0, "power2.out")
fromto(t0 + 0.4, "#lt1", "x: -70, opacity: 0", "x: 0, opacity: 1", 0.45, "power3.out")
for i, dt in enumerate([1.9, 2.7, 3.5], 1):
    fromto(t0 + dt, f"#chip{i}", "y: 18, opacity: 0, scale: 0.95", "y: 0, opacity: 1, scale: 1", 0.35, "power2.out")

# ============================================================ v4: トランジション補助
def tr_wipe(t0):
    setv(t0 - 0.23, "#twipe", "opacity: 1")
    fromto(t0 - 0.23, "#twipe", "x: -1990", "x: 0", 0.23, "power1.in")
    fromto(t0 + 0.02, "#twipe", "x: 0", "x: 1990", 0.3, "power2.in")
    setv(t0 + 0.35, "#twipe", "opacity: 0, x: -1990")


def tr_fade(t0):
    setv(t0 - 0.01, "#tbk", "opacity: 1")
    tw(t0 + 0.02, 'tl.to("#tbk", {opacity: 0, duration: 0.7, ease: "power2.out"}, %T%);')


# ============================================================ info panel
t0, t1 = B["info"]
el_video("infobgx", t0, t1, "bgx_info.mp4", 0.0)
icon_plane = ('<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3">'
              '<path d="M4 30 L42 16 M42 16 L30 20 L18 10 L14 12 L23 22 M42 16 L34 26 L36 38 L33 39 L27 28"/>'
              '<line x1="6" y1="40" x2="26" y2="40"/></svg>')
icon_yen = ('<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3">'
            '<circle cx="24" cy="24" r="17"/><path d="M17 14 L24 24 L31 14"/>'
            '<line x1="24" y1="24" x2="24" y2="35"/><line x1="18" y1="27" x2="30" y2="27"/>'
            '<line x1="18" y1="32" x2="30" y2="32"/></svg>')
icon_trophy = ('<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3">'
               '<path d="M14 8h20v10a10 10 0 0 1-20 0z"/>'
               '<path d="M14 10h-6a6 6 0 0 0 6 9M34 10h6a6 6 0 0 1-6 9"/>'
               '<line x1="24" y1="28" x2="24" y2="35"/><path d="M16 40h16M19 35h10"/></svg>')
items = [
    ("i1", icon_plane, "訪日客", "4268万人 — 過去最多を更新"),
    ("i2", icon_yen, "消費額", "9兆円超 — 経済の柱の1つに"),
    ("i3", icon_trophy, "世界の評価", "“最も魅力的な国” 3年連続1位"),
]
rows = "".join(
    f'<div class="irow" id="{iid}"><div class="iic">{ic}</div>'
    f'<div class="itx"><div class="iplace">{pl}</div><div class="idesc">{ds}</div></div></div>'
    for iid, ic, pl, ds in items)
el_div("infop", t0, t1, "panel clear", (
    '<div class="phead" id="ph1">世界中が、<br>日本へ向かっている<div class="phline" id="phl"></div></div>'
    f'<div class="irows">{rows}<div class="tline" id="tl1"></div></div>'))
fromto(t0 + 0.35, "#ph1", "x: -50, opacity: 0", "x: 0, opacity: 1", 0.5, "power3.out")
fromto(t0 + 0.8, "#phl", "scaleX: 0", "scaleX: 1", 0.5, "power2.inOut")
fromto(t0 + 0.6, "#tl1", "scaleY: 0", "scaleY: 1", 8.0, "none")
n4 = N["n04"]["start"]
for iid, dt in [("i1", 0.15), ("i2", 1.75), ("i3", 3.5)]:
    fromto(n4 + dt, f"#{iid}", "x: 70, opacity: 0", "x: 0, opacity: 1", 0.45, "power3.out")
tr_wipe(t0)

# ============================================================ diagram
t0, t1 = B["diagram"]
el_video("diagbgx", t0, t1, "bgx_diagram.mp4", 0.0)
tr_fade(t0)
outer = ""
pos = [(13, 22), (78, 16), (12, 68), (76, 72)]
for i, (x, y) in enumerate(pos, 1):
    outer += (f'<div class="onode" id="on{i}" style="left:{x}%;top:{y}%">'
              '<svg viewBox="0 0 36 36"><circle cx="18" cy="12" r="6.5" fill="currentColor"/>'
              '<path d="M5 33 a13 11 0 0 1 26 0z" fill="currentColor"/></svg></div>')
arrows = "".join(
    f'<div class="arrow" id="ar{i}" style="left:{ax}%;top:{ay}%;transform:rotate({deg}deg)"></div>'
    for i, (ax, ay, deg) in enumerate([(27, 33, 35), (63, 29, 145), (27, 63, -35), (62, 66, -145)], 1))
el_div("diag", t0, t1, "panel clear", (
    '<div class="dhead" id="dh1">彼らが語るのは <em>安心</em>と<em>優しさ</em></div>'
    f'{outer}{arrows}'
    '<div class="cnode" id="cn1"><span>日本</span></div>'
    '<div class="dnote" id="dn1">国籍も、年齢も、旅の理由も、ばらばらなのに</div>'))
fromto(t0 + 0.25, "#dh1", "y: -30, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
fromto(t0 + 0.55, "#cn1", "scale: 0, opacity: 0", "scale: 1, opacity: 1", 0.5, "back.out(1.6)")
for i, dt in enumerate([0.95, 1.1, 1.25, 1.4], 1):
    fromto(t0 + dt, f"#on{i}", "scale: 0, opacity: 0", "scale: 1, opacity: 1", 0.35, "back.out(2)")
for i, dt in enumerate([1.55, 1.65, 1.75, 1.85], 1):
    fromto(t0 + dt, f"#ar{i}", "opacity: 0", "opacity: 1", 0.25, "power2.out")
fromto(t0 + 1.0, "#dn1", "opacity: 0", "opacity: 1", 0.4, "power2.out")
tw(t0 + 2.1, 'tl.to("#cn1", {scale: 1.07, duration: 0.38, ease: "sine.inOut", repeat: 5, yoyo: true}, %T%);')

# ============================================================ title
t0, t1 = B["title"]
el_video("titlebgx", t0, t1, "bgx_title.mp4", 0.0)
el_div("titlebeat", t0, t1, "panel tpanel clear", (
    '<div class="glow" id="tglow"></div>'
    '<div class="ttl-wrap">'
    '<div class="ttl-top" id="tt1">なぜ、世界は</div>'
    '<div class="ttl-main" id="ttm">日本に<em>恋をする</em>のか</div>'
    '<div class="ttl-sub" id="tts">4人の外国人の体験から 徹底深掘り</div>'
    '</div>'))
glitch(t0, 1.0)
fromto(t0 + 0.2, "#tt1", "y: -26, opacity: 0", "y: 0, opacity: 1", 0.5, "power3.out")
fromto(t0 + 0.42, "#ttm", 'scale: 1.1, opacity: 0, filter: "blur(12px)"',
       'scale: 1, opacity: 1, filter: "blur(0px)"', 0.9, "power2.out")
fromto(t0 + 0.55, "#tglow", "opacity: 0", "opacity: 1", 1.2, "power2.out")
fromto(t0 + 1.5, "#tts", "y: 20, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")

# ============================================================ creator cards
t0, t1 = B["cards"]
cards = [
    ("c1", "card_thd.jpg", "01", "初来日の夫婦"),
    ("c2", "card_tak.jpg", "02", "在住アメリカ人"),
    ("c3", "card_chani.jpg", "03", "喪失を抱えた女性"),
    ("c4", "card_kalani.jpg", "04", "20代のひとり旅"),
]
chtml = "".join(
    f'<div class="card" id="{cid}"><img src="assets/img/{img}" alt="">'
    f'<div class="cshade"></div><div class="cnum">{num}</div><div class="clab">{lab}</div></div>'
    for cid, img, num, lab in cards)
el_div("cardbeat", t0, t1, "panel", f'<div class="chead" id="chd">4人の体験</div><div class="cgrid">{chtml}</div>')
tr_wipe(t0)
fromto(t0 + 0.2, "#chd", "opacity: 0", "opacity: 1", 0.4, "power2.out")
n7 = N["n07"]["start"]
for cid, dt in [("c1", 0.05), ("c2", 1.5), ("c3", 2.9), ("c4", 4.35)]:
    fromto(n7 + dt, f"#{cid}", "y: 90, opacity: 0, rotation: 1.5", "y: 0, opacity: 1, rotation: 0", 0.5, "power3.out")

# ============================================================ chapter 1
t0, t1 = B["ch1"]
el_video("ch1v", t0, t1, "ch1.mp4", 0.0)
el_div("ch1o", t0, t1, "qov", (
    '<div class="ch1scrim"></div>'
    '<div class="credit">引用: Those Happy Days</div>'
    '<div class="chno" id="chno">第 1 章</div>'
    '<div class="chttl" id="chttl">世界が、日本に驚く</div>'
    '<div class="chsub" id="chsub">— 初めての48時間に、何が起きるのか</div>'))
glitch(t0, 1.0)
fromto(t0 + 0.25, "#chno", "x: -40, opacity: 0", "x: 0, opacity: 1", 0.4, "power3.out")
fromto(t0 + 0.5, "#chttl", 'scale: 1.1, opacity: 0, filter: "blur(8px)"',
       'scale: 1, opacity: 1, filter: "blur(0px)"', 0.8, "power2.out")
fromto(t0 + 1.1, "#chsub", "opacity: 0", "opacity: 1", 0.45, "power2.out")
tw(COMP - 1.05, 'tl.to("#stage", {opacity: 0, duration: 0.9, ease: "power1.in"}, %T%);')

# ============================================================ assemble html
CSS = """
@font-face { font-family:'NotoB'; src:url('assets/fonts/NotoSansJP-Black.otf') format('opentype'); }
@font-face { font-family:'NotoBd'; src:url('assets/fonts/NotoSansJP-Bold.otf') format('opentype'); }
@font-face { font-family:'SerifJP'; src:url('assets/fonts/NotoSerifJP.ttf') format('truetype');
  font-weight:100 900; }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { background:#000; }
#root { position:relative; width:1920px; height:1080px; overflow:hidden;
  background:#0b0a07; font-family:'NotoB','NotoBd',sans-serif; color:#f2f1ec; }
#stage { position:absolute; inset:0; }
.clip { position:absolute; inset:0; width:100%; height:100%; }
video.bgv { object-fit:cover; transform:translateZ(0); backface-visibility:hidden; }
em { font-style:normal; color:#e3b55e; }
/* overlays */
#scan { position:absolute; inset:0; z-index:40; pointer-events:none; opacity:.14;
  background:repeating-linear-gradient(0deg, rgba(0,0,0,.55) 0 2px, rgba(0,0,0,0) 2px 5px); }
#vig { position:absolute; inset:0; z-index:41; pointer-events:none;
  background:radial-gradient(ellipse 115% 105% at 50% 46%, rgba(0,0,0,0) 58%, rgba(0,0,0,.52) 100%); }
#flash { position:absolute; inset:0; z-index:60; background:#f5ead5; opacity:0; pointer-events:none; }
.gl { position:absolute; left:-80px; right:-80px; z-index:59; opacity:0; pointer-events:none; }
#gl1 { background:rgba(217,164,65,.4); }
#gl2 { background:rgba(245,234,213,.3); }
#gl3 { background:rgba(242,241,236,.75); }
/* quote overlays */
.qov { z-index:10; }
.qscrim { position:absolute; left:0; right:0; bottom:0; height:460px;
  background:linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(2,3,5,.62) 42%, rgba(2,3,5,.86) 100%); }
.ch1scrim { position:absolute; inset:0;
  background:linear-gradient(180deg, rgba(2,3,5,.35) 0%, rgba(2,3,5,.72) 70%, rgba(2,3,5,.9) 100%); }
.credit { position:absolute; top:34px; right:44px; font-family:'NotoBd'; font-size:26px;
  color:rgba(242,241,236,.85); background:rgba(5,6,9,.55); padding:8px 18px; border-left:4px solid #d9a441; }
.qcap { position:absolute; left:0; right:0; bottom:150px; text-align:center; font-size:84px;
  letter-spacing:.02em; text-shadow:0 4px 26px rgba(0,0,0,.9), 0 0 2px rgba(0,0,0,.9); opacity:0; }
.qcap2 { bottom:56px; }
.qsub { position:absolute; left:0; right:0; bottom:66px; text-align:center; font-family:'NotoBd';
  font-size:34px; color:rgba(242,241,236,.8); text-shadow:0 2px 12px rgba(0,0,0,.9); opacity:0; }
.stm { position:absolute; left:0; right:0; bottom:236px; text-align:center; font-size:72px;
  text-shadow:0 4px 26px rgba(0,0,0,.92); opacity:0; }
.stm2 { bottom:118px; font-size:92px; }
.uline { position:absolute; left:50%; margin-left:-330px; bottom:-14px; width:660px; height:10px;
  background:#d9a441; transform:scaleX(0); transform-origin:left; }
/* lower third */
.lt { position:absolute; left:70px; bottom:96px; display:flex; opacity:0; }
.ltbar { width:12px; background:#d9a441; }
.ltbody { background:rgba(5,6,9,.78); padding:22px 38px 24px 30px; }
.ltname { font-size:52px; }
.ltrole { font-family:'NotoBd'; font-size:28px; color:#e8c37a; margin-top:6px; }
.chips { position:absolute; right:70px; bottom:110px; display:flex; gap:22px; }
.chip { font-size:36px; background:rgba(5,6,9,.72); border:2px solid #d9a441;
  padding:12px 26px; border-radius:999px; opacity:0; }
/* panels */
.panel { z-index:10; background:#16130c; }
.panel.clear { background:linear-gradient(180deg, rgba(10,9,6,.78) 0%, rgba(10,9,6,.48) 45%, rgba(10,9,6,.78) 100%); }
#tbk { position:absolute; inset:0; z-index:56; background:#000; opacity:0; pointer-events:none; }
#twipe { position:absolute; left:0; top:-2px; width:1930px; height:1084px; z-index:57; opacity:0;
  background:linear-gradient(90deg, #0a0d12 0%, #131a24 85%, #d9a441 99%, #d9a441 100%);
  transform:translateX(-1990px); pointer-events:none; }
.phead { position:absolute; left:110px; top:50%; transform:translateY(-50%); width:720px;
  font-size:80px; line-height:1.26; opacity:0; }
.phline { width:230px; height:12px; background:#d9a441; margin-top:30px; transform-origin:left; transform:scaleX(0); }
.irows { position:absolute; right:100px; top:50%; transform:translateY(-50%); width:880px; }
.tline { position:absolute; left:-56px; top:14px; bottom:10px; width:6px; background:#3a3220;
  transform-origin:top; transform:scaleY(0); }
.irow { display:flex; align-items:center; gap:36px; margin-bottom:74px; opacity:0; }
.irow:last-child { margin-bottom:0; }
.iic { width:110px; height:110px; flex:none; color:#e8c37a; background:#1c1812;
  border:3px solid #3a3220; border-radius:18px; display:flex; align-items:center; justify-content:center; }
.iic svg { width:64px; height:64px; }
.iplace { font-size:30px; color:#d9a441; font-family:'NotoBd'; letter-spacing:.14em; }
.idesc { font-size:44px; line-height:1.3; margin-top:4px; }
/* diagram */
.dhead { position:absolute; left:0; right:0; top:96px; text-align:center; font-size:66px; opacity:0; }
.cnode { position:absolute; left:50%; top:54%; width:340px; height:340px; margin:-170px 0 0 -170px;
  background:radial-gradient(circle at 50% 42%, #3a2c13, #1c1507 70%); border:6px solid #d9a441; border-radius:50%;
  display:flex; align-items:center; justify-content:center; text-align:center; font-size:64px; line-height:1.2;
  box-shadow:0 0 90px rgba(217,164,65,.35); opacity:0; }
.onode { position:absolute; width:150px; height:150px; margin:-75px 0 0 -75px; color:#8a93a0;
  background:#1c1812; border:3px solid #3a3220; border-radius:50%; padding:26px; opacity:0; }
.onode svg { width:100%; height:100%; }
.arrow { position:absolute; width:250px; height:8px; background:linear-gradient(90deg, rgba(138,147,160,0), #d9a441);
  opacity:0; }
.arrow::after { content:''; position:absolute; right:-4px; top:-10px; border:14px solid transparent;
  border-left:18px solid #d9a441; }
.dnote { position:absolute; left:0; right:0; bottom:64px; text-align:center; font-family:'NotoBd';
  font-size:34px; color:#8a93a0; opacity:0; }
/* title */
.tpanel { background:radial-gradient(ellipse 90% 80% at 50% 42%, #1a160e 0%, #0b0a07 70%); }
.glow { position:absolute; left:50%; top:50%; width:1500px; height:700px; margin:-350px 0 0 -750px;
  background:radial-gradient(ellipse, rgba(217,164,65,.14), rgba(217,164,65,0) 65%); opacity:0; }
.ttl-wrap { position:absolute; inset:0; }
.ttl-top { position:absolute; left:0; right:0; top:286px; text-align:center; font-size:58px;
  color:rgba(242,241,236,.92); letter-spacing:.06em; opacity:0; }
.ttl-main, .ttl-ghost { position:absolute; left:0; right:0; top:380px; text-align:center;
  font-size:160px; letter-spacing:.02em; font-family:'SerifJP'; font-weight:900; }
.ttl-main { opacity:0; text-shadow:0 10px 60px rgba(0,0,0,.8); }
.ttl-ghost { opacity:0; }
.ttl-r { color:#d9a441; transform:translateX(-9px); } .ttl-r em { color:#d9a441; }
.ttl-b { color:#46e0d4; transform:translateX(9px); } .ttl-b em { color:#46e0d4; }
.ttl-sub { position:absolute; left:0; right:0; top:648px; text-align:center; font-family:'NotoBd';
  font-size:40px; color:#e8c37a; letter-spacing:.1em; opacity:0; }
/* cards */
.chead { position:absolute; left:0; right:0; top:84px; text-align:center; font-family:'NotoBd';
  font-size:36px; letter-spacing:.5em; color:#8a93a0; opacity:0; }
.cgrid { position:absolute; left:90px; right:90px; top:190px; bottom:120px; display:flex; gap:34px; }
.card { position:relative; flex:1; border-radius:14px; overflow:hidden; background:#1c1812; opacity:0; }
.card img { position:absolute; width:auto; height:100%; left:50%; transform:translateX(-50%); filter:saturate(.85); }
.cshade { position:absolute; inset:0; background:linear-gradient(180deg, rgba(2,3,5,.08) 35%, rgba(2,3,5,.88) 88%); }
.cnum { position:absolute; left:26px; top:18px; font-size:54px; color:#d9a441; }
.clab { position:absolute; left:0; right:0; bottom:34px; text-align:center; font-size:46px;
  text-shadow:0 3px 14px rgba(0,0,0,.9); }
/* chapter */
.chno { position:absolute; left:150px; top:330px; font-size:56px; color:#d9a441; letter-spacing:.4em; opacity:0; }
.chttl { position:absolute; left:144px; top:404px; font-size:132px; letter-spacing:.03em;
  font-family:'SerifJP'; font-weight:900;
  text-shadow:0 8px 50px rgba(0,0,0,.85); opacity:0; }
.chsub { position:absolute; left:152px; top:624px; font-family:'NotoBd'; font-size:40px;
  color:#e8c37a; text-shadow:0 2px 14px rgba(0,0,0,.95); opacity:0; }
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
<div id="tbk"></div>
<div id="twipe"></div>
<div id="flash"></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>
window.__timelines = window.__timelines || {{}};
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
