# Exam Traps — 混同しやすい概念

> Status: complete

独自の復習用資料です。実試験問題の再現ではありません。「必ず」「すべて」「無償」のような断定を見たら、対象object・Edition・権限・compute・保持期間を確認します。各表のObjectiveから[本文の索引](README.md#objectiveから本文へ戻る)へ戻れます。Source IDは[出典台帳](../docs/sources.json)を参照します。

## Domain 1: 名前と役割を分ける

| 思い込み | 正しい判断・確認条件 | Objective | Source ID |
|---|---|---|---|
| Warehouseごとに業務データを保存する | 永続storageはcomputeと分離。別warehouseから同じtableを参照できる | 1.1 | `docs-key-concepts-architecture` |
| 上位Editionならどのregion・cloudでも同じ機能が使える | Editionとregion・cloudの対応を別々に確認する | 1.1 | `docs-snowflake-editions`, `docs-supported-cloud-platforms` |
| Toolを変えれば権限不足を解消できる | 同一接続先・role・context・権限を確認する。CLIも権限を迂回しない | 1.2 | `docs-snowflake-cli`, `docs-access-control-overview` |
| Warehouseはschema内のobject | Warehouseはaccount-level。Tableはdatabase・schema内 | 1.3 | `docs-access-control-objects` |
| SQL variableとparameterは同じ | SETした値は$nameで参照。動作設定はALTER SESSION等のparameter | 1.3 | `docs-sql-variables`, `docs-parameters` |
| Multi-clusterで単一queryを分割する | Cluster数はconcurrency、sizeは単一clusterの資源。症状を先に確認する | 1.4 | `docs-multicluster-warehouses`, `docs-warehouse-considerations` |
| Micro-partitionを利用者が手動管理する | Snowflakeが自動分割。Clustering keyは配置を改善する軸 | 1.5 | `docs-micro-partitions`, `docs-clustering-keys` |
| Secure viewは結果を保存し高速化する | Secureはprivacy属性。結果保存はmaterialized viewの性質 | 1.5 | `docs-secure-views`, `docs-materialized-views` |
| Cortex Searchが業務表への質問をSQL化する | 文書等の検索はSearch、semantic layerに基づくtext-to-SQLはAnalyst | 1.6 | `docs-cortex-search`, `docs-cortex-analyst` |

## Domain 2: 認証・許可・費用を分ける

| 思い込み | 正しい判断・確認条件 | Objective | Source ID |
|---|---|---|---|
| MFAやnetwork許可があればSELECTできる | 接続時の認証・network制御と、roleのobject privilegeは別 | 2.1 | `docs-mfa`, `docs-network-policies`, `docs-access-control-overview` |
| 親roleを子roleへgrantすると子の権限が増える | GRANT ROLE child TO ROLE parentでparentがchildの権限を継承する | 2.1 | `docs-access-control-overview` |
| Database roleをUSE ROLEで直接activateする | Database roleはaccount roleへgrantして利用する | 2.1 | `docs-access-control-overview` |
| Secondary roleが新規objectのownerになる | Object作成時のownershipはprimary roleを基準にする | 2.1 | `docs-access-control-overview` |
| Maskingで元データが書き換わる | Query時の返却値の制御。Rowの可視性はrow access policy | 2.2 | `docs-column-security`, `docs-row-access-policies` |
| Tag付与だけでアクセスを拒否する | Tagは分類metadata。Policyとの連携を別途構成する | 2.2 | `docs-object-tagging` |
| Resource Monitorがserverlessも止める | Warehouse向けの通知・停止。対応serverlessの予測監視はBudget等 | 2.3 | `docs-resource-monitors`, `docs-budgets` |
| Budgetのcredit limitは必ず処理を停止する | 標準の超過予測通知と、別設定のcustom actionを区別する | 2.3 | `docs-budgets`, `docs-budget-custom-actions` |
| Object tagとQUERY_TAGを同じjoinで扱える | Object分類とqueryのsession属性を区別。費用帰属にはidleの扱いも決める | 2.3 | `docs-cost-attributing`, `docs-query-attribution-history` |

## Domain 3: ファイル・変更・実行を分ける

| 思い込み | 正しい判断・確認条件 | Objective | Source ID |
|---|---|---|---|
| PUTは外部stageへuploadするSQL | PUTはlocalからinternal stageへ送るclient操作。External stageはcloud側でupload | 3.1 | `docs-put`, `docs-create-stage` |
| VALIDATION_MODEで検証しつつロードする | 検証のみ。変換SELECT付きCOPYの制約も確認する | 3.1 | `docs-copy-into-table` |
| FORCE=TRUEは安全な重複排除 | ロード履歴に関係なく再ロードし、重複し得る | 3.1 | `docs-copy-into-table` |
| ロードできる形式はすべてunloadできる | UnloadはCSV・JSON・PARQUET。Loadの6形式と区別 | 3.1 | `docs-copy-into-table`, `docs-copy-into-location` |
| Snowpipe Streamingもstageファイルが必要 | 行をAPIで送る。ファイル取り込みはSnowpipe | 3.2 | `docs-snowpipe-intro`, `docs-snowpipe-streaming-overview` |
| SELECTしただけでstreamを消費する | SELECTではoffsetを進めない。Streamを使うDMLのtransaction commitで進む | 3.2 | `docs-streams-intro` |
| TARGET_LAGは固定schedule・必達の遅延上限 | 鮮度の目標。依存関係・refreshの所要時間も影響する | 3.2 | `docs-dynamic-tables` |
| CREATE TASKで即座にschedule実行が始まる | 新しいtaskはsuspended。権限・computeを確認してRESUMEする | 3.2 | `docs-create-task`, `docs-tasks-intro` |
| API integrationがhandlerの任意通信を許可する | External function向けAPI integrationと、handler向けexternal access integrationを分ける | 3.3 | `docs-api-integration-ddl`, `docs-external-access-integration-ddl` |

## Domain 4: 症状・再利用・結果の粒度を分ける

| 思い込み | 正しい判断・確認条件 | Objective | Source ID |
|---|---|---|---|
| 実行が遅いならwarehouse拡大だけでよい | Queue・spill・scan・JOIN行数のどれが支配的かProfileで確認 | 4.1 | `docs-query-profile`, `docs-query-insights` |
| Queryへの配賦creditを合計するとwarehouseの全費用になる | QUERY_ATTRIBUTION_HISTORYはidleを含まない。QAS等の扱いも分ける | 4.1 | `docs-query-attribution-history` |
| 4つの最適化はすべて結果cache | QASはcompute、Search Optimizationは検索構造、clusteringは配置、materialized viewは保存結果 | 4.2 | `docs-performance-options`, `docs-performance-storage` |
| USE_CACHED_RESULT=FALSEで完全なcold状態になる | 保存結果の再利用だけを制御。Warehouse cacheは別 | 4.3 | `docs-parameters`, `docs-warehouse-cache` |
| Warehouse停止で保存query結果も消える | Local data cacheは失われるが、保存結果は別管理 | 4.3 | `docs-persisted-results`, `docs-warehouse-cache` |
| COUNT(column)とCOUNT(*)は常に同じ | 前者は非NULL値、後者は行数 | 4.4 | `docs-count` |
| FLATTEN後のCOUNT(*)が元の注文件数になる | ARRAY展開で行が増える。集計する粒度を決める | 4.4 | `docs-flatten` |
| RANK=1で各groupから必ず1件になる | 同率最高は複数件。1件ならROW_NUMBERとtie-breakerを使う | 4.4 | `docs-rank`, `docs-window-functions` |

## Domain 5: コピー・復元・許可を分ける

| 思い込み | 正しい判断・確認条件 | Objective | Source ID |
|---|---|---|---|
| Fail-safe期間に利用者がATでSELECTする | AT等はTime Travel。Fail-safeはSnowflakeによるbest effortの復旧 | 5.1 | `docs-time-travel`, `docs-fail-safe` |
| Transientは90日Time Travelと7日Fail-safeを持つ | Transient／temporaryは0〜1日のTime Travel、Fail-safeなし | 5.1 | `docs-temp-transient-tables` |
| Cloneは今後もstorage追加なしで同期する | 初期partitionを共有する独立分岐。変更・保持でstorageが増え得る | 5.1 | `docs-clone-storage` |
| COPY GRANTSで元tableのownershipも引き継ぐ | OWNERSHIPはコピーされず、clone作成roleが所有する | 5.1 | `docs-clone-command` |
| Replicationの全機能が全Editionで使える | DB・shareの複製と、追加account object・failoverのEdition条件を分ける | 5.1 | `docs-replication-bcdr` |
| 通常consumerとreaderでproviderのcompute負担は同じ | 通常consumerは自分のquery compute、readerはprovider負担 | 5.2 | `docs-secure-sharing`, `docs-reader-accounts` |
| Incoming dataは一切再共有できない | 現行仕様ではprovider許可と対象条件の下で自分のsecure view経由の再共有が可能 | 5.2 | `docs-resharing`, `docs-resharer` |
| Imported objectをそのまま自分のshareへgrantする | Imported objectの直接grantは禁止。許可済み再共有の構成と区別する | 5.2 | `docs-sharing-consumer`, `docs-resharer` |
| Clean Roomなら任意の分析・任意の出力が安全 | Template・policy・出力制約を構成。現行とlegacy方式も区別する | 5.2 | `docs-cleanrooms-overview`, `docs-cleanrooms-legacy-policies` |
| Private listingは必ず無料 | 公開対象と料金は別の選定軸 | 5.3 | `docs-listings` |
| Auto-Fulfillmentは別regionへの無償・瞬時の共有 | SSAへの配送・refresh・費用がある。Failoverとも別 | 5.3 | `docs-auto-fulfillment` |
| Native Appのinstallで全tableのSELECTが許可される | Consumerの権限grant・reference等が必要。Warehouseの権限だけでは不足 | 5.3 | `docs-native-app-access` |

誤答したときは、断定を丸暗記せず「その機能が扱う対象」と「成立する条件」を[比較表](comparison-tables.md)と本文で確認します。
