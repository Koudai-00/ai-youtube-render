"""朝倉海 UFC上海 勝利まとめ(日本+海外・多言語) index.html 生成(1920x1080・窓対応)。
   背景=ナレ一致(各ビート専用bgvid)。前景=海外メディアカード/英語コメントカード(一般人匿名化)。
   章タグ・DOM字幕(≤2行・JP)・出典ラベル・透かし。VISUAL_ONLYでレンダー→finalizeで音声mux。
   env: HF_WIN_START/HF_WIN_END/HF_VISUAL_ONLY/HF_OUTNAME。"""
from __future__ import annotations
import json, html, os, re as _re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "kaiufc_multi"
TPL = ROOT / "hyperframes" / "templates" / EP
TIM = json.load(open(ROOT / "subtitles" / "out" / EP / "timings.json", encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)
BEATS = TIM["beats"]
CHAPS = TIM["chapters"]

W0 = float(os.environ.get("HF_WIN_START") or 0)
_w1 = os.environ.get("HF_WIN_END")
W1 = float(_w1) if _w1 else COMP
VISUAL_ONLY = os.environ.get("HF_VISUAL_ONLY") == "1"
WIN = round(W1 - W0, 2)
OUTNAME = os.environ.get("HF_OUTNAME", "index.html")
def T(t): return round(t - W0, 3)
def OV(t0, t1): return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)
def esc(s): return html.escape(s)
BS = {b["id"]: b["start"] for b in BEATS}
BE = {b["id"]: b["end"] for b in BEATS}
def bs(bid): return BS[bid]
def be(bid): return BE[bid]

# ---- 字幕表示置換(読みかな→英字/正式表記) ----
DISP = {"ユーエフシーアメリカ": "UFCアメリカ", "ユーエフシー": "UFC",
        "エムエムエーマニア": "MMA Mania", "エムエムエーニュース": "MMA News", "エムエムエー": "MMA",
        "ケージサイドプレス": "Cageside Press", "シャードック": "Sherdog", "ヘビー": "Heavy",
        "パラマウント": "Paramount", "ショーン・オマリー": "Sean O'Malley",
        "ライジン": "RIZIN", "ユーチューブ": "YouTube", "ケーオー": "KO"}
def disp(t):
    for k in sorted(DISP, key=len, reverse=True): t = t.replace(k, DISP[k])
    return t

# 出典ラベル
S_KAI_YT = "出典: 朝倉海 (YouTube)"
S_KAI_SNS = "出典: 朝倉海 (SNS)"
S_HORI = "出典: 堀口恭司 (YouTube)"
S_UFC = "出典: UFC (試合映像)"

# beat_id -> 出典ラベル(bgvid は同名 <id>.mp4)
SRC = {
    "o1": S_KAI_SNS, "o2": S_UFC, "ko": S_UFC, "o3": S_KAI_SNS,
    "c1a": S_KAI_SNS, "c1b": S_UFC, "c1c": S_UFC, "c1d": S_KAI_YT, "c1e": S_KAI_YT, "c1f": S_KAI_YT,
    "c2a": S_HORI, "c2b": S_UFC, "c2c": S_UFC, "c2d": S_HORI,
    "c3a": S_UFC, "c3b": S_UFC, "c3c": S_UFC, "c3d": S_KAI_SNS, "c3e": S_KAI_SNS,
    "c4a": S_KAI_YT, "c4b": S_KAI_YT, "e1": S_KAI_SNS, "e2": S_UFC, "e3": S_KAI_SNS,
}
# Ken Burns motion(縦/スクエア=blur-contain背景はズーム控えめ)
MO = {"o2": "kb_zin", "ko": None, "c1c": "kb_zin", "c2c": "kb_zin", "e2": "kb_zin"}

# ---- 背景セグメント(各ビート=専用bgvid、連続同一は無し) ----
def clip_dur(fn):
    import subprocess
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(TPL / "assets" / "bgvid" / f"{fn}.mp4")], capture_output=True, text=True)
    try: return float(p.stdout.strip())
    except: return 0.0

BG = []
for b in BEATS:
    BG.append((b["start"], b["end"], b["id"], MO.get(b["id"]), SRC.get(b["id"], "")))
BG.sort(key=lambda e: e[0])
_bg2 = []
for i, (t0, t1, fn, mo, sl) in enumerate(BG):
    if i + 1 < len(BG): t1 = round(BG[i + 1][0] + 0.08, 3)
    _bg2.append((round(t0, 3), round(t1, 3), fn, mo, sl))
BG = _bg2
BG[-1] = (BG[-1][0], COMP, BG[-1][2], BG[-1][3], BG[-1][4])

# ---- 章タグ ----
CHAP_LABEL = {
    "ch1": ("朝倉海 本人が語る", "試合と、これから"),
    "ch2": ("堀口恭司の分析", "二度戦った男の視点"),
    "ch3": ("海外メディアの評価", "世界はどう見たか"),
    "ch4": ("海外ファンの声", "英語コメント殺到"),
}

# ---- カード: 海外メディア(cap) / 英語コメント(com) ----
# (beat, kind, title, body_en, meta)
CARDS_SPEC = [
    ("c3b", "media", "MMA Mania", "Slices through Aoriqileng with a brutal head-kick KO. Speed, accuracy, distance control — a clear level above.", "Source: MMA Mania"),
    ("c3c", "media", "Heavy", "0-2 start, then a dramatic turnaround. A top-15 opponent likely comes next.", "Source: Heavy.com"),
    ("c3d", "media", "Sean O'Malley", "\"This bantamweight division is stacked right now — it's amazing.\"", "Former UFC Champion"),
    ("c4b", "com", "@k_i_fan_us", "Start putting English translation in your videos bro — you got international fans.", "1.2K likes · Top comment"),
]

def card_html(cid, kind, title, body, meta, cont=False):
    op = ' style="opacity:1"' if cont else ''
    L = len(body)
    fs = 38 if L <= 60 else 33 if L <= 110 else 29 if L <= 160 else 25
    if kind == "com":
        h = f'<div class="chead"><div class="cav">{esc(title[1:2].upper())}</div>' \
            f'<div class="cnm"><div class="cname">格闘ファン</div><div class="chandle">{esc(title)}</div></div>' \
            f'<div class="clogo">𝕏</div></div>'
        return (f'<div class="ccard com" id="{cid}"{op}>{h}'
                f'<div class="ctext" style="font-size:{fs}px">{esc(body)}</div>'
                f'<div class="cmeta">{esc(meta)}</div></div>')
    else:
        return (f'<div class="ccard media" id="{cid}"{op}>'
                f'<div class="mtag">{esc(title)}</div>'
                f'<div class="ctext" style="font-size:{fs}px">{esc(body)}</div>'
                f'<div class="cmeta">{esc(meta)}</div></div>')

# ---- 字幕分割(≤2行 各≤26全角) ----
def zwidth(s):
    w = 0
    for ch in s:
        w += 0.55 if (ch.isascii() and (ch.isalnum() or ch in " .,'-〜!?")) else 1.0
    return w
def wrap_two(text, maxw):
    segs = [s for s in _re.split("(?<=、)", text) if s]
    best = None
    for i in range(1, len(segs)):
        l1 = "".join(segs[:i]); l2 = "".join(segs[i:])
        if zwidth(l1) <= maxw and zwidth(l2) <= maxw:
            if best is None or abs(zwidth(l1) - zwidth(l2)) < best[0]:
                best = (abs(zwidth(l1) - zwidth(l2)), l1, l2)
    if best: return (best[1], best[2])
    if zwidth(text) <= maxw * 2:
        target = int(len(text) * maxw / max(zwidth(text), 1))
        # 語中改行を避ける: 「区切ってよい直後」の文字(読点/句点/助詞/閉じ括弧)の後で折る
        BREAK_AFTER = set("、。」）】！？はがをにへとでものやねよ")
        def snap(t):
            for d in range(0, 9):
                for c in (t - d, t + d):
                    if 0 < c < len(text) and text[c-1] in BREAK_AFTER:
                        return c
            # 英数字連続の途中は避ける
            c = t
            while 0 < c < len(text) and text[c-1].isascii() and text[c].isascii() and (text[c-1].isalnum() or text[c].isalnum()):
                c += 1
            return c
        cut = snap(target)
        if cut >= len(text) or cut <= 0: cut = max(1, min(len(text) - 1, target))
        return (text[:cut], text[cut:])
    return None
def fits_two(text, maxw):
    return zwidth(text) <= maxw or wrap_two(text, maxw) is not None
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
for i, (t0, t1, fn, mo, srcl) in enumerate(BG):
    if not OV(t0, t1): continue
    bid = f"bg{i}"; vt0, vt1 = T(t0), T(t1)
    cont = vt0 <= 0.02
    cd = clip_dur(fn)
    ms = max(0.0, W0 - t0); ds = max(0.0, vt0)
    dur = (min(t1, W1) - max(t0, W0)) + 0.6
    if ms + dur > cd - 0.03:
        dur = max(0.3, cd - ms - 0.05)
    inner = (f'<video id="{bid}-v" src="assets/bgvid/{fn}.mp4" muted playsinline data-layout-allow-overflow '
             f'data-start="{ds:.2f}" data-duration="{dur:.2f}" data-media-start="{ms:.2f}" data-track-index="{10+i}"></video>')
    op = ";opacity:1" if cont else ""
    bg_divs.append(f'<div class="bgseg" id="{bid}" style="z-index:{i+1}{op}">{inner}</div>')
    if cont:
        bg_tws.append(f"tl.set('#{bid}',{{opacity:1}},0);")
    else:
        bg_tws.append(f"tl.fromTo('#{bid}',{{opacity:0}},{{opacity:1,duration:.45,ease:'power1.inOut'}},{vt0:.2f});")
    sel = f"'#{bid}-v'"; kbs = max(0.0, vt0); kbd = min(t1, W1) - max(t0, W0) + 0.4
    if mo == "kb_zin":
        bg_tws.append(f"tl.fromTo({sel},{{scale:1.0}},{{scale:1.08,duration:{kbd:.2f},ease:'none'}},{kbs:.2f});")
    if srcl:
        sid = f"src{i}"
        src_divs.append(f'<div class="srclab" id="{sid}">{esc(srcl)}</div>')
        bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{max(0.0,vt0+0.3):.2f});")
        bg_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{vt1-0.25:.2f});")

# ---- 章タグ ----
chap_divs, chap_tws, chap_audio = [], [], []
for j, c in enumerate(CHAPS):
    if c["chapter"] not in CHAP_LABEL: continue
    st = c["start"]
    if not OV(st, st + 3.8): continue
    ja, sub = CHAP_LABEL[c["chapter"]]; cid = f"chap{j}"
    chap_divs.append(f'<div class="chaptag" id="{cid}"><div class="chnum">{esc(ja)}</div>'
                     f'<div class="chttl">{esc(sub)}</div></div>')
    chap_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,y:40}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.6)'}},{T(st+0.1):.2f});")
    chap_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-26,duration:.4,ease:'power1.in'}},{T(st+3.4):.2f});")
    if not VISUAL_ONLY:
        chap_audio.append(f'<audio id="chs{j}" src="assets/se/chapter.wav" data-start="{T(st+0.1):.2f}" data-track-index="{200+j}" data-volume="0.5"></audio>')

# ---- カード ----
card_divs, card_tws = [], []
for k, (bid, kind, title, body, meta) in enumerate(CARDS_SPEC):
    t0 = bs(bid) + 0.2; t1 = be(bid) - 0.15
    if not OV(t0, t1): continue
    cid = f"cc{k}"; cont = T(t0) <= 0.02
    card_divs.append(card_html(cid, kind, title, body, meta, cont))
    if cont:
        card_tws.append(f"tl.set('#{cid}',{{opacity:1,x:0,y:0}},0);")
    else:
        card_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,x:60,y:18}},{{opacity:1,x:0,y:0,duration:.5,ease:'back.out(1.5)'}},{T(t0):.2f});")
    card_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-14,duration:.35,ease:'power1.in'}},{T(t1):.2f});")

# ---- 字幕(無音ビートはスキップ) ----
sub_divs, sub_tws = [], []
sidx = 0
for b in BEATS:
    if not b.get("text", "").strip(): continue
    text = disp(b["text"])
    cues = split_two_lines(text)
    dur = b["end"] - b["start"]
    wsum = sum(zwidth(c) for c in cues) or 1.0
    acc = 0.0
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
    '    <audio id="bgm" src="assets/audio/bgm.m4a" data-start="0" data-track-index="61" data-volume="0.075"></audio>')

HTML = f"""<!doctype html>
<!-- 朝倉海 UFC上海 勝利まとめ(多言語) 1920x1080 -->
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
        background:linear-gradient(180deg,rgba(0,0,0,.5) 0%,transparent 16%,transparent 58%,rgba(0,0,0,.55) 84%,rgba(0,0,0,.8) 100%);}}
  .wm{{position:absolute;z-index:360;left:36px;top:30px;font-family:"JPHeavy";font-size:30px;color:#fff;letter-spacing:.04em;filter:var(--edge-sm);opacity:.9;}}
  .srclab{{position:absolute;z-index:340;left:40px;bottom:38px;font-family:"JPMed";font-size:23px;color:#eaeaea;opacity:0;
        background:rgba(0,0,0,.5);border-left:4px solid var(--yellow);padding:6px 14px;border-radius:3px;filter:var(--edge-sm);}}
  .chaptag{{position:absolute;z-index:320;left:110px;top:37%;opacity:0;}}
  .chaptag .chnum{{font-family:"Mincho";font-size:44px;color:var(--yellow);filter:var(--edge);letter-spacing:.04em;}}
  .chaptag .chttl{{font-family:"JPHeavy";font-size:62px;color:#fff;filter:var(--edge);margin-top:6px;white-space:nowrap;}}
  .ccard{{position:absolute;z-index:330;right:74px;top:150px;width:800px;background:#fff;color:#0f1419;border-radius:20px;
        padding:26px 30px;box-shadow:0 18px 50px rgba(0,0,0,.6);opacity:0;border:1px solid #cfd9de;}}
  .ccard .ctext{{font-family:"JPMed";line-height:1.5;color:#0f1419;word-break:break-word;}}
  .ccard .cmeta{{margin-top:16px;padding-top:12px;border-top:1px solid #eaeef0;font-size:23px;color:#536471;}}
  .ccard.media .mtag{{display:inline-block;font-family:"JPHeavy";font-size:30px;color:#fff;background:#d62828;
        padding:5px 16px;border-radius:6px;margin-bottom:16px;letter-spacing:.02em;}}
  .chead{{display:flex;align-items:center;gap:16px;margin-bottom:16px;}}
  .cav{{width:60px;height:60px;border-radius:50%;background:#1d9bf0;display:flex;align-items:center;justify-content:center;color:#fff;font-family:"JPHeavy";font-size:28px;flex:none;}}
  .cnm{{flex:1;min-width:0;}} .cname{{font-family:"JPHeavy";font-size:29px;line-height:1.1;}}
  .chandle{{font-size:24px;color:#536471;}} .clogo{{font-size:31px;flex:none;}}
  .subt{{position:absolute;z-index:350;left:0;right:0;bottom:96px;text-align:center;opacity:0;
        font-family:"JPHeavy";font-size:45px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;padding:0 90px;}}
</style>
</head>
<body>
  <div id="root" data-composition-id="kaiufc" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
{J(bg_divs,"    ")}

    {AUDIO_BLOCK}
{J(chap_audio,"    ")}

    <div class="veil"></div>
    <div class="wm">格闘ニュースラボ</div>
{J(src_divs,"    ")}
{J(chap_divs,"    ")}
{J(card_divs,"    ")}
{J(sub_divs,"    ")}

    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({{paused:true}});
{J(bg_tws)}
{J(chap_tws)}
{J(card_tws)}
{J(sub_tws)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['kaiufc'] = tl;
    </script>
  </div>
</body>
</html>
"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} bg={len(bg_divs)} cards={len(card_divs)} subs={len(sub_divs)}")
