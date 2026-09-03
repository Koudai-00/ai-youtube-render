#!/usr/bin/env bash
# 窓分割レンダー(CI版)。chrome-headless-shell は各ピース描画の先頭~0.4sを黒で出す(ウォームアップ)。
# 対策: 各ピースを LEAD 秒の「捨てリードイン」付きで描画→そのLEAD秒をトリムして捨てる(黒を捨て部分へ追い出す)。
# これで尺・音声同期を保ったまま、ピース/窓境界の黒フラッシュを消す。
set -u
ROOT="$(pwd)"
EP="${EP:-rizin54-yosou}"
EP_SNAKE="${EP//-/_}"
TPL="$ROOT/hyperframes/templates/$EP"
OUTDIR="$ROOT/_segs"
BUILD="$ROOT/tools/build_${EP_SNAKE}_template.py"
# ★ビルダー名の別表記(アンダースコア無し)にもフォールバックし、どちらも無ければ即失敗させる。
#   以前、名前不一致でビルダーが無言スキップされ、テンプレ修正が反映されない事故が起きた。
if [ ! -f "$BUILD" ]; then
  ALT="$ROOT/tools/build_$(echo "$EP_SNAKE" | tr -d _)_template.py"
  if [ -f "$ALT" ]; then BUILD="$ALT"; else
    echo "::error::template builder not found: $BUILD / $ALT"; exit 1
  fi
fi
echo "BUILD=$BUILD"
WINS_PY="$ROOT/tools/${EP_SNAKE}_windows.py"
LEAD=1.0
TRAIL=0.5
mkdir -p "$OUTDIR"
export PRODUCER_PUPPETEER_PROTOCOL_TIMEOUT_MS="${PRODUCER_PUPPETEER_PROTOCOL_TIMEOUT_MS:-600000}"

# rs re out tag : 窓[rs,re]を描画(リトライのみ・分割なし=6sピースは十分小さい)
render_raw() {
  local rs="$1" re="$2" out="$3" tag="$4" a hd want
  want=$(python3 -c "print(round($re-$rs,3))")
  for a in 1 2 3 4; do
    HF_WIN_START="$rs" HF_WIN_END="$re" python3 "$BUILD" >/dev/null 2>&1
    ( cd "$TPL" && timeout 900 xvfb-run -a hyperframes render -c index.html -o "$out" --fps 30 -q standard --workers 1 >"$OUTDIR/$tag.log" 2>&1 )
    if [ -f "$out" ]; then
      hd=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out" 2>/dev/null)
      if [ -n "$hd" ] && python3 -c "exit(0 if abs($hd-$want)<1.2 and $hd>0.3 else 1)"; then return 0; fi
      rm -f "$out"
    fi
    echo "   raw $tag attempt$a fail ($rs-$re)"; tail -3 "$OUTDIR/$tag.log" 2>/dev/null
  done
  return 1
}

python3 "$BUILD" || { echo "::error::builder failed"; exit 1; }
mapfile -t WINS < <(python3 "$WINS_PY")
echo "windows: ${#WINS[@]}"
> "$OUTDIR/list.txt"
wi=0
for w in "${WINS[@]}"; do
  s="${w%:*}"; e="${w#*:}"; ia=$(printf '%02d' "$wi")
  want=$(python3 -c "print(round($e-$s,3))")
  np=$(python3 -c "import math;print(max(3,math.ceil(($e-$s)/${PIECE_SEC:-6}.0)))")
  inputs=""; filt=""; k=0
  while [ "$k" -lt "$np" ]; do
    ps=$(python3 -c "print(round($s+($e-$s)*$k/$np,3))")
    pe=$(python3 -c "print(round($s+($e-$s)*($k+1)/$np,3))")
    # 捨てリードイン(全体先頭のみ0) ＋ 捨てトレイル(末尾のクールダウン黒対策)
    lead=$(python3 -c "print(round(min($LEAD,$ps),3))")
    keep=$(python3 -c "print(round($pe-$ps,3))")
    rs=$(python3 -c "print(round($ps-$lead,3))")
    re=$(python3 -c "print(round($pe+$TRAIL,3))")
    render_raw "$rs" "$re" "$OUTDIR/seg${ia}q${k}.mp4" "seg${ia}q${k}" || { echo "::error::piece $ia q$k FAILED"; exit 1; }
    inputs="$inputs -i seg${ia}q${k}.mp4"
    # 先頭lead秒＋末尾TRAIL秒を捨て、正味[ps,pe]=keep秒だけ残す(前後の黒フレーム除去)
    filt="${filt}[${k}:v]trim=start=${lead}:duration=${keep},setpts=PTS-STARTPTS[t${k}];"
    k=$((k+1))
  done
  cc=""; k=0; while [ "$k" -lt "$np" ]; do cc="${cc}[t${k}]"; k=$((k+1)); done
  ( cd "$OUTDIR" && ffmpeg -loglevel error -y $inputs \
      -filter_complex "${filt}${cc}concat=n=${np}:v=1,tpad=stop_mode=clone:stop_duration=6[v]" \
      -map "[v]" -t "$want" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "seg$ia.mp4" )
  echo "file '$OUTDIR/seg$ia.mp4'" >> "$OUTDIR/list.txt"
  echo "OK window $wi $s-$e (pieces=$np, lead-trim=${LEAD}s)"
  wi=$((wi+1))
done
ffmpeg -loglevel error -y -f concat -safe 0 -i "$OUTDIR/list.txt" -c copy "$ROOT/visual.mp4"
python3 "$BUILD" >/dev/null 2>&1
echo "visual duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$ROOT/visual.mp4")"
