# -*- coding: utf-8 -*-
"""japan04cX 章ビルダ「症例ファイル(カルテ)」(窓分割対応)。EP_CH env で章選択。
long01(報道)/long02(和紙)/long03(深夜放送)と別系統 (DESIGN04.md):
 - 診療記録の紙 (#f4f2ec+罫線) + インク紺 + スタンプ朱 / 黒背景白線画(senga)
 - パネル: karte(タイプされる記録) case(症例カード) graph(W字曲線) stamp(診断)
   senga rx(処方箋) card(インデックスタブ扉) evid引用フレーム ask end
実績方式: tweenは絶対時刻で内側tlへ、root.fromTo(tl,{time:W0},{time:W1})登録。
"""
import json
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from japan04_chapters import BROLL, CREDIT, TAG, Q as QSPEC  # noqa: E402

NV_PRE = 0.6

EP = os.environ.get("EP_CH") or "japan04c1"
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


rng = random.Random(41)


def page_cut(t, strength=1.0):
    """紙めくり: 白フラッシュ+影のスイープ"""
    setv(t - 0.02, "#pflash", f'opacity: {0.7*strength:.2f}')
    tw(t + 0.02, 'tl.to("#pflash", {opacity: 0, duration: 0.5, ease: "power2.out"}, %T%);')
    cue("glitch", t, strength)


def typein(t0, sel_prefix, n, step=0.05, s=0.5):
    """1文字ずつ表示 (タイプライター)。spans #<prefix>0..n-1"""
    for i in range(n):
        setv(t0 + i * step, f"#{sel_prefix}{i}", "opacity: 1")
        if i % 2 == 0:
            cue("tick", t0 + i * step, s)


def spans(eid, txt):
    return "".join(f'<span class="tc" id="{eid}{i}">{c}</span>' for i, c in enumerate(txt))


TAB = '<div class="tab">CASE FILE <em>No.004</em> — 症例記録「日本ロス」</div>'


def pageno(s):
    p = s.get("pg")
    return f'<div class="pgno">- {p} -</div>' if p else ""


GRADE0 = {"gray": "grayscale(0) brightness(1)", "warm": "saturate(1) sepia(0) brightness(1)"}
GRADE1 = {"gray": "grayscale(1) saturate(.4) brightness(.92)",
          "warm": "saturate(1.14) sepia(.16) brightness(1.03)"}


def qframe(smp, credit=None, tape="TAPE 01"):
    return (f'<div class="lbT"><div class="clipmark"></div><div class="tape">{tape}</div>'
            f'<div class="qtag">{TAG[smp]}</div>'
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
    el_div(f"{qid}o", t0, t1, "qov", qframe(qi["sample"], qi["credit"], qi.get("tape", "記録映像")) + cdivs)
    for i, (dt, _h) in enumerate(caps):
        tin = sp + dt
        fromto(tin, f"#{qid}cap{i}", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.28, "power3.out")
        cue("pop", tin, 0.6)
        if i + 1 < len(caps):
            setv(sp + caps[i + 1][0] - 0.12, f"#{qid}cap{i}", "opacity: 0")
    g = qi.get("grade")
    if g:
        fromto(sp + 0.3, f"#{qid}v", f'filter: "{GRADE0[g]}"', f'filter: "{GRADE1[g]}"', 0.9, "power2.inOut")
    fromto(t0 + 0.02, f"#{qid}v", "scale: 1.04", "scale: 1", 2.2, "power2.out")
    page_cut(t0, 0.9 if abs(t0 - sc_start) < 0.2 else 0.6)


def sc_nv(s):
    t0, t1 = s["start"], s["end"]
    qid = s["q"]
    qs = QSPEC[qid]
    nids = s["nids"]
    caps = qs["caps"]
    assert len(caps) == len(nids), f"{EP}:{qid} caps{len(caps)} != nids{len(nids)}"
    el_video(f"{qid}v", t0, t1, f"{qid}.mp4", NV_PRE, cls="framed")
    cdivs = "".join(f'<div class="qcap" id="{qid}cap{i}">{h}</div>' for i, (_dt, h) in enumerate(caps))
    el_div(f"{qid}o", t0, t1, "qov", qframe(qs["s"], None, qs.get("tape", "記録映像")) + cdivs)
    times = [N[nid]["start"] for nid in nids]
    for i, st in enumerate(times):
        tin = max(t0 + 0.05, st - 0.12)
        fromto(tin, f"#{qid}cap{i}", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.28, "power3.out")
        cue("pop", tin, 0.6)
        if i + 1 < len(times):
            setv(times[i + 1] - 0.25, f"#{qid}cap{i}", "opacity: 0")
    g = qs.get("grade")
    if g:
        fromto(t0 + 0.4, f"#{qid}v", f'filter: "{GRADE0[g]}"', f'filter: "{GRADE1[g]}"', 0.9, "power2.inOut")
    fromto(t0 + 0.02, f"#{qid}v", "scale: 1.04", "scale: 1", 2.2, "power2.out")
    page_cut(t0, 0.7)


def sc_broll(s):
    t0, t1 = s["start"], s["end"]
    bid = s["bg"]
    smp = BROLL[bid][0]
    el_video(f'{s["id"]}v', t0, t1, f"{bid}.mp4", 0.0, cls="framed")
    lab = (f'<div class="biglabel" id="{s["id"]}lab">{s["label"]}</div>' if s.get("label") else "")
    el_div(f'{s["id"]}sc', t0, t1, "qov", qframe(smp, None, s.get("tape", "記録映像")) + lab)
    if s.get("label"):
        fromto(t0 + 0.35, f'#{s["id"]}lab', "x: -30, opacity: 0", "x: 0, opacity: 1", 0.5, "power2.out")
        cue("sub", t0 + 0.35, 0.7)
    page_cut(t0, 0.8)


def sc_kick(s):  # タイプライター1行 or スタンプ
    t0, t1 = s["start"], s["end"]
    k = s.get("kicker")
    if not k:
        raise SystemExit(f"{EP}:{s['id']}: kick には kicker が必要")
    eid = s["id"]
    style = s.get("kstyle") or "type"
    if style == "stampk":
        el_div(f"{eid}p", t0, t1, "panel paper", (
            TAB + pageno(s) +
            f'<div class="skwrap"><div class="skt" id="{eid}k">{k}</div></div>'))
        fromto(t0 + 0.3, f"#{eid}k", "scale: 1.9, opacity: 0, rotation: -5",
               "scale: 1, opacity: 1, rotation: -5", 0.3, "power4.in")
        cue("slam", t0 + 0.6, 0.9)
    else:
        plain = re.sub(r"<[^>]+>", "", k)
        el_div(f"{eid}p", t0, t1, "panel paper", (
            TAB + pageno(s) +
            f'<div class="tkwrap"><div class="tkt" id="{eid}k">{spans(eid, plain)}'
            f'<span class="caret" id="{eid}c"></span></div></div>'))
        typein(t0 + 0.35, eid, len(plain), 0.065, 0.5)
        tw(t0 + 0.3, f'tl.to("#{eid}c", {{opacity: 0, duration: 0.01, repeat: {int((t1-t0)*2)}, yoyo: true, repeatDelay: 0.5}}, %T%);')
        cue("sub", t0 + 0.35, 0.6)


def sc_karte(s):  # カルテ用紙: 項目行がタイプされる (rows=[(label, value)], ナレ行に同期)
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    rows = s["rows"]
    rh = ""
    for i, (lab, val) in enumerate(rows):
        rh += (f'<div class="krow" id="{eid}r{i}"><div class="klab">{lab}</div>'
               f'<div class="kval">{val}</div><div class="kline"></div></div>')
    el_div(f"{eid}p", t0, t1, "panel paper", (
        TAB + pageno(s) +
        f'<div class="khead" id="{eid}h">{s["head"]}</div>'
        f'<div class="kwrap">{rh}</div>'))
    fromto(t0 + 0.3, f"#{eid}h", "y: -18, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    cue("sub", t0 + 0.32, 0.7)
    nids = s["nids"]
    for i in range(len(rows)):
        st = N[nids[min(i, len(nids) - 1)]]["start"] + (0.3 if i < len(nids) else 0.3 + 0.9 * (i - len(nids) + 1))
        fromto(st, f"#{eid}r{i}", "x: -24, opacity: 0", "x: 0, opacity: 1", 0.35, "power2.out")
        cue("tick", st, 0.8)
        cue("tick", st + 0.14, 0.6)


def sc_case(s):  # 症例カード: CASE番号+表組 (video静止風サムネ付き)
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    rows = s["rows"]
    rh = "".join(
        f'<div class="crow" id="{eid}r{i}"><div class="clab">{lab}</div><div class="cval">{val}</div></div>'
        for i, (lab, val) in enumerate(rows))
    el_div(f"{eid}p", t0, t1, "panel paper", (
        TAB + pageno(s) +
        f'<div class="cno" id="{eid}n">{s["no"]}</div>'
        f'<div class="ctit" id="{eid}t">{s["title"]}</div>'
        f'<div class="cwrap" id="{eid}w">{rh}</div>'
        f'<div class="cstamp" id="{eid}s">{s.get("stamp","")}</div>'))
    fromto(t0 + 0.25, f"#{eid}n", "x: -30, opacity: 0", "x: 0, opacity: 1", 0.45, "power3.out")
    fromto(t0 + 0.45, f"#{eid}t", "opacity: 0", "opacity: 1", 0.5, "power2.out")
    cue("sub", t0 + 0.3, 0.8)
    n0 = N[s["nids"][0]]
    for i in range(len(rows)):
        st = n0["start"] + 0.5 + i * 0.55
        fromto(st, f"#{eid}r{i}", "x: -20, opacity: 0", "x: 0, opacity: 1", 0.3, "power2.out")
        cue("tick", st, 0.7)
    if s.get("stamp"):
        n_last = N[s["nids"][-1]]
        st = n_last["start"] + 0.6 * n_last["dur"]
        fromto(st, f"#{eid}s", "scale: 1.9, opacity: 0, rotation: -7",
               "scale: 1, opacity: 1, rotation: -7", 0.28, "power4.in")
        cue("slam", st + 0.28, 0.8)


def sc_graph(s):  # W字曲線 (方眼紙)
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    svg = ('<svg viewBox="0 0 1500 560" fill="none">'
           '<path id="wpath" d="M60 140 C 220 60, 330 70, 430 150 C 540 240, 600 400, 740 430 '
           'C 850 452, 930 330, 1010 250 C 1100 170, 1240 120, 1440 100"'
           ' stroke="#1d2b50" stroke-width="9" stroke-linecap="round"/></svg>')
    labs = [("出発前", 3, 8), ("旅行中<br>ハネムーン期", 20, 2), ("帰国<br>直後", 40, 52),
            ("日本ロスの谷", 58, 80), ("回復期", 82, 30)]
    lh = "".join(
        f'<div class="glab" id="{eid}l{i}" style="left:{x}%;top:{y}%">{tx}</div>'
        for i, (tx, x, y) in enumerate(labs))
    el_div(f"{eid}p", t0, t1, "panel paper grid", (
        TAB + pageno(s) +
        f'<div class="khead" id="{eid}h">{s["head"]}</div>'
        f'<div class="gwrap"><div class="gmask" id="{eid}m">{svg}</div>{lh}</div>'
        f'<div class="gsrc">{s.get("src","")}</div>'))
    fromto(t0 + 0.3, f"#{eid}h", "y: -18, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    fromto(t0 + 0.8, f"#{eid}m", "scaleX: 0", "scaleX: 1", 3.2, "power1.inOut")
    cue("sub", t0 + 0.8, 0.7)
    dur_n = t1 - t0 - 1.4
    for i in range(len(labs)):
        st = t0 + 1.0 + i * (dur_n * 0.72 / len(labs))
        fromto(st, f"#{eid}l{i}", "y: 14, opacity: 0", "y: 0, opacity: 1", 0.35, "power2.out")
        cue("tick", st, 0.7)


def sc_stamp(s):  # 診断スタンプ大
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    el_div(f"{eid}p", t0, t1, "panel paper", (
        TAB + pageno(s) +
        f'<div class="dhead" id="{eid}h">{s.get("head","診断")}</div>'
        f'<div class="bigstamp" id="{eid}s">{s["text"]}</div>'
        f'<div class="dnote" id="{eid}n">{s.get("note","")}</div>'))
    fromto(t0 + 0.3, f"#{eid}h", "opacity: 0", "opacity: 1", 0.4, "power2.out")
    n0 = N[s["nids"][0]]
    st = n0["start"] + min(1.8, 0.45 * n0["dur"])
    fromto(st, f"#{eid}s", "scale: 2.1, opacity: 0, rotation: -6",
           "scale: 1, opacity: 1, rotation: -6", 0.3, "power4.in")
    cue("slam", st + 0.3, 1.0)
    if s.get("note"):
        fromto(st + 1.0, f"#{eid}n", "y: 14, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")


# ---------------------------------------------------------------- senga (黒背景白線画)
def _fig(x, y, sc=1.0, pose="stand", flip=False):
    fl = " scale(-1,1)" if flip else ""
    if pose == "sit":
        body = ('<circle cx="0" cy="-150" r="26"/>'
                '<path d="M0 -122 C -2 -92, -2 -70, 0 -52 L 42 -52 L 42 0"/>'
                '<path d="M0 -52 L -6 0"/>'
                '<path d="M-2 -110 C -22 -98, -30 -84, -32 -68"/>'
                '<path d="M2 -110 C 20 -100, 28 -88, 30 -72"/>')
    elif pose == "suitcase":
        body = ('<circle cx="0" cy="-168" r="26"/>'
                '<path d="M0 -140 C -4 -96, -4 -60, -8 0"/>'
                '<path d="M0 -140 C 8 -96, 10 -60, 12 0"/>'
                '<path d="M-2 -126 C -24 -112, -34 -96, -38 -78"/>'
                '<path d="M2 -126 C 28 -114, 40 -96, 46 -66"/>'
                '<rect x="34" y="-66" width="56" height="78" rx="8"/>'
                '<path d="M50 -66 v-14 h24 v14"/>')
    else:
        body = ('<circle cx="0" cy="-168" r="26"/>'
                '<path d="M0 -140 C -4 -96, -4 -60, -8 0"/>'
                '<path d="M0 -140 C 8 -96, 10 -60, 12 0"/>'
                '<path d="M-2 -126 C -24 -112, -34 -96, -38 -78"/>'
                '<path d="M2 -126 C 26 -112, 36 -96, 40 -78"/>')
    return f'<g transform="translate({x},{y}) scale({sc}){fl}">{body}</g>'


ART = {
    # 部屋の東京化: 机+椅子の人物 + 壁のネオンサイン(TOKYO/ラーメン鉢)
    "room": (
        '<svg viewBox="0 0 1700 760" fill="none" stroke="#eef3f8" stroke-width="6" stroke-linecap="round">'
        '<path d="M120 720 H 1580" stroke-width="4" opacity="0.5"/>'
        '<rect x="980" y="420" width="420" height="300" rx="6" opacity="0.8"/>'
        '<path d="M1040 520 h300 M1040 600 h300" opacity="0.4"/>'
        + _fig(1180, 720, 1.5, "sit", flip=True) +
        '<rect x="330" y="150" width="360" height="130" rx="18" stroke="#7ce4f5" stroke-width="7"/>'
        '<text x="510" y="238" text-anchor="middle" fill="#7ce4f5" stroke="none"'
        ' font-family="Arial Black" font-size="74" letter-spacing="8">TOKYO</text>'
        '<g transform="translate(1050,210)" stroke="#ff8e73" stroke-width="7">'
        '<path d="M-90 0 a90 90 0 0 1 180 0 Z"/>'
        '<path d="M-50 -34 q 8 -40 24 -58 M0 -40 q 4 -44 16 -64 M48 -32 q 10 -36 28 -52"/></g>'
        '</svg>'),
    # 帰国の空港: スーツケースの人物 + 飛行機(帰路)
    "airport": (
        '<svg viewBox="0 0 1700 760" fill="none" stroke="#eef3f8" stroke-width="6" stroke-linecap="round">'
        '<path d="M120 720 H 1580" stroke-width="4" opacity="0.5"/>'
        + _fig(640, 720, 1.7, "suitcase") +
        '<g transform="translate(1150,240) rotate(-14)" opacity="0.9">'
        '<path d="M-120 0 L 90 0 L 150 -26 L 96 6 L -34 24 Z"/>'
        '<path d="M-10 2 L -52 44 L -24 46 Z"/>'
        '<path d="M-6 -2 L -40 -40 L -12 -40 Z"/></g>'
        '<path d="M900 160 q 60 -36 120 0" opacity="0.35"/>'
        '<path d="M1340 420 q 50 -30 100 0" opacity="0.35"/>'
        '</svg>'),
}


def sc_senga(s):
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    art = ART[s["art"]]
    cap = s.get("cap", "")
    el_div(f"{eid}p", t0, t1, "panel dark", (
        f'<div class="sgwrap" id="{eid}a">{art}</div>'
        f'<div class="sgcap" id="{eid}c">{cap}</div>'))
    fromto(t0 + 0.25, f"#{eid}a", 'opacity: 0, scale: 1.05, filter: "blur(6px)"',
           'opacity: 1, scale: 1, filter: "blur(0px)"', 0.7, "power2.out")
    cue("sub", t0 + 0.3, 0.8)
    if cap:
        fromto(t0 + 0.9, f"#{eid}c", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.45, "power2.out")
        cue("pop", t0 + 0.95, 0.6)
    fromto(t0 + 0.9, f"#{eid}a", "scale: 1", "scale: 1.045", max(2.0, t1 - t0 - 1.0), "none")


def sc_rx(s):  # 処方箋
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    rows = s["rows"]
    rh = "".join(f'<div class="rxrow" id="{eid}r{i}"><span class="rxn">{i+1}</span>{tx}</div>'
                 for i, tx in enumerate(rows))
    el_div(f"{eid}p", t0, t1, "panel paper", (
        TAB + pageno(s) +
        f'<div class="rxmark" id="{eid}m">Rx</div>'
        f'<div class="khead" id="{eid}h">{s["head"]}</div>'
        f'<div class="rxwrap">{rh}</div>'))
    fromto(t0 + 0.25, f"#{eid}m", "scale: 1.5, opacity: 0", "scale: 1, opacity: 1", 0.5, "back.out(1.8)")
    fromto(t0 + 0.4, f"#{eid}h", "y: -18, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    cue("sub", t0 + 0.4, 0.8)
    nids = s["nids"]
    for i in range(len(rows)):
        j = min(i + 1, len(nids) - 1)
        over = (i + 1) - j  # nids が足りない分は同一ナレ内で時間差
        st = N[nids[j]]["start"] + 0.25 + over * 0.55 * N[nids[j]]["dur"]
        fromto(st, f"#{eid}r{i}", "x: -24, opacity: 0", "x: 0, opacity: 1", 0.4, "power2.out")
        cue("tick", st, 0.8)


def sc_card(s):  # 章扉: インデックスタブ
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    if s.get("bg"):
        el_video(f"{eid}v", t0, t1, f'{s["bg"]}.mp4', 0.0)
        smp = BROLL[s["bg"]][0]
        credit = f'<div class="creditD">{CREDIT[smp]}</div>'
        scrim = '<div class="cdscrim"></div>'
        pcls = "qov"
    else:
        credit = scrim = ""
        pcls = "panel paper"
    el_div(f"{eid}o", t0, t1, pcls, (
        scrim + credit +
        f'<div class="ixghost" id="{eid}g">{s["gno"]}</div>'
        f'<div class="ixtab" id="{eid}b">{s["no"]}</div>'
        f'<div class="ixtitle" id="{eid}t">{s["title"]}</div>'
        + (f'<div class="ixsub" id="{eid}s">{s["sub"]}</div>' if s.get("sub") else "")))
    cue("riser", max(0.0, t0 - 1.3), 1.0, 1.3)
    page_cut(t0, 1.0)
    fromto(t0 + 0.2, f"#{eid}b", "x: -70, opacity: 0", "x: 0, opacity: 1", 0.5, "power3.out")
    fromto(t0 + 0.35, f"#{eid}g", "scale: 1.3, opacity: 0", "scale: 1, opacity: 0.16", 0.9, "power2.out")
    fromto(t0 + 0.5, f"#{eid}t", 'opacity: 0, y: 24, filter: "blur(8px)"',
           'opacity: 1, y: 0, filter: "blur(0px)"', 0.6, "power2.out")
    cue("slam", t0 + 0.72, 0.8)
    cue("sub", t0 + 0.78, 1.0)
    if s.get("sub"):
        fromto(t0 + 1.2, f"#{eid}s", "opacity: 0", "opacity: 1", 0.45, "power2.out")


def sc_q(s):
    for qid, qi in Q.items():
        if s["start"] - 0.01 <= qi["beat_start"] < s["end"]:
            quote_block(qid, s["start"])


def sc_ask(s):
    t0, t1 = s["start"], s["end"]
    el_div("askp", t0, t1, "panel paper", (
        TAB +
        '<div class="askt" id="ask1">あなたの日常が<br>誰かの「<em>特効薬</em>」かもしれない</div>'
        '<div class="asks" id="ask2">▼ 日本を離れて「恋しくなったもの」、コメントで教えてください</div>'))
    fromto(t0 + 0.3, "#ask1", 'opacity: 0, y: 24, filter: "blur(8px)"',
           'opacity: 1, y: 0, filter: "blur(0px)"', 0.7, "power2.out")
    cue("sub", t0 + 0.35, 0.8)
    fromto(t0 + 1.5, "#ask2", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
    cue("pop", t0 + 1.5, 0.6)
    tw(t0 + 2.1, 'tl.to("#ask2", {y: 8, duration: 0.5, ease: "sine.inOut", repeat: 5, yoyo: true}, %T%);')


def sc_end(s):  # カルテを閉じる
    t0, t1 = s["start"], s["end"]
    el_div("endp", t0, t1, "panel paper", (
        TAB +
        '<div class="endt" id="end1">ご視聴 ありがとうございました</div>'
        '<div class="ends" id="end2">チャンネル登録で、次の症例ファイルをお見逃しなく</div>'
        '<div class="fcover" id="fcov"><div class="fcttl">CASE FILE<br><span>No.004 — 日本ロス</span></div>'
        '<div class="fcstamp">CLOSED</div></div>'))
    fromto(t0 + 0.3, "#end1", "opacity: 0", "opacity: 1", 0.7, "power2.out")
    fromto(t0 + 1.2, "#end2", "opacity: 0", "opacity: 1", 0.5, "power2.out")
    cue("pop", t0 + 1.2, 0.5)
    te = t1 - 1.3
    fromto(te, "#fcov", "xPercent: -104", "xPercent: 0", 0.55, "power3.inOut")
    cue("slam", te + 0.55, 1.0)


KIND = {"broll": sc_broll, "kick": sc_kick, "q": sc_q, "nv": sc_nv,
        "karte": sc_karte, "case": sc_case, "graph": sc_graph, "stamp": sc_stamp,
        "senga": sc_senga, "rx": sc_rx, "card": sc_card, "ask": sc_ask, "end": sc_end}

TR_DEF = {"karte": "page", "case": "page", "graph": "dark", "stamp": "page", "senga": "dark",
          "rx": "page", "ask": "page", "end": "page", "kick": "page",
          "q": "none", "nv": "none", "broll": "none", "card": "none"}


def apply_tr(tr, s, ids):
    t0 = s["start"]
    if tr == "none" or t0 < 0.4:
        return
    if tr == "page":
        page_cut(t0, 0.7)
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
#tbk { position:absolute; inset:0; z-index:56; background:#0a0c12; opacity:0; pointer-events:none; }
/* ---------- 紙パネル ---------- */
.panel.paper { z-index:10; background:
  repeating-linear-gradient(0deg, rgba(90,110,150,0) 0 66px, rgba(90,110,150,.14) 66px 68px),
  radial-gradient(ellipse 140% 110% at 50% 30%, #f7f4ea 0%, #f2eee0 60%, #e8e2cf 100%); }
.panel.paper::after { content:''; position:absolute; inset:0; pointer-events:none;
  box-shadow:inset 0 0 160px rgba(120,104,60,.16); }
.panel.grid { background:
  repeating-linear-gradient(0deg, rgba(90,110,150,.1) 0 1px, transparent 1px 48px),
  repeating-linear-gradient(90deg, rgba(90,110,150,.1) 0 1px, transparent 1px 48px),
  radial-gradient(ellipse 140% 110% at 50% 30%, #f7f4ea 0%, #f0ecdd 100%); }
.panel.dark { z-index:10;
  background:radial-gradient(ellipse 130% 100% at 50% 40%, #0a0d16 0%, #04060c 70%); }
.tab { position:absolute; right:60px; top:0; z-index:4; font-family:'NotoBd'; font-size:24px;
  letter-spacing:.1em; color:#f4f2ec; background:#1d2b50; padding:12px 26px 10px;
  border-radius:0 0 10px 10px; }
.tab em { color:#f0b9ae; }
.pgno { position:absolute; left:50%; bottom:28px; transform:translateX(-50%);
  font-family:'NotoBd'; font-size:24px; color:#8d8468; }
/* ---------- 引用フレーム (資料映像) ---------- */
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
.biglabel { position:absolute; left:64px; top:128px; font-family:'NotoB'; font-size:52px;
  color:#1d2b50; background:rgba(242,238,224,.95); border-left:10px solid #c03b2d;
  padding:16px 38px; box-shadow:0 6px 24px rgba(40,30,8,.3); opacity:0; }
.creditD { position:absolute; top:26px; right:56px; font-family:'NotoBd'; font-size:24px;
  color:rgba(242,244,248,.92); background:rgba(10,12,18,.55); padding:7px 16px; z-index:5; }
/* ---------- karte ---------- */
.khead { position:absolute; left:0; right:0; top:110px; text-align:center; font-family:'NotoB';
  font-size:62px; color:#1d2b50; opacity:0; letter-spacing:.06em; }
.kwrap { position:absolute; left:250px; right:250px; top:290px; }
.krow { position:relative; margin-top:58px; opacity:0; }
.klab { display:inline-block; font-family:'NotoB'; font-size:40px; color:#f4f2ec; background:#2b5c8a;
  padding:8px 24px; border-radius:6px; margin-right:36px; vertical-align:middle; }
.kval { display:inline-block; font-family:'NotoB'; font-size:48px; color:#1d2b50;
  vertical-align:middle; line-height:1.4; }
.kline { position:absolute; left:0; right:0; bottom:-14px; height:2px; background:rgba(29,43,80,.25); }
/* ---------- case ---------- */
.cno { position:absolute; left:150px; top:120px; font-family:'NotoB'; font-size:56px;
  letter-spacing:.3em; color:#f4f2ec; background:#c03b2d; padding:12px 34px; border-radius:8px;
  opacity:0; }
.ctit { position:absolute; left:150px; top:244px; font-family:'NotoB'; font-size:74px;
  color:#1d2b50; opacity:0; }
.cwrap { position:absolute; left:160px; right:160px; top:400px; }
.crow { display:flex; margin-top:38px; opacity:0; border-bottom:2px solid rgba(29,43,80,.2);
  padding-bottom:16px; }
.clab { width:360px; font-family:'NotoB'; font-size:40px; color:#2b5c8a; }
.cval { flex:1; font-family:'NotoB'; font-size:42px; color:#1d2b50; line-height:1.4; }
.cstamp { position:absolute; right:170px; top:150px; font-family:'SerifJP'; font-weight:900;
  font-size:72px; color:#c03b2d; border:7px solid #c03b2d; border-radius:10px; padding:10px 34px;
  transform:rotate(-7deg); background:rgba(192,59,45,.05); opacity:0; }
/* ---------- graph ---------- */
.gwrap { position:absolute; left:180px; right:180px; top:280px; bottom:160px; }
.gmask { position:absolute; inset:0; transform-origin:left; }
.gmask svg { width:100%; height:100%; }
.glab { position:absolute; font-family:'NotoB'; font-size:36px; color:#1d2b50; opacity:0;
  text-align:center; transform:translateX(-50%); line-height:1.35; }
.glab:nth-child(5) { color:#c03b2d; }
.gsrc { position:absolute; left:60px; bottom:36px; font-family:'NotoBd'; font-size:23px;
  color:#8d8468; }
/* ---------- stamp ---------- */
.dhead { position:absolute; left:0; right:0; top:170px; text-align:center; font-family:'NotoB';
  font-size:58px; color:#1d2b50; opacity:0; }
.bigstamp { position:absolute; left:50%; top:40%; transform:translateX(-50%);
  font-family:'SerifJP'; font-weight:900; font-size:110px; color:#c03b2d; white-space:nowrap;
  border:12px solid #c03b2d; border-radius:16px; padding:26px 70px; background:rgba(192,59,45,.05);
  opacity:0; }
.dnote { position:absolute; left:0; right:0; top:72%; text-align:center; font-family:'NotoBd';
  font-size:38px; color:#5a5340; opacity:0; }
/* ---------- kick ---------- */
.tkwrap { position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  padding:0 130px; }
.tkt { font-family:'NotoB'; font-size:82px; color:#1d2b50; letter-spacing:.04em; line-height:1.5;
  text-align:center; }
.tc { opacity:0; }
.caret { display:inline-block; width:8px; height:0.95em; background:#c03b2d; margin-left:10px;
  vertical-align:-0.12em; }
.skwrap { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; }
.skt { font-family:'SerifJP'; font-weight:900; font-size:96px; color:#c03b2d;
  border:10px solid #c03b2d; border-radius:14px; padding:20px 60px; transform:rotate(-5deg);
  background:rgba(192,59,45,.05); opacity:0; }
/* ---------- senga ---------- */
.sgwrap { position:absolute; left:110px; right:110px; top:120px; bottom:240px; opacity:0; }
.sgwrap svg { width:100%; height:100%; filter:drop-shadow(0 0 7px rgba(238,243,248,.35)); }
.sgcap { position:absolute; left:0; right:0; bottom:104px; text-align:center; font-family:'NotoB';
  font-size:56px; color:#f2f4f8; opacity:0; letter-spacing:.04em;
  text-shadow:0 2px 16px rgba(0,0,0,.8); }
/* ---------- rx ---------- */
.rxmark { position:absolute; left:150px; top:104px; font-family:'SerifJP'; font-weight:900;
  font-size:120px; color:#2b5c8a; opacity:0; }
.rxwrap { position:absolute; left:250px; right:200px; top:320px; }
.rxrow { font-family:'NotoB'; font-size:52px; color:#1d2b50; margin-top:52px; opacity:0;
  line-height:1.45; }
.rxn { display:inline-block; width:64px; height:64px; line-height:64px; text-align:center;
  background:#2b5c8a; color:#f4f2ec; border-radius:50%; font-size:38px; margin-right:28px;
  vertical-align:4px; }
/* ---------- card (章扉) ---------- */
.cdscrim { position:absolute; inset:0;
  background:linear-gradient(0deg, rgba(10,12,18,.8) 0%, rgba(10,12,18,.42) 45%, rgba(10,12,18,.22) 100%); }
.ixghost { position:absolute; right:90px; top:44%; transform:translateY(-50%);
  font-family:'NotoB'; font-size:560px; color:#c03b2d; opacity:0; }
.qov .ixghost { color:#f2eee0; }
.ixtab { position:absolute; left:150px; top:330px; font-family:'NotoB'; font-size:46px;
  letter-spacing:.3em; color:#f4f2ec; background:#c03b2d; padding:14px 36px; border-radius:8px;
  opacity:0; }
.ixtitle { position:absolute; left:146px; top:452px; font-family:'NotoB'; font-size:94px;
  opacity:0; letter-spacing:.03em; }
.panel .ixtitle { color:#1d2b50; }
.qov .ixtitle { color:#f2f4f8; text-shadow:0 4px 30px rgba(0,0,0,.7); }
.ixsub { position:absolute; left:152px; top:600px; font-family:'NotoBd'; font-size:38px;
  opacity:0; }
.panel .ixsub { color:#5a5340; }
.qov .ixsub { color:#cfd6e4; }
/* ---------- ask / end ---------- */
.askt { position:absolute; left:0; right:0; top:26%; text-align:center; font-family:'NotoB';
  font-size:82px; line-height:1.6; color:#1d2b50; opacity:0; }
.asks { position:absolute; left:0; right:0; top:70%; text-align:center; font-family:'NotoBd';
  font-size:38px; color:#8a5a28; opacity:0; }
.endt { position:absolute; left:0; right:0; top:38%; text-align:center; font-family:'NotoB';
  font-size:84px; color:#1d2b50; opacity:0; }
.ends { position:absolute; left:0; right:0; top:56%; text-align:center; font-family:'NotoBd';
  font-size:36px; color:#8d8468; opacity:0; }
.fcover { position:absolute; inset:0; z-index:30; background:#8d6e4e;
  background:linear-gradient(135deg, #96785a 0%, #85643f 100%); transform:translateX(-104%);
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:60px; }
.fcttl { font-family:'NotoB'; font-size:92px; color:#f4ecd9; text-align:center; line-height:1.4;
  letter-spacing:.14em; }
.fcttl span { font-size:48px; color:#e3d2ae; }
.fcstamp { font-family:'SerifJP'; font-weight:900; font-size:76px; color:#c03b2d;
  border:9px solid #c03b2d; border-radius:12px; padding:10px 44px; transform:rotate(-8deg); }
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
if FULL:
    (ROOT / "subtitles" / "out" / EP / "sfx_cues.json").write_text(
        json.dumps({"total": COMP, "cues": sorted(CUES, key=lambda c: c["t"])}, ensure_ascii=False),
        encoding="utf-8")
print(f"{EP}: built index.html window {W0}-{W1} ({WDUR}s) els={len(ELS)} tweens={len(TWEENS)} cues={len(CUES)}")
