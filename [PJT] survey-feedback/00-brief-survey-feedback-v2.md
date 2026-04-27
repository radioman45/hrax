# 브리프 — 리더십 Survey Feedback Report 자동화

**영역**: 업무
**작성일**: 2026-04-18 (v2 업데이트: 2026-04-28)
**버전**: v2

---

## 1. 과제 정의

- **과제명**: 리더십 Survey Feedback Report 자동화 (웹 데모 → Databricks 이관)
- **Input**: 통합 엑셀 1장 (응답 53건 × 팀장 10명, Q01~Q10 5점 척도 + Q11·Q12 서술형)
  - 시트 구조: `응답원본` (응답ID·팀장ID·팀장명·팀명·Q01~Q12·응답일시), `문항목록`, `README`
  - "실"은 별도 컬럼이 없어 팀명 prefix 기반 자동 추출 (예: `운영1팀`/`운영2팀` → `운영실`, `안전환경팀` → `안전환경실`)
- **Output (1차 데모)**: 단일 HTML 파일 — 드롭다운 선택 시 실별/팀장별 피드백 리포트 화면 표시 + PDF 인쇄/저장
- **Output (2차, Databricks)**: 사내 VDI에서 엑셀 업로드 → 동일 구조 리포트를 사내망 웹앱으로 제공
- **Done 기준 (1차)**: 로컬 HTML 데모로 샘플 리포트 사용자 승인
- **Done 기준 (2차)**: Databricks 환경 이관 후 실제 사내 데이터로 검증, 무작위 2건 스폿체크 통과

## 2. 5단계 매뉴얼

### Clarify
본 브리프 대화로 완료. 재질의 불필요.

### Context Gather
- 업로드 파일: `dummy_leadership_survey.xlsx` (시트: 응답원본/문항목록/README)
- 1차 데모 스택: HTML + CSS + 바닐라 JS (외부 의존성 0, 사내 VDI에서 로컬 더블클릭 실행 가능)
- 2차 운영 스택: Databricks (Python/PySpark + Streamlit 또는 Databricks Apps), 사내 파일 업로드 채널 사용

### Plan

**1차 (완료) — 로컬 HTML 데모**
- 단일 파일 `output/feedback_report_demo.html`
- 더미 엑셀 데이터를 JS 상수로 임베딩 (사내 VDI에서 파일 업로드 불가능한 환경 가정)
- 상단 드롭다운: `리포트 선택...` / 실별 그룹 / 팀장별 그룹
- 선택 시 해당 리포트만 표시, 미선택 시 안내문만
- `PDF 인쇄/저장` 버튼 → `window.print()` (`@media print`로 헤더·툴바 숨김, 리포트별 page-break)

**2차 — Databricks 이관**
- 입력: 사내 파일 업로드 위젯으로 `*.xlsx` 수신 (사내망 채널 OK)
- 처리: pandas/openpyxl로 파싱 → 팀장별·실별 집계
- 출력 옵션 A: Streamlit/Databricks Apps에서 동일 UI(드롭다운 + 리포트 + PDF)
- 출력 옵션 B: docx 스킬로 팀장별 Word 10개 일괄 생성 (기존 v1 산출물과 호환)
- 권한·로깅: 사내 보안 정책에 따라 접근 로그 기록, 응답 원본 별도 저장 금지

**리포트 구성 (공통)**
- 헤더: 팀장명·실·팀·응답자 수
- KPI 4종: 종합 평균, 만족도(Q10), 강점 Top1 문항, 개선 Top1 문항
- ①문항별 점수 요약 (Q01~Q10 평균·N·분포)
- ②강점 Top 3 / 개선 Top 3 (척도 상위·하위 3개)
- ③서술형 응답 (Q11·Q12, 익명화·원문 인용)
- 실별 리포트는 추가로 소속 팀장 랭킹 테이블 포함

### Generate
- 1차: 단일 HTML 파일 (완료)
- 2차: Databricks 노트북 + Streamlit 앱 또는 Databricks Apps 배포 단위로 패키징
  - 파일명 규칙(Word 산출물): `leadership_feedback_[팀장ID]_[팀장명].docx`

### Evaluate
1) 1차 HTML 데모 — 사용자 육안 검수 (드롭다운 동작, PDF 인쇄 레이아웃, 익명성)
2) 2차 Databricks — 실제 사내 엑셀 업로드 → 결과 비교, 무작위 2개 팀장 리포트 스폿체크

## 3. 제약사항

- **실행 환경**: 사내 VDI (외부 인터넷 차단). 1차 데모는 CDN 의존성 없이 단일 HTML로 제공.
  2차 Databricks는 사내망 내부에서 동작, 파일 업로드는 사내 승인 채널만 사용.
- **민감정보**: 응답ID 리포트 미노출. 응답일시는 기간 범위(YYYY-MM-DD ~ YYYY-MM-DD)만 표시
- **익명화**: 서술형은 응답자 식별 단서 제거. 원문 인용 시에도 응답자 번호·순서 비공개
- **포맷**: 1차 HTML(화면 + PDF 인쇄), 2차 HTML/PDF 또는 DOCX 병행
- **금지**: 팀장명·팀명·원문 응답 데이터 외부 반출, 실명 데이터 개인 드라이브 저장,
  더미가 아닌 실데이터를 로컬 데모 HTML에 임베딩하는 행위

## 4. 포인터

- 원본 데이터(더미): `dummy_leadership_survey.xlsx`
- 1차 데모 산출물: `output/feedback_report_demo.html` (더미 데이터 임베딩 + 드롭다운 + PDF)
- 2차 Databricks 이관 시 참고:
  - 엑셀 파싱: pandas `read_excel(sheet_name=['응답원본','문항목록'])`
  - "실" 매핑: `팀명.replace(/\d+팀$/,'').replace(/팀$/,'') + '실'` (실명 매핑 테이블 별도 관리 권장)
  - UI 옵션: Streamlit `st.file_uploader` + `st.selectbox` + `st.dataframe`/HTML 임베딩
  - PDF: `weasyprint` 또는 브라우저 인쇄

## 5. v2 추가 규칙 (Lv1.5 → Lv2 업그레이드)
- 모든 설정은 _workspace/config.json에서 읽는다.
- QA 기준은 _workspace/qa-checklist.json에서 읽는다.
- 스킬 내부에 상수를 하드코딩하지 않는다.
- 설정 변경 시 스킬 수정 없이 config만 수정.