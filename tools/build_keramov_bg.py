# -*- coding: utf-8 -*-
"""ケラモフ減量×チャーリー柏木 ショート: 背景セグメントを作り xfade で1本に連結。
   ・尺は subtitles/out/keramov_charlie_short/timings.json のビート境界から自動算出(ナレと完全同期)。
   ・冒頭 t0 はユーザー支給サムネイルを「完全静止」で表示(KenBurns禁止・加工しない)。
   ・16:9素材は blur-contain。放送バナー(左上の大会名帯/右上のRIZIN LIVEロゴ)は crop で除去する。
   ・トランジションはディゾルブ基調、同じものを連続させない。"""
from __future__ import annotations
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = "keramov_charlie_short"
TPL = ROOT / "hyperframes" / "templates" / "keramov-charlie-short"
BGV = TPL / "assets" / "bgvid"
SRC = ROOT / "assets" / "source" / "episode_keramov_charlie"
CLIP = SRC / "clips"
PX = SRC / "pexels"
THUMB = ROOT / "assets" / "thumbnails" / "柏木サムネイル.png"
WORK = TPL / "assets" / "_bgwork"
for d in (BGV, WORK):
    d.mkdir(parents=True, exist_ok=True)
OUT = BGV / "keramov_bg_full.mp4"

FPS = 30
D = 0.45
ENC = ["-r", "30", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-g", "30", "-keyint_min", "30", "-crf", "20"]
# ★放送バナー(左上の大会名帯・右上のRIZIN LIVEロゴ)は上端120pxに収まるので落とす
DEBAND = "crop=1920:958:0:122,setsar=1"
BC = ("split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
      "gblur=sigma=26,eq=brightness=-0.30[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p")
COVER = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p"

ORIG = CLIP / "orig_1010.mp4"        # RIZIN公式「テッペンまで生テレビ」QA-Vx9hHoZM の 09:50 起点
WEIGH = CLIP / "weighin_keramov.mp4"  # RIZIN公式「超RIZIN.5 公開計量」_clmmq_jst4 の 28:30 起点
VSHADOW = CLIP / "vert_L6qCoMGgLc0.mp4"   # RIZIN公式 縦 #ヴガールケラモフ 写真撮影
VMIC = CLIP / "vert_T2gRsGmJ-ZE.mp4"      # RIZIN公式 縦 ヴガールケラモフ🆚高木凌
PX_SCALE = PX / "weight_scale_1_7801722.mp4"
PX_SWEAT = PX / "steam_room_hot_1_9145755.mp4"

# (beat_id, 分割位置, kind, source, 素材内の開始秒, 出典ラベル)
# ★c9 はナレが7秒あるので「1素材4秒以内」に収まるよう2分割する
PLAN = [
    ("t0",  None, "still", THUMB,    0.0,  ""),
    ("h1",  None, "bc",    ORIG,    100.0, "RIZIN公式 テッペンまで生テレビ"),
    ("h2",  None, "cover", VMIC,      2.0, "RIZIN公式"),
    ("c1",  None, "cover", PX_SCALE,  2.0, "Pexels"),
    ("c2",  None, "bc",    WEIGH,    36.0, "RIZIN公式 超RIZIN.5 公開計量"),
    ("c3",  None, "bc",    WEIGH,    57.0, "RIZIN公式 超RIZIN.5 公開計量"),
    ("c4",  None, "bc",    ORIG,    118.0, "RIZIN公式 テッペンまで生テレビ"),
    ("c5",  None, "bc",    ORIG,    240.0, "RIZIN公式 テッペンまで生テレビ"),
    ("c6",  None, "bc",    WEIGH,    65.0, "RIZIN公式 超RIZIN.5 公開計量"),
    ("c7",  None, "cover", PX_SWEAT, 23.0, "Pexels"),
    ("c9",  0.5,  "bc",    ORIG,    200.0, "RIZIN公式 テッペンまで生テレビ"),
    ("c9",  0.5,  "bc",    ORIG,    220.0, "RIZIN公式 テッペンまで生テレビ"),
    ("c10", None, "bc",    ORIG,    260.0, "RIZIN公式 テッペンまで生テレビ"),
    ("c11", None, "bc",    ORIG,    290.0, "RIZIN公式 テッペンまで生テレビ"),
    ("c12", None, "cover", VSHADOW,   8.0, "RIZIN公式"),
    ("e1",  None, "bc",    WEIGH,    43.0, "RIZIN公式 超RIZIN.5 公開計量"),
    ("e2",  None, "bc",    WEIGH,   103.0, "RIZIN公式 超RIZIN.5 公開計量"),
    ("e3",  None, "bc",    ORIG,    300.0, "RIZIN公式 テッペンまで生テレビ"),
    ("e4",  None, "bc",    WEIGH,    92.0, "RIZIN公式 超RIZIN.5 公開計量"),
]
TRANS = ["dissolve", "fade", "dissolve", "smoothleft", "dissolve", "fade", "dissolve",
         "circleopen", "dissolve", "fade", "dissolve", "smoothright", "dissolve",
         "fade", "dissolve", "smoothleft", "dissolve", "fade"]


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
