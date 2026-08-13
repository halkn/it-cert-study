# IT Certification Study Materials

複数のIT資格試験について、公式試験範囲と公式技術資料を根拠に日本語教材を作るリポジトリです。
各試験は独立したパッケージとして管理し、共通の品質基準、テンプレート、検証入口を共有します。

## 収録している試験

| ベンダー | 試験 | 状態 | 教材 |
|---|---|---|---|
| Snowflake | SnowPro Core COF-C03 | 執筆中 | [SnowPro Core COF-C03](exams/snowflake/snowpro-core-cof-c03/README.md) |

## リポジトリ構造

```text
exams/<vendor>/<exam>/
  exam-config.json
  textbook/
  exercises/
  diagrams/
  reference/
  docs/
shared/
  policies/
  templates/
scripts/
```

試験固有のObjective、出典、問題、進捗は各試験ディレクトリ内で完結させます。
異なる試験間でObjective ID、Domain番号、source IDが同じでも衝突しません。

## 検証

すべての試験を検証します。

```bash
python3 scripts/validate_content.py
```

特定の試験だけを検証する場合は、試験ディレクトリまたは設定ファイルを指定します。

```bash
python3 scripts/validate_content.py --exam exams/snowflake/snowpro-core-cof-c03
```

執筆方法は[CONTRIBUTING.md](CONTRIBUTING.md)、共通基準と雛形は[shared](shared/README.md)を参照してください。
