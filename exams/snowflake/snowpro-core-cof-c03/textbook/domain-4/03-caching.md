# 4.3 キャッシュを利用する

> Status: review
> Last verified: 2026-10-03

## この章で学ぶこと

- 結果再利用、metadataによる処理、warehouseのdata cacheを区別する。
- SQLやデータの変更、role、suspendが各仕組みへ与える影響を判断する。
- 性能比較でcacheの状態を揃える。

## 前提知識

[1.1 アーキテクチャ](../domain-1/01-architecture.md)のcomputeとstorageの分離、[1.5](../domain-1/05-storage-concepts.md)のmetadata、[4.1](01-evaluate-query-performance.md)のscan統計を前提にします。

## この章の用語

| 用語 | 意味 |
|---|---|
| persisted query result | 実行後に一定期間保存されるクエリ結果 |
| retrieval optimization | 条件が合う保存結果を使い、再計算を省くこと |
| metadata | tableやmicro-partitionの行数・値域など、データについての情報 |
| warehouse cache | 実行中warehouseのlocal storageに保持するtable data |
| warm／cold | 比較対象のtable dataがlocal cacheにある状態／ない状態 |

## 試験範囲との対応

| Topic | 本文 | 公式根拠 |
|---|---|---|
| Query result cache | [保存結果を再利用する](#query-result-cache) | `docs-persisted-results` |
| Metadata cache | [metadataで読み取りを省く](#metadata-cache) | `docs-micro-partitions`, `docs-count` |
| Warehouse cache | [localのtable dataを読む](#warehouse-cache) | `docs-warehouse-cache` |

[COF-C03 Syllabus](../../docs/syllabus.md)のObjective 4.3に対応します。

## 何を再利用するのかを分ける

| 仕組み | 再利用するもの | SQL実行への効果 | warehouse suspendの影響 |
|---|---|---|---|
| Query result cache | 計算済みの結果 | 条件が合えばクエリ処理自体を省略 | local cacheの破棄とは別。suspendだけでは結果は消えない |
| Metadata cache | table／partitionについての情報 | pruningや対応する集約で読み取りを省く | local warehouse data cacheとは別 |
| Warehouse cache | 以前読んだtable data | 再実行時のremote storage読み取りを減らす | local cacheが破棄される |

「2回目が速い」だけでは、どの仕組みが効いたかは分かりません。結果を返すだけだったのか、処理したがremoteから読む量が減ったのかを区別します。

[図: 3つの再利用対象](../../diagrams/domain-4/cache-layers.md)

<a id="query-result-cache"></a>
## 保存結果を再利用してクエリ処理を省く

前回と同じ結果を返せる条件が揃うと、Snowflakeは保存結果を取得し、クエリ処理を省略できます。warehouseのlocal data cacheを使う再実行と異なり、scanや集約そのものを繰り返しません。

代表的な再利用条件は、SQLが同一、結果に寄与するtable dataとmicro-partitionが変わっていない、結果が保持されている、roleが必要な権限を持つ、結果に影響する設定が変わっていないことです。SQLの大文字・小文字やaliasの差でも完全な再利用が妨げられます。RANDOMのような再利用できない関数、external function、hybrid table等にも条件があります。

SELECTでは対象tableへの権限が必要です。「同じuserだけ」「同じwarehouseだけ」という規則ではありません。SHOWの結果再利用では生成時と同じroleという条件があります。条件が揃っても再利用は保証されないため、Profileで実行の有無を確かめます。

結果は原則24時間保持され、再利用で24時間が更新されます。ただし初回実行から最大31日です。この保持期間はwarehouse cacheの保持期間ではありません。根拠: `docs-persisted-results`。

### USE_CACHED_RESULTで結果再利用を制御する

既定では結果再利用が有効です。sessionで無効にして比較したい場合は次の設定を使います。

```sql
ALTER SESSION SET USE_CACHED_RESULT = FALSE;
```

これは保存結果の再利用を無効にする設定で、warehouse cacheやmetadataをすべて空にする命令ではありません。SELECTが速いままでも、localから読み取っている可能性があります。

比較後、sessionに設定した上書きを外すなら次を使います。accountやuserから継承する設定へ戻るため、無条件にTRUEへ変更するより元の文脈を保てます。

```sql
ALTER SESSION UNSET USE_CACHED_RESULT;
```

根拠: `docs-persisted-results`, `docs-parameters`。

<a id="metadata-cache"></a>
## metadataで読み取りを省く

Snowflakeはmicro-partitionの列の値域などを保持します。日付filterと値域を比較し、該当しないpartitionを読まない判断がpruningです。完成したSELECT結果を再利用しているのではなく、データに関する情報から読む範囲を決めています。

tableの統計で答えられる処理もあります。単純なCOUNT等で統計を使える場合、明細をすべて読む必要がありません。ただし任意のWHEREやJOIN付き集計をmetadataだけで計算できると一般化しません。row access policyがあるCOUNTでは、roleごとに見える行を判定するために行をscanする必要があります。

metadataを利用した処理について、結果cacheと同じ「24時間」「同一SQLが必要」という規則を当てはめません。どの処理でscanが省かれたかをProfileと統計から読みます。根拠: `docs-micro-partitions`, `docs-count`。

<a id="warehouse-cache"></a>
## warehouseのlocalにあるtable dataを読む

実行中warehouseは読み取ったtable dataをlocalにcacheします。同じwarehouseで、そのデータを使う後続クエリはremote storageから読む量を減らせます。SQLが完全一致しなくても、同じtable dataを読むなら恩恵を受ける可能性があります。結果の再計算は行われます。

warehouseをsuspendするとlocal cacheは破棄されます。resume後は以前と同じwarehouse名でもcoldな状態から始まります。別warehouseのlocal cacheへ自動で引き継ぐものでもありません。保存結果は別管理なので、local cacheが消えても結果再利用の条件が揃う場合があります。

### auto-suspendはidle費用と再読み込みを比較する

短い間隔で同じdataを読むBIでは、毎回suspendするとcacheを繰り返し作り直します。適度に待ってsuspendする構成を検討します。一方、30分おきの処理に10分のauto-suspendを設定しても次の実行前にcacheが失われ、10分間のidle creditは発生します。cache維持だけを理由に常時稼働へしません。

SQLのAUTO_SUSPENDは秒単位です。次は既存warehouseを変更できるroleで使う10分の設定例で、すべてのworkloadの最適値ではありません。

```sql
ALTER WAREHOUSE bi_wh SET AUTO_SUSPEND = 600;
```

### scanしたdataのうちlocalから読んだ割合を確認する

QUERY_HISTORYの`percentage_scanned_from_cache`はlocal cacheからscanした割合です。保存結果へのhit率ではありません。次はSNOWFLAKE databaseの参照権限を持つroleで読む例です。

```sql
SELECT warehouse_name,
       SUM(bytes_scanned * percentage_scanned_from_cache)
         / NULLIF(SUM(bytes_scanned), 0) AS cache_scan_fraction
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
  AND bytes_scanned > 0
GROUP BY warehouse_name;
```

scan量で重み付けした比率です。大量scanと少量scanを単純平均せず、warehouseがどれだけlocal dataを利用したかを確認します。根拠: `docs-warehouse-cache`, `docs-query-history`。

## cacheを考慮した比較の手順

結果再利用を無効にし、同じSQL・データ・warehouse sizeで、coldとwarmを区別して測ります。local cacheの影響を調べるなら、結果再利用だけを切った2回目と、suspend／resume後を比べます。稼働中の共有warehouseを測定目的で勝手にsuspendせず、専用の検証環境で実施します。

## 試験で重要なポイント

結果cacheは処理の省略、metadataは読み取り範囲や対応する集約の判断、warehouse cacheは読み取ったdataの再利用です。suspendの説明では、どのcacheが対象かを特定します。

## 間違えやすいポイント

- USE_CACHED_RESULT = FALSEを「すべてのcache削除」と扱わない。
- local cacheのscan比率を結果cacheのhit率と呼ばない。
- tableや権限が変わっても同じSQLなら必ず再利用できる、と考えない。

## 確認問題

- [C4-4.3-Q01: 保存結果の再利用条件](../../exercises/chapter/c4-4.3-q01.md)
- [C4-4.3-Q02: 保存結果の保持](../../exercises/chapter/c4-4.3-q02.md)
- [C4-4.3-Q03: metadataを使う処理](../../exercises/chapter/c4-4.3-q03.md)
- [C4-4.3-Q04: suspendとlocal cache](../../exercises/chapter/c4-4.3-q04.md)
- [C4-4.3-Q05: 結果再利用の制御](../../exercises/chapter/c4-4.3-q05.md)

## 章のまとめ

保存結果、metadata、local table dataは再利用の対象と条件が異なります。性能比較では何が省略されたかを確認し、warehouseのidle費用とcache効果を両方評価します。

## 次に学ぶこと

[4.4 データ変換を実行する](04-data-transformation.md)で、SQLの処理と出力を確認します。

## 根拠・関連する公式ドキュメント

- `docs-persisted-results` — https://docs.snowflake.com/en/user-guide/querying-persisted-results
- `docs-parameters` — https://docs.snowflake.com/en/sql-reference/parameters
- `docs-micro-partitions` — https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions
- `docs-count` — https://docs.snowflake.com/en/sql-reference/functions/count
- `docs-warehouse-cache` — https://docs.snowflake.com/en/user-guide/performance-query-warehouse-cache
- `docs-query-history` — https://docs.snowflake.com/en/sql-reference/account-usage/query_history
