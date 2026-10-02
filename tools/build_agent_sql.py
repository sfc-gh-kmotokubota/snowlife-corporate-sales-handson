"""Agent の指示文（answers/agent_instructions/*.txt）を answers の SQL に反映する。

使い方: python3 tools/build_agent_sql.py
指示文を直したら、このスクリプトを実行して SQL を作り直す。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INS = ROOT / "answers" / "agent_instructions"

SKILL_LINE = "【スキルの使い方】\n- 訪問準備・提案準備・文面チェックの依頼では、対応するスキル（pre-visit-briefing / proposal-prep / compliance-check）の手順と出力フォーマットに従う。"


def block(key: str, text: str) -> str:
    body = "\n".join(("    " + line) if line else "" for line in text.strip("\n").split("\n"))
    return f"  {key}: |\n{body}\n"


def instructions(orch: str, resp: str) -> str:
    return "instructions:\n" + block("response", resp) + block("orchestration", orch)


def replace_instructions(sql: str, specs: list[str]) -> str:
    """出現順に instructions: ブロックを置き換える。"""
    pat = re.compile(r"instructions:\n(?:  .*\n|    .*\n|\n(?=    ))+")
    it = iter(specs)
    return pat.sub(lambda m: next(it), sql)


def main() -> None:
    orch = (INS / "orchestration_common.txt").read_text()
    resp = (INS / "response_common.txt").read_text()

    common = instructions(orch, resp)
    with_skills = instructions(orch.rstrip("\n") + "\n\n" + SKILL_LINE + "\n", resp)

    p3 = ROOT / "answers" / "part3_agents.sql"
    p3.write_text(replace_instructions(p3.read_text(), [common, common]))

    p4 = ROOT / "answers" / "part4_skill.sql"
    p4.write_text(replace_instructions(p4.read_text(), [with_skills]))


if __name__ == "__main__":
    main()
