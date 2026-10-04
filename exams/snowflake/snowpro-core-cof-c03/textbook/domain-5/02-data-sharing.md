# 5.2 データ共有機能を説明する

> Status: complete
> Last verified: 2026-10-03

## この章で学ぶこと

Provider、consumer、reader accountの責務と費用を区別し、direct shareの公開からconsumer内のgrantまでを説明します。再共有の条件と、共同分析を制約するData Clean Roomの用途も判断します。

## 前提知識

[5.1](01-collaboration-protection.md)の共有とcloneの違い、[2.1](../domain-2/01-security-model.md)のUSAGE、SELECT、OWNERSHIPを使います。共有と同じaccount内のroleへのgrantは異なる境界です。

## この章の用語

| 用語 | 意味 |
|---|---|
| provider／consumer | データを公開するaccount／公開されたデータを使うaccount |
| share | 共有するobjectへの権限と利用可能なaccountをまとめるobject |
| imported database | Consumerがshareから作る読取り専用database |
| reader account | Providerが作成・管理する、非Snowflake顧客向けの利用account |
| direct share | 特定の同一region accountへshareを直接公開する方法 |
| resharing | 受け取ったデータを許可条件の下で別accountへ共有すること |
| Data Clean Room | 提供データと分析方法・出力の制約を組み合わせる共同分析環境 |

## 試験範囲との対応

日本語版Study Guide p.12の5.2、全5 Topicに対応します。

| Topic | 本文 | 主な根拠 |
|---|---|---|
| accounts | [責務と費用負担](#accounts) | `docs-secure-sharing`, `docs-reader-accounts` |
| Secure Data Sharing | [objectとroleの境界](#secure-data-sharing) | `docs-sharing-provider`, `docs-sharing-consumer` |
| sharing／resharing | [再共有の条件](#sharing-resharing) | `docs-resharing`, `docs-resharer`, `docs-sharing-consumer` |
| direct share | [公開と取込みのSQL](#direct-shares) | `docs-sharing-provider`, `docs-sharing-consumer`, `docs-grant-share` |
| Data Clean Room | [制約付き共同分析](#data-clean-rooms) | `docs-cleanrooms-overview`, `docs-cleanrooms-legacy-policies` |

<a id="accounts"></a>
## Provider・consumer・reader accountの責務と費用負担

Providerは元データを保持し、共有object、許可するconsumer、公開範囲を管理します。通常のconsumerは自分のaccountのwarehouseで共有データをqueryし、そのcomputeを負担します。同一regionの通常共有ではconsumerに共有データの物理コピーを保存しないため、その共有データ自体のstorage料金はconsumerに発生しません。[共有モデル](https://docs.snowflake.com/en/user-guide/data-sharing-intro)

Snowflakeと直接契約していない取引先には、providerがreader accountを作れます。Readerは作成したproviderのデータだけを利用し、warehouseでqueryできますが、ロード、INSERT、UPDATEなどのDMLはできません。通常のconsumerと異なり、readerのwarehouse creditはproviderが負担します。[Reader管理](https://docs.snowflake.com/en/user-guide/data-sharing-reader-create)

Reader accountの作成はACCOUNTADMINまたはCREATE ACCOUNTを付与されたroleが行います。Providerは利用者・role・warehouseの運用とサポートも担当し、reader warehouseにResource Monitorを設定してcredit使用を管理します。Readerの費用を取引先へ請求する契約は、Snowflake側のcredit負担先とは別の話です。

| 項目 | 通常のconsumer | Reader account |
|---|---|---|
| Accountの管理 | Consumer自身 | 作成したprovider |
| 読むprovider | 許可された複数providerも可 | 作成したproviderのみ |
| Queryのwarehouse credit | Consumer | Provider |
| ロード／DML | 自分の通常databaseで可能。共有objectは不可 | 不可 |

<a id="secure-data-sharing"></a>
## 共有objectとconsumer内のroleを二段階で許可する

Shareはデータを格納するtableではなく、共有対象への権限とaccount間アクセスをまとめます。DatabaseとschemaのUSAGE、対象table／viewのSELECTなどをshareへ与え、consumer accountを追加します。Consumerがshareを見つけることと、consumer内の各roleがqueryできることは別です。[公開側の作業](https://docs.snowflake.com/en/user-guide/data-sharing-provider)

Consumerはshareからimported databaseを作ります。共有objectは読取り専用で、INSERT、UPDATE、object作成はできません。Imported databaseやそのschema／tableのcloneとTime Travelも利用できません。Providerの履歴設定をconsumerが自分で操作できると考えないようにします。[取込み側の制約](https://docs.snowflake.com/en/user-guide/data-share-consumers)

Providerがobjectをdatabase roleで区分していない場合、consumerは`IMPORTED PRIVILEGES`を自分のaccount roleへgrantします。Database roleで区分した場合は、imported database内の対応database roleをaccount roleへgrantします。ConsumerがschemaのUSAGEだけを得ても、これらの共有アクセスを代替できません。

元tableの新規行や更新は、すでにアクセス可能なconsumerにも見えます。一方、新しいtableやDROPして再作成した同名objectは、shareへ明示的にgrantする必要があります。Shareに対するfuture grantsは利用できません。[GRANT TO SHARE](https://docs.snowflake.com/en/sql-reference/sql/grant-privilege-share)

<a id="direct-shares"></a>
## Direct shareを公開してconsumerで取り込む

同じregionの既知のaccountへ限定したデータを渡すならdirect shareが適します。Marketplaceの検索・商品説明・課金機能を必要としない場合の単純なaccount間共有です。別regionでは、対象regionへのreplicationを準備するか、[5.3のauto-fulfillment](03-marketplace-listings.md#cross-region)を使うListingを検討します。

以下は既存の`prod.partner.customer_sales`を公開する例です。これは必要な列・行に絞ったsecure viewであり、基底tableはshareへ追加しません。Provider内でCREATE SHARE、shareの管理権限、対象objectのgrant権限を持つroleが実行します。Database roleを使わず、objectを直接grantする方式です。

```sql
CREATE SHARE customer_sales_share;
GRANT USAGE ON DATABASE prod TO SHARE customer_sales_share;
GRANT USAGE ON SCHEMA prod.partner TO SHARE customer_sales_share;
GRANT SELECT ON VIEW prod.partner.customer_sales TO SHARE customer_sales_share;
ALTER SHARE customer_sales_share ADD ACCOUNTS = partner_org.partner_account;
SHOW GRANTS TO SHARE customer_sales_share;
```

公開先identifierは例示値なので、同一regionの実在するaccount identifierに置き換えます。CREATE SHAREだけでは空のshareができ、SELECTのgrantだけでも利用accountは追加されません。Account指定とobject権限の両方を確認します。[Provider SQL](https://docs.snowflake.com/en/user-guide/data-sharing-provider)

Consumer側はCREATE DATABASEとIMPORT SHAREを持つroleが、SHOW SHARESで表示されたprovider identifierとshare名を使います。以下の`provider_locator`は置換する値です。ANALYSTは既存account roleとします。

```sql
SHOW SHARES;
CREATE DATABASE partner_sales FROM SHARE provider_locator.customer_sales_share;
GRANT IMPORTED PRIVILEGES ON DATABASE partner_sales TO ROLE analyst;
```

最後のgrantはimported databaseのownerまたはMANAGE GRANTSを持つroleが行います。Analystによるqueryには別途warehouseのUSAGEも必要です。Providerのaccountにanalystを作成する手順ではありません。

Database roleで分割されたshareでは、代わりに次のように付与します。`sales_reader`はproviderから公開された既存database roleで、consumerが任意のrole名を指定して公開範囲を増やせるわけではありません。

```sql
GRANT DATABASE ROLE partner_sales.sales_reader TO ROLE analyst;
```

## 公開範囲を減らすときの作用

Providerはshareのobject権限をrevokeしたり、consumer accountをshareからremoveしたりして、以後の共有アクセスを停止できます。Consumerのimported databaseは独立したデータコピーではないため、元の許可が必要です。ただしconsumerがすでに取得・保存したquery結果や自分のtableへ複写したデータを、この操作で回収することはできません。読取り専用は元objectへの変更制限であり、情報を取得できないという意味ではありません。

<a id="sharing-resharing"></a>
## 受け取ったデータを再共有する条件を確認する

Imported databaseやそのtableをそのまま別shareへgrantすることはできません。現在は、再共有が許可されたデータを自分のdatabaseのsecure viewから参照し、そのviewを下流へ共有するresharingに対応します。「Imported objectを直接shareへ追加できない」と「再共有が一切できない」を区別します。[再共有の概要](https://docs.snowflake.com/en/collaboration/reshare-listings)、[実行側の条件](https://docs.snowflake.com/en/collaboration/resharing-as-resharer)

Direct shareの再共有はconsumer自身のorganization内・同一regionに限られ、SHOW DATABASESのresharing_settingsで許可を確認します。Listingではproviderの有効な`resharing.enabled`と`resharing.only_within_organization`を確認し、許可された範囲へ共有します。再共有するためにimported databaseへviewを作るのではなく、自分の通常databaseへsecure viewを作ります。Native Appそのもののresharingは対応しません。[Direct shareの再共有](https://docs.snowflake.com/en/user-guide/data-share-consumers)

再共有の既定値はbehavior change bundleの適用で変わるため、許可を既定値から推測しません。2026_05の変更はorganization内への再共有を既定で許可する内容ですが、教材・設問ではproviderの有効な設定を明示して判断します。Organization外を禁止した設定で、consumerが自分のviewを作るだけでは制限を回避できません。[変更の根拠](https://docs.snowflake.com/en/release-notes/bcr-bundles/2026_05/bcr-2324)

<a id="data-clean-rooms"></a>
## 生データの公開と分析の許可を分けるData Clean Room

二社の顧客データを突き合わせて共通顧客の集計を求めたいが、双方の明細を自由に読ませたくない場合、Snowflake Data Clean Roomsを選びます。提供データ、利用できる分析、返す結果の制約を組み合わせる共同分析環境です。単にshared tableへSELECTを許可する場合より、利用方法を細かく制御する設計に向きます。

現在のcollaboration方式では、ownerが参加accountと役割を定め、data providerがデータと適用policyを持つdata offeringを公開し、analysis runnerが許可されたtemplateとdata offeringで分析します。Ownerであるだけでは分析実行権限を持ちません。Templateは実行時の値を受け取るJinjaSQLによる分析定義です。集計のみを返したいなら、その出力とpolicyを設計・確認します。Clean Roomという名前だけで明細の取得が自動的に禁止されるわけではありません。[現行方式の概要](https://docs.snowflake.com/en/user-guide/cleanrooms/overview)

従来のprovider／consumer方式では、許可JOIN列や結果へ出せる列をClean Room policyで指定します。カスタムtemplateには対応するpolicy filterが必要で、policyの設定だけでは検査されません。この旧方式の条件を現行collaborationの仕様へ一律に適用しないようにします。[従来方式のpolicy条件](https://docs.snowflake.com/en/user-guide/cleanrooms/v1/policies)

現行方式は対応regionでGAです。Data providerにはEnterpriseが必要で、owner／analysis runnerはStandardも利用できますが、Standardでpolicyを適用したデータ提供はできません。Trial、government、VPSの利用は対応しません。利用する方式・版・regionを確認し、Secure Data Sharing全体にEnterprise必須という条件を広げないようにします。

[共有の境界図](../../diagrams/domain-5/sharing-boundaries.md)で、providerからshareへのgrantとconsumer内のroleへのgrantを確認してください。

## 共有方法の比較

| 要件 | 選定 | 境界 |
|---|---|---|
| 同一regionの契約先に限定viewを読ませる | direct share | Consumer内のrole付与も必要 |
| 契約のない取引先にquery環境を用意する | reader account | Providerがcreditと管理を負担 |
| 許可されたデータを下流accountに渡す | resharing | 設定・organization制限、自分のsecure viewを確認 |
| 明細を自由に公開せず共通顧客を集計する | Data Clean Room | データ、分析、出力の制約を設計 |
| 公開検索・説明・課金も提供する | Listing | [5.3](03-marketplace-listings.md)で扱う |

## 試験で重要なポイント

Providerとconsumerはaccountの立場です。Shareへのgrant、consumer accountの追加、consumer内のroleへのgrantの3つを分けます。Readerのquery creditはproviderに発生します。

## 間違えやすいポイント

通常の共有は元データのコピーではありません。Clone・Time Travelの制約はimported objectを対象とし、consumerの自分の通常tableまで禁止しません。再共有はproviderの許可条件を確認し、Clean Roomは分析制約の設計とセットで選びます。

## 確認問題

- [C5-5.2-Q01: Readerの費用](../../exercises/chapter/c5-5.2-q01.md)
- [C5-5.2-Q02: Imported databaseの利用](../../exercises/chapter/c5-5.2-q02.md)
- [C5-5.2-Q03: 再共有の条件](../../exercises/chapter/c5-5.2-q03.md)
- [C5-5.2-Q04: Direct shareの境界](../../exercises/chapter/c5-5.2-q04.md)
- [C5-5.2-Q05: Clean Roomの用途](../../exercises/chapter/c5-5.2-q05.md)

## 章のまとめ

元objectをproviderが保持し、consumerは読取りアクセスを自分のroleに割り当てます。Readerの管理・費用はproviderが負担します。Direct share、許可されたresharing、制約付き共同分析を要件に応じて選びます。

## 次に学ぶこと

[5.3 MarketplaceとListing](03-marketplace-listings.md)で公開対象、料金、配送、実行する製品の違いを確認します。

## 根拠・関連する公式ドキュメント

- `docs-secure-sharing` — https://docs.snowflake.com/en/user-guide/data-sharing-intro
- `docs-reader-accounts` — https://docs.snowflake.com/en/user-guide/data-sharing-reader-create
- `docs-sharing-provider` — https://docs.snowflake.com/en/user-guide/data-sharing-provider
- `docs-sharing-consumer` — https://docs.snowflake.com/en/user-guide/data-share-consumers
- `docs-grant-share` — https://docs.snowflake.com/en/sql-reference/sql/grant-privilege-share
- `docs-resharing` — https://docs.snowflake.com/en/collaboration/reshare-listings
- `docs-resharer` — https://docs.snowflake.com/en/collaboration/resharing-as-resharer
- `docs-resharing-default-change` — https://docs.snowflake.com/en/release-notes/bcr-bundles/2026_05/bcr-2324
- `docs-cleanrooms-overview` — https://docs.snowflake.com/en/user-guide/cleanrooms/overview
- `docs-cleanrooms-legacy-policies` — https://docs.snowflake.com/en/user-guide/cleanrooms/v1/policies
