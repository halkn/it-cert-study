# 4.2 クエリ性能を最適化する

> Status: complete
> Last verified: 2026-10-03

## この章で学ぶこと

- 4つの最適化手法を、変える対象・適したクエリ・費用で比較する。
- 要件から候補を選び、Editionと適用条件を確認する。
- 改善前後を同じ条件で評価する。

## 前提知識

[4.1](01-evaluate-query-performance.md)の診断、[1.5](../domain-1/05-storage-concepts.md)のmicro-partitionとview、[1.4](../domain-1/04-virtual-warehouses.md)のwarehouseを前提にします。

## この章の用語

| 用語 | 意味 |
|---|---|
| selectivity（選択性） | filterが対象行をどれほど絞れるか。少数行へ絞る条件を高い選択性と呼ぶ |
| cardinality | 列や式に現れる異なる値の数 |
| Query Acceleration Service（QAS） | eligibleな処理の一部をserverless computeへ渡すサービス |
| Search Optimization Service | 検索用の永続的な構造を維持し、scanを減らすサービス |
| clustering key | データを近くに配置する基準となる列または式の組 |
| materialized view | SELECTの計算結果を保存し、Snowflakeが維持するview |

## 試験範囲との対応

| Topic | 本文 | 公式根拠 |
|---|---|---|
| Query Acceleration | [並列化できる処理へcomputeを追加](#query-acceleration) | `docs-query-acceleration` |
| Search Optimization | [少数行を探す](#search-optimization) | `docs-search-optimization`, `docs-performance-storage` |
| Clustering key | [配置を整える](#clustering-keys) | `docs-clustering-keys`, `docs-performance-storage` |
| Materialized view | [計算結果を保存](#materialized-views) | `docs-materialized-views`, `docs-performance-storage` |

日本語版Study Guide（2026-02-20更新、p.10）の対応範囲も照合済みです。`exam-study-guide-c03-jpn-2026-02-20`を参照してください。

[COF-C03 Syllabus](../../docs/syllabus.md)のObjective 4.2に対応します。

## 改善する対象で4つの手法を分ける

| 手法 | 変える対象 | 候補となる要件 | 主な追加費用 | Edition |
|---|---|---|---|---|
| QAS | クエリ処理のcompute | 大きなscan等の並列化可能な部分を速くする | 使用したserverless compute | Enterprise以上 |
| Search Optimization | 検索用のaccess path | 巨大tableからID等で少数行を探す | 構築・保守computeと構造のstorage | Enterprise以上 |
| Clustering | table dataの配置 | 頻繁な日付範囲等でpruningを改善する | 再配置compute、再書き込みに伴うstorage | Standardでも利用可能 |
| Materialized view | 事前計算したデータ集合 | 同じ単一tableの集約等を繰り返す | 保存storageと維持compute | Enterprise以上 |

まずJOIN条件やfilterの誤りを直し、それでも残るコストへ適用します。複数手法の併用は可能ですが、機能を増やすだけで費用対効果がよくなるわけではありません。根拠: `docs-performance-options`, `docs-performance-storage`。

[図: workloadから最適化手法を選ぶ](../../diagrams/domain-4/optimization-selection.md)

<a id="query-acceleration"></a>
## QASはeligibleな処理の一部をserverless computeへ渡す

時々大きなscanを行うクエリのためにwarehouse全体を常に大きくする代わりに、処理の一部をQASへ渡せます。warehouseが処理を統括し、QASのshared computeが並列化できる部分を担当します。cluster数を増やす機能ではありません。

大きなscanと選択性の高いfilterや集約などが候補です。ただしSQLの形だけではeligibleと決まらず、scan量、実行計画、warehouse sizeなどに依存します。利用できるservice資源によって効果も変わります。

### 対象と費用を確認して設定する

`SYSTEM$ESTIMATE_QUERY_ACCELERATION`に実行済みquery IDを渡し、対象可否やscale factor別の時間見積りを確認します。IDは自身の履歴から取得して置き換えます。

```sql
SELECT PARSE_JSON(SYSTEM$ESTIMATE_QUERY_ACCELERATION('<query-id>'));
```

次は既存warehouseを変更する設定例です。変更できるroleとEnterprise以上が必要です。

```sql
ALTER WAREHOUSE analytics_wh SET
  ENABLE_QUERY_ACCELERATION = TRUE
  QUERY_ACCELERATION_MAX_SCALE_FACTOR = 2;
```

scale factorはQASが借りるcomputeの上限をwarehouse sizeを基準に指定します。`2`は速度2倍の保証ではなく、`0`は無効化ではなく上限をなくす値です。QASのcreditはwarehouse分とは別に発生します。

2026-10-03確認の公式文書では、Gen2 standardやmulti-clusterの作成時にQASが自動で有効になる場合と、明示的に有効化する場合で既定scale factorが異なります。この例は値を明示します。また、以前の「LIMITには必ずORDER BYが必要」という制約を一般化せず、現在のeligible判定を確認します。根拠: `docs-query-acceleration`。

<a id="search-optimization"></a>
## Search Optimizationは巨大tableから少数行を探す

顧客IDを指定して数十億行から数行を取り出す場合、読むべきpartitionを素早く特定することが重要です。値とそれを含むmicro-partitionを結び付ける **search access path** を維持し、候補partitionを減らします。結果そのものを保存するcacheとは異なります。

代表例は等価条件のpoint lookupです。対応するsubstring・正規表現・geospatial・半構造化データの検索にも利用できますが、演算子・型に適用条件があります。tableの大半を返す検索を一律に高速化する機能ではありません。

次は既存tableの顧客IDへの等価検索を対象にする例です。対象tableを設定できるroleとEnterprise以上が必要です。

```sql
ALTER TABLE customers ADD SEARCH OPTIMIZATION ON EQUALITY(customer_id);
```

構造の構築・更新にserverless compute、保存にstorageが必要です。頻繁な更新では維持費も評価します。Search Optimizationで不要partitionを減らした後、残るeligibleなscanをQASへ渡す併用も可能です。根拠: `docs-search-optimization`, `docs-performance-options`。

<a id="clustering-keys"></a>
## clustering keyは頻繁なfilterに合わせて配置を整える

日付が各partitionへ広く混ざると、狭い日付条件でも多数のpartitionが候補になります。clusteringは似たkey値のデータを近くにまとめ、値域の重なりを減らしてpruningを助けます。明示的なkeyがなくても自然な配置とmetadataによるpruningは働きます。

大きなtableで、同じ列を使う範囲filterが頻繁な場合が候補です。tableごとのkeyは1つですが、複数の列・式を組み合わせられます。返却行の順序を保証するものではありません。

```sql
ALTER TABLE sales CLUSTER BY (TO_DATE(sold_at));
```

timestampの値が極端に多い場合、日付へ変換してcardinalityを減らす例です。keyは「ユニークな列ならよい」とは限りません。Booleanだけでは絞り込みが弱く、極端に高いcardinalityでは維持コストが増え得ます。頻繁なfilterと値域を一緒に検討します。

Automatic Clusteringはkeyに基づく配置を維持します。serverless computeを使い、再書き込みに伴うTime Travel／Fail-safeのstorageにも影響します。小さいtableやまれな検索では改善より維持費が大きい場合があります。根拠: `docs-clustering-keys`, `docs-performance-storage`。

<a id="materialized-views"></a>
## materialized viewは繰り返す計算結果を保存する

売上tableの日別集計を繰り返すなら、毎回明細から合計する代わりに集約済みデータを保存できます。通常のviewはSQL定義を保存しますが、materialized viewは結果も保存し、Snowflakeがbase tableの変更に合わせて維持します。

```sql
CREATE MATERIALIZED VIEW daily_sales AS
SELECT sold_date, SUM(amount) AS total_amount
FROM sales
GROUP BY sold_date;
```

`sales`に`sold_date`と`amount`がある前提です。schema上のCREATE MATERIALIZED VIEW、元tableのSELECTなどの権限とEnterprise以上が必要です。

直接viewを読むことも、optimizerが条件に合うbase tableへのクエリを書き換えて利用することもできます。保存した列・行・計算が対象で、元tableに対するすべてのクエリを高速化するわけではありません。

定義できるSELECTには制約があります。単一tableが基準で、JOINやwindow functionを含む任意のクエリをそのまま保存できるわけではありません。複雑なpipelineの自動更新は[3.2のDynamic Table](../domain-3/02-automated-ingestion.md#dynamic-tables)と用途を比較します。

頻繁なbase table変更では保守computeが増え得ます。保存storageも追加されるので、節約できる問い合わせ費用が維持費を上回るかを評価します。根拠: `docs-materialized-views`, `docs-performance-storage`。

## 同じ条件で改善前後を評価する

SQL、対象データ、warehouse size、同時負荷、cacheの状態を揃え、時間・scan量・creditを比較します。[4.3](03-caching.md)の結果再利用で処理自体を省略した実行と、scanした実行を直接比較しません。

## 試験で重要なポイント

少数行検索はSearch Optimization、範囲検索の配置改善はclustering、同じ計算の事前保存はmaterialized view、eligibleな処理へのcompute追加はQAS、と対象から選びます。

## 間違えやすいポイント

- QASのscale factorを速度倍率と同一視しない。
- clustering keyがないとpruningが働かない、と考えない。
- Enterprise以上という条件をclusteringへ一括適用しない。
- 通常のview・結果cache・materialized viewを同じ保存機構と扱わない。

## 確認問題

- [C4-4.2-Q01: QASの対象](../../exercises/chapter/c4-4.2-q01.md)
- [C4-4.2-Q02: scale factorの境界](../../exercises/chapter/c4-4.2-q02.md)
- [C4-4.2-Q03: Search Optimizationの対象](../../exercises/chapter/c4-4.2-q03.md)
- [C4-4.2-Q04: clustering keyの式](../../exercises/chapter/c4-4.2-q04.md)
- [C4-4.2-Q05: materialized viewの定義](../../exercises/chapter/c4-4.2-q05.md)

## 章のまとめ

compute、検索構造、データ配置、保存結果のどれを変えるかが選定軸です。実測したボトルネックに合う手法を選び、追加費用・Edition・制約を確認します。

## 次に学ぶこと

[4.3 キャッシュを利用する](03-caching.md)で、処理の省略と読み取りの高速化を分けます。

## 根拠・関連する公式ドキュメント

- `docs-query-acceleration` — https://docs.snowflake.com/en/user-guide/query-acceleration-service
- `docs-performance-options` — https://docs.snowflake.com/en/user-guide/performance-query-options
- `docs-search-optimization` — https://docs.snowflake.com/en/user-guide/search-optimization-service
- `docs-performance-storage` — https://docs.snowflake.com/en/user-guide/performance-query-storage
- `docs-clustering-keys` — https://docs.snowflake.com/en/user-guide/tables-clustering-keys
- `docs-micro-partitions` — https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions
- `docs-materialized-views` — https://docs.snowflake.com/en/user-guide/views-materialized
- `docs-create-materialized-view` — https://docs.snowflake.com/en/sql-reference/sql/create-materialized-view

- `exam-study-guide-c03-jpn-2026-02-20` — https://learn.snowflake.com/en/certifications/snowpro-core-jpn-C03/ （ユーザー提供の配布PDFを確認）
