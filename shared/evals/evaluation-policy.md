# Domain教材評価ポリシー

このポリシーは、認定試験教材の各Domainについて、問題そのものの品質と、textbookだけで問題を解けるCoverageを再現可能な手順で評価するためのものです。

## 評価を実施する時点

対象Domainのtextbook、章末問題、Domain演習、模擬問題が揃い、構造検証が成功した後に実施します。問題またはtextbookを変更した場合は、保存済み評価のcontent hashを再検証し、不一致なら再評価します。

## 1. 問題品質のブラインド受験

目的は、正解位置や不自然な誤答ではなく、要件と技術知識から解答できるかを確認することです。

- 現在利用可能な汎用モデルのうち、最軽量のモデルを使う。
- 利用可能な最低のreasoning effortを使う。
- 問題文と選択肢だけを渡す。
- 正解、解説、question registry、git diffは全回答確定まで渡さない。
- 全回答確定後に採点する。
- 誤答、低確信度、複数解釈、不自然なdistractor、正解位置から推測できた問題を記録する。

入力には`shared/evals/question-quality-prompt.md`と、`scripts/build_blind_exam.py`が生成するanswer-free bundleを使います。

## 2. textbook単独Coverage監査

目的は、モデルの事前知識ではなく、教材本文に正答と誤答除外の判断材料があるかを確認することです。

- 許可する資料は対象Domainの`textbook/domain-<n>/*.md`と、正解より前だけを含む模擬問題に限定する。
- 公式Web、問題解説、question registry、他の教材を根拠にしない。
- 各問にtextbookファイル、見出し、正解を支える説明を記録する。
- 誤答を除外できるかを明示する。
- 根拠箇所を提示できない場合は、回答が正しくても`missing`とする。
- 正解の一部だけを説明できる場合、または誤答除外に本文外の知識が必要な場合は`partial`とする。
- 正解と誤答除外の両方を本文で説明できる場合だけ`sufficient`とする。

入力には`shared/evals/textbook-only-prompt.md`と、`scripts/build_blind_exam.py --mode textbook-only`が生成するbundleを使います。

## 合格基準

- 総合正答率: 80%以上
- 各Domain正答率: 70%以上
- textbook根拠十分率: 90%以上
- 解釈により正解が変わる問題: 0件
- Markdown、question registry、必要選択数の不一致: 0件

複数Domainを一度に評価する場合も、各Domainの正答率を個別に満たす必要があります。

## 評価記録

結果は対象試験の`evals/`にJSONで保存し、`shared/templates/domain-evaluation-report.json`の構造に従います。少なくとも次を記録します。

- 評価日、モデルID、reasoning effort
- Git revisionとworking tree状態
- 対象Domainと問題ID
- 許可した教材path
- 問題ごとの回答、確信度、根拠、曖昧性
- 合計とDomain別の正答率
- textbook根拠十分率
- textbook、問題、Coverage Matrixのcontent hash

`question-quality`評価では`textbook_evidence_percent`を`null`とし、問題とCoverage Matrixのhashを検証します。`textbook-only`評価では問題ごとの`evidence_status`とtextbook hashも必須です。

自由記述の会話ログだけを合格記録として扱いません。

## content hashによる失効

`validate_domain_evaluation.py`は、pathとfile contentを安定した順序でSHA-256へ含めます。Coverage Matrixは評価対象Domainの配点・Objective・Topicと、公式Study Guideを識別する試験metadataだけを正規化してhash化するため、別Domainの追加だけでは既存評価を失効させません。次のいずれかが保存値と異なれば評価は失効します。

- 対象Domainのtextbook
- 評価対象の模擬問題
- `docs/coverage-matrix.json`

モデルが廃止された場合でも過去結果は履歴として残せますが、新しいDomainの評価では、その時点で利用可能な最軽量モデルと実際のmodel IDを記録します。
