# Reference

> Status: complete

日本語版Study Guide（2026-02-20更新）に対応する、全Domainの比較・復習用資料です。本文で仕組みを学んだ後、機能を選ぶ条件や用語の違いを確認します。

| 確認したいこと | 資料 | 使い方 |
|---|---|---|
| 用語の意味と学習先 | [用語集](glossary.md) | 英語名から探し、Objectiveに対応する本文へ戻る |
| 似た機能の選定条件 | [比較表](comparison-tables.md) | 入力・目的・権限・費用・制約を比較する |
| 誤答につながる思い込み | [混同しやすい概念](exam-traps.md) | 正しい判断と、その条件を説明する |
| SQLの目的と実行条件 | [SQLコマンド集](sql-command-reference.md) | role・context・必要権限を確認して構文を読む |
| 受験前の理解確認 | [直前確認](last-minute-review.md) | 資料を閉じて説明し、説明できない項目だけ復習する |

各資料のSource IDは[出典台帳](../docs/sources.json)の公式資料を指します。確認時点は2026-10-04です。Edition・region・機能状態・既定値は利用前に公式資料で再確認してください。Referenceは技術・出典・導線の確認と検証を経て`complete`としています。本文・問題のDomain評価とは別の成果物です。

## Objectiveから本文へ戻る

用語集・比較表・SQL集のObjective欄と、次の表を対応させます。

| Domain | Objectiveと本文 |
|---|---|
| 1 | [1.1 アーキテクチャ](../textbook/domain-1/01-architecture.md) / [1.2 ツール](../textbook/domain-1/02-interfaces-and-tools.md) / [1.3 階層](../textbook/domain-1/03-object-hierarchy.md) / [1.4 Warehouse](../textbook/domain-1/04-virtual-warehouses.md) / [1.5 ストレージ](../textbook/domain-1/05-storage-concepts.md) / [1.6 AI・開発](../textbook/domain-1/06-ai-ml-app-development.md) |
| 2 | [2.1 セキュリティ](../textbook/domain-2/01-security-model.md) / [2.2 ガバナンス](../textbook/domain-2/02-data-governance.md) / [2.3 コスト](../textbook/domain-2/03-monitoring-cost.md) |
| 3 | [3.1 ロード](../textbook/domain-3/01-loading-unloading.md) / [3.2 自動取り込み](../textbook/domain-3/02-automated-ingestion.md) / [3.3 接続・Integration](../textbook/domain-3/03-connectors-integrations.md) |
| 4 | [4.1 性能評価](../textbook/domain-4/01-evaluate-query-performance.md) / [4.2 最適化](../textbook/domain-4/02-optimize-query-performance.md) / [4.3 キャッシュ](../textbook/domain-4/03-caching.md) / [4.4 変換](../textbook/domain-4/04-data-transformation.md) |
| 5 | [5.1 保護](../textbook/domain-5/01-collaboration-protection.md) / [5.2 共有](../textbook/domain-5/02-data-sharing.md) / [5.3 Listing](../textbook/domain-5/03-marketplace-listings.md) |
