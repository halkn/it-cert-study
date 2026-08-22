# 2.3 監視とコスト管理を説明する

> Status: complete
> Last verified: 2026-08-16

## この章で学ぶこと

この章を終えると、次を説明・計算できます。

- Resource Monitorでcredit quotaに対するnotification／suspend actionを設定する
- Warehouse size、cluster数、running timeから概算creditを計算する
- Resizeとauto-suspendの課金境界を説明する
- `SNOWFLAKE.ACCOUNT_USAGE`からhistorical usageとmetadataを調べる
- 現在状態を見る`SHOW`／Information Schemaと、履歴分析を使い分ける

## 前提知識

- [1.4 Virtual Warehouse](../domain-1/04-virtual-warehouses.md)のsize、scale up／out、auto-suspend
- Creditはcomputeなどの利用量を表し、通貨costは契約上のcredit単価を掛けて求めること
- SQLの`SUM`、`GROUP BY`、date filterの基本

## この章の用語

| 用語 | この章での意味 |
|---|---|
| credit quota | Resource Monitorのfrequency interval内で100%とみなすcredit量 |
| trigger | Quota使用率がthresholdへ達したときのaction |
| suspend | 実行中queryの完了を待ってassigned warehouseを停止するaction |
| suspend immediate | 実行中queryをcancelしてassigned warehouseを直ちに停止するaction |
| metering | Resource使用量を測定しcreditとして記録すること |
| ACCOUNT_USAGE | Account内のhistorical usageとobject metadataを提供するread-only schema |
| latency | Event発生からviewへ反映されるまでの遅延 |
| retention | Historical recordを参照できる期間 |

## 試験範囲との対応

| Topic | 本文 | 主な公式根拠 |
|---|---|---|
| Resource Monitorによるcost／warehouse monitoring | [quotaとtriggerでwarehouseを制御する](#resource-monitors) | `docs-resource-monitors` |
| Virtual Warehouseのcredit使用量計算 | [rate × cluster × timeで概算する](#warehouse-credit-usage) | `docs-warehouses-overview`, `docs-warehouse-considerations` |
| ACCOUNT_USAGE schema | [履歴とmetadataをSQLで分析する](#account-usage) | `docs-account-usage`, `docs-warehouse-metering-history` |

公式ObjectiveとTopicは[COF-C03 Syllabus](../../docs/syllabus.md#23-監視とコスト管理を説明する)から公式Study Guideへ辿って確認できます。

## 予防・測定・請求を分ける

Cost管理では三つの役割を混同しないようにします。

- Resource Monitorはuser-managed warehouseのcredit usageをquotaと比較し、通知や停止を行います。
- Account Usage viewは実績を集計・分析します。
- Currencyでの請求額はmetered creditだけでなく契約単価、cloud services adjustment、serverless、storageなども関係します。

<a id="resource-monitors"></a>
## Resource Monitor — quotaとtriggerでwarehouseを制御する

Resource Monitorはcredit quota、frequency、start time、triggerを持ちます。作成後にwarehouseまたはaccountへ割り当てて初めて対象usageをmonitorします。

```sql
CREATE RESOURCE MONITOR monthly_etl_limit
  WITH CREDIT_QUOTA = 100
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS
    ON 75 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND
    ON 110 PERCENT DO SUSPEND_IMMEDIATE;

ALTER WAREHOUSE etl_wh
  SET RESOURCE_MONITOR = monthly_etl_limit;
```

75%で通知し、100%でrunning queryの完了後にwarehouseを停止し、raceや再開などで110%へ達した場合はrunning queryもcancelして即時停止します。

`CREDIT_QUOTA = 100`は100通貨単位ではありません。Credit単価を掛ける前のusage量です。Trigger thresholdはquotaに対するpercentであり、75 creditなどの絶対値ではありません。

### Account-levelとwarehouse-level

Account-level resource monitorはaccount内のuser-managed warehouse usageをmonitorします。Warehouse-level monitorは割り当てた1つ以上のwarehouseをmonitorします。Account-levelとwarehouse-levelの両方が適用される場合、いずれかのsuspend triggerに達すれば対象warehouseが停止しえます。

Resource Monitorはserverless featureのcredit usageを制御しません。Serverless costを含む全体監視にはbudgetやAccount／Organization Usageなど別の機能を検討します。

### Notifyと強制停止を選ぶ

| Action | 動作 | 向く要件 |
|---|---|---|
| `NOTIFY` | 通知するがwarehouseを停止しない | Soft threshold、早期warning |
| `SUSPEND` | Running query完了後に停止 | Query完了を優先しつつ超過を抑える |
| `SUSPEND_IMMEDIATE` | Running queryをcancelして停止 | Hard limitを優先する |

Resource Monitorのcredit accountingは即時・完全なcurrency budget保証ではありません。Notification delivery、反映timing、他serviceのusageを考慮します。

<a id="warehouse-credit-usage"></a>
## Virtual Warehouseのcredit使用量 — rate × cluster × timeで概算する

Standard warehouseのsizeが1段階上がると、一般にhourly credit rateは2倍になります。代表的なGen1 Standard warehouseのrateは次です。

| Size | 1 cluster・1時間のcredit |
|---|---:|
| X-Small | 1 |
| Small | 2 |
| Medium | 4 |
| Large | 8 |
| X-Large | 16 |

概算式は次です。

`credit = sizeのhourly rate × 稼働cluster数 × running time（時間）`

例: Mediumのwarehouseを2 clusterで30分間runningにすると、概算は`4 × 2 × 0.5 = 4 credits`です。

### 秒単位課金と最低課金

Warehouseはstart／resumeのたびに最初の60秒分がminimum chargeとなり、その後は秒単位で課金されます。30秒でsuspendしても1分相当です。90秒なら90秒相当です。

Sizeを変更すると新しいcompute resourceのprovisioningが関係します。試験計算では、各size／clusterのrunning intervalを分けてrateを掛けます。実際のmeteringは`WAREHOUSE_METERING_HISTORY`で確認します。

### Resizeとmulti-clusterのcost軸

- Scale upは1 clusterのsizeを上げ、複雑なqueryへより多いcomputeを与える。
- Scale outはcluster数を増やし、concurrencyを処理する。

Large 1 clusterを1時間なら8 credits、Medium 2 clustersを1時間なら同じく概算8 creditsです。ただし性能特性は同じではありません。前者は単一queryのcompute、後者はconcurrencyを改善する設計です。

### Currency costは別計算

Credit usageが分かってもcurrency costは確定しません。`currency cost = billed credits × contract credit price`が基本ですが、contract、cloud、region、Edition、cloud services adjustmentなどの条件を確認します。Warehouse meteringの`CREDITS_USED`をそのままinvoice amountと断定しません。

<a id="account-usage"></a>
## ACCOUNT_USAGE — 履歴とmetadataをSQLで分析する

`SNOWFLAKE.ACCOUNT_USAGE`はsystem-defined read-only `SNOWFLAKE` database内のschemaです。Accountのobject metadataとhistorical usageをviewとして提供します。

Warehouse別の当月credit usageは次のように確認できます。

```sql
SELECT
  warehouse_name,
  SUM(credits_used_compute) AS compute_credits,
  SUM(credits_used_cloud_services) AS cloud_services_credits,
  SUM(credits_used) AS total_metered_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATE_TRUNC('month', CURRENT_DATE())
GROUP BY warehouse_name
ORDER BY total_metered_credits DESC;
```

`CREDITS_USED`はcomputeとcloud servicesの合計です。Cloud services adjustmentを反映した実請求creditとは異なる場合があります。実際にbilledされた量をreconcileする場合は`METERING_DAILY_HISTORY`など目的に合うviewを使います。

### Query attributionとidleを区別する

`CREDITS_ATTRIBUTED_COMPUTE_QUERIES`はquery実行へ割り当てられたcompute creditで、warehouse idle timeを含みません。概算idle creditは次で調べられます。

```sql
SELECT
  warehouse_name,
  SUM(credits_used_compute)
    - SUM(credits_attributed_compute_queries) AS estimated_idle_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD('day', -7, CURRENT_DATE())
GROUP BY warehouse_name;
```

この差が大きい場合、auto-suspend、workload grouping、warehouse分離を調べます。Adaptive Warehouseなど列が`NULL`になる条件は公式viewのusage noteを確認します。

### ACCOUNT_USAGEのlatencyを前提にする

Account Usage viewにはdata latencyがあります。`WAREHOUSE_METERING_HISTORY`は多くの列で最大3時間、cloud services列はさらに長い場合があります。Thresholdに達した瞬間の即時制御にはResource Monitorを使い、Account Usageは履歴分析へ使います。

Retentionもviewごとに異なります。`WAREHOUSE_METERING_HISTORY`は最大365日です。すべてのAccount Usage viewが同じlatency／retentionではないため、個別referenceを確認します。

### SHOW・Information Schema・ACCOUNT_USAGE

| 情報源 | 主な用途 |
|---|---|
| `SHOW` command | 現在のobject状態を素早く確認。Warehouse不要のcommandもある |
| Information Schema | Database scopeのcurrent metadataやtable function |
| `SNOWFLAKE.ACCOUNT_USAGE` | Account scopeのhistorical usage／metadata。Latencyあり |
| `SNOWFLAKE.ORGANIZATION_USAGE` | Organization内の複数accountを横断する履歴 |

## Mini hands-on — 1週間のwarehouse usageを調べる

実行には`SNOWFLAKE.ACCOUNT_USAGE`を参照できるroleが必要です。Warehouse別にdaily usageを集計します。

```sql
SELECT
  DATE_TRUNC('day', start_time) AS usage_day,
  warehouse_name,
  SUM(credits_used_compute) AS compute_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
GROUP BY usage_day, warehouse_name
ORDER BY usage_day, compute_credits DESC;
```

結果が直近数時間を含まなくてもquery failureとは限りません。View latencyを確認してから、missing usageか反映待ちかを判定します。

## Compare — cost要件から機能を選ぶ

| 要件 | 選ぶ機能／情報 |
|---|---|
| 75%でwarningし100%でwarehouse停止 | Resource Monitor trigger |
| 全serverless serviceを含むcurrency budget | Budget／usage viewと契約単価。Resource Monitorだけではない |
| Warehouse別の過去1か月creditを集計 | `WAREHOUSE_METERING_HISTORY` |
| 現在のresource monitor割当を確認 | `SHOW RESOURCE MONITORS` |
| 複数accountのusageを横断 | `ORGANIZATION_USAGE` |
| Queryに使われずidleだったcomputeを概算 | Metered computeからquery-attributed computeを引く |

## 試験で重要なポイント

- Resource Monitorは作成後、accountまたはwarehouseへ割り当てる。
- Trigger thresholdはcredit quotaに対するpercentageである。
- `SUSPEND`はrunning query完了を待ち、`SUSPEND_IMMEDIATE`はcancelする。
- Warehouse creditはrate × cluster × running timeで概算する。
- Account Usageにはlatencyがあり、即時制御より履歴分析に向く。

## 間違えやすいポイント

- Resource Monitorをcurrency budgetまたは全serverless usageのmonitorとみなさない。
- Multi-clusterではrunning clusterごとにcreditを消費する。
- `CREDITS_USED`とinvoice上のbilled creditsが常に同じとは限らない。
- Account Usage viewごとのlatencyとretentionを同一と仮定しない。
- `CREDITS_ATTRIBUTED_COMPUTE_QUERIES`にはwarehouse idle timeが含まれない。

## 確認問題

- [C2-2.3-Q01: Resource Monitor](../../exercises/chapter/c2-2.3-q01.md)
- [C2-2.3-Q02: Warehouse credit計算](../../exercises/chapter/c2-2.3-q02.md)
- [C2-2.3-Q03: ACCOUNT_USAGE](../../exercises/chapter/c2-2.3-q03.md)

## 章のまとめ

- Resource Monitorはquotaに対するthreshold actionでuser-managed warehouseを制御する。
- Credit計算ではsize rate、active cluster数、各running intervalを分ける。
- Currency costを求めるにはbilled creditと契約単価が必要である。
- Account Usageは履歴分析に使い、view固有のlatency／retentionを前提にする。

## 次に学ぶこと

[Domain 3: データのロード、アンロード、接続](../domain-3/README.md)では、costとsecurityを考慮しながらdataをSnowflakeへ出し入れする方式を学びます。

## 根拠・関連する公式ドキュメント

- `docs-resource-monitors` — https://docs.snowflake.com/en/user-guide/resource-monitors
- `docs-warehouses-overview` — https://docs.snowflake.com/en/user-guide/warehouses-overview
- `docs-warehouse-considerations` — https://docs.snowflake.com/en/user-guide/warehouses-considerations
- `docs-account-usage` — https://docs.snowflake.com/en/sql-reference/account-usage
- `docs-warehouse-metering-history` — https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history
