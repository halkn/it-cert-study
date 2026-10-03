# データ保護手段の選定

> Status: complete
> Last verified: 2026-10-03

```mermaid
flowchart TD
  R[必要な結果] --> H[保持期間内の過去状態]
  H --> TT[Time Travel 検索・履歴clone・UNDROP]
  R --> C[独立して変更する開発用データ]
  C --> CL[Clone 作成後は相互に同期しない]
  R --> S[他accountに最新データの読取りを許可]
  S --> SH[Secure Data Sharing]
  R --> B[別regionで業務を継続]
  B --> REP[Replicationでsecondaryを更新]
  REP --> FG[Failover groupでprimaryへ昇格]
  TT --> E[Time Travel終了]
  E --> FS[PermanentはFail-safe Snowflakeによる最終復旧]
```

Time TravelからFail-safeへの矢印は標準permanent tableの履歴ライフサイクルです。Transient／temporaryはFail-safeを持ちません。Failoverと他のaccount objectの複製はBusiness Critical以上です。

## 根拠

- `docs-time-travel` — https://docs.snowflake.com/en/user-guide/data-time-travel
- `docs-fail-safe` — https://docs.snowflake.com/en/user-guide/data-failsafe
- `docs-clone-storage` — https://docs.snowflake.com/en/user-guide/tables-storage-considerations
- `docs-replication-bcdr` — https://docs.snowflake.com/en/user-guide/replication-intro
- `docs-secure-sharing` — https://docs.snowflake.com/en/user-guide/data-sharing-intro
