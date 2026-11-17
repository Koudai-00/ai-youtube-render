# -*- coding: utf-8 -*-
"""japan03 OP「深夜放送」: index.html ビルダ(窓分割対応)
構成: コールドオープン肉声(zhen) → profile → theme(ON AIR+題字ネオン) → TRACK01扉
HF_WIN_START / HF_WIN_END env で窓ビルド。
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "japan03"
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
    TWEENS.append(js.replace("%T%", str(round(t, 3))))


def fromto(t, sel, frm, to, dur, ease):
    tw(t, f'tl.fromTo("{sel}", {{{frm}}}, {{{to}, duration: {dur}, ease: "{ease}", immediateRender: false}}, %T%);')


def setv(t, sel, vars_):
    tw(t, f'tl.set("{sel}", {{{vars_}}}, %T%);')


def tline_cut(t):
    setv(t - 0.02, "#tline", "opacity: 1, y: 0")
    tw(t - 0.02, 'tl.to("#tline", {y: 1088, duration: 0.3, ease: "power2.inOut"}, %T%);')
    tw(t + 0.26, 'tl.to("#tline", {opacity: 0, duration: 0.15}, %T%);')


LOGO = '<div class="logo"><span class="dot"></span>深夜の日本論<span class="oa">ON AIR</span></div>'

# ============================================================ cold open: qzhen
qi = Q["qzhen"]
t0 = qi["beat_start"]
t1 = t0 + qi["dur"]
el_video("qzv", t0, t1, qi["clip"], qi["media_start"], cls="framed")
el_div("qzo", t0, t1, "qov", (
    '<div class="lbT"><span class="rec"></span><div class="qtag">日本を愛する中国人クリエイター</div>'
    '<div class="credit">引用: Zhen Into Chinese</div></div>'
    '<div class="lbB"></div>'
    '<div class="qcap" id="qzc1">「日本が大好きな <em>中国人</em>として」</div>'
    '<div class="qcap" id="qzc2">「2つの国の<em>違い</em>を 話したい」</div>'))
fromto(t0 + 0.05, "#qzv", "scale: 1.05", "scale: 1", 2.2, "power2.out")
sp = t0 + qi["lead"]
fromto(sp + 0.4, "#qzc1", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
setv(sp + 4.9, "#qzc1", "opacity: 0")
fromto(sp + 5.0, "#qzc2", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")

# ============================================================ profile beat
t0, t1 = B["profile"]
el_video("prv", t0, t1, "profile.mp4", 0.0, cls="framed")
el_div("pro", t0, t1, "qov", (
    '<div class="lbT"><span class="rec"></span><div class="qtag">日本在住歴あり — 現在は欧州在住</div>'
    '<div class="credit">引用: Zhen Into Chinese</div></div>'
    '<div class="lbB"></div>'
    '<div class="qcap" id="prc">彼女が語る 日中の「<em>決定的な差</em>」</div>'))
tline_cut(t0)
fromto(t0 + 0.05, "#prv", "scale: 1.04", "scale: 1", 2.0, "power2.out")
fromto(N["n01"]["start"] + 0.2, "#prc", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")

# ============================================================ theme beat (ON AIR + 題字)
t0, t1 = B["theme"]
el_div("thp", t0, t1, "panel", (
    '<div class="oawrap" id="oaw"><span class="oadot" id="oad"></span>ON AIR</div>'
    '<div class="pgname" id="pgn">深夜の日本論</div>'
    '<div class="thlabel" id="thl">本日のトークテーマ</div>'
    '<div class="thtitle" id="tht">「中国とは、<em>違いすぎた</em>」</div>'
    '<div class="thsub" id="ths">— 909万人が気づいた、日中の決定的な差</div>'))
tline_cut(t0)
fromto(t0 + 0.2, "#oaw", "opacity: 0", "opacity: 1", 0.4, "power2.out")
fromto(t0 + 0.25, "#oad", "scale: 0", "scale: 1", 0.3, "back.out(2)")
fromto(t0 + 0.55, "#pgn", "y: -20, opacity: 0", "y: 0, opacity: 1", 0.5, "power3.out")
n4 = N["n04"]["start"]
fromto(n4 - 0.3, "#thl", "opacity: 0, letterSpacing: '0.7em'", "opacity: 1, letterSpacing: '0.34em'", 0.6, "power2.out")
# 題字: ネオン点灯 (2度ちらつき→安定)
tt = n4 + 1.9
setv(tt - 0.02, "#tht", "opacity: 0")
tw(tt, 'tl.set("#tht", {opacity: 1}, %T%);')
tw(tt + 0.07, 'tl.set("#tht", {opacity: 0.25}, %T%);')
tw(tt + 0.15, 'tl.set("#tht", {opacity: 1}, %T%);')
tw(tt + 0.24, 'tl.set("#tht", {opacity: 0.4}, %T%);')
tw(tt + 0.33, 'tl.to("#tht", {opacity: 1, duration: 0.2}, %T%);')
fromto(tt + 0.33, "#tht", "scale: 1.02", "scale: 1", 0.8, "power2.out")
fromto(tt + 1.3, "#ths", "opacity: 0", "opacity: 1", 0.5, "power2.out")

# ============================================================ ch1 扉 (TRACK 01)
t0, t1 = B["ch1"]
el_video("ch1v", t0, t1, "ch1.mp4", 0.0)
el_div("ch1o", t0, t1, "qov", (
    '<div class="cdscrim"></div>'
    '<div class="creditD">引用: Nicaboo</div>' + LOGO +
    '<div class="cno" id="cn1">TRACK 01</div>'
    '<div class="cline" id="cl1"></div>'
    '<div class="ctitle" id="ct1">909万人の、謎</div>'
    '<div class="csub" id="cs1">— なぜ彼らは、隣の国へ行くのか</div>'))
tline_cut(t0)
fromto(t0 + 0.2, "#cn1", "x: -60, opacity: 0", "x: 0, opacity: 1", 0.55, "power3.out")
fromto(t0 + 0.4, "#cl1", "scaleX: 0", "scaleX: 1", 0.5, "power2.inOut")
fromto(t0 + 0.55, "#ct1", 'opacity: 0, y: 26, filter: "blur(8px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.65, "power2.out")
fromto(t0 + 1.25, "#cs1", "opacity: 0", "opacity: 1", 0.45, "power2.out")
tw(COMP - 1.05, 'tl.to("#stage", {opacity: 0, duration: 0.9, ease: "power1.in"}, %T%);')

# ============================================================ assemble html
CSS = """
@font-face { font-family:'NotoB'; src:url('assets/fonts/NotoSansJP-Black.otf') format('opentype'); }
@font-face { font-family:'NotoBd'; src:url('assets/fonts/NotoSansJP-Bold.otf') format('opentype'); }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { background:#000; }
#root { position:relative; width:1920px; height:1080px; overflow:hidden;
  background:#070b16; font-family:'NotoB',sans-serif; color:#f2f4f8; }
#stage { position:absolute; inset:0; }
.clip { position:absolute; inset:0; width:100%; height:100%; }
video.bgv { object-fit:cover; transform:translateZ(0); backface-visibility:hidden; }
video.framed { top:80px; height:810px; }
em { font-style:normal; color:#4fd8eb; }
#vig { position:absolute; inset:0; z-index:41; pointer-events:none;
  background:radial-gradient(ellipse 120% 110% at 50% 46%, rgba(0,0,0,0) 58%, rgba(2,4,10,.5) 100%); }
#tline { position:absolute; left:0; right:0; top:-4px; height:4px; z-index:60; opacity:0;
  background:linear-gradient(90deg, rgba(79,216,235,0), #eafcff 30%, #eafcff 70%, rgba(79,216,235,0));
  box-shadow:0 0 26px 6px rgba(79,216,235,.8); pointer-events:none; }
.panel { z-index:10;
  background:radial-gradient(ellipse 130% 100% at 50% 34%, #15213f 0%, #0d1529 56%, #070b16 100%); }
.logo { position:absolute; left:52px; top:42px; z-index:4; font-family:'NotoB'; font-size:30px;
  letter-spacing:.14em; color:#dfe7f2; display:flex; align-items:center; gap:16px; }
.logo .dot { width:16px; height:16px; border-radius:50%; background:#ff4a3c;
  box-shadow:0 0 14px 3px rgba(255,74,60,.75); }
.logo .oa { font-size:19px; letter-spacing:.3em; color:#8e9cb8; border:2px solid #8e9cb8;
  padding:4px 10px 4px 13px; border-radius:4px; margin-left:6px; }
.qov { z-index:10; }
.lbT { position:absolute; left:0; right:0; top:0; height:80px; background:#0a101f;
  border-bottom:2px solid rgba(79,216,235,.35); box-shadow:0 4px 22px rgba(0,0,0,.6); }
.lbB { position:absolute; left:0; right:0; bottom:0; height:190px; background:#0a101f;
  border-top:2px solid rgba(79,216,235,.35); box-shadow:0 -4px 22px rgba(0,0,0,.6); }
.rec { position:absolute; left:46px; top:50%; width:16px; height:16px; margin-top:-8px;
  border-radius:50%; background:#ff4a3c; box-shadow:0 0 12px 3px rgba(255,74,60,.7); }
.qtag { position:absolute; left:84px; top:50%; transform:translateY(-50%);
  font-family:'NotoB'; font-size:29px; color:#f2f4f8; letter-spacing:.08em; }
.credit { position:absolute; right:46px; top:50%; transform:translateY(-50%);
  font-family:'NotoBd'; font-size:24px; color:#8e9cb8; }
.qcap { position:absolute; left:60px; right:60px; bottom:52px; text-align:center; font-size:56px;
  font-family:'NotoB'; color:#f2f4f8; letter-spacing:.02em; opacity:0; z-index:11;
  text-shadow:0 2px 14px rgba(0,0,0,.6); }
.creditD { position:absolute; top:26px; right:56px; font-family:'NotoBd'; font-size:24px;
  color:rgba(242,244,248,.92); background:rgba(5,8,16,.55); padding:7px 16px; z-index:5; }
/* theme */
.oawrap { position:absolute; left:50%; top:150px; transform:translateX(-50%);
  font-family:'NotoB'; font-size:44px; letter-spacing:.46em; color:#ff8a7d; opacity:0;
  display:flex; align-items:center; gap:22px; text-shadow:0 0 24px rgba(255,74,60,.5); }
.oadot { width:26px; height:26px; border-radius:50%; background:#ff4a3c;
  box-shadow:0 0 22px 6px rgba(255,74,60,.8); }
.pgname { position:absolute; left:0; right:0; top:236px; text-align:center; font-family:'NotoB';
  font-size:54px; letter-spacing:.24em; color:#8e9cb8; opacity:0; }
.thlabel { position:absolute; left:0; right:0; top:396px; text-align:center; font-family:'NotoB';
  font-size:38px; letter-spacing:.34em; color:#d9b96a; opacity:0; }
.thtitle { position:absolute; left:0; right:0; top:470px; text-align:center; font-family:'NotoB';
  font-size:118px; color:#f2f4f8; opacity:0; letter-spacing:.02em;
  text-shadow:0 0 50px rgba(79,216,235,.45), 0 0 110px rgba(79,216,235,.25); }
.thsub { position:absolute; left:0; right:0; top:680px; text-align:center; font-family:'NotoBd';
  font-size:38px; color:#aeb9cf; opacity:0; }
/* ch1 card */
.cdscrim { position:absolute; inset:0;
  background:linear-gradient(0deg, rgba(5,8,16,.82) 0%, rgba(5,8,16,.45) 45%, rgba(5,8,16,.25) 100%); }
.cno { position:absolute; left:150px; top:340px; font-family:'NotoB'; font-size:54px;
  letter-spacing:.42em; color:#4fd8eb; opacity:0; text-shadow:0 0 24px rgba(79,216,235,.5); }
.cline { position:absolute; left:154px; top:428px; width:560px; height:4px; transform-origin:left;
  transform:scaleX(0); background:linear-gradient(90deg, #4fd8eb, rgba(79,216,235,0)); }
.ctitle { position:absolute; left:146px; top:470px; font-family:'NotoB'; font-size:96px;
  color:#f2f4f8; opacity:0; letter-spacing:.03em; text-shadow:0 4px 30px rgba(0,0,0,.7); }
.csub { position:absolute; left:152px; top:620px; font-family:'NotoBd'; font-size:38px;
  color:#aeb9cf; opacity:0; }
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
<div id="tline"></div>
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
