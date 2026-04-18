---
name: survey-feedback-orchestrator
description: "리더십 Survey Feedback Report 자동화 오케스트레이터. dummy_leadership_survey.xlsx에서 팀장별 DOCX 리포트 10개를 생성한다. 트리거: 설문 리포트 생성, 피드백 리포트 만들기, leadership feedback DOCX, 팀장 리포트 자동화. 후속 작업: 리포트 재생성, 특정 팀장만 다시 만들기, 리포트 수정 보완, 샘플 다시 생성, 스폿체크, QA 재실행, 이전 결과 개선 요청 시에도 반드시 이 스킬을 사용."
---

# Survey Feedback Orchestrator

`dummy_leadership_survey.xlsx` → 팀장 10명 × DOCX 피드백 리포트를 자동 생성한다.

## 실행 모드: 하이브리드

| Phase | 모드 | 이유 |
|-------|------|------|
| Phase 2 (데이터 파싱) | 서브 에이전트 | 단일 독립 작업 |
| Phase 3 (샘플 생성) | 서브 에이전트 | L001 단독, 사용자 검토 전 |
| Phase 4 (배치 생성) | 서브 에이전트 9개 병렬 | 독립 파일, 팀 통신 불필요 |
| Phase 5 (QA) | 서브 에이전트 2개 병렬 | 독립 검증 |

## 에이전트 구성

| 에이전트 | 파일 | 역할 | 스킬 |
|---------|------|------|------|
| data-analyst | `.claude/agents/data-analyst.md` | 엑셀 파싱·집계 | survey-data-parser, xlsx |
| report-writer | `.claude/agents/report-writer.md` | DOCX 생성 | feedback-report-writer, docx |
| qa-reviewer | `.claude/agents/qa-reviewer.md` | 품질·익명화 검증 | — |

---

## 워크플로우

### Phase 0: 컨텍스트 확인

`_workspace/` 존재 여부를 확인하여 실행 모드를 결정한다:

- **`_workspace/` 미존재** → 초기 실행. Phase 1로 진행
- **`_workspace/` 존재 + 특정 팀장 재생성 요청** → 부분 재실행. Phase 3(해당 팀장만)으로 점프
- **`_workspace/` 존재 + 새 엑셀 파일 제공** → 새 실행. 기존 `_workspace/`를 `_workspace_prev_{YYYYMMDD}/`로 이동 후 Phase 1

### Phase 1: 준비

1. 작업 디렉토리 생성:
   ```
   _workspace/
   ├── 01_data/       # 팀장별 JSON
   ├── 05_qa/         # QA 결과
   output/  # 최종 DOCX
   ```
2. 입력 파일 존재 확인: `dummy_leadership_survey.xlsx`
   - 미존재 시 사용자에게 파일 경로 확인 요청 후 중단

3. **config 파일 초기화** — `_workspace/config.json` 존재 여부 확인:
   - **없으면** 아래 기본값으로 생성한다
   - **있으면** 그대로 사용한다 (사용자가 수정한 값 보존)

   ```json
   {
     "brand": {
       "header_color": "000000",
       "accent_color": "000000",
       "dark_gray":    "2D2D2D",
       "light_bg":     "F5F5F5",
       "font_main":    "Noto Sans KR",
       "font_fallback":"나눔고딕"
     },
     "layout": {
       "max_pages": 2,
       "max_qualitative_per_question": 5,
       "min_responses_for_qualitative": 3,
       "top_n": 3
     },
     "anonymization": {
       "shuffle_responses": true,
       "mask_proper_nouns": true,
       "hide_response_id":  true,
       "date_format":       "range_only"
     },
     "output": {
       "dir": "output",
       "filename_pattern": "leadership_feedback_{leader_id}_{leader_name}.docx"
     }
   }
   ```

4. **qa-checklist 파일 초기화** — `_workspace/qa-checklist.json` 존재 여부 확인:
   - **없으면** 아래 기본값으로 생성한다
   - **있으면** 그대로 사용한다

   ```json
   {
     "structure": [
       {"id": "page_count",  "desc": "페이지 수 max_pages 이내",                     "severity": "Critical"},
       {"id": "section_1",   "desc": "섹션 1: 문항별 점수 요약(Q01~Q10) 존재",       "severity": "Critical"},
       {"id": "section_2",   "desc": "섹션 2: 강점 Top N / 개선 필요 Top N 존재",    "severity": "Critical"},
       {"id": "section_3",   "desc": "섹션 3: 서술형 응답 요지(Q11·Q12) 존재",       "severity": "Critical"}
     ],
     "anonymization": [
       {"id": "no_response_id", "desc": "응답ID(R###) 미노출",                        "severity": "Critical", "pattern": "R\\d{3}"},
       {"id": "no_timestamp",   "desc": "응답 일시 구체값 미포함(HH:MM 패턴 없음)",   "severity": "Critical", "pattern": "\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}"},
       {"id": "date_range",     "desc": "응답 기간이 범위(YYYY-MM-DD ~ YYYY-MM-DD)로만 표시", "severity": "Warning"}
     ],
     "brand": [
       {"id": "header_color", "desc": "헤더 배경색이 config.brand.header_color와 일치", "severity": "Warning"},
       {"id": "font",         "desc": "config.brand.font_main 또는 font_fallback 적용", "severity": "Info"}
     ]
   }
   ```

### Phase 2: 데이터 파싱

**실행 모드:** 서브 에이전트

```
Agent(
  name: "data-analyst",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: """
    .claude/agents/data-analyst.md의 역할을 수행한다.
    survey-data-parser 스킬을 먼저 읽고 시작한다.
    
    입력: dummy_leadership_survey.xlsx
    출력: _workspace/01_data/{leader_id}_data.json (10개)
         _workspace/01_data/parse_summary.md
    
    완료 후 팀장 목록(ID, 이름)을 반환한다.
  """
)
```

반환값에서 팀장 목록 추출. 목록이 비어있으면 parse_summary.md를 읽고 사용자에게 보고 후 중단.

### Phase 3: 샘플 생성 (L001)

**실행 모드:** 서브 에이전트

```
Agent(
  name: "report-writer-sample",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: """
    .claude/agents/report-writer.md의 역할을 수행한다.
    feedback-report-writer 스킬과 docx 스킬을 먼저 읽고 시작한다.
    
    입력: _workspace/01_data/L001_data.json
    출력: output/leadership_feedback_L001_{팀장명}.docx
    
    완료 후 파일 경로를 반환한다.
  """
)
```

**[사용자 검토 대기]**

샘플 생성 완료 후 사용자에게 다음을 보고한다:
```
샘플 리포트가 생성되었습니다:
📄 output/leadership_feedback_L001_{팀장명}.docx

확인 후 승인해 주세요:
- "승인" 또는 "진행" → 나머지 9개 배치 생성 시작
- "수정: [피드백]" → 피드백을 반영하여 샘플 재생성
```

수정 요청 시: feedback-report-writer 스킬을 업데이트하거나 에이전트 프롬프트를 조정하여 Phase 3 재실행.

### Phase 4: 배치 생성 (L002~L010)

**실행 모드:** 서브 에이전트 9개 병렬  
**조건:** 사용자가 샘플 승인 후 실행

Phase 2에서 확보한 팀장 목록에서 L001을 제외한 9명을 단일 메시지에서 동시 호출:

```
# 단일 메시지에서 9개 Agent 동시 호출 (run_in_background: true)

Agent(name: "writer-L002", subagent_type: "general-purpose", model: "opus",
  run_in_background: true,
  prompt: "feedback-report-writer 스킬, docx 스킬 읽고 시작. 입력: _workspace/01_data/L002_data.json → 출력: output/leadership_feedback_L002_{팀장명}.docx")

Agent(name: "writer-L003", ..., run_in_background: true, ...)
... (L004~L010 동일 패턴)
```

모든 에이전트 완료 후 10개 DOCX 존재 여부 확인.

### Phase 5: QA 스폿체크

**실행 모드:** 서브 에이전트 2개 병렬

output 디렉토리의 DOCX 중 L001(샘플)을 제외하고 2개를 무작위 선택:

```python
import random
all_files = [f for f in os.listdir("output") if f.endswith(".docx")]
spot_files = random.sample([f for f in all_files if "L001" not in f], 2)
```

2개를 단일 메시지에서 동시 호출:

```
Agent(name: "qa-1", subagent_type: "general-purpose", model: "opus",
  run_in_background: true,
  prompt: ".claude/agents/qa-reviewer.md 역할 수행. 파일: output/{spot_files[0]}. 결과: _workspace/05_qa/qa_{id1}.md")

Agent(name: "qa-2", ..., run_in_background: true, ...)
```

### Phase 6: 완료 보고

사용자에게 최종 결과를 보고한다:

```
✅ 리더십 Survey Feedback Report 생성 완료

📁 출력 경로: output/
   leadership_feedback_L001_홍길동.docx
   leadership_feedback_L002_김영희.docx
   ... (10개)

🔍 QA 스폿체크 결과:
   L00X: PASS / FAIL (주요 이슈 있으면 요약)
   L00Y: PASS / FAIL

⚠️  FAIL 항목이 있으면 수정 방법을 안내
```

FAIL 항목 존재 시: 해당 팀장 ID를 report-writer에 재할당하여 수정 생성.

완료 보고 직후 아래 회고 템플릿을 사용자에게 제시한다:

```
---
작업이 마무리되었습니다. 짧게 회고를 남겨 주세요.

# 회고 v{N} — {YYYY-MM-DD}

## 잘된 것
-

## 이상한 것 (원했던 결과와 어긋남)
-

## 다음 버전(v{N+1})에서 바꿀 것
-
---
```

- `{N}`은 이번 실행 회차 (초기 실행이면 1, 재실행이면 이전 회고 번호 +1)
- 회고 내용을 받으면 `99-retro-v{N}.md`에 저장한다
- "다음 버전에서 바꿀 것" 항목이 있으면 해당 내용을 하네스 개선 제안으로 정리하여 함께 제시한다

회고를 저장한 직후 ADR을 자동 생성한다:

### ADR 자동 생성 규칙

이번 실행에서 내린 아키텍처 결정을 파악하여 `adr/` 디렉토리에 저장한다.

**ADR 작성 대상 — 아래 중 하나라도 해당하면 신규 ADR을 생성한다:**
- 에이전트 수·역할·실행 모드를 변경한 경우
- 스킬의 핵심 로직(집계 방식, 레이아웃, 익명화 규칙)을 변경한 경우
- config.json 또는 qa-checklist.json 구조를 변경한 경우
- 에러 핸들링 방침을 바꾼 경우
- 사용자 피드백으로 설계 방향이 달라진 경우

**작성하지 않는 경우:** 설정값만 바꾼 경우(예: 색상 값 변경), 버그 수정, 재실행

**파일명 규칙:** `adr/NNN-{slug}.md`
- NNN: 001부터 순번 (기존 파일 확인 후 다음 번호 사용)
- slug: 결정 내용을 2~4단어로 요약한 kebab-case (한국어 가능)

**ADR 파일 형식:**

```markdown
# ADR-{NNN}: {결정 제목}

**날짜:** YYYY-MM-DD
**상태:** 확정

## 맥락

이 결정이 필요했던 배경과 해결해야 했던 문제를 서술한다.
비개발자도 읽을 수 있게 쉽게 쓴다.

## 결정

무엇을 어떻게 결정했는지 한 문단으로 요약한다.

## 이유

이 결정을 선택한 구체적 이유를 나열한다.
다른 선택지가 있었다면 왜 그것을 택하지 않았는지도 포함한다.

## 결과

이 결정으로 인해 생긴 트레이드오프나 후속 제약을 기록한다.
(좋은 결과, 나쁜 결과 모두 솔직하게 기재)
```

**ADR 생성 후 처리:**
- 생성한 ADR 목록을 완료 보고에 함께 표시한다
- CLAUDE.md 변경 이력에 `ADR-NNN 생성` 항목을 추가한다

---

## 데이터 흐름

```
dummy_leadership_survey.xlsx
         ↓
[data-analyst] → _workspace/01_data/{id}_data.json (×10)
         ↓
[report-writer L001] → output/leadership_feedback_L001.docx
         ↓ [사용자 승인]
[report-writer L002~L010 병렬] → output/leadership_feedback_L00X.docx (×9)
         ↓
[qa-reviewer ×2 병렬] → _workspace/05_qa/qa_{id}.md (×2)
         ↓
완료 보고
```

---

## 에러 핸들링

| 상황 | 전략 |
|------|------|
| 엑셀 파일 미존재 | 사용자에게 경로 확인 요청 후 중단 |
| 특정 팀장 JSON 생성 실패 | parse_summary.md 확인 후 1회 재시도. 재실패 시 해당 팀장 건너뛰고 보고서에 누락 명시 |
| report-writer 실패 | 1회 재시도. 재실패 시 해당 파일 미생성 명시 후 계속 |
| QA FAIL | 해당 팀장 재생성 제안. 사용자가 OK하면 Phase 3로 해당 팀장만 부분 재실행 |
| 2페이지 초과 | feedback-report-writer 스킬의 분량 조정 규칙 재적용 후 재생성 |

---

## 테스트 시나리오

### 정상 흐름
1. `dummy_leadership_survey.xlsx` 존재 확인
2. data-analyst가 JSON 10개 생성 (`_workspace/01_data/`)
3. L001 샘플 DOCX 생성 → 사용자 "승인"
4. L002~L010 병렬 생성 완료
5. 무작위 2개 QA PASS
6. `output/`에 DOCX 10개 존재

### 에러 흐름
1. Phase 4에서 report-writer-L005가 python-docx 오류로 실패
2. 1회 재시도 → 성공
3. 재시도 실패 시 → L005 미생성 명시하고 나머지 8개로 Phase 5 진행
4. 완료 보고에 "L005 생성 실패" 포함, 개별 재생성 방법 안내
