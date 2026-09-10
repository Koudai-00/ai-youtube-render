# -*- coding: utf-8 -*-
"""平本蓮×ダウトベック 判定物議 ショート: 背景セグメントを作り xfade で1本に連結。
   ・尺は subtitles/out/hiramoto_dautbek_short/timings.json のビート境界から自動算出。
   ・RIZIN公式の【速報】第6試合(1920x1080)は、右端のPPV広告バナーと上部の配信帯を
     crop で除去してから blur-contain する。下部のスコアボードはラウンドと残り時間が
     読み取れる公式情報なので残す。
   ・公式の縦型クリップ(1080x1920)はそのまま cover で使う。
   ・★ダウンは 1R残り2:40＝速報動画の t=140秒（ラウンドクロックで確定）。"""
from __future__ import annotations
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "hiramoto_dautbek_short"
TPL = ROOT / "hyperframes" / "templates" / "hiramoto-dautbek-short"
BGV = TPL / "assets" / "bgvid"
SRC = ROOT / "assets" / "source" / "episode_hiramoto_dautbek"
CLIP = SRC / "clips"
PX = SRC / "pexels"
THUMB = ROOT / "assets" / "thumbnails" / "柏木サムネイル.png"
WORK = TPL / "assets" / "_bgwork"
for d in (BGV, WORK):
    d.mkdir(parents=True, exist_ok=True)
OUT = BGV / "hiramoto_bg_full.mp4"

FPS = 30
D = 0.45
ENC = ["-r", "30", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-g", "30", "-keyint_min", "30", "-crf", "20"]
# ★放送バナー(左上の大会名帯・右上のRIZIN LIVEロゴ)は上端120pxに収まるので落とす
DEBAND = "crop=1920:958:0:122,setsar=1"
BC = ("split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
      "gblur=sigma=26,eq=brightness=-0.30[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p")
COVER = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p"

SOKUHO = CLIP / "sokuho_6.mp4"          # RIZIN公式【速報】第6試合(1R全編)
HL6 = CLIP / "hl6_IShJJtI2LhU.mp4"      # RIZIN公式 縦型ハイライト(ダウン前後)
FACE = CLIP / "v_QxC20-pTRZ4.mp4"       # RIZIN公式 縦型 フェイスオフ

# ★上部の配信帯(〜y114)と右端のPPV広告(x1672〜)を落としてから使う
DEBAND = "crop=1672:966:0:114,setsar=1"

# (beat_id, 分割, kind, source, 素材内の開始秒, 出典ラベル)
PLAN = [
    ("t0",  None, "cover", FACE,     2.0, "RIZIN公式"),
    ("h1",  None, "cover", HL6,      1.0, "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("h2",  None, "bc",    SOKUHO,  95.0, "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1",  None, "bc",    SOKUHO, 136.0, "RIZIN公式 超RIZIN.5 第6試合"),   # ★1R残り2:40のダウン
    ("c2",  None, "bc",    SOKUHO, 205.0, "RIZIN公式 超RIZIN.5 第6試合"),
    ("c3",  None, "bc",    SOKUHO,  70.0, "RIZIN公式 超RIZIN.5 第6試合"),
    ("c4",  None, "bc",    SOKUHO, 362.0, "RIZIN公式 超RIZIN.5 第6試合"),   # ラウンド間のリング全景
    ("c5",  None, "cover", FACE,    12.0, "RIZIN公式"),
    ("x1",  None, "bc",    SOKUHO,  40.0, "RIZIN公式 超RIZIN.5 第6試合"),
    ("x2",  None, "bc",    SOKUHO, 250.0, "RIZIN公式 超RIZIN.5 第6試合"),
    ("x3",  None, "cover", HL6,     12.0, "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("c7",  None, "bc",    SOKUHO, 300.0, "RIZIN公式 超RIZIN.5 第6試合"),
    ("e1",  None, "bc",    SOKUHO, 170.0, "RIZIN公式 超RIZIN.5 第6試合"),
    ("e2",  None, "cover", HL6,     20.0, "RIZIN公式 超RIZIN.5 試合ハイライト"),
]
TRANS = ["dissolve", "fade", "dissolve", "smoothleft", "dissolve", "fade", "dissolve",
         "circleopen", "dissolve", "fade", "dissolve", "smoothright", "dissolve"]


def run(cmd):
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit("ffmpeg failed: " + " ".join(str(c) for c in cmd[:12]))


def durations():
    """ナレのビート境界から各セグメントの尺を出す。境界＝次ビートの開始時刻。"""
    tj = json.loads((ROOT / "subtitles" / "out" / EP / "timings.json").read_text(encoding="utf-8"))
    total = tj["total"]
    starts = {b["id"]: b["start"] for b in tj["beats"]}
    order = [b["id"] for b in tj["beats"]]
    span = {}
    for i, bid in enumerate(order):
        span[bid] = (starts[bid], starts[order[i + 1]] if i + 1 < len(order) else total)
    out = []
    for bid, frac, *_ in PLAN:
        s, e = span[bid]
        out.append((e - s) * (frac if frac else 1.0))
    # 端数を最後のセグメントで吸収し、合計をナレ尺に一致させる
    out[-1] += total - sum(out)
    return out, total


def build_seg(kind, src, ss, dur, out):
    if kind == "still":
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", f"{dur:.3f}", "-i", str(src),
             "-vf", "scale=1080:1920,setsar=1,format=yuv420p", "-t", f"{dur:.3f}", *ENC, str(out)])
    elif kind == "bc":
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ss}", "-i", str(src),
             "-filter_complex", "[0:v]" + DEBAND + "," + BC, "-t", f"{dur:.3f}", *ENC, str(out)])
    elif kind == "cover":
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ss}", "-i", str(src),
             "-vf", COVER, "-t", f"{dur:.3f}", *ENC, str(out)])
    else:
        raise SystemExit("unknown kind " + kind)


def main():
    durs, total = durations()
    n = len(PLAN)
    segs = []
    for i, ((bid, _f, kind, src, ss, lab), base) in enumerate(zip(PLAN, durs)):
        dur = base + (D if i < n - 1 else 0.0)
        out = WORK / f"s{i:02d}.mp4"
        print(f"[{i:2d}] {bid:4} {base:5.2f}s {kind:5} {Path(src).name} @{ss}", flush=True)
        build_seg(kind, src, ss, dur, out)
        segs.append(out)

    offsets, acc = [], 0.0
    for k in range(n - 1):
        acc += durs[k]; offsets.append(round(acc, 3))

    inputs = []
    for s in segs:
        inputs += ["-i", str(s)]
    norm = "".join(f"[{i}:v]fps=30,setsar=1,format=yuv420p[s{i}];" for i in range(n))
    parts, prev = [], "[s0]"
    for k in range(1, n):
        o = "[v]" if k == n - 1 else f"[x{k}]"
        parts.append(f"{prev}[s{k}]xfade=transition={TRANS[k-1]}:duration={D}:offset={offsets[k-1]}{o}")
        prev = o
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", norm + ";".join(parts),
         "-map", "[v]", *ENC, str(OUT)])
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nk=1:nw=1", str(OUT)], capture_output=True, text=True).stdout.strip()
    # 出典ラベルの区間表をテンプレ側へ渡す
    segjson, acc = [], 0.0
    for (bid, _f, kind, src, ss, lab), base in zip(PLAN, durs):
        segjson.append({"t0": round(acc, 3), "t1": round(acc + base, 3), "beat": bid,
                        "src": Path(src).name, "ss": ss, "label": lab})
        acc += base
    (TPL / "assets" / "bg_segments.json").write_text(
        json.dumps(segjson, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"DONE {OUT} dur={d}s (target {total})")


if __name__ == "__main__":
    main()
