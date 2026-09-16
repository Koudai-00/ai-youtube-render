"""相本宗輝 完全解説 index.html 生成(1920x1080・窓対応・評伝型)。
   背景=事前結合した1本を分割したパート(<video>は数個)。前景=冒頭タイトル／章カード／章の常時コーナータグ(日付+対戦カード)／
   発言カード・採点テーブル／DOM字幕(キュー同期・≤2行)／出典ラベル／透かし。VISUAL_ONLYでレンダー→finalizeで音声mux。
   env: HF_WIN_START/HF_WIN_END/HF_VISUAL_ONLY/HF_OUTNAME。"""
from __future__ import annotations
import json, html, os, re as _re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "aimoto"
TPL = ROOT / "hyperframes" / "templates" / "aimoto"
TIM = json.load(open(ROOT / "subtitles" / "out" / EP / "timings.json", encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)
BEATS = TIM["beats"]; CUES = TIM["cues"]; CHAPS = TIM["chapters"]
CHAPTER_META = TIM["chapter_meta"]; DISP = TIM["disp"]

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

def disp(t):
    for k in sorted(DISP, key=len, reverse=True): t = t.replace(k, DISP[k])
    return t.replace("、と、", "と、").replace("、と。", "と。")

# 出典ラベル: bg_segments.json（背景生成の実割当）から引く＝素材と表示のズレ防止
_SEG = json.load(open(TPL / "assets" / "bg_segments.json", encoding="utf-8"))
SRC = {x["beat"]: "出典: " + x["label"] for x in _SEG}

# ---- 背景の時間帯(出典ラベル用) = bg_segments.json の順序 ----
BG = []
for i, x in enumerate(_SEG):
    t0 = x["t0"]
    t1 = _SEG[i + 1]["t0"] + 0.08 if i + 1 < len(_SEG) else COMP
    BG.append((round(t0, 3), round(t1, 3), x["beat"], "出典: " + x["label"]))

# ---- 冒頭タイトル ----
TITLE = [("トンネルから生まれたモンスター", "w", 0.9), ("相本宗輝", "y", 1.5)]
TITLE_T0, TITLE_T1 = 24.5, 34.0

# ---- 発言カード / テーブル ----
# (beat, kind, title, body, meta)  kind: media=発言カード / table=採点テーブル(bodyはrowsのlist)
CARDS_SPEC = [
    ("c1_1", "table", "相本宗輝（あいもと かずき）", [("生年月日", "2001.1.23", "茨城県水戸市出身"), ("身長／リーチ", "175cm／182cm", "フェザー級 66.0kg"), ("戦績", "10戦10勝", "8KO・TKO／判定2／無敗")], "DEEP／RIZIN公式サイト"),
    ("c4_4", "media", "鹿志村仁之介", "喧嘩自慢の先輩がいるって聞いて、一緒にやろうって。最初は僕がいじめてた。耳を潰したのも全部俺です。", "ゴング格闘技 インタビュー（2026年2月）"),
    ("c5_10", "media", "相本宗輝（DEEP 120 試合後マイク）", "名前のある選手をお願いします！", "2024年7月14日 後楽園ホール"),
    ("c7_3", "media", "相本宗輝", "自分の感覚では水抜き中に意識がなくなって、起きたら病院のベッドの上で点滴を打たれていました。", "MMAPLANET インタビュー（2025年9月）"),
    ("c8_5", "media", "相本宗輝（DEEP 127 試合後マイク）", "9か月ぶりの試合は、正直めちゃくちゃ怖かったです。前回の減量でぶっ倒れて記憶も飛ばしたけど、皆のおかげで戻ってこられました。", "2025年9月15日 後楽園ホール"),
    ("c9_5", "media", "榊原信行 RIZIN CEO", "RIZINで待ってる。", "DEEP 129 セミファイナル後にケージイン（2025年12月14日）"),
    ("c9_13", "media", "相本宗輝", "自分のやってきたこと全て押し付けるだけなんで。3月、しっかりぶっ飛ばしてみんなの記憶に刻む。", "RIZIN CONFESSIONS #206"),
    ("c9_16", "table", "RIZIN.52 試合変更のお知らせ（2026年3月5日）", [("3月3日", "ロードバイク走行中に車と接触", "転倒"), ("3月4日", "頭痛・めまい・嘔吐", "脳神経外科を受診"), ("3月5日", "容態が急変し救急搬送", "出場不可")], "RIZIN公式サイト"),
    ("c10_1", "media", "佐伯繁 DEEP代表", "減量のしすぎで脳がまともに機能しないんじゃないか。復帰に関してはとにかくライト級でやってくれ。", "U-NEXT格闘技 相本宗輝×佐伯繁"),
    ("c11_7", "media", "高橋遼伍", "ストライキングはもちろん、フィジカルが強い。", "MMAPLANET インタビュー（2025年12月）"),
    ("c13_2", "table", "アバイジャ・カレオ・メヘウラ", [("生年月日", "1995.11.25（30歳）", "米ハワイ州出身"), ("所属", "Xtreme Couture", "身長175cm／リーチ188cm"), ("戦績", "6勝4敗1無効試合", "KO4・一本1・判定1")], "RIZIN公式サイト／Wikipedia"),
]

def card_html(cid, kind, title, body, meta, cont=False):
    op = ' style="opacity:1"' if cont else ''
    if kind == "table":
        rows = "".join(f'<div class="trow"><div class="tk">{esc(a)}</div><div class="tv">{esc(b)}</div><div class="tn">{esc(c)}</div></div>' for a, b, c in body)
        return (f'<div class="ccard table" id="{cid}"{op}><div class="mtag">{esc(title)}</div>'
                f'<div class="tbl">{rows}</div><div class="cmeta">{esc(meta)}</div></div>')
    L = len(body)
    fs = 36 if L <= 60 else 32 if L <= 100 else 28 if L <= 150 else 25
    return (f'<div class="ccard media" id="{cid}"{op}>'
            f'<div class="mtag">{esc(title)}</div>'
            f'<div class="ctext" style="font-size:{fs}px">{esc(body)}</div>'
            f'<div class="cmeta">{esc(meta)}</div></div>')

# ---- 字幕分割(≤2行 各≤26全角) ----
def zwidth(s):
    w = 0
    for ch in s:
        w += 0.55 if (ch.isascii() and (ch.isalnum() or ch in " .,'-〜!?/%")) else 1.0
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
        BREAK_AFTER = set("、。」）】！？はがをにへとでものやねよ")
        def snap(t):
            for d in range(0, 9):
                for c in (t - d, t + d):
                    if 0 < c < len(text) and text[c-1] in BREAK_AFTER:
                        return c
            c = t
            while 0 < c < len(text) and text[c-1].isascii() and text[c].isascii() and (text[c-1].isalnum() or text[c].isalnum()):
                c += 1
            return c
        cut = snap(target)
        if cut >= len(text) or cut <= 0:
            cut = max(1, min(len(text) - 1, target))
        KATA = _re.compile(r'[ァ-ヴーｦ-ﾟA-Za-z0-9・\-]')
        def inside_word(c):
            return 0 < c < len(text) and bool(KATA.match(text[c-1])) and bool(KATA.match(text[c]))
        PUNCT = set("、。」』）】！？")
        def ok(c):
            lim = min(maxw + 4.5, 27.0)
            if not (0 < c < len(text)) or inside_word(c) or text[c] in PUNCT:
                return False
            if not any(ch not in PUNCT for ch in text[c:]) or not any(ch not in PUNCT for ch in text[:c]):
                return False
            return zwidth(text[:c]) <= lim and zwidth(text[c:]) <= lim
        if not ok(cut):
            cands = []
            for c in range(max(1, cut - 16), min(len(text) - 1, cut + 16) + 1):
                if not ok(c):
                    continue
                pen = 0 if text[c-1] in "、。" else (6 if text[c-1] in BREAK_AFTER else 10)
                if text[c] in "のをがにはでとへもや": pen += 5   # 助詞で始まる行を避ける
                cands.append((abs(c - target) + pen, c))
            if cands:
                cut = min(cands)[1]
        if zwidth(text[:cut]) > 27.0 or zwidth(text[cut:]) > 27.0 or text[cut] in PUNCT:
            c2 = max(1, min(len(text) - 1, target))
            while c2 > 1 and (zwidth(text[:c2]) > 27.0 or text[c2] in PUNCT):
                c2 -= 1
            cut = c2
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
    # 末尾の極小断片は直前へ吸収
    while len(cues) >= 2 and zwidth(cues[-1]) <= 7 and fits_two(cues[-2] + cues[-1], maxw):
        t = cues.pop(); cues[-1] += t
    return cues or [text]
def sub_lines(text, maxw=23.0):
    if zwidth(text) <= maxw: return [text]
    w = wrap_two(text, maxw)
    return [w[0], w[1]] if w else [text]

# ---- 背景 DOM/TL（パート方式） ----
bg_divs, bg_tws, src_divs = [], [], []
PARTS = json.load(open(TPL / "assets" / "bgvid_full" / "parts.json", encoding="utf-8"))
for k, pt in enumerate(PARTS):
    pt0, pt1 = pt["t0"], pt["t1"]
    if not OV(pt0, pt1):
        continue
    bid = f"bgp{k}"
    ds = max(0.0, T(pt0)); ms = max(0.0, W0 - pt0)
    dur = min(pt["media_len"] - ms, (W1 - max(pt0, W0)) + 0.6)
    if dur <= 0.05:
        continue
    bg_divs.append(
        f'<div class="bgseg" id="{bid}" style="z-index:{k + 1};opacity:1">'
        f'<video id="{bid}-v" src="assets/bgvid_full/{pt["file"]}" muted playsinline '
        f'data-layout-allow-overflow data-start="{ds:.2f}" data-duration="{dur:.2f}" '
        f'data-media-start="{ms:.2f}" data-track-index="{10 + k}"></video></div>')
    bg_tws.append(f"tl.set('#{bid}',{{opacity:1}},0);")

# 出典ラベル（連続同一はまとめる）
_ranges = []
for t0, t1, fn, sl in BG:
    if not sl: continue
    if _ranges and _ranges[-1][2] == sl and abs(_ranges[-1][1] - t0) < 0.2:
        _ranges[-1] = (_ranges[-1][0], t1, sl)
    else:
        _ranges.append((t0, t1, sl))
for i, (t0, t1, srcl) in enumerate(_ranges):
    if not OV(t0, t1): continue
    if (min(t1, W1) - max(t0, W0)) <= 0.6: continue
    vt0, vt1 = T(t0), T(t1)
    sid = f"src{i}"
    src_divs.append(f'<div class="srclab" id="{sid}">{esc(srcl)}</div>')
    if vt0 + 0.3 < 0:
        bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:1}},{{opacity:1,duration:.01}},0.00);")
    else:
        bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{vt0 + 0.3:.2f});")
    bg_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{vt1 - 0.25:.2f});")

# ---- 冒頭タイトル ----
title_divs, title_tws = [], []
if OV(TITLE_T0, TITLE_T1):
    rows = "".join(f'<div class="ttlrow {c}">{esc(txt)}</div>' for txt, c, _ in TITLE)
    title_divs.append(f'<div class="bigtitle" id="bigttl">{rows}</div>')
    for j, (txt, c, dl) in enumerate(TITLE):
        at = T(TITLE_T0) + dl
        if at < 0:
            title_tws.append(f"tl.set('#bigttl .ttlrow:nth-child({j+1})',{{opacity:1,y:0}},0);")
        else:
            title_tws.append(f"tl.fromTo('#bigttl .ttlrow:nth-child({j+1})',{{opacity:0,y:60}},{{opacity:1,y:0,duration:.6,ease:'power3.out'}},{at:.2f});")
    title_tws.append(f"tl.to('#bigttl',{{opacity:0,duration:.5}},{T(TITLE_T1):.2f});")

# ---- 章カード(3.4s) と 常時コーナータグ ----
chap_divs, chap_tws, chap_audio = [], [], []
for j, c in enumerate(CHAPS):
    st = c["start"]
    nxt = CHAPS[j + 1]["start"] if j + 1 < len(CHAPS) else COMP
    head, card = CHAPTER_META.get(c["chapter"], (c["chapter"], ""))
    # 章カード
    if OV(st, st + 3.8):
        cid = f"chap{j}"
        chap_divs.append(f'<div class="chaptag" id="{cid}"><div class="chnum">CHAPTER {j+1:02d}　{esc(head)}</div>'
                         f'<div class="chttl">{esc(card)}</div></div>')
        chap_tws.append(f"tl.fromTo('#{cid} .chnum',{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.5,ease:'power3.out'}},{max(0.0,T(st)+0.05):.2f});")
        chap_tws.append(f"tl.fromTo('#{cid} .chttl',{{opacity:0,y:40}},{{opacity:1,y:0,duration:.6,ease:'power3.out'}},{max(0.0,T(st)+0.2):.2f});")
        chap_tws.append(f"tl.to('#{cid}',{{opacity:0,duration:.4}},{T(st)+3.4:.2f});")
        if not VISUAL_ONLY:
            chap_audio.append(f'<audio id="chs{j}" src="assets/se/chapter.wav" data-start="{T(st+0.05):.2f}" data-track-index="{200+j}" data-volume="0.5"></audio>')
    # コーナータグ（章の間ずっと表示。窓境界では先頭から不透明）
    if OV(st + 3.6, nxt) and card:
        tid = f"ctag{j}"
        chap_divs.append(f'<div class="ctag" id="{tid}"><div class="ctd">{esc(head)}</div><div class="ctc">{esc(card)}</div></div>')
        a = T(st + 3.6)
        if a <= 0.02:
            chap_tws.append(f"tl.fromTo('#{tid}',{{opacity:1}},{{opacity:1,duration:.01}},0.00);")
        else:
            chap_tws.append(f"tl.fromTo('#{tid}',{{opacity:0}},{{opacity:1,duration:.5}},{a:.2f});")
        chap_tws.append(f"tl.to('#{tid}',{{opacity:0,duration:.3}},{T(nxt)-0.3:.2f});")

# ---- カード ----
card_divs, card_tws = [], []
for k, (bid, kind, title, body, meta) in enumerate(CARDS_SPEC):
    t0 = bs(bid) + 0.25; t1 = be(bid) - 0.15
    if not OV(t0, t1): continue
    cid = f"cc{k}"; cont = T(t0) <= 0.02
    card_divs.append(card_html(cid, kind, title, body, meta, cont))
    if cont:
        card_tws.append(f"tl.set('#{cid}',{{opacity:1,x:0,y:0}},0);")
    else:
        card_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,x:60,y:18}},{{opacity:1,x:0,y:0,duration:.5,ease:'back.out(1.5)'}},{T(t0):.2f});")
    card_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-14,duration:.35,ease:'power1.in'}},{T(t1):.2f});")

# ---- 字幕（キュー同期。無音キューはスキップ） ----
sub_divs, sub_tws = [], []
sidx = 0
for c in CUES:
    if c.get("silent") or not c.get("text", "").strip(): continue
    text = disp(c["text"])
    cues = split_two_lines(text)
    dur = c["end"] - c["start"]
    wsum = sum(zwidth(x) for x in cues) or 1.0
    acc = 0.0
    for cue in cues:
        cs = c["start"] + dur * acc / wsum; acc += zwidth(cue); ce = c["start"] + dur * acc / wsum
        if not OV(cs, ce): continue
        lines = sub_lines(cue); inner = "<br>".join(esc(l) for l in lines)
        did = f"sub{sidx}"; sidx += 1
        sub_divs.append(f'<div class="subt" id="{did}">{inner}</div>')
        if T(cs) < 0:
            sub_tws.append(f"tl.fromTo('#{did}',{{opacity:1}},{{opacity:1,duration:.01}},0.00);")
        else:
            sub_tws.append(f"tl.fromTo('#{did}',{{opacity:0}},{{opacity:1,duration:.18}},{T(cs):.2f});")
        sub_tws.append(f"tl.to('#{did}',{{opacity:0,duration:.14}},{T(ce-0.05):.2f});")

def J(items, ind="      "): return "\n".join(ind + x for x in items)
AUDIO_BLOCK = ("" if VISUAL_ONLY else
    '<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="60" data-volume="1"></audio>')

HTML = f"""<!doctype html>
<!-- 相本宗輝 完全解説 1920x1080 -->
<html>
<head>
<meta charset="utf-8">
<style>
  @font-face{{font-family:"Mincho";src:url("assets/fonts/GokubutoMincho.ttf");}}
  @font-face{{font-family:"JPHeavy";src:url("assets/fonts/SourceHanSansJP-Heavy.otf");}}
  @font-face{{font-family:"JPMed";src:url("assets/fonts/SourceHanSansJP-Medium.otf");}}
  :root{{
    --white:#fff; --yellow:#ffe23a; --red:#ff3a3a; --blue:#36b6ff; --gold:#e8b64c; --ink:#0a0c12;
    --edge:drop-shadow(4px 0 0 var(--ink)) drop-shadow(-4px 0 0 var(--ink)) drop-shadow(0 4px 0 var(--ink)) drop-shadow(0 -4px 0 var(--ink))
           drop-shadow(3px 3px 0 var(--ink)) drop-shadow(-3px 3px 0 var(--ink)) drop-shadow(0 8px 16px rgba(0,0,0,.8));
    --edge-sm:drop-shadow(0 0 2px var(--ink)) drop-shadow(1px 1px 1px var(--ink)) drop-shadow(0 2px 6px rgba(0,0,0,.85));
    --tsh: 4px 0 0 var(--ink),-4px 0 0 var(--ink),0 4px 0 var(--ink),0 -4px 0 var(--ink),3px 3px 0 var(--ink),-3px 3px 0 var(--ink),3px -3px 0 var(--ink),-3px -3px 0 var(--ink),0 10px 22px rgba(0,0,0,.85);
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
  .bigtitle{{position:absolute;z-index:330;left:0;right:0;top:27%;text-align:center;}}
  .bigtitle .ttlrow{{font-family:"Mincho";font-weight:900;line-height:1.15;text-shadow:var(--tsh);opacity:0;white-space:nowrap;}}
  .bigtitle .ttlrow.w{{font-size:84px;color:#fff;}} .bigtitle .ttlrow.y{{font-size:132px;color:var(--yellow);margin-top:10px;}}
  .chaptag{{position:absolute;z-index:320;left:110px;top:34%;opacity:1;}}
  .chaptag .chnum{{font-family:"JPHeavy";font-size:38px;color:var(--gold);letter-spacing:.06em;filter:var(--edge);opacity:0;white-space:nowrap;}}
  .chaptag .chttl{{font-family:"Mincho";font-weight:900;font-size:80px;color:#fff;text-shadow:var(--tsh);margin-top:10px;white-space:nowrap;opacity:0;}}
  .ctag{{position:absolute;z-index:325;right:40px;top:26px;text-align:right;opacity:0;}}
  .ctag .ctd{{font-family:"JPMed";font-size:22px;color:var(--gold);letter-spacing:.04em;filter:var(--edge-sm);}}
  .ctag .ctc{{font-family:"JPHeavy";font-size:30px;color:#fff;filter:var(--edge-sm);margin-top:2px;}}
  .ccard{{position:absolute;z-index:330;right:74px;top:150px;width:820px;background:#fff;color:#0f1419;border-radius:20px;
        padding:26px 30px;box-shadow:0 18px 50px rgba(0,0,0,.6);opacity:0;border:1px solid #cfd9de;}}
  .ccard .ctext{{font-family:"JPMed";line-height:1.5;color:#0f1419;word-break:break-word;}}
  .ccard .cmeta{{margin-top:16px;padding-top:12px;border-top:1px solid #eaeef0;font-size:22px;color:#536471;}}
  .ccard .mtag{{display:inline-block;font-family:"JPHeavy";font-size:29px;color:#fff;background:#d62828;
        padding:5px 16px;border-radius:6px;margin-bottom:16px;letter-spacing:.02em;max-width:100%;}}
  .ccard.table .tbl{{display:flex;flex-direction:column;gap:8px;}}
  .ccard.table .trow{{display:grid;grid-template-columns:200px 250px 1fr;align-items:center;gap:14px;padding:8px 10px;background:#f4f6f8;border-radius:8px;}}
  .ccard.table .tk{{font-family:"JPHeavy";font-size:27px;color:#0f1419;}}
  .ccard.table .tv{{font-family:"JPHeavy";font-size:30px;color:#d62828;}}
  .ccard.table .tn{{font-family:"JPMed";font-size:22px;color:#333;line-height:1.3;}}
  .subt{{position:absolute;z-index:350;left:0;right:0;bottom:96px;text-align:center;opacity:0;
        font-family:"JPHeavy";font-size:45px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;padding:0 90px;}}
</style>
</head>
<body>
  <div id="root" data-composition-id="aimoto" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
{J(bg_divs,"    ")}

    {AUDIO_BLOCK}
{J(chap_audio,"    ")}

    <div class="veil"></div>
    <div class="wm">格闘ニュースラボ</div>
{J(src_divs,"    ")}
{J(title_divs,"    ")}
{J(chap_divs,"    ")}
{J(card_divs,"    ")}
{J(sub_divs,"    ")}

    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({{paused:true}});
{J(bg_tws)}
{J(title_tws)}
{J(chap_tws)}
{J(card_tws)}
{J(sub_tws)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['aimoto'] = tl;
    </script>
  </div>
</body>
</html>
"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} bg={len(bg_divs)} cards={len(card_divs)} chaps={len(chap_divs)} subs={len(sub_divs)}")
