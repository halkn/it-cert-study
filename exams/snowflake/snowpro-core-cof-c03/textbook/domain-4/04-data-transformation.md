# 4.4 データ変換を実行する

> Status: review
> Last verified: 2026-10-03

## この章で学ぶこと

- データの形に応じて列、VARIANT、stageを使い分ける。
- 集約とwindow functionの出力粒度、NULL、frameを説明する。
- 結果の意味を保ちながら、filter・JOIN・集合演算を改善する。

## 前提知識

基本的なSELECT、WHERE、JOIN、GROUP BYを前提にします。[3.1](../domain-3/01-loading-unloading.md)のstageとdirectory table、[4.1](01-evaluate-query-performance.md)のpruningとJOINの診断を参照します。

## この章の用語

| 用語 | 意味 |
|---|---|
| VARIANT | 型情報を持つ値を保持し、JSON等の階層データを扱える型 |
| FLATTEN | ARRAYやOBJECTなどの複合値を複数行へ展開するtable function |
| aggregate function（集約関数） | 複数行から合計や件数などの値を求める関数 |
| window function（ウィンドウ関数） | 各行を残し、関連する行集合を使って値を計算する関数 |
| PARTITION BY | window計算の対象行を区切る指定。storageのpartitionとは別 |
| window frame | partition内で現在行の計算に使う範囲 |
| QUALIFY | window計算後の値で行を絞る句 |

## 試験範囲との対応

| Topic | 本文 | 公式根拠 |
|---|---|---|
| データの利用 | [3種類のデータ](#data-types) | `docs-query-semistructured`, `docs-flatten`, `docs-unstructured-intro` |
| Aggregate function | [粒度とNULL](#aggregate-functions) | `docs-aggregate-functions`, `docs-count` |
| クエリ最適化のためのSQL | [意味を保つ改善](#sql-query-optimization) | `docs-query-insights`, `docs-joins`, `docs-micro-partitions` |
| Window function | [行を残す計算](#window-functions) | `docs-window-functions`, `docs-qualify` |

[COF-C03 Syllabus](../../docs/syllabus.md)のObjective 4.4に対応します。

<a id="data-types"></a>
## データの形に応じて取り出し方を変える

| 形 | 例 | Snowflakeでの扱い |
|---|---|---|
| structured（構造化） | 日付・顧客ID・金額を持つ明細 | 型の定まったtable列をSQLで扱う |
| semi-structured（半構造化） | key、object、arrayを持つJSON | VARIANT等へ保持しpathで値を取り出す |
| unstructured（非構造化） | PDF、画像、音声 | stage上のfileを参照し、必要に応じhandler等で内容を処理する |

JSONにも構造はありますが、固定されたtable列と異なり、入れ子やrecordごとのkeyの違いを扱います。PDFをstageへ置くだけで文書内容がJSONのfieldになるわけではありません。

### JSONのpathで値を取り出し、ARRAYを行へ展開する

次はtableを作らず、CTE（このSQL内だけで使う名前付き結果）にJSONを1件用意する例です。SELECTを実行できるwarehouseで使います。

```sql
WITH orders AS (
  SELECT PARSE_JSON('{"customer":"A","items":[
    {"sku":"P1","qty":2},{"sku":"P2","qty":1}]}') AS payload
)
SELECT o.payload:customer::VARCHAR AS customer,
       f.value:sku::VARCHAR AS sku,
       f.value:qty::NUMBER AS qty
FROM orders o, LATERAL FLATTEN(INPUT => o.payload:items) f
ORDER BY sku;
```

| CUSTOMER | SKU | QTY |
|---|---|---|
| A | P1 | 2 |
| A | P2 | 1 |

`:`で最初のkey、`.`で下位のkey、`[0]`でarrayの最初の要素へアクセスします。pathからの値はVARIANTなので、計算や文字列処理に合わせて明示的にcastします。JSONのkeyは大文字・小文字を区別します。

LATERALは前にある行の値を使うための指定です。FLATTENは要素ごとに行を返し、VALUE列に要素が入ります。元の注文1行が2行になるので、展開後のCOUNT(*)は注文件数ではなく明細要素数になる点に注意します。根拠: `docs-query-semistructured`, `docs-flatten`。

### 非構造化fileはmetadataと内容を区別する

directory tableはstage上のfileのpath、size、URLなどを一覧化します。fileの内容を自動でSQL列へ変換するものではありません。内容の抽出はUDFやprocedure handler等の別処理が必要です。

```sql
SELECT relative_path, size, file_url
FROM DIRECTORY(@document_stage);
```

この例はdirectory tableが有効でmetadataが更新された既存stageを前提にします。参照にはinternal stageのREAD、external stageのUSAGEなど適切な権限が必要です。stageの設定は[3.1](../domain-3/01-loading-unloading.md#directory-tables)を参照します。根拠: `docs-unstructured-intro`, `docs-data-load-dirtables`。

<a id="aggregate-functions"></a>
## 集約は出力の粒度とNULLの扱いを決める

GROUP BYは同じkeyの行をまとめ、SUM、AVG、MIN、MAX、COUNTなどで代表値を求めます。顧客別にまとめれば結果は顧客ごとに1行です。keyを指定しない集約は入力全体を1つの集合として扱います。

```sql
WITH sales(customer, amount) AS (
  SELECT column1, column2::NUMBER
  FROM VALUES ('A', 100), ('A', 200), ('B', 50), ('B', NULL)
)
SELECT customer, COUNT(*) AS row_count,
       COUNT(amount) AS amount_count,
       SUM(amount) AS total_amount, AVG(amount) AS avg_amount
FROM sales
GROUP BY customer
ORDER BY customer;
```

| CUSTOMER | ROW_COUNT | AMOUNT_COUNT | TOTAL_AMOUNT | AVG_AMOUNT |
|---|---|---|---|---|
| A | 2 | 2 | 300 | 150 |
| B | 2 | 1 | 50 | 50 |

COUNT(*)は行数、COUNT(amount)はamountが非NULLの行数です。SUMやAVGはNULLを除外するので、Bの平均は25ではなく50です。NULLを0扱いする業務要件なら、COALESCE等で明示します。DISTINCTを使うCOUNTは重複を除いた値を数えます。根拠: `docs-aggregate-functions`, `docs-count`。

WHEREは集約前の行、HAVINGは集約後のgroupを絞ります。「有効な明細を対象とし、合計が一定以上の顧客を返す」なら明細条件をWHERE、合計条件をHAVINGへ置きます。

<a id="sql-query-optimization"></a>
## 結果の意味を保ってscanと中間データを減らす

まず結果の粒度と行の対応を正しくします。不要な列や行を避け、JOIN条件を明示し、重複除去が不要ならUNION ALLを検討します。UNIONは重複除去が必要な要件で使い、速さだけを理由に結果の意味を変えません。

### 日付filterは範囲と型を明確にする

既存のsales tableにTIMESTAMP_NTZ型のsold_atがある場合、次は2026年9月を対象にする例です。

```sql
SELECT customer_id, amount
FROM sales
WHERE sold_at >= '2026-09-01 00:00:00'::TIMESTAMP_NTZ
  AND sold_at <  '2026-10-01 00:00:00'::TIMESTAMP_NTZ;
```

上限を含まない範囲にすると9月末の小数秒も含み、10月の値は除外できます。columnを直接比較し、metadataの値域と対応を追いやすくします。「関数をcolumnに使うと必ずpruning不能」とは限りません。実際にscanするpartitionをProfileで確認します。根拠: `docs-micro-partitions`。

### JOINで粒度を崩し、最後にDISTINCTで隠さない

日別集計同士を結合したいなら、双方を日単位へ揃えてから結合します。明細同士を日付だけで結合すると、同じ日の各行同士が組み合わさり、金額が重複集計される場合があります。CTEを使っただけで中間結果が必ず物理保存されるわけではないので、書き方の短さと実行性能を同一視しません。根拠: `docs-joins`, `docs-query-insights`。

改善後は同じdataとcache状態でProfileを比べ、scanとjoin出力が要件に合って減ったか確認します。

<a id="window-functions"></a>
## window functionは各行を残して関連する行を計算する

GROUP BYはgroup単位へ縮約します。window functionは各明細行を残して、顧客合計、順位、累積値などを付けます。同じSUMでもOVERがあるかで出力の粒度が変わります。

[図: 集約とwindow計算の出力](../../diagrams/domain-4/transformation-grain.md)

```sql
WITH sales(id, customer, amount) AS (
  SELECT column1, column2, column3
  FROM VALUES (1, 'A', 100), (2, 'A', 200), (3, 'B', 50)
)
SELECT id, customer, amount,
       SUM(amount) OVER (PARTITION BY customer) AS customer_total,
       SUM(amount) OVER (
         PARTITION BY customer ORDER BY id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM sales
ORDER BY id;
```

| ID | CUSTOMER | AMOUNT | CUSTOMER_TOTAL | RUNNING_TOTAL |
|---|---|---|---|---|
| 1 | A | 100 | 300 | 100 |
| 2 | A | 200 | 300 | 300 |
| 3 | B | 50 | 50 | 50 |

PARTITION BYで顧客ごとに区切り、frameで先頭から現在行までを計算します。window内のORDER BYは計算順、最後のORDER BYは返却順です。window内だけでは出力順を保証しません。

### ROWSとRANGE、順位関数を使い分ける

ROWSは順序に沿った行位置、RANGEはORDER BYの値を基準に範囲を決めます。RANGEのCURRENT ROWは同じORDER BY値の行も含みます。値10、10、20で「先頭から現在まで」をSUMすると、ROWSでは順に10、20、40、RANGEでは20、20、40になります。ROWSの同値行の順序を固定したい場合は一意なtie-breakerを加えます。

ROW_NUMBERは行ごとに連番を付け、RANKは同順位を付けた後の順位に欠番が生じ、DENSE_RANKは欠番がありません。金額200、200、100を降順に並べるとRANKは1、1、3、DENSE_RANKは1、1、2です。「必ず1件」と「同率最高をすべて」は異なる要件です。根拠: `docs-window-functions`, `docs-window-syntax`, `docs-rank`, `docs-dense-rank`。

### QUALIFYで顧客ごとの1件を取り出す

```sql
WITH sales(id, customer, amount) AS (
  SELECT column1, column2, column3
  FROM VALUES (1, 'A', 100), (2, 'A', 200), (3, 'B', 50)
)
SELECT id, customer, amount
FROM sales
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY customer ORDER BY amount DESC, id
) = 1
ORDER BY customer;
```

結果はAのid=2とBのid=3です。amountが同じでもidで順序を固定し、各顧客から1件を返します。window計算前のWHEREへROW_NUMBER条件を置くことはできません。QUALIFYはwindow計算後に絞り込み、SELECTで付けたwindow式のaliasも参照できます。根拠: `docs-qualify`。

| 句 | 絞る段階 | 例 |
|---|---|---|
| WHERE | 集約・window計算の前 | 有効な明細 |
| HAVING | GROUP BYで集約した後 | 顧客合計が1,000以上 |
| QUALIFY | window計算の後 | 顧客内の連番が1 |

## 試験で重要なポイント

データ型、展開後の粒度、NULL、集約とwindowの違い、filterする段階を追います。SQLの性能改善でも求める結果は保ちます。

## 間違えやすいポイント

- directory tableを文書内容の抽出結果と扱わない。
- FLATTEN後のCOUNT(*)を元record数と混同しない。
- window内のORDER BYを結果の並び順と同一視しない。
- ROW_NUMBERとRANKを、同率最高の扱いを確認せず置き換えない。

## 確認問題

- [C4-4.4-Q01: 半構造化dataのkey](../../exercises/chapter/c4-4.4-q01.md)
- [C4-4.4-Q02: FLATTEN後の件数](../../exercises/chapter/c4-4.4-q02.md)
- [C4-4.4-Q03: directory tableの対象](../../exercises/chapter/c4-4.4-q03.md)
- [C4-4.4-Q04: COUNTとAVGのNULL](../../exercises/chapter/c4-4.4-q04.md)
- [C4-4.4-Q05: filterする段階](../../exercises/chapter/c4-4.4-q05.md)
- [C4-4.4-Q06: UNION ALLの意味](../../exercises/chapter/c4-4.4-q06.md)
- [C4-4.4-Q07: ROWSとRANGE](../../exercises/chapter/c4-4.4-q07.md)
- [C4-4.4-Q08: QUALIFYの対象](../../exercises/chapter/c4-4.4-q08.md)

## 章のまとめ

pathとFLATTENで半構造化データを扱い、stageではfile内容とmetadataを分けます。GROUP BYで縮約するか、windowで行を残すかを決め、WHERE・HAVING・QUALIFYを処理段階に合わせます。

## 次に学ぶこと

[Domain演習](../../exercises/domain/README.md)で診断・最適化・cache・変換を組み合わせます。その後は[Domain 5](../domain-5/README.md)へ進みますが、Domain 5は未完成です。

## 根拠・関連する公式ドキュメント

- `docs-query-semistructured` — https://docs.snowflake.com/en/user-guide/querying-semistructured
- `docs-flatten` — https://docs.snowflake.com/en/sql-reference/functions/flatten
- `docs-unstructured-intro` — https://docs.snowflake.com/en/user-guide/unstructured-intro
- `docs-data-load-dirtables` — https://docs.snowflake.com/en/user-guide/data-load-dirtables
- `docs-aggregate-functions` — https://docs.snowflake.com/en/sql-reference/functions-aggregation
- `docs-count` — https://docs.snowflake.com/en/sql-reference/functions/count
- `docs-query-insights` — https://docs.snowflake.com/en/user-guide/query-insights
- `docs-joins` — https://docs.snowflake.com/en/user-guide/querying-joins
- `docs-micro-partitions` — https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions
- `docs-set-operators` — https://docs.snowflake.com/en/sql-reference/operators-query
- `docs-window-functions` — https://docs.snowflake.com/en/user-guide/functions-window-using
- `docs-window-syntax` — https://docs.snowflake.com/en/sql-reference/functions-window-syntax
- `docs-qualify` — https://docs.snowflake.com/en/sql-reference/constructs/qualify
- `docs-rank` — https://docs.snowflake.com/en/sql-reference/functions/rank
- `docs-dense-rank` — https://docs.snowflake.com/en/sql-reference/functions/dense_rank
