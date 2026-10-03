# 何を変えて性能を改善するか

```mermaid
flowchart TD
  R["SQLの正しさとProfileを確認"] --> Q{"改善したい対象"}
  Q --> C["Eligibleな並列処理へcompute追加"]
  C --> QAS["QAS: Enterprise以上"]
  Q --> A["少数行を探す検索構造"]
  A --> SOS["Search Optimization: Enterprise以上"]
  Q --> D["頻繁な範囲filterに合うdata配置"]
  D --> CK["Clustering: Standardでも利用可能"]
  Q --> E["繰り返す単一tableの計算"]
  E --> MV["Materialized view: Enterprise以上"]
  QAS --> T["改善時間と追加creditを比較"]
  SOS --> T
  CK --> T
  MV --> T
```

候補を選ぶ図で、どれか1つだけを使う制約ではありません。検索構造でscan対象を減らし、残るeligibleな処理をQASへ渡す併用も可能です。JOINやwindowを含む任意のSQLをmaterialized viewとして保存できるわけではありません。

根拠: `docs-performance-options`, `docs-performance-storage`, `docs-query-acceleration`, `docs-materialized-views`。
