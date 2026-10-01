# 生命保険 法人営業向け Snowflake AI ハンズオン

CRM・面談記録 PDF・他部署データ・外部データを Snowflake に集約し、
**セマンティックビューを作ると Cortex Agent の回答がどう変わるか**、
そして **法人営業職員が CoWork で意図した回答を得られるか** を、2時間で実際に触って確かめるハンズオンです。

操作はすべて Snowsight 上で行い、作業の多くを **CoCo in Snowsight**（Cortex Code）と **Semantic Studio** に任せます。

---

## 概要

あなたは架空の生命保険会社 **スノー生命** の法人営業企画部の担当者です。現場の法人営業職員から、こんな声が届いています。

> 「訪問前に CRM・面談メモ・財務資料をあちこち見に行くのが大変。一言で聞いたら、まとめて返ってきてほしい」

> 「AI に聞いても、社内の用語やルールを分かっていない答えが返ってくると怖くて使えない」

このハンズオンでは、次の4点を順に確かめます。

1. **データ投入**: CRM・PDF・他部署データ・外部データが1つの基盤に集まる
2. **セマンティックビューの作成**: 業務の言葉（見込みランク、受注、千円単位、年度など）をデータに結びつける
3. **Agent の精度**: 意味づけのない Agent と意味づけのある Agent に同じ質問をして、回答を比べる
4. **CoWork での業務活用**: 法人営業の業務フローをスキルにして、営業職員の権限で使う

---

## アジェンダ（合計2時間）

| 時間 | Part | 内容 | 手順書 |
|---|---|---|---|
| 10分 | 0 | 趣旨説明・環境構築（setup.sql） | このページ |
| 15分 | 1 | データとカタログを確認する | [handson/part1_catalog.md](handson/part1_catalog.md) |
| 25分 | 2 | Semantic Studio でセマンティックビューを作る | [handson/part2_semantic_view.md](handson/part2_semantic_view.md) |
| 20分 | 3 | Cortex Agent を作って精度を比べる | [handson/part3_agent_ab.md](handson/part3_agent_ab.md) |
| 10分 | — | 休憩 | |
| 25分 | 4 | 法人営業の業務フローをスキルにする | [handson/part4_skill.md](handson/part4_skill.md) |
| 15分 | 5 | 営業職員として CoWork を使う・振り返り | [handson/part5_cowork.md](handson/part5_cowork.md) |

---

## 前提条件

- ハンズオン用に発行された Snowflake トライアルアカウント（AI 機能が有効なもの）
- `ACCOUNTADMIN` ロールが使えること
- ブラウザで Snowsight（app.snowflake.com）と CoWork（ai.snowflake.com）にアクセスできること

ローカルへのツールのインストールは不要です。

> **ご自身で用意したトライアルアカウントを使う場合**
> セルフサービスのトライアルアカウントでは、CoCo・Cortex Agent・AI 関数が既定で無効になっており、
> 有効にするにはクレジットカードの登録が必要です。

---

## Step 0: 環境構築

### 0-1. setup.sql を実行する（約3〜5分）

1. Snowsight で **Projects » Workspaces** を開く
2. **+ Add new » SQL File** で新しいファイルを作る
3. このリポジトリの [setup.sql](setup.sql) の中身をすべて貼り付ける
4. **Run All** で実行する

各ステップの最後に `【Step N】... が完了しました` と表示され、最後に完了バナーが出れば成功です。

### 0-2. Workspaces にこのリポジトリを追加する

1. **Projects » Workspaces** で **+ Add new » From Git repository** を選ぶ
2. 次のように入力して **Create** を押す

| 項目 | 値 |
|---|---|
| Repository URL | `https://github.com/sfc-gh-kmotokubota/snowlife-corporate-sales-handson.git` |
| Workspace name | `snowlife-corporate-sales-handson` |
| API integration | `GIT_API_INTEGRATION_SNOWLIFE`（setup.sql で作成済み） |
| Authentication | Public repository |

Part 2 以降はこのワークスペースで作業します。

---

## アーキテクチャ

ご提案アーキテクチャのうち、データ投入から CoWork までをこのアカウントの中に縮小して再現しています。

```mermaid
flowchart LR
  subgraph sources [データソース相当]
    crm["CRM（Salesforce 相当）"]
    pdf["面談記録・商品資料 PDF"]
    fin["財務企画部データ"]
    ext["外部データ（求人）"]
  end
  subgraph sf [Snowflake]
    raw["RAW スキーマ"]
    mart["MART スキーマ（データマート）"]
    search["Cortex Search"]
    sv["セマンティックビュー"]
    agent["Cortex Agent と業務スキル"]
  end
  crm --> raw
  pdf -->|"AI_PARSE_DOCUMENT"| search
  fin -->|"別DBから参照"| mart
  ext --> raw
  raw --> mart
  raw --> sv
  mart --> sv
  raw --> search
  sv --> agent
  search --> agent
  agent --> cowork["Snowflake CoWork（法人営業職員）"]
```

| ご提案アーキテクチャ | このハンズオン | 補足 |
|---|---|---|
| Salesforce（Openflow 連携） | `RAW.SF_*` テーブル | Openflow の代わりに CSV をロード |
| S3 / Snowpipe | GitHub → ステージ → `COPY INTO` | |
| 非構造化データの構造化 | `AI_PARSE_DOCUMENT`・`AI_EXTRACT` | Part 1 で体験 |
| 財務企画部のデータ共有 | `FINANCE_PLANNING_DB`（別データベース） | 実際のデータ共有ではなく、同じアカウント内の別DBで代用 |
| データマート | `MART` スキーマ | キー体系の違うデータを取引先 ID で引けるように整形 |
| Horizon Catalog | Catalog・セマンティックビュー・行アクセスポリシー | |
| Cortex Agents / CoWork | `AI.SALES_AGENT` ほか | |
| Copilot Studio（MCP 連携） | 対象外 | 説明のみ |

---

## 作成されるオブジェクト

### setup.sql で作成

| 種類 | 名前 | 内容 |
|---|---|---|
| Warehouse | `SNOWLIFE_HANDSON_WH` | XSMALL |
| Database | `SNOWLIFE_HANDSON_DB` | スキーマ `RAW` / `MART` / `AI` / `SECURITY` |
| Database | `FINANCE_PLANNING_DB` | 財務企画部データ（`CORP.COMPANY_PL`） |
| Table | `RAW.SF_ACCOUNT` ほか | 取引先20社・商談55件・活動294件・既契約35件・面談メモ120件・求人540件 |
| View | `MART.V_COMPANY_FINANCIALS` / `MART.V_JOB_POSTINGS` | 財務・求人を取引先 ID で引けるようにしたビュー |
| Cortex Search | `AI.MEETING_NOTE_SEARCH` / `AI.PRODUCT_DOC_SEARCH` | 面談メモ・商品資料の検索 |
| Semantic View | `AI.SV_SALES_MINIMAL` | 比較用（意味づけなし） |
| Role | `SNOWLIFE_SALES_REP_T01` | 東京第一法人営業部の営業職員ロール |
| Row Access Policy | `SECURITY.RAP_BY_BRANCH` | 営業職員ロールでは担当支社の取引先だけ見える |
| Stage | `RAW.DOC_STAGE` / `AI.SKILL_STAGE` | PDF / Agent スキル |
| Integration | `GIT_API_INTEGRATION_SNOWLIFE` | GitHub 連携 |

### ハンズオン中に作成

| 種類 | 名前 | Part | 答え合わせ |
|---|---|---|---|
| Semantic View | `AI.SV_SALES_ANALYTICS` | 2 | [answers/part2_semantic_view.sql](answers/part2_semantic_view.sql) |
| Cortex Agent | `AI.SALES_AGENT_BASIC` / `AI.SALES_AGENT` | 3 | [answers/part3_agents.sql](answers/part3_agents.sql) |
| Agent skill | `pre-visit-briefing` / `proposal-prep` / `compliance-check` | 4 | [answers/part4_skill.sql](answers/part4_skill.sql) |

---

## リポジトリ構成

```
snowlife-corporate-sales-handson/
├── README.md                 # このファイル
├── AGENTS.md                 # 講師向け（事前検証・データ再生成の手順）
├── setup.sql                 # 環境構築（Run All で実行）
├── cleanup.sql               # 後片付け
├── handson/                  # 各 Part の手順書・評価10問・スコアシート
├── answers/                  # 答え合わせ（セマンティックビュー・Agent・スキル・正解SQL）
├── skills/                   # 配布するスキル（proposal-prep / compliance-check）
├── data/csv/  data/docs/     # デモデータ（CSV と PDF）
└── tools/                    # 講師用スクリプト（データ生成・A/B 評価）
```

---

## トラブルシューティング

### setup.sql の Step 3 で `clone is not authorized` などのエラーになる

API 統合の `API_ALLOWED_PREFIXES` と、Git リポジトリの `ORIGIN` が一致しているか確認してください。

### `Cortex ... is not available in region` と表示される

クロスリージョン推論が有効になっていません。setup.sql の Step 1 を再実行してください。

```sql
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
```

### CoWork に Agent が表示されない

CoWork オブジェクトに Agent が追加されているか確認してください。追加されていなければ、次を実行します。

```sql
SHOW SNOWFLAKE INTELLIGENCES;
ALTER SNOWFLAKE INTELLIGENCE SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT ADD AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT;
```

### CoWork でスキルが使われない

1. `DESCRIBE AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT;` の出力に `skills` が含まれているか確認する
2. `LS @SNOWLIFE_HANDSON_DB.AI.SKILL_STAGE/ PATTERN = '.*SKILL\.md';` で `skills/<スキル名>/SKILL.md` の階層になっているか確認する
3. チャット入力欄の **+** ボタンからスキルを明示的に選ぶ

### Part 5 の後、Snowsight で権限エラーが出る

デフォルトロールが営業職員ロールのままになっています。[handson/part5_cowork.md](handson/part5_cowork.md) の 5-4 を実行してください。

---

## 後片付け

[cleanup.sql](cleanup.sql) を実行すると、このハンズオンで作成したオブジェクトを削除します。
CoWork オブジェクトとクロスリージョン推論の設定は、他の用途と共有している可能性があるため変更しません。

---

※ 本リポジトリのデータ・資料はすべてハンズオン用に作成した架空のものです。実在の企業名を使用していますが、数値・面談内容などは事実とは関係ありません。
