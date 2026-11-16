# -*- coding: utf-8 -*-
"""japan02cX 章ビルダ v2「紀行手記」(窓分割対応)。EP_CH env で章選択。
long01系(黒背景+赤/金パネル)と完全に別デザイン:
 - パネルは生成りの和紙 (#f0e8d5) + 墨文字 (#231c10) + 朱 (#b3402e)
 - 縦書き (tate/tatek/card章題/ask) を多用、図解は 短冊/財布アレイ/絵巻/道のり
 - 引用は上下の和紙帯でフレーム、字幕は帯上の墨文字
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
from japan02_chapters import BROLL, CREDIT, TAG, Q as QSPEC  # noqa: E402

NV_PRE = 0.6  # extract_quotes.NV_PRE と一致

EP = os.environ.get("EP_CH") or "japan02c1"
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


rng = random.Random(11)


def softcut(t, strength=1.0):
    """称賛トーン: 暖色の和紙フラッシュでつなぐ"""
    setv(t, "#flash", f'opacity: {0.46*strength:.2f}')
    tw(t + 0.04, f'tl.to("#flash", {{opacity: 0, duration: {0.55+0.15*strength:.2f}, ease: "power2.out"}}, %T%);')
    cue("glitch", t, strength)  # SFXは鈴+空気スウェル


# 落款 (全和紙パネル共通の隅印)
RAKKAN = '<div class="rk">日本<br>紀行</div>'

GRADE0 = {
    "gray": "grayscale(0) saturate(1) contrast(1) brightness(1)",
    "warm": "saturate(1) sepia(0) contrast(1) brightness(1)",
    "dream": "saturate(1) sepia(0) contrast(1) brightness(1)",
    "cold": "saturate(1) hue-rotate(0deg) brightness(1) contrast(1)",
}
GRADE1 = {
    "gray": "grayscale(1) saturate(0.35) contrast(1.08) brightness(0.9)",
    "warm": "saturate(1.15) sepia(0.18) contrast(1.02) brightness(1.04)",
    "dream": "saturate(1.22) sepia(0.24) contrast(0.98) brightness(1.07)",
    "cold": "saturate(0.62) hue-rotate(-10deg) brightness(0.94) contrast(1.06)",
}


def qframe(smp, credit=None):
    """引用フレーム: 上下の和紙帯 + 左上タグ + 右上クレジット"""
    return ('<div class="lbT"><div class="qtag">' + TAG[smp] + '</div>'
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
        fromto(tin, f"#{qid}cap{i}", "y: 20, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
        cue("pop", tin, 0.6)
        if i + 1 < len(caps):
            setv(sp + caps[i + 1][0] - 0.12, f"#{qid}cap{i}", "opacity: 0")
    g = qi.get("grade")
    if g:
        fromto(sp + 0.3, f"#{qid}v", f'filter: "{GRADE0[g]}"', f'filter: "{GRADE1[g]}"', 0.9, "power2.inOut")
        if g == "gray":
            cue("heart", sp + 0.5, 1.0, min(6.0, qi["adur"]))
    fromto(t0 + 0.02, f"#{qid}v", "scale: 1.05", "scale: 1", 2.2, "power2.out")
    softcut(t0, 0.9 if abs(t0 - sc_start) < 0.2 else 0.6)


def sc_nv(s):
    """ナレ引用: 映像ミュート+和紙帯の字幕(ナレ行開始に同期)"""
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
        fromto(tin, f"#{qid}cap{i}", "y: 20, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
        cue("pop", tin, 0.6)
        if i + 1 < len(times):
            setv(times[i + 1] - 0.25, f"#{qid}cap{i}", "opacity: 0")
    g = qs.get("grade")
    if g:
        fromto(t0 + 0.4, f"#{qid}v", f'filter: "{GRADE0[g]}"', f'filter: "{GRADE1[g]}"', 0.9, "power2.inOut")
        if g == "gray":
            cue("heart", t0 + 0.6, 1.0, min(6.0, max(1.5, t1 - t0 - 1.0)))
    fromto(t0 + 0.02, f"#{qid}v", "scale: 1.05", "scale: 1", 2.2, "power2.out")
    softcut(t0, 0.7)


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
    softcut(t0, 0.8)


# kick 2スタイル輪番: tatek=右端の縦書き一行 / fude=明朝+朱の筆点
KICK_STYLES = ["tatek", "fude"]
_ks_i = [0]


def _chars(txt):
    return None if "<" in txt else list(txt)


def sc_kick(s):
    t0, t1 = s["start"], s["end"]
    k = s.get("kicker")
    if not k:
        raise SystemExit(f"{EP}:{s['id']}: kick には必ず kicker テキストを付ける")
    eid = s["id"]
    style = s.get("kstyle") or KICK_STYLES[_ks_i[0] % len(KICK_STYLES)]
    _ks_i[0] += 1
    if style == "tatek":  # 右端の縦書き (一文字ずつ上から淡入 + 朱の添え線)
        chars = _chars(k) or [k]
        spans = "".join(f'<span class="tkc" id="{eid}c{i}">{c}</span>' for i, c in enumerate(chars))
        el_div(f"{eid}p", t0, t1, "panel", (
            f'<div class="tkwrap"><div class="tkline" id="{eid}l"></div>'
            f'<div class="tkt" id="{eid}k">{spans}</div></div>' + RAKKAN))
        n = len(chars)
        step = min(0.085, 1.1 / max(n, 1))
        for i in range(n):
            fromto(t0 + 0.3 + i * step, f"#{eid}c{i}",
                   'opacity: 0, y: -12, filter: "blur(5px)"',
                   'opacity: 1, y: 0, filter: "blur(0px)"', 0.45, "power2.out")
        fromto(t0 + 0.25, f"#{eid}l", "scaleY: 0", "scaleY: 1", 0.6, "power2.inOut")
        cue("sub", t0 + 0.3, 0.7)
    else:  # fude: 中央明朝 + 先行する朱の筆点
        el_div(f"{eid}p", t0, t1, "panel", (
            f'<div class="fdwrap"><div class="fdot" id="{eid}d"></div>'
            f'<div class="fdt" id="{eid}k">{k}</div></div>' + RAKKAN))
        fromto(t0 + 0.22, f"#{eid}d", "scale: 0, opacity: 0", "scale: 1, opacity: 1", 0.4, "back.out(2.2)")
        cue("pop", t0 + 0.26, 0.6)
        fromto(t0 + 0.42, f"#{eid}k",
               'opacity: 0, letterSpacing: "0.3em", filter: "blur(10px)"',
               'opacity: 1, letterSpacing: "0.08em", filter: "blur(0px)"', 0.7, "power2.out")
        cue("sub", t0 + 0.45, 0.8)


def sc_tate(s):  # 縦書きテーゼ
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    cols = s["text"].split("<br>")
    ch = "".join(f'<div class="ttcol" id="{eid}col{i}">{c}</div>' for i, c in enumerate(cols))
    el_div(f"{eid}p", t0, t1, "panel", f'<div class="tatew">{ch}</div>' + RAKKAN)
    for i in range(len(cols)):  # 右の列から順に (vertical-rl は右が先頭)
        fromto(t0 + 0.3 + i * 0.5, f"#{eid}col{i}",
               'opacity: 0, y: 26, filter: "blur(9px)"',
               'opacity: 1, y: 0, filter: "blur(0px)"', 0.8, "power2.out")
    cue("sub", t0 + 0.35, 0.9)


def sc_tanzaku(s):  # 短冊4枚
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    rows = s["rows"]
    th = "".join(
        f'<div class="tz" id="{eid}r{i}"><div class="tzin">'
        f'<div class="tztag">{tag}</div><div class="tztx">{tx}</div></div>'
        f'<div class="tzpin"></div></div>'
        for i, (tag, tx) in enumerate(rows))
    el_div(f"{eid}p", t0, t1, "panel", (
        f'<div class="dhead" id="{eid}h">{s["head"]}</div>'
        f'<div class="tzrow">{th}</div>' + RAKKAN))
    fromto(t0 + 0.3, f"#{eid}h", "y: -22, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    n = N[s["nids"][0]]
    for i in range(len(rows)):
        tt = n["start"] + 1.2 + i * ((n["dur"] - 1.2) / len(rows))
        fromto(tt, f"#{eid}r{i}", "y: -46, opacity: 0, rotation: -1.2", "y: 0, opacity: 1, rotation: 0",
               0.5, "power2.out")
        cue("tick", tt, 0.8)


def sc_fuda(s):  # 定義カード (木札)
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    el_div(f"{eid}p", t0, t1, "panel", (
        f'<div class="fuda" id="{eid}f"><div class="fudat">{s["title"]}</div>'
        f'<div class="fudab">{s["body"]}</div></div>'
        f'<div class="dnote" id="{eid}n">{s["note"]}</div>' + RAKKAN))
    fromto(t0 + 0.35, f"#{eid}f", "y: -40, opacity: 0, rotation: 0.8", "y: 0, opacity: 1, rotation: 0",
           0.55, "power2.out")
    cue("tick", t0 + 0.4, 0.9)
    fromto(t0 + 1.6, f"#{eid}n", "opacity: 0", "opacity: 1", 0.45, "power2.out")


WALLET = ('<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3">'
          '<rect x="6" y="14" width="36" height="24" rx="4"/>'
          '<path d="M6 20 h36"/><circle cx="33" cy="29" r="3" fill="currentColor"/></svg>')


def sc_wallets(s):  # 落とし物: 財布10個のうち7個が点灯
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    wl = "".join(
        f'<div class="wl" id="{eid}w{i}">{WALLET}<div class="wlg" id="{eid}g{i}">{WALLET}</div></div>'
        for i in range(10))
    el_div(f"{eid}p", t0, t1, "panel", (
        '<div class="dhead" id="wh">東京で1年間に届いた<em>現金</em></div>'
        '<div class="wnum" id="wn">約45<span>億円</span></div>'
        f'<div class="wrow">{wl}</div>'
        '<div class="wlab" id="wlb">約<em>7割</em>が 持ち主の元へ</div>'
        '<div class="cntsrc">出典: 警視庁 遺失物取扱状況(令和7年) ※現金の遺失者返還割合より</div>' + RAKKAN))
    fromto(t0 + 0.3, "#wh", "y: -22, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    fromto(t0 + 0.9, "#wn", 'scale: 1.12, opacity: 0, filter: "blur(8px)"',
           'scale: 1, opacity: 1, filter: "blur(0px)"', 0.7, "power2.out")
    cue("count", t0 + 0.9, 0.8, 0.7)
    for i in range(10):
        fromto(t0 + 1.3 + i * 0.08, f"#{eid}w{i}", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.3, "power2.out")
    n2 = N[s["nids"][1]]["start"]
    for i in range(7):
        tt = n2 + 0.3 + i * 0.28
        fromto(tt, f"#{eid}g{i}", "opacity: 0, scale: 0.7", "opacity: 1, scale: 1", 0.28, "back.out(1.8)")
        cue("tick", tt, 0.7)
    fromto(n2 + 0.3 + 7 * 0.28, "#wlb", "y: 18, opacity: 0", "y: 0, opacity: 1", 0.45, "power3.out")
    cue("pop", n2 + 0.3 + 7 * 0.28, 0.8)


def sc_emaki(s):  # 誠実の連鎖: 右→左の筆線に3つの結び目
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    nodes = [("届ける", "拾った人が 窓口へ"), ("記録する", "駅が預かり 追跡する"), ("返す", "持ち主の 元へ")]
    nh = "".join(
        f'<div class="emn" id="{eid}n{i}" style="right:{10+i*30}%">'
        f'<div class="emnc">{nm}</div><div class="emnd">{ds}</div></div>'
        for i, (nm, ds) in enumerate(nodes))
    el_div(f"{eid}p", t0, t1, "panel", (
        '<div class="dhead" id="emh">安心が生まれる<em>仕組み</em></div>'
        f'<div class="embrush" id="{eid}b"></div>' + nh +
        f'<div class="emstamp" id="{eid}st">信頼の連鎖</div>' + RAKKAN))
    fromto(t0 + 0.3, "#emh", "y: -22, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    fromto(t0 + 0.8, f"#{eid}b", "scaleX: 0", "scaleX: 1", 2.6, "power1.inOut")
    for i, dt in enumerate([1.0, 2.0, 3.0]):
        fromto(t0 + dt, f"#{eid}n{i}", "scale: 0.86, opacity: 0", "scale: 1, opacity: 1", 0.45, "power2.out")
        cue("pop", t0 + dt, 0.8)
    n2 = N[s["nids"][1]]["start"] if len(s["nids"]) > 1 else t0 + 4.2
    fromto(n2 + 0.8, f"#{eid}st", "scale: 1.5, opacity: 0, rotation: -7",
           "scale: 1, opacity: 1, rotation: -7", 0.4, "power3.out")
    cue("slam", n2 + 1.2, 0.6)


def sc_michi(s):  # 道のり: 曲線の道 + 4つの立て札
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    stops = s["stops"]
    path = ('<svg class="miline" viewBox="0 0 1700 420" fill="none">'
            '<path d="M30 320 C 420 180, 760 390, 1100 240 S 1600 120, 1670 150"'
            ' stroke="#8a7b57" stroke-width="7" stroke-dasharray="2 14" stroke-linecap="round"/></svg>')
    xs = [4, 29, 55, 80]
    ys = [52, 36, 50, 30]
    sh = "".join(
        f'<div class="mist" id="{eid}s{i}" style="left:{xs[i]}%;top:{ys[i]}%">'
        f'<div class="midot"></div><div class="mitag">{tag}</div><div class="midesc">{ds}</div></div>'
        for i, (tag, ds) in enumerate(stops))
    el_div(f"{eid}p", t0, t1, "panel", (
        '<div class="dhead" id="mih">旅は こう変わった</div>'
        f'<div class="miwrap"><div class="mimask" id="{eid}m">{path}</div>{sh}</div>' + RAKKAN))
    fromto(t0 + 0.3, "#mih", "y: -22, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    fromto(t0 + 0.7, f"#{eid}m", "scaleX: 0", "scaleX: 1", 3.4, "power1.inOut")
    dur_n = (t1 - t0 - 1.6)
    for i in range(len(stops)):
        tt = t0 + 0.9 + i * (dur_n / len(stops)) * 0.82
        fromto(tt, f"#{eid}s{i}", "y: 22, opacity: 0", "y: 0, opacity: 1", 0.45, "power2.out")
        cue("tick", tt, 0.7)


def sc_card(s):  # 章扉: 映像 + 右端の和紙帯に縦書き章題 + 漢数字ゴースト
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    if s.get("bg"):
        smp = BROLL[s["bg"]][0]
        el_video(f"{eid}v", t0, t1, f'{s["bg"]}.mp4', 0.0)
        credit = f'<div class="creditD">{CREDIT[smp]}</div>'
    else:
        credit = ""
    sub = f'<div class="chsub" id="{eid}s">{s["sub"]}</div>' if s.get("sub") else ""
    el_div(f"{eid}o", t0, t1, "qov", (
        '<div class="cdscrim"></div>' + credit +
        f'<div class="chghost" id="{eid}g">{s["no"]}</div>'
        f'<div class="chband" id="{eid}b"><div class="chno2">{s["no"]}</div>'
        f'<div class="chtate" id="{eid}t">{s["title"]}</div></div>' + sub))
    cue("riser", max(0.0, t0 - 1.3), 1.0, 1.3)
    softcut(t0, 1.0)
    fromto(t0 + 0.2, f"#{eid}b", "x: 240", "x: 0", 0.6, "power3.out")
    fromto(t0 + 0.45, f"#{eid}t", 'opacity: 0, filter: "blur(8px)"',
           'opacity: 1, filter: "blur(0px)"', 0.8, "power2.out")
    fromto(t0 + 0.35, f"#{eid}g", "scale: 1.3, opacity: 0", "scale: 1, opacity: 0.8", 0.9, "power2.out")
    cue("slam", t0 + 0.7, 0.8)
    cue("sub", t0 + 0.75, 1.0)
    if s.get("sub"):
        fromto(t0 + 1.2, f"#{eid}s", "opacity: 0", "opacity: 1", 0.45, "power2.out")


TECHO_CARDS = [
    ("card_abby.jpg", "驚き", "初来日の英国夫婦"),
    ("card_cecil.jpg", "信頼", "新幹線の忘れ物"),
    ("card_jen.jpg", "優しさ", "両脚骨折の母娘"),
    ("card_kalani.jpg", "変化", "初めてのひとり旅"),
]


def sc_techo(s):  # 手帖: 斜め貼りの写真4枚 + テープ + 朱スタンプ
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    rots = [-3.2, 2.4, -2.0, 3.0]
    ph = "".join(
        f'<div class="tph" id="{eid}c{i}" style="transform:rotate({rots[i]}deg)">'
        f'<img src="assets/img/{img}" alt=""><div class="tptape"></div>'
        f'<div class="tplab">{lab}</div>'
        f'<div class="tpkw" id="{eid}kw{i}">{kw}</div></div>'
        for i, (img, kw, lab) in enumerate(TECHO_CARDS))
    el_div(f"{eid}p", t0, t1, "panel", (
        f'<div class="chead" id="{eid}h">{s.get("head", "4つの旅の記録")}</div>'
        f'<div class="tprow">{ph}</div>' + RAKKAN))
    fromto(t0 + 0.2, f"#{eid}h", "opacity: 0", "opacity: 1", 0.4, "power2.out")
    for i, dt in enumerate([0.4, 0.65, 0.9, 1.15]):
        fromto(t0 + dt, f"#{eid}c{i}", "y: 60, opacity: 0", "y: 0, opacity: 1", 0.45, "power3.out")
        cue("pop", t0 + dt, 0.6)
    kw_nids = s["nids"][1:5]
    assert len(kw_nids) == 4, f"{EP}: techo はナレ5行(導入+4)が必要"
    for i, nid in enumerate(kw_nids):
        st = N[nid]["start"] + 0.55 * N[nid]["dur"]
        fromto(st, f"#{eid}kw{i}", "scale: 1.8, opacity: 0, rotation: -6",
               "scale: 1, opacity: 1, rotation: -6", 0.26, "power4.in")
        cue("slam", st + 0.26, 0.8)


def sc_q(s):
    for qid, qi in Q.items():
        if s["start"] - 0.01 <= qi["beat_start"] < s["end"]:
            quote_block(qid, s["start"])


def sc_ask(s):
    t0, t1 = s["start"], s["end"]
    el_div("askp", t0, t1, "panel", (
        '<div class="askt" id="ask1">あなたの当たり前は<br>誰かの<em>奇跡</em>かもしれない</div>'
        '<div class="asks" id="ask2">▼ 外国人に日本を褒められた体験、コメントで聞かせてください</div>' + RAKKAN))
    fromto(t0 + 0.3, "#ask1", 'opacity: 0, y: 24, filter: "blur(8px)"',
           'opacity: 1, y: 0, filter: "blur(0px)"', 0.7, "power2.out")
    cue("sub", t0 + 0.35, 0.8)
    fromto(t0 + 1.5, "#ask2", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
    cue("pop", t0 + 1.5, 0.6)
    tw(t0 + 2.1, 'tl.to("#ask2", {y: 8, duration: 0.5, ease: "sine.inOut", repeat: 5, yoyo: true}, %T%);')


def sc_end(s):
    t0, t1 = s["start"], s["end"]
    el_div("endp", t0, t1, "panel", (
        '<div class="endt" id="end1">ご視聴 ありがとうございました</div>'
        '<div class="ends" id="end2">チャンネル登録で、次の旅の記録をお見逃しなく</div>' + RAKKAN))
    fromto(t0 + 0.3, "#end1", "opacity: 0", "opacity: 1", 0.7, "power2.out")
    fromto(t0 + 1.2, "#end2", "opacity: 0", "opacity: 1", 0.5, "power2.out")
    cue("pop", t0 + 1.2, 0.5)


KIND = {"broll": sc_broll, "kick": sc_kick, "q": sc_q, "nv": sc_nv,
        "tate": sc_tate, "tanzaku": sc_tanzaku, "fuda": sc_fuda, "wallets": sc_wallets,
        "emaki": sc_emaki, "michi": sc_michi, "card": sc_card, "techo": sc_techo,
        "ask": sc_ask, "end": sc_end}


# トランジション: washi=和紙ディップ / ink=墨の円 / none
TR_DEF = {"tate": "ink", "tanzaku": "washi", "fuda": "ink", "wallets": "washi",
          "emaki": "ink", "michi": "washi", "techo": "washi", "ask": "ink", "end": "washi",
          "q": "none", "nv": "none", "broll": "none", "card": "none"}
KICK_TR = ["washi", "ink"]


def apply_tr(tr, s, ids):
    t0 = s["start"]
    if tr == "none" or t0 < 0.4:
        return
    if tr == "washi":  # 和紙ディップ
        setv(t0 - 0.01, "#flash", "opacity: 0.85")
        tw(t0 + 0.03, 'tl.to("#flash", {opacity: 0, duration: 0.65, ease: "power2.out"}, %T%);')
        cue("glitch", t0, 0.7)
    elif tr == "ink":  # 墨の円が広がって場面を変える
        setv(t0 - 0.30, "#inkc", "opacity: 1, scale: 0")
        tw(t0 - 0.30, 'tl.to("#inkc", {scale: 3.2, duration: 0.33, ease: "power2.in"}, %T%);')
        tw(t0 + 0.05, 'tl.to("#inkc", {opacity: 0, duration: 0.55, ease: "power2.out"}, %T%);')
        setv(t0 + 0.62, "#inkc", "scale: 0")
        cue("sub", t0 - 0.25, 0.8)


_id_re = re.compile(r'id="([^"]+)"')
_kick_i = 0
for s in SC:
    pre = len(ELS)
    KIND[s["kind"]](s)
    tr = s.get("tr")
    if not tr:
        if s["kind"] == "kick":
            tr = KICK_TR[_kick_i % len(KICK_TR)]
            _kick_i += 1
        else:
            tr = TR_DEF[s["kind"]]
    ids = [_id_re.search(e).group(1) for e in ELS[pre:]]
    apply_tr(tr, s, ids)

# ep-level fades
fromto(0.05, "#stage", "opacity: 0", "opacity: 1", 0.8, "power2.out")
tw(COMP - 1.15, 'tl.to("#stage", {opacity: 0, duration: 0.95, ease: "power1.in"}, %T%);')

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
#tbk { position:absolute; inset:0; z-index:56; background:#000; opacity:0; pointer-events:none; }
/* ---------- 和紙パネル ---------- */
.panel { z-index:10; background:
  radial-gradient(ellipse 130% 95% at 50% 36%, #f5eeda 0%, #efe6cf 58%, #e4d7b8 100%); }
.panel::before { content:''; position:absolute; inset:0; background-image:__NOISE__;
  pointer-events:none; }
.panel::after { content:''; position:absolute; inset:0; pointer-events:none;
  box-shadow:inset 0 0 180px rgba(120,96,50,.28); }
.rk { position:absolute; right:64px; bottom:56px; z-index:3; writing-mode:vertical-rl;
  font-family:'SerifJP'; font-weight:900; font-size:26px; line-height:1.15; letter-spacing:.12em;
  color:#b3402e; border:3px solid #b3402e; padding:10px 6px; opacity:.75; border-radius:4px; }
/* ---------- 引用フレーム ---------- */
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
.biglabel { position:absolute; left:64px; top:130px; font-family:'SerifJP'; font-weight:900;
  font-size:54px; color:#231c10; background:#efe7d3; border-left:10px solid #b3402e;
  padding:16px 38px; box-shadow:0 6px 24px rgba(20,12,2,.4); opacity:0; }
.creditD { position:absolute; top:26px; right:360px; font-family:'NotoBd'; font-size:24px;
  color:rgba(242,238,226,.9); background:rgba(23,16,6,.5); padding:7px 16px; }
/* ---------- 縦書きテーゼ ---------- */
.tatew { position:absolute; inset:0; display:flex; flex-direction:row-reverse; align-items:center; justify-content:center; }
.ttcol { writing-mode:vertical-rl; font-family:'SerifJP'; font-weight:900; font-size:100px;
  letter-spacing:.1em; line-height:1.5; color:#231c10; margin:0 34px; opacity:0; max-height:1020px; }
/* ---------- kick ---------- */
.tkwrap { position:absolute; right:270px; top:0; bottom:0; display:flex; align-items:center; gap:34px; }
.tkline { width:8px; height:420px; background:#b3402e; transform-origin:top; transform:scaleY(0);
  border-radius:4px; }
.tkt { writing-mode:vertical-rl; font-family:'SerifJP'; font-weight:900; font-size:84px;
  letter-spacing:.14em; color:#231c10; }
.tkc { opacity:0; display:inline-block; }
.fdwrap { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center;
  justify-content:center; gap:44px; padding:0 140px; }
.fdot { width:46px; height:46px; background:#b3402e; border-radius:52% 48% 50% 50%/48% 52% 48% 52%;
  opacity:0; }
.fdt { text-align:center; font-family:'SerifJP'; font-weight:900; font-size:86px; line-height:1.4;
  color:#231c10; opacity:0; }
/* ---------- 短冊 ---------- */
.dhead { position:absolute; left:0; right:0; top:92px; text-align:center; font-family:'SerifJP';
  font-weight:900; font-size:72px; color:#231c10; opacity:0; }
.tzrow { position:absolute; left:160px; right:160px; top:280px; bottom:190px; display:flex;
  flex-direction:row-reverse; gap:56px; justify-content:center; }
.tz { position:relative; width:250px; background:#faf4e4; border:2px solid #cfc09a;
  box-shadow:0 14px 34px rgba(90,66,24,.26); opacity:0; }
.tzpin { position:absolute; left:50%; top:-12px; width:22px; height:22px; margin-left:-11px;
  background:#b3402e; border-radius:50%; box-shadow:0 2px 6px rgba(60,30,10,.4); }
.tzin { position:absolute; inset:40px 0 30px; display:flex; flex-direction:row-reverse;
  justify-content:center; gap:26px; }
.tztag { writing-mode:vertical-rl; font-family:'SerifJP'; font-weight:900; font-size:62px;
  letter-spacing:.3em; color:#231c10; }
.tztx { writing-mode:vertical-rl; font-family:'SerifJP'; font-weight:700; font-size:31px;
  letter-spacing:.14em; line-height:1.7; color:#6b6353; max-height:540px; }
/* ---------- 木札 ---------- */
.fuda { position:absolute; left:50%; top:44%; transform:translate(-50%,-50%); width:1080px;
  background:#faf4e4; border:3px solid #b98a35; border-radius:10px; padding:64px 80px 70px;
  text-align:center; box-shadow:0 18px 50px rgba(90,66,24,.3); opacity:0; }
.fuda::before { content:''; position:absolute; inset:10px; border:1px solid #d8c694;
  border-radius:6px; pointer-events:none; }
.fudat { font-family:'SerifJP'; font-weight:900; font-size:92px; color:#231c10; letter-spacing:.1em; }
.fudab { font-family:'SerifJP'; font-weight:700; font-size:44px; color:#6b6353; margin-top:34px;
  line-height:1.55; }
.dnote { position:absolute; left:0; right:0; bottom:88px; text-align:center; font-family:'NotoBd';
  font-size:32px; color:#8a7b57; opacity:0; }
/* ---------- 財布 ---------- */
.wnum { position:absolute; left:0; right:0; top:218px; text-align:center; font-family:'SerifJP';
  font-weight:900; font-size:190px; color:#231c10; opacity:0; }
.wnum span { font-size:84px; color:#b3402e; margin-left:10px; }
.wrow { position:absolute; left:220px; right:220px; top:540px; display:flex; gap:28px;
  justify-content:center; }
.wl { position:relative; width:118px; height:118px; color:#c2b391; opacity:0; }
.wl svg { width:100%; height:100%; }
.wlg { position:absolute; inset:0; color:#b3402e; opacity:0; }
.wlab { position:absolute; left:0; right:0; top:700px; text-align:center; font-family:'SerifJP';
  font-weight:900; font-size:66px; color:#231c10; opacity:0; }
.cntsrc { position:absolute; right:60px; bottom:40px; font-family:'NotoBd'; font-size:23px;
  color:#8a7b57; }
/* ---------- 絵巻 ---------- */
.embrush { position:absolute; right:7%; left:7%; top:calc(42% + 64px); height:10px;
  background:linear-gradient(90deg, rgba(138,123,87,.15), #8a7b57 22%, #8a7b57 78%, rgba(138,123,87,.4));
  border-radius:6px; transform-origin:right; transform:scaleX(0); }
.emn { position:absolute; top:34%; width:24%; text-align:center; opacity:0; }
.emnc { width:216px; height:216px; margin:0 auto; border-radius:50%; background:#faf4e4;
  border:4px solid #b98a35; display:flex; align-items:center; justify-content:center;
  font-family:'SerifJP'; font-weight:900; font-size:42px; color:#231c10; white-space:nowrap;
  box-shadow:0 10px 30px rgba(90,66,24,.25); }
.emnd { font-family:'NotoBd'; font-size:29px; color:#6b6353; margin-top:22px; }
.emstamp { position:absolute; left:50%; top:70%; transform:translateX(-50%) rotate(-7deg);
  font-family:'SerifJP'; font-weight:900; font-size:96px; color:#b3402e; border:9px solid #b3402e;
  padding:8px 44px; border-radius:10px; background:rgba(179,64,46,.06); opacity:0; }
/* ---------- 道のり ---------- */
.miwrap { position:absolute; left:110px; right:110px; top:260px; bottom:110px; }
.mimask { position:absolute; inset:0; transform-origin:left; }
.miline { position:absolute; left:0; right:0; top:10%; width:100%; height:80%; }
.mist { position:absolute; width:300px; margin-left:-150px; text-align:center; opacity:0; }
.midot { width:30px; height:30px; margin:0 auto 18px; background:#b3402e; border-radius:50%;
  border:5px solid #faf4e4; box-shadow:0 4px 12px rgba(60,30,10,.35); }
.mitag { font-family:'SerifJP'; font-weight:900; font-size:46px; color:#231c10; }
.midesc { font-family:'NotoBd'; font-size:27px; color:#6b6353; margin-top:10px; }
/* ---------- 章扉 ---------- */
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
/* ---------- 手帖 ---------- */
.chead { position:absolute; left:0; right:0; top:80px; text-align:center; font-family:'SerifJP';
  font-weight:900; font-size:44px; letter-spacing:.4em; color:#6b6353; opacity:0; }
.tprow { position:absolute; left:100px; right:100px; top:200px; bottom:110px; display:flex;
  gap:44px; align-items:center; }
.tph { position:relative; flex:1; height:92%; background:#faf4e4; padding:16px 16px 58px;
  box-shadow:0 16px 40px rgba(60,40,12,.32); opacity:0; }
.tph img { width:100%; height:82%; object-fit:cover; filter:saturate(.88) sepia(.08); }
.tptape { position:absolute; left:50%; top:-16px; width:150px; height:38px; margin-left:-75px;
  background:rgba(214,196,150,.8); transform:rotate(-2deg); box-shadow:0 2px 8px rgba(60,40,12,.2); }
.tplab { position:absolute; left:0; right:0; bottom:16px; text-align:center; font-family:'SerifJP';
  font-weight:700; font-size:30px; color:#4a4335; }
.tpkw { position:absolute; left:12%; top:34%; width:76%; text-align:center; font-family:'SerifJP';
  font-weight:900; font-size:56px; color:#b3402e; border:6px solid #b3402e; border-radius:8px;
  padding:12px 4px; transform:rotate(-6deg); background:rgba(250,244,228,.75); opacity:0; }
/* ---------- ask / end ---------- */
.askt { position:absolute; left:0; right:0; top:26%; text-align:center; font-family:'SerifJP';
  font-weight:900; font-size:86px; line-height:1.55; color:#231c10; opacity:0; }
.asks { position:absolute; left:0; right:0; top:70%; text-align:center; font-family:'NotoBd';
  font-size:40px; color:#8a5a28; opacity:0; }
.endt { position:absolute; left:0; right:0; top:40%; text-align:center; font-family:'SerifJP';
  font-weight:900; font-size:86px; color:#231c10; opacity:0; }
.ends { position:absolute; left:0; right:0; top:58%; text-align:center; font-family:'NotoBd';
  font-size:36px; color:#8a7b57; opacity:0; }
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
<div id="tbk"></div>
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
if FULL:
    (ROOT / "subtitles" / "out" / EP / "sfx_cues.json").write_text(
        json.dumps({"total": COMP, "cues": sorted(CUES, key=lambda c: c["t"])}, ensure_ascii=False),
        encoding="utf-8")
print(f"{EP}: built index.html window {W0}-{W1} ({WDUR}s) els={len(ELS)} tweens={len(TWEENS)} cues={len(CUES)}")
