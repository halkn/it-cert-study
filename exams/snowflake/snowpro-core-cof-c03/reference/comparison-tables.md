# Comparison Tables

> Status: draft

類似機能の目的、入力、遅延、compute、管理方式、制約を同じ軸で比較します。

## Domain 1の主要な選定軸

| 問い | 選択肢 | 判断 |
|---|---|---|
| 操作場所 | Snowsight／CLI／VS Code | browser探索／自動化／IDE開発 |
| warehouse拡張 | scale up／scale out | single query resource／concurrency queue |
| 短期data | temporary／transient | session限定／明示dropまで |
| query abstraction | standard／materialized／secure view | 参照時計算／結果保持／privacy属性 |
| external data | external／Iceberg table | stage file read-only／open table format |
| AI question | AI Functions／Search／Analyst | row task／unstructured retrieval／structured text-to-SQL |
| 開発成果物 | Notebook／Streamlit／Snowpark | 実験／web app／language API processing |
