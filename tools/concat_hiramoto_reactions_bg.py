# -*- coding: utf-8 -*-
"""反応まとめ: ビート別の背景クリップを1本の背景動画へ xfade 連結する。

★なぜ連結するか（2026-09-11 に判明）
   ビート別に <video> を並べる方式は、ビート数が増えると Chrome の同時メディア要素の
   上限に当たり、フレームキャプチャが同じフレームで固まる（80ビートで再現。44ビートでは出ない）。
   ショート(hiramoto_dautbek_short)で実績のある「事前に1本へ結合して <video> は1個だけ」に揃える。

出力: hyperframes/templates/hiramoto-reactions/assets/bgvid_full/hiramoto_reactions_bg_full.mp4
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
EP = "hiramoto_reactions"
TPL = ROOT / "hyperframes" / "templates" / "hiramoto-reactions"
SRCDIR = TPL / "assets" / "bgvid"
OUTDIR = TPL / "assets" / "bgvid_full"
OUTDIR.mkdir(parents=True, exist_ok=True)
WORK = TPL / "assets" / "_catwork"
WORK.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / "hiramoto_reactions_bg_full.mp4"
TIM = json.loads((ROOT / "subtitles" / "out" / EP / "timings.json").read_text(encoding="utf-8"))
COMP = round(TIM["total"] + 0.3, 2)
D = 0.45                      # クロスフェード長（ショートと同じ）
ENC = ["-r", "30", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
       "-g", "30", "-keyint_min", "30", "-crf", "22", "-preset", "veryfast"]
TRANS = ["dissolve", "fade", "smoothleft", "dissolve", "fade", "smoothright"]


def run(cmd):
    if subprocess.run(cmd).returncode != 0:
        raise SystemExit("ffmpeg 失敗: " + " ".join(str(c) for c in cmd[:14]))


def main() -> int:
    beats = TIM["beats"]
    spans = []
    for i, b in enumerate(beats):
        t0 = b["start"]
        t1 = beats[i + 1]["start"] if i + 1 < len(beats) else COMP
        spans.append((b["id"], round(t0, 3), round(t1 - t0, 3)))

    segs = []
    n = len(spans)
    for i, (bid, t0, span) in enumerate(spans):
        src = SRCDIR / f"{bid}.mp4"
        if not src.exists():
            raise SystemExit(f"背景クリップがありません: {src}")
        need = span + (D if i < n - 1 else 0.0)
        out = WORK / f"s{i:02d}.mp4"
        if not (out.exists() and out.stat().st_size > 20000):
            run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", str(src),
                 "-t", f"{need:.3f}", *ENC, str(out)])
        segs.append(out)
        if (i + 1) % 20 == 0:
            print(f"  切り出し {i+1}/{n}", flush=True)

    offsets, acc = [], 0.0
    for k in range(n - 1):
        acc += spans[k][2]
        offsets.append(round(acc, 3))

    # ★一度に多くの入力を xfade するとメモリを食って落ちるので、5本ずつの再帰結合にする。
    #   各段の出力はファイルに残し、途中で落ちても作り直さずに再開できるようにする。
    FAN = 5

    def xfade_group(files, durs, tag):
        """files を xfade で1本にする。durs は各クリップの可視尺(最後の1本は不要)。"""
        outp = WORK / (tag + ".mp4")
        if outp.exists() and outp.stat().st_size > 20000:
            return outp
        inputs = []
        for f in files:
            inputs += ["-i", str(f)]
        m = len(files)
        norm = "".join("[%d:v]fps=30,setsar=1,format=yuv420p[s%d];" % (j, j) for j in range(m))
        parts, prev, acc2 = [], "[s0]", 0.0
        for k in range(1, m):
            acc2 += durs[k - 1]
            o = "[v]" if k == m - 1 else "[x%d]" % k
            parts.append("%s[s%d]xfade=transition=%s:duration=%s:offset=%s%s"
                         % (prev, k, TRANS[(k - 1) % len(TRANS)], D, round(acc2, 3), o))
            prev = o
        run(["ffmpeg", "-y", "-loglevel", "error", "-threads", "2",
             "-filter_complex_threads", "1", *inputs,
             "-filter_complex", norm + ";".join(parts), "-map", "[v]", *ENC, str(outp)])
        return outp

    def reduce_level(files, durs, level):
        """files を FAN 本ずつまとめて1段減らす。durs は各ファイルの可視尺。"""
        out_files, out_durs = [], []
        for gi, g0 in enumerate(range(0, len(files), FAN)):
            g = list(range(g0, min(g0 + FAN, len(files))))
            if len(g) == 1:
                out_files.append(files[g[0]]); out_durs.append(durs[g[0]]); continue
            gp = xfade_group([files[j] for j in g], [durs[j] for j in g[:-1]],
                             "L%d_%02d" % (level, gi))
            out_files.append(gp)
            out_durs.append(sum(durs[j] for j in g))
            print("  結合 L%d グループ%d (%d本)" % (level, gi + 1, len(g)), flush=True)
        return out_files, out_durs

    files = segs
    durs = [sp[2] for sp in spans]
    level = 1
    while len(files) > 1:
        files, durs = reduce_level(files, durs, level)
        print("  → L%d 完了 残り%d本" % (level, len(files)), flush=True)
        level += 1
    final = files[0]
    if final != OUT:
        OUT.unlink(missing_ok=True)
        final.replace(OUT)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(OUT)], capture_output=True, text=True).stdout.strip()
    print(f"DONE {OUT}  dur={d}s (目標 {COMP})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
