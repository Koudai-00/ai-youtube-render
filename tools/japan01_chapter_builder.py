# -*- coding: utf-8 -*-
"""japan01cX 章ビルダ (窓分割対応)。EP_CH env で章選択。
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
from japan01_chapters import BROLL, CREDIT, Q as QSPEC  # noqa: E402

NV_PRE = 0.6  # extract_quotes.NV_PRE と一致

EP = os.environ.get("EP_CH") or "japan01c1"
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


CUR_BGX = [None]  # 現シーンに背景映像があるとき panel を半透明化


def el_div(eid, t0, t1, cls, inner, style=""):
    if not OV(t0, t1):
        return
    if CUR_BGX[0] and "panel" in cls:
        cls += " clear"
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


def glitch(t, strength=1.0):
    for gid in ("#gl1", "#gl2", "#gl3"):
        y1, y2 = rng.randint(5, 85), rng.randint(5, 85)
        setv(t, gid, f'opacity: {0.75*strength:.2f}, top: "{y1}%", height: {rng.randint(14,60)}, x: {rng.randint(-70,70)}')
        setv(t + 0.067, gid, f'top: "{y2}%", height: {rng.randint(10,44)}, x: {rng.randint(-70,70)}')
        setv(t + 0.167, gid, 'opacity: 0, x: 0')
    setv(t, "#flash", f'opacity: {0.85*strength:.2f}')
    setv(t + 0.067, "#flash", f'opacity: {0.25*strength:.2f}')
    setv(t + 0.133, "#flash", 'opacity: 0')
    jx = int(14 * strength)
    setv(t, "#stage", f'x: {-jx}')
    setv(t + 0.067, "#stage", f'x: {jx}')
    setv(t + 0.133, "#stage", 'x: 0')
    cue("glitch", t, strength)


# モノクロ線画SVGアイコン (いらすとや禁止の代替。op の .iic と同トーン)
ICONS = {
    "torii": ('<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3">'
              '<path d="M5 13 Q24 7 43 13"/><line x1="11" y1="11" x2="11" y2="42"/>'
              '<line x1="37" y1="11" x2="37" y2="42"/><line x1="8" y1="21" x2="40" y2="21"/>'
              '<line x1="24" y1="13" x2="24" y2="21"/></svg>'),
    "train": ('<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3">'
              '<rect x="10" y="6" width="28" height="30" rx="5"/>'
              '<line x1="10" y1="22" x2="38" y2="22"/>'
              '<circle cx="17" cy="29" r="2.6" fill="currentColor"/><circle cx="31" cy="29" r="2.6" fill="currentColor"/>'
              '<line x1="16" y1="42" x2="12" y2="36"/><line x1="32" y1="42" x2="36" y2="36"/></svg>'),
    "camera": ('<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3">'
               '<path d="M8 14h8l4-5h8l4 5h8a3 3 0 0 1 3 3v20a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V17a3 3 0 0 1 3-3z"/>'
               '<circle cx="24" cy="27" r="7"/></svg>'),
    "coin": ('<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3">'
             '<circle cx="24" cy="24" r="17"/><path d="M17 14 L24 24 L31 14"/>'
             '<line x1="24" y1="24" x2="24" y2="35"/><line x1="18" y1="27" x2="30" y2="27"/>'
             '<line x1="18" y1="32" x2="30" y2="32"/></svg>'),
}

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


def quote_block(qid, sc_start):
    qi = Q[qid]
    t0 = qi["beat_start"]
    t1 = t0 + qi["dur"]
    sp = t0 + qi["lead"]
    el_video(f"{qid}v", t0, t1, qi["clip"], qi["media_start"])
    caps = qi["caps"]
    cdivs = "".join(f'<div class="qcap" id="{qid}cap{i}">{h}</div>' for i, (dt, h) in enumerate(caps))
    el_div(f"{qid}o", t0, t1, "qov", (
        '<div class="qscrim"></div>'
        f'<div class="credit">{qi["credit"]}</div>' + cdivs))
    for i, (dt, _h) in enumerate(caps):
        tin = sp + dt
        fromto(tin, f"#{qid}cap{i}", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
        cue("pop", tin, 0.6)
        if i + 1 < len(caps):
            setv(sp + caps[i + 1][0] - 0.12, f"#{qid}cap{i}", "opacity: 0")
    g = qi.get("grade")
    if g:
        fromto(sp + 0.3, f"#{qid}v", f'filter: "{GRADE0[g]}"', f'filter: "{GRADE1[g]}"', 0.9, "power2.inOut")
        if g == "gray":
            cue("heart", sp + 0.5, 1.0, min(6.0, qi["adur"]))
    glitch(t0, 0.9 if abs(t0 - sc_start) < 0.2 else 0.6)


def sc_nv(s):
    """ナレ引用: 映像ミュート+引用風字幕(ナレ行開始に同期)+ナレが内容を語る"""
    t0, t1 = s["start"], s["end"]
    qid = s["q"]
    qs = QSPEC[qid]
    nids = s["nids"]
    caps = qs["caps"]
    assert len(caps) == len(nids), f"{EP}:{qid} caps{len(caps)} != nids{len(nids)}"
    el_video(f"{qid}v", t0, t1, f"{qid}.mp4", NV_PRE)
    cdivs = "".join(f'<div class="qcap" id="{qid}cap{i}">{h}</div>' for i, (_dt, h) in enumerate(caps))
    el_div(f"{qid}o", t0, t1, "qov", (
        '<div class="qscrim"></div>'
        f'<div class="credit">{CREDIT[qs["s"]]}</div>' + cdivs))
    times = [N[nid]["start"] for nid in nids]
    for i, st in enumerate(times):
        tin = max(t0 + 0.05, st - 0.12)
        fromto(tin, f"#{qid}cap{i}", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
        cue("pop", tin, 0.6)
        if i + 1 < len(times):
            setv(times[i + 1] - 0.25, f"#{qid}cap{i}", "opacity: 0")
    g = qs.get("grade")
    if g:
        fromto(t0 + 0.4, f"#{qid}v", f'filter: "{GRADE0[g]}"', f'filter: "{GRADE1[g]}"', 0.9, "power2.inOut")
        if g == "gray":
            cue("heart", t0 + 0.6, 1.0, min(6.0, max(1.5, t1 - t0 - 1.0)))
    glitch(t0, 0.7)


def lower_third(pref, t0, t1, name, role, delay=0.5):
    el_div(f"{pref}lt", t0, t1, "qov", (
        f'<div class="lt" id="{pref}lt1"><div class="ltbar"></div>'
        f'<div class="ltbody"><div class="ltname">{name}</div>'
        f'<div class="ltrole">{role}</div></div></div>'))
    fromto(t0 + delay, f"#{pref}lt1", "x: -70, opacity: 0", "x: 0, opacity: 1", 0.45, "power3.out")
    cue("whoosh", t0 + delay, 0.7)


# ============================================================ scene renderers
def sc_broll(s):
    t0, t1 = s["start"], s["end"]
    bid = s["bg"]
    smp = BROLL[bid][0]
    el_video(f'{s["id"]}v', t0, t1, f"{bid}.mp4", 0.0)
    el_div(f'{s["id"]}sc', t0, t1, "qov", (
        '<div class="qscrim"></div>'
        f'<div class="credit">{CREDIT[smp]}</div>'
        + (f'<div class="biglabel" id="{s["id"]}lab">{s["label"]}</div>' if s.get("label") else "")))
    if s.get("lt"):
        lower_third(s["id"], t0, t1, s["lt"][0], s["lt"][1])
    if s.get("label"):
        fromto(t0 + 0.35, f'#{s["id"]}lab', "scale: 1.3, opacity: 0", "scale: 1, opacity: 1", 0.35, "expo.out")
        cue("slam", t0 + 0.35, 0.7)
    glitch(t0, 0.8)


# kick テキストアニメ輪番 (v5: 「中央テキスト+赤下線」の多用をやめ、参考動画の表現を移植)
# band=赤帯白抜きスイープ / serif=明朝+巨大漢字ゴースト+ブラーイン / typeline=タイプライター
# stamp=判子パンチ / barleft=左赤バー+マスクせり上がり / under=従来の赤下線(文字ステガー化)
KICK_STYLES = ["band", "serif", "typeline", "stamp", "barleft", "under"]
_ks_i = [0]


def _chars(txt):
    return None if "<" in txt else list(txt)


def sc_kick(s):
    t0, t1 = s["start"], s["end"]
    k = s.get("kicker")
    if not k:
        raise SystemExit(f"{EP}:{s['id']}: kick には必ず kicker テキストを付ける(赤線だけの画面を禁止)")
    eid = s["id"]
    style = s.get("kstyle") or KICK_STYLES[_ks_i[0] % len(KICK_STYLES)]
    _ks_i[0] += 1
    if style == "band":  # 参考A: キーワードを色ベタ帯に白抜き
        el_div(f"{eid}p", t0, t1, "panel",
               f'<div class="kband" id="{eid}b"><span id="{eid}k">{k}</span></div>')
        fromto(t0 + 0.25, f"#{eid}b", "scaleX: 0", "scaleX: 1", 0.4, "power3.inOut")
        fromto(t0 + 0.55, f"#{eid}k", "opacity: 0", "opacity: 1", 0.25, "power2.out")
        cue("whoosh", t0 + 0.25, 0.8)
        cue("slam", t0 + 0.62, 0.6)
    elif style == "serif":  # 参考A: 極太明朝+巨大漢字ゴースト
        g = next((c for c in k if "一" <= c <= "鿿"), None)
        ghost = f'<div class="kghost" id="{eid}g">{g}</div>' if g else ""
        el_div(f"{eid}p", t0, t1, "panel", ghost + f'<div class="kserif" id="{eid}k">{k}</div>')
        if g:
            fromto(t0 + 0.2, f"#{eid}g", "scale: 1.6, opacity: 0", "scale: 1, opacity: 0.13", 1.0, "power2.out")
        fromto(t0 + 0.3, f"#{eid}k",
               'opacity: 0, letterSpacing: "0.5em", filter: "blur(14px)"',
               'opacity: 1, letterSpacing: "0.1em", filter: "blur(0px)"', 0.8, "power2.out")
        cue("sub", t0 + 0.3, 0.8)
    elif style == "typeline" and _chars(k):  # タイプライター+赤カーソル
        chars = _chars(k)
        spans = "".join(f'<span class="kch" id="{eid}c{i}">{c}</span>' for i, c in enumerate(chars))
        el_div(f"{eid}p", t0, t1, "panel",
               f'<div class="ktype" id="{eid}k">{spans}<span class="kcaret" id="{eid}cr"></span></div>')
        n = len(chars)
        step = min(0.07, 1.1 / max(n, 1))
        for i in range(n):
            setv(t0 + 0.35 + i * step, f"#{eid}c{i}", "opacity: 1")
            if i % 3 == 0:
                cue("tick", t0 + 0.35 + i * step, 0.35)
        for j in range(6):  # カーソル点滅(有限)
            setv(t0 + 0.4 + n * step + j * 0.4, f"#{eid}cr", f"opacity: {1 if j % 2 == 0 else 0}")
    elif style == "stamp":  # 判子パンチ
        el_div(f"{eid}p", t0, t1, "panel", f'<div class="kstamp" id="{eid}k">{k}</div>')
        fromto(t0 + 0.3, f"#{eid}k", "scale: 2.0, opacity: 0, rotation: -3",
               "scale: 1, opacity: 1, rotation: -3", 0.26, "power4.in")
        cue("slam", t0 + 0.56, 1.0)
    elif style == "barleft":  # 左赤バー+マスクせり上がり
        el_div(f"{eid}p", t0, t1, "panel", (
            f'<div class="kbar" id="{eid}bb"></div>'
            f'<div class="kmask"><div class="kleft" id="{eid}k">{k}</div></div>'))
        fromto(t0 + 0.2, f"#{eid}bb", "scaleY: 0", "scaleY: 1", 0.35, "power3.out")
        setv(t0 + 0.01, f"#{eid}k", "y: 260")  # マスク外へ(CSS transformとの合成を避けGSAPのみで制御)
        tw(t0 + 0.35, f'tl.to("#{eid}k", {{y: 0, duration: 0.5, ease: "power3.out"}}, %T%);')
        cue("whoosh", t0 + 0.3, 0.7)
    else:  # under: 従来の赤下線(文字ステガー)
        chars = _chars(k)
        inner_k = "".join(f'<span class="kch2" id="{eid}c{i}">{c}</span>'
                          for i, c in enumerate(chars)) if chars else k
        el_div(f"{eid}p", t0, t1, "panel", (
            f'<div class="kstack"><div class="kick" id="{eid}k">{inner_k}</div>'
            f'<div class="kline" id="{eid}kl"></div></div>'))
        if chars:
            setv(t0 + 0.01, f"#{eid}k", "opacity: 1")
            step = min(0.055, 0.9 / max(len(chars), 1))
            for i in range(len(chars)):
                fromto(t0 + 0.25 + i * step, f"#{eid}c{i}", "y: 22, opacity: 0", "y: 0, opacity: 1", 0.3, "power3.out")
        else:
            fromto(t0 + 0.25, f"#{eid}k", "y: 20, opacity: 0", "y: 0, opacity: 1", 0.45, "power3.out")
        cue("whoosh", t0 + 0.25, 0.8)
        fromto(t0 + 0.3, f"#{eid}kl", "scaleX: 0", "scaleX: 1", 0.5, "power2.inOut")


def sc_cases(s):  # 事例リストパネル (行はナレ尺に均等同期)
    t0, t1 = s["start"], s["end"]
    eid = s["id"]
    rows = s["rows"]
    icons = s.get("icon_rows")
    if icons:
        assert len(icons) == len(rows), f"{EP}:{eid} icon_rows{len(icons)} != rows{len(rows)}"
    rh = "".join(
        f'<div class="crow" id="{eid}r{i}">'
        + (f'<div class="cic">{ICONS[icons[i]]}</div>' if icons else "")
        + f'<span class="ctag">{tag}</span><span class="ctx">{tx}</span></div>'
        for i, (tag, tx) in enumerate(rows))
    el_div(f"{eid}p", t0, t1, "panel", (
        f'<div class="dhead" id="{eid}h">{s["head"]}</div><div class="crows">{rh}</div>'))
    fromto(t0 + 0.3, f"#{eid}h", "y: -26, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    n = N[s["nids"][0]]
    for i in range(len(rows)):
        tt = n["start"] + i * (n["dur"] / len(rows)) + 0.1
        fromto(tt, f"#{eid}r{i}", "x: -70, opacity: 0", "x: 0, opacity: 1", 0.4, "power3.out")
        cue("tick", tt, 0.8)


def sc_pct(s):  # 99% / 1% パネル
    t0, t1 = s["start"], s["end"]
    el_div("pctp", t0, t1, "panel", (
        '<div class="dhead" id="ph">迷惑をかけるのは <em>1%</em></div>'
        '<div class="pbar" id="pb"><div class="p99" id="p99"><span>99%</span>は 日本の味方</div>'
        '<div class="p1" id="p1"></div></div>'
        '<div class="p1lab" id="p1l">しかし拡散されるのは<br>この<em>1%</em>だけ</div>'
        '<div class="cntsrc">出典: 引用元動画(Chopsticks and Trains)の主張</div>'))
    fromto(t0 + 0.3, "#ph", "y: -26, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    fromto(t0 + 1.0, "#p99", "scaleX: 0", "scaleX: 1", 1.0, "power2.inOut")
    cue("count", t0 + 1.0, 0.7, 1.0)
    fromto(t0 + 2.3, "#p1", "scaleX: 0", "scaleX: 1", 0.3, "power4.out")
    cue("slam", t0 + 2.45, 0.9)
    fromto(t0 + 2.7, "#p1l", "y: 24, opacity: 0", "y: 0, opacity: 1", 0.45, "power3.out")
    cue("pop", t0 + 2.7, 0.6)


def sc_q(s):
    for qid, qi in Q.items():
        if s["start"] - 0.01 <= qi["beat_start"] < s["end"]:
            quote_block(qid, s["start"])


ARR_SVG = ('<svg class="marrs" id="%s" style="left:%s" viewBox="0 0 96 36" fill="none">'
           '<line x1="0" y1="18" x2="66" y2="18" stroke="#e8322e" stroke-width="9"/>'
           '<polygon points="64,3 64,33 94,18" fill="#e8322e"/></svg>')


def sc_diagram(s):  # c1: 連帯責任メカニズム
    t0, t1 = s["start"], s["end"]
    steps = [("st1", "1人の<br>迷惑行為"), ("st2", '主語が<br>"あの人たち"に'), ("st3", "全員に<br>レッテル")]
    # 箱: left 8/39/70% 幅26% 高さ固定270px → 矢印は箱間ギャップ(34-39%, 65-70%)を箱の垂直中心で結ぶ
    sh = "".join(
        f'<div class="mstep" id="{sid}" style="left:{8+i*31}%"><div class="mnum">{i+1}</div><div class="mtx">{tx}</div></div>'
        + (ARR_SVG % (f"{sid}a", f"{34+i*31}%") if i < 2 else "")
        for i, (sid, tx) in enumerate(steps))
    el_div("mech", t0, t1, "panel", (
        '<div class="dhead" id="mh">レッテルが生まれる<em>仕組み</em></div>' + sh +
        '<div class="stamp" id="mstamp">連帯責任</div>'))
    fromto(t0 + 0.3, "#mh", "y: -26, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    for i, dt in enumerate([0.8, 2.0, 3.2]):
        fromto(t0 + dt, f"#st{i+1}", "scale: 0.6, opacity: 0", "scale: 1, opacity: 1", 0.4, "back.out(1.7)")
        cue("pop", t0 + dt, 0.8)
        if i < 2:
            fromto(t0 + dt + 0.75, f"#st{i+1}a", "scaleX: 0, opacity: 0", "scaleX: 1, opacity: 1", 0.3, "power2.out")
            cue("tick", t0 + dt + 0.75, 0.6)
    ts = t0 + 4.6
    fromto(ts, "#mstamp", "scale: 2.2, opacity: 0, rotation: -8", "scale: 1, opacity: 1, rotation: -8", 0.28, "power4.in")
    cue("slam", ts + 0.28, 1.0)


def sc_counter(s):  # c2: 訪日客数
    t0, t1 = s["start"], s["end"]
    bars = [("2019", 3188, 62), ("2023", 2507, 49), ("2024", 3687, 72)]
    bh = "".join(
        f'<div class="cbar" id="cb{i}"><div class="cbv" id="cbv{i}" style="width:{w}%"></div>'
        f'<span class="cby">{y}</span><span class="cbn">{v}万人</span></div>'
        for i, (y, v, w) in enumerate(bars))
    el_div("cntp", t0, t1, "panel", (
        '<div class="cntlab" id="cl1">2024年 訪日外国人数</div>'
        '<div class="cntnum" id="cn0">0<span>万人</span></div>'
        f'<div class="cbars">{bh}</div>'
        '<div class="cntsrc">出典: 日本政府観光局(JNTO) 推計値</div>'))
    fromto(t0 + 0.3, "#cl1", "y: -20, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    # stepped count-up 0 -> 3687 (hundreds representable, deterministic)
    n_steps = 22
    for i in range(n_steps + 1):
        v = int(3687 * (i / n_steps) ** 2)
        tt = t0 + 0.7 + 1.7 * i / n_steps
        tw(tt, f'tl.set("#cn0", {{ innerHTML: "{v}<span>万人</span>" }}, %T%);')
    cue("count", t0 + 0.7, 1.0, 1.7)
    setv(t0 + 0.7 + 1.7, "#cn0", 'color: "#e8322e"')
    cue("slam", t0 + 2.4, 0.8)
    for i, dt in enumerate([2.9, 3.4, 3.9]):
        fromto(t0 + dt, f"#cb{i}", "x: 60, opacity: 0", "x: 0, opacity: 1", 0.4, "power3.out")
        fromto(t0 + dt + 0.1, f"#cbv{i}", "scaleX: 0", "scaleX: 1", 0.55, "power2.inOut")
        cue("tick", t0 + dt, 0.6)


def sc_news(s):  # c2: 速報パネル
    t0, t1 = s["start"], s["end"]
    el_div("newsp", t0, t1, "panel", (
        '<div class="nband" id="nb1"><span class="ntag">NEWS</span>鉄道会社が激怒</div>'
        '<div class="nhead" id="nh1">車内ダンスに<br><em>法的措置</em>を検討</div>'
        '<div class="nsub" id="ns1">乗客を巻き込む危険行為として警告の掲示も — 引用元動画より</div>'))
    fromto(t0 + 0.25, "#nb1", "x: -900, opacity: 1", "x: 0, opacity: 1", 0.4, "power4.out")
    cue("whoosh", t0 + 0.25, 1.0)
    fromto(t0 + 0.65, "#nh1", "y: 34, opacity: 0", "y: 0, opacity: 1", 0.45, "power3.out")
    cue("slam", t0 + 0.75, 0.9)
    fromto(t0 + 1.3, "#ns1", "opacity: 0", "opacity: 1", 0.4, "power2.out")


def sc_journey(s):  # c3: 浅草→自由が丘
    t0, t1 = s["start"], s["end"]
    stops = [
        ("j1", "浅草", "土産物の下駄<br>→ 裏は「中国製」", "✕"),
        ("j2", "自由が丘", "老店主の<br>小さな下駄屋", "○"),
    ]
    sh = "".join(
        f'<div class="jstop" id="{jid}" style="left:{14+i*46}%">'
        f'<div class="jmark {"jx" if m=="✕" else "jo"}">{m}</div>'
        f'<div class="jname">{nm}</div><div class="jdesc">{ds}</div></div>'
        for i, (jid, nm, ds, m) in enumerate(stops))
    # ◯✕マーク(中心y=34%+60px)同士を結ぶ矢印: 円の縁から円の縁まで
    jarr = ('<svg class="jarr" id="jl" viewBox="0 0 744 28" fill="none">'
            '<line x1="0" y1="14" x2="706" y2="14" stroke="#8a93a0" stroke-width="8"/>'
            '<polygon points="704,1 704,27 742,14" fill="#46e0a0"/></svg>')
    el_div("jour", t0, t1, "panel", (
        '<div class="dhead" id="jh">"本物の下駄" を探して</div>' + jarr + sh))
    fromto(t0 + 0.3, "#jh", "y: -26, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    fromto(t0 + 1.0, "#j1", "y: 40, opacity: 0", "y: 0, opacity: 1", 0.45, "power3.out")
    cue("pop", t0 + 1.0, 0.8)
    fromto(t0 + 2.2, "#jl", "scaleX: 0", "scaleX: 1", 1.2, "power2.inOut")
    cue("tick", t0 + 2.2, 0.5)
    fromto(t0 + 3.6, "#j2", "y: 40, opacity: 0", "y: 0, opacity: 1", 0.45, "power3.out")
    cue("pop", t0 + 3.6, 0.9)


def sc_gion(s):  # c4: 祇園 看板
    t0, t1 = s["start"], s["end"]
    cam = ('<svg viewBox="0 0 48 48"><path d="M8 14h8l4-5h8l4 5h8a3 3 0 0 1 3 3v20a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V17a3 3 0 0 1 3-3z" '
           'fill="none" stroke="currentColor" stroke-width="3"/><circle cx="24" cy="27" r="7" fill="none" stroke="currentColor" stroke-width="3"/>'
           '<line x1="6" y1="42" x2="42" y2="6" stroke="#e8322e" stroke-width="4"/></svg>')
    el_div("gion", t0, t1, "panel", (
        '<div class="dhead" id="gh">祇園・私道 <em>撮影禁止</em>へ</div>'
        f'<div class="sign" id="gs"><div class="signic">{cam}</div>'
        '<div class="signtx">私道での撮影禁止<br><span>罰金 10,000円</span></div></div>'
        '<div class="dnote" id="gn">2024年〜 地元協議会が看板を設置</div>'))
    fromto(t0 + 0.3, "#gh", "y: -26, opacity: 0", "y: 0, opacity: 1", 0.4, "power3.out")
    fromto(t0 + 1.0, "#gs", "scale: 1.5, opacity: 0, rotation: 2", "scale: 1, opacity: 1, rotation: 0", 0.35, "power4.in")
    cue("slam", t0 + 1.35, 1.0)
    fromto(t0 + 2.2, "#gn", "opacity: 0", "opacity: 1", 0.4, "power2.out")


def sc_msg(s):
    t0, t1 = s["start"], s["end"]
    by = s.get("by")
    byh = f'<div class="msgby" id="{s["id"]}b">{by}</div>' if by else ""
    el_div(f'{s["id"]}m', t0, t1, "panel tpanel", (
        '<div class="glow" id="%sg"></div>' % s["id"] +
        f'<div class="msgt" id="{s["id"]}t">{s["text"]}</div>' + byh))
    fromto(t0 + 0.3, f'#{s["id"]}t', "scale: 1.25, opacity: 0", "scale: 1, opacity: 1", 0.45, "expo.out")
    cue("slam", t0 + 0.45, 1.0)
    fromto(t0 + 0.5, f'#{s["id"]}g', "opacity: 0", "opacity: 1", 1.2, "power2.out")
    if by:
        fromto(t0 + 1.2, f'#{s["id"]}b', "opacity: 0", "opacity: 1", 0.45, "power2.out")


def sc_card(s):
    t0, t1 = s["start"], s["end"]
    if s.get("bg"):
        smp = BROLL[s["bg"]][0]
        el_video(f'{s["id"]}v', t0, t1, f'{s["bg"]}.mp4', 0.0)
        credit = f'<div class="credit">{CREDIT[smp]}</div>'
    else:
        credit = ""
    sub = f'<div class="chsub" id="{s["id"]}s">{s["sub"]}</div>' if s.get("sub") else ""
    el_div(f'{s["id"]}o', t0, t1, "qov", (
        '<div class="ch1scrim"></div>' + credit +
        f'<div class="chno" id="{s["id"]}n">{s["no"]}</div>'
        f'<div class="chttl" id="{s["id"]}t">{s["title"]}</div>' + sub))
    cue("riser", max(0.0, t0 - 1.3), 1.0, 1.3)
    glitch(t0, 1.0)
    fromto(t0 + 0.25, f'#{s["id"]}n', "x: -40, opacity: 0", "x: 0, opacity: 1", 0.4, "power3.out")
    fromto(t0 + 0.5, f'#{s["id"]}t', "scale: 1.3, opacity: 0", "scale: 1, opacity: 1", 0.45, "expo.out")
    cue("slam", t0 + 0.7, 1.2)
    cue("sub", t0 + 0.75, 1.0)
    if s.get("sub"):
        fromto(t0 + 1.2, f'#{s["id"]}s', "opacity: 0", "opacity: 1", 0.45, "power2.out")


RECAP_CARDS = [
    ("card15.jpg", "01", "汚名を背負う者", "基準を下げるな"),
    ("card17.jpg", "02", "警告する者", "場所を選べ"),
    ("card18.jpg", "03", "差別された者", "普通でいてくれ"),
    ("card19.jpg", "04", "絶望する者", "礼儀と思いやりを"),
]


def _recap_grid(pref, kw):
    return '<div class="cgrid cgrid2">' + "".join(
        f'<div class="card" id="{pref}c{i}"><img src="assets/img/{img}" alt="">'
        f'<div class="cshade"></div><div class="cnum">{num}</div><div class="clab">{lab}</div>'
        + (f'<div class="ckw" id="{pref}kw{i}">{k}</div>' if kw else "")
        + '</div>'
        for i, (img, num, lab, k) in enumerate(RECAP_CARDS)) + "</div>"


def sc_recap4(s):
    t0, t1 = s["start"], s["end"]
    el_div("rec1", t0, t1, "panel",
           f'<div class="chead" id="rh1">{s.get("head", "4人の告白")}</div>' + _recap_grid("r1", False))
    fromto(t0 + 0.2, "#rh1", "opacity: 0", "opacity: 1", 0.4, "power2.out")
    for i, dt in enumerate([0.5, 0.75, 1.0, 1.25]):
        fromto(t0 + dt, f"#r1c{i}", "y: 70, opacity: 0", "y: 0, opacity: 1", 0.45, "power3.out")
        cue("pop", t0 + dt, 0.6)


def sc_recap4b(s):
    # items = [導入ナレ, 要求1, 要求2, 要求3, 要求4] — スタンプは各行の発話中盤に同期
    t0, t1 = s["start"], s["end"]
    el_div("rec2", t0, t1, "panel",
           f'<div class="chead" id="rh2">{s.get("head", "4人の告白")}</div>' + _recap_grid("r2", True))
    setv(t0 + 0.01, "#rh2", "opacity: 1")
    for i in range(4):
        setv(t0 + 0.01, f"#r2c{i}", "opacity: 1")
    kw_nids = s["nids"][1:5]
    assert len(kw_nids) == 4, f"{EP}: recap4b はナレ5行(導入+4)が必要"
    for i, nid in enumerate(kw_nids):
        st = N[nid]["start"] + 0.55 * N[nid]["dur"]
        fromto(st, f"#r2kw{i}", "scale: 1.8, opacity: 0, rotation: -6",
               "scale: 1, opacity: 1, rotation: -6", 0.26, "power4.in")
        cue("slam", st + 0.26, 0.8)


def sc_ask(s):
    t0, t1 = s["start"], s["end"]
    el_div("askp", t0, t1, "panel tpanel", (
        '<div class="glow" id="askg"></div>'
        '<div class="askt" id="ask1">あなたは、どう思いますか？</div>'
        '<div class="asks" id="ask2">▼ コメントで、あなたの意見を聞かせてください</div>'))
    fromto(t0 + 0.3, "#ask1", "y: 26, opacity: 0", "y: 0, opacity: 1", 0.5, "power3.out")
    cue("whoosh", t0 + 0.3, 0.8)
    fromto(t0 + 0.4, "#askg", "opacity: 0", "opacity: 1", 1.2, "power2.out")
    fromto(t0 + 1.4, "#ask2", "y: 16, opacity: 0", "y: 0, opacity: 1", 0.4, "power2.out")
    cue("pop", t0 + 1.4, 0.6)
    tw(t0 + 2.0, 'tl.to("#ask2", {y: 8, duration: 0.5, ease: "sine.inOut", repeat: 5, yoyo: true}, %T%);')


def sc_end(s):
    t0, t1 = s["start"], s["end"]
    el_div("endp", t0, t1, "panel", (
        '<div class="endt" id="end1">ご視聴 ありがとうございました</div>'
        '<div class="ends" id="end2">チャンネル登録で、次の「告白」をお見逃しなく</div>'))
    fromto(t0 + 0.3, "#end1", "opacity: 0", "opacity: 1", 0.7, "power2.out")
    fromto(t0 + 1.2, "#end2", "opacity: 0", "opacity: 1", 0.5, "power2.out")
    cue("pop", t0 + 1.2, 0.5)


KIND = {"broll": sc_broll, "kick": sc_kick, "q": sc_q, "nv": sc_nv, "diagram": sc_diagram,
        "cases": sc_cases, "pct": sc_pct,
        "counter": sc_counter, "news": sc_news, "journey": sc_journey, "gion": sc_gion,
        "msg": sc_msg, "card": sc_card, "recap4": sc_recap4, "recap4b": sc_recap4b,
        "ask": sc_ask, "end": sc_end}


# ============================================================ v4: トランジション
TR_DEF = {"msg": "zoom", "kick": "flash", "cases": "wipe", "pct": "wipe", "counter": "zoom",
          "diagram": "fade", "news": "slide", "journey": "fade", "gion": "fade",
          "recap4": "wipe", "recap4b": "none", "ask": "fade", "end": "fade",
          "q": "none", "nv": "none", "broll": "none", "card": "none"}
KICK_TR = ["flash", "wipe", "slide"]  # kick は輪番で変化をつける


def apply_tr(tr, s, ids):
    t0 = s["start"]
    main_ids = [i for i in ids if not i.endswith("bgx")]
    if tr == "none" or t0 < 0.4:
        return
    if tr == "fade":  # 黒からディップ
        setv(t0 - 0.01, "#tbk", "opacity: 1")
        tw(t0 + 0.02, 'tl.to("#tbk", {opacity: 0, duration: 0.7, ease: "power2.out"}, %T%);')
    elif tr == "flash":  # 白フラッシュ
        setv(t0, "#flash", "opacity: 0.8")
        tw(t0 + 0.04, 'tl.to("#flash", {opacity: 0, duration: 0.32, ease: "power2.out"}, %T%);')
        cue("pop", t0, 0.7)
    elif tr == "wipe":  # 赤エッジの横ワイプ
        setv(t0 - 0.23, "#twipe", "opacity: 1")
        fromto(t0 - 0.23, "#twipe", "x: -1990", "x: 0", 0.23, "power1.in")
        fromto(t0 + 0.02, "#twipe", "x: 0", "x: 1990", 0.3, "power2.in")
        setv(t0 + 0.35, "#twipe", "opacity: 0, x: -1990")
        cue("whoosh", t0 - 0.2, 0.9)
    elif tr == "slide":  # 横スライドイン
        for eid in main_ids:
            fromto(t0, f"#{eid}", "x: 150", "x: 0", 0.55, "power3.out")
        cue("whoosh", t0, 0.8)
    elif tr == "zoom":  # 黒ディップ + ズーム収束
        setv(t0 - 0.01, "#tbk", "opacity: 1")
        tw(t0 + 0.02, 'tl.to("#tbk", {opacity: 0, duration: 0.55, ease: "power1.out"}, %T%);')
        for eid in ids:
            fromto(t0, f"#{eid}", "scale: 1.1", "scale: 1", 1.2, "power2.out")
        cue("sub", t0, 0.7)


_id_re = re.compile(r'id="([^"]+)"')
_kick_i = 0
for s in SC:
    pre = len(ELS)
    has_bgx = s.get("bgx") and s["kind"] not in ("q", "nv", "broll")
    CUR_BGX[0] = s.get("bgx") if has_bgx else None
    if has_bgx:
        el_video(f'{s["id"]}bgx', s["start"], s["end"], f'bgx_{s["id"]}.mp4', 0.0)
    KIND[s["kind"]](s)
    CUR_BGX[0] = None
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

CSS = """
@font-face { font-family:'NotoB'; src:url('assets/fonts/NotoSansJP-Black.otf') format('opentype'); }
@font-face { font-family:'NotoBd'; src:url('assets/fonts/NotoSansJP-Bold.otf') format('opentype'); }
@font-face { font-family:'SerifJP'; src:url('assets/fonts/NotoSerifJP.ttf') format('truetype');
  font-weight:100 900; }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { background:#000; }
#root { position:relative; width:1920px; height:1080px; overflow:hidden;
  background:#07080b; font-family:'NotoB','NotoBd',sans-serif; color:#f2f1ec; }
#stage { position:absolute; inset:0; }
.clip { position:absolute; inset:0; width:100%; height:100%; }
video.bgv { object-fit:cover; transform:translateZ(0); backface-visibility:hidden; }
em { font-style:normal; color:#e8322e; }
#scan { position:absolute; inset:0; z-index:40; pointer-events:none; opacity:.14;
  background:repeating-linear-gradient(0deg, rgba(0,0,0,.55) 0 2px, rgba(0,0,0,0) 2px 5px); }
#vig { position:absolute; inset:0; z-index:41; pointer-events:none;
  background:radial-gradient(ellipse 115% 105% at 50% 46%, rgba(0,0,0,0) 58%, rgba(0,0,0,.52) 100%); }
#flash { position:absolute; inset:0; z-index:60; background:#e9e6df; opacity:0; pointer-events:none; }
.gl { position:absolute; left:-80px; right:-80px; z-index:59; opacity:0; pointer-events:none; }
#gl1 { background:rgba(232,50,46,.55); } #gl2 { background:rgba(70,224,212,.45); }
#gl3 { background:rgba(242,241,236,.75); }
.qov { z-index:10; }
.qscrim { position:absolute; left:0; right:0; bottom:0; height:430px;
  background:linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(2,3,5,.6) 42%, rgba(2,3,5,.85) 100%); }
.ch1scrim { position:absolute; inset:0;
  background:linear-gradient(180deg, rgba(2,3,5,.35) 0%, rgba(2,3,5,.72) 70%, rgba(2,3,5,.9) 100%); }
.credit { position:absolute; top:34px; right:44px; font-family:'NotoBd'; font-size:26px;
  color:rgba(242,241,236,.85); background:rgba(5,6,9,.55); padding:8px 18px; border-left:4px solid #e8322e; }
.qcap { position:absolute; left:60px; right:60px; bottom:92px; text-align:center; font-size:66px;
  letter-spacing:.02em; text-shadow:0 4px 26px rgba(0,0,0,.9), 0 0 2px rgba(0,0,0,.9); opacity:0; }
.biglabel { position:absolute; left:70px; top:120px; font-size:72px; color:#f2f1ec;
  background:rgba(5,6,9,.66); border-left:10px solid #e8322e; padding:16px 36px; opacity:0; }
.lt { position:absolute; left:70px; bottom:96px; display:flex; opacity:0; }
.ltbar { width:12px; background:#e8322e; }
.ltbody { background:rgba(5,6,9,.78); padding:22px 38px 24px 30px; }
.ltname { font-size:48px; } .ltrole { font-family:'NotoBd'; font-size:27px; color:#ffb648; margin-top:6px; }
.panel { z-index:10; background:#0c1016; }
.tpanel { background:radial-gradient(ellipse 90% 80% at 50% 42%, #10151d 0%, #07080b 70%); }
.panel.clear { background:linear-gradient(180deg, rgba(7,9,13,.78) 0%, rgba(7,9,13,.48) 45%, rgba(7,9,13,.78) 100%); }
.cic { width:96px; height:96px; flex:none; color:#ffb648; background:rgba(18,24,37,.85);
  border:3px solid #232c3d; border-radius:16px; display:flex; align-items:center; justify-content:center; }
.cic svg { width:56px; height:56px; }
#tbk { position:absolute; inset:0; z-index:56; background:#000; opacity:0; pointer-events:none; }
#twipe { position:absolute; left:0; top:-2px; width:1930px; height:1084px; z-index:57; opacity:0;
  background:linear-gradient(90deg, #0a0d12 0%, #131a24 85%, #e8322e 99%, #e8322e 100%);
  transform:translateX(-1990px); pointer-events:none; }
.glow { position:absolute; left:50%; top:50%; width:1500px; height:700px; margin:-350px 0 0 -750px;
  background:radial-gradient(ellipse, rgba(232,50,46,.17), rgba(232,50,46,0) 65%); opacity:0; }
.kstack { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center;
  justify-content:center; gap:36px; padding:0 120px; }
.kick { text-align:center; font-size:84px; line-height:1.35; letter-spacing:.04em; opacity:0;
  text-shadow:0 6px 40px rgba(0,0,0,.8); }
.kline { width:460px; height:10px; background:#e8322e; transform:scaleX(0); }
.kch2 { display:inline-block; opacity:0; }
/* kick 輪番スタイル (v5) */
.kband { position:absolute; left:0; bottom:38%; background:#e8322e; padding:26px 96px 30px 74px;
  transform-origin:left; transform:scaleX(0); box-shadow:0 10px 50px rgba(0,0,0,.55); }
.kband span { font-size:74px; color:#fff; opacity:0; letter-spacing:.06em; white-space:nowrap; }
.kghost { position:absolute; left:50%; top:50%; transform:translate(-50%,-54%);
  font-family:'SerifJP'; font-weight:900; font-size:560px; color:#e8322e; opacity:0; }
.kserif { position:absolute; left:0; right:0; top:42%; text-align:center; font-family:'SerifJP';
  font-weight:900; font-size:92px; letter-spacing:.1em; opacity:0;
  text-shadow:0 6px 40px rgba(0,0,0,.85); }
.ktype { position:absolute; left:0; right:0; top:44%; text-align:center; font-size:80px;
  letter-spacing:.06em; white-space:nowrap; }
.kch { opacity:0; }
.kcaret { display:inline-block; width:8px; height:74px; background:#e8322e; margin-left:14px;
  vertical-align:-6px; }
.kstamp { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%) rotate(-3deg);
  font-size:90px; color:#f2f1ec; border:8px solid #e8322e; padding:22px 58px; border-radius:8px;
  background:rgba(232,50,46,.10); opacity:0; white-space:nowrap; }
.kbar { position:absolute; left:150px; top:37%; width:14px; height:230px; background:#e8322e;
  transform-origin:top; transform:scaleY(0); }
.kmask { position:absolute; left:204px; right:100px; top:37%; height:240px; overflow:hidden; }
.kleft { font-size:78px; line-height:1.32; padding-top:34px; }
/* cases */
.crows { position:absolute; left:320px; right:280px; top:290px; }
.crow { display:flex; align-items:center; gap:36px; margin-bottom:46px; opacity:0; }
.ctag { background:#e8322e; color:#fff; font-family:'NotoBd'; font-size:34px; padding:10px 28px;
  border-radius:8px; white-space:nowrap; min-width:170px; text-align:center; }
.ctx { font-size:52px; }
/* pct */
.pbar { position:absolute; left:240px; right:240px; top:44%; height:130px; display:flex; }
.p99 { width:99%; background:#15202e; border:3px solid #2a3140; display:flex; align-items:center;
  justify-content:center; gap:22px; font-size:42px; color:#c9d2dc; transform-origin:left; }
.p99 span { font-size:64px; color:#46e0a0; }
.p1 { width:1%; background:#e8322e; box-shadow:0 0 36px rgba(232,50,46,.85); transform-origin:right; }
.p1lab { position:absolute; right:240px; top:calc(44% + 165px); text-align:right; font-size:42px;
  line-height:1.45; opacity:0; }
.dhead { position:absolute; left:0; right:0; top:96px; text-align:center; font-size:82px; opacity:0; }
.dnote { position:absolute; left:0; right:0; bottom:64px; text-align:center; font-family:'NotoBd';
  font-size:32px; color:#8a93a0; opacity:0; }
/* mech */
.mstep { position:absolute; top:40%; width:26%; height:270px; display:flex; align-items:center;
  justify-content:center; text-align:center; font-size:46px; line-height:1.3;
  background:#121825; border:3px solid #232c3d; border-radius:18px; opacity:0; }
.mnum { position:absolute; left:50%; top:-34px; width:68px; height:68px; margin-left:-34px; line-height:62px;
  background:#e8322e; border-radius:50%; font-size:38px; }
.mtx { padding:0 24px; }
/* 箱(高さ270px)の垂直中心 = 40%+135px に矢印(高さ36px)の中心を合わせる */
.marrs { position:absolute; top:calc(40% + 117px); width:5%; height:36px; opacity:0; transform-origin:left; }
.stamp { position:absolute; left:50%; top:66%; transform:translateX(-50%) rotate(-8deg);
  font-size:110px; color:#e8322e; border:10px solid #e8322e; padding:6px 46px; border-radius:10px;
  background:rgba(232,50,46,.08); opacity:0; }
/* counter */
.cntlab { position:absolute; left:0; right:0; top:120px; text-align:center; font-family:'NotoBd';
  font-size:44px; color:#8a93a0; letter-spacing:.2em; opacity:0; }
.cntnum { position:absolute; left:0; right:0; top:190px; text-align:center; font-size:200px;
  font-variant-numeric:tabular-nums; letter-spacing:.02em; }
.cntnum span { font-size:70px; color:#ffb648; margin-left:12px; }
.cbars { position:absolute; left:320px; right:320px; top:510px; }
.cbar { position:relative; height:74px; margin-bottom:38px; opacity:0; }
.cbv { position:absolute; left:120px; top:12px; height:50px; max-width:72%;
  background:linear-gradient(90deg, #5a2422, #e8322e); transform-origin:left; border-radius:6px; }
.cby { position:absolute; left:0; top:10px; font-size:40px; color:#8a93a0; font-family:'NotoBd'; }
.cbn { position:absolute; right:0; top:10px; font-size:40px; }
.cntsrc { position:absolute; right:60px; bottom:40px; font-family:'NotoBd'; font-size:24px; color:#5b6472; }
/* news */
.nband { position:absolute; left:0; top:200px; font-size:40px; background:#e8322e; color:#fff;
  padding:14px 60px 14px 40px; font-family:'NotoBd'; }
.ntag { background:#07080b; color:#e8322e; padding:4px 18px; margin-right:26px; letter-spacing:.3em; }
.nhead { position:absolute; left:120px; top:330px; font-size:128px; line-height:1.22; opacity:0; }
.nsub { position:absolute; left:124px; top:700px; font-family:'NotoBd'; font-size:34px; color:#8a93a0; opacity:0; }
/* journey: ◯✕マーク(直径120px, 中心y=34%+60px, 中心x=27%/73%)を縁から縁まで結ぶ */
.jarr { position:absolute; left:calc(27% + 70px); top:calc(34% + 46px); width:744px; height:28px;
  transform-origin:left; transform:scaleX(0); }
.jstop { position:absolute; top:34%; width:26%; text-align:center; opacity:0; }
.jmark { width:120px; height:120px; margin:0 auto 26px; border-radius:50%; font-size:60px; line-height:112px; }
.jx { background:#1c0a0c; border:4px solid #e8322e; color:#e8322e; }
.jo { background:#0e1f18; border:4px solid #46e0a0; color:#46e0a0; }
.jname { font-size:56px; } .jdesc { font-family:'NotoBd'; font-size:33px; color:#8a93a0; margin-top:14px; line-height:1.4; }
/* sign */
.sign { position:absolute; left:50%; top:46%; transform:translate(-50%,-50%); display:flex; gap:40px;
  align-items:center; background:#f2f1ec; color:#14161b; padding:52px 70px; border-radius:14px;
  border:6px solid #b8352f; opacity:0; }
.signic { width:150px; height:150px; color:#14161b; } .signic svg { width:100%; height:100%; }
.signtx { font-size:64px; line-height:1.3; }
.signtx span { color:#b8352f; font-size:54px; }
/* msg (テーゼは極太明朝でドキュメンタリー調) */
.msgt { position:absolute; left:0; right:0; top:34%; text-align:center; font-size:122px; line-height:1.34;
  font-family:'SerifJP'; font-weight:900; opacity:0; }
.msgby { position:absolute; left:0; right:0; top:72%; text-align:center; font-family:'NotoBd';
  font-size:38px; color:#ffb648; opacity:0; }
/* chapter card */
.chno { position:absolute; left:150px; top:330px; font-size:56px; color:#e8322e; letter-spacing:.4em; opacity:0; }
.chttl { position:absolute; left:144px; top:404px; font-size:132px; letter-spacing:.03em;
  font-family:'SerifJP'; font-weight:900; text-shadow:0 8px 50px rgba(0,0,0,.85); opacity:0; }
.chsub { position:absolute; left:152px; top:608px; font-family:'NotoBd'; font-size:38px;
  color:#ffb648; text-shadow:0 2px 14px rgba(0,0,0,.95); opacity:0; }
/* recap cards */
.chead { position:absolute; left:0; right:0; top:84px; text-align:center; font-family:'NotoBd';
  font-size:36px; letter-spacing:.5em; color:#8a93a0; opacity:0; }
.cgrid { position:absolute; left:90px; right:90px; top:190px; bottom:120px; display:flex; gap:34px; }
.card { position:relative; flex:1; border-radius:14px; overflow:hidden; background:#121825; opacity:0; }
.card img { position:absolute; width:auto; height:100%; left:50%; transform:translateX(-50%); filter:saturate(.85); }
.cshade { position:absolute; inset:0; background:linear-gradient(180deg, rgba(2,3,5,.08) 35%, rgba(2,3,5,.88) 88%); }
.cnum { position:absolute; left:26px; top:18px; font-size:54px; color:#e8322e; }
.clab { position:absolute; left:0; right:0; bottom:34px; text-align:center; font-size:42px;
  text-shadow:0 3px 14px rgba(0,0,0,.9); }
.ckw { position:absolute; left:6%; top:38%; width:88%; text-align:center; font-size:44px; color:#ffb648;
  border:5px solid #ffb648; border-radius:8px; padding:10px 4px; transform:rotate(-6deg);
  background:rgba(5,6,9,.55); opacity:0; }
/* ask / end */
.askt { position:absolute; left:0; right:0; top:38%; text-align:center; font-size:118px; opacity:0; }
.asks { position:absolute; left:0; right:0; top:62%; text-align:center; font-family:'NotoBd';
  font-size:44px; color:#ffb648; opacity:0; }
.endt { position:absolute; left:0; right:0; top:42%; text-align:center; font-size:92px; opacity:0; }
.ends { position:absolute; left:0; right:0; top:60%; text-align:center; font-family:'NotoBd';
  font-size:38px; color:#8a93a0; opacity:0; }
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
<div id="tbk"></div>
<div id="twipe"></div>
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
if FULL:
    (ROOT / "subtitles" / "out" / EP / "sfx_cues.json").write_text(
        json.dumps({"total": COMP, "cues": sorted(CUES, key=lambda c: c["t"])}, ensure_ascii=False),
        encoding="utf-8")
print(f"{EP}: built index.html window {W0}-{W1} ({WDUR}s) els={len(ELS)} tweens={len(TWEENS)} cues={len(CUES)}")
