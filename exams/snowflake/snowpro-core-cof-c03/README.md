# SnowPro Core COF-C03 Study Guide

SnowPro Core COF-C03 の公式試験範囲を、Snowflake 公式情報だけを根拠に学ぶための日本語教材プロジェクトです。試験問題の再現や暗記ではなく、概念の仕組み、使い分け、周辺知識まで説明できることを目標にします。

## 現在の状態

全Domainの本文・図・3層の演習と[Reference](reference/README.md)を整備しています。Issue #1の完了に向け、公式配点を考慮した模擬セット編成と教材全体の完成条件の確認を行います。教材全体のrelease_statusは`review`で、Issue #1はこの確認が終わるまでcloseしません。

この教材は、複数資格を収録する[it-cert-study](../../../README.md)内の独立した試験パッケージです。
進捗は [Coverage Matrix](docs/coverage-matrix.json) を正本とします。日本語受験向けに日本語版Study Guide（2026-02-20更新）の全試験範囲を照合・登録しています。Domain 1〜5の全19 Objective・89 Topicは`complete`です。各Domainの問題品質・本文限定評価を保存しています。詳細は[Verification Log](docs/verification-log.md)を参照してください。

## 読み始める

- **学習する方:** [START HERE](START_HERE.md)
- **執筆する方:** [教材ガイド](docs/README.md)
- [C03 syllabus](docs/syllabus.md)
- [Coverage Matrix の見方](docs/coverage-matrix.md)
- [出典ポリシー](../../../shared/policies/source-policy.md)
- [図のポリシー](../../../shared/policies/diagram-policy.md)
- [品質基準](../../../shared/policies/content-quality.md)

## 執筆・検証

章、問題、図はリポジトリの `shared/templates/` にある雛形から作成します。変更後はリポジトリルートで次を実行してください。

```bash
python3 scripts/validate_content.py --exam exams/snowflake/snowpro-core-cof-c03
```

検証は Coverage Matrix、出典台帳、図台帳、章ファイルの参照整合性を確認します。

## 免責

Snowflake、SnowPro は Snowflake Inc. の商標です。本リポジトリは Snowflake Inc. による公式教材ではありません。公式 Study Guide や公式図を転載せず、参照 URL と確認履歴を保持したうえで独自に説明・作図します。
