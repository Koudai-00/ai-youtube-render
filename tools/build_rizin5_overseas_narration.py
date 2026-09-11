# -*- coding: utf-8 -*-
"""超RIZIN.5 メイン AJ・マッキー vs シェイドゥラエフ「海外の反応」まとめ JPナレ生成。
   音声=Fish 女性ニュース音声D(丁寧体)。読みは phonetic_map + 局所置換。
   出力: subtitles/out/rizin5_overseas/ に narration_full.wav + timings.json。"""
from __future__ import annotations
import hashlib, json, subprocess, sys, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from voice.voicevox_tts import load_phonetic_map, apply_phonetic  # noqa
from voice.fish_tts import synth_fish  # noqa

OUT_DIR = ROOT / "subtitles" / "out" / "rizin5_overseas"
OUT_DIR.mkdir(parents=True, exist_ok=True)
VOICE_ID = "446030196f23417b9bf30be4c350a18a"   # 女性ニュース音声D
SR = 44100
LEAD_IN = 0.25
GAP = 0.24
CHAP_GAP = 0.55
_PMAP = load_phonetic_map()
# 局所読み(Fish誤読対策)。テロップ表記は別(テンプレDISPで正式表記)。
READ = {"京セラドーム": "きょうセラドーム", "全8試合": "ぜんはちしあい"}

# (chapter, id, JP text)
# ★出典の扱い: 大手メディア・著名記者・団体公式・実名の解説者は実名で紹介する。
#   一般の海外ファンは匿名（「海外のファンからは」等）。リサーチ元＝
#   research_output/news_reactions/shaydullaev_mckee_overseas_reactions_20260910.json（ユーザー提供）
BEATS = [
    # ===== オープニング =====
    ("open", "o1", "スーパーライジンファイブのメインイベント。この試合を、いちばん大きく取り上げたのは海外でした。"),
    ("open", "o2", "ラジャブアリシェイドゥラエフがエージェーマッキーを判定さんたいゼロで下し、ライジンとピーエフエル、ふたつの団体の王座を同時に持つ選手になりました。"),
    ("open", "o3", "この動画では、海外の格闘技メディアや記者、解説者の反応をまとめてお届けします。"),

    # ===== 第1章 海外メディアの速報 =====
    ("ch1", "c1a", "試合が終わると、海外の大手メディアが一斉に速報を出しました。"),
    ("ch1", "c1b", "アメリカの全国紙ユーエスエートゥデイが運営する格闘技専門サイト、エムエムエージャンキー。アンドニューの見出しで、シェイドゥラエフがピーエフエルとライジンのフェザー級王座を同時に保持したと速報しました。"),
    ("ch1", "c1c", "ヤフースポーツが立ち上げた格闘技専門メディア、アンクラウンドは、シェイドゥラエフは無敗のまま、にじゅうせんぜんしょう。ピーエフエルとライジンの両方でベルトを持っている、と報じました。"),
    ("ch1", "c1d", "シェイドゥラエフが王座を持つアメリカの団体で、ユーエフシーに次ぐ規模とされるピーエフエル。その公式アカウントは、日本で歴史が作られたと投稿し、じゅうまんかい以上表示されています。"),
    ("ch1", "c1e", "にじゅうねん以上続く老舗のエムエムエー専門サイトで、選手の戦績データベースとしても使われているシャードッグ。記事では、ユーエフシーの外で戦う選手のなかで間違いなく最高のひとりだ、と書きました。"),
    ("ch1", "c1f", "そして、海外でもっとも影響力のあるエムエムエー記者、アリエルヘルワニ。ユーエフシーの契約や移籍のスクープを最初に報じることで知られ、日本でいえば格闘技担当の番記者の頂点にあたる存在です。"),
    ("ch1", "c1g", "おおさかのメインのあの光景はとても楽しかった。素晴らしいアイデアだ、とまず会場の演出をたたえました。"),
    ("ch1", "c1h", "そのうえでシェイドゥラエフを、疑いようもなくユーエフシーの外で最強のフェザー級だ、と評しています。"),

    # ===== 第2章 試合内容への評価 =====
    ("ch2", "c2a", "海外でもっとも拡散したのは、いちラウンドのスラムでした。"),
    ("ch2", "c2b", "ライジンの英語公式が投稿したこの場面は、ひゃくさんじゅうまんかい以上表示されています。"),
    ("ch2", "c2c", "海外のファンに広く読まれているコンバットスポーツの情報アカウント、チャンピオンシップラウンズ。シェイドゥラエフがいちラウンド早々にマッキーをスラムしたという投稿は、さんじゅうななまんかい以上表示されました。"),
    ("ch2", "c2d", "ホームオブファイトも、美しいスラムだと紹介しています。"),
    ("ch2", "c2e", "コンバットスポーツトゥデイは、シェイドゥラエフがさんラウンドを通してマッキーを支配したと伝えました。"),
    ("ch2", "c2f", "一方で、留保をつける声もあります。"),
    ("ch2", "c2g", "人気番組モーニングコンバットの司会を務めるアナリスト、ルークトーマス。技術的な分析に定評がある、日本でいえば解説者の代表格のような存在です。彼はこう書きました。シェイドゥラエフは無敵には見えない。"),
    ("ch2", "c2h", "マッキーがあれほど普段らしくなく疲れていなければ、まったく違う試合になっていた可能性がある、という見方です。"),
    ("ch2", "c2i", "その疲れの理由を、マッキー本人が試合後に明かしています。"),
    ("ch2", "c2j", "さんしゅうかんほど前に足首を脱臼してしまい、そこからしばらく走れなかった。最後の追い込みができなかったことは、少なからず影響があったと思う、と話しました。"),
    ("ch2", "c2k", "そのうえで、打撃では自分のほうが上回っていたと思うが、テイクダウンとコントロールでだいぶ押さえつけられたと振り返っています。"),
    ("ch2", "c2l", "次はアメリカで、自分たちのルールとごラウンドでやってみたい。マッキーは再戦を求めました。"),
    ("ch2", "c2m", "海外のエムエムエー解説クリエイターからは、もっと厳しい書き方も出ています。"),
    ("ch2", "c2n", "マッキーは自分が地球上で最高のフェザー級だと話していた。シェイドゥラエフは彼をスパーリングパートナーのように扱った。スラムして押さえ込み、ふたつのベルトを持って帰った、と書いています。"),

    # ===== 第3章 契約とUFC論 =====
    ("ch3", "c3a", "そして試合の直後、もうひとつのニュースが海外を駆け巡りました。"),
    ("ch3", "c3b", "ジェイクポールが共同で立ち上げたプロモーション、エムブイピーは、ことしピーエフエルと合併しました。ヘルワニが報じたのは、シェイドゥラエフがにせんにじゅうななねんいちがつから、この新体制とにねん契約を結ぶという話です。"),
    ("ch3", "c3c", "つまり当面、ユーエフシーの舞台には立たないことになります。"),
    ("ch3", "c3d", "この報道は海外で大きく広がりました。ジェイクポールはやはり動きが早い。ユーエフシーは逃した。そんな反応が並んでいます。"),
    ("ch3", "c3e", "海外のファンからは厳しい見方も出ました。ふたつのベルトを取ったのに、ユーエフシーのトップ選手であるトポリアやエヴロエフとはやらないのか。ジェイクポールのかねを取るのか、という声です。"),
    ("ch3", "c3f", "一方で、まだにじゅうごさい。経験とお金を積んでから行けばいい、という擁護もあります。"),
    ("ch3", "c3g", "夢のカードを望む投稿も目立ちました。ユーエフシーで長くフェザー級王座を守ったアレクサンダーボルカノフスキーとの一戦を見てみたい、という声です。"),
    ("ch3", "c3h", "ユーエフシーがプライドを捨てて団体をまたいだ対戦を実現しないのは残念だ、という書き込みも広がりました。"),
    ("ch3", "c3i", "シェイドゥラエフ自身は、ライジンとの契約はあと一試合残っていると話しています。今後がどうなるかは、まだ分からないという言い方です。"),

    # ===== まとめ =====
    ("close", "e1", "勝ったシェイドゥラエフは、マッキーをこう評価しました。非常にフィジカルが強く優れたファイター。打撃も組みも強かった。ただ自分のほうが強かった、と。"),
    ("close", "e2", "マッキーはフェザー級で世界最強のひとりだと思っていたので、さんラウンドをフルで戦うことを想定して練習してきた。じゅうごふんを戦い切ったのはキャリアで初めてだ、とも明かしています。"),
    ("close", "e3", "リング上ではあきもときょうま選手がおおみそかの対戦を直接うったえ、その場で決定しました。シェイドゥラエフは、戦いたいと言ってくれるなら受けて立つと応じています。"),
    ("close", "e4", "キルギス出身のにじゅうごさいが、日本のリングで海外の評価を一気に塗り替えた一夜でした。"),
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
