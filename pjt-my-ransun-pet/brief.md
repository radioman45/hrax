# 브리프 — AI 랜선펫

**영역**: 업무 (AX 실험실 트랙)
**작성일**: 2026-04-28
**버전**: v1

---

## 1. 과제 정의

- **과제명**: AI 랜선펫
- **Input**: 사용자 발화 + 정기 체크인 응답 (이모지·한 줄·자유 대화)
- **Output**: 3층 구조
  - 사용자(실시간): 펫 응답 메시지 + 상태 이미지(5~6단계)
  - 사용자(주간): 본인 전용 "이번 주 나의 상태 리포트"
  - HR(월간): 익명 집계 참여율·감정 분포·키워드 TOP10 (부서간 비교 리포트 제외)
- **Done 기준**: 한 팀(10명 이상) 2주 파일럿 완료, 응답률 50%+, 사용자 만족도(자유응답 기반) 정성 검증

## 2. 5단계 매뉴얼

### Clarify
- 사번/비번 로그인 = SSO 연동 가능한지 IT보안 사전 확인
- 펫 이름은 사용자가 직접 명명 (애착 강화)
- "체크인 안 하는 사용자"에게 펫이 어디까지 push할지 톤 정의 필요

### Context Gather
- HR_AX.md (Lighthouse #1, #3 / Quick-win Pool: 팀원 이상징후, Motivation)
- WellCub 디자인 컨셉 (참고 무드보드 수준)
- 사내 EAP/펄스서베이 기존 솔루션 — 중복·차별점 파악

### Plan
- Week 1: Databricks 데이터 코어 (Delta Lake 대화 로그 테이블, Mosaic AI 펫 프롬프트, opt-in 구조)
- Week 2: Teams Bot 연동 + Adaptive Card UI + 주간/월간 리포트 쿼리
- 파일럿 운영 2주 → 회고 → Phase 2 진입 판단

### Generate
- Databricks 풀스택 (Unity Catalog · Delta Lake · Mosaic AI · Model Serving · AI/BI)
- Teams 개인 채팅 Bot (최소 Azure Bot 등록만, 백엔드 = Databricks Endpoint)
- 펫 이미지 5~6장 (Unity Catalog Volume 저장)

### Evaluate
- 사용자 응답률, 자유응답 솔직도, 재사용 의향
- 프라이버시 침해 우려 인터뷰 (파일럿 종료 후)
- HR 익명 집계 리포트의 실제 활용 가치 검증

## 3. 제약사항

- **민감정보**: 대화 원문은 사용자 본인만 열람. HR은 익명 집계만. Unity Catalog row-level security 필수
- **인증**: 사번/비번 로그인 = 사내 SSO 연동 (별도 비번 X)
- **프라이버시 라인**: 부서간 비교 리포트 제외, opt-in 방식, 탈퇴 시 데이터 삭제 보장
- **금지**: Graph API 객관 데이터 수집 금지(Phase 2 보류), 개인 식별 가능 형태로 HR 리포트 생성 금지, 노조법/개인정보보호법 검토 미완료 시 전사 확산 금지

## 4. Phase 2 보류 항목

- Microsoft Graph API 연동 (회의·메일·Teams 활동량 객관 데이터)
- 발동 조건: 파일럿 사용 정착(응답률 안정적 50%+ 3개월 유지) 후 검토

## 5. 포인터

- Databricks 아키텍처 상세: 별도 기술 노트 (Mosaic AI / Model Serving / Vector Search)
- Teams Bot 등록 절차: MS Learn 공식 문서
- 사내 EAP·펄스서베이 현황: HR Analytics 팀 확인
- Lighthouse 매핑: HR_AX.md 5개 Lighthouse 중 #1(팀장 Mgmt) #3(개인화 EX)

---