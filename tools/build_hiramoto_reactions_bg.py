# -*- coding: utf-8 -*-
"""④ 平本蓮×ダウトベック 判定への反応集 ビート別背景クリップ生成（横1920x1080）。

素材はすべてRIZIN公式。放送映像は上部の配信帯と右端のPPV広告を crop で除去する。
縦型ハイライト(1080x1920)は blur-contain で16:9に収める。

出力: hyperframes/templates/hiramoto-reactions/assets/bgvid/<beatid>.mp4
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
EP = "hiramoto_reactions"
SRC = ROOT / "assets" / "source" / "episode_rizin5_reactions" / "clips"
SRC_HR = ROOT / "assets" / "source" / "episode_hiramoto_reactions" / "clips"
SRC_HD = ROOT / "assets" / "source" / "episode_hiramoto_dautbek" / "clips"
TPL = ROOT / "hyperframes" / "templates" / "hiramoto-reactions"
OUT = TPL / "assets" / "bgvid"
OUT.mkdir(parents=True, exist_ok=True)
TIM = json.loads((ROOT / "subtitles" / "out" / EP / "timings.json").read_text(encoding="utf-8"))
DUR = {b["id"]: round(b["end"] - b["start"], 2) for b in TIM["beats"]}

# ★メモリ逼迫でffmpegが落ちるのでスレッドとプリセットを絞る
ENC = ["-r", "30", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
       "-g", "30", "-keyint_min", "30", "-crf", "21", "-preset", "veryfast", "-threads", "2"]

# 素材（発言者を紹介する区間は必ずその本人の映像を使う）
F6 = SRC_HD / "sokuho_6.mp4"             # RIZIN公式【速報】第6試合 1R全編（放送画面）
H6 = SRC_HD / "hl6_IShJJtI2LhU.mp4"      # RIZIN公式 第6試合 縦型ハイライト
FACE = SRC_HD / "v_QxC20-pTRZ4.mp4"      # RIZIN公式 縦型 公開計量のフェイスオフ
CEO = SRC_HD / "ceo_sakakibara.mp4"      # RIZIN公式 榊原信行CEO 大会後会見
WL = SRC_HD / "winner_loser.mp4"         # RIZIN公式【勝者と敗者】(客席1215〜/控室1310〜/手当て1350〜)
IV6 = SRC / "iv6_full.mp4"               # RIZIN公式 試合後インタビュー(平本 20〜740 / ダウトベック 810〜1660)
ISHI = SRC / "an_ishiwatari.mp4"         # 石渡伸太郎（元修斗世界王者）
OGI = SRC / "an_ogikubo.mp4"             # 扇久保博正（RIZIN現役）
SUZU = SRC / "an_suzuki.mp4"             # 鈴木千裕（RIZIN現役）
MAEDA = SRC / "an_maeda.mp4"             # 前田日明（元RINGS代表・縦動画をピラーボックスした素材）
JOB1 = SRC / "an_jobin1.mp4"             # ジョビン（元DEEPフェザー級王者）
HIKA = SRC_HR / "hikakin_raw.mp4"        # ヒカキン（HikakinClipTV 同時視聴配信）
STRA = SRC_HR / "strasser_raw.mp4"       # ストラッサー起一（4:40:00起点）
STRB = SRC_HR / "strasser_b.mp4"         # ストラッサー起一（4:50:30起点／平本は悪くない、の区間）
KWA = SRC_HR / "kawajiri_a.mp4"          # 川尻達也（24:00起点／解説中の自分の採点）
KWB = SRC_HR / "kawajiri_b.mp4"          # 川尻達也（45:00起点／見返して考えが変わった）

# ★放送の配信帯(上部〜y114)と右端のPPV広告(x1672〜)を落とす
DEBAND = "crop=1672:966:0:114,setsar=1"
COVER = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,format=yuv420p"
CROPR = "crop=1090:720:0:0,setsar=1"
VPILL = "crop=406:720:437:0,setsar=1"
BC = ("split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
      "gblur=sigma=28,eq=brightness=-0.26[bg];[b]scale=-2:1080[fg];"
      "[bg][fg]overlay=(W-w)/2:0,setsar=1,format=yuv420p")

S_F6 = "RIZIN公式 超RIZIN.5 第6試合"
S_HL = "RIZIN公式 超RIZIN.5 試合ハイライト"
S_WE = "RIZIN公式 超RIZIN.5 公開計量"
S_CEO = "RIZIN公式 榊原信行CEO 大会後会見"
S_WL = "RIZIN公式【勝者と敗者】"
S_IV = "RIZIN公式 試合後インタビュー"
PLAN = [
    ("o1",  F6, 20.0,  "bcast", S_F6),
    ("o2",  H6, 1.0,   "vert",  S_HL),
    # 第1章 試合の中身と判定結果
    ("c1a", F6, 133.0, "bcast", S_F6),
    ("c1b", F6, 160.0, "bcast", S_F6),
    ("c1c", F6, 205.0, "bcast", S_F6),
    ("c1d", F6, 240.0, "bcast", S_F6),
    ("c1e", H6, 8.0,   "vert",  S_HL),
    ("c1f", F6, 300.0, "bcast", S_F6),
    ("c1g", F6, 340.0, "bcast", S_F6),
    # 第2章 判定に反対・驚いた人たち
    ("c2a", FACE, 2.0, "vert",  S_WE),
    ("c2b", HIKA, 155.0, "plain", "HikakinClipTV（超RIZIN.5 同時視聴配信）"),
    ("c2c", JOB1, 60.0,  "plain", "ジョビン切り抜きチャンネル"),
    ("c2d", JOB1, 200.0, "plain", "ジョビン切り抜きチャンネル"),
    ("c2e", WL, 1222.0,  "plain", S_WL),
    ("c2f", STRA, 210.0, "plain", "ストラッサー起一 [ストチャンネル]"),
    ("c2g", STRA, 255.0, "plain", "ストラッサー起一 [ストチャンネル]"),
    ("c2h", STRB, 80.0,  "plain", "ストラッサー起一 [ストチャンネル]"),
    ("c2i", MAEDA, 160.0,"vpill", "前田日明チャンネル"),
    # 第3章 判定を説明する／反論していない人たち
    ("c3a", F6, 60.0,  "bcast", S_F6),
    ("c3b", CEO, 545.0, "plain", S_CEO),
    ("c3c", CEO, 596.0, "plain", S_CEO),
    ("c3d", CEO, 640.0, "plain", S_CEO),
    ("c3e", WL, 1352.0, "plain", S_WL),
    ("c3f", IV6, 40.0,  "plain", S_IV),
    ("c3g", IV6, 150.0, "plain", S_IV),
    ("c3h", WL, 1314.0, "plain", S_WL),
    ("c3i", WL, 1333.0, "plain", S_WL),
    ("c3j", SUZU, 140.0, "plain", "鈴木千裕 Chihiro Suzuki"),
    ("c3k", SUZU, 175.0, "plain", "鈴木千裕 Chihiro Suzuki"),
    ("c3l", OGI, 400.0, "plain", "扇久保博正 おぎちゃんねる。"),
    ("c3m", OGI, 460.0, "plain", "扇久保博正 おぎちゃんねる。"),
    ("c3n", ISHI, 60.0,  "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c3o", ISHI, 160.0, "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c3p", ISHI, 260.0, "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c3q", KWA, 85.0,  "plain", "川尻達也のじりラジオ"),
    ("c3r", KWA, 120.0, "plain", "川尻達也のじりラジオ"),
    ("c3s", KWA, 160.0, "plain", "川尻達也のじりラジオ"),
    ("c3t", KWB, 20.0,  "plain", "川尻達也のじりラジオ"),
    ("c3u", KWB, 70.0,  "plain", "川尻達也のじりラジオ"),
    ("c3v", KWB, 120.0, "plain", "川尻達也のじりラジオ"),
    # まとめ
    ("e1",  F6, 370.0, "bcast", S_F6),
    ("e2",  H6, 14.0,  "vert",  S_HL),
    ("e3",  FACE, 12.0,"vert",  S_WE),
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
