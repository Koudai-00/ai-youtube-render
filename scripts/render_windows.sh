#!/usr/bin/env bash
# 窓分割レンダー(CI版・ローカルrender_*_segments.shの移植)。
# 各窓を~6sピースに分割→chrome-headless-shell(beginFrame)でrender→concatフィルタ結合→正確span尺にtrim→全窓concat。
# 長尺単一レンダーの protocolTimeout ハングを、小片の連続で回避する。
set -u
ROOT="$(pwd)"
TPL="$ROOT/hyperframes/templates/rizin54-yosou"
OUTDIR="$ROOT/_segs"
BUILD="$ROOT/tools/build_rizin54_yosou_template.py"
WINS_PY="$ROOT/tools/rizin54_yosou_windows.py"
mkdir -p "$OUTDIR"
export PRODUCER_PUPPETEER_PROTOCOL_TIMEOUT_MS="${PRODUCER_PUPPETEER_PROTOCOL_TIMEOUT_MS:-600000}"
# HYPERFRAMES_BROWSER_PATH は workflow が chrome-headless-shell を指す

render_piece() {
  local hs="$1" he="$2" hp="$3" tag="$4" a hd span mm
  span=$(python3 -c "print($he-$hs)")
  if [ -f "$hp" ]; then
    hd=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$hp" 2>/dev/null)
    if [ -n "$hd" ] && python3 -c "exit(0 if abs($hd-$span)<1.0 and $hd>0.5 else 1)"; then return 0; fi
  fi
  local maxa=3
  python3 -c "exit(0 if $span<=7 else 1)" && maxa=5
  for a in $(seq 1 $maxa); do
    HF_WIN_START="$hs" HF_WIN_END="$he" python3 "$BUILD" >/dev/null 2>&1
    ( cd "$TPL" && timeout 240 xvfb-run -a hyperframes render -c index.html -o "$hp" --fps 30 -q standard --workers 1 >"$OUTDIR/$tag.log" 2>&1 )
    if [ -f "$hp" ]; then
      hd=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$hp" 2>/dev/null)
      [ -n "$hd" ] && return 0
      rm -f "$hp"
    fi
    echo "   piece $tag attempt$a fail ($hs-$he span=${span}s)"; tail -3 "$OUTDIR/$tag.log" 2>/dev/null
  done
  if python3 -c "exit(0 if $span>7 else 1)"; then
    mm=$(python3 -c "print(round(($hs+$he)/2,3))")
    echo "   -> split $tag ${hs}-${mm} / ${mm}-${he}"
    render_piece "$hs" "$mm" "${hp%.mp4}_1.mp4" "${tag}_1" || return 1
    render_piece "$mm" "$he" "${hp%.mp4}_2.mp4" "${tag}_2" || return 1
    ( cd "$OUTDIR" && ffmpeg -loglevel error -y -i "$(basename "${hp%.mp4}_1.mp4")" -i "$(basename "${hp%.mp4}_2.mp4")" \
        -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" -map "[v]" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$(basename "$hp")" )
    [ -f "$hp" ] && return 0
  fi
  return 1
}

python3 "$BUILD" >/dev/null 2>&1                 # フルビルド(窓算出の前提)
mapfile -t WINS < <(python3 "$WINS_PY")
echo "windows: ${#WINS[@]}"
> "$OUTDIR/list.txt"
i=0
for w in "${WINS[@]}"; do
  s="${w%:*}"; e="${w#*:}"; ia=$(printf '%02d' "$i")
  want=$(python3 -c "print(round($e-$s,3))")
  np=$(python3 -c "import math;print(max(4,math.ceil(($e-$s)/6.0)))")
  okall=1; inputs=""; filt=""; k=0
  while [ "$k" -lt "$np" ]; do
    ps=$(python3 -c "print(round($s+($e-$s)*$k/$np,3))")
    pe=$(python3 -c "print(round($s+($e-$s)*($k+1)/$np,3))")
    render_piece "$ps" "$pe" "$OUTDIR/seg${ia}q${k}.mp4" "seg${ia}q${k}" || { okall=0; break; }
    inputs="$inputs -i seg${ia}q${k}.mp4"; filt="${filt}[${k}:v]"; k=$((k+1))
  done
  [ "$okall" = "1" ] || { echo "::error::WINDOW $i ($s-$e) FAILED"; exit 1; }
  ( cd "$OUTDIR" && ffmpeg -loglevel error -y $inputs -filter_complex "${filt}concat=n=${np}:v=1:a=0,tpad=stop_mode=clone:stop_duration=6[v]" -map "[v]" -t "$want" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "seg$ia.mp4" )
  echo "file '$OUTDIR/seg$ia.mp4'" >> "$OUTDIR/list.txt"
  echo "OK window $i $s-$e (pieces=$np)"
  i=$((i+1))
done
ffmpeg -loglevel error -y -f concat -safe 0 -i "$OUTDIR/list.txt" -c copy "$ROOT/visual.mp4"
python3 "$BUILD" >/dev/null 2>&1                 # index.htmlをフルに戻す(念のため)
echo "visual duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$ROOT/visual.mp4")"
