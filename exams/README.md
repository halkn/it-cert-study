# Exams

資格試験ごとの教材を `exams/<vendor>/<exam>/` に配置します。
各試験パッケージは `exam-config.json`、教材、演習、図、参照資料、管理台帳を持ちます。

新しい試験を追加するときは、既存試験の内容を流用せず、公式Study GuideからObjectiveとTopicを独立して登録してください。
設定は[exam-config template](../shared/templates/exam-config.json)を基に作成し、公式Blueprintに配点や固定Topic一覧がない場合は、対応する任意項目を空または未設定にできます。
