# SnowPro Core COF-C03 Syllabus

基準は英語版 Snowflake 公式 *SnowPro Core COF-C03 Exam Study Guide*（2026-07-08 更新）です。以下は公式目標とトピックを教材向けに日本語で再構成したものです。日本語版Study Guideとの同等性は未検証であり、確認状態は `sources.json` に記録します。原文は [公式 Study Guide](https://publish-p93462-e887935.adobeaemcloud.com/content/dam/snowpro-sg/SnowProCoreStudyGuideC03.pdf) で確認してください。

## Domain 1 — Snowflake AI Data Cloud の機能とアーキテクチャ（31%）

### 1.1 アーキテクチャを説明し、利用する

- Cloud Services layer
- Compute layer
- Database Storage layer
- Snowflake Edition の比較

### 1.2 インターフェースとツールを利用する

- Snowsight
- Snowflake CLI
- IDE integration（Visual Studio Codeなど）

### 1.3 オブジェクト階層と種類を区別する

- OrganizationとAccountのオブジェクト
- Database object: stage、schema、table、view、UDF、file format、stored procedure、pipe、share、sequence、ML model、application
- Session／context variable、parameter hierarchy、parameter precedence

### 1.4 Virtual Warehouse を構成する

- Warehouse type: Snowpark-optimized、Standard Gen 1／Gen 2、Notebooksの既定warehouse
- Scaling policy
- 用途別構成: ad-hoc query、data loading、BI／reporting
- Best practice: sizing up/down、scaling in/out、auto-suspend、チーム分離、高同時実行、複雑なquery

Notebooksの既定warehouseは、global GAまでは出題対象外です。GA後も最新Study Guideで出題範囲を再確認します。

### 1.5 ストレージ概念を説明する

- Micro-partition
- Data clustering
- Table type: permanent、temporary、transient、Apache Iceberg、external、dynamic
- View type: standard、materialized、secure

### 1.6 AI/ML とアプリケーション開発機能を説明する

- Snowflake Notebooks
- Streamlit in Snowflake
- Snowpark
- Snowflake Cortex: AI SQL functions、Cortex Search、Cortex Analyst
- Snowflake ML

## Domain 2 — アカウント管理とデータガバナンス（20%）

### 2.1 セキュリティモデルと原則を説明する

- RBAC、securable object hierarchy、DAC、network policy
- Authentication: MFA、federated authentication、SSO、OAuth、key-pair authentication
- System-defined role
- Functional role: account role、database role、custom role
- Secondary role、account identifier、logging／tracing

### 2.2 データガバナンス機能と用途を定義する

- Data masking、row-level security、column-level security
- Object tagging、privacy policy、Trust Center
- Encryption key management
- Alert、notification
- Data replication／failover、data lineage

### 2.3 監視とコスト管理を説明する

- Resource Monitorによるcost／warehouse monitoring
- Virtual Warehouseのcredit使用量計算
- ACCOUNT_USAGE schema

## Domain 3 — データのロード、アンロード、接続（18%）

### 3.1 データをロード／アンロードする

- File format
- Stage: internal、external、server-side encryption、directory table
- COPY INTO command
- Error handling option

### 3.2 自動データ取り込みを実行する

- Snowpipe
- Snowpipe Streaming
- Stream
- Task
- Dynamic Table
- Openflow

Openflowは、global GAまでは出題対象外です。GA後も最新Study Guideで出題範囲を再確認します。

### 3.3 Connector と Integration を識別する

- Snowflake driver
- Snowflake connector
- Storage integration
- API integration
- Git integration

## Domain 4 — 性能最適化、クエリ、変換（21%）

### 4.1 クエリ性能を評価する

- Query Profile／Query Insights: bytes spilled to storage、inefficient pruning、exploding join、queuing
- SNOWFLAKE.ACCOUNT_USAGE view: query attribution、query history
- Workload management: 類似workloadのグループ化

### 4.2 クエリ性能を最適化する

- Query Acceleration Service
- Search Optimization Service
- Clustering key
- Materialized view

### 4.3 キャッシュを利用する

- Query result cache
- Metadata cache
- Warehouse cache

### 4.4 データ変換を実行する

- Structured／semi-structured／unstructured data
- Aggregate function
- クエリ最適化のためのSQL
- Window function

## Domain 5 — データコラボレーション（10%）

### 5.1 コラボレーションとデータ保護を説明する

- Data replication／failover
- Secure data sharing feature
- Cloning
- Time Travel
- Fail-safe

### 5.2 データ共有機能を説明する

- Account: provider、consumer、reader account
- Secure Data Sharing
- Sharing／resharing
- Direct share
- Data Clean Room

### 5.3 Marketplace と Listing で共有する

- Snowflake Marketplace
- Listing: private、public
- Native App

## 前提知識

公式ガイドでは基本 SQL、データベース基礎、クラウド基礎は試験の直接範囲外ですが、設問理解の前提とされています。本教材では必要箇所で補足し、前提知識そのものの網羅は行いません。
