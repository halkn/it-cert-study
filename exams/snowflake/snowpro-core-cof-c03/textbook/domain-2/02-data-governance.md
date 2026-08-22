# 2.2 データガバナンス機能と用途を定義する

> Status: complete
> Last verified: 2026-08-17

## この章で学ぶこと

この章を終えると、次を説明・判断できます。

- 行を減らすrow access policyと、列値を変えるmasking policyを使い分ける
- Tagでdataを分類し、policyの適用やcost attributionへつなげる
- Privacy policyでdifferential privacyを適用する要件を識別する
- Trust Centerでaccountのsecurity postureを継続評価する
- Snowflake管理keyとcustomer-managed keyの責任範囲を区別する
- Alertの判定・actionとnotificationの配送を分ける
- Replicationとfailoverの目的を区別する
- Lineageでupstream／downstreamのdata flowとdependencyを追う

## 前提知識

- [2.1 セキュリティモデル](01-security-model.md)のrole、privilege、context function
- Rowはtableの横方向のrecord、columnは同じ属性を持つ縦方向のfieldであること
- Primaryは更新元、secondaryは複製先という一般的な意味

## この章の用語

| 用語 | この章での意味 |
|---|---|
| masking policy | Query時にcontextなどを評価し、columnの返却値を変換するschema-level object |
| row access policy | Query時に各rowを返すか評価するschema-level object |
| tag | Snowflake objectへkey-value型の分類情報を付けるschema-level object |
| privacy policy | Differential privacyで個人に関する推測riskを抑えるpolicy |
| scanner | Trust Centerでaccountをsecurity recommendationに照らして評価する処理 |
| CMK | Customer-Managed Key。Customerがcloud KMSで管理する鍵 |
| alert | Conditionを評価し、trueならactionを実行するschema-level object |
| notification integration | Snowflakeからemail、queue、webhookなどへmessageを配送する設定 |
| replication group | 対象object、複製先、scheduleをまとめるobject |
| failover group | Replicationに加えてsecondaryをprimaryへ昇格できるobject |
| lineage | Dataのsourceからtargetへの移動またはobject dependencyの関係 |

## 試験範囲との対応

| Topic | 本文 | 主な公式根拠 |
|---|---|---|
| Data masking／row-level／column-level security | [Query結果を行と列で制御する](#data-masking) | `docs-column-security`, `docs-row-access-policies` |
| Object tagging | [分類をpolicyとcostへ再利用する](#object-tagging) | `docs-object-tagging` |
| Privacy policy | [個人に関する推測riskを制限する](#privacy-policies) | `docs-differential-privacy`, `docs-privacy-overview` |
| Trust Center | [scannerでsecurity postureを評価する](#trust-center) | `docs-trust-center` |
| Encryption key management | [key hierarchyとCMKの責任を分ける](#encryption-key-management) | `docs-encryption-key-management`, `docs-encryption-tss` |
| Alert | [conditionがtrueならactionを実行する](#alerts) | `docs-alerts` |
| Notification | [messageを外部channelへ配送する](#notifications) | `docs-notifications` |
| Data replication／failover | [同期と昇格を分ける](#replication-failover) | `docs-replication-bcdr` |
| Data lineage | [upstreamとdownstreamを追跡する](#data-lineage) | `docs-data-lineage` |

公式ObjectiveとTopicは[COF-C03 Syllabus](../../docs/syllabus.md#22-データガバナンス機能と用途を定義する)から公式Study Guideへ辿って確認できます。

## Governanceは分類・適用・検証の循環で考える

Data governanceはpolicy objectを作るだけでは完了しません。

1. Tagやlineageでdataの意味、sensitivity、流れを把握する。
2. Role、masking、row access、privacyなどのpolicyを適用する。
3. Trust Center、policy reference、query historyなどで状態を検証する。
4. Alert／notificationで変化へ対応する。

[図を開く: Governance policyの適用単位](../../diagrams/domain-2/governance-policies.md)

<a id="data-masking"></a>
## Data masking — Query結果を行と列で制御する

### Column-level securityは返す値を変える

Dynamic Data Maskingはmasking policyをtable／viewのcolumnへ適用し、query実行時にroleなどのcontextを評価して返却値を変えます。Base tableの値を静的に書き換える機能ではありません。

```sql
CREATE MASKING POLICY email_mask AS
  (val STRING) RETURNS STRING ->
  CASE
    WHEN IS_ROLE_IN_SESSION('PII_READER') THEN val
    ELSE '***MASKED***'
  END;

ALTER TABLE customers
  MODIFY COLUMN email
  SET MASKING POLICY email_mask;
```

Authorized roleには元のemail、その他にはmask済み値を返します。同じdataを複製してrole別tableを作る必要を減らせます。Masking policyのinputとreturnは同じdata typeであることが基本です。

### Row-level securityは返すrecordを減らす

Row access policyはtable／viewへ適用し、policy signatureのcolumnとcontext、必要に応じてmapping tableを使って各rowを返すか判定します。

```sql
CREATE ROW ACCESS POLICY region_filter AS
  (region STRING) RETURNS BOOLEAN ->
    region = CURRENT_REGION()
    OR IS_ROLE_IN_SESSION('GLOBAL_SALES');

ALTER TABLE orders
  ADD ROW ACCESS POLICY region_filter ON (region);
```

実務では`CURRENT_REGION()`がbusiness regionを表すとは限らないため、roleやmapping tableを使う設計が一般的です。この例の目的はBoolean判定でrowをfilterする構造を示すことです。

### 行・列・権限を区別する

| 要件 | 選ぶ制御 | 結果 |
|---|---|---|
| APAC担当にはAPACのrowだけ | Row access policy | Result rowをfilter |
| Support担当には電話番号の末尾だけ | Masking policy | Column valueを変換 |
| Tableを一切queryさせない | Role／`SELECT` privilege | Object accessを拒否 |

Column-level securityとrow-level securityはEnterprise Edition以上が必要です。Policy要件とEdition要件を同時に確認します。

<a id="object-tagging"></a>
## Object tagging — 分類をpolicyとcostへ再利用する

Tagはschema-level objectで、Snowflake objectへtag valueを関連付けます。たとえば`sensitivity = pii`、`cost_center = finance`のように分類します。

```sql
CREATE TAG governance.tags.sensitivity
  ALLOWED_VALUES 'public', 'internal', 'pii';

ALTER TABLE customers
  MODIFY COLUMN email
  SET TAG governance.tags.sensitivity = 'pii';
```

Tagは分類metadataです。単独で値をmaskしません。Tag-based maskingではmasking policyをtagへ関連付け、そのtagが付いた対応data typeのcolumnへpolicyを適用します。分類と強制を分けて理解します。

Tagはdatabase、schema、table、column、warehouseなど複数object typeへ利用でき、discovery、policy適用、cost attributionに再利用できます。Allowed valuesを設定すると表記ゆれを抑えられます。

Object taggingはEnterprise Edition以上です。Tagによる設計を選ぶときはEdition条件も確認します。

<a id="privacy-policies"></a>
## Privacy policy — 個人に関する推測riskを制限する

Privacy policyはtable／viewへdifferential privacyを適用します。Analystが集計queryを繰り返しても、特定個人に関する情報を推測しすぎないようprivacy budgetとnoiseを使います。

Masking policyが個々の返却値を置換するのに対し、privacy policyは集計結果から個人を推測するriskを扱います。Aggregation policyは最小group size、projection policyはcolumnの直接投影、join policyは許可するjoinを制御する別のpolicyです。

試験範囲の`privacy policy`はdifferential privacyのobjectを指します。Privacy関連機能全般を一つのpolicy名と誤解しないようにします。Privacy policyはEnterprise Edition以上です。

<a id="trust-center"></a>
## Trust Center — scannerでsecurity postureを評価する

Trust Centerはaccountをsecurity recommendationに照らして継続評価し、potential riskをfindingとして示します。Scanner packageをenableし、scannerを実行して結果を確認します。

- Violationは現在のconfigurationがscanner要件に適合しない継続状態です。
- Detectionは一回のeventとして検出されるfindingです。
- Findingはriskとremediation情報を提供しますが、すべてを自動修正する機能ではありません。

Accessには`SNOWFLAKE.TRUST_CENTER_VIEWER`や`SNOWFLAKE.TRUST_CENTER_ADMIN` application roleを使います。2026年3月にOverview tabがGAとなりましたが、個別scannerやnotificationにはPreview条件がありうるため、導入時は公式ページで状態を再確認します。

<a id="encryption-key-management"></a>
## Encryption key management — key hierarchyとCMKの責任を分ける

Snowflakeは保存dataを階層的なkey modelで暗号化し、通常のkey rotationをSnowflakeが自動管理します。Enterprise以上ではperiodic rekeyingにより既存dataを新しいkeyで再暗号化できます。Customerが自分のcloud KMS keyもcontrolする要件ではTri-Secret Secureを検討します。

Tri-Secret SecureはSnowflake-managed keyとcustomer-managed key（CMK）を組み合わせ、composite account master keyを構成します。このcomposite keyがaccount key hierarchyをwrapします。Raw dataをcomposite master keyで直接暗号化する説明は不正確です。

CMKを無効化・削除するとdata accessへ影響するため、availability、rotation、recoveryを含む運用責任が増えます。Tri-Secret SecureはBusiness Critical以上です。Editionを上げるだけでCMK登録とactivationが自動完了するわけではありません。

<a id="alerts"></a>
## Alert — conditionがtrueならactionを実行する

Snowflake Alertは、condition、action、評価timingを持つschema-level objectです。

- Scheduled alertは定期的に既存data全体へconditionを評価します。
- Alert on new dataはtable／viewへ新しいrowが現れたとき、その新規dataを評価します。

Credit使用量が閾値を超えたかを30分ごとに調べ、trueなら通知procedureをcallする、といった構成に使えます。Alertは判断とactionを担当します。Message配送先のcredentialやchannelはnotification integrationへ分離します。

<a id="notifications"></a>
## Notification — messageを外部channelへ配送する

NotificationはSnowflakeからcloud queue、email、webhookへmessageを送ります。Notification integrationにendpointや許可情報を設定し、`SYSTEM$SEND_SNOWFLAKE_NOTIFICATION`、alert、taskなどから利用します。

Alertなしでもprocedureを直接callして送信できます。一方、alertを使ってもactionがtableへのinsertならnotificationは発生しません。

| 機能 | 答える問い |
|---|---|
| Alert | いつconditionを評価し、trueなら何を実行するか |
| Notification integration | どのchannelへ、どの設定でmessageを送るか |
| Notification history | 過去の送信状態をどう確認するか |

<a id="replication-failover"></a>
## Data replication／failover — 同期と昇格を分ける

Replicationはsource accountの選択したobjectをtarget accountのsecondaryへ非同期で同期します。Replication groupは何を、どこへ、どのscheduleで複製するかを定義します。

Failoverは障害やdrillでsecondary failover groupを新しいwritable primaryへpromoteします。Failbackは元のregionが復旧した後、primaryを戻す手順です。

Replication groupは複製を提供しますが、group自体をprimaryへpromoteするfailover能力はありません。Failover groupはreplicationとpromotionを提供します。Account object replicationとfailover／failbackはBusiness Critical以上です。一方、databaseとshare replicationにはより広いEdition availabilityがあります。

Replicationはbackupと同義ではありません。誤った変更もrefreshによりsecondaryへ伝播しえます。またasynchronous replicationではscheduleに応じたdata lagが生じます。Recovery pointとrecovery time要件からrefresh頻度、runbook、client redirectを設計します。

<a id="data-lineage"></a>
## Data lineage — upstreamとdownstreamを追跡する

Data lineageはdataがどこから来てどこへ進むかを、object／column間の関係として示します。

- Data movement: `CTAS`、`INSERT ... SELECT`、`MERGE`などでdataをmaterialize／copyする関係
- Object dependency: Viewがbase tableを参照するなど、dataをcopyしない依存関係

Sourceはtargetのupstream、targetはsourceのdownstreamです。`CREATE TABLE t2 AS SELECT c1 FROM t1`なら`t1`がupstream、`t2`がdownstreamです。

SnowsightのLineage tabに加え、`SNOWFLAKE.CORE.GET_LINEAGE`でprogrammaticに取得できます。Lineageはimpact analysisやsensitive data flowの確認に使います。すべての過去操作を無条件に再構築できる監査logとは異なり、supported operation、retention、privilegeを確認します。Data lineageはEnterprise Edition以上です。

## Mini hands-on — policyの適用単位を観察する

次は、同じtableにmasking policyとrow access policyを適用し、roleによる結果の違いを確認する構成例です。Enterprise以上の演習accountと、database・role・policyを作成できる管理roleが必要です。共有環境では管理者のpolicyを変更せず、専用databaseで実行します。

```sql
USE ROLE ACCOUNTADMIN;

CREATE DATABASE OBJ22_LAB;
CREATE ROLE OBJ22_APAC_ANALYST;
CREATE ROLE OBJ22_GLOBAL_PII;

SET LAB_USER = CURRENT_USER();
GRANT ROLE OBJ22_APAC_ANALYST TO USER IDENTIFIER($LAB_USER);
GRANT ROLE OBJ22_GLOBAL_PII TO USER IDENTIFIER($LAB_USER);

CREATE TABLE OBJ22_LAB.PUBLIC.CUSTOMERS (
  REGION STRING,
  EMAIL STRING
);

INSERT INTO OBJ22_LAB.PUBLIC.CUSTOMERS VALUES
  ('APAC', 'a@example.com'),
  ('EMEA', 'e@example.com');

CREATE MASKING POLICY OBJ22_LAB.PUBLIC.EMAIL_MASK AS
  (val STRING) RETURNS STRING ->
  CASE
    WHEN IS_ROLE_IN_SESSION('OBJ22_GLOBAL_PII') THEN val
    ELSE '***MASKED***'
  END;

CREATE ROW ACCESS POLICY OBJ22_LAB.PUBLIC.REGION_FILTER AS
  (region STRING) RETURNS BOOLEAN ->
    region = 'APAC'
    OR IS_ROLE_IN_SESSION('OBJ22_GLOBAL_PII');

ALTER TABLE OBJ22_LAB.PUBLIC.CUSTOMERS
  MODIFY COLUMN EMAIL
  SET MASKING POLICY OBJ22_LAB.PUBLIC.EMAIL_MASK;

ALTER TABLE OBJ22_LAB.PUBLIC.CUSTOMERS
  ADD ROW ACCESS POLICY OBJ22_LAB.PUBLIC.REGION_FILTER ON (REGION);

GRANT USAGE ON DATABASE OBJ22_LAB TO ROLE OBJ22_APAC_ANALYST;
GRANT USAGE ON SCHEMA OBJ22_LAB.PUBLIC TO ROLE OBJ22_APAC_ANALYST;
GRANT SELECT ON TABLE OBJ22_LAB.PUBLIC.CUSTOMERS TO ROLE OBJ22_APAC_ANALYST;

GRANT USAGE ON DATABASE OBJ22_LAB TO ROLE OBJ22_GLOBAL_PII;
GRANT USAGE ON SCHEMA OBJ22_LAB.PUBLIC TO ROLE OBJ22_GLOBAL_PII;
GRANT SELECT ON TABLE OBJ22_LAB.PUBLIC.CUSTOMERS TO ROLE OBJ22_GLOBAL_PII;
```

Secondary roleの影響を除き、APAC担当roleで結果を確認します。

```sql
USE ROLE OBJ22_APAC_ANALYST;
USE SECONDARY ROLES NONE;

SELECT REGION, EMAIL
FROM OBJ22_LAB.PUBLIC.CUSTOMERS
ORDER BY REGION;
```

結果はAPACの1 rowだけで、`EMAIL`は`***MASKED***`になります。Row access policyがEMEA rowを除外した後、masking policyが返却するemail値を変えるためです。

次に、全regionのPIIを参照できるroleへ切り替えます。

```sql
USE ROLE OBJ22_GLOBAL_PII;
USE SECONDARY ROLES NONE;

SELECT REGION, EMAIL
FROM OBJ22_LAB.PUBLIC.CUSTOMERS
ORDER BY REGION;
```

結果はAPACとEMEAの2 rowsで、どちらも元のemailを返します。これにより、row access policyはrow数、masking policyは残ったrowのcolumn valueを制御すると観察できます。実環境ではpolicy administratorとobject ownerを分離します。

演習後は、policyを所有する管理roleへ戻して専用objectを削除します。

```sql
USE ROLE ACCOUNTADMIN;
DROP DATABASE IF EXISTS OBJ22_LAB;
DROP ROLE IF EXISTS OBJ22_APAC_ANALYST;
DROP ROLE IF EXISTS OBJ22_GLOBAL_PII;
```

## Compare — governance要件から機能を選ぶ

| 要件 | 選ぶ機能 |
|---|---|
| Roleに応じてemail表示を一部隠す | Masking policy |
| 担当地域外のrecordを返さない | Row access policy |
| PII columnを分類して一括管理する | Tag、必要に応じてtag-based policy |
| 集計の反復から個人を推測しにくくする | Privacy policy |
| Account設定をrecommendationへ照合する | Trust Center |
| Customerがcloud KMS keyもcontrolする | Tri-Secret Secure |
| Data conditionが成立したら処理する | Alert |
| Email／queue／webhookへmessageを送る | Notification |
| 別regionへobjectを同期する | Replication group |
| Secondaryをwritable primaryへ昇格する | Failover group |
| Sensitive columnの派生先を追う | Data lineage |

## 試験で重要なポイント

- Masking policyはcolumn value、row access policyはresult rowを制御する。
- Tagは分類metadataであり、単独ではdata accessを強制しない。
- Privacy policyはdifferential privacyを提供する。
- Alertはconditionとaction、notificationはmessage配送を担当する。
- Replicationは同期、failoverはsecondaryのpromotionである。
- Lineageではsourceがupstream、targetがdownstreamである。

## 間違えやすいポイント

- Dynamic maskingはbase dataの静的置換ではない。
- Trust Center findingは必ずしも自動修正されない。
- Customer-managed keyはcontrolを増やす一方、availability責任も増やす。
- Replicationをpoint-in-time backupとみなさない。
- Object dependencyとdata movementはどちらもlineageだが、物理copyの有無が異なる。
- Enterprise／Business CriticalなどEdition条件を機能要件と同時に確認する。

## 確認問題

- [C2-2.2-Q01: Data masking](../../exercises/chapter/c2-2.2-q01.md)
- [C2-2.2-Q02: Object tagging](../../exercises/chapter/c2-2.2-q02.md)
- [C2-2.2-Q03: Privacy policy](../../exercises/chapter/c2-2.2-q03.md)
- [C2-2.2-Q04: Trust Center](../../exercises/chapter/c2-2.2-q04.md)
- [C2-2.2-Q05: Encryption key management](../../exercises/chapter/c2-2.2-q05.md)
- [C2-2.2-Q06: Alert](../../exercises/chapter/c2-2.2-q06.md)
- [C2-2.2-Q07: Notification](../../exercises/chapter/c2-2.2-q07.md)
- [C2-2.2-Q08: Replication／failover](../../exercises/chapter/c2-2.2-q08.md)
- [C2-2.2-Q09: Data lineage](../../exercises/chapter/c2-2.2-q09.md)

## 章のまとめ

- Data protection policyは適用単位と変える結果で区別する。
- Tagで分類し、policyとcost管理へ再利用する。
- Trust Centerはscannerとfindingでaccountのsecurity postureを可視化する。
- Alertの判定、notificationの配送、lineageの追跡は別の責務である。
- BCDRではreplication scheduleとfailover runbookの両方が必要である。

## 次に学ぶこと

[2.3 監視とコスト管理](03-monitoring-cost.md)では、credit quota、warehouse usage、Account Usage viewを使って運用状態を数値で確認します。

## 根拠・関連する公式ドキュメント

- `docs-column-security` — https://docs.snowflake.com/en/user-guide/security-column-intro
- `docs-row-access-policies` — https://docs.snowflake.com/en/user-guide/security-row-intro
- `docs-create-masking-policy` — https://docs.snowflake.com/en/sql-reference/sql/create-masking-policy
- `docs-create-row-access-policy` — https://docs.snowflake.com/en/sql-reference/sql/create-row-access-policy
- `docs-object-tagging` — https://docs.snowflake.com/en/user-guide/object-tagging/introduction
- `docs-privacy-overview` — https://docs.snowflake.com/en/guides-overview-privacy
- `docs-differential-privacy` — https://docs.snowflake.com/en/user-guide/diff-privacy/differential-privacy-overview
- `docs-trust-center` — https://docs.snowflake.com/en/user-guide/trust-center/overview
- `docs-encryption-tss` — https://docs.snowflake.com/en/user-guide/security-encryption-tss
- `docs-encryption-key-management` — https://docs.snowflake.com/en/user-guide/security-encryption-manage
- `docs-alerts` — https://docs.snowflake.com/en/user-guide/alerts
- `docs-notifications` — https://docs.snowflake.com/en/user-guide/notifications/about-notifications
- `docs-replication-bcdr` — https://docs.snowflake.com/en/user-guide/replication-intro
- `docs-data-lineage` — https://docs.snowflake.com/en/user-guide/ui-snowsight-lineage
