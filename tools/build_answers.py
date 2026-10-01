"""
answers/part2_semantic_view.yaml から answers/part2_semantic_view.sql を生成する（講師用）

  python3 tools/build_answers.py

YAML を直したら必ず再実行して、SQL 版と内容を揃えてください。
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
yaml_text = (ROOT / "answers" / "part2_semantic_view.yaml").read_text(encoding="utf-8")

if "$$" in yaml_text:
    raise SystemExit("YAML に $$ が含まれているため、ドル記号クォートで埋め込めません")

sql = f"""/*
================================================================================
Part 2 答え合わせ: セマンティックビュー AI.SV_SALES_ANALYTICS を作成する
================================================================================
Semantic Studio での作成が間に合わなかった場合に実行してください。
内容は answers/part2_semantic_view.yaml と同じです（tools/build_answers.py で生成）。

Semantic Studio で使う場合は、YAML ファイルの中身を .sv.yaml に貼り付けて Deploy しても
同じ結果になります。
================================================================================
*/

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE SNOWLIFE_HANDSON_WH;

-- 1. 作成前に検証だけ行う（第3引数 TRUE）
CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
    'SNOWLIFE_HANDSON_DB.AI',
    $${yaml_text}$$,
    TRUE
);

-- 2. 作成する
CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
    'SNOWLIFE_HANDSON_DB.AI',
    $${yaml_text}$$
);

-- 3. 営業職員ロールにも参照させる
GRANT SELECT ON SEMANTIC VIEW SNOWLIFE_HANDSON_DB.AI.SV_SALES_ANALYTICS TO ROLE SNOWLIFE_SALES_REP_T01;

-- 4. 確認
SHOW SEMANTIC METRICS IN SNOWLIFE_HANDSON_DB.AI.SV_SALES_ANALYTICS;
"""

(ROOT / "answers" / "part2_semantic_view.sql").write_text(sql, encoding="utf-8")
print("wrote answers/part2_semantic_view.sql")
