# -*- coding: utf-8 -*-
"""超RIZIN.5 勝敗予想まとめ index.html 生成(1920x1080・窓対応)。
   背景=ビート専用bgvid(build_rizin5yosou_bg)。
   前景=DOM字幕(≤2行)・章タグ(タイトル+サブ)・予想者ラベル・出典ラベル・透かし。
   ★全試合ガイドで確立した対策を踏襲:
     - 背景セグメントはpiece(窓)終端まで延長(piece途中でvideoが終わると次が2.7秒黒くなる)
     - 字幕折返しは句読点/助詞優先・均等・小書き行頭回避(語中改行の根絶)
   env: HF_WIN_START/HF_WIN_END/HF_VISUAL_ONLY/HF_OUTNAME。
"""
from __future__ import annotations
import json, html, os, re as _re, subprocess
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "rizin5_yosou"
TPL = ROOT / "hyperframes" / "templates" / EP
TIM = json.load(open(ROOT / "subtitles" / "out" / EP / "timings.json", encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)
BEATS = TIM["beats"]; CHAPS = TIM["chapters"]

W0 = float(os.environ.get("HF_WIN_START") or 0)
_w1 = os.environ.get("HF_WIN_END")
W1 = float(_w1) if _w1 else COMP
VISUAL_ONLY = os.environ.get("HF_VISUAL_ONLY") == "1"
OUTNAME = os.environ.get("HF_OUTNAME", "index.html")
def T(t): return round(t - W0, 3)
def OV(t0, t1): return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)
def esc(s): return html.escape(s)

# ---- 出典/予想者ラベル/KenBurns対象 (gen_rizin5yosou_srckb.py が生成) ----
_SK = json.load(open(TPL / "src_kb.json", encoding="utf-8"))
SRCMAP, PREDMAP, KBSET = _SK["src"], _SK["pred"], set(_SK["kb"])
def srcof(bid):  return SRCMAP.get(bid, "出典: RIZIN公式")
def predof(bid): return PREDMAP.get(bid)
def is_card(bid): return bid in KBSET

@lru_cache(maxsize=None)
def clip_dur(fn: str) -> float:
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(TPL / "assets" / "bgvid" / f"{fn}.mp4")],
                       capture_output=True, text=True)
    try: return float(p.stdout.strip())
    except: return 0.0

# ---- 背景セグメント(ビート=1セグメント) ----
BG_SEG = []
for i, b in enumerate(BEATS):
    t1 = BEATS[i + 1]["start"] + 0.08 if i + 1 < len(BEATS) else COMP
    BG_SEG.append((round(b["start"], 3), round(t1, 3), b["id"]))

# ---- 字幕分割(≤2行 各≤23全角) ----
def zwidth(s):
    w = 0
    for ch in s:
        w += 0.55 if (ch.isascii() and (ch.isalnum() or ch in " .,'-〜!?%")) else 1.0
    return w
_SMALL_LEAD = set("っゃゅょぁぃぅぇぉゎんー・")
def _is_kata(ch):
    return "ァ" <= ch <= "ヺ" or ch in "ーヴ・"
def _valid_cut(text, c):
    if not (0 < c < len(text)): return False
    if text[c] in _SMALL_LEAD: return False
    if text[c-1].isascii() and text[c].isascii() and (text[c-1].isalnum() or text[c].isalnum()):
        return False
    # ★カタカナ語の途中で改行しない(「ケ/ラモフ」のような分断を防ぐ)
    if _is_kata(text[c-1]) and _is_kata(text[c]): return False
    return True
def wrap_two(text, maxw):
    cands = []
    for c in range(1, len(text)):
        if not _valid_cut(text, c): continue
        l1, l2 = text[:c], text[c:]; w1, w2 = zwidth(l1), zwidth(l2)
        prev = text[c-1]
        pri = 0 if prev in "。、" else (1 if prev in "」）】！？はがをにへとでもとやねよ" else 2)
        cands.append((pri, abs(w1 - w2), max(w1, w2), c, l1, l2))
    if not cands: return None
    # ★両行が幅内に収まる候補を最優先(句読点の位置だけを優先すると極端に短い行が生まれる)
    inw = [c for c in cands if c[2] <= maxw + 0.5]
    pool = inw or cands
    pool.sort(key=lambda x: (x[0], x[1], x[2]))
    return (pool[0][4], pool[0][5])
def fits_two(text, maxw):
    if zwidth(text) <= maxw: return True
    w = wrap_two(text, maxw)
    return w is not None and zwidth(w[0]) <= maxw + 0.5 and zwidth(w[1]) <= maxw + 0.5
def split_two_lines(text, maxw=23.0):
    parts = [p for p in _re.split("(?<=[、。])", text) if p]
    cues, cur = [], ""
    for p in parts:
        cand = cur + p
        if fits_two(cand, maxw): cur = cand
        else:
            if cur: cues.append(cur)
            cur = p
    if cur: cues.append(cur)
    # ★極小キュー(数文字だけ)を単独で出さない: 隣へ吸収する
    out = []
    for c in cues:
        if (out and (zwidth(out[-1]) < 8 or zwidth(c) < 8)
                and zwidth(out[-1] + c) <= 2 * maxw - 6 and fits_two(out[-1] + c, maxw)):
            out[-1] = out[-1] + c
        else:
            out.append(c)
    return out or [text]
def sub_lines(text, maxw=23.0):
    if zwidth(text) <= maxw: return [text]
    w = wrap_two(text, maxw)
    return [w[0], w[1]] if w else [text]

# ---- 背景 DOM/TL ----
bg_divs, bg_tws, src_divs, pl_divs = [], [], [], []
for i, (t0, t1, fn) in enumerate(BG_SEG):
    if not OV(t0, t1): continue
    bid = f"bg{i}"; vt0, vt1 = T(t0), T(t1)
    cont = vt0 <= 0.02
    cd = clip_dur(fn)
    ms = max(0.0, W0 - t0); ds = max(0.0, vt0)
    dur = (W1 - max(t0, W0)) + 0.6     # ★piece終端まで延長(黒対策)
    lead = min(1.5, ds)
    if lead > 0: ds -= lead; dur += lead
    if ms + dur > cd - 0.03: dur = max(0.3, cd - ms - 0.05)
    inner = (f'<video id="{bid}-v" src="assets/bgvid/{fn}.mp4" muted playsinline data-layout-allow-overflow '
             f'data-start="{ds:.2f}" data-duration="{dur:.2f}" data-media-start="{ms:.2f}" data-track-index="{10+i}"></video>')
    op = ";opacity:1" if cont else ""
    bg_divs.append(f'<div class="bgseg" id="{bid}" style="z-index:{i+1}{op}">{inner}</div>')
    if cont: bg_tws.append(f"tl.set('#{bid}',{{opacity:1}},0);")
    else: bg_tws.append(f"tl.fromTo('#{bid}',{{opacity:0}},{{opacity:1,duration:.45,ease:'power1.inOut'}},{vt0:.2f});")
    if is_card(fn):     # 公式カードはKenBurns
        kbd = min(t1, W1) - max(t0, W0) + 0.4
        bg_tws.append(f"tl.fromTo('#{bid}-v',{{scale:1.0}},{{scale:1.08,duration:{kbd:.2f},ease:'none'}},{max(0.0,vt0):.2f});")
    seg_len = min(t1, W1) - max(t0, W0)
    if seg_len > 0.6:
        sid = f"src{i}"
        src_divs.append(f'<div class="srclab" id="{sid}">{esc(srcof(fn))}</div>')
        bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{max(0.0,vt0+0.3):.2f});")
        bg_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{vt1-0.25:.2f});")
        # 予想者ラベル(本人の解説映像を出している間だけ)
        nm = predof(fn)
        if nm and seg_len > 1.2:
            pid = f"pl{i}"
            pl_divs.append(f'<div class="plab" id="{pid}"><span class="plname">{esc(nm)}</span></div>')
            bg_tws.append(f"tl.fromTo('#{pid}',{{opacity:0,x:-30}},{{opacity:1,x:0,duration:.45,ease:'power2.out'}},{max(0.0,vt0+0.25):.2f});")
            bg_tws.append(f"tl.to('#{pid}',{{opacity:0,duration:.3}},{vt1-0.3:.2f});")

# ---- 章タグ ----
chap_divs, chap_tws = [], []
for j, c in enumerate(CHAPS):
    st, en = c["start"], c["end"]
    if not OV(st, en + 0.6): continue
    cid = f"chap{j}"
    chap_divs.append(f'<div class="chapscrim" id="{cid}s"></div>')
    chap_divs.append(f'<div class="chaptag" id="{cid}"><div class="chnum">{esc(c["title"])}</div>'
                     f'<div class="chttl">{esc(c["sub"])}</div></div>')
    chap_tws.append(f"tl.fromTo('#{cid}s',{{opacity:0}},{{opacity:1,duration:.4}},{T(st):.2f});")
    chap_tws.append(f"tl.to('#{cid}s',{{opacity:0,duration:.35}},{T(en-0.34):.2f});")
    chap_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,y:40}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.6)'}},{T(st):.2f});")
    chap_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-26,duration:.32,ease:'power1.in'}},{T(en-0.34):.2f});")

# ---- 字幕 ----
sub_divs, sub_tws = [], []
sidx = 0
for b in BEATS:
    text = b.get("text", "").strip()
    if not text: continue
    cues = split_two_lines(text)
    dur = b["end"] - b["start"]; wsum = sum(zwidth(c) for c in cues) or 1.0; acc = 0.0
    for cue in cues:
        cs = b["start"] + dur * acc / wsum; acc += zwidth(cue); ce = b["start"] + dur * acc / wsum
        if not OV(cs, ce): continue
        inner = "<br>".join(esc(l) for l in sub_lines(cue))
        did = f"sub{sidx}"; sidx += 1
        sub_divs.append(f'<div class="subt" id="{did}">{inner}</div>')
        sub_tws.append(f"tl.fromTo('#{did}',{{opacity:0}},{{opacity:1,duration:.18}},{max(0.0,T(cs)):.2f});")
        sub_tws.append(f"tl.to('#{did}',{{opacity:0,duration:.14}},{T(ce-0.05):.2f});")

def J(items, ind="      "): return "\n".join(ind + x for x in items)
AUDIO = ("" if VISUAL_ONLY else
    '<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="60" data-volume="1"></audio>')
WIN = round(W1 - W0, 2)

HTML = f"""<!doctype html>
<!-- 超RIZIN.5 勝敗予想まとめ 1920x1080 -->
<html>
<head>
<meta charset="utf-8">
<style>
  @font-face{{font-family:"Mincho";src:url("assets/fonts/GokubutoMincho.ttf");}}
  @font-face{{font-family:"JPHeavy";src:url("assets/fonts/SourceHanSansJP-Heavy.otf");}}
  @font-face{{font-family:"JPMed";src:url("assets/fonts/SourceHanSansJP-Medium.otf");}}
  :root{{
    --white:#fff; --yellow:#ffe23a; --ink:#0a0c12;
    --edge:drop-shadow(4px 0 0 var(--ink)) drop-shadow(-4px 0 0 var(--ink)) drop-shadow(0 4px 0 var(--ink)) drop-shadow(0 -4px 0 var(--ink))
           drop-shadow(3px 3px 0 var(--ink)) drop-shadow(-3px 3px 0 var(--ink)) drop-shadow(0 8px 16px rgba(0,0,0,.8));
    --edge-sm:drop-shadow(0 0 2px var(--ink)) drop-shadow(1px 1px 1px var(--ink)) drop-shadow(0 2px 6px rgba(0,0,0,.85));
  }}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  #root{{position:absolute;inset:0;overflow:hidden;background:#05060a;font-family:"JPMed";}}
  .bgseg{{position:absolute;inset:0;opacity:0;overflow:hidden;}}
  .bgseg video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform:translateZ(0);backface-visibility:hidden;}}
  .veil{{position:absolute;inset:0;z-index:300;pointer-events:none;
        background:linear-gradient(180deg,rgba(0,0,0,.45) 0%,transparent 15%,transparent 55%,rgba(0,0,0,.55) 76%,rgba(0,0,0,.88) 100%);}}
  .wm{{position:absolute;z-index:360;left:36px;top:30px;font-family:"JPHeavy";font-size:30px;color:#fff;letter-spacing:.04em;filter:var(--edge-sm);opacity:.9;}}
  .srclab{{position:absolute;z-index:340;left:40px;bottom:22px;font-family:"JPMed";font-size:22px;color:#eaeaea;opacity:0;
        background:rgba(0,0,0,.5);border-left:4px solid var(--yellow);padding:5px 12px;border-radius:3px;filter:var(--edge-sm);}}
  .plab{{position:absolute;z-index:330;left:56px;top:150px;opacity:0;
        background:linear-gradient(90deg,rgba(10,14,28,.92),rgba(10,14,28,.55));
        border-left:9px solid var(--yellow);padding:14px 40px 14px 22px;border-radius:3px;}}
  .plab .plname{{font-family:"JPHeavy";font-size:50px;color:#fff;letter-spacing:.03em;filter:var(--edge-sm);white-space:nowrap;}}
  .chapscrim{{position:absolute;inset:0;z-index:310;opacity:0;background:rgba(0,0,0,.66);}}
  .chaptag{{position:absolute;z-index:320;left:0;right:0;top:35%;text-align:center;opacity:0;}}
  .chaptag .chnum{{font-family:"Mincho";font-size:42px;color:var(--yellow);filter:var(--edge);letter-spacing:.10em;}}
  .chaptag .chttl{{font-family:"JPHeavy";font-size:62px;color:#fff;filter:var(--edge);margin-top:10px;white-space:nowrap;}}
  .subt{{position:absolute;z-index:350;left:0;right:0;bottom:104px;text-align:center;opacity:0;
        font-family:"JPHeavy";font-size:45px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;padding:0 90px;}}
</style>
</head>
<body>
  <div id="root" data-composition-id="rizin5yosou" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
{J(bg_divs,"    ")}

    {AUDIO}

    <div class="veil"></div>
    <div class="wm">格闘ニュースラボ</div>
{J(src_divs,"    ")}
{J(pl_divs,"    ")}
{J(chap_divs,"    ")}
{J(sub_divs,"    ")}

    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({{paused:true}});
{J(bg_tws)}
{J(chap_tws)}
{J(sub_tws)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['rizin5yosou'] = tl;
    </script>
  </div>
</body>
</html>
"""

(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} bg={len(bg_divs)} "
      f"subs={len(sub_divs)} chaps={len(chap_divs)} plabels={len(pl_divs)}")
