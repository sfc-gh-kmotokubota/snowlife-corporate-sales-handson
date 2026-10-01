# Part 3: Cortex Agent を作って精度を比べる（20分）

## このパートでやること

ツールも指示文も同じ2つの Agent を作り、同じ質問を投げて回答を比べます。
違いは Cortex Analyst ツールが参照するセマンティックビューだけです。

| Agent | 表示名 | セマンティックビュー |
|---|---|---|
| A: `AI.SALES_AGENT_BASIC` | 法人営業アシスタント（A: 意味づけなし） | `AI.SV_SALES_MINIMAL`（テーブル・主キー・リレーションのみ。setup.sql で作成済み） |
| B: `AI.SALES_AGENT` | 法人営業アシスタント（B: 意味づけあり） | `AI.SV_SALES_ANALYTICS`（Part 2 で作成） |

---

## 3-1. Agent を作る（5分）

まず Part 2 のセマンティックビューができているか確認します。

```sql
SHOW SEMANTIC VIEWS IN SCHEMA SNOWLIFE_HANDSON_DB.AI;
```

`SV_SALES_ANALYTICS` が一覧になければ、先に `answers/part2_semantic_view.sql` を実行してください。

続けて `answers/part3_agents.sql` を Workspaces で開き、Run All で実行してください。
2つの Agent が作成され、CoWork に表示されるよう CoWork オブジェクトに追加されます。

> **Snowsight の画面で作りたい場合**
> **AI & ML » Agents » Create agent** から作成し、**Tools** で Cortex Analyst（セマンティックビュー）と
> Cortex Search（`AI.MEETING_NOTE_SEARCH`、`AI.PRODUCT_DOC_SEARCH`）を追加します。
> ただし時間の都合上、ハンズオンでは SQL で作成した Agent を使って比較を進めます。
> 作成後、画面で Agent を開いて、ツールと指示文がどう設定されているかを確認してください。

---

## 3-2. 同じ質問を2つの Agent に投げる（10分）

1. [ai.snowflake.com](https://ai.snowflake.com) を**2つのタブ**で開く
2. 片方で A、もう片方で B を選ぶ
3. 次の4問を両方に投げ、[scoresheet.md](scoresheet.md) に ○ / △ / × を付ける

```
進行中の商談のうち、見込みランクがAの商談の見込み金額合計を支社別に円で教えて
```

```
2026年度上期に受注した商談の件数と見込み金額の合計（円）を教えて
```

```
GLTDの進行中の商談の件数と見込み金額の合計（円）を教えて
```

```
2025年度の売上高が前年度より増えていて、進行中の商談がある取引先を教えて
```

正解は [eval_questions.md](eval_questions.md) にあります（Q1・Q2・Q8・Q9）。
時間があれば残りの6問も試してください。

> **回答の「思考ステップ」を開いてください**
> 生成された SQL を見ると、A は `AMT_EST` をそのまま合計し、B は `AMT_EST * 1000` を使っていることが分かります。
> A の回答は「数字としては自然に見える」ため、誤りに気づきにくいのがポイントです。

---

## 3-3. 間違えた回答を Semantic Studio で直す（5分）

Agent の誤答は、Semantic Studio の CoCo に調べさせて直せます。本番運用でも、この流れで精度を上げていきます。

1. **AI & ML » Agents** で `SALES_AGENT_BASIC`（A）を開き、**Monitoring** タブを開く
2. 3-2 で A が間違えた質問（例: Q2）のリクエストを選び、**リクエスト ID** をコピーする
3. Workspaces で、既存のセマンティックビュー `SV_SALES_MINIMAL` を開く（新規作成はしません）。
   CoCo に「SNOWLIFE_HANDSON_DB.AI.SV_SALES_MINIMAL を開いて」と頼むと開いてくれます
4. CoCo に次のように送る

```
このリクエストの回答が間違っていました。リクエスト ID: <コピーしたID>
正しい見込み金額の合計は 427,182,000円 です。原因と修正案を教えてください。
```

5. CoCo が原因（例:「AMT_EST が千円単位であることが定義されていない」）と修正の差分を示すので、内容を確認する

> **注意:** ここでは修正案を確認するところまでで止めてください。
> Deploy すると `SV_SALES_MINIMAL` が変わり、A と B の比較ができなくなります。

---

## 時間があれば: Evaluations タブで一括評価する（講師デモ）

Agent の **Evaluations** タブでは、質問と正解のセットを用意して、Agent の回答をまとめて採点できます（answer_correctness などの指標）。
Agent の設定を変えるたびに同じセットで評価し直すと、精度が上がったか下がったかを数値で追えます。

---

次は [Part 4: 法人営業の業務フローをスキルにする](part4_skill.md) です。
