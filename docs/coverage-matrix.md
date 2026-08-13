# Coverage Matrix

機械可読な本体は [`coverage-matrix.json`](coverage-matrix.json) です。各 objective の `topics` が、公式 Study Guide の箇条書き単位を追跡します。公式ガイド内でさらに例や種類が列挙される場合は `scope` に保持し、欠落検知の対象にします。

## 追跡項目

- `objective_id`: Study Guide の番号
- `topics[].topic_id`: 公式トピックの安定ID
- `topics[].scope`: 公式トピック配下に列挙された機能・種類・用途
- `topics[].chapter_anchor`: 章内の対応位置
- `topics[].source_ids`, `topics[].diagram_ids`, `topics[].question_ids`: トピック単位の根拠・図・演習
- `topics[].status`, `last_verified`: トピック単位の進捗と照合日
- `chapter`: 対応する教科書
- objectiveの`status`, `last_verified`: 章全体の進捗と公式資料を最後に照合した日

問題ごとの解答根拠と追加学習資料は `questions.json` の `answer_source_ids` と `further_reading_source_ids` で区別します。

## 完了の意味

`complete` は本文ファイルが存在するだけでは設定できません。What / How / When-Why / Compare、技術根拠、必要な図、章末問題、Domain 演習、模擬試験への対応、各問題の解答根拠が揃い、レビューと自動検証を通過した状態です。

初期登録では全目標・全トピックを `planned` としています。これは試験範囲の登録完了を示すだけで、教材の coverage 完了ではありません。`planned` のトピックでは根拠・図・問題の配列を省略でき、`draft` 以降で明示的に登録します。
