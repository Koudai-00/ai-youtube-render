"""今週の格闘技ニュースまとめ(2026-08-14) index.html 生成(1920x1080・長尺・窓対応)。
3トピック(ABEMA中心化/萩原vs木村デマ/超RIZIN.5追加カード)。冒頭要約→章タグ「Nつ目」→まとめ。
前景: 下部字幕(DISP漢字/英字・算用数字)・著名人ネームプレート・Xカード(公人実名/一般匿名)・
      萩原×木村VS合成・公式カード・宇佐美/皇治写真・希望チップ・ロゴ切替。窓env=HF_WIN_START/END/VISUAL_ONLY/HF_OUTNAME。"""
from __future__ import annotations
import json, html, os, re, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "weekly0814"
TPL = ROOT / "hyperframes" / "templates" / EP
TIM = json.load(open(ROOT / "subtitles" / "out" / EP / "timings.json", encoding="utf-8"))
XIDX = {x["id"]: x for x in json.load(open(ROOT / "assets" / "source" / f"episode_{EP}" / "xposts" / "assets_index.json", encoding="utf-8"))}
BEATS = TIM["beats"]
B = {b["id"]: b for b in BEATS}
COMP = round(TIM["total"] + 0.3, 2)

W0 = float(os.environ.get("HF_WIN_START") or 0)
_w1 = os.environ.get("HF_WIN_END")
W1 = float(_w1) if _w1 else COMP
VISUAL_ONLY = os.environ.get("HF_VISUAL_ONLY") == "1"
WIN = round(W1 - W0, 2)
OUTNAME = os.environ.get("HF_OUTNAME", "index.html")
def T(t): return round(t - W0, 3)
def OV(t0, t1): return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)
def st(bid): return B[bid]["start"]
def en(bid): return B[bid]["end"]
def esc(s): return html.escape(s)

# ===== DISP: 読みかな→漢字/英字(長いキー優先) =====
DISP = {
    "ちょうらいじんふぁいぶ": "超RIZIN.5", "超ライジンファイブ": "超RIZIN.5",
    "ライジンハンドレッドクラブ": "RIZIN 100 CLUB", "ライジンライブ": "RIZIN LIVE", "ライジンティーヴィー": "RIZIN TV",
    "ライジンチャンネル": "RIZINチャンネル", "ライジン": "RIZIN",
    "ペイパービュー": "PPV", "ユーネクスト": "U-NEXT", "アベマプレミアム": "ABEMAプレミアム", "アベマ": "ABEMA",
    "ユーエフシー": "UFC", "ユーチューブ": "YouTube", "エックス": "X", "ケイオー": "KO", "ピーエフエル": "PFL",
    "ディープ": "DEEP", "ワン": "ONE", "スカパー": "スカパー",
    "さかきばら": "榊原", "ささはらけいいち": "笹原圭一", "はぎわらきょうへい": "萩原京平", "きむらしゅうや": "木村柊也",
    "あおきしんや": "青木真也", "かわじりたつや": "川尻達也", "さえきしげる": "佐伯繁",
    "あさくらみくる": "朝倉未来", "ひらもとれん": "平本蓮", "しぇいどぅらえふ": "シェイドゥラエフ",
    "エイジェイマッキー": "AJ・マッキー", "レナ": "RENA", "ナターシャクジュティナ": "ナターシャ・クジュティナ",
    "うさみひでメイソン": "宇佐美秀メイソン", "うさみしょうパトリック": "宇佐美正パトリック",
    "べいのあ": "ベイノア", "くぼゆうた": "久保優太", "あんぽるきや": "安保瑠輝也", "こうじ": "皇治", "たける": "武尊",
    # 姓の短キー(フルネームは上で先に変換済み。「〜さん/〜が」等で残る姓を拾う)
    "ささはら": "笹原", "はぎわら": "萩原", "きむら": "木村", "あおき": "青木", "かわじり": "川尻",
    "さえき": "佐伯", "あさくら": "朝倉", "ひらもと": "平本", "うさみ": "宇佐美", "くぼ": "久保",
}
def disp(t):
    for k in sorted(DISP, key=len, reverse=True):
        t = t.replace(k, DISP[k])
    # 字幕整形(表示のみ・音声は不変): 「、と、」等の細切れ読点をならす
    t = t.replace("、と、", "と、").replace("、と。", "と。")
    return t

# ===== 字幕2行分割 =====
def zwidth(s):
    return sum(0.55 if (c.isascii() and (c.isalnum() or c in " .,'-")) else 1.0 for c in s)
def wrap_two(text, maxw):
    segs = [s for s in re.split("(?<=、)", text) if s]
    for i in range(1, len(segs)):
        l1 = "".join(segs[:i]); l2 = "".join(segs[i:])
        if zwidth(l1) <= maxw and zwidth(l2) <= maxw:
            return (l1, l2)
    if zwidth(text) <= maxw * 2:
        cut = max(1, int(len(text) * maxw / max(zwidth(text), 1)))
        return (text[:cut], text[cut:])
    return None
def fits_two(text, maxw):
    return zwidth(text) <= maxw or wrap_two(text, maxw) is not None
def split_cues(text, maxw=26.0):
    parts = [p for p in re.split("(?<=[、。])", text) if p]
    cues, cur = [], ""
    for p in parts:
        if fits_two(cur + p, maxw):
            cur += p
        else:
            if cur: cues.append(cur)
            cur = p
    if cur: cues.append(cur)
    return cues or [text]
def sub_lines(text, maxw=26.0):
    if zwidth(text) <= maxw: return [text]
    w = wrap_two(text, maxw)
    return [w[0], w[1]] if w else [text]

# ===== 章 =====
CHAP_LABEL = {
    "1つ目 RIZIN配信がABEMA中心へ": ("1つ目のニュース", "RIZIN配信が ABEMA中心へ"),
    "2つ目 幻の対戦カード": ("2つ目のニュース", "萩原京平 vs 木村柊也 の真相"),
    "3つ目 超RIZIN.5 追加カード": ("3つ目のニュース", "超RIZIN.5 追加カードSP"),
}
CHAPS = [(b["chapter"], b["start"]) for b in BEATS if b["chapter"]]

# ===== 背景プラン: (t0_bid, t1_bid, kind, ref, motion, srclabel). t*_bidはbeat id、'END'で全体末 =====
S_SHOW = "出典:「榊原社長に呼び出されました」(YouTube)"
S_R54 = "出典: RIZIN.54 / 発表配信より"
S_PEX = "出典: イメージ映像(Pexels)"
S_OFF = "出典: RIZIN 公式"
S_AOKI = "出典: 青木真也さぶちゃんねる(YouTube)"
S_KAWA = "出典: 川尻達也のじりラジオ(YouTube)"
S_SAEKI = "出典: ジョビンチャンネル(YouTube)"
def _endt(): return COMP
S_PEX2 = "出典: イメージ映像(Pexels)"
BG = [
    ("intro1", "intro2", "vid", "rizin54_ground.mp4@0", None, S_R54),
    ("intro2", "intro3", "vid", "sak_gesture.mp4@0", None, S_SHOW),
    ("intro3", "intro4", "vid", "neon.mp4@0", None, S_PEX),
    ("intro4", "t1_fact1", "vid", "esports_crowd_arena_cheering.mp4@0", None, S_PEX),
    # CH1
    ("t1_fact1", "t1_fact2", "vid", "sak_announce.mp4@0", None, S_SHOW),
    ("t1_fact2", "t1_fact3a", "vid", "sak_think.mp4@0", None, S_SHOW),       # logo switch FG
    ("t1_fact3a", "t1_fact3b", "vid", "sakakibara_crowd.mp4@0", None, S_SHOW),
    ("t1_fact3b", "t1_fact3c", "vid", "ito_talk.mp4@0", None, S_SHOW),
    ("t1_fact3c", "t1_why1", "vid", "disappointed.mp4@0", None, S_PEX),
    ("t1_why1", "t1_why2a", "vid", "social_media_notifications_phone.mp4@0", None, S_PEX),
    ("t1_why2a", "t1_why2b", "vid", "yen.mp4@0", None, S_PEX),               # 理由1 ポイント割引
    ("t1_why2b", "t1_why2c", "vid", "person_watching_sports_on_phone.mp4@0", None, S_PEX),  # 理由2 分断(logo chips FG)
    ("t1_why2c", "t1_fan1", "vid", "typing.mp4@0", None, S_PEX),             # 理由3 不信
    ("t1_fan1", "t1_why3", "vid", "thinking.mp4@0", None, S_PEX),            # fan card FG
    ("t1_why3", "t1_price", "vid", "sak_gesture.mp4@1", None, S_SHOW),
    ("t1_price", "t1_positive", "vid", "cashback.mp4@0", None, S_PEX),       # 料金/キャッシュバック
    ("t1_positive", "t1_exp_intro", "vid", "stadium.mp4@0", None, S_PEX),
    ("t1_exp_intro", "t1_aoki_a", "vid", "tokyo.mp4@0", None, S_PEX),
    ("t1_aoki_a", "t1_kawajiri", "img", "aoki.jpg", "kb_zin", S_AOKI),        # aoki_a/b/2
    ("t1_kawajiri", "t1_saeki", "img", "kawajiri.jpg", "kb_zin", S_KAWA),
    ("t1_saeki", "t2_spread", "img", "saeki_jobin.jpg", "kb_zin", S_SAEKI),
    # CH2
    ("t2_spread", "t2_skeptic", "img", "__vs2__", None, S_OFF),
    ("t2_skeptic", "t2_denial_lead", "img", "hagiwara_kyohei.jpg", "kb_zin", S_OFF),
    ("t2_denial_lead", "t2_bridge", "vid", "social_media_notifications_phone.mp4@8", None, S_PEX),  # 笹原card+stamp FG
    ("t2_bridge", "t3_sp", "vid", "fans.mp4@0", None, S_PEX),                # bridge_q card FG
    # CH3
    ("t3_sp", "t3_cards_a", "vid", "applause.mp4@0", None, S_PEX),           # RIZIN公式 card FG
    # t3_cards_a..t3_usami は公式カード3枚(下で分割)
    ("t3_usami", "t3_wishes_a", "img", "usami_hide_meison.jpg", "kb_zin", S_OFF),
    ("t3_wishes_a", "t3_koji", "vid", "esports_crowd_arena_cheering.mp4@8", None, S_PEX),  # chips FG
    ("t3_koji", "t3_ask", "img", "koji.jpg", "kb_zin", S_OFF),
    ("t3_ask", "outro", "vid", "neon.mp4@8", None, S_PEX),
    ("outro", "END", "vid", "rizin54_ground.mp4@2", None, S_R54),
]
# t3_cards_a..t3_usami 区間を公式カード3枚に分割
def _card_bg_segments():
    a, b = st("t3_cards_a"), st("t3_usami"); step = (b - a) / 3.0
    imgs = ["card_asakura_aoki.jpg", "card_shai_mckee.jpg", "card_rena.jpg"]
    return [(a + i * step, a + (i + 1) * step, "img", imgs[i], "kb_zout", S_OFF) for i in range(3)]

def _t(bid):
    return _endt() if bid == "END" else st(bid)
BG_ABS = []
for (t0b, t1b, k, r, m, s) in BG:
    BG_ABS.append((_t(t0b), _t(t1b), k, r, m, s))
BG_ABS += _card_bg_segments()
BG_ABS.sort(key=lambda e: e[0])
# 連続/隙間を一律 次開始+0.08 まで延長(境界黒防止)
_bg2 = []
for i, (t0, t1, k, r, m, s) in enumerate(BG_ABS):
    if i + 1 < len(BG_ABS):
        t1 = round(BG_ABS[i + 1][0] + 0.08, 3)
    _bg2.append((round(t0, 3), round(t1, 3), k, r, m, s))
BG_ABS = _bg2

# ===== BGプラン書き出し(事前合成bg用) =====
if os.environ.get("HF_EXPORT_BG") == "1":
    plan = [{"t0": round(t0, 3), "t1": round(t1, 3), "kind": k, "ref": r,
             "motion": (m or ("kb_zin" if i % 2 == 0 else "kb_pan")),
             "port": (k == "img" and r in ("hagiwara_kyohei.jpg", "usami_hide_meison.jpg", "koji.jpg"))}
            for i, (t0, t1, k, r, m, s) in enumerate(BG_ABS)]
    (TPL / "bg_plan.json").write_text(json.dumps({"total": COMP, "segments": plan}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"exported bg_plan.json ({len(plan)} segments, total {COMP}s)"); raise SystemExit(0)

# ===== 背景=事前合成bgを窓別に分割(CI高速化: 各~13MBでChromeロードが速い)。前景=DOM。 =====
# bg_w{N} は絶対区間 [max(0,N*60-1.5), (N+1)*60+1.5] をカバー。窓/ピースのW0から該当ファイルを選択。
bg_divs, bg_tws, src_divs = [], [], []
_wi = min(5, int((W0 + 1.5) // 60))
_fstart = max(0.0, _wi * 60 - 1.5)
_media = round(W0 - _fstart, 3)
_bgdur = (min(COMP, W1) - W0) + 0.6
bg_divs.append('<div class="bgseg" id="bgmain" style="z-index:1;opacity:1">'
               f'<video id="bgmain-v" src="assets/bgvid/weekly0814_bg_w{_wi}.mp4" muted playsinline data-layout-allow-overflow '
               f'data-start="0" data-duration="{_bgdur:.2f}" data-media-start="{_media:.3f}" data-track-index="10"></video></div>')
bg_tws.append("tl.set('#bgmain',{opacity:1},0);")
# 出典ラベル(FG・BG_ABSのタイミング)
for i, (t0, t1, kind, ref, mo, srcl) in enumerate(BG_ABS):
    if not srcl or not OV(t0, t1): continue
    sid = f"src{i}"; vt0 = T(t0)
    src_divs.append(f'<div class="srclab" id="{sid}">{esc(srcl)}</div>')
    bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{max(0.0,vt0+0.3):.2f});")
    bg_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{T(t1)-0.25:.2f});")
# VS合成の文字(超RIZIN.5で実現？ / VS)はbg画像に焼かず、FGで重ねる
_vs = next((e for e in BG_ABS if e[3] == "__vs2__"), None)
vs2_divs, vs2_tws = [], []
if _vs and OV(_vs[0], _vs[1]):
    vs2_divs.append('<div class="vs2fg" id="vs2fg"><div class="vsq">超RIZIN.5で実現！？</div><div class="vsvsC">VS</div></div>')
    vs2_tws.append(f"tl.fromTo('#vs2fg',{{opacity:0}},{{opacity:1,duration:.4}},{max(0.0,T(_vs[0]+0.3)):.2f});")
    vs2_tws.append(f"tl.to('#vs2fg',{{opacity:0,duration:.3}},{T(_vs[1])-0.2:.2f});")

# ===== 章タグ =====
chap_divs, chap_tws, chap_audio = [], [], []
for j, (ch, cst) in enumerate(CHAPS):
    if ch not in CHAP_LABEL or not OV(cst, cst + 3.8): continue
    ja, sub = CHAP_LABEL[ch]; cid = f"chap{j}"
    chap_divs.append(f'<div class="chaptag" id="{cid}"><div class="chnum">{esc(ja)}</div><div class="chttl">{esc(sub)}</div></div>')
    chap_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,y:40}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.6)'}},{T(cst+0.1):.2f});")
    chap_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-26,duration:.4,ease:'power1.in'}},{T(cst+3.4):.2f});")
    if not VISUAL_ONLY:
        chap_audio.append(f'<audio id="chs{j}" src="assets/se/chapter.wav" data-start="{T(cst+0.1):.2f}" data-track-index="{200+j}" data-volume="0.5"></audio>')

# ===== 著名人ネームプレート(t1_aoki/kawajiri/saeki) =====
EXPERTS = [
    ("t1_aoki_a", "t1_kawajiri", "青木 真也", "@青木真也さぶちゃんねる", "「ABEMAがU-NEXTを蹴り落とした。露出増は選手にプラス」"),
    ("t1_kawajiri", "t1_saeki", "川尻 達也", "川尻達也のじりラジオ", "「U-NEXT移行以来の衝撃。ABEMAの企画力には期待」"),
    ("t1_saeki", "t2_spread", "佐伯 繁 (DEEP代表)", "ジョビンチャンネル", "「DEEPはどうなる。まだ聞いていない。正直ショック」"),
]
exp_divs, exp_tws = [], []
for k, (b0, b1, nm, hd, quote) in enumerate(EXPERTS):
    t0, t1 = st(b0), st(b1)
    if not OV(t0, t1): continue
    eid = f"exp{k}"
    exp_divs.append(f'<div class="nameplate" id="{eid}"><div class="npbar"></div>'
                    f'<div class="npname">{esc(nm)}</div><div class="nphandle">{esc(hd)}</div>'
                    f'<div class="npquote">{esc(quote)}</div></div>')
    exp_tws.append(f"tl.fromTo('#{eid}',{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.5,ease:'back.out(1.4)'}},{max(0.0,T(t0+0.2)):.2f});")
    exp_tws.append(f"tl.to('#{eid}',{{opacity:0,duration:.3}},{T(t1-0.1):.2f});")

# ===== ロゴ切替(t1_fact2)・ロゴチップ(t1_why2) =====
logo_divs, logo_tws = [], []
def _logo(eid, t0, t1, inner, y=140):
    logo_divs.append(f'<div class="logobox" id="{eid}" style="top:{y}px">{inner}</div>')
    logo_tws.append(f"tl.fromTo('#{eid}',{{opacity:0,y:-20,scale:.95}},{{opacity:1,y:0,scale:1,duration:.4,ease:'back.out(1.3)'}},{max(0.0,T(t0)):.2f});")
    logo_tws.append(f"tl.to('#{eid}',{{opacity:0,duration:.25}},{T(t1-0.05):.2f});")
if OV(st("t1_fact2"), st("t1_fact3a")):
    _logo("lgsw", st("t1_fact2"), st("t1_fact3a"),
          '<div class="lgrow"><div class="ltile"><img src="assets/img/unext_black.png"><div class="ltag end">終了</div></div>'
          '<div class="larrow">➡</div><div class="ltile abm"><img src="assets/img/abema.png"><div class="ltag new">中心へ</div></div></div>')
if OV(st("t1_why2b"), st("t1_why2c")):
    _logo("lgchips", st("t1_why2b"), st("t1_why2c"),
          '<div class="lgchips"><span class="chip">U-NEXT</span><span class="chip">UFC</span><span class="chip">ONE</span><span class="chip">DEEP</span><span class="chipx">が分断</span></div>', y=150)

# ===== 希望チップ(t3_wishes)・皇治賛否(t3_koji) =====
chip_divs, chip_tws = [], []
if OV(st("t3_wishes_a"), st("t3_koji")):
    inner = ('<div class="wishbox" id="wishbox"><div class="wishttl">宇佐美秀メイソン の相手は？ ファンの希望</div>'
             '<div class="wishlist"><span class="wl">① ベイノア <em>兄パトの敵討ち</em></span>'
             '<span class="wl">② 久保 優太</span><span class="wl">③ 安保 瑠輝也 <em>キック</em></span>'
             '<span class="wl">④ 海外の強豪</span></div></div>')
    chip_divs.append(inner)
    wa = "wishbox"
    chip_tws.append(("tl.set('#%s',{opacity:1,y:0},0);" % wa) if T(st('t3_wishes_a')+0.3) <= 0.02
                    else f"tl.fromTo('#{wa}',{{opacity:0,y:24}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.3)'}},{max(0.0,T(st('t3_wishes_a')+0.3)):.2f});")
    chip_tws.append(f"tl.to('#{wa}',{{opacity:0,duration:.3}},{T(st('t3_koji')-0.1):.2f});")
if OV(st("t3_koji"), st("t3_ask")):
    inner = ('<div class="kojibox" id="kojibox"><div class="kojittl">皇治 出場予想 ＝ 賛否</div>'
             '<div class="kojivs">相手に <b>武尊</b> 案 → <span class="kojino">「それは見たくない」の声も</span></div></div>')
    chip_divs.append(inner)
    chip_tws.append(f"tl.fromTo('#kojibox',{{opacity:0,y:24}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.3)'}},{max(0.0,T(st('t3_koji')+0.3)):.2f});")
    chip_tws.append(f"tl.to('#kojibox',{{opacity:0,duration:.3}},{T(st('t3_ask')-0.1):.2f});")

# ===== デマ/大嘘スタンプ(t2_denial_lead..t2_bridge) =====
stamp_divs, stamp_tws = [], []
if OV(st("t2_denial_lead"), st("t2_bridge")):
    stamp_divs.append('<div class="demastamp" id="demastamp">デマ<span class="ds2">大嘘</span></div>')
    stamp_tws.append(f"tl.fromTo('#demastamp',{{opacity:0,scale:1.6,rotation:-14}},{{opacity:1,scale:1,rotation:-8,duration:.4,ease:'back.out(2)'}},{max(0.0,T(st('t2_denial')+0.1)):.2f});")
    stamp_tws.append(f"tl.to('#demastamp',{{opacity:0,duration:.3}},{T(st('t2_bridge')-0.1):.2f});")

# ===== Xカード(公人=実名 / 一般=匿名) =====
ANON_NAMES = ["格闘技ファン", "MMAウォッチャー", "リングサイド", "週末の観戦勢", "格闘技好き", "現地観戦民"]
def anon_card_html(cid, name_seed, text, likes=None):
    h = int(hashlib.md5(name_seed.encode()).hexdigest(), 16)
    name = ANON_NAMES[h % len(ANON_NAMES)]
    b36 = "0123456789abcdefghijklmnopqrstuvwxyz"
    handle = "@" + "".join(b36[(h >> (i * 5)) % 36] for i in range(8))
    L = len(text); fs = 34 if L <= 40 else 30 if L <= 70 else 26
    stat = f'<div class="xstats"><span class="st"><b>{likes:,}</b> いいね</span></div>' if likes else ""
    return (f'<div class="xcard rea" id="{cid}"><div class="xhead">'
            f'<div class="xav anon" style="background:hsl({h%360},45%,55%)">{esc(name[:1])}</div>'
            f'<div class="xnm"><div class="xname">{esc(name)}</div><div class="xhandle">{handle}</div></div>'
            f'<div class="xlogo">𝕏</div></div><div class="xtext" style="font-size:{fs}px">{esc(text)}</div>{stat}</div>')
def real_card_html(cid, pid, style="cap"):
    p = XIDX[pid]
    name = esc(p.get("name", "")); handle = esc("@" + p.get("handle", ""))
    av = f'<img class="xav" src="assets/img/avatars/{pid}.jpg">'
    badge = '<span class="vbadge">✔</span>' if p.get("verified") else ""
    txt = re.sub(r"https?://t\.co/\S+", "", p.get("text", "")).strip()
    txt = esc(txt).replace("\n", "<br>")
    L = len(txt); fs = 38 if L <= 55 else 32 if L <= 100 else 27
    fav = p.get("favorite_count")
    stat = f'<div class="xstats"><span class="st"><b>{fav:,}</b> いいね</span></div>' if fav else ""
    return (f'<div class="xcard {style}" id="{cid}"><div class="xhead">{av}'
            f'<div class="xnm"><div class="xname">{name}{badge}</div><div class="xhandle">{handle}</div></div>'
            f'<div class="xlogo">𝕏</div></div><div class="xtext" style="font-size:{fs}px">{txt}</div>{stat}</div>')

card_divs, card_tws = [], []
def _add_card(cid, t0, t1, html_fn, style):
    if not OV(t0, t1): return
    card_divs.append(html_fn(cid))
    fromx = 70 if style == "cap" else -60
    card_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,x:{fromx},y:18}},{{opacity:1,x:0,y:0,duration:.5,ease:'back.out(1.5)'}},{max(0.0,T(t0)):.2f});")
    card_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-14,duration:.35,ease:'power1.in'}},{T(t1):.2f});")
# 一般ファン(topic1 引用): t1_fan1
_add_card("cfan1", st("t1_fan1"), en("t1_fan1")+0.3, lambda c: anon_card_html(c, "abema_fan1", "どこが良いお知らせなの？U-NEXTで見させてよ", 364), "rea")
# 笹原 否定(実名・公人): t2_denial_lead..t2_denial2
_add_card("cden", st("t2_denial_lead"), en("t2_denial2")+0.2, lambda c: real_card_html(c, "2087867394652086323", "cap"), "cap")
# ブリッジ(一般匿名): t2_bridge_q
_add_card("cbrg", st("t2_bridge_q"), en("t2_bridge2")+0.2, lambda c: anon_card_html(c, "bridge1", "大嘘であってほしいのは、U-NEXTのPPV廃止の方ですよ！", 75), "rea")
# 8/17 SP告知(RIZIN公式・実名): t3_sp
_add_card("csp", st("t3_sp"), en("t3_sp")+0.2, lambda c: real_card_html(c, "2087484052224045060", "cap"), "cap")

# ===== 下部字幕(ナレーターbeatのみ。引用beatはカードが担う) =====
QUOTE_IDS = {"t1_fan1", "t2_denial", "t2_bridge_q"}
sub_divs, sub_tws = [], []; sidx = 0
for b in BEATS:
    if b["id"] in QUOTE_IDS: continue
    text = disp(b["text"]); cues = split_cues(text); n = len(cues)
    seg = (b["end"] - b["start"]) / n
    for ci, cue in enumerate(cues):
        cs = b["start"] + ci * seg; ce = cs + seg
        if not OV(cs, ce): continue
        inner = "<br>".join(esc(l) for l in sub_lines(cue))
        did = f"sub{sidx}"; sidx += 1
        sub_divs.append(f'<div class="subt" id="{did}">{inner}</div>')
        sub_tws.append(f"tl.fromTo('#{did}',{{opacity:0}},{{opacity:1,duration:.18}},{max(0.0,T(cs)):.2f});")
        sub_tws.append(f"tl.to('#{did}',{{opacity:0,duration:.14}},{T(ce-0.05):.2f});")

# 窓境界のちらつき対策: 窓開始(<=0.02s)で始まる入場tweenは再アニメせず即・最終状態にセット
def _cont_fix(tws):
    out = []
    for s in tws:
        m = re.match(r"tl\.fromTo\('(#[^']+)',\{[^}]*\},\{[^}]*\},([\-0-9.]+)\);\s*$", s)
        if m and float(m.group(2)) <= 0.02:
            rot = -8 if m.group(1) == "#demastamp" else 0
            out.append("tl.set('%s',{opacity:1,x:0,y:0,scale:1,rotation:%d},0);" % (m.group(1), rot))
        else:
            out.append(s)
    return out
for _nm in ("bg_tws", "chap_tws", "exp_tws", "logo_tws", "stamp_tws", "vs2_tws", "chip_tws", "card_tws", "sub_tws"):
    globals()[_nm] = _cont_fix(globals()[_nm])

def J(items, ind="      "): return "\n".join(ind + x for x in items)
AUDIO_BLOCK = ("" if VISUAL_ONLY else
    '<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="60" data-volume="1"></audio>\n'
    '    <audio id="bgm" src="assets/audio/bgm.mp3" data-start="0" data-track-index="61" data-volume="0.07"></audio>')

HTML = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
  @font-face{{font-family:"Mincho";src:url("assets/fonts/GokubutoMincho.ttf");}}
  @font-face{{font-family:"JPHeavy";src:url("assets/fonts/SourceHanSansJP-Heavy.otf");}}
  @font-face{{font-family:"JPMed";src:url("assets/fonts/SourceHanSansJP-Medium.otf");}}
  :root{{--white:#fff;--yellow:#ffe23a;--red:#ff3a3a;--blue:#36b6ff;--green:#12c07a;--ink:#0a0c12;
    --edge:drop-shadow(4px 0 0 var(--ink)) drop-shadow(-4px 0 0 var(--ink)) drop-shadow(0 4px 0 var(--ink)) drop-shadow(0 -4px 0 var(--ink))
           drop-shadow(3px 3px 0 var(--ink)) drop-shadow(-3px 3px 0 var(--ink)) drop-shadow(0 8px 16px rgba(0,0,0,.8));
    --edge-sm:drop-shadow(0 0 2px var(--ink)) drop-shadow(1px 1px 1px var(--ink)) drop-shadow(0 2px 6px rgba(0,0,0,.85));}}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  #root{{position:absolute;inset:0;overflow:hidden;background:#05060a;font-family:"JPMed";}}
  .bgseg{{position:absolute;inset:0;opacity:0;overflow:hidden;}}
  .bgseg video,.bgseg .kbimg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform:translateZ(0);backface-visibility:hidden;}}
  .bgseg .kbimg.port{{object-position:center top;}}
  .vsbg{{position:absolute;inset:0;background:radial-gradient(circle at 50% 42%,#20304e,#070a12 75%);}}
  .vsbg .vsq{{position:absolute;top:70px;left:0;right:0;text-align:center;font-family:"JPHeavy";font-size:64px;color:var(--yellow);filter:var(--edge);}}
  .vsimg{{position:absolute;bottom:0;height:74%;object-fit:contain;filter:drop-shadow(0 10px 30px rgba(0,0,0,.7));}}
  .vsL{{left:6%;}} .vsR{{right:6%;}}
  .vsvsC{{position:absolute;left:0;right:0;top:46%;text-align:center;font-family:"JPHeavy";font-size:120px;color:var(--red);filter:var(--edge);}}
  .vs2fg{{position:absolute;inset:0;z-index:38;pointer-events:none;opacity:0;}}
  .vs2fg .vsq{{position:absolute;top:70px;left:0;right:0;text-align:center;font-family:"JPHeavy";font-size:64px;color:var(--yellow);filter:var(--edge);}}
  .veil{{position:absolute;inset:0;z-index:30;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,.5) 0%,transparent 16%,transparent 58%,rgba(0,0,0,.5) 84%,rgba(0,0,0,.78) 100%);}}
  .wm{{position:absolute;z-index:60;left:36px;top:30px;font-family:"JPHeavy";font-size:30px;color:#fff;letter-spacing:.04em;filter:var(--edge-sm);opacity:.9;}}
  .srclab{{position:absolute;z-index:55;left:40px;bottom:40px;font-family:"JPMed";font-size:23px;color:#eaeaea;opacity:0;background:rgba(0,0,0,.5);border-left:4px solid var(--yellow);padding:6px 14px;border-radius:3px;filter:var(--edge-sm);}}
  .chaptag{{position:absolute;z-index:48;left:120px;top:38%;opacity:0;}}
  .chaptag .chnum{{font-family:"Mincho";font-size:46px;color:var(--yellow);filter:var(--edge);letter-spacing:.04em;}}
  .chaptag .chttl{{font-family:"JPHeavy";font-size:74px;color:#fff;filter:var(--edge);margin-top:6px;white-space:nowrap;}}
  /* 著名人ネームプレート */
  .nameplate{{position:absolute;z-index:44;left:70px;bottom:230px;background:rgba(10,14,24,.82);border-radius:14px;padding:22px 30px 24px;opacity:0;max-width:760px;border-left:8px solid var(--yellow);}}
  .nameplate .npname{{font-family:"JPHeavy";font-size:44px;color:#fff;filter:var(--edge-sm);}}
  .nameplate .nphandle{{font-family:"JPMed";font-size:26px;color:#9fd0ff;margin-top:4px;}}
  .nameplate .npquote{{font-family:"JPMed";font-size:30px;color:#ffe23a;margin-top:12px;line-height:1.4;}}
  /* ロゴ */
  .logobox{{position:absolute;z-index:42;left:0;right:0;text-align:center;opacity:0;}}
  .lgrow{{display:inline-flex;align-items:center;gap:26px;}}
  .ltile{{background:#fff;border-radius:18px;padding:22px 30px;box-shadow:0 14px 40px rgba(0,0,0,.5);position:relative;}}
  .ltile img{{height:70px;object-fit:contain;display:block;}}
  .ltile.abm{{background:#eafff6;border:4px solid var(--green);}}
  .ltag{{position:absolute;bottom:-20px;left:50%;transform:translateX(-50%);font-family:"JPHeavy";font-size:26px;padding:3px 16px;border-radius:16px;white-space:nowrap;filter:var(--edge-sm);}}
  .ltag.end{{background:var(--red);color:#fff;}} .ltag.new{{background:var(--green);color:#fff;}}
  .larrow{{font-size:70px;color:#fff;filter:var(--edge);}}
  .lgchips{{display:inline-flex;align-items:center;gap:16px;}}
  .lgchips .chip{{font-family:"JPHeavy";font-size:44px;color:#fff;background:rgba(20,30,50,.9);border:3px solid #4a6ea0;border-radius:12px;padding:8px 22px;filter:var(--edge-sm);}}
  .lgchips .chipx{{font-family:"JPHeavy";font-size:40px;color:var(--red);filter:var(--edge);}}
  /* デマスタンプ */
  .demastamp{{position:absolute;z-index:47;right:150px;top:36%;font-family:"JPHeavy";font-size:150px;color:var(--red);border:10px solid var(--red);border-radius:20px;padding:6px 34px;transform:rotate(-8deg);opacity:0;filter:drop-shadow(0 6px 14px rgba(0,0,0,.8));background:rgba(255,255,255,.06);}}
  .demastamp .ds2{{display:block;font-size:70px;text-align:center;letter-spacing:.1em;margin-top:-6px;}}
  /* 希望チップ/皇治 */
  .wishbox{{position:absolute;z-index:44;left:80px;top:270px;background:rgba(10,14,24,.84);border-radius:16px;padding:26px 34px;opacity:0;border-left:8px solid var(--yellow);}}
  .wishttl{{font-family:"JPHeavy";font-size:40px;color:#fff;filter:var(--edge-sm);margin-bottom:16px;}}
  .wishlist{{display:flex;flex-direction:column;gap:12px;}}
  .wishlist .wl{{font-family:"JPHeavy";font-size:38px;color:#ffe23a;}}
  .wishlist .wl em{{font-family:"JPMed";font-style:normal;font-size:26px;color:#9fd0ff;margin-left:10px;}}
  .kojibox{{position:absolute;z-index:44;left:80px;bottom:250px;background:rgba(10,14,24,.84);border-radius:16px;padding:24px 32px;opacity:0;border-left:8px solid var(--red);}}
  .kojittl{{font-family:"JPHeavy";font-size:44px;color:#fff;filter:var(--edge-sm);}}
  .kojivs{{font-family:"JPMed";font-size:32px;color:#fff;margin-top:12px;}}
  .kojivs b{{color:var(--yellow);}} .kojino{{color:var(--red);}}
  /* Xカード */
  .xcard{{position:absolute;z-index:40;background:#fff;color:#0f1419;border-radius:20px;padding:26px 30px;box-shadow:0 18px 50px rgba(0,0,0,.6);opacity:0;border:1px solid #cfd9de;}}
  .xcard.cap{{right:80px;top:120px;width:780px;}}
  .xcard.rea{{left:80px;top:320px;width:640px;}}
  .xhead{{display:flex;align-items:center;gap:16px;margin-bottom:14px;}}
  .xav{{width:64px;height:64px;border-radius:50%;object-fit:cover;flex:none;}}
  .xav.anon{{display:flex;align-items:center;justify-content:center;color:#fff;font-family:"JPHeavy";font-size:30px;}}
  .xnm{{flex:1;min-width:0;}}
  .xname{{font-family:"JPHeavy";font-size:30px;line-height:1.1;display:flex;align-items:center;gap:8px;}}
  .vbadge{{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;background:#1d9bf0;color:#fff;font-size:15px;}}
  .xhandle{{font-size:24px;color:#536471;}}
  .xlogo{{font-size:32px;color:#0f1419;flex:none;}}
  .xtext{{font-family:"JPMed";font-size:36px;line-height:1.5;color:#0f1419;word-break:break-word;}}
  .xstats{{display:flex;gap:24px;margin-top:16px;padding-top:12px;border-top:1px solid #eaeef0;font-size:24px;color:#536471;}}
  .xstats .st b{{color:#0f1419;}}
  /* 下部字幕 */
  .subt{{position:absolute;z-index:50;left:0;right:0;bottom:96px;text-align:center;opacity:0;font-family:"JPHeavy";font-size:46px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;}}
</style></head><body>
  <div id="root" data-composition-id="wk-news" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
{J(bg_divs,"    ")}
    {AUDIO_BLOCK}
{J(chap_audio,"    ")}
    <div class="veil"></div>
    <div class="wm">格闘ニュースラボ</div>
{J(src_divs,"    ")}
{J(chap_divs,"    ")}
{J(exp_divs,"    ")}
{J(logo_divs,"    ")}
{J(stamp_divs,"    ")}
{J(vs2_divs,"    ")}
{J(chip_divs,"    ")}
{J(card_divs,"    ")}
{J(sub_divs,"    ")}
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({{paused:true}});
{J(bg_tws)}
{J(chap_tws)}
{J(exp_tws)}
{J(logo_tws)}
{J(stamp_tws)}
{J(vs2_tws)}
{J(chip_tws)}
{J(card_tws)}
{J(sub_tws)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['wk-news'] = tl;
    </script>
  </div>
</body></html>"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} bg={len(bg_divs)} cards={len(card_divs)} experts={len(exp_divs)} subs={len(sub_divs)}")
