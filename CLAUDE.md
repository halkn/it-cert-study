# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このリポジトリの性質

コードではなく、IT 認定試験の日本語教材を「試験範囲・公式出典・図・演習の追跡可能性」を保った状態で管理するリポジトリ。文章を書くこと自体より、registry（JSON 台帳）と本文・問題ファイルの参照整合が保たれることが成果物の条件になる。

## コマンド

すべてリポジトリルートで実行する（各スクリプトは自身の親ディレクトリを ROOT として解決する）。

```bash
# 全試験パッケージの構造検証
python3 scripts/validate_content.py

# 単一試験のみ検証（試験ディレクトリ or exam-config.json を指定）
python3 scripts/validate_content.py --exam exams/snowflake/snowpro-core-cof-c03

# 正解を除去したブラインド試験束を生成（mode: question-quality / textbook-only）
python3 scripts/build_blind_exam.py --exam <試験ディレクトリ> --domains 2 --mode textbook-only --output <一時ファイル>

# 保存済み評価レポートの検証（閾値・content hash の失効判定）
python3 scripts/validate_domain_evaluation.py --exam <試験ディレクトリ> --report <評価レポート.json>
```

テストフレームワークはない。`validate_content.py` が唯一の構造テストであり、変更後は必ず `git diff --check` と併せて実行する。CI（`.github/workflows/content-validation.yml`）も PR と main への push で全試験の `validate_content.py` だけを実行する。

## 構造

```text
exams/<vendor>/<exam>/     試験パッケージ（自己完結。試験間で ID が衝突しない）
  exam-config.json         registry の場所、期待 objective_ids / domain_weights / topic_count /
                           topic_scope_sha256、official_hosts、release 条件
  docs/coverage-matrix.json  Source of Truth: objective → 章・anchor・出典・図・問題
  docs/sources.json          公式資料と checked_on / status
  docs/diagrams.json         自作図の registry
  docs/questions.json        問題 registry（layer・正解・required_selections・出典）
  textbook/domain-<n>/       章本文（objective ごとに 1 ファイル）
  exercises/{chapter,domain,mock}/  問題本文（1 問 1 ファイル。ファイル名は question id の小文字）
  diagrams/domain-<n>/       自作図（SVG または Mermaid の .md）
  reference/                 比較表・用語集・SQL リファレンス
  evals/                     Domain 評価レポート（保存必須）
shared/policies/           出典・品質・図の共通基準
shared/templates/          章・問題・図・評価レポートの雛形（validate_content.py が必須見出しを検査）
shared/evals/              評価ポリシーと評価用プロンプト
scripts/                   検証・ブラインド試験生成
.agents/skills/            執筆・評価の手順 Skill（$write-certification-chapter / $evaluate-certification-domain）
```

## 中心にある不変条件

`validate_content.py` が強制するもの。ここを理解せずに JSON を編集すると必ず落ちる。

- **双方向参照**: topic が参照する question は `layer` が一致し、その question 側の `objective_ids` にも当該 objective を含む必要がある。図も同様に `objective_ids` で戻り参照する。
- **章 anchor**: topic の `chapter_anchor` は章本文に `id="<anchor>"` として存在しなければならない。
- **章ヘッダ**: 章本文は `# <objective_id> ` と `> Status: <status>` を含み、Coverage Matrix の status と一致させる。
- **問題本文の必須見出し**: status が `review`/`complete` の問題は `問題` / `選択肢` / `正解` / `正解理由` / `各誤答が誤りである理由` / `周辺知識` / `解答根拠` / `追加学習` の各節に本文が必要。`## 正解` は `build_blind_exam.py` の分割マーカーでもあるため見出し名を変えない。
- **出典**: `sources.json` の URL は `exam-config.json` の `official_hosts` に含まれる HTTPS ホストのみ。`answer_source_ids`（正解の直接根拠）と `further_reading_source_ids`（周辺知識）は別物として扱う。
- **試験範囲の凍結**: topic の id と scope は `topic_scope_sha256` でハッシュ固定されている。公式 Study Guide の再確認なしに topic を足す・scope を書き換えると検証が落ちる。これは意図的なガードなので、ハッシュを合わせるために scope を後追いで書き換えない。

## 検証が拾わないもの

- registry JSON（`coverage-matrix.json` / `questions.json` / `sources.json` / `diagrams.json`）は 1 レコード 1 行の圧縮形式。整形ツールで pretty-print すると全行が diff になるため、既存の行フォーマットに合わせて編集する。
- status を変えたら `textbook/domain-<n>/README.md`・`START_HERE.md`・`docs/coverage-matrix.md`・`docs/verification-log.md` を手で追随させる。`validate_content.py` はこれらの記述を検査しない。

## status の扱い

`planned` → `draft` → `review` → `complete` を順に進める。`complete` へ直接飛ばさない。

objective を `complete` にするには、章・出典・必要な図・章末問題・Domain 演習・模擬問題がすべて揃い、topic もすべて `complete` である必要がある。検証が通ることは `complete` の十分条件ではなく、`shared/policies/content-quality.md` の全条件を満たしてから状態を上げる。

Domain 全体を `complete` にする前に、`shared/evals/evaluation-policy.md` に従って最軽量モデルによるブラインド評価（問題品質 / textbook 単独 Coverage）を実施し、レポートを `evals/` へ保存して `validate_domain_evaluation.py` を通す。合格閾値は総合 80% / Domain 別 70% / textbook 根拠十分率 90% / 曖昧問題 0 件。textbook・模擬問題・coverage-matrix.json を変更すると content hash が失効し、再評価が必要になる。

## 執筆時の判断基準

- 新しい objective の実装・既存章の推敲・レビューは `write-certification-chapter`、Domain 評価は `evaluate-certification-domain` の手順に従う。skill として読み込まれていない場合は実体の `.agents/skills/<name>/SKILL.md` を直接開く（`.claude/skills/` にあるのは `.agents/skills/` への symlink で、実体は Codex など他ツールと共有している）。
- 技術的主張の根拠は認定団体・技術提供元の公式資料のみ。非公式記事・LLM の記憶・Exam Dump は使わない。URL を貼っただけでは検証済みにしない。
- 公式 Study Guide や公式図を転載しない。説明は自分の言葉、図は自作。
- 本文は外部ページを開かずに What / How / When-Why / Compare を理解できる自立性を持たせる。ただし objective 外の機能で章を膨らませない。
- 文章設計の詳細基準は `shared/policies/content-quality.md` の「初学者向けの文章設計」にある。用語名を先に置いて暗記させない、結果だけでなく機構を書く、置いた問いは同じ章で回収する。
