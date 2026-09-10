# -*- coding: utf-8 -*-
"""超RIZIN.5 海外反応まとめ ビート別背景クリップ生成（横1920x1080）。

素材はすべてRIZIN公式。放送映像は上部の配信帯と右端のPPV広告を crop で除去する。
縦型ハイライト(1080x1920)は blur-contain で16:9に収める。

出力: hyperframes/templates/rizin5-overseas/assets/bgvid/<beatid>.mp4
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
EP = "rizin5_overseas"
SRC = ROOT / "assets" / "source" / "episode_rizin5_reactions" / "clips"
SRC_OV = ROOT / "assets" / "source" / "episode_rizin5_overseas" / "clips"
SRC_HD = ROOT / "assets" / "source" / "episode_hiramoto_dautbek" / "clips"
TPL = ROOT / "hyperframes" / "templates" / "rizin5-overseas"
OUT = TPL / "assets" / "bgvid"
OUT.mkdir(parents=True, exist_ok=True)
TIM = json.loads((ROOT / "subtitles" / "out" / EP / "timings.json").read_text(encoding="utf-8"))
DUR = {b["id"]: round(b["end"] - b["start"], 2) for b in TIM["beats"]}

# ★メモリ逼迫でffmpegが落ちるのでスレッドとプリセットを絞る
ENC = ["-r", "30", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
       "-g", "30", "-keyint_min", "30", "-crf", "21", "-preset", "veryfast", "-threads", "2"]

# 素材（すべてRIZIN公式。話者区間はフレーム目視で確定済み）
F8 = SRC / "main_f8.mp4"                 # 【速報】第8試合 1R全編（放送画面 1920x1080）
H8 = SRC / "hl_1gCgKoJD9Xg.mp4"          # 第8試合 縦型ハイライト
IV8 = SRC / "iv8_full.mp4"               # 試合後インタビュー: AJ・マッキー 20〜1500 / シェイドゥラエフ 1620〜2200
ARR = SRC_OV / "arrival.mp4"             # 【超RIZIN.5】選手会場入り
WL = SRC_HD / "winner_loser.mp4"         # 【勝者と敗者】第8試合の直後は 2050〜2300（2冠のベルトを持つシェイ）

# ★放送の配信帯(上部〜y114)と右端のPPV広告(x1672〜)を落とす
DEBAND = "crop=1672:966:0:114,setsar=1"
COVER = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,format=yuv420p"
CROPR = "crop=1090:720:0:0,setsar=1"
VPILL = "crop=406:720:437:0,setsar=1"
BC = ("split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
      "gblur=sigma=28,eq=brightness=-0.26[bg];[b]scale=-2:1080[fg];"
      "[bg][fg]overlay=(W-w)/2:0,setsar=1,format=yuv420p")

# (beat_id, 素材, 開始秒, 種別, 出典ラベル)
S_RZ = "RIZIN公式 超RIZIN.5 第8試合"
S_HL = "RIZIN公式 超RIZIN.5 試合ハイライト"
S_IV = "RIZIN公式 試合後インタビュー"
S_AR = "RIZIN公式 超RIZIN.5 選手会場入り"
S_WL = "RIZIN公式【勝者と敗者】"
PLAN = [
    ("o1",  F8, 15.0,  "bcast", S_RZ),
    ("o2",  H8, 1.0,   "vert",  S_HL),
    ("o3",  ARR, 30.0, "plain", S_AR),
    # 第1章 海外メディアの速報
    ("c1a", IV8, 1640.0, "plain", S_IV),
    ("c1b", F8, 45.0,  "bcast", S_RZ),
    ("c1c", F8, 70.0,  "bcast", S_RZ),
    ("c1d", F8, 95.0,  "bcast", S_RZ),
    ("c1e", F8, 120.0, "bcast", S_RZ),
    ("c1f", IV8, 1690.0, "plain", S_IV),
    ("c1g", ARR, 120.0, "plain", S_AR),
    ("c1h", H8, 12.0,  "vert",  S_HL),
    # 第2章 試合内容への評価
    ("c2a", F8, 150.0, "bcast", S_RZ),
    ("c2b", F8, 170.0, "bcast", S_RZ),
    ("c2c", F8, 190.0, "bcast", S_RZ),
    ("c2d", F8, 215.0, "bcast", S_RZ),
    ("c2e", F8, 235.0, "bcast", S_RZ),
    ("c2f", IV8, 190.0, "plain", S_IV),
    ("c2g", F8, 260.0, "bcast", S_RZ),
    ("c2h", F8, 282.0, "bcast", S_RZ),
    ("c2i", IV8, 120.0, "plain", S_IV),
    ("c2j", IV8, 430.0, "plain", S_IV),
    ("c2k", IV8, 460.0, "plain", S_IV),
    ("c2l", IV8, 490.0, "plain", S_IV),
    ("c2m", F8, 305.0, "bcast", S_RZ),
    ("c2n", F8, 325.0, "bcast", S_RZ),
    # 第3章 契約とUFC論
    ("c3a", WL, 2120.0, "plain", S_WL),
    ("c3b", IV8, 1730.0, "plain", S_IV),
    ("c3c", F8, 350.0, "bcast", S_RZ),
    ("c3d", IV8, 1790.0, "plain", S_IV),
    ("c3e", ARR, 250.0, "plain", S_AR),
    ("c3f", IV8, 1840.0, "plain", S_IV),
    ("c3g", F8, 370.0, "bcast", S_RZ),
    ("c3h", ARR, 350.0, "plain", S_AR),
    ("c3i", IV8, 1880.0, "plain", S_IV),
    # まとめ
    ("e1",  IV8, 1920.0, "plain", S_IV),
    ("e2",  IV8, 1975.0, "plain", S_IV),
    ("e3",  WL, 2190.0, "plain", S_WL),
    ("e4",  WL, 2260.0, "plain", S_WL),
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

    sigf = TPL / "assets" / "_assign.json"
    old = json.loads(sigf.read_text(encoding="utf-8")) if sigf.exists() else {}
    new = {b: f"{Path(sr).name}|{s2}|{k}" for b, sr, s2, k, _ in PLAN}

    segs = []
    for bid, src, ss, kind, label in PLAN:
        # ★窓分割レンダーでpiece途中に尺切れが起きないよう、尾を+13秒確保する
        need = DUR[bid] + 13.0
        out = OUT / f"{bid}.mp4"
        if out.exists() and old.get(bid) == new[bid] and out.stat().st_size > 20000:
            segs.append({"beat": bid, "src": Path(src).name, "ss": ss, "kind": kind, "label": label})
            continue
        # 短い素材(縦ハイライト等)は必要尺に足りないのでループさせる
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1",
               "-ss", f"{ss}", "-i", str(src)]
        if kind == "bcast":
            cmd += ["-vf", DEBAND + "," + COVER]
        elif kind == "cropr":
            cmd += ["-vf", CROPR + "," + COVER]
        elif kind == "vpill":
            cmd += ["-filter_complex", "[0:v]" + VPILL + "," + BC]
        elif kind == "vert":
            cmd += ["-filter_complex", "[0:v]" + BC]
        else:
            cmd += ["-vf", COVER]
        cmd += ["-t", f"{need:.2f}", *ENC, str(out)]
        run(cmd)
        # ★生成直後にデコード検査する（途中で落ちた書きかけを「完成」と誤判定しないため）
        chk = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", str(out)], capture_output=True, text=True)
        if chk.returncode != 0 or not chk.stdout.strip():
            out.unlink(missing_ok=True)
            raise SystemExit(f"{bid}.mp4 が壊れています（生成失敗）")
        segs.append({"beat": bid, "src": Path(src).name, "ss": ss, "kind": kind, "label": label})
        old[bid] = new[bid]
        sigf.write_text(json.dumps(old, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {bid:4} {DUR[bid]:6.2f}s +尾13s  {kind:5} {Path(src).name} @{ss}", flush=True)

    (TPL / "assets" / "bg_segments.json").write_text(
        json.dumps(segs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(segs)}本のビート背景を生成しました → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
