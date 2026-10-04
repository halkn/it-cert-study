# Comparison Tables — 機能の使い分け

> Status: complete

要件の「入力」「改善したい対象」「利用者」「許容する費用」を先に決めて比較します。Objectiveの本文リンクは[Referenceの索引](README.md#objectiveから本文へ戻る)、Source IDのURLは[出典台帳](../docs/sources.json)を参照します。

## Domain 1: 操作・計算・ストレージ・AI

### Architectureとobjectの境界（1.1・1.3）

| 対象 | 責務・包含関係 | 判断の要点 |
|---|---|---|
| Database Storage | 永続データを保持 | Warehouseを停止してもtableは残る |
| Compute | Query等の処理を実行 | 同じデータへworkload別warehouseを割り当てられる |
| Cloud Services | 認証・metadata・query最適化等を調整 | 業務データの永続保存やwarehouseでの計算とは役割が異なる |
| Organization → account | 複数accountをまとめる管理境界 | Region・cloudはaccountの配置、Editionは提供機能の区分 |
| Database → schema → object | Table・view・stage等の包含関係 | Warehouse・account role・integrationはschema内のtableと同じ階層ではない |

根拠: `docs-key-concepts-architecture`, `docs-organizations`, `docs-access-control-objects`, `docs-snowflake-editions`, `docs-supported-cloud-platforms`。

### 操作する場所（1.2）

| 機能 | 主な目的 | 選ぶ場面 | 境界 |
|---|---|---|---|
| Snowsight | ブラウザーで探索・SQL実行・監視 | 画面で状態を確認する | 接続成功後もroleとwarehouse等のcontextが必要 |
| Snowflake CLI | SQL・開発プロジェクトの操作をコマンド化 | CIや反復する実行・deploy | SnowSQLと同じ機能の改名とは扱わない |
| VS Code拡張 | IDE内でSQL・Snowpark開発 | ソース編集と接続先の操作をまとめる | IDEの選択だけでは権限エラーは解消しない |

根拠: `docs-snowsight`, `docs-snowflake-cli`, `docs-vscode-extension`。

### Warehouseの拡張（1.4）

| 選択 | 変えるもの | 改善を狙う症状 | 制約・費用 |
|---|---|---|---|
| Scale up | 1 clusterのsize | 単一queryの計算資源・メモリー不足 | 大きくしてもSQLやJOINの誤りは残る。稼働単価が増える |
| Scale out | Multi-clusterのcluster数 | 同時queryが多くqueueで待つ | Enterprise以上。単一queryを複数clusterへ分割する仕組みではない |
| Warehouse分離 | Workloadごとのwarehouse | ETLとBIの負荷・費用を分ける | 同じ保存データを参照できる。idleとcacheの影響を各々評価する |
| Auto-suspend | idle時の停止 | 利用していない時間の費用削減 | Warehouse cacheは停止で失われる |

根拠: `docs-warehouses-overview`, `docs-multicluster-warehouses`, `docs-warehouse-considerations`, `docs-warehouse-cache`。

### Tableとview（1.5）

| 種類 | データ・結果の扱い | 選ぶ場面 | 注意 |
|---|---|---|---|
| Permanent table | Snowflake管理の永続データ | 通常の業務データ | Time Travelと、その後の7日Fail-safe |
| Transient table | 明示的なDROPまで存続 | 再生成可能な中間データ | Time Travelは0〜1日、Fail-safeなし |
| Temporary table | Session内で存続 | Session限定の中間処理 | Session終了で削除、Fail-safeなし |
| External table | 外部stageのファイルを参照 | 既存cloud storageのデータを読む | 読取り専用。通常tableと同じDML対象ではない |
| Iceberg table | Apache Iceberg形式のデータ | Open table formatで相互運用 | Catalogとstorageの管理主体で運用・機能条件が変わる |
| Dynamic Table | Query結果をtarget lagに従いrefresh | 宣言的な変換pipeline | 外部入力を取り込むAPIではなく、refreshにもcomputeが必要 |
| Standard view | Query定義を参照時に評価 | 共通のSELECTを抽象化 | 結果を永続保存しない |
| Materialized view | 結果を保存し自動維持 | 繰り返す対象計算を削減 | Enterprise以上、定義制約・保守compute・storageあり |
| Secure view | 内部定義や処理でデータの露出を抑制 | 機密データの公開 | Secureはprivacy属性。結果の保存や高速化を意味しない |

根拠: `docs-temp-transient-tables`, `docs-time-travel`, `docs-external-tables`, `docs-iceberg-tables`, `docs-dynamic-tables`, `docs-views`, `docs-materialized-views`, `docs-secure-views`。

Secureはstandard viewにもmaterialized viewにも指定できる属性です。「結果を保存するか」と「privacyを重視するか」を別々に判断します。

### AIと開発機能（1.6）

| 機能 | 主な入力・成果物 | 選ぶ目的 |
|---|---|---|
| Cortex AI Functions | テキスト等を渡すSQL関数 | 要約・分類等のAI処理をSQLへ組み込む |
| Cortex Search | 検索対象データと検索要求 | 文書等を検索し必要な情報を取り出す |
| Cortex Analyst | 自然言語とsemantic model／view | 構造化データへの質問をSQLへ対応付ける |
| Snowpark | Python・Java・ScalaのAPI | Snowflake内でデータ処理を実装する |
| Notebook | Code・SQL・実行結果 | 対話的に実験・分析する |
| Streamlit | Pythonによる画面 | データアプリを利用者へ提供する |
| Snowflake ML / Model Registry | 学習処理・model version | ML開発とmodelの管理・推論を行う |

根拠: `docs-cortex-ai-functions`, `docs-cortex-search`, `docs-cortex-analyst`, `docs-snowpark`, `docs-notebooks`, `docs-streamlit`, `docs-snowflake-ml`。

## Domain 2: 権限・ガバナンス・コスト

### 権限と認証（2.1）

| 概念 | 判断するもの | 混同しやすい境界 |
|---|---|---|
| Authentication | 誰として接続するか | 接続成功だけでtableへのSELECTは許可されない |
| Authorization / RBAC | Roleに与えたprivilegeで何を操作できるか | Database・schemaのUSAGEとtableのSELECTを組み合わせる |
| Account role | Accountの権限を集約しsessionで使う | Warehouse等のaccount-level objectも対象 |
| Database role | 1 database内の権限をまとめる | Sessionで直接activateせずaccount roleへgrantする |
| Primary / secondary role | Sessionでactiveなrole | Object作成時のownershipはprimary roleを基準にする |
| Network policy | 許可する接続元 | User本人の認証方式やobject privilegeとは別 |
| Authentication policy | 利用可能な認証方式等 | Network policyによる接続元制限とは別 |

根拠: `docs-access-control-overview`, `docs-authentication-overview`, `docs-network-policies`, `docs-authentication-policies`。

### データを守る制約（2.2）

| 機能 | 主な対象 | 制御・役割 | 境界 |
|---|---|---|---|
| Masking policy | Column値 | Query時に返す値を変える | 元データをUPDATEして匿名化する操作ではない |
| Row access policy | Row | Query時に返す行を判定 | Columnの表示値変換とは別 |
| Tag | Objectの分類 | Key-valueのmetadataを付ける | Tagだけでアクセス拒否しない。Tag-based masking等との連携は別途設定 |
| Privacy policy | 分析の出力 | Differential privacyの制約 | 通常のmaskingと同じ「値の置換」ではない |
| Trust Center | Accountのsecurity posture | Scannerのfindingを調査する | Findingは自動的な全違反修復を意味しない |
| Tri-Secret Secure | 保存データの暗号鍵 | Snowflake鍵と顧客管理鍵を組み合わせる | Business Critical以上。SQLの行・列権限とは別 |

根拠: `docs-column-security`, `docs-row-access-policies`, `docs-object-tagging`, `docs-differential-privacy`, `docs-trust-center`, `docs-encryption-tss`。

### コストの停止・予測・帰属（2.3）

| 機能・指標 | 対象 | できること | 注意 |
|---|---|---|---|
| Resource Monitor | User-managed warehouseのcredit | Thresholdに応じて通知・停止 | Serverlessを一律停止する上限ではない |
| Budget | Account全体または選択した対応object | UTC暦月のcredit超過予測を通知 | 標準の予測通知を自動停止と同一視しない。Custom actionは別設定 |
| Cost center tag | Warehouse等のobject | 部門・projectへ費用を帰属 | Object tagとsessionのQUERY_TAGを区別する |
| QUERY_ATTRIBUTION_HISTORY | Query実行へのcompute配賦 | 共有warehouse内のquery費用を分析 | idleを含まず、請求全額と一致する指標ではない |
| WAREHOUSE_METERING_HISTORY | Warehouseの使用量 | 稼働期間のcreditを確認 | idleを含み得る。Viewのlatencyと課金調整も確認する |

根拠: `docs-resource-monitors`, `docs-budgets`, `docs-custom-budgets`, `docs-cost-attributing`, `docs-query-attribution-history`, `docs-warehouse-metering-history`。

## Domain 3: 入出力とpipeline

### Stageとロードの制御（3.1）

| 選択 | 主な目的 | 境界・権限 |
|---|---|---|
| User stage / table stage | 利用者／tableに付随するファイル置き場 | Named stageのような独立したgrant運用とは異なる |
| Named internal stage | Snowflake管理storageの共有ファイル置き場 | READ／WRITE。WRITEにはREADも必要 |
| External stage | 外部cloud storageの場所を参照 | StageのUSAGEとcloud側アクセス設定が必要 |
| ON_ERROR | ロード時のerror処理方針 | CONTINUE等は不正データを直す設定ではない |
| VALIDATION_MODE | ロード前の検証 | データを投入しない。変換SELECTを含むCOPYでは利用できない |
| VALIDATE() | 実行したCOPYのerror調査 | 事前検証のoptionではない。対応するCOPYの制約を確認する |
| COPY_HISTORY / LOAD_HISTORY | 過去のロード調査 | COPY_HISTORYはSnowpipeを含む。LOAD_HISTORYはCOPY INTOのみ |

ロードの対応形式はCSV・JSON・AVRO・ORC・PARQUET・XML、アンロードはCSV・JSON・PARQUETです。入力と出力の対応形式を同一視しません。

根拠: `docs-data-load-local-create-stage`, `docs-access-control-privileges`, `docs-create-stage`, `docs-copy-into-table`, `docs-copy-into-location`, `docs-validate-function`, `docs-copy-history`, `docs-load-history`。

### 起点・compute・実装方法（3.2）

| 機能 | 起点・入力 | Compute | 選ぶ要件・注意 |
|---|---|---|---|
| COPY INTO table | Stageのファイルをbatchで処理 | User-managed warehouse | 実行時点とbatchを利用者が制御する |
| Snowpipe | Stageのファイル到着通知／RESTによる依頼 | Snowflake管理 | ファイル単位の継続取り込み。同期の即時完了ではない |
| Snowpipe Streaming | Clientからの行データ | Snowflake管理 | ファイル化を介さない取り込み |
| Stream + Task | 変更offsetとschedule／trigger | Taskはwarehouseまたはserverless | 手続き的なDMLや独自の分岐を実装する |
| Dynamic Table | SELECTとtarget lag | Refresh用warehouse | 宣言的な依存関係。Lagは目標であり厳密な完了保証ではない |
| Openflow | 外部systemとのdata flow | Deployment構成による | NiFiに基づく接続・変換を管理する |

根拠: `docs-copy-into-table`, `docs-snowpipe-intro`, `docs-snowpipe-streaming-overview`, `docs-streams-intro`, `docs-tasks-intro`, `docs-dynamic-tables`, `docs-openflow-about`。

### 接続とIntegration（3.3）

| 種類 | 通信・操作の用途 | 例 |
|---|---|---|
| Driver / connector | 外部clientからSnowflakeへ接続 | JDBC・ODBC・Python、Kafka・Sparkとの連携 |
| Storage integration | 外部storageへのアクセスを管理 | StageからS3等を利用 |
| API integration | External functionのHTTPS proxyへのアクセス | SQLから外部serviceの処理を呼ぶ |
| Security integration | 認証・securityの連携設定 | OAuthやfederation等、integrationのtypeに依存 |
| Notification integration | 通知先への配送設定 | Email・queue・webhook |
| External access integration | Handlerの外向き通信を許可 | UDF／procedureから許可endpointへ接続 |
| Git integration | Snowflake内repositoryとremoteを連携 | 許可されたremoteからcodeを取得 |

Integrationを作っただけでは、対応するstage・function等やcloud側の許可まで完成しません。

根拠: `docs-drivers-overview`, `docs-storage-integration-ddl`, `docs-api-integration-ddl`, `docs-security-integration-ddl`, `docs-notification-integration-ddl`, `docs-external-access-integration-ddl`, `docs-git-overview`。

## Domain 4: 診断・最適化・cache・変換

### 性能改善の対象（4.1・4.2）

| 症状・目的 | 確認する証拠 | 手段 | 制約・費用 |
|---|---|---|---|
| Queueで待つ | Queued時間・warehouse負荷 | 同時実行の調整、multi-cluster | 単一queryのspillとは原因が違う |
| メモリー不足 | Local／remote spill | SQLの中間行削減、size見直し | JOIN条件の誤りを拡大で隠さない |
| 少数行の検索 | Filterのselectivity | Search Optimization | Enterprise以上、access pathの維持とstorage |
| 頻繁なfilterでscanが多い | Scanned partition・clustering | Clustering key | 配置維持のcomputeと書換えstorage |
| 同じ計算を繰り返す | 適合するSELECT・base変更頻度 | Materialized view | Enterprise以上、定義制約と保守費用 |
| Eligibleな重い処理 | QAS eligible判定・Profile | Query Acceleration Service | Enterprise以上、serverless computeの追加費用 |

根拠: `docs-query-profile`, `docs-memory-spillage`, `docs-reducing-queues`, `docs-search-optimization`, `docs-clustering-keys`, `docs-materialized-views`, `docs-query-acceleration`。

### 3つのcache（4.3）

| 種類 | 再利用するもの | Warehouse停止の影響 | 境界 |
|---|---|---|---|
| Persisted query result | 過去queryの結果 | 停止で直ちに失われない | 一致条件・権限等を満たす場合に再利用。常にhitする保証はない |
| Warehouse cache | 読んだtable data | 停止で失われる | Query自体の計算は残る |
| Metadata | 配置・統計等の情報 | Warehouse localのdataとは別 | Pruningや対応する処理の最適化に使う。一般的なSELECT全体の結果ではない |

`USE_CACHED_RESULT=FALSE`は保存結果の再利用を止めます。Warehouse cacheやmetadataまで無効にする設定ではありません。

根拠: `docs-persisted-results`, `docs-warehouse-cache`, `docs-micro-partitions`, `docs-parameters`。

### 集約とwindow（4.4）

| 機能 | 出力の粒度 | NULL・同順位などの注意 |
|---|---|---|
| GROUP BY + aggregate | Groupごとに集約 | COUNT(*)は行数、COUNT(column)は非NULLの数 |
| Window function | 元の行を残す | PARTITION BY・ORDER BY・frameが計算範囲を決める |
| ROW_NUMBER | 各partition内で連番 | 1件を選ぶならtie-breakerを指定する |
| RANK / DENSE_RANK | 同順位を付ける | 同順位の後で欠番あり／なし |
| QUALIFY | Window計算後の行を絞る | WHEREはwindow計算前 |
| FLATTEN | ARRAY等の要素を複数行へ展開 | 展開後の行数は元データの件数とは異なる |

根拠: `docs-count`, `docs-window-functions`, `docs-window-syntax`, `docs-qualify`, `docs-rank`, `docs-dense-rank`, `docs-flatten`。

## Domain 5: 復元・共有・配送

### 保護と分岐（5.1）

| 機能 | 目的 | 操作する主体 | 制約・費用 |
|---|---|---|---|
| Time Travel | 保持期間内の検索・clone・UNDROP | 利用者 | PermanentはStandard 0〜1日、Enterprise以上0〜90日。権限と有効保持期間が必要 |
| Fail-safe | Time Travel後の最終復旧 | Snowflake | Permanentの7日、best effort。利用者がSELECTする期間ではない |
| Zero-copy clone | 開発等の独立した分岐 | 利用者 | 標準tableは初期partitionを共有、以後の変更・保持でstorageが増え得る |
| Replication | 別account／regionの複製を更新 | 管理者 | DBとshareの複製は全Edition。追加account objectはBusiness Critical以上 |
| Failover group | Secondaryをprimaryへ切替 | 管理者 | Business Critical以上。Cloneの分岐と異なる |

根拠: `docs-time-travel`, `docs-fail-safe`, `docs-temp-transient-tables`, `docs-clone-storage`, `docs-replication-bcdr`。

Fail-safeの復旧には対応条件があります。Classic Snowpipe Streamingで取り込んだデータを含むtableはFail-safe復旧の対象外です。Time TravelとFail-safeの期間があれば、どのtableも復旧できるとは一般化しません。根拠: `docs-fail-safe`。

### 共有の利用者と提供物（5.2・5.3）

| 選択 | 利用者・提供物 | Compute・配送 | 注意 |
|---|---|---|---|
| Direct share | 同一regionの指定accountへデータ公開 | 通常consumerが自分のwarehouseでquery | 同一regionの通常共有で物理コピーを要求しない。Imported DBは読取り専用 |
| Reader account | Snowflake契約のない利用者 | Providerが管理・creditを負担 | Provider提供データ向け。通常consumerと費用主体が異なる |
| Data Clean Room | 制約付きの共同分析 | 許可されたtemplate・policyで分析 | 入力を渡すだけで任意出力が安全になる仕組みではない |
| Listing | 説明・公開対象・利用条件を持つproduct | 別regionへはAuto-Fulfillment等で配送 | Private／publicとfree／paidを別の軸として選ぶ |
| Marketplace | Listingの発見・取得の場 | Productごとの条件で利用 | Marketplace自体をtableやshareと同一視しない |
| Native App | Consumerへinstallするapplication | Consumerのデータアクセスは許可が必要 | Application packageとinstall後のapplicationを区別する |

根拠: `docs-secure-sharing`, `docs-sharing-consumer`, `docs-reader-accounts`, `docs-cleanrooms-overview`, `docs-listings`, `docs-marketplace`, `docs-auto-fulfillment`, `docs-native-app-framework`, `docs-native-app-access`。

再共有は、providerの許可条件を確認し、自分のdatabase内のsecure view経由で行います。Imported objectをそのまま自分のshareへgrantしません。Direct shareの再共有は同じorganization・region内という条件があります。根拠: `docs-resharing`, `docs-resharer`。
