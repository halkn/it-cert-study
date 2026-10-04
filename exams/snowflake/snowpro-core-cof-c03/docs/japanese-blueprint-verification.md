# 日本語版の試験範囲照合

日本語受験に合わせ、2026-02-20更新の日本語版Study Guideを教材の試験範囲の正本とします。確認日は2026-10-03です。英語版の再取得・版間の同等性確認は、日本語教材の完成条件から外します。

出典IDは`exam-study-guide-c03-jpn-2026-02-20`、配布案内は[公式日本語認定ページ](https://learn.snowflake.com/en/certifications/snowpro-core-jpn-C03/)です。ユーザー提供の15ページのPDFを本文抽出・ページ表示で照合しました。配布PDFの直接URLは未確認です。提供された版より新しい日本語版の有無は確認できていないため、受験前に配布版を再確認します。

## 照合結果

p.5の配点、p.6〜10・12の全ObjectiveとTopic、その配下の種類・例・出題条件をCoverage Matrixと比較しました。Objective番号・配点・既存87 Topicの対応は一致し、2.3に不足していた2 Topicを追加しました。

| Domain | PDFページ | 配点 | Objective数 | Topic数 | 既存登録との差分 |
|---|---|---:|---:|---:|---|
| 1 | 6〜7 | 31% | 6 | 23 | なし |
| 2 | 8 | 20% | 3 | 24 | 2.3にコストセンタータグ付け・予算を追加 |
| 3 | 9 | 18% | 3 | 15 | なし |
| 4 | 10 | 21% | 4 | 14 | なし |
| 5 | 12 | 10% | 3 | 13 | なし |
| 合計 | | 100% | 19 | 89 | 2 Topic増加 |

Topic数はガイドの最上位の箇条書き単位です。下位項目は`scope`に保持します。1.4のワークロードの下位例は既存のフラットなscopeで対応し、1.4のNotebooks既定warehouseと3.2のOpenflowに付くglobal GA条件を維持します。4.1の日本語表記「クエリ属性」は既存のquery attributionに対応させ、技術的な説明はQUERY_ATTRIBUTION_HISTORYの公式文書を根拠にします。

## 範囲の確認と教材の完成を区別する

`japanese_guide_verification: verified`は、日本語版の全試験範囲を照合して登録した状態を表します。教材完成の判定は各Topic・Objectiveのstatusと`release_status`で行います。

- 2.3の追加2 Topicは本文・図・3層の演習を補完して`complete`です。[Issue #8](https://github.com/halkn/it-cert-study/issues/8)の対応としてDomain 2を再評価し、問題品質・本文限定の両レポートを保存しました。
- Domain 5の13 Topicも本文・図・3層の演習と独立評価を整備し、`complete`です。Referenceと日本語版の配点に合わせた100問の模擬セットも完成しています。教材全体は完成条件の最終確認を残す`review`です。
- 基準のsource ID・言語・更新日を変更したため、英語版基準で保存した評価は失効します。Domain 1〜5は日本語版基準で評価済みです。

PDF原本・抽出文・公式図・サンプル問題はリポジトリに複製しません。原本識別情報は出典台帳、取得不能だった経緯はVerification Logに保持します。
