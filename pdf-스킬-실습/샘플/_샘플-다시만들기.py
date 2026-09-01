# -*- coding: utf-8 -*-
"""
실습용 샘플 PDF를 처음부터 다시 만드는 스크립트 (강사용).

수강생은 이 파일을 실행할 필요가 없습니다. 이미 만들어진 PDF를 그냥 쓰면 됩니다.
샘플 내용을 바꾸고 싶을 때만 수정하고 아래처럼 실행하세요.

    python 샘플/_샘플-다시만들기.py

필요 라이브러리: reportlab
"""
import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.acroform import AcroForm
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# 한글 폰트
#
# 본문용: reportlab 내장 CJK 폰트(UnicodeCIDFont). 폰트 파일을 따로 받을 필요가
#         없고 어느 OS에서나 동작한다. 한글 PDF를 만드는 가장 쉬운 방법이다.
# 양식용: AcroForm 입력칸은 CID 폰트를 못 받아서 TTF가 따로 필요하다.
# ---------------------------------------------------------------------------
MYUNGJO, GOTHIC = "HYSMyeongJo-Medium", "HYGothic-Medium"
pdfmetrics.registerFont(UnicodeCIDFont(MYUNGJO))
pdfmetrics.registerFont(UnicodeCIDFont(GOTHIC))

FORM_FONT = "Helvetica"  # TTF를 못 찾으면 폴백 (입력칸에 한글이 안 들어감)
for path in (r"C:\Windows\Fonts\malgun.ttf",
             "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
             "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"):
    if os.path.exists(path):
        pdfmetrics.registerFont(TTFont("FormKR", path))
        AcroForm.formFontNames["FormKR"] = "FormKR"
        FORM_FONT = "FormKR"
        break
else:
    print("! 한글 TTF를 못 찾아 양식 입력칸은 영문 폰트로 만듭니다.", file=sys.stderr)


def styles():
    s = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=s["Title"], fontName=GOTHIC, fontSize=22, leading=30),
        "h1": ParagraphStyle("h1", parent=s["Heading1"], fontName=GOTHIC, fontSize=15,
                             leading=22, spaceBefore=14, spaceAfter=8,
                             textColor=colors.HexColor("#1f3d5c")),
        "h2": ParagraphStyle("h2", parent=s["Heading2"], fontName=GOTHIC, fontSize=12,
                             leading=18, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("b", parent=s["Normal"], fontName=MYUNGJO, fontSize=10.5,
                               leading=18, spaceAfter=6),
        "small": ParagraphStyle("s", parent=s["Normal"], fontName=MYUNGJO, fontSize=9,
                                leading=14, textColor=colors.HexColor("#666666")),
    }


def table_style(header_bg="#1f3d5c"):
    return TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), GOTHIC),
        ("FONTNAME", (0, 1), (-1, -1), MYUNGJO),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b9c6d4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f6fa")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])


# ===========================================================================
# 1) 3페이지 운영 보고서 - 읽기 / 요약 / 표 추출 / 쪽 나누기 실습용
# ===========================================================================
def make_report(out):
    st = styles()
    doc = SimpleDocTemplate(out, pagesize=A4, title="책방오후 2026년 상반기 운영 보고서",
                            author="책방오후 운영팀", subject="상반기 운영 실적 및 하반기 계획",
                            leftMargin=22 * mm, rightMargin=22 * mm,
                            topMargin=22 * mm, bottomMargin=20 * mm)
    S = []

    # --- 1쪽: 표지 + 요약 -------------------------------------------------
    S += [Spacer(1, 40 * mm),
          Paragraph("책방오후<br/>2026년 상반기 운영 보고서", st["title"]),
          Spacer(1, 10 * mm),
          Paragraph("작성일 2026년 7월 3일 · 작성 책방오후 운영팀 · 문서번호 BO-2026-H1-01",
                    st["small"]),
          Spacer(1, 18 * mm),
          Paragraph("요약", st["h1"]),
          Paragraph(
              "2026년 상반기 책방오후의 총매출은 8,420만 원으로 전년 동기 대비 18.6% 늘었다. "
              "성장의 대부분은 1월에 시작한 독서모임 멤버십에서 나왔다. 멤버십 회원은 6월 말 기준 "
              "214명이며 회원의 월평균 방문 횟수는 비회원의 3.1배였다.", st["body"]),
          Paragraph(
              "반면 음료 부문 매출은 2.4% 줄었다. 4월에 올린 가격 인상분이 방문객 수 감소를 "
              "상쇄하지 못했다. 도서 판매는 6.8% 성장했지만 재고 회전율이 연 2.1회에 그쳐 "
              "개선이 필요하다.", st["body"]),
          Paragraph(
              "하반기에는 멤버십을 두 등급으로 나누고, 평일 낮 시간대 유휴 좌석을 스터디 예약석으로 "
              "전환하는 두 가지를 우선 과제로 삼는다.", st["body"]),
          PageBreak()]

    # --- 2쪽: 표 두 개 ----------------------------------------------------
    S += [Paragraph("1. 월별 실적", st["h1"]),
          Paragraph("단위: 매출 만 원 / 방문객 명 / 객단가 원", st["small"]), Spacer(1, 4)]
    rows = [["월", "매출", "방문객", "객단가", "신규회원"],
            ["1월", "1,180", "1,842", "6,406", "58"],
            ["2월", "1,240", "1,905", "6,509", "41"],
            ["3월", "1,395", "2,088", "6,681", "37"],
            ["4월", "1,510", "2,010", "7,512", "29"],
            ["5월", "1,588", "2,143", "7,411", "26"],
            ["6월", "1,507", "1,974", "7,634", "23"]]
    t = Table(rows, colWidths=[24 * mm, 30 * mm, 30 * mm, 30 * mm, 30 * mm], hAlign="LEFT")
    t.setStyle(table_style())
    S += [t, Spacer(1, 12)]

    S += [Paragraph("2. 부문별 매출", st["h1"]), Spacer(1, 4)]
    rows2 = [["부문", "상반기 매출", "비중", "전년 대비"],
             ["멤버십", "3,180", "37.8%", "신규"],
             ["음료", "2,740", "32.5%", "-2.4%"],
             ["도서 판매", "1,910", "22.7%", "+6.8%"],
             ["대관 · 기타", "590", "7.0%", "+11.2%"]]
    t2 = Table(rows2, colWidths=[36 * mm, 36 * mm, 30 * mm, 34 * mm], hAlign="LEFT")
    t2.setStyle(table_style("#4a6b8a"))
    S += [t2, Spacer(1, 12),
          Paragraph(
              "월별 실적에서 눈에 띄는 지점은 4월이다. 방문객은 3월보다 78명 줄었는데 매출은 "
              "115만 원 늘었다. 4월 1일 음료 가격을 평균 12% 올린 효과다. 다만 5·6월 방문객이 "
              "회복되지 않아 가격 인상이 방문 빈도를 낮췄을 가능성을 배제하기 어렵다.", st["body"]),
          PageBreak()]

    # --- 3쪽: 계획 -------------------------------------------------------
    S += [Paragraph("3. 하반기 개선 계획", st["h1"]),
          Paragraph("3.1 멤버십 2단계 개편", st["h2"]),
          Paragraph(
              "현재 단일 등급(월 3만 원)을 베이직(월 1만 9천 원)과 플러스(월 4만 5천 원)로 나눈다. "
              "베이직은 독서모임 참여만, 플러스는 스터디석 예약과 도서 10% 상시 할인을 포함한다. "
              "목표는 9월 말까지 전환율 70%, 플러스 비중 25%다.", st["body"]),
          Paragraph("3.2 평일 낮 좌석 재배치", st["h2"]),
          Paragraph(
              "평일 11시부터 16시까지 좌석 점유율은 31%에 그친다. 창가 8석을 사전 예약제 "
              "스터디석으로 돌려 시간당 3천 원을 받는다. 손익분기는 하루 6시간 기준 점유율 42%다.",
              st["body"]),
          Paragraph("3.3 도서 재고 정리", st["h2"]),
          Paragraph(
              "12개월 이상 미판매 도서 340권을 8월 중고장터에서 정리한다. 확보한 공간에는 "
              "회전율이 높은 신간 에세이와 그래픽노블을 배치한다.", st["body"]),
          Spacer(1, 10),
          Paragraph("4. 위험 요인", st["h1"]),
          Paragraph(
              "첫째, 8월 건물 임대 재계약에서 임대료 인상이 예상된다. 인상률 10%를 가정하면 "
              "연 480만 원의 추가 비용이 발생한다. 둘째, 반경 500m 내 신규 카페 2곳이 하반기 "
              "개점을 예고했다. 셋째, 멤버십 개편 과정에서 기존 회원 이탈이 20%를 넘으면 "
              "상반기 성장분이 상쇄된다.", st["body"])]

    doc.build(S)
    print("만듦:", out)


# ===========================================================================
# 2) 거래명세서 3장 - 표 추출 / 합치기 실습용
# ===========================================================================
INVOICES = [
    ("2026-06_A문구.pdf", "A문구 유통", "2026-06-05", "BO-260605",
     [("A4 복사용지 500매", 12, 4500), ("네임펜 흑색", 40, 900),
      ("포스트잇 76x76", 24, 1200), ("독서모임 명찰 케이스", 60, 700)]),
    ("2026-06_B식자재.pdf", "B식자재 마트", "2026-06-12", "BO-260612",
     [("원두 에티오피아 1kg", 8, 23000), ("우유 1L", 60, 2400),
      ("종이컵 12oz 1000개", 3, 31000), ("시럽 바닐라 750ml", 6, 9800),
      ("냅킨 2000매", 4, 12000)]),
    ("2026-06_C인쇄소.pdf", "C인쇄소", "2026-06-21", "BO-260621",
     [("독서모임 안내 리플렛 A5", 500, 180), ("멤버십 카드 인쇄", 250, 620),
      ("현수막 3x1m", 2, 45000)]),
]


def make_invoice(out, vendor, date, docno, items):
    st = styles()
    doc = SimpleDocTemplate(out, pagesize=A4, title="거래명세서 " + docno, author=vendor,
                            leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=20 * mm, bottomMargin=20 * mm)
    S = [Paragraph("거 래 명 세 서", st["title"]), Spacer(1, 6),
         Paragraph("문서번호 " + docno + " · 거래일자 " + date, st["small"]), Spacer(1, 10)]

    info = Table([["공급자", vendor, "공급받는자", "책방오후"],
                  ["연락처", "02-000-0000", "사업자번호", "123-45-67890"]],
                 colWidths=[26 * mm, 52 * mm, 26 * mm, 52 * mm], hAlign="LEFT")
    info.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), MYUNGJO), ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("FONTNAME", (0, 0), (0, -1), GOTHIC), ("FONTNAME", (2, 0), (2, -1), GOTHIC),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2f6")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#eef2f6")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b9c6d4")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    S += [info, Spacer(1, 12)]

    rows = [["품명", "수량", "단가", "금액"]]
    total = 0
    for name, qty, price in items:
        amount = qty * price
        total += amount
        rows.append([name, format(qty, ","), format(price, ","), format(amount, ",")])
    vat = round(total * 0.1)
    rows += [["소계", "", "", format(total, ",")],
             ["부가세 10%", "", "", format(vat, ",")],
             ["합계", "", "", format(total + vat, ",")]]

    t = Table(rows, colWidths=[72 * mm, 24 * mm, 32 * mm, 36 * mm], hAlign="LEFT")
    style = table_style()
    style.add("FONTNAME", (0, len(items) + 1), (-1, -1), GOTHIC)
    style.add("BACKGROUND", (0, len(items) + 1), (-1, -1), colors.HexColor("#eef2f6"))
    style.add("ALIGN", (0, 1), (0, len(items)), "LEFT")
    t.setStyle(style)
    S += [t, Spacer(1, 14),
          Paragraph("※ 대금은 거래일로부터 30일 이내 지정 계좌로 입금 바랍니다.", st["small"])]

    doc.build(S)
    print("만듦:", out)


# ===========================================================================
# 3) 빈 신청서 양식 - 폼 채우기 실습용 (fillable AcroForm)
# ===========================================================================
def make_form(out):
    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle("AI 활용 워크숍 수강신청서")
    W, H = A4
    f = c.acroForm
    LEFT = 28 * mm

    c.setFillColor(colors.HexColor("#1f3d5c"))
    c.rect(0, H - 22 * mm, W, 22 * mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont(GOTHIC, 16)
    c.drawString(LEFT, H - 14.5 * mm, "AI 활용 워크숍 수강신청서")
    c.setFillColor(colors.HexColor("#333333"))

    def label(text, yy, size=10.5):
        c.setFont(GOTHIC, size)
        c.drawString(LEFT, yy, text)

    y = H - 36 * mm
    for name, tip in [("이름", "신청자 이름"), ("이메일", "연락받을 이메일 주소"),
                      ("연락처", "휴대폰 번호"), ("소속", "회사 또는 학교")]:
        label(name, y)
        f.textfield(name=name, tooltip=tip, x=LEFT + 34 * mm, y=y - 2.5 * mm,
                    width=95 * mm, height=9 * mm, borderStyle="underlined",
                    borderColor=colors.HexColor("#8fa3b8"),
                    fillColor=colors.HexColor("#f7f9fb"), forceBorder=True,
                    fontName=FORM_FONT, fontSize=10.5, value="")
        y -= 14 * mm

    y -= 2 * mm
    label("관심 분야 (복수 선택)", y)
    y -= 9 * mm
    for i, (name, text) in enumerate([("관심_AI활용", "업무에 AI 활용"),
                                      ("관심_자동화", "반복업무 자동화"),
                                      ("관심_문서작업", "문서 · 자료 만들기")]):
        x = LEFT + i * 52 * mm
        f.checkbox(name=name, tooltip=text, x=x, y=y - 1 * mm, size=11,
                   buttonStyle="check", borderColor=colors.HexColor("#8fa3b8"),
                   fillColor=colors.white, forceBorder=True, checked=False)
        c.setFont(MYUNGJO, 9.5)
        c.drawString(x + 15, y + 1.5, text)

    y -= 16 * mm
    label("AI 도구 사용 경험", y)
    y -= 9 * mm
    # 라디오 버튼의 value는 PDF 내부에서 Name 객체로 저장돼 한글을 담지 못한다
    # (한글로 넣으면 /Ì98Ç4c 처럼 깨진다). 값은 영문, 보이는 글자는 한글로 둔다.
    for i, (value, text) in enumerate([("none", "처음이다"), ("some", "조금 써봤다"),
                                       ("often", "자주 쓴다")]):
        x = LEFT + i * 52 * mm
        f.radio(name="사용경험", value=value, tooltip=text, x=x, y=y - 1 * mm, size=11,
                selected=False, buttonStyle="circle", shape="circle",
                borderColor=colors.HexColor("#8fa3b8"), fillColor=colors.white,
                forceBorder=True)
        c.setFont(MYUNGJO, 9.5)
        c.drawString(x + 15, y + 1.5, text)

    # 참고: 드롭다운(choice) 필드는 reportlab이 한글 옵션을 처리하지 못해 넣지 않았다.
    # PDF 스킬 자체는 choice 필드도 읽고 채울 수 있다.

    y -= 17 * mm
    label("신청 동기", y)
    y -= 30 * mm
    f.textfield(name="신청동기", tooltip="워크숍에서 얻고 싶은 것", x=LEFT, y=y,
                width=W - 2 * LEFT, height=28 * mm, borderStyle="solid",
                borderColor=colors.HexColor("#8fa3b8"),
                fillColor=colors.HexColor("#f7f9fb"), forceBorder=True,
                fontName=FORM_FONT, fontSize=10.5, fieldFlags="multiline", value="")

    y -= 14 * mm
    f.checkbox(name="개인정보동의", tooltip="개인정보 수집 및 이용에 동의",
               x=LEFT, y=y - 1 * mm, size=11, buttonStyle="check",
               borderColor=colors.HexColor("#8fa3b8"), fillColor=colors.white,
               forceBorder=True, checked=False)
    c.setFont(MYUNGJO, 9.5)
    c.drawString(LEFT + 15, y + 1.5, "개인정보 수집 및 이용에 동의합니다. (필수)")

    y -= 16 * mm
    label("신청일", y)
    f.textfield(name="신청일", tooltip="신청서 작성일 (YYYY-MM-DD)",
                x=LEFT + 34 * mm, y=y - 2.5 * mm, width=45 * mm, height=9 * mm,
                borderStyle="underlined", borderColor=colors.HexColor("#8fa3b8"),
                fillColor=colors.HexColor("#f7f9fb"), forceBorder=True,
                fontName=FORM_FONT, fontSize=10.5, value="")

    c.setFont(MYUNGJO, 8.5)
    c.setFillColor(colors.HexColor("#888888"))
    c.drawString(LEFT, 18 * mm, "책방오후 · 문의 hello@example.com · 접수마감 2026년 9월 12일")
    c.save()
    print("만듦:", out)


if __name__ == "__main__":
    make_report(os.path.join(HERE, "책방오후-상반기-운영보고서.pdf"))
    inv_dir = os.path.join(HERE, "거래명세서")
    os.makedirs(inv_dir, exist_ok=True)
    for fn, vendor, date, docno, items in INVOICES:
        make_invoice(os.path.join(inv_dir, fn), vendor, date, docno, items)
    make_form(os.path.join(HERE, "수강신청서-빈양식.pdf"))
    print("\n샘플 5개 생성 완료.")
