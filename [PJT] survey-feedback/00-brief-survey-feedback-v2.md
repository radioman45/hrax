# 브리프 — 리더십 Survey Feedback Report 자동화

**영역**: 업무
**작성일**: 2026-04-18
**버전**: v1

---

## 1. 과제 정의

- **과제명**: 리더십 Survey Feedback Report 자동화
- **Input**: 통합 엑셀 1장 (응답 53건 × 팀장 10명, Q01~Q10 5점 척도 + Q11·Q12 서술형)
- **Output**: 팀장별 DOCX 10개, 각 2페이지
- **Done 기준**: 샘플 1개(L001) 사용자 승인 → 나머지 9개 일괄 생성 → 무작위 2개 스폿체크 통과

## 2. 5단계 매뉴얼

### Clarify
본 브리프 대화로 완료. 재질의 불필요.

### Context Gather
- 업로드 파일: `dummy_leadership_survey.xlsx` (시트: 응답원본/문항목록/README)
- 스킬: `xlsx`(데이터 파싱), `docx`(Word 생성)

### Plan
샘플 팀장 1명(L001) 먼저 생성 → 사용자 검토·확정 → 나머지 9개 일괄.
리포트 구성 3섹션: ①문항별 점수 요약(Q01~Q10 평균·분포)
②강점 Top 3 / 개선 필요 Top 3 (척도 상위·하위 3개)
③서술형 응답 핵심 요지 (Q11·Q12, 익명화)

### Generate
pandas로 엑셀 파싱 → 팀장별 데이터 집계 → `docx` 스킬로 Word 10개 생성.
파일명 규칙: `leadership_feedback_[팀장ID]_[팀장명].docx`

### Evaluate
1) 샘플 1개 사용자 육안 검수 (2페이지 분량·가독성·익명성)
2) 전체 완료 후 10개 중 무작위 2개 스폿체크

## 3. 제약사항

- **민감정보**: 응답ID 리포트 미노출. 응답일시는 기간 범위(YYYY-MM-DD ~ YYYY-MM-DD)만 표시
- **익명화**: 서술형은 응답자 식별 단서 제거. 원문 인용 시에도 응답자 번호·순서 비공개
- **포맷**: 내부 HR 문서 기본 DOCX (IPC 브랜드 PPT 규칙은 해당 없음)
- **금지**: 팀장명·팀명·원문 응답 데이터 외부 반출, 실명 데이터 개인 드라이브 저장

## 4. 포인터

- 원본 데이터: `/mnt/user-data/uploads/dummy_leadership_survey.xlsx`
- Word 생성 규칙: `docx` 스킬 참조
- 엑셀 파싱 규칙: `xlsx` 스킬 참조

## 5. v2 추가 규칙 (Lv1.5 → Lv2 업그레이드)
- 모든 설정은 _workspace/config.json에서 읽는다.
- QA 기준은 _workspace/qa-checklist.json에서 읽는다.
- 스킬 내부에 상수를 하드코딩하지 않는다.
- 설정 변경 시 스킬 수정 없이 config만 수정.