"""
A/B 評価ハーネス（講師用）: 評価10問を Agent A / B に投げ、回答を EVAL_RESULTS テーブルに保存する

  python3 tools/run_ab_eval.py <snow接続名>
"""

import json
import subprocess
import sys
import tempfile

CONN = sys.argv[1] if len(sys.argv) > 1 else "KMOT_AWS1"

QUESTIONS = [
    "進行中の商談のうち、見込みランクがAの商談の見込み金額合計を支社別に円で教えて",
    "2026年度上期に受注した商談の件数と見込み金額の合計（円）を教えて",
    "製造業の取引先は何社ありますか",
    "従業員5,000人以上で、総合福祉団体定期保険の有効な既契約がない取引先を教えて",
    "進行中でランクSかAの商談がある取引先のうち、2026年7月から9月に訪問していない取引先を教えて",
    "2026年度上期の支社別の訪問件数を教えて",
    "有効な既契約の年間保険料合計が多い取引先の上位5社を、保険料（円）と一緒に教えて",
    "GLTDの進行中の商談の件数と見込み金額の合計（円）を教えて",
    "2025年度の売上高が前年度より増えていて、進行中の商談がある取引先を教えて",
    "2026年7月から9月の求人件数合計が、前年同期の1.5倍以上に増えた取引先を教えて",
]
AGENTS = {"A": "SNOWLIFE_HANDSON_DB.AI.SALES_AGENT_BASIC", "B": "SNOWLIFE_HANDSON_DB.AI.SALES_AGENT"}


def body(q):
    return json.dumps({"messages": [{"role": "user", "content": [{"type": "text", "text": q}]}]}, ensure_ascii=False)


lines = [
    "USE ROLE ACCOUNTADMIN;",
    "USE WAREHOUSE SNOWLIFE_HANDSON_WH;",
    "USE SCHEMA SNOWLIFE_HANDSON_DB.AI;",
    "CREATE TABLE IF NOT EXISTS EVAL_RESULTS (RUN_TS TIMESTAMP_LTZ, AGENT VARCHAR, QNO NUMBER, QUESTION VARCHAR, RESP VARIANT);",
]
for i, q in enumerate(QUESTIONS, 1):
    for label, fqn in AGENTS.items():
        lines.append(
            "INSERT INTO EVAL_RESULTS SELECT CURRENT_TIMESTAMP(), '{l}', {n}, '{q}', "
            "TRY_PARSE_JSON(SNOWFLAKE.CORTEX.DATA_AGENT_RUN('{a}', $${b}$$));".format(
                l=label, n=i, q=q.replace("'", "''"), a=fqn, b=body(q))
        )

with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
    f.write("\n".join(lines))
    path = f.name

res = subprocess.run(["snow", "sql", "-c", CONN, "-f", path, "--format", "csv"], capture_output=True, text=True)
print(res.stdout[-2000:], res.stderr[-2000:])
