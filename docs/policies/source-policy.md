# Source Policy

## 利用できる根拠

優先順位は次のとおりです。

1. 試験範囲: Snowflake 公式 Certification Page / COF-C03 Study Guide
2. 技術仕様・概念・SQL: Snowflake Documentation
3. 変更されうる状態: Snowflake Release Notes / Behavior Change / 公式 announcement

非公式ブログ、Q&A、動画、試験対策サイト、Exam Dump、LLM の内部知識は技術的事実の根拠にしません。探索のきっかけに使った場合も、教材に反映する前に公式資料で確認します。

## 出典台帳

参照資料は `docs/sources.json` に一意な ID で登録します。

- URL は対象を直接説明する公式ページにする。
- `checked_on` に実際に内容を確認した日を入れる。
- Preview、Edition、region、cloud など適用条件を `notes` に残す。
- 変更されやすい資料は `review_interval_days` を短くする。
- 廃止・移動を見つけたら削除せず `status` と代替先を更新する。

リンクを貼っただけでは検証済みになりません。章の主張と出典の対応をレビューします。

## 本文の自立性

公式 URL は本文の代替ではありません。各トピックは外部ページを開かなくても、試験に必要な What / How / When-Why / Compare を理解できる説明を含めます。リンクは根拠確認と追加学習に使います。

## 引用と著作権

Study Guide、公式文書、公式図をリポジトリへ複製しません。短い用語や目標 ID を除き、内容は自分の言葉で説明します。図は公式情報と照合した自作図にします。

## 問題の出典

`answer_source_ids` は正解を直接裏付ける資料、`further_reading_source_ids` は周辺知識を広げる資料です。両者を混同しません。
