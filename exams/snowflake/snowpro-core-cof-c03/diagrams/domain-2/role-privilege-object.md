# Role・privilege・objectの関係

```mermaid
flowchart LR
  U[User / service] -->|account roleをgrant| FR[Functional account role]
  AR[Access account role] -->|roleをgrant<br/>privilegeを継承| FR
  DR[Database role] -->|account roleへgrant| AR
  P[Privilege<br/>SELECT / USAGE等] -->|grant| AR
  P -->|grant| DR
  AR -->|許可された操作| O[Securable object]
  DR -->|同じdatabase内| O
  O -->|唯一のOWNERSHIP| OWNER[Owner role]
```

- Roleはprivilegeをまとめ、userへ直接objectを大量grantする代わりに使います。
- Database roleはsessionで直接activateせず、account roleへgrantして利用します。
- Object ownerがaccessを委任できる点がDAC、role経由で利用者へ届ける点がRBACです。

根拠: `docs-access-control-overview`, `docs-access-control-best-practices`
