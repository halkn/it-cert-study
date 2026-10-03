# 遅さの症状から調査先を選ぶ

```mermaid
flowchart TD
  Q["Query Historyで時間内訳を確認"] --> W{"待機が大きいか"}
  W -->|はい| C{"待機の種類"}
  C --> O["Overload: workload分離・scale out"]
  C --> P["Provisioning: 起動・resize設定"]
  C --> L["Transaction blocked: lock競合"]
  W -->|いいえ| N["Profileの重い処理ノード"]
  N --> S["Scan: filterとpartition数"]
  N --> J["Join: 条件・key重複・出力行数"]
  N --> M["Spill: 入力削減・batch分割・scale up"]
```

待機と処理の問題を先に分けます。scan量や行数は要件と比較し、全件scanや正しいone-to-many JOINを異常と決めつけません。QAS有効時の少量remote書き込みも、重大なspillとは限りません。

根拠: `docs-query-profile`, `docs-query-history`, `docs-memory-spillage`, `docs-query-insights`, `docs-reducing-queues`。
