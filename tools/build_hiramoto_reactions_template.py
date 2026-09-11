"""超RIZIN.5 反応まとめ(3試合) index.html 生成(1920x1080・窓対応)。
   背景=ナレ一致(各ビート専用bgvid)。前景=発言カード(実名は選手・解説者・報道のみ)。
   章タグ・DOM字幕(≤2行・JP)・出典ラベル・透かし。VISUAL_ONLYでレンダー→finalizeで音声mux。
   env: HF_WIN_START/HF_WIN_END/HF_VISUAL_ONLY/HF_OUTNAME。"""
from __future__ import annotations
import json, html, os, re as _re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "hiramoto_reactions"
TPL = ROOT / "hyperframes" / "templates" / "hiramoto-reactions"
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
DISP = {
    "スーパーライジンファイブ": "超RIZIN.5", "ライジン": "RIZIN", "ケーオー": "KO",
    "ひらもとれん": "平本蓮", "ひらもと": "平本",
    "カルシャガダウトベック": "カルシャガ・ダウトベック", "ダウトベック": "ダウトベック",
    "いしわたりしんたろう": "石渡伸太郎", "いしわたり": "石渡",
    "おうぎくぼひろまさ": "扇久保博正", "おうぎくぼ": "扇久保",
    "ストラッサーきいち": "ストラッサー起一", "すずきちひろ": "鈴木千裕", "すずき": "鈴木",
    "まえだあきら": "前田日明", "さかきばらのぶゆき": "榊原信行",
    "かわじりたつや": "川尻達也", "かわじり": "川尻", "ヒカキン": "ヒカキン",
    "ライジンフィフティー": "RIZIN.50", "ランドマークボリュームツー": "RIZIN LANDMARK vol.2",
    "ディープ": "DEEP", "リングス": "RINGS", "しゅうと": "修斗",
    "はんていにたいいち": "判定2-1", "にたいいち": "2-1",
    "にじゅうきゅうたいにじゅうはち": "29-28", "にじゅうきゅうたいにじゅうなな": "29-27",
    "にじゅうはちたいにじゅうはち": "28-28", "じゅうたいはち": "10-8", "じゅうたいきゅう": "10-9",
    "いちラウンド": "1R", "にラウンド": "2R", "さんラウンド": "3R",
    "かたひざ": "片膝", "てきかくに": "的確に", "ひとり": "1人", "ふたり": "2人",
}
def disp(t):
    for k in sorted(DISP, key=len, reverse=True): t = t.replace(k, DISP[k])
    return t

# 出典ラベル
S_KAI_YT = "出典: 朝倉海 (YouTube)"
S_KAI_SNS = "出典: 朝倉海 (SNS)"
S_HORI = "出典: 堀口恭司 (YouTube)"
S_UFC = "出典: UFC (試合映像)"
S_PEX = "出典: イメージ映像 (Pexels)"

# beat_id -> 出典ラベル。bg_segments.json をそのまま使い、素材と表示のズレを防ぐ。
_SEG = json.load(open(TPL / "assets" / "bg_segments.json", encoding="utf-8"))
SRC = {x["beat"]: "出典: " + x["label"] for x in _SEG}

# Ken Burns motion(縦/スクエア=blur-contain背景はズーム控えめ)
MO = {"c1a": "kb_zin", "c1b": "kb_zin", "c1c": "kb_zin", "c1d": "kb_zin", "c1e": "kb_zin", "c1f": "kb_zin", "c1g": "kb_zin", "c1h": "kb_zin", "c1i": "kb_zin", "c1j": "kb_zin", "c1k": "kb_zin", "c1l": "kb_zin", "c1q": "kb_zin", "c3a": "kb_zin", "c3c": "kb_zin", "c3d": "kb_zin", "c3e": "kb_zin", "e2": "kb_zin"}

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
    "ch1": ("何が起きた試合だったのか", "1Rの被弾、2R・3Rの巻き返し"),
    "ch2": ("納得できない、という声", "驚きと反発"),
    "ch3": ("判定を説明する声", "ラウンドマストという基準"),
    "close": ("まとめ", "分かれ目は1Rの見方だった"),
}

# ---- カード: 海外メディア(cap) / 英語コメント(com) ----
# (beat, kind, title, body_en, meta)
CARDS_SPEC = [
    # ★実名で出すのは選手・元選手・解説者・団体代表・当事者のみ。一般視聴者のアカウントは出さない。
    ("c2c", "media", "ジョビン", "え、マジで? 今までの判定で1番びっくりしたかも。", "元DEEPフェザー級王者／実況配信"),
    ("c2d", "media", "ジョビン", "平本自身が負けた顔してたもん。3ラウンド終わった時点で。これはまずいんじゃない? さすがに。", "元DEEPフェザー級王者／実況配信"),
    ("c2g", "media", "ストラッサー起一", "嘘やろ。これはダウトベックがかわいそうやって。これは俺ちょっと納得できへんわ。", "現役MMAファイター／全試合生解説"),
    ("c2h", "media", "ストラッサー起一", "でもこの採点に関しては平本蓮は悪くないよ。ジャッジがやったわけやから、平本蓮を攻めるのは絶対違う。", "現役MMAファイター／全試合生解説"),
    ("c2i", "media", "前田日明", "平本君の判定はちょっとなあ。あの展開で2-1はちょっと辛いなというのが正直な感想。", "元RINGS代表"),
    ("c3c", "media", "榊原信行", "ディフェンシブなエスケープ的なテイクダウンとかって、全くポイントにならないですよね。", "RIZIN CEO／大会後会見"),
    ("c3d", "media", "榊原信行", "1ラウンド目で平本が片膝ついてますけど、ダウンは取られてないんだろうな。だから10-8にはならなかったんじゃないかな。", "RIZIN CEO／大会後会見"),
    ("c3f", "media", "平本 蓮", "KOするつもりだったんで、ちょっと悔しくて泣いちゃいました。", "RIZIN公式 試合後インタビューより"),
    ("c3g", "media", "平本 蓮", "2・3は見返しても取れてたなと思う。RIZINはトータルじゃなくてラウンドマストなんで。", "RIZIN公式 試合後インタビューより"),
    ("c3i", "media", "セコンド（控室にて）", "ジャッジとしては1ラウンド10-8を1人がつけた。あとは10-9で向こう。で、2と3が10-9で（平本）。", "RIZIN公式【勝者と敗者】より"),
    ("c3k", "media", "鈴木千裕", "別に俺はKOするから関係ねぇんだよ。もうね、他人に自分の勝敗を任せた時点で死んでんだよ。", "RIZIN現役／ダウトベック・平本蓮と対戦経験"),
    ("c3k2", "media", "鈴木千裕", "それはもうレフェリーが決めることだからしょうがないじゃん。", "RIZIN現役／ダウトベック・平本蓮と対戦経験"),
    ("c3k3", "media", "鈴木千裕", "多少なりの抗議はあると思うけど、判定まで行く前に処理しなきゃいけないじゃん。", "RIZIN現役／ダウトベック・平本蓮と対戦経験"),
    ("c3m", "media", "扇久保博正", "何発クリーンヒットしても立ち続けた平本蓮選手の打たれ強さに驚愕しました。タックルを取られた後の立つ技術も素晴らしい。", "RIZIN フライ級"),
    ("c3o", "media", "石渡伸太郎", "冷静に考えてみると平本選手の勝ち。分かれ目は1ラウンドを10-8と見るか10-9と見るかなんですよ。", "元修斗世界王者"),
    ("c3p", "media", "石渡伸太郎", "ダウンはしてないけども、KO負け寸前じゃんと評価すれば10-8も分かる。だから両者勝ちでした。", "元修斗世界王者"),
    ("c3r", "media", "川尻達也", "僕は1ラウンド目10-8で、2・3が平本選手。28-28のドローで、そこからダメージ差でダウトベックかなと解説中は言ってたんですけど。", "元DREAM/RIZIN／実況席で解説"),
    ("c3t", "media", "川尻達也", "完全に効いたのは1発目の左だけで、あとはしっかり打ち返してた。確かにこれ10-8はつかないかもしれない。", "元DREAM/RIZIN／試合を見返して"),
    ("c3u", "media", "川尻達也", "1ラウンドが10-9でダウトベックであるならば、2・3が平本の10-9、10-9で29-28は全然あり得るし、正当な評価かもな。", "元DREAM/RIZIN／試合を見返して"),
    ("c3v", "media", "川尻達也", "俺とか解説実況がちょっと寄せられちゃって、1ラウンド目の左フックのイメージと最後のパウンドのイメージで。", "元DREAM/RIZIN／試合を見返して"),
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
        if cut >= len(text) or cut <= 0:
            cut = max(1, min(len(text) - 1, target))
        # ★スナップで行が maxw を超えたら、素直に target で切り直す（幅の上限を必ず守る）
        if zwidth(text[:cut]) > maxw or zwidth(text[cut:]) > maxw:
            c2 = max(1, min(len(text) - 1, target))
            while c2 > 1 and zwidth(text[:c2]) > maxw:
                c2 -= 1
            if zwidth(text[:c2]) <= maxw and zwidth(text[c2:]) <= maxw:
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
    return cues or [text]
def sub_lines(text, maxw=23.0):
    if zwidth(text) <= maxw: return [text]
    w = wrap_two(text, maxw)
    return [w[0], w[1]] if w else [text]

# ---- 背景 DOM/TL ----
# ★38ビート＝<video>は38個。Chromeの同時メディア要素の上限(目安40)に収まるのでビート別のまま。
#   これを超えるエピソードは concat_*_bg.py で1本へ連結してから分割する（反応まとめ参照）。
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
    if srcl and (min(t1, W1) - max(t0, W0)) > 0.6:
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
  <div id="root" data-composition-id="hiramoto-reactions" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
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
      window.__timelines['hiramoto-reactions'] = tl;
    </script>
  </div>
</body>
</html>
"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} bg={len(bg_divs)} cards={len(card_divs)} subs={len(sub_divs)}")
