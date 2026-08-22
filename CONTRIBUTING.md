# Contributing

このリポジトリでは「文章がある」ことより、試験目標・根拠・図・演習を試験ごとに追跡できることを重視します。

## 基本フロー

新しい試験は `exams/<vendor>/<exam>/` に追加します。
新しいObjectiveの章と演習一式を実装するときは、対象の試験パッケージを指定してリポジトリSkill `$write-certification-chapter` を使用してください。

1. 対象試験の `docs/coverage-matrix.json` で objective を選ぶ。
2. 対象試験の `docs/sources.json` に必要な公式資料を登録し、内容と更新状態を確認する。
3. `shared/templates/chapter.md` を基に章を書く。
4. 必要な図と問題を各テンプレートから作る。
5. Coverage Matrix の参照と状態を更新する。
6. `python3 scripts/validate_content.py --exam <試験ディレクトリ>` を実行する。
7. Domain の模擬問題が揃ったら、`shared/evals/evaluation-policy.md` に従ってブラインド受験と textbook 単独 Coverage 監査を実施する。
8. 評価結果を対象試験の `evals/` へ保存し、`python3 scripts/validate_domain_evaluation.py --exam <試験ディレクトリ> --report <評価結果>` を実行する。

## 状態遷移

`planned` → `draft` → `review` → `complete`

- `planned`: 目標と置き場所だけが決まっている。
- `draft`: 本文または関連成果物が未完成。
- `review`: 必須要素が揃い、技術・出典レビュー待ち。
- `complete`: 品質基準を満たし、検証が通っている。

`complete` への直接変更は禁止です。詳しい判定は [品質基準](shared/policies/content-quality.md) に従ってください。

## 禁止事項

- Exam Dump、受験時に見た問題、非公開試験内容の投稿
- 非公式ブログや LLM の記憶だけを技術的根拠にすること
- 出典を読まずに URL だけを追加すること
- 認定団体・技術提供元の公式 Study Guide、公式図、公式文書の大量転載
- 未完成の項目を `complete` にすること
