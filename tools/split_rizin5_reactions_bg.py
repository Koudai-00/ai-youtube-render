# -*- coding: utf-8 -*-
"""連結した背景動画を、GitHubの100MB制限に収まるパートへ分割する。

各パートは次のパートの開始から TAIL 秒ぶん余分に持たせる。テンプレ側は
「次のパートを上のz-indexで重ねる」ので、piece終端まで背景が途切れない。
出力: assets/bgvid_full/bg_part{N}.mp4 と parts.json
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "hyperframes" / "templates" / "rizin5-reactions"
FULL = TPL / "assets" / "bgvid_full" / "rizin5_reactions_bg_full.mp4"
OUTD = FULL.parent
NPART = 6
TAIL = 8.0                       # 次パート開始から余分に持つ尺（piece終端まで埋めるため）
ENC = ["-r", "30", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
       "-g", "30", "-keyint_min", "30", "-crf", "22", "-preset", "veryfast"]


def main() -> int:
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", str(FULL)], capture_output=True,
                               text=True).stdout.strip())
    step = dur / NPART
    parts = []
    for k in range(NPART):
        t0 = round(k * step, 3)
        t1 = round(min(dur, (k + 1) * step + (TAIL if k < NPART - 1 else 0.0)), 3)
        out = OUTD / f"bg_part{k}.mp4"
        if not (out.exists() and out.stat().st_size > 20000):
            # ★-ss を -i の後に置いて正確に切る（前に置くとキーフレームに丸められてズレる）
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(FULL),
                            "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-threads", "2",
                            *ENC, str(out)], check=True)
        mb = out.stat().st_size / 1024 / 1024
        parts.append({"file": out.name, "t0": t0, "t1": round(min(dur, (k + 1) * step), 3),
                      "media_len": round(t1 - t0, 3)})
        print(f"  part{k}  {t0:7.2f}〜{t1:7.2f}s  {mb:6.1f}MB", flush=True)
        if mb > 95:
            print(f"  ★ part{k} が95MBを超えています。NPART を増やしてください")
    (OUTD / "parts.json").write_text(json.dumps(parts, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
    print(f"{NPART}分割しました → {OUTD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
