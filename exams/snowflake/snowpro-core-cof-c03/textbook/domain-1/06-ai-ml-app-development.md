# 1.6 AI/MLとアプリケーション開発機能を説明する

> Status: complete
> Last verified: 2026-08-13

## この章で学ぶこと

Notebooks、Streamlit、Snowpark、Cortex AI Functions／Search／Analyst、Snowflake MLを成果物とdata typeから選び、組み合わせを説明します。

## 前提知識

- SQL、Python、web application、machine learning modelの役割
- structured dataとunstructured text／documentの違い
- warehouseとcompute poolが異なるcompute resourceであること

## この章の用語

| 用語 | 意味 |
|---|---|
| Notebook | SQL、Python、Markdownをcellで対話実行する開発artifact |
| Streamlit | Pythonでinteractive data web appを構築するframework |
| Snowpark | Python／Java／ScalaからSnowflake dataを処理するAPIとruntime |
| Cortex | Snowflakeのmanaged AI機能群 |
| semantic model／view | business metric・dimension・relationshipをphysical dataへ対応付ける層 |
| Feature Store | ML feature定義・更新・再利用を管理する仕組み |
| Model Registry | model version、metadata、deployment／inferenceを管理するschema-level object |

## 試験範囲との対応

| Topic | 本文 | 根拠 |
|---|---|---|
| Notebooks | [対話的開発](#notebooks) | `docs-notebooks` |
| Streamlit | [web data app](#streamlit) | `docs-streamlit` |
| Snowpark | [codeをdataへ近づける](#snowpark) | `docs-snowpark` |
| Cortex | [AI function／Search／Analyst](#cortex) | Cortex各公式docs |
| Snowflake ML | [ML lifecycle](#snowflake-ml) | `docs-snowflake-ml` |

## 成果物から機能を選ぶ

![AI/ML app selection](../../diagrams/domain-1/ai-ml-app-selection.md)

機能は排他的ではありません。Notebookは開発interface、Snowparkはdata processing API、Snowflake MLはML lifecycle、Streamlitはend-user applicationです。異なる層を組み合わせます。

<a id="notebooks"></a>
## Notebooksで分析と実験を反復する

Snowflake NotebooksはSQL、Python、Markdownをcellで組み合わせる対話的環境です。Data exploration、visualization、feature engineering、model trainingに向きます。Workspaces世代ではnotebook fileをworkspace内で整理し、実行contextとしてdatabase／schemaを指定します。

Workspaces世代ではJupyter互換のcontainer runtimeを中心に発展しています。Legacy Notebooksから移行中のため、固定されたmenu名やruntime versionではなく、**cell-basedなreproducible exploration**という役割を覚えます。Queryはwarehouse、kernel／trainingはruntimeに応じてcompute pool等を使い、idle sessionにもcostが生じ得ます。

<a id="streamlit"></a>
## Streamlit in Snowflakeで利用者向けdata appを作る

Streamlit in SnowflakeはPython codeからinteractive web applicationを構築・deployし、Snowflake dataを外部systemへ移さず利用できます。SourceとenvironmentはSnowflake objectとしてRBACで管理され、warehouseまたはcontainer runtimeを選べます。

Notebookが作成者の探索・実験に向くのに対し、Streamlitはdashboard、input form、ML prediction UIなどを他の利用者へ提供する成果物です。

<a id="snowpark"></a>
## SnowparkでPython／Java／Scala処理をpush downする

Snowpark APIはDataFrame等を使い、Python、Java、ScalaでSnowflake dataをquery・transformします。Client codeはlogical planを構築し、処理をSnowflakeへpush downするため、large dataをclientへ全件downloadして処理する設計を避けられます。

SnowparkはUIではありません。Local IDE、Notebook、stored procedure、taskなど複数の実行・開発環境から使います。SQLで表現しにくいcodeと、Snowflakeのelastic computeを結び付ける層です。

<a id="cortex"></a>
## Cortexをdata typeと質問で選ぶ

### Cortex AI Functions

SQL／Pythonからtextやimageに対してcompletion、classification、extraction、filter、translation等を行うmanaged functionです。Table rowへAI処理を組み込みたい要件に合います。FunctionごとにGA／Preview、model、region availability、privilegeを確認します。

### Cortex Search

Document、support ticket、transcriptなどunstructured text corpusから関連箇所を低latencyで検索するserviceです。Vectorとkeywordのhybrid retrieval、attribute filterを提供し、RAGやenterprise searchのretrieval layerに向きます。Answer生成そのものとsearch indexを区別します。

### Cortex Analyst

Structured business dataへのnatural-language questionからSQLを生成するmanaged featureです。Semantic model／viewがmetric、dimension、relationship、business termをphysical tableへ対応付け、text-to-SQLの精度を支えます。Document検索にはSearch、structured metric questionにはAnalystを選びます。

<a id="snowflake-ml"></a>
## Snowflake MLでpredictive modelのlifecycleを管理する

Snowflake MLはdata preparation、Feature Store、training／tuning、experiment、Model Registry、inference、observability、lineageをSnowflake上でつなぐ機能群です。Custom predictive modelを開発・version管理・deploy・monitorする要件に使います。

Cortex AI Functionsがprebuilt／managed AI taskをSQLから使うのに対し、Snowflake MLは自分のdatasetとalgorithmでmodel lifecycleを管理する場面が中心です。Model RegistryはSnowflake内外でtrainingしたPython modelも管理し、warehouseまたはSnowpark Container Servicesでinferenceできます。

## 公式ドキュメント読解課題

1. `docs-streamlit`でRBACとruntime選択を確認します。
2. `docs-cortex-search`と`docs-cortex-analyst`のinput dataとoutputを比較します。
3. `docs-snowflake-ml`でFeature Store→training→Registry→observabilityの流れを辿ります。

## 20分ミニハンズオン: AI/ML artifactをaccountで発見する

SNOWFLAKE databaseのACCOUNT_USAGE閲覧権限は環境依存です。権限がなければ`SHOW`で見える範囲だけ確認します。Metadata query中心ですがwarehouseを使う場合はcompute costがあります。Objectは作りません。

```sql
-- Legacy Notebook objectが存在するaccountでは次を確認
SHOW NOTEBOOKS;
SHOW STREAMLITS;
SHOW MODELS;
SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE();
```

各artifactがどのdatabase／schema、owner roleに属するか確認します。作成物がないためcleanupは不要です。

## 比較表

| 要件 | 選択 |
|---|---|
| cellでSQL／Pythonを探索 | Notebooks |
| end-user向けinteractive web UI | Streamlit |
| Python／Java／Scalaでpushdown transform | Snowpark |
| rowごとのmanaged AI task | Cortex AI Functions |
| unstructured corpusのretrieval | Cortex Search |
| structured metricsへのnatural language | Cortex Analyst |
| custom predictive modelのend-to-end lifecycle | Snowflake ML |

## 試験で重要なポイント

- Notebookは開発環境、Streamlitはweb app、Snowparkはprocessing APIである。
- Cortex Searchはunstructured retrieval、Analystはstructured text-to-SQLである。
- Semantic model／viewはAnalystのbusiness meaningを支える。
- Snowflake MLはfeatureからmodel monitoringまでのlifecycleを扱う。
- availability、Preview、privilege、compute costを機能ごとに確認する。

## 間違えやすいポイント

- NotebookとStreamlitをどちらもPython UIという理由で同一視しない。
- Snowparkをdata connectorだけ、またはwarehouse typeだけと誤認しない。
- Cortex SearchがLLM answerを必ず生成するとは限らない。
- Cortex Analystをunstructured document検索に使わない。
- CortexとSnowflake MLを完全に排他的な製品と考えない。

## 確認問題

- [C1-1.6-Q01](../../exercises/chapter/c1-1.6-q01.md) Notebook
- [C1-1.6-Q02](../../exercises/chapter/c1-1.6-q02.md) Streamlit
- [C1-1.6-Q03](../../exercises/chapter/c1-1.6-q03.md) Snowpark
- [C1-1.6-Q04](../../exercises/chapter/c1-1.6-q04.md) Cortex
- [C1-1.6-Q05](../../exercises/chapter/c1-1.6-q05.md) Snowflake ML

[Domain D1-Q12〜Q13](../../exercises/domain/README.md)、[模擬M1-Q12〜Q13](../../exercises/mock/README.md)でDomain 1を仕上げます。

## 章のまとめ

成果物が探索ならNotebook、web appならStreamlit、language APIによるpushdownならSnowparkです。AIではrow task、unstructured retrieval、structured text-to-SQLをCortex内で分け、custom predictive ML lifecycleにはSnowflake MLを使います。

## 次に学ぶこと

Domain 1を終えたら[Domain 2](../domain-2/README.md)でsecurity、governance、monitoringを学びます。

## 根拠・関連する公式ドキュメント

- `docs-notebooks` — https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks-in-workspaces/notebooks-in-workspaces-overview
- `docs-streamlit` — https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit
- `docs-snowpark` — https://docs.snowflake.com/en/developer-guide/snowpark/index
- `docs-cortex-ai-functions` — https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql
- `docs-cortex-search` — https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/query-cortex-search-service
- `docs-cortex-analyst` — https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst
- `docs-snowflake-ml` — https://docs.snowflake.com/en/developer-guide/snowflake-ml/overview
