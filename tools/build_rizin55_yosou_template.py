# -*- coding: utf-8 -*-
"""RIZIN.55勝敗予想(THE VERDICT型)テンプレ生成。CIでも動く=標準ライブラリのみ。
   HF_WIN_START/END で窓内の要素だけDOMへ出す。GSAPは絶対時刻のtlに組み、rootがtl.timeを進める(負の位置を作らない)。"""
import html, json, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "tools"))
import rizin55yosou_script as SC
EP = "rizin55_yosou"; TPL = ROOT / "hyperframes/templates" / EP
TIM = json.load(open(ROOT / f"subtitles/out/{EP}/timings.json", encoding="utf-8")); TB = {b["id"]: b for b in TIM["beats"]}
COMP = TIM["total"]; W0 = float(os.environ.get("HF_WIN_START", 0)); W1 = float(os.environ.get("HF_WIN_END", COMP)); FULL = W0 == 0 and W1 >= COMP
CFGF = ROOT / "tools/rizin55yosou_clipcfg.json"; CFG = json.load(open(CFGF, encoding="utf-8")) if CFGF.exists() else {}
BGSRC = {"f5d": "Fighting NEXUS", "f5f": "RIZIN／Fighting NEXUS", "f9c": "DEEP", "f9e": "DEEP／RIZIN", "f12d": "OCTAGON"}
OV = lambda s, e: s < W1 + .6 and e > W0 - .6
vid = []; ov = []; js = []; hits = []; n = [0]; tk = [10]
def J(s, e, c):
    if OV(s, e): js.append(c)
def attr(s, e):
    a = max(s, W0); b = min(e, W1); return round(a - W0, 3), round(b - a, 3)
def video(src, s, e, ms=0, z=1, fx=.5, fy=.5, push=.04, side=None, gray=False):
    if not OV(s, e) or min(e, W1) - max(s, W0) <= .02: return
    n[0] += 1; i = n[0]; W = 960 if side else 1920
    tx = W / 2 - 1920 * z * fx; ty = 540 - 1080 * z * fy; tx = min(0, max(tx, W - 1920 * z)); ty = min(0, max(ty, 1080 - 1080 * z))
    pos = f"left:{W if side == 'r' else 0}px;width:{W}px" + (";filter:grayscale(.9) brightness(.6)" if gray else "")
    st, du = attr(s, e + .4); m = round(ms + max(0, W0 - s), 3)  # +.4s: 次の映像の初フレーム待ちで黒が出ないよう下に残す
    trk = ((3 if side == "l" else 4) + 2 * (i % 2)) if side else i % 2 + 1
    vid.append(f'<div class="vw" id="w{i}" style="{pos}"><video id="v{i}" class="clip" data-start="{st}" data-duration="{du}" data-track-index="{trk}" data-media-start="{m}" src="assets/{src}.mp4" muted playsinline style="width:1920px;height:1080px;transform-origin:0 0;transform:translate({tx:.1f}px,{ty:.1f}px) scale({z})"></video></div>')
    J(s, e, f'tl.fromTo("#w{i}",{{scale:1}},{{scale:{1 + push},duration:{round(e - s, 3)},ease:"none"}},{round(s, 3)});')
def timed(cls, s, e, inner, idv=None, z=None):
    tk[0] += 1; i = idv or f"t{tk[0]}"
    if OV(s, e) and min(e, W1) - max(s, W0) > .02:
        st, du = attr(s, e); zs = f"z-index:{z};" if z else ""
        ov.append(f'<div id="{i}" class="clip {cls}" data-start="{st}" data-duration="{du}" data-track-index="{tk[0]}" style="{zs}">{inner}</div>')
    return i
def flash(t, c="#fff", a=.9, d=.22):
    J(t, t + d, f'tl.set("#fl",{{background:"{c}"}},{t:.3f});tl.fromTo("#fl",{{opacity:{a}}},{{opacity:0,duration:{d},ease:"power2.out"}},{t:.3f});')
def shake(sel, t, amp=20, d=.26):
    x = t
    for a, b in [(1, -.8), (-.9, .6), (.7, .5), (-.5, -.4), (.3, .2), (0, 0)]:
        J(t, t + d, f'tl.to("{sel}",{{x:{a * amp:.1f},y:{b * amp:.1f},duration:{d / 6:.3f},ease:"none"}},{x:.3f});'); x += d / 6
def hit(t, k, p="x"): hits.append(dict(t=round(t, 3), k=k, pick=p))
DKEY = sorted(SC.DISP, key=len, reverse=True)
def disp(x):
    out = []; i = 0
    while i < len(x):
        for k in DKEY:
            if x.startswith(k, i): out.append(SC.DISP[k]); i += len(k); break
        else: out.append(x[i]); i += 1
    return "".join(out)
def zw(s): return sum(.5 if ord(c) < 128 else 1 for c in s)
def okcut(t, c):
    a, b = t[c - 1], t[c]; kat = lambda x: "ァ" <= x <= "ヶ" or x in "ー・" or x.isascii()
    if b in "、。ーぁぃぅぇぉっゃゅょァィゥェォッャュョ！？」": return False
    if kat(a) and kat(b): return False
    return True
def wrap(t, maxw=27):
    if zw(t) <= maxw: return [t]
    best = None
    for c in range(1, len(t)):
        if not okcut(t, c): continue
        a, b = t[:c], t[c:]
        if zw(a) > maxw or zw(b) > maxw: continue
        pri = 0 if a[-1] in "、。" else (6 if a[-1] in "はがをにへでもやねよの" else 14)
        if b[:2] in ("いう", "して", "した", "する", "いる") or a[-2:] in ("する", "いう"): pri += 30
        sc = pri + abs(zw(a) - zw(b))
        if best is None or sc < best[0]: best = (sc, a, b)
    return [best[1], best[2]] if best else None
def cues(t):
    parts = [p for p in re.split(r"(?<=[。])", t) if p]; out = []
    for p in parts:
        if wrap(p): out.append(p); continue
        cur = ""
        for q in [x for x in re.split(r"(?<=[、])", p) if x]:
            if wrap(cur + q): cur += q
            else:
                if cur: out.append(cur)
                cur = q
        if cur: out.append(cur)
    m = []
    for c in out:
        if m and zw(c) <= 6 and wrap(m[-1] + c): m[-1] += c
        else: m.append(c)
    return m
def color(x, F):
    x = html.escape(x)
    if not F: return x
    for nm, cl in ((F["l"], "r"), (F["r"], "b")): x = x.replace(nm, f'<b class="{cl}">{nm}</b>')
    return x
BG_ALIAS = {"f12ishi": ("pred/f12_ishi_b", 36), "f12ishi_a": ("pred/f12_ishi_a", 9), "f12ishi_a2": ("pred/f12_ishi_a", 26), "f13_ishi_a": ("pred/f13_ishi_a", 4), "f13_ishi_b": ("pred/f13_ishi_b", 4)}
USED = {}
def bgv(name, dur):
    if name in BG_ALIAS: return BG_ALIAS[name]
    ms = USED.get(name, 0); USED[name] = ms + dur + .3; return f"bg/{name}", ms
def cfg(c):
    d = CFG.get(c, {}); return d.get("z", 1.24), d.get("fx", .5), d.get("fy", .34), d.get("ms", 8)
FBG = {"f05": "f5c", "f09": "f9c", "f10": "f10g", "f12": "f12f", "f13": "f13h"}
def pvideo(clip, s, e, m, z, fx, fy, sec):
    """予想者クリップ。split指定(画面中央に別物が映る素材)は左半分=本人、右半分=その試合の映像。"""
    if CFG.get(clip, {}).get("split"):
        video(f"pred/{clip}", s, e, m, z, fx, fy, .03, side="l")
        nm, off = bgv(FBG[sec], e - s); video(nm, s, e, off, 1.1, .5, .45, .03, side="r")
    else:
        video(f"pred/{clip}", s, e, m, z, fx, fy, .03)
def src(s, e, t): timed("src", s, e, html.escape("出典：" + t), z=41)
PPOS = {}  # 予想者クリップの再生位置(スラム→本人トークで続きから流す=同じ場面を繰り返さない)
CLIPLEN = 44.5
def ppos(clip, ms, d):
    a = PPOS.get(clip, ms); PPOS[clip] = a + d
    if a + d > CLIPLEN: raise SystemExit(f"clip overrun {clip} {a:.1f}+{d:.1f}")
    return a
def isframe(k): return k.startswith(("av_", "fr_"))
def imgtag(key, h, iid):
    if isframe(key): return f'<img class="frm" id="{iid}" src="assets/cut/{key}.jpg" style="height:520px;width:520px;left:1290px;bottom:240px">'
    return f'<div class="cutw"><img class="cut" src="assets/cut/{key}.png" id="{iid}" style="height:{h}px"></div>'
def slam(idv, s, e, pick, F, who, verdict, quote, date=None, word=None):
    col = {"l": "red", "r": "blue", "n": "gray"}[pick]; nm, key, _ = SC.P[who]
    w = word or (F["l"] if pick == "l" else F["r"]); L = len(w)
    fr = isframe(key)  # 枠写真(右寄せ)の時は大文字を左へ寄せて写真と重ねない
    fs = min(600, int((1380 if fr else 1780) / L)); top = int(120 + (600 - fs) * .42)
    gpad = "padding-right:440px;" if fr else ""
    ql = quote.split("|") if quote else []
    qfs = min(54, int(750 / (max(map(len, ql)) * 1.05))) if ql else 0
    q = f'<div class="q" id="{idv}q" style="font-size:{qfs}px">{"<br>".join(map(html.escape, ql))}</div>' if ql else ""
    dt = f'<div class="dt" id="{idv}d">{html.escape(date)}</div>' if date else ""
    inner = f'<div class="sb {col}" id="{idv}b"><div class="st"></div><div class="gk" id="{idv}k" style="font-size:{fs}px;top:{top}px;{gpad}">{w}</div>{imgtag(key, 860, idv + "i")}<div class="rc"><div class="nm" id="{idv}n">{html.escape(nm)}</div><div class="vd" id="{idv}v">{html.escape(verdict)}</div>{dt}</div>{q}</div>'
    timed("slam", s, e, inner, idv=idv, z=20)
    J(s, e, f'tl.from("#{idv}k",{{scale:1.7,opacity:0,duration:.26,ease:"expo.out"}},{s:.3f});')
    if not isframe(key):
        J(s, e, f'tl.fromTo("#{idv}i",{{y:150,xPercent:-50,scale:1.12}},{{y:0,xPercent:-50,scale:1,duration:.32,ease:"back.out(1.6)"}},{s + .03:.3f});tl.to("#{idv}i",{{scale:1.035,duration:{max(.1, e - s - .35):.3f},ease:"none"}},{s + .35:.3f});')
    else:
        J(s, e, f'tl.fromTo("#{idv}i",{{y:120,rotation:-5}},{{y:0,rotation:-2,duration:.32,ease:"back.out(1.6)"}},{s + .03:.3f});')
    J(s, e, f'tl.from("#{idv}n",{{x:90,opacity:0,duration:.2,ease:"power4.out"}},{s + .08:.3f});tl.from("#{idv}v",{{scale:3.2,opacity:0,rotation:-16,duration:.2,ease:"power4.in"}},{s + .14:.3f});')
    if ql: J(s, e, f'tl.from("#{idv}q",{{opacity:0,y:-36,duration:.28,ease:"power2.out"}},{s + .22:.3f});')
    shake(f"#{idv}b", s + .3); flash(s, "#fff", .85, .2)
    hit(s, "stamp", pick); hit(s + .34, "thud", pick)
KWI = [0]
def kw(t0, t1, text):
    KWI[0] += 1; k = KWI[0] % 3; i = f"kw{KWI[0]}"
    if k == 0:
        inner = f'<div class="kt" id="{i}">{html.escape(text)}</div>'; code = f'tl.from("#{i}",{{opacity:0,scale:1.25,duration:.4,ease:"power2.out"}},{t0:.3f});'
    elif k == 1:
        inner = f'<div class="kt w"><i id="{i}">{html.escape(text)}</i></div>'; code = f'tl.fromTo("#{i}",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:.34,ease:"power3.out"}},{t0:.3f});'
    else:
        sp = "".join(f'<span id="{i}_{j}">{html.escape(c)}</span>' for j, c in enumerate(text))
        inner = f'<div class="kt">{sp}</div>'; code = "".join(f'tl.from("#{i}_{j}",{{opacity:0,y:46,duration:.22,ease:"back.out(1.7)"}},{t0 + j * .035:.3f});' for j in range(len(text)))
    timed("kick", t0, t1, inner, z=15); J(t0, t1, code); hit(t0, "whoosh")
SEC_SCORE = {}; COUNTED = {}; EV = {}; LINE = {}
SS = SC.S
def add_score(sec, who, pick, t, flip=False):
    sc = SEC_SCORE.setdefault(sec, dict(l=0, r=0)); ct = COUNTED.setdefault(sec, {})
    if who in ct and ct[who] != pick: sc[ct[who]] -= 1
    sc[pick] += 1; ct[who] = pick
    EV.setdefault(sec, []).append((t, sc["l"], sc["r"]))
    L = LINE.setdefault(sec, {"l": [], "r": []})
    for k in "lr":
        if who in L[k]: L[k].remove(who)
    L[pick].append(who)
SHORT = {"ストラッサー起一": "ストラッサー", "扇久保博正": "扇久保", "ジョビン": "ジョビン", "井上雄策": "雄策", "チャーリー柏": "チャーリー"}
def lineup_col(a, c, i, lift=0):
    w = min(235, int(920 / max(1, len(a)))); ih = min(600, int(w * 2.55)); fz = 40 if w >= 190 else 30; o = ""; nmrow = ""
    for j, p in enumerate(a):
        nmf, key, _ = SC.P[p]; short = SHORT.get(nmf, nmf[:2])
        im = f'<img class="ff" src="assets/cut/{key}.jpg" style="width:{int(w * .92)}px;height:{int(w * .92)}px">' if isframe(key) else f'<img src="assets/cut/{key}.png" style="height:{ih}px">'
        vt = ' class="vt"' if w < 150 else ""
        o += f'<div class="lu" id="lu{i}{c}{j}" style="width:{w}px">{im}</div>'
        nmrow += f'<div class="lu" id="lu{i}{c}{j}n" style="width:{w}px"><span{vt} style="font-size:{fz}px">{short}</span></div>'
    return o + f'</div><div class="lr lrn" style="bottom:{lift}px">{nmrow}'  # 名前は別レイヤー(全員の写真より上)
first_seen = set()
for i, b in enumerate(SS):
    t = TB[b["id"]]; s, e = t["start"], t["end"]; sec = b.get("sec", "op"); F = SC.FIGHTS.get(sec)
    nxt = SS[i + 1] if i + 1 < len(SS) else None; vis_e = TB[nxt["id"]]["start"] if nxt else COMP
    if b["kind"] == "n":
        dur = t["dur"]; raw = b["text"]; mark = raw.find("|"); ratio = (mark / max(1, len(raw) - 1)) if mark >= 0 else None
        txt = raw.replace("|", "")
        if b.get("black"):
            timed("black", s - .05, vis_e, f'<div class="dag" id="dag{i}">{txt}</div>', z=30)
            J(s, e, f'tl.from("#dag{i}",{{opacity:0,scale:1.15,duration:.3,ease:"power2.out"}},{s:.3f});'); hit(s - .05, "tape")
        elif b.get("pred"):
            z, fx, fy, ms = cfg(b["clip"]); ts = round(s + dur * (ratio if ratio is not None else .3) - .05, 3)
            if not b.get("fast"): ts = max(s + .5, ts)
            pvideo(b["clip"], s, ts + .1, ppos(b["clip"], ms, ts + .1 - s), z, fx, fy, sec)
            slam(f"s{i}", ts, vis_e, b["pick"], F, b["pred"], b["verdict"], b.get("quote"), b.get("date"), b.get("word"))
            src(s, vis_e, b.get("src") or SC.P[b["pred"]][2])
            if b["pick"] in "lr" and not b.get("nocount"): add_score(sec, b["pred"], b["pick"], ts)
        elif b.get("talk"):
            z, fx, fy, ms = cfg(b["clip"]); who = b["talk"]
            pvideo(b["clip"], s, vis_e, ppos(b["clip"], ms, vis_e - s + .1), z, fx, fy, sec); src(s, vis_e, b.get("src") or SC.P[who][2])
            timed("kick", s + .1, vis_e, f'<div class="sp"><div class="nm" id="np{i}">{html.escape(SC.P[who][0])}</div></div>', z=16)
            J(s, e, f'tl.from("#np{i}",{{x:-80,opacity:0,duration:.25,ease:"expo.out"}},{s + .1:.3f});')
            if b.get("kw"): kw(s + .15, vis_e, b["kw"])
        elif b.get("clip"):
            z, fx, fy, ms = cfg(b["clip"])
            if nxt and nxt["kind"] == "r" and nxt.get("clip") == b["clip"]: ms = max(0, nxt["ss"] - (vis_e - s))
            video(f"pred/{b['clip']}", s, vis_e, ms, z, fx, fy, .03); src(s, vis_e, SC.P[b["who"]][2])
            timed("kick", s + .1, vis_e, f'<div class="sp"><div class="nm" id="np{i}">{html.escape(SC.P[b["who"]][0])}</div></div>', z=16)
            J(s, e, f'tl.from("#np{i}",{{x:-80,opacity:0,duration:.25,ease:"expo.out"}},{s + .1:.3f});')
        elif b.get("summary"):
            rows = ""
            for j, k in enumerate(["f05", "f09", "f10", "f12", "f13"]):
                G = SC.FIGHTS[k]; sc = SEC_SCORE[k]; ra = .5 + (sc["l"] - sc["r"]) / (2 * (sc["l"] + sc["r"])) * .8
                rows += f'<div class="sr{" m" if k == "f13" else ""}" id="sr{j}"><div class="no">{G["no"]}</div><div class="nl">{G["l"]}</div><div class="sn">{sc["l"]}</div><div class="bt"><u style="transform:scaleX({ra:.3f})"></u></div><div class="sn">{sc["r"]}</div><div class="nr">{G["r"]}</div></div>'
            timed("sum", s - .1, vis_e, rows, z=24)
            for j, p in enumerate([0, .2, .4, .6, .82]):
                tj = s + dur * p; J(s, e, f'tl.from("#sr{j}",{{x:-160,opacity:0,duration:.3,ease:"expo.out"}},{tj:.3f});'); hit(tj, "thud")
        elif b.get("roll"):
            pre, a, c = b["roll"]; rid = f"rd{i}"
            nm, off = bgv(b["bg"], vis_e - s); video(nm, s, vis_e, off, 1.24, .5, .34, .03, gray=True)
            timed("roller", s, vis_e, f'<div class="rl">{pre}<span id="{rid}">{a:02d}</span></div>', z=27)
            step = dur * .9 / (c - a)
            for j, d in enumerate(range(a + 1, c + 1)):
                tt = s + j * step + .1; J(s, e, f'tl.set("#{rid}",{{textContent:"{d:02d}"}},{tt:.3f});'); hit(tt, "tick")
        else:
            if b.get("ending"):
                video("bg/f13c_2", s - .05, vis_e, 8, 1.25, .3, .5, .05, side="l"); video("bg/f13f", s - .05, vis_e, 6, 1.2, .5, .42, .05, side="r")
                timed("split", s - .05, vis_e, '<div class="spl r"><span id="spl">王者の<br>初防衛か</span></div><div class="spl b"><span id="spr">新王者の<br>誕生か</span></div>', z=24)
                J(s, e, f'tl.from("#spl",{{x:-90,opacity:0,duration:.3,ease:"expo.out"}},{s + .05:.3f});tl.from("#spr",{{x:90,opacity:0,duration:.3,ease:"expo.out"}},{s + dur * .5:.3f});')
                flash(s - .05, "#fff", .7, .25); hit(s - .05, "whoosh"); hit(s + dur * .5, "thud")
            else:
                nm, off = bgv(b["bg"], vis_e - s); isp = nm.startswith("pred/")
                z, fx, fy, _ = cfg(nm[5:]) if isp else (1, .5, .5, 0)
                video(nm, s, vis_e, off, z, fx, fy, .04)
                if not isp: src(s, vis_e, BGSRC.get(b["bg"], "RIZIN"))
            if b.get("fi"):
                sd = b["fi"]; key = F["lc"] if sd == "l" else F["rc"]; full = F["lf"] if sd == "l" else F["rf"]; col = "r" if sd == "l" else "b"
                full = full if len(full) < 9 else full.split("・")[-1]
                timed("fi", s + .15, vis_e, f'<div class="fishade"></div><div class="fiw" id="fw{i}"><img src="assets/cut/{key}.png"></div><div class="fin" id="fn{i}"><small>{F["no"]}</small><b class="{col}">{html.escape(full)}</b></div>', z=16)
                J(s, e, f'tl.from("#fw{i}",{{x:160,opacity:0,duration:.34,ease:"expo.out"}},{s + .15:.3f});tl.from("#fn{i}",{{x:-120,opacity:0,duration:.3,ease:"expo.out"}},{s + .25:.3f});'); hit(s + .15, "boom", sd)
            if b.get("kw"): kw(s + .15, vis_e, b["kw"])
            if b.get("tally"):
                sc = SEC_SCORE[sec]; lead = "r" if sc["l"] >= sc["r"] else "b"
                timed(f"tint {lead}", s, vis_e, "", z=12)
                timed("tally", s + .05, vis_e, f'<div class="tl4" id="ta{i}"><b>{sc["l"]}</b><i>:</i><b>{sc["r"]}</b></div>', z=26)
                J(s, e, f'tl.from("#ta{i}",{{scale:2.6,opacity:0,duration:.22,ease:"power4.in"}},{s + .05:.3f});'); shake(f"#ta{i}", s + .27); flash(s + .27, "#fff", .8, .2); hit(s + .27, "boom")
            if b.get("lineup"):
                L = LINE[sec]; sc = SEC_SCORE[sec]; lift = 150 if max(len(L["l"]), len(L["r"])) > 6 else 0  # 大人数は写真が小さく字幕に隠れるので持ち上げる
                timed("lineup", s, vis_e, f'<div class="lh red"><div class="lw" style="font-size:{min(300, int(860 / len(F["l"])))}px">{F["l"]}</div><div class="lr" style="bottom:{lift}px">{lineup_col(L["l"], "r", i, lift)}</div></div><div class="lh blue"><div class="lw" style="font-size:{min(300, int(860 / len(F["r"])))}px">{F["r"]}</div><div class="lr" style="bottom:{lift}px">{lineup_col(L["r"], "b", i, lift)}</div></div><div class="sc" id="sc{i}"><b>{sc["l"]}</b><i>:</i><b>{sc["r"]}</b></div>', idv=f"lua{i}", z=22)
                for j in range(max(len(L["l"]), len(L["r"]))):
                    for c, lst in (("r", L["l"]), ("b", L["r"])):
                        if j < len(lst): J(s, e, f'tl.from("#lu{i}{c}{j}",{{y:520,duration:.26,ease:"back.out(1.3)"}},{s + .05 + j * .08:.3f});tl.from("#lu{i}{c}{j}n",{{y:520,duration:.26,ease:"back.out(1.3)"}},{s + .05 + j * .08:.3f});')
                    hit(s + .05 + j * .08, "thud")
                J(s, e, f'tl.from("#sc{i}",{{scale:3,opacity:0,duration:.2,ease:"power4.in"}},{s + .3:.3f});'); flash(s, "#fff", .9, .3); shake(f"#lua{i}", s + .5, 22, .3); hit(s + .5, "boom")
            if b.get("title_at"):
                ti = round(s + dur * b["title_at"], 3)
                timed("title", ti, vis_e, '<div class="tt1" id="tt1">THE VERDICT</div><div class="tt2" id="tt2">格闘家たちの勝敗予想</div><div class="tt3" id="tt3">abc presents RIZIN.55　2026.11.8</div>', z=26)
                J(s, e, f'tl.from("#tt1",{{scale:2.4,opacity:0,duration:.28,ease:"power4.in"}},{ti:.3f});tl.from("#tt2",{{y:50,opacity:0,duration:.25,ease:"expo.out"}},{ti + .3:.3f});tl.from("#tt3",{{opacity:0,y:-20,duration:.25,ease:"power2.out"}},{ti + .5:.3f});')
                flash(ti + .28, "#fff", .9, .3); hit(ti + .28, "boom")
        if F and sec not in first_seen:
            first_seen.add(sec)
            timed("fcard", s, s + 2.1, f'<img id="fc{i}" src="assets/card/{F["card"]}.jpg">', z=18)
            J(s, s + 2.1, f'tl.fromTo("#fc{i}",{{scale:1}},{{scale:1.05,duration:2.1,ease:"none"}},{s:.3f});'); flash(s, "#fff", .6, .2); hit(s, "boom")
        if not (b.get("black") or b.get("summary")):
            cs = cues(txt); tot = sum(len(c) for c in cs); tc = s
            for j, c in enumerate(cs):
                d = dur * len(c) / tot; dc = disp(c).rstrip("。"); ln = wrap(dc) or [dc]
                if max(zw(x) for x in ln) > 27 or len(ln) > 2: raise SystemExit(f"caption overflow {b['id']} {dc}")
                sid = f"c{i}_{j}"; sp = "".join(f'<span id="{sid}_{q}">{color(x, F)}</span>' for q, x in enumerate(ln))
                timed("cap", tc, (tc + d + .06) if j < len(cs) - 1 else e + .1, f'<div class="capin">{sp}</div>', idv=sid, z=40)
                for q in range(len(ln)):
                    J(tc, tc + d, f'tl.from("#{sid}_{q}",{{opacity:0,y:16,duration:.14,ease:"power3.out"}},{tc + d * .5 * q:.3f});')
                tc += d
    else:
        ss = b["ss"]; z, fx, fy, _ = cfg(b["clip"])
        video(f"pred/{b['clip']}", s, vis_e, ss, z, fx, fy, .03); PPOS[b["clip"]] = max(PPOS.get(b["clip"], 0), ss + (vis_e - s) + .1)
        ql = b["quote"].split("|"); fs = min(120, int(1100 / max(map(len, ql))))
        sp = "".join(f'<span id="bq{i}_{j}" style="font-size:{fs}px">{html.escape(x)}</span>' for j, x in enumerate(ql))
        nmp = f'<div class="nm" id="bn{i}">{html.escape(b["who"])}</div>'
        if b.get("pred"): nmp += f'<div class="vd" id="bv{i}">{html.escape(b["verdict"])}</div>'
        if b.get("date"): nmp += f'<div class="dt">{b["date"]}</div>'
        timed("bq", s, vis_e, f'<div class="bigq">{sp}</div><div class="sp">{nmp}</div>', z=25)
        for j in range(len(ql)):
            tj = s + .1 + (e - s) * .5 * j
            J(s, e, f'tl.from("#bq{i}_{j}",{{scale:1.8,opacity:0,duration:.18,ease:"power4.in"}},{tj:.3f});'); hit(tj + .18, "thud", b.get("pick", "x"))
        J(s, e, f'tl.from("#bn{i}",{{x:-80,opacity:0,duration:.22,ease:"expo.out"}},{s + .1:.3f});')
        if b.get("pred"):
            tc = round(s + (e - s) * .5, 3)
            J(s, e, f'tl.from("#bv{i}",{{scale:3,opacity:0,rotation:-12,duration:.2,ease:"power4.in"}},{tc:.3f});'); flash(tc, "#E8192C" if b["pick"] == "l" else "#0F6FFF", .6, .22); hit(tc, "stamp", b["pick"])
            add_score(sec, b["pred"], b["pick"], tc, b.get("flip", False))
        src(s, vis_e, next(v[2] for v in SC.P.values() if v[0] == b["who"]))
huds = ""
for sec, F in SC.FIGHTS.items():
    beats = [b for b in SS if b.get("sec") == sec]; a = next(TB[b["id"]]["start"] for b in beats if b.get("hud", True))
    z = max(TB[b["id"]]["end"] for b in beats); nx = [TB[b["id"]]["start"] for b in SS if TB[b["id"]]["start"] > z]; z = nx[0] if nx else COMP
    if not OV(a, z) or min(z, W1) - max(a, W0) <= .02: continue
    st, du = attr(a, z); tk[0] += 1
    huds += f'<div id="hud{sec}" class="clip" data-start="{st}" data-duration="{du}" data-track-index="{tk[0]}" style="left:0;right:0;top:0;height:100px;z-index:50"><div class="hb" id="hb{sec}"><span class="hno">{F["no"]}</span><span class="hn r">{F["l"]}</span><span class="hs" id="hl{sec}">0</span><div class="ht"><div class="hf" id="hf{sec}"></div><div class="hm"></div></div><span class="hs" id="hr{sec}">0</span><span class="hn b">{F["r"]}</span></div></div>'
    js.append(f'tl.set("#hf{sec}",{{scaleX:.5}},0);tl.from("#hb{sec}",{{y:-120,duration:.35,ease:"expo.out"}},{a:.3f});')
    for tv, l, r in EV.get(sec, []):
        ra = .5 + (l - r) / (2 * max(1, l + r)) * .8; t2 = tv + .14
        js.append(f'tl.set("#hl{sec}",{{textContent:"{l}"}},{t2:.3f});tl.set("#hr{sec}",{{textContent:"{r}"}},{t2:.3f});tl.fromTo("#hl{sec},#hr{sec}",{{scale:1.5}},{{scale:1,duration:.25,ease:"back.out(2)",immediateRender:false}},{t2:.3f});tl.to("#hf{sec}",{{scaleX:{ra:.3f},duration:.45,ease:"elastic.out(1,.55)"}},{t2:.3f});')
    for b in beats:
        if b.get("black") or b.get("ending") or b.get("lineup"):
            bs = TB[b["id"]]["start"]; nx2 = [TB[x["id"]]["start"] for x in SS if TB[x["id"]]["start"] > bs]; be = nx2[0] if nx2 else COMP
            js.append(f'tl.to("#hb{sec}",{{opacity:0,duration:.01}},{bs - .06:.3f});tl.to("#hb{sec}",{{opacity:1,duration:.01}},{be:.3f});')
ee = TB["e2"]["end"]
timed("end", ee, COMP, '<div class="tt1 e" id="eV">THE VERDICT</div>', z=31)
J(ee, COMP, f'tl.from("#eV",{{scale:1.5,opacity:0,duration:.16,ease:"power4.in"}},{ee:.3f});'); flash(ee, "#fff", 1, .25); hit(ee, "final")
css = open(ROOT / "tools/rizin55yosou_style.css", encoding="utf-8").read()
JS = "\n".join(js)
doc = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{css}</style></head><body>
<div id="root" data-composition-id="root" data-start="0" data-duration="{round(W1 - W0, 3)}" data-width="1920" data-height="1080">
<div id="stage">{''.join(vid)}<div class="vig"></div>{''.join(ov)}{huds}<div id="fl"></div></div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});
{JS}
const root=gsap.timeline({{paused:true}});tl.time({W0});root.fromTo(tl,{{time:{W0}}},{{time:{W1},duration:{round(W1 - W0, 3)},ease:"none"}},0);
window.__timelines["root"]=root;</script></div></body></html>'''
TPL.mkdir(parents=True, exist_ok=True); (TPL / "index.html").write_text(doc, encoding="utf-8")
if FULL:
    json.dump(dict(hits=sorted(hits, key=lambda x: x["t"]), events=EV, line=LINE, score=SEC_SCORE), open(ROOT / f"subtitles/out/{EP}/visual_events.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    chars = sorted(set(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", "", doc, flags=re.S)) | set("0123456789.-:"))
    (ROOT / f"subtitles/out/{EP}/chars.txt").write_text("".join(chars), encoding="utf-8")
    print("score", SEC_SCORE, "hits", len(hits), "comp", COMP)
