# 教材・執筆ガイド

学習を始める方は、管理ファイルを読む前に [START HERE](../START_HERE.md) を参照してください。このページの後半は主に執筆者向けです。

## 学習コンテンツ

| Domain | 配点 | 教材 |
|---|---:|---|
| 1. Snowflake AI Data Cloud の機能とアーキテクチャ | 31% | [Domain 1](../textbook/domain-1/README.md) |
| 2. アカウント管理とデータガバナンス | 20% | [Domain 2](../textbook/domain-2/README.md) |
| 3. ロード、アンロード、接続 | 18% | [Domain 3](../textbook/domain-3/README.md) |
| 4. 性能最適化、クエリ、変換 | 21% | [Domain 4](../textbook/domain-4/README.md) |
| 5. データコラボレーション | 10% | [Domain 5](../textbook/domain-5/README.md) |

## 学習の進め方

1. [syllabus](syllabus.md) で目標と全体像を確認する。
2. 各 objective の章を読み、確認問題を解く。
3. Domain 演習で複数概念を組み合わせて判断する。
4. [100問の模擬試験](../exercises/mock/README.md)で総合演習し、採点後に弱点を復習する。
5. [Reference](../reference/README.md) で比較・復習する。

本文がまだ `planned` または `draft` の章は、学習完了の根拠にできません。[Coverage Matrix](coverage-matrix.md) で状態を確認してください。

## 管理情報

- `coverage-matrix.json`: 試験目標から本文・根拠・図・演習への対応
- `sources.json`: 公式資料と最終確認日
- `diagrams.json`: 自作図の目的、根拠、状態
- `mock-sets.json`: 総合模擬セットの問題ID、出題順、冊子の出力先
- `verification-log.md`: Study Guide や変更されやすい仕様の確認履歴
- [日本語版の試験範囲照合](japanese-blueprint-verification.md): 基準版、全範囲の比較結果、未実装範囲

## 模擬冊子の更新

個別の問題ファイルとセット台帳を更新した後、リポジトリルートで冊子を再生成します。

```bash
python3 scripts/build_mock_exam.py --exam exams/snowflake/snowpro-core-cof-c03 --set full-01
python3 scripts/validate_content.py --exam exams/snowflake/snowpro-core-cof-c03
```

生成された問題冊子・解答冊子も保存します。構造Validatorは問題IDの重複、配点に対応する問題数、全Objectiveの採用、冊子の更新漏れを確認します。個別の模擬問題を変えた場合は、対象Domainの独立評価も更新します。
