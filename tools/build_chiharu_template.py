"""相本宗輝 完全解説 index.html 生成(1920x1080・窓対応・評伝型)。
   背景=事前結合した1本を分割したパート(<video>は数個)。前景=冒頭タイトル／章カード／章の常時コーナータグ(日付+対戦カード)／
   発言カード・採点テーブル／DOM字幕(キュー同期・≤2行)／出典ラベル／透かし。VISUAL_ONLYでレンダー→finalizeで音声mux。
   env: HF_WIN_START/HF_WIN_END/HF_VISUAL_ONLY/HF_OUTNAME。"""
from __future__ import annotations
import json, html, os, re as _re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "chiharu"
TPL = ROOT / "hyperframes" / "templates" / "chiharu"
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
# 骨格オーバーレイ映像は出典を映像内に焼き込み済み＝label が空のビートはラベルを出さない
SRC = {x["beat"]: ("出典: " + x["label"] if x["label"] else "") for x in _SEG}

# ---- 背景の時間帯(出典ラベル用) = bg_segments.json の順序 ----
BG = []
for i, x in enumerate(_SEG):
    t0 = x["t0"]
    t1 = _SEG[i + 1]["t0"] + 0.08 if i + 1 < len(_SEG) else COMP
    BG.append((round(t0, 3), round(t1, 3), x["beat"], ("出典: " + x["label"]) if x["label"] else ""))

# ---- 冒頭タイトル ----
# ---- 冒頭タイトル ----
TITLE = [("49秒で終わった、", "w", 0.92), ("路地裏の王者", "y", 1.58)]
# h7（飛車角の入場）〜h8 の上。人物の顔を避けた引きの区間に出す
TITLE_T0, TITLE_T1 = 40.5, 48.0

# ---- 発言カード / テーブル ----
# (beat, kind, title, body, meta)  kind: media=発言カード / table=テーブル
CARDS_SPEC = [
    # ---- 第1章 必然 ----
    ("n13", "media", "千春",
     "小学校入ったぐらいから、もう格闘技で飯食ってくんだろうなって思ってたんですよね。その時まだ柔道すらもやってなかったんすけど。",
     "生まれ育った団地で（SOUL JAPAN／極め道 #40）"),
    ("n20", "media", "千春",
     "偶然じゃないっすね。自分の中では偶然じゃなくて必然だなって、全然思ってます。",
     "SOUL JAPAN／極め道 #40"),

    # ---- 第2章 転校 ----
    ("t9", "media", "千春",
     "ランバーさんのことも知らなくて、タイの先生が教えてるジムなんだなぁくらいにしか思ってなかったです。",
     "中学2年で入ったムエタイジムについて（MMAPLANET）"),

    # ---- 第3章 路地裏 ----
    ("r12", "media", "千春",
     "相手がその時すごい強く感じて。相手のジムどこだろうと思ったら、蕨のジムだったんで。そこに入ったのがきっかけだったんすけど、今の所属のジムなんすけど。",
     "地下格闘技の初戦で負けた相手について（SOUL JAPAN／極め道 #40）"),

    # ---- 第4章 喧嘩會 ----
    ("k6", "media", "千春",
     "俺らこんな行けてるやつの集まりだぞってのは、みんなに知ってもらいたくて。王子、僕らのチームを盛り上げるためにも派手に行こうと思って。",
     "王子喧嘩會を作った理由（SOUL JAPAN／極め道 #40）"),

    # ---- 第5章 飛車角 ----
    ("f10", "media", "千春",
     "一番強いやつやらしてくれって。タイトルマッチはすぐ無理だろうと思ったんで、次に一番強いやつって言ったら、当時のチャンピオンとやらないかって来たんで、即答で、やりますって。",
     "飛車角の初戦でKO勝ちした直後（SOUL JAPAN／極め道 #40）"),
    ("f24", "media", "千春",
     "チャンピオンになった時にやっぱ刺激が足りなくて。俺、こいつに勝っちゃったらもう敵ないじゃんって、ふとその時思ったんすよね。",
     "王座獲得直後にプロ転向を決めた理由（SOUL JAPAN／極め道 #40）"),

    # ---- 第6章 四十九秒 ----
    ("d10", "media", "BoutReview 試合レポート",
     "1R、岩松がタックルから抱えて倒すが、千春が反則となる後頭部への打撃を連打し一時中断する。ドクターチェックの結果、岩松はストップがかかり反則勝ちとなった。岩松はセコンドに肩を抱えられて退場した。",
     "Fighting NEXUS vol.32（2023年8月20日・後楽園ホール）"),

    # ---- 第7章 連勝 ----
    ("w16", "media", "千春",
     "プロ5戦したっすけど、全然僕の実力の20%ぐらいしか見せてないつもりなんで。",
     "プロ5戦時点（SOUL JAPAN／極め道 #40）"),

    # ---- 第8章 戦い方 ----
    ("s12", "media", "千春",
     "日本人で組み際とか首相撲からのヒジ・ヒザをちゃんとやっている選手って少ないじゃないですか。日本人はタックルに入ってテイクダウンして、コツコツ削って一本勝ちみたいな戦い方が定着していて、自分はその隙を突くというか。",
     "自身のスタイルについて（MMAPLANET）"),
    ("s17", "table", "RIZIN.55 フェザー級 5分3R",
     [("戦績", "7勝1敗", "千春"),
      ("年齢", "25歳", "2001年6月3日生"),
      ("身長", "182cm", "東京都北区王子"),
      ("所属", "FREEDOM@OZ", "柔道・ムエタイ"),
      ("タイトル", "第3代 Fighting NEXUS フェザー級王者", "第2代 飛車角ライト級王者")],
     "RIZIN公式／Fighting NEXUS公式"),

    # ---- 第9章 兄弟 ----
    ("b19", "media", "アポロ中山",
     "千春、3日前にインフルエンザ？ バイトじゃねーんだよ。俺の地元だったらヤキなんだよ。ヤキいれるのが観たいか、ベルト獲るのが観たいか、みんな決めてください。",
     "千春の欠場を受けてのマイク（ゴング格闘技）"),
    ("b27", "media", "千春",
     "僕の弟・賢民がセコンドについてくれて、僕ら兄弟にとって挑戦する年で、すごいキツいこともいろいろあって。ここまで来れたのは自分ひとりの力じゃないんで。",
     "アポロ中山戦の勝利者マイク（2025年12月21日）"),

    # ---- 第10章 王座 ----
    ("c12", "media", "高須将大",
     "僕はもともと余命3カ月の肝臓がんでした。ステージ4Bって宣告されたし、肺にも転移したし、再発も何回もしました。その時はもう未来のことなんて、全然考えられなかったです。",
     "王座決定戦の計量2日前の投稿（ゴング格闘技）"),
    ("c13", "media", "高須将大",
     "僕がベルトを巻くことが出来たら、同じ病気の子だったり、壁にぶち当たってる人に少しでも勇気を与えられるんじゃないかなって思ってるんで。",
     "王座決定戦の計量2日前の投稿（ゴング格闘技）"),
    ("c18", "media", "千春",
     "相手のことを悪く言うつもりは全然ないんですけど、自分とはレベルが違うと思っているし、自分も必死こいて人生かけて格闘技をやっているんで、ここは譲れない。",
     "王座決定戦の試合前（MMAPLANET）"),
    ("c40", "media", "千春",
     "弟が前回ライト級のチャンピオンになって、自分もあとを追う形になっちゃって、正直プレッシャーは強かったですね。でもこの2カ月、格闘技と対話できて。格闘技と対話している自分が一番好きだし、格闘技最高だなって思います。",
     "第3代フェザー級王座決定戦の勝利者マイク（2026年7月3日）"),
    ("c45", "media", "榊原信行（RIZIN CEO）",
     "千春、最高です。NEXUSを代表してRIZINで待っています。日本を、世界を、ぜひ、いわしてください。",
     "王座決定戦の直後にケージイン（2026年7月3日）"),
    ("c50", "media", "榊原信行（RIZIN CEO）",
     "ハングリーで、ギラギラした千春選手には以前から注目してました。RIZINの舞台でも拳一つで成り上がっていく千春の生き様を見せつけて欲しいです。",
     "試合当夜のX投稿"),

    # ---- 第11章 番人 ----
    ("g15", "media", "山本空良",
     "『試合中に絶対この人、笑うんだろうな』って。まあ案の定、笑われちゃって、自分が情けねえなって思っちゃいました。また1からやり直した方がいいんじゃないかな？と思っています。",
     "鈴木博昭に敗れた直後（RIZIN LANDMARK 11・2025年6月14日）"),
    ("g22", "media", "鈴木博昭",
     "もうここ数戦ずっと、2000年以降生まれの若い選手が相手なんですけど、今回も他団体の現役王者の千春選手ということで、また活きが良さそうなんで。",
     "RIZIN.55 追加対戦カード発表記者会見（2026年9月25日）"),
    ("g27", "table", "RIZIN.55 対戦データ",
     [("鈴木博昭", "41歳 / 167cm", "13戦7勝6敗・全てRIZIN"),
      ("千春", "25歳 / 182cm", "8戦7勝1敗・NEXUS王者"),
      ("身長差", "15cm", "千春が上回る"),
      ("年齢差", "16歳", "鈴木が上回る"),
      ("鈴木の直近", "3連勝中", "山本空良・ファン・イェーロウ・宮川日向")],
     "RIZIN公式"),
    ("g33", "media", "千春",
     "今回サッカーボールキック、踏みつけありなので、自分の喧嘩の強いところを見せられるかなと思います。",
     "RIZIN.55 追加対戦カード発表記者会見（2026年9月25日）"),
    ("g42", "media", "榊原信行（RIZIN CEO）",
     "Fighting NEXUSをすごく愛しているし、その中での戦いを通じてキャリアアップしてきている姿を僕らも見ていて、しっかりベースがある。ぽっと出じゃない。",
     "千春について（RIZIN.55 記者会見）"),

    # ---- 第12章 証明 ----
    ("z11", "media", "千春",
     "今この状況、多分ガキの頃の自分にタイムスリップして「こうなってるよ」って言っても、多分その頃の自分は全然びっくりしないと思います。",
     "23歳・生まれ育った団地で（SOUL JAPAN／極め道 #40）"),
    ("z15", "media", "千春",
     "俺が千春です。もっとね、有名になって、みんなに俺の強さ証明する時が来ると思うんで、その時まで楽しみにしてください。",
     "プロ5戦時点のカメラに向けて（SOUL JAPAN／極め道 #40）"),
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
    head, card = (c.get("sub") or c["name"]), (c.get("sub2") or "")
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
  .srclab{{position:absolute;z-index:340;left:40px;bottom:30px;font-family:"JPMed";font-size:23px;color:#eaeaea;opacity:0;
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
  .subt{{position:absolute;z-index:350;left:0;right:0;bottom:110px;text-align:center;opacity:0;
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
