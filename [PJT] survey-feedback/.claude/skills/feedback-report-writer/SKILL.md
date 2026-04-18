---
name: feedback-report-writer
description: "팀장 피드백 JSON 데이터를 DOCX 리포트(2페이지)로 변환하는 스킬. 3섹션 구조(점수 요약/강점·개선/서술형 요지), Noto Sans KR 폰트 적용. 팀장별 피드백 리포트 생성, Word 문서 출력, leadership_feedback DOCX 작성 요청 시 반드시 이 스킬을 사용. 샘플 생성(L001), 배치 생성, 재생성 모두 해당."
---

# Feedback Report Writer

팀장 피드백 JSON → DOCX 리포트 (2페이지).
`docx` 스킬을 보완하는 도메인 특화 규칙을 담는다.

## config 로딩 (필수 — 스킬 시작 전 실행)

스킬 내부에 색상·폰트·레이아웃 상수를 하드코딩하지 않는다.
모든 설정은 `_workspace/config.json`에서 읽는다. 파일이 없으면 오케스트레이터에게 알리고 중단한다.

```python
import json, os

CONFIG_PATH = "_workspace/config.json"

with open(CONFIG_PATH, encoding="utf-8") as f:
    cfg = json.load(f)

brand  = cfg["brand"]
layout = cfg["layout"]
output = cfg["output"]

HEADER_COLOR  = brand["header_color"]
ACCENT_COLOR  = brand["accent_color"]
DARK_GRAY     = brand["dark_gray"]
LIGHT_BG      = brand["light_bg"]
FONT_MAIN     = brand["font_main"]
FONT_FALLBACK = brand["font_fallback"]

MAX_PAGES            = layout["max_pages"]
MAX_QUALITATIVE      = layout["max_qualitative_per_question"]
MIN_RESP_QUALITATIVE = layout["min_responses_for_qualitative"]
TOP_N                = layout["top_n"]

OUTPUT_DIR      = output["dir"]
FILENAME_PATTERN = output["filename_pattern"]
```

## 리포트 구조 (2페이지)

### 페이지 1 — 헤더 + 섹션 1 + 섹션 2

```
┌─────────────────────────────────────┐
│ [config.brand.accent_color 헤더 바]                  │
│ 리더십 Survey Feedback Report        │ ← 18pt Bold, White on Orange
│ {팀장명} 팀장  |  {팀명}  |  {기간}  │ ← 10pt Gray
├─────────────────────────────────────┤
│ 섹션 1. 문항별 점수 요약              │ ← 12pt Bold, config.brand.accent_color
│                                     │
│ Q01 명확한 방향성…  ████░  4.2 / 5  │
│ Q02 …              ███░░  3.8 / 5  │
│ …(Q01~Q10 전체)                     │
├─────────────────────────────────────┤
│ 섹션 2. 강점 / 개선 필요              │
│ ┌ 강점 Top 3 ──────┐ ┌ 개선 Top 3 ─┐│
│ │ 1. Q03 코칭 역량  │ │ 1. Q09 …   ││
│ │ 2. Q07 소통 능력  │ │ 2. Q05 …   ││
│ │ 3. Q01 방향 제시  │ │ 3. Q10 …   ││
│ └──────────────────┘ └────────────┘│
└─────────────────────────────────────┘
```

### 페이지 2 — 섹션 3

```
┌─────────────────────────────────────┐
│ 섹션 3. 구성원 의견 요약              │ ← 12pt Bold, config.brand.accent_color
│                                     │
│ Q11 잘하고 있는 점                   │ ← 11pt Bold
│ • [익명화된 응답 핵심 요지 1]         │ ← 10pt, 최대 5개
│ • [익명화된 응답 핵심 요지 2]         │
│ …                                   │
│                                     │
│ Q12 개선이 필요한 점                  │
│ • [익명화된 응답 핵심 요지 1]         │
│ …                                   │
│                                     │
│ ─────────────────────────────────── │
│ 응답 기간: YYYY-MM-DD ~ YYYY-MM-DD   │ ← 9pt Gray, 하단
│ 본 리포트는 HR 내부용입니다           │
└─────────────────────────────────────┘
```

## python-docx 구현 가이드

### 의존성

```bash
pip install python-docx
# Noto Sans KR은 시스템 폰트로 설치 필요
# Windows: https://fonts.google.com/noto/specimen/Noto+Sans+KR
```

### 문서 초기화

```python
from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# A4 페이지 설정
section = doc.sections[0]
section.page_width  = Cm(21)
section.page_height = Cm(29.7)
section.top_margin  = Cm(1.8)
section.bottom_margin = Cm(1.8)
section.left_margin  = Cm(2.0)
section.right_margin = Cm(2.0)
```

### 헤더 바 (config.brand.accent_color 배경)

```python
def add_header(doc, leader_name, team_name, date_range):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # 배경색 설정 (단락 shading)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "000000")
    pPr.append(shd)

    run = p.add_run("리더십 Survey Feedback Report")
    run.font.name   = FONT_MAIN
    run.font.size   = Pt(16)
    run.font.bold   = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # 부제목 단락
    sub = doc.add_paragraph()
    sub_run = sub.add_run(f"{leader_name} 팀장  |  {team_name}  |  {date_range['from']} ~ {date_range['to']}")
    sub_run.font.name  = FONT_MAIN
    sub_run.font.size  = Pt(10)
    sub_run.font.color.rgb = RGBColor(0x2D, 0x2D, 0x2D)
```

### 섹션 1: 막대 그래프 (텍스트 기반)

5점 척도는 ▓(채움) ░(빈칸)으로 표현한다.

```python
def score_bar(mean: float, max_score: int = 5) -> str:
    filled = round(mean)
    bar = "▓" * filled + "░" * (max_score - filled)
    return f"{bar}  {mean:.1f} / {max_score}"

# 출력 예: ▓▓▓▓░  4.2 / 5
```

### 섹션 2: 강점/개선 2열 레이아웃

```python
from docx.oxml import OxmlElement

def add_two_column_table(doc, strengths_data, improvements_data, questions):
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"

    # 강점 열
    cell_left = table.cell(0, 0)
    cell_left.text = "강점 Top 3\n"
    for i, q_id in enumerate(strengths_data, 1):
        cell_left.paragraphs[0].add_run(f"{i}. {questions[q_id]['question']}\n")

    # 개선 열
    cell_right = table.cell(0, 1)
    cell_right.text = "개선 필요 Top 3\n"
    for i, q_id in enumerate(improvements_data, 1):
        cell_right.paragraphs[0].add_run(f"{i}. {questions[q_id]['question']}\n")
```

### 섹션 3: 서술형 응답

응답 수가 `MIN_RESP_QUALITATIVE`(config) 미만이면 섹션 3 전체를 "응답 수가 충분하지 않아 개별 의견을 제공할 수 없습니다"로 대체한다.

```python
def add_qualitative(doc, qualitative: dict, response_count: int):
    if response_count < MIN_RESP_QUALITATIVE:   # config에서 로드
        p = doc.add_paragraph("응답 수가 충분하지 않아 개별 의견을 제공할 수 없습니다.")
        return

    for q_id, label in [("Q11", "잘하고 있는 점"), ("Q12", "개선이 필요한 점")]:
        responses = qualitative.get(q_id, [])
        if not responses:
            continue
        doc.add_heading(label, level=2)
        for r in responses[:MAX_QUALITATIVE]:   # config에서 로드
            p = doc.add_paragraph(r, style="List Bullet")
            p.runs[0].font.size = Pt(10)
```

### 파일 저장

```python
import os

os.makedirs(OUTPUT_DIR, exist_ok=True)   # config에서 로드

filename = FILENAME_PATTERN.format(      # config에서 로드
    leader_id=data["leader_id"],
    leader_name=data["leader_name"]
)
doc.save(os.path.join(OUTPUT_DIR, filename))
```

## 2페이지 준수 방법

- 섹션 1의 표를 9pt로 설정하고 행 간격을 줄인다
- 섹션 3의 응답을 최대 5개로 제한한다
- 헤더 단락의 상하 여백을 최소화한다 (`space_before = Pt(0)`, `space_after = Pt(4)`)
- 생성 후 python-docx로 페이지 수를 직접 확인할 수 없으므로, 섹션당 대략적인 줄 수로 추정한다:
  - 헤더: ~2줄, 섹션1: ~12줄, 섹션2: ~5줄 → 페이지 1 충분
  - 섹션3: Q11 5개 + Q12 5개 = ~12줄 → 페이지 2 충분

## 민감정보 체크

리포트 저장 전 아래 항목을 자동 확인한다:

```python
import re

def check_sensitive(doc_text: str) -> list[str]:
    issues = []
    if re.search(r'R\d{3}', doc_text):       # 응답ID 패턴
        issues.append("응답ID 포함 가능성")
    if re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', doc_text):  # 구체적 시각
        issues.append("응답 일시 구체값 포함")
    return issues
```

이슈가 발견되면 해당 부분을 수정하고 재저장한다.
