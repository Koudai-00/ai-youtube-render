#!/usr/bin/env bash
# visual.mp4(窓分割concat済) + ナレ + 単一BGM を合成し loudnorm I=-14。
# 中立まとめ=BGMは全編一定。BGMは動画尺にループ+両端フェード。映像は -map 0:v のみ使用。
set -euo pipefail
ROOT="$(pwd)"
TPL="$ROOT/hyperframes/templates/rizin54-yosou/assets"
V="$ROOT/visual.mp4"
NARR="$TPL/audio/narration.wav"
BGM="$TPL/audio/bgm.m4a"
OUT="$ROOT/final.mp4"

for f in "$V" "$NARR" "$BGM"; do
  [ -f "$f" ] || { echo "MISSING: $f" >&2; exit 1; }
done

VD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
FO=$(awk "BEGIN{print $VD-2.0}")

ffmpeg -y -i "$V" -i "$NARR" -stream_loop -1 -i "$BGM" \
  -filter_complex "\
[1:a]aresample=48000,apad,volume=1.0[na];\
[2:a]aresample=48000,volume=0.075,afade=t=in:st=0:d=1.2,afade=t=out:st=${FO}:d=2.0[bg];\
[na][bg]amix=inputs=2:duration=first:normalize=0[mx];\
[mx]loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -ar 48000 -ac 2 -shortest "$OUT"

echo "-> $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
