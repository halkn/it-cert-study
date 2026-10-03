# 4.1 クエリ性能を評価する

> Status: complete
> Last verified: 2026-10-03

## この章で学ぶこと

- 待機と実行を分け、Query Profileから重い処理を探す。
- spill、pruning、exploding join、queueから改善の方向を判断する。
- query historyとquery attributionを使い分け、workloadを分離する理由を説明する。

## 前提知識

[1.4 Virtual Warehouse](../domain-1/04-virtual-warehouses.md)のscale up／out、[1.5 ストレージ概念](../domain-1/05-storage-concepts.md)のmicro-partition、[2.3 監視とコスト管理](../domain-2/03-monitoring-cost.md)を前提にします。JOINとGROUP BYの基本は既知とします。

## この章の用語

| 用語 | 意味 |
|---|---|
| bottleneck（ボトルネック） | 全体の速さを制約する処理や資源 |
| operator node（処理ノード） | scan、join、aggregateなど実行計画を構成する処理単位 |
| spill | メモリーに収まらない中間データをdiskへ退避すること |
| pruning | metadataから結果に不要なmicro-partitionを読み飛ばすこと |
| exploding join | JOIN後の行数が入力に比べて大きく増える状態 |
| queue | 実行を開始できず待機する状態 |
| query attribution | クエリの資源消費に基づくcompute creditの配賦 |

## 試験範囲との対応

| Topic | 本文 | 公式根拠 |
|---|---|---|
| Query Performance Tuning | [症状と観測値](#query-performance-tuning) | `docs-query-profile`, `docs-query-insights`, `docs-memory-spillage` |
| ACCOUNT_USAGE view | [履歴と配賦](#account-usage-views) | `docs-query-history`, `docs-query-attribution-history`, `docs-performance-exploring` |
| Workload management | [似た処理をまとめる](#workload-management) | `docs-warehouse-considerations`, `docs-reducing-queues` |

[登録済みCOF-C03 Syllabus](../../docs/syllabus.md)のObjective 4.1に対応します。公式Study Guideの再取得状況は[検証記録](../../docs/verification-log.md)に記載しています。

<a id="query-performance-tuning"></a>
## 遅いクエリを待機と実行に分ける

実行2秒、混雑による待機40秒のクエリでは、scanを速くしても待機40秒は解消できません。Query Historyの時間内訳から、実行を開始できない問題か、実行中の問題かを分けます。

Snowsightの **Monitoring → Query History** でquery IDを開き、**Query Profile** を確認します。処理ノードとその間を流れる行数をたどり、**Most Expensive Nodes** から時間を使う処理を探します。scanなら読み取り量、joinなら行数、aggregateやsortなら中間データ量を確認します。

**Query Insights** は非効率なfilter、行数が増大するjoin、remote spill、長いqueueなどを検出し、調査・改善を提案します。Profileの実測値を読む入口として使います。Insightがないことは最適化済みの証明ではありません。根拠: `docs-query-profile`, `docs-query-insights`。

[図: 症状から調査先を選ぶ](../../diagrams/domain-4/query-bottlenecks.md)

### spillは中間データがメモリーに収まらない兆候

JOIN、sort、aggregateには処理途中のデータを保持するメモリーが必要です。収まらないデータはlocal diskへ、さらに足りなければremote storageへ退避され、書き込みと読み戻しで遅くなります。とくにremoteへの退避は影響が大きくなります。

`bytes_spilled_to_local_storage`と`bytes_spilled_to_remote_storage`を確認し、Profileで発生ノードを探します。入力行・列の削減、小さなbatchへの分割、より大きいwarehouseによるメモリー増加を検討します。multi-clusterでclusterを増やしても、単一クエリのメモリーを複数clusterへ合算するものではありません。

QASが有効な場合、eligibleなクエリではQASを実際に使わなくても少量のremote書き込みが記録される場合があります。remote spillが非ゼロという一点で深刻なメモリー不足と断定せず、量・ノード・時間を併せて判断します。根拠: `docs-memory-spillage`。

### pruningは要件に対して読み取り範囲が狭いかを評価する

micro-partitionの列ごとの値域などのmetadataから、filterに該当し得ないpartitionを除外します。日付範囲がpartition間で分離されていれば、1日分の検索で他の日付を読み飛ばせます。

`partitions_scanned`と`partitions_total`を比べます。1,000個中20個なら読み飛ばしが働いています。狭い日付条件なのに950個を読むならfilterとデータ配置を調べます。一方、全期間集計で全partitionを読むことは要件に合う場合があります。scan比率だけで非効率と決めません。

頻繁な範囲検索でpruningが弱ければ[4.2のclustering](02-optimize-query-performance.md#clustering-keys)、特定IDで少数行を探すならSearch Optimizationが候補です。根拠: `docs-micro-partitions`。

### exploding joinは入力と出力の行数を比べる

顧客1行と注文3行を結合すれば3行になるので、正しい行数増加もあります。しかしJOIN条件の欠落、keyの重複、意図しないmany-to-many関係は、予想を超える増加を起こし、後続のsortやaggregateまで重くします。

10行と20行のtableを条件なしでcross joinすると200行になります。結合条件、keyの一意性、双方で何行が対応するかを確認します。最後にDISTINCTで重複を消しても、途中の増加や誤った集計の原因は残ります。根拠: `docs-query-insights`, `docs-joins`。

### queueは混雑・起動待ち・lockを区別する

| 観測する時間 | 意味 | 調査・対策 |
|---|---|---|
| `queued_overload_time` | warehouseの負荷による待機 | workload分離、multi-cluster、同時実行の見直し |
| `queued_provisioning_time` | 起動やresizeなどcompute準備の待機 | suspend／resumeの頻度、設定 |
| `transaction_blocked_time` | transaction lockによる待機 | 競合するtransactionや更新処理 |
| `execution_time` | クエリの実行時間 | Profileでscan、join、spillを調査 |

単一クエリは十分速く、同時利用時だけoverload queueが増えるなら、Enterprise以上のmulti-clusterによるscale outが候補です。lock待ちは競合するtransactionを調べます。根拠: `docs-query-history`, `docs-reducing-queues`。

<a id="account-usage-views"></a>
## 履歴で遅さを探し、配賦で費用を調べる

1件のProfileは個別の診断に向きます。反復クエリの傾向や利用者・warehouse別の負荷は、`SNOWFLAKE.ACCOUNT_USAGE`のviewで集計します。参照にはSNOWFLAKE databaseへの適切な権限が必要です。自身のSQL実行権限だけで全accountの履歴を読めるわけではありません。[2.3](../domain-2/03-monitoring-cost.md)のアクセス設定を確認します。

| View | 答える問い | 保持・反映の目安 |
|---|---|---|
| `QUERY_HISTORY` | 何をscanし、実行・待機に何秒使ったか | 過去365日、最大45分のlatency |
| `WAREHOUSE_LOAD_HISTORY` | warehouseの実行・queue・block状態の負荷はどれくらいか | 過去365日、最大3時間のlatency |
| `QUERY_ATTRIBUTION_HISTORY` | 実行へcompute creditがどれだけ配賦されたか | 過去365日、最大8時間のlatency |

実行直後に必ず反映されるものではありません。直後はSnowsightやInformation SchemaのQUERY_HISTORY table functionを使い、長期分析と使い分けます。Profile詳細の保持期間とACCOUNT_USAGE履歴の保持期間も別です。根拠: `docs-performance-exploring`, `docs-warehouse-load-history`, `docs-query-attribution-history`。

### 履歴のSQLで待機とspillを並べる

SNOWFLAKE databaseへの参照権限と、SELECTを実行できるwarehouseを持つroleで実行する読み取り例です。時間の単位はmillisecondなので、秒へ変換する列では1,000で割ります。

```sql
SELECT query_id, warehouse_name,
       total_elapsed_time / 1000.0 AS elapsed_seconds,
       execution_time / 1000.0 AS execution_seconds,
       queued_overload_time / 1000.0 AS overload_seconds,
       partitions_scanned, partitions_total,
       bytes_spilled_to_local_storage,
       bytes_spilled_to_remote_storage
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
  AND execution_status = 'SUCCESS'
ORDER BY total_elapsed_time DESC
LIMIT 20;
```

overloadが大きいものとexecutionが大きいものを分けます。上位1件だけでなく同じ処理の実行頻度も確認します。少し遅い処理でも数千回実行されれば、改善の効果が大きくなるためです。

### 配賦creditはwarehouse請求全体ではない

`CREDITS_ATTRIBUTED_COMPUTE`は資源消費に基づいてクエリ実行へ配賦したwarehouse compute creditです。idle時間は含まず、storage、data transfer、cloud services、ほかのserverless機能を合計した総請求でもありません。QAS分は別列`CREDITS_USED_QUERY_ACCELERATION`で扱います。

同時実行したクエリにも資源消費に基づいて配賦されるため、同じ秒数でも同じ費用とは限りません。非常に短いクエリなど、このviewに含まれないケースもあります。

```sql
SELECT query_tag, COUNT(*) AS query_count,
       SUM(credits_attributed_compute) AS attributed_compute,
       SUM(COALESCE(credits_used_query_acceleration, 0)) AS qas_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY
WHERE start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
GROUP BY query_tag
ORDER BY attributed_compute DESC;
```

QUERY_TAGは処理名などを識別するラベルです。設定されたtagで集計し、処理別の費用傾向を見ます。配賦合計とmetered creditの差を、すべて誤差と扱わないようにします。根拠: `docs-query-attribution-history`。

<a id="workload-management"></a>
## 似たworkloadをまとめ、競合する処理を分ける

短いBI問い合わせと大量のbatch変換を同じwarehouseへ混在させると、batchの資源消費でBIが待たされる場合があります。応答時間、資源量、実行頻度が似た処理をまとめ、違う性質の処理を分離します。

分離すればBIとbatchでsize、auto-suspend、scale outを別々に設定できます。同じtable dataを共有しながらcomputeを分けられます。ただしwarehouseを増やせばidle creditやcacheの分散も増え得るので、部門ごとに無条件で分けず、queueと費用を観測して選びます。根拠: `docs-warehouse-considerations`, `docs-reducing-queues`。

## 試験で重要なポイント

単一クエリのメモリー不足には入力削減やscale up、同時実行の混雑にはworkload分離やscale out、JOINの行数異常にはSQLとkeyの確認が対応します。

## 間違えやすいポイント

- scan比率が高いだけでclusteringが必要と決めない。
- attributionの合計をwarehouse請求全体とみなさない。
- size変更、cluster追加、QASを同じ対策として扱わない。

## 確認問題

- [C4-4.1-Q01: Profileで重い処理を探す](../../exercises/chapter/c4-4.1-q01.md)
- [C4-4.1-Q02: spillの意味](../../exercises/chapter/c4-4.1-q02.md)
- [C4-4.1-Q03: pruningの評価](../../exercises/chapter/c4-4.1-q03.md)
- [C4-4.1-Q04: JOIN後の行数](../../exercises/chapter/c4-4.1-q04.md)
- [C4-4.1-Q05: queueの種類](../../exercises/chapter/c4-4.1-q05.md)
- [C4-4.1-Q06: 履歴と配賦のlatency](../../exercises/chapter/c4-4.1-q06.md)
- [C4-4.1-Q07: 配賦が含まない費用](../../exercises/chapter/c4-4.1-q07.md)
- [C4-4.1-Q08: 似た処理のgrouping](../../exercises/chapter/c4-4.1-q08.md)

## 章のまとめ

履歴で待機と実行を分け、Profileで行数・scan・spillを調べます。attributionは実行へのcompute配賦を示します。観測した原因に合わせてSQL、warehouse、データ配置を改善します。

## 次に学ぶこと

[4.2 クエリ性能を最適化する](02-optimize-query-performance.md)で、診断後の機能選定を学びます。

## 根拠・関連する公式ドキュメント

- `docs-query-profile` — https://docs.snowflake.com/en/user-guide/ui-query-profile
- `docs-query-insights` — https://docs.snowflake.com/en/user-guide/query-insights
- `docs-memory-spillage` — https://docs.snowflake.com/en/user-guide/performance-query-warehouse-memory
- `docs-micro-partitions` — https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions
- `docs-query-history` — https://docs.snowflake.com/en/sql-reference/account-usage/query_history
- `docs-joins` — https://docs.snowflake.com/en/user-guide/querying-joins
- `docs-query-attribution-history` — https://docs.snowflake.com/en/sql-reference/account-usage/query_attribution_history
- `docs-warehouse-load-history` — https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_load_history
- `docs-performance-exploring` — https://docs.snowflake.com/en/user-guide/performance-query-exploring
- `docs-warehouse-considerations` — https://docs.snowflake.com/en/user-guide/warehouses-considerations
- `docs-reducing-queues` — https://docs.snowflake.com/en/user-guide/performance-query-warehouse-queue

- `exam-study-guide-c03-jpn-2026-02-20` — https://learn.snowflake.com/en/certifications/snowpro-core-jpn-C03/ （ユーザー提供の配布PDFを確認）
