# Glossary

> Status: draft

用語は定義、関連objective、公式source IDとともに追加します。教材全体の用語は未完成です。

## Objective 1.1

| 用語 | 定義 | Objective | Source ID |
|---|---|---|---|
| Database Storage | 永続dataを保持するSnowflakeのarchitecture layer | 1.1 | `docs-key-concepts-architecture` |
| Compute | SQLやSnowparkの処理を実行するarchitecture layer | 1.1 | `docs-key-concepts-architecture` |
| Cloud Services | 認証、metadata、query parse／optimizationなどを調整するarchitecture layer | 1.1 | `docs-key-concepts-architecture` |
| Virtual Warehouse | 1つ以上のcompute clusterで構成される、ユーザー管理の計算資源 | 1.1 | `docs-key-concepts-architecture` |
| MPP | Massively Parallel Processing。複数nodeで処理を並列実行する方式 | 1.1 | `docs-key-concepts-architecture` |
| Snowflake Edition | 利用可能な機能やservice levelを定める区分 | 1.1 | `docs-snowflake-editions` |
| VPS | Virtual Private Snowflake。他accountから隔離された最上位Edition | 1.1 | `docs-snowflake-editions` |
| metadata | dataの名前、構造、配置、統計など、dataを管理・処理するための情報 | 1.1 | `docs-key-concepts-architecture` |
| role | 利用者や処理へ権限をまとめて与える単位 | 1.1 | `docs-key-concepts-architecture` |
| DML | Data Manipulation Language。tableのdataを読み書きするSQL操作 | 1.1 | `docs-compute-cost` |
| Snowpark | Java、Python、ScalaなどのcodeをSnowflakeで実行するための機能群 | 1.1 | `docs-key-concepts-architecture` |
| credit | Snowflakeのcomputeなどの利用量を表す課金単位 | 1.1 | `docs-compute-cost` |
| micro-partition | Snowflake tableのdataを自動分割して保存する連続したstorage単位 | 1.1 | `docs-key-concepts-architecture` |
| PHI | Protected Health Information。個人を識別できる保護対象の医療情報 | 1.1 | `docs-snowflake-editions` |
| BAA | Business Associate Agreement。PHIを扱う際に必要となる事業提携者契約 | 1.1 | `docs-snowflake-editions` |

## Domain 1 — Objectives 1.2〜1.6

| 用語 | 定義 | Objective | Source ID |
|---|---|---|---|
| Snowsight | Snowflakeのbrowser-based web interface | 1.2 | `docs-snowsight` |
| Snowflake CLI | `snow` commandでSQLとdeveloper workloadを操作するtool | 1.2 | `docs-snowflake-cli` |
| Organization | 1つのbusiness entityが所有する複数accountを包含するobject | 1.3 | `docs-organizations` |
| session context | current role、warehouse、database、schema等の実行文脈 | 1.3 | `docs-context-functions` |
| SQL variable | session内で`SET`し`$name`で参照する利用者定義値 | 1.3 | `docs-sql-variables` |
| scale up | warehouseのcluster sizeを増やすこと | 1.4 | `docs-warehouses-overview` |
| scale out | multi-cluster warehouseでcluster数を増やすこと | 1.4 | `docs-multicluster-warehouses` |
| pruning | metadataを使い不要なmicro-partition／column scanを避けること | 1.5 | `docs-micro-partitions` |
| clustering key | related valueを近いmicro-partitionへ配置・維持する明示的な軸 | 1.5 | `docs-clustering-keys` |
| target lag | dynamic tableがbase dataに対して目標とする鮮度 | 1.5 | `docs-dynamic-tables` |
| Snowpark | Python／Java／ScalaからSnowflake内dataを処理するAPI群 | 1.6 | `docs-snowpark` |
| semantic model／view | business metric等をphysical dataへ対応付けるsemantic layer | 1.6 | `docs-cortex-analyst` |
| Model Registry | model version、metadata、inferenceを管理するschema-level object | 1.6 | `docs-snowflake-ml` |

## Domain 2 — Objectives 2.1〜2.3

| 用語 | 定義 | Objective | Source ID |
|---|---|---|---|
| Securable object | privilegeをgrantできる保護対象 | 2.1 | `docs-access-control-overview` |
| RBAC | Privilegeをroleへ、roleをuserへ割り当てるaccess control方式 | 2.1 | `docs-access-control-overview` |
| DAC | Object ownerがそのobjectへのaccessを委任できる方式 | 2.1 | `docs-access-control-overview` |
| Account role | Account内のobject privilegeを持ち、sessionでactivateできるrole | 2.1 | `docs-access-control-overview` |
| Database role | 同じdatabase内のprivilegeをまとめ、account roleへgrantして使うrole | 2.1 | `docs-access-control-overview` |
| Secondary role | Primary roleと同時にactiveにし、通常操作の権限を集約できるaccount role | 2.1 | `docs-access-control-overview` |
| Network policy | IP addressやnetwork ruleでSnowflakeへのtrafficを制御するpolicy | 2.1 | `docs-network-policies` |
| Federated authentication | External IdPで認証し、その結果をSnowflakeへ渡す方式 | 2.1 | `docs-federated-authentication` |
| OAuth | Security integrationとaccess tokenを使ってclient accessを委任する方式 | 2.1 | `docs-oauth` |
| Key-pair authentication | Userへpublic keyを登録し、client側private keyで認証する方式 | 2.1 | `docs-key-pair-auth` |
| Account identifier | Organization名とaccount名などで接続先accountを一意に示す識別子 | 2.1 | `docs-account-identifiers-c03` |
| Event table | Log、trace、metricなどのtelemetryを保存するtable | 2.1 | `docs-logging-tracing` |
| Masking policy | Query時にcolumnの返却値をcontextに応じて変換するpolicy | 2.2 | `docs-column-security` |
| Row access policy | Query時に各rowを返すかBooleanで判定するpolicy | 2.2 | `docs-row-access-policies` |
| Tag | Objectへkey-value型の分類metadataを付けるschema-level object | 2.2 | `docs-object-tagging` |
| Privacy policy | Differential privacyで個人に関する推測riskを抑えるpolicy | 2.2 | `docs-differential-privacy` |
| Trust Center | Scannerとfindingでaccountのsecurity postureを評価する機能 | 2.2 | `docs-trust-center` |
| Tri-Secret Secure | Snowflake-managed keyとCMKを組み合わせるdual-key model | 2.2 | `docs-encryption-tss` |
| Alert | Conditionを評価し、trueならactionを実行するschema-level object | 2.2 | `docs-alerts` |
| Notification integration | Email、queue、webhookなどへのmessage配送設定 | 2.2 | `docs-notifications` |
| Failover group | Objectのreplicationとsecondaryのprimaryへのpromotionを提供するgroup | 2.2 | `docs-replication-bcdr` |
| Data lineage | Sourceからtargetへのdata movementまたはobject dependencyの関係 | 2.2 | `docs-data-lineage` |
| Resource Monitor | Warehouse creditをquotaと比較して通知／停止するobject | 2.3 | `docs-resource-monitors` |
| WAREHOUSE_METERING_HISTORY | Warehouse別のhistorical credit usageを提供するAccount Usage view | 2.3 | `docs-warehouse-metering-history` |
