# -*- coding: utf-8 -*-
"""今週の格闘技ニュース（weekly1113）テンプレ生成。rizin55_kanso のビルダーを流用。CIでも動く＝標準ライブラリのみ。
   HF_WIN_START/END で窓内の要素だけDOMへ出す。GSAPは絶対時刻のtlに組み、rootがtl.timeを進める（負の位置を作らない）。"""
import html, json, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "tools"))
import weekly1113_script as SC
EP = SC.EP; TPL = ROOT / "hyperframes/templates" / EP
TIM = json.load(open(ROOT / f"subtitles/out/{EP}/timings.json", encoding="utf-8")); TB = {b["id"]: b for b in TIM["beats"]}
COMP = TIM["total"]; W0 = float(os.environ.get("HF_WIN_START", 0)); W1 = float(os.environ.get("HF_WIN_END", COMP)); FULL = W0 == 0 and W1 >= COMP
CFGF = ROOT / "tools/weekly1113_clipcfg.json"; CFG = json.load(open(CFGF, encoding="utf-8")) if CFGF.exists() else {}
LENF = ROOT / "tools/weekly1113_cliplen.json"; CLEN = json.load(open(LENF, encoding="utf-8")) if LENF.exists() else {}
OV = lambda s, e: s < W1 + .6 and e > W0 - .6
vid = []; ov = []; js = []; hits = []; n = [0]; tk = [10]; USE = []
def J(s, e, c):
    if OV(s, e): js.append(c)
def attr(s, e):
    a = max(s, W0); b = min(e, W1); return round(a - W0, 3), round(b - a, 3)
def cfg(c):
    d = CFG.get(c, {}); return d.get("z", 1.0), d.get("fx", .5), d.get("fy", .5)
def segname(src, ms): return f"{src}_{int(round(ms * 10))}"
def video(src, s, e, ms=0, push=.04, side=None):
    if s < .3 and ms >= s: ms -= s; s = 0  # 冒頭0.25秒の黒を出さない（映像だけ先に始める）
    USE.append((src, round(ms, 2), round(ms + e - s, 2)))
    if src in CLEN and ms + (e - s) > CLEN[src] + .05: raise SystemExit(f"clip overrun {src} {ms:.1f}+{e - s:.1f} > {CLEN[src]}")
    if not OV(s, e) or min(e, W1) - max(s, W0) <= .02: return
    z, fx, fy = cfg(src)
    n[0] += 1; i = n[0]; W = 960 if side else 1920
    tx = W / 2 - 1920 * z * fx; ty = 540 - 1080 * z * fy; tx = min(0, max(tx, W - 1920 * z)); ty = min(0, max(ty, 1080 - 1080 * z))
    pos = f"left:{W if side == 'r' else 0}px;width:{W}px"
    st, du = attr(s, e + .4); m = round(max(0, W0 - s), 3)  # +.4s: 次の映像の初フレーム待ちで黒が出ないよう下に残す。素材は使用区間だけ切り出した seg/ を参照（容量節約）
    trk = ((3 if side == "l" else 4) + 2 * (i % 2)) if side else i % 2 + 1
    vid.append(f'<div class="vw" id="w{i}" style="{pos}"><video id="v{i}" class="clip" data-start="{st}" data-duration="{du}" data-track-index="{trk}" data-media-start="{m}" src="assets/seg/{segname(src, ms)}.mp4" muted playsinline style="width:1920px;height:1080px;transform-origin:0 0;transform:translate({tx:.1f}px,{ty:.1f}px) scale({z})"></video></div>')
    J(s, e, f'tl.fromTo("#w{i}",{{scale:1}},{{scale:{1 + push},duration:{round(e - s, 3)},ease:"none"}},{round(s, 3)});')
def timed(cls, s, e, inner, idv=None, z=None):
    tk[0] += 1; i = idv or f"t{tk[0]}"
    if OV(s, e) and min(e, W1) - max(s, W0) > .02:
        st, du = attr(s, e); zs = f"z-index:{z};" if z else ""
        ov.append(f'<div id="{i}" class="clip {cls}" data-start="{st}" data-duration="{du}" data-track-index="{tk[0]}" style="{zs}">{inner}</div>')
        # 表示/非表示をGSAPのopacityで明示する（visibilityは層合成で上書きされる。層合成モードのピースでは clip の自動切替が効かず前のテロップが残るため。2026-11-09）
        js.append(f'tl.set("#{i}",{{opacity:0}},{W0:.3f});tl.set("#{i}",{{opacity:1}},{max(s, W0):.3f});tl.set("#{i}",{{opacity:0}},{e:.3f});')
    return i
def flash(t, c="#fff", a=.9, d=.22):
    J(t, t + d, f'tl.set("#fl",{{background:"{c}"}},{t:.3f});tl.fromTo("#fl",{{opacity:{a}}},{{opacity:0,duration:{d},ease:"power2.out"}},{t:.3f});')
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
    if "一" <= a <= "龥" and "一" <= b <= "龥": return False  # 熟語・人名の途中で切らない
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
        if wrap(disp(p)): out.append(p); continue
        cur = ""
        for q in [x for x in re.split(r"(?<=[、])", p) if x]:
            if wrap(disp(cur + q)): cur += q
            else:
                if cur: out.append(cur)
                cur = q
        if cur: out.append(cur)
    m = []
    for c in out:
        if m and zw(disp(c)) <= 6 and wrap(disp(m[-1] + c)): m[-1] += c
        else: m.append(c)
    return m
NAMES = ["関原翔", "関原", "濱田巧", "濱田", "佐伯繁", "佐伯", "神龍誠", "神龍", "トニー・ララミー", "青木真也", "青木", "シェイドゥラエフ", "秋元強真", "秋元", "榊原信行", "榊原", "ダニー・サバテロ", "サバテロ", "後藤丈治", "イリスベク・ティレノフ", "井上直樹", "アバイジャ・カレオ・メヘウラ", "メヘウラ", "相本宗輝", "相本", "金原正徳", "ルイス・グスタボ", "朝倉未来", "鈴木千裕", "YA-MAN", "桜庭大世", "ダナ・ホワイト", "ハビブ・ヌルマゴメドフ", "イスラム・マカチェフ"]
def color(x):
    x = html.escape(x)
    for nm in sorted(NAMES, key=len, reverse=True):
        if nm in x: x = x.replace(nm, f"\x00{nm}\x01")
    return x.replace("\x00", '<b class="y">').replace("\x01", "</b>")
def src(s, e, t):
    if t: timed("src", s, e, html.escape("出典：" + t), z=41)
KWI = [0]
def kw(t0, t1, text):
    KWI[0] += 1; k = KWI[0] % 3; i = f"kw{KWI[0]}"; text = disp(text)
    if k == 0:
        inner = f'<div class="kt" id="{i}">{html.escape(text)}</div>'; code = f'tl.from("#{i}",{{opacity:0,scale:1.25,duration:.4,ease:"power2.out"}},{t0:.3f});'
    elif k == 1:
        inner = f'<div class="kt w"><i id="{i}">{html.escape(text)}</i></div>'; code = f'tl.fromTo("#{i}",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:.34,ease:"power3.out"}},{t0:.3f});'
    else:
        sp = "".join(f'<span id="{i}_{j}">{html.escape(c)}</span>' for j, c in enumerate(text))
        inner = f'<div class="kt">{sp}</div>'; code = "".join(f'tl.from("#{i}_{j}",{{opacity:0,y:46,duration:.22,ease:"back.out(1.7)"}},{t0 + j * .035:.3f});' for j in range(len(text)))
    if zw(text) * (72 if k == 1 else 64) > 1760: raise SystemExit(f"kw too wide {text}")
    timed("kick", t0, t1, inner, z=15); J(t0, t1, code); hit(t0, "whoosh")
def plate(i, s, e, who):
    timed("kick", s + .1, e, f'<div class="sp tp"><div class="nm" id="np{i}">{html.escape(who)}</div></div>', z=16)
    J(s, e, f'tl.from("#np{i}",{{x:-80,opacity:0,duration:.25,ease:"expo.out"}},{s + .1:.3f});')
_CHAMPS = [("ライト級", "ルイス・グスタボ", "gustavo", "ブラジル"), ("フェザー級", "シェイドゥラエフ", "shaydullaev", "キルギス"), ("バンタム級", "ダニー・サバテロ", "sabatello", "アメリカ"), ("フライ級", "トニー・ララミー", "laramie", "カナダ")]
SS = SC.S; ORDER = [b["id"] for b in TIM["beats"]]
SB = {b["id"]: b for b in SS}
for i, bid in enumerate(ORDER):
    t = TB[bid]; s, e = t["start"], t["end"]; vis_e = TB[ORDER[i + 1]]["start"] if i + 1 < len(ORDER) else COMP
    if t["kind"] == "c":
        b = SB[bid[:-5]]; no, title = b["chap"]
        inner = '<div class="cbg2"></div>'
        fs = min(110, int(1640 / zw(title)))
        inner += f'<div class="cshade"></div><div class="cno" id="cn{i}">{html.escape(no)}</div><div class="cti" id="ct{i}" style="font-size:{fs}px">{html.escape(title)}</div><div class="cbar" id="cb{i}"></div>'
        timed("chap", s, vis_e, inner, z=35)
        J(s, vis_e, f'tl.from("#cn{i}",{{x:-200,opacity:0,duration:.35,ease:"expo.out"}},{s:.3f});tl.from("#cb{i}",{{scaleX:0,duration:.4,ease:"expo.out"}},{s + .1:.3f});tl.from("#ct{i}",{{y:60,opacity:0,duration:.35,ease:"expo.out"}},{s + .2:.3f});')
        flash(s, "#fff", .8, .25); hit(s, "chap"); continue
    b = SB[bid]
    if t["kind"] == "n":
        dur = t["dur"]; txt = b["text"]
        video(b["bg"], s, vis_e, b.get("at", 0), .03 if b.get("talk") else .05)
        src(s, vis_e, SC.P[b["talk"]][1] if b.get("talk") else SC.src_of(b["bg"]))
        if b.get("talk"): plate(i, s, vis_e, SC.P[b["talk"]][0])
        if b.get("kw"): kw(s + .15, vis_e, b["kw"])
        if b.get("title"):
            ti = round(s + .2, 3)
            timed("title", ti, vis_e, '<div class="tt1 j" id="tt1">今週の格闘技ニュース</div><div class="tt2 d" id="tt2">2026.11.13</div><div class="tt3" id="tt3">関原翔の状況／神龍誠の会見／超RIZIN.6 ほか</div>', z=26)
            J(s, e, f'tl.from("#tt1",{{scale:2.4,opacity:0,duration:.28,ease:"power4.in"}},{ti:.3f});tl.from("#tt2",{{y:50,opacity:0,duration:.25,ease:"expo.out"}},{ti + .3:.3f});tl.from("#tt3",{{opacity:0,y:-20,duration:.25,ease:"power2.out"}},{ti + .5:.3f});')
            flash(ti + .28, "#fff", .9, .3); hit(ti + .28, "boom")
        if b.get("cards"):
            rows = [("タイトルマッチ", "シェイドゥラエフ", "秋元強真"), ("", "ルイス・グスタボ", "朝倉未来"), ("", "鈴木千裕", "YA-MAN"), ("ヘビー級GP決勝", "スダリオ剛", "エドポロキング"), ("引退試合", "青木真也", "桜庭大世")]
            inner = '<div class="eh">超RIZIN.6　主な決定カード</div>' + "".join(f'<div class="er" id="er{i}_{j}">{("<small>" + html.escape(l) + "</small>") if l else ""}<span>{html.escape(a)}</span><i>vs</i><span>{html.escape(c)}</span></div>' for j, (l, a, c) in enumerate(rows))
            timed("cards", s + .1, vis_e, inner, z=24)
            for j in range(len(rows)):
                tj = s + .3 + dur * .16 * j; J(s, vis_e, f'tl.from("#er{i}_{j}",{{x:-140,opacity:0,duration:.32,ease:"expo.out"}},{tj:.3f});'); hit(tj, "thud")
        cs = cues(txt); tot = sum(len(c) for c in cs); tc = s
        for j, c in enumerate(cs):
            d = dur * len(c) / tot; dc = disp(c).rstrip("。"); ln = wrap(dc) or [dc]
            if max(zw(x) for x in ln) > 27 or len(ln) > 2: raise SystemExit(f"caption overflow {bid} {dc}")
            sid = f"c{i}_{j}"; sp = "".join(f'<span id="{sid}_{q}">{color(x)}</span>' for q, x in enumerate(ln))
            timed("cap", tc, (tc + d + .06) if j < len(cs) - 1 else e + .1, f'<div class="capin">{sp}</div>', idv=sid, z=40)
            for q in range(len(ln)):
                J(tc, tc + d, f'tl.from("#{sid}_{q}",{{opacity:0,y:16,duration:.14,ease:"power3.out"}},{tc + d * .5 * q:.3f});')
            tc += d
    else:
        video(b["clip"], s, vis_e, b["ss"], .03)
        ql = b["quote"].split("|"); fs = min(116, int(1300 / max(zw(x) for x in ql)))
        sp = "".join(f'<span id="bq{i}_{j}" style="font-size:{fs}px">{html.escape(x)}</span>' for j, x in enumerate(ql))
        timed("bq", s, vis_e, f'<div class="bigq">{sp}</div><div class="sp"><div class="nm" id="bn{i}">{html.escape(b["who"])}</div></div>', z=25)
        for j in range(len(ql)):
            tj = s + .1 + (e - s) * .45 * j
            J(s, e, f'tl.from("#bq{i}_{j}",{{scale:1.8,opacity:0,duration:.18,ease:"power4.in"}},{tj:.3f});'); hit(tj + .18, "thud")
        J(s, e, f'tl.from("#bn{i}",{{x:-80,opacity:0,duration:.22,ease:"expo.out"}},{s + .1:.3f});')
        src(s, vis_e, SC.src_of(b["clip"]))
css = open(ROOT / "tools/weekly1113_style.css", encoding="utf-8").read()
JS = "\n".join(js)
doc = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{css}</style></head><body>
<div id="root" data-composition-id="root" data-start="0" data-duration="{round(W1 - W0, 3)}" data-width="1920" data-height="1080">
<div id="stage">{''.join(vid)}<div class="vig"></div>{''.join(ov)}<div id="fl"></div></div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});
{JS}
const root=gsap.timeline({{paused:true}});tl.time({W0});root.fromTo(tl,{{time:{W0}}},{{time:{W1},duration:{round(W1 - W0, 3)},ease:"none"}},0);
window.__timelines["root"]=root;</script></div></body></html>'''
TPL.mkdir(parents=True, exist_ok=True); (TPL / "index.html").write_text(doc, encoding="utf-8")
if FULL:
    json.dump(dict(hits=sorted(hits, key=lambda x: x["t"])), open(ROOT / f"subtitles/out/{EP}/visual_events.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(USE, open(ROOT / f"subtitles/out/{EP}/clip_use.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    chars = sorted(set(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", "", doc, flags=re.S)) | set("0123456789.-:"))
    (ROOT / f"subtitles/out/{EP}/chars.txt").write_text("".join(chars), encoding="utf-8")
    print("hits", len(hits), "comp", COMP, "videos", n[0])
