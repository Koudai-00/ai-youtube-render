"""カルシャガ・ダウトベック 完全解説 テンプレ(index.html)生成。ビート別背景セグメント＋
下部字幕(cue完全同期・DISP)＋章タグ(textfx風・3s hold・章SE)＋出典ラベル(bgセグ別)＋冒頭タイトル＋透かし。
窓env=HF_WIN_START/END/VISUAL_ONLY/HF_OUTNAME/HF_EXPORT_SFX。"""
from __future__ import annotations
import os, json, html, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "hyperframes" / "templates" / "dautbek"
TIM = json.load(open(ROOT / "subtitles" / "out" / "dautbek" / "timings.json", encoding="utf-8"))
CUES = TIM["cues"]; COMP = round(TIM["total"], 3)
# bgセグ計画(CI側も素材に含まれる bg_plan.json を読む)
_plan = json.load(open(TPL / "assets" / "bg_plan.json", encoding="utf-8"))
SRC_OF = {s["clip"]: s["src"] for s in _plan["segments"]}

# muxはローカルで行うため既定visual-only(CIはHF_WITH_AUDIO未設定=visual-only)
VISUAL_ONLY = os.environ.get("HF_WITH_AUDIO") != "1"
EXPORT_SFX = os.environ.get("HF_EXPORT_SFX") == "1"
W0 = float(os.environ.get("HF_WIN_START") or 0)
_w1 = os.environ.get("HF_WIN_END"); W1 = float(_w1) if _w1 else COMP
WIN = round(W1 - W0, 3)
OUTNAME = os.environ.get("HF_OUTNAME", "index.html")
def T(t): return round(t - W0, 3)
def OV(t0, t1): return (t1 > W0 + 0.05) and (t0 < W1 - 0.02)
def esc(s): return html.escape(s)

# ===== DISP: 読みかな→正式表記 =====
DISP = {
    "かるしゃがだうとべっく": "カルシャガ・ダウトベック", "だうとべっく": "ダウトベック",
    "しむけんと": "シムケント", "かざふすたん": "カザフスタン", "きるぎす": "キルギス",
    "しらっと": "シラット", "まれーしあ": "マレーシア",
    "あらしゅぷらいど": "Alash Pride", "ぴーえふえる": "PFL",
    "らいじんらんどまーく15": "RIZIN LANDMARK 15", "らんどまーく": "LANDMARK",
    "超らいじん5": "超RIZIN.5", "超らいじん4": "超RIZIN.4", "超らいじん3": "超RIZIN.3",
    "らいじん52": "RIZIN.52", "らいじん50": "RIZIN.50", "らいじん49": "RIZIN.49",
    "らいじん48": "RIZIN.48", "らいじん47": "RIZIN.47", "らいじん13": "RIZIN.13",
    "らいじん": "RIZIN",
    "あさくらみくる": "朝倉未来", "すずきちひろ": "鈴木千裕", "やーまん": "YA-MAN",
    "はぎわらきょうへい": "萩原京平", "きのしたからて": "木下カラテ", "せきてつや": "関鉄矢",
    "まつしまこよみ": "松嶋こよみ", "くぼゆうた": "久保優太", "ひらもとれん": "平本蓮",
    "しぇいどぅらえふ": "シェイドゥラエフ", "あきもときょうま": "秋元強真",
    "ふくだりゅうや": "福田龍彌", "もとやゆうき": "元谷友貴", "おうぎくぼひろまさ": "扇久保博正",
    "あめりかんとっぷちーむ": "アメリカン・トップチーム", "きょうせらどーむおおさか": "京セラドーム大阪",
    "いごーりじるこふ": "イゴーリ・ジルコフ", "ノックアウト": "KO", "しっしん": "失神",
    "きょくしん": "極真", "むえたい": "ムエタイ", "とうきょう": "東京",
}
def disp(t):
    for k in sorted(DISP, key=len, reverse=True): t = t.replace(k, DISP[k])
    return t
def zwidth(s): return sum(0.55 if (c.isascii() and (c.isalnum() or c in " .,'-%")) else 1.0 for c in s)
def sub_lines(text, maxw=25.0):
    if zwidth(text) <= maxw: return [text]
    segs = [s for s in re.split("(?<=、)", text) if s]
    if len(segs) > 1:
        for i in range(1, len(segs)):
            a = "".join(segs[:i]); b = "".join(segs[i:])
            if zwidth(a) <= maxw and zwidth(b) <= maxw: return [a, b]
    # 助詞境界で2分割
    best=None
    for i in range(1,len(text)):
        if text[i-1] in "はがをにでとへものだ":
            a,b=text[:i],text[i:]
            if zwidth(a)<=maxw and zwidth(b)<=maxw:
                if best is None or abs(zwidth(a)-zwidth(b))<abs(zwidth(best[0])-zwidth(best[1])): best=(a,b)
    return list(best) if best else [text]

# ===== 出典ラベル(clip→引用元) =====
SRCLAB = {
  "asakura_rizin13":"出典: RIZIN公式 RIZIN.13", "seki_rizin47":"出典: RIZIN公式 RIZIN.47",
  "kinoshita_rizin48":"出典: RIZIN公式 RIZIN.48", "yaman_rizin49":"出典: RIZIN公式 RIZIN.49",
  "suzuki_rizin50":"出典: RIZIN公式 RIZIN.50", "hagiwara_lm15":"出典: RIZIN公式 RIZIN LANDMARK 15",
  "matsushima_topbrights":"出典: TOP BRIGHTS", "zhirkov_rcc":"出典: RCC: MMA & Boxing",
  "silat_malaysia":"出典: nurik 777（シラット世界大会）", "alash_yousefi":"出典: Alash Pride TV",
  "alash_neres":"出典: Alash Pride TV", "kazakh_feature":"出典: Қазақ Батырлары",
  "ow13_a":"出典: RIZIN公式 RIZIN.13 前日公開計量",
  "o47_a":"出典: RIZIN公式 試合後インタビュー / RIZIN.47",
  "o47_b":"出典: RIZIN公式 試合後インタビュー / RIZIN.47",
  "o47_c":"出典: RIZIN公式 試合後インタビュー / RIZIN.47",
  "o47_d":"出典: RIZIN公式 試合後インタビュー / RIZIN.47",
  "o47_e":"出典: RIZIN公式 試合後インタビュー / RIZIN.47",
  "o48_a":"出典: RIZIN公式 試合後インタビュー 前編 / RIZIN.48",
  "o50_a":"出典: RIZIN公式 試合後インタビュー / RIZIN.50",
  "o50_b":"出典: RIZIN公式 試合後インタビュー / RIZIN.50",
  "o50_c":"出典: RIZIN公式 試合後インタビュー / RIZIN.50",
  "o50_d":"出典: RIZIN公式 試合後インタビュー / RIZIN.50",
  "o50_e":"出典: RIZIN公式 試合後インタビュー / RIZIN.50",
  "lm15_a":"出典: RIZIN公式 LANDMARK 15 試合前インタビュー",
  "lm15_b":"出典: RIZIN公式 LANDMARK 15 試合前インタビュー",
  "lm15_c":"出典: RIZIN公式 LANDMARK 15 試合前インタビュー",
  "sr4_a":"出典: RIZIN公式 Karshyga Dautbek Interview",
  "sr4_b":"出典: RIZIN公式 Karshyga Dautbek Interview",
  "sr4_c":"出典: RIZIN公式 Karshyga Dautbek Interview",
  "card_dautbek_hiramoto":"出典: RIZIN公式 超RIZIN.5 対戦カード", "card_kv":"出典: RIZIN公式 超RIZIN.5 大会キービジュアル",
  "card_sr4_akimoto":"出典: RIZIN公式 超RIZIN.4 対戦カード", "card_r52_fukuda":"出典: RIZIN公式 RIZIN.52 対戦カード",
  "kaiken_sr5":"出典: RIZIN公式 超RIZIN.5 対戦カード発表記者会見",
}
# ---- 背景セグメント(1ビート=1セグメント。章タグは次セクションの背景に載せる) ----
_first, _chap_beat = {}, {}
for c in CUES:
    _first.setdefault(c["base_id"], c["start"])
    if c["chapter"]: _chap_beat.setdefault(c["base_id"], True)
BEAT_IDS = list(_first)
_starts = [max(0.0, _first[b] - 0.15) if b in _chap_beat else _first[b] for b in BEAT_IDS]
_starts[0] = 0.0            # ★冒頭を黒で始めない
BG_SEG = []
for i, b in enumerate(BEAT_IDS):
    t1 = _starts[i + 1] + 0.08 if i + 1 < len(BEAT_IDS) else COMP
    BG_SEG.append((round(_starts[i], 3), round(t1, 3), b))

import subprocess
_dcache = {}
def clip_dur(fn):
    if fn in _dcache: return _dcache[fn]
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(TPL / "assets" / "bgvid" / f"{fn}.mp4")],
                       capture_output=True, text=True)
    try: v = float(r.stdout.strip())
    except: v = 0.0
    _dcache[fn] = v; return v
def is_card(fn): return SRC_OF.get(fn, "").startswith("card_")
def srcof(fn):   return SRCLAB[SRC_OF[fn]]

# ===== 章 =====
_ch_raw = [(c["chapter"], c["start"]) for c in CUES if c["chapter"]]
CHAPS = []                       # ★同名の章タグが連続で二重表示されるのを防ぐ
for _t, _s in _ch_raw:
    if CHAPS and CHAPS[-1][0] == _t: continue
    CHAPS.append((_t, _s))

# ===== 冒頭タイトル(0.3〜10.5) =====
TITLE = [("7年間 無敗", 0.9, "y"), ("キング・オブ・カザフスタン", 1.5, "r")]

# ===== SFX events(mux用) =====
def build_sfx():
    ev = [{"t": 1.2, "kind": "open"}]
    for ch, cst in CHAPS:
        if cst < 6.0: continue
        ev.append({"t": round(cst + 0.05, 2), "kind": "chap"})
    return sorted(ev, key=lambda e: e["t"])
if EXPORT_SFX:
    (TPL / "sfx_events.json").write_text(json.dumps(build_sfx(), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"exported sfx_events.json"); raise SystemExit(0)

# ===== 背景(ビート別セグメント・piece終端まで延長で黒対策) =====
bg_divs, tws, src_divs = [], [], []
for i, (t0, t1, fn) in enumerate(BG_SEG):
    if not OV(t0, t1): continue
    bid = f"bg{i}"; vt0, vt1 = T(t0), T(t1)
    cont = vt0 <= 0.02
    cd = clip_dur(fn)
    ms = max(0.0, W0 - t0); ds = max(0.0, vt0)
    dur = (W1 - max(t0, W0)) + 0.6          # ★piece終端まで延長
    lead = min(1.5, ds)
    if lead > 0: ds -= lead; dur += lead
    if cd > 0 and ms + dur > cd - 0.03: dur = max(0.3, cd - ms - 0.05)
    inner = (f'<video id="{bid}-v" src="assets/bgvid/{fn}.mp4" muted playsinline data-layout-allow-overflow '
             f'data-start="{ds:.2f}" data-duration="{dur:.2f}" data-media-start="{ms:.2f}" data-track-index="{10+i}"></video>')
    op = ";opacity:1" if cont else ""
    bg_divs.append(f'<div class="bgseg" id="{bid}" style="z-index:{i+1}{op}">{inner}</div>')
    if cont: tws.append(f"tl.set('#{bid}',{{opacity:1}},0);")
    else: tws.append(f"tl.fromTo('#{bid}',{{opacity:0}},{{opacity:1,duration:.45,ease:'power1.inOut'}},{vt0:.2f});")
    if is_card(fn):
        kbd = min(t1, W1) - max(t0, W0) + 0.4
        tws.append(f"tl.fromTo('#{bid}-v',{{scale:1.0}},{{scale:1.08,duration:{kbd:.2f},ease:'none'}},{max(0.0,vt0):.2f});")
    if min(t1, W1) - max(t0, W0) > 0.6:
        sid = f"src{i}"
        src_divs.append(f'<div class="srclab" id="{sid}">{esc(srcof(fn))}</div>')
        tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{max(0.0,vt0+0.3):.2f});")
        tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{vt1-0.25:.2f});")

# 冒頭タイトル(暗アリーナ背景の区間0.3〜5.2のみ=顔被り回避)
title_divs = []
if OV(0.3, 5.4):
    rows = "".join(f'<div class="ttlrow {c}">{esc(txt)}</div>' for txt, _, c in TITLE)
    title_divs.append(f'<div class="bigtitle" id="bigttl">{rows}</div>')
    for j,(txt,dl,c) in enumerate(TITLE):
        tws.append(f"tl.fromTo('#bigttl .ttlrow:nth-child({j+1})',{{opacity:0,y:60}},{{opacity:1,y:0,duration:.6,ease:'power3.out'}},{T(0.3)+dl:.2f});")
    tws.append(f"tl.to('#bigttl',{{opacity:0,duration:.4}},{T(4.9):.2f});")

# 章タグ
chap_divs = []
for j,(ch,cst) in enumerate(CHAPS):
    if cst < 6.0: continue          # ★冒頭は大タイトルを出すので章タグを重ねない
    if not OV(cst, cst+3.6): continue
    cid=f"chap{j}"
    chap_divs.append(f'<div class="chaptag" id="{cid}"><div class="chnum">CHAPTER {j+1:02d}</div><div class="chttl">{esc(ch)}</div></div>')
    a=max(0.0,T(cst));
    tws.append(f"tl.fromTo('#{cid} .chnum',{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.5,ease:'power3.out'}},{a+0.05:.2f});")
    tws.append(f"tl.fromTo('#{cid} .chttl',{{opacity:0,y:40}},{{opacity:1,y:0,duration:.6,ease:'power3.out'}},{a+0.2:.2f});")
    tws.append(f"tl.to('#{cid}',{{opacity:0,duration:.4}},{T(cst)+3.4:.2f});")

# 章SE(mux)
chap_audio = []
if not VISUAL_ONLY:
    for j,(ch,cst) in enumerate(CHAPS):
        if OV(cst, cst+1.0):
            chap_audio.append(f'<audio id="chs{j}" src="assets/se/se_impact.mp3" data-start="{T(cst+0.05):.2f}" data-track-index="{200+j}" data-volume="0.5"></audio>')

# 下部字幕
def split_chunks(disp_text, maxw=24.0):
    """disp済みテキストを読点境界で1行チャンク(<=maxw)にまとめる。発話追従用。
    末尾の極小チャンクは孤立させず直前へ吸収(不自然な区切り防止・video-production.md準拠)。"""
    parts = [p for p in re.split("(?<=、)", disp_text) if p]
    chunks, cur = [], ""
    for p in parts:
        if not cur or zwidth(cur + p) <= maxw: cur += p
        else: chunks.append(cur); cur = p
    if cur: chunks.append(cur)
    while len(chunks) >= 2 and zwidth(chunks[-1]) <= 7 and zwidth(chunks[-2] + chunks[-1]) <= maxw * 1.6:
        _tail = chunks.pop()
        chunks[-1] += _tail
    return chunks or [disp_text]

sub_divs = []
_si = 0
for c in CUES:
    cs, ce = c["start"], c["end"]
    chunks = split_chunks(disp(c["text"]))
    tot = sum(zwidth(x) for x in chunks) or 1.0
    span = ce - cs; t = cs
    for ch in chunks:
        cw = zwidth(ch); c0 = t; c1 = t + span * (cw / tot); t = c1
        if not OV(c0, c1): continue
        inner = "<br>".join(esc(l) for l in sub_lines(ch))
        did = f"sub{_si}"; _si += 1
        sub_divs.append(f'<div class="subt" id="{did}">{inner}</div>')
        tws.append(f"tl.fromTo('#{did}',{{opacity:0}},{{opacity:1,duration:.14}},{max(0.0,T(c0)):.2f});")
        tws.append(f"tl.to('#{did}',{{opacity:0,duration:.1}},{T(c1-0.04):.2f});")

# 窓境界cont
def cont_fix(items):
    out=[]
    for s in items:
        m=re.match(r"tl\.fromTo\('(#[^']+)',\{[^}]*\},\{[^}]*\},([\-0-9.]+)\);\s*$", s)
        if m and float(m.group(2))<=0.02:
            out.append("tl.set('%s',{opacity:1,x:0,y:0,scale:1},0);" % m.group(1))
        else: out.append(s)
    return out
tws = cont_fix(tws)

def J(items, ind="      "): return "\n".join(ind+x for x in items)
AUDIO_BLOCK = ("" if VISUAL_ONLY else
    '<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="60" data-volume="1"></audio>\n'
    '    <audio id="bgm" src="assets/audio/bgm.mp3" data-start="0" data-track-index="61" data-volume="0.07"></audio>')

HTML = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
  @font-face{{font-family:"Mincho";src:url("assets/fonts/GokubutoMincho.ttf");}}
  @font-face{{font-family:"JPHeavy";src:url("assets/fonts/SourceHanSansJP-Heavy.otf");}}
  @font-face{{font-family:"JPMed";src:url("assets/fonts/SourceHanSansJP-Medium.otf");}}
  :root{{--white:#fff;--yellow:#ffe23a;--red:#ff5a3a;--blue:#37c0ff;--gold:#e8b64c;--ink:#0a0c12;
    --edge:drop-shadow(4px 0 0 var(--ink)) drop-shadow(-4px 0 0 var(--ink)) drop-shadow(0 4px 0 var(--ink)) drop-shadow(0 -4px 0 var(--ink)) drop-shadow(3px 3px 0 var(--ink)) drop-shadow(0 8px 16px rgba(0,0,0,.8));
    --edsm:drop-shadow(0 0 2px var(--ink)) drop-shadow(1px 1px 1px var(--ink)) drop-shadow(0 2px 6px rgba(0,0,0,.85));}}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  #root{{position:absolute;inset:0;overflow:hidden;background:#05060a;font-family:"JPMed";}}
  .bgseg{{position:absolute;inset:0;opacity:0;overflow:hidden;}}
  .bgseg video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform:translateZ(0);backface-visibility:hidden;}}
  .veil{{position:absolute;inset:0;z-index:30;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,.5) 0%,transparent 20%,transparent 55%,rgba(0,0,0,.52) 82%,rgba(0,0,0,.8) 100%);}}
  .wm{{position:absolute;z-index:60;left:36px;top:26px;font-family:"JPHeavy";font-size:27px;color:#fff;letter-spacing:.03em;filter:var(--edsm);opacity:.85;}}
  .srclab{{position:absolute;z-index:55;left:40px;bottom:22px;font-family:"JPMed";font-size:22px;color:#eaeaea;opacity:0;background:rgba(0,0,0,.5);border-left:4px solid var(--gold);padding:6px 14px;border-radius:3px;filter:var(--edsm);}}
  .chaptag{{position:absolute;z-index:48;left:120px;top:34%;opacity:0;}}
  .chaptag .chnum{{font-family:"JPHeavy";font-size:38px;color:var(--gold);letter-spacing:.14em;filter:var(--edge);}}
  .chaptag .chttl{{font-family:"Mincho";font-weight:900;font-size:82px;color:#fff;filter:var(--edge);margin-top:8px;white-space:nowrap;}}
  .bigtitle{{position:absolute;z-index:49;left:0;right:0;top:30%;text-align:center;}}
  .bigtitle .ttlrow{{font-family:"Mincho";font-weight:900;font-size:96px;line-height:1.16;filter:var(--edge);opacity:0;white-space:nowrap;}}
  .bigtitle .ttlrow.y{{color:var(--yellow);}} .bigtitle .ttlrow.r{{color:#fff;}}
  .subt{{position:absolute;z-index:50;left:0;right:0;bottom:104px;text-align:center;opacity:0;font-family:"JPHeavy";font-size:46px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;}}
</style></head><body>
  <div id="root" data-composition-id="dautbek" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
{J(bg_divs,"    ")}
    {AUDIO_BLOCK}
{J(chap_audio,"    ")}
    <div class="veil"></div>
    <div class="wm">格闘ニュースラボ</div>
{J(src_divs,"    ")}
{J(title_divs,"    ")}
{J(chap_divs,"    ")}
{J(sub_divs,"    ")}
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({{paused:true}});
{J(tws)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['dautbek'] = tl;
    </script>
  </div>
</body></html>"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} src={len(src_divs)} chap={len(chap_divs)} subs={len(sub_divs)}/{len(CUES)}")
