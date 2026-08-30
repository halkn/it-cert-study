# 3.1 データをロード／アンロードする

> Status: complete
> Last verified: 2026-08-30

## この章で学ぶこと

この章を終えると、次を説明・選択できます。

- User stage、table stage、named internal stage、external stageを要件から選ぶ
- Internal stageのencryption typeと、stageに付くdirectory tableの役割を説明する
- File formatのtypeとoption、loadとunloadで扱えるtypeの差を説明する
- `COPY INTO <table>`／`COPY INTO <location>`の主要optionと、load metadataによる重複回避を説明する
- `ON_ERROR`、`VALIDATION_MODE`、`VALIDATE()`、load履歴viewをerror対応の目的別に使い分ける

## 前提知識

- [1.3 オブジェクト階層](../domain-1/03-object-hierarchy.md)のdatabase／schema／schema-level object
- [1.4 Virtual Warehouse](../domain-1/04-virtual-warehouses.md)。bulk loadはuser-managed warehouseで実行される
- [2.1 セキュリティモデル](../domain-2/01-security-model.md)のprivilegeとgrant
- CSV、JSONなどのテキストファイル形式の基本

## この章の用語

| 用語 | この章での意味 |
|---|---|
| stage | ロード元／アンロード先のファイル置き場を指すSnowflakeのobjectまたは領域 |
| internal stage | Snowflakeが管理するstorage上のstage |
| external stage | S3、Google Cloud Storage、Azureなど外部cloud storage上のstage |
| bulk load | `COPY INTO <table>`でstage上のファイルをまとめてロードする方式 |
| unload | `COPY INTO <location>`でquery結果をstageへファイル出力すること |
| file format | ファイルの型とparse規則をまとめたschema-level objectまたはinline指定 |
| load metadata | どのファイルをいつロードしたかをtableごとに記録するmetadata |
| directory table | stage上のファイルのmetadata catalogを提供する、stageに付随する暗黙のobject |
| staged file | stageへ置かれ、まだtableへロードされていないファイル |

## 試験範囲との対応

| Topic | 本文 | 主な公式根拠 |
|---|---|---|
| File format | [ファイルの解釈規則を1か所へまとめる](#file-formats) | `docs-create-file-format`, `docs-copy-into-location` |
| Stage: internal、external、server-side encryption、directory table | [ファイルの置き場所と読み取り権限を決める](#stages) | `docs-create-stage`, `docs-data-load-local-create-stage`, `docs-data-load-dirtables` |
| COPY INTO command | [ロードとアンロードを実行する](#copy-into) | `docs-copy-into-table`, `docs-copy-into-location`, `docs-data-load-transform` |
| Error handling option | [失敗の扱いを事前に決め、後から切り分ける](#error-handling) | `docs-copy-into-table`, `docs-validate-function`, `docs-copy-history` |

公式ObjectiveとTopicは[COF-C03 Syllabus](../../docs/syllabus.md#31-データをロードアンロードする)から公式Study Guideへ辿って確認できます。

## ロードは「置く」「解釈する」「入れる」の3段階

Snowflakeへのファイルロードは、次の3つを別々に決める作業です。混同すると、どのcommandやoptionを直すべきか分からなくなります。

1. ファイルをどこへ置くか — stage
2. ファイルをどう読むか — file format
3. どのtableへどう入れるか — `COPY INTO`とcopy option

Bulk loadの実行にはuser-managed warehouseが必要です。`COPY INTO`はSQL文であり、session内のcurrent warehouseで動きます。[3.2](02-automated-ingestion.md)で扱うSnowpipeは、この点でbulk loadと異なります。

アンロードは逆向きに同じ3段階を通ります。Query結果をfile formatに従ってファイル化し、stageへ書き出します。

[図を開く: Stageの種類と権限の対応](../../diagrams/domain-3/stage-types.md)

手動の`COPY INTO`と、[3.2](02-automated-ingestion.md)で扱う自動取り込みの位置関係は[図を開く: 取り込み方式の選定](../../diagrams/domain-3/ingestion-selection.md)で確認できます。

<a id="stages"></a>
## Stage — ファイルの置き場所と読み取り権限を決める

Stageは「Snowflakeがファイルを読み書きできる場所」です。Internal stageはSnowflakeが管理するstorage、external stageはS3、Google Cloud Storage、Azure上の場所を指します。`CREATE STAGE`で`URL`を指定しなければinternal stageになります。

### Internal stageの3種類を用途で選ぶ

Internal stageは、誰が使うか・どのtableへ入れるかで3種類に分かれます。

| Stage | 参照名 | 想定用途 | 主な制約 |
|---|---|---|---|
| User stage | `@~` | 1人のuserが複数tableへロードする | 変更・削除不可。File format optionを持てず`COPY INTO`側で指定する。他userと共有できない |
| Table stage | `@%<table>` | 1つのtableへ複数userがロードする | 変更・削除不可。ファイル操作はtableのOWNERSHIP保持者のみ。ロード時のデータ変換不可 |
| Named internal stage | `@<stage>` | 複数user・複数tableで定期的にロードする | Schema-level objectとして作成し、権限付与・所有権移譲ができる |

User stageとtable stageはaccountやtableに最初から付随する領域で、`CREATE`しません。運用でロード基盤を組むときにnamed internal stageが推奨されるのは、roleへ権限を付け替えられる唯一の内部stageだからです。

```sql
CREATE STAGE raw_events_stage
  FILE_FORMAT = (TYPE = JSON)
  DIRECTORY = (ENABLE = TRUE);
```

### External stageは外部storageを指す

External stageは`URL`と認証情報を持ちます。認証情報をSQL文へ直接書かず、storage integrationを参照する形が推奨されます。Storage integrationは[3.3](03-connectors-integrations.md#storage-integration)で扱います。

```sql
CREATE STAGE s3_landing
  STORAGE_INTEGRATION = my_s3_int
  URL = 's3://mybucket/landing/'
  FILE_FORMAT = my_csv_format;
```

### Stage privilegeはinternalとexternalで異なる

Stageのprivilegeは種類によって使う名前が変わります。ここは設問になりやすい非対称です。

- External stage: `USAGE`。`READ`と`WRITE`を含み、internal stageには適用されない。
- Internal stage: `READ`（読み取り）と`WRITE`（書き込み）を個別にgrantする。

つまり「internal stageへ`USAGE`をgrantする」という選択肢は誤りです。Storage integrationを使うstageを作る場合は、integration objectへの`USAGE`も別途必要です。

### PUTとGETはlocalとinternal stageの間だけ

ローカルファイルをinternal stageへ上げるのが`PUT`、internal stageからローカルへ下ろすのが`GET`です。

```sql
PUT file:///data/orders*.csv @raw_events_stage AUTO_COMPRESS = TRUE;
GET @%orders file:///tmp/unloaded/;
```

制約を3つ押さえます。

- `PUT`も`GET`もSnowsightのworksheetからは実行できません。SnowSQL、driver、Snowflake CLIなどのclientから実行します。SnowsightのUIにはnamed internal stageへファイルをuploadする別機能があります。
- `GET`はinternal stage専用です。External stageからのdownloadには使えません。
- `PUT`は既定で`AUTO_COMPRESS = TRUE`、`OVERWRITE = FALSE`です。同名ファイルは既定で上書きされません。

### Internal stageのencryptionは作成時に決まる

Internal stageのファイルは常に暗号化されます。選べるのは暗号化の担い手です。

| `ENCRYPTION` | 意味 |
|---|---|
| `SNOWFLAKE_FULL` | client-side暗号化とserver-side暗号化の両方。既定値 |
| `SNOWFLAKE_SSE` | server-side暗号化のみ |

```sql
CREATE STAGE docs_stage
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
  DIRECTORY = (ENABLE = TRUE);
```

`SNOWFLAKE_SSE`を選ぶ理由は、client-side暗号化されたファイルはSnowflakeのclientを通さないと復号できず、pre-signed URLなどでファイル本体を直接扱う用途に向かないためです。Unstructured dataをdirectory table経由で参照する構成では`SNOWFLAKE_SSE`が使われます。Encryption typeはstage作成後に変更できないため、用途を決めてから作成します。

External stageのencryptionは外部storage側の方式に合わせます。S3は`AWS_SSE_S3`、`AWS_SSE_KMS`、`AWS_CSE`、`NONE`、Google Cloud Storageは`GCS_SSE_KMS`と`NONE`、Azureは`AZURE_CSE`と`NONE`を指定できます。

<a id="directory-tables"></a>
### Directory tableはstageのファイル一覧をSQLで扱う

Directory tableは、stage上のファイルのmetadata catalogです。独立したdatabase objectではなく、stageに重ねられる暗黙のobjectであり、internal stageとexternal stageの両方で使えます。

```sql
ALTER STAGE docs_stage SET DIRECTORY = (ENABLE = TRUE);
ALTER STAGE docs_stage REFRESH;

SELECT relative_path, size, last_modified, file_url
FROM DIRECTORY(@docs_stage);
```

保持される列は`RELATIVE_PATH`、`SIZE`、`LAST_MODIFIED`、`MD5`、`ETAG`、`FILE_URL`です。Metadataの更新には、`ALTER STAGE ... REFRESH`による手動更新と、cloud event notificationによる自動更新があります。手動`REFRESH`はcloud servicesとして課金され、自動更新のoverheadはSnowpipe課金として請求されます。Directory tableは「ファイルの一覧と属性」を持つのであって、ファイルの中身を持たない点に注意します。

Stage上のファイルは、ロードせずにそのままqueryすることもできます。列は`$1`、`$2`のような位置で参照し、半構造化データは`$1:a.b`のようにpathを付けます。公式docsはこの機能を簡単なqueryのためのものと位置付けており、tableへのロードの代わりにはしません。

```sql
SELECT $1, $2 FROM @raw_events_stage/orders.csv
  (FILE_FORMAT => my_csv_format);
```

<a id="file-formats"></a>
## File format — ファイルの解釈規則を1か所へまとめる

File formatは、ファイルのtypeとparse規則をまとめたものです。`CREATE FILE FORMAT`で名前付きobjectにするか、stage定義や`COPY INTO`にinlineで書きます。

### Loadできるtypeとunloadできるtypeは同じではない

ロードでサポートされるtypeはCSV、JSON、AVRO、ORC、PARQUET、XMLの6種類です。一方、`COPY INTO <location>`によるアンロードで指定できるtypeはCSV、JSON、PARQUETの3種類で、JSONでのアンロードはVARIANT列からに限られます。

この非対称は設問で狙われます。「ORCへアンロードする」「XMLへアンロードする」は選べません。

### 主要optionと既定値

```sql
CREATE FILE FORMAT my_csv_format
  TYPE = CSV
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  NULL_IF = ('', 'NULL')
  COMPRESSION = AUTO;
```

| Option | Type | 既定値 | 役割 |
|---|---|---|---|
| `COMPRESSION` | 共通 | `AUTO` | 圧縮方式の指定。`AUTO`は拡張子などから推定する |
| `FIELD_DELIMITER` | CSV | `,` | 列の区切り文字 |
| `SKIP_HEADER` | CSV | `0` | 先頭から読み飛ばす行数。header行があるなら`1` |
| `FIELD_OPTIONALLY_ENCLOSED_BY` | CSV | `NONE` | 区切り文字を含む値を囲む引用符 |
| `NULL_IF` | CSV／JSON | `\N` | NULLとして扱う文字列 |
| `EMPTY_FIELD_AS_NULL` | CSV | `TRUE` | 空フィールドをNULLにするか |
| `ERROR_ON_COLUMN_COUNT_MISMATCH` | CSV | `TRUE` | 列数不一致をerrorにするか |
| `STRIP_OUTER_ARRAY` | JSON | `FALSE` | 最外周の`[ ]`を外して要素ごとに1行にするか |
| `BINARY_AS_TEXT` | PARQUET | `TRUE` | binary列をtextとして解釈するか |

`SKIP_HEADER = 1`を付け忘れるとheader行がデータ行として読まれ、`STRIP_OUTER_ARRAY = TRUE`を付け忘れるとJSON配列全体が1行のVARIANTになります。どちらもerrorにならないまま結果が壊れるため、原因の切り分けに使えるように挙動を覚えます。

### 名前付きformatとinline指定の使い分け

同じ規則を複数のロードで使うなら名前付きfile formatにします。Stage定義に`FILE_FORMAT`を持たせておくと、そのstageを使う`COPY INTO`で毎回書かずに済みます。

一方、**copy optionはstage定義に置きません**。公式docsは`CREATE STAGE`や`CREATE TABLE`でcopy optionを指定せず、`COPY INTO <table>`で指定することを推奨しています。File formatは「ファイルの読み方」、copy optionは「ロードの振る舞い」であり、後者はロードごとに変わるためです。

User stageはfile format optionを保持できません。User stageから読むときは`COPY INTO`側でfile formatを指定します。

<a id="copy-into"></a>
## COPY INTO — ロードとアンロードを実行する

### COPY INTO <table> でstageからロードする

```sql
COPY INTO orders
FROM @raw_events_stage/orders/
  FILE_FORMAT = (FORMAT_NAME = my_csv_format)
  PATTERN = '.*[.]csv[.]gz'
  ON_ERROR = SKIP_FILE;
```

対象ファイルの絞り込みには`PATTERN`（正規表現）と`FILES`（ファイル名の明示列挙）を使います。`PURGE = TRUE`を付けると、ロード成功後にstageからファイルを削除します。既定は`FALSE`です。

半構造化データを列名でtable列へ対応付けるには`MATCH_BY_COLUMN_NAME`を使います。既定は`NONE`で、`SELECT`によるロード時変換とは併用できません。

### 同じファイルが二重にロードされない仕組み

Snowflakeはtableごとにload metadataを保持し、ロード済みのファイルを再度ロードしません。ここで押さえる期限は64日です。

- ファイルの`LAST_MODIFIED`が64日より古い、または初回ロードから64日以上経過した場合、そのファイルのロード状態は「不明」になります。
- 不明な状態のファイルをロードするには`LOAD_UNCERTAIN_FILES = TRUE`を指定します。既定は`FALSE`です。
- `FORCE = TRUE`はload metadataを無視して全ファイルをロードします。既定は`FALSE`で、重複データが生じ得ます。

`LOAD_UNCERTAIN_FILES`は「状態が不明なものだけ」を対象にし、`FORCE`は「状態に関係なく全部」を対象にします。重複を避けたい運用で`FORCE = TRUE`を選ぶのは誤りです。

### ロード中の簡易変換でできること・できないこと

`COPY INTO`は`FROM`にqueryを書くことで、ロードしながら列を加工できます。

```sql
COPY INTO orders (order_id, ordered_at, region)
FROM (
  SELECT $1::NUMBER, TO_TIMESTAMP($2), UPPER($3)
  FROM @raw_events_stage/orders/
)
FILE_FORMAT = (FORMAT_NAME = my_csv_format);
```

できるのは列の並べ替え、列の省略、cast、多数のscalar関数、sequenceやIDENTITY列の利用、半構造化データからの列抽出です。ファイルの列数や順序をtableと一致させる必要はありません。

できないのは`WHERE`によるfilter、`ORDER BY`／`LIMIT`／`FETCH`／`TOP`、`JOIN`、`GROUP BY`、`FLATTEN`です。`DISTINCT`も想定どおりに動きません。「ロード時に不要な行を除外する」という要件はこの機能では満たせず、ロード後の変換で行います。

### COPY INTO <location> でアンロードする

```sql
COPY INTO @exports/orders_2026/
FROM (SELECT * FROM orders WHERE order_date >= '2026-08-01')
  FILE_FORMAT = (TYPE = CSV COMPRESSION = GZIP)
  HEADER = TRUE
  MAX_FILE_SIZE = 100000000
  OVERWRITE = FALSE;
```

アンロードの既定挙動を押さえます。

| Option | 既定値 | 挙動 |
|---|---|---|
| `SINGLE` | `FALSE` | 既定では複数ファイルへ並列出力し、末尾に一意なsuffixが付く |
| `MAX_FILE_SIZE` | 16777216（16 MB） | スレッドごとに生成する各ファイルの最大サイズ。上限は5 GB |
| `OVERWRITE` | `FALSE` | 同名ファイルを上書きしない |
| `HEADER` | `FALSE` | 列名の見出し行を出力しない |

アンロードしたファイルは既定でgzip圧縮されます。「1ファイルにまとめたい」なら`SINGLE = TRUE`、「BIツールでそのまま開きたい」なら`HEADER = TRUE`というように、要件からoptionへ対応付けます。`MAX_FILE_SIZE`の既定16 MBは小さく、大きな結果は自動的に多数のファイルへ分かれます。

### ファイルサイズは圧縮後100〜250 MBを目安にする

公式docsは、圧縮後でおよそ100〜250 MB以上を目安にファイルを用意することを推奨しています。理由は、この単位が並列処理の効率とファイルごとのoverheadのバランスが取りやすいためです。100 GB級の巨大ファイルは推奨されません。大きなファイルは行単位で分割してからstageへ置きます。

<a id="error-handling"></a>
## Error handling — 失敗の扱いを事前に決め、後から切り分ける

### ON_ERRORでロード継続の方針を決める

`ON_ERROR`は「errorを含むファイルに当たったときどうするか」を決めます。

| 値 | 挙動 |
|---|---|
| `ABORT_STATEMENT` | errorが1件でもあればCOPY文全体を中止する |
| `CONTINUE` | error行を飛ばしてロードを続ける |
| `SKIP_FILE` | error行を含むファイルをまるごとスキップする |
| `SKIP_FILE_<num>` | error行が`num`件以上のファイルをスキップする |
| `SKIP_FILE_<num>%` | error行の割合が`num`%を超えたファイルをスキップする |

既定値がロード方式で異なる点が重要です。**bulk loadの`COPY INTO`は`ABORT_STATEMENT`、Snowpipeは`SKIP_FILE`**です。同じoption名でも既定の厳しさが逆方向であり、「Snowpipeは既定でCOPYと同じく全体を中止する」は誤りです。

`CONTINUE`は部分的にロードされた状態を残すため、後からどの行が入らなかったかを確認する手順とセットで使います。

### ロード前に検証する VALIDATION_MODE

`VALIDATION_MODE`を付けたCOPY文は**データをロードせず**、検証結果だけを返します。

| 値 | 返すもの |
|---|---|
| `RETURN_n_ROWS` | 指定行数を検証し、問題なければその行を返す |
| `RETURN_ERRORS` | 対象ファイル全体のerrorを返す |
| `RETURN_ALL_ERRORS` | 部分ロードされたファイルのerrorも含めた全errorを返す |

```sql
COPY INTO orders
FROM @raw_events_stage/orders/
  FILE_FORMAT = (FORMAT_NAME = my_csv_format)
  VALIDATION_MODE = 'RETURN_ERRORS';
```

`VALIDATION_MODE`は`SELECT`による変換を伴うCOPY文とは併用できません。「変換しながら検証だけする」はできず、変換前のファイルを検証するか、ロード後に確認します。

### ロード後に調べる VALIDATE() と履歴view

`VALIDATE()`は**すでに実行したCOPY文**の結果を後から検証し、最初のerrorだけでなく発生した全errorを返します。

```sql
SELECT * FROM TABLE(VALIDATE(orders, JOB_ID => '_last'));
```

ただし`ON_ERROR = ABORT_STATEMENT`（既定）でロードした場合、文全体が中止されるため`VALIDATE()`は結果を返しません。`VALIDATE()`を活かすには`CONTINUE`や`SKIP_FILE`で実行しておく必要があります。

ロード履歴は目的でviewを選びます。

| View | 対象 | 主な特徴 |
|---|---|---|
| `SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY` | `COPY INTO`とSnowpipeの両方 | 365日保持。latencyは多くの場合最大120分 |
| `SNOWFLAKE.ACCOUNT_USAGE.LOAD_HISTORY` | `COPY INTO`のみ | 365日保持。latencyは多くの場合最大90分。**Snowpipeによるロードは返さない** |

「Snowpipeのロード履歴を調べたい」なら`COPY_HISTORY`です。Account Usageの`LOAD_HISTORY`では見えません。

なお、10,000行という上限を持つのはInformation Schemaの`LOAD_HISTORY` viewです。`COPY_HISTORY`はこの制限を受けません。Account Usageの`LOAD_HISTORY`にこの行数上限はなく、違いはlatencyとretention、そしてSnowpipeを含むかどうかにあります。

### 値の長さと処理量に関わるoption

- `ENFORCE_LENGTH`（既定`TRUE`）: 文字列がtarget列長を超えるとerrorにする。`FALSE`で切り詰める。
- `TRUNCATECOLUMNS`（既定`FALSE`）: `TRUE`で切り詰める。`ENFORCE_LENGTH`と機能は同等で挙動が逆です。
- `SIZE_LIMIT`（既定なし）: 指定バイト数を超えるまでロードを続けます。上限に達していなくても、対象ファイルがあれば最低1ファイルはロードされます。

## Mini hands-on — CSVを検証してからロードする

Named internal stageとfile formatを用意し、検証してからロードします。実行にはstageへの`READ`／`WRITE`とtableへの`INSERT`が必要です。

```sql
CREATE FILE FORMAT csv_with_header
  TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"';

CREATE STAGE load_demo FILE_FORMAT = csv_with_header;

-- clientから実行する。Snowsight worksheetでは実行できない
PUT file:///data/orders.csv @load_demo;

LIST @load_demo;

COPY INTO orders FROM @load_demo
  VALIDATION_MODE = 'RETURN_ERRORS';

COPY INTO orders FROM @load_demo
  ON_ERROR = SKIP_FILE;

SELECT * FROM TABLE(VALIDATE(orders, JOB_ID => '_last'));
```

`VALIDATION_MODE`の実行では行が入らないため、直後に`SELECT COUNT(*)`が0でも失敗ではありません。ロードは次のCOPY文で行われます。

## Compare — 要件からstageとoptionを選ぶ

| 要件 | 選ぶもの |
|---|---|
| 複数チームが同じlanding領域へ定期ロードする | Named internal stageまたはexternal stage |
| 1人の担当者が手元のファイルを複数tableへ試験投入する | User stage（`@~`） |
| 1つのtable専用に、追加objectを作らず投入する | Table stage（`@%<table>`） |
| S3上のファイルを、鍵をSQLへ書かずに読む | External stage + storage integration |
| Pre-signed URLで扱うファイルをstageへ置く | Internal stage + `ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')` |
| Stage上のファイル一覧をSQLで結合したい | Directory table |
| Error行があっても残りをロードしたい | `ON_ERROR = CONTINUE` |
| ロードせずに問題行だけ知りたい | `VALIDATION_MODE = 'RETURN_ERRORS'` |
| 実行済みロードのerrorを全部見たい | `VALIDATE()`（`ABORT_STATEMENT`以外で実行済みのこと） |
| Snowpipeを含むロード履歴を集計したい | `COPY_HISTORY` |
| 結果を1つのCSVに見出し付きで出したい | `COPY INTO <location>` + `SINGLE = TRUE` + `HEADER = TRUE` |

## 試験で重要なポイント

- Internal stageはuser（`@~`）、table（`@%<table>`）、named internalの3種で、named internal stageだけが権限を付け替えられる。
- External stageのprivilegeは`USAGE`、internal stageは`READ`／`WRITE`。
- `PUT`／`GET`はSnowsight worksheetで実行できず、`GET`はinternal stage専用。
- Internal stageの`ENCRYPTION`既定は`SNOWFLAKE_FULL`、server-sideのみにするなら`SNOWFLAKE_SSE`。作成後は変更できない。
- ロードは6形式、アンロードはCSV／JSON／PARQUETの3形式。
- `ON_ERROR`の既定はbulk loadが`ABORT_STATEMENT`、Snowpipeが`SKIP_FILE`。
- `VALIDATION_MODE`はロードしない。`VALIDATE()`は実行済みCOPYを対象にする。

## 間違えやすいポイント

- Copy optionをstage定義へ置かない。File formatはstageに持てるが、copy optionは`COPY INTO`で指定する。
- `FORCE = TRUE`を重複回避の手段と取り違えない。重複を生む方の設定である。
- `LOAD_UNCERTAIN_FILES`は状態不明のファイルだけを対象にし、`FORCE`とは範囲が違う。
- `COPY INTO`の変換で`WHERE`、`JOIN`、`GROUP BY`、`FLATTEN`は使えない。
- Directory tableはファイルのmetadataを持つだけで、ファイル本体をtable化しない。
- `LOAD_HISTORY`ではSnowpipeのロードを追えない。
- `MAX_FILE_SIZE`の既定は16 MBで、大きな結果は既定で複数ファイルに分かれる。

## 確認問題

- [C3-3.1-Q01: Internal stageの種類](../../exercises/chapter/c3-3.1-q01.md)
- [C3-3.1-Q02: Stage privilege](../../exercises/chapter/c3-3.1-q02.md)
- [C3-3.1-Q03: Internal stageのencryption](../../exercises/chapter/c3-3.1-q03.md)
- [C3-3.1-Q04: Directory table](../../exercises/chapter/c3-3.1-q04.md)
- [C3-3.1-Q05: アンロードできるfile format](../../exercises/chapter/c3-3.1-q05.md)
- [C3-3.1-Q06: CSV file formatのoption](../../exercises/chapter/c3-3.1-q06.md)
- [C3-3.1-Q07: 重複ロードの回避](../../exercises/chapter/c3-3.1-q07.md)
- [C3-3.1-Q08: ロード時変換の制限](../../exercises/chapter/c3-3.1-q08.md)
- [C3-3.1-Q09: アンロードの既定挙動](../../exercises/chapter/c3-3.1-q09.md)
- [C3-3.1-Q10: ON_ERRORの既定値](../../exercises/chapter/c3-3.1-q10.md)
- [C3-3.1-Q11: VALIDATION_MODEとVALIDATE()](../../exercises/chapter/c3-3.1-q11.md)
- [C3-3.1-Q12: ロード履歴view](../../exercises/chapter/c3-3.1-q12.md)

## 章のまとめ

- Stageは置き場所と権限、file formatは読み方、copy optionはロードの振る舞いを担当する。
- Internal stageの3種類は「誰が使うか」「どのtableか」で選び、権限を運用するならnamed internal stageを使う。
- `COPY INTO`はload metadataで重複を防ぎ、64日を超えると状態が不明になる。
- Error対応は、事前方針（`ON_ERROR`）、事前検証（`VALIDATION_MODE`）、事後調査（`VALIDATE()`と履歴view）の3段階で使い分ける。

## 次に学ぶこと

[3.2 自動データ取り込みを実行する](02-automated-ingestion.md)では、この章の`COPY INTO`を手動で実行する代わりに、ファイル到着や変更を起点として継続的に取り込む方式を学びます。

## 根拠・関連する公式ドキュメント

- `docs-data-load-overview` — https://docs.snowflake.com/en/user-guide/data-load-overview
- `docs-data-load-prepare` — https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare
- `docs-create-stage` — https://docs.snowflake.com/en/sql-reference/sql/create-stage
- `docs-data-load-local-create-stage` — https://docs.snowflake.com/en/user-guide/data-load-local-file-system-create-stage
- `docs-data-load-dirtables` — https://docs.snowflake.com/en/user-guide/data-load-dirtables
- `docs-querying-stage` — https://docs.snowflake.com/en/user-guide/querying-stage
- `docs-create-file-format` — https://docs.snowflake.com/en/sql-reference/sql/create-file-format
- `docs-copy-into-table` — https://docs.snowflake.com/en/sql-reference/sql/copy-into-table
- `docs-copy-into-location` — https://docs.snowflake.com/en/sql-reference/sql/copy-into-location
- `docs-data-load-transform` — https://docs.snowflake.com/en/user-guide/data-load-transform
- `docs-validate-function` — https://docs.snowflake.com/en/sql-reference/functions/validate
- `docs-put` — https://docs.snowflake.com/en/sql-reference/sql/put
- `docs-get` — https://docs.snowflake.com/en/sql-reference/sql/get
- `docs-copy-history` — https://docs.snowflake.com/en/sql-reference/account-usage/copy_history
- `docs-load-history` — https://docs.snowflake.com/en/sql-reference/account-usage/load_history
- `docs-access-control-privileges` — https://docs.snowflake.com/en/user-guide/security-access-control-privileges
