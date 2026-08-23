"""ドンマイ川端 テンプレ(index.html)生成。単一bg動画(kawabata_bg_full.mp4)＋
下部字幕(cue完全同期・DISP)＋章タグ(textfx風・3s hold・章SE)＋出典ラベル(bgセグ別)＋冒頭タイトル＋透かし。
窓env=HF_WIN_START/END/VISUAL_ONLY/HF_OUTNAME/HF_EXPORT_SFX。"""
from __future__ import annotations
import os, json, html, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "hyperframes" / "templates" / "kawabata"
TIM = json.load(open(ROOT / "subtitles" / "out" / "kawabata" / "timings.json", encoding="utf-8"))
CUES = TIM["cues"]; COMP = round(TIM["total"], 3)
# bgセグ計画(CI側は素材に含まれる bg_plan.json を読む。ローカルはビルダーが生成済み)
_plan = json.load(open(TPL / "assets" / "bg_plan.json", encoding="utf-8"))
SEGS = [(s["t0"], s["clip"], 0, "") for s in _plan["segments"]]

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
    "どんまい、かわばた": "ドンマイ川端", "どんまいかわばた": "ドンマイ川端", "かわばたりゅう": "川端龍",
    "たかとうなおひさ": "髙藤直寿", "こうどうかんはい": "講道館杯", "こくしかんだいがく": "国士舘大学",
    "とみざわだいち": "冨澤大智", "あさくらかい": "朝倉海", "あさくらみくる": "朝倉未来", "ひろや": "ヒロヤ",
    "ぶれいきんぐだうん": "ブレイキングダウン", "きょうせらどーむ": "京セラドーム",
    "すーぱーらいじん、ファイブ": "超RIZIN.5", "すーぱーらいじん": "超RIZIN", "らいじん": "RIZIN",
    "とよなか": "豊中", "とよはし": "豊橋", "つくばだいがく": "筑波大学",
    "きんきだいがくふぞくひろしまこうこうふくやまこう": "近畿大学附属広島高校福山校",
    "よしだひでひこ": "吉田秀彦", "ロンダラウジー": "ロンダ・ラウジー",
    "あおきしんや": "青木真也", "わたなべかな": "渡辺華奈", "やすいひゅうま": "安井飛馬",
    "ウデヒシギジュウジガタメ": "腕ひしぎ十字固め",
    # 単独キー(分割cue対策・長キー優先でマッチするので安全)
    "どんまい": "ドンマイ", "かわばた": "川端", "とみざわ": "冨澤",
    "ゆーちゅーぶ": "YouTube", "ユーチューブ": "YouTube", "ユーチューバー": "YouTuber",
    "かいは": "海は", "かいと": "海と", "かいも": "海も", "かいが": "海が", "かいの": "海の", "かいに": "海に",
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
  "nanimono":"出典: ORICON NEWS(YouTube)","kao16":"出典: 講道館杯2011(YouTube)","judo":"出典: 川端龍 柔道映像(YouTube)",
  "recap":"出典: ドンマイ川端(YouTube)","yameyou":"出典: ドンマイ川端(YouTube)","sr5sel":"出典: 朝倉海 KAI Channel(YouTube)",
  "collab2":"出典: 朝倉海 KAI Channel(YouTube)","aboutkai":"出典: ドンマイ川端(YouTube)","bd8":"出典: BreakingDown公式(YouTube)",
  "aoki":"出典: ONE Championship(YouTube)","watanabe":"出典: RIZIN公式(YouTube)","yasui":"出典: U-NEXT格闘技(YouTube)",
  "yoshida":"出典: PRIDE(YouTube)","rousey":"出典: UFC/YouTube","tomizawa":"出典: RIZIN公式(YouTube)",
  "card":"出典: RIZIN公式サイト",
  "takato_ipp":"出典: 講道館杯2011(YouTube)","ippon2":"出典: グランドスラム東京2011(YouTube)",
  "zennihon_a":"出典: 全日本柔道(YouTube)","zennihon_b":"出典: 全日本柔道(YouTube)",
  "gs_finals":"出典: グランドスラム東京2011(YouTube)",
  "m_arena":"イメージ映像(Pexels)","m_rain":"イメージ映像(Pexels)","m_osaka":"イメージ映像(Pexels)",
  "m_lonely":"イメージ映像(Pexels)","m_train":"イメージ映像(Pexels)","m_sun":"イメージ映像(Pexels)",
  "m_crowd":"イメージ映像(Pexels)","m_room":"イメージ映像(Pexels)","m_medal":"イメージ映像(Pexels)",
  "m_kids":"イメージ映像(Pexels)","m_resolve":"イメージ映像(Pexels)","m_school":"イメージ映像(Pexels)",
  "m_spotlight":"イメージ映像(Pexels)","m_wtrain":"イメージ映像(Pexels)","m_storm":"イメージ映像(Pexels)",
}
# bgセグメント絶対時刻レンジ + 出典(連続同一はまとめる)
SEG_ABS = []
for i, s in enumerate(SEGS):
    t0 = s[0]; t1 = SEGS[i+1][0] if i+1 < len(SEGS) else COMP
    SEG_ABS.append((t0, t1, SRCLAB[s[1]]))
SRC_RANGES = []
for t0, t1, lab in SEG_ABS:
    if SRC_RANGES and SRC_RANGES[-1][2] == lab and abs(SRC_RANGES[-1][1]-t0) < 0.01:
        SRC_RANGES[-1] = (SRC_RANGES[-1][0], t1, lab)
    else:
        SRC_RANGES.append((t0, t1, lab))

# ===== 章 =====
CHAPS = [(c["chapter"], c["start"]) for c in CUES if c["chapter"]]

# ===== 冒頭タイトル(0.3〜10.5) =====
TITLE = [("柔道日本一の男が", 0.9, "y"), ("36歳でMMAへ", 1.5, "r")]

# ===== SFX events(mux用) =====
def build_sfx():
    ev = [{"t": 1.2, "kind": "open"}]
    for ch, cst in CHAPS:
        ev.append({"t": round(cst + 0.05, 2), "kind": "chap"})
    return sorted(ev, key=lambda e: e["t"])
if EXPORT_SFX:
    (TPL / "sfx_events.json").write_text(json.dumps(build_sfx(), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"exported sfx_events.json"); raise SystemExit(0)

# ===== 背景(窓別bg動画・aori方式) =====
bg_divs, tws = [], []
_MAXW = int((COMP - 0.01) // 60)
_wi = min(_MAXW, int((W0 + 1.5) // 60)); _fstart = max(0.0, _wi * 60 - 1.5); _media = round(W0 - _fstart, 3)
_bgdur = WIN + 0.6
bg_divs.append('<div class="bgseg" id="bgmain" style="z-index:1;opacity:1">'
               f'<video id="bgmain-v" src="assets/bgvid/kawabata_bg_w{_wi}.mp4" muted playsinline '
               f'data-start="0" data-duration="{_bgdur:.2f}" data-media-start="{_media:.3f}" data-track-index="10"></video></div>')
tws.append("tl.set('#bgmain',{opacity:1},0);")

# 出典ラベル
src_divs = []
for i, (t0, t1, lab) in enumerate(SRC_RANGES):
    if not OV(t0, t1): continue
    sid = f"src{i}"
    src_divs.append(f'<div class="srclab" id="{sid}">{esc(lab)}</div>')
    tws.append(f"tl.fromTo('#{sid}',{{opacity:0}},{{opacity:1,duration:.4}},{max(0.0,T(t0)+0.3):.2f});")
    tws.append(f"tl.to('#{sid}',{{opacity:0,duration:.3}},{T(t1)-0.2:.2f});")

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
    """disp済みテキストを、、境界で1行チャンク(<=maxw)にまとめる。発話追従用。"""
    parts = [p for p in re.split("(?<=、)", disp_text) if p]
    chunks, cur = [], ""
    for p in parts:
        if not cur or zwidth(cur + p) <= maxw: cur += p
        else: chunks.append(cur); cur = p
    if cur: chunks.append(cur)
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
  .srclab{{position:absolute;z-index:55;left:40px;bottom:26px;font-family:"JPMed";font-size:22px;color:#eaeaea;opacity:0;background:rgba(0,0,0,.5);border-left:4px solid var(--gold);padding:6px 14px;border-radius:3px;filter:var(--edsm);}}
  .chaptag{{position:absolute;z-index:48;left:120px;top:34%;opacity:0;}}
  .chaptag .chnum{{font-family:"JPHeavy";font-size:38px;color:var(--gold);letter-spacing:.14em;filter:var(--edge);}}
  .chaptag .chttl{{font-family:"Mincho";font-weight:900;font-size:82px;color:#fff;filter:var(--edge);margin-top:8px;white-space:nowrap;}}
  .bigtitle{{position:absolute;z-index:49;left:0;right:0;top:30%;text-align:center;}}
  .bigtitle .ttlrow{{font-family:"Mincho";font-weight:900;font-size:96px;line-height:1.16;filter:var(--edge);opacity:0;white-space:nowrap;}}
  .bigtitle .ttlrow.y{{color:var(--yellow);}} .bigtitle .ttlrow.r{{color:#fff;}}
  .subt{{position:absolute;z-index:50;left:0;right:0;bottom:100px;text-align:center;opacity:0;font-family:"JPHeavy";font-size:46px;line-height:1.34;color:#fff;filter:var(--edge);letter-spacing:.01em;white-space:pre-line;}}
</style></head><body>
  <div id="root" data-composition-id="kawabata" data-start="0" data-duration="{WIN}" data-width="1920" data-height="1080">
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
      window.__timelines['kawabata'] = tl;
    </script>
  </div>
</body></html>"""
(TPL / OUTNAME).write_text(HTML, encoding="utf-8")
print(f"wrote {OUTNAME} win=[{W0},{W1}] dur={WIN}s vo={VISUAL_ONLY} src={len(src_divs)} chap={len(chap_divs)} subs={len(sub_divs)}/{len(CUES)}")
