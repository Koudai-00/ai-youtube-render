# -*- coding: utf-8 -*-
"""海外反応まとめ: 海外メディアのサイト/YouTubeチャンネル/X投稿を Playwright でキャプチャする。
   背景素材として使う（「名前だけでは規模が分からない」への対応＝実物のキャプチャで見せる）。
   出力: assets/source/episode_rizin5_overseas/media/<name>.png
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "source" / "episode_rizin5_overseas" / "media"
OUT.mkdir(parents=True, exist_ok=True)

# (name, url, kind)  kind: page=1920x1080のページ全体 / tweet=X埋め込みカード / yt=YouTubeチャンネル
TARGETS = [
    ("site_mmajunkie",  "https://mmajunkie.usatoday.com/story/sports/pfl/2026/09/10/super-rizin-5-results-razhabali-shaydullaev-beats-a-j-mckee-for-rizin-pfl-belts/91687579007/", "page"),
    ("site_sherdog",    "https://www.sherdog.com/news/news/Rajabali-Shaidullaev-improves-to-200-and-becomes-double-champ-at-Super-Rizin-5-202749", "page"),
    ("site_mmafighting","https://www.mmafighting.com/rizin/509449/super-rizin-5-results-razhabali-shaidulloev-tops-a-j-mckee-to-win-rizin-pfl-titles-mikuru-asakura-knocks-out-shinya-aoki", "page"),
    ("site_pfl",        "https://pflmma.com/", "page"),
    ("site_uncrowned",  "https://www.uncrownedcombat.com/", "page"),
    ("yt_morningkombat","https://www.youtube.com/@MorningKombat", "yt"),
    ("yt_mmajunkie",    "https://www.youtube.com/@MMAjunkie", "yt"),
    ("yt_pfl",          "https://www.youtube.com/@PFLMMA", "yt"),
    ("tw_helwani_osaka","2098034343482417650", "tweet"),
    ("tw_helwani_mvp",  "2098043333306114066", "tweet"),
    ("tw_mmajunkie",    "2098032244694642786", "tweet"),
    ("tw_mmafighting",  "2098041868454072645", "tweet"),
    ("tw_uncrowned",    "2098033029604356141", "tweet"),
    ("tw_pfl",          "2098038304683831552", "tweet"),
    ("tw_rizintv",      "2098027222061703625", "tweet"),
    ("tw_champrds_slam","2098027606276788283", "tweet"),
    ("tw_champrds_res", "2098031841378795660", "tweet"),
    ("tw_hof_slam",     "2098027820928598291", "tweet"),
    ("tw_hof_mvp",      "2098054922235216061", "tweet"),
    ("tw_cst",          "2098032093808705656", "tweet"),
    ("tw_lukethomas",   "2098030633192706073", "tweet"),
]


def main() -> int:
    log = []
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        for name, url, kind in TARGETS:
            out = OUT / f"{name}.png"
            try:
                if kind == "tweet":
                    ctx = br.new_context(viewport={"width": 1200, "height": 1400}, device_scale_factor=2,
                                         locale="en-US")
                    pg = ctx.new_page()
                    pg.goto(f"https://platform.twitter.com/embed/Tweet.html?id={url}&theme=light&width=800&lang=en",
                            wait_until="networkidle", timeout=60000)
                    time.sleep(2.5)
                    el = pg.query_selector("article") or pg.query_selector("body")
                    el.screenshot(path=str(out))
                else:
                    ctx = br.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1,
                                         locale="en-US", user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"))
                    pg = ctx.new_page()
                    pg.goto(url, wait_until="domcontentloaded", timeout=60000)
                    time.sleep(4)
                    # 同意/クッキーのダイアログを閉じる（あれば）
                    for sel in ("button:has-text('Accept')", "button:has-text('Accept all')", "button:has-text('I agree')",
                                "button:has-text('同意')", "button:has-text('すべて同意')", "#onetrust-accept-btn-handler"):
                        try:
                            b = pg.query_selector(sel)
                            if b: b.click(timeout=2000); time.sleep(1)
                        except Exception:
                            pass
                    pg.screenshot(path=str(out), full_page=False)
                ctx.close()
                log.append((name, "OK", out.stat().st_size))
                print(f"  OK  {name}", flush=True)
            except Exception as e:
                log.append((name, "NG", str(e)[:80]))
                print(f"  NG  {name}: {str(e)[:80]}", flush=True)
        br.close()
    (OUT / "_capture_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for l in log if l[1] == "OK")
    print(f"取得 {ok}/{len(TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
