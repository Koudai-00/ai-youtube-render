# -*- coding: utf-8 -*-
"""超RIZIN.5 全試合ガイド 背景ビルダー。各ビート=専用bgvid(<id>.mp4)。
   方針: 各選手のビート=その選手の代表試合フッテージの別セグメント(使い回し回避)。試合紹介=公式VSカード。
     抽象/マッチアップ/OP/締め=Pexels(新規ID)/キービジュアル。冨澤=中止カード。
   試合映像は上下のスコアボード/スポンサーをクロップ除去。1秒毎キーフレーム再エンコード。
   ソース素材の内容はassets_index.json/finish_windows.txtに記録済み。"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "source" / "episode_rizin5_guide"
FI = SRC / "fights"; CA = SRC / "cards"; PX = SRC / "pexels"; PV = SRC / "provided"
OUT = ROOT / "hyperframes" / "templates" / "rizin5_guide" / "assets" / "bgvid"
OUT.mkdir(parents=True, exist_ok=True)
TIM = json.load(open(ROOT / "subtitles" / "out" / "rizin5_guide" / "timings.json", encoding="utf-8"))
DUR = {b["id"]: b["end"] - b["start"] for b in TIM["beats"]}
# ★ビート内分割(bg_splits.json)に対応: <beat>_2 等の必要尺を分割境界から算出する
_SP = ROOT / "hyperframes" / "templates" / "rizin5_guide" / "bg_splits.json"
if _SP.exists():
    _splits = json.load(open(_SP, encoding="utf-8"))
    for b in TIM["beats"]:
        cuts = sorted(t for t in _splits.get(b["id"], []) if b["start"] + 0.4 < t < b["end"] - 0.4)
        if not cuts: continue
        bounds = [b["start"]] + cuts + [b["end"]]
        for k in range(len(bounds) - 1):
            key = b["id"] if k == 0 else f'{b["id"]}_{k+1}'
            DUR[key] = bounds[k+1] - bounds[k]

def pex(name):
    g = list(PX.glob(f"{name}_*.mp4")); return g[0] if g else None

# フィルタ: 試合映像=上下グラフィッククロップ→cover / カード・Pexels=cover
F_FIGHT = "crop=iw:ih*0.80:0:ih*0.10,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p"
F_COVER = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p"
F_ABEMA = "crop=iw*0.86:ih*0.70:0:ih*0.16,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p"

def FT(name, ms, f=None): return (FI / f"{name}.mp4", ms, f or F_FIGHT, False)   # 試合(動画)
def CD(n, kb=True): return (CA / f"card_{n}.jpg", 0, F_COVER, kb)    # カード(静止画・KenBurns)
def PE(name, ms): return (pex(name), ms, F_COVER, False)             # Pexels(動画)★この動画では使用禁止
def PR(name, ms): return (PV / f"{name}.mp4", ms, F_FIGHT, False)    # 提供(会見/練習/冒頭)
def PRC(name, ms): return (PV / f"{name}.mp4", ms, F_COVER, False)   # 提供(クロップ無し=会見の字幕を残す場合)

# ★画面左右2分割(対戦両者を対比表示)= チャーリー・ガイド型。SP("左clip",左ms,"右clip",右ms)
def SP(lname, lms, rname, rms):
    return ("SPLIT", (FI / f"{lname}.mp4", lms), (FI / f"{rname}.mp4", rms))

# beat_id -> source
PLAN = {
    # ============ OP ============
    "o1": PR("opening", 5),                       # 大会オープニング映像
    "o2": CD("01"),                               # メインVSカード(シェイド×AJ)
    "o3": CD("09"),                               # 大会キービジュアル(全選手)
    "o4": PR("openworkout", 1997),                # ★B1 出場選手がマイクで話している様子(1:04〜。アナウンサー回避)
    "z1": PR("openworkout", 3838),                # ★冨澤の対戦相手言及(1:03:52〜)ユーザー指定
    # ============ 第1試合 ベイノア×宇佐美(OFGキック) ============
    "f1a": CD("08"),                              # 対戦カード
    "f1b": FT("usami_peemai", 32),                # 宇佐美 リング紹介(名前コール/ポーズ)
    "f1c": FT("usami_peemai", 112),               # 前戦KOフィニッシュ(D1・維持)
    "f1d": FT("usami_intro2", 4047),              # ★B2 武尊の番組に出演する宇佐美(3:09〜)
    "f1e": FT("beynoah_recent", 40),              # ベイノア 名前コール+プロフィール(現状維持)
    "f1f": FT("beynoah_recent", 290),             # ★B3/B4 前戦の試合本編(f1eの40〜と重複させない=巻き戻り解消)
    "f1g": SP("usami_peemai", 104, "beynoah_recent", 300),   # ★B5 左=宇佐美のダウン前の攻防に変更
    "f1h": PR("openworkout", 783),                # ★B6 宇佐美の公開練習(13:03〜)
    # ============ 第2試合 RENA×クジュティナ ============
    "f2a": CD("06"),
    "f2b": FT("rena_intro", 695),                 # ★B7 RENA本人(伊澤の映像を回避)
    "f2c": FT("rena_intro", 695),                 # ★B8 (5:24〜)
    "f2c_2": FT("rena_izawa", 170),               # ★B9 (5:37〜 lZ6r7WZWT28の2:50)
    "f2d": PR("presser1", 900),                   # 会見(王座返上→見えないトーナメント)
    "f2e": FT("kuzi_fight", 25),                  # ★B10 クジュティナ 名前コール+プロフィール(6:22〜)
    "f2e_2": FT("rena_other", 241),               # ★B11 (6:30〜)
    "f2f": FT("kuzi_fight", 380),                 # ★B12 (6:52〜)
    "f2g": SP("rena_intro", 680, "kuzi_fight", 172), # ★B13 左=uLV3tAnngUA11:20/右=fCH-NrV1TlY2:52
    # ============ 第3試合 ケラモフ×高木 ============
    "f3a": CD("04"),
    "f3b": FT("kelamov_asakura", 180),            # ケラモフ 紹介
    "f3c": FT("kelamov_asakura", 320),            # 朝倉戦フィニッシュ(代表試合)
    "f3d": FT("satoshi_kelamov", 430),            # サトシ戦一本負け(連敗)
    "f3e": FT("takagi_kaiwen", 55),               # ★高木 名前コール+プロフィール
    "f3f": FT("takagi_kaiwen", 184),              # ★カイウェン戦KO(C4/打撃の代表試合)
    "f3g": SP("takagi_other", 273, "takagi_kaiwen", 186),  # ★B14 左=niq1AKbWOCk 4:33
    "f3h": PR("openworkout", 4094),               # ★B15 高木の公開練習(ベイノアと逆だったのを修正)
    # ============ 第4試合 斎藤×YA-MAN ============
    "f4a": CD("03"),
    "f4b": FT("saito_asakura", 200),              # 斎藤 紹介
    "f4c": FT("saito_asakura", 1152),             # ★判定勝利シーン(D4・ダウン回避)
    "f4d": FT("saito_other", 723),                # ★B16 (11:28〜)
    "f4e": FT("yaman_asakura", 150),              # YA-MAN 紹介
    "f4f": FT("yaman_other", 325),                # ★B17 (12:24〜)
    "f4g": SP("saito_intro", 217, "yaman_other", 873),  # ★B18 2分割 左=AEZosftj1GE3:37/右=4r8TECMXsNI14:33
    "f4h": PR("presser1", 2152),                  # ★B19 対戦カード発表(35:52〜)
    # ============ 第5試合 ダウトベック×平本 ============
    "f5a": CD("02"),
    "f5b": FT("dautbek_hagiwara", 180),           # ダウトベック 紹介
    "f5c": FT("dautbek_hagiwara", 355),           # 萩原戦1RKO(代表試合)
    "f5d": FT("dautbek_other", 24),               # ★B20 (14:21〜)
    "f5d_2": FT("dautbek_intro", 242),            # ★B21 (14:33〜)
    "f5e": FT("hiramoto_other", 283),             # ★B22 (14:43〜)
    "f5f": FT("hiramoto_koji", 38),               # ★皇治との復帰戦・平本入場+プロフィール(C8)
    "f5g": SP("hiramoto_intro", 164, "dautbek_hagiwara", 360), # ★B23 左=SKXpMO13OL8 2:44
    "f5h": PR("presser3", 1093),                  # ★B24 開催発表会見(18:13〜)
    # ============ 第6試合 サトシ×野村 ============
    "f6a": CD("07"),
    "f6b": FT("satoshi_other", 54),               # ★B25 サトシ プロフィール表示(16:33〜)
    "f6c": FT("satoshi_musaev", 270),             # ムサエフ戦 三角絞め(代表試合)
    "f6d": FT("satoshi_kelamov", 200),            # 王座陥落〜奪回への思い
    "f6e": FT("nomura_other", 27),                # ★B26 野村 名前コール+プロフィール(17:36〜)
    "f6e_2": FT("nomura_other", 952),             # ★B27 (17:56〜)
    "f6f": FT("nomura_patricky", 900),            # パトリッキー戦 判定勝ち(代表試合)
    "f6g": SP("satoshi_musaev", 275, "nomura_patricky", 905), # ★2分割(寝技/打撃レスリング)
    "f6h": PR("openworkout", 2350),               # 公開練習
    # ============ セミ 朝倉×青木 ============
    "f7a": CD("05"),
    "f7b": FT("shaydullaev_asakura", 130),        # 朝倉 紹介
    "f7c": FT("aoki_other", 297),                 # ★B28 (20:02〜)
    "f7d": FT("hiramoto_asakura", 210),           # 近年の苦戦(平本戦)
    "f7e": FT("aoki_hansen", 300),                # ★青木 紹介(ハンセン戦の攻防)
    "f7f": FT("aoki_hansen", 735),                # ★ハンセン戦 腕十字フィニッシュ(D6)
    "f7g": PR("presser2", 2861),                  # ★B29 追加カード発表(47:41〜)
    "f7h": SP("shaydullaev_asakura", 140, "aoki_hansen", 600), # ★2分割(新旧ドリームマッチ)
    # ============ メイン シェイド×AJ ============
    "m1": CD("01"),
    "m2": FT("shaydullaev_kleber", 180),          # シェイド 紹介
    "m3": FT("shaydullaev_kubo", 300),            # トップコントロール
    "m4": FT("shaydullaev_kleber", 300),          # クレベル戦KO(代表試合)
    "m5": FT("ajmckee_satoshi", 1560),            # ★AJ 紹介(実映像・勝利者インタビュー)
    "m6": FT("ajmckee_b263", 17),                 # ★B30 Bellator263 決勝(2:25:17〜)
    "m6b": FT("ajmckee_satoshi", 620),            # RIZIN.40 サトシ戦(24:56=現状維持)
    "m6b_2": FT("ajmckee_pfl", 977),              # ★B31 PFLイスブラエフ戦(25:15〜)
    "m7": FT("ajmckee_satoshi", 980),             # リーチ差/サウスポーの打撃
    "m8": SP("shaydullaev_kleber", 310, "ajmckee_satoshi", 1000), # ★2分割(統一戦の対比)
    "m9": FT("shaydullaev_asakura", 190),         # トップコントロールを止められるか
    "m10": PR("opening", 12),                     # ★B32 大会オープニング 0:12〜0:38
    # ============ 締め ============
    "e1": CD("09"),
    "e2": PR("presser1", 2400),                   # 会見(「どの試合が注目か」の問いかけ)
    "e3": PR("presser3", 1200),                   # 会見(締め・CTA)
}

MO_KB = True  # カード静止画はKenBurns

def srcdur(p):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(p)],
                       capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 0.0

def build_split(bid, left, right, force=False):
    """左右2分割(各960x1080)で対戦両者を対比表示。中央に細い区切り線。"""
    out = OUT / f"{bid}.mp4"
    if out.exists() and out.stat().st_size > 5000 and not force: return "skip"
    (lp, lms), (rp, rms) = left, right
    for p in (lp, rp):
        if not p or not Path(p).exists(): return f"MISSING {p}"
    need = DUR.get(bid, 6.0) + 13.0   # ★piece終端まで延長できるよう十分な尾を確保(黒対策)
    def seg(p, ms, idx):
        sd = srcdur(p)
        return (["-stream_loop","-1","-i",str(p),"-ss",f"{ms:.2f}","-t",f"{need:.2f}"]
                if (ms+need) > (sd-0.1) else ["-ss",f"{ms:.2f}","-i",str(p),"-t",f"{need:.2f}"])
    # 各半分: 上下グラフィックをクロップ→960x1080にcover
    half = ("crop=iw:ih*0.80:0:ih*0.10,scale=960:1080:force_original_aspect_ratio=increase,"
            "crop=960:1080,fps=30,format=yuv420p")
    fc = (f"[0:v]{half}[L];[1:v]{half}[R];[L][R]hstack=inputs=2[s];"
          f"[s]drawbox=x=958:y=0:w=4:h=1080:color=white@0.85:t=fill[v]")
    cmd = ["ffmpeg","-y","-v","error"] + seg(lp, lms, 0) + seg(rp, rms, 1) + \
          ["-filter_complex", fc, "-map","[v]","-an","-r","30","-g","30","-keyint_min","30",
           "-c:v","libx264","-crf","21","-pix_fmt","yuv420p","-movflags","+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: return f"ERR {r.stderr[-200:]}"
    return f"ok(split) {out.stat().st_size//1024}KB"


def build(bid, src, ms, filt, kb, force=False):
    out = OUT / f"{bid}.mp4"
    if out.exists() and out.stat().st_size > 5000 and not force: return "skip"
    if not src or not Path(src).exists(): return f"MISSING {src}"
    need = DUR.get(bid, 6.0) + 13.0
    is_img = str(src).lower().endswith((".jpg", ".jpeg", ".png"))
    cmd = ["ffmpeg","-y","-v","error"]
    if is_img:
        # 静止画→静止cover(動き=テンプレ側GSAPのKenBurnsで付与。zoompanは激遅/巨大化のため不使用)
        cmd += ["-loop","1","-t",f"{need:.2f}","-i",str(src)]
        cmd += ["-vf","scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p"]
    else:
        sd=srcdur(src); loop=(ms+need)>(sd-0.1)
        if loop: cmd = ["ffmpeg","-y","-v","error","-stream_loop","-1","-i",str(src),"-ss",f"{ms:.2f}","-t",f"{need:.2f}"]
        else: cmd += ["-ss",f"{ms:.2f}","-i",str(src),"-t",f"{need:.2f}"]
        cmd += ["-vf",filt]
    cmd += ["-an","-r","30","-g","30","-keyint_min","30","-c:v","libx264","-crf","21",
            "-pix_fmt","yuv420p","-movflags","+faststart",str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: return f"ERR {r.stderr[-200:]}"
    return f"ok {out.stat().st_size//1024}KB"

if __name__ == "__main__":
    only = [x for x in sys.argv[1:] if not x.startswith("--")] or None
    force = "--force" in sys.argv
    for bid, spec in PLAN.items():
        if only and bid not in only: continue
        if spec and spec[0] == "SPLIT":
            print(f"[{bid}] {build_split(bid, spec[1], spec[2], force)}")
        else:
            src, ms, filt, kb = spec
            print(f"[{bid}] {build(bid, src, ms, filt, kb, force)}")
