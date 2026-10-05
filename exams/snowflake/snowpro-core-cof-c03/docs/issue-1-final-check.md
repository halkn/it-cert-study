# Issue #1 最終チェック対応

2026-10-05。日本語版COF-C03 Study Guide（2026-02-20版）の既存照合記録を正本として、全19章・89 Topic・18図・285問を対象に確認しました。教材、設問、出典とCoverageの対応を修正し、この正本に対する教材全体のrelease_statusをreviewからcompleteへ更新しました。

## 指摘への対応

| ID | 対応 |
|---|---|
| R01 | 無関係な問題のTopic対応を除き、IDE／Snowpark、organization／schema object、scaling policy、micro-partition／clustering、Openflow、Git、Marketplaceを測るDomain演習7問を追加。本文・演習index・Coverage・question registryへ登録。 |
| R02 | COPYの64日判定をファイル更新・成功ロード・table初回ロードの組合せへ修正。LOAD_UNCERTAIN_FILESは利用可能なmetadataで重複を避けながら不明なファイルも対象にする説明へ統一。直接根拠の公式ページを追加。 |
| R03 | Streamのstaleを一律14日とせず、保持設定・延長・共有の例外・STALE_AFTERで判断する説明へ統一。 |
| R04 | Snowpipe auto-ingestのS3 SQS／SNS経路と、Azure／GCPのnotification integrationを区別。 |
| R05 | Gitの認証なし・token・OAuthを区別。Token構成の3objectは該当方式に限定し、設問の前提と図も修正。 |
| R06 | Dynamic TableのTARGET_LAGを鮮度目標として問う設問へ修正し、必達保証との違いを解説。 |
| R07 | Business Critical以上とCMKの選択肢をTri-Secret Secureに限定。 |
| R08 | Policy演習に専用warehouseと両roleへのUSAGEを追加。Stream＋task演習は専用role・object・grant・context・非同期実行の確認・期待結果・費用・cleanupを整備。 |
| R09 | CSV headerは列型とON_ERRORに応じてerrorになる場合もある説明へ修正。 |
| R10 | Domain 4章末26問の選択肢を並べ替え、正解位置の周期を解消。各選択肢の内容、解説、正解の対応を変更前と照合。 |
| R11 | 確認期限を過ぎたactive出典55件について、公式本文の教材で使う主張を再確認し、確認日を更新。Streams／Query Profileの転送先を台帳へ反映。Snowpipeの課金はoverviewの古い説明ではなく専用billing資料を根拠にすることを記録。 |
| R12 | Markdownを画像として指定していた2箇所を図へのリンクに変更。不正anchor3箇所とDomain 5未完成の説明と、READMEに残った古い評価・問題数を修正。 |

再確認では、WorkspacesがLegacy Worksheetsを置換済みであること、storage integrationのUSAGEはstage作成側に必要で既存stageのload／unload利用者へ追加付与は不要であることも反映しました。

独立評価を受け、TARGET_LAGの時間幅指定、lineageのEdition・権限・対応operation・保持期間、変換なしCOPYで検証する入力parseの条件を明確化しました。New data alertのchange tracking前提と、Domain 1で接続失敗／権限不足、Organization／管理用account、固定cluster数／自動増減、保存配置／ORDER BYを区別する説明を本文へ追加し、SQL変数の識別子参照、tag APPLYとAPPLYBUDGET、Snowpipe RESTとStreamingの誤答肢を近い概念の比較へ修正しました。

## 検証

構造Validator、100問模擬セットの再生成照合、git diff --checkが成功。285問の内訳は章末124／Domain58／模擬103で、模擬セットのDomain配分31／20／18／21／10を維持しています。ローカルMarkdownリンク1,152件の不正参照・anchor、Markdown画像指定は0件です。2026-10-05時点の期限切れactive出典は0件です。

gpt-6-luna / lowの独立評価は、問題品質・本文限定の両方で全103問正答、各Domain正答率100%、本文根拠十分率100%、曖昧な問題0件です。現在の本文・問題・Coverageのcontent hashで10レポートを保存し、全Validatorが成功しました。

| Domain | 問題数 | 問題品質 | 本文限定 |
|---|---:|---|---|
| 1 | 31 | [100%](../evals/domain-1-question-quality.json) | [100%・根拠100%](../evals/domain-1-baseline.json) |
| 2 | 20 | [100%](../evals/domain-2-question-quality.json) | [100%・根拠100%](../evals/domain-2-baseline.json) |
| 3 | 18 | [100%](../evals/domain-3-question-quality.json) | [100%・根拠100%](../evals/domain-3-baseline.json) |
| 4 | 21 | [100%](../evals/domain-4-question-quality.json) | [100%・根拠100%](../evals/domain-4-baseline.json) |
| 5 | 13 | [100%](../evals/domain-5-question-quality.json) | [100%・根拠100%](../evals/domain-5-baseline.json) |

問題品質評価の機能比較・暗記寄りの設問などの改善メモはレポートに保持しました。これらの得点は今回のモデルと教材・問題bankに対する結果で、人間受験者の合格率を示すものではありません。

全回答は正解・registryを見せる前に確定させ、親が採点しました。本文限定試験は対象Domainのtextbookだけを根拠とし、一般知識・公式Web・問題解説・既存評価を許可していません。初回の全Domain一括束による拾い漏れや指摘付き回答は完成根拠へ流用せず、修正後に新規エージェントでDomain別の本文監査を実施しました。

## 確認範囲

日本語Study Guideの版・SHA・全範囲は既存の全内容照合記録を参照しました。今回PDF原本を再取得して照合していないため、最新公開版との同一性は未確認です。Snowflake SQLは公式構文・権限・少量例の期待結果を静的に確認し、実アカウントでは未実行です。図は定義・ラベル・接続を確認しましたが、利用可能なrendererがなく、最終表示の視覚検査は未実施です。

最終チェック実施時点では、GitHub Issueの投稿・close、commit・pushは行っていません。
