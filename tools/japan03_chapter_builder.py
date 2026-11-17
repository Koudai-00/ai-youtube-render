# -*- coding: utf-8 -*-
"""japan03cX 章ビルダ「深夜放送(ミッドナイト・オンエア)」(窓分割対応)。EP_CH env で章選択。
long01(報道)/long02(和紙紀行)と完全に別デザイン (DESIGN03.md):
 - 深紺の放送室キャンバス + シアン(日本)/朱橙(中国)のネオン + 白
 - パネル: tune(テーゼ) split(左右対比) senga(黒背景白線画) datac(ネオン数字)
   kick(line/fuseji) card(TRACK扉) monitor引用フレーム ask end(CRTオフ)
実績方式: tweenは絶対時刻で内側tlへ、root.fromTo(tl,{time:W0},{time:W1})登録。
副産物: subtitles/out/<EP>/sfx_cues.json (フル範囲ビルド時のみ信頼)。
"""
import json
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from japan03_chapters import BROLL, CREDIT, TAG, Q as QSPEC  # noqa: E402

NV_PRE = 0.6  # extract_quotes.NV_PRE と一致

EP = os.environ.get("EP_CH") or "japan03c1"
TPL = ROOT / "hyperframes" / "templates" / EP
TIM = json.loads((ROOT / "subtitles" / "out" / EP / "timings.json").read_text(encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)

W0 = float(os.environ.get("HF_WIN_START") or 0)
W1 = float(os.environ.get("HF_WIN_END") or COMP)
WDUR = round(W1 - W0, 3)
FULL = (W0 == 0 and W1 >= COMP - 0.01)


def T(t):
    return round(t - W0, 3)


def OV(t0, t1):
    return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)


N = TIM["narr"]
Q = TIM["quotes"]
SC = TIM["scenes"]

ELS = []
TWEENS = []
CUES = []
_track = [0]


def cue(k, t, s=1.0, d=0.0):
    CUES.append({"k": k, "t": round(t, 3), "s": s, "d": d})


def track():
    _track[0] += 1
    return _track[0]


def el_div(eid, t0, t1, cls, inner, style=""):
    if not OV(t0, t1):
        return
    s = max(t0, W0)
    d = round(min(t1, COMP) - s, 3)
    ELS.append(
        f'<div id="{eid}" class="clip {cls}" data-start="{T(s)}" data-duration="{d}" '
        f'data-track-index="{track()}" style="{style}">{inner}</div>')


def el_video(eid, t0, t1, src, ms, cls=""):
    if not OV(t0, t1):
        return
    s = max(t0, W0)
    d = round(min(t1, COMP) - s, 3)
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


rng = random.Random(31)


def tline_cut(t, strength=1.0):
    """チャンネル切替: 白い走査線が縦に走る"""
    setv(t - 0.02, "#tline", "opacity: 1, y: 0")
    tw(t - 0.02, 'tl.to("#tline", {y: 1088, duration: 0.3, ease: "power2.inOut"}, %T%);')
    tw(t + 0.26, 'tl.to("#tline", {opacity: 0, duration: 0.15}, %T%);')
    cue("glitch", t, strength)


# 番組ロゴ (全パネル共通)
LOGO = ('<div class="logo"><span class="dot"></span>深夜の日本論<span class="oa">ON AIR</span></div>')


def tracktag(s):
    tr = s.get("trk")
    return f'<div class="trk">{tr}</div>' if tr else ""


GRADE0 = {
    "gray": "grayscale(0) saturate(1) contrast(1) brightness(1)",
    "warm": "saturate(1) sepia(0) contrast(1) brightness(1)",
    "cold": "saturate(1) hue-rotate(0deg) brightness(1) contrast(1)",
}
GRADE1 = {
    "gray": "grayscale(1) saturate(0.35) contrast(1.08) brightness(0.9)",
    "warm": "saturate(1.15) sepia(0.14) contrast(1.02) brightness(1.04)",
    "cold": "saturate(0.6) hue-rotate(-12deg) brightness(0.92) contrast(1.08)",
}


def qframe(smp, credit=None):
    """引用フレーム: モニターベゼル (上バー: REC+タグ+クレジット / 下: 字幕ゾーン)"""
    return ('<div class="lbT"><span class="rec"></span><div class="qtag">' + TAG[smp] + '</div>'
            f'<div class="credit">{credit or CREDIT[smp]}</div></div>'
            '<div class="lbB"></div>')


def quote_block(qid, sc_start):
    qi = Q[qid]
    t0 = qi["beat_start"]
    t1 = t0 + qi["dur"]
    sp = t0 + qi["lead"]
    el_video(f"{qid}v", t0, t1, qi["clip"], qi["media_start"], cls="framed")
    caps = qi["caps"]
    cdivs = "".join(f'<div class="qcap" id="{qid}cap{i}">{h}</div>' for i, (dt, h) in enumerate(caps))
    el_div(f"{qid}o", t0, t1, "qov", qframe(qi["sample"], qi["credit"]) + cdivs)
    for i, (dt, _h) in enumerate(caps):
        tin = sp + dt
        fromto(tin, f"#{qid}cap{i}", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.28, "power3.out")
        cue("pop", tin, 0.6)
        if i + 1 < len(caps):
            setv(sp + caps[i + 1][0] - 0.12, f"#{qid}cap{i}", "opacity: 0")
    g = qi.get("grade")
    if g:
        fromto(sp + 0.3, f"#{qid}v", f'filter: "{GRADE0[g]}"', f'filter: "{GRADE1[g]}"', 0.9, "power2.inOut")
    fromto(t0 + 0.02, f"#{qid}v", "scale: 1.04", "scale: 1", 2.2, "power2.out")
    tline_cut(t0, 0.9 if abs(t0 - sc_start) < 0.2 else 0.6)


def sc_nv(s):
    t0, t1 = s["start"], s["end"]
    qid = s["q"]
    qs = QSPEC[qid]
    nids = s["nids"]
    caps = qs["caps"]
    assert len(caps) == len(nids), f"{EP}:{qid} caps{len(caps)} != nids{len(nids)}"
    el_video(f"{qid}v", t0, t1, f"{qid}.mp4", NV_PRE, cls="framed")
    cdivs = "".join(f'<div class="qcap" id="{qid}cap{i}">{h}</div>' for i, (_dt, h) in enumerate(caps))
    el_div(f"{qid}o", t0, t1, "qov", qframe(qs["s"]) + cdivs)
    times = [N[nid]["start"] for nid in nids]
    for i, st in enumerate(times):
        tin = max(t0 + 0.05, st - 0.12)
        fromto(tin, f"#{qid}cap{i}", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.28, "power3.out")
        cue("pop", tin, 0.6)
        if i + 1 < len(times):
            setv(times[i + 1] - 0.25, f"#{qid}cap{i}", "opacity: 0")
    g = qs.get("grade")
    if g:
        fromto(t0 + 0.4, f"#{qid}v", f'filter: "{GRADE0[g]}"', f'filter: "{GRADE1[g]}"', 0.9, "power2.inOut")
    fromto(t0 + 0.02, f"#{qid}v", "scale: 1.04", "scale: 1", 2.2, "power2.out")
    tline_cut(t0, 0.7)


def sc_broll(s):
    t0, t1 = s["start"], s["end"]
    bid = s["bg"]
    smp = BROLL[bid][0]
    el_video(f'{s["id"]}v', t0, t1, f"{bid}.mp4", 0.0, cls="framed")
    lab = (f'<div class="biglabel" id="{s["id"]}lab">{s["label"]}</div>' if s.get("label") else "")
    el_div(f'{s["id"]}sc', t0, t1, "qov", qframe(smp) + lab)
    if s.get("label"):
        fromto(t0 + 0.35, f'#{s["id"]}lab', "x: -30, opacity: 0", "x: 0, opacity: 1", 0.5, "power2.out")
        cue("sub", t0 + 0.35, 0.7)
    tline_cut(t0, 0.8)


KICK_STYLES = ["line", "fuseji"]
_ks_i = [0]


def sc_kick(s):
    t0, t1 = s["start"], s["end"]
    k = s.get("kicker")
    if not k:
        raise SystemExit(f"{EP}:{s['id']}: kick には必ず kicker テキストを付ける")
    eid = s["id"]
    style = s.get("kstyle") or KICK_STYLES[_ks_i[0] % len(KICK_STYLES)]
    _ks_i[0] += 1
    if style == "fuseji" and "<em>" in k:
        # <em>語</em> を伏字◯◯で隠し、途中でフリップして開く
        m = re.search(r"<em>(.+?)</em>", k)
        word = m.group(1)
        mask = "〇" * max(2, len(re.sub(r"<[^>]+>", "", word)))
        pre, post = k.split("<em>", 1)[0], k.split("</em>", 1)[1]
        el_div(f"{eid}p", t0, t1, "panel", (
            LOGO + tracktag(s) +
            f'<div class="fswrap"><div class="fst" id="{eid}k">{pre}'
            f'<span class="fsslot"><span class="fsmask" id="{eid}m">{mask}</span>'
            f'<span class="fsopen" id="{eid}w">{word}</span></span>{post}</div></div>'))
        fromto(t0 + 0.25, f"#{eid}k", 'opacity: 0, y: 22, filter: "blur(8px)"',
               'opacity: 1, y: 0, filter: "blur(0px)"', 0.55, "power2.out")
        cue("sub", t0 + 0.3, 0.8)
        n0 = N[s["nids"][0]]
        tf = n0["start"] + 0.72 * n0["dur"]
        fromto(tf, f"#{eid}m", "rotationX: 0, opacity: 1", "rotationX: 90, opacity: 0", 0.22, "power2.in")
        fromto(tf + 0.2, f"#{eid}w", "rotationX: -90, opacity: 0, xPercent: -50",
               "rotationX: 0, opacity: 1, xPercent: -50", 0.26, "power2.out")
        cue("slam", tf + 0.24, 0.7)
    else:  # line: 左のシアンバー + 一行
        el_div(f"{eid}p", t0, t1, "panel", (
            LOGO + tracktag(s) +
            f'<div class="klwrap"><div class="klbar" id="{eid}b"></div>'
            f'<div class="klt" id="{eid}k">{k}</div></div>'))
        fromto(t0 + 0.22, f"#{eid}b", "scaleY: 0", "scaleY: 1", 0.4, "power3.out")
        fromto(t0 + 0.4, f"#{eid}k", "x: -36, opacity: 0", "x: 0, opacity: 1", 0.5, "power3.out")
        cue("sub", t0 + 0.42, 0.8)


def sc_tune(s):  # テーゼ: 中央ネオン一文
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    el_div(f"{eid}p", t0, t1, "panel", (
        LOGO + tracktag(s) +
        f'<div class="tnwrap"><div class="tnt" id="{eid}t">{s["text"]}</div>'
        f'<div class="tnline" id="{eid}l"></div></div>'))
    fromto(t0 + 0.3, f"#{eid}t", 'opacity: 0, y: 26, filter: "blur(10px)"',
           'opacity: 1, y: 0, filter: "blur(0px)"', 0.7, "power2.out")
    fromto(t0 + 0.75, f"#{eid}l", "scaleX: 0", "scaleX: 1", 0.55, "power2.inOut")
    cue("sub", t0 + 0.35, 0.9)


def sc_split(s):  # 左右対比 (左=中国 朱橙 / 右=日本 シアン)
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    lt, lls = s["left"]
    rt, rls = s["right"]
    lrows = "".join(f'<div class="sprow" id="{eid}l{i}">{x}</div>' for i, x in enumerate(lls))
    rrows = "".join(f'<div class="sprow" id="{eid}r{i}">{x}</div>' for i, x in enumerate(rls))
    el_div(f"{eid}p", t0, t1, "panel", (
        LOGO + tracktag(s) +
        f'<div class="dhead" id="{eid}h">{s["head"]}</div>'
        f'<div class="spwrap">'
        f'<div class="spcol cn" id="{eid}L"><div class="sptitle">{lt}</div>{lrows}</div>'
        f'<div class="spmid"><div class="spline" id="{eid}ln"></div><div class="spvs" id="{eid}vs">VS</div></div>'
        f'<div class="spcol jp" id="{eid}R"><div class="sptitle">{rt}</div>{rrows}</div>'
        f'</div>'))
    fromto(t0 + 0.3, f"#{eid}h", "y: -22, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    fromto(t0 + 0.55, f"#{eid}L", "x: -60, opacity: 0", "x: 0, opacity: 1", 0.5, "power2.out")
    fromto(t0 + 0.7, f"#{eid}R", "x: 60, opacity: 0", "x: 0, opacity: 1", 0.5, "power2.out")
    fromto(t0 + 0.6, f"#{eid}ln", "scaleY: 0", "scaleY: 1", 0.5, "power2.inOut")
    fromto(t0 + 1.0, f"#{eid}vs", "scale: 1.8, opacity: 0", "scale: 1, opacity: 1", 0.4, "back.out(2)")
    cue("slam", t0 + 1.05, 0.6)
    dur_n = t1 - t0 - 1.8
    nrows = max(len(lls), len(rls))
    for i in range(nrows):
        tt = t0 + 1.35 + i * (dur_n * 0.8 / max(nrows, 1))
        if i < len(lls):
            fromto(tt, f"#{eid}l{i}", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.35, "power2.out")
            cue("tick", tt, 0.7)
        if i < len(rls):
            fromto(tt + 0.16, f"#{eid}r{i}", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.35, "power2.out")
            cue("tick", tt + 0.16, 0.7)


# ---------------------------------------------------------------- 白線画 (senga)
def _fig(x, y, sc=1.0, pose="stand", flip=False):
    """線画人物: 頭+胴+脚。pose: stand/bow/hold/point"""
    fl = " scale(-1,1)" if flip else ""
    if pose == "bow":
        body = ('<circle cx="0" cy="-150" r="26"/>'
                '<path d="M-6 -124 C 30 -100, 56 -60, 60 -6 L 40 -6 C 36 -52, 16 -86, -14 -104 Z" />'
                '<path d="M60 -6 L 60 0 M 40 -6 L 40 0"/>'
                '<path d="M-2 -110 C 24 -96, 40 -74, 44 -48"/>')
        body = ('<circle cx="18" cy="-118" r="24"/>'
                '<path d="M36 -100 C 64 -78, 72 -40, 72 0"/>'
                '<path d="M40 -96 C 20 -60, 16 -30, 20 0"/>'
                '<path d="M34 -92 C 52 -78, 58 -58, 56 -40"/>')
    elif pose == "hold":
        body = ('<circle cx="0" cy="-168" r="26"/>'
                '<path d="M0 -140 C -4 -96, -4 -60, -6 0"/>'
                '<path d="M0 -140 C 10 -96, 12 -60, 14 0"/>'
                '<path d="M-2 -128 C -34 -112, -48 -92, -54 -74"/>'
                '<path d="M2 -128 C 34 -112, 48 -92, 54 -74"/>')
    elif pose == "point":
        body = ('<circle cx="0" cy="-168" r="26"/>'
                '<path d="M0 -140 C -4 -96, -4 -60, -8 0"/>'
                '<path d="M0 -140 C 8 -96, 10 -60, 12 0"/>'
                '<path d="M-2 -126 C -22 -118, -34 -104, -40 -88"/>'
                '<path d="M2 -132 C 40 -138, 66 -142, 88 -146"/>')
    else:
        body = ('<circle cx="0" cy="-168" r="26"/>'
                '<path d="M0 -140 C -4 -96, -4 -60, -8 0"/>'
                '<path d="M0 -140 C 8 -96, 10 -60, 12 0"/>'
                '<path d="M-2 -126 C -24 -112, -34 -96, -38 -78"/>'
                '<path d="M2 -126 C 26 -112, 36 -96, 40 -78"/>')
    return f'<g transform="translate({x},{y}) scale({sc}){fl}">{body}</g>'


ART = {
    # 報告された中国人: 左=お辞儀する同僚 右=誘う男性(スマホ) 上に通報マーク
    "report": (
        '<svg viewBox="0 0 1700 760" fill="none" stroke="#eef3f8" stroke-width="6" stroke-linecap="round">'
        '<path d="M120 720 H 1580" stroke-width="4" opacity="0.5"/>'
        + _fig(540, 720, 1.7, "bow") + _fig(1150, 720, 1.7, "hold", flip=True) +
        '<rect x="1218" y="452" width="64" height="104" rx="12"/>'
        '<path d="M1230 478 h40 M1230 500 h40 M1230 522 h26"/>'
        '<g transform="translate(850,170)"><circle r="88"/>'
        '<path d="M0 -42 V 20 M0 48 V 50" stroke-width="13"/></g>'
        '</svg>'),
    # 果物店: 果物かご+1個を手にする旅行者+店主
    "fruit": (
        '<svg viewBox="0 0 1700 760" fill="none" stroke="#eef3f8" stroke-width="6" stroke-linecap="round">'
        '<path d="M120 720 H 1580" stroke-width="4" opacity="0.5"/>'
        '<path d="M700 600 h300 l-36 110 h-228 Z"/>'
        '<circle cx="780" cy="580" r="34"/><circle cx="850" cy="566" r="34"/><circle cx="920" cy="580" r="34"/>'
        + _fig(430, 720, 1.7, "hold") +
        '<circle cx="492" cy="598" r="30"/>'
        + _fig(1280, 720, 1.7, "point", flip=True) +
        '<g transform="translate(1065,300)"><circle r="68"/>'
        '<path d="M-24 -24 l48 48 M24 -24 l-48 48" stroke-width="9"/></g>'
        '</svg>'),
    # 静かな車内: 座席の列+座る人々
    "train": (
        '<svg viewBox="0 0 1700 760" fill="none" stroke="#eef3f8" stroke-width="6" stroke-linecap="round">'
        '<path d="M160 180 H 1540 M160 180 V 700 M1540 180 V 700 M160 700 H 1540" opacity="0.6"/>'
        '<rect x="300" y="260" width="250" height="170" rx="18" opacity="0.7"/>'
        '<rect x="1150" y="260" width="250" height="170" rx="18" opacity="0.7"/>'
        '<path d="M360 700 V 560 Q 360 520 400 520 H 520 Q 560 520 560 560 V 700"/>'
        '<path d="M1140 700 V 560 Q 1140 520 1180 520 H 1300 Q 1340 520 1340 560 V 700"/>'
        '<circle cx="460" cy="470" r="26"/><circle cx="1240" cy="470" r="26"/>'
        '<path d="M820 330 q 26 -40 52 0 q 26 40 52 0" opacity="0.65"/>'
        '</svg>'),
}


def sc_senga(s):  # 黒背景+白線画の再現イラスト
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    art = ART[s["art"]]
    cap = s.get("cap", "")
    el_div(f"{eid}p", t0, t1, "panel dark", (
        LOGO + tracktag(s) +
        f'<div class="sgwrap" id="{eid}a">{art}</div>'
        f'<div class="sgcap" id="{eid}c">{cap}</div>'))
    fromto(t0 + 0.25, f"#{eid}a", 'opacity: 0, scale: 1.05, filter: "blur(6px)"',
           'opacity: 1, scale: 1, filter: "blur(0px)"', 0.7, "power2.out")
    cue("sub", t0 + 0.3, 0.8)
    if cap:
        fromto(t0 + 0.9, f"#{eid}c", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.45, "power2.out")
        cue("pop", t0 + 0.95, 0.6)
    # ゆっくりズーム (静止画の間延び防止)
    fromto(t0 + 0.9, f"#{eid}a", "scale: 1", "scale: 1.045", max(2.0, t1 - t0 - 1.0), "none")


def sc_datac(s):  # ネオン数字カード
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    el_div(f"{eid}p", t0, t1, "panel", (
        LOGO + tracktag(s) +
        f'<div class="dhead" id="{eid}h">{s["head"]}</div>'
        f'<div class="dcnum" id="{eid}n">{s["num"]}<span>{s.get("unit","")}</span></div>'
        f'<div class="dcsub" id="{eid}s">{s.get("sub","")}</div>'
        f'<div class="cntsrc">{s.get("src","")}</div>'))
    fromto(t0 + 0.3, f"#{eid}h", "y: -22, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    n0 = N[s["nids"][0]]
    tn = n0["start"] + min(1.6, 0.35 * n0["dur"])
    fromto(tn, f"#{eid}n", 'scale: 1.14, opacity: 0, filter: "blur(10px)"',
           'scale: 1, opacity: 1, filter: "blur(0px)"', 0.7, "power2.out")
    cue("count", tn, 0.8, 0.7)
    if s.get("sub"):
        fromto(tn + 1.1, f"#{eid}s", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.45, "power2.out")
        cue("pop", tn + 1.1, 0.6)


def sc_card(s):  # TRACK扉: キューシート
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    if s.get("bg"):
        el_video(f"{eid}v", t0, t1, f'{s["bg"]}.mp4', 0.0)
        smp = BROLL[s["bg"]][0]
        credit = f'<div class="creditD">{CREDIT[smp]}</div>'
        scrim = '<div class="cdscrim"></div>'
    else:
        credit = scrim = ""
    el_div(f"{eid}o", t0, t1, "qov cardov", (
        scrim + credit + LOGO +
        f'<div class="cno" id="{eid}n">{s["no"]}</div>'
        f'<div class="cline" id="{eid}l"></div>'
        f'<div class="ctitle" id="{eid}t">{s["title"]}</div>'
        + (f'<div class="csub" id="{eid}s">{s["sub"]}</div>' if s.get("sub") else "")))
    cue("riser", max(0.0, t0 - 1.3), 1.0, 1.3)
    tline_cut(t0, 1.0)
    fromto(t0 + 0.2, f"#{eid}n", "x: -60, opacity: 0", "x: 0, opacity: 1", 0.55, "power3.out")
    fromto(t0 + 0.4, f"#{eid}l", "scaleX: 0", "scaleX: 1", 0.5, "power2.inOut")
    fromto(t0 + 0.55, f"#{eid}t", 'opacity: 0, y: 26, filter: "blur(8px)"',
           'opacity: 1, y: 0, filter: "blur(0px)"', 0.65, "power2.out")
    cue("slam", t0 + 0.75, 0.8)
    cue("sub", t0 + 0.8, 1.0)
    if s.get("sub"):
        fromto(t0 + 1.25, f"#{eid}s", "opacity: 0", "opacity: 1", 0.45, "power2.out")


def sc_q(s):
    for qid, qi in Q.items():
        if s["start"] - 0.01 <= qi["beat_start"] < s["end"]:
            quote_block(qid, s["start"])


def sc_ask(s):
    t0, t1 = s["start"], s["end"]
    el_div("askp", t0, t1, "panel", (
        LOGO +
        '<div class="askt" id="ask1">あなたは どちらの国の<br>「<em>優しさ</em>」が心地いいですか</div>'
        '<div class="asks" id="ask2">▼ 海外の方と接して感じた「違い」、コメントで聞かせてください</div>'))
    fromto(t0 + 0.3, "#ask1", 'opacity: 0, y: 24, filter: "blur(8px)"',
           'opacity: 1, y: 0, filter: "blur(0px)"', 0.7, "power2.out")
    cue("sub", t0 + 0.35, 0.8)
    fromto(t0 + 1.5, "#ask2", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
    cue("pop", t0 + 1.5, 0.6)
    tw(t0 + 2.1, 'tl.to("#ask2", {y: 8, duration: 0.5, ease: "sine.inOut", repeat: 5, yoyo: true}, %T%);')


def sc_end(s):  # 放送終了: メッセージ → CRTオフ
    t0, t1 = s["start"], s["end"]
    el_div("endp", t0, t1, "panel", (
        LOGO +
        '<div class="endt" id="end1">ご視聴 ありがとうございました</div>'
        '<div class="ends" id="end2">チャンネル登録で、次の放送をお聞き逃しなく</div>'
        '<div class="crt" id="crt"></div>'))
    fromto(t0 + 0.3, "#end1", "opacity: 0", "opacity: 1", 0.7, "power2.out")
    fromto(t0 + 1.2, "#end2", "opacity: 0", "opacity: 1", 0.5, "power2.out")
    cue("pop", t0 + 1.2, 0.5)
    # CRTオフ: 白線に収束して消える
    te = t1 - 1.0
    setv(te - 0.02, "#crt", "opacity: 1")
    fromto(te, "#crt", "scaleY: 1, scaleX: 1", "scaleY: 0.004, scaleX: 1", 0.3, "power3.in")
    tw(te + 0.3, 'tl.to("#crt", {scaleX: 0.002, duration: 0.3, ease: "power2.in"}, %T%);')
    cue("sub", te, 1.0)


KIND = {"broll": sc_broll, "kick": sc_kick, "q": sc_q, "nv": sc_nv,
        "tune": sc_tune, "split": sc_split, "senga": sc_senga, "datac": sc_datac,
        "card": sc_card, "ask": sc_ask, "end": sc_end}


TR_DEF = {"tune": "tline", "split": "dark", "senga": "dark", "datac": "tline",
          "ask": "tline", "end": "dark",
          "q": "none", "nv": "none", "broll": "none", "card": "none", "kick": "tline"}


def apply_tr(tr, s, ids):
    t0 = s["start"]
    if tr == "none" or t0 < 0.4:
        return
    if tr == "tline":
        tline_cut(t0, 0.7)
    elif tr == "dark":
        setv(t0 - 0.22, "#tbk", "opacity: 0")
        tw(t0 - 0.22, 'tl.to("#tbk", {opacity: 1, duration: 0.2, ease: "power2.in"}, %T%);')
        tw(t0 + 0.02, 'tl.to("#tbk", {opacity: 0, duration: 0.45, ease: "power2.out"}, %T%);')
        cue("sub", t0 - 0.2, 0.7)


_id_re = re.compile(r'id="([^"]+)"')
for s in SC:
    pre = len(ELS)
    KIND[s["kind"]](s)
    tr = s.get("tr") or TR_DEF[s["kind"]]
    ids = [_id_re.search(e).group(1) for e in ELS[pre:]]
    apply_tr(tr, s, ids)

fromto(0.05, "#stage", "opacity: 0", "opacity: 1", 0.8, "power2.out")
tw(COMP - 1.15, 'tl.to("#stage", {opacity: 0, duration: 0.95, ease: "power1.in"}, %T%);')

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
#tbk { position:absolute; inset:0; z-index:56; background:#05070e; opacity:0; pointer-events:none; }
/* ---------- パネル (放送室) ---------- */
.panel { z-index:10;
  background:radial-gradient(ellipse 130% 100% at 50% 34%, #15213f 0%, #0d1529 56%, #070b16 100%); }
.panel.dark { background:radial-gradient(ellipse 130% 100% at 50% 40%, #0a0d16 0%, #04060c 70%); }
.logo { position:absolute; left:52px; top:42px; z-index:4; font-family:'NotoB'; font-size:30px;
  letter-spacing:.14em; color:#dfe7f2; display:flex; align-items:center; gap:16px; }
.logo .dot { width:16px; height:16px; border-radius:50%; background:#ff4a3c;
  box-shadow:0 0 14px 3px rgba(255,74,60,.75); }
.logo .oa { font-size:19px; letter-spacing:.3em; color:#8e9cb8; border:2px solid #8e9cb8;
  padding:4px 10px 4px 13px; border-radius:4px; margin-left:6px; }
.trk { position:absolute; right:56px; bottom:44px; z-index:4; font-family:'NotoB'; font-size:26px;
  letter-spacing:.3em; color:#8e9cb8; }
/* ---------- 引用モニター ---------- */
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
.biglabel { position:absolute; left:64px; top:128px; font-family:'NotoB'; font-size:52px;
  color:#f2f4f8; background:rgba(10,16,31,.92); border-left:10px solid #4fd8eb;
  padding:16px 38px; box-shadow:0 6px 24px rgba(0,0,0,.5); opacity:0; }
.creditD { position:absolute; top:26px; right:56px; font-family:'NotoBd'; font-size:24px;
  color:rgba(242,244,248,.92); background:rgba(5,8,16,.55); padding:7px 16px; z-index:5; }
/* ---------- tune ---------- */
.tnwrap { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center;
  justify-content:center; gap:40px; padding:0 150px; }
.tnt { text-align:center; font-family:'NotoB'; font-size:88px; line-height:1.5; color:#f2f4f8;
  letter-spacing:.04em; opacity:0; text-shadow:0 0 34px rgba(79,216,235,.3); }
.tnline { width:420px; height:6px; border-radius:3px; transform:scaleX(0);
  background:linear-gradient(90deg, #ff6b4a, #4fd8eb);
  box-shadow:0 0 18px rgba(79,216,235,.6); }
/* ---------- kick ---------- */
.klwrap { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; gap:44px;
  padding:0 140px; }
.klbar { width:10px; height:300px; border-radius:5px; background:#4fd8eb; transform-origin:top;
  transform:scaleY(0); box-shadow:0 0 22px rgba(79,216,235,.7); }
.klt { font-family:'NotoB'; font-size:80px; line-height:1.45; color:#f2f4f8; opacity:0;
  letter-spacing:.04em; }
.fswrap { position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  padding:0 120px; perspective:900px; }
.fst { text-align:center; font-family:'NotoB'; font-size:86px; line-height:1.5; color:#f2f4f8;
  opacity:0; letter-spacing:.04em; }
.fsslot { display:inline-block; position:relative; }
.fsmask { display:inline-block; color:#8e9cb8; background:rgba(142,156,184,.14);
  border-radius:10px; padding:0 14px; }
.fsopen { display:inline-block; color:#ff6b4a; opacity:0; white-space:nowrap;
  text-shadow:0 0 30px rgba(255,107,74,.55); position:absolute; left:50%; top:0;
  transform-origin:center; }
/* ---------- split ---------- */
.dhead { position:absolute; left:0; right:0; top:104px; text-align:center; font-family:'NotoB';
  font-size:66px; color:#f2f4f8; opacity:0; letter-spacing:.05em; }
.spwrap { position:absolute; left:130px; right:130px; top:270px; bottom:150px; display:flex;
  align-items:stretch; gap:0; }
.spcol { flex:1; padding:44px 56px; opacity:0; border-radius:18px; }
.spcol.cn { border:2px solid rgba(255,107,74,.5); background:rgba(255,107,74,.06); margin-right:44px; }
.spcol.jp { border:2px solid rgba(79,216,235,.5); background:rgba(79,216,235,.06); margin-left:44px; }
.sptitle { font-family:'NotoB'; font-size:52px; letter-spacing:.1em; margin-bottom:34px; }
.spcol.cn .sptitle { color:#ff8e73; }
.spcol.jp .sptitle { color:#7ce4f5; }
.sprow { font-family:'NotoBd'; font-size:38px; line-height:1.55; color:#dfe7f2; margin-top:22px;
  opacity:0; padding-left:28px; position:relative; }
.sprow::before { content:''; position:absolute; left:0; top:0.62em; width:12px; height:12px;
  border-radius:50%; background:currentColor; opacity:.55; }
.spmid { position:absolute; left:50%; top:0; bottom:0; width:0; display:flex; align-items:center;
  justify-content:center; }
.spline { position:absolute; top:0; bottom:0; width:3px; margin-left:-1px;
  background:linear-gradient(180deg, rgba(142,156,184,0), #8e9cb8 25%, #8e9cb8 75%, rgba(142,156,184,0));
  transform-origin:top; }
.spvs { position:relative; font-family:'NotoB'; font-size:46px; color:#070b16; background:#f2f4f8;
  width:104px; height:104px; line-height:104px; text-align:center; border-radius:50%;
  box-shadow:0 0 30px rgba(242,244,248,.4); opacity:0; }
/* ---------- senga ---------- */
.sgwrap { position:absolute; left:110px; right:110px; top:120px; bottom:240px; opacity:0; }
.sgwrap svg { width:100%; height:100%; filter:drop-shadow(0 0 7px rgba(238,243,248,.35)); }
.sgcap { position:absolute; left:0; right:0; bottom:104px; text-align:center; font-family:'NotoB';
  font-size:56px; color:#f2f4f8; opacity:0; letter-spacing:.04em;
  text-shadow:0 2px 16px rgba(0,0,0,.8); }
/* ---------- datac ---------- */
.dcnum { position:absolute; left:0; right:0; top:328px; text-align:center; font-family:'NotoB';
  font-size:230px; color:#d9b96a; opacity:0; font-variant-numeric:tabular-nums;
  text-shadow:0 0 44px rgba(217,185,106,.4); }
.dcnum span { font-size:92px; color:#f2f4f8; margin-left:14px; }
.dcsub { position:absolute; left:0; right:0; top:648px; text-align:center; font-family:'NotoB';
  font-size:54px; color:#dfe7f2; opacity:0; }
.cntsrc { position:absolute; left:60px; bottom:40px; font-family:'NotoBd'; font-size:23px;
  color:#8e9cb8; }
/* ---------- card (TRACK扉) ---------- */
.cardov { }
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
/* ---------- ask / end ---------- */
.askt { position:absolute; left:0; right:0; top:26%; text-align:center; font-family:'NotoB';
  font-size:82px; line-height:1.6; color:#f2f4f8; opacity:0; }
.asks { position:absolute; left:0; right:0; top:70%; text-align:center; font-family:'NotoBd';
  font-size:38px; color:#d9b96a; opacity:0; }
.endt { position:absolute; left:0; right:0; top:38%; text-align:center; font-family:'NotoB';
  font-size:84px; color:#f2f4f8; opacity:0; }
.ends { position:absolute; left:0; right:0; top:56%; text-align:center; font-family:'NotoBd';
  font-size:36px; color:#8e9cb8; opacity:0; }
.crt { position:absolute; inset:0; background:#eafcff; opacity:0; transform-origin:center;
  z-index:30; }
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
if FULL:
    (ROOT / "subtitles" / "out" / EP / "sfx_cues.json").write_text(
        json.dumps({"total": COMP, "cues": sorted(CUES, key=lambda c: c["t"])}, ensure_ascii=False),
        encoding="utf-8")
print(f"{EP}: built index.html window {W0}-{W1} ({WDUR}s) els={len(ELS)} tweens={len(TWEENS)} cues={len(CUES)}")
