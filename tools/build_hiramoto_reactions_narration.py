# -*- coding: utf-8 -*-
"""朝倉海 UFC上海 勝利まとめ(日本+海外・多言語) JPナレ生成。
   音声=Fish 女性ニュース音声D(丁寧体)。読みは phonetic_map + 局所置換。
   フィニッシュ挿入(ko)は無音ビート(SILENCE:秒)。実音声はfinalizeでmux。
   出力: subtitles/out/hiramoto_reactions/ に narration_full.wav + timings.json。"""
from __future__ import annotations
import hashlib, json, subprocess, sys, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from voice.voicevox_tts import load_phonetic_map, apply_phonetic  # noqa
from voice.fish_tts import synth_fish  # noqa

OUT_DIR = ROOT / "subtitles" / "out" / "hiramoto_reactions"
OUT_DIR.mkdir(parents=True, exist_ok=True)
VOICE_ID = "446030196f23417b9bf30be4c350a18a"   # 女性ニュース音声D
SR = 44100
LEAD_IN = 0.25
GAP = 0.24
CHAP_GAP = 0.55
_PMAP = load_phonetic_map()
# 局所読み(Fish誤読対策)。テロップ表記は別(テンプレDISPで正式表記)。
READ = {"金原": "かねはら", "竹内": "たけうち", "朝倉海": "あさくらかい", "朝倉": "あさくら",
        "修斗": "しゅうと", "全8試合": "ぜんはちしあい", "京セラドーム": "きょうセラドーム"}

# (chapter, id, JP text)
# ★冒頭72秒はナレなしのリアクション・モンタージュ（build_hiramoto_reactions_open.py）。
#   この台本はその直後から始まる本編。順番はユーザー指定:
#   試合の概要 → 判定結果 → 反対・驚いた人たち → 詳しく説明/反論していない人たち。
BEATS = [
    # ===== 導入 =====
    ("open", "o1", "スーパーライジンファイブ第6試合。ひらもとれん対カルシャガダウトベック。この判定結果が大きな議論になっています。"),
    ("open", "o2", "まずは試合の中身を確認します。"),

    # ===== 第1章 試合の概要と判定結果 =====
    ("ch1", "c1a", "いちラウンド、ダウトベックの左が何度もクリーンヒットします。ひらもとは明らかに効かされ、かたひざをつく場面もありました。"),
    ("ch1", "c1b", "ただ、レフェリーはダウンを取っていません。ここがあとで大きな意味を持ちます。"),
    ("ch1", "c1c", "にラウンドはひらもとがインローを効かせて盛り返します。ダウトベックのテイクダウンも決め手にはなりませんでした。"),
    ("ch1", "c1d", "さんラウンドもダウトベックがテイクダウンを奪いますが、倒したあとの攻撃は多くありません。ひらもとは手数を出し続けました。"),
    ("ch1", "c1e", "判定は、はんていにたいいちでひらもとの勝利。"),
    ("ch1", "c1f", "報じられたスコアは、にじゅうきゅうたいにじゅうはちでひらもとがふたり。にじゅうきゅうたいにじゅうななでダウトベックがひとりです。"),
    ("ch1", "c1g", "ひとりのジャッジだけが、いちラウンドをじゅうたいはちと見ていた計算になります。"),

    # ===== 第2章 判定に反対・驚いた人たち =====
    ("ch2", "c2a", "この結果に、まず強い反応が出ました。"),
    ("ch2", "c2b", "同時視聴配信をしていたヒカキンさんは、スコアが読み上げられるたびに、ひらもと、と聞き返していました。"),
    ("ch2", "c2b2", "そしてダウトベックはあり得ないって顔をしている、とも口にしています。"),
    ("ch2", "c2c", "元ディープフェザー級王者のジョビンさんは、今までの判定でいちばん驚いたかもしれない、と漏らしました。"),
    ("ch2", "c2d", "そのうえで、ひらもと自身が負けた顔をしていた。これはさすがにまずいんじゃないか、とも語っています。"),
    ("ch2", "c2e", "会場でも、ひらもとの陣営が結果を聞いた瞬間に固まっていました。"),
    ("ch2", "c2f", "現役で戦うストラッサーきいち選手は、生解説の途中で言葉を失います。"),
    ("ch2", "c2g", "嘘やろ。これはダウトベックがかわいそう。俺は納得できへん。そう繰り返しました。"),
    ("ch2", "c2h", "そのうえで、この採点に関してひらもとは悪くない。ジャッジがつけたのだから、ひらもとを責めるのは絶対に違う、と付け加えています。"),
    ("ch2", "c2i", "元リングス代表のまえだあきらさんも、あの展開でにたいいちは正直つらい、という見方を示しました。"),

    # ===== 第3章 判定を説明する／反論していない人たち =====
    ("ch3", "c3a", "一方で、判定の中身を説明する声もあります。"),
    ("ch3", "c3b", "ライジンのさかきばらのぶゆきさんは、大会後の会見でこう述べました。"),
    ("ch3", "c3c", "ディフェンシブなエスケープ的なテイクダウンはまったくポイントにならない。てきかくににラウンドとさんラウンドを取ったのがひらもとだと、ジャッジは見たのではないか、と。"),
    ("ch3", "c3d", "いちラウンドでひらもとはかたひざをついたが、ダウンは取られていない。だからじゅうたいはちにはならなかったのだろう、とも話しています。"),
    ("ch3", "c3e", "ひらもと本人は、リング上で判定を聞いた瞬間に驚いた表情を見せ、試合後には涙も見せました。"),
    ("ch3", "c3f", "その理由を、ケーオーするつもりだったので悔しくて泣いてしまった、と説明しています。"),
    ("ch3", "c3g", "にラウンドとさんラウンドは見返しても取れていた。ライジンはトータルではなくラウンドマストだから、そこも大きかったとも話しました。"),
    ("ch3", "c3h", "その計算は、試合直後に控室でセコンドからも伝えられていました。"),
    ("ch3", "c3i", "いちラウンドをじゅうたいはちとつけたジャッジはひとり。あとはじゅうたいきゅうで、にラウンドとさんラウンドはひらもと。だから勝てている、という説明です。"),
    # ★引用は本人の一人称の発言だけを使う（聞き手が論点を整理した部分は本人の言葉にしない）
    ("ch3", "c3j", "ライジンフィフティーでダウトベックと、ランドマークボリュームツーでひらもとと戦っているすずきちひろ選手は、判定そのものへの向き合い方を語りました。"),
    ("ch3", "c3k", "自分はケーオーするつもりで戦っているから関係ない。他人に自分の勝敗をゆだねた時点で終わっている、と話します。"),
    ("ch3", "c3k2", "そのうえで、決めるのはレフェリーなのだからしょうがない、と言い切りました。"),
    ("ch3", "c3k3", "多少の抗議は出ると思う。ただ判定まで行く前に自分で処理しなければいけない、とも話しています。"),
    ("ch3", "c3l", "ライジンで戦うおうぎくぼひろまさ選手は、終わった瞬間これはひらもとの勝ちかなと思ったと明かしています。"),
    ("ch3", "c3m", "何発クリーンヒットしても立ち続けた打たれ強さに驚愕した。テイクダウンを取られたあとに立つ技術も素晴らしかった、と評価しました。"),
    ("ch3", "c3n", "元修斗世界王者のいしわたりしんたろうさんも、最初は嘘じゃないかと思ったと振り返ります。"),
    ("ch3", "c3o", "ただ冷静に考えるとひらもとの勝ち。にラウンドとさんラウンドはひらもとで間違いない。分かれ目はいちラウンドをじゅうたいはちと見るか、じゅうたいきゅうと見るかだけだ、という整理です。"),
    ("ch3", "c3p", "ダウンはしていないけれど、ケーオー負け寸前だと評価すればじゅうたいはちも分かる。だからどちらも妥当で、両者勝ちだとも話しました。"),
    ("ch3", "c3q", "もっとも率直だったのは、実況席で解説していたかわじりたつやさんです。"),
    ("ch3", "c3r", "解説中は、いちラウンドをじゅうたいはちでダウトベック。にじゅうはちたいにじゅうはちのドローからダメージ差でダウトベックだと思っていた、と明かしました。"),
    ("ch3", "c3s", "ところが試合を見返して、考えを変えたと話します。"),
    ("ch3", "c3t", "完全に効いたのは最初の左だけで、そのあとはしっかり打ち返していた。これならじゅうたいはちはつかないかもしれない、と。"),
    ("ch3", "c3u", "いちラウンドがじゅうたいきゅうでダウトベックなら、にラウンドとさんラウンドがひらもと。にじゅうきゅうたいにじゅうはちは全然あり得るし、正当な評価かもしれない、と述べています。"),
    ("ch3", "c3v", "自分も実況も、いちラウンドの左フックと最後のパウンドの印象に引っ張られてしまった、とも振り返りました。"),

    # ===== まとめ =====
    ("close", "e1", "分かれ目は、いちラウンドをどう見るか。そしてラウンドごとに見るのか、試合全体で見るのかでした。"),
    ("close", "e2", "同じ映像を見ていても、見る基準が違えば結論は変わります。だからこそ、これだけ意見が割れたのかもしれません。"),
    ("close", "e3", "あなたは、どちらの勝ちだと思いましたか。"),
]


def _read(text: str) -> str:
    t = apply_phonetic(text, _PMAP)
    for k, v in READ.items():
        t = t.replace(k, v)
    return t


def tts(text: str, out: Path) -> float:
    if not (out.exists() and out.stat().st_size > 2000):
        synth_fish(_read(text), out, temperature=0.6, sr=SR, voice_id=VOICE_ID)
    with wave.open(str(out), "rb") as w:
        return w.getnframes() / w.getframerate()


def silence(seconds: float, out: Path) -> None:
    n = max(0, int(seconds * SR))
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(b"\x00\x00" * n)


def main() -> int:
    wavs = OUT_DIR / "wavs"; wavs.mkdir(parents=True, exist_ok=True)
    parts, cur = [], 0.0
    beats, chapters = [], []
    sp = wavs / "lead.wav"; silence(LEAD_IN, sp); parts.append(sp); cur += LEAD_IN
    prev_ch, bi = None, 0
    for i, (ch, bid, text) in enumerate(BEATS):
        if i > 0:
            g = GAP + (CHAP_GAP if ch != prev_ch else 0.0)
            gp = wavs / f"gap_{i}.wav"; silence(g, gp); parts.append(gp); cur += g
        if ch != prev_ch:
            chapters.append({"chapter": ch, "start": round(cur, 3)})
            prev_ch = ch
        is_sil = text.startswith("SILENCE:")
        key = hashlib.sha1(_read(text).encode("utf-8")).hexdigest()[:12]
        wav = wavs / f"{bi:02d}_{bid}_{key}.wav"
        if is_sil:
            d = float(text.split(":", 1)[1]); silence(d, wav)
        else:
            d = tts(text, wav)
        parts.append(wav)
        beats.append({"id": bid, "chapter": ch, "idx": bi, "start": round(cur, 3),
                      "end": round(cur + d, 3), "text": ("" if is_sil else text), "silence": is_sil})
        print(f"  [{bi:2d}] {ch:4} {cur:7.2f}-{cur+d:7.2f} ({d:4.2f}s) {bid}{' [SILENCE]' if is_sil else ''}", flush=True)
        cur += d; bi += 1
    sp = wavs / "tail.wav"; silence(0.6, sp); parts.append(sp); cur += 0.6
    total = cur
    lst = OUT_DIR / "_concat.txt"
    lst.write_text("\n".join(f"file '{p.as_posix()}'" for p in parts), encoding="utf-8")
    narration = OUT_DIR / "narration_full.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-ar", str(SR), "-ac", "1", str(narration)], check=True)
    (OUT_DIR / "timings.json").write_text(json.dumps(
        {"total": round(total, 3), "voice": VOICE_ID, "engine": "fish",
         "beats": beats, "chapters": chapters}, ensure_ascii=False, indent=2), encoding="utf-8")
    mm, ss = divmod(total, 60)
    print(f"\nTOTAL = {total:.2f}s ({int(mm)}:{ss:04.1f}) beats={len(beats)} chapters={len(chapters)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
