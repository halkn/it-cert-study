---
name: evaluate-certification-domain
description: IT認定試験教材の指定Domainについて、正解を隠した問題品質試験とtextbookだけを許可する合格可能性監査を、利用可能な最低性能モデルの独立サブエージェントで実施し、再現可能な評価レポートとして保存・検証する。新しいDomainの教材と問題を追加した後、教材だけで初学者が合格可能か確認するとき、模擬問題の曖昧さ・難易度・Coverageを検査するとき、または内容変更後に過去の評価が有効か再確認するときに使用する。
---

# 認定試験Domainをモデル評価する

指定Domainを、問題を解く能力と教材から根拠を導く能力に分けて評価する。自己採点や会話履歴による答えの漏洩を避け、結果を後から再検証できる状態で残す。

## 1. 評価条件を読む

作業前に次をすべて読む。

- `shared/evals/evaluation-policy.md`
- `shared/policies/content-quality.md`
- 対象試験の`exam-config.json`
- 対象試験の`docs/coverage-matrix.json`
- 保存済み評価があれば対象試験の`evals/*.json`

対象試験ディレクトリとDomain番号を確定する。指定がなければ、変更された教材とCoverage Matrixから安全に特定できる場合だけ推定する。

## 2. 前提検証を通す

次を実行し、失敗があれば評価より先に教材を修正する。

```bash
git diff --check
python3 scripts/validate_content.py --exam <対象試験ディレクトリ>
```

対象DomainのObjective、Topic、textbook、章末問題、Domain演習、模擬問題が揃っていない場合は合格評価を出さない。

## 3. 独立した試験束を生成する

問題品質試験と教材限定試験を別々に生成する。

```bash
python3 scripts/build_blind_exam.py \
  --exam <対象試験ディレクトリ> \
  --domains <Domain番号...> \
  --mode question-quality \
  --output <一時ファイル>

python3 scripts/build_blind_exam.py \
  --exam <対象試験ディレクトリ> \
  --domains <Domain番号...> \
  --mode textbook-only \
  --output <一時ファイル>
```

生成物に`## 正解`以降が含まれないことを確認する。一時ファイルは評価レポートへ含めず、評価完了後に削除する。

## 4. 最低性能モデルで二つの評価を実施する

利用可能なモデル一覧から最も性能が低いモデルを選び、推論設定は`low`にする。モデルを固定できない環境では、実際に使用できた中で最も低いモデル名と制約をレポートへ記録する。

会話履歴を渡さない独立サブエージェントを二つ起動する。

1. `question-quality`の試験束だけを渡し、全問を解答させる。教材、question registry、正解、既存評価レポートを見せない。
2. `textbook-only`の試験束だけを渡し、全問の解答、根拠となるtextbook見出し、各誤答を排除できるかを回答させる。リポジトリ探索、Web、外部知識、既存評価レポートを禁止する。

サブエージェントには完成レポートや期待正答を渡さない。評価中に同じエージェントへ修正後の再試験を継続させず、再試験は新しい独立エージェントで行う。

## 5. 結果を保存する

`shared/templates/domain-evaluation-report.json`を構造の基準にし、対象試験の`evals/`へ次の二つを保存する。

- `domain-<範囲>-question-quality.json`
- `domain-<範囲>-baseline.json`

モデル名、推論設定、全問題の選択肢、正誤、Domain別得点、曖昧性、教材見出し、誤答排除可否、閾値、Git revision、content hashを省略しない。判定基準は`shared/evals/evaluation-policy.md`から緩和しない。

基準未達、曖昧な設問、教材根拠不足が一つでもあれば、対応する教材または問題を修正する。修正後は別の新規サブエージェントで両評価を再実施する。

## 6. 保存結果を検証する

各レポートを検証する。

```bash
python3 scripts/validate_domain_evaluation.py \
  --exam <対象試験ディレクトリ> \
  --report <評価レポート.json>
```

Validatorが問題の欠落、採点不整合、存在しない教材見出し、対象外資料、古いcontent hashを拒否することを前提にする。対象教材や問題を後から変更した場合は、保存済み合格を流用せず再評価する。

## 7. 完了を報告する

次を簡潔に報告する。

- 使用モデルと推論設定
- 問題数、総合得点、Domain別得点、教材根拠率、曖昧な問題数
- 合否と、未達なら修正が必要なObjective
- 保存した二つのレポート
- 実行したValidatorの結果

「textbookだけで合格できる」と断定するのは、教材限定試験が閾値を満たし、全根拠が対象textbook内にあり、保存レポートの検証が成功した場合だけにする。
