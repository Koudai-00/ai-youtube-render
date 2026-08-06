# ai-youtube-render

格闘ニュースラボ動画を **GitHub Actions で直列（継ぎ目なし）レンダー**する専用リポジトリ。
ローカルPCのスペック不足を回避し、無料枠内で焼き上げる。

## 仕組み
- `episodes/<name>/index.html` は **textfx・タイムライン(DATA)を埋め込み済みの自己完結HTML**。`assets/` を相対参照。
- Actions が `hyperframes render` で**窓分割なしのフル1本**を描画 → ナレ＋単一BGM＋loudnorm → `final.mp4`。
- 成果物は **Actions artifact** と **Releases**（`<name>-<hash>.mp4`）に保存。

## 使い方
1. GitHub の **Actions タブ → render → Run workflow** で `episode`（既定 `rizin54-yosou`）を指定して実行。
2. 完了後、そのRunの **Artifacts**、または **Releases** から `final.mp4` をDL。

## 無料枠を守る設計
- **手動起動のみ**（`workflow_dispatch`）。push では走らない。
- **内容ハッシュでスキップ**：`episodes/<name>/` の中身が前回と同一なら、既存 release を返すだけで**再レンダーしない**（分数消費ゼロ）。中身を変えた時だけ1回焼く。
- `concurrency` で同一エピソードの多重起動を防止。
- **レンダー前のQA（レイアウト/字幕/重なり/ナレ一致）は必ずローカルの静止画・プレビューで済ませてから**push する（本番レンダーは“最後の焼き上げ”一発）。

## 新エピソードの追加
`AI_YouTube/hyperframes/templates/<template>/` を `episodes/<name>/` へコピーしてcommit/push → Actionsで実行。
（源泉素材・`.env`・APIキーはこのリポジトリに置かない。）
