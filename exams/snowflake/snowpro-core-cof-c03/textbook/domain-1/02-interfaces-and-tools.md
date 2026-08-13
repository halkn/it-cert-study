# 1.2 インターフェースとツールを利用する

> Status: complete
> Last verified: 2026-08-13

## この章で学ぶこと

この章を終えると、操作場所と自動化要件からSnowsight、Snowflake CLI、Visual Studio Code拡張を選べるようになります。また、どのinterfaceを使ってもSnowflake側のrole、warehouse、database、schemaというsession contextが処理結果を左右することを説明できます。

## 前提知識

- [1.1](01-architecture.md)で扱ったCloud ServicesとVirtual Warehouseの役割
- SQLを対話的に実行する作業と、scriptとして繰り返し実行する作業の違い
- local computerで動くclientと、Snowflake account内のserviceの違い

## この章の用語

| 用語 | この章での意味 |
|---|---|
| interface | Snowflakeへ接続し、操作を送る入口 |
| Snowsight | browserで利用するSnowflakeのweb interface |
| Workspace | Snowsight内でSQL、Python、file、folderを扱う開発環境 |
| Snowflake CLI | terminalから`snow`コマンドでSnowflake workloadを操作する公式command-line tool |
| IDE | code編集、補完、実行、debugなどをまとめた統合開発環境 |
| VS Code extension | Visual Studio CodeへSnowflake接続・開発機能を追加する公式拡張 |
| connection | account、user、authentication方式など、接続に必要な設定のまとまり |
| session context | 現在のrole、warehouse、database、schemaなど、statement実行時の文脈 |

## 試験範囲との対応

| Topic | 本文 | 主な公式根拠 |
|---|---|---|
| Snowsight | [browserで探索・実行・監視する](#snowsight) | `docs-snowsight`, `docs-snowsight-workspaces` |
| Snowflake CLI | [terminalから反復可能に操作する](#snowflake-cli) | `docs-snowflake-cli` |
| IDE integration（Visual Studio Code） | [codeとSnowflake操作を同じIDEで扱う](#ide-integrations) | `docs-vscode-extension` |

公式のObjectiveとTopicは[COF-C03 Syllabus](../../docs/syllabus.md#12-インターフェースとツールを利用する)から公式Study Guideへ辿れます。

## 同じSnowflakeへ異なる入口から接続する

3つのtoolは別々のdatabase製品ではありません。いずれもSnowflake accountへ要求を送り、Snowflake側でauthentication、authorization、query最適化、compute実行が行われます。違うのは、利用者が要求を作成・保存・再実行する場所です。

| 要件 | 第一候補 | 選ぶ理由 |
|---|---|---|
| browserだけでobjectを探索し、query結果を表やchartで確認する | Snowsight | account管理、探索、開発、監視をGUIで行える |
| CI/CDやshell scriptから同じ操作を繰り返す | Snowflake CLI | commandとして自動化し、project fileとversion管理しやすい |
| local repositoryのcode編集とSQL実行を同じ画面で行う | VS Code extension | IDEのfile、source control、debug workflowに接続を統合できる |

interfaceを変えてもprivilegeは増えません。たとえばVS Code拡張を使っても、active roleに`SELECT`がなければtableはqueryできません。queryがwarehouseを必要とするなら、SnowsightでもCLIでもVS Codeでも利用可能なwarehouseが必要です。

<a id="snowsight"></a>
## Snowsightで探索・実行・監視する

SnowsightはSnowflakeのweb interfaceです。browserからdatabase objectの探索、SQLやPythonの開発、data loading、query historyやtaskの監視、warehouse・user・role・costの管理などへ移動できます。表示される操作はactive roleの権限と、region／platformで利用可能な機能に依存します。

Snowsightの開発面では、Workspacesがfile-basedの環境を提供します。SQLとPythonのfileをfolderで整理し、実行し、Git repositoryと連携できます。COF-C03で重要なのは特定のmenu位置の暗記ではなく、**browser内で対話的に探索・開発・管理する入口**だと識別することです。

旧来のWorksheetsからWorkspacesへの移行が進んでいます。したがって「SQLをbrowserで対話実行する」という能力と、特定時点のnavigation名を分けて覚えます。画面名が変わっても、statementを実行するroleとwarehouseのcontextは必要です。

### Snowsightを選ぶ場面

- 初めて見るdatabaseやschemaを階層的に探索する
- queryを少しずつ実行し、結果・chart・query historyを確認する
- warehouse、task、load history、costなどを視覚的に監視する
- user、role、privilegeを権限の範囲内で管理する

GUIで操作したこと自体は自動化を保証しません。repeatable deploymentやCIで同じ変更を再現したい場合は、SQL fileとCLIなどを組み合わせます。

<a id="snowflake-cli"></a>
## Snowflake CLIでterminalから反復可能に操作する

Snowflake CLIはdeveloper workload向けのopen-source command-line toolで、実行commandは`snow`です。SQLの実行だけでなく、object、stage、Snowparkのprocedure／function、Streamlit、Notebook、Native App、Snowpark Container Servicesなどを管理できます。

CLIではconnectionを設定し、そのconnection名をcommandから選びます。connectionは接続先とauthenticationを定めますが、実行可能な操作は接続userのroleとprivilegeで決まります。passwordやprivate keyなどのsecretをproject repositoryへcommitしてはいけません。

代表的な流れは次のとおりです。

```bash
snow connection test --connection cert-study
snow sql --connection cert-study --query "SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE()"
snow sql --connection cert-study --filename scripts/check.sql
```

最初のcommandは接続を確認し、次は短いSQL、最後はfileに保存したSQLを実行する例です。command optionはversionで変化し得るため、実際の利用時は`snow --help`と公式command referenceで確認します。

### CLIを選ぶ場面

- local shellから同じSQL fileを繰り返し実行する
- deployment手順をrepositoryでversion管理する
- CI/CDからapplicationやSnowflake objectを操作する
- GUI操作ではなくcommandの終了状態とoutputを後続処理へ渡す

CLIとSnowSQLを名前だけで同一視しません。COF-C03のTopicはSnowflake CLIです。Snowflake CLIはSQL clientに限定されず、developer workloadをproject単位で管理する広いtoolです。

<a id="ide-integrations"></a>
## Visual Studio Code拡張でcodeとSnowflake操作を統合する

Snowflake Extension for Visual Studio Codeは、local IDEからSnowflakeへ接続してSQL statementを実行し、database objectを探索するための公式拡張です。Snowpark Python stored procedureの作成とdebugにも利用できます。

VS Code拡張を使う利点は、Snowflake専用の別画面へcodeをcopyせず、repository内のSQLやPythonを編集・version管理しながら実行できることです。IDEはcodeを作る場所であり、実際のdata処理は接続先Snowflakeのsession contextとcomputeで行われます。

Snowpark Pythonでは、Python interpreterの選択とSnowflake connectionは別の設定です。local dependencyを解決できてもSnowflakeへ接続できるとは限らず、接続できてもroleのprivilegeがなければobjectを操作できません。

### VS Code拡張を選ぶ場面

- 複数のSQL／Python fileをlocal repositoryで編集する
- Git diffやreviewとSnowflake開発を同じworkflowに置く
- Snowpark Python stored procedureをauthoring・debugする
- IDEの補完とobject explorerを利用しながらSQLを試す

## 3つのtoolで共通するsession context

interface選択と実行contextは別の判断です。実行前に、少なくとも次を確認します。

```sql
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(),
       CURRENT_DATABASE(), CURRENT_SCHEMA();
```

同じ`SELECT * FROM orders`でも、current database／schemaが違えば別objectを参照するか、解決できません。roleが違えば可視objectと許可操作が変わります。warehouseが違えばqueryに使うcomputeとcostの帰属が変わります。

## 公式ドキュメント読解課題

1. `docs-snowsight`でProjects、Monitoring、Adminに属する代表操作を1つずつ確認し、GUIを選ぶ要件を説明してください。
2. `docs-snowflake-cli`でSQL以外に管理できるworkloadを3つ確認し、「CLIはSnowSQLの単なる改名ではない」理由を説明してください。
3. `docs-vscode-extension`でSQL実行とSnowpark Python debuggingの記述を探し、IDE integrationとCLIの使い分けを説明してください。

## 15分ミニハンズオン: contextをinterface非依存で確認する

必要権限はSnowflakeへsign inできるuserと、使用するwarehouseへの`USAGE`です。queryはmetadata／context function中心ですが、warehouseを起動する場合は最低60秒分のcompute課金が生じ得ます。既存objectは変更しません。

1. SnowsightのSQL実行環境で上記`CURRENT_*` queryを実行します。
2. Snowflake CLIを導入済みなら、同じqueryを`snow sql`で実行します。未導入なら公式CLI pageでcommand構造だけ確認します。
3. 出力のrole、warehouse、database、schemaを比較します。
4. Snowsight側でwarehouseまたはroleを変え、別sessionであるCLIのcontextが自動では変わらないことを確認します。

作成objectがないためcleanupは不要です。warehouseを手動で起動した場合は、学習後にsuspendするかauto-suspendを確認します。

## Snowsight、CLI、VS Code拡張の比較

| 観点 | Snowsight | Snowflake CLI | VS Code extension |
|---|---|---|---|
| 主な操作場所 | browser | terminal／script／CI | local IDE |
| 得意な作業 | 探索、対話実行、可視化、監視、管理 | 反復実行、自動化、deployment | code編集、Git、SQL実行、Snowpark debugging |
| 保存単位 | Workspace内file等 | local file／project definition | local repositoryのfile |
| 権限判定 | Snowflakeのrole | Snowflakeのrole | Snowflakeのrole |
| query compute | 選択したwarehouse等 | connection／SQLで選んだwarehouse等 | connection／SQLで選んだwarehouse等 |

## 試験で重要なポイント

- Snowsightはbrowserで探索、開発、監視、管理を行うweb interfaceである。
- Snowflake CLIは`snow`を使い、SQLだけでなくdeveloper workloadをcommandで管理できる。
- VS Code拡張はlocal development workflowへSnowflake接続、SQL実行、object探索、Snowpark開発を統合する。
- interfaceを変えてもrole privilegeやwarehouse要件を回避できない。
- 対話的な探索、反復可能な自動化、IDE中心の開発という要件で選ぶ。

## 間違えやすいポイント

- Snowsightを「SQL worksheetだけ」と限定しない。監視や管理、AI/ML、application開発への入口でもあります。
- GUIならwarehouseが不要とは限らない。dataをqueryする操作はwarehouse computeを使うことがあります。
- CLIのconnection設定をauthorizationと混同しない。接続後の操作可否はroleとprivilegeで決まります。
- VS Codeでcodeが動く場所をすべてlocalと決めつけない。SQLやpushdown処理はSnowflakeで実行されます。

## 確認問題

- [C1-1.2-Q01: browserでの探索と監視](../../exercises/chapter/c1-1.2-q01.md)
- [C1-1.2-Q02: 反復可能なcommand実行](../../exercises/chapter/c1-1.2-q02.md)
- [C1-1.2-Q03: IDE中心のSnowpark開発](../../exercises/chapter/c1-1.2-q03.md)

続けて[Domain演習D1-Q04〜Q05](../../exercises/domain/README.md)と[模擬問題M1-Q04〜Q05](../../exercises/mock/README.md)で要件からtoolを選びます。

## 章のまとめ

Snowsight、Snowflake CLI、VS Code拡張は同じSnowflakeを異なる作業環境から操作します。browserでの探索・監視にはSnowsight、反復可能なcommandとCI/CDにはCLI、local codeとGit中心の開発にはVS Code拡張を選びます。どの入口でもsession context、role privilege、warehouse computeの原則は共通です。

## 次に学ぶこと

次は[1.3 オブジェクト階層](03-object-hierarchy.md)で、各toolから探索・指定するorganization、account、database、schema、schema objectの関係を学びます。

## 根拠・関連する公式ドキュメント

- `exam-study-guide-c03-2026-07-08` — [COF-C03 Study Guide](https://publish-p93462-e887935.adobeaemcloud.com/content/dam/snowpro-sg/SnowProCoreStudyGuideC03.pdf)
- `docs-snowsight` — [Snowsight](https://docs.snowflake.com/en/user-guide/ui-snowsight)
- `docs-snowsight-workspaces` — [Workspaces](https://docs.snowflake.com/en/user-guide/ui-snowsight/workspaces-working)
- `docs-snowflake-cli` — [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli/index)
- `docs-vscode-extension` — [Snowflake Extension for Visual Studio Code](https://docs.snowflake.com/en/user-guide/vscode-ext)
