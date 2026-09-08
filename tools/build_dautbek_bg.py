# -*- coding: utf-8 -*-
"""カルシャガ・ダウトベック 完全解説 背景ビルダー（評伝型）。
   方針:
     ・ナレが述べている試合＝その試合の実際の映像を使う（別試合で代用しない）
     ・KO/TKOのナレなし無音区間＝決定打の15秒前〜レフェリーストップを見せる
     ・本人の言葉を紹介する区間＝その発言をしている実際のインタビュー映像
     ・生い立ち/カザフスタン時代＝シラット決勝・Alash Pride・カザフ語特集
   ★1ビート=1素材を明示指定。連続同一素材を作らない(--check)。尾を+13秒確保(黒対策)。
   素材の出所: assets/source/episode_dautbek/assets_index.json
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "source" / "episode_dautbek"
FI = SRC / "fights"; IV = SRC / "iv_clips"; CA = SRC / "cards"
OUT = ROOT / "hyperframes" / "templates" / "dautbek" / "assets" / "bgvid"

# ★割当シグネチャ: 素材名+開始位置+フィルタが変わったビートは強制的に作り直す。
#   これが無いと「ビートIDが同名のまま素材を差し替えた時に古い映像が残る」。
import json as _json
_ASSIGN = OUT / "_assign.json"
try:
    _prev = _json.loads(_ASSIGN.read_text(encoding="utf-8"))
except Exception:
    _prev = {}
_cur = {}
OUT.mkdir(parents=True, exist_ok=True)
TIM = json.load(open(ROOT / "subtitles" / "out" / "dautbek" / "timings.json", encoding="utf-8"))
# cue単位ではなく base_id 単位で背景を持つ
DUR = {}
for c in TIM["cues"]:
    b = c["base_id"]
    DUR[b] = max(DUR.get(b, 0.0), c["end"]) - min(DUR.get(b + "_s", c["start"]), c["start"]) \
        if b in DUR else c["end"] - c["start"]
_span = {}
for c in TIM["cues"]:
    b = c["base_id"]
    s, e = _span.get(b, (c["start"], c["end"]))
    _span[b] = (min(s, c["start"]), max(e, c["end"]))
DUR = {b: e - s for b, (s, e) in _span.items()}

_FIT = ("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p")
# 試合映像は上下のスコアボード/スポンサー帯をクロップして除去
F_FIGHT = "crop=iw:ih*0.80:0:ih*0.10," + _FIT
F_COVER = _FIT


def FT(name, ms):  return (FI / f"{name}.mp4", ms, F_FIGHT, False)   # 試合映像
def IVC(name, ms=1): return (IV / f"{name}.mp4", ms, F_COVER, False)  # インタビュー
def CD(name):      return (CA / f"{name}.jpg", 0, F_COVER, True)      # 対戦カード(KenBurns)


# ★ピラーボックス(左右の黒帯)がある素材は、先に中身だけを切り出してから合わせる。
#   kazakh_feature は区間により 1552/1584/1920 と横幅が変わるので beat 単位で指定する。
def FTP(name, ms, cw, cx):
    f = f"crop={cw}:ih:{cx}:0," + F_FIGHT
    return (FI / f"{name}.mp4", ms, f, False)


PLAN = {
    # ===== 冒頭: 日本のトップを倒してきた男 =====
    "o1":  FT("suzuki_rizin50", 1180),      # 鈴木千裕戦の打ち合い
    "o2":  FT("yaman_rizin49", 900),        # YA-MAN戦
    "o3":  FT("hagiwara_lm15", 71),         # ★本人紹介なので本人単体の区間(40sは萩原のネームスーパーが出る)
    "o4":  FT("kinoshita_rizin48", 250),    # 木下カラテ戦のKO前後
    "o5":  CD("card_dautbek_hiramoto"),     # 対戦カード(ダウトベック×平本蓮)
    "o6":  FT("seki_rizin47", 120),         # 関鉄矢戦

    # ===== 1章 シムケントの少年 =====
    "c1_1": FTP("kazakh_feature", 10, 1364, 274),   # ★左右の黒帯と透かしを除去       # カザフ語特集(故郷・本人)
    "c1_2": FTP("kazakh_feature", 70, 1458, 230),   # ★左右の黒帯と透かしを除去
    "c1_3": IVC("ow13_a"),                 # RIZIN.13 公開計量(2018年当時の本人・計量台)
    "c1_4": IVC("o47_e"),                  # RIZIN.47公式 試合後IV(本人トーキングヘッド)

    # ===== 2章 食えなかった王者 =====
    "c2_1": FTP("kazakh_feature", 130, 1458, 230),  # ★左右の黒帯と透かしを除去
    "c2_2": FT("alash_neres", 5),           # 打撃のKOシーン(ボクシング由来の左)
    "c2_3": IVC("o47_b"),                  # RIZIN.47公式 試合後IV
    "c2_4": FT("kazakh_feature", 190),

    # ===== 3章 シラット世界一 =====
    "c3_1": FT("silat_malaysia", 2),
    "c3_2": FT("silat_malaysia", 25),
    "c3_3": FT("silat_malaysia", 50),
    "c3_4": FT("silat_malaysia", 75),

    # ===== 4章 MMAへ =====
    "c4_1": FT("alash_yousefi", 20),
    "c4_2": FT("alash_yousefi", 150),
    "c4_3": FT("alash_neres", 40),
    "c4_4": FT("matsushima_topbrights", 60),

    # ===== 5章 朝倉未来の壁 =====
    "c5_1": FT("asakura_rizin13", 60),      # 入場・コール
    "c5_2": FT("asakura_rizin13", 240),
    "c5_3": FT("asakura_rizin13", 900),
    "ko_asakura": FT("asakura_rizin13", 1348),  # ★判定結果の発表(1353s)の5秒前から
    "c5_4": IVC("o47_c"),                  # RIZIN.47公式 試合後IV(RIZIN観を語る)
    "c5_5": FT("zhirkov_rcc", 1000),        # ジルコフ戦＝最後の敗戦

    # ===== 6章 6年の沈黙 =====
    "c6_1": FT("zhirkov_rcc", 1180),
    "c6_2": FT("alash_yousefi", 300),
    "c6_3": FT("alash_neres", 20),
    "ko_alash": FT("alash_neres", 40),      # ★海外KO: Alash Pride ネレス戦の決着(約50s)の10秒前から
    "c6_4": FT("matsushima_topbrights", 250),
    "c6_5": FT("matsushima_topbrights", 620),
    "c6_6": IVC("o47_d"),                  # RIZIN.47公式 試合後IV(再上陸の喜び)

    # ===== 7章 RIZIN再上陸 =====
    "c7_1": FT("seki_rizin47", 30),
    "c7_2": FT("seki_rizin47", 160),
    "ko_seki": FT("seki_rizin47", 250),     # ★関戦のKO決着(約263s)の13秒前から
    "c7_3": FT("kinoshita_rizin48", 120),
    "ko_kinoshita": FT("kinoshita_rizin48", 171),  # ★木下戦のKO決着(181s)の10秒前から
    "c7_4": IVC("o47_a"),                  # ★RIZIN.47公式「日本は初めてではない/東京・日本」の実発言
    "c7_5": FT("yaman_rizin49", 1150),      # YA-MAN戦
    "c7_6": FT("suzuki_rizin50", 1500),     # 鈴木千裕戦
    "c7_7": IVC("o50_a"),                  # ★RIZIN.50公式 試合後IV(左目を腫らした直後)
    "c7_8": IVC("o50_b"),                  # ★RIZIN.50公式 試合後IV(鈴木千裕を称える実発言)

    # ===== 8章 離脱と復活 =====
    "c8_1": FT("suzuki_rizin50", 1560),
    "c8_2": CD("card_sr4_akimoto"),         # ★超RIZIN.4 公式カード(ダウトベック×秋元強真。欠場した試合)
    "c8_3": FT("yaman_rizin49", 300),
    "c8_4": CD("card_r52_fukuda"),          # ★RIZIN.52 公式カード(ダウトベック×福田龍彌。中止した試合)
    "c8_5": FT("kazakh_feature", 220),
    "c8_6": FT("zhirkov_rcc", 60),
    "c8_7": IVC("lm15_a"),                  # 「必ず戻ってきます」の文脈
    "c8_8": FT("hagiwara_lm15", 90),
    "c8_9": FT("hagiwara_lm15", 200),
    "ko_hagiwara": FT("hagiwara_lm15", 352),  # ★萩原戦のTKO決着(約362s)の10秒前から
    "c8_10": IVC("lm15_b"),
    "c8_11": IVC("lm15_c"),                 # 「20年経ちますので」

    # ===== 9章 クリーンに勝つ =====
    "c9_1": FT("kinoshita_rizin48", 300),
    "c9_2": IVC("o50_e"),                  # ★RIZIN.50公式「対戦相手を大変尊敬している」
    "c9_3": IVC("lm15_b", 30),              # 萩原の戦績について
    "c9_4": IVC("lm15_c", 30),
    "c9_5": IVC("sr4_c"),                   # 「一人は挙げられない」
    "c9_6": IVC("sr4_b"),                   # 「ランキングは関係ない」
    "c9_7": FT("suzuki_rizin50", 1400),
    "c9_8": IVC("o50_d"),                  # ★RIZIN.50公式 モットー「クリーンな試合で正々堂々と」
    "c9_9": IVC("lm15_a", 30),
    "c9_10": IVC("o48_a"),                 # RIZIN.48公式 試合後IV(会見での本人)
    "c9_11": IVC("o50_c"),                 # ★RIZIN.50公式「お寿司が大好き」の実発言

    # ===== 10章 そして平本蓮 =====
    "c10_1": IVC("sr4_a"),                  # シェイドゥラエフの話
    "c10_2": IVC("sr4_a", 30),
    "c10_3": IVC("sr4_b", 30),
    "c10_4": IVC("sr4_c", 30),              # ATT・元谷友貴
    "c10_5": FT("kazakh_feature", 250),     # シムケントで調整
    "c10_6": IVC("kaiken_sr5"),             # 超RIZIN.5 対戦カード発表記者会見(ダウトベックと平本蓮)
    "c10_7": IVC("kaiken_sr5", 26),         # ★平本評の続きなので本人の会見発言(350sは萩原戦の決着=ko_hagiwaraと同一シーン)

    # ===== 締め =====
    "e1": FTP("kazakh_feature", 40, 1364, 272),     # ★左右の黒帯と透かしを除去
    "e2": FT("silat_malaysia", 84),   # ★カザフスタン国旗を掲げる優勝の瞬間(「世界一になり」に一致)
    "e3": FT("hagiwara_lm15", 330),
    "e4": CD("card_kv"),                    # 超RIZIN.5 大会キービジュアル(9/10 京セラドーム大阪)
    "e5": FT("suzuki_rizin50", 1580),
}


def srcdur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 0.0


_HDR_TM = ("zscale=t=linear:npl=100,tonemap=hable:desat=0,"
           "zscale=p=bt709:t=bt709:m=bt709:r=tv,format=yuv420p,")
_ct_cache = {}
def _is_hdr(p):
    """★HLG/HDR(arib-std-b67, bt2020)が1本でも混じるとCIのソフトウェア合成が
       HDR経路に入り、特定フレームでハングしてピースが必ず失敗する(リトライ無効)。
       ここで検出してSDR(bt709)へトーンマップしてから使う。"""
    p = str(p)
    if p in _ct_cache: return _ct_cache[p]
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=color_transfer", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    v = r.stdout.strip().rstrip(",")
    hd = v not in ("bt709", "", "unknown")
    _ct_cache[p] = hd; return hd


def build(bid, src, ms, filt, kb, force=False):
    out = OUT / f"{bid}.mp4"
    sig = f"{Path(src).name}|{ms}|{filt}|{int(bool(kb))}"
    _cur[bid] = sig
    if _prev.get(bid) != sig: force = True     # ★割当が変わったら作り直す
    if out.exists() and out.stat().st_size > 5000 and not force: return "skip"
    src = Path(src)
    if not src.exists(): return f"MISSING {src.name}"
    need = DUR.get(bid, 6.0) + 13.0
    is_img = str(src).lower().endswith((".jpg", ".jpeg", ".png"))
    cmd = ["ffmpeg", "-y", "-v", "error"]
    if is_img:
        cmd += ["-loop", "1", "-t", f"{need:.2f}", "-i", str(src), "-vf", F_COVER]
    else:
        sd = srcdur(src); loop = (ms + need) > (sd - 0.1)
        if loop:
            cmd = ["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", str(src),
                   "-ss", f"{ms:.2f}", "-t", f"{need:.2f}"]
        else:
            cmd += ["-ss", f"{ms:.2f}", "-i", str(src), "-t", f"{need:.2f}"]
        cmd += ["-vf", (_HDR_TM + filt) if _is_hdr(src) else filt]
    cmd += ["-an", "-r", "30", "-g", "30", "-keyint_min", "30", "-c:v", "libx264", "-crf", "21",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: return f"ERR {r.stderr[-160:]}"
    return f"ok {out.stat().st_size//1024}KB"


def check():
    ids = [c["base_id"] for c in TIM["cues"]]
    seen = []
    for i in ids:
        if not seen or seen[-1] != i: seen.append(i)
    ok = True
    miss = [i for i in dict.fromkeys(ids) if i not in PLAN]
    extra = [i for i in PLAN if i not in ids]
    if miss: print(f"★未割当ビート({len(miss)}): {miss}"); ok = False
    if extra: print(f"★存在しないビートID: {extra}"); ok = False
    prev = None
    for i in seen:
        v = PLAN.get(i)
        if not v: continue
        key = (Path(v[0]).name, round(v[1]))
        if prev and key == prev[1]:
            print(f"★連続同一素材: {prev[0]} -> {i} {key}"); ok = False
        prev = (i, key)
    print(f"beats={len(dict.fromkeys(ids))} planned={len(PLAN)} 判定={'OK' if ok else 'NG'}")
    return ok


if __name__ == "__main__":
    if "--check" in sys.argv:
        raise SystemExit(0 if check() else 1)
    only = [x for x in sys.argv[1:] if not x.startswith("--")] or None
    force = "--force" in sys.argv
    for bid, (src, ms, filt, kb) in PLAN.items():
        if only and bid not in only: continue
        print(f"[{bid}] {build(bid, src, ms, filt, kb, force)}")
    if not only:
        _ASSIGN.write_text(_json.dumps(_cur, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"割当シグネチャを保存 ({len(_cur)}件)")
