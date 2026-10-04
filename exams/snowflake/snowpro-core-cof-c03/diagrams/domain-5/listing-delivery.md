# Listingの製品と利用経路

> Status: complete
> Last verified: 2026-10-03

```mermaid
flowchart TD
  S[Share データ] --> L[Listing 説明・公開先・利用条件]
  P[Application package logicと必要なデータ] --> L
  L --> PV[Private 指定consumer]
  L --> PB[Public Marketplaceで発見]
  PV --> C[条件を満たしたconsumer]
  PB --> C
  C --> D[データ製品 imported databaseをquery]
  C --> A[App製品 consumer accountへinstall]
  L --> X[別region Auto-fulfillmentでSSAへ配送・refresh]
```

Private／publicは公開先、free／trial／paidはアクセス条件です。別region配送には時間と費用が必要です。Appのinstallとconsumerデータへの許可は別です。

## 根拠

- `docs-listings` — https://docs.snowflake.com/en/collaboration/collaboration-listings-about
- `docs-auto-fulfillment` — https://docs.snowflake.com/en/collaboration/provider-listings-auto-fulfillment
- `docs-native-app-framework` — https://docs.snowflake.com/en/developer-guide/native-apps/native-apps-about
