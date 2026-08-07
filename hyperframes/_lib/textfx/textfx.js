/* ============================================================
   textfx.js — 動画用テキスト「アニメーション」登録ライブラリ（再利用）
   GSAP前提・seek安全（全て paused timeline tl に時刻 t で tween を積む）。
   使い方: TextFX.charRise(tl, el, t, {dur, stagger}); など。退場は TextFX.exit。
   HyperFramesルール順守: gsapのみ/同要素同プロパティ多重禁止/exitはオーバーレイのみ可。
   ============================================================ */
(function () {
  const g = () => window.gsap;

  // 文字を span.tfx-ch に分割（インラインブロック）。空白は保持。1回だけ実行。
  function splitChars(el) {
    if (el.__tfxSplit) return el.__tfxChars;
    const text = el.textContent;
    el.textContent = "";
    const chars = [];
    for (const ch of text) {
      const s = document.createElement("span");
      s.className = "tfx-ch";
      s.style.display = "inline-block";
      s.style.whiteSpace = "pre";
      s.textContent = ch;
      el.appendChild(s);
      if (ch !== " " && ch !== "　") chars.push(s);
    }
    el.__tfxSplit = true; el.__tfxChars = chars;
    return chars;
  }

  const TextFX = {
    // 文字が下からせり上がり（スタッガー）
    charRise(tl, el, t, o = {}) {
      const ch = splitChars(el); const tl2 = g();
      tl.fromTo(el, { opacity: 1 }, { opacity: 1, duration: 0.01 }, t);
      tl.fromTo(ch, { yPercent: 120, opacity: 0 },
        { yPercent: 0, opacity: 1, duration: o.dur || 0.5, ease: o.ease || "back.out(1.6)", stagger: o.stagger || 0.035 }, t);
    },
    // 文字がスケールでポップ
    charPop(tl, el, t, o = {}) {
      const ch = splitChars(el);
      tl.fromTo(ch, { scale: 0.2, opacity: 0 },
        { scale: 1, opacity: 1, duration: o.dur || 0.45, ease: o.ease || "back.out(2)", stagger: o.stagger || 0.03 }, t);
    },
    // 左→右クリップワイプ表示
    wipe(tl, el, t, o = {}) {
      tl.fromTo(el, { clipPath: "inset(0 100% 0 0)", opacity: 1 },
        { clipPath: "inset(0 0% 0 0)", duration: o.dur || 0.8, ease: o.ease || "power4.out" }, t);
    },
    // 下からマスク表示（行が立ち上がる）
    riseMask(tl, el, t, o = {}) {
      tl.fromTo(el, { clipPath: "inset(110% 0 0 0)", yPercent: 18, opacity: 1 },
        { clipPath: "inset(0% 0 0 0)", yPercent: 0, duration: o.dur || 0.6, ease: o.ease || "power3.out" }, t);
    },
    // ふわっと上昇フェード
    fadeUp(tl, el, t, o = {}) {
      tl.fromTo(el, { y: o.y || 40, opacity: 0 },
        { y: 0, opacity: 1, duration: o.dur || 0.5, ease: o.ease || "power3.out" }, t);
    },
    // スケールポップ（要素全体）
    scalePop(tl, el, t, o = {}) {
      tl.fromTo(el, { scale: o.from || 0.6, opacity: 0 },
        { scale: 1, opacity: 1, duration: o.dur || 0.5, ease: o.ease || "back.out(1.7)" }, t);
    },
    // インパクトのあるスラム（大→等倍＋ブラー）
    slam(tl, el, t, o = {}) {
      tl.fromTo(el, { scale: o.from || 1.5, opacity: 0 },
        { scale: 1, opacity: 1, duration: o.dur || 0.42, ease: o.ease || "power3.out" }, t);
      blurTween(tl, el, t, o.blur || 16, o.dur || 0.42);
    },
    // ブラーイン（焦点が合う）
    blurIn(tl, el, t, o = {}) {
      tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: (o.dur || 0.5) * 0.8, ease: "power1.out" }, t);
      blurTween(tl, el, t, o.blur || 18, o.dur || 0.5);
    },
    // ライトスピード（斜めスライドイン）
    lightspeed(tl, el, t, o = {}) {
      tl.fromTo(el, { x: o.x || 140, skewX: -22, opacity: 0 },
        { x: 0, skewX: 0, opacity: 1, duration: o.dur || 0.5, ease: o.ease || "power3.out" }, t);
    },
    // 下線スイープ（.tfx-uline 等の幅0→width）
    underline(tl, el, t, width, o = {}) {
      tl.fromTo(el, { width: 0 }, { width: width, duration: o.dur || 0.5, ease: o.ease || "power2.out" }, t);
    },
    // ゴールド等のグラデにシャイン走らせ（要素は background-size:230% 100% 想定）
    shine(tl, el, t, o = {}) {
      tl.fromTo(el, { backgroundPositionX: "120%" }, { backgroundPositionX: "-20%", duration: o.dur || 1.0, ease: "power1.inOut" }, t);
    },
    // オーバーレイ退場（カード等のみ可。シーン遷移には使わない）
    exit(tl, el, t, o = {}) {
      tl.to(el, { opacity: 0, y: o.y || -12, duration: o.dur || 0.35, ease: "power1.in" }, t);
    },
  };

  // filterブラーをオブジェクトproxyでtween（seek時もonUpdateで反映）。完了でinline filterを消し、CSSクラスのfilterを復帰。
  function blurTween(tl, el, t, from, dur) {
    const p = { b: from };
    tl.to(p, {
      b: 0, duration: dur, ease: "power2.out",
      onUpdate() { el.style.filter = "blur(" + p.b.toFixed(2) + "px)"; },
      onComplete() { el.style.filter = ""; },
      onReverseComplete() { el.style.filter = "blur(" + from + "px)"; },
    }, t);
  }

  window.TextFX = TextFX;
})();
