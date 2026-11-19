# -*- coding: utf-8 -*-
"""japan03v2「シネマ・ドキュメンタリー」: index.html ビルダ(窓分割対応)
DESIGN03_v2.md 準拠。背景=フリーストック全画面 + 常時下部テロップ + 明朝見出し。
引用は qzhen(肉声) / n_cold(肉声) のみ。HF_WIN_START / HF_WIN_END env で窓ビルド。
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "japan03v2"
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


def el_bg(sid, t0, t1, src, ms, z):
    """背景動画: 非タイム wrapper (ズーム/フェード用) + clip video"""
    if not OV(t0, t1):
        return
    s = max(t0, W0)
    d = round(min(t1, W1 + 0.2) - s, 3)
    ms_eff = round(ms + (s - t0), 3)
    ELS.append(
        f'<div class="bgw" id="w_{sid}" style="z-index:{z}">'
        f'<video class="clip bgv" data-start="{T(s)}" data-duration="{d}" '
        f'data-media-start="{ms_eff}" data-track-index="{track()}" '
        f'src="assets/bg/{src}" muted playsinline></video></div>')


def tw(t, js):
    TWEENS.append(js.replace("%T%", str(round(t, 3))))


def fromto(t, sel, frm, to, dur, ease):
    tw(t, f'tl.fromTo("{sel}", {{{frm}}}, {{{to}, duration: {dur}, ease: "{ease}", immediateRender: false}}, %T%);')


def setv(t, sel, vars_):
    tw(t, f'tl.set("{sel}", {{{vars_}}}, %T%);')


def xfade(sid, t0, dur_total):
    fromto(t0, f"#w_{sid}", "opacity: 0", "opacity: 1", 0.45, "power1.inOut")
    tw(t0, f'tl.fromTo("#w_{sid}", {{scale: 1.0}}, {{scale: 1.05, duration: {round(dur_total, 2)}, '
           f'ease: "none", immediateRender: false}}, %T%);')


def telop(eid, lid, html, hold=0.7):
    """常時テロップ: ナレ行に同期 (アニメはクリップ内側の .telop に)"""
    st = N[lid]["start"] - 0.05
    en = N[lid]["start"] + N[lid]["dur"] + hold
    el_div(eid, st, en, "telopw", f'<div class="telop" id="{eid}i">{html}</div>')
    fromto(st + 0.02, f"#{eid}i", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.3, "power2.out")
    tw(en - 0.25, f'tl.to("#{eid}i", {{opacity: 0, duration: 0.22}}, %T%);')


ZBG = [0]


def zbg():
    ZBG[0] += 1
    return ZBG[0]


def scene_bg(sid, last=False):
    sc = SC[sid]
    t0 = sc["start"]
    t1 = COMP if last else sc["end"] + 0.55
    z = zbg()
    el_bg(sid, t0, t1, f"bg_{sid}.mp4", 0.0, z)
    xfade(sid, t0, t1 - t0)


# ============================================================ s_cold: qzhen 肉声
qi = Q["qzhen"]
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
el_div("qzo", t0, t1 + 0.1, "qov", (
    '<div class="qchip"><div class="qtag">日本を愛する中国人クリエイター</div>'
    '<div class="qcredit">引用: Zhen Into Chinese</div></div>'
    '<div class="qcap" id="qzc1">「日本が大好きな <em class="cn">中国人</em>として」</div>'
    '<div class="qcap" id="qzc2">「2つの国の<em>違い</em>を 話したい」</div>'))
sp = t0 + qi["lead"]
fromto(t0 + 0.3, "#qzo .qchip", "x: -14, opacity: 0", "x: 0, opacity: 1", 0.4, "power2.out")
fromto(sp + 0.4, "#qzc1", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
setv(sp + 4.9, "#qzc1", "opacity: 0")
fromto(sp + 5.0, "#qzc2", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")

# ============================================================ s_title
scene_bg("s_title")
sc = SC["s_title"]
telop("tp01", "n01", '日本を愛する中国人が語った、日中の「<em>決定的な差</em>」', hold=0.4)
tt = N["n01"]["start"] + N["n01"]["dur"] + 0.25
el_div("ttl", tt - 0.1, sc["end"] + 0.1, "twrap", (
    '<div class="tlabel" id="tlb">ある中国人クリエイターの言葉</div>'
    '<div class="ttitle" id="tti">中国とは、<span class="cn">違いすぎた</span></div>'
    '<div class="tline" id="tln"></div>'
    '<div class="tsub" id="tsb">— 909万人が気づいた、日中の決定的な差</div>'))
fromto(tt, "#tlb", "opacity: 0, y: -14, scale: 1.06", "opacity: 1, y: 0, scale: 1", 0.55, "power2.out")
fromto(tt + 0.35, "#tti", 'opacity: 0, y: 24, filter: "blur(10px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.7, "power2.out")
fromto(tt + 0.9, "#tln", "scaleX: 0", "scaleX: 1", 0.5, "power2.inOut")
fromto(tt + 1.15, "#tsb", "opacity: 0", "opacity: 1", 0.45, "power2.out")

# ============================================================ s_data1 (909万)
scene_bg("s_data1")
sc = SC["s_data1"]
el_div("dp1", sc["start"] + 0.25, sc["end"] + 0.1, "dpanelw", (
    '<div class="dpanel" id="dp1i"><div class="dlabel">2025年に日本を訪れた中国人</div>'
    '<div class="dnum"><span id="dnv">0</span><span class="dunit">万人</span></div>'
    '<div class="dsub">前年比 <em>+30%</em> — 過去最多ペース</div>'
    '<div class="dsrc">出典: JNTO 訪日外客統計(2025年)</div></div>'))
d1 = N["n02"]["start"]
fromto(d1 - 0.1, "#dp1i", "y: 40, opacity: 0", "y: 0, opacity: 1", 0.5, "power3.out")
tw(d1 + 0.9, 'tl.fromTo(CNT, {v: 0}, {v: 909, duration: 1.15, ease: "power2.out", '
             'onUpdate: () => { const el = document.getElementById("dnv"); '
             'if (el) el.textContent = Math.round(CNT.v); }}, %T%);')

# ============================================================ s_data2 (8月100万)
scene_bg("s_data2")
sc = SC["s_data2"]
el_div("dp2", sc["start"] + 0.2, sc["end"] + 0.1, "dpanelw", (
    '<div class="dpanel" id="dp2i"><div class="dlabel">2025年8月 — ひと月だけで</div>'
    '<div class="dnum">100<span class="dunit">万人超</span></div>'
    '<div class="dsub">国・地域別で<em>最多</em></div>'
    '<div class="dsrc">出典: JNTO 訪日外客統計(2025年8月)</div></div>'))
fromto(N["n03"]["start"] - 0.05, "#dp2i", "y: 40, opacity: 0", "y: 0, opacity: 1", 0.5, "power3.out")

# ============================================================ s_fam / s_go
scene_bg("s_fam")
telop("tp04", "n04", '中華系マレーシア人家族・<em>6人</em>の日本旅行', hold=0.5)
scene_bg("s_go")
telop("tp04b", "n04b", 'レンタカーで、旅がスタート', hold=0.5)

# ============================================================ s_noodle (テキスト引用)
scene_bg("s_noodle")
sc = SC["s_noodle"]
telop("tp05", "n05", '到着初日の「最初の一杯」', hold=0.2)
qt = N["n05"]["start"] + N["n05"]["dur"] + 0.25
el_div("tq", qt - 0.1, sc["end"] + 0.1, "tqwrap", (
    '<div class="tquote" id="tqt">「コシがあって、柔らかい。<br>この味、<em>好き</em>」</div>'
    '<div class="tqsrc" id="tqs">— 家族の動画より(引用: Nicaboo)</div>'))
fromto(qt, "#tqt", 'opacity: 0, y: 20, filter: "blur(6px)"',
       'opacity: 1, y: 0, filter: "blur(0px)"', 0.55, "power2.out")
fromto(qt + 0.7, "#tqs", "opacity: 0", "opacity: 1", 0.4, "power2.out")

# ============================================================ s_fuji / s_coldlead
scene_bg("s_fuji")
telop("tp06", "n06", '氷点下5度の河口湖 — <em>富士山</em>に見入る', hold=0.6)
scene_bg("s_coldlead")
telop("tp07", "n07", 'ただし、日本の冬を<em class="cn">なめてはいけない</em>', hold=0.4)

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
    '<div class="qchip"><div class="qtag">東京の夜 — 家族の記録</div>'
    '<div class="qcredit">引用: Nicaboo</div></div>'
    '<div class="qcap" id="ncc1">「こんなに寒いと 思わなかった…」</div>'
    '<div class="qcap" id="ncc2">「いま ちょっと<em>後悔</em>してます(笑)」</div>'))
sp = t0 + qi["lead"]
fromto(t0 + 0.25, "#nco .qchip", "x: -14, opacity: 0", "x: 0, opacity: 1", 0.4, "power2.out")
fromto(sp + 0.15, "#ncc1", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
setv(sp + 3.9, "#ncc1", "opacity: 0")
fromto(sp + 4.0, "#ncc2", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")

# ============================================================ s_pivot (伏字)
scene_bg("s_pivot")
sc = SC["s_pivot"]
telop("tp08", "n08", '本当の驚きは、景色でも食事でもなかった', hold=0.1)
kt = N["n08"]["start"] + N["n08"]["dur"] + 0.3
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
# ディップ・トゥ・ブラック
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
@font-face { font-family:'Serif'; src:url('assets/fonts/NotoSerifJP.ttf') format('truetype');
  font-weight:900; }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { background:#000; }
#root { position:relative; width:1920px; height:1080px; overflow:hidden;
  background:#0a0d14; font-family:'NotoBd',sans-serif; color:#f2f4f8; }
#stage { position:absolute; inset:0; }
.clip { position:absolute; inset:0; width:100%; height:100%; }
.bgw { position:absolute; inset:0; opacity:0; will-change:transform,opacity; }
video.bgv { position:absolute; inset:0; width:100%; height:100%; object-fit:cover;
  transform:translateZ(0); backface-visibility:hidden; }
em { font-style:normal; color:#7db8e8; }
em.cn, .cn { font-style:normal; color:#ff7a5c; }
#scrim { position:absolute; inset:0; z-index:28; pointer-events:none;
  background:linear-gradient(0deg, rgba(5,7,12,.72) 0%, rgba(5,7,12,.18) 16%, rgba(5,7,12,0) 32%); }
#barT, #barB { position:absolute; left:0; right:0; height:64px; background:#000; z-index:40; }
#barT { top:0; } #barB { bottom:0; }
#dip { position:absolute; inset:0; background:#000; z-index:38; opacity:0; pointer-events:none; }
/* 常時テロップ */
.telopw { z-index:33; pointer-events:none; display:flex; align-items:flex-end;
  justify-content:center; padding-bottom:92px; }
.telop { font-family:'NotoB'; font-size:46px; letter-spacing:.04em; text-align:center;
  max-width:1680px; color:#f2f4f8; opacity:0;
  text-shadow:0 2px 16px rgba(0,0,0,.85), 0 0 2px rgba(0,0,0,.9); }
/* 引用チェローム */
.qov { z-index:34; pointer-events:none; }
.qchip { position:absolute; left:56px; top:96px; background:rgba(5,8,14,.68);
  padding:14px 22px; border-left:3px solid #7db8e8; opacity:0; }
.qchip .qtag { font-family:'NotoB'; font-size:27px; letter-spacing:.06em; }
.qchip .qcredit { font-size:20px; color:#aab6c8; margin-top:4px; }
.qcap { position:absolute; left:60px; right:60px; bottom:96px; text-align:center; font-size:52px;
  font-family:'NotoB'; color:#f2f4f8; letter-spacing:.02em; opacity:0;
  text-shadow:0 2px 16px rgba(0,0,0,.85); }
/* タイトル */
.twrap { z-index:35; pointer-events:none; }
.tlabel { position:absolute; left:0; right:0; top:300px; text-align:center; font-family:'NotoB';
  font-size:32px; letter-spacing:.34em; color:#cfd8e4; opacity:0;
  text-shadow:0 2px 10px rgba(0,0,0,.8); }
.ttitle { position:absolute; left:0; right:0; top:380px; text-align:center; font-family:'Serif';
  font-weight:900; font-size:128px; color:#f5f6f8; opacity:0; letter-spacing:.015em;
  text-shadow:0 4px 34px rgba(0,0,0,.85); }
.tline { position:absolute; left:50%; top:600px; width:560px; margin-left:-280px; height:3px;
  transform-origin:center; transform:scaleX(0);
  background:linear-gradient(90deg, rgba(255,122,92,0), #ff7a5c 30%, #7db8e8 70%, rgba(125,184,232,0)); }
.tsub { position:absolute; left:0; right:0; top:640px; text-align:center; font-family:'NotoBd';
  font-size:36px; color:#d6dde7; opacity:0; text-shadow:0 2px 12px rgba(0,0,0,.85); }
/* データパネル */
.dpanelw { z-index:33; pointer-events:none; }
.dpanel { position:absolute; left:120px; bottom:120px; width:760px;
  background:rgba(8,11,18,.78); border-left:4px solid #ff7a5c; padding:30px 40px 24px; opacity:0; }
.dlabel { font-family:'NotoB'; font-size:30px; letter-spacing:.08em; color:#e8edf4; }
.dnum { font-family:'NotoB'; font-size:110px; line-height:1.15; color:#fff;
  font-variant-numeric:tabular-nums; letter-spacing:.01em; }
.dnum .dunit { font-size:48px; margin-left:8px; color:#e8edf4; }
.dsub { font-family:'NotoBd'; font-size:30px; color:#cfd8e4; margin-top:2px; }
.dsrc { font-size:21px; color:#8d99ab; margin-top:14px; }
/* テキスト引用 */
.tqwrap { z-index:35; pointer-events:none; }
.tquote { position:absolute; left:0; right:0; top:300px; text-align:center; font-family:'Serif';
  font-weight:900; font-size:76px; line-height:1.5; color:#f5f6f8; opacity:0;
  text-shadow:0 4px 28px rgba(0,0,0,.9); }
.tqsrc { position:absolute; left:0; right:0; top:570px; text-align:center; font-family:'NotoBd';
  font-size:30px; color:#cfd8e4; opacity:0; text-shadow:0 2px 12px rgba(0,0,0,.85); }
/* 伏字キック */
.kwrap { z-index:35; pointer-events:none; }
.kdark { position:absolute; inset:0; background:rgba(4,6,10,.55); }
.kick { position:absolute; left:0; right:0; top:450px; text-align:center; font-family:'Serif';
  font-weight:900; font-size:88px; color:#f5f6f8; opacity:0;
  text-shadow:0 4px 30px rgba(0,0,0,.9); }
.fsslot { position:relative; display:inline-block; min-width:300px; }
.fsw { display:inline-block; }
.fsa { color:#aab6c8; }
.fsb { position:absolute; left:50%; top:0; color:#ff7a5c; white-space:nowrap; }
/* 章扉 */
.cdark { position:absolute; inset:0; background:rgba(4,6,10,.62); }
.cwrap { position:absolute; inset:0; }
.cno { position:absolute; left:0; right:0; top:330px; text-align:center; font-family:'NotoB';
  font-size:40px; letter-spacing:.5em; color:#7db8e8; opacity:0; }
.cline { position:absolute; left:50%; top:412px; width:420px; margin-left:-210px; height:3px;
  transform-origin:center; transform:scaleX(0); background:rgba(125,184,232,.7); }
.ctitle { position:absolute; left:0; right:0; top:448px; text-align:center; font-family:'Serif';
  font-weight:900; font-size:108px; color:#f5f6f8; opacity:0;
  text-shadow:0 4px 30px rgba(0,0,0,.85); }
.csub { position:absolute; left:0; right:0; top:636px; text-align:center; font-family:'NotoBd';
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
