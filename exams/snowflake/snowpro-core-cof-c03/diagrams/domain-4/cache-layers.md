# 保存結果・metadata・local dataの違い

```mermaid
flowchart TD
  SQL["SQL"] --> R{"保存結果の再利用条件"}
  R -->|再利用される| OUT["保存した結果を返す"]
  R -->|再利用しない| META["Metadata: 読むpartition等を判断"]
  META --> DATA["Warehouseでdataを処理"]
  LOCAL["Warehouse local cacheのtable data"] --> DATA
  REMOTE["Remote storageのtable data"] --> DATA
  DATA --> NEW["新しい結果を生成"]
  SUSPEND["Warehouse suspend"] --> DROP["Local data cacheを破棄"]
```

理解のために処理を簡略化しています。metadataだけで答えられる処理もあります。suspendは保存結果やmetadataを同時に削除する命令ではありません。USE_CACHED_RESULTは保存結果の再利用を制御します。

根拠: `docs-persisted-results`, `docs-warehouse-cache`, `docs-micro-partitions`, `docs-count`。
