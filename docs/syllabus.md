# SnowPro Core COF-C03 Syllabus

基準は Snowflake 公式 *SnowPro Core COF-C03 Exam Study Guide*（2026-07-08 更新）です。以下は公式目標を教材向けに日本語で再構成したものです。原文は [公式 Study Guide](https://publish-p93462-e887935.adobeaemcloud.com/content/dam/snowpro-sg/SnowProCoreStudyGuideC03.pdf) で確認してください。

## Domain 1 — Snowflake AI Data Cloud の機能とアーキテクチャ（31%）

### 1.1 アーキテクチャを説明し、利用する

Cloud Services、Compute、Database Storage の責務と分離の利点、Snowflake Edition の違いを扱います。

### 1.2 インターフェースとツールを利用する

Snowsight、Snowflake CLI、Visual Studio Code などの IDE 連携を扱います。

### 1.3 オブジェクト階層と種類を区別する

Organization、Account、Database、Schema と各種 database object、セッション／コンテキスト変数、パラメータ階層と優先順位を扱います。

### 1.4 Virtual Warehouse を構成する

Standard と Snowpark-optimized、世代、scaling policy、用途別構成、sizing、scaling、auto-suspend、ワークロード分離を扱います。Notebooks の既定 warehouse は GA 状態を再確認します。

### 1.5 ストレージ概念を説明する

Micro-partition、clustering、permanent／temporary／transient／Iceberg／external／dynamic table、standard／materialized／secure view を扱います。

### 1.6 AI/ML とアプリケーション開発機能を説明する

Notebooks、Streamlit in Snowflake、Snowpark、Cortex AI SQL functions／Search／Analyst、Snowflake ML を扱います。

## Domain 2 — アカウント管理とデータガバナンス（20%）

### 2.1 セキュリティモデルと原則を説明する

RBAC、securable object hierarchy、DAC、network policy、各認証方式、system-defined／account／database／custom／secondary role、account identifier、logging と tracing を扱います。

### 2.2 データガバナンス機能と用途を定義する

masking、row／column level security、tag、privacy policy、Trust Center、暗号鍵管理、alert、notification、replication／failover、lineage を扱います。

### 2.3 監視とコスト管理を説明する

Resource Monitor、warehouse のコスト監視と credit 計算、ACCOUNT_USAGE を扱います。

## Domain 3 — データのロード、アンロード、接続（18%）

### 3.1 データをロード／アンロードする

file format、internal／external stage、server-side encryption、directory table、COPY INTO、エラー処理を扱います。

### 3.2 自動データ取り込みを実行する

Snowpipe、Snowpipe Streaming、Stream、Task、Dynamic Table、Openflow を扱います。Openflow の出題可否は GA 状態と最新 Study Guide を再確認します。

### 3.3 Connector と Integration を識別する

driver、connector、storage／API／Git integration を扱います。

## Domain 4 — 性能最適化、クエリ、変換（21%）

### 4.1 クエリ性能を評価する

Query Profile／Query Insights、spill、pruning、exploding join、queue、ACCOUNT_USAGE の query attribution／history、ワークロード分離を扱います。

### 4.2 クエリ性能を最適化する

Query Acceleration Service、Search Optimization Service、clustering key、materialized view の選定を扱います。

### 4.3 キャッシュを利用する

query result、metadata、warehouse cache の場所、条件、用途の違いを扱います。

### 4.4 データ変換を実行する

構造化／半構造化／非構造化データ、集約、性能を意識した SQL、window function を扱います。

## Domain 5 — データコラボレーション（10%）

### 5.1 コラボレーションとデータ保護を説明する

replication／failover、secure sharing、clone、Time Travel、Fail-safe を扱います。

### 5.2 データ共有機能を説明する

provider／consumer／reader account、Secure Data Sharing、resharing、direct share、Data Clean Room を扱います。

### 5.3 Marketplace と Listing で共有する

Snowflake Marketplace、private／public listing、Native App を扱います。

## 前提知識

公式ガイドでは基本 SQL、データベース基礎、クラウド基礎は試験の直接範囲外ですが、設問理解の前提とされています。本教材では必要箇所で補足し、前提知識そのものの網羅は行いません。
