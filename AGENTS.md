# AGENTS.md（講師・CoCo 向け）

このリポジトリは、生命保険の法人営業企画部向け2時間ハンズオンの教材です。
受講者向けの手順は README.md と handson/ にあります。このファイルは講師が事前準備・検証をするときの手順です。

## 事前検証の手順

講師環境（ACCOUNTADMIN が使えるアカウント）で次を順に実行し、すべてエラーなく終わることを確認する。

1. `setup.sql`（約3〜5分）
2. `answers/part2_semantic_view.sql`
3. `answers/part3_agents.sql`
4. `python3 tools/run_ab_eval.py <snow接続名>` で評価10問を A / B に投げる（約20分）。結果は `AI.EVAL_RESULTS` に入る
5. `answers/eval_ground_truth.sql` の結果と照合し、`handson/eval_questions.md` のリハーサル結果を更新する
6. `answers/part4_skill.sql`
7. 営業職員ロールでの確認（下記）
8. `cleanup.sql`

### 営業職員ロールで Agent を確認するとき

SQL から `SNOWFLAKE.CORTEX.DATA_AGENT_RUN` を呼ぶ場合、Agent は**セッションのロール**で動く。
`USE ROLE SNOWLIFE_SALES_REP_T01; USE SECONDARY ROLES NONE;` をしてから呼ぶこと。
CoWork（ai.snowflake.com）から確認する場合は、ユーザーのデフォルトロールが使われる（handson/part5_cowork.md の手順）。

## データを作り直すとき

```bash
python3 tools/generate_data.py   # data/csv と data/docs を再生成（乱数シード固定）
python3 tools/build_answers.py   # answers/part2_semantic_view.yaml から .sql を再生成
```

データを変えたら、`answers/eval_ground_truth.sql` を実行して `handson/eval_questions.md` の正解欄を更新すること。

## 当日の進行メモ（講師用）

受講者は README の「ハンズオンの進め方」を見ながら進めます。講師は次を補足してください。

- 事前準備: 受講者アカウントにログインできるか確認する。画面共有で A / B の回答を並べて見せられるようにする（Q1・Q2・Q8 が差の出やすい質問）。
- Part 0: 今日確かめる4点と、ご提案アーキテクチャとの対応を説明する。
- Part 2: 「たたき台は AI、業務の言葉は人が入れる」を強調する。0:45 で未 Deploy の人には answers を案内する。
- Part 3: 「A でも推測で当たる質問はある。問題はもっともらしい誤答が混ざること」を伝える（eval_questions.md の講師メモ）。
- 休憩: 講師画面に「KDDIの訪問準備をして」の回答を出しておく。
- Part 4: 4-1 で受講者1〜2人に実際の訪問準備の流れを聞き、SKILL.md に反映する。1:38 で未登録の人には answers を案内する。
- Part 5: 本番は営業職員ごとのユーザーと SSO で運用すること、Cortex Search には行アクセスポリシーが効かないことを伝える。最後にデフォルトロールを全員が戻したか確認する。

## 作成時に分かった注意点

- セマンティックビューの DDL は `<論理テーブル>.<名前> AS <式>` の順。逆に書くと `invalid identifier` になる。
- 検証済みクエリ（VQR）の SQL は、物理テーブルではなく論理テーブル名（`__OPPORTUNITIES` のように `__` を付ける）と論理列名で書く。
- 行アクセスポリシーの引数名を、ポリシー内のサブクエリの列名と同じにしない（列名として解決されてしまう）。
- Cortex Search は所有者の権限で検索するため、元テーブルの行アクセスポリシーは検索結果に効かない。Part 5 で受講者にも説明している。
- `CREATE AGENT` 直後は `VERSION$1` がコミットされる。`ALTER AGENT ... MODIFY LIVE VERSION` で追加したスキルは、検証環境では CoWork・`DATA_AGENT_RUN` の両方で使われることを確認済み。
