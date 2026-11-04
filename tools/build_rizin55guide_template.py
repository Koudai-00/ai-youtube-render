# -*- coding: utf-8 -*-
"""超RIZIN.5 全試合ガイド index.html 生成(1920x1080・窓対応)。
   背景=ビート専用bgvid(build_rizin55guide_bg)。前景=DOM字幕(≤2行)・試合別章タグ・出典ラベル・透かし。
   カード/静止画ビートはKenBurns(GSAP)。VISUAL_ONLYレンダー→finalizeで音声mux。
   env: HF_WIN_START/HF_WIN_END/HF_VISUAL_ONLY/HF_OUTNAME。"""
from __future__ import annotations
import json, html, os, re as _re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "rizin55_guide"
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
DISP = {
 # --- 試合番号・大会 ---
 "だいじゅういち試合": "第11試合", "だいじゅうに試合": "第12試合", "だいじゅう試合": "第10試合",
 "だいいち試合": "第1試合", "だいに試合": "第2試合", "だいさん試合": "第3試合", "だいよん試合": "第4試合",
 "だいご試合": "第5試合", "だいろく試合": "第6試合", "だいなな試合": "第7試合", "だいはち試合": "第8試合",
 "だいきゅう試合": "第9試合", "全じゅうろく試合": "全16試合", "三試合": "3試合", "五分にラウンド": "5分2ラウンド",
 "じゅういちがつようか": "11月8日",
 # --- 契約体重・身長 ---
 "ごじゅうななキロ": "57キロ", "ろくじゅういちキロ": "61キロ", "ろくじゅうろくキロ": "66キロ",
 "ななじゅういちキロ": "71キロ", "ひゃくにじゅうよんキロ": "124キロ", "ひゃくにじゅうキロ": "120キロ",
 "ひゃくななじゅっセンチ": "170センチ", "ひゃくはちじゅうさんセンチ": "183センチ",
 "ひゃくはちじゅうにセンチ": "182センチ", "じゅうごセンチ": "15センチ",
 # --- 年齢 ---
 "じゅういっさい差": "11歳差", "じゅうよんさい差": "14歳差", "じゅうろくさい差": "16歳差",
 "じゅうはっさい": "18歳", "じゅうきゅうさい": "19歳", "にじゅういっさい": "21歳", "にじゅうにさい": "22歳",
 "にじゅうさんさい": "23歳", "にじゅうごさい": "25歳", "にじゅうろくさい": "26歳", "にじゅうななさい": "27歳",
 "にじゅうきゅうさい": "29歳", "さんじゅっさい": "30歳", "さんじゅういっさい": "31歳", "さんじゅうにさい": "32歳",
 "さんじゅうさんさい": "33歳", "さんじゅうよんさい": "34歳", "さんじゅうろくさい": "36歳",
 "さんじゅうななさい": "37歳", "よんじゅっさい": "40歳", "よんじゅういっさい": "41歳", "はたち": "20歳",
 # --- 戦績 ---
 "じゅうよんしょうじゅうさんぱい": "14勝13敗", "じゅうよんしょうごはい": "14勝5敗",
 "じゅうごしょうごはい": "15勝5敗", "じゅういっしょういっぱい": "11勝1敗", "はっしょういっぱい": "8勝1敗",
 "よんしょういっぱい": "4勝1敗", "にじゅうろくしょう": "26勝", "じゅうさんしょうのうち": "13勝のうち",
 "ななしょうをKO": "7勝をKO", "じゅっしょうが一本勝ち": "10勝が一本勝ち", "じゅっしょう無敗": "10勝無敗",
 "はっしょうがKO": "8勝がKO", "なな勝無敗": "7勝無敗", "よん勝すべて": "4勝すべて", "じゅうに勝": "12勝",
 "にじゅうなな戦": "27戦", "にじゅうよん戦": "24戦", "さんじゅうさん戦": "33戦",
 "ひゃくじゅうさん戦ひゃくろく勝": "113戦106勝", "ひゃくろく勝": "106勝", "よん戦全勝": "4戦全勝",
 "はまだに戦ながら、そのに戦を": "はまだ2戦ながら、その2戦を", "プロさん戦全勝": "プロ3戦全勝",
 "さん連勝": "3連勝", "なな連勝": "7連勝", "じゅう連勝": "10連勝", "、に連敗中": "、2連敗中",
 "フィニッシュ率九割": "フィニッシュ率9割",
 # --- タイム・ラウンド・再生数 ---
 "じゅうよんびょう": "14秒", "さんじゅうさんびょう": "33秒", "よんじゅうななびょう": "47秒",
 "ろくじゅうびょう": "60秒", "開始ろくびょう": "開始6秒", "さんラウンドにKO": "3ラウンドにKO",
 "にラウンドTKO": "2ラウンドTKO", "にラウンド開始": "2ラウンド開始",
 "ひゃくじゅうきゅうまん回": "119万回", "ひゃくまん回": "100万回", "判定スリーゼロ": "判定3-0",
 # --- 年月・期間 ---
 "ことし三月": "ことし3月", "ことし四月": "ことし4月", "ことし五月": "ことし5月", "ことし六月": "ことし6月",
 "ことし七月": "ことし7月", "去年四月": "去年4月", "去年の十一月": "去年の11月", "去年九月": "去年9月",
 "七月の広島": "7月の広島", "十月の長崎": "10月の長崎", "五月の再起戦": "5月の再起戦",
 "五年前": "5年前", "四年前": "4年前", "二年越し": "2年越し", "約二年ぶり": "約2年ぶり",
 "約二年間": "約2年間", "約七か月ぶり": "約7か月ぶり", "わずか一か月": "わずか1か月",
 "約十年修行": "約10年修行", "約一年ぶり": "約1年ぶり", "月二万円": "月2万円", "中学一年の夏": "中学1年の夏",
 "三歳から": "3歳から", "五歳から": "5歳から", "九年": "9年", "二度輝いた": "2度輝いた",
 "二度防衛": "2度防衛", "二階級": "2階級", "二本のベルト": "2本のベルト", "わずか一分あまり": "わずか1分あまり",
 "じゅうにさいから": "12歳から", "じゅうはっさいからは": "18歳からは",
 # --- 英字表記 ---
 "エスカップ": "S-cup", "アベマ": "ABEMA", "ケーワンの舞台": "K-1の舞台", "ワンの舞台": "ONEの舞台",
 "ワンチャンピオンシップ": "ONE Championship", "ブラックローズ": "BLACK ROSE", "バトルボックス": "Battle-Box",
 "ファイティングネクサス": "Fighting NEXUS", "ジョルジュサンピエール": "ジョルジュ・サンピエール",
 "ブレイキングダウン": "BreakingDown",
}
DISP.update({"ごふん、にラウンド":"5分2ラウンド","じゅっさい差":"10歳差","三十二歳":"32歳","百六十九センチ":"169センチ",
 "三十代前半":"30代前半","ななしょう無敗":"7勝無敗","百八十三センチ":"183センチ","百二十四キロ":"124キロ","二戦":"2戦",
 "じゅうにしょうのうち":"12勝のうち","雑賀ヤン坊達也":"雑賀“ヤン坊”達也","雑賀達也":"雑賀“ヤン坊”達也","ことし":"今年","ティージェー":"TJ","二つ":"2つ","二冠":"2冠","史上二人目":"史上2人目","二十二歳":"22歳","百七十三センチ":"173センチ","百六十五センチ":"165センチ","百七十二センチ":"172センチ","百七十八センチ":"178センチ","百七十四センチ":"174センチ","百七十一センチ":"171センチ","百六十七センチ":"167センチ","百八十センチ":"180センチ","百七十センチ":"170センチ","百七十五センチ":"175センチ","百六十センチ":"160センチ","二勝一敗":"2勝1敗","八勝三敗":"8勝3敗","十九勝十四敗":"19勝14敗","七勝六敗":"7勝6敗","八勝六敗":"8勝6敗","二十二勝十二敗":"22勝12敗","十七勝八敗":"17勝8敗","六勝四敗":"6勝4敗","十二勝六敗":"12勝6敗","二十四勝九敗一分":"24勝9敗1分","二十一勝五敗":"21勝5敗","二十三勝五敗一分":"23勝5敗1分"})
def disp(t):
    for k in sorted(DISP, key=len, reverse=True): t = t.replace(k, DISP[k])
    return t

# ---- 出典ラベル / KenBurns判定(src_kb.jsonから) ----
SRC = _SK["src"]; KB = {b: True for b in _SK["kb"]}
def srcof(bid): return SRC.get(bid, "出典: RIZIN (試合映像)")

# ---- 章タグ(試合ごと) ----
CHAP_LABEL = {
    "opf": ("オープニングファイト / 3試合", "未来のスターたち"),
    "f1": ("第1試合 / フライ級57kg", "力也 vs 木村琉音"),
    "f2": ("第2試合 / フライ級57kg", "濱田巧 vs 関原翔"),
    "f3": ("第3試合 / 71kg", "雑賀“ヤン坊”達也 vs 倉本大悟"),
    "f4": ("第4試合 / バンタム級61kg", "中島太一 vs 溝口司"),
    "f5": ("第5試合 / フェザー級66kg", "鈴木博昭 vs 千春"),
    "f6": ("第6試合 / ヘビー級120kg", "マック・パパリイ vs 赤沢幸典"),
    "f7": ("第7試合 / 71kg", "キム・ギョンピョ vs ズマガジー"),
    "f8": ("第8試合 / フェザー級66kg", "牛久絢太郎 vs リー・カイウェン"),
    "f9": ("第9試合 / フェザー級66kg", "メヘウラ vs 相本宗輝"),
    "f10": ("第10試合 / バンタム級61kg", "鹿志村仁之介 vs 太田忍"),
    "f11": ("第11試合 / バンタム級61kg", "福田龍彌 vs キム・スーチョル"),
    "f12": ("セミ / 次期挑戦者決定戦", "井上直樹 vs ティレノフ"),
    "f13": ("メイン / フライ級タイトルマッチ", "神龍誠 vs トニー・ララミー"),
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
    kata = lambda ch: ("ァ" <= ch <= "ヺ") or ch in "ー・"
    if kata(text[c-1]) and kata(text[c]):
        return False
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
    within = [x for x in cands if x[2] <= 27.0]
    if within: cands = within
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
    merged = []
    i = 0
    while i < len(cues):
        if len(cues[i]) <= 6 and i + 1 < len(cues) and zwidth(cues[i] + cues[i+1]) <= 52:
            merged.append(cues[i] + cues[i+1]); i += 2
        else:
            merged.append(cues[i]); i += 1
    return merged or [text]
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
  .chaptag{{position:absolute;z-index:320;left:100px;top:47%;opacity:0;}}
  .chaptag .chnum{{font-family:"Mincho";font-size:42px;color:var(--yellow);filter:var(--edge);letter-spacing:.04em;}}
  .chaptag .chttl{{font-family:"JPHeavy";font-size:58px;color:#fff;filter:var(--edge);margin-top:6px;white-space:nowrap;}}
  .subt{{position:absolute;z-index:350;left:0;right:0;bottom:96px;text-align:center;opacity:0;
        font-family:"JPHeavy";font-size:45px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;padding:0 90px;}}
</style>
</head>
<body>
  <div id="root" data-composition-id="rizin55" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
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
      window.__timelines['rizin55'] = tl;
    </script>
  </div>
</body>
</html>
"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} bg={len(bg_divs)} subs={len(sub_divs)} chaps={len(chap_divs)}")
