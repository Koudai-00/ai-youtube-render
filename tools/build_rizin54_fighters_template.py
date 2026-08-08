"""RIZIN.54 全選手紹介まとめ 横テンプレ(1920x1080)生成【評伝型・プロトタイプ=メインカード】。
構成: 対戦カード紹介→クレベル経歴(+STATカード)→朝倉未来戦フィニッシュ20秒(ナレ無しダック)
      →秋元経歴(+STATカード)→パッチミックス戦フィニッシュ20秒(ダック)→勝敗予想。
背景=本人実写(試合映像/王座/KO)＋公式カード＋生い立ちムード(新規Pexels)。連続Ken Burns。
オーバーレイ: STATカード(名前/身長体重/リーチ/出身/戦績)、ダック帯(実映像・ナレ無し・字幕停止)、章4、DOM字幕、出典。
時間分割レンダー対応(HF_WIN_START/END, cont/cont_end)。評伝クローン声。
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
TPL = ROOT / "hyperframes" / "templates" / "rizin54-fighters"
TIM = json.loads((ROOT / "subtitles" / "out" / "rizin54_fighters" / "timings.json").read_text(encoding="utf-8"))
BEATS = TIM["beats"]
DUCKS = TIM["ducks"]
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


def _norm(s: str) -> str:
    return s.replace("、", "").replace("。", "").replace(" ", "").replace("　", "")


def beats_of(sec: str):
    return [b for b in BEATS if b["sec"] == sec]


def beat_at(sub: str):
    nsub = _norm(sub)
    for b in BEATS:
        if nsub in _norm(b["text"]):
            return b
    raise SystemExit(f"BEAT NOT FOUND: {sub}")


# ============ 背景レジストリ (img / vid) ============
# 実写クリップ(video)。それ以外(card_main/*_portrait/akimoto_win)は画像。
VID = {
    "fight_kleber_asakura", "fight_akimoto_mix", "fight_akimoto_kintaro",
    "kb_action", "kb_belt", "kb_face", "kb_rizin49", "kb_shayd_ko", "talk_aoki",
    "akimoto_r1", "akimoto_stand", "px_labor", "px_bjj", "px_soccer",
}
# contain表示(全体を見せる)=公式カードのみ。他はcover。
CONTAIN = {"card_main"}


def is_vid(name: str) -> bool:
    return name in VID


SRC_OF = {
    "card_main": "画像: RIZIN FF公式",
    "kleber_portrait": "画像: RIZIN FF公式", "akimoto_portrait": "画像: RIZIN FF公式",
    "akimoto_win": "試合映像: RIZIN(RIZIN.48)",
    "fight_kleber_asakura": "試合映像: RIZIN(RIZIN.28)",
    "fight_akimoto_mix": "試合映像: RIZIN(RIZIN.52)", "fight_akimoto_kintaro": "試合映像: RIZIN(RIZIN.48)",
    "akimoto_r1": "試合映像: RIZIN(RIZIN.48)", "akimoto_stand": "試合映像: RIZIN(RIZIN.48)",
    "kb_action": "試合映像: RIZIN", "kb_face": "試合映像: RIZIN", "kb_belt": "試合映像: RIZIN",
    "kb_rizin49": "試合映像: RIZIN(RIZIN.49)", "kb_shayd_ko": "試合映像: RIZIN(2025.5.4)",
    "talk_aoki": "出典: YouTube「青木真也」",
    "px_labor": "映像: Pexels", "px_bjj": "映像: Pexels", "px_soccer": "映像: Pexels",
}


def src_of(name: str) -> str:
    return SRC_OF.get(name, "画像: RIZIN FF公式")


# ============ セクション別・ビート順の背景 ============
# 同一素材は原則1回。fight_*の2回使用はナレが同一シーンに2度言及＋重要な場合のみ(下記で担保)。
SECTION_BG = {
    # 対戦カード紹介(b0-b1は公式カード=merge, b2でクレベルへ)
    "c_card": ["card_main", "card_main", "kb_face"],
    # クレベル(11): name/stats/原点差別/来日いじめ工場/柔術ソウザ/寝技/ボペガー/朝倉三角/王座2度/シェイドKO負け/lead-in
    "c_kleber": ["kleber_portrait", "kleber_portrait", "px_labor", "px_labor", "px_bjj",
                 "kb_action", "kb_belt", "fight_kleber_asakura", "kb_rizin49", "kb_shayd_ko", "kb_face"],
    # 秋元(9): name/stats/サッカー朝倉/高校辞退MMA/破壊力/金太郎TKO/元谷判定負け/JTTパッチ撃破/lead-in(歓喜)
    "c_akimoto": ["akimoto_portrait", "akimoto_portrait", "px_soccer", "akimoto_stand", "akimoto_r1",
                  "fight_akimoto_kintaro", "akimoto_r1", "fight_akimoto_mix", "akimoto_win"],
    # 勝敗予想(3)
    "c_yosou": ["card_main", "talk_aoki", "kb_action"],
}

# ============ STATカード ============
# 名前/ローマ字/国旗/生年月日(年齢)/身長/体重/リーチ/出身/所属/戦績。
# 顔を避けて配置(クレベル=顔左→カード右 / 秋元=顔中央→カード左)。
STATS = [
    {"anchor": "クレベル・コイケ・エルベスト", "hold_to": "そのうち一本勝ちは",
     "side": "right", "flag": "BRA", "flag_c": "#3aa856", "name": "クレベル・コイケ", "roma": "KLEBER KOIKE",
     "rows": [("生年月日", "1989.10.16（36歳）"), ("身長 / 体重", "178cm / 66.0kg"),
              ("リーチ", "183cm"), ("出身", "ブラジル・サンパウロ"), ("所属", "ボンサイ柔術"),
              ("戦績", "35勝9敗1分")], "record_hi": "一本 29"},
    {"anchor": "続いては挑戦者", "hold_to": "唯一の黒星以外",
     "side": "left", "flag": "JPN", "flag_c": "#d64550", "name": "秋元 強真", "roma": "KYOMA AKIMOTO",
     "rows": [("生年月日", "2006.3.8（20歳）"), ("身長 / 体重", "177cm / 66.0kg"),
              ("リーチ", "177.5cm"), ("出身", "千葉県旭市"), ("所属", "JAPAN TOP TEAM"),
              ("戦績", "12勝1敗")], "record_hi": "KO/TKO 7・一本 2"},
]

CHANNEL = "格闘ニュースラボ"

SECTION_TAGS = {
    "c_card": "メインイベント", "c_kleber": "クレベル・コイケ",
    "c_akimoto": "秋元 強真", "c_yosou": "勝敗予想",
}

# 長尺ビート分割(単調回避・ナレ一致): (anchor, 2nd_asset, frac)
SPLITS = []


KB_VARIANTS = [
    ((1.03, -2.5, -1.2), (1.11, 2.5, 1.2)),
    ((1.11, 2.5, 1.0), (1.03, -2.5, -0.6)),
    ((1.04, 3.0, -0.8), (1.12, -3.0, 1.0)),
    ((1.12, -2.8, 1.2), (1.04, 2.8, -1.0)),
]


def kb_for(kb_idx, seg_start, seg_end, vis_start, vis_end):
    (s0, x0, y0), (s1, x1, y1) = KB_VARIANTS[kb_idx % 4]
    basis = max(0.1, (seg_end - seg_start) + FADE)

    def lerp(p):
        p = min(1.0, max(0.0, p))
        return {"scale": round(s0 + (s1 - s0) * p, 4),
                "x": round(x0 + (x1 - x0) * p, 3),
                "y": round(y0 + (y1 - y0) * p, 3)}
    return lerp((vis_start - seg_start) / basis), lerp((vis_end - seg_start) / basis)


def build_bg_segments():
    used = Counter()
    beat_rows = []
    for sid in SECORDER:
        lst = SECTION_BG[sid]
        bts = beats_of(sid)
        if len(bts) != len(lst):
            raise SystemExit(f"SECTION_BG mismatch {sid}: beats={len(bts)} bg={len(lst)}")
        for b, asset in zip(bts, lst):
            beat_rows.append([b, asset, sid])
    segs = []
    for b, asset, sid in beat_rows:
        if segs and segs[-1]["name"] == asset and segs[-1]["sec"] == sid and (b["end"] - segs[-1]["start"]) <= 15.0:
            segs[-1]["end"] = b["end"]
        else:
            segs.append({"start": b["start"], "end": b["end"], "name": asset, "sec": sid, "duck": False})
    # 各セクション先頭背景をセクション開始(=章カード開始)まで前詰め→前セクション末尾がそこで終わる
    seen_sec = set()
    for s in segs:
        if s["sec"] not in seen_sec:
            s["start"] = SECS[s["sec"]]["start"]
            seen_sec.add(s["sec"])
    for i in range(len(segs) - 1):
        segs[i]["end"] = segs[i + 1]["start"]
    segs[0]["start"] = 0.0
    # 長尺ビート分割
    for anchor, asset2, frac in SPLITS:
        b = beat_at(anchor)
        for i, s in enumerate(segs):
            if s["start"] <= b["start"] < s["end"] and s["end"] - s["start"] > 9.0:
                cut = round(s["start"] + (s["end"] - s["start"]) * frac, 3)
                new = {"start": cut, "end": s["end"], "name": asset2, "sec": s["sec"], "duck": False}
                s["end"] = cut
                segs.insert(i + 1, new)
                break
    # ダック(ナレ無し試合映像20秒)をbgセグメントとして挿入(該当時間帯を上書き)
    duck_map = {"fight_kleber_asakura": "fight_kleber_asakura", "fight_akimoto_mix": "fight_akimoto_mix"}
    for d in DUCKS:
        ds, de, clip = d["start"], d["end"], duck_map[d["clip"]]
        # ダック区間に重なる既存セグメントを削り、ダックセグメントを差し込む
        newsegs = []
        for s in segs:
            if s["end"] <= ds or s["start"] >= de:
                newsegs.append(s); continue
            if s["start"] < ds:
                newsegs.append({**s, "end": ds})
            if s["end"] > de:
                newsegs.append({**s, "start": de})
        newsegs.append({"start": ds, "end": de, "name": clip, "sec": d["sec"], "duck": True})
        segs = sorted(newsegs, key=lambda x: x["start"])
    # 隙間埋め/末尾
    for i in range(len(segs) - 1):
        if segs[i]["end"] < segs[i + 1]["start"]:
            segs[i]["end"] = segs[i + 1]["start"]
    segs[-1]["end"] = TOTAL
    # 微小セグメント(<0.6s)を隣接へ吸収(ダック carve で生じるsliver対策)
    cleaned = []
    for s in segs:
        if s["end"] - s["start"] < 0.6 and cleaned:
            cleaned[-1]["end"] = s["end"]
        else:
            cleaned.append(s)
    segs = cleaned
    vi = 0
    for s in segs:
        nm = s["name"]
        s["video"] = is_vid(nm)
        s["contain"] = nm in CONTAIN
        ext = "mp4" if s["video"] else "jpg"
        sub = "bgvid" if s["video"] else "img"
        p = TPL / "assets" / sub / f"{nm}.{ext}"
        if not p.exists():
            raise SystemExit(f"MISSING BG: {p}")
        s["src"] = src_of(nm)
        s["asset"] = f"{sub}/{nm}.{ext}"
        s["id"] = f"bg{vi}"
        s["track"] = 40 + (vi % 12)
        s["kb"] = vi % 4
        # ダック/contain は Ken Burns 弱め(または無し)
        if s["duck"]:
            s["kb_from"] = {"scale": 1.0, "x": 0, "y": 0}
            s["kb_to"] = {"scale": 1.0, "x": 0, "y": 0}
        elif s["contain"]:
            s["kb_from"] = {"scale": 1.0, "x": 0, "y": 0}
            s["kb_to"] = {"scale": 1.04, "x": 0, "y": 0}
        else:
            f, t = kb_for(s["kb"], s["start"], s["end"], s["start"], s["end"])
            s["kb_from"], s["kb_to"] = f, t
        if s["video"]:
            cd = clip_dur(str(p))
            seglen = (s["end"] - s["start"]) + FADE
            s["mstart"] = 0.0
            s["mdur"] = round(min(seglen + 0.15, cd - 0.05), 3)
            if s["mdur"] < seglen - 0.3:
                s["loop"] = True
                s["mdur"] = round(cd - 0.05, 3)
        vi += 1
        used[nm] += 1
    for s in segs:
        s["start"] = round(s["start"], 3); s["end"] = round(s["end"], 3)
    return segs, used


CAP_LINE_MAX = 23.0
CAP_BREAK_AFTER = set("、。，・！？」』）】")
CAP_PARTICLE = set("はがをにでとへものやか")
DUCK_RANGES = [(d["start"], d["end"]) for d in DUCKS]


def in_duck(t):
    return any(ds - 0.05 <= t < de for ds, de in DUCK_RANGES)


def build_caps():
    def width(s):
        return sum(0.5 if ch.isascii() else 1.0 for ch in s)

    def wrap_lines(s):
        lines, cur = [], ""
        i = 0
        while i < len(s):
            cur += s[i]
            if width(cur) >= CAP_LINE_MAX and i < len(s) - 1:
                cut = len(cur)
                for j in range(len(cur) - 1, max(0, len(cur) - 10), -1):
                    ch = cur[j - 1]
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
        if in_duck(b["start"]):
            continue
        start = b["start"]
        nxt = BEATS[i + 1]["start"] if i + 1 < len(BEATS) else b["end"] + 0.4
        end = min(b["end"] + 0.30, nxt - 0.05)
        if end <= start:
            end = max(b["end"], start + 0.4)
        txt = b["text"].replace("「", "").replace("」", "")
        lines = wrap_lines(txt)
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
    for k in range(len(caps) - 1):
        if caps[k]["e"] > caps[k + 1]["s"]:
            caps[k]["e"] = round(caps[k + 1]["s"] - 0.02, 2)
    return caps


def build_stats():
    out = []
    for st in STATS:
        b0 = beat_at(st["anchor"])
        b1 = beat_at(st["hold_to"])
        d = dict(st)
        d["start"] = round(b0["start"] + 0.35, 2)
        d["end"] = round(b1["end"] + 0.10, 2)
        out.append(d)
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


def build_duck_badges():
    out = []
    for d in DUCKS:
        out.append({"start": round(d["start"] + 0.2, 2), "end": round(d["end"] - 0.2, 2)})
    return out


bg_segs, used = build_bg_segments()
DATA = {
    "total": DUR,
    "bg": bg_segs,
    "tags": [{"start": SECS[s]["start"], "end": SECS[s]["end"], "label": SECTION_TAGS.get(s, "")} for s in SECORDER],
    "stats": build_stats(),
    "ducks": build_duck_badges(),
    "srcs": _src_windows(bg_segs),
    "caps": build_caps(),
    "chapters": TIM.get("chapters", []),
    "channel": CHANNEL,
}

# ============ 窓分割 ============
if WINDOWED:
    off, wdur = WIN_START, round(WIN_END - WIN_START, 3)
    def _win_timed(items, ks="start", ke="end"):
        out = []
        for it in items:
            ns, ne = it[ks] - off, it[ke] - off
            if ne <= 0.001 or ns >= wdur - 0.001:
                continue
            it = dict(it); it["cont"] = ns < 0.05; it["cont_end"] = ne > wdur - 0.05
            it[ks] = round(max(0.0, ns), 3); it[ke] = round(min(wdur, ne), 3)
            out.append(it)
        return out
    def _win_bg(items):
        out = []
        for it in items:
            it = dict(it)
            ns, ne = it["start"] - off, it["end"] - off
            if ne <= 0.001 or ns >= wdur - 0.001:
                continue
            it["cont"] = ns < 0.05
            it["cont_end"] = ne > wdur - 0.05
            vis0 = max(it["start"], off)
            vis1 = min(it["end"], off + wdur)
            if not it["duck"] and not it["contain"]:
                f, t = kb_for(it.get("kb", 0), it["start"], it["end"], vis0, vis1)
                it["kb_from"], it["kb_to"] = f, t
            if it["video"]:
                ms = it.get("mstart", 0.0)
                if ns < 0:
                    ms = round(ms - ns, 3)
                dd = it.get("mdur", ne - max(0.0, ns))
                st = max(0.0, ns)
                ddd = min(dd, wdur - st) if it["cont_end"] else min(dd, (min(wdur, ne) - st) + FADE)
                it["mstart"] = ms; it["mdur"] = round(max(0.3, ddd), 3)
            it["start"] = round(max(0.0, ns), 3); it["end"] = round(min(wdur, ne), 3)
            out.append(it)
        return out
    DATA["bg"] = _win_bg(bg_segs)
    for k in ("stats", "ducks", "tags", "srcs", "chapters"):
        DATA[k] = _win_timed(DATA[k])
    DATA["caps"] = _win_timed(DATA["caps"], "s", "e")
    DUR = wdur; DATA["total"] = wdur
    bg_segs = DATA["bg"]

# ============ メディア要素 ============
media = []
for s in bg_segs:
    contain_cls = " contain" if s.get("contain") else ""
    if s["video"]:
        media.append(
            f'<div class="bg{contain_cls}" id="{s["id"]}"><div class="bgfill" style="background-image:url(assets/{s["asset"]})"></div>'
            f'<video class="bgv" id="{s["id"]}-v" src="assets/{s["asset"]}" muted playsinline '
            f'data-start="{s["start"]}" data-duration="{s.get("mdur",1)}" data-media-start="{s.get("mstart",0)}" data-track-index="{s["track"]}"></video></div>')
    else:
        media.append(
            f'<div class="bg{contain_cls}" id="{s["id"]}"><div class="bgfill" style="background-image:url(assets/{s["asset"]})"></div>'
            f'<div class="bgmain" style="background-image:url(assets/{s["asset"]})"></div></div>')
media.append('<audio id="narr" src="assets/audio/narration.wav" data-start="0" data-track-index="70" data-volume="1"></audio>')
media.append('<audio id="bgm" src="assets/audio/bgm.m4a" data-start="0" data-duration="__DUR__" data-track-index="71" data-volume="0.08"></audio>')
MEDIA = "\n    ".join(media)

LIB = ROOT / "hyperframes" / "_lib" / "textfx"
TEXTFX_CSS = (LIB / "textfx.css").read_text(encoding="utf-8")
TEXTFX_JS = (LIB / "textfx.js").read_text(encoding="utf-8")

TEMPLATE = r"""<!doctype html>
<!-- RIZIN.54 全選手紹介まとめ 1920x1080【評伝型・プロトタイプ(メインカード)】 -->
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
  #root { position:relative; width:1920px; height:1080px; overflow:hidden; background:#05070c; font-family:"JPHeavy","Noto Sans JP",sans-serif; color:#fff; }

  .bg { position:absolute; inset:0; z-index:1; opacity:0; overflow:hidden; will-change:opacity; }
  .bgfill { position:absolute; inset:-4%; background-size:cover; background-position:center; filter:blur(22px) brightness(.42) saturate(.9); transform:scale(1.1); }
  .bgmain { position:absolute; inset:0; background-size:cover; background-position:center top; background-repeat:no-repeat; will-change:transform; }
  .bg.contain .bgmain { background-size:contain; background-position:center; }
  .bg .bgv { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; transform:translateZ(0); backface-visibility:hidden; }

  .veil { position:absolute; inset:0; z-index:5; pointer-events:none; background:linear-gradient(180deg, rgba(0,0,0,.34) 0%, rgba(0,0,0,.02) 20%, rgba(0,0,0,.02) 52%, rgba(0,0,0,.42) 82%, rgba(0,0,0,.80) 100%); }
  .vignette { position:absolute; inset:0; z-index:6; pointer-events:none; background:radial-gradient(ellipse at 50% 46%, transparent 0 56%, rgba(0,0,0,.46) 100%); }

  .tag { position:absolute; z-index:20; left:56px; top:52px; padding:8px 24px 8px 18px; background:rgba(8,9,12,.6); border-left:5px solid #e7b94a; border-radius:2px; font-family:"Mincho",serif; font-size:34px; font-weight:900; letter-spacing:.05em; color:#fff; text-shadow:0 0 2px #000,0 2px 8px rgba(0,0,0,.9); white-space:nowrap; opacity:0; -webkit-backdrop-filter:blur(6px); backdrop-filter:blur(6px); }
  .badge { position:absolute; z-index:20; right:56px; top:54px; padding:9px 22px; background:rgba(8,8,10,.82); border:2px solid rgba(255,213,74,.85); border-radius:40px; font-family:"JPHeavy"; font-size:26px; color:#ffe89a; letter-spacing:.03em; text-shadow:0 1px 3px rgba(0,0,0,.9); }
  .src { position:absolute; z-index:20; left:40px; bottom:24px; padding:3px 11px; background:rgba(0,0,0,.62); border-left:3px solid rgba(255,213,74,.85); border-radius:2px; font-family:"JPMed"; font-size:18px; color:#e2e2e2; letter-spacing:.01em; text-shadow:0 1px 2px rgba(0,0,0,.9); opacity:0; }

  /* STATカード */
  #statLayer { position:absolute; inset:0; z-index:18; pointer-events:none; }
  .stat { position:absolute; top:50%; transform:translateY(-50%); width:640px; opacity:0;
          background:linear-gradient(160deg, rgba(10,13,20,.93), rgba(14,17,26,.86)); border-radius:18px;
          border:1px solid rgba(255,255,255,.10); box-shadow:0 20px 60px rgba(0,0,0,.6); overflow:hidden; }
  .stat.left { left:70px; } .stat.right { right:70px; }
  .stat .shead { padding:26px 34px 18px; border-bottom:2px solid rgba(255,213,74,.5);
                 background:linear-gradient(180deg, rgba(231,185,74,.14), transparent); }
  .stat .sflag { display:inline-block; padding:3px 14px; border-radius:6px; font-family:"JPHeavy"; font-size:23px; letter-spacing:.14em; color:#fff; text-shadow:0 1px 2px rgba(0,0,0,.6); margin-bottom:8px; }
  .stat .sname { font-family:"Mincho",serif; font-weight:900; font-size:62px; line-height:1.02; color:#fff; letter-spacing:.02em;
                 paint-order:stroke fill; text-shadow:0 0 2px #000,2px 0 1px #000,-2px 0 1px #000,0 2px 1px #000,0 6px 16px rgba(0,0,0,.9); white-space:nowrap; }
  .stat .sroma { font-family:"JPHeavy"; font-size:24px; letter-spacing:.16em; color:#ffce6a; margin-top:6px; }
  .stat .sbody { padding:16px 34px 26px; }
  .stat .srow { display:flex; align-items:baseline; gap:14px; padding:10px 0; border-bottom:1px solid rgba(255,255,255,.07); }
  .stat .srow:last-child { border-bottom:0; }
  .stat .sk { flex:none; width:180px; font-family:"JPMed"; font-size:24px; color:#9fb0c4; letter-spacing:.02em; }
  .stat .sv { font-family:"JPHeavy"; font-size:32px; color:#fff; letter-spacing:.01em; font-variant-numeric:tabular-nums; }
  .stat .srow.rec .sv { color:#ffce2e; }
  .stat .srec2 { margin-top:4px; font-family:"JPHeavy"; font-size:23px; color:#ff9a52; letter-spacing:.02em; }

  /* ダック(ナレ無し試合映像)帯 */
  #duckLayer { position:absolute; inset:0; z-index:19; pointer-events:none; }
  .duck { position:absolute; left:50%; top:60px; transform:translateX(-50%); opacity:0;
          padding:9px 30px; background:rgba(6,8,12,.66); border:2px solid rgba(255,255,255,.22); border-radius:40px;
          font-family:"JPHeavy"; font-size:27px; letter-spacing:.06em; color:#fff; white-space:nowrap;
          text-shadow:0 2px 6px rgba(0,0,0,.9); -webkit-backdrop-filter:blur(5px); backdrop-filter:blur(5px); }
  .duck .dred { color:#ff5f52; }

  #chapLayer { position:absolute; inset:0; z-index:25; pointer-events:none; }
  .chap { position:absolute; inset:0; opacity:0; }
  .chap .cfull { position:absolute; inset:0; -webkit-backdrop-filter:blur(22px) brightness(.4) saturate(.85); backdrop-filter:blur(22px) brightness(.4) saturate(.85); background:rgba(4,6,10,.36); }
  .chap .cinner { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); text-align:center; }
  .chap .csub2 { font-family:"Mincho",serif; font-weight:900; font-size:52px; letter-spacing:.1em; color:#ffce2e; text-shadow:0 0 2px #000,2px 2px 1px #000,0 4px 14px rgba(0,0,0,.92); margin-bottom:.20em; white-space:nowrap; }
  .chap .ctitle { font-family:"Mincho",serif; font-weight:900; font-size:150px; line-height:1.0; letter-spacing:.04em; color:#fff; white-space:nowrap; text-shadow:0 0 2px #000,3px 0 2px #000,-3px 0 2px #000,0 3px 2px #000,0 0 16px rgba(0,0,0,.95),0 9px 30px rgba(0,0,0,.9); }
  .chap .cline { width:0; height:5px; margin:26px auto 0; background:linear-gradient(90deg,transparent,#ffce2e 25%,#ffce2e 75%,transparent); border-radius:3px; }

  #capLayer { position:absolute; inset:0; z-index:17; pointer-events:none; }
  .cap { position:absolute; left:50%; bottom:96px; transform:translateX(-50%); width:1760px; text-align:center; opacity:0; }
  .cap .cl { display:inline-block; max-width:1760px; font-family:"JPHeavy"; font-weight:900; font-size:46px; line-height:1.32; color:#fff; white-space:nowrap; letter-spacing:.005em; paint-order:stroke fill; -webkit-text-stroke:5.5px #000; text-shadow:0 3px 7px rgba(0,0,0,.92); }
</style>
</head>
<body>
  <div id="root" data-composition-id="rizin54-fighters" data-start="0" data-duration="__DUR__" data-width="1920" data-height="1080">
    __MEDIA__
    <div class="veil"></div>
    <div class="vignette"></div>
    <div id="capLayer"></div>
    <div id="statLayer"></div>
    <div id="duckLayer"></div>
    <div id="ovLayer"></div>
    <div id="chapLayer"></div>
  </div>
<script>
  const DATA = __DATA__;
  const ovLayer = document.getElementById('ovLayer');
  const FADE = 0.5;
  const tl = gsap.timeline({paused:true});

  DATA.bg.forEach((s) => {
    const el = document.getElementById(s.id);
    const kb = el.querySelector('.bgmain') || el.querySelector('.bgv');
    const dur = Math.max(0.6, s.end - s.start);
    const kf = s.kb_from || {scale:1.03,x:0,y:0}, kt = s.kb_to || {scale:1.09,x:0,y:0};
    if (kb) tl.fromTo(kb,
      {scale:kf.scale, xPercent:kf.x, yPercent:kf.y},
      {scale:kt.scale, xPercent:kt.x, yPercent:kt.y, duration:dur, ease:'none'}, s.start);
    if (s.cont) tl.set(el, {opacity:1}, s.start);
    else tl.fromTo(el, {opacity:0}, {opacity:1, duration:FADE, ease:'power1.out'}, s.start);
    if (!s.cont_end) tl.to(el, {opacity:0, duration:FADE, ease:'power1.in'}, s.end);
  });

  DATA.tags.forEach((t) => {
    if (!t.label) return;
    const el = document.createElement('div'); el.className='tag'; el.textContent=t.label; ovLayer.appendChild(el);
    if (t.cont) tl.set(el,{opacity:1,x:0},t.start);
    else tl.fromTo(el,{opacity:0,x:-22},{opacity:1,x:0,duration:.4,ease:'back.out(1.4)'}, t.start);
    if (!t.cont_end) tl.to(el,{opacity:0,duration:.35,ease:'power1.in'}, t.end-.35);
  });
  const badge = document.createElement('div'); badge.className='badge'; badge.textContent=DATA.channel; ovLayer.appendChild(badge);
  DATA.srcs.forEach((s) => {
    if (!s.text) return;
    const el = document.createElement('div'); el.className='src'; el.textContent=s.text; ovLayer.appendChild(el);
    if (s.cont) tl.set(el,{opacity:1},s.start); else tl.to(el,{opacity:1,duration:.4}, s.start);
    if (!s.cont_end) tl.to(el,{opacity:0,duration:.4}, s.end-.4);
  });

  // STATカード
  const statLayer = document.getElementById('statLayer');
  DATA.stats.forEach((st) => {
    const el = document.createElement('div'); el.className='stat '+st.side;
    const rows = st.rows.map((r)=>{
      const rec = (r[0]==='戦績');
      return "<div class='srow"+(rec?" rec":"")+"'><div class='sk'>"+r[0]+"</div><div class='sv'>"+r[1]
        + (rec && st.record_hi ? "<div class='srec2'>"+st.record_hi+"</div>" : "") + "</div></div>";
    }).join('');
    el.innerHTML = "<div class='shead'><div class='sflag' style='background:"+(st.flag_c||'#555')+"'>"+st.flag+"</div><div class='sname'>"+st.name+"</div><div class='sroma'>"+st.roma+"</div></div>"
      + "<div class='sbody'>"+rows+"</div>";
    statLayer.appendChild(el);
    const dx = st.side==='left' ? -40 : 40;
    if (st.cont) tl.set(el,{opacity:1,x:0},st.start);
    else tl.fromTo(el,{opacity:0,x:dx},{opacity:1,x:0,duration:.5,ease:'power3.out'}, st.start);
    if (!st.cont_end) tl.to(el,{opacity:0,duration:.35,ease:'power1.in'}, st.end-.35);
  });

  // ダック帯(ナレ無し・実際の試合映像)
  const duckLayer = document.getElementById('duckLayer');
  DATA.ducks.forEach((d) => {
    const el = document.createElement('div'); el.className='duck';
    el.innerHTML = "<span class='dred'>●</span> 実際の試合映像";
    duckLayer.appendChild(el);
    if (d.cont) tl.set(el,{opacity:1,y:0},d.start);
    else tl.fromTo(el,{opacity:0,y:-14},{opacity:1,y:0,duration:.4,ease:'power2.out'}, d.start);
    if (!d.cont_end) tl.to(el,{opacity:0,duration:.35,ease:'power1.in'}, d.end-.35);
  });

  const capLayer = document.getElementById('capLayer');
  (DATA.caps||[]).forEach((c) => {
    const el = document.createElement('div'); el.className='cap';
    el.innerHTML = c.lines.map((l)=>"<div class='cl'>"+l+"</div>").join('');
    capLayer.appendChild(el);
    if (c.cont) tl.set(el,{opacity:1,y:0},c.s);
    else tl.fromTo(el,{opacity:0,y:8},{opacity:1,y:0,duration:.14,ease:'power1.out'}, c.s);
    if (!c.cont_end) tl.to(el,{opacity:0,duration:.1,ease:'power1.in'}, c.e);
  });

  const chapLayer = document.getElementById('chapLayer');
  (DATA.chapters||[]).forEach((ch)=>{
    const el=document.createElement('div'); el.className='chap';
    el.innerHTML="<div class='cfull'></div><div class='cinner'><div class='csub2'>"+ch.sub+"</div><div class='ctitle'>"+ch.title+"</div><div class='cline'></div></div>";
    chapLayer.appendChild(el);
    const inner=el.querySelector('.cinner'), ttl=el.querySelector('.ctitle'), line=el.querySelector('.cline');
    if (ch.cont) { tl.set(el,{opacity:1},0); tl.set(inner,{scale:1.0},0); tl.set(ttl,{letterSpacing:'0.04em',opacity:1},0); tl.set(line,{width:560},0); }
    else {
      tl.fromTo(el,{opacity:0},{opacity:1,duration:.2,ease:'power1.out'}, ch.start);
      tl.fromTo(inner,{scale:1.1},{scale:1.0,duration:.55,ease:'power3.out'}, ch.start);
      tl.fromTo(ttl,{letterSpacing:'0.2em',opacity:0},{letterSpacing:'0.04em',opacity:1,duration:.5,ease:'power2.out'}, ch.start+0.04);
      tl.fromTo(line,{width:0},{width:560,duration:.55,ease:'power2.out'}, ch.start+0.18);
    }
    if (!ch.cont_end) tl.to(el,{opacity:0,duration:.3,ease:'power1.in'}, ch.end-0.3);
  });

  window.__timelines = window.__timelines || {};
  window.__timelines['rizin54-fighters'] = tl;
</script>
</body>
</html>
"""

HTML = (TEMPLATE.replace("__TEXTFX_CSS__", TEXTFX_CSS)
                .replace("__TEXTFX_JS__", TEXTFX_JS)
                .replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
                .replace("__MEDIA__", MEDIA)
                .replace("__DUR__", str(DUR)))
(TPL / "index.html").write_text(HTML, encoding="utf-8")

over = {a: n for a, n in used.items() if n >= 3}
vid_time = sum(s["end"] - s["start"] for s in bg_segs if s.get("video"))
print(f"-> {TPL / 'index.html'}")
print(f"bg segs:{len(bg_segs)} stats:{len(DATA['stats'])} ducks:{len(DATA['ducks'])} chapters:{len(DATA['chapters'])} caps:{len(DATA['caps'])} total:{DUR}s")
print(f"背景セグメント最大尺: {max(s['end']-s['start'] for s in bg_segs):.1f}s")
print(f"★背景の【映像】比率: {100*vid_time/max(1,DUR):.0f}%")
print(f"3回以上使用: {over if over else 'なし'}")
print("使用回数:", dict(used))
