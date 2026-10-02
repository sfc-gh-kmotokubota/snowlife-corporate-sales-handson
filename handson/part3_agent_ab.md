# Part 3: Cortex Agent を作って精度を比べる（20分）

> **このページの手順を上から順にコピペして進めれば完了します。**
> 「SQL」の枠は Workspaces の SQL ファイルに、「CoWork に送る」の枠は ai.snowflake.com のチャット欄に、
> 「入力する値」の表は Snowsight の画面の各欄に、そのままコピーして貼り付けてください。

## このパートでやること

ツールも指示文も同じ2つの Agent を作り、同じ質問を投げて回答を比べます。
違いは Cortex Analyst ツールが参照するセマンティックビューだけです。

| Agent | 表示名 | セマンティックビュー |
|---|---|---|
| A: `AI.SALES_AGENT_BASIC` | 法人営業アシスタント（A: 意味づけなし） | `AI.SV_SALES_MINIMAL`（テーブル・主キー・リレーションのみ。setup.sql で作成済み） |
| B: `AI.SALES_AGENT` | 法人営業アシスタント（B: 意味づけあり） | `AI.SV_SALES_ANALYTICS`（Part 2 で作成） |

---

## 3-0. 事前確認（1分）

**SQL**

```sql
SHOW SEMANTIC VIEWS IN SCHEMA SNOWLIFE_HANDSON_DB.AI;
```

`SV_SALES_MINIMAL` と `SV_SALES_ANALYTICS` の2行が出れば OK です。
`SV_SALES_ANALYTICS` がなければ、先に `answers/part2_semantic_view.sql` を開いて **Run All** してください。

---

## 3-1. Agent を作る（5〜10分）

作り方を **どちらか1つ** 選んでください。どちらでも、できあがる Agent は同じです。

| | 方法1: SQL で作る（おすすめ・2分） | 方法2: 画面で Agent B を作る（10分） |
|---|---|---|
| 向いている人 | 比較を早く始めたい | Agent の設定項目を自分の手で確かめたい |

### 方法1: SQL で作る

1. Workspaces で `answers/part3_agents.sql` を開く
2. **Run All** を押す
3. 最後の結果（`SHOW AGENTS`）に `SALES_AGENT_BASIC` と `SALES_AGENT` の2行が出れば完了 → **3-2 へ**

### 方法2: 画面で Agent B を作る

#### (1) Agent を作成する

1. ナビゲーションメニューの **AI & ML » Agents** を開き、**Create agent** を押す
2. 次の値を入れて **Create agent** を押す

| 項目 | 入力する値 |
|---|---|
| データベース / スキーマ（選択欄がある場合） | `SNOWLIFE_HANDSON_DB` / `AI` |
| Agent object name | `SALES_AGENT` |
| Display name | `法人営業アシスタント（B: 意味づけあり）` |

#### (2) 説明を入れる

作成した Agent を開いて **Edit** を押し、**Description** に貼り付けます。

```
スノー生命 法人営業アシスタント
```

#### (3) ツールを3つ追加する

**Tools** を開き、次の3つを追加します。

**ツール1: Cortex Analyst** → **Cortex Analyst** の **+ Add**

| 項目 | 入力する値 |
|---|---|
| Name | `sales_analytics` |
| Semantic view | `SNOWLIFE_HANDSON_DB.AI.SV_SALES_ANALYTICS` を選ぶ |
| Warehouse | `SNOWLIFE_HANDSON_WH` を選ぶ |
| Query timeout (seconds) | `60` |
| Description | 下の枠をコピー |

```
法人営業の取引先・商談・活動履歴・既契約・企業財務・求人件数を SQL で集計するツール。件数・金額・一覧・ランキングの質問に使う。
```

**ツール2: 面談メモ検索** → **Cortex Search Services** の **+ Add**

| 項目 | 入力する値 |
|---|---|
| Name | `meeting_notes_search` |
| Description | 下の枠をコピー |
| Search service | `SNOWLIFE_HANDSON_DB.AI.MEETING_NOTE_SEARCH` を選ぶ |
| ID column | `NOTE_ID` |
| Title column | `ACCT_NM` |
| Source stage / Relative path column | 空欄のまま |

```
営業職員が記録した面談メモを検索するツール。先方が何を話したか、課題・関心事・次回アクションを調べるときに使う。
```

**ツール3: 商品資料検索** → **Cortex Search Services** の **+ Add**

| 項目 | 入力する値 |
|---|---|
| Name | `product_docs_search` |
| Description | 下の枠をコピー |
| Search service | `SNOWLIFE_HANDSON_DB.AI.PRODUCT_DOC_SEARCH` を選ぶ |
| ID column | `RELATIVE_PATH` |
| Title column | `RELATIVE_PATH` |
| Source stage | `@SNOWLIFE_HANDSON_DB.RAW.DOC_STAGE` |
| Relative path column | `RELATIVE_PATH` |

```
スノー生命の商品パンフレット・約款を検索するツール。商品の特長・引受条件・約款の規定を調べるときに使う。
```

> Source stage を入れておくと、CoWork の回答の引用から PDF をその場で開けます。

#### (4) 指示文を入れる

**Orchestration** を開き、次の値を入れます。

| 項目 | 入力する値 |
|---|---|
| Orchestration model | `auto` |
| Planning instructions | 下の1つ目の枠をコピー |
| Response instruction | 下の2つ目の枠をコピー |

```
数値・件数・一覧の質問は sales_analytics を使ってください。面談の内容は meeting_notes_search、商品の内容は product_docs_search を使ってください。
```

```
日本語で、結論から簡潔に答えてください。数値には単位を付けてください。
```

#### (5) 保存する

右上の **Save** を押します。

#### (6) 比較用の Agent A を作り、2つとも CoWork に表示する

Agent A は B とセマンティックビューだけが違うので、SQL でまとめて作ります。次をそのまま実行してください。

**SQL**

```sql
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE SNOWLIFE_HANDSON_WH;

CREATE OR REPLACE AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT_BASIC
    COMMENT = '比較用。意味づけのない最小セマンティックビューを使う法人営業 Agent'
    PROFILE = '{"display_name": "法人営業アシスタント（A: 意味づけなし）"}'
    FROM SPECIFICATION
$$
models:
  orchestration: auto
instructions:
  response: "日本語で、結論から簡潔に答えてください。数値には単位を付けてください。"
  orchestration: "数値・件数・一覧の質問は sales_analytics を使ってください。面談の内容は meeting_notes_search、商品の内容は product_docs_search を使ってください。"
tools:
  - tool_spec:
      type: "cortex_analyst_text_to_sql"
      name: "sales_analytics"
      description: "法人営業の取引先・商談・活動履歴・既契約・企業財務・求人件数を SQL で集計するツール。件数・金額・一覧・ランキングの質問に使う。"
  - tool_spec:
      type: "cortex_search"
      name: "meeting_notes_search"
      description: "営業職員が記録した面談メモを検索するツール。先方が何を話したか、課題・関心事・次回アクションを調べるときに使う。"
  - tool_spec:
      type: "cortex_search"
      name: "product_docs_search"
      description: "スノー生命の商品パンフレット・約款を検索するツール。商品の特長・引受条件・約款の規定を調べるときに使う。"
tool_resources:
  sales_analytics:
    semantic_view: "SNOWLIFE_HANDSON_DB.AI.SV_SALES_MINIMAL"
    execution_environment:
      type: "warehouse"
      warehouse: "SNOWLIFE_HANDSON_WH"
  meeting_notes_search:
    search_service: "SNOWLIFE_HANDSON_DB.AI.MEETING_NOTE_SEARCH"
    max_results: 5
    id_column: "NOTE_ID"
    title_column: "ACCT_NM"
  product_docs_search:
    search_service: "SNOWLIFE_HANDSON_DB.AI.PRODUCT_DOC_SEARCH"
    max_results: 5
    id_column: "RELATIVE_PATH"
    title_column: "RELATIVE_PATH"
    stage_path: "@SNOWLIFE_HANDSON_DB.RAW.DOC_STAGE"
    relative_path_column: "RELATIVE_PATH"
$$;

-- 2つの Agent を CoWork に表示する（追加済みでもエラーになりません）
EXECUTE IMMEDIATE $$
BEGIN
    ALTER SNOWFLAKE INTELLIGENCE SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT ADD AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT_BASIC;
    RETURN 'A を CoWork に追加しました';
EXCEPTION WHEN OTHER THEN RETURN 'A は追加済みです';
END;
$$;

EXECUTE IMMEDIATE $$
BEGIN
    ALTER SNOWFLAKE INTELLIGENCE SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT ADD AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT;
    RETURN 'B を CoWork に追加しました';
EXCEPTION WHEN OTHER THEN RETURN 'B は追加済みです';
END;
$$;

GRANT USAGE ON AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT_BASIC TO ROLE SNOWLIFE_SALES_REP_T01;
GRANT USAGE ON AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT       TO ROLE SNOWLIFE_SALES_REP_T01;

SHOW AGENTS IN SCHEMA SNOWLIFE_HANDSON_DB.AI;
```

最後の結果に `SALES_AGENT_BASIC` と `SALES_AGENT` の2行が出れば完了です。

> **画面での作成がうまくいかなかったら:** 方法1（`answers/part3_agents.sql` の Run All）に切り替えてください。
> 画面で作った `SALES_AGENT` は同じ設定で作り直されるので、そのまま先に進めます。

---

## 3-2. 同じ質問を2つの Agent に投げる（10分）

1. [ai.snowflake.com](https://ai.snowflake.com) を**2つのタブ**で開く
2. 片方のタブで **法人営業アシスタント（A: 意味づけなし）**、もう片方で **法人営業アシスタント（B: 意味づけあり）** を選ぶ
   （一覧に出ないときはタブを再読み込みしてください）
3. 次の4問を両方に投げ、[scoresheet.md](scoresheet.md) に ○ / △ / × を付ける

**CoWork に送る**

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

正解は [eval_questions.md](eval_questions.md) の Q1・Q2・Q8・Q9 です。
時間があれば残りの6問も試してください。

> **回答の「思考ステップ」を開いてください**
> 生成された SQL を見ると、A は `AMT_EST` をそのまま合計し、B は `AMT_EST * 1000` を使っていることが分かります。
> A の回答は「数字としては自然に見える」ため、誤りに気づきにくいのがポイントです。

---

## 3-3. 間違えた回答を Semantic Studio で直す（5分）

Agent の誤答は、Semantic Studio の CoCo に調べさせて直せます。本番運用でも、この流れで精度を上げていきます。

1. **AI & ML » Agents** で `SALES_AGENT_BASIC`（A）を開き、**Monitoring** タブを開く
2. 3-2 で A が間違えた質問（例: 2問目の「2026年度上期に受注した…」）のリクエストを選び、**リクエスト ID** をコピーする
3. **Projects » Workspaces** を開き、CoCo パネルに次を送る（既存のセマンティックビューを開きます。新規作成はしません）

**CoCo に送る**

```
SNOWLIFE_HANDSON_DB.AI.SV_SALES_MINIMAL を Semantic Studio で開いて
```

4. 開いたら、同じ CoCo の会話に次を送る（`<コピーしたID>` を 2 でコピーした ID に置き換える）

**CoCo に送る**

```
このリクエストの回答が間違っていました。リクエスト ID: <コピーしたID>
正しい見込み金額の合計は 427,182,000円 です。原因と修正案を教えてください。
```

5. CoCo が原因（例:「AMT_EST が千円単位であることが定義されていない」）と修正の差分を示すので、内容を確認する

> **注意:** ここでは修正案を確認するところまでで止めてください。**Deploy は押さないでください。**
> Deploy すると `SV_SALES_MINIMAL` が変わり、A と B の比較ができなくなります。

---

## 時間があれば: Evaluations タブで一括評価する（講師デモ）

Agent の **Evaluations** タブでは、質問と正解のセットを用意して、Agent の回答をまとめて採点できます（answer_correctness などの指標）。
Agent の設定を変えるたびに同じセットで評価し直すと、精度が上がったか下がったかを数値で追えます。

---

次は [Part 4: 法人営業の業務フローをスキルにする](part4_skill.md) です。
