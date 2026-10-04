# 模擬試験

## 本番形式の100問セット

[問題冊子](sets/full-01-questions.md)を開き、解答を見ずに115分を目安として解いてください。単一選択と複数選択を混在させ、各問の必要選択数を明記しています。採点は[解答・復習冊子](sets/full-01-answers.md)で行います。

| Domain | 問題数 | 日本語版の配点 |
|---|---|---|
| 1 | 31 | 31% |
| 2 | 20 | 20% |
| 3 | 18 | 18% |
| 4 | 21 | 21% |
| 5 | 10 | 10% |
| 合計 | 100 | 100% |

全19 Objectiveから重複なしで出題し、Domainを混ぜた固定順序です。各問は選択肢の集合が正解と一致した場合に1点、部分点なしで採点します。学習の目安は総合80%以上・各Domain70%以上です。この素点は実試験のscaled scoreへ換算できません。115分はこの教材での練習時間の目安です。

解答冊子の採点一覧で全問を採点し、Domain別の正答率を記録してください。各問の解説から対応する本文に戻れます。100問は総合演習のための代表的な構成であり、89 Topicすべての確認には章末問題・Domain演習・以下の問題bankも使います。

## 問題bank

IDは `M1-Q<number>` を使用します。全103問のうち100問を総合セットに採用し、M1-Q56・Q62・Q63は公開範囲、再共有、共有tableの再作成を確認する補足問題として残しています。問題bankの並び順やDomain比率は総合セットとは異なります。構成の正本は[セット台帳](../../docs/mock-sets.json)です。

## 問題bank — Domain 1〜3

- [M1-Q01: 同時workloadの設計](m1-q01.md)
- [M1-Q02: 規制要件とEdition](m1-q02.md)
- [M1-Q03: account設計の選定軸](m1-q03.md)
- [M1-Q04: 統制されたdeployment tool](m1-q04.md)
- [M1-Q05: interface変更後の権限error](m1-q05.md)
- [M1-Q06: multi-account配置](m1-q06.md)
- [M1-Q07: 環境別timeout設定](m1-q07.md)
- [M1-Q08: concurrency改善](m1-q08.md)
- [M1-Q09: sporadic development warehouse](m1-q09.md)
- [M1-Q10: pruning改善](m1-q10.md)
- [M1-Q11: privacyとperformance](m1-q11.md)
- [M1-Q12: customer support assistant](m1-q12.md)
- [M1-Q13: business metric assistant](m1-q13.md)
- [M1-Q14: Managed grant model](m1-q14.md)
- [M1-Q15: Humanとserviceの認証分離](m1-q15.md)
- [M1-Q16: Cross-database session](m1-q16.md)
- [M1-Q17: PII governance rollout](m1-q17.md)
- [M1-Q18: Privacyとmaskingの選定](m1-q18.md)
- [M1-Q19: Security finding response](m1-q19.md)
- [M1-Q20: Regional disaster recovery](m1-q20.md)
- [M1-Q21: Warehouse cost incident](m1-q21.md)
- [M1-Q22: Customer-managed encryption key](m1-q22.md)
- [M1-Q23: Data quality alert](m1-q23.md)
- [M1-Q24: System roleの責務分離](m1-q24.md)
- [M1-Q25: 外部storageからの定期ロード設計](m1-q25.md)
- [M1-Q26: ローカルファイルの投入経路](m1-q26.md)
- [M1-Q27: 再ロードによる重複の調査](m1-q27.md)
- [M1-Q28: 部分的な失敗を許容するロード](m1-q28.md)
- [M1-Q29: 分析用エクスポートの出力形式](m1-q29.md)
- [M1-Q30: 到着即ロードの設計](m1-q30.md)
- [M1-Q31: CDC pipelineの不具合](m1-q31.md)
- [M1-Q32: 宣言的なpipelineの選択](m1-q32.md)
- [M1-Q33: 外部API呼び出しの構成](m1-q33.md)
- [M1-Q34: Git管理のSQLを実行する構成](m1-q34.md)

## 問題bank — Domain 4

- [M1-Q35: BIの待機だけが悪化](m1-q35.md)
- [M1-Q36: 集約の大量spill](m1-q36.md)
- [M1-Q37: 配賦と請求の差](m1-q37.md)
- [M1-Q38: 狭いfilterとJOIN増大](m1-q38.md)
- [M1-Q39: まれな大規模scan](m1-q39.md)
- [M1-Q40: 顧客IDの少数行検索](m1-q40.md)
- [M1-Q41: Standardの日付範囲検索](m1-q41.md)
- [M1-Q42: 安定した単一tableの反復集約](m1-q42.md)
- [M1-Q43: suspend後の結果再利用](m1-q43.md)
- [M1-Q44: COUNTとrow access policy](m1-q44.md)
- [M1-Q45: cacheを揃えた性能比較](m1-q45.md)
- [M1-Q46: JSON明細の数量集計](m1-q46.md)
- [M1-Q47: PDF一覧と本文の抽出](m1-q47.md)
- [M1-Q48: 明細を残した顧客合計](m1-q48.md)
- [M1-Q49: 顧客ごとの最新有効record](m1-q49.md)
- [M1-Q50: 重複を残す累積計算](m1-q50.md)

## 問題bank — Domain 2補足

- [M1-Q51: 共有applicationの配賦](m1-q51.md)
- [M1-Q52: 部門予算の対象管理](m1-q52.md)
- [M1-Q53: タグの権限境界](m1-q53.md)
- [M1-Q54: 予測通知後の停止判断](m1-q54.md)

## 問題bank — Domain 5

- [M1-Q55: 復旧先での書込み再開](m1-q55.md)
- [M1-Q56: 取引先ごとの公開範囲](m1-q56.md)
- [M1-Q57: 検証用分岐の更新](m1-q57.md)
- [M1-Q58: 誤DROP後の同名object](m1-q58.md)
- [M1-Q59: 保持期間を過ぎた復旧](m1-q59.md)
- [M1-Q60: 契約のない取引先の分析](m1-q60.md)
- [M1-Q61: Imported databaseの利用権限](m1-q61.md)
- [M1-Q62: 許可範囲内の再共有](m1-q62.md)
- [M1-Q63: 再作成した共有table](m1-q63.md)
- [M1-Q64: 制約付きの顧客重複分析](m1-q64.md)
- [M1-Q65: 外部データの発見と利用](m1-q65.md)
- [M1-Q66: 指定顧客への別region提供](m1-q66.md)
- [M1-Q67: 顧客accountで動く品質検査](m1-q67.md)

## 問題bank — 追加問題

- [M1-Q68: 停止中warehouseと保存データ](m1-q68.md)
- [M1-Q69: 復旧保持期間によるEdition選定](m1-q69.md)
- [M1-Q70: ブラウザーでの調査と可視化](m1-q70.md)
- [M1-Q71: SQLとSnowparkのIDE内開発](m1-q71.md)
- [M1-Q72: 再利用する処理objectの選定](m1-q72.md)
- [M1-Q73: Table名をSQL変数から参照する](m1-q73.md)
- [M1-Q74: Auto-scaleの応答性を優先する](m1-q74.md)
- [M1-Q75: メモリー主体のSnowpark workload](m1-q75.md)
- [M1-Q76: 短い間隔の再開とcache](m1-q76.md)
- [M1-Q77: Sessionをまたぐ中間table](m1-q77.md)
- [M1-Q78: 外部ファイルの読取りインターフェース](m1-q78.md)
- [M1-Q79: 日付filterで読むpartitionを減らす](m1-q79.md)
- [M1-Q80: Clusteringの維持費を評価する](m1-q80.md)
- [M1-Q81: 分析手順と実行結果をcellへまとめる](m1-q81.md)
- [M1-Q82: 業務利用者向けの入力画面](m1-q82.md)
- [M1-Q83: Pythonから大規模データの処理をpush downする](m1-q83.md)
- [M1-Q84: Table行への要約・分類の組込み](m1-q84.md)
- [M1-Q85: 予測modelのversionと推論を管理する](m1-q85.md)
- [M1-Q86: 接続元と認証方式を別々に制御する](m1-q86.md)
- [M1-Q87: Handlerのlogとtraceを収集する](m1-q87.md)
- [M1-Q88: 下流objectへの変更影響を調べる](m1-q88.md)
- [M1-Q89: 担当regionと個人情報の表示制約](m1-q89.md)
- [M1-Q90: Credit実績と請求額の境界](m1-q90.md)
- [M1-Q91: ファイルの場所と解釈規則の再利用](m1-q91.md)
- [M1-Q92: 非構造化ファイルをURLで利用する](m1-q92.md)
- [M1-Q93: 変換付きCOPYの事前検証](m1-q93.md)
- [M1-Q94: 通知を使えないファイル到着のロード依頼](m1-q94.md)
- [M1-Q95: ファイルを作らず行を取り込む](m1-q95.md)
- [M1-Q96: Serverless taskのowner権限](m1-q96.md)
- [M1-Q97: 外部systemとのNiFiベースのdata flow](m1-q97.md)
- [M1-Q98: Pythonでresource管理とSQL実行を分ける](m1-q98.md)
- [M1-Q99: Joinの出力行数増大](m1-q99.md)
- [M1-Q100: QASの適用条件とコスト](m1-q100.md)
- [M1-Q101: 保存済み結果の保持期間](m1-q101.md)
- [M1-Q102: NULLを含む集計](m1-q102.md)
- [M1-Q103: 同額の最高額注文をすべて返す](m1-q103.md)
