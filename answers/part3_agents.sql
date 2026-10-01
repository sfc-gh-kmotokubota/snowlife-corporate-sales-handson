/*
================================================================================
Part 3 答え合わせ: Cortex Agent A / B の作成
================================================================================
Agent A（SALES_AGENT_BASIC）と Agent B（SALES_AGENT）は、ツール構成も指示文も同じです。
違いは Cortex Analyst ツールが参照するセマンティックビューだけです。

  Agent A: AI.SV_SALES_MINIMAL    … テーブルと主キー・リレーションのみ（setup.sql で作成）
  Agent B: AI.SV_SALES_ANALYTICS  … 説明・同義語・指標・検証済みクエリ付き（Part 2 で作成）

Part 2 を終えていない場合は、先に answers/part2_semantic_view.sql を実行してください。
================================================================================
*/

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE SNOWLIFE_HANDSON_WH;
USE SCHEMA SNOWLIFE_HANDSON_DB.AI;


-- ----------------------------------------------------------------------------
-- Agent A: 意味づけのないセマンティックビューを使う Agent
-- ----------------------------------------------------------------------------
CREATE OR REPLACE AGENT SALES_AGENT_BASIC
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


-- ----------------------------------------------------------------------------
-- Agent B: 受講者が作ったセマンティックビューを使う Agent
-- ----------------------------------------------------------------------------
CREATE OR REPLACE AGENT SALES_AGENT
    COMMENT = 'スノー生命 法人営業アシスタント'
    PROFILE = '{"display_name": "法人営業アシスタント（B: 意味づけあり）"}'
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
$$;


-- ----------------------------------------------------------------------------
-- CoWork に表示する
-- ----------------------------------------------------------------------------
-- CoWork オブジェクトがあるアカウントでは、追加しないと CoWork に表示されません。
ALTER SNOWFLAKE INTELLIGENCE SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT ADD AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT_BASIC;
ALTER SNOWFLAKE INTELLIGENCE SNOWFLAKE_INTELLIGENCE_OBJECT_DEFAULT ADD AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT;

-- 営業職員ロールにも使わせる（setup.sql の FUTURE GRANT で付与済みですが、念のため明示します）
GRANT USAGE ON AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT_BASIC TO ROLE SNOWLIFE_SALES_REP_T01;
GRANT USAGE ON AGENT SNOWLIFE_HANDSON_DB.AI.SALES_AGENT       TO ROLE SNOWLIFE_SALES_REP_T01;

SHOW AGENTS IN SCHEMA SNOWLIFE_HANDSON_DB.AI;
