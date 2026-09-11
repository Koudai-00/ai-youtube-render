# -*- coding: utf-8 -*-
"""④ 判定への反応集: 冒頭のリアクション・モンタージュを作る（ナレなし・実音声）。

ユーザー指定の4本を指定区間で連結する。Xの切り抜きは画質が落ちるので、
すべて元動画から切り出す（Xとの一致はフレーム/視聴者数/文字起こしで照合済み）。
出典は画面左下に小さく焼き込む。
"""
from __future__ import annotations
import subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "source" / "episode_hiramoto_reactions" / "clips"
HD = ROOT / "assets" / "source" / "episode_hiramoto_dautbek" / "clips"
RX = ROOT / "assets" / "source" / "episode_rizin5_reactions" / "clips"
WORK = SRC.parent / "_openwork"
WORK.mkdir(parents=True, exist_ok=True)
OUT = SRC / "open_montage.mp4"
FONT = (ROOT / "hyperframes" / "templates" / "rizin5-reactions" / "assets" / "fonts"
        / "SourceHanSansJP-Medium.otf").as_posix().replace(":", "\:")

# (素材, 開始秒, 尺, 出典ラベル)
#   ★Xの切り抜きと元動画の対応は次で照合した:
#     ヒカキン=画面右上の視聴者数と表情でフレーム一致(X7s=元142s)
#     勝者と敗者=客席カットのフレーム一致(X5s=元1215s)
#     ストラッサー=自動字幕の文言一致(X30.8s『はい29と28』=元144s → オフセット113.2秒)
CLIPS = [
    (SRC / "hikakin_raw.mp4", 142.0, 8.0, "出典: HikakinClipTV（超RIZIN.5 同時視聴配信）"),
    (RX / "an_jobin1.mp4", 469.0, 8.0, "出典: ジョビン切り抜きチャンネル"),
    (HD / "winner_loser.mp4", 1215.0, 4.4, "出典: RIZIN公式【勝者と敗者】試合直後の選手に密着"),
    (SRC / "strasser_raw.mp4", 145.3, 52.0, "出典: ストラッサー起一 [ストチャンネル] 全試合生解説"),
]
COVER = ("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
         "setsar=1,format=yuv420p")
ENC = ["-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-g", "30", "-keyint_min", "30",
       "-crf", "20", "-preset", "veryfast", "-threads", "2",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def run(cmd):
    if subprocess.run(cmd).returncode != 0:
        raise SystemExit("ffmpeg 失敗: " + " ".join(str(c) for c in cmd[:12]))


def main() -> int:
    parts = []
    for i, (src, ss, dur, label) in enumerate(CLIPS):
        if not src.exists():
            raise SystemExit(f"素材がありません: {src}")
        out = WORK / f"o{i}.mp4"
        lab = label.replace(":", "\:").replace("'", "")
        vf = (COVER + f",drawtext=fontfile='{FONT}':text='{lab}':x=28:y=h-52:"
              "fontsize=26:fontcolor=white@0.92:box=1:boxcolor=black@0.45:boxborderw=10")
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ss}", "-i", str(src),
             "-t", f"{dur:.3f}", "-vf", vf,
             "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000", *ENC, str(out)])
        parts.append(out)
        print(f"  [{i}] {src.name} @{ss} {dur}s  {label}", flush=True)

    lst = WORK / "concat.txt"
    lst.write_text("\n".join(f"file '{p.as_posix()}'" for p in parts), encoding="utf-8")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(OUT)])
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(OUT)], capture_output=True, text=True).stdout.strip()
    print(f"DONE {OUT}  dur={d}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
