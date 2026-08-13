# Glossary

> Status: draft

用語は定義、関連objective、公式source IDとともに追加します。教材全体の用語は未完成です。

## Objective 1.1

| 用語 | 定義 | Objective | Source ID |
|---|---|---|---|
| Database Storage | 永続dataを保持するSnowflakeのarchitecture layer | 1.1 | `docs-key-concepts-architecture` |
| Compute | SQLやSnowparkの処理を実行するarchitecture layer | 1.1 | `docs-key-concepts-architecture` |
| Cloud Services | 認証、metadata、query parse／optimizationなどを調整するarchitecture layer | 1.1 | `docs-key-concepts-architecture` |
| Virtual Warehouse | 1つ以上のcompute clusterで構成される、ユーザー管理の計算資源 | 1.1 | `docs-key-concepts-architecture` |
| MPP | Massively Parallel Processing。複数nodeで処理を並列実行する方式 | 1.1 | `docs-key-concepts-architecture` |
| Snowflake Edition | 利用可能な機能やservice levelを定める区分 | 1.1 | `docs-snowflake-editions` |
| VPS | Virtual Private Snowflake。他accountから隔離された最上位Edition | 1.1 | `docs-snowflake-editions` |
| metadata | dataの名前、構造、配置、統計など、dataを管理・処理するための情報 | 1.1 | `docs-key-concepts-architecture` |
| role | 利用者や処理へ権限をまとめて与える単位 | 1.1 | `docs-key-concepts-architecture` |
| DML | Data Manipulation Language。tableのdataを読み書きするSQL操作 | 1.1 | `docs-compute-cost` |
| Snowpark | Java、Python、ScalaなどのcodeをSnowflakeで実行するための機能群 | 1.1 | `docs-key-concepts-architecture` |
| credit | Snowflakeのcomputeなどの利用量を表す課金単位 | 1.1 | `docs-compute-cost` |
| micro-partition | Snowflake tableのdataを自動分割して保存する連続したstorage単位 | 1.1 | `docs-key-concepts-architecture` |
| PHI | Protected Health Information。個人を識別できる保護対象の医療情報 | 1.1 | `docs-snowflake-editions` |
| BAA | Business Associate Agreement。PHIを扱う際に必要となる事業提携者契約 | 1.1 | `docs-snowflake-editions` |
