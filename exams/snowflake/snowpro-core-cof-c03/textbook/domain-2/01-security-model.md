# 2.1 セキュリティモデルと原則を説明する

> Status: complete
> Last verified: 2026-08-16

## この章で学ぶこと

この章を終えると、次を説明・判断できます。

- authenticationとauthorizationを分け、要件に合う制御を選ぶ
- privilegeをroleへ集約し、role hierarchyで継承させる
- RBACとDAC、account roleとdatabase role、primary roleとsecondary roleを区別する
- system-defined roleとcustom functional roleの責務を分離する
- network policy、MFA、SSO、OAuth、key-pair authenticationを利用主体に合わせる
- account identifierを接続先指定に使う
- handler codeのlogとtraceをevent tableで収集する

## 前提知識

- [1.3 オブジェクト階層](../domain-1/03-object-hierarchy.md)のorganization、account、database、schema、schema object
- authenticationは本人確認、authorizationは確認済み主体に操作を許可する判定であること
- human userとservice／applicationでは、対話的な認証が可能かどうかが異なること

## この章の用語

| 用語 | この章での意味 |
|---|---|
| securable object | privilegeをgrantできる保護対象 |
| privilege | objectに対して許可される操作。`USAGE`、`SELECT`、`CREATE`など |
| role | privilegeをまとめ、userや別roleへgrantする主体 |
| RBAC | Role-Based Access Control。privilegeをroleへ、roleをuserへ割り当てる方式 |
| DAC | Discretionary Access Control。object ownerがaccessを委任できる方式 |
| primary role | sessionで常に1つだけactiveになり、object作成時のownerになるaccount role |
| secondary role | primary roleと同時にactiveにして、通常操作のauthorizationへ権限を追加できるaccount role |
| IdP | Identity Provider。外部でcredentialを管理し、利用者を認証する主体 |
| SSO | Single Sign-On。IdPでの認証結果を使って複数serviceへaccessする方式 |
| OAuth | applicationへ限定されたaccess tokenを渡すauthorization framework |
| event table | log、trace、metricなどのtelemetry dataを格納するtable |

## 試験範囲との対応

| Topic | 本文 | 主な公式根拠 |
|---|---|---|
| Role-Based Access Control | [privilegeをrole経由で届ける](#rbac) | `docs-access-control-overview` |
| Securable object hierarchy | [containerごとに必要なprivilege](#securable-object-hierarchy) | `docs-access-control-overview` |
| Discretionary Access Control | [ownerが委任する](#dac) | `docs-access-control-overview` |
| Network policy | [接続元networkを制限する](#network-policies) | `docs-network-policies` |
| Authentication | [主体に合う認証方式](#authentication) | `docs-authentication-overview`, `docs-authentication-policies`, `docs-mfa`, `docs-federated-authentication`, `docs-oauth`, `docs-key-pair-auth` |
| System-defined role | [account管理責務を分離する](#system-defined-roles) | `docs-access-control-overview` |
| Functional role | [業務機能とobject accessをroleへ分ける](#functional-roles) | `docs-access-control-best-practices` |
| Secondary role | [複数roleの権限をsessionで集約する](#secondary-roles) | `docs-access-control-overview` |
| Account identifier | [接続先accountを一意に示す](#account-identifiers) | `docs-account-identifiers-c03` |
| Logging／tracing | [handler codeの動作をevent tableへ記録する](#logging-tracing) | `docs-logging-tracing` |

公式ObjectiveとTopicは[COF-C03 Syllabus](../../docs/syllabus.md#21-セキュリティモデルと原則を説明する)から公式Study Guideへ辿って確認できます。

## 認証・network・権限は別の関門

Snowflakeへの操作が成功するには、接続元、主体、操作の三つを別々に評価します。

1. Network policyが接続元IPやprivate endpointを許可する。
2. Authenticationがuser／serviceの本人性を確認する。
3. Authorizationがactive roleなどのprivilegeから操作を許可する。

Network policyを通過しても`SELECT` privilegeは得られません。MFAに成功してもtable accessが自動付与されるわけではありません。設問では「どの関門を変更する要件か」を先に特定します。

![Role・privilege・objectの関係](../../diagrams/domain-2/role-privilege-object.md)

<a id="rbac"></a>
## RBAC — privilegeをrole経由で届ける

SnowflakeのRole-Based Access Control（RBAC）では、保護対象へのprivilegeをroleへgrantし、そのroleをuserまたは上位roleへgrantします。個々のuserへ同じprivilegeを繰り返し割り当てず、job function単位で管理できます。

たとえばanalystへ売上tableの参照を許可する基本形は次です。

```sql
GRANT USAGE ON DATABASE sales_db TO ROLE sales_reader;
GRANT USAGE ON SCHEMA sales_db.analytics TO ROLE sales_reader;
GRANT SELECT ON TABLE sales_db.analytics.orders TO ROLE sales_reader;
GRANT ROLE sales_reader TO USER analyst_1;
```

`SELECT`だけではdatabaseとschemaを辿れません。containerの`USAGE`と対象tableの`SELECT`を組み合わせる必要があります。

Roleを別roleへgrantすると、上位roleは下位roleのprivilegeを継承します。`GRANT ROLE sales_reader TO ROLE sales_analyst`なら、`sales_analyst`は`sales_reader`の権限を継承します。grantの矢印とprivilege継承の向きを逆にしないことが重要です。

<a id="securable-object-hierarchy"></a>
## Securable object hierarchy — containerごとに必要なprivilege

Securable objectは、許可されないaccessを拒否する保護対象です。代表的なcontainer hierarchyは次の順です。

`Organization → Account → Database → Schema → Table／View／Stageなど`

子objectへの操作には、子object固有のprivilegeに加えて親containerを参照する権限が必要です。tableをqueryする典型例ではdatabaseとschemaの`USAGE`、tableの`SELECT`を確認します。

Hierarchyはprivilegeの自動継承を意味しません。databaseの`USAGE`だけで配下tableを`SELECT`できず、tableの`SELECT`だけで親databaseを辿れるとも限りません。

<a id="dac"></a>
## DAC — ownerがaccessを委任する

Discretionary Access Control（DAC）では、各objectに唯一のowner roleがあり、ownerがそのobjectへのaccessをgrantできます。通常、objectを作成したprimary roleが`OWNERSHIP`を持ちます。

RBACとDACは排他的な選択肢ではありません。Ownerがobject privilegeをroleへgrantする部分がDAC、そのroleを利用者へ割り当てる部分がRBACです。

Managed access schemaでは例外があります。配下objectのownerではなく、schema ownerまたは`MANAGE GRANTS`を持つroleがgrant判断を集約します。中央管理要件ではmanaged access schema、各object ownerへ委任する要件ではregular schemaという違いを確認します。

<a id="network-policies"></a>
## Network policy — 接続元networkを制限する

Network policyは、Snowflake serviceへのnetwork trafficをIP addressやnetwork ruleに基づいて許可・拒否します。Account、user、対応するsecurity integrationなどへactivateして使います。

User-level policyがaccount-level policyより具体的に適用されます。Security integrationへ設定したpolicyは、そのintegrationが管理するtrafficを制限します。作成しただけで有効になるとは限らず、どの対象へactivateしたかを確認します。

Network policyはauthentication methodやobject privilegeの代替ではありません。

| 要件 | 選ぶ制御 |
|---|---|
| 許可したoffice IPからだけ接続 | Network policy |
| Password loginにMFAを要求 | Authentication policy／MFA |
| Finance tableの行を参照可能にする | Roleとprivilege |

<a id="authentication"></a>
## Authentication — 主体に合う認証方式

Authentication policyは、MFA enrollment、許可するauthentication method、利用可能なSAML／OIDC integration、client typeなどをaccountまたはuser単位で制御します。Accountとuserの両方へ設定した場合はuser-level policyが優先されます。

### MFAはpasswordを増やす仕組みではない

Multi-factor authentication（MFA）は異なるfactorを組み合わせます。Human userのinteractive loginを強化する要件に使います。2026年8月時点でhuman userのMFA移行要件はaccount作成時期やauthentication policyにより条件があるため、固定的に「全接続で必ず同じ」と一般化せず公式ページを再確認します。

SSO利用時、既定ではIdP側がstrong authenticationを強制する設計です。Snowflake側でもSSO後のMFAを要求したい場合はauthentication policyのMFA設定を使います。

### Federated authenticationとSSOはIdPへ本人確認を委ねる

Federated authenticationでは外部IdPがcredentialを保持・認証し、Snowflakeはservice providerとして認証結果を受け取ります。SnowflakeはSAML 2.0とOIDCのsecurity integrationをサポートします。

SSOはhuman userが一度のIdP認証を使ってSnowflakeなどへaccessする利用体験です。Roleとprivilegeは引き続きSnowflakeでauthorizationへ使われます。

### OAuthはapplicationへ限定accessを委任する

OAuthはaccess tokenを使い、applicationがuserまたはserviceの代わりにSnowflakeへaccessする方式です。Passwordをapplicationへ保存せず、scopeやtoken lifetimeによりaccessを限定できます。Interactive SSOとOAuthはいずれもsecurity integrationを使う場合がありますが、目的は同一ではありません。

### Key-pair authenticationは非対話serviceに適する

Key-pair authenticationは公開鍵をuserへ登録し、clientが秘密鍵による署名で認証します。Password入力やMFA promptが困難なservice、script、connectorに適します。秘密鍵の保護とrotationは利用者側の責任です。

| 主体・要件 | 代表的な方式 |
|---|---|
| Human userのpassword loginを強化 | MFA |
| Corporate IdPへloginを集約 | SAML／OIDC federated authentication、SSO |
| Applicationへ限定access tokenを渡す | OAuth |
| 非対話serviceが秘密鍵を安全に保持できる | Key-pair authentication |

<a id="system-defined-roles"></a>
## System-defined role — account管理責務を分離する

System-defined roleはSnowflakeが作成し、dropできません。代表的な役割を責務で覚えます。

| Role | 主な責務 |
|---|---|
| `GLOBALORGADMIN` | Organization accountでaccount lifecycleとorganization usageを管理する推奨role |
| `ORGADMIN` | Regular accountからorganization operationを管理する旧来role。将来廃止予定のため`GLOBALORGADMIN`への移行が推奨される |
| `ACCOUNTADMIN` | account最上位の管理。`SECURITYADMIN`と`SYSADMIN`を継承し、限定的に使用 |
| `SECURITYADMIN` | grant管理。`MANAGE GRANTS`を持ち、`USERADMIN`を継承 |
| `USERADMIN` | userとroleの作成・管理 |
| `SYSADMIN` | warehouse、databaseなどのobject管理。custom role hierarchyの上位に置くことが推奨される |
| `PUBLIC` | 全userと全roleへ自動grantされるpseudo-role |

System roleへ業務tableのprivilegeを直接積み増すより、custom roleへgrantし、custom hierarchyを`SYSADMIN`へ接続します。これによりaccount管理権限と業務data accessを分離できます。

<a id="functional-roles"></a>
## Functional role — 業務機能とobject accessをroleへ分ける

Functional roleはjob functionに必要な複数accessをまとめるcustom account roleです。Snowflakeに`FUNCTIONAL ROLE`という別object typeがあるわけではなく、custom roleの設計上の役割です。

推奨設計では、tableなど特定objectへのprivilegeをaccess roleへまとめ、そのaccess roleを`FINANCE_ANALYST`などのfunctional roleへgrantします。Userにはfunctional roleをgrantします。

Account roleはaccount内のobject privilegeを保持し、sessionでactivateできます。Database roleは同じdatabase内のobject accessをまとめ、account roleへgrantして利用します。Database roleをprimary／secondary roleとして直接activateすることはできません。

<a id="secondary-roles"></a>
## Secondary role — 複数roleの権限をsessionで集約する

Sessionにはprimary roleが必ず1つあります。さらに、userへgrant済みのaccount roleをsecondary roleとして複数activeにできます。

```sql
USE ROLE finance_analyst;
USE SECONDARY ROLES ALL;

SELECT CURRENT_ROLE(), CURRENT_SECONDARY_ROLES();
```

通常の`SELECT`などはactiveなprimary／secondary roleのaggregate privilegesでauthorizeできます。Cross-database queryで、別々のroleにある権限を同時に使う場面が代表例です。

`CREATE <object>`のauthorizationと新規objectのownershipはprimary roleだけを基準にします。Secondary roleをactiveにしても、新規object ownerがsecondary roleになるわけではありません。

<a id="account-identifiers"></a>
## Account identifier — 接続先accountを一意に示す

Account identifierはSnowflake accountをorganization内およびglobal network上で識別します。推奨形式はorganization名とaccount名の組合せです。用途により`organization-account`または`organization.account`の表現を使います。

Snowflake-assigned account locatorを使うlegacy形式もありますが、新しい構成ではorganization nameとaccount nameを使う形式が推奨されます。Account identifierはlogin URL、CLI、driver、sharing、replicationなどで接続先や相手accountを指定します。

Account identifierはuser名やdatabase名ではなく、accountそのものを示します。Region情報が常に手入力で必要とは限りません。

<a id="logging-tracing"></a>
## Logging／tracing — handler codeの動作をevent tableへ記録する

Snowflakeのlogging、tracing、metricsは、functionやstored procedureのhandler code、Snowpark codeのobservabilityを提供します。収集先はactiveなevent tableです。

1. Event tableをaccountへ設定する。
2. Log／trace／metricのtelemetry levelを設定する。
3. Handler codeからlog messageやtrace eventをemitする。
4. Event tableをSQLでqueryして分析する。

Log messageは独立した詳細messageで、個々の実行時状態の調査に向きます。Trace eventはattributeを持つ構造化dataで、spanとして複数処理を関連付け、高水準の流れを追うのに向きます。

これはuser loginや全SQLの監査履歴そのものではありません。Login調査には`LOGIN_HISTORY`、query調査には`QUERY_HISTORY`など目的に合うAccount Usage viewを使います。

## SQLでrole contextを確認する

```sql
SELECT
  CURRENT_USER(),
  CURRENT_ROLE(),
  CURRENT_SECONDARY_ROLES(),
  CURRENT_ACCOUNT_NAME(),
  CURRENT_ORGANIZATION_NAME();
```

このSQLは現在のsession contextを観察します。Role hierarchy全体や全grantを表示するものではありません。Grant調査には`SHOW GRANTS`や対応するAccount Usage viewを使います。

## Compare — 要件からsecurity controlを選ぶ

| 問い | 主な対象 | 選ぶ機能 |
|---|---|---|
| どこから接続できるか | Source network | Network policy |
| 誰／何が接続しているか | Human／service identity | MFA、SSO、OAuth、key pair |
| 何を実行できるか | Securable object operation | Roleとprivilege |
| 誰がgrantを決めるか | Object／schema ownership | DAC、managed access schema |
| 複数roleを同時利用するか | Session authorization | Secondary role |
| Handler内部で何が起きたか | Code telemetry | Log／traceとevent table |

## 試験で重要なポイント

- Snowflakeのaccess controlはRBACとDACを組み合わせる。
- Table queryには親database／schemaの`USAGE`とtableの`SELECT`を確認する。
- Database roleはaccount roleへgrantして利用し、sessionで直接activateしない。
- `CREATE`と新規objectのownershipはprimary roleが基準である。
- Network、authentication、authorizationは別の制御である。
- System roleと業務accessはcustom role hierarchyで分離する。

## 間違えやすいポイント

- `ACCOUNTADMIN`を日常業務roleとして使わない。
- `PUBLIC`へgrantすると全user／roleから利用可能になる。
- Roleのownerであることと、そのroleのprivilegeを継承することは同じではない。
- SSO成功はtable privilegeの付与を意味しない。
- Network policyを作成しただけでは対象へactivateされているとは限らない。
- Logging／tracingのevent tableと、`QUERY_HISTORY`／`LOGIN_HISTORY`を混同しない。

## 確認問題

- [C2-2.1-Q01: RBAC](../../exercises/chapter/c2-2.1-q01.md)
- [C2-2.1-Q02: Securable object hierarchy](../../exercises/chapter/c2-2.1-q02.md)
- [C2-2.1-Q03: DAC](../../exercises/chapter/c2-2.1-q03.md)
- [C2-2.1-Q04: Network policy](../../exercises/chapter/c2-2.1-q04.md)
- [C2-2.1-Q05: Authentication](../../exercises/chapter/c2-2.1-q05.md)
- [C2-2.1-Q06: System-defined role](../../exercises/chapter/c2-2.1-q06.md)
- [C2-2.1-Q07: Functional role](../../exercises/chapter/c2-2.1-q07.md)
- [C2-2.1-Q08: Secondary role](../../exercises/chapter/c2-2.1-q08.md)
- [C2-2.1-Q09: Account identifier](../../exercises/chapter/c2-2.1-q09.md)
- [C2-2.1-Q10: Logging／tracing](../../exercises/chapter/c2-2.1-q10.md)

## 章のまとめ

- 接続の可否はnetwork、authentication、authorizationの順で切り分ける。
- Privilegeはroleへまとめ、role hierarchyでjob functionへ届ける。
- Object ownerによる委任がDAC、roleを介した割当がRBACである。
- Primary／secondary role、account／database roleはactive化と適用範囲が異なる。
- Human userにはMFA／SSO、serviceにはOAuth／key pairを要件に応じて選ぶ。
- Handler codeのlogとtraceはtelemetry levelを設定し、event tableで分析する。

## 次に学ぶこと

[2.2 データガバナンス機能](02-data-governance.md)では、ここで学んだroleとcontextを使い、返す行や列値、data分類、privacyを制御します。

## 根拠・関連する公式ドキュメント

- `docs-access-control-overview` — https://docs.snowflake.com/en/user-guide/security-access-control-overview
- `docs-access-control-best-practices` — https://docs.snowflake.com/en/user-guide/security-access-control-considerations
- `docs-network-policies` — https://docs.snowflake.com/en/user-guide/network-policies
- `docs-authentication-policies` — https://docs.snowflake.com/en/user-guide/authentication-policies
- `docs-mfa` — https://docs.snowflake.com/en/user-guide/security-mfa
- `docs-federated-authentication` — https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-overview
- `docs-authentication-overview` — https://docs.snowflake.com/en/user-guide/security-authentication-overview
- `docs-oauth` — https://docs.snowflake.com/en/user-guide/oauth-intro
- `docs-key-pair-auth` — https://docs.snowflake.com/en/user-guide/key-pair-auth
- `docs-account-identifiers-c03` — https://docs.snowflake.com/en/user-guide/admin-account-identifier
- `docs-logging-tracing` — https://docs.snowflake.com/en/developer-guide/logging-tracing/logging-tracing-overview
