# Last-minute Review — 受験前の理解確認

> Status: complete

日本語版Study Guide（2026-02-20更新）の配点はDomain 1から順に31%・20%・18%・21%・10%です。根拠: `exam-study-guide-c03-jpn-2026-02-20`（[照合記録](../docs/japanese-blueprint-verification.md)）。配点の大きいDomainと自分の誤答が多いObjectiveを優先して復習します。

次の確認を資料を閉じて説明します。判断の要点を確認したら、説明できなかった項目だけ本文へ戻ります。すべてのObjectiveはCoverage Matrixで`complete`ですが、この確認表や既存模擬問題の正答率だけで合格を保証するものではありません。

## Domain 1 — 31%

| Objective・復習先 | 自分で説明する問い | 判断の要点 |
|---|---|---|
| [1.1](../textbook/domain-1/01-architecture.md) | 認証、query実行、永続保存はどの層か。Editionとcloud・regionはどう関係するか | Cloud Services／Compute／Database Storageの責務を分け、機能のEditionと可用性を確認する |
| [1.2](../textbook/domain-1/02-interfaces-and-tools.md) | 対話的な探索、CIでの操作、IDE内開発の入口は何か | Snowsight／CLI／VS Code。どの入口でもrole・context・権限を確認する |
| [1.3](../textbook/domain-1/03-object-hierarchy.md) | Warehouseとtableの包含関係、parameterとSQL variableの違いは何か | Warehouseはaccount、tableはschema内。動作設定とsession内の値を区別する |
| [1.4](../textbook/domain-1/04-virtual-warehouses.md) | 単一queryがspillする場合と、同時実行でqueueが増える場合に何を変えるか | SQLとsizeの見直し／concurrencyとcluster数。Auto-suspendとcacheのtrade-offも説明する |
| [1.5](../textbook/domain-1/05-storage-concepts.md) | Pruningの根拠は何か。Tableとviewを寿命・管理主体・保存結果で選べるか | Micro-partition metadataを使う。Transientとtemporary、externalとIceberg、standardとmaterializedとsecureを比較する |
| [1.6](../textbook/domain-1/06-ai-ml-app-development.md) | 要約、文書検索、業務表への自然言語質問、データアプリに何を使うか | AI Functions／Search／Analyst／Streamlit。Snowpark・Notebook・MLの役割も分ける |

根拠: `docs-key-concepts-architecture`, `docs-snowflake-editions`, `docs-supported-cloud-platforms`, `docs-snowsight`, `docs-snowflake-cli`, `docs-vscode-extension`, `docs-access-control-objects`, `docs-parameters`, `docs-sql-variables`, `docs-warehouse-considerations`, `docs-multicluster-warehouses`, `docs-micro-partitions`, `docs-temp-transient-tables`, `docs-external-tables`, `docs-iceberg-tables`, `docs-views`, `docs-materialized-views`, `docs-secure-views`, `docs-cortex-ai-functions`, `docs-cortex-search`, `docs-cortex-analyst`, `docs-streamlit`, `docs-snowpark`, `docs-notebooks`, `docs-snowflake-ml`。

## Domain 2 — 20%

| Objective・復習先 | 自分で説明する問い | 判断の要点 |
|---|---|---|
| [2.1](../textbook/domain-2/01-security-model.md) | 接続成功なのにSELECTできないとき何を確認するか | Role、database・schemaのUSAGE、tableのSELECT、warehouseのUSAGEを確認。認証・network許可とobject権限を分ける |
| [2.2](../textbook/domain-2/02-data-governance.md) | Column値、行、分類、分析出力、暗号鍵を守る機能は何か | Masking／row access／tag／privacy policy／Tri-Secret Secure。Trust Center、lineage、alert・notification、BCDRの役割も確認する |
| [2.3](../textbook/domain-2/03-monitoring-cost.md) | Warehouseをthresholdで止める、serverlessを含むcreditを予測する、部門へ費用を配るには何を使うか | Resource Monitor／Budget／cost center tagとquery配賦。idle・latency・meteredとbilledを分ける |

根拠: `docs-access-control-overview`, `docs-network-policies`, `docs-authentication-overview`, `docs-column-security`, `docs-row-access-policies`, `docs-object-tagging`, `docs-differential-privacy`, `docs-encryption-tss`, `docs-trust-center`, `docs-data-lineage`, `docs-alerts`, `docs-notifications`, `docs-replication-bcdr`, `docs-resource-monitors`, `docs-budgets`, `docs-cost-attributing`, `docs-query-attribution-history`, `docs-warehouse-metering-history`。

## Domain 3 — 18%

| Objective・復習先 | 自分で説明する問い | 判断の要点 |
|---|---|---|
| [3.1](../textbook/domain-3/01-loading-unloading.md) | Stage種別、入出力形式、error処理、事前検証、事後調査を区別できるか | InternalのREAD／WRITEとexternalのUSAGE。ON_ERROR／VALIDATION_MODE／VALIDATE()。COPY_HISTORYはSnowpipeも対象 |
| [3.2](../textbook/domain-3/02-automated-ingestion.md) | Batchファイル、到着ファイル、行、変更レコード、宣言的変換のどれを処理するか | COPY／Snowpipe／Streaming／Stream + Task／Dynamic Table。Streamのoffsetは消費DMLのcommitで進み、taskには実行開始とcomputeの設定が必要 |
| [3.3](../textbook/domain-3/03-connectors-integrations.md) | Client接続とstorage・API・security・notification・external access・Git integrationの役割は何か | 通信の相手と用途で選ぶ。Integrationの作成と、対応object・外部側の許可を区別する |

根拠: `docs-create-stage`, `docs-access-control-privileges`, `docs-copy-into-table`, `docs-copy-into-location`, `docs-validate-function`, `docs-copy-history`, `docs-snowpipe-intro`, `docs-snowpipe-streaming-overview`, `docs-streams-intro`, `docs-tasks-intro`, `docs-dynamic-tables`, `docs-drivers-overview`, `docs-storage-integration-ddl`, `docs-api-integration-ddl`, `docs-security-integration-ddl`, `docs-notification-integration-ddl`, `docs-external-access-integration-ddl`, `docs-git-overview`。

## Domain 4 — 21%

| Objective・復習先 | 自分で説明する問い | 判断の要点 |
|---|---|---|
| [4.1](../textbook/domain-4/01-evaluate-query-performance.md) | Queue、spill、scan、JOIN行数増大をどの証拠で区別するか | Query Profile／Insightsとhistoryを読む。Query配賦creditはidleを含まない |
| [4.2](../textbook/domain-4/02-optimize-query-performance.md) | 4つの最適化は何を改善し、どんな費用を増やすか | QASはeligible compute、Search Optimizationは検索構造、clusteringは配置、materialized viewは保存計算結果。維持費・Edition・定義制約を確認 |
| [4.3](../textbook/domain-4/03-caching.md) | Warehouse停止とUSE_CACHED_RESULT=FALSEはそれぞれ何に作用するか | 前者はlocal data cache、後者は保存query結果の再利用。Metadataとは別 |
| [4.4](../textbook/domain-4/04-data-transformation.md) | JSON展開、集約、window、QUALIFYで結果の粒度がどう変わるか | FLATTENで行が増える。COUNTのNULL、JOINの多重化、frame、同順位とtie-breaker、WHEREとQUALIFYの順序を確認 |

根拠: `docs-query-profile`, `docs-query-insights`, `docs-query-attribution-history`, `docs-performance-options`, `docs-performance-storage`, `docs-query-acceleration`, `docs-search-optimization`, `docs-clustering-keys`, `docs-materialized-views`, `docs-persisted-results`, `docs-warehouse-cache`, `docs-parameters`, `docs-flatten`, `docs-count`, `docs-joins`, `docs-window-functions`, `docs-window-syntax`, `docs-qualify`。

## Domain 5 — 10%

| Objective・復習先 | 自分で説明する問い | 判断の要点 |
|---|---|---|
| [5.1](../textbook/domain-5/01-collaboration-protection.md) | 誤操作の復元、開発分岐、別regionの保護、業務切替に何を使うか | Time Travel／clone／replication／failover。Fail-safeは利用者の履歴検索ではなくSnowflakeのbest effort復旧 |
| [5.2](../textbook/domain-5/02-data-sharing.md) | 通常consumerとreaderの権限・費用はどう違うか。再共有の条件は何か | Imported DBは読取り専用。通常consumerは自分のcompute、readerはprovider負担。再共有はprovider許可と自分のsecure view、org・region等の条件を確認 |
| [5.3](../textbook/domain-5/03-marketplace-listings.md) | Marketplace、listing、share、SSA、application package、applicationを区別できるか | 発見の場／product公開／データ許可／別regionの配送先／providerのpackage／consumerのinstall。公開対象と料金、installとデータアクセス許可を分ける |

根拠: `docs-time-travel`, `docs-fail-safe`, `docs-clone-storage`, `docs-replication-bcdr`, `docs-sharing-consumer`, `docs-reader-accounts`, `docs-resharing`, `docs-resharer`, `docs-marketplace`, `docs-listings`, `docs-auto-fulfillment`, `docs-native-app-framework`, `docs-native-app-access`。

## 演習の誤答から復習する

1. [模擬問題](../exercises/mock/README.md)の誤答を、対応Objectiveと「知らなかった用語」「条件の読み落とし」「機能の混同」に分ける。
2. [用語集](glossary.md)、[比較表](comparison-tables.md)、[混同しやすい概念](exam-traps.md)で原因を確認し、本文を読み直す。
3. 正解肢だけでなく、各誤答肢が要件を満たさない理由を説明する。
4. [章末問題](../exercises/chapter/README.md)と[Domain演習](../exercises/domain/README.md)で確認する。

[100問の模擬試験](../exercises/mock/sets/full-01-questions.md)は日本語版の配点に合わせて編成しています。採点後は[解答・復習冊子](../exercises/mock/sets/full-01-answers.md)から本文へ戻ります。Topic確認用の問題bankは別の比率で構成されているため、総合セットと使い分けます。Source IDとObjectiveの詳細は[Referenceの索引](README.md)を参照します。
