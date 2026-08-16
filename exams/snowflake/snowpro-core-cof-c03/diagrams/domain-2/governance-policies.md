# Governance policyの適用単位

```mermaid
flowchart TD
  Q[Query] --> T[Table / View]
  T --> RAP[Row access policy<br/>返すrowを判定]
  T --> PP[Privacy policy<br/>differential privacy]
  T --> C[Column]
  C --> MP[Masking policy<br/>返す値を変換]
  TAG[Tag + value<br/>分類・属性] -->|object / columnへ付与| T
  TAG --> C
  TAG -->|tag-based policy| MP
  RAP --> R[許可された結果]
  PP --> R
  MP --> R
```

- Row access policyは行、masking policyは列値、privacy policyは個人の情報推測リスクを制御します。
- Tagは分類用metadataであり、単独ではrowをfilterしたり値をmaskしたりしません。

根拠: `docs-column-security`, `docs-row-access-policies`, `docs-object-tagging`, `docs-differential-privacy`
