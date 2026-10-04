# SQL Command Reference — 目的と実行条件

> Status: complete

構文の全文ではなく、試験範囲の目的・重要option・実行文脈を整理します。以下は互いに独立した例で、全体を順番に実行するscriptではありません。`REF_`名は例示用です。既存objectのある演習用database・schemaを前提とする例では、名前を自分の環境へ置き換えます。

Object作成・ロード・refresh・queryはcreditやstorageを使用し得ます。変更例は演習用objectだけで試し、各章のミニハンズオンにある準備とcleanupを使ってください。`CREATE OR REPLACE`や`FORCE=TRUE`を手軽な再実行方法として使いません。SQLは公式構文との静的照合で確認し、Snowflake実環境では未実行です。

Objectiveに対応する本文は[Referenceの索引](README.md#objectiveから本文へ戻る)、Source IDのURLは[出典台帳](../docs/sources.json)を参照します。

## Contextと設定（1.3・2.3・4.3）

`USE ROLE`は利用者に付与されたaccount roleを選びます。Warehouse・database・schemaの選択には対象のUSAGE等が必要です。まず読み取りで現在値を確認します。

```sql
SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();
SHOW PARAMETERS LIKE 'USE_CACHED_RESULT' IN SESSION;
```

値を保持するSQL variableと、動作を変えるparameterを区別します。

```sql
SET ref_min_amount = 100;
SELECT $ref_min_amount AS min_amount;
ALTER SESSION SET QUERY_TAG = 'reference_review';
ALTER SESSION SET USE_CACHED_RESULT = FALSE;
```

`QUERY_TAG`はqueryの分類値です。Object tagではありません。`USE_CACHED_RESULT`をFALSEにしてもwarehouse cacheは無効になりません。復元は変更前の設定値に合わせます。

```sql
UNSET ref_min_amount;
ALTER SESSION UNSET QUERY_TAG;
ALTER SESSION UNSET USE_CACHED_RESULT;
```

この復元例は、変更前にsessionの明示設定がなかった場合です。明示設定があった場合は元の値へ戻します。

根拠: `docs-context-functions`, `docs-sql-variables`, `docs-parameters`, `docs-cost-attributing`。

## Warehouseのsizeと自動停止（1.4）

AccountのCREATE WAREHOUSEを持つroleで作成します。例はsingle-clusterを明示し、作成直後の稼働を避けます。

```sql
CREATE WAREHOUSE REF_WH
  WAREHOUSE_SIZE = 'XSMALL'
  MIN_CLUSTER_COUNT = 1 MAX_CLUSTER_COUNT = 1
  AUTO_SUSPEND = 60 AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;
```

Size変更にはwarehouseのMODIFY等が必要です。`WAREHOUSE_SIZE`は1 clusterの資源、`MIN_CLUSTER_COUNT`／`MAX_CLUSTER_COUNT`はcluster数です。後者を増やすmulti-clusterはEnterprise以上です。Query実行やresumeから課金が発生し得ます。

根拠: `docs-create-warehouse-c03`, `docs-multicluster-warehouses`, `docs-warehouse-considerations`。

## Roleとprivilegeのgrant（2.1）

以下は通常schema内の既存tableを読むroleの例です。各grantを行えるobject ownerまたはMANAGE GRANTS等の権限を持つ管理roleで実行します。Managed access schemaではgrantの管理主体が異なります。

```sql
GRANT USAGE ON DATABASE REF_DB TO ROLE REF_ANALYST;
GRANT USAGE ON SCHEMA REF_DB.PUBLIC TO ROLE REF_ANALYST;
GRANT SELECT ON TABLE REF_DB.PUBLIC.ORDERS TO ROLE REF_ANALYST;
GRANT USAGE ON WAREHOUSE REF_WH TO ROLE REF_ANALYST;
GRANT ROLE REF_ANALYST TO ROLE REF_TEAM;
```

最後の文では`REF_TEAM`が`REF_ANALYST`の権限を継承します。Database roleは、例えば`GRANT DATABASE ROLE REF_DB.READ_DATA TO ROLE REF_ANALYST`でaccount roleへ渡します。Database・schemaのUSAGEだけではtableへのSELECTを与えません。

根拠: `docs-access-control-overview`, `docs-access-control-best-practices`, `docs-access-control-privileges`。

## 使用量を調べる（2.3・4.1）

SNOWFLAKE databaseの対象viewへの参照権限を持つroleと、query用warehouseで実行します。

```sql
SELECT warehouse_name, SUM(credits_used_compute) AS compute_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
GROUP BY warehouse_name;
```

これはwarehouseの測定compute creditです。Viewのlatencyがあり、即時の請求額ではありません。Queryごとの配賦を知る場合は`QUERY_ATTRIBUTION_HISTORY`を使い、idleやQASのcreditを別に扱います。部門別のtag join・budget操作は[2.3の本文](../textbook/domain-2/03-monitoring-cost.md)を参照します。

根拠: `docs-warehouse-metering-history`, `docs-query-attribution-history`, `docs-account-usage`, `docs-cost-attributing`。

## StageのファイルとCOPY（3.1）

既存named internal stage `REF_DB.PUBLIC.REF_STAGE`、CSV形式と一致する既存table `REF_DB.PUBLIC.ORDERS`を前提にします。StageのREAD、tableのINSERT、親database・schemaとwarehouseのUSAGE等が必要です。

```sql
COPY INTO REF_DB.PUBLIC.ORDERS
FROM @REF_DB.PUBLIC.REF_STAGE
FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1)
VALIDATION_MODE = 'RETURN_ERRORS';
```

検証はロードしません。変換SELECT付きCOPYでは`VALIDATION_MODE`は使えません。File formatとtableへの対応を確認後、独立したロード例は次の形です。

```sql
COPY INTO REF_DB.PUBLIC.ORDERS
FROM @REF_DB.PUBLIC.REF_STAGE
FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1)
ON_ERROR = 'ABORT_STATEMENT';
```

`ON_ERROR`はerror時の方針、`FORCE`はロード履歴にかかわらず再ロードする指定です。`FORCE=TRUE`は重複につながり得ます。`VALIDATE()`は過去の対応するCOPYのerror調査に使います。

PUT／GETは対応clientで実行するファイル転送です。Local pathはclient側であり、SnowsightのSQLでlocalファイルを直接送る例ではありません。PUT先・GET元はinternal stageです。PUTにはstageのWRITE（およびREAD）、GETにはREAD等が必要です。

```sql
PUT file:///tmp/reference/orders.csv @REF_DB.PUBLIC.REF_STAGE;
GET @REF_DB.PUBLIC.REF_STAGE file:///tmp/reference/download/;
```

アンロードの例では元tableのSELECT、named internal stageのWRITE／READ、親object・warehouseのUSAGE等が必要です。

```sql
COPY INTO @REF_DB.PUBLIC.REF_STAGE/export/
FROM (SELECT * FROM REF_DB.PUBLIC.ORDERS)
FILE_FORMAT = (TYPE = PARQUET);
```

外部stageの場合はREAD／WRITEではなくUSAGEとcloud側のアクセスを確認します。Storage integrationの利用を含む準備は[3.1](../textbook/domain-3/01-loading-unloading.md)・[3.3](../textbook/domain-3/03-connectors-integrations.md)を参照します。

根拠: `docs-copy-into-table`, `docs-copy-into-location`, `docs-put`, `docs-get`, `docs-validate-function`, `docs-access-control-privileges`。

## Stream・Task・Dynamic Table（3.2）

Sourceはchange trackingを有効化済みの既存標準tableとし、SELECT、親containerのUSAGEとschemaのCREATE STREAM等を持つroleで作成します。Change trackingが未設定なら、初回streamの作成にはtableのOWNERSHIPが必要です。

```sql
CREATE STREAM REF_DB.PUBLIC.ORDERS_CHANGES
  ON TABLE REF_DB.PUBLIC.ORDERS;
SELECT * FROM REF_DB.PUBLIC.ORDERS_CHANGES;
```

SELECTだけではstreamのoffsetを進めません。Streamを入力にするDMLがtransactionでcommitすると進みます。複数の独立consumerは別streamを使う設計を検討します。

Taskは作成後suspendedです。以下は準備済みのtaskを動かす操作で、OWNERSHIP、またはOPERATEと親containerのUSAGEが必要です。Owner roleにはEXECUTE TASK、処理するobjectとwarehouseの権限等が必要です。Serverlessの場合はEXECUTE MANAGED TASK等の条件も確認します。SUSPENDは新しい予定実行を止めますが、実行中のtaskをcancelする操作ではありません。

```sql
ALTER TASK REF_DB.PUBLIC.REF_TASK RESUME;
ALTER TASK REF_DB.PUBLIC.REF_TASK SUSPEND;
```

宣言的な変換では、schemaのCREATE DYNAMIC TABLE、source SELECT、親container・refresh用warehouseのUSAGE等を持つroleで次のように定義します。Sourceのchange trackingは準備済みとします。

```sql
CREATE DYNAMIC TABLE REF_DB.PUBLIC.ORDER_TOTALS
  TARGET_LAG = '10 minutes'
  WAREHOUSE = REF_WH
  REFRESH_MODE = AUTO
AS SELECT customer_id, SUM(amount) AS total_amount
   FROM REF_DB.PUBLIC.ORDERS
   GROUP BY customer_id;
```

`AUTO`のrefresh方式は作成時に解決されます。Target lagは目標で、refreshを必ず10分間隔で実行する設定ではありません。作成時の初期refreshと以後の処理にもcompute・storageを使います。

根拠: `docs-create-stream`, `docs-streams-intro`, `docs-tasks-intro`, `docs-create-task`, `docs-dynamic-tables`, `docs-dt-refresh-modes`, `docs-create-dynamic-table-reference`。

## 最適化のoptionを読む（4.2）

各例は独立しています。QASとSearch OptimizationはEnterprise以上です。対象warehouseのMODIFY／tableのOWNERSHIP等、機能に応じた権限が必要です。追加serverless compute・storageを使い得るため、Profile等で必要性を確認します。

```sql
ALTER WAREHOUSE REF_WH SET
  ENABLE_QUERY_ACCELERATION = TRUE
  QUERY_ACCELERATION_MAX_SCALE_FACTOR = 2;
ALTER TABLE REF_DB.PUBLIC.ORDERS ADD SEARCH OPTIMIZATION;
ALTER TABLE REF_DB.PUBLIC.ORDERS CLUSTER BY (customer_id);
```

QASはeligibleな処理だけを加速し、scale factorは性能倍率の保証ではありません。Search Optimizationは検索構造、clustering keyは配置を改善します。QASの有効化やscale factorの既定値には構成による差があるため、例では明示しています。

根拠: `docs-query-acceleration`, `docs-search-optimization`, `docs-clustering-keys`。

## JSONとwindowを読む（4.4）

次の例は永続objectを作りません。SQL実行用warehouseのUSAGE等を持つroleで確認できます。

```sql
WITH src AS (
  SELECT PARSE_JSON('{"items":[{"amount":10},{"amount":20}]}') AS payload
)
SELECT f.value:amount::NUMBER AS amount
FROM src, LATERAL FLATTEN(INPUT => src.payload:items) f;
```

期待する値は10と20の2行です。ARRAY展開後の行数を、元データの件数と混同しません。

```sql
WITH orders AS (
  SELECT column1 AS customer_id, column2 AS order_id, column3 AS amount
  FROM VALUES ('A', 1, 200), ('A', 2, 200), ('B', 3, 50)
)
SELECT customer_id, order_id, amount
FROM orders
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY customer_id ORDER BY amount DESC, order_id DESC
) = 1;
```

期待結果はAのorder_id=2とBのorder_id=3です。Order_idをtie-breakerに使い、同額でも1件を選びます。同額の最高値をすべて返すには、QUALIFYの条件を`RANK() OVER (PARTITION BY customer_id ORDER BY amount DESC) = 1`へ変更し、order_idを並べ替え条件から外します。この場合はAの2行とBの1行を返します。Order_idを残したままROW_NUMBERだけをRANKへ置き換えても、Aの2行は同順位にならず、返るのはorder_id=2の1行です。

根拠: `docs-query-semistructured`, `docs-flatten`, `docs-window-functions`, `docs-qualify`, `docs-rank`。

## 過去状態・clone・復元（5.1）

以下は独立した操作例です。既存tableのSELECT、query用warehouseと親containerのUSAGE等が必要です。過去の時点が有効なTime Travel保持期間内であることを確認します。

```sql
SELECT * FROM REF_DB.PUBLIC.ORDERS AT (OFFSET => -300);
```

Clone作成にはsourceのSELECT、作成先schemaのCREATE TABLE、親containerのUSAGE等が必要です。

```sql
CREATE TABLE REF_DB.PUBLIC.ORDERS_CLONE
  CLONE REF_DB.PUBLIC.ORDERS COPY GRANTS;
```

`COPY GRANTS`はOWNERSHIPをコピーしません。標準tableの初期partitionは共有され、変更は独立します。保持期間・変更に伴うstorage費用があります。

`UNDROP TABLE ORDERS`は、実際にDROPされ保持期間内にあるtableだけが対象です。復元先の元database・schemaをsession contextとして選び、対象のOWNERSHIPとschemaのCREATE TABLE、親containerの権限等を確認します。同名objectが存在すると衝突します。この例のために既存tableをDROPしません。

根拠: `docs-time-travel`, `docs-clone-command`, `docs-clone-storage`, `docs-undrop-table-reference`。

## Shareとconsumerの権限（5.2）

Providerはshareと対象objectを管理できるroleで、database・schemaのUSAGEと対象table／secure viewのSELECT等をshareへgrantします。Consumerへ公開するまでの一式は[5.2の本文](../textbook/domain-5/02-data-sharing.md)を参照します。

Consumer側でdatabase roleを使わない共有を利用する独立例は次の形です。作成にはCREATE DATABASEとIMPORT SHARE等、grantには対象の管理権限が必要です。`provider_locator.ref_share`はSHOW SHARESで確認したprovider identifierとshare名へ置き換えます。

```sql
CREATE DATABASE REF_IMPORTED
  FROM SHARE provider_locator.ref_share;
GRANT IMPORTED PRIVILEGES ON DATABASE REF_IMPORTED TO ROLE REF_ANALYST;
GRANT USAGE ON WAREHOUSE REF_WH TO ROLE REF_ANALYST;
```

共有元がdatabase roleで公開する場合は、imported database roleをaccount roleへgrantする方式を使います。Imported databaseは読取り専用です。許可された再共有でもincoming objectを直接自分のshareへgrantせず、自分のsecure viewとproviderの条件を確認します。

根拠: `docs-grant-share`, `docs-sharing-consumer`, `docs-resharer`, `docs-create-database-reference`。
