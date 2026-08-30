# 取り込み方式の選定

```mermaid
flowchart TD
  Q{取り込みの引き金は何か} --> F[Stageへのファイル到着]
  Q --> R[Applicationからの行の到着]
  Q --> C[既存tableの変更]
  Q --> S[時刻・先行処理の完了]
  Q --> D[結果の鮮度目標]

  F --> F1{継続的か}
  F1 -->|継続| SP[Snowpipe<br/>serverless compute<br/>順序保証なし]
  F1 -->|バッチ| CP[COPY INTO table<br/>user-managed warehouse]

  R --> SS[Snowpipe Streaming<br/>行単位・channel]
  C --> ST[Stream<br/>offsetで変更を返す]
  ST --> TK
  S --> TK[Task<br/>SCHEDULE / AFTER]
  D --> DT[Dynamic Table<br/>TARGET_LAG]
```

- Snowpipeとbulk `COPY INTO`の差はcomputeの担い手と課金であり、どちらもファイル単位で取り込みます。
- Streamは変更を返すだけで実行しません。実行はTaskが担うため、この2つは組で使います。
- Dynamic Tableは引き金を鮮度目標として宣言し、refreshの順序と実行をSnowflakeへ委ねます。

根拠: `docs-data-load-overview`, `docs-snowpipe-intro`, `docs-snowpipe-streaming-overview`, `docs-streams-intro`, `docs-tasks-intro`, `docs-dynamic-tables`
