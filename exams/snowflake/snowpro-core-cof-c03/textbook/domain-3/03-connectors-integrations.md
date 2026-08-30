# 3.3 Connector と Integration を識別する

> Status: complete
> Last verified: 2026-08-30

## この章で学ぶこと

この章を終えると、次を説明・選択できます。

- Snowflakeが提供するdriverの種類と、driverが担う役割を説明する
- Kafka connectorとSpark connectorが内部で何を使い、何を解決するかを説明する
- Driver、connector、Snowpark、Snowflake Python APIの役割を区別する
- Storage integrationとAPI integrationの対象と、指定するパラメータの違いを説明する
- Git integrationに必要な3つのobjectを挙げ、参照pathの形を説明する
- Integration objectの種類（security／storage／API／notification／external access）を用途で識別する

## 前提知識

- [1.2 インターフェースとツール](../domain-1/02-interfaces-and-tools.md)のSnowsight、Snowflake CLI
- [1.6 AI/MLとアプリケーション開発](../domain-1/06-ai-ml-app-development.md)のSnowpark
- [2.1 セキュリティモデル](../domain-2/01-security-model.md)のrole、privilege、OAuth、key-pair認証
- [3.1](01-loading-unloading.md)のexternal stage

## この章の用語

| 用語 | この章での意味 |
|---|---|
| driver | Application codeからSnowflakeへ接続し、SQLを実行するためのclient library |
| connector | 特定の外部product（Kafka、Sparkなど）とSnowflakeの間でデータを受け渡す部品 |
| integration | Snowflakeと外部serviceの間のinterfaceを定義する、名前付きのaccount-level object |
| external function | Snowflakeの外で実行され、SQLから呼び出せる利用者定義関数 |
| secret | Password、token、OAuth情報などの資格情報を保持するschema-level object |
| Git repository | Remote Git repositoryのcloneをSnowflake内に持つschema-level object |

## 試験範囲との対応

| Topic | 本文 | 主な公式根拠 |
|---|---|---|
| Snowflake driver | [applicationからSQLを実行する層](#drivers) | `docs-drivers-overview`, `docs-python-connector`, `docs-python-api-overview` |
| Snowflake connector | [外部productとデータを受け渡す層](#connectors) | `docs-kafka-connector-overview`, `docs-spark-connector-overview` |
| Storage integration | [cloud storageの資格情報をobjectへ切り出す](#storage-integration) | `docs-storage-integration-ddl`, `docs-s3-storage-integration` |
| API integration | [外部HTTPS serviceの呼び出しを許可する](#api-integration) | `docs-api-integration-ddl`, `docs-external-functions` |
| Git integration | [repositoryのcloneをSnowflake内に持つ](#git-integration) | `docs-git-overview`, `docs-git-repository-ddl` |

公式ObjectiveとTopicは[COF-C03 Syllabus](../../docs/syllabus.md#33-connector-と-integration-を識別する)から公式Study Guideへ辿って確認できます。

## 接続の関心事を3層に分ける

この章の対象は名前が似ていますが、担当する関心事が違います。設問では「どの層の話か」を見分けることが答えの半分です。

| 層 | 何をするか | 具体例 |
|---|---|---|
| Driver | 自作applicationからSnowflakeへ接続し、SQLを送る | JDBC、ODBC、Python Connector、Node.js、Go |
| Connector | 既存product（Kafka、Spark）とSnowflakeの間を繋ぐ | Kafka connector、Spark connector |
| Integration | Snowflakeが外部serviceへアクセスする際の資格情報と許可範囲を定義する | Storage、API、security、notification、external access |

DriverとconnectorはSnowflakeの外側から中へ接続する部品、integrationはSnowflakeの中から外へ出る経路を定義するobjectです。この向きの違いを押さえると混同しにくくなります。

[図を開く: Driver・connector・integrationの担当範囲](../../diagrams/domain-3/integration-map.md)

<a id="drivers"></a>
## Driver — applicationからSQLを実行する層

Snowflakeは、Go、C#、JavaScript、Pythonなどの言語で書いたapplicationからSnowflakeを操作するためのdriverを提供します。

| Driver | 補足 |
|---|---|
| JDBC Driver | JDBC type 4 driver。64bit環境とJava 1.8以上が必要 |
| ODBC Driver | ODBCベースのclient applicationから接続する。Windows／macOS／Linux向け |
| Snowflake Connector for Python | PEP-249（Python DB API v2）準拠。JDBCにもODBCにも依存しないpure Python package |
| Node.js Driver | pure JavaScriptで書かれた非同期interface |
| Go Snowflake Driver | Goの`database/sql` interfaceを実装 |
| .NET Driver、PHP PDO Driver | それぞれの言語からの接続に使う |

Python向けだけが公式に「Connector」という名前ですが、位置付けはほかのdriverと同じです。名前ではなく役割で判断します。

### DriverとSnowflake Python APIとSnowparkの違い

同じPythonでも、目的が異なる3つのlibraryがあります。

| Library | 何を書くか | 主な用途 |
|---|---|---|
| Snowflake Connector for Python | SQL文の文字列を書き、cursorで実行する | 既存applicationからのquery実行 |
| Snowflake Python API（`snowflake.core`） | SQLを書かず、database、table、warehouse、taskなどをPython objectとして操作する | Resource管理、DevOpsの自動化 |
| Snowpark | DataFrame APIでデータ処理を記述し、Snowflake内で実行する | データに近い場所での変換・処理 |

「SQL文字列を書くか」「resourceを宣言的に扱うか」「データを処理するか」で分かれます。

<a id="connectors"></a>
## Connector — 外部productとデータを受け渡す層

### Kafka connectorはtopicをtableへ流す

Snowflake Connector for Kafkaは、Kafkaのtopicから読み取ったmessageをSnowflakeのtableへロードします。ロード方式はSnowpipeとSnowpipe Streamingの2つをサポートし、どちらを使うか選べます（[3.2](02-automated-ingestion.md#snowpipe)）。

Topicは明示的にtableへmappingできます。mappingしない場合はconnectorがtableを作成し、小文字のtopic名は大文字のtable名へ変換され、識別子として使えない文字はアンダースコアへ置き換えられます。

既定では、各tableに2つのVARIANT列が作られます。

| 列 | 内容 |
|---|---|
| `RECORD_CONTENT` | Kafka messageの本体。parseされないまま格納される |
| `RECORD_METADATA` | topic、partition、offset、timestamp、key、headerなどのmetadata |

schema detection and evolutionを使う場合は、この2列構成の代わりに、messageのschemaに合わせた列を持つtableになります。

Kafka connectorが扱うのはKafkaからSnowflakeへの一方向のロードです。Snowflakeからkafkaへの書き出しはこのconnectorの役割ではありません。

### Spark connectorはJDBC driver経由でSnowflakeと通信する

Snowflake Connector for Sparkは、Spark clusterからSnowflakeのデータを読み書きします。内部ではSnowflake JDBC driverを使ってSnowflakeと通信します。

Query pushdownにより、Sparkのlogical planの全部または一部をSnowflake側で処理させられます。ただし**Spark UDFはpushdownできません**。

SnowparkはSpark clusterを別に用意せず、処理をSnowflake内で実行します。SnowflakeのUDFを含むすべての操作をSnowflake側で実行できる点が、Spark connectorのpushdown制限との違いです。既にSpark基盤がある構成ではSpark connector、Snowflake内で完結させたい構成ではSnowparkを選びます。

### Native App形式のconnector

Kafka、Sparkのほかに、SaaS製品向けのSnowflake Connectorがあります。例えばServiceNow向けのconnectorはSnowflake Native App Frameworkの上に構築され、Snowflake Marketplace経由でinstallして使います。Driverのようにapplicationへ組み込むものではなく、accountへinstallするapplicationである点が異なります。

<a id="storage-integration"></a>
## Storage integration — cloud storageの資格情報をobjectへ切り出す

Integrationは、Snowflakeと外部serviceの間のinterfaceを表す名前付きobjectです。公式docsは、integrationの目的を「secret keyやaccess tokenといったcloud providerの資格情報を明示的に渡す必要をなくすこと」と説明しています。

Storage integrationは、そのうちcloud storage（S3、Google Cloud Storage、Azure）へのアクセスを担当します。

```sql
CREATE STORAGE INTEGRATION my_s3_int
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::001234567890:role/myrole'
  ENABLED = TRUE
  STORAGE_ALLOWED_LOCATIONS = ('s3://mybucket/landing/')
  STORAGE_BLOCKED_LOCATIONS = ('s3://mybucket/landing/secret/');
```

- `STORAGE_ALLOWED_LOCATIONS`／`STORAGE_BLOCKED_LOCATIONS`が、参照を許す／禁じるbucketとpathを決めます。
- `ENABLED`（既定`TRUE`）は、stageがこのintegrationを参照できるかを制御します。
- `DESC INTEGRATION`で、AWS IAM roleとの信頼関係に使うexternal IDを取得します。

External stageは定義の中でstorage integrationを参照します。1つのstorage integrationを複数のexternal stageで共有できるため、cloud側の権限設定を1か所に集約できます。3.1で作ったexternal stageの`STORAGE_INTEGRATION = my_s3_int`がこれにあたります。

Storage integrationはaccount-level objectです。作成にはaccount-levelの`CREATE INTEGRATION`が必要で、既定ではACCOUNTADMINだけが持ちます。使う側のroleにはintegrationへの`USAGE`が要ります。

<a id="api-integration"></a>
## API integration — 外部HTTPS serviceの呼び出しを許可する

API integrationは、SnowflakeからHTTPSのproxy serviceを呼び出すための設定です。External functionの呼び出しに使うほか、Git integrationでも使われます。

```sql
CREATE API INTEGRATION my_api_int
  API_PROVIDER = aws_api_gateway
  API_AWS_ROLE_ARN = 'arn:aws:iam::001234567890:role/api-role'
  API_ALLOWED_PREFIXES = ('https://xyz.execute-api.us-west-2.amazonaws.com/prod/')
  ENABLED = TRUE;
```

`API_PROVIDER`にはAWS API Gateway系のほか、`azure_api_management`、`google_api_gateway`、`git_https_api`などがあります。許可範囲は`API_ALLOWED_PREFIXES`と`API_BLOCKED_PREFIXES`でHTTPSエンドポイント単位に指定します。

External functionは、Snowflakeの外に保存・実行されるユーザー定義関数です。geocoder、機械学習model、外部の独自codeなどをSQLから呼び出せるようにし、データをexport／importし直す手間をなくします。

### Storage integrationとAPI integrationを取り違えない

| | Storage integration | API integration |
|---|---|---|
| 対象 | Cloud storage（bucketとpath） | HTTPS proxy service（endpoint） |
| 許可範囲の指定 | `STORAGE_ALLOWED_LOCATIONS` | `API_ALLOWED_PREFIXES` |
| 主な利用先 | External stage、external table | External function、Git repository |

どちらもaccount-level objectで、作成には`CREATE INTEGRATION`が必要という共通点があるため、「どこへ繋ぐか」で見分けます。

<a id="git-integration"></a>
## Git integration — repositoryのcloneをSnowflake内に持つ

Git integrationは、remote Git repositoryのファイルをSnowflake内のGit repository cloneへ同期する機能です。cloneはbranch、tag、commitを含む完全なcloneとして保持されます。

### 必要なobjectは3つ

単一のobjectでは完結しません。

1. **Secret**: repositoryへの認証情報。`TYPE = password`のtoken認証やOAuthを使います（schema-level object）。
2. **API integration**: `API_PROVIDER = git_https_api`を指定し、`API_ALLOWED_PREFIXES`で対象repositoryのURL接頭辞、`ALLOWED_AUTHENTICATION_SECRETS`で使えるsecretを限定します（account-level object）。
3. **Git repository**: `ORIGIN`にHTTPSのrepository URL、`API_INTEGRATION`、`GIT_CREDENTIALS`を指定します（schema-level object）。

```sql
CREATE SECRET my_git_secret
  TYPE = password
  USERNAME = 'octocat'
  PASSWORD = 'ghp_xxxxxxxx';

CREATE API INTEGRATION my_git_api_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/my-account')
  ALLOWED_AUTHENTICATION_SECRETS = (my_git_secret)
  ENABLED = TRUE;

CREATE GIT REPOSITORY snowflake_extensions
  API_INTEGRATION = my_git_api_integration
  GIT_CREDENTIALS = my_git_secret
  ORIGIN = 'https://github.com/my-account/snowflake-extensions.git';
```

認証方式は、認証なし、token、OAuth flowから選べます。

### 同期と参照

```sql
ALTER GIT REPOSITORY snowflake_extensions FETCH;

LIST @snowflake_extensions/branches/main/;

EXECUTE IMMEDIATE FROM @snowflake_extensions/branches/main/setup.sql;
```

`ALTER GIT REPOSITORY ... FETCH`がremoteの内容をcloneへ取り込みます。参照pathは`@<repo>/branches/<branch>/`、`@<repo>/tags/<tag>/`、`@<repo>/commits/<hash>/`の形で、stageと同じ記法で扱えます。`EXECUTE IMMEDIATE FROM`と組み合わせると、repository内のSQLスクリプトをそのまま実行できます。

同期の向きはremoteからSnowflakeのcloneへです。`FETCH`にはGit repository objectへのOWNERSHIPまたは`WRITE`が必要で、secretが別schemaにある場合はそのschemaへの`USAGE`も要ります。

## Integration objectの種類を用途で識別する

Integrationは複数の種類があり、いずれもaccount-level objectです。作成には`CREATE INTEGRATION`（既定でACCOUNTADMINのみ）と、種類ごとの権限が必要です。

| 種類 | 用途 |
|---|---|
| Security integration | 外部IdPやOAuth clientとの認証・認可（`SAML2`、`EXTERNAL_OAUTH`、`OAUTH`、`OIDC`、`SCIM`、`API_AUTHENTICATION`） |
| Storage integration | Cloud storageへのアクセス |
| API integration | External functionやGitなど、HTTPS proxy serviceの呼び出し |
| Notification integration | Cloud message queue、email、webhookへの通知（[2.2](../domain-2/02-data-governance.md)） |
| External access integration | UDFやprocedureのhandlerから外部network locationへ出る通信。`ALLOWED_NETWORK_RULES`が必須 |

「認証の話ならsecurity」「storageならstorage」「HTTPS呼び出しならAPI」「通知ならnotification」「UDFからの外向き通信ならexternal access」と対応付けます。

## Mini hands-on — integrationとstageの対応を確認する

Account内のintegrationとexternal stageの結び付きを確認します。実行には対象objectを参照できるroleが必要です。

```sql
SHOW INTEGRATIONS;
DESC INTEGRATION my_s3_int;
SHOW STAGES;
DESC STAGE s3_landing;
```

`DESC INTEGRATION`の出力には、cloud側で信頼関係を設定するために使うIAM user ARNやexternal IDが含まれます。`DESC STAGE`ではそのstageが参照するstorage integrationを確認できます。両者が対応していれば、資格情報がstage定義ではなくintegrationに集約されています。

## Compare — 要件から接続部品を選ぶ

| 要件 | 選ぶもの |
|---|---|
| Javaのapplicationから直接SQLを実行する | JDBC Driver |
| Pythonの既存applicationからSQLを実行する | Snowflake Connector for Python |
| PythonでSQLを書かずにwarehouseやtaskを作成・管理する | Snowflake Python API（`snowflake.core`） |
| Kafkaのtopicをtableへ継続的に取り込む | Kafka connector |
| 既存のSpark基盤からSnowflakeを読み書きする | Spark connector |
| Spark clusterを持たずSnowflake内でDataFrame処理する | Snowpark |
| S3の鍵をSQLへ書かずにexternal stageを作る | Storage integration |
| SQLから外部の機械学習APIを呼び出す | API integration + external function |
| GitHub上のSQLスクリプトをSnowflakeから実行する | Secret + API integration（`git_https_api`）+ Git repository |
| UDFのhandlerから外部endpointへ通信する | External access integration |
| 外部IdPでSSOを構成する | Security integration |

## 試験で重要なポイント

- DriverとconnectorはSnowflakeへ接続する側、integrationはSnowflakeから外部serviceへ出る経路を定義するobject。
- Snowflake Connector for Pythonはpure Python packageで、JDBCやODBCに依存しない。
- Spark connectorは内部でJDBC driverを使い、Spark UDFはpushdownできない。
- Kafka connectorはSnowpipeとSnowpipe Streamingの両方をサポートする。
- Storage integrationは`STORAGE_ALLOWED_LOCATIONS`、API integrationは`API_ALLOWED_PREFIXES`で許可範囲を指定する。
- Git integrationにはsecret、API integration（`git_https_api`）、Git repositoryの3つが要る。
- Integrationはaccount-level objectで、作成権限は既定でACCOUNTADMINが持つ。

## 間違えやすいポイント

- 「Python Connector」はdriverの一種であり、Snowparkでも Snowflake Python APIでもない。
- Storage integrationでexternal functionは呼び出せない。逆にAPI integrationでexternal stageは作れない。
- Git repository objectはschema-levelだが、それが参照するAPI integrationはaccount-levelである。
- Git repositoryの同期はremoteからcloneへの`FETCH`で行う。
- External access integrationは`ALLOWED_NETWORK_RULES`が必須で、UDFやprocedureの外向き通信に使う。
- ServiceNowなどのSaaS向けconnectorはNative Appとしてinstallするもので、driverのように組み込まない。

## 確認問題

- [C3-3.3-Q01: driverの役割](../../exercises/chapter/c3-3.3-q01.md)
- [C3-3.3-Q02: Python向けlibraryの使い分け](../../exercises/chapter/c3-3.3-q02.md)
- [C3-3.3-Q03: Kafka connectorの既定列](../../exercises/chapter/c3-3.3-q03.md)
- [C3-3.3-Q04: Spark connectorとSnowpark](../../exercises/chapter/c3-3.3-q04.md)
- [C3-3.3-Q05: Storage integrationの目的](../../exercises/chapter/c3-3.3-q05.md)
- [C3-3.3-Q06: 許可範囲のパラメータ](../../exercises/chapter/c3-3.3-q06.md)
- [C3-3.3-Q07: API integrationとexternal function](../../exercises/chapter/c3-3.3-q07.md)
- [C3-3.3-Q08: Git integrationに必要なobject](../../exercises/chapter/c3-3.3-q08.md)
- [C3-3.3-Q09: Git repositoryの参照path](../../exercises/chapter/c3-3.3-q09.md)
- [C3-3.3-Q10: integrationの種類](../../exercises/chapter/c3-3.3-q10.md)

## 章のまとめ

- Driverは自作applicationからの接続、connectorは既存productとの受け渡し、integrationは外部serviceへの経路を担当する。
- Kafka connectorは2つのロード方式を選べ、Spark connectorはJDBC経由でpushdownを行う。
- Storage integrationはstorage、API integrationはHTTPS endpointを対象とし、許可範囲の指定パラメータが異なる。
- Git integrationはsecret、API integration、Git repositoryの組合せで構成し、`FETCH`でremoteから同期する。
- Integrationはすべてaccount-level objectであり、作成権限は既定でACCOUNTADMINにある。

## 次に学ぶこと

[Domain 4: 性能最適化、クエリ、変換](../domain-4/README.md)では、取り込んだデータに対するquery性能の評価と最適化を学びます。取り込み方式の選択が、その後のquery性能とcostへどう効くかを結び付けて確認してください。

## 根拠・関連する公式ドキュメント

- `docs-drivers-overview` — https://docs.snowflake.com/en/developer-guide/drivers
- `docs-jdbc` — https://docs.snowflake.com/en/developer-guide/jdbc/jdbc
- `docs-odbc` — https://docs.snowflake.com/en/developer-guide/odbc/odbc
- `docs-python-connector` — https://docs.snowflake.com/en/developer-guide/python-connector/python-connector
- `docs-python-api-overview` — https://docs.snowflake.com/en/developer-guide/snowflake-python-api/snowflake-python-overview
- `docs-kafka-connector-overview` — https://docs.snowflake.com/en/user-guide/kafka-connector-overview
- `docs-spark-connector-overview` — https://docs.snowflake.com/en/user-guide/spark-connector-overview
- `docs-storage-integration-ddl` — https://docs.snowflake.com/en/sql-reference/sql/create-storage-integration
- `docs-s3-storage-integration` — https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration
- `docs-api-integration-ddl` — https://docs.snowflake.com/en/sql-reference/sql/create-api-integration
- `docs-external-functions` — https://docs.snowflake.com/en/sql-reference/external-functions
- `docs-git-overview` — https://docs.snowflake.com/en/developer-guide/git/git-overview
- `docs-git-setting-up` — https://docs.snowflake.com/en/developer-guide/git/git-setting-up
- `docs-git-repository-ddl` — https://docs.snowflake.com/en/sql-reference/sql/create-git-repository
- `docs-alter-git-repository` — https://docs.snowflake.com/en/sql-reference/sql/alter-git-repository
- `docs-security-integration-ddl` — https://docs.snowflake.com/en/sql-reference/sql/create-security-integration
- `docs-notification-integration-ddl` — https://docs.snowflake.com/en/sql-reference/sql/create-notification-integration
- `docs-external-access-integration-ddl` — https://docs.snowflake.com/en/sql-reference/sql/create-external-access-integration
