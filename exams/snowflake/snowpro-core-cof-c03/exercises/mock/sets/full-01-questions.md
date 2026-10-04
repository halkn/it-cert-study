# SnowPro Core COF-C03 日本語模擬試験 01 — 問題

問題数: 100。各問は必要な選択数をすべて選び、選択肢の集合が一致した場合に1点とします。部分点はありません。

練習時間の目安: 115分。解答・解説を開かずに全問を解き、回答を記録してから採点します。

## 第1問

必要選択数: 1

Consumerはdatabase roleで区分されていないshareを取り込み、imported databaseのowner roleではSELECTできます。別のANALYST roleはqueryできません。Warehouse USAGEは確認済みです。Ownerが行う適切な対応はどれですか。

### 選択肢

- A. ProviderのdatabaseにANALYSTを作って同じ名前を揃える
- B. Consumerのimported databaseでIMPORTED PRIVILEGESをANALYSTへgrantする
- C. Imported tableをcloneしてそのcloneへSELECTをgrantする
- D. Imported schemaへUSAGEだけをgrantすれば共有objectのSELECTを代替できる

## 第2問

必要選択数: 1

分析者がSQLによる抽出、Pythonの可視化、Markdownの説明を同じ成果物にまとめ、試行錯誤しながらcell単位で再実行したいと考えています。中心となる開発環境はどれですか。

### 選択肢

- A. Cortex Analyst
- B. Snowflake Notebooks
- C. Model Registry
- D. Snowflake CLIの接続設定

## 第3問

必要選択数: 1

外部applicationが生成する行データを、stageへファイル化・uploadするstepを設けずSnowflake tableへ送信したいと考えています。この入力方式に対応する機能はどれですか。

### 選択肢

- A. Snowpipe auto-ingest
- B. Stage上のCOPY INTO
- C. Snowpipe Streaming
- D. Dynamic TableのTARGET_LAG

## 第4問

必要選択数: 3

ある企業が新しいSnowflake accountを設計しています。次の要件へ直接対応する選定を3つ選んでください。

- dataを特定の地理的位置に保持する。
- row-level securityを利用する。
- ETLとdashboardのcompute resourceを分離する。

### 選択肢

- A. 要件に合うcloud platform／regionを選択する
- B. dashboard用に永続dataを別databaseへcopyする
- C. Enterprise Edition以上を選択する
- D. warehouse sizeを変更すればregionとEditionの要件も満たせる
- E. ETLとdashboardへ別々のVirtual Warehouseを割り当てる

## 第5問

必要選択数: 1

streamとtaskで増分反映を組みました。streamをworksheetで`SELECT`して変更を確認していますが、taskは実行されているのに同じ変更が何度も処理されているように見えます。最初に確認すべき点はどれですか。
### 選択肢
- A. taskがsuspendedになっていないか
- B. streamがDML文で消費されているか
- C. streamが`APPEND_ONLY`になっていないか
- D. source tableのclustering keyが設定されているか

## 第6問

必要選択数: 1

Enterpriseで安定した売上tableから同じ日別集約を高頻度に計算している。JOIN・windowを含まず、base tableの更新に合わせて集約結果を自動維持し、複数のクエリから参照したい。結果の保存と保守費は許容できる。候補として最も直接的なものはどれか。

1つ選んでください。

### 選択肢

- A. USE_CACHED_RESULTを有効にし、同一SQLの結果再利用を使う
- B. 日別集約をmaterialized viewへ保存する
- C. 日別集約を通常のviewへ登録する
- D. 日付をclustering keyへ指定する

## 第7問

必要選択数: 1

developerはSnowsightで成功した、完全修飾名でtableを参照する`SELECT`をVS Code拡張から実行すると、そのtableへのSELECT権限不足になりました。両方とも接続は成功しており、account、current warehouse、database／schemaは同じで、warehouseへの`USAGE`も確認済みです。次に比較すべきものはどれですか。

### 選択肢

- A. 両sessionのcurrent warehouseと、そのwarehouseへの`USAGE`
- B. 両sessionのcurrent database／schemaと、object名の解決結果
- C. 両sessionのcurrent roleと、そのroleへのprivilege
- D. 両interfaceに適用されるnetwork policyと接続元IP address

## 第8問

必要選択数: 1

ある企業では、朝のETLが実行されると経営dashboardのqueryが遅くなります。両方が同じtableを参照しており、dataの鮮度は共通に保ちたいという要件があります。Snowflakeのアーキテクチャを最も活かす変更はどれですか。

### 選択肢

- A. ETL用Virtual Warehouseだけをsize upし、dashboardも同じwarehouseを使い続ける
- B. 同じmulti-cluster warehouseをETLとdashboardで共有し、最大cluster数を増やす
- C. dashboard用databaseを毎朝cloneし、ETLとは別のdataを参照させる
- D. ETLとdashboardに独立したVirtual Warehouseを割り当て、同じ永続dataを参照させる

## 第9問

必要選択数: 1

SQLのqueryから社外の住所正規化APIを呼び出し、結果を列として得たいという要件があります。必要な構成はどれですか。
### 選択肢
- A. storage integrationとexternal stage
- B. notification integrationとalert
- C. API integrationとexternal function
- D. security integrationとnetwork policy

## 第10問

必要選択数: 1

企業がAWS東京とAzure東日本に別々のSnowflake accountを持ち、accountを横断してbillingとusageを管理します。両accountを包含する最上位の管理単位はどれですか。
### 選択肢
- A. Failover group
- B. Replication group
- C. Organization
- D. Organization account

## 第11問

必要選択数: 1

Providerは検査logicを複数顧客のSnowflake accountへ届け、各顧客の既存tableをそのaccount内で検査したいと考えています。Consumerデータへの権限はまだ許可されていません。適切な構成はどれですか。

### 選択肢

- A. ProviderがpackageをListingで公開し、consumerがinstall後にCREATE WAREHOUSEだけをappへ許可して既存tableを検査する
- B. Consumerがproviderのapplication packageをinstallすれば全既存tableのSELECTが付与される
- C. Providerがapplication packageをListingで公開し、consumerがappをinstallして必要なtableアクセスを許可する
- D. Providerがreader accountにlogicを置き、そこから全consumer accountの既存tableを読む

## 第12問

必要選択数: 1

再生成できる中間データを、翌日に別sessionの処理からも使います。長い履歴保持やFail-safeは不要ですが、作成session終了後も明示DROPまでtableを残す必要があります。適切なtable typeはどれですか。

### 選択肢

- A. Temporary table
- B. Transient table
- C. Permanent table
- D. External table

## 第13問

必要選択数: 1

保持期間1日の標準permanent tableを30分前にDROPしました。担当者は同じschemaに同名の空tableを新規作成しています。権限は揃い、旧tableの履歴は残っています。旧tableをDROP直前の状態で復元する方法はどれですか。

### 選択肢

- A. 同名のままUNDROP TABLEを実行する
- B. 空tableでAT OFFSETを使い、旧tableの履歴として検索する
- C. 現在の空tableをrenameしてから、正しいcurrent schemaで旧tableをUNDROPする
- D. DATA_RETENTION_TIME_IN_DAYSを90にすれば旧tableが現在の空tableを置き換える

## 第14問

必要選択数: 1

列amountに3行の値10、NULL、20があります。GROUP BYなしでCOUNT(*)、COUNT(amount)、AVG(amount)を計算した結果はどれですか。

### 選択肢

- A. 3、3、10
- B. 2、2、15
- C. 3、2、15
- D. 3、2、10

## 第15問

必要選択数: 1

開発者は既存のVisual Studio CodeでGit管理のSQLとSnowpark Pythonコードを編集しています。接続先の操作、SQL実行、Snowparkのdebuggingを同じIDEへまとめたいと考えています。最も直接的な選択はどれですか。

### 選択肢

- A. Snowsightへ全ソースを移し、ブラウザーだけで編集する
- B. Terraform providerでSQLとPythonの任意処理を実行する
- C. Snowflake CLIだけを使用し、IDEの接続機能は使わない
- D. Visual Studio CodeのSnowflake拡張を使用する

## 第16問

必要選択数: 1

対応region・利用条件は確認済みです。指定顧客だけに説明と利用条件を付けた有料データを提供し、別regionへの配送をSnowflakeに管理させたいと考えています。適切な構成はどれですか。

### 選択肢

- A. Free public listingとResource Monitor
- B. Paid private listingとCross-Cloud Auto-Fulfillment
- C. Paid public listingとClient Redirect
- D. 同一region向けdirect shareとTime Travel

## 第17問

必要選択数: 1

UserはFINANCE_ROLEと、DB_A／DB_Bへaccessする2つのaccount roleをgrantされています。一つのqueryで両databaseをjoinし、新規objectのownerはFINANCE_ROLEにしたい場合の最適な方法はどれですか。
### 選択肢
- A. FINANCE_ROLEをprimaryにし、DB_AとDB_Bのaccount roleをsecondaryでactiveにする
- B. DB_Aのaccount roleをprimary、DB_Bのaccount roleをsecondaryにしたまま新規objectを作る
- C. FINANCE_ROLEをprimaryにするが、DB_Aのaccess roleだけをsecondaryでactiveにする
- D. DB_Aのdatabase roleをprimary、DB_Bのdatabase roleをsecondaryとして直接activateする

## 第18問

必要選択数: 4

Human userにはcorporate SSOとstrong authenticationを要求し、ETL serviceにはinteractive promptを要求せず、interactive applicationには委任tokenを使う設計を4つ選んでください。
### 選択肢
- A. ETL serviceへ共有human passwordとMFA prompt
- B. SAML／OIDC security integration
- C. ETL serviceへkey-pair authentication
- D. IdPまたはauthentication policyでhuman MFAを強制
- E. Interactive applicationへOAuth
- F. ETL serviceへbrowser-based SSOを設定し、operatorのlogin完了を毎回待つ

## 第19問

必要選択数: 1

チームが自分のデータとalgorithmでPythonの予測modelを学習しました。複数versionのmetadataを管理し、modelを利用する推論へつなげたいと考えています。最も直接的に対応する機能はどれですか。

### 選択肢

- A. Cortex Searchの検索index
- B. Snowflake MLのModel Registry
- C. File format object
- D. Cortex Analystのsemantic modelだけ

## 第20問

必要選択数: 1

Procedureのhandlerで発生したlogやtraceを保存し、後でSQLで調べたいと考えています。Query実行時間の履歴だけではなく、処理内部のtelemetryを対象にする保存先はどれですか。

### 選択肢

- A. QUERY_HISTORY viewだけ
- B. LOGIN_HISTORY viewだけ
- C. Event table
- D. WAREHOUSE_METERING_HISTORY viewだけ

## 第21問

必要選択数: 1

過去週の実行履歴が揃った状態でattributionのcompute合計がwarehouseのmetered computeより少ない。warehouseには長いidle区間がある。適切な説明はどれか。

1つ選んでください。

### 選択肢

- A. 同時実行した各クエリへ同じ秒数分のwarehouse creditを等しく割り当てる
- B. QAS creditは別に発生しないので差額をQASの利用分とみなす
- C. 実行への配賦にはidle時間を含まないので、差だけで集計不具合とは言えない
- D. idle時間は全クエリへ均等配賦されるため、差をSQLの欠落行とみなす

## 第22問

必要選択数: 1

標準tableのload順序が日付に近く、queryは特定の月だけを読みます。Snowflakeが全partitionを読まずに対象を絞れる主な理由はどれですか。

### 選択肢

- A. Micro-partitionの列の値域等のmetadataをfilterと比較する
- B. 利用者が月ごとの物理partitionを事前に作成している
- C. Tableにprimary keyを定義すると日付の索引が自動作成される
- D. QueryでORDER BYを指定すると保存データが月順に書き換わる

## 第23問

必要選択数: 2

BIのqueryが短い間隔で繰り返されるwarehouseでAUTO_SUSPENDを短くしたところ、再開直後のqueryが遅くなり、起動回数も増えました。確認すべき点を2つ選んでください。

### 選択肢

- A. 停止でwarehouseのlocal data cacheが失われること
- B. 再開のたびに起動後60秒の最低課金が適用されること
- C. 停止のたびにpermanent tableのデータが再ロードされること
- D. AUTO_SUSPENDがwarehouseのsizeを縮小すること

## 第24問

必要選択数: 1

標準のpermanent tableについて、誤更新を発見するまで数週間かかる場合に備え、30日間のTime Travelを設定したいと考えています。専用環境の隔離や顧客管理鍵は今回の要件に含みません。必要な機能を満たす最小のEditionはどれですか。

### 選択肢

- A. Standard
- B. Business Critical
- C. Enterprise
- D. Virtual Private Snowflake

## 第25問

必要選択数: 1

Snowflakeと直接契約していない取引先へ、自社の共有データをSQLで分析する環境を提供したいと考えています。取引先はデータロードを必要としません。最も適切なaccount構成と費用負担はどれですか。

### 選択肢

- A. Providerがreader accountを作り、そこで使うwarehouse creditを負担する
- B. Providerがreader accountを作り、warehouse creditは通常consumerと同様にreader側の契約へ請求される
- C. Reader accountを作り、複数の外部providerの共有データをロードして分析する
- D. Providerがreader accountを作り、共有tableをreader側へ物理コピーして元データのstorage負担を移す

## 第26問

必要選択数: 2

利用者のデータ参照権限は別途適切に設定済みです。view定義や基盤データの露出を抑えるsecureの性質と、高コストな反復queryの結果を事前保持するmaterializedの性質を両立したいと考えています。機能の可否と設計時の評価に関する正しい選択肢を2つ選んでください。
### 選択肢
- A. Standard viewはquery結果を自動的にstorageへ保持する
- B. Materialized viewをsecureとして定義できる
- C. Secureを指定するとmaterialized viewのmaintenance costがなくなる
- D. Storage／maintenance costとsecure処理によるperformance影響を評価する

## 第27問

必要選択数: 2

SELECT結果がまだ保持され、SQL・data・結果設定が変わらず、roleの参照権限もある。warehouseをsuspendした後の判断として正しいものを2つ選べ。

2つ選んでください。

### 選択肢

- A. warehouse local data cacheは破棄される
- B. 保存結果の再利用はsuspendだけでは否定されない
- C. 保存結果の再利用にはresumeしてlocal cacheを再構築する必要がある
- D. 同じwarehouse名でresumeすればlocal cacheもそのまま利用できる

## 第28問

必要選択数: 1

顧客ごとに最新の有効recordを必ず1件返したい。同じ更新時刻が複数あり、idは一意である。適切な方針はどれか。

1つ選んでください。

### 選択肢

- A. updated_atだけのRANK=1で必ず1件になるとみなす
- B. 顧客ごとにMAX(updated_at)だけをGROUP BYして返す
- C. WHEREで有効行を絞り、updated_at DESC, idでROW_NUMBERを付けてQUALIFYで1を選ぶ
- D. WHEREにROW_NUMBER() = 1を直接書く

## 第29問

必要選択数: 1

担当者はブラウザのSnowsightだけを使える環境で、手元のCSVをnamed internal stageへ置きたいと考えています。正しい説明はどれですか。
### 選択肢
- A. worksheetで`PUT`を実行すればアップロードできる
- B. worksheetで`GET`を実行すればアップロードできる
- C. `PUT`はworksheetから実行できないため、SnowsightのファイルアップロードかSnowSQLなどのclientを使う
- D. internal stageへのアップロードにはstorage integrationが必要になる

## 第30問

必要選択数: 1

EnterpriseのStandard warehouseをMIN_CLUSTER_COUNT=1、MAX_CLUSTER_COUNT=3で使っています。短時間に多数のBI queryが集中し、Economy policyではqueue時間が目標を超えています。Sizeは維持し、追加clusterの起動による応答性をcredit節約より優先したい場合、適切な変更はどれですか。

### 選択肢

- A. MINとMAXを両方3へ変更し、Economy policyで増減する
- B. SCALING_POLICYをStandardへ変更する
- C. MAX_CLUSTER_COUNTを1へ変更する
- D. AUTO_SUSPENDを短くして実行中queryのqueueを解消する

## 第31問

必要選択数: 1

すでにcloud storageにあるCSVファイルを、Snowflake tableへロードせず、外部stage上のファイルmetadataに基づく読取り専用のtableとして参照したいと考えています。Iceberg形式への変換やsnapshot管理は今回不要です。選ぶobjectはどれですか。

### 選択肢

- A. Dynamic Table
- B. Transient table
- C. Iceberg table
- D. External table

## 第32問

必要選択数: 1

あるteamはSnowflake objectとStreamlit applicationの変更をGitでreviewし、承認後にCI runnerから同一手順でdevelopmentとproductionへdeployしたいと考えています。最適な中心toolはどれですか。

### 選択肢

- A. Snowsight Workspaceで変更を確認し、各環境へのdeployは担当者が手動で再現する
- B. Snowflake CLIとversion管理されたproject／SQL file
- C. Terraformのresource定義の適用を、SQL処理とStreamlit application codeの実行手順として使用する
- D. VS Code拡張から各developerがproductionへ直接deployする

## 第33問

必要選択数: 1

Standard accountの大きな明細tableで、日付範囲filterが頻繁に使われる。値域が多くのpartitionで重なり、必要以上にscanしている。Editionを変えず、tableの配置を改善したい。要件に合う選択はどれか。

1つ選んでください。

### 選択肢

- A. materialized viewで日付別の結果を保存する
- B. QASを有効にしてscanの一部を追加computeへ渡す
- C. 利用する日付に沿ったclustering keyを検討する
- D. 日付列へSearch Optimizationを設定する

## 第34問

必要選択数: 1

Finance部門の専用warehouseとAutomatic Clusteringを使うtableへcost_center = financeのobject tagを付けています。対象が増えても予算の個別object一覧を更新せず、月次credit超過の見込みを通知したい。どの構成が適切ですか。

### 選択肢

- A. Warehouse-level Resource Monitorへ両objectを割り当て、forecast通知を有効にする
- B. Account budgetの対象をfinance tagだけへ絞り、その他の部門を対象から削除する
- C. QUERY_TAGにfinanceを設定し、session parameterを作成するだけでcustom budgetの対象を登録する
- D. Financeのtagと値をcustom budgetへ追加し、月次credit limitと超過予測の通知先を設定する

## 第35問

必要選択数: 1

新しくnamed internal stageを作り、directory tableでPDFのmetadataを管理します。Snowflake clientを使わずpre-signed URLでファイルを利用し、client-side暗号化を行わずserver-side暗号化のみを使います。Stage作成時に選ぶencryption typeとして適切なものはどれですか。

### 選択肢

- A. SNOWFLAKE_FULL
- B. SNOWFLAKE_SSE
- C. AWS_SSE_KMS
- D. NONE

## 第36問

必要選択数: 2

夜間処理用warehouseを停止した後も、利用者は認証してtableの構造を確認できます。別warehouseで同じtableをqueryすると、前夜のデータが返りました。この状況を説明するものを2つ選んでください。

### 選択肢

- A. 永続データの保存はwarehouseの稼働と分離されている
- B. 認証とmetadataの管理はCloud Servicesが担う
- C. Tableの永続データは最後に使用したwarehouseのlocal diskから転送される
- D. Warehouse停止時にCloud Servicesが業務データの永続保存を引き継ぐ

## 第37問

必要選択数: 2

受注処理で、SELECTの式から呼ぶ税額計算と、作業tableの作成・更新を含む複数stepの処理を別々に再利用したいと考えています。対応として適切なものを2つ選んでください。

### 選択肢

- A. 税額計算をUDFとして定義する
- B. 複数stepの処理をfile formatとして定義する
- C. 税額計算をpipeとして定義する
- D. 複数stepの処理をstored procedureとして定義する

## 第38問

必要選択数: 1

注文JSONのitems arrayにskuとqtyがあり、SKU別の数量を集計したい。同じarray内に複数要素がある。適切な処理はどれか。

1つ選んでください。

### 選択肢

- A. items[0]のqtyを数値へcastし、SKU別にSUMする
- B. LATERAL FLATTENでitemsを展開し、VALUEのqtyを数値へcastしてSKU別にSUMする
- C. itemsをFLATTENし、SKU別にCOUNT(*)する
- D. itemsをFLATTENし、SUMではなくCOUNT(VALUE:qty)する

## 第39問

必要選択数: 1

Pythonでtableのfilter・join・集約を記述し、大量データをclientへ全件downloadする設計を避けたいと考えています。DataFrame等から処理計画を作り、Snowflake側へ処理をpush downするAPIはどれですか。

### 選択肢

- A. Snowpark
- B. Snowflake Python Connectorで全件fetchしてからpandasで処理する
- C. Cortex Analystの自然言語入力
- D. Storage integration

## 第40問

必要選択数: 1

基底tableのcolumnを変更する前に、そのデータを使うviewと、CTASで作られた下流tableへの影響を調べたいと考えています。適切な調査方針はどれですか。

### 選択肢

- A. Data lineageでobject dependencyとdata movementの両方を辿る
- B. Lineageでviewの依存関係だけを辿り、CTASのデータ移動は対象から外す
- C. Lineageで変更元をdownstream、派生先をupstreamとして辿る
- D. 同じtagが付いたcolumnはすべて派生関係があるとして、tagの一致だけで影響範囲を決める

## 第41問

必要選択数: 2

各table ownerは引き続きtableのOWNERSHIPを保持しますが、個別にgrantする権限はSnowflakeの権限モデルとして取り除きたいと考えています。security teamのroleにはaccount全体のMANAGE GRANTSを付与せず、このschemaのownerとして配下のgrant判断を集約します。組み合わせるべき選択肢を2つ選んでください。
### 選択肢
- A. Schemaはregular schemaのままとし、security roleへ`MANAGE GRANTS`を付与する
- B. Schemaをmanaged access schemaとして作成する
- C. Regular schema配下の各tableで、security roleへfuture grantを設定する
- D. そのschemaのownerをsecurity teamのroleにする

## 第42問

必要選択数: 1

複数の外部systemとSnowflakeを接続し、Apache NiFiのprocessorを組み合わせてデータの流れを管理したいと考えています。Snowflake内部のSELECT結果のrefreshだけではなく、外部systemとの接続・変換が中心です。対応する機能はどれですか。

### 選択肢

- A. Dynamic Table
- B. Openflow
- C. Standard stream
- D. Materialized view

## 第43問

必要選択数: 2

セキュリティチームは、human userの接続元を会社のnetworkへ限定し、password loginにはMFAを要求したいと考えています。要件への対応を2つ選んでください。

### 選択肢

- A. RoleへtableのSELECTをgrantして接続元を限定する
- B. Network policyを対象へactivateして許可する接続元を制御する
- C. Authentication policy等でpassword loginのMFA要件を設定する
- D. Warehouseへresource monitorを割り当てて認証方式を制御する

## 第44問

必要選択数: 2

標準tableからcloneした検証用tableで値を更新しました。本番への影響と費用について、正しい説明を2つ選んでください。

### 選択肢

- A. 変更は本番tableへ反映される
- B. 本番tableの値はこの更新で変わらない
- C. 作成時にpartitionを共有しても、変更分や履歴でstorageが増え得る
- D. COPY GRANTSを付けてcloneすると、source tableのOWNERSHIPもcloneへ引き継げる

## 第45問

必要選択数: 1

Pythonで、業務担当者が条件を入力してSnowflakeデータを確認するweb画面を提供したいと考えています。分析者用の実験ノートより、利用者へdeployする対話的なdata appが目的です。最も直接的な選択はどれですか。

### 選択肢

- A. Snowflake Notebooks
- B. SnowparkのDataFrame APIだけ
- C. Cortex Search service
- D. Streamlit in Snowflake

## 第46問

必要選択数: 1

Snowparkで大きなデータセットを処理する専用workloadについて、node当たりの大きなメモリーを重視し、memory／CPU architectureの構成も検討したいと考えています。用途に最も対応するwarehouse typeはどれですか。

### 選択肢

- A. Standard Gen1 warehouse
- B. Standard Gen2 warehouse
- C. Snowpark-optimized warehouse
- D. Standard warehouseのcluster数を増やす構成

## 第47問

必要選択数: 1

Developerが数時間に数回、短いqueryを実行します。待機中costを抑え、必要時は自動起動したい場合の第一構成はどれですか。
### 選択肢
- A. 小さめwarehouse、短いauto-suspend、auto-resume有効
- B. 小さめwarehouse、60分のauto-suspend、auto-resume有効
- C. 小さめwarehouse、短いauto-suspend、auto-resume無効
- D. Snowpark-optimized warehouse、短いauto-suspend、auto-resume有効

## 第48問

必要選択数: 1

数百万件のmanualとticketから質問に関連するpassageをlow latencyで取得し、sourceを回答appへ渡したい場合の中心機能はどれですか。
### 選択肢
- A. Cortex Search
- B. Cortex Analyst
- C. AI SQLのtext generation functionだけを各manualへ個別実行する
- D. Snowflake MLのModel Registry

## 第49問

必要選択数: 2

1日分の売上検索がほぼ全partitionをscanし、JOIN後の行数も要件上の予想より大幅に増えている。まず確認すべきものを2つ選べ。

2つ選んでください。

### 選択肢

- A. Profileのlocal／remote spill量を比較し、中間データのメモリー不足を調べる
- B. 日付filterとpartitionの値域・data配置
- C. JOIN条件と結合keyの重複・対応行数
- D. queued_overload_timeとwarehouseの同時実行数を比較し、混雑による待機を調べる

## 第50問

必要選択数: 4

規制要件によりcustomerがcloud KMS keyをcontrolし、Snowflake keyと組み合わせ、既存dataも定期的にrekeyしたいと考えています。機能、機能別のEdition条件、運用上の注意について正しい選択肢を4つ選んでください。Edition条件はTri-Secret Secureとperiodic rekeyingをそれぞれ独立に判定します。
### 選択肢
- A. Tri-Secret Secure
- B. Snowflake-managed keyだけを使い、CMKを登録しない
- C. Business Critical以上のEdition
- D. CMKのavailability／rotation／recovery手順
- E. Periodic rekeyingにはEnterprise以上が必要
- F. Periodic rekeyingを有効にすれば、CMKの無効化や削除に備えるrecovery手順は不要になる

## 第51問

必要選択数: 1

Enterpriseで巨大な顧客tableから一意性の高いcustomer_idの等価条件で数行だけ取り出す処理が頻繁にある。全件集約の保存は不要で、既存のデータ配置を変更せず、検索条件から候補micro-partitionを特定するsearch access pathを追加したい。適した手法はどれか。

1つ選んでください。

### 選択肢

- A. customer_idをclustering keyへ指定する
- B. 同じSELECTを通常のviewへ登録する
- C. multi-clusterの最大cluster数を増やす
- D. customer_idへのSearch Optimization

## 第52問

必要選択数: 1

標準permanent tableの必要な履歴はTime Travelを過ぎ、Fail-safe期間内にあります。ほかの復旧手段も使えません。担当者は当日中の確実な復旧を要求しています。適切な説明はどれですか。

### 選択肢

- A. 7日間は利用者のAT queryで読み出せる
- B. 7日間を90日へ変更して復旧まで延長できる
- C. UNDROPはTime Travel終了後もFail-safeから即時に戻す
- D. Snowflake Supportへ復旧を依頼できるが、成功と当日中の完了は保証しない

## 第53問

必要選択数: 2

組織がPHIをSnowflakeへ保存する計画を立てています。適切な判断を2つ選んでください。

### 選択肢

- A. Standard Editionのwarehouseを大きくすれば同じ要件を満たせる
- B. Business Critical以上のEdition要件を確認する
- C. BI用warehouseをSnowpark-optimizedへ変更すればcompliance要件を満たせる
- D. SnowflakeとのBAAなど、PHI保存に必要な条件を確認する

## 第54問

必要選択数: 1

単純なCOUNT(*)が速かったtableへrow access policyを導入した。導入後の同じSQLが行をscanしている。適切な説明はどれか。

1つ選んでください。

### 選択肢

- A. policy導入後もrole別件数をmetadataから即座に返せるため、scanは不要である
- B. policyは列の値だけを変えるので、行の可視性はCOUNTに影響しない
- C. COUNT(*)をCOUNT(column)へ変えればpolicyの判定は省略できる
- D. 可視行を判定する必要があり、統計だけで答える最適化を一律に期待できない

## 第55問

必要選択数: 3

ETL warehouseのunexpected credit増加を早期通知し、hard limitでrunning queryも停止し、翌日に原因となったwarehouse usageを分析したい場合に必要なものを3つ選んでください。
### 選択肢
- A. Resource MonitorのNOTIFY trigger
- B. Budgetのnotificationだけ
- C. Resource MonitorのSUSPEND_IMMEDIATE trigger
- D. WAREHOUSE_LOAD_HISTORYのqueue時間だけを集計
- E. WAREHOUSE_METERING_HISTORYの集計

## 第56問

必要選択数: 1

同一SQLの保存済み結果を、データや必要権限などの条件を変えず毎日24時間以内に再利用しています。最初の実行から32日経った時点でも、その初回の結果を再利用できると考えてよいですか。保持期間について正しい説明はどれですか。

### 選択肢

- A. 初回実行の24時間後に必ず失効するため、2日目以降の再利用はできない
- B. 再利用で24時間の保持期間は更新されるが、初回実行から最大31日なので初回の結果は32日目には残らない
- C. warehouseを停止せず動かし続けていれば、初回の保存済み結果の保持期間に上限はない
- D. 再利用のたびに最大31日の起点も更新されるため、初回の結果を無期限に使い続けられる

## 第57問

必要選択数: 2

Support userには電話番号末尾4桁だけを返し、research analystの集計にはdifferential privacyのnoiseとprivacy budgetを適用したい場合に選ぶものを2つ選んでください。
### 選択肢
- A. Aggregation policy
- B. Privacy policy
- C. Row access policy
- D. Masking policy

## 第58問

必要選択数: 1

担当roleはcustom budgetの管理に必要なinstance ADMINと関連USAGE権限を持ちます。既存tagをobjectへ割り当てる権限もありますが、そのtagをbudgetの対象選択へ追加すると権限不足になります。Tagのbudget追加に必要なprivilegeはまだ付与していません。追加すべき権限はどれですか。

### 選択肢

- A. Tagに対するAPPLYBUDGET
- B. Warehouseに対するMODIFY
- C. Custom budgetのVIEWER instance role
- D. Tagを含むschemaへのCREATE TAG

## 第59問

必要選択数: 1

ファイルの一部columnをSELECTで変換してtableへCOPYする前に、入力ファイルのerrorを検査したいと考えています。VALIDATION_MODEの制約を踏まえた方法として適切なものはどれですか。

### 選択肢

- A. 変換SELECT付きCOPYへVALIDATION_MODEを追加する
- B. ON_ERROR=CONTINUEを指定し、投入せず検証結果だけを受け取る
- C. FORCE=TRUEを指定し、parse errorを検証済み扱いにする
- D. 変換なしの対応する検証COPYを別途実行し、変換・ロードと区別して確認する

## 第60問

必要選択数: 1

同じsessionで`SET target_table = 'SALES.PUBLIC.ORDERS';`を実行しました。この値をtableの識別子として使い、行を読むSQLはどれですか。

### 選択肢

- A. SELECT * FROM $target_table;
- B. SELECT * FROM IDENTIFIER($target_table);
- C. SELECT * FROM CURRENT_DATABASE();
- D. ALTER SESSION SET target_table = SALES.PUBLIC.ORDERS;

## 第61問

必要選択数: 3

Least privilegeを保ちながらuser／role、grant、database objectの管理責務を分離する対応を3つ選んでください。
### 選択肢
- A. SECURITYADMIN: user／role、grant、database objectの全日常管理
- B. USERADMIN: userとroleの管理
- C. SECURITYADMIN: grant管理
- D. USERADMIN: warehouseやdatabase object管理
- E. SYSADMIN: warehouseやdatabase object管理

## 第62問

必要選択数: 1

同じSQLの改善前後を比較する。保存結果を返すだけの実行を除外し、local data cacheの影響も見分けたい。適切な手順はどれか。

1つ選んでください。

### 選択肢

- A. 同じSQLで結果再利用を有効にしたまま、2回目の時間だけで比較する
- B. local cacheのscan割合だけを見て、保存結果を再利用した実行も一緒に比較する
- C. 結果再利用を無効にし、SQL・data・warehouse・負荷を揃えてcoldとwarmを分けて測る
- D. USE_CACHED_RESULTをFALSEにすればlocalも必ずcoldなので確認不要

## 第63問

必要選択数: 1

Consumerは外部の気象データを探し、社内の売上とJOINして分析したいと考えています。MarketplaceでデータListingを取得した後の説明として適切なものはどれですか。

### 選択肢

- A. Marketplace自身がconsumerのSQLを実行するwarehouseになる
- B. Marketplaceから取得した共有tableを更新して社内売上を書き込む
- C. 同一regionのデータshareを取得したconsumerは、共有データのstorageと自分のquery computeをともに負担する
- D. 共有データを自分のwarehouseでqueryし、自社データと組み合わせる

## 第64問

必要選択数: 2

売上recordを2系統から連結し、重複も残す要件である。顧客ごとにtimestamp、次にidの昇順で1行ずつ累積金額を求めたい。連結後の各行には順序を一意に決めるidがあり、SUMのwindowには`PARTITION BY customer ORDER BY timestamp ASC, id ASC`を指定済みである。連結方法とwindow frameについて適切な指定を2つ選べ。

2つ選んでください。

### 選択肢

- A. SUMのwindowにROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWINGを指定する
- B. UNION ALLで連結する
- C. SUMのwindowにROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROWを指定する
- D. UNIONで連結する

## 第65問

必要選択数: 1

Pythonでwarehouseやdatabase等のSnowflake resourceをobjectとして操作する処理と、接続してSQLを実行し結果を受け取る処理を整理しています。用途の対応として適切なものはどれですか。

### 選択肢

- A. Resourceのobject操作はPython API、SQL接続・結果取得はPython Connector
- B. Resourceのobject操作はPython Connector、SQL接続・結果取得はPython APIのsnowflake.core
- C. Resourceのobject操作はPython API、PythonからのSQL接続・結果取得にはJava用JDBC driverを直接使う
- D. Resourceのobject操作はSQL APIのSQL文送信だけで行い、SQL接続・結果取得はPython APIのresource object操作だけで行う

## 第66問

必要選択数: 1

外部systemがcloud storageへ数分おきにファイルを置きます。warehouseを常時起動せず、到着後まもなくロードしたいという要件があります。最も適した構成はどれですか。
### 選択肢
- A. `AUTO_INGEST = TRUE`のpipeを作り、cloud側のevent notificationを設定する
- B. 1分間隔のtaskから`COPY INTO`を実行する
- C. Snowpipe Streamingのchannelを開いてファイルを書き込む
- D. Openflow BYOCのflowでファイルを転送する

## 第67問

必要選択数: 1

BI queryは単独なら速いものの、始業時に200 usersが接続するとqueueが増えます。response timeを優先し自動対応する最適解はどれですか。
### 選択肢
- A. 単一clusterのwarehouseをsize upし、同時query数が増えてもscale outしない
- B. Auto-scale multi-cluster warehouseとEconomy policy
- C. Maximized multi-cluster warehouseで最大cluster数を常時起動する
- D. Auto-scale multi-cluster warehouseとStandard policy

## 第68問

必要選択数: 1

NULL金額の明細も含めてすべての行を残し、各行に顧客内の合計金額を付けたい。合計の計算だけではNULL金額を除外する。各顧客には少なくとも1件の非NULL金額がある。適切なSQL方針はどれか。

1つ選んでください。

### 選択肢

- A. SELECT customer, SUM(amount) FROM sales GROUP BY customerを使う
- B. SELECT id, customer, amount, SUM(amount) OVER () FROM salesを使う
- C. SUM(amount) OVER (PARTITION BY customer ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)を付ける
- D. SUM(amount) OVER (PARTITION BY customer)をSELECTへ加える

## 第69問

必要選択数: 2

query結果を1つのCSVファイルとして、列見出し付きでstageへ出力します。指定すべきoptionを2つ選んでください。
### 選択肢
- A. `SINGLE = TRUE`
- B. `HEADER = TRUE`
- C. `OVERWRITE = TRUE`
- D. `MATCH_BY_COLUMN_NAME = CASE_SENSITIVE`

## 第70問

必要選択数: 1

同じorganizationの二つのBusiness Critical accountで、主要databaseとrolesを別regionへ定期複製しています。Region障害後はsecondary側で書込みも再開したいと考えています。要件に合う構成はどれですか。

### 選択肢

- A. Replication groupだけを用意し、refreshで書込み可能にする
- B. 共有databaseをconsumerへimportし、そのtableへINSERTする
- C. Primaryをcloneし、以後の変更をcloneに同期する
- D. Failover groupを準備し、secondaryをprimaryへ昇格する

## 第71問

必要選択数: 2

Account budgetから月末credit超過の予測通知を受けました。現在の実績は月次limit未満で、通常のlimit通知のみ設定済みです。担当者が「通知が来たのでwarehouseはすでに停止し、今月の請求額もlimit以内で確定した」と報告しました。正しい判断を2つ選んでください。

### 選択肢

- A. 通知が来たため、実績creditはすでにlimitを超えたと判断する
- B. 通知は将来の超過予測であり、通常のlimit通知だけではwarehouseは停止しない
- C. 月次limitはcreditなので、この通知を通貨の請求額上限保証として扱わない
- D. 予測通知を受けたaccountのserverless処理はResource Monitorによってすでに停止した

## 第72問

必要選択数: 1

複数のCOPY処理で、同じ外部storageの場所と、CSVのheader・delimiterの設定を再利用したいと考えています。用途の対応として適切なものはどれですか。

### 選択肢

- A. 場所をfile format、解釈規則をstageへまとめる
- B. 場所と解釈規則の両方をstreamのoffsetへまとめる
- C. 場所をstage、解釈規則をnamed file formatへまとめる
- D. 場所をwarehouse、解釈規則をnetwork policyへまとめる

## 第73問

必要選択数: 1

数TB tableを日付で頻繁に絞るqueryがほぼ全micro-partitionをscanします。DMLは少なく、同じfilterが多用されます。最適な検討はどれですか。
### 選択肢
- A. Warehouseをsize upし、micro-partitionの重なりはそのままにする
- B. 日付expressionのclustering keyを評価する
- C. 同じtableにstandard viewを作り、日付順の`ORDER BY`をview定義へ追加する
- D. Multi-cluster warehouseの最大cluster数を増やす

## 第74問

必要選択数: 1

問い合わせtableの各行の本文を要約・分類し、SQLの処理pipelineへ結果を組み込みたいと考えています。自作のpredictive modelの学習・version管理は不要です。中心となる機能はどれですか。

### 選択肢

- A. Cortex Searchで文書indexだけを作る
- B. Cortex Analystへ集計の自然言語質問を送る
- C. Cortex AI FunctionsをSQLから利用する
- D. Model Registryで自作modelのversionを登録する

## 第75問

必要選択数: 3

Critical account objectを別regionへ非同期同期し、障害時にsecondary accountをwritable primaryへ切り替えます。Application設定では切替後のaccountをorganization nameとaccount nameで一意に指定します。必要なものを3つ選んでください。
### 選択肢
- A. Replication groupとrefresh scheduleだけ
- B. Failover group
- C. Region内でのみ一意なaccount name単独
- D. 定期refreshとpromotion runbook
- E. Organization／account nameに基づくaccount identifierまたはconnection URL

## 第76問

必要選択数: 2

Serverless taskのowner roleには処理するtableへの権限とEXECUTE TASKがありますが、EXECUTE MANAGED TASKがありません。Warehouseを指定せず、継続実行できる状態にしたいと考えています。必要な対応を2つ選んでください。

### 選択肢

- A. Owner roleへEXECUTE MANAGED TASKを付与する
- B. WarehouseのMONITORを付与すればserverless実行権限を代替できる
- C. 作成後suspendedのtaskを、準備完了後にRESUMEする
- D. TaskをSELECTすればschedule実行が有効になる

## 第77問

必要選択数: 3

GitHubのprivate repositoryにあるSQLスクリプトを、Snowflakeから直接実行できるようにします。必要なものを3つ選んでください。
### 選択肢
- A. 認証情報を保持するsecret
- B. `API_PROVIDER = git_https_api`のAPI integration
- C. `ORIGIN`にHTTPSのURLを指定したGit repository object
- D. repositoryを指すexternal stageとstorage integration

## 第78問

必要選択数: 2

WAREHOUSE_METERING_HISTORYのcredit実績を集計しました。担当者は、この値に一律の単価を掛けた値がaccountの請求全額になると考えています。この解釈の検証に当たって正しい選択肢を2つ選んでください。

### 選択肢

- A. Warehouse実績以外にserverless・storage等の費用項目があること
- B. Metered creditから請求額へ換算する際は、契約単価とcloud servicesの課金調整を確認すること
- C. Creditの数値が契約に関係なくそのまま通貨額を表すこと
- D. QUERY_TAGを付ければmetered creditとbilled creditが同じになること

## 第79問

必要選択数: 1

Enterprise accountでBIクエリは単独なら2秒、利用者が増える時間帯は実行2秒のままoverload待機が40秒になる。BI workloadだけを実行するwarehouseで、clusterのsizeを一定に保ち、同時利用者の増加に追従したい。最も要件に合う対策はどれか。

1つ選んでください。

### 選択肢

- A. multi-cluster warehouseのscale outを検討する
- B. warehouse sizeを上げ、単一クエリの実行時間短縮を主目的にする
- C. QASで各クエリの大きなscanを速くする
- D. AUTO_SUSPENDを延ばし、起動待ちだけを減らす

## 第80問

必要選択数: 1

ordersの同一customer_idにはamountが100の注文が2行、50の注文が1行あります。order_idは各行で異なります。各顧客の最高額と同額の注文をすべて返したい場合、QUALIFYに指定する条件はどれですか。

### 選択肢

- A. ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY amount DESC, order_id DESC) = 1
- B. RANK() OVER (PARTITION BY customer_id ORDER BY amount DESC, order_id DESC) = 1
- C. ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY amount DESC) = 1
- D. RANK() OVER (PARTITION BY customer_id ORDER BY amount DESC) = 1

## 第81問

必要選択数: 2

SQLだけで表現できる集約結果を、鮮度目標を宣言して自動維持させます。dynamic tableについて正しい説明を2つ選んでください。
### 選択肢
- A. `TARGET_LAG`はbase dataに対する遅れの目標を表す
- B. 作成時に`REFRESH_MODE = AUTO`により解決されたrefresh modeは、定義を変更しなくても実行のたびに`INCREMENTAL`と`FULL`の間で自動的に切り替わる
- C. 指定できる最小の`TARGET_LAG`は60秒である
- D. `TARGET_LAG = '10 minutes'`を指定すると、refreshは10分間隔の固定scheduleで実行される

## 第82問

必要選択数: 2

Business userが「地域別net revenue」を自然言語で質問し、承認済みmetric定義に沿うSQLを生成したい場合に必要なものを2つ選んでください。
### 選択肢
- A. Cortex Analyst
- B. Cortex Search service
- C. Snowflake MLのforecasting model
- D. Semantic modelまたはsemantic view

## 第83問

必要選択数: 1

日次ロードで、error行のあるファイルはそのファイルごとスキップし、残りのファイルはロードを続けたいという要件があります。指定するoptionはどれですか。
### 選択肢
- A. `ON_ERROR = SKIP_FILE`
- B. `ON_ERROR = CONTINUE`
- C. `ON_ERROR = ABORT_STATEMENT`
- D. `VALIDATION_MODE = 'RETURN_ALL_ERRORS'`

## 第84問

必要選択数: 1

同じstageのファイルに対して`COPY INTO`を再実行したところ、想定外に行数が2倍になりました。最も可能性が高い原因はどれですか。
### 選択肢
- A. `ON_ERROR = CONTINUE`が指定されていた
- B. `PURGE = TRUE`が指定されていた
- C. `FORCE = TRUE`が指定されていた
- D. `VALIDATION_MODE`が指定されていた

## 第85問

必要選択数: 2

PDFをstageへ置き、file一覧と文書内の金額を別々に扱いたい。正しい説明を2つ選べ。

2つ選んでください。

### 選択肢

- A. directory tableでpathやsize等の一覧metadataを取得できる
- B. 金額の抽出にはhandler等による内容処理が別途必要になる
- C. directory tableでPDF内のkeyを取得し、VARIANT pathで金額を読む
- D. directory tableのmetadataをrefreshし、更新された金額を文書内のfieldとしてSELECTする

## 第86問

必要選択数: 1

小さなtableにclustering keyを追加する提案があります。対象の範囲検索は月に数回だけで、tableは頻繁に更新されます。採用前に最も適切な確認はどれですか。

### 選択肢

- A. 検索時間の改善だけを測り、reclusteringの費用は判断から除外する
- B. 実際のfilterに関係なく、cardinalityが最も高い列をkeyにする
- C. 検索の改善量とreclusteringのcompute・履歴storage費用を比較する
- D. query用warehouseを小さくすればAutomatic Clusteringの計算費用も下がると判断する

## 第87問

必要選択数: 1

Query ProfileでJoinの入力は数万行ですが、出力が数千万行になっています。結合キーに重複があり、意図した「注文ごとに1行」より結果の粒度が細かくなっています。最初に行う対応として適切なものはどれですか。

### 選択肢

- A. Joinの条件と両入力の粒度を確認し、必要な集約や結合キーの修正を行う
- B. 結果の粒度を確認せずwarehouseを大きくする
- C. 同じSQLを再実行して結果キャッシュへの保存だけで根本原因を解消する
- D. 結合条件を取り除いてCROSS JOINへ変更する

## 第88問

必要選択数: 3

Trust Centerのprogrammatic notifications（Preview）を利用できる環境で、Accountのsecurity misconfigurationを継続検出し、critical findingをPagerDutyへ送り、UDF修正後の内部処理も追跡したい場合に必要なものを3つ選んでください。
### 選択肢
- A. Trust Center scanner
- B. `ALERT_HISTORY`をsourceにしたscheduled alert
- C. Notification integration
- D. `LOGIN_HISTORY`をsourceにしたsecurity alert
- E. Logging／tracingとevent table

## 第89問

必要選択数: 2

二社が顧客データを持ち寄り、承認された集計だけを共同実行したいと考えています。現行collaboration方式のSnowflake Data Clean Roomsを使います。正しい設計判断を2つ選んでください。

### 選択肢

- A. Ownerであればanalysis runner指定なしで全templateを実行できる
- B. Data offeringの公開先・policyと、runnerが使えるtemplateを設定する
- C. Private listingでtable全体を公開すれば集計だけに制約される
- D. 集計だけを返すよう出力条件を設計し、許可された分析で確認する

## 第90問

必要選択数: 3

複数databaseのPII columnを分類し、非承認roleには値を隠し、派生先への伝播影響を調べたい場合に選ぶものを3つ選んでください。
### 選択肢
- A. PII分類用のobject tag（sensitivity tag）
- B. Row access policyだけを各tableへ個別設定
- C. Tag-based masking policy
- D. Automatic Classificationだけ
- E. Data lineage

## 第91問

必要選択数: 2

Enterpriseの同じ顧客tableに対し、利用者には担当regionの行だけを返し、個人情報を参照できるrole以外にはemailの表示値を置き換えたいと考えています。Query時の制御として必要なものを2つ選んでください。

### 選択肢

- A. Region名のobject tagだけを付ける
- B. Row access policyで可視行を判定する
- C. Time Travelの保持期間を延ばす
- D. Masking policyでemailの返却値を制御する

## 第92問

必要選択数: 1

ファイルはすでにstageへuploadされていますが、cloud event notificationを使えません。外部applicationからファイル名を指定してpipeへ取り込みを依頼し、Snowflake管理のcomputeでロードしたいと考えています。適切な方式はどれですか。

### 選択肢

- A. Snowpipe REST APIでstageのファイルをロード依頼する
- B. User-managed warehouseでCOPYを実行する方式へ限定する
- C. Streamへファイル名をINSERTしてロードを起動する
- D. Snowpipe Streamingへstageのファイルpathだけを送る

## 第93問

必要選択数: 1

S3のbucketへ毎晩CSVが置かれます。cloud側の資格情報をSQL文へ残さず、複数のroleが同じ場所からロードできるようにします。最も適した構成はどれですか。
### 選択肢
- A. user stageへPUTし、各userが`COPY INTO`する
- B. storage integrationを参照するexternal stageを作り、必要なroleへ`USAGE`をgrantする
- C. external stageの定義にaccess keyを直接記述し、`READ`をgrantする
- D. table stageへS3のURLを設定して共有する

## 第94問

必要選択数: 1

運用担当者が、ローカルに開発ツールを導入せず、ブラウザーからSQLの結果を探索し、queryやwarehouseの稼働状態を画面で確認したいと考えています。中心となるインターフェースはどれですか。

### 選択肢

- A. Snowflake CLI
- B. Snowsight
- C. Visual Studio CodeのSnowflake拡張
- D. Snowpark API

## 第95問

必要選択数: 2

日次集約が遅く、単独実行でもaggregate nodeに大量のlocal・remote spillがある。overload queueはほぼゼロで、QASに伴う少量書き込みではない。原因に合う対策を2つ選べ。

2つ選んでください。

### 選択肢

- A. より大きなwarehouseでメモリーを増やす効果を評価する
- B. clusterを増やして当該クエリを全clusterへ分割する
- C. USE_CACHED_RESULTをFALSEにし、退避を抑える
- D. 入力を要件に沿って減らすかbatchを小さくする

## 第96問

必要選択数: 1

同じservice userが複数顧客部門のSQLを同じwarehouseで実行します。部門別にquery computeを報告し、idle費用は別途配賦する方針です。どの設計が適切ですか。

### 選択肢

- A. Warehouseに部門tagを一つ割り当て、WAREHOUSE_METERING_HISTORYを部門別query使用量として集計する
- B. Service userに部門tagを一つ割り当て、user別query使用量をその部門へ集計する
- C. SessionのQUERY_TAGを部門ごとに切り替え、QUERY_ATTRIBUTION_HISTORYでquery computeを分類する
- D. Custom budgetにwarehouseを個別追加し、その合計creditをqueryを実行した部門別に自動分割する

## 第97問

必要選択数: 1

Enterpriseで、普段は小さな問い合わせが多いwarehouseに、時々大規模scanと選択性の高いfilterを含むクエリが来る。warehouseの基本sizeを常時上げる運用を避け、必要なクエリの並列化できる部分に追加computeを使いたい。適切な次の手順はどれか。

1つ選んでください。

### 選択肢

- A. QASのeligible判定・時間見積りを確認し、有限scale factorで評価する
- B. 頻繁な範囲filterをkeyに選び、Automatic Clusteringで配置を維持する
- C. 反復する計算結果をmaterialized viewへ保存して維持する
- D. scale factorを0にしてQASの課金を停止する

## 第98問

必要選択数: 2

大規模スキャンを伴うクエリの改善候補としてQuery Acceleration Service（QAS）を検討しています。適切な判断を二つ選んでください。

### 選択肢

- A. 対象クエリの適格性と、改善効果に対する追加のserverless計算コストを確認する
- B. QASを有効にすればすべてのクエリで同じ割合の高速化が保証される
- C. 設定するscale factorは使用可能なQAS資源の上限を制御するもので、一定倍率の高速化を保証しない
- D. QASの利用料金はwarehouseの通常クレジットだけに含まれるため追加コストを検討しなくてよい

## 第99問

必要選択数: 1

account全体のsession timeout既定は維持しつつ、あるservice userの新規sessionだけ別の既定値にしたいと考えています。最も適切なlevelはどれですか。
### 選択肢
- A. Account
- B. User
- C. Session
- D. Warehouse

## 第100問

必要選択数: 3

Change trackingが有効なevent tableへ新しいerror rowが到着したときだけconditionを評価し、該当時にwebhookへ送信したい場合に必要なものを3つ選んでください。
### 選択肢
- A. Alert on new data
- B. 1分ごとのscheduled taskでtable全体を再scan
- C. Conditionとaction
- D. Webhook notification integration
- E. Email notification integrationだけ
