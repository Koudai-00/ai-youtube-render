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

# 素材（すべて出所を記録。関係者のコメントを紹介する区間は「その本人の映像」を使う）
F6 = SRC / "sokuho_6.mp4"              # RIZIN公式【速報】第6試合 1R全編
F7 = SRC / "main_f7.mp4"               # RIZIN公式【速報】第7試合
F8 = SRC / "main_f8.mp4"               # RIZIN公式【速報】第8試合 1R全編
H6 = SRC / "hl6_IShJJtI2LhU.mp4"       # RIZIN公式 第6試合 縦型ハイライト
H7 = SRC / "hl_qXZY9nrWMjY.mp4"        # RIZIN公式 第7試合 縦型ハイライト
H8 = SRC / "hl_1gCgKoJD9Xg.mp4"        # RIZIN公式 第8試合 縦型ハイライト
# ★試合後インタビュー(RIZIN公式・全編)。フレーム目視で話者の区間を確定済み:
#     IV6  平本蓮 20〜740 / カルシャガ・ダウトベック 810〜1660
#     IV7  青木真也 20〜700 / 朝倉未来 800〜1600
#     IV8  AJ・マッキー 20〜1500 / シェイドゥラエフ 1620〜2200
IV6 = SRC / "iv6_full.mp4"
IV7 = SRC / "iv7_full.mp4"
IV8 = SRC / "iv8_full.mp4"
# 関係者本人の映像
SRC2 = ROOT / "assets" / "source" / "episode_hiramoto_dautbek" / "clips"
CEO = SRC2 / "ceo_sakakibara.mp4"      # RIZIN公式 榊原信行CEO 大会後会見
WL = SRC2 / "winner_loser.mp4"         # RIZIN公式【勝者と敗者】試合直後の選手に密着
ISHI = SRC / "an_ishiwatari.mp4"       # 石渡伸太郎（元修斗世界王者）【超RIZIN.5】爆速感想
STRA = SRC / "an_strasser.mp4"         # ストラッサー起一（現役）超RIZIN.5 感想
HOSO = SRC / "an_hosokawa.mp4"         # 細川バレンタイン（元プロボクサー）超速報
OGI = SRC / "an_ogikubo.mp4"           # 扇久保博正（RIZIN現役）超RIZIN.5 の感想
JOB1 = SRC / "an_jobin1.mp4"           # ジョビン（元DEEPフェザー級王者）平本×ダウトベック判定
JOB3 = SRC / "an_jobin3.mp4"           # ジョビン シェイドゥラエフ×AJマッキー
KANE = SRC / "an_kanehara.mp4"         # 金原正徳（元修斗世界王者・RIZIN現役）超RIZIN5 浪速の超速報感想
MAEDA = SRC / "an_maeda.mp4"           # 前田日明（元RINGS代表）RIZIN総括（縦動画をピラーボックスした素材）
SUZU = SRC / "an_suzuki.mp4"           # 鈴木千裕（RIZIN現役）怪我の現状と超RIZIN5を見て感じたこと
AOKI = SRC / "an_aoki.mp4"             # 青木真也 本人チャンネル「超RIZIN5 応援ありがとうございました」

# ★放送の配信帯(上部〜y114)と右端のPPV広告(x1672〜)を落とす
DEBAND = "crop=1672:966:0:114,setsar=1"
COVER = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,format=yuv420p"
# 右下にスポンサーQRが焼き込まれている素材は、右端を落としてから使う
CROPR = "crop=1090:720:0:0,setsar=1"
# 縦動画が16:9にピラーボックスされている素材（前田日明ch）は、黒帯を外してから blur-contain する
VPILL = "crop=406:720:437:0,setsar=1"
# 縦素材→16:9はぼかし背景に原比率で載せる
BC = ("split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
      "gblur=sigma=28,eq=brightness=-0.26[bg];[b]scale=-2:1080[fg];"
      "[bg][fg]overlay=(W-w)/2:0,setsar=1,format=yuv420p")

# (beat_id, 素材, 開始秒, 種別, 出典ラベル)
#   bcast=放送映像(バナー除去→cover) / plain=そのままcover / vert=縦→blur-contain
PLAN = [
    # ===== オープニング =====
    ("o1",  F8, 15.0,  "bcast", "RIZIN公式 超RIZIN.5 第8試合"),
    ("o2",  H6, 2.0,   "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("o3",  H7, 9.0,   "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),

    # ===== 第1章 平本蓮 vs ダウトベック =====
    ("c1a", F6, 20.0,  "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1b", F6, 133.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),   # ダウトベックの左が当たる区間
    ("c1c", F6, 205.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1d", F6, 275.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("c1e", JOB1, 60.0,  "plain", "ジョビン切り抜きチャンネル"),
    ("c1f", JOB1, 220.0, "plain", "ジョビン切り抜きチャンネル"),
    ("c1g", ISHI, 60.0,  "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c1h", ISHI, 160.0, "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c1i", ISHI, 260.0, "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c1j", OGI, 400.0, "plain", "扇久保博正 おぎちゃんねる。"),
    ("c1k", OGI, 460.0, "plain", "扇久保博正 おぎちゃんねる。"),
    ("c1j2", KANE, 430.0, "plain", "金原正徳の金ちゃんTV"),
    ("c1j3", KANE, 470.0, "plain", "金原正徳の金ちゃんTV"),
    ("c1j4", KANE, 505.0, "plain", "金原正徳の金ちゃんTV"),
    ("c1j5", KANE, 545.0, "plain", "金原正徳の金ちゃんTV"),
    ("c1j6", SUZU, 140.0, "plain", "鈴木千裕 Chihiro Suzuki"),
    ("c1j7", SUZU, 175.0, "plain", "鈴木千裕 Chihiro Suzuki"),
    ("c1j8", MAEDA, 160.0, "vpill", "前田日明チャンネル"),
    ("c1j9", MAEDA, 195.0, "vpill", "前田日明チャンネル"),
    ("c1l", CEO, 545.0, "plain", "RIZIN公式 榊原信行CEO 大会後会見"),
    ("c1m", CEO, 596.0, "plain", "RIZIN公式 榊原信行CEO 大会後会見"),
    ("c1n", CEO, 640.0, "plain", "RIZIN公式 榊原信行CEO 大会後会見"),
    ("c1o", WL, 1344.0, "plain", "RIZIN公式【勝者と敗者】"),        # 控室に戻った平本
    ("c1p", IV6, 40.0,  "plain", "RIZIN公式 試合後インタビュー"),   # 平本本人
    ("c1q", IV6, 150.0, "plain", "RIZIN公式 試合後インタビュー"),
    ("c1r", IV6, 900.0, "plain", "RIZIN公式 試合後インタビュー"),   # ダウトベック本人
    ("c1s", IV6, 1020.0,"plain", "RIZIN公式 試合後インタビュー"),
    ("c1t", IV6, 1150.0,"plain", "RIZIN公式 試合後インタビュー"),

    # ===== 第2章 朝倉未来 vs 青木真也 =====
    ("c2a", F7, 1.0,   "plain", "ABEMA 格闘【公式】 超RIZIN.5 第7試合"),
    ("c2b", H7, 0.5,   "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("c2c", F7, 24.0,  "plain", "ABEMA 格闘【公式】 超RIZIN.5 第7試合"),
    ("c2d", WL, 1450.0, "plain", "RIZIN公式【勝者と敗者】"),   # 決着直後に控室へ戻る青木
    ("c2e", ISHI, 360.0, "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c2f", ISHI, 450.0, "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c2g", ISHI, 550.0, "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c2h", STRA, 30.0,  "plain", "ストラッサー起一 [ストチャンネル]"),
    ("c2i", STRA, 130.0, "plain", "ストラッサー起一 [ストチャンネル]"),
    ("c2j", STRA, 330.0, "plain", "ストラッサー起一 [ストチャンネル]"),
    ("c2k", HOSO, 20.0,  "cropr", "細川バレンタイン / 前向き教室"),
    ("c2l", HOSO, 120.0, "cropr", "細川バレンタイン / 前向き教室"),
    ("c2m", HOSO, 260.0, "cropr", "細川バレンタイン / 前向き教室"),
    ("c2n", OGI, 530.0, "plain", "扇久保博正 おぎちゃんねる。"),
    ("c2n2", KANE, 180.0, "plain", "金原正徳の金ちゃんTV"),
    ("c2n3", KANE, 215.0, "plain", "金原正徳の金ちゃんTV"),
    ("c2n4", KANE, 255.0, "plain", "金原正徳の金ちゃんTV"),
    ("c2n5", MAEDA, 20.0, "vpill", "前田日明チャンネル"),
    ("c2n6", MAEDA, 60.0, "vpill", "前田日明チャンネル"),
    ("c2o", WL, 1660.0, "plain", "RIZIN公式【勝者と敗者】"),   # 勝って花道を戻る朝倉
    ("c2p", IV7, 60.0,  "plain", "RIZIN公式 試合後インタビュー"),   # 青木真也本人
    ("c2q", IV7, 300.0, "plain", "RIZIN公式 試合後インタビュー"),

    ("c2r", AOKI, 30.0,  "plain", "青木真也 [SHINYA AOKI] チャンネル"),
    ("c2s", AOKI, 70.0,  "plain", "青木真也 [SHINYA AOKI] チャンネル"),
    ("c2t", AOKI, 115.0, "plain", "青木真也 [SHINYA AOKI] チャンネル"),
    ("c2u", AOKI, 265.0, "plain", "青木真也 [SHINYA AOKI] チャンネル"),
    ("c2v", AOKI, 490.0, "plain", "青木真也 [SHINYA AOKI] チャンネル"),
    ("c2w", AOKI, 660.0, "plain", "青木真也 [SHINYA AOKI] チャンネル"),

    # ===== 第3章 シェイドゥラエフ vs マッキー =====
    ("c3a", F8, 40.0,  "bcast", "RIZIN公式 超RIZIN.5 第8試合"),
    ("c3b", H8, 1.0,   "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("c3c", F8, 130.0, "bcast", "RIZIN公式 超RIZIN.5 第8試合"),
    ("c3d", ISHI, 100.0, "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c3e", ISHI, 210.0, "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c3f", ISHI, 300.0, "plain", "石渡伸太郎 Shintaro Ishiwatari"),
    ("c3g", JOB3, 60.0,  "plain", "ジョビン切り抜きチャンネル"),
    ("c3h", OGI, 700.0, "plain", "扇久保博正 おぎちゃんねる。"),
    ("c3h2", KANE, 20.0,  "plain", "金原正徳の金ちゃんTV"),
    ("c3h3", KANE, 60.0,  "plain", "金原正徳の金ちゃんTV"),
    ("c3h4", KANE, 100.0, "plain", "金原正徳の金ちゃんTV"),
    ("c3h5", SUZU, 85.0,  "plain", "鈴木千裕 Chihiro Suzuki"),
    ("c3h6", MAEDA, 230.0,"vpill", "前田日明チャンネル"),
    ("c3i", IV8, 100.0, "plain", "RIZIN公式 試合後インタビュー"),   # AJ・マッキー本人
    ("c3j", IV8, 430.0, "plain", "RIZIN公式 試合後インタビュー"),
    ("c3k", IV8, 1700.0,"plain", "RIZIN公式 試合後インタビュー"),   # シェイドゥラエフ本人
    ("c3l", IV8, 1850.0,"plain", "RIZIN公式 試合後インタビュー"),
    ("c3m", IV8, 2010.0,"plain", "RIZIN公式 試合後インタビュー"),

    # ===== まとめ =====
    ("e1",  H8, 14.0,  "vert",  "RIZIN公式 超RIZIN.5 試合ハイライト"),
    ("e2",  F6, 330.0, "bcast", "RIZIN公式 超RIZIN.5 第6試合"),
    ("e3",  F8, 330.0, "bcast", "RIZIN公式 超RIZIN.5 第8試合"),
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
