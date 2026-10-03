# Providerとconsumerの許可境界

> Status: complete
> Last verified: 2026-10-03

```mermaid
flowchart LR
  subgraph P[Provider account]
    O[公開table・secure view] -->|object権限| S[Share]
    PS[元データstorage]
  end
  S -->|consumer accountを許可| I[Consumerのimported database]
  I -->|IMPORTED PRIVILEGES またはdatabase role| R[Consumerのaccount role]
  R -->|warehouseでquery| W[Consumerがquery creditを負担]
  S --> RA[Providerが管理するreader account]
  RA --> RW[Readerのquery creditはproviderが負担]
```

同一regionの通常共有ではconsumerに共有データの物理コピーを保存しません。Imported objectは読取り専用です。Readerは作成providerのデータだけを利用します。

## 根拠

- `docs-secure-sharing` — https://docs.snowflake.com/en/user-guide/data-sharing-intro
- `docs-sharing-provider` — https://docs.snowflake.com/en/user-guide/data-sharing-provider
- `docs-sharing-consumer` — https://docs.snowflake.com/en/user-guide/data-share-consumers
- `docs-reader-accounts` — https://docs.snowflake.com/en/user-guide/data-sharing-reader-create
