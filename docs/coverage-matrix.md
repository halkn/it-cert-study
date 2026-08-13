# Coverage Matrix

機械可読な本体は [`coverage-matrix.json`](coverage-matrix.json) です。1 行に相当する各 object が、1 つの公式試験目標を追跡します。

## 追跡項目

- `objective_id`: Study Guide の番号
- `chapter`: 対応する教科書
- `technical_source_ids`: `sources.json` の公式技術根拠
- `diagram`: 必要性と `diagrams.json` の ID
- `chapter_question_ids`, `domain_question_ids`, `mock_question_ids`: 各演習層
- `answer_source_ids`, `further_reading_source_ids`: 解答根拠と追加学習の区別
- `status`: `planned` / `draft` / `review` / `complete`
- `last_verified`: 内容と公式資料を最後に照合した日

## 完了の意味

`complete` は本文ファイルが存在するだけでは設定できません。What / How / When-Why / Compare、技術根拠、必要な図、章末問題、Domain 演習、模擬試験への対応、各問題の解答根拠が揃い、レビューと自動検証を通過した状態です。

初期登録では全目標を `planned` としています。これは試験範囲の登録完了を示すだけで、教材の coverage 完了ではありません。
