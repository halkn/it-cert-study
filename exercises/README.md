# 演習

演習は次の 3 層で管理します。

- `chapter/`: 1 objective の理解確認
- `domain/`: 同一 Domain 内の複数概念を組み合わせる判断問題
- `mock/`: 公式配点を考慮した総合模擬試験

問題は [question template](../templates/question.md) の全項目を満たし、ID を Coverage Matrix に登録します。空ディレクトリの代わりに各層の README を置き、問題作成時にファイルを追加します。

問題の機械可読なメタデータは `docs/questions.json` に登録します。必須項目は `id`、`layer`、`objective_ids`、`question_type`、`required_selections`、`file`、`status`、`answer_source_ids`、`further_reading_source_ids` です。Domain／模擬問題では `objective_ids` に複数の目標を指定できます。
