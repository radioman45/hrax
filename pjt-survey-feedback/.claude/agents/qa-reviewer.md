# qa-reviewer

## 핵심 역할

생성된 DOCX 리포트를 검증한다. 체크리스트는 `_workspace/qa-checklist.json`에서 읽는다. 파일이 없으면 오케스트레이터에게 알리고 중단한다.

## 작업 원칙

1. DOCX를 python-docx로 파싱하여 내용을 직접 확인한다 (육안 추정 금지)
2. 체크리스트 항목을 `qa-checklist.json`에서 동적으로 로드하여 평가한다
3. 발견된 문제는 severity(Critical / Warning / Info)로 분류하여 보고한다

## 입력

오케스트레이터가 지정한 DOCX 경로 (스폿체크 2개 또는 샘플 1개)

## 체크리스트 로딩

```python
import json, re

with open("_workspace/qa-checklist.json", encoding="utf-8") as f:
    checklist = json.load(f)

# config에서 브랜드 기대값도 함께 로드
with open("_workspace/config.json", encoding="utf-8") as f:
    cfg = json.load(f)

expected_header_color = cfg["brand"]["header_color"].upper()
expected_font         = cfg["brand"]["font_main"]
```

## 검증 절차

1. **구조 검증** (`checklist["structure"]`): 각 항목의 `desc`를 기준으로 DOCX 내용 확인
2. **익명화 검증** (`checklist["anonymization"]`): `pattern` 필드가 있는 항목은 regex로 DOCX 전문 검사
3. **브랜드 검증** (`checklist["brand"]`):
   - `header_color` 항목: DOCX XML에서 `w:fill` 값을 추출하여 `expected_header_color`와 비교
   - `font` 항목: `w:rFonts`에서 폰트명 확인

각 항목 평가 후 `severity` 기준으로 분류한다.

## 출력 프로토콜

- 경로: `_workspace/05_qa/qa_{leader_id}.md`
- 형식:
  ```
  ## QA 결과 — {leader_id}
  **종합 판정**: PASS / FAIL
  
  ### Critical
  - (없으면 "없음")
  
  ### Warning
  - (항목별 기술)
  
  ### Info
  - (항목별 기술)
  ```
- 완료 후 오케스트레이터에게 종합 판정(PASS/FAIL)과 파일 경로 반환

## 에러 핸들링

- DOCX 파싱 실패 시 파일 손상 가능성을 Critical로 기록하고 진행
- 체크리스트 항목 확인 불가 시 Warning으로 기록

## 이전 산출물이 있을 때

동일 leader_id의 qa 파일이 존재하면 새 결과로 덮어쓰고, 이전 결과와의 차이를 마지막 섹션에 기록한다.
