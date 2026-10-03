# 2.3 監視とコスト管理を説明する

> Status: complete
> Last verified: 2026-10-03

## この章で学ぶこと

この章を終えると、次を説明・計算できます。

- Resource Monitorでcredit quotaに対するnotification／suspend actionを設定する
- Warehouse size、cluster数、running timeから概算creditを計算する
- Resizeとauto-suspendの課金境界を説明する
- `SNOWFLAKE.ACCOUNT_USAGE`からhistorical usageとmetadataを調べる
- 現在状態を見る`SHOW`／Information Schemaと、履歴分析を使い分ける
- 専用warehouse、共有warehouse、共有applicationごとに費用の帰属方法を選ぶ
- Budgetの月次予測通知とResource Monitorの停止actionを使い分ける

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
| コストセンター（cost center） | 費用を帰属させる部門・プロジェクトなどの単位 |
| オブジェクトタグ（object tag） | Objectへ分類名と文字列値を関連付けるmetadata |
| クエリタグ（QUERY_TAG） | 個々のqueryを識別・分類するsession parameter |
| 予算（Budget） | Accountまたは対象object群のcredit使用量を月次limitと比較し、超過予測を通知する機能 |
| APPLYBUDGET | Objectやtagをcustom budgetへ追加・削除するためのprivilege |

## 試験範囲との対応

| Topic | 本文 | 主な公式根拠 |
|---|---|---|
| Resource Monitorによるcost／warehouse monitoring | [quotaとtriggerでwarehouseを制御する](#resource-monitors) | `docs-resource-monitors` |
| Virtual Warehouseのcredit使用量計算 | [rate × cluster × timeで概算する](#warehouse-credit-usage) | `docs-warehouses-overview`, `docs-warehouse-considerations` |
| ACCOUNT_USAGE schema | [履歴とmetadataをSQLで分析する](#account-usage) | `docs-account-usage`, `docs-warehouse-metering-history` |
| コストセンタータグ付け | [部門へ費用を帰属させる](#cost-center-tagging) | `docs-cost-attributing`, `docs-object-tagging-work` |
| 予算 | [月次credit超過を予測する](#budgets) | `docs-budgets`, `docs-custom-budgets` |

公式ObjectiveとTopicは[COF-C03 Syllabus](../../docs/syllabus.md#23-監視とコスト管理を説明する)から公式Study Guideへ辿って確認できます。

## 予防・測定・請求を分ける

Cost管理では分類、測定、予測、停止、請求を分けます。

- Resource Monitorはuser-managed warehouseのcredit usageをquotaと比較し、通知や停止を行います。
- Tagは費用を部門などへ帰属させる分類情報です。
- Account Usage viewは実績を集計・分析します。
- Budgetは対象のcredit使用量を集め、月末までの超過を予測して通知します。
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
| Serverlessを含む月次creditの超過予測を通知 | Account budget、または対応objectを選ぶcustom budget |
| 部門別にcomputeを帰属・集計 | Object tag／QUERY_TAGとusage view |
| Currencyの請求額を分析 | Billed usageと契約単価、storageなどの費用。Budgetのlimitはcredit |
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

<a id="cost-center-tagging"></a>
## コストセンタータグ付け — 部門へ費用を帰属させる

Account全体のcreditだけでは、どの部門のworkloadを改善すべきか分かりません。費用を負担する部門やprojectをコストセンター（cost center）として定義し、resourceやuserへ分類情報を付けて使用履歴と対応させます。これがcost attributionです。部門へ利用量を見せるshowbackや、部門へ費用を配賦するchargebackに使います。

Object tagはschema内に定義するobjectで、割当先ごとに文字列の値を持ちます。`cost_center = 'finance'`なら、`cost_center`が分類名、`finance`が帰属先です。Tag自体は使用量を測定せず、warehouseを停止したりSQLの参照権限を与えたりもしません。[2.2のobject tagging](02-data-governance.md#object-tagging)と同じ仕組みを、費用分類へ使っています。

### 専用resourceと共有resourceでは帰属の粒度が異なる

| 使用形態 | 分類する対象 | 使用量の根拠と境界 |
|---|---|---|
| 部門専用warehouse | Warehouseへobject tag | `TAG_REFERENCES`と`WAREHOUSE_METERING_HISTORY`をobject IDで結合。Warehouse全体のcomputeを帰属できる |
| 複数部門のuserが同じwarehouseを使う | Userへobject tag | User名で`QUERY_ATTRIBUTION_HISTORY`と対応させ、userのquery computeを部門別に集計する |
| 同じapplication userが複数部門のSQLを実行する | Queryごとの`QUERY_TAG` | `QUERY_ATTRIBUTION_HISTORY`のquery tagで分類する。Userやwarehouseの固定tagだけでは部門を区別できない |

Queryへ帰属したcomputeにはwarehouseのidle時間が含まれません。共有warehouseの全使用量を部門へ配賦する場合は、idleをquery使用量の比率で按分するなど、組織としての配賦規則を別に決めます。Query creditの合計をそのままwarehouseの全額とみなしません。

### Tagを付け、使用履歴を部門別に集計する

次は、finance専用の既存warehouseへtagを付ける構成例です。`governance.tags` schemaと`finance_wh`が存在する前提です。Tag作成にはschemaの`CREATE TAG`と親database／schemaの権限、割当にはaccountの`APPLY TAG`、またはtagの`APPLY`と対象warehouseの`OWNERSHIP`が必要です。

```sql
CREATE TAG governance.tags.cost_center
  ALLOWED_VALUES 'finance', 'engineering';

ALTER WAREHOUSE finance_wh
  SET TAG governance.tags.cost_center = 'finance';
```

履歴を参照できるroleで、当月のwarehouse computeを集計します。Tagのdatabase・schema・名前・object種類を限定してから結合するため、別の分類tagによる二重集計を避けられます。未分類のwarehouseも残します。

```sql
SELECT
  COALESCE(t.tag_value, 'untagged') AS cost_center,
  SUM(w.credits_used_compute) AS compute_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY w
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES t
  ON w.warehouse_id = t.object_id
  AND t.domain = 'WAREHOUSE'
  AND t.tag_database = 'GOVERNANCE'
  AND t.tag_schema = 'TAGS'
  AND t.tag_name = 'COST_CENTER'
WHERE w.start_time >= DATE_TRUNC('month', CURRENT_TIMESTAMP())
GROUP BY cost_center;
```

これは現在のtag割当とusageを対応させる集計です。途中で部門を付け替えた場合、過去の帰属を自動復元する履歴台帳としては扱いません。履歴分析には各viewの反映遅延も考慮します。

共有applicationでは、SQLを発行するsessionの`QUERY_TAG`を部門ごとに設定します。これはschema objectであるobject tagとは異なるparameterです。Session内で後続queryへ適用されるため、部門が変わったら変更し、session再利用時に前の値を引き継がないようにします。

```sql
ALTER SESSION SET QUERY_TAG = 'cost_center=finance';
```

基本的なtag作成・割当は全Editionで利用できます。自動tag propagationやtag-based maskingはEnterprise Edition以上です。費用分類を行う要件と、policyや自動伝播を使う要件のEdition条件を区別します。

<a id="budgets"></a>
## 予算 — 月次credit超過を予測する

月途中の実績がlimit未満でも、同じペースが続くと月末に超える場合があります。Budgetはcredit使用量から超過を予測し、対応する時間を確保するために通知します。Spending limitの単位は通貨ではなくcreditで、期間はUTCの暦月です。請求額やstorage料金全体を上限以内へ固定する機能ではありません。

Account budgetはaccountのcredit使用量全体を監視します。Serverlessも対象ですが、対応は`METERING_HISTORY`のservice typeの可用性に依存します。Custom budgetは部門・projectなどの対象群を選び、対応するobjectのcomputeを監視します。Warehouseに加え、pipeのSnowpipe、tableのAutomatic Clustering、serverless taskなどを対象にできます。任意の全object・全費用が対応するとは仮定せず、公式の対応一覧を確認します。

### Custom budgetの対象を選ぶ

対象は個別objectとして追加するか、object tagと値の組で選びます。たとえば`cost_center = 'finance'`をbudgetへ追加すると、その組を持つ対応objectが対象になります。単にtagを作成しただけではbudgetへ追加されません。

Tag経由なら対象objectの増減に追随でき、同じobjectを複数custom budgetへ含められます。個別追加は1 objectにつき1 custom budgetで、別budgetへ追加すると前のbudgetから外れます。同じbudgetに個別指定とtag指定の両方で入っても使用量は一度だけ数えます。

設定では、対象選択、月次credit limit、通知先を揃えます。Snowsightでcustom budgetを作成するには、先にaccount budgetを有効化します。SQLではaccount budgetが無効でもcustom budgetを作成できます。メール通知には検証済みの宛先が必要で、SQL経由ではnotification integrationの設定とSNOWFLAKE applicationへの`USAGE` grantも必要です。[2.2のnotification](02-data-governance.md#notifications)と費用監視を組み合わせます。

### 監視権限と対象追加権限を分ける

Account budgetの管理はSNOWFLAKE applicationの`BUDGET_ADMIN`、閲覧は`BUDGET_VIEWER`で分けます。Custom budgetのinstanceには`ADMIN`と`VIEWER`があります。さらに両budgetで`SNOWFLAKE.USAGE_VIEWER` database roleなどの関連権限が必要で、budgetを見られることだけでは対象を追加できません。

Custom budget作成には`SNOWFLAKE.BUDGET_CREATOR` database role、格納schemaの`CREATE SNOWFLAKE.CORE.BUDGET`、親database／schemaの`USAGE`が必要です。対象の追加・削除にはそのobjectの`APPLYBUDGET`、tagによる選択にはそのtagの`APPLYBUDGET`と親database／schemaの`USAGE`が必要です。Tagをobjectへ付ける`APPLY`と、tagをbudgetへ追加する`APPLYBUDGET`は別の権限です。

### 予測通知は超過直前の強制停止とは異なる

Budgetの基本のlimitは通知に使います。Limit設定だけではwarehouseを停止しません。Warehouseのquota到達時に組み込みの停止actionを実行する要件はResource Monitorに対応します。

現行Budgetには、予測使用量または実績使用量のthresholdでuser-defined stored procedureを呼ぶcustom actionもあります。停止処理を実装することもできますが、owner's rightsのprocedure、関連grant、action設定が必要です。「Budgetでは停止できない」と一括りにせず、標準のlimit通知と追加実装した処理を区別します。

Budgetにはusage反映・refreshの遅延があります。既定refresh intervalは最大6.5時間で、low latency設定では1時間です。Low latency化はbudget自身のcompute費用を増やします。Budget運用にもserverless測定処理とmetadata storageの費用がかかるため、通知と停止を無遅延の厳密な請求上限保証とは扱いません。

[費用の分類・予測・停止の図](../../diagrams/domain-2/cost-management-selection.md)で、同じtagを帰属分析とcustom budgetの対象選択に再利用する流れを確認してください。

## 確認問題

- [C2-2.3-Q01: Resource Monitor](../../exercises/chapter/c2-2.3-q01.md)
- [C2-2.3-Q02: Warehouse credit計算](../../exercises/chapter/c2-2.3-q02.md)
- [C2-2.3-Q03: ACCOUNT_USAGE](../../exercises/chapter/c2-2.3-q03.md)
- [C2-2.3-Q04: 費用分類の粒度](../../exercises/chapter/c2-2.3-q04.md)
- [C2-2.3-Q05: 予算の単位と動作](../../exercises/chapter/c2-2.3-q05.md)

## 章のまとめ

- Resource Monitorはquotaに対するthreshold actionでuser-managed warehouseを制御する。
- Credit計算ではsize rate、active cluster数、各running intervalを分ける。
- Currency costを求めるにはbilled creditと契約単価が必要である。
- Account Usageは履歴分析に使い、view固有のlatency／retentionを前提にする。
- 専用resourceはobject tag、共有applicationのqueryはQUERY_TAGで帰属の粒度を揃える。
- Budgetは月次creditの超過予測を通知し、標準limitだけでは停止しない。
- Custom budgetの対象追加にはAPPLYBUDGETが必要で、閲覧権限とは異なる。

## 次に学ぶこと

[Domain 3: データのロード、アンロード、接続](../domain-3/README.md)では、costとsecurityを考慮しながらdataをSnowflakeへ出し入れする方式を学びます。

## 根拠・関連する公式ドキュメント

- `docs-resource-monitors` — https://docs.snowflake.com/en/user-guide/resource-monitors
- `docs-warehouses-overview` — https://docs.snowflake.com/en/user-guide/warehouses-overview
- `docs-warehouse-considerations` — https://docs.snowflake.com/en/user-guide/warehouses-considerations
- `docs-account-usage` — https://docs.snowflake.com/en/sql-reference/account-usage
- `docs-warehouse-metering-history` — https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history
- `docs-cost-attributing` — https://docs.snowflake.com/en/user-guide/cost-attributing
- `docs-object-tagging-work` — https://docs.snowflake.com/en/user-guide/object-tagging/work
- `docs-budgets` — https://docs.snowflake.com/en/user-guide/budgets
- `docs-custom-budgets` — https://docs.snowflake.com/en/user-guide/budgets/custom-budget
- `docs-budget-costs` — https://docs.snowflake.com/en/user-guide/budgets/cost
- `docs-budget-custom-actions` — https://docs.snowflake.com/en/user-guide/budgets/custom-actions
- `docs-budget-tutorial` — https://docs.snowflake.com/en/user-guide/tutorials/budgets
