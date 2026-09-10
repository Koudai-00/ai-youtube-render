# -*- coding: utf-8 -*-
"""ケラモフ減量×チャーリー柏木 ショート テンプレ生成(縦1080x1920)。
   背景=事前結合した単一動画(hiramoto_bg_full.mp4)。
   要素: 透かし(左上)/全ナレのフル字幕(下・読みかな→正式表記DISP・キーワード原色)/出典ラベル(左下)。
   ★冒頭 t0 はユーザー支給サムネイル区間なので、字幕・透かし・ヴェール・出典を一切載せない(加工しない)。
   SFXは 背景切替 + 字幕切替 で多数(sfx_events.json)。"""
from __future__ import annotations
import json, html, os, re
from pathlib import Path

VISUAL_ONLY = os.environ.get("HF_VISUAL_ONLY") == "1" or os.environ.get("HF_WITH_AUDIO") != "1"
ROOT = Path(__file__).resolve().parents[1]
EP = "hiramoto_dautbek_short"
TPL = ROOT / "hyperframes" / "templates" / "hiramoto-dautbek-short"
TIM = json.load(open(ROOT / "subtitles" / "out" / EP / "timings.json", encoding="utf-8"))
SEG = json.load(open(TPL / "assets" / "bg_segments.json", encoding="utf-8"))
B = {b["id"]: b for b in TIM["beats"]}
ORDER = [b["id"] for b in TIM["beats"]]
DUR = round(TIM["total"] + 0.3, 2)
THUMB_END = 0.0   # ★今回は支給サムネなし。冒頭から字幕・透かしを出し、別途タイトルを重ねる
# ★CIの窓分割レンダー: HF_WIN_START/END の区間だけを 0 起点で描画する
W0 = float(os.environ.get("HF_WIN_START") or 0)
_w1 = os.environ.get("HF_WIN_END")
W1 = float(_w1) if _w1 else DUR
WIN = round(W1 - W0, 3)
OUTNAME = os.environ.get("HF_OUTNAME", "index.html")


def T(t): return round(t - W0, 3)


def OV(t0, t1): return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)


def st(b): return B[b]["start"]


def en(b): return B[b]["end"]


def esc(s): return html.escape(s)


# ===== 読み(かな)→ 正式表記 DISP変換 (長いキー優先) =====
DISP = [("にじゅうきゅうたいにじゅうはち", "29-28"), ("にじゅうきゅうたいにじゅうなな", "29-27"),
        ("スーパーライジンファイブ", "超RIZIN.5"), ("かわはらゆうじ", "河原由次"),
        ("ジャンさいとう", "ジャン斉藤"), ("ひらもとれん", "平本蓮"), ("ひらもと", "平本"),
        ("ライジン", "RIZIN"), ("エスエヌエス", "SNS"),
        ("はんていにたいいち", "判定2-1"), ("にたいいち", "2-1"),
        ("じゅうたいはち", "10-8"), ("ジャッジひとり", "ジャッジ1人"),
        ("いちラウンド", "1R"), ("にラウンド", "2R"), ("さんラウンド", "3R"),
        ("ふたり", "2人"), ("ひとり", "1人"), ("第6試合", "第6試合"), ("有効打", "有効打")]


def disp(s):
    for k, v in DISP:
        s = s.replace(k, v)
    return s


# ===== キーワード原色 (人名=赤 / 数字・強調=黄 / 団体・大会=青) =====
KWCOL = [("カルシャガ・ダウトベック", "b"), ("ダウトベック", "b"), ("平本蓮", "r"), ("平本", "r"),
         ("河原由次", "y"), ("ジャン斉藤", "y"),
         ("超RIZIN.5", "b"), ("RIZIN", "b"), ("SNS", "b"),
         ("判定2-1", "y"), ("29-28", "y"), ("29-27", "y"), ("2-1", "y"), ("10-8", "y"), ("賛否", "y"),
         ("クリーンヒット", "y"), ("キャンバスに落ち", "y"), ("テイクダウン", "y"),
         ("有効打", "y"), ("スポーツじゃない", "y"), ("驚いていた", "y")]


def colorize(s):
    toks = []
    for kw, col in KWCOL:
        i = 0
        while True:
            j = s.find(kw, i)
            if j < 0:
                break
            if "\x01" in s[max(0, j - 4):j + len(kw) + 4]:
                i = j + len(kw)
                continue
            tok = f"\x01{len(toks)}\x02"
            toks.append(f'<span class="c-{col}">{esc(kw)}</span>')
            s = s[:j] + tok + s[j + len(kw):]
            i = j + len(tok)
    s = esc(s)
    for n, rep in enumerate(toks):
        s = s.replace(esc(f"\x01{n}\x02"), rep)
    return s


# ===== フル字幕: 句点で分割→時間配分→文節の切れ目で改行 =====
PARTICLES = set("はがをにでとへもの")


def dlen(s): return sum(1.0 if ord(c) > 0x2E80 else 0.5 for c in s)


def _kata(c): return "ァ" <= c <= "ヴ" or c == "ー"


def _latin(c): return c.isascii() and c.isalnum()


def jp_lines(text, maxlen=13.5):
    if dlen(text) <= maxlen:
        return [text]
    n = len(text)
    mid = n / 2

    def score(i):
        L, R = text[:i], text[i:]
        if dlen(L) > maxlen or dlen(R) > maxlen:
            return None
        s = abs(i - mid)
        if text[i - 1] in PARTICLES:
            s -= 3
        if (_kata(text[i - 1]) and _kata(text[i])) or (_latin(text[i - 1]) and _latin(text[i])):
            s += 100
        return s
    best, bs = None, 1e9
    for i in range(1, n):
        sc = score(i)
        if sc is not None and sc < bs:
            bs, best = sc, i
    if best is None:
        for i in range(1, n):
            s = abs(i - mid)
            if (_kata(text[i - 1]) and _kata(text[i])) or (_latin(text[i - 1]) and _latin(text[i])):
                s += 100
            if s < bs:
                bs, best = s, i
    return [text[:best], text[best:]]


def split_long(p, limit=26.0):
    """1キューが2行(=13.5全角×2)に収まらない長さなら、助詞直後で時間分割用に切る。
       ★カタカナ語/英数字の語中では絶対に切らない(「キャッチ|ウェイト」を防ぐ)。"""
    if dlen(p) <= limit:
        return [p]
    n = len(p)
    mid = n / 2
    best, bs = None, 1e9
    for i in range(1, n):
        if dlen(p[:i]) > limit or dlen(p[i:]) > limit:
            continue
        s = abs(i - mid)
        if p[i - 1] in PARTICLES:
            s -= 4
        if (_kata(p[i - 1]) and _kata(p[i])) or (_latin(p[i - 1]) and _latin(p[i])):
            s += 100
        if s < bs:
            bs, best = s, i
    if best is None:
        return [p]
    return split_long(p[:best], limit) + split_long(p[best:], limit)


def phrase_cues(bid):
    text = disp(B[bid]["text"])
    t0, t1 = st(bid), en(bid)
    parts = [p for p in re.split(r"[、。]", text) if p.strip()]
    merged = []
    i = 0
    while i < len(parts):
        p = parts[i]
        while i + 1 < len(parts) and dlen(p) < 7 and dlen(p + parts[i + 1]) <= 13:
            i += 1
            p += parts[i]
        merged.append(p)
        i += 1
    if len(merged) >= 2 and dlen(merged[-1]) < 5:      # 末尾の極小断片は直前へ吸収
        merged[-2] += merged[-1]
        merged.pop()
    merged = [q for p in merged for q in split_long(p)]  # 長すぎるキューは時間分割
    total = sum(len(p) for p in merged) or 1
    cues, cur = [], t0
    for p in merged:
        d = (t1 - t0) * len(p) / total
        cues.append((round(cur, 2), round(cur + d, 2), jp_lines(p)))
        cur += d
    return cues


# ===== 出典ラベル(背景セグメントに追従。サムネ区間は出さない) =====
merged_lab = []
for s in SEG:
    if not s["label"]:
        continue
    if merged_lab and merged_lab[-1][2] == s["label"] and abs(merged_lab[-1][1] - s["t0"]) < 0.05:
        merged_lab[-1][1] = s["t1"]
    else:
        merged_lab.append([s["t0"], s["t1"], s["label"]])

TRANS_SFX = ["se_scene.mp3", "se_taiko.mp3", "se_metal.mp3"]
SUB_SFX = ["se_type.mp3", "se_shakiin.mp3", "se_bell.mp3", "se_hyoshigi.mp3"]
BG_CUTS = [s["t0"] for s in SEG[1:]]                    # xfade開始時刻(=セグメント境界)

tl = []
bg_div = ('<div class="bgv" id="bg" style="opacity:1">'
          '<video id="bg-v" src="assets/bgvid/hiramoto_bg_full.mp4" muted playsinline '
          f'data-start="0" data-duration="{WIN + 0.6:.2f}" data-media-start="{W0:.2f}" '
          'data-track-index="10"></video></div>')

sub_divs, sub_times, all_lines = [], [], []
si = 0
for bid in ORDER:
    for (c0, c1, lines) in phrase_cues(bid):
        if not OV(c0, c1):
            continue
        sid = f"sub{si}"
        si += 1
        sub_times.append(round(c0, 2))
        all_lines.append((sid, lines))
        body = "<br>".join(f'<span class="ln">{colorize(ln)}</span>' for ln in lines)
        sub_divs.append(f'<div class="sub" id="{sid}">{body}</div>')
        # ★窓/pieceの先頭より前に始まったキュー(cont)は、先頭から不透明で出す。
        #   負の位置に置くとGSAPが描画せず字幕が丸ごと消え、0でフェードさせると
        #   piece境界で再フェード＝ちらつきになるため、どちらも避ける。
        if T(c0) < 0:
            tl.append(f"tl.fromTo('#{sid}',{{opacity:1}},{{opacity:1,duration:.01}},0.00);")
        else:
            tl.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.14}},{T(c0):.2f});")
        tl.append(f"tl.to('#{sid}',{{opacity:0,duration:.10}},{T(c1 - 0.02):.2f});")

# ===== 冒頭タイトル(0〜t0終わり)。語ごとに原色で色分けし、行ごとに黒帯を敷く =====
TITLE_LINES = [("どう見ても", "w"), ("ダウトベック", "b"), ("判定2-1に賛否", "y")]
T_END = B["h1"]["start"]
title_divs = []
if OV(0.0, T_END):
    inner = "".join(f'<span class="tl t-{c}">{esc(t)}</span>' for t, c in TITLE_LINES)
    title_divs.append(f'<div class="bigtitle" id="bigt">{inner}</div>')
    tl.append("tl.fromTo('#bigt',{opacity:0},{opacity:1,duration:.18},%.2f);" % max(0.0, T(0.15)))
    tl.append("tl.to('#bigt',{opacity:0,duration:.20},%.2f);" % T(T_END - 0.30))

src_divs = []
for n, (t0, t1, lab) in enumerate(merged_lab):
    if not OV(t0, t1):
        continue
    sid = f"src{n}"
    src_divs.append(f'<div class="src" id="{sid}">{esc("出典: " + lab)}</div>')
    if T(t0 + 0.15) < 0:
        tl.append(f"tl.fromTo('#{sid}',{{opacity:.92}},{{opacity:.92,duration:.01}},0.00);")
    else:
        tl.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:.92,duration:.25}},{T(t0 + 0.15):.2f});")
    tl.append(f"tl.to('#{sid}',{{opacity:0,duration:.15}},{T(t1 - 0.05):.2f});")

# ★透かし・ヴェールもサムネ区間は出さない(支給素材を加工しない)
if W0 >= THUMB_END:
    tl.append("tl.set('#wm',{opacity:.92},0);")
    tl.append("tl.set('#veil',{opacity:1},0);")
else:
    tl.append("tl.set('#wm',{opacity:0},0);")
    tl.append(f"tl.to('#wm',{{opacity:.92,duration:.25}},{T(THUMB_END + 0.1):.2f});")
    tl.append("tl.set('#veil',{opacity:0},0);")
    tl.append(f"tl.to('#veil',{{opacity:1,duration:.25}},{T(THUMB_END + 0.05):.2f});")

# ===== SFX (背景切替 + 字幕切替), 近接除去+同音連続回避 =====
raw = ([(0.15, "M")]                                    # ★冒頭サムネ(全画面テキスト)は専用の衝撃音
       + [(round(t, 2), "T") for t in BG_CUTS] + [(round(t, 2), "S") for t in sub_times])
raw = [(t, k) for t, k in raw if 0.1 <= t < DUR - 0.2]
raw.sort(key=lambda x: x[0])
pri = {"M": 0, "T": 1, "S": 2}
dd = []
for t, k in raw:
    if dd and abs(t - dd[-1][0]) < 0.13:
        if pri[k] < pri[dd[-1][1]]:
            dd[-1] = (t, k)
        continue
    dd.append((t, k))
POOL = {"M": ["se_moji.mp3"], "T": TRANS_SFX, "S": SUB_SFX}
idxp = {"M": 0, "T": 0, "S": 0}
sfx = []
last = None
for t, k in dd:
    pool = POOL[k]
    f = pool[idxp[k] % len(pool)]
    idxp[k] += 1
    if f == last:
        f = pool[idxp[k] % len(pool)]
        idxp[k] += 1
    last = f
    sfx.append({"t": round(t, 2), "file": f})
if W0 == 0:   # ★窓ビルドで部分リストに上書きしないよう、通しビルドの時だけ書く
    (TPL / "sfx_events.json").write_text(json.dumps(sfx, ensure_ascii=False, indent=1), encoding="utf-8")

# ===== 幅検算: 1行がセーフ幅(1080-60=1020px)に収まるか =====
FS = 68
over, three = [], []
for sid, lines in all_lines:
    if len(lines) > 2:
        three.append((sid, lines))
    for ln in lines:
        w = sum(FS if ord(c) > 0x2E80 else FS * 0.55 for c in ln)
        if w > 1020:
            over.append((sid, ln, round(w)))
for sid, ln, w in over:
    print(f"  ★セーフ幅超過 {sid} {w}px: {ln}")
for sid, lines in three:
    print(f"  ★3行以上 {sid}: {lines}")
if over or three:
    raise SystemExit("字幕のレイアウト検算に失敗しました")

narr_tag = '' if VISUAL_ONLY else '<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="60" data-volume="1"></audio>'
bgm_tag = '' if VISUAL_ONLY else '<audio id="bgm" src="assets/audio/bgm.mp3" data-start="0" data-track-index="61" data-volume="0.06"></audio>'

HTML = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
  @font-face{{font-family:"JPHeavy";src:url("assets/fonts/SourceHanSansJP-Heavy.otf");}}
  @font-face{{font-family:"JPMed";src:url("assets/fonts/SourceHanSansJP-Medium.otf");}}
  :root{{--yellow:#ffd21e;--white:#fff;--red:#ff3b3b;--blue:#36b3ff;--ink:#0a0a0a;
    --edge:drop-shadow(5px 0 0 var(--ink)) drop-shadow(-5px 0 0 var(--ink)) drop-shadow(0 5px 0 var(--ink)) drop-shadow(0 -5px 0 var(--ink))
      drop-shadow(4px 4px 0 var(--ink)) drop-shadow(-4px 4px 0 var(--ink)) drop-shadow(4px -4px 0 var(--ink)) drop-shadow(-4px -4px 0 var(--ink)) drop-shadow(0 10px 22px rgba(0,0,0,.9));
    --edsm:drop-shadow(0 0 2px var(--ink)) drop-shadow(2px 0 1px var(--ink)) drop-shadow(-2px 0 1px var(--ink)) drop-shadow(0 2px 1px var(--ink)) drop-shadow(0 3px 8px rgba(0,0,0,.9));}}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  #root{{position:absolute;inset:0;overflow:hidden;background:#05060a;font-family:"JPHeavy";}}
  .bgv{{position:absolute;inset:0;z-index:1;overflow:hidden;}}
  .bgv video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform:translateZ(0);backface-visibility:hidden;}}
  .veil{{position:absolute;inset:0;z-index:5;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,.30) 0%,transparent 20%,transparent 52%,rgba(0,0,0,.55) 100%);}}
  .wm{{position:absolute;z-index:30;left:34px;top:40px;font-family:"JPHeavy";font-size:34px;color:#fff;letter-spacing:.04em;filter:var(--edsm);opacity:0;}}
  .sub{{position:absolute;z-index:25;left:30px;right:30px;top:1120px;text-align:center;opacity:0;
    font-family:"JPHeavy";font-weight:900;font-size:{FS}px;line-height:1.28;color:#fff;filter:var(--edge);letter-spacing:.01em;}}
  .sub .ln{{display:inline-block;white-space:nowrap;}}
  .sub .c-r{{color:var(--red);}} .sub .c-y{{color:var(--yellow);}} .sub .c-b{{color:var(--blue);}} .sub .c-w{{color:#fff;}}
  .bigtitle{{position:absolute;z-index:28;left:0;right:0;top:300px;text-align:center;opacity:0;}}
  .bigtitle .tl{{display:block;width:fit-content;margin:0 auto 12px;padding:6px 22px;border-radius:8px;
    background:rgba(0,0,0,.78);font-family:"JPHeavy";font-weight:900;font-size:104px;line-height:1.16;
    letter-spacing:.01em;text-shadow:-6px 0px 0 var(--ink),6px 0px 0 var(--ink),0px -6px 0 var(--ink),0px 6px 0 var(--ink),-5px -5px 0 var(--ink),5px -5px 0 var(--ink),-5px 5px 0 var(--ink),5px 5px 0 var(--ink),-3px 0px 0 var(--ink),3px 0px 0 var(--ink),0px -3px 0 var(--ink),0px 3px 0 var(--ink),0 12px 26px rgba(0,0,0,.9);white-space:nowrap;}}
  .bigtitle .t-w{{color:#fff;}} .bigtitle .t-b{{color:var(--blue);}} .bigtitle .t-y{{color:var(--yellow);}}
  .src{{position:absolute;z-index:30;left:34px;top:1636px;font-family:"JPMed";font-size:25px;color:#eee;letter-spacing:.02em;
    background:rgba(0,0,0,.6);border-left:5px solid var(--yellow);padding:6px 14px;border-radius:3px;filter:var(--edsm);opacity:0;}}
</style></head><body>
  <div id="root" data-composition-id="hiramoto-dautbek-short" data-start="0" data-duration="{WIN:.2f}" data-width="1080" data-height="1920">
    {bg_div}
    {narr_tag}
    {bgm_tag}
    <div class="veil" id="veil"></div>
    <div class="wm" id="wm">格闘ニュースラボ</div>
    {''.join(title_divs)}
    {''.join(sub_divs)}
    {''.join(src_divs)}
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({{paused:true}});
{chr(10).join('      ' + x for x in tl)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['hiramoto-dautbek-short'] = tl;
    </script>
  </div>
</body></html>"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s subs={si} srclab={len(merged_lab)} sfx={len(sfx)} thumb_end={THUMB_END}")
