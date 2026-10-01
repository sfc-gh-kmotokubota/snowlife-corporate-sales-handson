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

## 進行ガイド（講師用）

時刻は開始からの経過時間です。各 Part の「確認ポイント」を全員が満たしてから次へ進んでください。
遅れている受講者には「間に合わなかった場合」の答え合わせ SQL を案内し、全体の進行を止めないようにします。

### 事前準備（前日まで）

- [ ] 受講者分のトライアルアカウント（AI 機能有効）が発行され、ログインできることを確認する
- [ ] 講師用アカウントで setup.sql から Part 5 までを一度通す（[AGENTS.md](AGENTS.md) の手順）
- [ ] 画面共有用に、Agent A / B の回答を並べて見せられる状態にしておく（Q1・Q2・Q8 が差の出やすい質問）
- [ ] [handson/eval_questions.md](handson/eval_questions.md) の正解とリハーサル結果を手元に用意する

### 0:00〜0:10　Part 0: 趣旨説明・環境構築

| 項目 | 内容 |
|---|---|
| 講師が話すこと | 今日確かめる4点（データ投入／セマンティックビュー作成／Agent の精度／CoWork での業務活用）と、ご提案アーキテクチャとの対応（README の「アーキテクチャ」） |
| 受講者の作業 | setup.sql を Run All（3〜5分）→ 待ち時間に Workspaces へ Git リポジトリを追加 |
| 確認ポイント | 最後に完了バナーが出ている／ワークスペースに `snowlife-corporate-sales-handson` が見える |
| つまずきやすい点 | Step 3 の GitHub 連携エラー（README のトラブルシューティング参照） |

### 0:10〜0:25　Part 1: データとカタログを確認する

| 項目 | 内容 |
|---|---|
| 講師が話すこと | CRM・PDF・他部署・外部データが1つのアカウントに集まっていること。列名とコード値だけでは意味が分からないこと |
| 受講者の作業 | Catalog で `SF_OPPORTUNITY` を見る → CoCo に3つ質問 → 面談記録 PDF を AI_PARSE_DOCUMENT / AI_EXTRACT で構造化 |
| 確認ポイント | 「AMT_EST が千円単位かどうかはデータから確定できない」ことに気づいている |
| 伝えたいメッセージ | 業務の取り決めは、データの外にある。それを教えるのが次のセマンティックビュー |

### 0:25〜0:50　Part 2: Semantic Studio でセマンティックビューを作る

| 項目 | 内容 |
|---|---|
| 講師が話すこと | Semantic Studio は Workspaces の中の CoCo。たたき台は AI、業務の言葉（同義語・説明）は人が入れる |
| 受講者の作業 | Add new » Semantic View で生成 → 中身を確認 → 4項目（千円単位・ステージ・ランク・訪問）の説明を手で入れる → カスタム指示と検証済みクエリを追加 → Deploy → SEMANTIC_VIEW() で確認 |
| 確認ポイント | `SHOW SEMANTIC VIEWS IN SCHEMA SNOWLIFE_HANDSON_DB.AI;` に `SV_SALES_ANALYTICS` がある |
| 時間切れの対応 | 0:45 の時点で Deploy できていない人は `answers/part2_semantic_view.sql` を実行 |
| つまずきやすい点 | 名前を `SV_SALES_ANALYTICS` 以外にしてしまう（Part 3 の Agent B が参照できない） |

### 0:50〜1:10　Part 3: Cortex Agent を作って精度を比べる

| 項目 | 内容 |
|---|---|
| 講師が話すこと | 2つの Agent はツールも指示文も同じで、違いはセマンティックビューだけ |
| 受講者の作業 | `answers/part3_agents.sql` を実行 → CoWork を2タブで開き、4問を A / B に投げてスコアシートに記入 → A の誤答をリクエスト ID から CoCo に診断させる |
| 確認ポイント | Q1・Q2 で A が「千円のまま」の金額を返していることに、思考ステップの SQL で気づいている |
| 伝えたいメッセージ | A でも推測で当たる質問はある。問題は「もっともらしい誤答」が混ざること（eval_questions.md の講師メモ） |
| 注意 | 3-3 で `SV_SALES_MINIMAL` を Deploy しないよう念押しする（比較できなくなる） |

### 1:10〜1:20　休憩

休憩中に、講師画面で Part 4 の完成形（「KDDIの訪問準備をして」の回答）を表示しておくと、後半の導入がスムーズです。

### 1:20〜1:45　Part 4: 法人営業の業務フローをスキルにする

| 項目 | 内容 |
|---|---|
| 講師が話すこと | スキルは業務の「型」を書いた1枚のテキスト。CoCo 用スキルと Agent 用スキルは別物 |
| 受講者の作業 | 自社の訪問準備の流れをメモ → CoCo で SKILL.md を作成 → ステージにアップロード → Agent に3スキルを登録 → CoWork で3つ依頼 |
| 確認ポイント | `DESCRIBE AGENT` に skills が3件ある／回答がスキルのフォーマット順になっている |
| 時間切れの対応 | 1:38 の時点で登録できていない人は `answers/part4_skill.sql` を実行 |
| 盛り上げどころ | 4-1 で受講者の実際の業務を1〜2人に聞き、その内容を SKILL.md に反映するとリアリティが増す |

### 1:45〜2:00　Part 5: 営業職員として CoWork を使う・振り返り

| 項目 | 内容 |
|---|---|
| 講師が話すこと | CoWork と Agent はデフォルトロールの権限で動く。本番では営業職員ごとのユーザーと SSO で運用 |
| 受講者の作業 | デフォルトロールを営業職員ロールに切替 → ai.snowflake.com を開き直して4問 → **デフォルトロールを戻す** |
| 確認ポイント | 支社別一覧が東京第一だけになる／トヨタの既契約数値が返らない |
| 伝えたいメッセージ | 行アクセスポリシーは Analyst に効くが、Cortex Search には効かない。本番では検索サービスの分け方も設計が必要 |
| 締め | 振り返り表（part5 の 5-5）で4点を確認し、次のステップ（PoC の範囲・対象業務）を議論する |
| 注意 | 5-4 のロールを戻す SQL を全員が実行したか確認する |

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
