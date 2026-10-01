/*
================================================================================
Part 4 答え合わせ: 業務スキルを Agent B（SALES_AGENT）に登録する
================================================================================
Snowsight の Agent 画面（Skills タブ » Add Skill）で登録できなかった場合に実行してください。

  1. SKILL.md を SKILL_STAGE に置く（自分で書いたものが置けていない場合は見本をコピー）
  2. Agent の仕様に skills を追加する
  3. 登録されたことを確認する
================================================================================
*/

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE SNOWLIFE_HANDSON_WH;
USE SCHEMA SNOWLIFE_HANDSON_DB.AI;


-- ----------------------------------------------------------------------------
-- 1. SKILL.md をステージに置く
-- ----------------------------------------------------------------------------
-- 自分で書いた pre-visit-briefing/SKILL.md をアップロード済みなら、このブロックは飛ばしてください。
-- 見本（answers/skills/pre-visit-briefing/SKILL.md）を GitHub からコピーします。
ALTER GIT REPOSITORY SNOWLIFE_HANDSON_DB.RAW.SNOWLIFE_HANDSON_REPO FETCH;

COPY FILES INTO @SKILL_STAGE/skills/pre-visit-briefing/
    FROM @SNOWLIFE_HANDSON_DB.RAW.SNOWLIFE_HANDSON_REPO/branches/main/answers/skills/pre-visit-briefing/;

-- SKILL.md が skills/<スキル名>/SKILL.md の階層にあることを確認する
LS @SKILL_STAGE/ PATTERN = '.*SKILL\.md';


-- ----------------------------------------------------------------------------
-- 2. Agent の仕様に skills を追加する
-- ----------------------------------------------------------------------------
-- 注意: ALTER AGENT ... SET SPECIFICATION は仕様全体を置き換えます。
--       既存のツール設定もすべて書き直す必要があります。
ALTER AGENT SALES_AGENT MODIFY LIVE VERSION SET SPECIFICATION =
$$
models:
  orchestration: auto

instructions:
  response: "日本語で、結論から簡潔に答えてください。数値には単位を付けてください。"
  orchestration: "数値・件数・一覧の質問は sales_analytics を使ってください。面談の内容は meeting_notes_search、商品の内容は product_docs_search を使ってください。訪問準備・提案準備・文面チェックの依頼では、対応するスキルの手順に従ってください。"

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
    semantic_view: "SNOWLIFE_HANDSON_DB.AI.SV_SALES_ANALYTICS"
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

skills:
  - name: "pre-visit-briefing"
    source:
      type: "STAGE"
      path: "@SNOWLIFE_HANDSON_DB.AI.SKILL_STAGE/skills/pre-visit-briefing"
  - name: "proposal-prep"
    source:
      type: "STAGE"
      path: "@SNOWLIFE_HANDSON_DB.AI.SKILL_STAGE/skills/proposal-prep"
  - name: "compliance-check"
    source:
      type: "STAGE"
      path: "@SNOWLIFE_HANDSON_DB.AI.SKILL_STAGE/skills/compliance-check"
$$;


-- ----------------------------------------------------------------------------
-- 3. 登録されたことを確認する
-- ----------------------------------------------------------------------------
-- 出力の agent_spec に skills が3件含まれていれば成功です。
DESCRIBE AGENT SALES_AGENT;
