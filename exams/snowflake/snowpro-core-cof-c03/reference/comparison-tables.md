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

## Domain 3の主要な選定軸

| 問い | 選択肢 | 判断 |
|---|---|---|
| ファイル置き場 | user／table／named internal／external stage | 個人利用／単一table／権限運用／外部storage |
| stage privilege | `USAGE`／`READ`・`WRITE` | external stage／internal stage |
| ロード形式 | 6形式（load）／3形式（unload） | CSV・JSON・AVRO・ORC・PARQUET・XML／CSV・JSON・PARQUET |
| error方針 | `ON_ERROR`／`VALIDATION_MODE`／`VALIDATE()` | 事前方針／事前検証（ロードしない）／事後調査 |
| ロード履歴 | `COPY_HISTORY`／`LOAD_HISTORY` | Snowpipeを含む／`COPY INTO`のみ |
| 取り込みの引き金 | COPY／Snowpipe／Snowpipe Streaming／Stream+Task／Dynamic Table | 手動batch／ファイル到着／行到着／変更検知＋実行／鮮度目標 |
| task compute | user-managed／serverless | 指定warehouseの稼働時間／使用compute資源 |
| pipeline記述 | Dynamic Table／Stream + Task | 宣言的・依存自動／手続き的・独自ロジック可 |
| 接続の向き | driver・connector／integration | 外部からSnowflakeへ／Snowflakeから外部へ |
| integration種別 | storage／API／security／notification／external access | storage／HTTPS endpoint／認証／通知／handlerの外向き通信 |
