# -*- coding: utf-8 -*-
"""japan04 OP「症例ファイル」: index.html ビルダ(窓分割対応)
構成: コールドオープン肉声(dennis) → profile → file(フォルダが開く+タイプ題字) → 第1章扉
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "japan04"
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


def page_cut(t, s=1.0):
    setv(t - 0.02, "#pflash", f'opacity: {0.7*s:.2f}')
    tw(t + 0.02, 'tl.to("#pflash", {opacity: 0, duration: 0.5, ease: "power2.out"}, %T%);')


def spans(eid, txt):
    return "".join(f'<span class="tc" id="{eid}{i}">{c}</span>' for i, c in enumerate(txt))


# ============================================================ cold open: qdennis
qi = Q["qdennis"]
t0 = qi["beat_start"]
t1 = t0 + qi["dur"]
el_video("qdv", t0, t1, qi["clip"], qi["media_start"], cls="framed")
el_div("qdo", t0, t1, "qov", (
    '<div class="lbT"><div class="clipmark"></div><div class="tape">記録映像</div>'
    '<div class="qtag">帰国から2週間 — アメリカ</div>'
    '<div class="credit">引用: Dennis Garcia</div></div>'
    '<div class="lbB"></div>'
    '<div class="qcap" id="qdc1">「帰国して2週間——<em>日本ロス</em>が直撃してる」</div>'))
fromto(t0 + 0.05, "#qdv", "scale: 1.05", "scale: 1", 2.2, "power2.out")
sp = t0 + qi["lead"]
fromto(sp + 0.5, "#qdc1", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")

# ============================================================ profile beat
t0, t1 = B["profile"]
el_video("prv", t0, t1, "profile.mp4", 0.0, cls="framed")
el_div("pro", t0, t1, "qov", (
    '<div class="lbT"><div class="clipmark"></div><div class="tape">記録映像</div>'
    '<div class="qtag">部屋には 東京のネオンサイン</div>'
    '<div class="credit">引用: Dennis Garcia</div></div>'
    '<div class="lbB"></div>'
    '<div class="qcap" id="prc">彼の部屋は少しずつ <em>東京化</em>していた</div>'))
page_cut(t0)
fromto(t0 + 0.05, "#prv", "scale: 1.04", "scale: 1", 2.0, "power2.out")
fromto(N["n01"]["start"] + 0.2, "#prc", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")

# ============================================================ file beat (フォルダが開く)
t0, t1 = B["file"]
TITLE = "日本ロス"
el_div("filep", t0, t1, "panel paper", (
    '<div class="tab">CASE FILE <em>No.004</em> — 症例記録</div>'
    '<div class="fhead" id="fh">PATIENT: 日本を離れた、すべての旅行者</div>'
    f'<div class="ftitle" id="ft">{spans("ftc", TITLE)}<span class="caret" id="fcr"></span></div>'
    '<div class="fsubt" id="fs">— Post-Japan Depression という"症状"の記録</div>'
    '<div class="fstamp" id="fst">受付</div>'
    '<div class="folder" id="fold"><div class="foldtab"></div>'
    '<div class="foldttl">CASE FILE<br><span>No.004</span></div></div>'))
# フォルダカバーが開く(左へスライドアウト)
setv(t0 - 0.01, "#fold", "xPercent: 0")
n2 = N["n02"]["start"]
tw(n2 + 0.15, 'tl.to("#fold", {xPercent: -104, duration: 0.7, ease: "power3.inOut"}, %T%);')
page_cut(n2 + 0.75, 0.6)
fromto(n2 + 0.9, "#fh", "y: -16, opacity: 0", "y: 0, opacity: 1", 0.45, "power2.out")
n3 = N["n03"]["start"]
for i in range(len(TITLE)):
    setv(n3 + 1.2 + i * 0.22, f"#ftc{i}", "opacity: 1")
tw(n3 + 0.3, f'tl.to("#fcr", {{opacity: 0, duration: 0.01, repeat: 20, yoyo: true, repeatDelay: 0.42}}, %T%);')
n4 = N["n04"]["start"]
fromto(n4 + 0.2, "#fs", "opacity: 0", "opacity: 1", 0.5, "power2.out")
fromto(n4 + 1.1, "#fst", "scale: 2.0, opacity: 0, rotation: -8",
       "scale: 1, opacity: 1, rotation: -8", 0.28, "power4.in")

# ============================================================ ch1 扉
t0, t1 = B["ch1"]
el_video("ch1v", t0, t1, "ch1.mp4", 0.0)
el_div("ch1o", t0, t1, "qov", (
    '<div class="cdscrim"></div>'
    '<div class="creditD">引用: Dennis Garcia</div>'
    '<div class="ixghost" id="cg">1</div>'
    '<div class="ixtab" id="cb">第1章 主訴</div>'
    '<div class="ixtitle" id="ct">帰国したのに、帰りたい</div>'
    '<div class="ixsub" id="cs">— 世界中で 同じ訴えが続いている</div>'))
page_cut(t0)
fromto(t0 + 0.2, "#cb", "x: -70, opacity: 0", "x: 0, opacity: 1", 0.5, "power3.out")
fromto(t0 + 0.35, "#cg", "scale: 1.3, opacity: 0", "scale: 1, opacity: 0.2", 0.9, "power2.out")
fromto(t0 + 0.5, "#ct", 'opacity: 0, y: 24, filter: "blur(8px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.6, "power2.out")
fromto(t0 + 1.2, "#cs", "opacity: 0", "opacity: 1", 0.45, "power2.out")
tw(COMP - 1.05, 'tl.to("#stage", {opacity: 0, duration: 0.9, ease: "power1.in"}, %T%);')

CSS = """
@font-face { font-family:'NotoB'; src:url('assets/fonts/NotoSansJP-Black.otf') format('opentype'); }
@font-face { font-family:'NotoBd'; src:url('assets/fonts/NotoSansJP-Bold.otf') format('opentype'); }
@font-face { font-family:'SerifJP'; src:url('assets/fonts/NotoSerifJP.ttf') format('truetype');
  font-weight:100 900; }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { background:#000; }
#root { position:relative; width:1920px; height:1080px; overflow:hidden;
  background:#e9e5d8; font-family:'NotoBd',sans-serif; color:#1d2b50; }
#stage { position:absolute; inset:0; }
.clip { position:absolute; inset:0; width:100%; height:100%; }
video.bgv { object-fit:cover; transform:translateZ(0); backface-visibility:hidden; }
video.framed { top:80px; height:810px; }
em { font-style:normal; color:#c03b2d; }
#vig { position:absolute; inset:0; z-index:41; pointer-events:none;
  background:radial-gradient(ellipse 125% 112% at 50% 44%, rgba(0,0,0,0) 64%, rgba(70,60,36,.22) 100%); }
#pflash { position:absolute; inset:0; z-index:60; background:#fbf9f2; opacity:0; pointer-events:none; }
.panel.paper { z-index:10; background:
  repeating-linear-gradient(0deg, rgba(90,110,150,0) 0 66px, rgba(90,110,150,.14) 66px 68px),
  radial-gradient(ellipse 140% 110% at 50% 30%, #f7f4ea 0%, #f2eee0 60%, #e8e2cf 100%); }
.panel.paper::after { content:''; position:absolute; inset:0; pointer-events:none;
  box-shadow:inset 0 0 160px rgba(120,104,60,.16); }
.tab { position:absolute; right:60px; top:0; z-index:4; font-family:'NotoBd'; font-size:24px;
  letter-spacing:.1em; color:#f4f2ec; background:#1d2b50; padding:12px 26px 10px;
  border-radius:0 0 10px 10px; }
.tab em { color:#f0b9ae; }
.qov { z-index:10; }
.lbT { position:absolute; left:0; right:0; top:0; height:80px; background:#f2eee0;
  border-bottom:3px solid #1d2b50; box-shadow:0 4px 18px rgba(40,30,8,.25); }
.lbB { position:absolute; left:0; right:0; bottom:0; height:190px; background:#f2eee0;
  border-top:3px solid #1d2b50; box-shadow:0 -4px 18px rgba(40,30,8,.25); }
.clipmark { position:absolute; left:46px; top:50%; width:30px; height:44px; margin-top:-22px;
  border:5px solid #8d8468; border-radius:14px 14px 4px 4px; border-bottom:none; }
.tape { position:absolute; left:100px; top:50%; transform:translateY(-50%);
  font-family:'NotoB'; font-size:24px; letter-spacing:.2em; color:#f4f2ec; background:#c03b2d;
  padding:8px 18px; border-radius:4px; }
.qtag { position:absolute; left:300px; top:50%; transform:translateY(-50%);
  font-family:'NotoB'; font-size:29px; color:#1d2b50; letter-spacing:.06em; }
.credit { position:absolute; right:46px; top:50%; transform:translateY(-50%);
  font-family:'NotoBd'; font-size:24px; color:#8d8468; }
.qcap { position:absolute; left:60px; right:60px; bottom:52px; text-align:center; font-size:56px;
  font-family:'NotoB'; color:#1d2b50; letter-spacing:.02em; opacity:0; z-index:11; }
.creditD { position:absolute; top:26px; right:56px; font-family:'NotoBd'; font-size:24px;
  color:rgba(242,244,248,.92); background:rgba(10,12,18,.55); padding:7px 16px; z-index:5; }
/* file */
.fhead { position:absolute; left:0; right:0; top:240px; text-align:center; font-family:'NotoB';
  font-size:44px; letter-spacing:.14em; color:#2b5c8a; opacity:0; }
.ftitle { position:absolute; left:0; right:0; top:360px; text-align:center; font-family:'NotoB';
  font-size:200px; color:#1d2b50; letter-spacing:.06em; }
.tc { opacity:0; }
.caret { display:inline-block; width:10px; height:0.9em; background:#c03b2d; margin-left:14px;
  vertical-align:-0.08em; }
.fsubt { position:absolute; left:0; right:0; top:660px; text-align:center; font-family:'NotoBd';
  font-size:42px; color:#5a5340; opacity:0; }
.fstamp { position:absolute; right:250px; top:200px; font-family:'SerifJP'; font-weight:900;
  font-size:64px; color:#c03b2d; border:7px solid #c03b2d; border-radius:10px; padding:8px 30px;
  opacity:0; background:rgba(192,59,45,.05); }
.folder { position:absolute; inset:0; z-index:20; background:linear-gradient(135deg, #96785a, #85643f);
  display:flex; align-items:center; justify-content:center; }
.foldtab { position:absolute; left:120px; top:66px; width:420px; height:64px; background:#a98a66;
  border-radius:14px 14px 0 0; }
.foldttl { font-family:'NotoB'; font-size:100px; color:#f4ecd9; text-align:center; line-height:1.4;
  letter-spacing:.14em; }
.foldttl span { font-size:52px; color:#e3d2ae; }
/* ch1 card */
.cdscrim { position:absolute; inset:0;
  background:linear-gradient(0deg, rgba(10,12,18,.8) 0%, rgba(10,12,18,.42) 45%, rgba(10,12,18,.22) 100%); }
.ixghost { position:absolute; right:90px; top:44%; transform:translateY(-50%);
  font-family:'NotoB'; font-size:560px; color:#f2eee0; opacity:0; }
.ixtab { position:absolute; left:150px; top:330px; font-family:'NotoB'; font-size:46px;
  letter-spacing:.3em; color:#f4f2ec; background:#c03b2d; padding:14px 36px; border-radius:8px;
  opacity:0; }
.ixtitle { position:absolute; left:146px; top:452px; font-family:'NotoB'; font-size:94px;
  color:#f2f4f8; opacity:0; letter-spacing:.03em; text-shadow:0 4px 30px rgba(0,0,0,.7); }
.ixsub { position:absolute; left:152px; top:600px; font-family:'NotoBd'; font-size:38px;
  color:#cfd6e4; opacity:0; }
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
<div id="pflash"></div>
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
