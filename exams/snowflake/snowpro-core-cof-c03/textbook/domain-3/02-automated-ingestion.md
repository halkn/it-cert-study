# 3.2 自動データ取り込みを実行する

> Status: complete
> Last verified: 2026-08-30

## この章で学ぶこと

この章を終えると、次を説明・選択できます。

- SnowpipeとbulkのCOPYを、compute、課金、順序保証、重複回避の履歴期間で区別する
- Snowpipeのauto-ingestとREST APIの2方式と、pipeの状態確認方法を説明する
- Snowpipe Streamingがファイルではなく行を取り込む方式であることを説明する
- StreamのoffsetがいつDMLで進むか、いつstaleになるかを説明する
- Taskのschedule／DAG、serverlessとuser-managed warehouseの違いを説明する
- Dynamic Tableの宣言的なtarget lagと、stream + taskの手続き的な組合せを使い分ける
- Openflowの位置付けとデプロイ形態を識別する

## 前提知識

- [3.1](01-loading-unloading.md)のstage、file format、`COPY INTO`、`ON_ERROR`
- [1.4 Virtual Warehouse](../domain-1/04-virtual-warehouses.md)のsizeとcredit
- [1.5 ストレージ概念](../domain-1/05-storage-concepts.md)のtable種別とdata retention
- [2.3 監視とコスト管理](../domain-2/03-monitoring-cost.md)のcreditとAccount Usage

## この章の用語

| 用語 | この章での意味 |
|---|---|
| pipe | `COPY INTO <table>`文を保持し、Snowpipeのロードを定義するschema-level object |
| auto-ingest | Cloud storageのevent notificationを起点にpipeへロードを依頼する方式 |
| serverless compute | Snowflakeが管理し、利用量で課金されるcompute。Warehouseを指定しない |
| channel | Snowpipe Streamingでclientとtableを結ぶ、行を書き込むための論理接続 |
| stream | Objectの変更をCDCとして返すschema-level object |
| offset | Streamが「どこまで消費済みか」を示すtransaction versionの位置 |
| stale | Streamのoffsetがsource objectのdata retention範囲を外れ、変更を返せなくなった状態 |
| task | SQLやprocedureをscheduleまたは依存関係で実行するschema-level object |
| task graph | Root taskとその後続taskで構成されるDAG |
| target lag | Dynamic Tableがbase dataに対して目標とする鮮度 |

## 試験範囲との対応

| Topic | 本文 | 主な公式根拠 |
|---|---|---|
| Snowpipe | [ファイル到着を起点に継続ロードする](#snowpipe) | `docs-snowpipe-intro`, `docs-snowpipe-auto`, `docs-create-pipe` |
| Snowpipe Streaming | [ファイルを作らず行を直接書き込む](#snowpipe-streaming) | `docs-snowpipe-streaming-overview` |
| Stream | [変更をoffsetで追跡する](#streams) | `docs-streams-intro`, `docs-streams`, `docs-create-stream` |
| Task | [処理をscheduleと依存関係で動かす](#tasks) | `docs-tasks-intro`, `docs-create-task`, `docs-tasks-graphs` |
| Dynamic Table | [結果の鮮度を宣言して維持させる](#dynamic-tables) | `docs-dynamic-tables`, `docs-dt-refresh-modes` |
| Openflow | [外部systemとの接続をNiFiベースで統合する](#openflow) | `docs-openflow-about` |

公式ObjectiveとTopicは[COF-C03 Syllabus](../../docs/syllabus.md#32-自動データ取り込みを実行する)から公式Study Guideへ辿って確認できます。

## 自動化は「何が引き金になるか」で分かれる

3.1の`COPY INTO`は、人またはjob schedulerが実行する文でした。この章の機能は、その実行の引き金を別のものに置き換えます。引き金の違いが、そのまま選定基準になります。

| 引き金 | 機能 | 取り込む単位 |
|---|---|---|
| Stageへのファイル到着 | Snowpipe | ファイル |
| Client applicationからの書き込み | Snowpipe Streaming | 行 |
| Source objectの変更 | Stream（変更の検知） | 変更レコード |
| 時刻または先行taskの完了 | Task（処理の実行） | 任意のSQL |
| 目標の鮮度から逆算した自動refresh | Dynamic Table | Query結果全体 |
| 外部systemとのconnector flow | Openflow | Flowの定義による |

StreamとTaskは対になる部品です。Streamは「何が変わったか」を答えるだけで、それ自体は何も実行しません。実行はTaskが担います。

[図を開く: 取り込み方式の選定](../../diagrams/domain-3/ingestion-selection.md)

<a id="snowpipe"></a>
## Snowpipe — ファイル到着を起点に継続ロードする

Snowpipeは、stageへ置かれたファイルを到着後まもなくロードする仕組みです。ロード内容はpipe objectが保持する`COPY INTO <table>`文で定義します。

```sql
CREATE PIPE orders_pipe
  AUTO_INGEST = TRUE
AS
COPY INTO orders
FROM @s3_landing/orders/
FILE_FORMAT = (FORMAT_NAME = my_csv_format);
```

### Bulk COPYとの違いを4点で押さえる

| 観点 | Bulk load（`COPY INTO`） | Snowpipe |
|---|---|---|
| Compute | User-specified warehouseが必要 | Snowflakeが提供するcompute（serverless） |
| 課金 | Warehouseがactiveだった時間 | ロードしたデータ量（GB）あたりの固定credit額 |
| ロード順序 | 文単位で明示的に制御 | 古いファイルを先に読む傾向はあるが、stageされた順序でロードされる保証はない |
| 重複回避のmetadata | Target tableのload historyで64日 | Pipeのmetadataで14日 |

「serverlessだから無料」ではありません。Warehouseを自分で用意・起動しなくてよいだけで、取り込みには課金されます。現行のSnowpipe課金は、ロードしたデータ量1 GBあたりの固定credit額です。compute資源をper-second／per-coreで測り、1,000ファイルあたりの手数料を加える方式は旧モデルとされています。使用量は`PIPE_USAGE_HISTORY`の`BYTES_BILLED`などで確認します。

もう一点、Snowpipeが使う内部のcomputeにはResource Monitorが効きません。Resource Monitorはuser-managed warehouseを対象とする機能だからです（[2.3](../domain-2/03-monitoring-cost.md#resource-monitors)）。

### Auto-ingestとREST APIの2方式

- **Auto-ingest**: cloud storageのevent notification（Amazon S3 event notification、Azure Event Grid、Google Pub/Sub）を受けて、対象ファイルをingest queueへ入れます。`AUTO_INGEST = TRUE`で有効にし、cloud側の通知設定とnotification integrationが必要です。
- **REST API**: clientが`insertFiles`エンドポイントをpipe名とファイル一覧で呼び出します。sessionを維持しないため、認証はkey-basedの方式を使います。`AUTO_INGEST = FALSE`のpipeはこの呼び出しで動きます。

Pipeをpauseしている間、event notificationが保持されるのは14日です。それを超えるとpipeはstaleになり、古い通知の処理は保証されません。Pipeが取りこぼしたファイルを取り込み直すには`ALTER PIPE ... REFRESH`を使いますが、対象にできるのは直近7日以内にstageされたファイルです。

### Snowpipeの状態を確認する

```sql
SELECT SYSTEM$PIPE_STATUS('orders_pipe');
ALTER PIPE orders_pipe REFRESH;
```

`SYSTEM$PIPE_STATUS`はJSONで`executionState`（`RUNNING`、`PAUSED`など）、`pendingFileCount`、`lastIngestedTimestamp`などを返します。実行にはpipeのOWNERSHIPまたは`MONITOR`が必要です。ロード結果の履歴は、3.1で扱った`COPY_HISTORY`で確認します。`LOAD_HISTORY`はSnowpipeのロードを返しません。

`ON_ERROR`の既定値がbulk loadと異なる点も再確認します。Bulk loadは`ABORT_STATEMENT`、Snowpipeは`SKIP_FILE`です。

ファイル到着の頻度は、1分に1回程度を目安にします。細かすぎるファイルはファイルごとのoverheadが積み上がり、大きすぎるファイルは遅延を増やします。

<a id="snowpipe-streaming"></a>
## Snowpipe Streaming — ファイルを作らず行を直接書き込む

Snowpipe Streamingは、ファイルをstageへ置かずに、行が届いた順にtableへ書き込むAPIです。「ファイル単位か、行単位か」がSnowpipeとの最大の違いです。

Kafkaのtopic、IoT device、application eventのように、そもそもファイルという単位を持たないデータで遅延を短くしたい場合に選びます。逆に、既にcloud storageへファイルが置かれている構成ではSnowpipeが素直です。

Client側にはSnowflake Ingest SDK（Java、Python、Node.js）、REST API、Snowflake Connector for Kafkaのいずれかを使います。課金は、取り込んだ非圧縮データ量あたりのcreditで計算されるthroughputベースです。

現行の高性能アーキテクチャではpipe objectを使い、channelがoffset tokenによって重複のない書き込みと順序を扱います。従来のclassic architectureはpipe objectを使わず、channelをtableへ直接構成します。classicは引き続きサポートされますが将来の廃止が予告されており、新規構成では高性能アーキテクチャを前提にします（2026-08-30時点の公式docs記載）。

<a id="streams"></a>
## Stream — 変更をoffsetで追跡する

Streamは、tableなどのobjectに対するDML変更（INSERT、UPDATE、DELETE）を、変更レコードとして返すobjectです。

### Streamはデータを持たない

Stream自体はtableのデータを一切保持しません。保持するのはoffset、つまり「source objectのどのtransaction versionまでを消費済みとみなすか」という位置だけです。変更レコードは、offset以降のversioning履歴から都度生成されます。

この構造から2つの帰結があります。1つ目は、streamに変更が「溜まっている」わけではないこと。2つ目は、source objectのdata retentionを超えた過去は再現できないことです。

### 返される変更レコードの読み方

Streamをqueryすると、source objectの列に加えて次のmetadata列が付きます。

| 列 | 意味 |
|---|---|
| `METADATA$ACTION` | その行に対するDML操作。`INSERT`または`DELETE` |
| `METADATA$ISUPDATE` | `UPDATE`の一部だったか。`UPDATE`は削除行と挿入行のペアとして記録され、そのとき`TRUE`になる |
| `METADATA$ROW_ID` | 行を追跡する一意で不変のID |

`UPDATE`という`METADATA$ACTION`の値は存在しません。更新は`DELETE`と`INSERT`のペアで表され、`METADATA$ISUPDATE = TRUE`で識別します。

### 3種類のstream

| 種類 | 追跡する変更 | 主な対象 |
|---|---|---|
| Standard | INSERT、UPDATE、DELETEのすべて | Table、dynamic table、Snowflake管理のIcebergテーブル、directory table、view |
| Append-only | INSERTのみ。update／delete／truncateは返さない | Table、dynamic table、Snowflake管理のIcebergテーブル、view |
| Insert-only | INSERTのみ。deleteは返さない | External table、外部管理のIcebergテーブルなど |

```sql
CREATE STREAM orders_stream ON TABLE orders;
CREATE STREAM orders_append_stream ON TABLE orders APPEND_ONLY = TRUE;
```

`APPEND_ONLY`と`SHOW_INITIAL_ROWS`はいずれも既定`FALSE`です。追記だけを扱う要件でappend-onlyを選ぶと、削除行を無視できる分だけ処理が単純になります。

### Offsetが進むのはDMLで消費したときだけ

Streamのoffsetは、そのstreamをDML transactionで使ったときに進みます。`INSERT ... SELECT FROM stream`や`CREATE TABLE AS SELECT`がこれにあたります。

**Streamを`SELECT`しただけではoffsetは進みません。** 明示的なtransaction内でqueryしても同じです。「確認のためにSELECTしたら消費された」という理解は誤りで、逆に「SELECTを繰り返しても同じ変更が返り続ける」が正しい挙動です。

```sql
-- 消費されない（何度でも同じ結果）
SELECT * FROM orders_stream;

-- 消費される（offsetが進む）
INSERT INTO orders_history SELECT * FROM orders_stream;
```

### Staleを避ける

Offsetがsource objectのdata retention期間の外へ出ると、streamはstaleになり変更を返せなくなります。未消費のstreamがある場合、Snowflakeはretention期間を一時的に延長してstale化を防ぎますが、延長できる上限は`MAX_DATA_EXTENSION_TIME_IN_DAYS`が決め、既定は14日です。

長期間消費されないstreamは、この延長期間を過ぎるとstaleになります。したがってstreamは「作って放置する」ものではなく、消費するtaskとセットで運用します。`SYSTEM$STREAM_HAS_DATA('<stream>')`で消費すべき変更の有無を判定できます。

<a id="tasks"></a>
## Task — 処理をscheduleと依存関係で動かす

Taskは、SQL文、stored procedure、Snowflake Scripting blockを、時刻または先行taskの完了を引き金に実行します。

```sql
CREATE TASK load_orders_task
  WAREHOUSE = etl_wh
  SCHEDULE = 'USING CRON 0 * * * * UTC'
  WHEN SYSTEM$STREAM_HAS_DATA('orders_stream')
AS
  INSERT INTO orders_history SELECT * FROM orders_stream;

ALTER TASK load_orders_task RESUME;
```

### 作成しただけでは動かない

**新しく作成したtaskはsuspended状態です。** `ALTER TASK ... RESUME`でscheduleを有効にするまで実行されません。単発で試すなら`EXECUTE TASK`を使います。この点は設問で頻出します。

### ScheduleとAFTERは別の起動条件

- `SCHEDULE`: `'USING CRON <expr> <timezone>'`（分・時・日・月・曜日の5フィールド）または`'<num> MINUTES'`のような間隔指定。
- `AFTER <task>`: 先行taskを指定し、その完了後に実行します。これを連ねるとtask graph（DAG）になります。

Task graphのscheduleはroot taskが持ちます。子taskに`SCHEDULE`は付けません。Task graphは最大1,000 tasks、1つのtaskが持てる親taskと子taskはそれぞれ最大100です。既定では、連続して10回失敗するとtask graphはsuspendされます。

`WHEN`は実行するかどうかの条件です。`WHEN SYSTEM$STREAM_HAS_DATA('orders_stream')`と書くと、変更がないときはcompute資源を使わずにスキップされます。Stream + taskのpipelineでは、この組合せがcost効率の要になります。

### Serverless taskとuser-managed task

| 種類 | 指定 | 課金 |
|---|---|---|
| User-managed task | `WAREHOUSE = <name>` | 指定したwarehouseがactiveだった時間 |
| Serverless task | `WAREHOUSE`を指定しない。任意で`USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE` | 使ったcompute資源（compute-hours） |

Serverless taskは、Snowflakeが必要なsizeを調整します。初期sizeのヒントを与えるのが`USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE`です。短時間で終わるtaskをwarehouseの起動待ちなしに動かしたい場合はserverless、既存warehouseのworkloadへまとめたい場合はuser-managedを選びます。

権限も分かれます。作成にはschemaの`CREATE TASK`、user-managed taskではwarehouseへの`USAGE`が必要です。実行にはaccount-levelの`EXECUTE TASK`、serverless taskでは`EXECUTE MANAGED TASK`が必要です。実行履歴は`TASK_HISTORY`で確認します。

<a id="dynamic-tables"></a>
## Dynamic Table — 結果の鮮度を宣言して維持させる

Dynamic Tableは、`SELECT`とtarget lagを宣言すると、Snowflakeが依存関係を追跡してrefreshを実行するtableです。

```sql
CREATE DYNAMIC TABLE daily_orders
  TARGET_LAG = '10 minutes'
  WAREHOUSE = transform_wh
AS
SELECT order_date, region, SUM(amount) AS total
FROM orders
GROUP BY order_date, region;
```

### Target lagは鮮度の目標を表す

`TARGET_LAG = '10 minutes'`は「base dataに対する遅れを10分以内に保とうとする」という宣言です。refreshの時刻や回数を指定するのではありません。指定できる最小のtarget lagは60秒です。

中間のdynamic tableには`TARGET_LAG = DOWNSTREAM`を指定できます。これは「下流が新しいデータを必要とするときにだけrefreshする」という意味で、参照されない中間結果の無駄なrefreshを避けます。

### Incremental refreshとfull refresh

`REFRESH_MODE`は`AUTO`、`INCREMENTAL`、`FULL`などから選びます。`AUTO`は**作成時に一度だけ**定義を評価して`INCREMENTAL`か`FULL`へ解決し、解決後は固定されます。運用中にデータ量が変わっても自動で切り替わりません。モードを変えるには`CREATE OR ALTER`または`CREATE OR REPLACE`が必要で、`ALTER DYNAMIC TABLE`では変更できません。

Incremental refreshは、定義がincremental対応の構文だけで書かれている場合に、変更分だけを処理します。Full refreshは定義全体を再実行して結果を置き換えます。

### Stream + taskとの使い分け

| 観点 | Dynamic Table | Stream + Task |
|---|---|---|
| 記述 | 目標状態（`SELECT`とtarget lag）を宣言する | 変更検知と処理手順を自分で組む |
| 依存関係 | Queryから自動で推論し、順序どおりrefreshする | Task graphで自分が定義する |
| 変更の扱い | `METADATA$`列を意識しない | 変更レコードを直接扱える |
| 向く要件 | 集約やjoinの結果を一定の鮮度で保ちたい | 変更ごとに独自ロジックや外部呼び出しを行いたい |

Dynamic Tableの定義ではstored procedureと外部関数を使えません。手続き的な処理が必要ならstream + taskを選びます。

<a id="openflow"></a>
## Openflow — 外部systemとの接続をNiFiベースで統合する

OpenflowはApache NiFi上に構築された統合サービスで、多数のprocessorを組み合わせて任意のデータソースと宛先を接続します。構造化データだけでなく、テキスト、画像、音声、動画、センサーデータも扱います。

デプロイ形態は2つです。

| 形態 | 実行場所 |
|---|---|
| Openflow — Snowflake Deployment | Snowpark Container Services上でSnowflakeが実行する |
| Openflow — BYOC（Bring Your Own Cloud） | 利用者自身のcloud環境で実行し、control planeはSnowflakeが管理する |

2026-08-30時点の公式docsでは、Openflowは Generally Available で、Snowflake DeploymentはAWS、Azure、GCPのcommercial regionで、BYOCはAWSのcommercial regionで利用できます。「BYOCならどのcloudでも使える」わけではない点に注意します。

この章のほかの機能がSnowflake内部の取り込み・変換であるのに対し、Openflowは外部systemとの接続そのものを設計・運用する層です。試験範囲としての扱いは、受験前に最新のStudy Guideで確認してください。

## Mini hands-on — stream + taskで増分を反映する

Streamで変更を検知し、変更があるときだけtaskで反映します。

```sql
CREATE STREAM orders_stream ON TABLE orders;

CREATE TASK apply_orders
  WAREHOUSE = etl_wh
  SCHEDULE = '5 MINUTES'
  WHEN SYSTEM$STREAM_HAS_DATA('orders_stream')
AS
  INSERT INTO orders_history
  SELECT order_id, amount, METADATA$ACTION, METADATA$ISUPDATE
  FROM orders_stream;

ALTER TASK apply_orders RESUME;

SELECT SYSTEM$STREAM_HAS_DATA('orders_stream');
SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
  TASK_NAME => 'APPLY_ORDERS'));
```

`RESUME`を忘れるとtaskは動きません。`TASK_HISTORY`に実行行が出ないときは、まずtaskの状態と`WHEN`条件を確認します。

## Compare — 要件から取り込み方式を選ぶ

| 要件 | 選ぶもの |
|---|---|
| S3へ置かれたファイルを数分以内にロードしたい | Snowpipe（auto-ingest） |
| Warehouseを自分で用意せずファイルを継続ロードしたい | Snowpipe |
| 独自のscheduleでまとめてロードし、順序を制御したい | Bulk `COPY INTO` |
| Applicationから行単位で低遅延に書き込みたい | Snowpipe Streaming |
| Tableの変更行だけを取り出して独自処理したい | Stream |
| 変更があるときだけ処理を走らせたい | Task + `WHEN SYSTEM$STREAM_HAS_DATA()` |
| 依存する複数の処理を順序どおり実行したい | Task graph（`AFTER`） |
| 集約結果を10分以内の鮮度で自動的に保ちたい | Dynamic Table（`TARGET_LAG`） |
| Warehouseの起動を管理せず短いtaskを回したい | Serverless task |
| 多様な外部systemとのconnector flowを構築したい | Openflow |

## 試験で重要なポイント

- Snowpipeはserverless computeを使い、warehouseを指定しない。課金は発生する。
- Snowpipeはロード順序を保証せず、重複回避のpipe metadataは14日保持（bulk loadは64日）。
- `ON_ERROR`既定はbulk loadが`ABORT_STATEMENT`、Snowpipeが`SKIP_FILE`。
- StreamのoffsetはDMLで消費したときだけ進む。`SELECT`では進まない。
- Streamはデータを保持せず、offsetとsourceの変更履歴から変更レコードを生成する。
- `METADATA$ACTION`は`INSERT`と`DELETE`だけ。更新は`METADATA$ISUPDATE = TRUE`で表す。
- 作成直後のtaskはsuspended。`ALTER TASK ... RESUME`が必要。
- Dynamic Tableの`REFRESH_MODE = AUTO`は作成時に解決され、以後固定される。

## 間違えやすいポイント

- 「serverless＝無課金」と読み替えない。Snowpipeもserverless taskも利用量で課金される。
- SnowpipeのcomputeはResource Monitorの対象外である。
- Streamを`SELECT`しただけでは消費にならない。
- Streamのstale化は`MAX_DATA_EXTENSION_TIME_IN_DAYS`（既定14日）を超えた放置で起きる。
- Task graphのscheduleはroot taskだけが持つ。子taskは`AFTER`で繋ぐ。
- Dynamic Tableのtarget lagはrefresh間隔の指定ではなく、鮮度の目標である。
- OpenflowのBYOCはAWSのcommercial regionが対象で、全cloudではない。

## 確認問題

- [C3-3.2-Q01: Snowpipeとbulk loadのcompute](../../exercises/chapter/c3-3.2-q01.md)
- [C3-3.2-Q02: Snowpipeのロード順序と重複回避](../../exercises/chapter/c3-3.2-q02.md)
- [C3-3.2-Q03: Snowpipeの起動方式](../../exercises/chapter/c3-3.2-q03.md)
- [C3-3.2-Q04: Snowpipe Streamingの取り込み単位](../../exercises/chapter/c3-3.2-q04.md)
- [C3-3.2-Q05: Streamが保持するもの](../../exercises/chapter/c3-3.2-q05.md)
- [C3-3.2-Q06: Stream offsetの進み方](../../exercises/chapter/c3-3.2-q06.md)
- [C3-3.2-Q07: Streamのmetadata列](../../exercises/chapter/c3-3.2-q07.md)
- [C3-3.2-Q08: Append-only stream](../../exercises/chapter/c3-3.2-q08.md)
- [C3-3.2-Q09: Task作成直後の状態](../../exercises/chapter/c3-3.2-q09.md)
- [C3-3.2-Q10: Serverless taskとuser-managed task](../../exercises/chapter/c3-3.2-q10.md)
- [C3-3.2-Q11: Task graphの構成](../../exercises/chapter/c3-3.2-q11.md)
- [C3-3.2-Q12: Dynamic Tableのtarget lag](../../exercises/chapter/c3-3.2-q12.md)
- [C3-3.2-Q13: Dynamic Tableとstream + task](../../exercises/chapter/c3-3.2-q13.md)
- [C3-3.2-Q14: Openflowのデプロイ形態](../../exercises/chapter/c3-3.2-q14.md)

## 章のまとめ

- 自動取り込みは引き金で分類できる。ファイル到着はSnowpipe、行の到着はSnowpipe Streaming、変更はStream、時刻と依存はTask、鮮度目標はDynamic Table。
- Snowpipeはwarehouseを指定しないが課金され、順序保証がなく、重複回避の履歴は14日である。
- Streamはoffsetだけを持ち、DMLで消費されたときにoffsetが進む。
- Taskは作成直後suspendedで、`RESUME`と権限（`EXECUTE TASK`／`EXECUTE MANAGED TASK`）が要る。
- Dynamic Tableは宣言的、stream + taskは手続き的であり、外部呼び出しや独自ロジックが要るなら後者を選ぶ。

## 次に学ぶこと

[3.3 Connectorとintegrationを識別する](03-connectors-integrations.md)では、この章で扱ったpipelineが外部のapplicationやcloud serviceと接続するための、driver、connector、integration objectを整理します。

## 根拠・関連する公式ドキュメント

- `docs-snowpipe-intro` — https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro
- `docs-snowpipe-auto` — https://docs.snowflake.com/en/user-guide/data-load-snowpipe-auto
- `docs-snowpipe-rest` — https://docs.snowflake.com/en/user-guide/data-load-snowpipe-rest-overview
- `docs-create-pipe` — https://docs.snowflake.com/en/sql-reference/sql/create-pipe
- `docs-alter-pipe` — https://docs.snowflake.com/en/sql-reference/sql/alter-pipe
- `docs-system-pipe-status` — https://docs.snowflake.com/en/sql-reference/functions/system_pipe_status
- `docs-snowpipe-billing` — https://docs.snowflake.com/en/user-guide/data-load-snowpipe-billing
- `docs-snowpipe-streaming-overview` — https://docs.snowflake.com/en/user-guide/snowpipe-streaming/data-load-snowpipe-streaming-overview
- `docs-streams-intro` — https://docs.snowflake.com/en/user-guide/streams-intro
- `docs-streams` — https://docs.snowflake.com/en/user-guide/streams
- `docs-create-stream` — https://docs.snowflake.com/en/sql-reference/sql/create-stream
- `docs-tasks-intro` — https://docs.snowflake.com/en/user-guide/tasks-intro
- `docs-create-task` — https://docs.snowflake.com/en/sql-reference/sql/create-task
- `docs-tasks-graphs` — https://docs.snowflake.com/en/user-guide/tasks-graphs
- `docs-dynamic-tables` — https://docs.snowflake.com/en/user-guide/dynamic-tables/overview
- `docs-dt-refresh-modes` — https://docs.snowflake.com/en/user-guide/dynamic-tables/refresh-modes
- `docs-openflow-about` — https://docs.snowflake.com/en/user-guide/data-integration/openflow/about
- `docs-copy-history` — https://docs.snowflake.com/en/sql-reference/account-usage/copy_history
