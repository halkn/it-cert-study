# 1.4 Virtual Warehouseを構成する

> Status: complete
> Last verified: 2026-08-13

## この章で学ぶこと

Warehouse type、generation、size、cluster数、scaling policy、auto-suspend／resumeを異なる軸として説明し、ad-hoc query、data loading、BI、高concurrency、complex queryに合う構成を選びます。

## 前提知識

- [1.1](01-architecture.md)のcompute layer
- [1.3](03-object-hierarchy.md)のaccount objectとsession warehouse
- queue、cache、parallel processingの基本

## この章の用語

| 用語 | 意味 |
|---|---|
| size | 1 clusterへ割り当てるcompute量。上げる操作がscale up |
| multi-cluster | 同じwarehouse名の下で複数clusterを動かす構成 |
| scale out | cluster数を増やしてconcurrencyを処理する |
| scaling policy | Auto-scaleでclusterを増減する応答性とcostの方針 |
| Standard | 一般的なSQL／DML用warehouse type |
| Snowpark-optimized | memory-intensive Snowpark workload向けtype |
| auto-suspend | idle後にwarehouse全体を停止する設定 |
| auto-resume | warehouseが必要なstatementで自動再開する設定 |

## 試験範囲との対応

| Topic | 本文 | 根拠 |
|---|---|---|
| Warehouse type | [typeとgeneration](#warehouse-types) | `docs-gen2-warehouses`, `docs-snowpark-optimized-warehouses` |
| Scaling policy | [multi-cluster](#scaling-policies) | `docs-multicluster-warehouses` |
| 用途に応じた構成 | [workload別選定](#use-case-configurations) | `docs-warehouse-considerations` |
| Best practice | [2つの拡張軸](#best-practices) | `docs-warehouses-overview`, `docs-warehouse-considerations` |

<a id="warehouse-types"></a>
## Type、generation、sizeを別々に選ぶ

Standard warehouseは一般的なSQL query、DML、loadに使います。Standard Gen1とGen2はcompute generationの違いです。利用可能なregionでは新規Standard warehouseのgeneration既定がGen2ですが、availabilityはcloud／regionで異なります。試験では「Gen2はすべてのregionで必ず利用可能」と一般化しません。

Snowpark-optimized warehouseはlarge memoryを必要とするSnowpark workload向けです。既定構成はstandardよりnode当たりmemoryが大きく、`RESOURCE_CONSTRAINT`でmemory／CPU architectureを選びます。通常の短いSQLだからという理由だけで選びません。

Warehouse typeとsizeは別です。`LARGE STANDARD`と`LARGE SNOWPARK-OPTIMIZED`は同じ用途・resource構成とは限りません。Notebooks default warehouseはStudy Guide注記によりglobal GAまで出題対象外なので、本章の選定対象に含めません。

```sql
CREATE WAREHOUSE cert_d1_wh
  WAREHOUSE_TYPE = STANDARD
  WAREHOUSE_SIZE = XSMALL
  GENERATION = '2'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;
```

Gen2 availabilityは実行regionで確認します。利用できない場合にfallbackする挙動を前提に、productionではgenerationを明示してtestします。

<a id="scaling-policies"></a>
## Multi-clusterとScaling policyでconcurrencyを処理する

Multi-cluster warehouseは同じwarehouseにclusterを追加し、同時queryのqueueを別clusterへ配分します。Enterprise Edition以上の機能です。1 queryを複数clusterへ分割して必ず高速化する機能ではありません。

Auto-scale modeでは`MIN_CLUSTER_COUNT`から`MAX_CLUSTER_COUNT`の範囲で増減します。Standard policyはqueueの抑制と応答性を優先し、Economy policyはcluster起動を控えてcredit節約を優先するため、queryがqueueで待つ時間が長くなり得ます。Scaling policyはcluster数が固定されるMaximized modeでは意味を持ちません。

<a id="use-case-configurations"></a>
## Workloadから構成を選ぶ

| Workload | 最初の構成 | 観測して調整するもの |
|---|---|---|
| ad-hoc／開発 | 小さめ、auto-suspend短め | query complexity、再開頻度 |
| bulk data loading | file数とsizeに合うwarehouse、専用化 | load throughput。極端に少数fileならsize up効果が限定的 |
| BI／reporting | workload専用warehouse | queueが多ければmulti-cluster、response time重視ならStandard policy |
| complex query | まずscale up | spill、scan、query profile。concurrencyだけならscale out |
| 異なるteam | team／workload別warehouse | cost attributionと相互干渉 |

同じwarehouseにはcomplexityとdata setが近いhomogeneous workloadをまとめると、load分析とsize選定が容易です。ETLとinteractive BIを分けると、両者のcomputeとcostを独立調整できます。

<a id="best-practices"></a>
## Scale up/downとScale out/inを症状で分ける

![warehouse scaling](../../diagrams/domain-1/warehouse-scaling.md)

- 1つのlarge queryが遅い、spillしている: sizeを上げるscale upを検討する。
- 多数queryがqueueする: cluster数を増やすscale outを検討する。
- 負荷低下後: sizeを下げるscale down、cluster数を減らすscale inでcostを抑える。

Larger is not always fasterです。単純なqueryは追加resourceを活用できない場合があります。同じ代表queryを複数sizeで測り、elapsed timeとcreditを比較します。

### Auto-suspendとcacheのtrade-off

短いidleでsuspendすればcreditを節約できます。一方、warehouseをsuspendするとlocal data cacheが失われ、resume後の最初のqueryが遅くなる場合があります。短すぎる設定で頻繁にresumeすると、起動ごとの60秒minimum billingも繰り返します。query間隔に合わせて設定します。

## 公式ドキュメント読解課題

1. `docs-gen2-warehouses`で利用可能regionとdefault条件を確認します。
2. `docs-multicluster-warehouses`でStandardとEconomyのcluster開始条件の違いを説明します。
3. `docs-warehouse-considerations`でload、ad-hoc、production queryのinitial size指針を比較します。

## 20分ミニハンズオン: sizeと自動停止を観測する

`CREATE WAREHOUSE`権限が必要で、warehouse起動ごとに最低60秒分のcompute課金があり得ます。専用名を使い既存objectを変更しません。

```sql
CREATE WAREHOUSE cert_d1_14_wh WAREHOUSE_SIZE=XSMALL
  AUTO_SUSPEND=60 AUTO_RESUME=TRUE INITIALLY_SUSPENDED=TRUE;
USE WAREHOUSE cert_d1_14_wh;
SELECT CURRENT_WAREHOUSE(), CURRENT_VERSION();
ALTER WAREHOUSE cert_d1_14_wh SET WAREHOUSE_SIZE=SMALL;
DROP WAREHOUSE cert_d1_14_wh;
```

実行時間とquery historyを確認し、最後に必ずdropします。production dataをscanしません。

## 試験で重要なポイント

- sizeは1 clusterの能力、cluster数は主にconcurrencyを調整する。
- Standard／Economy policyはAuto-scale multi-clusterに適用する。
- Standardは応答性、Economyはcredit節約を相対的に優先する。
- workloadを分離するとperformance isolationとcost attributionがしやすい。
- auto-suspendはcreditを抑える一方、cacheとminimum billingを考慮する。

## 間違えやすいポイント

- scale upを高concurrencyの万能解にしない。
- multi-clusterをsingle query高速化機能と断定しない。
- Snowpark-optimizedをすべてのPython／Snowpark処理に必須としない。
- Gen2 availabilityとdefaultはregion／時点で変わるため再確認する。

## 確認問題

- [C1-1.4-Q01](../../exercises/chapter/c1-1.4-q01.md) Type選定
- [C1-1.4-Q02](../../exercises/chapter/c1-1.4-q02.md) Scaling policy
- [C1-1.4-Q03](../../exercises/chapter/c1-1.4-q03.md) Scale up/out
- [C1-1.4-Q04](../../exercises/chapter/c1-1.4-q04.md) Auto-suspend

[Domain演習D1-Q08〜Q09](../../exercises/domain/README.md)、[模擬M1-Q08〜Q09](../../exercises/mock/README.md)へ進みます。

## 章のまとめ

Warehouseはtype、generation、size、cluster数、自動化設定をworkloadの症状に合わせて構成します。single queryのresource不足にはscale up、concurrency queueにはscale outを使い分け、auto-suspendとcacheのcost／performance trade-offを測定します。

## 次に学ぶこと

[1.5 ストレージ概念](05-storage-concepts.md)でwarehouseがscanするmicro-partitionとtable／view typeを学びます。

## 根拠・関連する公式ドキュメント

- `docs-warehouses-overview` — https://docs.snowflake.com/en/user-guide/warehouses-overview
- `docs-warehouse-considerations` — https://docs.snowflake.com/en/user-guide/warehouses-considerations
- `docs-multicluster-warehouses` — https://docs.snowflake.com/en/user-guide/warehouses-multicluster
- `docs-gen2-warehouses` — https://docs.snowflake.com/en/user-guide/warehouses-gen2
- `docs-snowpark-optimized-warehouses` — https://docs.snowflake.com/en/user-guide/warehouses-snowpark-optimized
- `docs-create-warehouse-c03` — https://docs.snowflake.com/en/sql-reference/sql/create-warehouse
