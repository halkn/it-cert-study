# 費用の分類・予測・停止

> Status: complete
> Last verified: 2026-10-03

```mermaid
flowchart TD
  R[専用warehouseなどのresource] --> T[Object tagと部門値]
  Q[共有applicationのquery] --> QT[QUERY_TAGでqueryごとに分類]
  T --> A[Usage viewと対応させ部門へ費用帰属]
  QT --> A
  T --> B[対応objectをcustom budgetの対象に選ぶ]
  B --> F[UTC暦月のcredit超過を予測して通知]
  W[User-managed warehouseのcredit quota] --> M[Resource Monitor]
  M --> S[通知 または停止action]
```

Tagは分類metadataです。費用の測定はusage view、超過予測はBudget、warehouseの組み込み停止actionはResource Monitorが担当します。Budgetのlimit設定だけでは停止しません。別途custom actionとprocedureを設定すれば処理を追加できます。

## 根拠

- `docs-cost-attributing` — https://docs.snowflake.com/en/user-guide/cost-attributing
- `docs-budgets` — https://docs.snowflake.com/en/user-guide/budgets
- `docs-resource-monitors` — https://docs.snowflake.com/en/user-guide/resource-monitors
- `docs-budget-custom-actions` — https://docs.snowflake.com/en/user-guide/budgets/custom-actions
