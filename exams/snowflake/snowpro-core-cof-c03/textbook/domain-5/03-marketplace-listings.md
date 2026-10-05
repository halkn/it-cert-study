# 5.3 Marketplace と Listing で共有する

> Status: complete
> Last verified: 2026-10-05

## この章で学ぶこと

Marketplaceを発見・公開の場、Listingを製品の公開単位として区別します。公開先、料金、regionへの配送、データだけか実行するアプリかを別々に判断します。

## 前提知識

[5.2](02-data-sharing.md)のprovider／consumerとshareを前提にします。Native Appの実行環境については[1.6](../domain-1/06-ai-ml-app-development.md)を参照できます。

## この章の用語

| 用語 | 意味 |
|---|---|
| Snowflake Marketplace | データやアプリのListingを発見・取得・公開する場 |
| Listing | 製品、説明、公開対象、利用条件などをまとめる公開単位 |
| private／public | 指定consumerへの限定公開／Marketplaceでの公開 |
| Cross-Cloud Auto-Fulfillment | 別regionのconsumerへListingの製品を届ける自動配送 |
| application package | Providerがデータ・code・manifest・setup script等をまとめるobject |
| Snowflake Native App | Consumer accountへインストールされるapplication object |

## 試験範囲との対応

日本語版Study Guide p.12の5.3、全3 Topicに対応します。

| Topic | 本文 | 主な根拠 |
|---|---|---|
| Marketplace | [発見・取得・公開の場](#marketplace) | `docs-marketplace` |
| private／public Listing | [公開先と料金](#listings) | `docs-listings`, `docs-auto-fulfillment` |
| Native App | [データの近くでlogicを実行](#native-apps) | `docs-native-app-framework`, `docs-native-app-access`, `docs-native-app-responsibility` |

<a id="marketplace"></a>
## Marketplaceで製品を発見・取得・公開する

外部の気象データを社内売上と組み合わせたいconsumerは、Snowflake MarketplaceでListingを探し、説明・sample・利用条件を確認して取得します。Providerにとっては、各consumerと個別の共有関係を用意するだけでなく、広く製品を見つけてもらう場です。データに加えてNative Appも公開できます。[Marketplace](https://docs.snowflake.com/en/collaboration/collaboration-marketplace-about)

Marketplaceはtableを格納するdatabaseでも、Snowflake computeのEditionでもありません。データListingを取得した後は共有データを自分のwarehouseでqueryし、自社データと組み合わせます。「Marketplaceで見つけた」ことだけで品質・契約条件・region可用性・料金は決まりません。

<a id="listings"></a>
## Listingの公開先と利用料金を別々に決める

Listingはshareやapplication packageというdata productに、タイトル、説明、sample SQL、利用条件などを付ける公開単位です。Shareはobject権限を担い、Listingは製品の発見や提供方法を加えます。Native AppのListingはインストールするpackageを提供し、データのListingはqueryするデータを提供します。[Listingの役割](https://docs.snowflake.com/en/collaboration/collaboration-listings-about)

Private listingは指定したconsumer accountだけに提供します。Public listingはMarketplaceで見つけられるように公開します。Publicにしたから全Snowflakeユーザーへ無条件のSELECT権限が生まれるわけではありません。取得、利用条件への同意、料金、制限付きtrialからの申請などの条件を別途満たします。

| 選定軸 | 選択肢 | 例 |
|---|---|---|
| 公開先 | private／public | 契約先限定／市場で広く発見 |
| アクセス条件 | free／limited trial／paid | 無料提供／試用後に全製品を申請／有料利用 |
| 製品 | share／application package | データをquery／appをinstall |
| 配送先 | 同一region／別region | 通常の共有／auto-fulfillment等 |

Privateでも有料、publicでも無料にできます。Limited trialは一部データや期間制限などで試し、全製品へのアクセスを申請する方式です。指定顧客への有料データ提供ならpaid private listing、不特定のconsumerへ無料データを広く公開するならfree public listingを選べます。Paid listingの可用性はprovider／consumerのregionなどに依存します。

無料のデータListingでもquery computeは通常consumerの負担です。有料製品のアクセス料金はcompute料金と別なので、料金の一つだけから合計費用を判断しません。

<a id="cross-region"></a>
## 別regionへListingの製品を自動配送する

Cross-Cloud Auto-Fulfillmentでは、Snowflakeが配送先regionにsecure share area（SSA）を用意し、Listingの製品を提供・refreshします。Providerがregionごとの配送を自分で組む負担を減らせます。同一regionで元データを直接参照する共有と異なり、別regionへはデータを複製・転送します。[auto-fulfillment](https://docs.snowflake.com/en/collaboration/provider-listings-auto-fulfillment)

配送やrefreshには時間と費用が必要で、別regionに対して更新が常に即時に見えるとは判断しません。対象region・cloud、契約経路、製品の対応objectを確認し、配送側のstorage・refresh・transfer費用とconsumerのquery費用を分けます。Region障害後の書込み再開というBCDR要件には、Listing配送だけでなく[5.1のfailover設計](01-collaboration-protection.md#replication-failover)が必要です。

<a id="native-apps"></a>
## Native Appでconsumerのデータの近くにlogicを届ける

データ品質検査の処理を各顧客のaccountで実行したい場合、providerはSnowflake Native App Frameworkでapplication packageを作ります。Packageはcodeや必要なデータ、manifest、setup script、version情報などをまとめ、privateまたはMarketplaceのListingで公開できます。[Framework](https://docs.snowflake.com/en/developer-guide/native-apps/native-apps-about)

Consumerがinstallすると、自分のaccountにapplication objectが作られ、setup scriptが必要なobjectを構成します。Packageを作るproviderと、applicationをinstallするconsumerを区別します。単なるデータshareは実行するlogicの配布・installを代替しません。

### インストールとconsumerデータへのアクセスは別

Appはinstallしただけではconsumerが所有するtableを自由に読めません。Consumerは必要なobjectへのアクセスをgrant／referenceで許可します。Warehouseなど運用resourceを作る権限と既存データを読む権限も別です。Consumer側のユーザーがapp内の機能を使うには、公開されたapplication roleをaccount roleへgrantします。[Appへのアクセス許可](https://docs.snowflake.com/en/developer-guide/native-apps/consumer-guide-access)、[Application role](https://docs.snowflake.com/en/developer-guide/native-apps/creating-setup-script)

Native Appはlogicをデータの近くで実行でき、通常の処理のために外部へデータを搬出する必要を減らします。ただし外部接続やデータを返す機能を持つappもあり、installしたappが決してデータを外へ出さないという保証ではありません。Consumerが追加権限と外部送信先を確認し、必要な範囲を許可します。Provider側の知的財産を保護する境界もあるため、consumerのACCOUNTADMINならapp内の全codeを読めるとも考えません。[責務の分離](https://docs.snowflake.com/en/developer-guide/native-apps/consumer-guide-responsibility)

Frameworkは対応cloudでGAですが、特定のapp、container、private connectivity、政府regionなどの条件は個別に確認します。Data sharing、Native App、Clean Roomを同じ機能として扱わず、配布する製品と分析の制約で選びます。

[公開から利用までの図](../../diagrams/domain-5/listing-delivery.md)で、shareをqueryする経路とpackageをinstallする経路を確認してください。

## Direct share・Listing・Native Appの比較

| 要件 | 選ぶ構成 | 理由 |
|---|---|---|
| 既知の同一region accountへデータを直接公開 | direct share | 製品の市場公開を必要としない |
| 指定顧客へ説明・条件付きで有料データを提供 | paid private listing＋share | 限定公開と課金を組み合わせる |
| 多数のconsumerへデータ製品を発見してもらう | public listing＋share | Marketplaceで公開する |
| 顧客accountで処理logicを実行 | Listing＋application package | ConsumerでNative Appをinstallする |
| 生データ利用を制約して共同分析 | Data Clean Room | 分析と出力条件の設計を含む |

## 試験で重要なポイント

Private／publicとfree／paidは独立した軸です。Listingはデータだけでなくappを提供できます。Native Appはconsumer内で動作しますが、既存データへのアクセスは別途許可が必要です。

## 間違えやすいポイント

「Publicだから無料」「Freeだからcomputeも無料」「Auto-fulfillmentだから複製費用なし」は成り立ちません。Appのinstall、appのデータアクセス、利用者がappを使う権限も分けます。

## 確認問題

- [C5-5.3-Q01: Marketplaceの役割](../../exercises/chapter/c5-5.3-q01.md)
- [C5-5.3-Q02: Listingの公開先と料金](../../exercises/chapter/c5-5.3-q02.md)
- [C5-5.3-Q03: Packageとapplication](../../exercises/chapter/c5-5.3-q03.md)

- [D5-Q09: Domain演習](../../exercises/domain/d5-q09.md)

## 章のまとめ

Marketplaceは製品を発見・公開する場で、Listingは製品と提供条件をまとめます。データのshareとlogicのpackageを区別し、公開先、料金、region配送、実行権限を要件に合わせます。

## 次に学ぶこと

[Domain 5演習](../../exercises/domain/README.md#domain-5)で比較を練習し、[模擬問題](../../exercises/mock/README.md#問題bank--domain-5)で要件から選定します。

## 根拠・関連する公式ドキュメント

- `docs-marketplace` — https://docs.snowflake.com/en/collaboration/collaboration-marketplace-about
- `docs-listings` — https://docs.snowflake.com/en/collaboration/collaboration-listings-about
- `docs-auto-fulfillment` — https://docs.snowflake.com/en/collaboration/provider-listings-auto-fulfillment
- `docs-native-app-framework` — https://docs.snowflake.com/en/developer-guide/native-apps/native-apps-about
- `docs-native-app-access` — https://docs.snowflake.com/en/developer-guide/native-apps/consumer-guide-access
- `docs-native-app-roles` — https://docs.snowflake.com/en/developer-guide/native-apps/creating-setup-script
- `docs-native-app-responsibility` — https://docs.snowflake.com/en/developer-guide/native-apps/consumer-guide-responsibility
