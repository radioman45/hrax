# survey-feedback — Claude Code 가이드

**상위 프로젝트:** HR AX > 팀장 Mgmt. 강화 > Phase 1 Quick-Win

## 하네스: 리더십 Survey Feedback Report 자동화

**목표:** `dummy_leadership_survey.xlsx` → 팀장별 DOCX 리포트 10부 자동 생성

**트리거:** 설문 리포트 생성, 팀장 피드백 DOCX, 리포트 재생성 등 요청 시 `survey-feedback-orchestrator` 스킬을 사용하라.

**실행 방법:** 이 폴더(`survey-feedback/`)에서 `claude` 실행

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-04-18 | 초기 구성 | 전체 | 브리프 v1 기반 신규 구축 |
| 2026-04-18 | 브랜드 색상 SK Orange→검정 | feedback-report-writer | 사용자 요청 |
| 2026-04-18 | QA 색상 체크 기준 업데이트 | qa-reviewer | 색상 변경 오탐 수정 |
| 2026-04-18 | v2 업그레이드: config 외부화 | 스킬 3개 + qa-reviewer | 설정 단일화 |
| 2026-04-18 | ADR 자동 생성 추가 | survey-feedback-orchestrator | 아키텍처 결정 기록 |
| 2026-04-18 | 프로젝트 폴더 분리 | 전체 | HR AX 멀티 프로젝트 구조 전환 |
