# -*- coding: utf-8 -*-
"""超RIZIN.5 全試合ガイド index.html 生成(1920x1080・窓対応)。
   背景=ビート専用bgvid(build_rizin5guide_bg)。前景=DOM字幕(≤2行)・試合別章タグ・出典ラベル・透かし。
   カード/静止画ビートはKenBurns(GSAP)。VISUAL_ONLYレンダー→finalizeで音声mux。
   env: HF_WIN_START/HF_WIN_END/HF_VISUAL_ONLY/HF_OUTNAME。"""
from __future__ import annotations
import json, html, os, re as _re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "rizin5_guide"
TPL = ROOT / "hyperframes" / "templates" / EP
_SK = json.load(open(TPL / "src_kb.json", encoding="utf-8"))  # {src:{bid:label}, kb:[bid]}
TIM = json.load(open(ROOT / "subtitles" / "out" / EP / "timings.json", encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)
BEATS = TIM["beats"]; CHAPS = TIM["chapters"]

W0 = float(os.environ.get("HF_WIN_START") or 0)
_w1 = os.environ.get("HF_WIN_END")
W1 = float(_w1) if _w1 else COMP
VISUAL_ONLY = os.environ.get("HF_VISUAL_ONLY") == "1"
WIN = round(W1 - W0, 2)
OUTNAME = os.environ.get("HF_OUTNAME", "index.html")
def T(t): return round(t - W0, 3)
def OV(t0, t1): return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)
def esc(s): return html.escape(s)

# ---- 字幕表示置換(最小・ナレは既に表記形) ----
DISP = {"三角絞めをきめて": "三角絞めを極めて", "していてもきめてしまう": "していても極めてしまう"}
def disp(t):
    for k in sorted(DISP, key=len, reverse=True): t = t.replace(k, DISP[k])
    return t

# ---- 出典ラベル / KenBurns判定(src_kb.jsonから) ----
SRC = _SK["src"]; KB = {b: True for b in _SK["kb"]}
def srcof(bid): return SRC.get(bid, "出典: RIZIN (試合映像)")

# ---- 章タグ(試合ごと) ----
CHAP_LABEL = {
    "f1": ("第1試合 / キック", "ベイノア vs 宇佐美秀メイソン"),
    "f2": ("第2試合 / 女子49kg", "RENA vs ナターシャ・クジュティナ"),
    "f3": ("第3試合 / 66kg", "ヴガール・ケラモフ vs 高木凌"),
    "f4": ("第4試合 / 66kg", "斎藤裕 vs YA-MAN"),
    "f5": ("第5試合 / 66kg", "ダウトベック vs 平本蓮"),
    "f6": ("第6試合 / 71kg", "サトシ・ソウザ vs 野村駿太"),
    "f7": ("セミファイナル / 71kg", "朝倉未来 vs 青木真也"),
    "main": ("メインイベント / W王座統一", "シェイドゥラエフ vs AJ・マッキー"),
}

# ---- 背景セグメント ----
def clip_dur(fn):
    import subprocess
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(TPL / "assets" / "bgvid" / f"{fn}.mp4")], capture_output=True, text=True)
    try: return float(p.stdout.strip())
    except: return 0.0

# ★ビート内分割: bg_splits.json = {"<beat_id>": [絶対秒, ...]} でビート内に切替点を追加できる。
#   1ビートに複数の背景指定がある場合に使う(クリップ名は <beat_id>_2, _3 ... となる)。
_SPLITS = {}
_sp_path = TPL / "bg_splits.json"
if _sp_path.exists():
    _SPLITS = json.load(open(_sp_path, encoding="utf-8"))

BG_SEG = []
for b in BEATS:
    cuts = sorted(t for t in _SPLITS.get(b["id"], []) if b["start"] + 0.4 < t < b["end"] - 0.4)
    if not cuts:
        BG_SEG.append((b["start"], b["end"], b["id"]))
    else:
        bounds = [b["start"]] + cuts + [b["end"]]
        for k in range(len(bounds) - 1):
            fn = b["id"] if k == 0 else f'{b["id"]}_{k+1}'
            BG_SEG.append((bounds[k], bounds[k+1], fn))
BG_SEG.sort(key=lambda e: e[0])
_bg2 = []
for i, (t0, t1, fn) in enumerate(BG_SEG):
    if i + 1 < len(BG_SEG): t1 = round(BG_SEG[i + 1][0] + 0.08, 3)
    _bg2.append((round(t0, 3), round(t1, 3), fn))
BG_SEG = _bg2
BG_SEG[-1] = (BG_SEG[-1][0], COMP, BG_SEG[-1][2])

# ---- 字幕分割(≤2行 各≤23全角) ----
def zwidth(s):
    w = 0
    for ch in s:
        w += 0.55 if (ch.isascii() and (ch.isalnum() or ch in " .,'-〜!?%")) else 1.0
    return w
# 行頭に置けない文字(小書きかな/長音/ん/中黒)＝ここで割ると語中改行になる
_SMALL_LEAD = set("っゃゅょぁぃぅぇぉゎんー・")
def _valid_cut(text, c):
    if not (0 < c < len(text)): return False
    if text[c] in _SMALL_LEAD: return False           # 2行目先頭が小書き等はNG(語中改行)
    if text[c-1].isascii() and text[c].isascii() and (text[c-1].isalnum() or text[c].isalnum()):
        return False                                   # ascii語(英数)の途中で割らない
    return True
def wrap_two(text, maxw):
    # 全ての有効な改行位置から「句読点/助詞優先・2行が均等・行幅が小さい」ものを選ぶ。
    # 小書きかな行頭やascii語中では割らない(語中改行の根絶)。
    cands = []
    for c in range(1, len(text)):
        if not _valid_cut(text, c): continue
        l1, l2 = text[:c], text[c:]; w1, w2 = zwidth(l1), zwidth(l2)
        prev = text[c-1]
        pri = 0 if prev in "。、" else (1 if prev in "」）】！？はがをにへとでもとやねよ" else 2)
        cands.append((pri, abs(w1 - w2), max(w1, w2), c, l1, l2))
    if not cands: return None
    cands.sort(key=lambda x: (x[0], x[1], x[2]))       # 区切り種別→均等さ→最大行幅
    _, _, _, _, l1, l2 = cands[0]
    return (l1, l2)
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
    return cues or [text]
def sub_lines(text, maxw=23.0):
    if zwidth(text) <= maxw: return [text]
    w = wrap_two(text, maxw)
    return [w[0], w[1]] if w else [text]

# ---- 背景 DOM/TL ----
bg_divs, bg_tws, src_divs = [], [], []
for i, (t0, t1, fn) in enumerate(BG_SEG):
    if not OV(t0, t1): continue
    bid = f"bg{i}"; vt0, vt1 = T(t0), T(t1)
    cont = vt0 <= 0.02
    cd = clip_dur(fn)
    ms = max(0.0, W0 - t0); ds = max(0.0, vt0)
    # ★背景はpiece(窓)終端まで延長する。piece途中でvideoが終了すると、その瞬間に
    #   次の背景videoが約2.7秒描画不能になり黒が出る(ローカル検証で特定)。
    #   上に不透明な次セグメントが重なるため、延長しても見た目は変わらない。
    dur = (W1 - max(t0, W0)) + 0.6
    # ★プリロード先行: 要素をPRELOAD秒早く開始して読み込ませる(不透明化は従来どおりvt0)。
    #   前セグメント終了時に次のvideoがまだ描画開始しておらず黒が出る事故を防ぐ。
    PRELOAD = 1.5
    lead = min(PRELOAD, ds)
    if lead > 0:
        ds -= lead; dur += lead
    if ms + dur > cd - 0.03: dur = max(0.3, cd - ms - 0.05)
    inner = (f'<video id="{bid}-v" src="assets/bgvid/{fn}.mp4" muted playsinline data-layout-allow-overflow '
             f'data-start="{ds:.2f}" data-duration="{dur:.2f}" data-media-start="{ms:.2f}" data-track-index="{10+i}"></video>')
    op = ";opacity:1" if cont else ""
    bg_divs.append(f'<div class="bgseg" id="{bid}" style="z-index:{i+1}{op}">{inner}</div>')
    if cont: bg_tws.append(f"tl.set('#{bid}',{{opacity:1}},0);")
    else: bg_tws.append(f"tl.fromTo('#{bid}',{{opacity:0}},{{opacity:1,duration:.45,ease:'power1.inOut'}},{vt0:.2f});")
    # 静止画(カード)はKenBurns
    if KB.get(fn):
        kbs = max(0.0, vt0); kbd = min(t1, W1) - max(t0, W0) + 0.4
        bg_tws.append(f"tl.fromTo('#{bid}-v',{{scale:1.0}},{{scale:1.09,duration:{kbd:.2f},ease:'none'}},{kbs:.2f});")
    # 出典ラベル
    srcl = srcof(fn)
    if srcl and (min(t1, W1) - max(t0, W0)) > 0.6:
        sid = f"src{i}"
        src_divs.append(f'<div class="srclab" id="{sid}">{esc(srcl)}</div>')
        bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{max(0.0,vt0+0.3):.2f});")
        bg_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{vt1-0.25:.2f});")

# ---- 章タグ ----
chap_divs, chap_tws = [], []
for j, c in enumerate(CHAPS):
    if c["chapter"] not in CHAP_LABEL: continue
    st = c["start"]
    if not OV(st, st + 3.8): continue
    ja, sub = CHAP_LABEL[c["chapter"]]; cid = f"chap{j}"
    chap_divs.append(f'<div class="chaptag" id="{cid}"><div class="chnum">{esc(ja)}</div>'
                     f'<div class="chttl">{esc(sub)}</div></div>')
    chap_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,y:40}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.6)'}},{T(st+0.1):.2f});")
    chap_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-26,duration:.4,ease:'power1.in'}},{T(st+3.6):.2f});")

# ---- 字幕 ----
sub_divs, sub_tws = [], []
sidx = 0
for b in BEATS:
    if not b.get("text", "").strip(): continue
    text = disp(b["text"])
    cues = split_two_lines(text)
    dur = b["end"] - b["start"]; wsum = sum(zwidth(c) for c in cues) or 1.0; acc = 0.0
    for cue in cues:
        cs = b["start"] + dur * acc / wsum; acc += zwidth(cue); ce = b["start"] + dur * acc / wsum
        if not OV(cs, ce): continue
        lines = sub_lines(cue); inner = "<br>".join(esc(l) for l in lines)
        did = f"sub{sidx}"; sidx += 1
        sub_divs.append(f'<div class="subt" id="{did}">{inner}</div>')
        sub_tws.append(f"tl.fromTo('#{did}',{{opacity:0}},{{opacity:1,duration:.18}},{max(0.0,T(cs)):.2f});")
        sub_tws.append(f"tl.to('#{did}',{{opacity:0,duration:.14}},{T(ce-0.05):.2f});")

def J(items, ind="      "): return "\n".join(ind + x for x in items)
AUDIO_BLOCK = ("" if VISUAL_ONLY else
    '<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="60" data-volume="1"></audio>\n'
    '    <audio id="bgm" src="assets/audio/bgm.m4a" data-start="0" data-track-index="61" data-volume="0.05"></audio>')

HTML = f"""<!doctype html>
<!-- 超RIZIN.5 全試合ガイド 1920x1080 -->
<html>
<head>
<meta charset="utf-8">
<style>
  @font-face{{font-family:"Mincho";src:url("assets/fonts/GokubutoMincho.ttf");}}
  @font-face{{font-family:"JPHeavy";src:url("assets/fonts/SourceHanSansJP-Heavy.otf");}}
  @font-face{{font-family:"JPMed";src:url("assets/fonts/SourceHanSansJP-Medium.otf");}}
  :root{{
    --white:#fff; --yellow:#ffe23a; --red:#ff3a3a; --blue:#36b6ff; --ink:#0a0c12;
    --edge:drop-shadow(4px 0 0 var(--ink)) drop-shadow(-4px 0 0 var(--ink)) drop-shadow(0 4px 0 var(--ink)) drop-shadow(0 -4px 0 var(--ink))
           drop-shadow(3px 3px 0 var(--ink)) drop-shadow(-3px 3px 0 var(--ink)) drop-shadow(0 8px 16px rgba(0,0,0,.8));
    --edge-sm:drop-shadow(0 0 2px var(--ink)) drop-shadow(1px 1px 1px var(--ink)) drop-shadow(0 2px 6px rgba(0,0,0,.85));
  }}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  #root{{position:absolute;inset:0;overflow:hidden;background:#05060a;font-family:"JPMed";}}
  .bgseg{{position:absolute;inset:0;opacity:0;overflow:hidden;}}
  .bgseg video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform:translateZ(0);backface-visibility:hidden;}}
  .veil{{position:absolute;inset:0;z-index:300;pointer-events:none;
        background:linear-gradient(180deg,rgba(0,0,0,.45) 0%,transparent 15%,transparent 58%,rgba(0,0,0,.6) 84%,rgba(0,0,0,.82) 100%);}}
  .wm{{position:absolute;z-index:360;left:36px;top:30px;font-family:"JPHeavy";font-size:30px;color:#fff;letter-spacing:.04em;filter:var(--edge-sm);opacity:.9;}}
  .srclab{{position:absolute;z-index:340;left:40px;bottom:38px;font-family:"JPMed";font-size:23px;color:#eaeaea;opacity:0;
        background:rgba(0,0,0,.5);border-left:4px solid var(--yellow);padding:6px 14px;border-radius:3px;filter:var(--edge-sm);}}
  .chaptag{{position:absolute;z-index:320;left:100px;top:35%;opacity:0;}}
  .chaptag .chnum{{font-family:"Mincho";font-size:42px;color:var(--yellow);filter:var(--edge);letter-spacing:.04em;}}
  .chaptag .chttl{{font-family:"JPHeavy";font-size:58px;color:#fff;filter:var(--edge);margin-top:6px;white-space:nowrap;}}
  .subt{{position:absolute;z-index:350;left:0;right:0;bottom:96px;text-align:center;opacity:0;
        font-family:"JPHeavy";font-size:45px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;padding:0 90px;}}
</style>
</head>
<body>
  <div id="root" data-composition-id="rizin5" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
{J(bg_divs,"    ")}

    {AUDIO_BLOCK}

    <div class="veil"></div>
    <div class="wm">格闘ニュースラボ</div>
{J(src_divs,"    ")}
{J(chap_divs,"    ")}
{J(sub_divs,"    ")}

    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({{paused:true}});
{J(bg_tws)}
{J(chap_tws)}
{J(sub_tws)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['rizin5'] = tl;
    </script>
  </div>
</body>
</html>
"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} bg={len(bg_divs)} subs={len(sub_divs)} chaps={len(chap_divs)}")
