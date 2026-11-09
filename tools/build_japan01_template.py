# -*- coding: utf-8 -*-
"""japan01 長尺・冒頭1分: index.html ビルダ(窓分割対応)
HF_WIN_START / HF_WIN_END env で窓ビルド。全tweenは fromTo(immediateRender:false) 絶対時刻
→ 窓外tweenは出力されず、要素はCSSの最終状態で表示される(=cont対応)。
"""
import json
import os
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "japan01"
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
    """フラッシュ+スライス+ジッター 0.2秒バースト"""
    for i, (gid,) in enumerate([("#gl1",), ("#gl2",), ("#gl3",)]):
        y1 = rng.randint(5, 85)
        y2 = rng.randint(5, 85)
        h = rng.randint(14, 60)
        dx1 = rng.randint(-70, 70)
        dx2 = rng.randint(-70, 70)
        setv(t + 0.0, gid, f'opacity: {0.75*strength:.2f}, top: "{y1}%", height: {h}, x: {dx1}')
        setv(t + 0.067, gid, f'top: "{y2}%", height: {rng.randint(10, 44)}, x: {dx2}')
        setv(t + 0.167, gid, 'opacity: 0, x: 0')
    setv(t, "#flash", f'opacity: {0.85*strength:.2f}')
    setv(t + 0.067, "#flash", f'opacity: {0.25*strength:.2f}')
    setv(t + 0.133, "#flash", 'opacity: 0')
    jx = int(14 * strength)
    setv(t, "#stage", f'x: {-jx}')
    setv(t + 0.067, "#stage", f'x: {jx}')
    setv(t + 0.133, "#stage", 'x: 0')


# ============================================================ quote beats
QCAP = {
    "qb": {"credit": "引用: Chopsticks and Trains",
           "cap": '一歩間違えば <em>最悪の事態</em>になるぞ', "sub": None},
    "qd": {"credit": "引用: Addy",
           "cap": '芸者は撮影の<em>"小道具"</em>じゃない', "sub": None},
    "qc": {"credit": "引用: Japanese Immersion Lab",
           "cap": '<em>出て行け。国へ帰れ。</em>', "sub": "— 日本好きの外国人が、店で投げつけられた言葉"},
    "qa": {"credit": "引用: Axel in Japan", "cap": None, "sub": None},
}

for q in ["qb", "qd", "qc", "qa"]:
    qi = Q[q]
    t0 = qi["beat_start"]
    t1 = t0 + qi["dur"]
    el_video(f"{q}v", t0, t1, qi["clip"], qi["media_start"])
    c = QCAP[q]
    if q == "qa":
        inner = ('<div class="qscrim"></div>'
                 f'<div class="credit">{c["credit"]}</div>'
                 '<div class="qcap" id="qa-c1">君らは<em>2週間</em>で帰る</div>'
                 '<div class="qcap qcap2" id="qa-c2"><em>汚名</em>を背負うのは 残る俺たちだ</div>')
    else:
        sub = f'<div class="qsub" id="{q}-s">{c["sub"]}</div>' if c["sub"] else ""
        inner = ('<div class="qscrim"></div>'
                 f'<div class="credit">{c["credit"]}</div>'
                 f'<div class="qcap" id="{q}-c">{c["cap"]}</div>' + sub)
    el_div(f"{q}o", t0, t1, "qov", inner)

# caption entrances
fromto(0.95, "#qb-c", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
fromto(5.05, "#qd-c", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
fromto(9.75, "#qc-c", "scale: 1.18, opacity: 0", "scale: 1, opacity: 1", 0.28, "power4.out")
fromto(10.6, "#qc-s", "opacity: 0", "opacity: 1", 0.4, "power2.out")
qa0 = Q["qa"]["beat_start"]
fromto(qa0 + 0.45, "#qa-c1", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
fromto(qa0 + 2.35, "#qa-c2", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")

# boundary glitches
glitch(B["qb"][0], 0.9)
glitch(B["qd"][0], 1.0)
glitch(B["qc"][0], 1.0)
glitch(B["n01"][0], 0.8)
glitch(B["qa"][0], 1.0)

# ============================================================ n01 statement over dance
t0, t1 = B["n01"]
el_video("n01v", t0, t1, "dance.mp4", 0.0)
el_div("n01o", t0, t1, "qov", (
    '<div class="qscrim"></div>'
    '<div class="credit">引用: Chopsticks and Trains</div>'
    '<div class="stm" id="stm1">日本を愛する外国人が</div>'
    '<div class="stm stm2" id="stm2"><em>"同じ外国人"</em>に怒っている<div class="uline" id="ul1"></div></div>'))
fromto(N["n01"]["start"] + 0.1, "#stm1", "y: 24, opacity: 0", "y: 0, opacity: 1", 0.35, "power3.out")
fromto(N["n01"]["start"] + 1.6, "#stm2", "y: 24, opacity: 0", "y: 0, opacity: 1", 0.35, "power3.out")
fromto(N["n01"]["start"] + 3.3, "#ul1", "scaleX: 0", "scaleX: 1", 0.45, "power2.inOut")

# ============================================================ n02 axel profile
t0, t1 = B["n02"]
el_video("n02v", t0, t1, "axel.mp4", 0.0)
chips = "".join(f'<div class="chip" id="chip{i}">{c}</div>'
                for i, c in enumerate(["在住 8年", "2児の父", "会社経営"], 1))
el_div("n02o", t0, t1, "qov", (
    '<div class="qscrim"></div>'
    '<div class="credit">引用: Axel in Japan</div>'
    '<div class="lt" id="lt1"><div class="ltbar"></div>'
    '<div class="ltbody"><div class="ltname">日本在住8年の外国人男性</div>'
    '<div class="ltrole">Axel in Japan — 怒りの告白</div></div></div>'
    f'<div class="chips">{chips}</div>'))
glitch(t0, 0.7)
fromto(t0 + 0.4, "#lt1", "x: -70, opacity: 0", "x: 0, opacity: 1", 0.45, "power3.out")
for i, dt in enumerate([1.9, 2.7, 3.5], 1):
    fromto(t0 + dt, f"#chip{i}", "y: 18, opacity: 0, scale: 0.9", "y: 0, opacity: 1, scale: 1", 0.3, "back.out(2)")

# ============================================================ info panel
t0, t1 = B["info"]
icon_cam = ('<svg viewBox="0 0 48 48"><path d="M8 14h8l4-5h8l4 5h8a3 3 0 0 1 3 3v20a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V17a3 3 0 0 1 3-3z" '
            'fill="none" stroke="currentColor" stroke-width="3"/><circle cx="24" cy="27" r="7" fill="none" stroke="currentColor" stroke-width="3"/>'
            '<line x1="6" y1="42" x2="42" y2="6" stroke="#e8322e" stroke-width="4"/></svg>')
icon_fuji = ('<svg viewBox="0 0 48 48"><path d="M4 40 L20 12 L24 18 L28 10 L44 40 Z" fill="none" stroke="currentColor" stroke-width="3"/>'
             '<path d="M18 16 L21 20 L25 14 L29 19" fill="none" stroke="currentColor" stroke-width="2.4"/></svg>')
icon_train = ('<svg viewBox="0 0 48 48"><rect x="10" y="6" width="28" height="30" rx="5" fill="none" stroke="currentColor" stroke-width="3"/>'
              '<line x1="10" y1="22" x2="38" y2="22" stroke="currentColor" stroke-width="3"/>'
              '<circle cx="17" cy="29" r="2.6" fill="currentColor"/><circle cx="31" cy="29" r="2.6" fill="currentColor"/>'
              '<line x1="16" y1="42" x2="12" y2="36" stroke="currentColor" stroke-width="3"/>'
              '<line x1="32" y1="42" x2="36" y2="36" stroke="currentColor" stroke-width="3"/></svg>')
items = [
    ("i1", icon_cam, "祇園", "私道での撮影・立ち入りが禁止に"),
    ("i2", icon_fuji, "富士山", "ローソン前に「目隠し幕」設置"),
    ("i3", icon_train, "鉄道会社", "車内ダンスに法的措置を検討へ"),
]
rows = "".join(
    f'<div class="irow" id="{iid}"><div class="iic">{ic}</div>'
    f'<div class="itx"><div class="iplace">{pl}</div><div class="idesc">{ds}</div></div></div>'
    for iid, ic, pl, ds in items)
el_div("infop", t0, t1, "panel", (
    '<div class="phead" id="ph1">怒るのは、<br>日本人だけじゃない<div class="phline" id="phl"></div></div>'
    f'<div class="irows">{rows}<div class="tline" id="tl1"></div></div>'))
fromto(t0 + 0.35, "#ph1", "x: -50, opacity: 0", "x: 0, opacity: 1", 0.5, "power3.out")
fromto(t0 + 0.8, "#phl", "scaleX: 0", "scaleX: 1", 0.5, "power2.inOut")
fromto(t0 + 0.6, "#tl1", "scaleY: 0", "scaleY: 1", 8.0, "none")
n4 = N["n04"]["start"]
for iid, dt in [("i1", 0.15), ("i2", 1.75), ("i3", 3.5)]:
    fromto(n4 + dt, f"#{iid}", "x: 70, opacity: 0", "x: 0, opacity: 1", 0.45, "power3.out")
glitch(t0, 0.6)

# ============================================================ diagram
t0, t1 = B["diagram"]
outer = ""
pos = [(13, 22), (78, 16), (12, 68), (76, 72)]
for i, (x, y) in enumerate(pos, 1):
    outer += (f'<div class="onode" id="on{i}" style="left:{x}%;top:{y}%">'
              '<svg viewBox="0 0 36 36"><circle cx="18" cy="12" r="6.5" fill="currentColor"/>'
              '<path d="M5 33 a13 11 0 0 1 26 0z" fill="currentColor"/></svg></div>')
arrows = "".join(
    f'<div class="arrow" id="ar{i}" style="left:{ax}%;top:{ay}%;transform:rotate({deg}deg)"></div>'
    for i, (ax, ay, deg) in enumerate([(27, 33, 35), (63, 29, 145), (27, 63, -35), (62, 66, -145)], 1))
el_div("diag", t0, t1, "panel", (
    '<div class="dhead" id="dh1">怒りの矛先は <em>"同胞"</em>へ</div>'
    f'{outer}{arrows}'
    '<div class="cnode" id="cn1"><span>迷惑<br>外国人</span></div>'
    '<div class="dnote" id="dn1">日本を愛する外国人たち</div>'))
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
el_div("titlebeat", t0, t1, "panel tpanel", (
    '<div class="glow" id="tglow"></div>'
    '<div class="ttl-wrap">'
    '<div class="ttl-top" id="tt1">なぜ、日本を愛する外国人は</div>'
    '<div class="ttl-ghost ttl-r" id="ttr"><em>"同胞"</em>に怒るのか</div>'
    '<div class="ttl-ghost ttl-b" id="ttb"><em>"同胞"</em>に怒るのか</div>'
    '<div class="ttl-main" id="ttm"><em>"同胞"</em>に怒るのか</div>'
    '<div class="ttl-sub" id="tts">4人の外国人の告白から 徹底深掘り</div>'
    '</div>'))
glitch(t0, 1.0)
fromto(t0 + 0.2, "#tt1", "y: -26, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
fromto(t0 + 0.42, "#ttm", "scale: 1.45, opacity: 0", "scale: 1, opacity: 1", 0.38, "expo.out")
setv(t0 + 0.45, "#ttr", "opacity: 0.55")
setv(t0 + 0.45, "#ttb", "opacity: 0.55")
setv(t0 + 0.75, "#ttr", "opacity: 0")
setv(t0 + 0.75, "#ttb", "opacity: 0")
fromto(t0 + 0.55, "#tglow", "opacity: 0", "opacity: 1", 1.2, "power2.out")
fromto(t0 + 1.5, "#tts", "y: 20, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
# 中間の再グリッチ(ゴーストを一瞬)
setv(t0 + 3.8, "#ttr", "opacity: 0.45, x: -10")
setv(t0 + 3.8, "#ttb", "opacity: 0.45, x: 10")
setv(t0 + 3.93, "#ttr", "opacity: 0, x: -6")
setv(t0 + 3.93, "#ttb", "opacity: 0, x: 6")
glitch(t0 + 3.8, 0.5)

# ============================================================ creator cards
t0, t1 = B["cards"]
cards = [
    ("c1", "card15.jpg", "01", "汚名を背負う者"),
    ("c2", "card17.jpg", "02", "警告する者"),
    ("c3", "card18.jpg", "03", "差別された者"),
    ("c4", "card19.jpg", "04", "絶望する者"),
]
chtml = "".join(
    f'<div class="card" id="{cid}"><img src="assets/img/{img}" alt="">'
    f'<div class="cshade"></div><div class="cnum">{num}</div><div class="clab">{lab}</div></div>'
    for cid, img, num, lab in cards)
el_div("cardbeat", t0, t1, "panel", f'<div class="chead" id="chd">4人の告白</div><div class="cgrid">{chtml}</div>')
glitch(t0, 0.7)
fromto(t0 + 0.2, "#chd", "opacity: 0", "opacity: 1", 0.4, "power2.out")
n7 = N["n07"]["start"]
for cid, dt in [("c1", 0.05), ("c2", 1.5), ("c3", 2.9), ("c4", 4.35)]:
    fromto(n7 + dt, f"#{cid}", "y: 90, opacity: 0, rotation: 1.5", "y: 0, opacity: 1, rotation: 0", 0.5, "power3.out")

# ============================================================ chapter 1
t0, t1 = B["ch1"]
el_video("ch1v", t0, t1, "intro15.mp4", 0.5)
el_div("ch1o", t0, t1, "qov", (
    '<div class="ch1scrim"></div>'
    '<div class="credit">引用: Axel in Japan</div>'
    '<div class="chno" id="chno">第 1 章</div>'
    '<div class="chttl" id="chttl">俺たちは、残る</div>'
    '<div class="chsub" id="chsub">— 在住8年、2児の父の告白</div>'))
glitch(t0, 1.0)
fromto(t0 + 0.25, "#chno", "x: -40, opacity: 0", "x: 0, opacity: 1", 0.4, "power3.out")
fromto(t0 + 0.5, "#chttl", "scale: 1.3, opacity: 0", "scale: 1, opacity: 1", 0.45, "expo.out")
fromto(t0 + 1.1, "#chsub", "opacity: 0", "opacity: 1", 0.45, "power2.out")
tw(COMP - 1.05, 'tl.to("#stage", {opacity: 0, duration: 0.9, ease: "power1.in"}, %T%);')

# ============================================================ assemble html
CSS = """
@font-face { font-family:'NotoB'; src:url('assets/fonts/NotoSansJP-Black.otf') format('opentype'); }
@font-face { font-family:'NotoBd'; src:url('assets/fonts/NotoSansJP-Bold.otf') format('opentype'); }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { background:#000; }
#root { position:relative; width:1920px; height:1080px; overflow:hidden;
  background:#07080b; font-family:'NotoB','NotoBd',sans-serif; color:#f2f1ec; }
#stage { position:absolute; inset:0; }
.clip { position:absolute; inset:0; width:100%; height:100%; }
video.bgv { object-fit:cover; transform:translateZ(0); backface-visibility:hidden; }
em { font-style:normal; color:#e8322e; }
/* overlays */
#scan { position:absolute; inset:0; z-index:40; pointer-events:none; opacity:.14;
  background:repeating-linear-gradient(0deg, rgba(0,0,0,.55) 0 2px, rgba(0,0,0,0) 2px 5px); }
#vig { position:absolute; inset:0; z-index:41; pointer-events:none;
  background:radial-gradient(ellipse 115% 105% at 50% 46%, rgba(0,0,0,0) 58%, rgba(0,0,0,.52) 100%); }
#flash { position:absolute; inset:0; z-index:60; background:#e9e6df; opacity:0; pointer-events:none; }
.gl { position:absolute; left:-80px; right:-80px; z-index:59; opacity:0; pointer-events:none; }
#gl1 { background:rgba(232,50,46,.55); }
#gl2 { background:rgba(70,224,212,.45); }
#gl3 { background:rgba(242,241,236,.75); }
/* quote overlays */
.qov { z-index:10; }
.qscrim { position:absolute; left:0; right:0; bottom:0; height:460px;
  background:linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(2,3,5,.62) 42%, rgba(2,3,5,.86) 100%); }
.ch1scrim { position:absolute; inset:0;
  background:linear-gradient(180deg, rgba(2,3,5,.35) 0%, rgba(2,3,5,.72) 70%, rgba(2,3,5,.9) 100%); }
.credit { position:absolute; top:34px; right:44px; font-family:'NotoBd'; font-size:26px;
  color:rgba(242,241,236,.85); background:rgba(5,6,9,.55); padding:8px 18px; border-left:4px solid #e8322e; }
.qcap { position:absolute; left:0; right:0; bottom:150px; text-align:center; font-size:84px;
  letter-spacing:.02em; text-shadow:0 4px 26px rgba(0,0,0,.9), 0 0 2px rgba(0,0,0,.9); opacity:0; }
.qcap2 { bottom:56px; }
.qsub { position:absolute; left:0; right:0; bottom:66px; text-align:center; font-family:'NotoBd';
  font-size:34px; color:rgba(242,241,236,.8); text-shadow:0 2px 12px rgba(0,0,0,.9); opacity:0; }
.stm { position:absolute; left:0; right:0; bottom:236px; text-align:center; font-size:72px;
  text-shadow:0 4px 26px rgba(0,0,0,.92); opacity:0; }
.stm2 { bottom:118px; font-size:92px; }
.uline { position:absolute; left:50%; margin-left:-330px; bottom:-14px; width:660px; height:10px;
  background:#e8322e; transform:scaleX(0); transform-origin:left; }
/* lower third */
.lt { position:absolute; left:70px; bottom:96px; display:flex; opacity:0; }
.ltbar { width:12px; background:#e8322e; }
.ltbody { background:rgba(5,6,9,.78); padding:22px 38px 24px 30px; }
.ltname { font-size:52px; }
.ltrole { font-family:'NotoBd'; font-size:28px; color:#ffb648; margin-top:6px; }
.chips { position:absolute; right:70px; bottom:110px; display:flex; gap:22px; }
.chip { font-size:36px; background:rgba(5,6,9,.72); border:2px solid #e8322e;
  padding:12px 26px; border-radius:999px; opacity:0; }
/* panels */
.panel { z-index:10; background:#0c1016; }
.phead { position:absolute; left:110px; top:50%; transform:translateY(-50%); width:720px;
  font-size:80px; line-height:1.26; opacity:0; }
.phline { width:230px; height:12px; background:#e8322e; margin-top:30px; transform-origin:left; transform:scaleX(0); }
.irows { position:absolute; right:100px; top:50%; transform:translateY(-50%); width:880px; }
.tline { position:absolute; left:-56px; top:14px; bottom:10px; width:6px; background:#2a3140;
  transform-origin:top; transform:scaleY(0); }
.irow { display:flex; align-items:center; gap:36px; margin-bottom:74px; opacity:0; }
.irow:last-child { margin-bottom:0; }
.iic { width:110px; height:110px; flex:none; color:#ffb648; background:#121825;
  border:3px solid #232c3d; border-radius:18px; display:flex; align-items:center; justify-content:center; }
.iic svg { width:64px; height:64px; }
.iplace { font-size:30px; color:#e8322e; font-family:'NotoBd'; letter-spacing:.14em; }
.idesc { font-size:44px; line-height:1.3; margin-top:4px; }
/* diagram */
.dhead { position:absolute; left:0; right:0; top:96px; text-align:center; font-size:86px; opacity:0; }
.cnode { position:absolute; left:50%; top:54%; width:340px; height:340px; margin:-170px 0 0 -170px;
  background:radial-gradient(circle at 50% 42%, #3a1113, #1c0a0c 70%); border:6px solid #e8322e; border-radius:50%;
  display:flex; align-items:center; justify-content:center; text-align:center; font-size:64px; line-height:1.2;
  box-shadow:0 0 90px rgba(232,50,46,.45); opacity:0; }
.onode { position:absolute; width:150px; height:150px; margin:-75px 0 0 -75px; color:#8a93a0;
  background:#121825; border:3px solid #2a3140; border-radius:50%; padding:26px; opacity:0; }
.onode svg { width:100%; height:100%; }
.arrow { position:absolute; width:250px; height:8px; background:linear-gradient(90deg, rgba(138,147,160,0), #e8322e);
  opacity:0; }
.arrow::after { content:''; position:absolute; right:-4px; top:-10px; border:14px solid transparent;
  border-left:18px solid #e8322e; }
.dnote { position:absolute; left:0; right:0; bottom:64px; text-align:center; font-family:'NotoBd';
  font-size:34px; color:#8a93a0; opacity:0; }
/* title */
.tpanel { background:radial-gradient(ellipse 90% 80% at 50% 42%, #10151d 0%, #07080b 70%); }
.glow { position:absolute; left:50%; top:50%; width:1500px; height:700px; margin:-350px 0 0 -750px;
  background:radial-gradient(ellipse, rgba(232,50,46,.17), rgba(232,50,46,0) 65%); opacity:0; }
.ttl-wrap { position:absolute; inset:0; }
.ttl-top { position:absolute; left:0; right:0; top:286px; text-align:center; font-size:58px;
  color:rgba(242,241,236,.92); letter-spacing:.06em; opacity:0; }
.ttl-main, .ttl-ghost { position:absolute; left:0; right:0; top:380px; text-align:center;
  font-size:170px; letter-spacing:.02em; }
.ttl-main { opacity:0; text-shadow:0 10px 60px rgba(0,0,0,.8); }
.ttl-ghost { opacity:0; }
.ttl-r { color:#e8322e; transform:translateX(-9px); } .ttl-r em { color:#e8322e; }
.ttl-b { color:#46e0d4; transform:translateX(9px); } .ttl-b em { color:#46e0d4; }
.ttl-sub { position:absolute; left:0; right:0; top:648px; text-align:center; font-family:'NotoBd';
  font-size:40px; color:#ffb648; letter-spacing:.1em; opacity:0; }
/* cards */
.chead { position:absolute; left:0; right:0; top:84px; text-align:center; font-family:'NotoBd';
  font-size:36px; letter-spacing:.5em; color:#8a93a0; opacity:0; }
.cgrid { position:absolute; left:90px; right:90px; top:190px; bottom:120px; display:flex; gap:34px; }
.card { position:relative; flex:1; border-radius:14px; overflow:hidden; background:#121825; opacity:0; }
.card img { position:absolute; width:auto; height:100%; left:50%; transform:translateX(-50%); filter:saturate(.85); }
.cshade { position:absolute; inset:0; background:linear-gradient(180deg, rgba(2,3,5,.08) 35%, rgba(2,3,5,.88) 88%); }
.cnum { position:absolute; left:26px; top:18px; font-size:54px; color:#e8322e; }
.clab { position:absolute; left:0; right:0; bottom:34px; text-align:center; font-size:46px;
  text-shadow:0 3px 14px rgba(0,0,0,.9); }
/* chapter */
.chno { position:absolute; left:150px; top:330px; font-size:56px; color:#e8322e; letter-spacing:.4em; opacity:0; }
.chttl { position:absolute; left:144px; top:404px; font-size:150px; letter-spacing:.04em;
  text-shadow:0 8px 50px rgba(0,0,0,.85); opacity:0; }
.chsub { position:absolute; left:152px; top:624px; font-family:'NotoBd'; font-size:40px;
  color:#ffb648; text-shadow:0 2px 14px rgba(0,0,0,.95); opacity:0; }
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
<div id="scan"></div>
<div id="vig"></div>
<div id="gl1" class="gl"></div>
<div id="gl2" class="gl"></div>
<div id="gl3" class="gl"></div>
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
