"""アオリ・チロン完全解説 index.html 生成(1920x1080・長尺・窓対応)。
背景=単一bg動画を窓別選択(bg_w{N})。前景=DOM(下部字幕DISP・章タグ・試合映像PiP枠・規模マップ図・スタッツカード・出典・透かし)。
試合映像は360pのため枠付き中サイズPiP(全画面にしない)。窓env=HF_WIN_START/END/VISUAL_ONLY/HF_OUTNAME/HF_EXPORT_BG。"""
from __future__ import annotations
import json, html, os, re
from pathlib import Path
VISUAL_ONLY = os.environ.get("HF_VISUAL_ONLY") == "1"

ROOT = Path(__file__).resolve().parents[1]
EP = "aori"
TPL = ROOT / "hyperframes" / "templates" / EP
TIM = json.load(open(ROOT / "subtitles" / "out" / EP / "timings.json", encoding="utf-8"))
BEATS = TIM["beats"]; B = {b["id"]: b for b in BEATS}
COMP = round(TIM["total"] + 0.3, 2)
W0 = float(os.environ.get("HF_WIN_START") or 0)
_w1 = os.environ.get("HF_WIN_END"); W1 = float(_w1) if _w1 else COMP
WIN = round(W1 - W0, 2)
OUTNAME = os.environ.get("HF_OUTNAME", "index.html")
def T(t): return round(t - W0, 3)
def OV(t0, t1): return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)
def st(b): return B[b]["start"]
def en(b): return B[b]["end"]
def esc(s): return html.escape(s)

# ===== DISP: 読みかな→正式表記(長キー優先) =====
DISP = {
    "あおりちろん": "アオリ・チロン", "あさくらかい": "朝倉海", "うさみ": "宇佐美",
    "だぶりゅーえるえふ": "WLF", "さんだー": "散打", "ちょういり": "張偉麗", "いーろん": "一龍",
    "こーでぃぎぶそん": "コーディ・ギブソン", "きゃめろんえるす": "キャメロン・エルス",
    "あいまんざはび": "アイマン・ザハビ", "らうるろさすじゅにあ": "ラウル・ロサス・ジュニア",
    "こーでぃはどん": "コーディ・ハドン", "じぇふもりな": "ジェフ・モリナ",
    "ユーエフシー": "UFC", "ワン": "ONE", "ライジン": "RIZIN", "ディープ": "DEEP",
    "パンクラス": "パンクラス", "ケーワン": "K-1", "ノックアウト": "KO",
    "モンゴリアンマーダラー": "モンゴリアン・マーダラー", "ハイリスク・ハイリターン": "ハイリスク・ハイリターン",
}
def disp(t):
    for k in sorted(DISP, key=len, reverse=True): t = t.replace(k, DISP[k])
    t = t.replace("、と、", "と、").replace("、と。", "と。")
    return t

# ===== 字幕2行分割 =====
def zwidth(s): return sum(0.55 if (c.isascii() and (c.isalnum() or c in " .,'-")) else 1.0 for c in s)
def wrap_two(text, maxw):
    segs = [s for s in re.split("(?<=、)", text) if s]
    for i in range(1, len(segs)):
        l1 = "".join(segs[:i]); l2 = "".join(segs[i:])
        if zwidth(l1) <= maxw and zwidth(l2) <= maxw: return (l1, l2)
    if zwidth(text) <= maxw * 2:
        cut = max(1, int(len(text) * maxw / max(zwidth(text), 1))); return (text[:cut], text[cut:])
    return None
def fits_two(text, maxw): return zwidth(text) <= maxw or wrap_two(text, maxw) is not None
def split_cues(text, maxw=26.0):
    parts = [p for p in re.split("(?<=[、。])", text) if p]; cues, cur = [], ""
    for p in parts:
        if fits_two(cur + p, maxw): cur += p
        else:
            if cur: cues.append(cur)
            cur = p
    if cur: cues.append(cur)
    return cues or [text]
def sub_lines(text, maxw=26.0):
    if zwidth(text) <= maxw: return [text]
    w = wrap_two(text, maxw); return [w[0], w[1]] if w else [text]

# ===== 章 =====
CHAP_LABEL = {
    "アオリ・チロンとは": ("PROFILE", "アオリ・チロンとは"),
    "WLF時代と団体の規模": ("ORIGIN", "WLF時代と、団体の規模"),
    "UFCでの戦い": ("UFC", "UFCでの戦い"),
    "ファイトスタイル徹底分析": ("STYLE", "ファイトスタイル徹底分析"),
    "朝倉海戦の見どころ": ("THE FIGHT", "朝倉海戦の、見どころ"),
}
CHAPS = [(b["chapter"], b["start"]) for b in BEATS if b["chapter"]]

# ===== 背景プラン (t0_bid, t1_bid, ref, motion, srclabel)  refは画像/動画ファイル。ENDで末尾 =====
S_UFC = "出典: UFC公式 素材"; S_RIZIN = "出典: RIZIN公式"; S_PEX = "出典: イメージ映像(Pexels)"
IMG = {"aori_fullbody.png", "aori_headshot.png", "asakura_kai.jpg"}
def _pex(n): return f"pex_{n}.mp4"  # bgvidにステージした名前
BG = [
    ("h1", "h2", "aori_fullbody.png", "kb_zin", S_UFC),
    ("h2", "c1_1", "shanghai.mp4", None, S_PEX),
    ("c1_1", "c1_2", "grassland.mp4", None, S_PEX),
    ("c1_2", "c1_3", "nomad.mp4", None, S_PEX),
    ("c1_3", "c1_4", "aori_headshot.png", "kb_zin", S_UFC),
    ("c1_4", "c1_5", "gym.mp4", None, S_PEX),
    ("c1_5", "c2_1", "silhouette.mp4", None, S_PEX),
    ("c2_1", "c2_2", "stadium.mp4", None, S_PEX),
    ("c2_2", "c2_3", "cage.mp4", None, S_PEX),
    ("c2_3", "c2_4", "lantern.mp4", None, S_PEX),
    ("c2_4", "c2_6", "aerial.mp4", None, S_PEX),          # 規模マップFGが乗る
    ("c2_6", "c2_7", "cage.mp4", None, S_PEX),
    ("c2_7", "c3_1", "stadium.mp4", None, S_PEX),
    ("c3_1", "c3_2", "aori_fullbody.png", "kb_pan", S_UFC),
    ("c3_2", "c3_3", "shanghai.mp4", None, S_PEX),
    ("c3_3", "c3_3b", "fists.mp4", None, S_PEX),
    ("c3_3b", "c3_4", "silhouette.mp4", None, S_PEX),      # PiP hl_ko=21秒KO
    ("c3_4", "c3_5", "cage.mp4", None, S_PEX),             # PiP rosas(黒星)
    ("c3_5", "c4_1", "aori_headshot.png", "kb_zin", S_UFC),
    ("c4_1", "c4_2", "gym.mp4", None, S_PEX),
    ("c4_2", "c4_3", "silhouette.mp4", None, S_PEX),       # PiP hl_finish
    ("c4_3", "c4_4", "fists.mp4", None, S_PEX),            # スタッツカード
    ("c4_4", "c4_5", "cage.mp4", None, S_PEX),
    ("c4_5", "c5_1", "aori_fullbody.png", "kb_zin", S_UFC),
    ("c5_1", "c5_1b", "asakura_kai.jpg", "kb_zin", S_RIZIN),
    ("c5_1b", "c5_2", "shanghai.mp4", None, S_PEX),        # PiP asakura
    ("c5_2", "c5_3", "aerial.mp4", None, S_PEX),           # VSカード
    ("c5_3", "c5_4", "silhouette.mp4", None, S_PEX),
    ("c5_4", "c5_5", "cage.mp4", None, S_PEX),             # スタッツ比較
    ("c5_5", "c5_6", "shanghai.mp4", None, S_PEX),
    ("c5_6", "c5_7", "aori_fullbody.png", "kb_pan", S_UFC),
    ("c5_7", "e1", "stadium.mp4", None, S_PEX),
    ("e1", "END", "aori_fullbody.png", "kb_zin", S_UFC),
]
def _t(bid): return COMP if bid == "END" else st(bid)
BG_ABS = [(_t(a), _t(b), r, m, s) for (a, b, r, m, s) in BG]
BG_ABS.sort(key=lambda e: e[0])
_bg2 = []
for i, (t0, t1, r, m, s) in enumerate(BG_ABS):
    if i + 1 < len(BG_ABS): t1 = round(BG_ABS[i + 1][0] + 0.08, 3)
    _bg2.append((round(t0, 3), round(t1, 3), r, m, s))
BG_ABS = _bg2

# ===== BGプラン書き出し(bg合成用) =====
if os.environ.get("HF_EXPORT_BG") == "1":
    plan = [{"t0": t0, "t1": t1, "kind": ("img" if r in IMG else "vid"), "ref": r,
             "motion": (m or ("kb_zin" if i % 2 == 0 else "kb_pan")),
             "port": (r in ("aori_fullbody.png",))}
            for i, (t0, t1, r, m, s) in enumerate(BG_ABS)]
    (TPL / "bg_plan.json").write_text(json.dumps({"total": COMP, "segments": plan}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"exported bg_plan.json ({len(plan)} segments, total {COMP})"); raise SystemExit(0)

# ===== 背景=窓別bg動画 =====
bg_divs, bg_tws, src_divs = [], [], []
_wi = min(6, int((W0 + 1.5) // 60)); _fstart = max(0.0, _wi * 60 - 1.5); _media = round(W0 - _fstart, 3)
_bgdur = (min(COMP, W1) - W0) + 0.6
bg_divs.append('<div class="bgseg" id="bgmain" style="z-index:1;opacity:1">'
               f'<video id="bgmain-v" src="assets/bgvid/aori_bg_w{_wi}.mp4" muted playsinline data-layout-allow-overflow '
               f'data-start="0" data-duration="{_bgdur:.2f}" data-media-start="{_media:.3f}" data-track-index="10"></video></div>')
bg_tws.append("tl.set('#bgmain',{opacity:1},0);")
for i, (t0, t1, r, m, s) in enumerate(BG_ABS):
    if not s or not OV(t0, t1): continue
    sid = f"src{i}"; vt0 = T(t0)
    src_divs.append(f'<div class="srclab" id="{sid}">{esc(s)}</div>')
    bg_tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{max(0.0,vt0+0.3):.2f});")
    bg_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{T(t1)-0.25:.2f});")

# ===== 試合映像PiP(枠付き中サイズ・360p対策) (b0,b1,clip,label) =====
PIP = [
    ("h1", "h2", "hl_ko.mp4", "試合映像 (UFC)"),           # 冒頭フック=KO/打撃
    ("c1_5", "c2_1", "wlf1.mp4", "WLF 武林風 の試合"),      # 散打→WLF例
    ("c2_6", "c2_7", "wlf2.mp4", "WLF 武林風 の試合"),
    ("c3_1", "c3_2", "molina.mp4", "UFCデビュー (対モリナ)"),
    ("c3_3", "c3_3b", "hl_ufc1.mp4", "試合映像 (UFC)"),
    ("c3_3b", "c3_4", "hl_ko.mp4", "21秒TKO (対ギブソン)"),
    ("c3_4", "c3_5", "rosas.mp4", "対ロサス Jr (判定負け)"),
    ("c4_2", "c4_3", "hl_finish.mp4", "試合映像 (UFC)"),
    ("c4_5", "c5_1", "hl_ufc1.mp4", "試合映像 (UFC)"),
    ("c5_1b", "c5_2", "asakura.mp4", "朝倉海 vs スモザーマン"),
]
pip_divs, pip_tws = [], []
for k, (b0, b1, clip, lab) in enumerate(PIP):
    t0, t1 = st(b0), en(b1) if b1 in B else st(b1)
    t1 = st(b1) if b1 in B else t1
    if not OV(t0, t1): continue
    pid = f"pip{k}"
    pip_divs.append(f'<div class="pipbox" id="{pid}"><div class="pipframe">'
                    f'<video id="{pid}-v" src="assets/pip/{clip}" muted playsinline loop '
                    f'data-start="{max(0.0,T(t0)):.2f}" data-duration="{(min(t1,W1)-max(t0,W0))+0.4:.2f}" data-track-index="{40+k}"></video>'
                    f'</div><div class="piplabel">{esc(lab)}</div></div>')
    cont = T(t0) <= 0.02
    if cont:
        pip_tws.append(f"tl.set('#{pid}',{{opacity:1,scale:1}},0);")
    else:
        pip_tws.append(f"tl.fromTo('#{pid}',{{opacity:0,scale:.94}},{{opacity:1,scale:1,duration:.4,ease:'back.out(1.3)'}},{T(t0):.2f});")
    pip_tws.append(f"tl.to('#{pid}',{{opacity:0,duration:.3}},{T(t1)-0.05:.2f});")

# ===== 規模マップ図(ch2: c2_4..c2_6) =====
map_divs, map_tws = [], []
if OV(st("c2_4"), st("c2_6")):
    inner = ('<div class="scalemap" id="scalemap"><div class="smttl">世界の主要MMA団体 規模マップ</div>'
             '<div class="smrow"><span class="smtier">世界</span><span class="smorg big">UFC</span></div>'
             '<div class="smrow"><span class="smtier">アジア</span><span class="smorg">ONE</span></div>'
             '<div class="smrow"><span class="smtier">日本</span><span class="smorg">RIZIN</span><span class="smorg sm">DEEP</span><span class="smorg sm">パンクラス</span></div>'
             '<div class="smrow hi"><span class="smtier">中国</span><span class="smorg">WLF 武林風</span><span class="smnote">← アオリはここの王者</span></div></div>')
    map_divs.append(inner)
    map_tws.append(f"tl.fromTo('#scalemap',{{opacity:0,y:24}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.3)'}},{max(0.0,T(st('c2_4')+0.2)):.2f});")
    map_tws.append(f"tl.to('#scalemap',{{opacity:0,duration:.3}},{T(st('c2_6')-0.1):.2f});")

# ===== スタッツカード =====
STAT = [
    ("c4_3", "c4_4", '<div class="statttl">攻撃データ</div><div class="statrow"><b>有効打 命中率</b><span class="sv">49%</span></div><div class="statrow"><b>被弾数 / 分</b><span class="sv warn">5.47発</span></div><div class="statnote">当てる力は高いが、もらう隙も大きい</div>'),
    ("c5_4", "c5_5", '<div class="statttl">戦績</div><div class="statrow"><b>プロ通算</b><span class="sv">26勝 13敗 1NC</span></div><div class="statrow"><b>KO</b><span class="sv">9</span><b>UFC</b><span class="sv">4勝5敗1NC</span></div><div class="statnote">勝つも負けるも豪快なストライカー</div>'),
]
stat_divs, stat_tws = [], []
for k, (b0, b1, inner) in enumerate(STAT):
    if not OV(st(b0), st(b1)): continue
    sid = f"stat{k}"
    stat_divs.append(f'<div class="statcard" id="{sid}">{inner}</div>')
    stat_tws.append(f"tl.fromTo('#{sid}',{{opacity:0,x:40}},{{opacity:1,x:0,duration:.5,ease:'back.out(1.3)'}},{max(0.0,T(st(b0)+0.2)):.2f});")
    stat_tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{T(st(b1)-0.1):.2f});")

# ===== VSカード(c5_2..c5_3) =====
vs_divs, vs_tws = [], []
if OV(st("c5_2"), st("c5_3")):
    vs_divs.append('<div class="vscard" id="vscard"><img class="vsimg vsL" src="assets/img/aori_fullbody.png">'
                   '<div class="vsmid"><div class="vsn vnL">アオリ・チロン</div><div class="vsvs">VS</div><div class="vsn vnR">朝倉 海</div></div>'
                   '<img class="vsimg vsR" src="assets/img/asakura_kai.jpg"></div>')
    vs_tws.append(f"tl.fromTo('#vscard',{{opacity:0,scale:.95}},{{opacity:1,scale:1,duration:.5,ease:'back.out(1.3)'}},{max(0.0,T(st('c5_2')+0.2)):.2f});")
    vs_tws.append(f"tl.to('#vscard',{{opacity:0,duration:.3}},{T(st('c5_3')-0.1):.2f});")

# ===== 章タグ =====
chap_divs, chap_tws, chap_audio = [], [], []
for j, (ch, cst) in enumerate(CHAPS):
    if ch not in CHAP_LABEL or not OV(cst, cst + 3.8): continue
    en_, sub = CHAP_LABEL[ch]; cid = f"chap{j}"
    chap_divs.append(f'<div class="chaptag" id="{cid}"><div class="chnum">{esc(en_)}</div><div class="chttl">{esc(sub)}</div></div>')
    chap_tws.append(f"tl.fromTo('#{cid}',{{opacity:0,y:40}},{{opacity:1,y:0,duration:.5,ease:'back.out(1.6)'}},{T(cst+0.1):.2f});")
    chap_tws.append(f"tl.to('#{cid}',{{opacity:0,y:-26,duration:.4,ease:'power1.in'}},{T(cst+3.4):.2f});")
    if not VISUAL_ONLY:
        chap_audio.append(f'<audio id="chs{j}" src="assets/se/chapter.wav" data-start="{T(cst+0.1):.2f}" data-track-index="{200+j}" data-volume="0.5"></audio>')

# ===== 下部字幕 =====
sub_divs, sub_tws = [], []; sidx = 0
for b in BEATS:
    text = disp(b["text"]); cues = split_cues(text); n = len(cues); seg = (b["end"] - b["start"]) / n
    for ci, cue in enumerate(cues):
        cs = b["start"] + ci * seg; ce = cs + seg
        if not OV(cs, ce): continue
        inner = "<br>".join(esc(l) for l in sub_lines(cue)); did = f"sub{sidx}"; sidx += 1
        sub_divs.append(f'<div class="subt" id="{did}">{inner}</div>')
        sub_tws.append(f"tl.fromTo('#{did}',{{opacity:0}},{{opacity:1,duration:.18}},{max(0.0,T(cs)):.2f});")
        sub_tws.append(f"tl.to('#{did}',{{opacity:0,duration:.14}},{T(ce-0.05):.2f});")

# 窓境界cont
def _cont_fix(tws):
    out = []
    for s in tws:
        m = re.match(r"tl\.fromTo\('(#[^']+)',\{[^}]*\},\{[^}]*\},([\-0-9.]+)\);\s*$", s)
        if m and float(m.group(2)) <= 0.02:
            out.append("tl.set('%s',{opacity:1,x:0,y:0,scale:1},0);" % m.group(1))
        else: out.append(s)
    return out
for _nm in ("bg_tws", "chap_tws", "pip_tws", "map_tws", "stat_tws", "vs_tws", "sub_tws"):
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
  :root{{--white:#fff;--yellow:#ffe23a;--red:#ff3a3a;--blue:#37c0ff;--gold:#e8b64c;--ink:#0a0c12;
    --edge:drop-shadow(4px 0 0 var(--ink)) drop-shadow(-4px 0 0 var(--ink)) drop-shadow(0 4px 0 var(--ink)) drop-shadow(0 -4px 0 var(--ink))
           drop-shadow(3px 3px 0 var(--ink)) drop-shadow(-3px 3px 0 var(--ink)) drop-shadow(0 8px 16px rgba(0,0,0,.8));
    --edsm:drop-shadow(0 0 2px var(--ink)) drop-shadow(1px 1px 1px var(--ink)) drop-shadow(0 2px 6px rgba(0,0,0,.85));}}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  #root{{position:absolute;inset:0;overflow:hidden;background:#05060a;font-family:"JPMed";}}
  .bgseg{{position:absolute;inset:0;opacity:0;overflow:hidden;}}
  .bgseg video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform:translateZ(0);backface-visibility:hidden;}}
  .veil{{position:absolute;inset:0;z-index:30;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,.45) 0%,transparent 20%,transparent 56%,rgba(0,0,0,.5) 84%,rgba(0,0,0,.78) 100%);}}
  .wm{{position:absolute;z-index:60;left:36px;top:30px;font-family:"JPHeavy";font-size:30px;color:#fff;letter-spacing:.04em;filter:var(--edsm);opacity:.9;}}
  .srclab{{position:absolute;z-index:55;left:40px;bottom:40px;font-family:"JPMed";font-size:23px;color:#eaeaea;opacity:0;background:rgba(0,0,0,.5);border-left:4px solid var(--gold);padding:6px 14px;border-radius:3px;filter:var(--edsm);}}
  .chaptag{{position:absolute;z-index:48;left:120px;top:37%;opacity:0;}}
  .chaptag .chnum{{font-family:"JPHeavy";font-size:40px;color:var(--gold);letter-spacing:.14em;filter:var(--edge);}}
  .chaptag .chttl{{font-family:"JPHeavy";font-size:76px;color:#fff;filter:var(--edge);margin-top:6px;white-space:nowrap;}}
  /* 試合映像PiP(枠付き中サイズ・右上) */
  .pipbox{{position:absolute;z-index:42;right:70px;top:150px;opacity:0;}}
  .pipframe{{width:1000px;height:562px;border:6px solid #fff;border-radius:10px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.7);background:#000;}}
  .pipframe video{{width:100%;height:100%;object-fit:cover;}}
  .piplabel{{position:absolute;left:0;bottom:-14px;background:var(--red);color:#fff;font-family:"JPHeavy";font-size:28px;padding:6px 20px;border-radius:6px;filter:var(--edsm);}}
  /* 規模マップ */
  .scalemap{{position:absolute;z-index:44;left:90px;top:230px;background:rgba(8,12,22,.9);border:2px solid #2a3a5a;border-radius:18px;padding:30px 40px;opacity:0;min-width:900px;}}
  .smttl{{font-family:"JPHeavy";font-size:42px;color:#fff;filter:var(--edsm);margin-bottom:20px;}}
  .smrow{{display:flex;align-items:center;gap:22px;margin:14px 0;}}
  .smtier{{font-family:"JPHeavy";font-size:30px;color:#9fd0ff;width:120px;}}
  .smorg{{font-family:"JPHeavy";font-size:44px;color:#fff;background:rgba(40,60,90,.8);padding:6px 24px;border-radius:10px;}}
  .smorg.big{{font-size:56px;color:#0a0c12;background:var(--gold);}}
  .smorg.sm{{font-size:32px;color:#cfe;background:rgba(40,60,90,.6);}}
  .smrow.hi .smorg{{background:var(--red);color:#fff;}}
  .smnote{{font-family:"JPHeavy";font-size:30px;color:var(--yellow);filter:var(--edsm);}}
  /* スタッツカード */
  .statcard{{position:absolute;z-index:44;right:80px;top:300px;background:rgba(8,12,22,.9);border:2px solid #2a3a5a;border-radius:16px;padding:26px 34px;opacity:0;min-width:560px;}}
  .statttl{{font-family:"JPHeavy";font-size:36px;color:var(--gold);margin-bottom:16px;}}
  .statrow{{display:flex;align-items:baseline;gap:18px;font-family:"JPMed";font-size:34px;color:#fff;margin:10px 0;}}
  .statrow b{{font-family:"JPHeavy";}} .statrow .sv{{font-family:"JPHeavy";font-size:42px;color:var(--yellow);}}
  .statrow .sv.warn{{color:var(--red);}}
  .statnote{{font-family:"JPMed";font-size:26px;color:#9fd0ff;margin-top:14px;}}
  /* VSカード */
  .vscard{{position:absolute;z-index:44;left:0;right:0;top:180px;display:flex;align-items:center;justify-content:center;gap:0;opacity:0;}}
  .vsimg{{height:620px;object-fit:contain;filter:drop-shadow(0 12px 30px rgba(0,0,0,.7));}}
  .vsmid{{display:flex;flex-direction:column;align-items:center;margin:0 -20px;z-index:2;}}
  .vsn{{font-family:"JPHeavy";font-size:52px;color:#fff;filter:var(--edge);}}
  .vsvs{{font-family:"JPHeavy";font-size:100px;color:var(--red);filter:var(--edge);margin:6px 0;}}
  /* 下部字幕 */
  .subt{{position:absolute;z-index:50;left:0;right:0;bottom:96px;text-align:center;opacity:0;font-family:"JPHeavy";font-size:46px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;}}
</style></head><body>
  <div id="root" data-composition-id="aori" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
{J(bg_divs,"    ")}
    {AUDIO_BLOCK}
{J(chap_audio,"    ")}
    <div class="veil"></div>
    <div class="wm">格闘ニュースラボ</div>
{J(src_divs,"    ")}
{J(chap_divs,"    ")}
{J(pip_divs,"    ")}
{J(map_divs,"    ")}
{J(stat_divs,"    ")}
{J(vs_divs,"    ")}
{J(sub_divs,"    ")}
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({{paused:true}});
{J(bg_tws)}
{J(chap_tws)}
{J(pip_tws)}
{J(map_tws)}
{J(stat_tws)}
{J(vs_tws)}
{J(sub_tws)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['aori'] = tl;
    </script>
  </div>
</body></html>"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} bg={len(bg_divs)} pip={len(pip_divs)} stats={len(stat_divs)} subs={sidx}")
