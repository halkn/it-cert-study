# START HERE — 学習を始める方へ

このリポジトリは Snowflake 初学者が COF-C03 の試験範囲を順番に学ぶための教材です。ただし、試験と本教材はデータベース・SQL・クラウドの完全な入門コースではありません。

教材の試験範囲は英語版COF-C03 Study Guideを基準にしています。日本語版Study Guideとの同等性は未検証であり、各Objectiveの`complete`は英語版の試験範囲に対する完成を示します。

## 最初に確認すること

公式 Study Guide は、受験前に Snowflake を6か月程度利用していることと、基本的な ANSI SQL の理解を推奨しています。また、データベースとクラウドの基礎を設問理解の前提としています。

次を説明できない場合は、先に基礎学習が必要です。

- table、view、schema、database の違い
- `SELECT`、`WHERE`、`JOIN`、`GROUP BY` の基本
- authentication と authorization の違い
- cloud storage と compute の基本的な役割

本教材では Snowflake を理解するために必要な範囲で補足しますが、SQL構文やクラウド一般をゼロから網羅しません。

## 現在学習できる範囲

`planned` または `draft` の章は学習完了に使えません。[Coverage Matrix の説明](docs/coverage-matrix.md)で状態を確認してください。

現在完成している章:

- [1.1 アーキテクチャを説明し、利用する](textbook/domain-1/01-architecture.md)
- [1.2 インターフェースとツールを利用する](textbook/domain-1/02-interfaces-and-tools.md)
- [1.3 オブジェクト階層と種類を区別する](textbook/domain-1/03-object-hierarchy.md)
- [1.4 Virtual Warehouseを構成する](textbook/domain-1/04-virtual-warehouses.md)
- [1.5 ストレージ概念を説明する](textbook/domain-1/05-storage-concepts.md)
- [1.6 AI/MLとアプリケーション開発機能を説明する](textbook/domain-1/06-ai-ml-app-development.md)

## 教材完成後の学習順序

1. [Syllabus](docs/syllabus.md)で試験全体と用語を眺める。
2. Domain 1から5まで、各DomainのREADMEに記載された順に章を読む。
3. 各章の確認問題を解き、誤答理由まで説明できるか確認する。
4. Domain演習で複数機能の使い分けを練習する。
5. 模擬試験を解き、弱いトピックをCoverage Matrixから章へ戻って復習する。
6. Referenceで比較表・用語・SQLを直前確認する。

## 最初の章

[Domain 1: Snowflake AI Data Cloud の機能とアーキテクチャ](textbook/domain-1/README.md)から開始します。章が`complete`になるまでは、未完成であることを前提に参照してください。
