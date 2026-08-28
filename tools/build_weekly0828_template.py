"""今週の格闘技ニュース(2026-07下旬) index.html 生成(1920x1080・長尺・窓対応)。
   背景=ナレ一致(試合映像/会見/ACA/イメージ)。前景=高精細Xキャプチャ+反応カード(一般人は匿名化)。
   章タグ・DOM字幕(≤2行)・出典ラベル・透かし。VISUAL_ONLYでレンダー→finalizeで音声mux。
   env: HF_WIN_START/HF_WIN_END/HF_VISUAL_ONLY/HF_OUTNAME。"""
from __future__ import annotations
import json, html, os, re as _re, hashlib as _hl
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "weekly0828"
TPL = ROOT / "hyperframes" / "templates" / EP
TIM = json.load(open(ROOT / "subtitles" / "out" / EP / "timings.json", encoding="utf-8"))
IDX = {x["id"]: x for x in json.load(open(ROOT / "assets" / "source" / f"episode_{EP}" / "xposts" / "assets_index.json", encoding="utf-8"))}
COMP = round(TIM["total"] + 0.3, 2)
BEATS = TIM["beats"]
CHAPS = TIM["chapters"]

W0 = float(os.environ.get("HF_WIN_START") or 0)
_w1 = os.environ.get("HF_WIN_END")
W1 = float(_w1) if _w1 else COMP
# 音声は常に外部mux(finalize)。assets/audio/narration.wav が無ければ自動でvisual-only(CI/ローカル共通)。
VISUAL_ONLY = os.environ.get("HF_VISUAL_ONLY") == "1" or not (TPL / "assets" / "audio" / "narration.wav").exists()
WIN = round(W1 - W0, 2)
OUTNAME = os.environ.get("HF_OUTNAME", "index.html")
def T(t): return round(t - W0, 3)
def OV(t0, t1): return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)
def esc(s): return html.escape(s)

BS = {b["id"]: b["start"] for b in BEATS}
BE = {b["id"]: b["end"] for b in BEATS}
def bs(bid): return BS[bid]
def be(bid): return BE[bid]

# ---- 字幕表示置換(読みかな→漢字/英字・数字) ----
DISP = {"ライジン": "RIZIN", "ユーエフシー": "UFC", "エムエムエー": "MMA", "エックス": "X",
        "ブレイキングダウン": "BreakingDown"}
DISP_NUM = {  # 漢数字→算用(日付/数量)。慣用句(一番/一心/一方/一戦 等)は変換しない
    "九月十日": "9月10日", "八月二十一日": "8月21日",
    "三つ": "3つ", "二人": "2人"}
def disp(t):
    for k in sorted(DISP_NUM, key=len, reverse=True): t = t.replace(k, DISP_NUM[k])
    for k in sorted(DISP, key=len, reverse=True): t = t.replace(k, DISP[k])
    return t

# 出典ラベル
S_AK = "出典: RIZIN.52 秋元強真 vs パッチー・ミックス (RIZIN / U-NEXT)"
S_MIKU = "出典: 朝倉未来 YouTube"
S_HOSO = "出典: 細川バレンタイン YouTube"
S_BD = "出典: BreakingDown"
S_NAN = "出典: ORICON『超RIZIN.5』独占インタビュー"
S_KAIKEN = "出典: RIZIN 記者会見"
S_KWJ = "出典: ドンマイ川端 柔道"
S_KWY = "出典: ドンマイ川端 / 朝倉海 YouTube"
S_RIZINP = "出典: 超RIZIN.5 公式対戦カード"
S_JRE = "出典: JRE MMA Show #184 (PowerfulJRE)"
S_RIZINS = "出典: RIZIN 公式 (RIZINtv)"
S_PEX = "出典: イメージ映像"

# ============ 背景プラン: beat_id -> (bgvidファイル, motion, srclabel) ============
# 連続で同一ファイルは自動マージ=1セグメント。Pexels(px_*)は各≤2セグメント厳守。
BID_BG = {
    # OPEN(3topicのチラ見せ)
    "o1": ("ak_a", None, S_AK),
    "o2": ("miku2", None, S_MIKU),
    "o3": ("nanimono", None, S_NAN),
    "o4": ("ak_tag", None, S_AK),
    "o5": ("kaiken_kb", None, S_KAIKEN),
    # CH1 朝倉未来×細川バレンタイン
    "c1_tag": ("miku1", None, S_MIKU),
    "c1_a": ("miku2", None, S_MIKU),
    "c1_b": ("miku3", None, S_MIKU),
    "c1_c": ("miku1", None, S_MIKU),
    "c1_d": ("bd_ctx", None, S_BD),                 # BreakingDown批判
    "c1_e": ("hoso_tweet", None, S_HOSO),           # 未来の発言(ツイート文字起こし)
    "c1_f": ("hoso_tweet", None, S_HOSO),           # 炎上手法…の引用(c1_e-fで1セグ)
    "c1_g": ("miku3", None, S_MIKU),                # 一蹴(未来)
    "c1_h": ("hoso_talk", None, S_HOSO),            # 細川本人が反応
    "c1_i": ("hoso_talk2", None, S_HOSO),           # ファンの声
    # CH2 ドンマイ川端 欠場疑惑
    "c2_tag": ("nanimono", None, S_NAN),
    "c2_a": ("kaiken_kb", None, S_KAIKEN),          # 大前提(会見の川端)
    "c2_b": ("nanimono2", None, S_NAN),
    "c2_c": ("sr5_card", "kb_zin", S_RIZINP),       # 公式対戦カード
    "c2_d": ("kaiken_kb2", None, S_KAIKEN),         # なぜ噂が(会見の川端)
    "c2_e": ("kaiken_kb3", None, S_KAIKEN),         # 野村道場欠席の噂
    "c2_f": ("kawabata_train", None, S_KWJ),        # 追い込み/怪我(柔道)
    "c2_g": ("kaiken_kb", None, S_KAIKEN),          # 欠場疑惑(会見の川端)
    "c2_h": ("kaiken_kb2", None, S_KAIKEN),         # 会見の川端
    "c2_i": ("nanimono", None, S_NAN),              # ファンの声(会見で笑い)
    "c2_j": ("nanimono2", None, S_NAN),             # 公式待ち(明るい川端)
    # CH3 秋元強真 海外絶賛
    "c3_tag": ("ak_a2", None, S_AK),
    "c3_a": ("ak_finish", None, S_AK),
    "c3_b": ("sterling", None, S_JRE),
    "c3_c": ("sterling2", None, S_JRE),
    "c3_d": ("ak_dodge", None, S_AK),               # ネオのようにかわす
    "c3_e": ("matrix", None, S_RIZINS),             # マトリックス
    "c3_f": ("ak_tag", None, S_AK),                 # 海外ファン驚き
    "c3_g": ("matrix2", None, S_RIZINS),            # RIZIN公式クリップ
    # END(回顧)
    "e1": ("ak_end", None, S_AK),
    "e2": ("miku1", None, S_MIKU),
    "e3": ("nanimono2", None, S_NAN),
}

# beat順に走査→連続同一ファイルをマージしてBGセグメント化
def clip_dur(fn):
    import subprocess
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(TPL / "assets" / "bgvid" / f"{fn}.mp4")], capture_output=True, text=True)
    try: return float(p.stdout.strip())
    except: return 0.0

BG = []
for b in BEATS:
    bid = b["id"]
    fn, mo, sl = BID_BG.get(bid, ("px_arena", None, S_PEX))
    if BG and BG[-1][2] == fn:
        BG[-1] = (BG[-1][0], b["end"], fn, BG[-1][4] or mo, sl)
    else:
        BG.append((b["start"], b["end"], fn, mo, sl))
# 隙間/連続を次開始+0.08まで延長(境界黒回避)
BG.sort(key=lambda e: e[0])
_bg2 = []
for i, seg in enumerate(BG):
    t0, t1, fn, mo, sl = seg
    if i + 1 < len(BG): t1 = round(BG[i + 1][0] + 0.08, 3)
    _bg2.append((round(t0, 3), round(t1, 3), fn, mo, sl))
BG = _bg2
BG[0] = (0.0, BG[0][1], BG[0][2], BG[0][3], BG[0][4])
BG[-1] = (BG[-1][0], COMP, BG[-1][2], BG[-1][3], BG[-1][4])

# ============ Xカード配置 (post_id, bid_start, bid_end, style) ============
CARDS_SPEC = [
    # CH2のみ(実在の反応・一般ファン=匿名化)。CH1/CH3は一次映像で構成しカード無し。
    ("kw_e",  "c2_e", "c2_e", "cap"),   # 噂の火種(野村道場欠席→怪我で欠場?)
    ("kw_h",  "c2_g", "c2_h", "rea"),   # 海のセコンド発言は否定にならない/どちらとも言えない
    ("kw_i1", "c2_i", "c2_i", "cap"),   # 会見で笑いとってたのに…
    ("kw_i2", "c2_i", "c2_i", "rea"),   # ガセであって欲しい
    ("kw_j",  "c2_j", "c2_j", "rea"),   # 出るなら出るで否定しろ
]
CARDS = []
for pid, b0, b1, st in CARDS_SPEC:
    t0 = bs(b0) + 0.15; t1 = be(b1) - 0.1
    CARDS.append((pid, round(t0, 3), round(t1, 3), st))

CHAP_LABEL = {
    "ch1": ("1つ目のニュース", "朝倉未来 が 細川バレンタイン を語る"),
    "ch2": ("2つ目のニュース", "ドンマイ川端 に 欠場疑惑（公式未確認）"),
    "ch3": ("3つ目のニュース", "秋元強真 が 海外で大絶賛"),
}

# ---------- 字幕分割(≤2行 各≤26全角) ----------
def zwidth(s):
    w = 0
    for ch in s:
        w += 0.55 if (ch.isascii() and (ch.isalnum() or ch in " .,'-〜")) else 1.0
    return w
def wrap_two(text, maxw):
    # まず読点(、)境界で2行に分ける(自然な改行)
    segs = [s for s in _re.split("(?<=、)", text) if s]
    best = None
    for i in range(1, len(segs)):
        l1 = "".join(segs[:i]); l2 = "".join(segs[i:])
        if zwidth(l1) <= maxw and zwidth(l2) <= maxw:
            # 2行の長さが均等な分割を優先
            if best is None or abs(zwidth(l1) - zwidth(l2)) < best[0]:
                best = (abs(zwidth(l1) - zwidth(l2)), l1, l2)
    if best: return (best[1], best[2])
    if zwidth(text) <= maxw * 2:
        # 読点で割れない時は、英数字/連語トークンを割らない位置で中央付近を折る
        def safe(cut):
            # cutが英数字連続の途中なら境界までずらす
            while 0 < cut < len(text) and text[cut-1].isascii() and text[cut].isascii() \
                    and (text[cut-1].isalnum() or text[cut].isalnum()):
                cut += 1
            return cut
        target = int(len(text) * maxw / max(zwidth(text), 1))
        cut = safe(target)
        if cut >= len(text): cut = safe(max(1, target - 2))
        return (text[:cut], text[cut:])
    return None
def fits_two(text, maxw):
    if zwidth(text) <= maxw: return True
    return wrap_two(text, maxw) is not None
def split_two_lines(text, maxw=26.0):
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
def sub_lines(text, maxw=26.0):
    if zwidth(text) <= maxw: return [text]
    w = wrap_two(text, maxw)
    return [w[0], w[1]] if w else [text]

# ---------- 背景 DOM/TL ----------
bg_divs, bg_tws, src_divs = [], [], []
for i, (t0, t1, fn, mo, srcl) in enumerate(BG):
    if not OV(t0, t1): continue
    bid = f"bg{i}"; vt0, vt1 = T(t0), T(t1)
    cont = vt0 <= 0.02
    cd = clip_dur(fn)
    ms = max(0.0, W0 - t0)
    ds = max(0.0, vt0)
    dur = (min(t1, W1) - max(t0, W0)) + 0.6
    if ms + dur > cd - 0.03:            # クリップ長を超えない(黒尾防止)
        dur = max(0.3, cd - ms - 0.05)
    inner = (f'<video id="{bid}-v" src="assets/bgvid/{fn}.mp4" muted playsinline data-layout-allow-overflow '
             f'data-start="{ds:.2f}" data-duration="{dur:.2f}" data-media-start="{ms:.2f}" data-track-index="{10+i}"></video>')
    op = ";opacity:1" if cont else ""
    bg_divs.append(f'<div class="bgseg" id="{bid}" style="z-index:{i+1}{op}">{inner}</div>')
    if cont:
        bg_tws.append(f"tl.set('#{bid}',{{opacity:1}},0);")
    else:
        bg_tws.append(f"tl.fromTo('#{bid}',{{opacity:0}},{{opacity:1,duration:.45,ease:'power1.inOut'}},{vt0:.2f});")
    sel = f"'#{bid}-v'"
    kbs = max(0.0, vt0); kbd = min(t1, W1) - max(t0, W0) + 0.4
    m = mo or ("kb_zin" if (i % 2 == 0) else "kb_pan")
    if m == "kb_zin":
        bg_tws.append(f"tl.fromTo({sel},{{scale:1.0}},{{scale:1.10,duration:{kbd:.2f},ease:'none'}},{kbs:.2f});")
    elif m == "kb_pan":
        bg_tws.append(f"tl.fromTo({sel},{{scale:1.08,x:-24}},{{x:24,duration:{kbd:.2f},ease:'none'}},{kbs:.2f});")
    if srcl:
        sid = f"src{i}"
        src_divs.append(f'<div class="srclab" id="{sid}">{esc(srcl)}</div>')
        bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{max(0.0,vt0+0.3):.2f});")
        bg_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{vt1-0.25:.2f});")

# ---------- 章タグ ----------
chap_divs, chap_tws, chap_audio = [], [], []
for j, c in enumerate(CHAPS):
    if c["chapter"] not in CHAP_LABEL: continue
    st = c["start"]
    if not OV(st, st + 3.8): continue
    ja, sub = CHAP_LABEL[c["chapter"]]
    cid = f"chap{j}"
    chap_divs.append(f'<div class="chaptag" id="{cid}"><div class="chnum">{esc(ja)}</div>'
                     f'<div class="chttl">{esc(sub)}</div></div>')
    chap_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,y:40}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.6)'}},{T(st+0.1):.2f});")
    chap_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-26,duration:.4,ease:'power1.in'}},{T(st+3.4):.2f});")
    if not VISUAL_ONLY:
        chap_audio.append(f'<audio id="chs{j}" src="assets/se/chapter.wav" data-start="{T(st+0.1):.2f}" data-track-index="{200+j}" data-volume="0.55"></audio>')

# ---------- Xカード(一般人=匿名化) ----------
ANON_NAMES = ["格闘技ファン", "MMAウォッチャー", "リングサイド", "週末の観戦勢",
              "格闘技好き", "現地観戦民", "格闘技マニア", "海外MMAファン"]
def card_html(cid, post, style, cont=False):
    pid = post["id"]
    keep = post.get("role") == "capture"
    if keep:
        name = esc(post.get("name", "")); handle = esc("@" + post.get("handle", ""))
        av_html = f'<img class="xav" src="assets/img/avatars/{pid}.jpg">'
        badge = '<span class="vbadge">✔</span>' if post.get("verified") else ""
    else:
        h = int(_hl.md5(pid.encode()).hexdigest(), 16)
        name = esc(ANON_NAMES[h % len(ANON_NAMES)])
        b36 = "0123456789abcdefghijklmnopqrstuvwxyz"
        handle = "@" + "".join(b36[(h >> (i * 5)) % 36] for i in range(8))
        av_html = f'<div class="xav anon" style="background:hsl({h % 360},45%,55%)">{esc(post.get("name","")[:1] or "?")}</div>'
        badge = ""
    txt = post.get("text", "")
    txt = _re.sub(r"https?://t\.co/\S+", "", txt).strip()
    txt = _re.sub(r"^(@\w+\s*)+", "", txt).strip()
    txt_html = esc(txt).replace("\n", "<br>")
    L = len(txt)
    if style == "cap":
        fs = 38 if L <= 55 else 34 if L <= 95 else 30 if L <= 140 else 26 if L <= 195 else 22
    else:
        fs = 33 if L <= 48 else 29 if L <= 88 else 25 if L <= 130 else 21
    eng = post.get("engagement", {})
    def fmt(n):
        if not n: return None
        return f"{n/10000:.1f}万".replace(".0万", "万") if n >= 10000 else f"{n:,}"
    stats = []
    if eng.get("reposts"): stats.append(f'<span class="st"><b>{fmt(eng["reposts"])}</b> リポスト</span>')
    if eng.get("likes"): stats.append(f'<span class="st"><b>{fmt(eng["likes"])}</b> いいね</span>')
    if eng.get("views"): stats.append(f'<span class="st"><b>{fmt(eng["views"])}</b> 表示</span>')
    stat_html = '<div class="xstats">' + "".join(stats) + '</div>' if stats else ""
    cls = "xcard cap" if style == "cap" else "xcard rea"
    op = ' style="opacity:1"' if cont else ''
    return (f'<div class="{cls}" id="{cid}"{op}>'
            f'<div class="xhead">{av_html}'
            f'<div class="xnm"><div class="xname">{name}{badge}</div>'
            f'<div class="xhandle">{handle}</div></div>'
            f'<div class="xlogo">𝕏</div></div>'
            f'<div class="xtext" style="font-size:{fs}px">{txt_html}</div>{stat_html}</div>')

card_divs, card_tws = [], []
for k, (pid, t0, t1, style) in enumerate(CARDS):
    if pid not in IDX or not OV(t0, t1): continue
    cid = f"xc{k}"; cont = T(t0) <= 0.02
    card_divs.append(card_html(cid, IDX[pid], style, cont))
    fromx = 70 if style == "cap" else -60
    if cont:
        card_tws.append(f"tl.set('#{cid}',{{opacity:1,x:0,y:0}},0);")
    else:
        card_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,x:{fromx},y:18}},{{opacity:1,x:0,y:0,duration:.5,ease:'back.out(1.5)'}},{T(t0):.2f});")
    card_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-14,duration:.35,ease:'power1.in'}},{T(t1):.2f});")

# ---------- 字幕 ----------
sub_divs, sub_tws = [], []
sidx = 0
for b in BEATS:
    text = disp(b["text"])
    cues = split_two_lines(text)
    # ★キュー表示時間は文字量に比例(発話ペースに近づけ、ナレとのズレを軽減)
    dur = b["end"] - b["start"]
    wsum = sum(zwidth(c) for c in cues) or 1.0
    acc = 0.0
    for ci, cue in enumerate(cues):
        cs = b["start"] + dur * acc / wsum
        acc += zwidth(cue)
        ce = b["start"] + dur * acc / wsum
        if not OV(cs, ce): continue
        lines = sub_lines(cue)
        inner = "<br>".join(esc(l) for l in lines)
        did = f"sub{sidx}"; sidx += 1
        sub_divs.append(f'<div class="subt" id="{did}">{inner}</div>')
        sub_tws.append(f"tl.fromTo('#{did}',{{opacity:0}},{{opacity:1,duration:.18}},{max(0.0,T(cs)):.2f});")
        sub_tws.append(f"tl.to('#{did}',{{opacity:0,duration:.14}},{T(ce-0.05):.2f});")

def J(items, ind="      "): return "\n".join(ind + x for x in items)
AUDIO_BLOCK = ("" if VISUAL_ONLY else
    '<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="60" data-volume="1"></audio>\n'
    '    <audio id="bgm" src="assets/audio/bgm.m4a" data-start="0" data-track-index="61" data-volume="0.075"></audio>')

HTML = f"""<!doctype html>
<!-- 今週の格闘技ニュース(自動生成/手編集可) 1920x1080 -->
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
  .srclab{{position:absolute;z-index:340;left:40px;bottom:24px;font-family:"JPMed";font-size:23px;color:#eaeaea;opacity:0;
        background:rgba(0,0,0,.5);border-left:4px solid var(--yellow);padding:6px 14px;border-radius:3px;filter:var(--edge-sm);}}
  .chaptag{{position:absolute;z-index:320;left:110px;top:39%;opacity:0;}}
  .chaptag .chnum{{font-family:"Mincho";font-size:44px;color:var(--yellow);filter:var(--edge);letter-spacing:.04em;}}
  .chaptag .chttl{{font-family:"JPHeavy";font-size:66px;color:#fff;filter:var(--edge);margin-top:6px;white-space:nowrap;}}
  .xcard{{position:absolute;z-index:330;background:#fff;color:#0f1419;border-radius:20px;padding:24px 28px;
        box-shadow:0 18px 50px rgba(0,0,0,.6);opacity:0;border:1px solid #cfd9de;}}
  .xcard.cap{{right:78px;top:150px;width:790px;}}
  .xcard.cap .xtext{{line-height:1.45;}}
  .xcard.rea{{left:78px;top:330px;width:650px;transform-origin:left center;}}
  .xcard.rea .xtext{{line-height:1.4;}}
  .xhead{{display:flex;align-items:center;gap:16px;margin-bottom:14px;}}
  .xav{{width:64px;height:64px;border-radius:50%;object-fit:cover;flex:none;}}
  .xav.anon{{display:flex;align-items:center;justify-content:center;color:#fff;font-family:"JPHeavy";font-size:30px;}}
  .xnm{{flex:1;min-width:0;}}
  .xname{{font-family:"JPHeavy";font-size:31px;line-height:1.1;display:flex;align-items:center;gap:8px;}}
  .vbadge{{display:inline-flex;align-items:center;justify-content:center;width:25px;height:25px;border-radius:50%;background:#1d9bf0;color:#fff;font-size:15px;}}
  .xhandle{{font-size:25px;color:#536471;}}
  .xlogo{{font-size:33px;color:#0f1419;flex:none;}}
  .xtext{{font-family:"JPMed";font-size:36px;line-height:1.5;color:#0f1419;word-break:break-word;}}
  .xstats{{display:flex;gap:24px;margin-top:16px;padding-top:13px;border-top:1px solid #eaeef0;font-size:24px;color:#536471;}}
  .xstats .st b{{color:#0f1419;}}
  .subt{{position:absolute;z-index:350;left:0;right:0;bottom:112px;text-align:center;opacity:0;
        font-family:"JPHeavy";font-size:45px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;padding:0 90px;}}
</style>
</head>
<body>
  <div id="root" data-composition-id="wk-news" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
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
      window.__timelines['wk-news'] = tl;
    </script>
  </div>
</body>
</html>
"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} bg={len(bg_divs)} cards={len(card_divs)} subs={len(sub_divs)}")
