# Stageの種類と権限の対応

```mermaid
flowchart LR
  L[ローカルファイル] -->|PUT| INT
  subgraph INT[Internal stage - Snowflakeが管理]
    U["User stage @~<br/>自分専用・変更不可"]
    T["Table stage @%table<br/>1 table専用・変更不可"]
    N["Named internal stage @name<br/>schema-level object"]
  end
  EXT["External stage<br/>S3 / GCS / Azure"]
  SI[Storage integration] -->|資格情報を提供| EXT

  INT -->|COPY INTO table| TB[(Table)]
  EXT -->|COPY INTO table| TB
  TB -->|COPY INTO location| EXT
  INT -->|GET| L

  N -.->|DIRECTORY = ENABLE TRUE| DIR[Directory table<br/>ファイルのmetadata]
  EXT -.->|DIRECTORY = ENABLE TRUE| DIR
```

- Privilegeは種類で異なります。External stageは`USAGE`（`READ`と`WRITE`を含む）、internal stageは`READ`と`WRITE`を個別にgrantします。
- `PUT`と`GET`はローカルとinternal stageの間だけで使い、`GET`はexternal stageに使えません。どちらもSnowsightのworksheetからは実行できません。
- Directory tableはinternal／externalの両方のstageに付けられ、ファイル本体ではなくmetadataを保持します。

根拠: `docs-create-stage`, `docs-data-load-local-create-stage`, `docs-access-control-privileges`, `docs-put`, `docs-get`, `docs-data-load-dirtables`
