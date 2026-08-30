# SnowPro Core COF-C03 Study Guide

SnowPro Core COF-C03 の公式試験範囲を、Snowflake 公式情報だけを根拠に学ぶための日本語教材プロジェクトです。試験問題の再現や暗記ではなく、概念の仕組み、使い分け、周辺知識まで説明できることを目標にします。

## 現在の状態

Issue #1 に向けた教材全体の設計基盤を整備しています。公式試験目標と配下トピックは登録済みですが、教材本文と演習は順次執筆します。この設計基盤だけでは Issue #1 の完了条件を満たさないため、関連する PR は `Refs #1` とし、全教材が完成するまで Issue を close しません。

この教材は、複数資格を収録する[it-cert-study](../../../README.md)内の独立した試験パッケージです。
進捗は [Coverage Matrix](docs/coverage-matrix.json) を Source of Truth とし、`planned` を完了とは扱いません。現在はDomain 1からDomain 3までが`complete`です。

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
