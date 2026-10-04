# 5.1 コラボレーションとデータ保護を説明する

> Status: complete
> Last verified: 2026-10-03

## この章で学ぶこと

誤更新、開発用の分岐、他accountとの共同利用、region障害を分け、Time Travel、clone、共有、replication／failoverを選びます。Fail-safeを利用者の履歴検索や即時復旧と混同しないことも目標です。

## 前提知識

[1.5 ストレージ概念](../domain-1/05-storage-concepts.md)のmicro-partitionとtable種別、[2.1 セキュリティモデル](../domain-2/01-security-model.md)のroleと権限を前提にします。[2.2](../domain-2/02-data-governance.md)のBCDRを、データ保護手段の比較として整理します。

## この章の用語

| 用語 | 意味 |
|---|---|
| Time Travel | 保持期間内の過去データを検索・複製・復元する機能 |
| Fail-safe | Time Travel終了後、Snowflakeが最終手段として復旧を試みる保護期間 |
| zero-copy clone | 作成時の標準tableのmicro-partitionを共有する独立した複製 |
| replication／refresh | 別accountへデータ等を複製し、secondaryを更新する処理 |
| failover／failback | secondaryをprimaryへ昇格する切替／元の側へ戻す切替 |
| primary／secondary | 複製元の書込み可能な側／refreshを受ける側 |

## 試験範囲との対応

日本語版Study Guide p.12の5.1、全5 Topicに対応します。

| Topic | 本文 | 主な根拠 |
|---|---|---|
| replication／failover | [別regionへの複製と切替](#replication-failover) | `docs-replication-bcdr` |
| secure sharing feature | [読取り権限による共同利用](#secure-sharing-features) | `docs-secure-sharing`, `docs-sharing-secure-objects` |
| cloning | [独立した開発用分岐](#cloning) | `docs-clone-storage`, `docs-clone-command`, `docs-clone-considerations` |
| Time Travel | [過去状態の検索と復元](#time-travel) | `docs-time-travel`, `docs-temp-transient-tables` |
| Fail-safe | [Snowflakeによる最終復旧](#fail-safe) | `docs-fail-safe`, `docs-temp-transient-tables` |

## 保護したい対象から機能を選ぶ

誤ったDELETE直前の状態を確認するなら履歴、開発で自由に変更するなら独立した分岐、取引先に最新データを読ませるなら権限による共有を使います。別regionで業務を継続するなら、別accountに複製を維持して切替へ備えます。

[保護手段の選定図](../../diagrams/domain-5/protection-selection.md)は、利用者による復旧とSnowflakeによる復旧、読取り共有と書込み可能な分岐を区別します。

<a id="replication-failover"></a>
## 別regionへの複製と業務の切替

データと対象objectを別accountへ複製するのがreplicationです。同じorganization内の別region／cloudのaccountへ複製を用意できます。Replication groupは対象、複製先、refreshの予定をまとめ、failover groupは切替能力を加えます。[公式根拠](https://docs.snowflake.com/en/user-guide/replication-intro)

Secondaryのrefreshはprimaryの状態を取り込みますが、同期書込みではありません。障害時に利用できる状態は最後の成功refreshに依存するため、複製を設定しただけでデータ損失ゼロとは判断できません。Replication groupだけではsecondaryを書込み可能なprimaryへ切り替える能力も保証されません。

Failoverではfailover groupのsecondaryをprimaryへ昇格し、その側で書込みを再開します。元の側が回復したら新しいprimaryから状態を同期し、failbackを計画します。Client Redirectは接続URLの行き先を変える機能で、データ複製や昇格の代わりではありません。

Databaseとshareのreplicationは全Editionで利用可能です。Users、roles、warehousesなど他のaccount objectの複製とfailover／failback、Client RedirectにはBusiness Critical以上が必要です。対象objectの対応状況、追加storage・transfer・refreshの費用も確認します。対象の機能が別のEditionを要求する場合、その条件も残ります。

<a id="secure-sharing-features"></a>
## 読取り権限を渡して最新データを共同利用する

Secure Data Sharingではproviderが選んだobjectへの読取りアクセスをconsumerへ渡します。同一regionで通常の共有を行う場合、consumerへtable全体を物理コピーせず、metadataを通じて元データを参照します。Providerの更新がconsumerにも見えるので、固定snapshotや独立したバックアップとは異なります。[共有の仕組み](https://docs.snowflake.com/en/user-guide/data-sharing-intro)

必要な列と行だけを返すsecure viewを公開し、基底tableをshareへ直接追加しない構成を選べます。Secure viewは定義や内部データの露出を抑えますが、`SECURE`と付けるだけで行の許可条件が生まれるわけではありません。必要なfilterやpolicyを別途設計します。[secure objectの利用](https://docs.snowflake.com/en/user-guide/data-sharing-secure-views)

顧客別の売上viewなら、consumer accountに対応した許可行を返します。Consumerの利用者・roleをproviderが管理しているとは限らないため、共有先の判定にprovider内のrole名をそのまま使わないようにします。Account境界、費用負担、SQL手順は[5.2](02-data-sharing.md)で扱います。

<a id="cloning"></a>
## 初期データを共有して独立した開発用分岐を作る

本番と同じデータで変更を試すとき、`CREATE TABLE … CLONE`などでzero-copy cloneを作ります。標準のSnowflake tableでは、作成時に元とcloneが同じmicro-partitionを参照します。その後の変更は新しいpartitionに保存され、元とcloneの変更は相互に反映されません。[storageの仕組み](https://docs.snowflake.com/en/user-guide/tables-storage-considerations)

初期データの追加storageが不要でも、変更後のpartition、履歴保持、queryのcomputeには費用が発生します。「zero-copyだから以後も無料」「元を変更するとcloneも追従する」は誤りです。このstorage説明は標準tableを対象とし、databaseに含まれるhybrid tableなどへ無条件に広げません。

```sql
CREATE TABLE lab.public.orders_trial CLONE prod.public.orders;
CREATE TABLE lab.public.orders_before_fix CLONE prod.public.orders
  AT (OFFSET => -1800);
```

例は同一account内の既存標準tableを現在時点／30分前から複製します。対象がその時点に存在し、履歴が残っている必要があります。実行roleはsource tableのSELECT、sourceとtargetのdatabase／schemaのUSAGE、target schemaのCREATE TABLEを持つものとします。履歴cloneは保持期間を延長しません。[構文と権限](https://docs.snowflake.com/en/sql-reference/sql/create-clone)

Tableのcloneへsourceの明示的grantを引き継ぐには`COPY GRANTS`を使用でき、OWNERSHIPはコピーしません。Database／schemaをcloneした場合は子objectのgrantが引き継がれますが、container自体のgrantは引き継がれません。Object依存や権限まで完全に同じになると考えず、アクセスを確認します。[cloneの注意点](https://docs.snowflake.com/en/user-guide/object-clone)

<a id="time-travel"></a>
## 保持期間内の過去状態を検索・複製・復元する

誤更新前の値を調べるとき、Time Travelでtableの履歴を読みます。`AT`は指定時点、`BEFORE`は指定statementによる変更の直前を選びます。TIMESTAMP、現在からの秒差OFFSET、query IDのSTATEMENTで時点を指定します。[Time Travel](https://docs.snowflake.com/en/user-guide/data-time-travel)

```sql
SELECT order_id, amount
FROM prod.public.orders AT (OFFSET => -600);

CREATE TABLE lab.public.orders_review CLONE prod.public.orders
  BEFORE (STATEMENT => '<誤更新のquery ID>');

USE DATABASE prod;
USE SCHEMA public;
UNDROP TABLE orders;
```

最初は10分前の検索、次は誤更新直前の検証用複製、最後はDROPしたtableの復元です。別の状況で使う例で、連続実行する手順ではありません。SELECTやcloneだけでは元tableを書き戻しません。誤ったDMLの修復は過去結果を確認してから別途行います。

UNDROPはDROP直前の状態でobjectを復元します。対象のOWNERSHIPと復元先のCREATE権限が必要で、tableはcurrent schema、schemaはcurrent databaseで復元します。同名objectが存在すると失敗するので、新しく作った同名objectと消えたobjectを混同せず、既存側をrenameしてから復元します。

### 保持期間はEditionとtable種別の両方で決まる

`DATA_RETENTION_TIME_IN_DAYS`の通常の既定値は1日です。Account／database／schemaの設定を継承でき、objectの明示値で上書きします。Accountの`MIN_DATA_RETENTION_TIME_IN_DAYS`が設定されている場合は、その下限も有効な保持期間へ影響します。

| 標準tableの種別・Edition | 設定可能なTime Travel | Fail-safe |
|---|---|---|
| permanent、Standard | 0〜1日 | 7日 |
| permanent、Enterprise以上 | 0〜90日 | 7日 |
| transient、全Edition | 0〜1日 | なし |
| temporary、全Edition | 0〜1日。ただしsession終了で削除 | なし |

Enterpriseでもtransientを90日にはできません。保持期間を増やすと追加storageが必要で、すでに履歴から除去されたデータは復活しません。STATEMENTのquery ID参照は直近14日までなので、それより前で保持期間内の状態を指定するにはTIMESTAMPを使用します。[table種別](https://docs.snowflake.com/en/user-guide/tables-temp-transient)、[時点指定の制約](https://docs.snowflake.com/en/sql-reference/sql/create-clone)

<a id="fail-safe"></a>
## Time Travel終了後の最終復旧をSnowflakeへ依頼する

標準のpermanent tableでは、Time Travel終了後に変更不能な7日のFail-safe期間があります。利用者がSQLで履歴を検索する期間ではありません。ほかの手段で回復できない場合、Snowflake Supportへ依頼し、Snowflakeがbest effortで復旧を試みます。数時間から数日かかることがあり、成功や即時復旧を保証する手段として扱いません。[Fail-safe](https://docs.snowflake.com/en/user-guide/data-failsafe)

Temporary／transientにはFail-safeがありません。再生成できる中間データならtransientで保護storageの費用を抑えられますが、Time Travelを過ぎた後の復旧手段を失います。Permanentの履歴storageやFail-safe復旧のserverless computeも費用対象で、無料の長期バックアップとは考えません。Snowpipe Streamingのclassic architectureで投入されたデータを含むtableではFail-safe復旧は対応しないため、標準permanentという種別だけで全投入経路の対応を推測しません。

## 要件と手段の比較

| 要件 | 選ぶ手段 | 代替にならない理由 |
|---|---|---|
| 保持期間内の誤DROPを戻す | UNDROP | cloneは新しいobjectを作る |
| 誤更新前の値を比較する | Time TravelのSELECT | Fail-safeは利用者の履歴検索ではない |
| 本番から独立して変更を試す | clone | shareは読取り専用で元の更新を参照する |
| 取引先に最新の限定データを読ませる | Secure Data Sharing | cloneは作成後に同期しない |
| region障害後に別accountで書込みを再開する | replicationとfailover group | Time Travelは業務の接続先を切り替えない |

## 試験で重要なポイント

現在の独立した複製と過去状態の利用を分けます。Time Travelとcloneは組み合わせられますが、Fail-safeはSQLで利用できません。Replicationの対象とfailoverのEdition条件を別々に確認します。

## 間違えやすいポイント

保持日数を延長しても消えた履歴は戻りません。Cloneは変更が独立し、shareは元の最新データを参照します。別regionへ共有するときのreplicationやauto-fulfillmentは、同一region共有の「データをコピーしない」説明から除外して考えます。

## 確認問題

- [C5-5.1-Q01: 別regionの書込み再開](../../exercises/chapter/c5-5.1-q01.md)
- [C5-5.1-Q02: 共有と開発用分岐](../../exercises/chapter/c5-5.1-q02.md)
- [C5-5.1-Q03: Cloneの変更とstorage](../../exercises/chapter/c5-5.1-q03.md)
- [C5-5.1-Q04: 保持期間の上限](../../exercises/chapter/c5-5.1-q04.md)
- [C5-5.1-Q05: Fail-safeの担当](../../exercises/chapter/c5-5.1-q05.md)

## 章のまとめ

履歴の検索・復元はTime Travel、独立した分岐はclone、最新データの共同利用はshare、別regionの継続はreplicationとfailoverです。Fail-safeは利用者が操作できない最終手段です。

## 次に学ぶこと

[5.2 データ共有](02-data-sharing.md)でproviderとconsumerの作業・権限・費用負担を確認します。

## 根拠・関連する公式ドキュメント

- `docs-replication-bcdr` — https://docs.snowflake.com/en/user-guide/replication-intro
- `docs-secure-sharing` — https://docs.snowflake.com/en/user-guide/data-sharing-intro
- `docs-sharing-secure-objects` — https://docs.snowflake.com/en/user-guide/data-sharing-secure-views
- `docs-clone-storage` — https://docs.snowflake.com/en/user-guide/tables-storage-considerations
- `docs-clone-command` — https://docs.snowflake.com/en/sql-reference/sql/create-clone
- `docs-clone-considerations` — https://docs.snowflake.com/en/user-guide/object-clone
- `docs-time-travel` — https://docs.snowflake.com/en/user-guide/data-time-travel
- `docs-temp-transient-tables` — https://docs.snowflake.com/en/user-guide/tables-temp-transient
- `docs-fail-safe` — https://docs.snowflake.com/en/user-guide/data-failsafe
