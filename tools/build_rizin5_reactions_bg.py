# -*- coding: utf-8 -*-
"""超RIZIN.5 反応まとめ ビート別背景クリップ生成（横1920x1080）。

素材はすべてRIZIN公式。放送映像は上部の配信帯と右端のPPV広告を crop で除去する。
縦型ハイライト(1080x1920)は blur-contain で16:9に収める。

出力: hyperframes/templates/rizin5-reactions/assets/bgvid/<beatid>.mp4
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
EP = "rizin5_reactions"
SRC = ROOT / "assets" / "source" / "episode_rizin5_reactions" / "clips"
TPL = ROOT / "hyperframes" / "templates" / "rizin5-reactions"
OUT = TPL / "assets" / "bgvid"
OUT.mkdir(parents=True, exist_ok=True)
TIM = json.loads((ROOT / "subtitles" / "out" / EP / "timings.json").read_text(encoding="utf-8"))
DUR = {b["id"]: round(b["end"] - b["start"], 2) for b in TIM["beats"]}

ENC = ["-r", "30", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
       "-g", "30", "-keyint_min", "30", "-crf", "20"]

# 素材
F6 = SRC / "sokuho_6.mp4"              # 第6試合 1R全編（RIZIN公式速報）
F8 = SRC / "main_f8.mp4"               # 第8試合 1R全編（RIZIN公式速報）
IV = SRC / "iv_asakura_aoki.mp4"       # 朝倉未来vs青木真也 試合後インタビュー（RIZIN公式）
IV6 = SRC / "iv_hiramoto_dautbek.mp4"  # 平本蓮vsダウトベック 試合後インタビュー（RIZIN公式）
H6 = SRC / "hl6_IShJJtI2LhU.mp4"       # 第6試合 縦型ハイライト
H7 = SRC / "hl_qXZY9nrWMjY.mp4"        # 第7試合 縦型ハイライト
H8 = SRC / "hl_1gCgKoJD9Xg.mp4"        # 第8試合 縦型ハイライト

# ★放送の配信帯(上部〜y114)と右端のPPV広告(x1672〜)を落とす
DEBAND = "crop=1672:966:0:114,setsar=1"
COVER = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,format=yuv420p"
# 縦素材→16:9はぼかし背景に原比率で載せる
BC = ("split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
      "gblur=sigma=28,eq=brightness=-0.26[bg];[b]scale=-2:1080[fg];"
      "[bg][fg]overlay=(W-w)/2:0,setsar=1,format=yuv420p")

# (beat_id, 素材, 開始秒, 種別, 出典ラベル)
#   bcast=放送映像(バナー除去→cover) / plain=そのままcover / vert=縦→blur-contain
PLAN = [
    # ===== オープニング =====
    ("o1",  H7, 1.0,  "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("o2",  H8, 2.0,  "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("o3",  H6, 2.0,  "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    # ===== 第1章 平本蓮 vs ダウトベック =====
    ("c1a", F6, 20.0,  "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1b", F6, 45.0,  "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("ko1", H6, 0.5,   "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("c1c", F6, 75.0,  "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1d", F6, 133.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),   # 左が当たる区間
    ("c1e", F6, 200.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1f", F6, 230.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1g", F6, 95.0,  "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1h", F6, 150.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1i", F6, 250.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1j", F6, 275.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1k", F6, 60.0,  "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1l", F6, 175.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1m", IV6, 15.0,  "plain", "RIZIN公式 試合後インタビュー"),
    ("c1n", IV6, 40.0,  "plain", "RIZIN公式 試合後インタビュー"),   # 平本本人が語る
    ("c1o", IV6, 90.0,  "plain", "RIZIN公式 試合後インタビュー"),
    ("c1p", IV6, 140.0, "plain", "RIZIN公式 試合後インタビュー"),
    ("c1q", F6, 340.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1r", IV6, 300.0, "plain", "RIZIN公式 試合後インタビュー"),
    ("c1s", IV6, 330.0, "plain", "RIZIN公式 試合後インタビュー"),
    ("c1t", H6, 8.0,   "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("c1u", IV6, 360.0, "plain", "RIZIN公式 試合後インタビュー"),
    # ===== 第2章 朝倉未来 vs 青木真也 =====
    ("c2a", H7, 6.0,   "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("c2b", H7, 11.0,  "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("ko2", H7, 0.5,   "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("c2c", IV, 300.0, "plain", "RIZIN公式 試合後インタビュー"),
    ("c2d", IV, 330.0, "plain", "RIZIN公式 試合後インタビュー"),
    ("c2e", H7, 3.0,   "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("c2f", IV, 120.0, "plain", "RIZIN公式 試合後インタビュー"),
    ("c2g", IV, 20.0,  "plain", "RIZIN公式 試合後インタビュー"),
    ("c2h", IV, 60.0,  "plain", "RIZIN公式 試合後インタビュー"),
    ("c2i", IV, 200.0, "plain", "RIZIN公式 試合後インタビュー"),
    # ===== 第3章 シェイドゥラエフ vs マッキー =====
    ("c3a", F8, 15.0,  "bcast", "RIZIN公式 超RIZIN.5 第8試合"),
    ("c3b", H8, 1.0,   "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("ko3", H8, 8.0,   "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("c3c", F8, 60.0,  "bcast", "RIZIN公式 超RIZIN.5 第8試合"),
    ("c3d", F8, 200.0, "bcast", "RIZIN公式 超RIZIN.5 第8試合"),
    ("c3e", F8, 280.0, "bcast", "RIZIN公式 超RIZIN.5 第8試合"),
    # ===== まとめ =====
    ("e1",  H8, 14.0,  "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("e2",  F8, 330.0, "bcast", "RIZIN公式 超RIZIN.5 第8試合"),
    ("e3",  IV, 250.0, "plain", "RIZIN公式 試合後インタビュー"),
]


def run(cmd):
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit("ffmpeg failed: " + " ".join(str(c) for c in cmd[:12]))


def main() -> int:
    ids = {b["id"] for b in TIM["beats"]}
    planned = {p[0] for p in PLAN}
    if ids - planned:
        raise SystemExit(f"PLANに無いビート: {sorted(ids - planned)}")

    segs = []
    for bid, src, ss, kind, label in PLAN:
        # ★窓分割レンダーでpiece途中に尺切れが起きないよう、尾を+13秒確保する
        need = DUR[bid] + 13.0
        out = OUT / f"{bid}.mp4"
        # 短い素材(縦ハイライト等)は必要尺に足りないのでループさせる
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1",
               "-ss", f"{ss}", "-i", str(src)]
        if kind == "bcast":
            cmd += ["-vf", DEBAND + "," + COVER]
        elif kind == "vert":
            cmd += ["-filter_complex", "[0:v]" + BC]
        else:
            cmd += ["-vf", COVER]
        cmd += ["-t", f"{need:.2f}", *ENC, str(out)]
        run(cmd)
        segs.append({"beat": bid, "src": Path(src).name, "ss": ss, "kind": kind, "label": label})
        print(f"  {bid:4} {DUR[bid]:6.2f}s +尾13s  {kind:5} {Path(src).name} @{ss}", flush=True)

    (TPL / "assets" / "bg_segments.json").write_text(
        json.dumps(segs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(segs)}本のビート背景を生成しました → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
