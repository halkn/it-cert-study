# Driver・connector・integrationの担当範囲

```mermaid
flowchart LR
  APP[自作application] -->|JDBC / ODBC / Python / Node.js / Go| SF
  KAFKA[Kafka] -->|Kafka connector<br/>Snowpipe または Snowpipe Streaming| SF
  SPARK[Spark cluster] -->|Spark connector<br/>内部でJDBC driverを使用| SF

  subgraph SF[Snowflake account]
    STG[External stage] --- SI
    EF[External function] --- AI
    GR[Git repository] --- AI
    UDF[UDF / procedure handler] --- EAI
    SI[Storage integration]
    AI[API integration]
    EAI[External access integration]
    NI[Notification integration]
    SEC[Security integration]
  end

  SI -->|bucket / path を許可| CS[(Cloud storage)]
  AI -->|HTTPS endpointを許可| HS[HTTPS proxy service<br/>API Gateway / Git host]
  EAI -->|network ruleを許可| NET[外部network location]
  NI -->|通知を配送| MSG[Queue / email / webhook]
  SEC -->|認証を委譲| IDP[External IdP / OAuth client]
```

- 左からSnowflakeへ入る矢印がdriverとconnector、Snowflakeから外へ出る矢印がintegrationです。
- Storage integrationは`STORAGE_ALLOWED_LOCATIONS`でbucketとpathを、API integrationは`API_ALLOWED_PREFIXES`でHTTPS endpointを許可します。
- Git repositoryはAPI integration（`API_PROVIDER = git_https_api`）とsecretを前提に構成します。

根拠: `docs-drivers-overview`, `docs-kafka-connector-overview`, `docs-spark-connector-overview`, `docs-storage-integration-ddl`, `docs-api-integration-ddl`, `docs-git-repository-ddl`, `docs-external-access-integration-ddl`, `docs-notification-integration-ddl`, `docs-security-integration-ddl`
