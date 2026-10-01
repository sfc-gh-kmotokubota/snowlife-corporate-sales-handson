"""
ハンズオン用デモデータ生成スクリプト（講師用。受講者は実行不要）

架空の生命保険会社「スノー生命」の法人営業データを生成し、
data/csv/ に CSV、data/docs/ に PDF を書き出します。
乱数シードを固定しているため、何度実行しても同じデータになります。

  python3 tools/generate_data.py

依存: reportlab（PDF生成）、macOS の Arial Unicode フォント
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT / "data" / "csv"
DOC_DIR = ROOT / "data" / "docs"
random.seed(20261005)

# ---------------------------------------------------------------------------
# マスタ
# ---------------------------------------------------------------------------
BRANCHES = [
    ("T01", "東京第一法人営業部"),
    ("T02", "東京第二法人営業部"),
    ("K01", "関西法人営業部"),
    ("C01", "中部法人営業部"),
]

USERS = [
    ("U001", "山田 太郎", "T01", "シニア営業"),
    ("U002", "鈴木 花子", "T01", "営業"),
    ("U003", "田中 次郎", "T02", "シニア営業"),
    ("U004", "佐藤 美咲", "T02", "営業"),
    ("U005", "高橋 健", "K01", "シニア営業"),
    ("U006", "伊藤 彩", "C01", "営業"),
]

INDUSTRIES = [
    ("MFG", "製造業"), ("TRD", "商社"), ("ITC", "情報通信業"), ("FIN", "金融業"),
    ("ENE", "電気・ガス業"), ("RTL", "小売業"), ("CON", "建設業"), ("TRN", "運輸業"),
    ("RES", "不動産業"),
]

# (ACCT_ID, 企業名, 業種コード, 従業員数, 本社都道府県, 支社, 担当, 証券コード, 法人番号, 上場フラグ)
ACCOUNTS = [
    ("A001", "トヨタ自動車(株)", "MFG", 72700, "愛知県", "C01", "U006", "7203", "1180301018771", "1"),
    ("A002", "パナソニック ホールディングス(株)", "MFG", 63400, "大阪府", "K01", "U005", "6752", "5120001158218", "1"),
    ("A003", "伊藤忠商事(株)", "TRD", 44500, "東京都", "T01", "U001", "8001", "4120001077474", "1"),
    ("A004", "NTTデータグループ(株)", "ITC", 190000, "東京都", "T02", "U003", "9613", "9010601021385", "1"),
    ("A005", "野村ホールディングス(株)", "FIN", 26000, "東京都", "T01", "U002", "8604", "1010001009052", "1"),
    ("A006", "JERA(株)", "ENE", 5100, "東京都", "T02", "U004", "", "4010001168312", "0"),
    ("A007", "イオン(株)", "RTL", 306000, "千葉県", "T02", "U003", "8267", "5040001003865", "1"),
    ("A008", "住友商事(株)", "TRD", 48200, "東京都", "T01", "U001", "8053", "3010001008782", "1"),
    ("A009", "鹿島建設(株)", "CON", 21800, "東京都", "T02", "U004", "1812", "6010401005040", "1"),
    ("A010", "日本郵船(株)", "TRN", 36000, "東京都", "T01", "U002", "9101", "4010001034784", "1"),
    ("A011", "武田薬品工業(株)", "MFG", 14000, "大阪府", "K01", "U005", "4502", "1120001077461", "1"),
    ("A012", "ANAホールディングス(株)", "TRN", 44000, "東京都", "T02", "U003", "9202", "1010401025536", "1"),
    ("A013", "セブン&アイ・ホールディングス(株)", "RTL", 130000, "東京都", "T01", "U001", "3382", "2010001109769", "1"),
    ("A014", "KDDI(株)", "ITC", 48000, "東京都", "T01", "U002", "9433", "9011101031552", "1"),
    ("A015", "三菱地所(株)", "RES", 10000, "東京都", "T02", "U004", "8802", "3010001008848", "1"),
    ("A016", "日本製鉄(株)", "MFG", 51000, "東京都", "T01", "U001", "5401", "4010001008772", "1"),
    ("A017", "三井住友フィナンシャルグループ(株)", "FIN", 40000, "東京都", "T02", "U003", "8316", "1010001065327", "1"),
    ("A018", "サントリーホールディングス(株)", "MFG", 40000, "大阪府", "K01", "U005", "", "5120001158143", "0"),
    ("A019", "東日本旅客鉄道(株)", "TRN", 70000, "東京都", "T01", "U002", "9020", "8011001046021", "1"),
    ("A020", "旭化成(株)", "MFG", 45000, "東京都", "T02", "U004", "3407", "9010001033076", "1"),
]

PRODUCTS = [
    ("P01", "総合福祉団体定期保険", "団体保障", "従業員の死亡・高度障害を保障する1年更新の団体保険"),
    ("P02", "団体長期障害所得補償保険（GLTD）", "団体保障", "病気やケガで長期間働けなくなった従業員の所得を補償"),
    ("P03", "確定拠出年金（企業型DC）運営管理", "企業年金", "企業型DCの運営管理機関業務"),
    ("P04", "確定給付企業年金（DB）受託", "企業年金", "DB制度の受託と資産運用"),
    ("P05", "長期定期保険（経営者向け）", "経営者保障", "役員の死亡保障と退職慰労金の財源確保"),
    ("P06", "団体医療保険", "団体保障", "従業員の入院・手術を保障する任意加入型の団体保険"),
    ("P07", "団体がん保険", "団体保障", "がん治療と就労継続を支援する任意加入型の団体保険"),
    ("P08", "健康経営支援サービス Wellness-Star", "非保険サービス", "健康経営優良法人認定の取得支援と従業員の健康データ分析"),
]

STAGES = [("10", "初回提案"), ("20", "ニーズ確認"), ("30", "提案中"), ("40", "最終交渉"), ("90", "受注"), ("99", "失注")]
ACT_TYPES = [("V", "訪問"), ("O", "オンライン面談"), ("T", "電話")]

START = date(2025, 4, 1)   # FY2025 期首
END = date(2026, 9, 30)    # データ最終日（FY2026 上期末）


def rand_date(a: date, b: date) -> date:
    return a + timedelta(days=random.randint(0, (b - a).days))


def write_csv(name, header, rows):
    with open(CSV_DIR / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


# ---------------------------------------------------------------------------
# CRM（Salesforce 相当）。列名はあえて業務的に分かりにくい名前にしている
# ---------------------------------------------------------------------------
def gen_crm():
    write_csv("sf_branch.csv", ["BR_CD", "BR_NM"], BRANCHES)
    write_csv("sf_user.csv", ["OWNER_ID", "USR_NM", "BR_CD", "TITLE"], USERS)
    write_csv("mst_industry.csv", ["IND_CD", "IND_NM"], INDUSTRIES)
    write_csv("mst_product.csv", ["PRD_CD", "PRD_NM", "PRD_CAT", "PRD_DESC"], PRODUCTS)
    write_csv("mst_stage.csv", ["STAGE_CD", "STAGE_NM"], STAGES)
    write_csv(
        "sf_account.csv",
        ["ACCT_ID", "ACCT_NM", "IND_CD", "EMP_CNT", "HQ_PREF", "BR_CD", "OWNER_ID", "SEC_CD", "HOJIN_NO", "LISTED_FLG"],
        ACCOUNTS,
    )

    owner_of = {a[0]: a[6] for a in ACCOUNTS}

    # 既契約（ANN_PREM は円単位）
    contracts = []
    cid = 1
    for a in ACCOUNTS:
        held = random.sample(["P01", "P03", "P04", "P05", "P06"], k=random.randint(1, 3))
        # 団体定期を持たない大企業を意図的に作る（評価質問 Q4 用）
        if a[0] in ("A004", "A012", "A020"):
            held = [p for p in held if p != "P01"] or ["P03"]
        if a[0] in ("A001", "A003", "A014"):
            held = list(dict.fromkeys(["P01"] + held))
        for p in held:
            start = rand_date(date(2015, 4, 1), date(2024, 4, 1))
            lapsed = random.random() < 0.12
            sts = "9" if lapsed else "1"
            end = rand_date(date(2024, 4, 1), date(2025, 9, 30)) if lapsed else ""
            prem = int(a[3] * random.uniform(800, 4500) / 1000) * 1000
            contracts.append((f"K{cid:04d}", a[0], p, sts, start.isoformat(), end if end == "" else end.isoformat(),
                              prem, int(a[3] * random.uniform(0.3, 0.95)), owner_of[a[0]]))
            cid += 1
    write_csv("sf_contract.csv",
              ["CNT_ID", "ACCT_ID", "PRD_CD", "STS_CD", "START_DT", "END_DT", "ANN_PREM", "INS_CNT", "OWNER_ID"],
              contracts)

    # 商談（AMT_EST は千円単位の年換算保険料見込み）
    opps = []
    oid = 1
    for a in ACCOUNTS:
        for _ in range(random.randint(2, 4)):
            prd = random.choice(["P01", "P02", "P02", "P03", "P05", "P06", "P07", "P08"])
            crt = rand_date(START, date(2026, 8, 31))
            stage = random.choices(["10", "20", "30", "40", "90", "99"], weights=[2, 3, 4, 3, 3, 2])[0]
            rank = {"10": "C", "20": random.choice("BC"), "30": random.choice("AB"),
                    "40": random.choice("SA"), "90": "S", "99": random.choice("BC")}[stage]
            amt = int(a[3] * random.uniform(0.2, 1.6))  # 千円
            close = crt + timedelta(days=random.randint(30, 240))
            if stage in ("90", "99") and close > END:
                close = rand_date(crt, END)
            opps.append((f"O{oid:04d}", a[0], prd, stage, rank, amt, crt.isoformat(), close.isoformat(), owner_of[a[0]]))
            oid += 1
    write_csv("sf_opportunity.csv",
              ["OPP_ID", "ACCT_ID", "PRD_CD", "STAGE_CD", "RANK_FLG", "AMT_EST", "CRT_DT", "CLOSE_DT", "OWNER_ID"],
              opps)

    # 活動履歴
    subjects = ["福利厚生制度の見直し相談", "団体保険の更改提案", "人的資本開示に関する情報提供", "健康経営の取り組みヒアリング",
                "企業年金の運用状況報告", "経営者保障のご提案", "DC 加入者向けセミナー打ち合わせ", "定例訪問"]
    acts = []
    aid = 1
    for a in ACCOUNTS:
        n = random.randint(8, 22)
        # 7〜9月に訪問していない先を意図的に作る（評価質問 Q5 用）
        quiet = a[0] in ("A005", "A009", "A016")
        for _ in range(n):
            d = rand_date(START, END)
            if quiet and d >= date(2026, 7, 1):
                d = rand_date(START, date(2026, 6, 30))
            typ = random.choices(["V", "O", "T"], weights=[5, 3, 2])[0]
            acts.append((f"ACT{aid:05d}", a[0], owner_of[a[0]], d.isoformat(), typ, random.choice(subjects)))
            aid += 1
    write_csv("sf_activity.csv", ["ACT_ID", "ACCT_ID", "OWNER_ID", "ACT_DT", "ACT_TYP", "SUBJ"], acts)
    return acts


# ---------------------------------------------------------------------------
# 財務企画部のデータ（キーは証券コード。CRM とは別DBに置く）
# ---------------------------------------------------------------------------
def gen_finance():
    rows = []
    for a in ACCOUNTS:
        if not a[7]:
            continue
        base = a[3] * random.uniform(8, 60)  # 売上高（百万円）
        growth = random.uniform(-0.08, 0.15)
        for fy in (2023, 2024, 2025):
            rev = base * (1 + growth) ** (fy - 2023)
            op = rev * random.uniform(0.04, 0.14)
            rows.append((a[7], fy, round(rev), round(op), int(a[3] * (1 + growth / 3) ** (fy - 2023))))
    write_csv("fin_company_pl.csv", ["SEC_CD", "FISCAL_YEAR", "REVENUE_MJPY", "OP_PROFIT_MJPY", "EMP_CNT"], rows)


# ---------------------------------------------------------------------------
# 外部データ（求人件数。キーは法人番号）
# ---------------------------------------------------------------------------
def gen_jobs():
    rows = []
    surge = {"A014", "A004", "A018"}  # 直近で求人が急増している先（評価質問 Q10 用）
    for a in ACCOUNTS:
        base = max(5, int(a[3] / 800))
        m = date(2024, 7, 1)
        while m <= date(2026, 9, 1):
            mult = 1.0
            if a[0] in surge and m >= date(2026, 7, 1):
                mult = random.uniform(1.7, 2.3)
            rows.append((a[8], m.isoformat(), int(base * random.uniform(0.85, 1.15) * mult)))
            m = date(m.year + (m.month // 12), m.month % 12 + 1, 1)
    write_csv("ext_job_postings.csv", ["HOJIN_NO", "POST_MONTH", "POSTING_CNT"], rows)


# ---------------------------------------------------------------------------
# 面談メモ（Cortex Search 用の非構造化テキスト）
# ---------------------------------------------------------------------------
TOPICS = [
    ("健康経営", "健康経営優良法人の認定更新に向けて、ストレスチェック結果の活用方法を知りたいとのこと。Wellness-Star の分析レポートをサンプルで提示した。"),
    ("人的資本開示", "有価証券報告書の人的資本開示で、福利厚生の充実度を定量的に示したいという課題感。団体保険の加入率や GLTD 導入の有無が指標になり得ると説明した。"),
    ("DC移行", "DB 制度の一部を企業型 DC へ移行する検討が始まっている。移行時の想定利回りと従業員説明会の進め方について質問を受けた。"),
    ("M&A", "海外子会社の買収が決まり、統合後の福利厚生制度の統一が課題。グループ全体での団体定期保険の一本化に関心を示した。"),
    ("採用強化", "エンジニア採用を大幅に増やす方針。採用競争力のため、GLTD や団体がん保険など就業不能リスクへの備えを福利厚生に加えたいとの話があった。"),
    ("介護離職", "管理職層の介護離職が増えている。両立支援の一環として、介護に関する保障と相談サービスの組み合わせを検討したいとのこと。"),
    ("役員保障", "役員の世代交代を控え、役員退職慰労金の財源確保について相談。長期定期保険の解約返戻率の推移を次回提示する約束をした。"),
]


def gen_meeting_notes(acts):
    acct = {a[0]: a for a in ACCOUNTS}
    visits = [x for x in acts if x[4] in ("V", "O")]
    random.shuffle(visits)
    rows = []
    for i, v in enumerate(sorted(visits[:120], key=lambda x: x[3])):
        a = acct[v[1]]
        topic, body = random.choice(TOPICS)
        follow = random.choice(["次回は人事部長同席で具体的な提案を行う。", "見積もりを2週間以内に提出する。",
                                "先方の社内稟議の日程を確認する。", "他社比較の資料を求められたため準備する。"])
        text = (f"【面談記録】{a[1]} / {v[3]} / {dict(ACT_TYPES)[v[4]]}\n"
                f"テーマ: {topic}\n"
                f"内容: {body}\n"
                f"先方の反応: {random.choice(['前向き', '慎重', '情報収集段階', '強い関心'])}\n"
                f"次回アクション: {follow}")
        rows.append((f"MN{i + 1:04d}", v[1], a[1], v[2], v[3], topic, text))
    write_csv("meeting_notes.csv", ["NOTE_ID", "ACCT_ID", "ACCT_NM", "OWNER_ID", "NOTE_DT", "TOPIC", "NOTE_TEXT"], rows)


# ---------------------------------------------------------------------------
# PDF（商品パンフレット・約款抜粋・面談記録）
# ---------------------------------------------------------------------------
def gen_pdfs():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    pdfmetrics.registerFont(TTFont("JP", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"))
    h1 = ParagraphStyle("h1", fontName="JP", fontSize=16, leading=24, spaceAfter=10)
    h2 = ParagraphStyle("h2", fontName="JP", fontSize=12.5, leading=20, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("b", fontName="JP", fontSize=10.5, leading=17)

    def build(fname, title, sections):
        doc = SimpleDocTemplate(str(DOC_DIR / fname), pagesize=A4, title=title,
                                leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
        story = [Paragraph(title, h1)]
        for head, paras in sections:
            story.append(Paragraph(head, h2))
            for p in paras:
                story.append(Paragraph(p, body))
                story.append(Spacer(1, 4))
        story.append(Spacer(1, 12))
        story.append(Paragraph("※本資料はハンズオン用に作成した架空の資料です。実在の保険会社・商品とは関係ありません。", body))
        doc.build(story)

    build("product/gltd_brochure.pdf", "スノー生命 団体長期障害所得補償保険（GLTD）のご案内", [
        ("1. 商品の概要", ["病気やケガで長期間働けなくなった従業員の所得を、最長で定年まで補償する団体保険です。",
                        "健康保険の傷病手当金（最長1年6か月）が終了した後の収入減少に備えられます。"]),
        ("2. 主な特長", ["補償額は月額給与の最大60%まで設定できます。",
                       "精神疾患による就業不能も補償の対象です（支払期間は最長2年）。",
                       "企業が保険料を負担する基本プランと、従業員が任意で上乗せできるプランを組み合わせられます。"]),
        ("3. 導入メリット", ["人的資本開示において、就業不能リスクへの備えを定量的に示せます。",
                         "採用・定着の観点で福利厚生の差別化になります。"]),
        ("4. 引受条件", ["加入対象は従業員50名以上の法人です。", "てん補期間は免責期間（180日）経過後から開始します。"]),
    ])
    build("product/group_term_terms.pdf", "総合福祉団体定期保険 約款抜粋（ハンズオン用）", [
        ("第1条 保険金の支払", ["被保険者が保険期間中に死亡したときは、死亡保険金を支払います。",
                            "被保険者が保険期間中に所定の高度障害状態に該当したときは、高度障害保険金を支払います。"]),
        ("第5条 保険期間と更新", ["保険期間は1年とし、契約者から申し出がない限り同一条件で更新します。",
                            "更新時の保険料は、更新日現在の被保険者の年齢と人数により再計算します。"]),
        ("第9条 告知義務", ["加入時に所定の告知が必要です。告知内容が事実と異なる場合、保険金を支払えないことがあります。"]),
        ("第12条 契約の解約", ["契約者はいつでも将来に向かって契約を解約できます。団体定期保険には解約返戻金はありません。"]),
    ])
    build("product/wellness_star.pdf", "健康経営支援サービス Wellness-Star サービス概要", [
        ("サービス内容", ["健康診断・ストレスチェックの結果を匿名化して分析し、部署別の健康リスクを可視化します。",
                       "健康経営優良法人の認定申請に必要な取り組みの棚卸しを支援します。"]),
        ("提供条件", ["団体保険の契約がある法人は無償で利用できます。契約がない法人は年額制で提供します。"]),
        ("関連商品", ["団体医療保険、団体がん保険、GLTD と組み合わせると、予防から就業不能時の補償までを一体で提案できます。"]),
    ])
    build("meeting/kddi_20260910.pdf", "面談記録 KDDI(株) 2026年9月10日", [
        ("出席者", ["先方: 人事部長 野沢様、厚生課長 浜田様 / 当社: 鈴木（東京第一法人営業部）"]),
        ("議題", ["エンジニア採用強化に伴う福利厚生の見直し、人的資本開示の指標について"]),
        ("内容", ["2026年度下期からエンジニア採用を前年比2倍に増やす計画。採用競争力の観点で、就業不能時の所得補償（GLTD）を検討したい。",
                "人的資本開示では、福利厚生の充実度を加入率で示したい。現状の団体定期保険の加入率は約72%。",
                "健康経営優良法人ホワイト500の継続取得のため、ストレスチェック結果の活用にも関心がある。"]),
        ("次回アクション", ["GLTD と Wellness-Star を組み合わせた提案書を10月中旬までに提出する。",
                         "加入率向上の施策事例を3社分用意する。"]),
    ])
    build("meeting/panasonic_20260822.pdf", "面談記録 パナソニック ホールディングス(株) 2026年8月22日", [
        ("出席者", ["先方: グループ人事部 総合厚生課長 松本様 / 当社: 高橋（関西法人営業部）"]),
        ("議題", ["DB 制度の一部 DC 移行、グループ会社間の制度統一"]),
        ("内容", ["2027年4月を目途に、DB 制度の一部を企業型 DC へ移行する方向で検討を開始した。",
                "移行に伴う従業員説明会を年内に実施したい。想定利回りの設定根拠を知りたい。",
                "グループ会社ごとに団体定期保険の契約が分かれており、一本化によるコスト削減に関心がある。"]),
        ("次回アクション", ["DC 移行の他社事例と説明会資料のひな形を提示する。", "団体定期保険の一本化シミュレーションを作成する。"]),
    ])


def main():
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    (DOC_DIR / "product").mkdir(parents=True, exist_ok=True)
    (DOC_DIR / "meeting").mkdir(parents=True, exist_ok=True)
    acts = gen_crm()
    gen_finance()
    gen_jobs()
    gen_meeting_notes(acts)
    gen_pdfs()
    print("generated:", sorted(p.name for p in CSV_DIR.iterdir()), sorted(str(p.relative_to(DOC_DIR)) for p in DOC_DIR.rglob("*.pdf")))


if __name__ == "__main__":
    main()
