"""超RIZIN.5 反応まとめ(3試合) index.html 生成(1920x1080・窓対応)。
   背景=ナレ一致(各ビート専用bgvid)。前景=発言カード(実名は選手・解説者・報道のみ)。
   章タグ・DOM字幕(≤2行・JP)・出典ラベル・透かし。VISUAL_ONLYでレンダー→finalizeで音声mux。
   env: HF_WIN_START/HF_WIN_END/HF_VISUAL_ONLY/HF_OUTNAME。"""
from __future__ import annotations
import json, html, os, re as _re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "lm16_yosou"
TPL = ROOT / "hyperframes" / "templates" / "lm16-yosou"
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
    # 読みかな → 正式表記（長いキーを先に置換する）
    "ライジンランドマークじゅうろく": "RIZIN LANDMARK 16", "ライジン": "RIZIN",
    "ほりえよしのり": "堀江圭功", "ほりえ": "堀江",
    "うさみしょうパトリック": "宇佐美正パトリック", "うさみ": "宇佐美",
    "ビクターコレスニック": "ビクター・コレスニック", "コレスニック": "コレスニック",
    "まつしまこよみ": "松嶋こよみ", "まつしま": "松嶋",
    "ライアンカファロ": "ライアン・カファロ", "カファロ": "カファロ",
    "やすいひゅうま": "安井飛馬", "やすい": "安井",
    "ケイトロータス": "ケイト・ロータス", "ノエル": "NOEL",
    "あきもときょうま": "秋元強真", "かねはらまさのり": "金原正徳",
    "おうぎくぼひろまさ": "扇久保博正", "あらいすぐる": "新居すぐる",
    "あおきしんや": "青木真也", "いしわたりしんたろう": "石渡伸太郎",
    "さいとうゆたか": "斎藤裕", "やちゆうすけ": "矢地祐介",
    "かわじりたつや": "川尻達也", "ささはらけいいち": "笹原圭一",
    "かしむらじんのすけ": "鹿志村仁之介", "かしむらせん": "鹿志村戦", "にしかわやまと": "西川大和",
    "ほそかわいっさ": "細川一颯", "さいかヤンボ": "雑賀“ヤン坊”達也",
    "パトリッキーピットブル": "パトリッキー・ピットブル",
    "シェイドゥラエフ": "シェイドゥラエフ", "たけだこうじ": "武田光司",
    "きしもとあつし": "岸本篤史", "たかぎりょう": "高木凌",
    "おおしまさおり": "大島沙緒里", "シンユリ": "シン・ユリ", "イボミ": "イ・ボミ",
    "レナ": "RENA", "海咲イルカ": "海咲イルカ",
    "させぼ": "佐世保", "ハピネスアリーナ": "HAPPINESS ARENA",
    # 数字・単位
    "じゅうがつみっか": "10月3日", "はちがつ": "8月", "八月": "8月",
    "だいななしあい": "第7試合", "だいはちしあい": "第8試合",
    "だいきゅうしあい": "第9試合", "だいじゅっしあい": "第10試合",
    "よんじゅうきゅうキロ": "49kg", "ろくじゅうろくキロ": "66kg", "ななじゅういちキロ": "71kg",
    "いちラウンド": "1R", "にラウンド": "2R", "さんラウンド": "3R",
    "さんじゅうさんびょう": "33秒", "ななたいさん": "7対3",
    "にじゅうはっさい": "28歳", "じゅうはっさい": "18歳", "じゅうにさい": "12歳",
    "にじゅうにさい": "22歳", "にじゅうごさい": "25歳", "にじゅうろくさい": "26歳",
    "ごさいから": "5歳から",
    "さんじゅっさい": "30歳", "さんじゅういっさい": "31歳",
    "さんじゅうさんさい": "33歳", "さんじゅうろくさい": "36歳",
    "中学いちねん": "中学1年", "高校ろっかん": "高校6冠",
    "いちまいもにまいも": "1枚も2枚も", "さんにん": "3人", "ふたり": "2人", "ひとり": "1人",
    "よんしあい": "4試合", "じゅうだい": "10代",
    "いっぱつ": "一発", "ケーオー": "KO", "ティーケーオー": "TKO",
    "エムエムエー": "MMA", "シーエフエフシー": "CFFC", "エスエヌエス": "SNS", "ワン": "ONE",
    "ディープ": "DEEP", "ブレイキングダウン": "BreakingDown",
    "腕ひしぎじゅうじがため": "腕ひしぎ十字固め",
    "れんぱい": "連敗", "ぜんせん": "前戦",
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
MO = {}

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
# ---- 章タグは timings.json の chapters(title/sub) をそのまま使う ----

# ---- カード: 海外メディア(cap) / 英語コメント(com) ----
# (beat, kind, title, body_en, meta)
# ---- 予想者カード / 集計カード ----
# anchor = ビート本文の一部（ビートIDの直書きを避け、台本を直しても壊れないようにする）
def beat_at(sub: str):
    n = sub.replace("、", "").replace("。", "").replace(" ", "")
    for b in BEATS:
        if n in b["text"].replace("、", "").replace("。", "").replace(" ", ""):
            return b["id"]
    raise SystemExit(f"BEAT NOT FOUND: {sub}")

KATE, NOEL_C = "#ff7ab8", "#5ad1ff"
CAF, YAS = "#ffd34d", "#6ee36e"
KOL, MAT = "#ff6a4d", "#4e9bff"
HOR, USA = "#4e9bff", "#ff6a4d"

# (anchor, kind, 名前, 予想ラベル, 色, 引用文, 肩書/出典)
CARDS_SPEC = [
    # ===== 第7試合 =====
    ("おうぎくぼひろまさ選手は、ケイトロータス選手の判定勝ちを予想します", "pred", "扇久保 博正", "ケイト・ロータス 判定",
     KATE, "NOELが金網に押し込んでもテイクできずに膝、というのをイメージしてます。ケイト・ロータス選手の判定勝ちかな。", "RIZIN フライ級／YouTube「おぎちゃんねる」"),
    ("あらいすぐる選手もケイトロータス選手です", "pred", "新居 すぐる", "ケイト・ロータス 判定",
     KATE, "ケイト選手が打撃の圧をかけて、最初はNOEL選手もチャレンジしていくけど、3ラウンドトータルでケイト選手が打撃でつけるんじゃないかな。", "RIZIN フェザー級／YouTube「新居すぐるチャンネル」"),
    ("やちゆうすけ選手は、立ち技のケイトロータス選手と", "pred", "矢地 祐介", "ケイト・ロータス 寄り",
     KATE, "立ち技のケイト選手対、組み系のNOEL選手。分かりやすい構図ですよね。立ち技が上手なぶん、ケイト選手が有利に運ぶ気はするけど。", "RIZIN ライト級／YouTube「矢地祐介」"),
    ("ひとりだけノエル選手を推したのが、あきもときょうま選手です", "pred", "秋元 強真", "NOEL 判定",
     NOEL_C, "NOEL選手で。応援も込みですけど、10代であそこまでやれるのは本当にすごいと思うので。", "RIZIN バンタム級／YouTube「秋元強真」"),
    ("さらに、ノエル選手が打撃で仕掛けたとき", "pred", "笹原 圭一", "ぶつかり合いになる",
     "#ffd76a", "NOEL選手が打撃で仕掛けたときに、ケイトがその勝負を避けるとは僕は思えない。上等だ、殴ったろうってなると思う。", "RIZIN統括本部長／YouTube「川尻達也のじりラジオ」"),
    ("予想は、ケイトロータス選手にさんにん、ノエル選手にひとり", "tally", "ケイト・ロータス", "3",
     "NOEL", "1", "第7試合 予想集計"),

    # ===== 第8試合 =====
    ("おうぎくぼひろまさ選手は、ライアンカファロ選手の判定勝ち", "pred", "扇久保 博正", "カファロ 判定",
     CAF, "要所要所で打撃を当てそうな、テイクダウンはされるけど、という展開になりそうな気がします。", "RIZIN フライ級／YouTube「おぎちゃんねる」"),
    ("やすいひゅうま選手は、柔道を総合に生かすのがフェザー級で一番うまい", "pred", "新居 すぐる", "カファロ 圧勝",
     CAF, "安井選手はテイクダウンまではできるかもしれない。でも、その他すべてがライアン・カファロ選手のほうが何個か上だと思う。", "RIZIN フェザー級／YouTube「新居すぐるチャンネル」"),
    ("ふたりともMMAが綺麗じゃないタイプで", "pred", "金原 正徳", "極上のドロドロMMA",
     "#ffd76a", "二人ともMMAが汚いんですよ。ごちゃごちゃにできるんで、極上のドロドロのMMAが見られるんじゃないかと。", "元修斗世界王者／YouTube「金ちゃんTV」"),
    ("いちラウンドの腕ひしぎじゅうじがため", "pred", "秋元 強真", "安井 1R 腕十字",
     YAS, "安井選手が1ラウンドで腕十字。組めれば決められると思う。ただ、そこが遅れたら厳しいと思います。", "RIZIN バンタム級／YouTube「秋元強真」"),
    ("かしむらじんのすけ選手に一本を取らせなかった組みの強さ", "pred", "笹原 圭一", "安井に大チャンス",
     "#ffd76a", "安井くんが1本とか取ってくると、一気に、やっぱり安井強いじゃんってなると思いますね。大チャンスだと思います。", "RIZIN統括本部長／YouTube「川尻達也のじりラジオ」"),
    ("予想はライアンカファロ選手にさんにん、やすいひゅうま選手にひとり", "tally", "ライアン・カファロ", "3",
     "安井 飛馬", "1", "第8試合 予想集計"),

    # ===== 第9試合 =====
    ("まつしまこよみ選手は、能力的にはまだ日本人トップ", "pred", "青木 真也", "松嶋 序盤フィニッシュ",
     MAT, "松嶋こよみは心身ともに整えば、ビクター・コレスニックは相手じゃない。そのぐらいの能力を持ってます。", "RIZIN ライト級／YouTube「青木真也」"),
    ("おうぎくぼひろまさ選手も、まつしまこよみ選手の判定勝ち", "pred", "扇久保 博正", "松嶋 判定",
     MAT, "松嶋選手の判定勝ちかな。どこかのタイミングで、蹴りとかでダウンを取りそうな気がしますね。", "RIZIN フライ級／YouTube「おぎちゃんねる」"),
    ("まつしまこよみ選手の本当の強さは、まだ日本で出せていない", "pred", "新居 すぐる", "松嶋 判定",
     MAT, "松嶋の良さが本当は日本でまだ出せてないと思う。立ちだろうが寝技だろうがコレスを倒せる強さ。判定で松嶋が勝つと思います。", "RIZIN フェザー級／YouTube「新居すぐるチャンネル」"),
    ("にラウンドのケーオー。右ストレートで仕留める", "pred", "秋元 強真", "コレスニック 2R KO",
     KOL, "コレスニック選手の2ラウンドKO。右ストレートで。松嶋選手は2ラウンドで疲れちゃう気がします。", "RIZIN バンタム級／YouTube「秋元強真」"),
    ("さいとうゆたか選手も、打撃の勝負になるならビクターコレスニック選手が有利", "pred", "斎藤 裕", "打撃ならコレスニック",
     KOL, "正面から打撃の交換をすると、ビクターの良さが生きる気がする。松嶋選手は組みを混ぜて攻めた方が勝ちに近づくのかな。", "元RIZINフェザー級王者／YouTube「斎藤裕」"),
    ("やちゆうすけ選手は、ビクターコレスニック選手が打撃で入ってテイクダウンを奪い", "pred", "矢地 祐介", "コレスニックのペース",
     KOL, "コレスが打撃を打ってテイクして、パウンド打って削ってみたいな試合になりそう。松嶋選手の三日月あたりがキーかな。", "RIZIN ライト級／YouTube「矢地祐介」"),
    ("まつしまこよみ選手が体力の配分をできるかどうか", "pred", "金原 正徳", "明言せず",
     "#d8d8d8", "松嶋が体力のペース配分をちゃんとできるかどうか。超つまんない試合になるか、超楽しいか、どっちかだと思います。", "元修斗世界王者／YouTube「金ちゃんTV」"),
    ("ささはらけいいちさんによると、ビクターコレスニック選手は今回が契約最後", "pred", "笹原 圭一", "お互い後がない",
     "#ffd76a", "コレスニックは今回が現契約の最後。松嶋選手もここで負けたら連敗で、なかなかチャンスが巡ってこなくなる。", "RIZIN統括本部長／YouTube「川尻達也のじりラジオ」"),
    ("あおきしんや選手は、この試合をサバイバルマッチと呼びました", "tally", "松嶋 こよみ", "3",
     "コレスニック", "3", "第9試合 予想集計（評価は真っ二つ）"),

    # ===== メインイベント =====
    ("うさみしょうパトリック選手は、アマチュアボクシングの怪物中の怪物", "pred", "石渡 伸太郎", "打ち合えば宇佐美",
     USA, "宇佐美選手はアマチュアボクシングの怪物中の怪物。懐に入られたら、堀江選手といえどダウンします。", "元RIZINバンタム級王者／YouTube「石渡伸太郎」"),
    ("それでも、ほりえよしのり選手には選択肢の多さとフィジカルがある", "pred", "石渡 伸太郎", "確率は堀江",
     HOR, "確率的にどっちが高く起こるかと言うと、やっぱり選択肢が多い堀江選手かな。ただ、触れてみないと分からない。", "元RIZINバンタム級王者／YouTube「石渡伸太郎」"),
    ("あおきしんや選手は、ななたいさんでほりえよしのり選手の有利", "pred", "青木 真也", "7対3で堀江",
     HOR, "今回は俺の予想では7対3で堀江有利。でも、パトリックが一発当てる可能性はマジである。", "RIZIN ライト級／YouTube「青木真也」"),
    ("ただし、うさみしょうパトリック選手のパンチはいっぱつで終わらせるレベル", "pred", "青木 真也", "一発で終わる試合",
     USA, "一発で瀕死、一発で死ぬレベルの打撃を与えると思ってます。そのぐらいリスキーな試合だなと。", "RIZIN ライト級／YouTube「青木真也」"),
    ("おうぎくぼひろまさ選手は、ほりえよしのり選手の判定勝ち", "pred", "扇久保 博正", "堀江 判定",
     HOR, "堀江選手の判定勝ちかな。テイクダウンされて立てるかどうかが、やっぱりキーになってくるんじゃないですかね。", "RIZIN フライ級／YouTube「おぎちゃんねる」"),
    ("うさみしょうパトリック選手はいいパンチを当ててくるけれど", "pred", "新居 すぐる", "堀江 判定",
     HOR, "パトリック君はいいのを当てるけど、何回か当てても堀江君はそこで引かず自分の戦い方をして勝つんじゃないかな。", "RIZIN フェザー級／YouTube「新居すぐるチャンネル」"),
    ("かねはらまさのりさんも、経験値を含めたトータルバランスで", "pred", "金原 正徳", "堀江が1枚も2枚も上",
     HOR, "経験値も含めてMMAのトータルバランスで考えたら、堀江の方が1枚も2枚も上手なのかなというのが、パッと見た時の感想。", "元修斗世界王者／YouTube「金ちゃんTV」"),
    ("いちラウンドからにラウンド前半で決まるなら", "pred", "秋元 強真", "時間で分かれる",
     "#d8d8d8", "1ラウンドから2ラウンド前半なら宇佐美選手のKO。2ラウンド中盤以降から判定なら堀江選手。", "RIZIN バンタム級／YouTube「秋元強真」"),
    ("パンチ勝負に行けば、ほりえよしのり選手は分が悪いかもしれない", "pred", "斎藤 裕", "組みを混ぜるべき",
     "#ffd76a", "パンチ勝負に行ったら堀江選手は部が悪いかもしれない。しっかり組みを混ぜた上で、自分もパンチを振っていく方がいい。", "元RIZINフェザー級王者／YouTube「斎藤裕」"),
    ("やちゆうすけ選手は、選択肢が多いのはほりえよしのり選手だとしたうえで", "pred", "矢地 祐介", "選択肢は堀江",
     HOR, "打撃で付き合うこともできるし、組みに行ってドミネートすることもできる。選択肢が多いのは堀江選手なのかなと。", "RIZIN ライト級／YouTube「矢地祐介」"),
    ("ライト級では海外の選手も含めて一番速く", "pred", "川尻 達也", "宇佐美のパンチは最速",
     USA, "パトリック選手はライト級で海外の選手も含めて一番パンチが速いし破壊力がある。パトリッキーの全盛期と同じような感じがする。", "元RIZIN／YouTube「川尻達也のじりラジオ」"),
    ("予想は、ほりえよしのり選手に大きく傾いています", "tally", "堀江 圭功", "5",
     "宇佐美正パトリック", "0", "メインイベント 予想集計（ほかに条件つき・明言なし 4人）"),
]


def card_html(cid, kind, a, b, c, d, meta, cont=False):
    """kind=pred: a=名前 b=予想ラベル c=色 d=引用文 meta=肩書/出典
       kind=tally: a=左の名前 b=左の票 c=右の名前 d=右の票 meta=見出し"""
    op = ' style="opacity:1"' if cont else ''
    if kind == "tally":
        return (f'<div class="tcard" id="{cid}"{op}>'
                f'<div class="ttl">{esc(meta)}</div>'
                f'<div class="trow">'
                f'<div class="tside"><div class="tname">{esc(a)}</div><div class="tnum l">{esc(b)}</div></div>'
                f'<div class="tvs">VS</div>'
                f'<div class="tside"><div class="tname">{esc(c)}</div><div class="tnum r">{esc(d)}</div></div>'
                f'</div><div class="tunit">人が予想</div></div>')
    L = len(d)
    fs = 36 if L <= 60 else 32 if L <= 100 else 28 if L <= 150 else 25
    return (f'<div class="ccard pred" id="{cid}"{op}>'
            f'<div class="phead"><div class="pname">{esc(a)}</div>'
            f'<div class="ppick" style="background:{c}">{esc(b)}</div></div>'
            f'<div class="ctext" style="font-size:{fs}px">{esc(d)}</div>'
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
        # ★カタカナ語・英数字・「ー」「・」の途中で切らない（語中改行の禁止）。
        #   切る位置の前後±12文字で「語の途中でなく、両行が幅内」に収まる最も近い位置を探す。
        KATA = _re.compile(r'[ァ-ヴーｦ-ﾟA-Za-z0-9・]')
        def inside_word(c):
            return 0 < c < len(text) and bool(KATA.match(text[c-1])) and bool(KATA.match(text[c]))
        PUNCT = set("、。，．！？")
        def ok(c):
            # 語中改行を避けるためなら、設計幅(23)より少し広い 27全角（ルール上限）まで許す。
            # ★行頭に句読点を置かない＝切る位置の文字が句読点なら不可。
            lim = min(maxw + 4.5, 27.0)
            return (0 < c < len(text) and not inside_word(c) and text[c] not in PUNCT
                    and zwidth(text[:c]) <= lim and zwidth(text[c:]) <= lim)
        if not ok(cut):
            for d in range(1, 13):
                if ok(cut - d): cut = cut - d; break
                if ok(cut + d): cut = cut + d; break
        # ★幅の上限(27全角=ルール上限)だけは必ず守る。語中で切るしかない時のみ最後の手段として target で切る
        if zwidth(text[:cut]) > 27.0 or zwidth(text[cut:]) > 27.0:
            c2 = max(1, min(len(text) - 1, target))
            while c2 > 1 and zwidth(text[:c2]) > 27.0:
                c2 -= 1
            cut = c2
        while 0 < cut < len(text) - 1 and text[cut] in "、。，．！？":
            cut += 1
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
# ★背景は事前に1本へ連結し、GitHubの100MB制限に収まるよう6分割したものを重ねて流す。
#   ビート別に <video> を並べるとビート数が多い時に Chrome の同時メディア要素の上限に当たり、
#   フレームキャプチャが同じフレームで固まる（80ビートで再現）。連結方式はショートで実績あり。
#   各パートは次パート開始から8秒ぶん余分に持っているので、piece終端まで背景が途切れない。
bg_divs, bg_tws, src_divs = [], [], []
PARTS = json.load(open(TPL / "assets" / "bgvid_full" / "parts.json", encoding="utf-8"))
for k, pt in enumerate(PARTS):
    pt0, pt1 = pt["t0"], pt["t1"]
    if not OV(pt0, pt1):
        continue
    bid = f"bgp{k}"
    ds = max(0.0, T(pt0))                       # 窓内での表示開始
    ms = max(0.0, W0 - pt0)                     # パート内の再生開始位置
    dur = min(pt["media_len"] - ms, (W1 - max(pt0, W0)) + 0.6)   # piece終端まで持たせる
    if dur <= 0.05:
        continue
    bg_divs.append(
        f'<div class="bgseg" id="{bid}" style="z-index:{k + 1};opacity:1">'
        f'<video id="{bid}-v" src="assets/bgvid_full/{pt["file"]}" muted playsinline '
        f'data-layout-allow-overflow data-start="{ds:.2f}" data-duration="{dur:.2f}" '
        f'data-media-start="{ms:.2f}" data-track-index="{10 + k}"></video></div>')
    bg_tws.append(f"tl.set('#{bid}',{{opacity:1}},0);")

# 出典ラベルは連結後も各ビートの時間帯に追従させる
for i, (t0, t1, fn, mo, srcl) in enumerate(BG):
    if not OV(t0, t1) or not srcl:
        continue
    if (min(t1, W1) - max(t0, W0)) <= 0.6:   # 窓端で可視が短い区間は出さない(残留防止)
        continue
    vt0, vt1 = T(t0), T(t1)
    sid = f"src{i}"
    src_divs.append(f'<div class="srclab" id="{sid}">{esc(srcl)}</div>')
    if vt0 + 0.3 < 0:
        bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:1}},{{opacity:1,duration:.01}},0.00);")
    else:
        bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{vt0 + 0.3:.2f});")
    bg_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{vt1 - 0.25:.2f});")

# ---- 章タグ ----
chap_divs, chap_tws, chap_audio = [], [], []
for j, c in enumerate(CHAPS):
    st = c["start"]
    if not OV(st, st + 3.8): continue
    ja, sub = c["title"], c["sub"]; cid = f"chap{j}"
    chap_divs.append(f'<div class="chaptag" id="{cid}"><div class="chnum">{esc(ja)}</div>'
                     f'<div class="chttl">{esc(sub)}</div></div>')
    chap_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,y:40}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.6)'}},{T(st+0.1):.2f});")
    chap_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-26,duration:.4,ease:'power1.in'}},{T(st+3.4):.2f});")
    if not VISUAL_ONLY:
        chap_audio.append(f'<audio id="chs{j}" src="assets/se/chapter.wav" data-start="{T(st+0.1):.2f}" data-track-index="{200+j}" data-volume="0.5"></audio>')

# ---- カード ----
card_divs, card_tws = [], []
for k, (anchor, kind, ca, cb, cc, cd, meta) in enumerate(CARDS_SPEC):
    bid = beat_at(anchor)
    t0 = bs(bid) + 0.2; t1 = be(bid) - 0.15
    if not OV(t0, t1): continue
    cid = f"cc{k}"; cont = T(t0) <= 0.02
    card_divs.append(card_html(cid, kind, ca, cb, cc, cd, meta, cont))
    if cont:
        card_tws.append(f"tl.set('#{cid}',{{opacity:1,x:0,y:0}},0);")
    else:
        card_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,x:60,y:18}},{{opacity:1,x:0,y:0,duration:.5,ease:'back.out(1.5)'}},{T(t0):.2f});")
    card_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-14,duration:.35,ease:'power1.in'}},{T(t1):.2f});")

# ---- 冒頭タイトル（大会名＋主題）----
op_divs, op_tws = [], []
_opb = beat_at("長崎スタジアムシティ ハピネスアリーナ")
_t0, _t1 = bs(_opb) + 0.35, be(_opb) - 0.25
if OV(_t0, _t1):
    op_divs.append('<div class="optitle" id="optl">'
                   '<div class="ev">abc presents RIZIN LANDMARK 16 in NAGASAKI</div>'
                   '<div class="mn">注目4試合 勝敗予想まとめ</div></div>')
    if T(_t0) <= 0.02:
        op_tws.append("tl.fromTo('#optl',{opacity:1},{opacity:1,duration:.01},0);")
    else:
        op_tws.append(f"tl.fromTo('#optl',{{opacity:0}},{{opacity:1,duration:.5}},{T(_t0):.2f});")
    op_tws.append(f"tl.to('#optl',{{opacity:0,duration:.4}},{T(_t1):.2f});")

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
  .srclab{{position:absolute;z-index:340;left:40px;bottom:22px;font-family:"JPMed";font-size:23px;color:#eaeaea;opacity:0;
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
  .optitle{{position:absolute;z-index:334;left:0;right:0;top:120px;text-align:center;opacity:0;}}
  .optitle .ev{{font-family:"JPHeavy";font-size:34px;color:var(--yellow);letter-spacing:.10em;
        text-shadow:0 0 6px #000,3px 3px 0 #000,-3px 3px 0 #000,3px -3px 0 #000,-3px -3px 0 #000;}}
  .optitle .mn{{font-family:"Mincho";font-size:76px;color:#fff;margin-top:14px;white-space:nowrap;
        letter-spacing:.04em;
        text-shadow:0 0 10px #000,
          5px 0 0 #000,-5px 0 0 #000,0 5px 0 #000,0 -5px 0 #000,
          4px 4px 0 #000,-4px 4px 0 #000,4px -4px 0 #000,-4px -4px 0 #000,
          0 10px 26px rgba(0,0,0,.85);}}
  .ccard.pred .phead{{display:flex;align-items:center;gap:16px;margin-bottom:16px;flex-wrap:wrap;}}
  .ccard.pred .pname{{font-family:"JPHeavy";font-size:34px;color:#0f1419;letter-spacing:.02em;}}
  .ccard.pred .ppick{{font-family:"JPHeavy";font-size:25px;color:#10131a;padding:5px 14px;border-radius:999px;white-space:nowrap;}}
  .tcard{{position:absolute;z-index:332;left:50%;top:50%;transform:translate(-50%,-50%);width:1120px;
        background:rgba(8,10,16,.88);border:2px solid rgba(255,226,58,.75);border-radius:22px;padding:30px 44px 26px;
        box-shadow:0 22px 60px rgba(0,0,0,.72);opacity:0;text-align:center;}}
  .tcard .ttl{{font-family:"JPHeavy";font-size:34px;color:var(--yellow);letter-spacing:.04em;margin-bottom:18px;}}
  .tcard .trow{{display:flex;align-items:center;justify-content:center;gap:42px;}}
  .tcard .tside{{flex:1;min-width:0;}}
  .tcard .tname{{font-family:"JPHeavy";font-size:38px;color:#fff;white-space:nowrap;margin-bottom:6px;}}
  .tcard .tnum{{font-family:"JPHeavy";font-size:108px;line-height:1;}}
  .tcard .tnum.l{{color:#5ad1ff;}} .tcard .tnum.r{{color:#ff7a5a;}}
  .tcard .tvs{{font-family:"Mincho";font-size:44px;color:#ffe23a;flex:none;}}
  .tcard .tunit{{font-family:"JPMed";font-size:26px;color:#cfd6e4;margin-top:12px;}}
  .subt{{position:absolute;z-index:350;left:0;right:0;bottom:118px;text-align:center;opacity:0;
        font-family:"JPHeavy";font-size:45px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;padding:0 90px;}}
</style>
</head>
<body>
  <div id="root" data-composition-id="lm16-yosou" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
{J(bg_divs,"    ")}

    {AUDIO_BLOCK}
{J(chap_audio,"    ")}

    <div class="veil"></div>
    <div class="wm">格闘ニュースラボ</div>
{J(src_divs,"    ")}
{J(chap_divs,"    ")}
{J(op_divs,"    ")}
{J(card_divs,"    ")}
{J(sub_divs,"    ")}

    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({{paused:true}});
{J(bg_tws)}
{J(chap_tws)}
{J(op_tws)}
{J(card_tws)}
{J(sub_tws)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['lm16-yosou'] = tl;
    </script>
  </div>
</body>
</html>
"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} bg={len(bg_divs)} cards={len(card_divs)} subs={len(sub_divs)}")
