"""RIZIN.54 体重超過ニュース 横テンプレ(1920x1080)生成【ニュースまとめ型】。
背景=計量フェイスオフ/解説者talking-head/計量ステージ(動画)＋公式対戦カード(画像)。
オーバーレイ: Xカード(公式/榊原/伊藤/川尻/ジャン斉藤=実名・実アイコン / 一般ファン=匿名=仮名+イニシャル丸),
数値カード(2.85/1.75), 章4, 出典, DOM字幕(算用数字), セクションタグ。単一BGM・CI窓対応。
rizin54-yosou テンプレを土台に、予想者要素を除去しニュース用に再構成。
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
TPL = ROOT / "hyperframes" / "templates" / "rizin54-weightmiss"
TIM = json.loads((ROOT / "subtitles" / "out" / "rizin54_weightmiss" / "timings.json").read_text(encoding="utf-8"))
XPOSTS = json.loads((ROOT / "research_output" / "rizin54_weightmiss" / "xposts" / "xposts.json").read_text(encoding="utf-8"))
BEATS = TIM["beats"]
SECS = {s["sec"]: s for s in TIM["sections"]}
SECORDER = [s["sec"] for s in TIM["sections"]]
TOTAL = TIM["total"]
DUR = round(TOTAL + 0.6, 2)
FADE = 0.5

WIN_START = float(os.environ.get("HF_WIN_START", "0") or "0")
WIN_END = float(os.environ.get("HF_WIN_END", "0") or "0")
WINDOWED = "HF_WIN_START" in os.environ or "HF_WIN_END" in os.environ
if not WINDOWED:
    WIN_START, WIN_END = 0.0, DUR


def _norm(s):
    return s.replace("、", "").replace("。", "").replace(" ", "").replace("　", "").replace("・", "")


def beats_of(sec):
    return [b for b in BEATS if b["sec"] == sec]


def beat_at(sub):
    n = _norm(sub)
    for b in BEATS:
        if n in _norm(b["text"]):
            return b
    raise SystemExit(f"BEAT NOT FOUND: {sub}")


# ===== 背景(video/img) =====
VIDEOS = {"faceoff_sato_mix", "faceoff_ito_gaja", "talk_aoki", "talk_aoki2", "talk_jobin", "talk_jobin2",
          "talk_kanehara", "weighin_stage", "weighin_stage2", "weighin_crowd", "weighin_faceoff2",
          "saka_stage", "mix_presser"}
IMAGES = {"card_main", "card_sato_mix", "card_ito_gaja", "card_order"}
CONTAIN = {"card_main", "card_sato_mix", "card_ito_gaja", "card_order"}  # 公式カードは全体表示


def is_vid(n):
    return n in VIDEOS


SRC_OF = {
    "faceoff_sato_mix": "映像: RIZIN公式 公開計量", "faceoff_ito_gaja": "映像: RIZIN公式 公開計量",
    "weighin_stage": "映像: RIZIN公式 公開計量", "weighin_stage2": "映像: RIZIN公式 公開計量",
    "weighin_crowd": "映像: RIZIN公式 公開計量", "weighin_faceoff2": "映像: RIZIN公式 公開計量",
    "saka_stage": "映像: RIZIN公式 公開計量", "mix_presser": "映像: RIZIN公式 記者会見",
    "talk_aoki": "出典: YouTube「青木真也」", "talk_aoki2": "出典: YouTube「青木真也」",
    "talk_jobin": "出典: YouTube「ジョビンチャンネル」", "talk_jobin2": "出典: YouTube「ジョビンチャンネル」",
    "talk_kanehara": "出典: YouTube「kinchanTV(金原正徳)」",
    "card_main": "画像: RIZIN FF公式", "card_sato_mix": "画像: RIZIN FF公式",
    "card_ito_gaja": "画像: RIZIN FF公式", "card_order": "画像: RIZIN FF公式",
}


def src_of(n):
    return SRC_OF.get(n, "画像: RIZIN FF公式")


# ===== セクション別・ビート順の背景 =====
SECTION_BG = {
    "s0_intro":   ["weighin_stage", "mix_presser", "weighin_crowd"],
    "s1_facts":   ["weighin_faceoff2", "card_sato_mix", "card_ito_gaja", "faceoff_sato_mix"],
    "s2_rules":   ["weighin_stage2", "card_order", "faceoff_ito_gaja", "card_sato_mix"],
    "s3_sato":    ["faceoff_sato_mix", "mix_presser", "faceoff_sato_mix", "weighin_faceoff2"],
    "s4_ito":     ["faceoff_ito_gaja", "faceoff_ito_gaja", "weighin_crowd"],
    "s5_saka":    ["saka_stage", "saka_stage", "weighin_stage", "card_order"],
    "s6_fighters":["weighin_crowd", "talk_aoki", "talk_aoki2", "talk_kanehara", "talk_jobin", "weighin_stage2"],
    "s7_fans":    ["talk_jobin2", "weighin_stage", "weighin_faceoff2", "card_order"],
    "s8_end":     ["card_sato_mix", "card_main", "weighin_stage2"],
}

# ===== 数値カード(2.85 / 1.75) =====
NUM_ANCHORS = ["公式に発表された数字", "パッチー・ミックスが2.85キロ"]

# ===== Xカード =====
# public=Trueは実名・実アイコン。一般ファンは匿名(仮名+イニシャル丸)。
# (anchor, post_id, opts)  opts: big/pos/anon_name/anon_initial/anon_color
def X(anchor, pid, **opts):
    return {"anchor": anchor, "pid": pid, **opts}

XCARDS = [
    # s1 公式計量結果
    X("契約体重61キロに対し、パッチー・ミックスは", "2086709931982696657", big=True),
    X("契約57キロに対し、ガジャマトフは", "2086709557414469863", big=True),
    # s2 NCルール(メディア)
    X("超過した選手が勝っても、その勝利は記録されず", "2086694997894816035", pos="right"),
    # s3 佐藤同情(匿名ファン)
    X("佐藤将光が可哀想すぎる", "2086772350583001264", pos="left",
      anon_name="格闘技ファン", anon_initial="S", anon_color="#c0417a"),
    # s4 伊藤ボーナス(実名・当事者)
    X("ファイトマネー・オーバーボーナス制度", "2086805193061175563", big=True),
    # s5 榊原声明+試合順(実名・主催者)
    X("トップ選手2名の体重超過は、決して容認できるものではない", "2086752492562596098", pos="left"),
    X("伊藤対ガジャマトフを休憩前の第6試合に繰り上げ", "2086791598634094793", pos="right"),
    # s6 川尻自虐(実名)
    X("全て私のせいです", "2086757365890842834_KAWAJIRI_PLACEHOLDER"),  # 差し替え: 川尻のid
    # s7 ファン賛否
    X("なめられている、対戦相手にも", "2086791675528294839", pos="left",
      anon_name="格闘技ファン", anon_initial="R", anon_color="#3b7fd4"),
    X("現状ではノーコンテストが一番厳しい処置", "2086774772214710594", pos="right"),  # ジャン斉藤=公人
    X("今後ミックスはフェザー級、ガジャマトフはバンタム級で", "2086700451349885348", pos="left",
      anon_name="格闘技ファン", anon_initial="M", anon_color="#4d8a5a"),
]

CHANNEL = "格闘ニュースラボ"
SECTION_TAGS = {
    "s0_intro": "", "s1_facts": "計量結果", "s2_rules": "適用ルール", "s3_sato": "当事者・佐藤将光",
    "s4_ito": "当事者・伊藤裕樹", "s5_saka": "主催者の対応", "s6_fighters": "選手・解説の反応",
    "s7_fans": "ファンの賛否", "s8_end": "まとめ",
}

KB_VARIANTS = [
    ((1.03, -2.5, -1.2), (1.11, 2.5, 1.2)), ((1.11, 2.5, 1.0), (1.03, -2.5, -0.6)),
    ((1.04, 3.0, -0.8), (1.12, -3.0, 1.0)), ((1.12, -2.8, 1.2), (1.04, 2.8, -1.0)),
]


def kb_for(kb_idx, seg_start, seg_end, vis_start, vis_end):
    (s0, x0, y0), (s1, x1, y1) = KB_VARIANTS[kb_idx % 4]
    basis = max(0.1, (seg_end - seg_start) + FADE)
    def lerp(p):
        p = min(1.0, max(0.0, p))
        return {"scale": round(s0 + (s1 - s0) * p, 4), "x": round(x0 + (x1 - x0) * p, 3), "y": round(y0 + (y1 - y0) * p, 3)}
    return lerp((vis_start - seg_start) / basis), lerp((vis_end - seg_start) / basis)


def build_bg_segments():
    used = Counter()
    rows = []
    for sid in SECORDER:
        lst = SECTION_BG[sid]; bts = beats_of(sid)
        if len(bts) != len(lst):
            raise SystemExit(f"SECTION_BG mismatch {sid}: beats={len(bts)} bg={len(lst)}")
        for b, a in zip(bts, lst):
            rows.append([b, a, sid])
    segs = []
    for b, a, sid in rows:
        if segs and segs[-1]["name"] == a and segs[-1]["sec"] == sid and (b["end"] - segs[-1]["start"]) <= 12.0:
            segs[-1]["end"] = b["end"]
        else:
            segs.append({"start": b["start"], "end": b["end"], "name": a, "sec": sid})
    for i in range(len(segs) - 1):
        segs[i]["end"] = segs[i + 1]["start"]
    segs[0]["start"] = 0.0
    segs[-1]["end"] = TOTAL
    vi = 0
    for s in segs:
        nm = s["name"]
        s["video"] = is_vid(nm); s["contain"] = nm in CONTAIN
        ext = "mp4" if s["video"] else "jpg"; sub = "bgvid" if s["video"] else "img"
        p = TPL / "assets" / sub / f"{nm}.{ext}"
        if not p.exists():
            raise SystemExit(f"MISSING BG: {p}")
        s["src"] = src_of(nm); s["asset"] = f"{sub}/{nm}.{ext}"; s["id"] = f"bg{vi}"; s["track"] = 40 + (vi % 12)
        s["kb"] = vi % 4
        if s["contain"]:
            s["kb_from"] = {"scale": 1.0, "x": 0, "y": 0}; s["kb_to"] = {"scale": 1.05, "x": 0, "y": 0}
        else:
            f, t = kb_for(s["kb"], s["start"], s["end"], s["start"], s["end"]); s["kb_from"], s["kb_to"] = f, t
        if s["video"]:
            cd = clip_dur(str(p)); seglen = (s["end"] - s["start"]) + FADE
            s["mstart"] = 0.0; s["mdur"] = round(min(seglen + 0.15, cd - 0.05), 3)
            if s["mdur"] < seglen - 0.3:
                s["loop"] = True; s["mdur"] = round(cd - 0.05, 3)
        vi += 1; used[nm] += 1
    for s in segs:
        s["start"] = round(s["start"], 3); s["end"] = round(s["end"], 3)
    return segs, used


# ===== 字幕 =====
CAP_LINE_MAX = 23.0
CAP_BREAK_AFTER = set("、。，・！？」』）】")
CAP_PARTICLE = set("はがをにでとへものやか")


def build_caps():
    def width(s): return sum(0.5 if ch.isascii() else 1.0 for ch in s)
    def wrap(s):
        lines, cur, i = [], "", 0
        while i < len(s):
            cur += s[i]
            if width(cur) >= CAP_LINE_MAX and i < len(s) - 1:
                cut = len(cur)
                for j in range(len(cur) - 1, max(0, len(cur) - 10), -1):
                    ch = cur[j - 1]
                    def _k(c): return "゠" <= c <= "ヿ" or c == "ー"
                    if _k(ch) and j < len(cur) and _k(cur[j]): continue
                    if ch.isascii() and ch.isalnum() and j < len(cur) and cur[j].isascii() and cur[j].isalnum(): continue
                    if ch in CAP_BREAK_AFTER or ch in CAP_PARTICLE: cut = j; break
                lines.append(cur[:cut]); cur = cur[cut:]
            i += 1
        if cur: lines.append(cur)
        return [x for x in lines if x]
    caps = []
    for i, b in enumerate(BEATS):
        start = b["start"]; nxt = BEATS[i + 1]["start"] if i + 1 < len(BEATS) else b["end"] + 0.4
        end = min(b["end"] + 0.30, nxt - 0.05)
        if end <= start: end = max(b["end"], start + 0.4)
        txt = b["text"].replace("「", "").replace("」", "")
        lines = wrap(txt); groups = [lines[k:k + 2] for k in range(0, len(lines), 2)]
        wsum = sum(width("".join(g)) for g in groups) or 1; t = start
        for gi, g in enumerate(groups):
            frac = width("".join(g)) / wsum
            gend = end if gi == len(groups) - 1 else min(end - 0.05, t + (end - start) * frac)
            if gend <= t: gend = t + 0.4
            caps.append({"s": round(t, 2), "e": round(gend, 2), "lines": g}); t = round(gend, 2)
    for k in range(len(caps) - 1):
        if caps[k]["e"] > caps[k + 1]["s"]:
            caps[k]["e"] = round(caps[k + 1]["s"] - 0.02, 2)
    return caps


def anchored_x():
    out = []
    for c in XCARDS:
        pid = c["pid"]
        # 川尻プレースホルダ解決(handle=CRUSHER_MMA)
        if pid.endswith("_KAWAJIRI_PLACEHOLDER"):
            pid = next((k for k, v in XPOSTS.items() if v.get("handle") == "CRUSHER_MMA"), None)
            if not pid:
                continue
        rec = XPOSTS.get(pid)
        if not rec:
            print(f"  ! XPOST missing {pid} ({c['anchor'][:20]})"); continue
        b = beat_at(c["anchor"])
        d = {"start": round(b["start"] + 0.25, 2), "end": round(b["end"] + 0.10, 2),
             "text": rec["text"], "big": bool(c.get("big")), "pos": c.get("pos", "center")}
        if c.get("anon_name"):  # 一般ファン=匿名
            d.update(anon=True, name=c["anon_name"], handle="@" + ("*" * 6),
                     initial=c.get("anon_initial", "?"), color=c.get("anon_color", "#3b7fd4"),
                     verified=False, likes=rec.get("likes"))
        else:  # 公人=実名・実アイコン
            d.update(anon=False, name=rec["name"], handle="@" + rec["handle"], verified=rec.get("verified", False),
                     avatar=rec.get("avatar_file"), likes=rec.get("likes"))
        out.append(d)
    return out


def build_nums():
    out = []
    for a in NUM_ANCHORS:
        b = beat_at(a)
        out.append({"start": round(b["start"] + 0.3, 2), "end": round(b["end"] + 0.2, 2)})
    return out


def _src_windows(segs):
    out = []
    for s in segs:
        txt = s.get("src", "")
        if out and out[-1]["text"] == txt and abs(out[-1]["end"] - s["start"]) < 0.05:
            out[-1]["end"] = s["end"]
        else:
            out.append({"start": s["start"], "end": s["end"], "text": txt})
    return out


bg_segs, used = build_bg_segments()
DATA = {
    "total": DUR, "bg": bg_segs,
    "tags": [{"start": SECS[s]["start"], "end": SECS[s]["end"], "label": SECTION_TAGS.get(s, "")} for s in SECORDER],
    "xcards": anchored_x(), "nums": build_nums(), "srcs": _src_windows(bg_segs),
    "caps": build_caps(), "chapters": TIM.get("chapters", []), "channel": CHANNEL,
}

if WINDOWED:
    off, wdur = WIN_START, round(WIN_END - WIN_START, 3)
    def _wt(items, ks="start", ke="end"):
        out = []
        for it in items:
            ns, ne = it[ks] - off, it[ke] - off
            if ne <= 0.001 or ns >= wdur - 0.001: continue
            it = dict(it); it["cont"] = ns < 0.05; it["cont_end"] = ne > wdur - 0.05
            it[ks] = round(max(0.0, ns), 3); it[ke] = round(min(wdur, ne), 3); out.append(it)
        return out
    def _wbg(items):
        out = []
        for it in items:
            it = dict(it); ns, ne = it["start"] - off, it["end"] - off
            if ne <= 0.001 or ns >= wdur - 0.001: continue
            it["cont"] = ns < 0.05; it["cont_end"] = ne > wdur - 0.05
            vis0 = max(it["start"], off); vis1 = min(it["end"], off + wdur)
            if not it["contain"]:
                f, t = kb_for(it.get("kb", 0), it["start"], it["end"], vis0, vis1); it["kb_from"], it["kb_to"] = f, t
            if it["video"]:
                ms = it.get("mstart", 0.0)
                if ns < 0: ms = round(ms - ns, 3)
                dd = it.get("mdur", ne - max(0.0, ns)); st = max(0.0, ns)
                ddd = min(dd, wdur - st) if it["cont_end"] else min(dd, (min(wdur, ne) - st) + FADE)
                it["mstart"] = ms; it["mdur"] = round(max(0.3, ddd), 3)
            it["start"] = round(max(0.0, ns), 3); it["end"] = round(min(wdur, ne), 3); out.append(it)
        return out
    DATA["bg"] = _wbg(bg_segs)
    for k in ("xcards", "nums", "tags", "srcs", "chapters"):
        DATA[k] = _wt(DATA[k])
    DATA["caps"] = _wt(DATA["caps"], "s", "e")
    DUR = wdur; DATA["total"] = wdur; bg_segs = DATA["bg"]

media = []
for s in bg_segs:
    cc = " contain" if s.get("contain") else ""
    if s["video"]:
        media.append(f'<div class="bg{cc}" id="{s["id"]}"><div class="bgfill" style="background-image:url(assets/{s["asset"]})"></div>'
                     f'<video class="bgv" id="{s["id"]}-v" src="assets/{s["asset"]}" muted playsinline '
                     f'data-start="{s["start"]}" data-duration="{s.get("mdur",1)}" data-media-start="{s.get("mstart",0)}" data-track-index="{s["track"]}"></video></div>')
    else:
        media.append(f'<div class="bg{cc}" id="{s["id"]}"><div class="bgfill" style="background-image:url(assets/{s["asset"]})"></div>'
                     f'<div class="bgmain" style="background-image:url(assets/{s["asset"]})"></div></div>')
media.append('<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="70" data-volume="1"></audio>')
media.append('<audio id="bgm" src="assets/audio/bgm.m4a" data-start="0" data-duration="__DUR__" data-track-index="71" data-volume="0.07"></audio>')
MEDIA = "\n    ".join(media)

LIB = ROOT / "hyperframes" / "_lib" / "textfx"
TEXTFX_CSS = (LIB / "textfx.css").read_text(encoding="utf-8")
TEXTFX_JS = (LIB / "textfx.js").read_text(encoding="utf-8")

TEMPLATE = r"""<!doctype html>
<!-- RIZIN.54 体重超過ニュース 1920x1080 -->
<html><head><meta charset="utf-8" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script>__TEXTFX_JS__</script>
<style>
__TEXTFX_CSS__
  @font-face { font-family:"Mincho"; src:url("assets/fonts/GokubutoMincho.ttf") format("truetype"); font-weight:900; font-display:block; }
  @font-face { font-family:"JPHeavy"; src:url("assets/fonts/SourceHanSansJP-Heavy.otf") format("opentype"); font-weight:900; font-display:block; }
  @font-face { font-family:"JPMed"; src:url("assets/fonts/SourceHanSansJP-Medium.otf") format("opentype"); font-weight:500; font-display:block; }
  * { box-sizing:border-box; margin:0; padding:0; }
  html,body { width:100%; height:100%; background:#000; overflow:hidden; }
  #root { position:relative; width:1920px; height:1080px; overflow:hidden; background:#05070c; font-family:"JPHeavy","Noto Sans JP",sans-serif; color:#fff; }
  .bg { position:absolute; inset:0; z-index:1; opacity:0; overflow:hidden; will-change:opacity; }
  .bgfill { position:absolute; inset:-4%; background-size:cover; background-position:center; filter:blur(22px) brightness(.42) saturate(.9); transform:scale(1.1); }
  .bgmain { position:absolute; inset:0; background-size:cover; background-position:center; background-repeat:no-repeat; will-change:transform; }
  .bg.contain .bgmain { background-size:contain; }
  .bg .bgv { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; transform:translateZ(0); backface-visibility:hidden; }
  .veil { position:absolute; inset:0; z-index:5; pointer-events:none; background:linear-gradient(180deg, rgba(0,0,0,.34) 0%, rgba(0,0,0,.02) 20%, rgba(0,0,0,.02) 52%, rgba(0,0,0,.42) 82%, rgba(0,0,0,.80) 100%); }
  .vignette { position:absolute; inset:0; z-index:6; pointer-events:none; background:radial-gradient(ellipse at 50% 46%, transparent 0 56%, rgba(0,0,0,.46) 100%); }
  .tag { position:absolute; z-index:20; left:56px; top:52px; padding:8px 24px 8px 18px; background:rgba(8,9,12,.6); border-left:5px solid #e7b94a; border-radius:2px; font-family:"Mincho",serif; font-size:34px; font-weight:900; letter-spacing:.05em; color:#fff; text-shadow:0 0 2px #000,0 2px 8px rgba(0,0,0,.9); white-space:nowrap; opacity:0; -webkit-backdrop-filter:blur(6px); backdrop-filter:blur(6px); }
  .badge { position:absolute; z-index:20; right:56px; top:54px; padding:9px 22px; background:rgba(8,8,10,.82); border:2px solid rgba(255,213,74,.85); border-radius:40px; font-family:"JPHeavy"; font-size:26px; color:#ffe89a; letter-spacing:.03em; text-shadow:0 1px 3px rgba(0,0,0,.9); }
  .src { position:absolute; z-index:20; left:40px; bottom:24px; padding:3px 11px; background:rgba(0,0,0,.62); border-left:3px solid rgba(255,213,74,.85); border-radius:2px; font-family:"JPMed"; font-size:18px; color:#e2e2e2; letter-spacing:.01em; text-shadow:0 1px 2px rgba(0,0,0,.9); opacity:0; }
  /* 数値カード */
  #numLayer { position:absolute; inset:0; z-index:19; pointer-events:none; }
  .nums { position:absolute; left:50%; top:52%; transform:translate(-50%,-50%); opacity:0; text-align:center; }
  .nums .nhead { font-family:"Mincho",serif; font-size:40px; color:#ffce2e; letter-spacing:.08em; margin-bottom:22px; text-shadow:0 2px 10px rgba(0,0,0,.9); }
  .nums .nrow { display:flex; gap:40px; justify-content:center; }
  .nums .ncell { min-width:420px; padding:22px 26px; background:rgba(8,10,14,.8); border-radius:16px; border-top:6px solid #ff5f52; }
  .nums .ncell .nname { font-family:"JPHeavy"; font-size:36px; color:#fff; margin-bottom:6px; }
  .nums .ncell .nsub { font-family:"JPMed"; font-size:22px; color:#9fb0c4; margin-bottom:10px; }
  .nums .ncell .nover { font-family:"Mincho",serif; font-size:82px; line-height:.95; color:#ff5f52; }
  .nums .ncell .nover em { font-style:normal; font-size:34px; color:#fff; }
  /* Xカード */
  #xLayer { position:absolute; inset:0; z-index:19; pointer-events:none; }
  .xc { position:absolute; opacity:0; width:760px; background:rgba(21,24,30,.97); border:1px solid rgba(255,255,255,.14); border-radius:20px; padding:26px 30px; box-shadow:0 16px 44px rgba(0,0,0,.6); font-family:"JPMed"; }
  .xc.big { width:940px; }
  .xc .xhead { display:flex; align-items:center; gap:16px; margin-bottom:14px; }
  .xc .xav { width:64px; height:64px; border-radius:50%; object-fit:cover; flex:none; }
  .xc .xavi { width:64px; height:64px; border-radius:50%; flex:none; display:flex; align-items:center; justify-content:center; font-family:"JPHeavy"; font-size:30px; color:#fff; }
  .xc .xname { font-family:"JPHeavy"; font-size:30px; color:#fff; display:flex; align-items:center; gap:8px; }
  .xc .xver { width:26px; height:26px; }
  .xc .xhandle { font-size:22px; color:#8b98a5; margin-top:2px; }
  .xc .xtext { font-size:32px; line-height:1.5; color:#f2f5f8; white-space:pre-wrap; }
  .xc.big .xtext { font-size:35px; }
  .xc .xmeta { margin-top:16px; font-size:21px; color:#8b98a5; }
  .xc .xmeta b { color:#e2555f; font-family:"JPHeavy"; }
  #capLayer { position:absolute; inset:0; z-index:17; pointer-events:none; }
  .cap { position:absolute; left:50%; bottom:96px; transform:translateX(-50%); width:1760px; text-align:center; opacity:0; }
  .cap .cl { display:inline-block; max-width:1760px; font-family:"JPHeavy"; font-weight:900; font-size:46px; line-height:1.32; color:#fff; white-space:nowrap; letter-spacing:.005em; paint-order:stroke fill; -webkit-text-stroke:5.5px #000; text-shadow:0 3px 7px rgba(0,0,0,.92); }
  #chapLayer { position:absolute; inset:0; z-index:25; pointer-events:none; }
  .chap { position:absolute; inset:0; opacity:0; }
  .chap .cfull { position:absolute; inset:0; -webkit-backdrop-filter:blur(22px) brightness(.4) saturate(.85); backdrop-filter:blur(22px) brightness(.4) saturate(.85); background:rgba(4,6,10,.36); }
  .chap .cinner { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); text-align:center; }
  .chap .csub2 { font-family:"Mincho",serif; font-weight:900; font-size:52px; letter-spacing:.1em; color:#ffce2e; text-shadow:0 0 2px #000,2px 2px 1px #000,0 4px 14px rgba(0,0,0,.92); margin-bottom:.2em; white-space:nowrap; }
  .chap .ctitle { font-family:"Mincho",serif; font-weight:900; font-size:130px; line-height:1.0; letter-spacing:.03em; color:#fff; white-space:nowrap; text-shadow:0 0 2px #000,3px 0 2px #000,-3px 0 2px #000,0 3px 2px #000,0 0 16px rgba(0,0,0,.95),0 9px 30px rgba(0,0,0,.9); }
  .chap .cline { width:0; height:5px; margin:26px auto 0; background:linear-gradient(90deg,transparent,#ffce2e 25%,#ffce2e 75%,transparent); border-radius:3px; }
</style></head>
<body>
  <div id="root" data-composition-id="rizin54-weightmiss" data-start="0" data-duration="__DUR__" data-width="1920" data-height="1080">
    __MEDIA__
    <div class="veil"></div><div class="vignette"></div>
    <div id="capLayer"></div><div id="numLayer"></div><div id="xLayer"></div><div id="ovLayer"></div><div id="chapLayer"></div>
  </div>
<script>
  const DATA = __DATA__;
  const ovLayer = document.getElementById('ovLayer');
  const FADE = 0.5;
  const tl = gsap.timeline({paused:true});
  const VER = "<svg class='xver' viewBox='0 0 24 24' fill='#1d9bf0'><path d='M22.25 12c0-1.43-.88-2.67-2.19-3.34.46-1.39.2-2.9-.81-3.91s-2.52-1.27-3.91-.81c-.66-1.31-1.91-2.19-3.34-2.19s-2.67.88-3.33 2.19c-1.4-.46-2.91-.2-3.92.81s-1.26 2.52-.8 3.91c-1.31.67-2.2 1.91-2.2 3.34s.89 2.67 2.2 3.34c-.46 1.39-.21 2.9.8 3.91s2.52 1.26 3.91.81c.67 1.31 1.91 2.19 3.34 2.19s2.68-.88 3.34-2.19c1.39.45 2.9.2 3.91-.81s1.27-2.52.81-3.91c1.31-.67 2.19-1.91 2.19-3.34zm-11.71 4.2L6.8 12.46l1.41-1.42 2.26 2.26 4.8-5.23 1.47 1.36-6.2 6.77z'></path></svg>";

  DATA.bg.forEach((s) => {
    const el = document.getElementById(s.id); const kb = el.querySelector('.bgmain') || el.querySelector('.bgv');
    const dur = Math.max(0.6, s.end - s.start);
    const kf = s.kb_from||{scale:1.03,x:0,y:0}, kt = s.kb_to||{scale:1.09,x:0,y:0};
    if (kb) tl.fromTo(kb,{scale:kf.scale,xPercent:kf.x,yPercent:kf.y},{scale:kt.scale,xPercent:kt.x,yPercent:kt.y,duration:dur,ease:'none'}, s.start);
    if (s.cont) tl.set(el,{opacity:1}, s.start); else tl.fromTo(el,{opacity:0},{opacity:1,duration:FADE,ease:'power1.out'}, s.start);
    if (!s.cont_end) tl.to(el,{opacity:0,duration:FADE,ease:'power1.in'}, s.end);
  });
  DATA.tags.forEach((t) => {
    if (!t.label) return;
    const el=document.createElement('div'); el.className='tag'; el.textContent=t.label; ovLayer.appendChild(el);
    if (t.cont) tl.set(el,{opacity:1,x:0},t.start); else tl.fromTo(el,{opacity:0,x:-22},{opacity:1,x:0,duration:.4,ease:'back.out(1.4)'}, t.start);
    if (!t.cont_end) tl.to(el,{opacity:0,duration:.35,ease:'power1.in'}, t.end-.35);
  });
  const badge=document.createElement('div'); badge.className='badge'; badge.textContent=DATA.channel; ovLayer.appendChild(badge);
  DATA.srcs.forEach((s) => {
    if (!s.text) return;
    const el=document.createElement('div'); el.className='src'; el.textContent=s.text; ovLayer.appendChild(el);
    if (s.cont) tl.set(el,{opacity:1},s.start); else tl.to(el,{opacity:1,duration:.4}, s.start);
    if (!s.cont_end) tl.to(el,{opacity:0,duration:.4}, s.end-.4);
  });
  // 数値カード
  const numLayer=document.getElementById('numLayer');
  DATA.nums.forEach((n) => {
    const el=document.createElement('div'); el.className='nums';
    el.innerHTML="<div class='nhead'>公開計量・体重超過</div><div class='nrow'>"
      +"<div class='ncell'><div class='nname'>パッチー・ミックス</div><div class='nsub'>契約 61.0kg → 63.85kg</div><div class='nover'>+2.85<em>kg</em></div></div>"
      +"<div class='ncell'><div class='nname'>ガジャマトフ</div><div class='nsub'>契約 57.0kg → 58.75kg</div><div class='nover'>+1.75<em>kg</em></div></div></div>";
    numLayer.appendChild(el); const cells=el.querySelectorAll('.ncell');
    if (n.cont){ tl.set(el,{opacity:1},n.start); tl.set(cells,{opacity:1,y:0},n.start); }
    else { tl.fromTo(el,{opacity:0},{opacity:1,duration:.3},n.start); tl.fromTo(cells,{opacity:0,y:26},{opacity:1,y:0,duration:.45,stagger:.12,ease:'back.out(1.3)'},n.start+.1); }
    if (!n.cont_end) tl.to(el,{opacity:0,duration:.3,ease:'power1.in'}, n.end-.3);
  });
  // Xカード
  const xLayer=document.getElementById('xLayer');
  DATA.xcards.forEach((c) => {
    const el=document.createElement('div'); el.className='xc'+(c.big?' big':'');
    if (c.big){ el.style.left='50%'; el.style.top='40%'; el.style.transform='translate(-50%,-50%)'; }
    else if (c.pos==='left'){ el.style.left='70px'; el.style.top='30%'; }
    else if (c.pos==='right'){ el.style.right='70px'; el.style.top='52%'; }
    else { el.style.left='50%'; el.style.top='40%'; el.style.transform='translateX(-50%)'; }
    const av = c.anon ? "<div class='xavi' style='background:"+(c.color||'#3b7fd4')+"'>"+(c.initial||'?')+"</div>"
                      : (c.avatar ? "<img class='xav' src='assets/xav/"+c.avatar+"'>" : "<div class='xavi' style='background:#444'>"+(c.name||'?').slice(0,1)+"</div>");
    el.innerHTML="<div class='xhead'>"+av+"<div><div class='xname'>"+c.name+(c.verified?VER:"")+"</div><div class='xhandle'>"+c.handle+"</div></div></div>"
      +"<div class='xtext'>"+c.text+"</div><div class='xmeta'>♡ <b>"+(c.likes!=null?c.likes:"—")+"</b>  ・ X(旧Twitter)より</div>";
    xLayer.appendChild(el);
    if (c.cont) tl.set(el,{opacity:1},c.start); else tl.fromTo(el,{opacity:0,y:16},{opacity:1,y:0,duration:.4,ease:'power3.out'}, c.start);
    if (!c.cont_end) tl.to(el,{opacity:0,duration:.3,ease:'power1.in'}, c.end-.3);
  });
  const capLayer=document.getElementById('capLayer');
  (DATA.caps||[]).forEach((c) => {
    const el=document.createElement('div'); el.className='cap'; el.innerHTML=c.lines.map((l)=>"<div class='cl'>"+l+"</div>").join(''); capLayer.appendChild(el);
    if (c.cont) tl.set(el,{opacity:1,y:0},c.s); else tl.fromTo(el,{opacity:0,y:8},{opacity:1,y:0,duration:.14,ease:'power1.out'}, c.s);
    if (!c.cont_end) tl.to(el,{opacity:0,duration:.1,ease:'power1.in'}, c.e);
  });
  const chapLayer=document.getElementById('chapLayer');
  (DATA.chapters||[]).forEach((ch)=>{
    const el=document.createElement('div'); el.className='chap';
    el.innerHTML="<div class='cfull'></div><div class='cinner'><div class='csub2'>"+ch.sub+"</div><div class='ctitle'>"+ch.title+"</div><div class='cline'></div></div>";
    chapLayer.appendChild(el);
    const inner=el.querySelector('.cinner'), ttl=el.querySelector('.ctitle'), line=el.querySelector('.cline');
    if (ch.cont){ tl.set(el,{opacity:1},0); tl.set(inner,{scale:1.0},0); tl.set(ttl,{letterSpacing:'0.03em',opacity:1},0); tl.set(line,{width:560},0); }
    else { tl.fromTo(el,{opacity:0},{opacity:1,duration:.2,ease:'power1.out'}, ch.start);
      tl.fromTo(inner,{scale:1.1},{scale:1.0,duration:.55,ease:'power3.out'}, ch.start);
      tl.fromTo(ttl,{letterSpacing:'0.2em',opacity:0},{letterSpacing:'0.03em',opacity:1,duration:.5,ease:'power2.out'}, ch.start+0.04);
      tl.fromTo(line,{width:0},{width:560,duration:.55,ease:'power2.out'}, ch.start+0.18); }
    if (!ch.cont_end) tl.to(el,{opacity:0,duration:.3,ease:'power1.in'}, ch.end-0.3);
  });
  window.__timelines=window.__timelines||{}; window.__timelines['rizin54-weightmiss']=tl;
</script></body></html>
"""

HTML = (TEMPLATE.replace("__TEXTFX_CSS__", TEXTFX_CSS).replace("__TEXTFX_JS__", TEXTFX_JS)
        .replace("__DATA__", json.dumps(DATA, ensure_ascii=False)).replace("__MEDIA__", MEDIA).replace("__DUR__", str(DUR)))
(TPL / "index.html").write_text(HTML, encoding="utf-8")

over = {a: n for a, n in used.items() if n >= 3}
vid = sum(s["end"] - s["start"] for s in bg_segs if s.get("video"))
print(f"-> {TPL/'index.html'}")
print(f"bg:{len(bg_segs)} xcards:{len(DATA['xcards'])} nums:{len(DATA['nums'])} chapters:{len(DATA['chapters'])} caps:{len(DATA['caps'])} total:{DUR}s")
print(f"背景映像比率:{100*vid/max(1,DUR):.0f}%  最大セグ:{max(s['end']-s['start'] for s in bg_segs):.1f}s")
print(f"3回以上使用:{over if over else 'なし'}")
