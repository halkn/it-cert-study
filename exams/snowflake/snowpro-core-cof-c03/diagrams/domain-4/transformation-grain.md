# GROUP BYとwindow計算の出力粒度

```mermaid
flowchart LR
  A["A: 100<br/>A: 200<br/>B: 50"] --> G["GROUP BY customer<br/>SUM(amount)"]
  G --> GO["A: 300<br/>B: 50<br/>顧客ごとに1行"]
  A --> W["SUM(amount) OVER<br/>PARTITION BY customer"]
  W --> WO["A: 100, 合計300<br/>A: 200, 合計300<br/>B: 50, 合計50<br/>明細行を残す"]
  WO --> Q["QUALIFYで<br/>window計算後に絞る"]
```

PARTITION BYはwindow計算のgroupを作る指定で、table storageのmicro-partitionを操作する指定ではありません。window内のORDER BYも最終結果の返却順とは別です。

根拠: `docs-aggregate-functions`, `docs-window-functions`, `docs-qualify`。
