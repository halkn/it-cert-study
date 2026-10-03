# Verification Log

公式情報を再確認した履歴です。個々の URL の確認日は `sources.json` に記録します。

| Date | Scope | Result |
|---|---|---|
| 2026-08-13 | 英語版 COF-C03 Certification Page / Study Guide | Study Guide 2026-07-08 版を確認。5 domains、weights、19 objectives と配下トピックを登録。 |
| 2026-08-13 | 日本語版 COF-C03 Certification Page | 日本語認定ページとStudy Guide申込フォームを確認。配布PDFの版・英語版との同等性は未検証。 |
| 2026-08-13 | Objective 1.1 | Architecture、cloud platform、Edition、compute costの公式docsを確認。本文、図、8問、Coverage Matrixを更新。 |
| 2026-08-13 | Objective 1.1 学習量レビュー | 公式Study Guideのsample question、公式Practice Exam、公式Level Up、合格体験の学習傾向と比較。公式文書読解課題、ミニハンズオン、重複を抑えた4問を追加し、全12問へ拡充。 |
| 2026-08-13 | Objective 1.2 | Snowsight、Workspaces移行、Snowflake CLI、VS Code拡張の公式docsを確認。本文、読解課題、context確認ハンズオン、7問、Coverage Matrixを更新。 |
| 2026-08-13 | Objective 1.3 | Organization／account／database object階層、parameter precedence、SQL variable、context functionの公式docsを確認。自作階層図、本文、ハンズオン、7問、各registryを更新。 |
| 2026-08-13 | Objective 1.4 | Standard Gen1／Gen2、Snowpark-optimized、multi-cluster policy、workload別sizing、auto-suspendの公式docsを確認。scaling図、本文、ハンズオン、8問、各registryを更新。 |
| 2026-08-13 | Objective 1.5 | Micro-partition／clustering、6 table types、3 view typesの公式docsを確認。pruning図、本文、ハンズオン、8問、各registryを更新。 |
| 2026-08-13 | Objective 1.6 | Notebooks、Streamlit、Snowpark、Cortex AI Functions／Search／Analyst、Snowflake MLの公式docsを確認。選定図、本文、ハンズオン、9問、各registryを更新。 |
| 2026-08-16 | Objective 2.1 | RBAC／DAC、object hierarchy、network／authentication policy、MFA、federation、OAuth／key pair、role種別、account identifier、logging／tracingの公式docsを確認。権限図、本文、章末10問、関連Domain 4問、関連模擬6問へ対応。MFA移行条件は14日周期で再確認。 |
| 2026-08-16 | Objective 2.2 | Masking／row access／tag／differential privacy、Trust Center、hierarchical key／Tri-Secret Secure、alert／notification、replication／failover、lineageの公式docsを確認。policy図、本文、章末9問、関連Domain 5問、関連模擬7問へ対応。EditionとPreview／GA条件を本文・source notesへ記録。 |
| 2026-08-16 | Objective 2.3 | Resource Monitor、warehouse credit、ACCOUNT_USAGE／WAREHOUSE_METERING_HISTORYの公式docsを確認。計算例、SQL、章末3問、関連Domain 2問、模擬1問へ対応。Latencyとmetered／billed creditの境界を確認。 |
| 2026-08-17 | Domain 2 初学者レビュー | 図への導線とgrant方向、account identifierの用途別形式、masking／row access policyの実行手順を公式docsで再確認。42問の正解肢へ個別理由を追加し、Domain／模擬問題のdistractorを要件判断型へ修正。 |
| 2026-08-30 | Objective 3.1 | stage種別／privilege、internal stageのencryption、directory table、file format、COPY INTOのcopy option、ON_ERROR／VALIDATION_MODE／VALIDATE()、COPY_HISTORY／LOAD_HISTORYの公式docsを確認。stage図、本文、章末12問、Domain 5問、模擬6問へ対応。 |
| 2026-08-30 | Objective 3.2 | Snowpipe（auto-ingest／REST、課金、14日metadata）、Snowpipe Streaming、Stream（offset・METADATA$列・stale）、Task（RESUME・serverless・task graph上限）、Dynamic Table（TARGET_LAG・REFRESH_MODE）、Openflowの公式docsを確認。取り込み選定図、本文、章末16問、Domain 5問、模擬3問へ対応。OpenflowはGeneral Availabilityとregion可用性を確認のうえ本文へ反映。 |
| 2026-08-30 | Objective 3.3 | driver一覧、Snowflake Python API、Kafka／Spark connector、storage／API／security／notification／external access integration、Git integrationの公式docsを確認。integration図、本文、章末10問、Domain 2問、模擬3問へ対応。 |
| 2026-08-30 | Domain 3 ブラインド評価 | claude-haiku-4-5-20251001で問題品質受験とtextbook単独Coverage監査を実施。いずれも9問中9問正答、textbook根拠十分率100%、曖昧問題0件。初回に曖昧と記録されたM1-Q32の選択肢を差し替えて再実行し、レポートを`evals/`へ保存。 |
| 2026-10-03 | Objective 4.1〜4.4 技術照合 | Query Profile／Insights、spill、pruning、queue、ACCOUNT_USAGE、query attribution、4つの最適化手法、3つのcache、VARIANT／FLATTEN、非構造化file、集約、window／QUALIFYの公式docsを確認。QASの既定値・eligible判定の変更、Edition、費用、viewのlatencyを本文とsource notesへ反映。SQLは公式構文と小規模例の期待結果を静的確認し、Snowflake実環境では未実行。 |
| 2026-10-03 | 公式Study Guideの再取得 | 登録済みPDF URLはHTTP 404。公式COF-C03認定ページの概要は閲覧できたが、Study Guideの配布先と現行の全Topicは再確認できなかった。前回の英語版2026-07-08版の識別情報とTopic scopeを維持。Domain 4は本文・図・問題のレビュー後も`review`に留め、公式範囲の再照合後に完了判断する。日本語版との同等性も未検証のまま。 |
| 2026-10-03 | Domain 4 ブラインド評価 | gpt-6-luna / lowの独立した2エージェントへ会話履歴なしで試験束を渡し、問題品質受験とtextbook単独Coverage監査を実施。両方16問中16問正答（総合・Domain 4とも100%）、本文根拠十分率100%、曖昧問題0件。全回答確定後に採点し、[問題品質レポート](../evals/domain-4-question-quality.json)と[教材限定レポート](../evals/domain-4-baseline.json)を保存。両評価Validatorと構造Validatorが成功。新規52問の正解・必要選択数・全選択肢の解説ID、ローカルリンク116件を確認。集約・window・JSON例の期待値をSQLite相当式とPythonで独立確認したが、Snowflake実環境では未実行。公式範囲の再照合は未完了のため`review`を維持。 |
| 2026-10-03 | PR作成後の公式範囲再調査 | 英語の公式認定ページ（`?pdf_name=SnowProCoreStudyGuideC03`付きも含む）と、公式トップページから辿った日本語の認定ページを再確認。取得できた内容は試験概要とStudy Guide案内のみで、PDF本文と直接リンクは取得できなかった。公開検索でも公式PDFの移転先は確認できず、HTML取得は権限昇格後もネットワーク許可リストで拒否された。利用可能なブラウザーもない。認定ページの確認日と確認範囲を出典台帳へ反映し、Study Guideの全内容照合日は維持。再開には現行の公式PDFまたはアクセス可能な公式配布URLが必要。PR #7のCIは成功しているが、公式範囲との再照合と日本語版の同等性確認は未完了。 |
