# -*- coding: utf-8 -*-
"""japan02 OP v2「紀行手記」: index.html ビルダ(窓分割対応)
構成: コールドオープン肉声(kalani泣いた) → 人物ひと言 → 和紙の数字 → 縦書き題字 → 壱の扉
HF_WIN_START / HF_WIN_END env で窓ビルド。
"""
import json
import os
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


def softcut(t, strength=1.0):
    setv(t, "#flash", f'opacity: {0.46*strength:.2f}')
    tw(t + 0.04, f'tl.to("#flash", {{opacity: 0, duration: {0.55+0.15*strength:.2f}, ease: "power2.out"}}, %T%);')


def inkc(t):
    setv(t - 0.30, "#inkc", "opacity: 1, scale: 0")
    tw(t - 0.30, 'tl.to("#inkc", {scale: 3.2, duration: 0.33, ease: "power2.in"}, %T%);')
    tw(t + 0.05, 'tl.to("#inkc", {opacity: 0, duration: 0.55, ease: "power2.out"}, %T%);')
    setv(t + 0.62, "#inkc", "scale: 0")


RAKKAN = '<div class="rk">日本<br>紀行</div>'

# ============================================================ cold open: qkalani
qi = Q["qkalani"]
t0 = qi["beat_start"]
t1 = t0 + qi["dur"]
el_video("qkv", t0, t1, qi["clip"], qi["media_start"], cls="framed")
el_div("qko", t0, t1, "qov", (
    '<div class="lbT"><div class="qtag">初めてのひとり旅 — 旅の最終日</div>'
    '<div class="credit">引用: Kalani James Lenehan</div></div>'
    '<div class="lbB"></div>'
    '<div class="qcap" id="qkc1">美しすぎて 何度も<em>泣いた</em></div>'
    '<div class="qcap" id="qkc2">人生で<em>最高</em>の旅だった</div>'))
fromto(t0 + 0.05, "#qkv", "scale: 1.05", "scale: 1", 2.2, "power2.out")
sp = t0 + qi["lead"]
fromto(sp + 0.5, "#qkc1", "y: 20, opacity: 0", "y: 0, opacity: 1", 0.35, "power3.out")
setv(sp + 3.2, "#qkc1", "opacity: 0")
fromto(sp + 3.3, "#qkc2", "y: 20, opacity: 0", "y: 0, opacity: 1", 0.35, "power3.out")

# ============================================================ profile beat
t0, t1 = B["profile"]
el_video("prv", t0, t1, "profile.mp4", 0.0, cls="framed")
el_div("pro", t0, t1, "qov", (
    '<div class="lbT"><div class="qtag">オーストラリアから来た 20代</div>'
    '<div class="credit">引用: Kalani James Lenehan</div></div>'
    '<div class="lbB"></div>'
    '<div class="qcap" id="prc">無計画の<em>ひとり旅</em>が 彼を変えた</div>'))
softcut(t0, 0.8)
fromto(t0 + 0.05, "#prv", "scale: 1.04", "scale: 1", 2.0, "power2.out")
fromto(N["n01"]["start"] + 0.2, "#prc", "y: 20, opacity: 0", "y: 0, opacity: 1", 0.35, "power3.out")

# ============================================================ stat beat (和紙の数字)
t0, t1 = B["stat"]
el_div("statp", t0, t1, "panel", (
    '<div class="sthead" id="sth">いま 世界中が<br>日本へ向かっている</div>'
    '<div class="stnum" id="stn">4,268<span>万人</span></div>'
    '<div class="stsub" id="sts">2025年 訪日外客数 — 過去最多</div>'
    '<div class="stvert" id="stv">世界で最も魅力的な国<em>三年連続 一位</em></div>'
    '<div class="cntsrc">出典: JNTO推計 / Condé Nast Traveler 読者投票(米国版 2023-2025)</div>' + RAKKAN))
inkc(t0)
fromto(t0 + 0.3, "#sth", "x: -40, opacity: 0", "x: 0, opacity: 1", 0.55, "power3.out")
n2 = N["n02"]["start"]
fromto(n2 + 1.4, "#stn", 'scale: 1.1, opacity: 0, filter: "blur(10px)"',
       'scale: 1, opacity: 1, filter: "blur(0px)"', 0.8, "power2.out")
fromto(n2 + 2.2, "#sts", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.45, "power2.out")
fromto(n2 + 5.2, "#stv", "opacity: 0, x: 26", "opacity: 1, x: 0", 0.6, "power2.out")

# ============================================================ title beat (縦書き題字)
t0, t1 = B["title"]
el_div("titlep", t0, t1, "panel", (
    '<div class="tglow" id="tgl"></div>'
    '<div class="tatew">'
    '<div class="ttcol ttl2" id="tc1">日本に<em>恋をする</em>のか</div>'
    '<div class="ttcol ttl1" id="tc0">なぜ、世界は</div>'
    '</div>'
    '<div class="tsub" id="tsb">— 4つの旅の記録から、徹底深掘り</div>'
    '<div class="tseal" id="tsl">恋</div>' + RAKKAN))
softcut(t0, 1.0)
fromto(t0 + 0.25, "#tc0", 'opacity: 0, y: 30, filter: "blur(10px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.9, "power2.out")
fromto(t0 + 0.75, "#tc1", 'opacity: 0, y: 30, filter: "blur(10px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.9, "power2.out")
fromto(t0 + 0.6, "#tgl", "opacity: 0", "opacity: 1", 1.4, "power2.out")
fromto(t0 + 1.7, "#tsl", "scale: 1.6, opacity: 0, rotation: -8",
       "scale: 1, opacity: 1, rotation: -8", 0.45, "power3.out")
fromto(t0 + 2.3, "#tsb", "opacity: 0", "opacity: 1", 0.5, "power2.out")

# ============================================================ ch1 扉 (壱)
t0, t1 = B["ch1"]
el_video("ch1v", t0, t1, "ch1.mp4", 0.0)
el_div("ch1o", t0, t1, "qov", (
    '<div class="cdscrim"></div>'
    '<div class="creditD">引用: Abby and Gaz</div>'
    '<div class="chghost" id="chg">壱</div>'
    '<div class="chband" id="chb"><div class="chno2">壱</div>'
    '<div class="chtate" id="cht">初めての日本は、何もかもが違った</div></div>'
    '<div class="chsub" id="chs">— 世界を3年旅した2人の、最初の一日</div>'))
softcut(t0, 1.0)
fromto(t0 + 0.2, "#chb", "x: 240", "x: 0", 0.6, "power3.out")
fromto(t0 + 0.45, "#cht", 'opacity: 0, filter: "blur(8px)"', 'opacity: 1, filter: "blur(0px)"', 0.8, "power2.out")
fromto(t0 + 0.35, "#chg", "scale: 1.3, opacity: 0", "scale: 1, opacity: 0.8", 0.9, "power2.out")
fromto(t0 + 1.2, "#chs", "opacity: 0", "opacity: 1", 0.45, "power2.out")
tw(COMP - 1.05, 'tl.to("#stage", {opacity: 0, duration: 0.9, ease: "power1.in"}, %T%);')

# ============================================================ assemble html
NOISE = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='2' seed='7'"
         " stitchTiles='stitch'/><feColorMatrix type='saturate' values='0'/><feComponentTransfer>"
         "<feFuncA type='linear' slope='0.055'/></feComponentTransfer></filter>"
         "<rect width='260' height='260' filter='url(%23n)'/></svg>\")")

CSS = """
@font-face { font-family:'NotoB'; src:url('assets/fonts/NotoSansJP-Black.otf') format('opentype'); }
@font-face { font-family:'NotoBd'; src:url('assets/fonts/NotoSansJP-Bold.otf') format('opentype'); }
@font-face { font-family:'SerifJP'; src:url('assets/fonts/NotoSerifJP.ttf') format('truetype');
  font-weight:100 900; }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { background:#000; }
#root { position:relative; width:1920px; height:1080px; overflow:hidden;
  background:#171209; font-family:'SerifJP',serif; font-weight:700; color:#231c10; }
#stage { position:absolute; inset:0; }
.clip { position:absolute; inset:0; width:100%; height:100%; }
video.bgv { object-fit:cover; transform:translateZ(0); backface-visibility:hidden; }
video.framed { top:80px; height:810px; }
em { font-style:normal; color:#b3402e; }
#vig { position:absolute; inset:0; z-index:41; pointer-events:none;
  background:radial-gradient(ellipse 118% 108% at 50% 46%, rgba(0,0,0,0) 62%, rgba(26,18,8,.38) 100%); }
#flash { position:absolute; inset:0; z-index:60; background:#efe7d3; opacity:0; pointer-events:none; }
#inkc { position:absolute; left:50%; top:50%; width:1400px; height:1400px; margin:-700px 0 0 -700px;
  border-radius:50%; z-index:58; opacity:0; pointer-events:none; transform:scale(0);
  background:radial-gradient(circle, #241b0d 0%, #241b0d 62%, rgba(36,27,13,0) 72%); }
.panel { z-index:10; background:
  radial-gradient(ellipse 130% 95% at 50% 36%, #f5eeda 0%, #efe6cf 58%, #e4d7b8 100%); }
.panel::before { content:''; position:absolute; inset:0; background-image:__NOISE__;
  pointer-events:none; }
.panel::after { content:''; position:absolute; inset:0; pointer-events:none;
  box-shadow:inset 0 0 180px rgba(120,96,50,.28); }
.rk { position:absolute; right:64px; bottom:56px; z-index:3; writing-mode:vertical-rl;
  font-family:'SerifJP'; font-weight:900; font-size:26px; line-height:1.15; letter-spacing:.12em;
  color:#b3402e; border:3px solid #b3402e; padding:10px 6px; opacity:.75; border-radius:4px; }
.qov { z-index:10; }
.lbT { position:absolute; left:0; right:0; top:0; height:80px; background:#efe7d3;
  box-shadow:0 2px 14px rgba(20,12,2,.35); }
.lbB { position:absolute; left:0; right:0; bottom:0; height:190px; background:#efe7d3;
  box-shadow:0 -2px 14px rgba(20,12,2,.35); }
.lbT::before, .lbB::before { content:''; position:absolute; inset:0; background-image:__NOISE__; }
.qtag { position:absolute; left:46px; top:50%; transform:translateY(-50%);
  font-family:'SerifJP'; font-weight:900; font-size:30px; color:#231c10; letter-spacing:.1em; }
.qtag::before { content:''; display:inline-block; width:12px; height:12px; background:#b3402e;
  border-radius:50%; margin-right:18px; vertical-align:2px; }
.credit { position:absolute; right:46px; top:50%; transform:translateY(-50%);
  font-family:'NotoBd'; font-size:24px; color:#6b6353; }
.qcap { position:absolute; left:60px; right:60px; bottom:52px; text-align:center; font-size:58px;
  font-family:'SerifJP'; font-weight:900; color:#231c10; letter-spacing:.02em; opacity:0; z-index:11; }
/* stat */
.sthead { position:absolute; left:150px; top:200px; font-family:'SerifJP'; font-weight:900;
  font-size:76px; line-height:1.4; color:#231c10; opacity:0; }
.stnum { position:absolute; left:142px; top:470px; font-family:'SerifJP'; font-weight:900;
  font-size:230px; color:#231c10; opacity:0; font-variant-numeric:tabular-nums; }
.stnum span { font-size:90px; color:#b3402e; margin-left:10px; }
.stsub { position:absolute; left:152px; top:772px; font-family:'NotoBd'; font-size:40px;
  color:#8a5a28; opacity:0; }
.stvert { position:absolute; right:250px; top:140px; writing-mode:vertical-rl;
  font-family:'SerifJP'; font-weight:900; font-size:62px; letter-spacing:.18em; line-height:1.6;
  color:#231c10; opacity:0; }
.cntsrc { position:absolute; left:60px; bottom:40px; font-family:'NotoBd'; font-size:23px;
  color:#8a7b57; }
/* title */
.tglow { position:absolute; left:50%; top:50%; width:1500px; height:800px; margin:-400px 0 0 -750px;
  background:radial-gradient(ellipse, rgba(185,138,53,.18), rgba(185,138,53,0) 65%); opacity:0; }
.tatew { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; }
.ttcol { writing-mode:vertical-rl; font-family:'SerifJP'; font-weight:900; color:#231c10;
  margin:0 52px; opacity:0; max-height:1010px; }
.ttl1 { font-size:80px; letter-spacing:.12em; }
.ttl2 { font-size:88px; letter-spacing:.04em; line-height:1.3; }
.tsub { position:absolute; left:0; right:0; bottom:56px; text-align:center; font-family:'NotoBd';
  font-size:38px; color:#8a5a28; opacity:0; }
.tseal { position:absolute; right:170px; bottom:160px; width:150px; height:150px; line-height:150px;
  text-align:center; font-family:'SerifJP'; font-weight:900; font-size:92px; color:#f5eeda;
  background:#b3402e; border-radius:12px; transform:rotate(-8deg); opacity:0;
  box-shadow:0 10px 30px rgba(120,40,20,.35); }
/* 章扉 */
.cdscrim { position:absolute; inset:0;
  background:linear-gradient(90deg, rgba(18,12,4,.18) 55%, rgba(18,12,4,.55) 100%); }
.chghost { position:absolute; left:120px; top:50%; transform:translateY(-54%);
  font-family:'SerifJP'; font-weight:900; font-size:620px; color:#efe7d3; opacity:0;
  text-shadow:0 0 80px rgba(0,0,0,.4); }
.chband { position:absolute; right:110px; top:0; bottom:0; width:250px; background:#efe7d3;
  box-shadow:0 0 44px rgba(10,6,0,.5); display:flex; flex-direction:column; align-items:center;
  padding-top:50px; }
.chband::before { content:''; position:absolute; inset:0; background-image:__NOISE__; }
.chno2 { font-family:'SerifJP'; font-weight:900; font-size:54px; color:#fff;
  background:#b3402e; width:84px; height:84px; line-height:84px; text-align:center;
  border-radius:50%; margin-bottom:34px; }
.chtate { writing-mode:vertical-rl; font-family:'SerifJP'; font-weight:900; font-size:52px;
  letter-spacing:.03em; line-height:1.0; color:#231c10; opacity:0; }
.chsub { position:absolute; left:96px; bottom:96px; font-family:'SerifJP'; font-weight:700;
  font-size:38px; color:#f2eee2; text-shadow:0 2px 16px rgba(0,0,0,.9); opacity:0; }
.creditD { position:absolute; top:26px; right:360px; font-family:'NotoBd'; font-size:24px;
  color:rgba(242,238,226,.9); background:rgba(23,16,6,.5); padding:7px 16px; }
""".replace("__NOISE__", NOISE)

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
<div id="inkc"></div>
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
