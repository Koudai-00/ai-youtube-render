"""AJ・マッキー完全解説 横テンプレ(1920x1080)生成【評伝型・ナレ一致キュレーション】。
suzuki-chihiro 方式を踏襲: 背景=セクション別意味順リスト＋PIN同期、textfxカード、DOM字幕(DISP変換)、
章別BGM埋め込み、時間分割レンダー対応(HF_WIN_START/END, cont/cont_end)。
字幕はナレ読みかな→正式表記へDISP変換（読みかな残留禁止ルール対応）。
"""
from __future__ import annotations
import json, os, sys, subprocess
from collections import Counter
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=None)
def clip_dur(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "hyperframes" / "templates" / "shaydullaev"
TIM = json.loads((ROOT / "subtitles" / "out" / "shaydullaev" / "timings.json").read_text(encoding="utf-8"))
BEATS = TIM["beats"]
SECS = {s["sec"]: s for s in TIM["sections"]}
SECORDER = [s["sec"] for s in TIM["sections"]]
TOTAL = TIM["total"]
DUR = round(TOTAL + 0.6, 2)

WIN_START = float(os.environ.get("HF_WIN_START", "0") or "0")
WIN_END = float(os.environ.get("HF_WIN_END", "0") or "0")
WINDOWED = "HF_WIN_START" in os.environ or "HF_WIN_END" in os.environ
if not WINDOWED:
    WIN_START, WIN_END = 0.0, DUR

sys.path.insert(0, str(Path(__file__).resolve().parent))
from card_fit import check_card_widths  # noqa: E402


def _norm(s: str) -> str:
    return s.replace("、", "").replace("。", "").replace(" ", "").replace("　", "")


def beat_at(sub: str):
    nsub = _norm(sub)
    for b in BEATS:
        if nsub in _norm(b["text"]):
            return b
    raise SystemExit(f"BEAT NOT FOUND for anchor: {sub}")


TEMPLATE = r"""<!doctype html>
<!-- シェイドゥラエフ 完全解説 1920x1080【評伝型】 -->
<html>
<head>
<meta charset="utf-8" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script>__TEXTFX_JS__</script>
<style>
__TEXTFX_CSS__
  @font-face { font-family:"Mincho"; src:url("assets/fonts/GokubutoMincho.ttf") format("truetype"); font-weight:900; font-display:block; }
  @font-face { font-family:"JPHeavy"; src:url("assets/fonts/SourceHanSansJP-Heavy.otf") format("opentype"); font-weight:900; font-display:block; }
  @font-face { font-family:"JPMed"; src:url("assets/fonts/SourceHanSansJP-Medium.otf") format("opentype"); font-weight:500; font-display:block; }
  * { box-sizing:border-box; margin:0; padding:0; }
  html,body { width:100%; height:100%; background:#000; overflow:hidden; }
  #root { position:relative; width:1920px; height:1080px; overflow:hidden; background:#050507; font-family:"JPHeavy","Noto Sans JP",sans-serif; color:#fff; }

  .bgvid { position:absolute; inset:0; z-index:1; opacity:0; overflow:hidden; will-change:opacity,transform; }
  .bgvid video { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }

  .veil { position:absolute; inset:0; z-index:5; pointer-events:none; background:linear-gradient(180deg, rgba(0,0,0,.42) 0%, rgba(0,0,0,.05) 18%, rgba(0,0,0,.02) 50%, rgba(0,0,0,.36) 80%, rgba(0,0,0,.72) 100%); }
  .vignette { position:absolute; inset:0; z-index:6; pointer-events:none; background:radial-gradient(ellipse at 50% 44%, transparent 0 60%, rgba(0,0,0,.42) 100%); }
  .scan { position:absolute; inset:0; z-index:7; opacity:.04; pointer-events:none; mix-blend-mode:overlay; background:repeating-linear-gradient(0deg, rgba(255,255,255,.5) 0 1px, transparent 1px 4px); }

  .tag { position:absolute; z-index:20; left:60px; top:58px; padding:8px 22px 8px 18px; background:rgba(8,9,12,.56); border-left:4px solid #e7b94a; border-radius:2px; font-family:"Mincho",serif; font-size:33px; font-weight:900; letter-spacing:.05em; color:#fff; text-shadow:0 0 2px #000,0 2px 8px rgba(0,0,0,.9); white-space:nowrap; opacity:0; -webkit-backdrop-filter:blur(7px); backdrop-filter:blur(7px); }
  .badge { position:absolute; z-index:20; right:62px; top:60px; padding:10px 24px; background:rgba(8,8,10,.84); border:2px solid rgba(255,213,74,.9); border-radius:40px; font-family:"JPHeavy"; font-size:28px; color:#ffe89a; letter-spacing:.04em; text-shadow:0 1px 3px rgba(0,0,0,.9); }
  .src { position:absolute; z-index:20; left:40px; bottom:22px; padding:3px 10px; background:rgba(0,0,0,.62); border-left:3px solid rgba(255,213,74,.85); border-radius:2px; font-family:"JPMed"; font-size:17px; color:#dcdcdc; letter-spacing:.01em; text-shadow:0 1px 2px rgba(0,0,0,.9); opacity:0; }

  .cardpos { position:absolute; z-index:18; left:50%; transform:translate(-50%,-50%); text-align:center; opacity:0; }
  .pos-mid { top:42%; } .pos-low { top:66%; }
  .cardpos .cblur { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); width:168%; height:260%; z-index:-1; pointer-events:none; border-radius:30px; -webkit-backdrop-filter:blur(16px) brightness(.46) saturate(.9); backdrop-filter:blur(16px) brightness(.46) saturate(.9); -webkit-mask-image:radial-gradient(ellipse at 50% 50%, #000 48%, transparent 78%); mask-image:radial-gradient(ellipse at 50% 50%, #000 48%, transparent 78%); }
  .cardwrap { display:inline-block; }
  .cardwrap .csub { display:inline-block; margin-bottom:.40em; color:#ffd76a; font-family:"JPHeavy"; letter-spacing:.18em; text-shadow:0 0 2px #000,0 2px 8px rgba(0,0,0,.95); }
  .cardwrap .cl1 { display:inline-block; white-space:nowrap; margin-bottom:.18em; color:#ffd76a; letter-spacing:.06em; font-family:"JPHeavy"; text-shadow:0 0 2px #000,0 2px 9px rgba(0,0,0,.95); }
  .cardwrap .cmain { line-height:1.06; white-space:nowrap; letter-spacing:.01em; }
  .gmincho { font-family:"Mincho",serif; font-weight:900; color:#fff; text-shadow: 0 0 1px #000, 2px 0 1px #000, -2px 0 1px #000, 0 2px 1px #000, 0 -2px 1px #000, 0 0 11px rgba(0,0,0,.95), 0 5px 18px rgba(0,0,0,.9), 0 0 32px rgba(0,0,0,.65); }
  .gaccent { color:#ff5a4d; }

  #openLayer { position:absolute; inset:0; z-index:22; pointer-events:none; }
  .op-kicker { position:absolute; left:50%; top:29%; transform:translateX(-50%); opacity:0; white-space:nowrap; }
  .op-kicker span { display:inline-block; font-size:34px; letter-spacing:.34em; padding:.16em 1em; }
  .op-title { position:absolute; left:50%; top:43%; transform:translate(-50%,-50%); text-align:center; }
  .op-title .l1 { font-size:118px; line-height:1.0; letter-spacing:.04em; white-space:nowrap; }
  .op-title .uline { margin:22px auto 0; }
  .op-kw { position:absolute; left:0; right:0; top:362px; text-align:center; font-size:88px; letter-spacing:.04em; white-space:nowrap; opacity:0; }
  .op-kw .kwin { display:inline-block; transform-origin:center center; }
  .op-kw em { font-style:normal; }
  /* A2: 「18連勝」等の縁取りが太すぎるのを是正=外向き縁を細い版に（scoped） */
  .op-kw .tfx-outline, .op-kw .tfx-fire, .op-kw .kwin { filter: var(--tfx-edge-sm); }
  .op-stat { position:absolute; left:0; right:0; top:336px; text-align:center; opacity:0; }
  .op-stat .s1 { font-size:34px; letter-spacing:.2em; }
  .op-stat .s2 { margin-top:8px; font-size:120px; line-height:.96; }
  .op-stat .s2 em { font-style:normal; color:#ff4654; }

  #chapLayer { position:absolute; inset:0; z-index:25; pointer-events:none; }
  .chap { position:absolute; inset:0; opacity:0; }
  .chap .cfull { position:absolute; inset:0; -webkit-backdrop-filter:blur(24px) brightness(.38) saturate(.85); backdrop-filter:blur(24px) brightness(.38) saturate(.85); background:rgba(4,5,8,.28); }
  .chap .cinner { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); text-align:center; }
  .chap .csub2 { font-family:"Mincho",serif; font-weight:900; font-size:62px; letter-spacing:.1em; color:#ffce2e; text-shadow:0 0 2px #000,2px 2px 1px #000,-2px 2px 1px #000,0 4px 14px rgba(0,0,0,.92); margin-bottom:.16em; white-space:nowrap; }
  .chap .ctitle { font-family:"Mincho",serif; font-weight:900; font-size:170px; line-height:1.0; letter-spacing:.04em; color:#fff; white-space:nowrap; text-shadow: 0 0 2px #000,3px 0 2px #000,-3px 0 2px #000,0 3px 2px #000,0 -3px 2px #000,0 0 16px rgba(0,0,0,.95),0 9px 30px rgba(0,0,0,.9); }
  .chap .cline { width:0; height:5px; margin:26px auto 0; background:linear-gradient(90deg,transparent,#ffce2e 25%,#ffce2e 75%,transparent); border-radius:3px; }

  #capLayer { position:absolute; inset:0; z-index:17; pointer-events:none; }
  .cap { position:absolute; left:50%; bottom:116px; transform:translateX(-50%); width:1760px; text-align:center; opacity:0; }
  .cap .cl { display:inline-block; max-width:1760px; font-family:"JPHeavy"; font-weight:900; font-size:46px; line-height:1.32; color:#fff; white-space:nowrap; letter-spacing:.005em; paint-order:stroke fill; -webkit-text-stroke:5.5px #000; text-shadow:0 3px 7px rgba(0,0,0,.92); }
</style>
</head>
<body>
  <div id="root" data-composition-id="shaydullaev" data-start="0" data-duration="__DUR__" data-width="1920" data-height="1080">
    __MEDIA__
    <div class="veil"></div>
    <div class="vignette"></div>
    <div id="ovLayer"></div>
    <div id="capLayer"></div>
    <div id="openLayer"></div>
    <div id="chapLayer"></div>
  </div>
<script>
  const DATA = __DATA__;
  const ovLayer = document.getElementById('ovLayer');
  const openLayer = document.getElementById('openLayer');
  const FADE = 0.5;
  const tl = gsap.timeline({paused:true});

  DATA.bg.forEach((s) => {
    const dur = Math.max(0.6, s.end - s.start);
    const span = dur + FADE;
    const el = document.getElementById(s.id);
    tl.fromTo(el.querySelector('video'),{scale:1.0},{scale:1.06,duration:span,ease:'none'}, s.start);
    if (s.cont) tl.set(el, {opacity:1}, s.start);
    else tl.fromTo(el, {opacity:0}, {opacity:1, duration:FADE, ease:'power1.out'}, s.start);
    if (!s.cont_end) tl.to(el, {opacity:0, duration:FADE, ease:'power1.in'}, s.end);
  });

  DATA.tags.forEach((t) => {
    if (!t.label) return;
    const el = document.createElement('div'); el.className='tag'; el.textContent=t.label; ovLayer.appendChild(el);
    tl.fromTo(el,{opacity:0,x:-24},{opacity:1,x:0,duration:.4,ease:'back.out(1.4)'}, t.start);
    tl.to(el,{opacity:0,duration:.35,ease:'power1.in'}, t.end-.35);
  });
  const badge = document.createElement('div'); badge.className='badge'; badge.textContent=DATA.channel; ovLayer.appendChild(badge);
  DATA.srcs.forEach((s) => {
    const el = document.createElement('div'); el.className='src'; el.textContent=s.text; ovLayer.appendChild(el);
    tl.to(el,{opacity:1,duration:.4}, s.start);
    tl.to(el,{opacity:0,duration:.4}, s.end-.4);
  });

  const FX = window.TextFX;
  function mkt(cls, html, px){ const e=document.createElement('div'); e.className=cls; e.innerHTML=html; if(px) e.style.fontSize=px+'px'; return e; }
  DATA.cards.forEach((c) => {
    const d = c.data;
    const el = document.createElement('div'); el.className = 'cardpos ' + (c.type==='name' ? 'pos-low' : 'pos-mid');
    const blur = document.createElement('div'); blur.className='cblur'; el.appendChild(blur);
    const wrap = document.createElement('div'); wrap.className = 'cardwrap'; el.appendChild(wrap);
    ovLayer.appendChild(el);
    let target, subEl, l1El;
    if (c.type==='name') {
      const nm = mkt('cmain gmincho', d.name, 78);
      subEl = mkt('csub', d.sub, 30);
      wrap.appendChild(nm); wrap.appendChild(subEl); target = nm;
    } else if (c.type==='date') {
      l1El = mkt('cl1', d.l1, 40);
      const l2 = mkt('cmain gmincho', d.l2, 86);
      wrap.appendChild(l1El); wrap.appendChild(l2); target = l2;
    } else {
      if (d.sub){ subEl = mkt('csub', d.sub, 36); wrap.appendChild(subEl); }
      const mn = mkt('cmain gmincho', (d.main||''), 96);
      wrap.appendChild(mn); target = mn;
    }
    if (c.cont) {
      // 窓境界をまたいで継続するカードは最初から完成状態（再アニメ禁止=二重アニメ防止）
      tl.set(el, {opacity:1}, 0);
      if (target) tl.set(target, {opacity:1, scale:1, filter:'none'}, 0);
      if (subEl) tl.set(subEl, {opacity:1, y:0}, 0);
      if (l1El) tl.set(l1El, {opacity:1, y:0}, 0);
    } else {
      tl.fromTo(el, {opacity:0}, {opacity:1, duration:.22}, c.start);
      if (subEl) FX.fadeUp(tl, subEl, c.start+0.04, {y:-14, dur:.4});
      if (l1El)  FX.fadeUp(tl, l1El, c.start+0.04, {y:14, dur:.4});
      (FX[d._anim] || FX.scalePop)(tl, target, c.start+0.14, {});
    }
    if (!c.cont_end) FX.exit(tl, el, c.end-0.35, {});
  });

  if (__SHOW_OPEN__) {
  const kicker = document.createElement('div'); kicker.className='op-kicker'; kicker.innerHTML="<span class='tfxc-band tfx-heavy'>完 全 解 説</span>";
  openLayer.appendChild(kicker);
  FX.fadeUp(tl, kicker, 1.0, {y:18, dur:.45}); FX.exit(tl, kicker, 7.6, {});
  const title = document.createElement('div'); title.className='op-title';
  title.innerHTML = "<div class='l1 tfx-mincho tfx-gold-solid'>シェイドゥラエフ</div><div class='uline tfx-uline'></div>";
  openLayer.appendChild(title);
  FX.charRise(tl, title.querySelector('.l1'), 1.2, {stagger:.08, dur:.6});
  FX.underline(tl, title.querySelector('.uline'), 2.5, 620, {});
  FX.exit(tl, title, 7.6, {y:-20});

  const kw = document.createElement('div'); kw.className='op-kw'; kw.innerHTML="<span class='kwin tfx-mincho tfx-outline'>19戦全て<em class='tfx-fire'>フィニッシュ</em></span>";
  openLayer.appendChild(kw);
  tl.set(kw,{opacity:1}, __KW_T__);
  FX.slam(tl, kw.querySelector('.kwin'), __KW_T__, {from:1.4, blur:18, dur:.5}); FX.exit(tl, kw, __KW_T__+3.4, {});

  const stat = document.createElement('div'); stat.className='op-stat';
  stat.innerHTML="<div class='s1 tfx-kicker'>19戦19勝・無敗</div><div class='s2 tfx-mincho tfx-emboss'>判定<em>0</em></div>";
  openLayer.appendChild(stat);
  FX.fadeUp(tl, stat.querySelector('.s1'), __ST_T__, {y:16, dur:.4});
  tl.set(stat,{opacity:1}, __ST_T__);
  FX.slam(tl, stat.querySelector('.s2'), __ST_T__+0.15, {from:1.5, blur:20, dur:.5});
  FX.exit(tl, stat, __ST_T__+4.2, {});
  }

  const capLayer = document.getElementById('capLayer');
  (DATA.caps||[]).forEach((c) => {
    const el = document.createElement('div'); el.className='cap';
    el.innerHTML = c.lines.map((l)=>"<div class='cl'>"+l+"</div>").join('');
    capLayer.appendChild(el);
    tl.fromTo(el,{opacity:0,y:8},{opacity:1,y:0,duration:.14,ease:'power1.out'}, c.s);
    tl.to(el,{opacity:0,duration:.1,ease:'power1.in'}, c.e);
    tl.set(el,{opacity:0}, c.e+0.11); // 退場後に不透明度0を固定（窓分割フレームシーク時の居残り防止）
  });

  const chapLayer = document.getElementById('chapLayer');
  (DATA.chapters||[]).forEach((ch)=>{
    const el=document.createElement('div'); el.className='chap';
    el.innerHTML="<div class='cfull'></div><div class='cinner'><div class='csub2'>"+ch.sub+"</div><div class='ctitle'>"+ch.title+"</div><div class='cline'></div></div>";
    chapLayer.appendChild(el);
    const inner=el.querySelector('.cinner'), ttl=el.querySelector('.ctitle'), line=el.querySelector('.cline');
    if (ch.cont) {
      // 窓境界をまたぐ章タイトルは最初から完成状態（二重アニメ防止）
      tl.set(el,{opacity:1},0); tl.set(inner,{scale:1.0},0);
      tl.set(ttl,{letterSpacing:'0.04em',opacity:1},0); tl.set(line,{width:560},0);
    } else {
      tl.fromTo(el,{opacity:0},{opacity:1,duration:.2,ease:'power1.out'}, ch.start);
      tl.fromTo(inner,{scale:1.1},{scale:1.0,duration:.55,ease:'power3.out'}, ch.start);
      tl.fromTo(ttl,{letterSpacing:'0.2em',opacity:0},{letterSpacing:'0.04em',opacity:1,duration:.5,ease:'power2.out'}, ch.start+0.04);
      tl.fromTo(line,{width:0},{width:560,duration:.55,ease:'power2.out'}, ch.start+0.18);
    }
    if (!ch.cont_end) tl.to(el,{opacity:0,duration:.3,ease:'power1.in'}, ch.end-0.3);
  });

  window.__timelines = window.__timelines || {};
  window.__timelines['shaydullaev'] = tl;
</script>
</body>
</html>
"""

SECTION_TAGS = {
    "s0_hook": "", "s1_who": "プロフィール", "s2_origin": "生い立ち", "s3_grapple": "格闘技の礎",
    "s4_kg": "無敗街道", "s5_intl": "世界への進出", "s6_debut": "RIZIN参戦", "s7_run": "王座への道",
    "s8_kleber": "戴冠", "s9_defense": "絶対王者", "s9b_ufc": "去就", "s10_style": "ファイトスタイル",
    "s11_human": "素顔", "s12_next": "9.10 京セラドーム", "s13_end": "まとめ",
}

# セクション別「意味順」背景。各assetはその区間のナレ内容に対応。
# 素材重複を解消(原則1回・フィニッシュ等は最大2回)。各リストは原則ユニーク要素。
# 試合クリップは「イントロ(入場/フェイスオフ)」と「フィニッシュ」を別素材化し、
# ナレ無しダック=フィニッシュ / ナレ中=イントロ という住み分けにする(#121/#122)。
SECTION_BG = {
    "s0_hook":     ["sh_kubo2_tko", "asakura_action", "sh_kubo2_win", "vp_cards", "prep_boy", "prep_eagle2", "prep_belt"],
    "s1_who":      ["prep_talk", "prep_room", "prep_home", "prep_medals", "prep_talk2", "prep_eagle", "prep_horse"],
    "s2_origin":   ["prep_boy", "prep_family", "prep_father", "prep_horse2", "prep_sheep", "prep_home"],
    "s3_grapple":  ["prep_gym", "prep_cage", "prep_bag", "prep_mitts", "prep_eagle2", "prep_train2"],
    "s4_kg":       ["kg_mont1", "kg_mont2", "kg_mont3", "prep_belt", "prep_medals"],
    "s5_intl":     ["aca_stand", "aca_action", "aca_down", "aca", "roadfc_walk", "kg_mont3"],
    # RIZIN戦: 各試合の30秒ダック(rz_*)がその窓を自動占有。ここはダック前後のナレ(相手紹介/結果)の背景。
    "s6_debut":    ["takeda_action", "prep_spar", "takeda_win", "sh_arch", "archuleta_action", "prep_bag", "prep_mitts"],
    "s7_run":      ["kubo_k1", "kubo1_action", "prep_run", "prep_train2", "kleber_face"],
    "s8_kleber":   ["kleber_face", "kleber_tri", "kleber_suz", "sh_kleber_belt", "sh_flag", "prep_runsnow"],
    "s9_defense":  ["prep_run", "kole_face", "sh_kole_belt", "asakura_face", "asakura_yt", "dome_crowd", "asakura_lift", "asakura_action", "sh_kubo2_win", "sh_kubo2_tko"],
    "s9b_ufc":     ["prep_talk", "prep_talk3", "vp_two"],
    "s10_style":   ["prep_gym", "prep_cage", "kleber_action", "sh_arch", "uae", "prep_spar"],
    "s11_human":   ["prep_horse", "prep_food", "prep_horse3", "prep_family", "prep_talk3"],
    "s12_next":    ["vp_cards", "vp_stage", "vp_mckee_talk", "vp_saka", "vp_two"],
    "s13_end":     ["sh_flag", "sh_kleber_belt", "prep_runsnow", "prep_mountain", "vp_stage"],
}

VIDEO_BG = {n for lst in SECTION_BG.values() for n in lst}

# クリップ内の決着位置(秒)。再カット後の実測フィニッシュ位置に合わせる。
FINISH_IN_CLIP = {
    "roadfc": 6, "takeda": 6, "uae": 12,
    "sh_kleber_ko": 7, "sh_asakura_tko": 8, "sh_kubo2_tko": 11, "sh_kole_tko": 7, "sh_arch": 8,
}
# ダック(timings.jsonのclip名) → bgvidアセット。
# RIZIN7戦は30秒フル切り出し(rz_*: 冒頭から再生し末尾でフィニッシュ)。roadfcのみ従来の短尺(決着同期)。
DUCK_ASSET = {
    "roadfc": "rz_roadfc",
    "takeda": "rz_takeda", "archuleta": "rz_archuleta", "kubo1": "rz_kubo1", "kleber": "rz_kleber",
    "kolesnik": "rz_kolesnik", "asakura": "rz_asakura", "kubo2": "rz_kubo2",
}

PINS = [
    ("バティルバシュをはじめ", "kg_mont1", None),
    ("2020年8月には、地元キルギス", "kg_mont2", None),
    # s3 憧れ=ヒョードル(本人PRIDE映像)
    ("我々の祖先は鷲を使って狩り", "prep_eagle", None),
    ("週末は必ずキルギスの山を走る", "prep_mountain", None),
    ("憧れの選手は、あの伝説エメリヤーエンコヒョードル", "fedor", None),
    ("長い棒にたくさんの釘", "prep_father", None),
    # s5 世界進出: バンタム級/ACA/アフマトフ フラッシュダウン(#115/#116)
    ("ここで注目したいのが、彼の階級", "aca_action", None),
    ("参戦したのは、強豪の登竜門ACA", "aca", None),
    ("中でも特筆すべきが、2022年のアスワドアフマトフ", "aca_down", None),
    ("だが、シェイドゥラエフは全く動じなかった", "aca_action", None),
    ("舞台は韓国", "roadfc_walk", None),
    ("同じ年の10月、中東", "uae", 12),
    # s6 武田(相手紹介+展開)/アーチュレッタ(展開)。ダック=フィニッシュ15秒。
    ("デビュー戦の相手は、武田光司", "takeda_action", None),
    ("だが試合が始まると、その差は問題にならなかった", "takeda_action", None),
    ("武田を一本で沈め", "takeda_win", None),
    ("続く2戦目、2024年9月のライジン48", "sh_arch", None),
    ("世界王座を経験した実力者。だが、この男の前でも", "archuleta_action", None),
    # s7 久保①: K-1キック紹介→展開→クレベル登場
    ("久保優太は、ケーワンの三階級を制した", "kubo_k1", None),
    ("純粋なグラップラーであるシェイドゥラエフが", "kubo_k1", None),
    ("だが蓋を開けてみれば、打ち合いでも上回った", "kubo1_action", None),
    ("そして立ちはだかるのが、王者クレベル", "kleber_face", None),
    # s8 クレベル: 三角締め(対朝倉)/判定勝ち(対鈴木)→フェイスオフ→決着はダック
    ("相手は、柔術の鬼と呼ばれる", "kleber_face", None),
    ("クレベルは、あの朝倉未来を、三角締め", "kleber_tri", None),
    ("さらに、鈴木千裕にも判定で競り勝った", "kleber_suz", None),
    ("第7代ライジンフェザー級王者", "sh_kleber_belt", None),
    ("このベルトを、キルギスに持ち帰る", "sh_flag", None),
    # s9 防衛: 相手紹介=相手戦の入場/攻防、決着はダック
    ("初防衛戦の相手は、ロシアのベテラン", "kole_face", None),
    ("2度目の防衛戦の相手は、日本で最も有名なMMAファイター", "asakura_face", None),
    ("いち早くユーチューブに目をつけて活動し", "asakura_yt", None),
    ("経営者としても数多くの事業を手掛ける", "asakura_face", None),
    ("彼が出場する大会は、ドームが満員", "dome_crowd", None),
    ("そしてこの試合で、シェイドゥラエフの規格外のパワー", "asakura_action", None),
    ("腰が重く、テイクダウンを許さないことで知られる朝倉", "asakura_lift", None),
    ("1ラウンド2分54秒、TKO", "asakura_action", None),
    ("3度目の防衛戦は、かつて破った打撃巧者", "sh_kubo2_win", None),
    # s9b 去就(UFC/契約/マッキー決定)
    ("次はUFCへ行くのではないか", "prep_talk", None),
    ("ライジンとの契約は、残り2試合", "prep_talk3", None),
    ("動いたのはライジンだった", "vp_saka", None),
    ("馬を一頭飼い", "prep_horse", None),
    ("羊肉や馬肉を使った郷土料理", "prep_food", None),
    ("2026年9月10日、京セラドーム大阪。超ライジン5", "vp_cards", None),
    ("榊原CEOはこの試合を", "vp_saka", None),
    ("相手は、ピーエフエルが誇る最強", "vp_mckee_talk", None),
]
FADE = 0.5

CLIP_SOURCE = {}
# RIZIN公式(Preparation密着＝生活/生い立ち・presser・RIZIN試合)
for _n in ["prep_home","prep_room","prep_medals","prep_family","prep_father","prep_gym","prep_train2",
           "prep_food","prep_horse","prep_horse2","prep_mountain","prep_eagle","prep_talk",
           "prep_belt","prep_boy","prep_spar","prep_bag","prep_cage","prep_mitts","prep_run",
           "prep_runsnow","prep_horse3","prep_sheep","prep_eagle2","prep_talk2","prep_talk3",
           "takeda","takeda_win","takeda_action","kubo1","sh_arch",
           "sh_kleber_ko","kleber_face","kleber_action","sh_kleber_belt",
           "sh_kole_tko","kole_face","sh_kole_belt","sh_asakura_tko","asakura_face","asakura_start","asakura_action",
           "sh_kubo2_tko","sh_kubo2_win","sh_flag","vp_stage","vp_two","vp_mckee_talk","vp_saka","vp_cards"]:
    CLIP_SOURCE[_n] = "出典: RIZIN FF"
for _n in ["rz_takeda", "rz_archuleta", "rz_kubo1", "rz_kleber", "rz_kolesnik", "rz_asakura", "rz_kubo2"]:
    CLIP_SOURCE[_n] = "試合映像: RIZIN FF"
CLIP_SOURCE["fedor"] = "映像: PRIDE FC"
CLIP_SOURCE["roadfc"] = "出典: Road FC"
CLIP_SOURCE["roadfc_walk"] = "出典: Road FC"
CLIP_SOURCE["uae"] = "出典: UAE Warriors"
CLIP_SOURCE["aca"] = "出典: ACA Young Eagles"
CLIP_SOURCE["aca_action"] = "出典: ACA Young Eagles"
CLIP_SOURCE["aca_stand"] = "出典: ACA Young Eagles"
CLIP_SOURCE["aca_down"] = "出典: ACA Young Eagles"
CLIP_SOURCE["rz_roadfc"] = "試合映像: Road FC"
# 対戦相手紹介・展開クリップ(#187-190)
for _n in ["archuleta_action", "kubo1_action", "kleber_tri", "kleber_suz", "asakura_lift", "dome_crowd"]:
    CLIP_SOURCE[_n] = "試合映像: RIZIN FF"
CLIP_SOURCE["kubo_k1"] = "出典: K-1"
CLIP_SOURCE["asakura_yt"] = "出典: 朝倉未来 YouTube"
for _n in ["kg_mont1", "kg_mont2", "kg_mont3"]:
    CLIP_SOURCE[_n] = "出典: キルギスMMA (Batyr Bashy 他)"
for _n in ["d18_walk","d18_aoki_fin","d18_lose"]:
    CLIP_SOURCE[_n] = "出典: DREAM.18(2012)"
for _n in ["fs_talk","fs_talk2"]:
    CLIP_SOURCE[_n] = "出典: Orange County Register"
for _n in ["st_rampage","st_henderson","st_askren","st_chandler","st_cormier","st_askren_chandler"]:
    CLIP_SOURCE[_n] = "画像: Wikimedia Commons"


def src_of(name: str) -> str:
    if name in CLIP_SOURCE:
        return CLIP_SOURCE[name]
    if name.startswith("px_"):
        return "映像: Pexels"
    return "出典: Bellator MMA"


def build_bg_segments():
    used = Counter()
    beat_rows = []
    for sid in SECORDER:
        lst = SECTION_BG[sid]
        bts = [b for b in BEATS if b["sec"] == sid]
        B, L = len(bts), len(lst)
        for i, b in enumerate(bts):
            beat_rows.append([b, lst[min(L - 1, i * L // B)], sid])
    pin_sync = {}
    for sub, name, fic in PINS:
        bt = beat_at(sub)
        for row in beat_rows:
            if row[0] is bt:
                row[1] = name
                if fic is not None:
                    w = bt["start"] + min(2.4, (bt["end"] - bt["start"]) * 0.6)
                    pin_sync[id(bt)] = (fic, w)
                break
    segs = []
    for b, asset, sid in beat_rows:
        if (segs and segs[-1]["name"] == asset and segs[-1]["sec"] == sid
                and (b["end"] - segs[-1]["start"]) <= 9.5):
            segs[-1]["end"] = b["end"]
            if id(b) in pin_sync and not segs[-1]["sync"]:
                segs[-1]["sync"] = pin_sync[id(b)]
        else:
            segs.append({"start": b["start"], "end": b["end"], "name": asset,
                         "sec": sid, "sync": pin_sync.get(id(b))})
    for dk in TIM.get("ducks", []):
        ds, de, clip = dk["start"], dk["end"], DUCK_ASSET.get(dk["clip"], dk["clip"])
        # RIZIN30秒ダック(rz_*)は冒頭から丸ごと再生(切り出し済みで末尾に決着)。sync=Noneでmstart=0。
        if clip.startswith("rz_"):
            sync = None
        else:
            # 短尺クリップ(roadfc等): 決着をダック窓の後方(0.72)に置く(#119/#120)
            mid = ds + (de - ds) * 0.72
            fic = FINISH_IN_CLIP.get(clip, (de - ds) / 2)
            sync = (fic, mid)
        segs = [s for s in segs if not (s["start"] >= ds - 0.01 and s["end"] <= de + 0.01)]
        for s in segs:
            if s["start"] < ds < s["end"]:
                s["end"] = ds
            if s["start"] < de < s["end"]:
                s["start"] = de
        segs.append({"start": ds, "end": de, "name": clip, "sec": dk["sec"],
                     "sync": sync, "duck": True})
    segs.sort(key=lambda s: s["start"])
    for i in range(len(segs) - 1):
        if segs[i].get("duck"):
            continue
        segs[i]["end"] = segs[i + 1]["start"]
    segs[0]["start"] = 0.0
    segs[-1]["end"] = TOTAL
    for s in segs:
        s["start"] = round(s["start"], 3); s["end"] = round(s["end"], 3)
    vi = 0
    for s in segs:
        nm = s["name"]
        if not (TPL / "assets" / "bgvid" / f"{nm}.mp4").exists():
            raise SystemExit(f"MISSING BGVID: {nm}")
        s["video"] = True
        s["src"] = src_of(nm)
        s["asset"] = f"bgvid/{nm}.mp4"
        s["id"] = f"bv{vi}"
        s["track"] = 40 + (vi % 10)
        cd = clip_dur(str(TPL / "assets" / "bgvid" / f"{nm}.mp4"))
        seglen = (s["end"] - s["start"]) + FADE
        ms = 0.0
        if s["sync"]:
            fic, w = s["sync"]
            ms = max(0.0, fic - (w - s["start"]))
        if ms + seglen > cd - 0.05:
            ms = max(0.0, cd - seglen - 0.05)
        mdur = min(seglen + 0.15, cd - ms - 0.02)
        if mdur < seglen - 0.3:
            print(f"  ! WARN 短尺クリップ {nm}: clip={cd:.1f}s < seg={seglen:.1f}s (黒の恐れ)")
        s["mstart"] = round(ms, 3)
        s["mdur"] = round(mdur, 3)
        vi += 1
        used[nm] += 1
    return segs, used


def card(anchor_sub, dur, typ, data, lead=0.2):
    b = beat_at(anchor_sub)
    st = round(b["start"] + lead, 2)
    return (st, round(st + dur, 2), typ, data)


CARDS = [
    card("ラジャブアリシェイドゥラエフ。2000年", 5.8, "name", {"name": "シェイドゥラエフ", "sub": "キルギスの犬鷲 ／ RIZINフェザー級王者・19戦無敗", "_anim": "charRise"}),
    card("身長170センチ", 5.2, "card", {"sub": "PROFILE", "main": "2000.10.11 キルギス", "_anim": "fadeUp"}),
    card("戦績はプロ19戦19勝", 5.4, "card", {"sub": "全試合フィニッシュ", "main": "19戦19勝・無敗", "_anim": "slam"}),
    card("2025年5月、ライジン男祭り", 5.6, "date", {"l1": "2025.5.4 RIZIN男祭り", "l2": "第7代 フェザー級王者", "_anim": "charRise"}),
    card("開始わずか33秒でTKO", 5.0, "card", {"sub": "初防衛", "main": "33秒 TKO", "_anim": "slam"}),
    card("19勝のうち12が、この一本勝ち", 5.2, "card", {"sub": "無敗の内訳", "main": "12一本 ／ 7KO", "_anim": "slam"}),
    card("2026年9月10日、京セラドーム大阪。超ライジン5", 5.8, "date", {"l1": "2026.9.10 京セラドーム大阪", "l2": "RIZIN×PFL Ｗ王座戦", "_anim": "charRise"}),
]
FONT_PX = {
    "card": {"sub": 36, "main": 96},
    "name": {"name": 78, "sub": 30},
    "date": {"l1": 40, "l2": 86},
}

SRCS = []  # 個別セグメントの出典で表示
CHANNEL = "格闘ニュースラボ"

check_card_widths(CARDS, FONT_PX)

# ---- 字幕: ナレ読みかな → 正式表記 (長いキー優先) ----
DISP = [
    ("ラジャブアリシェイドゥラエフ", "ラジャブアリ・シェイドゥラエフ"),
    ("エイジェイマッキー", "AJ・マッキー"),
    ("リアネイキッドチョーク", "リアネイキドチョーク"),
    ("エメリヤーエンコヒョードル", "エメリヤーエンコ・ヒョードル"),
    ("ホベルトサトシソウザ", "ホベルト・サトシ・ソウザ"),
    ("フアンアーチュレッタ", "フアン・アーチュレッタ"),
    ("アスワドアフマトフ", "アスワド・アフマトフ"),
    ("クレベルコイケ", "クレベル・コイケ"),
    ("ビクターコレスニック", "ビクター・コレスニック"),
    ("武田光司", "武田光司"),
    ("久保優太", "久保優太"),
    ("朝倉未来", "朝倉未来"),
    ("ロードエフシー64", "Road FC 64"),
    ("ロードエフシー", "Road FC"),
    ("アカヤングイーグルス", "ACA Young Eagles"),
    ("ユーエーイーウォリアーズ", "UAE Warriors"),
    ("バティルバシュ", "Batyr Bashy"),
    ("ヤンジヨン", "ヤン・ジヨン"),
    ("超ライジン5", "超RIZIN.5"),
    ("ライジン47", "RIZIN.47"),
    ("ライジン男祭り", "RIZIN男祭り"),
    ("ライジン", "RIZIN"),
    ("ユーエフシー", "UFC"),
    ("ピーエフエル", "PFL"),
]


def disp(text: str) -> str:
    for k, v in DISP:
        text = text.replace(k, v)
    return text


# 下部字幕の1行あたり最大幅(全角換算)。font46px/幅1760px内に確実に収める安全値。
CAP_LINE_MAX = 23.0
# 改行を優先する助詞・記号（この直後で折る）
CAP_BREAK_AFTER = set("、。，・！？」』）】")
CAP_PARTICLE = set("はがをにでとへものやか")  # 文節境界になりやすい助詞


def build_caps():
    def width(s):
        return sum(0.5 if ch.isascii() else 1.0 for ch in s)

    def wrap_lines(s):
        """sを CAP_LINE_MAX 以内の行に分割（助詞/句読点直後を優先。語中・英数字/カタカナ連続の途中で折らない）。"""
        lines, cur = [], ""
        i = 0
        while i < len(s):
            cur += s[i]
            # 現在行が上限に近づいたら、良い改行位置で折る
            if width(cur) >= CAP_LINE_MAX and i < len(s) - 1:
                # curの末尾から遡って改行に適した位置を探す
                cut = len(cur)
                for j in range(len(cur) - 1, max(0, len(cur) - 10), -1):
                    ch, nx = cur[j - 1], cur[j] if j < len(cur) else ""
                    # カタカナ連続/英数字連続の内部では折らない
                    def _kata(c): return "゠" <= c <= "ヿ" or c == "ー"
                    if _kata(ch) and j < len(cur) and _kata(cur[j]):
                        continue
                    if ch.isascii() and ch.isalnum() and j < len(cur) and cur[j].isascii() and cur[j].isalnum():
                        continue
                    if ch in CAP_BREAK_AFTER or ch in CAP_PARTICLE:
                        cut = j; break
                lines.append(cur[:cut]); cur = cur[cut:]
            i += 1
        if cur:
            lines.append(cur)
        return [ln for ln in lines if ln]

    caps = []
    for i, b in enumerate(BEATS):
        start = b["start"]
        nxt = BEATS[i + 1]["start"] if i + 1 < len(BEATS) else b["end"] + 0.4
        end = min(b["end"] + 0.30, nxt - 0.05)
        if end <= start:
            end = max(b["end"], start + 0.4)
        txt = disp(b["text"].replace("「", "").replace("」", ""))
        lines = wrap_lines(txt)
        # 2行/キュー にまとめ、3行以上は時間分割。各キューは文字数比で時間配分・非重複。
        groups = [lines[k:k + 2] for k in range(0, len(lines), 2)]
        wsum = sum(width("".join(g)) for g in groups) or 1
        t = start
        for gi, g in enumerate(groups):
            frac = width("".join(g)) / wsum
            gend = end if gi == len(groups) - 1 else min(end - 0.05, t + (end - start) * frac)
            if gend <= t:
                gend = t + 0.4
            caps.append({"s": round(t, 2), "e": round(gend, 2), "lines": g})
            t = round(gend, 2)
    # 隣接キューは必ず 0.14s 以上の間隔を空ける（完全隣接=前キュー退場が居残り重なる描画バグ防止・退場0.1sより長く）
    CAP_GAP = 0.14
    for k in range(len(caps) - 1):
        if caps[k]["e"] > caps[k + 1]["s"] - CAP_GAP:
            caps[k]["e"] = round(caps[k + 1]["s"] - CAP_GAP, 2)
    return caps


def _src_windows(segs):
    out = []
    for s in segs:
        txt = s.get("src", "出典: Bellator MMA")
        if out and out[-1]["text"] == txt and abs(out[-1]["end"] - s["start"]) < 0.05:
            out[-1]["end"] = s["end"]
        else:
            out.append({"start": s["start"], "end": s["end"], "text": txt})
    return out


bg_segs, used = build_bg_segments()
SHOW_OPEN = True
DATA = {
    "total": DUR,
    "bg": bg_segs,
    "tags": [{"start": SECS[s]["start"], "end": SECS[s]["end"], "label": SECTION_TAGS.get(s, "")} for s in SECORDER],
    "cards": [{"start": a, "end": b, "type": c, "data": d} for (a, b, c, d) in CARDS],
    "srcs": _src_windows(bg_segs),
    "caps": build_caps(),
    "chapters": TIM.get("chapters", []),
    "channel": CHANNEL,
}

if WINDOWED:
    off, wdur = WIN_START, round(WIN_END - WIN_START, 3)
    SHOW_OPEN = off <= 0.01
    def _win_timed(items, ks="start", ke="end"):
        out = []
        for it in items:
            ns, ne = it[ks] - off, it[ke] - off
            if ne <= 0.001 or ns >= wdur - 0.001:
                continue
            it = dict(it); it["cont"] = ns < -0.001; it["cont_end"] = ne > wdur + 0.001
            it[ks] = round(max(0.0, ns), 3); it[ke] = round(min(wdur, ne), 3)
            out.append(it)
        return out
    def _win_video(items):
        out = []
        for it in items:
            it = dict(it)
            ne = it["end"] - off
            st, d = it["start"] - off, it["mdur"]
            ms = it.get("mstart", 0)
            it["cont"] = st < 0.05
            it["cont_end"] = ne > wdur - 0.05
            if st < 0:
                ms = round(ms - st, 3); d = round(d + st, 3); st = 0.0
            if st >= wdur - 0.001 or d <= 0.05:
                continue
            if st + d > wdur:
                d = round(wdur - st, 3)
            it["start"] = round(st, 3); it["mdur"] = d; it["mstart"] = ms
            it["end"] = wdur if it["cont_end"] else round(it["start"] + max(0.6, d - FADE), 3)
            out.append(it)
        return out
    DATA["bg"] = _win_video(bg_segs)
    DATA["cards"] = _win_timed(DATA["cards"])
    DATA["tags"] = _win_timed(DATA["tags"])
    DATA["srcs"] = _win_timed(DATA["srcs"])
    DATA["caps"] = _win_timed(DATA["caps"], "s", "e")
    DATA["chapters"] = _win_timed(DATA["chapters"])
    DUR = wdur; DATA["total"] = wdur
    bg_segs = DATA["bg"]

media = []
for s in bg_segs:
    media.append(
        f'<div class="bgvid" id="{s["id"]}"><video id="{s["id"]}-v" src="assets/{s["asset"]}" muted playsinline '
        f'data-start="{s["start"]}" data-duration="{s["mdur"]}" data-media-start="{s.get("mstart",0)}" data-track-index="{s["track"]}"></video></div>')
for a in ("audio/narration.wav", "audio/bgm.m4a"):
    if not (TPL / "assets" / a).exists():
        # CIのビジュアルのみレンダーでは音声不要(muxはローカルfinalize)。警告のみで続行。
        print(f"  ! 音声なし(ビジュアルのみレンダー想定): {a}")
media.append('<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="60" data-volume="1"></audio>')
media.append('<audio id="bgm" src="assets/audio/bgm.m4a" data-start="0" data-track-index="61" data-volume="0.085"></audio>')
MEDIA = "\n    ".join(media)

KW_T = round(beat_at("異名はキルギスの犬鷲")["start"] + 0.3, 2)
ST_T = round(beat_at("武田光司、アーチュレッタ")["start"] + 0.2, 2)

LIB = ROOT / "hyperframes" / "_lib" / "textfx"
TEXTFX_CSS = (LIB / "textfx.css").read_text(encoding="utf-8")
TEXTFX_JS = (LIB / "textfx.js").read_text(encoding="utf-8")
HTML = (TEMPLATE.replace("__TEXTFX_CSS__", TEXTFX_CSS)
                .replace("__TEXTFX_JS__", TEXTFX_JS)
                .replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
                .replace("__MEDIA__", MEDIA)
                .replace("__KW_T__", str(KW_T))
                .replace("__ST_T__", str(ST_T))
                .replace("__SHOW_OPEN__", "true" if SHOW_OPEN else "false")
                .replace("__DUR__", str(DUR)))
(TPL / "index.html").write_text(HTML, encoding="utf-8")

over = {a: n for a, n in used.items() if n >= 3}
vid_time = sum(s["end"] - s["start"] for s in bg_segs)
print(f"-> {TPL / 'index.html'}")
print(f"bg:{len(bg_segs)} (全動画) cards:{len(CARDS)} total:{DUR}s")
print(f"背景セグメント尺の最大: {max(s['end']-s['start'] for s in bg_segs):.1f}s (目標<10s)")
print(f"★背景の【映像】比率: {100*vid_time/max(1,DUR):.0f}% (全動画)")
print(f"3回以上使用(報告対象): {over if over else 'なし'}")
print(f"同期ピン: {[(p[1],p[2]) for p in PINS if p[2]]}")
