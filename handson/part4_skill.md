# Part 4: 法人営業の業務フローをスキルにする（25分）

## このパートでやること

「訪問前にこれを確認して、この形にまとめる」という法人営業の業務の型を、
Cortex Agent の **スキル（Agent skill）** として登録します。

スキルは `SKILL.md` という1つのテキストファイルです。中身は次の3つです。

| 項目 | 役割 |
|---|---|
| `name` | スキルの名前 |
| `description` | どんな依頼のときに使うか。Agent はこれを読んで、使うかどうかを判断します |
| 本文（手順） | 使うことになったときに Agent が従う手順と出力フォーマット |

> **混同しやすい点**
> Workspaces の `.snowflake/cortex/skills` に置くスキルは **CoCo 用**（開発者の作業を助けるもの）です。
> このパートで作るのは **Cortex Agent 用**のスキルで、ステージに置いた `SKILL.md` を Agent に登録します。
> CoWork で営業職員が使うのは後者です。

---

## 4-1. 自分たちの業務フローを言葉にする（5分）

次の問いに、自社の実際の業務で答えてみてください（メモで構いません）。

- 訪問の前日に、営業職員は何を確認していますか？
- その情報はどのシステムにありますか？
- 上司に報告するとき、どんな項目の順番でまとめますか？
- 言ってはいけないこと、必ず添えることはありますか？

---

## 4-2. CoCo と一緒に SKILL.md を書く（10分）

Workspaces の `snowlife-corporate-sales-handson` で CoCo を開き、次のプロンプトを送ります。
4-1 のメモがあれば、プロンプトの手順部分を自社の内容に書き換えてください。

```
Cortex Agent 用のスキルファイルを作ってください。
ファイル: my-skills/pre-visit-briefing/SKILL.md
name: pre-visit-briefing
description: 法人営業職員が顧客企業を訪問する前の準備資料（訪問前ブリーフィング）を作る。
  「〇〇社の訪問準備をして」「〇〇社のブリーフィングを作って」といった依頼で使う。
手順:
  1. 面談メモ検索ツール（meeting_notes_search）で対象企業の直近の面談を3件確認する
  2. 営業分析ツール（sales_analytics）で進行中の商談・有効な既契約・最終訪問日を確認する
  3. 営業分析ツールで直近2年度の売上高と、直近3か月の求人件数の前年比を確認する
  4. 商品資料検索ツール（product_docs_search）で、課題に合う商品の根拠を探す
出力フォーマット: 直近の面談サマリー / 未対応の宿題 / 商談・既契約 / 企業の変化 / 推奨する提案と根拠 / 想定Q&A 3つ
注意: 金額は円で書く。データにないことは書かない。「必ず」「確実に」などの断定表現は使わない。
```

見本は [answers/skills/pre-visit-briefing/SKILL.md](../answers/skills/pre-visit-briefing/SKILL.md) にあります。

---

## 4-3. ステージに置いて Agent に登録する（5分）

### (1) SKILL.md をステージにアップロードする

1. 作った `SKILL.md` をダウンロードする（ワークスペースのファイルを右クリック » Download）
2. **Catalog » Database Explorer** で `SNOWLIFE_HANDSON_DB` » `AI` » **Stages** » `SKILL_STAGE` を開く
3. **+ Files** を押し、パスに `skills/pre-visit-briefing/` を指定して `SKILL.md` をアップロードする

> **注意:** `SKILL.md` はスキルフォルダの直下に置く必要があります（サブフォルダは探索されません）。
> 結果が `skills/pre-visit-briefing/SKILL.md` になっていることを確認してください。

```sql
LS @SNOWLIFE_HANDSON_DB.AI.SKILL_STAGE/ PATTERN = '.*SKILL\.md';
```

`proposal-prep` と `compliance-check` は setup.sql で配置済みです。

### (2) Agent に登録する

1. **AI & ML » Agents** で `SALES_AGENT`（B: 意味づけあり）を開き、**Edit** を押す
2. **Skills** タブで **Add Skill** を押し、ソースに **Stage** を選ぶ
3. ステージ `SNOWLIFE_HANDSON_DB.AI.SKILL_STAGE`、パス `skills/pre-visit-briefing` を指定して追加する
4. 同じ手順で `skills/proposal-prep` と `skills/compliance-check` も追加し、**Save** を押す

登録できたか確認します。出力の仕様に `skills` が3件含まれていれば成功です。

```sql
DESCRIBE AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT;
```

> **間に合わなかった場合:** `answers/part4_skill.sql` を実行すると、見本の SKILL.md の配置と3スキルの登録をまとめて行います。
> この SQL は Agent の設定全体を置き換えるため、画面で追加したスキルの設定も上書きされます（同じ3スキルが登録された状態になります）。

---

## 4-4. CoWork で使ってみる（5分）

[ai.snowflake.com](https://ai.snowflake.com) を開き、Agent に **法人営業アシスタント（B: 意味づけあり）** を選んで次を送ります。

```
KDDIの訪問準備をして
```

```
パナソニック向けに、DC移行の提案の骨子をまとめて
```

```
この文面に問題がないか確認して：「GLTDに加入すれば、確実に税負担が軽減され、従業員の離職もなくなります」
```

確認するポイント:

- 回答の思考ステップに、スキルが使われたことが表示されているか
- 出力が SKILL.md に書いたフォーマットの順番になっているか
- 金額が円で、断定表現が使われていないか

> **スキルが使われないとき**
> チャット入力欄の **+** ボタンからスキルを明示的に選べます。
> それでも使われない場合は、`description` に「どんな依頼で使うか」の例文を増やしてください。
> Agent は `description` を見て使うかどうかを判断します。

---

次は [Part 5: 営業職員として CoWork を使う](part5_cowork.md) です。
