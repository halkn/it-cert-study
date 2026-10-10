# Glossary

> Status: complete

英語名を手掛かりに、日本語で意味と機能の境界を確認する用語集です。Objectiveに対応する本文は[Referenceの索引](README.md#objectiveから本文へ戻る)、Source IDのURLは[出典台帳](../docs/sources.json)を参照します。同じ用語が複数Domainで登場する場合は、関連Objectiveを併記します。

## Domain 1 — Objectives 1.1〜1.6

| 用語 | 定義 | Objective | Source ID |
|---|---|---|---|
| BAA | Business Associate Agreement。PHIを扱う際に必要となる事業提携者契約 | 1.1 | `docs-snowflake-editions` |
| Cloud Services | 認証、metadata、query parse／optimizationなどを調整するarchitecture layer | 1.1 | `docs-key-concepts-architecture` |
| Compute | SQLやSnowparkの処理を実行するarchitecture layer | 1.1 | `docs-key-concepts-architecture` |
| credit | Snowflakeのcomputeなどの利用量を表す課金単位 | 1.1 | `docs-compute-cost` |
| Database Storage | 永続dataを保持するSnowflakeのarchitecture layer | 1.1 | `docs-key-concepts-architecture` |
| DML | Data Manipulation Language。INSERT・UPDATE・DELETE・MERGE等、tableのデータを変更するSQL操作 | 1.1・4.4 | `docs-dml-reference` |
| metadata | dataの名前、構造、配置、統計など、dataを管理・処理するための情報 | 1.1 | `docs-key-concepts-architecture` |
| micro-partition | 標準tableのデータをSnowflakeが自動分割するstorage単位。配置・統計のmetadataを持つ | 1.1・1.5 | `docs-key-concepts-architecture` |
| MPP | Massively Parallel Processing。複数nodeで処理を並列実行する方式 | 1.1 | `docs-key-concepts-architecture` |
| PHI | Protected Health Information。個人を識別できる保護対象の医療情報 | 1.1 | `docs-snowflake-editions` |
| role | 利用者や処理へ権限をまとめて与える単位 | 1.1 | `docs-key-concepts-architecture` |
| Snowflake Edition | 利用可能な機能やservice levelを定める区分 | 1.1 | `docs-snowflake-editions` |
| Snowpark | Python／Java／ScalaからSnowflake内dataを処理するAPI群 | 1.1・1.6 | `docs-snowpark` |
| Virtual Warehouse | 1つ以上のcompute clusterで構成される、ユーザー管理の計算資源 | 1.1 | `docs-key-concepts-architecture` |
| VPS | Virtual Private Snowflake。他accountから隔離された最上位Edition | 1.1 | `docs-snowflake-editions` |
| Snowflake CLI | `snow` commandでSQLとdeveloper workloadを操作するtool | 1.2 | `docs-snowflake-cli` |
| Snowsight | Snowflakeのbrowser-based web interface | 1.2 | `docs-snowsight` |
| Visual Studio Code拡張 | IDE内でSnowflakeのSQL実行・Snowpark開発を行う拡張 | 1.2 | `docs-vscode-extension` |
| Database / Schema | Schemaをまとめるcontainer／table等のobjectをまとめるcontainer | 1.3 | `docs-databases` |
| Organization | 1つのbusiness entityが所有する複数accountを包含するobject | 1.3 | `docs-organizations` |
| Parameter | Account・user・session・object等の動作を設定する値。設定可能なlevelは項目ごとに異なる | 1.3 | `docs-parameters` |
| session context | current role、warehouse、database、schema等の実行文脈 | 1.3 | `docs-context-functions` |
| SQL variable | session内で`SET`し`$name`で参照する利用者定義値 | 1.3 | `docs-sql-variables` |
| Stored procedure | CALLで起動する、複数操作や処理手順をまとめたobject | 1.3 | `docs-procedures-vs-udfs` |
| UDF | User-defined function。式の一部として値やtableを返す利用者定義関数 | 1.3 | `docs-procedures-vs-udfs` |
| Auto-suspend / auto-resume | idleでwarehouseを停止する設定／必要時に自動再開する設定 | 1.4 | `docs-warehouses-overview` |
| Multi-cluster warehouse | 同じwarehouse内のcluster数を増減してconcurrencyを処理する構成 | 1.4 | `docs-multicluster-warehouses` |
| scale out | multi-cluster warehouseでcluster数を増やすこと | 1.4 | `docs-multicluster-warehouses` |
| scale up | warehouseのcluster sizeを増やすこと | 1.4 | `docs-warehouses-overview` |
| clustering key | 関連する値を近いmicro-partitionへ配置・維持する明示的な軸 | 1.5・4.2 | `docs-clustering-keys` |
| Dynamic Table | SELECT定義の結果をtarget lagに従いrefreshするtable | 1.5・3.2 | `docs-dynamic-tables` |
| External table | 外部stageのファイルをmetadataに基づいて参照する読取り専用table | 1.5 | `docs-external-tables` |
| Iceberg table | Apache Iceberg形式のtable。Catalog・storageの管理方式を選ぶ | 1.5 | `docs-iceberg-tables` |
| Permanent table | 通常の永続table。Time Travelと、その後のFail-safeを持つ | 1.5・5.1 | `docs-time-travel`, `docs-fail-safe` |
| pruning | metadataを使い不要なmicro-partition／column scanを避けること | 1.5・4.1 | `docs-micro-partitions` |
| Secure view | 定義の公開や内部最適化によるデータ露出を抑えるprivacy属性を持つview | 1.5・5.2 | `docs-secure-views` |
| Temporary table | Session限定で存続するtable。Session終了で削除され、Fail-safeはない | 1.5・5.1 | `docs-temp-transient-tables` |
| Transient table | 明示DROPまで存続するtable。Time Travelは0〜1日、Fail-safeはない | 1.5・5.1 | `docs-temp-transient-tables` |
| Cortex AI Functions | 要約・分類等のAI処理をSQLから利用する関数群 | 1.6 | `docs-cortex-ai-functions` |
| Cortex Analyst | Semantic model／viewを用い、構造化データへの自然言語質問をSQLへ対応付けるservice | 1.6 | `docs-cortex-analyst` |
| Cortex Search | 文書等の検索対象から関連する情報を検索するservice | 1.6 | `docs-cortex-search` |
| Model Registry | model version、metadata、inferenceを管理するschema-level object | 1.6 | `docs-snowflake-ml` |
| Notebook / Streamlit | Code・SQL・結果を扱う対話的な開発環境／Pythonで作るデータアプリ | 1.6 | `docs-notebooks`, `docs-streamlit` |
| semantic model／view | business metric等をphysical dataへ対応付けるsemantic layer | 1.6 | `docs-cortex-analyst` |

## Domain 2 — Objectives 2.1〜2.3

| 用語 | 定義 | Objective | Source ID |
|---|---|---|---|
| Account identifier | Organization名とaccount名などで接続先accountを一意に示す識別子 | 2.1 | `docs-account-identifiers-c03` |
| Account role | Account内のobject privilegeを持ち、sessionでactivateできるrole | 2.1 | `docs-access-control-overview` |
| Authentication policy | 使用可能な認証方式やclient等を制御するpolicy | 2.1 | `docs-authentication-policies` |
| DAC | Object ownerがそのobjectへのaccessを委任できる方式 | 2.1 | `docs-access-control-overview` |
| Database role | 同じdatabase内のprivilegeをまとめ、account roleへgrantして使うrole | 2.1 | `docs-access-control-overview` |
| Event table | Log、trace、metricなどのtelemetryを保存するtable | 2.1 | `docs-logging-tracing` |
| Federated authentication | External IdPで認証し、その結果をSnowflakeへ渡す方式 | 2.1 | `docs-federated-authentication` |
| IdP | Identity provider。Federation等で本人の認証を担う外部サービス | 2.1 | `docs-federated-authentication` |
| Key-pair authentication | Userへpublic keyを登録し、client側private keyで認証する方式 | 2.1 | `docs-key-pair-auth` |
| MFA | Multi-factor authentication。複数の要素を組み合わせる認証 | 2.1 | `docs-mfa` |
| Network policy | IP addressやnetwork ruleでSnowflakeへのtrafficを制御するpolicy | 2.1 | `docs-network-policies` |
| OAuth | Security integrationとaccess tokenを使ってclient accessを委任する方式 | 2.1 | `docs-oauth` |
| OWNERSHIP | Objectの所有権。通常の利用権限のgrantとは区別する | 2.1 | `docs-access-control-overview` |
| Primary role | Sessionの主role。Object作成時のownershipの基準となる | 2.1 | `docs-access-control-overview` |
| Privilege | ObjectへのSELECTやUSAGE等、特定操作を許可する権限 | 2.1 | `docs-access-control-overview` |
| RBAC | Privilegeをroleへ、roleをuserへ割り当てるaccess control方式 | 2.1 | `docs-access-control-overview` |
| Secondary role | Primary roleと同時にactiveにし、通常操作の権限を集約できるaccount role | 2.1 | `docs-access-control-overview` |
| Securable object | privilegeをgrantできる保護対象 | 2.1 | `docs-access-control-overview` |
| Alert | Conditionを評価し、trueならactionを実行するschema-level object | 2.2 | `docs-alerts` |
| CMK | Customer-managed key。顧客がcloud鍵管理serviceで管理する暗号鍵 | 2.2 | `docs-encryption-tss` |
| Data lineage | Sourceからtargetへのdata movementまたはobject dependencyの関係 | 2.2 | `docs-data-lineage` |
| Finding | Trust Centerのscannerが検出した調査対象のsecurity上の問題 | 2.2 | `docs-trust-center` |
| Masking policy | Query時にcolumnの返却値をcontextに応じて変換するpolicy | 2.2 | `docs-column-security` |
| Notification integration | Cloud queueからの通知受信や、email・queue・webhookへの通知送信の設定object | 2.2 | `docs-notifications`, `docs-notification-integration-ddl` |
| Privacy policy | Differential privacyで個人に関する推測riskを抑えるpolicy | 2.2 | `docs-differential-privacy` |
| Row access policy | Query時に各rowを返すかBooleanで判定するpolicy | 2.2 | `docs-row-access-policies` |
| Tag | Objectへkey-value型の分類metadataを付けるschema-level object | 2.2 | `docs-object-tagging` |
| Tri-Secret Secure | Snowflake-managed keyとCMKを組み合わせるdual-key model | 2.2 | `docs-encryption-tss` |
| Trust Center | Scannerとfindingでaccountのsecurity postureを評価する機能 | 2.2 | `docs-trust-center` |
| ACCOUNT_USAGE | Account全体の使用量・履歴等を公開するSNOWFLAKE databaseのschema | 2.3・4.1 | `docs-account-usage` |
| APPLYBUDGET | Object・tagをbudget対象へ追加・削除する権限。Tag割当のAPPLYとは異なる | 2.3 | `docs-budgets`, `docs-custom-budgets` |
| Budget | UTC暦月のcredit使用量をlimitと比較し、超過予測を通知する機能 | 2.3 | `docs-budgets` |
| Cost center | 部門・projectなど費用を帰属する単位 | 2.3 | `docs-cost-attributing` |
| Custom budget | 対応objectを個別指定またはtagと値で選ぶ予算 | 2.3 | `docs-custom-budgets` |
| Idle credit | Warehouseが稼働しているがquery処理へ配賦されない時間等のcredit | 2.3・4.1 | `docs-cost-attributing`, `docs-query-attribution-history` |
| Metered / billed credit | 測定された利用量／課金調整を反映した請求対象credit | 2.3 | `docs-compute-cost` |
| QUERY_TAG | Queryの分類情報を持つsession parameter。Object tagとは異なる | 2.3 | `docs-cost-attributing` |
| Resource Monitor | Warehouse creditをquotaと比較して通知／停止するobject | 2.3 | `docs-resource-monitors` |
| Showback／chargeback | 使用費用を部門へ可視化する／配賦する運用 | 2.3 | `docs-cost-attributing` |
| WAREHOUSE_METERING_HISTORY | Warehouse別のhistorical credit usageを提供するAccount Usage view | 2.3 | `docs-warehouse-metering-history` |

## Domain 3 — Objectives 3.1〜3.3

| 用語 | 定義 | Objective | Source ID |
|---|---|---|---|
| COPY_HISTORY | `COPY INTO`とSnowpipeの両方のロード履歴を返すAccount Usage view | 3.1 | `docs-copy-history` |
| Directory table | Stage上のファイルのmetadata catalogを提供する暗黙のobject | 3.1 | `docs-data-load-dirtables` |
| External stage | S3、Google Cloud Storage、Azure上の場所を指すstage | 3.1 | `docs-create-stage` |
| File format | ファイルのtypeとparse規則をまとめたobjectまたはinline指定 | 3.1 | `docs-create-file-format` |
| Internal stage | Snowflakeが管理するstorage上のstage。user／table／named internalの3種 | 3.1 | `docs-data-load-local-create-stage` |
| Load metadata | Tableごとにロード済みファイルを記録し、重複ロードを防ぐmetadata | 3.1 | `docs-copy-into-table` |
| ON_ERROR | Error行を含むファイルの扱いを決めるcopy option | 3.1 | `docs-copy-into-table` |
| SNOWFLAKE_SSE | Internal stageでserver-side encryptionのみを使うencryption type | 3.1 | `docs-create-stage` |
| VALIDATION_MODE | データをロードせずファイルを検証するcopy option | 3.1 | `docs-copy-into-table` |
| Auto-ingest | Cloud storageのevent notificationを起点にpipeへロードを依頼する方式 | 3.2 | `docs-snowpipe-auto` |
| CDC | Change data capture。INSERT・UPDATE・DELETE等の変更を追跡する仕組み | 3.2 | `docs-streams-intro` |
| METADATA$ISUPDATE | 変更レコードがUPDATEの一部かを示すstreamのmetadata列 | 3.2 | `docs-streams` |
| Offset | Streamがどこまでを消費済みとみなすかを示すtransaction versionの位置 | 3.2 | `docs-streams-intro` |
| Openflow | Apache NiFi上に構築された、外部systemとSnowflakeを繋ぐ統合service | 3.2 | `docs-openflow-about` |
| Pipe | `COPY INTO <table>`文を保持し、Snowpipeのロードを定義するobject | 3.2 | `docs-create-pipe` |
| REFRESH_MODE | Dynamic Table作成時にAUTO・FULL・INCREMENTALを選ぶ設定 | 3.2 | `docs-dt-refresh-modes` |
| Serverless task | Warehouseを指定せず、Snowflakeのcompute資源で実行するtask | 3.2 | `docs-tasks-intro` |
| Snowpipe | StageのファイルをSnowflake管理のcomputeで継続的に取り込むservice | 3.2 | `docs-snowpipe-intro` |
| Snowpipe Streaming | ファイルを介さず行を直接tableへ書き込む取り込みAPI | 3.2 | `docs-snowpipe-streaming-overview` |
| Stream | Objectの変更をoffsetで追跡するobject。Standard streamはoffset間の正味の差分を返す | 3.2 | `docs-streams-intro` |
| Streamのstale | Offsetが参照する変更履歴を利用できなくなり、変更を読めない状態 | 3.2 | `docs-streams-intro` |
| TARGET_LAG（target lag） | Dynamic Tableがbase dataに対して目標とする鮮度。固定scheduleや厳密な完了保証ではない | 1.5・3.2 | `docs-dynamic-tables` |
| Task | SQLをscheduleまたは先行taskの完了で実行するobject | 3.2 | `docs-create-task` |
| Task graph | Root taskと後続taskで構成されるDAG | 3.2 | `docs-tasks-graphs` |
| API integration | 外部HTTPS proxy serviceの呼び出しを許可するaccount-level object | 3.3 | `docs-api-integration-ddl` |
| Driver | Applicationから接続しSQLを実行するclient library | 3.3 | `docs-drivers-overview` |
| External access integration | UDF／procedure handlerからの外部通信を許可するintegration | 3.3 | `docs-external-access-integration-ddl` |
| External function | SQLから外部serviceの処理を呼び出す関数 | 3.3 | `docs-external-functions` |
| Git repository | Remote Git repositoryのcloneをSnowflake内に持つschema-level object | 3.3 | `docs-git-repository-ddl` |
| Query pushdown | Sparkのlogical planの一部をSnowflake側で処理させる仕組み | 3.3 | `docs-spark-connector-overview` |
| RECORD_CONTENT | Kafka connectorが既定で作るmessage本体のVARIANT列 | 3.3 | `docs-kafka-connector-overview` |
| Snowflake Python API | SQLを書かずSnowflakeのresourceを操作する`snowflake.core` package | 3.3 | `docs-python-api-overview` |
| Storage integration | 外部cloud storageへの認証と許可場所を管理するaccount-level object | 3.3 | `docs-storage-integration-ddl` |

## Domain 4 — Objectives 4.1〜4.4

| 用語 | 定義 | Objective | Source ID |
|---|---|---|---|
| exploding join | 入力に対してJOIN後の行数が大きく増える状態 | 4.1 | `docs-query-insights` |
| query attribution | 資源消費に基づくクエリ実行へのcompute creditの配賦。idleは含まない | 4.1 | `docs-query-attribution-history` |
| Query Insights | 検出した性能上の条件と調査・改善の提案 | 4.1 | `docs-query-insights` |
| Query Profile | 処理ノード、行数、scan、spill等からクエリの動作を調べる実行情報 | 4.1 | `docs-query-profile` |
| Queue | Warehouseの資源等を待つqueryの待ち行列 | 4.1 | `docs-reducing-queues` |
| spill | メモリーに収まらない中間データのlocal／remote storageへの退避 | 4.1 | `docs-memory-spillage` |
| Automatic Clustering | Clustering keyに基づく配置をSnowflakeが維持するservice | 4.2 | `docs-clustering-keys` |
| cardinality | 列または式の異なる値の数 | 4.2 | `docs-clustering-keys` |
| materialized view | SELECTの結果を保存し、Snowflakeが維持するview | 4.2 | `docs-materialized-views` |
| Query Acceleration Service | eligibleな処理の一部をshared serverless computeへ渡すサービス | 4.2 | `docs-query-acceleration` |
| search access path | 値とmicro-partitionを結び付ける永続的な検索構造 | 4.2 | `docs-search-optimization` |
| Search Optimization Service | 検索構造を維持し、選択性の高い対象検索を高速化する機能 | 4.2 | `docs-search-optimization` |
| selectivity | filterが対象行を絞り込む程度 | 4.2 | `docs-performance-storage` |
| persisted query result | 実行後に一定期間保存されるクエリ結果 | 4.3 | `docs-persisted-results` |
| USE_CACHED_RESULT | 保存結果の再利用を制御するsession parameter | 4.3 | `docs-parameters` |
| warehouse cache | 稼働中warehouseのlocalに保持するtable data | 4.3 | `docs-warehouse-cache` |
| Aggregate function | 複数行をCOUNT・SUM・AVG等の値へ集約する関数 | 4.4 | `docs-aggregate-functions`, `docs-count` |
| FLATTEN | ARRAYやOBJECT等の複合値を複数行へ展開するtable function | 4.4 | `docs-flatten` |
| LATERAL | FROMの先行する行の値を、続くtable function等で参照する指定 | 4.4 | `docs-flatten` |
| QUALIFY | window function計算後の値で行を絞る句 | 4.4 | `docs-qualify` |
| ROW_NUMBER / RANK / DENSE_RANK | 行ごとの連番／同順位後に欠番が生じる順位／欠番のない順位 | 4.4 | `docs-window-functions`, `docs-rank`, `docs-dense-rank` |
| VARIANT | 半構造化データを含む値を保持する型 | 4.4 | `docs-query-semistructured` |
| window frame | partition内で現在行の計算対象とする範囲 | 4.4 | `docs-window-functions` |
| Window function | Partition・順序・frameに基づいて、各行を残したまま計算する関数 | 4.4 | `docs-window-functions` |

## Domain 5 — Objectives 5.1〜5.3

| 用語 | 定義 | Objective | Source ID |
|---|---|---|---|
| AT / BEFORE | 指定した時点／statement実行直前の過去状態を参照するTime Travelの句 | 5.1 | `docs-time-travel` |
| COPY GRANTS | Clone作成等でOWNERSHIPを除く権限をコピーするoption | 5.1 | `docs-clone-command` |
| Fail-safe | Time Travel終了後にSnowflakeがbest effortで復旧を試みる7日の期間 | 5.1 | `docs-fail-safe` |
| failover group | Replicationに加えsecondaryからprimaryへの切替を可能にするobject | 2.2・5.1 | `docs-replication-bcdr` |
| replication group | 複製対象・複製先・refresh予定をまとめるobject | 5.1 | `docs-replication-bcdr` |
| Time Travel | 保持期間内の過去状態を利用者が検索・clone・復元する機能 | 5.1 | `docs-time-travel` |
| UNDROP | 保持期間内のDROPされた対応objectを復元するコマンド | 5.1 | `docs-time-travel` |
| zero-copy clone | 標準tableの初期partitionを共有する、作成後の変更が独立した複製 | 5.1 | `docs-clone-storage` |
| Data Clean Room | 提供データと許可分析・出力の制約を組み合わせる共同分析環境 | 5.2 | `docs-cleanrooms-overview` |
| direct share | 同一regionの特定accountへ直接公開するshare | 5.2 | `docs-sharing-provider` |
| imported database | Shareからconsumerが作る読取り専用database | 5.2 | `docs-sharing-consumer` |
| IMPORTED PRIVILEGES | Database roleで区分しない共有objectへのアクセスをconsumer内のroleへ付与する権限 | 5.2 | `docs-sharing-consumer` |
| provider／consumer | データを公開するaccount／そのデータを利用するaccount | 5.2 | `docs-secure-sharing` |
| reader account | Providerが管理・creditを負担する、契約のない取引先向けのaccount | 5.2 | `docs-reader-accounts` |
| resharing | 許可されたincoming dataを自分のsecure view経由で下流へ共有すること | 5.2 | `docs-resharer` |
| Share | Providerがconsumerへ公開するobjectのアクセス許可をまとめる単位 | 5.2 | `docs-secure-sharing` |
| application package | Providerがcode・データ・manifest・setup script等をまとめるobject | 5.3 | `docs-native-app-framework` |
| Application role | Native Appが定義する権限のまとまり。Consumer側account roleへgrantして使う | 5.3 | `docs-native-app-roles`, `docs-native-app-access` |
| Cross-Cloud Auto-Fulfillment | 別regionのSSAへListingの製品を配送・refreshする機能 | 5.3 | `docs-auto-fulfillment` |
| Listing | Data productに説明・公開対象・利用条件等を付ける公開単位 | 5.3 | `docs-listings` |
| Marketplace | Listingを発見・取得・公開する場 | 5.3 | `docs-marketplace` |
| Native App | Consumer accountへinstallされるapplication object | 5.3 | `docs-native-app-framework` |
| private／public listing | 指定consumerへの限定公開／Marketplaceでの公開 | 5.3 | `docs-listings` |
| Reference（Native App） | Consumerが許可したobjectをapplicationから参照するための仕組み | 5.3 | `docs-native-app-access` |
| SSA | Snowflake-managed secure share area。Auto-Fulfillmentで別regionへproductを配送する場所 | 5.3 | `docs-auto-fulfillment` |
