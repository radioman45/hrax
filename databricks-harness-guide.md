# Databricks 하네스 엔지니어링 가이드

> 회사 VDI 내 Databricks Genie Code를 활용한 Agent 구축
> 작성: 2026-04-18 · v1.0
> 기반: 하네스 엔지니어링 가이드 v1.0 (2026-04-18)

---

## 이 가이드를 쓰는 법

- **처음이면**: 1·2장부터
- **실제 과제**: 3·4장 (실행 대본·프롬프트)
- **반복 재사용**: 5장 (하네스 자산화)
- **막히면**: 6장

기본 하네스 가이드(Claude Code 기준)를 먼저 읽으셨다고 가정합니다. 이 가이드는 **Databricks 환경 차이점**만 다룹니다.

---

## 1. Claude Code와 Genie Code 개념 대응표

| 역할 | Claude Code | Databricks Genie Code |
|---|---|---|
| 전역 가이드 | `CLAUDE.md` | `.assistant_instructions.md` |
| 도메인 스킬 | `.claude/skills/*/SKILL.md` | `~/.assistant/skills/*/SKILL.md` |
| 에이전트 | `.claude/agents/*.md` | AI Playground Endpoint |
| 실행 파일 | `.py`, `.md` | `.ipynb` (Databricks Notebook) |
| 데이터 저장 | 로컬 폴더 | Unity Catalog (3-level) |
| 컴퓨트 | 로컬 CPU/GPU | Serverless / Warehouse |
| 대화형 Q&A | — | Genie Space (Text2SQL) |
| Agent 프로토타입 | harness 플러그인 | AI Playground + Tool Calling |
| 최종 배포 | `.py` 실행 | Model Serving Endpoint / Databricks Apps |

**핵심 통찰**: 개념과 파일명 규칙이 거의 같습니다. 기존 하네스 경험이 85% 그대로 적용됩니다.

---

## 2. Databricks 환경의 3가지 특수성

### 2-1. Unity Catalog 3-Level Namespace (강제)

모든 테이블 참조는 `catalog.schema.table` 형태 필수.
- 영환님 카탈로그: `personal_dev`
- 영환님 스키마: `{영문사번}` (예: `sixxxxx`)
- 브리프에 **카탈로그·스키마 슬롯을 명시적으로 넣어야** 프롬프트가 망가지지 않음

### 2-2. Serverless Warehouse

- 노트북 실행용 컴퓨트: Serverless (매번 선택해야 함)
- Genie Space 질의용 컴퓨트: Serverless Warehouse (별도)
- 브리프에 "컴퓨트는 Serverless 사용" 한 줄 필수

### 2-3. VDI·엔터프라이즈 제약

- 외부 네트워크 제한적 → 외부 API 호출 불가할 수 있음
- 민감정보 컬럼 (`cardNumber`, `email`) → `.assistant_instructions.md`에서 전역 차단
- 팀원 공유 필요 시 Genie Space Instructions·SKILL.md를 Git 또는 공용 폴더로

---

## 3. Databricks 전용 브리프 템플릿

기본 브리프 템플릿에 Databricks 섹션 3개를 추가한 버전입니다.

```markdown
# 브리프 — [과제명]

**영역**: 업무
**실행 환경**: Databricks Genie Code
**작성일**: YYYY-MM-DD
**버전**: v1

---

## 1. 과제 정의 (필수)

- **과제명**:
- **Input**:
- **Output**:
- **Done 기준**:

## 2. Databricks 환경 (필수, 신규)

- **카탈로그**: personal_dev (또는 지정)
- **스키마**: {영환님 사번 기반 스키마}
- **소스 테이블**: catalog.schema.table 형식으로 전부 명시
- **출력 테이블/볼륨**: catalog.schema.{name}
- **컴퓨트**: Serverless (Warehouse 필요 시 별도 명시)
- **임베딩/RAG 모델**: databricks-gte-large-en 등 (해당 시)

## 3. 5단계 매뉴얼

### Clarify
[여기서는 이미 완료. 브리핑룸에서 채운 내용]

### Context Gather
- 참조 스킬: ~/.assistant/skills/{name}/SKILL.md (있는 경우)
- 참조 테이블 메타: Unity Catalog에서 확인
- 또는: 생략. 이유: ___

### Plan
[Notebook 구조 · 셀 분할 방식]
- 상단: 마크다운 설명 + 패키지 설치 셀
- 중간: 단계별 SQL/PySpark 셀
- 하단: 검증 쿼리

### Generate
[Genie Code 단일 대화 / Agent 모드 / @스킬 호출 중 어느 쪽]

### Evaluate
- 소스·타겟 비교 쿼리 (복사 작업 시)
- Benchmark 등록 (Genie Space 사용 시)
- 또는: 생략. 이유: ___

## 4. 제약사항 (Databricks 특화)

- 민감정보: cardNumber·email 등 금지 컬럼
- 브랜드/포맷: 차트 색상·언어 규칙
- 컴퓨트 비용: Serverless 외 사용 금지
- 금지: 외부 API 호출 / 공개 카탈로그 쓰기

## 5. 포인터

- `.assistant_instructions.md`: 영환님 전역 규칙
- 관련 스킬: ~/.assistant/skills/{name}/SKILL.md
- 참조 Notebook: /Workspace/Users/.../...

---

<!-- 분량 가이드: 60줄 이내. 초과 시 포인터로 대체 -->
```

---

## 4. 실행 대본 — HR 예시 과제 1건

영환님의 HR AX 맥락에 맞춘 실제 과제로 시뮬레이션합니다. Quick-win 중 **HR Analytics AI**를 Databricks에서 구현하는 흐름입니다.

### 4-1. 브리핑룸에서 받은 브리프 (예시)

```markdown
# 브리프 — HR 월별 이직률 대시보드 (Databricks)

**영역**: 업무
**실행 환경**: Databricks Genie Code
**작성일**: 2026-04-18 · v1

## 1. 과제 정의
- **과제명**: HR 월별·부서별 이직률 대시보드
- **Input**: personal_dev.{사번}.hr_employee (직원 마스터), personal_dev.{사번}.hr_separation (퇴사 이력)
- **Output**: Databricks Dashboard + Genie Space
- **Done 기준**: 3개 차트 + KPI 4개 게시, Genie Space에서 자연어 질의 가능

## 2. Databricks 환경
- 카탈로그: personal_dev
- 스키마: {영환님 사번}
- 컴퓨트: Serverless (노트북), Serverless Warehouse (Genie)
- 사용 모델: Claude Sonnet 4.6 (Genie Code 내부)

## 3. 5단계
### Clarify
- 이직률 정의: (퇴사자수 / 월초 재직자수) × 100, 정규직만
- 기간 범위: 최근 12개월
### Context Gather
- 과거 수작업 월별 이직률 계산 로직(Excel) 참조 위치 지정
### Plan
- Silver: hr_silver_monthly_roster (월별 스냅샷)
- Gold: hr_gold_monthly_turnover_rate (월별·부서별 집계)
- Dashboard: 4개 데이터셋 (KPI, 월별 추이, 부서별, 직급별)
### Generate
- Genie Code Agent 모드 + @hr-analytics 스킬 사용
### Evaluate
- 자체 비교: 작년 HR팀 엑셀 수작업 결과와 3개월 스폿체크

## 4. 제약사항
- 민감정보: 개인식별정보(이름·주민번호) 컬럼 제외
- 브랜드: 차트 한국어, SK 오렌지 #F05023
- 금지: 외부 API 호출

## 5. 포인터
- ~/.assistant/skills/hr-analytics/SKILL.md
- ~/Workspace/Users/{영환님}/.assistant_instructions.md
```

### 4-2. Genie Code에 전달할 실행 프롬프트

Databricks 워크스페이스에 로그인하신 후, Genie Code 패널에서 **Agent 모드**로 전환하고 아래 프롬프트를 입력합니다. 브리프 파일 내용을 맨 앞에 붙입니다.

```
아래 브리프에 맞춰 Databricks 노트북을 작성해줘.

[브리프 내용 전체 복붙]

실행 규칙:
1. 노트북 최상단에 브리프 요약 마크다운 셀
2. 필수 패키지 설치 셀
3. 카탈로그·스키마 변수 선언 셀
4. Silver 테이블 생성 셀 (월별 스냅샷)
5. Gold 테이블 생성 셀 (이직률 집계)
6. 검증 쿼리 셀 (3개월 스폿체크)
7. 각 셀 위에 한국어 마크다운 설명

컴퓨트는 Serverless 사용.
코드 주석은 한국어, 변수명은 snake_case.

Build harness for this task.
```

> **중요**: 마지막 줄의 `Build harness for this task`는 Genie Code 공식 트리거가 아니라 영환님의 관습 마커입니다. Databricks에선 실제로는 Agent 모드에서 Skills를 호출합니다. 아래처럼 @ 멘션으로 명시하면 더 확실합니다:

```
@hr-analytics 위 브리프대로 노트북 전체를 생성해줘.
```

### 4-3. 6-Phase 관찰 체크리스트

Genie Code가 노트북 셀들을 생성하는 동안 관찰할 것:

- ☐ 카탈로그·스키마 변수 선언이 브리프대로인가
- ☐ Serverless 컴퓨트 선택 셀 포함됐나
- ☐ 민감정보 컬럼이 SELECT에서 제외됐나
- ☐ Silver·Gold 단계 구분이 브리프대로인가
- ☐ 검증 쿼리가 마지막 셀에 있는가

Run all 실행 후:

- ☐ 에러 없이 완료됐나
- ☐ Gold 테이블 행 수가 예상과 맞나
- ☐ 3개월 스폿체크 결과가 수작업과 일치하나

---

## 5. 하네스 자산화 — Genie Code에 영구 설치

첫 과제 끝나면, 같은 과제 반복 시 재사용 가능하도록 **스킬로 승격**합니다.

### 5-1. `.assistant_instructions.md` — 영환님 전역 규칙

`/Workspace/Users/{영환님}/.assistant/.assistant_instructions.md` 생성:

```markdown
# 이영환 Databricks 작업 기본 규칙

## 신원
- 소속: SK인천석유화학 P&C 팀
- 역할: HR Manager, HRBP 전환 중, 사내 AI 교육 리드
- 담당 영역: HR AX, 보상·교육·징계

## 데이터 접근 범위
- 카탈로그: personal_dev
- 스키마: {영환님 사번 기반 스키마}
- 공개 참고: samples.* (학습용)
- 금지: 타 사용자 스키마 접근

## 코딩 규칙
- 언어: PySpark + Spark SQL
- 주석: 한국어
- 변수명: snake_case
- 결과 출력: display()
- 컴퓨트: Serverless 고정

## 시각화 규칙
- 라이브러리: matplotlib 기본
- 차트 제목·축 레이블: 한국어
- 색상: SK 오렌지 팔레트
  - Primary: #F05023
  - Secondary: #FF8C42, #FFB380, #333333

## 데이터 보안 (회사 정책)
- 개인식별정보 컬럼 (이름, 주민번호, 계좌, 카드번호) 절대 SELECT 금지
- 급여 데이터는 집계 수준으로만 표시
- 징계·평가 원문은 요약으로만

## 응답 스타일
- 코드 단계별 한국어 주석 설명
- 결과 해석은 Facts(데이터)와 Opinion(해석) 분리
- 마지막에 확장 질문 2개 제시

## 하네스 원칙
- 새 과제는 Input/Output 정의부터
- 5단계 중 Context 또는 Evaluate 생략 시 이유 명시
- 단일 스킬로 시작, 반복 확인 후 서브에이전트 분리
```

### 5-2. 과제별 스킬 예시 — `hr-analytics/SKILL.md`

첫 과제를 성공적으로 끝냈다면 재사용 가능한 스킬로 승격:

```markdown
---
name: hr-analytics
description: HR 데이터(인원·이직·조직) 분석을 수행합니다. 월별·부서별·직급별 집계와 대시보드 구성. "이직률", "인원 현황", "조직 분석", "HR KPI" 관련 요청에 사용합니다.
---

# HR Analytics Skill (SK인천석유화학)

## 개요
personal_dev.{사번} 스키마의 HR 데이터를 분석하는 스킬입니다.

## 사용 가능한 테이블 (예시)
| 테이블 | 설명 | 주요 컬럼 |
|--------|------|-----------|
| hr_employee | 직원 마스터 | employee_id, dept_code, position, join_date, status |
| hr_separation | 퇴사 이력 | employee_id, sep_date, sep_type, sep_reason |
| hr_dept | 부서 마스터 | dept_code, dept_name, parent_dept |
| hr_silver_monthly_roster | 월별 재직 스냅샷 | year_month, employee_id, dept_code |
| hr_gold_monthly_turnover_rate | 월별 이직률 | year_month, dept_code, turnover_rate |

## 분석 수행 절차

### Step 1: 데이터 로드
```
catalog = "personal_dev"
schema = "{영환님 사번}"
df_emp = spark.table(f"{catalog}.{schema}.hr_employee")
df_sep = spark.table(f"{catalog}.{schema}.hr_separation")
```

### Step 2: 분석 유형별 집계
- 이직률: (퇴사자 / 월초 재직자) × 100, 정규직만
- 조직별: dept_code 조인 후 GROUP BY
- 시계열: year_month 기준 date_trunc

### Step 3: 시각화
- matplotlib, 한국어 레이블
- SK 오렌지 팔레트: #F05023, #FF8C42, #FFB380

## 비즈니스 규칙
- 이직률 분모: 월초 정규직 재직자 수
- 육아휴직·군입대는 이직에서 제외
- 분석 단위 기본: 본부 → 팀 드릴다운
- 최소 집계 단위: 5명 이상 (소수 노출 방지)

## 민감정보
- 직원명·주민번호·급여 절대 표시 금지
- 퇴사 사유는 카테고리 수준만 (개별 상세 금지)

## 예시

사용자: "올해 본부별 이직률 추이 보여줘"
→ hr_gold_monthly_turnover_rate에서 올해 12개월·본부 GROUP BY, 라인 차트

사용자: "[특정 부서]의 이직 원인 분석해줘"
→ 5명 미만이면 거절, 5명 이상이면 사유 카테고리 집계
```

### 5-3. ADR — Databricks 환경의 아키텍처 결정 기록

Databricks는 일반 하네스보다 설계 결정이 더 많이 생깁니다. Unity Catalog 구조, 컴퓨트 선택, Bronze/Silver/Gold 단계 설계 등 처음 보는 분이 "왜 이렇게 했지?"라고 물어볼 포인트가 많기 때문입니다.

**ADR이 특히 필요한 Databricks 결정들:**

| 결정 | ADR 필요 여부 |
|------|--------------|
| Silver/Gold 테이블을 나눈 이유 | 필수 |
| Serverless Warehouse vs Shared Cluster 선택 | 필수 |
| Genie Code Agent 모드 vs 단일 스킬 선택 | 필수 |
| 특정 카탈로그·스키마를 선택한 이유 | 권장 |
| 색상 코드 변경 | 불필요 |

**저장 위치**: `/Workspace/Users/{사번}/projects/{과제}/adr/NNN-{제목}.md`

**요청 프롬프트** (Genie Code에서):
```
이번 노트북 설계에서 내린 구조적 결정들(테이블 구조, 컴퓨트 선택,
스킬 분리 방식)을 ADR 문서로 기록해 줘.
adr/ 폴더에 저장해줘.
```

> **비개발자 팁**: ADR은 기술 문서가 아닙니다. "Silver 테이블을 만든 건 원본 데이터를 건드리지 않으려고" 같은 평범한 한국어로 써도 됩니다. 핵심은 나중에 AI나 동료가 읽었을 때 "아, 그래서 이렇게 했구나"라고 이해할 수 있는 것입니다.

### 5-4. Genie Space용 Instructions

회사 전체가 쓰는 Genie Space라면 지침을 강하게 걸어둬야 합니다:

```
[Genie Space Instructions 예시]

* 구체 기준이 모호하면 임의 정의하지 말고 사용자에게 되물을 것
* 이직률 정의는 항상 (퇴사자수 / 월초 재직자수) × 100, 정규직만
* 개인식별정보 컬럼(이름, 주민번호, 계좌) 조회 절대 금지
* 5명 미만 집계는 결과에서 제외 (k-익명성 확보)
* 부서 레벨: 본부(level 1) / 팀(level 2) / 파트(level 3)
* 기본 표시 단위: 본부. 사용자가 드릴다운 요청 시에만 하위로
```

---

## 6. 막히는 지점 대처법 (Databricks 특화)

| 증상 | 원인 추정 | 대처 |
|---|---|---|
| 노트북이 엉뚱한 카탈로그·스키마 사용 | 브리프에 명시 안 됨 | 브리프 2장 "Databricks 환경" 재확인 후 재실행 |
| Serverless 컴퓨트 선택 안 됨 | Genie Code가 자동 연결 못함 | 노트북 상단 드롭다운에서 수동 선택 |
| Genie Space가 임의로 정의 추가 | Instructions 미설정 | `.assistant_instructions.md` + Genie Instructions 동시 설정 |
| 같은 질문에 다른 결과 | Benchmark 미등록 | 5-3처럼 Benchmark에 Ground Truth 등록 |
| 벡터 서치 오프라인 | 엔드포인트 준비 중 | online 상태 될 때까지 대기 (10-20분) |
| 권한 부족 | 카탈로그·스키마 권한 | 데이터 팀에 요청 |

---

## 7. 회사 내 확산 팁 (동료에게 전달할 때)

영환님 본인이 3회 이상 성공한 뒤에 전달. 동료용 축소판:

### 축소판 3단 체크리스트

1. ☐ `.assistant_instructions.md` 개인 설정 (영환님 버전 복사 후 사번만 수정)
2. ☐ 첫 과제는 **단일 Notebook**으로 시작, 스킬 만들지 말 것
3. ☐ 3회 성공 후 반복 패턴 생기면 그때 SKILL.md로 승격

### 설명 1줄

> "Databricks에 업무 매뉴얼(스킬)을 붙여두면, 같은 분석을 반복할 때마다 품질이 같은 수준으로 나온다."

---

## 부록 A — 첫 과제 체크리스트 (프린트용)

```
[ ] 1. 브리핑룸에서 Kickoff (5-10분)
[ ] 2. 브리프 파일 확정 (영역·과제·Input·Output)
[ ] 3. Databricks 로그인 · Workspace 이동
[ ] 4. 새 노트북 생성 · Serverless 선택
[ ] 5. Genie Code 패널 열기 · Agent 모드
[ ] 6. 브리프 복붙 + 실행 프롬프트
[ ] 7. 6-Phase 관찰 · Accept all
[ ] 8. Run all · 에러 시 진단 버튼
[ ] 9. Gold 테이블 건수·샘플 확인
[ ] 10. 회고 기록 (99-retro-databricks-v1.md)
[ ] 11. ADR 작성 — 이번 과제에서 내린 구조적 결정 기록
     (Silver/Gold 분리 이유, 컴퓨트 선택 이유 등)
     요청: "이번 설계 결정을 ADR 문서로 남겨줘"
```

---

## 부록 B — 용어 사전 (Databricks 추가분)

| 용어 | 쉬운 뜻 |
|---|---|
| Unity Catalog | 모든 데이터·AI 자산의 관리 도구 |
| 3-Level Namespace | catalog.schema.table 필수 표기 |
| Serverless | 클릭 한 번으로 쓰는 공용 컴퓨트 |
| Warehouse | SQL 전용 Serverless 컴퓨트 |
| Notebook | 셀 단위로 코드 실행하는 작업 문서 |
| Genie Space | 테이블 연결형 자연어 Q&A |
| Genie Code | 코드·노트북 자동 생성 어시스턴트 |
| AI Playground | 여러 LLM 비교·에이전트 프로토타입 |
| Tool Calling | 모델이 함수를 직접 호출 (Python exec, Vector Search 등) |
| Endpoint | 배포된 모델·에이전트의 호출 주소 |
| Bronze/Silver/Gold | Raw → Cleansed → Aggregated 데이터 단계 |
| Vector Search | 문서 벡터화 후 유사도 검색 |
| RAG | 검색 기반 답변 생성 (문서 Q&A) |
| ADR | Architecture Decision Record. "왜 이 구조를 선택했나"를 기록하는 문서. Silver/Gold 분리 이유, 컴퓨트 선택 이유 등을 남겨두면 다음 세션에서 AI가 맥락을 즉시 이해함 |

---

## 맺음

이 가이드는 기본 하네스 가이드(Claude Code 기준)의 **Databricks 확장판**입니다. 핵심 철학은 동일하니, 기본 가이드를 먼저 숙지하신 뒤 이 가이드를 참조하세요.

### 3줄 핵심

1. **파일명만 다르고 철학은 같다** — Genie Code의 SKILL.md = Claude Code의 SKILL.md
2. **Databricks 특화는 3가지뿐** — Unity Catalog 3-level, Serverless, 민감정보 정책
3. **첫 과제는 단일 노트북으로** — 스킬 승격은 3회 성공 후

---

*작성: 이영환 × Claude · 2026-04-18*
