# HR AX — 프로젝트 허브

**목표:** AI 기반 HR Transform — 팀장 지원 · 구성원 지원 · HR 운영 효율화

---

## 프로젝트 구조

각 프로젝트는 **독립 폴더에서 `claude` 실행**. 에이전트·스킬은 폴더 안 `.claude/`에 격리.

| 폴더 | HR AX 영역 | 진행 상태 | Quick-Win 과제 |
|------|-----------|----------|----------------|
| `[PJT] survey-feedback/` | 팀장 Mgmt. 강화 | ✅ 운영 중 | 리더십 Survey Feedback Report |
| `[PJT] Leadership/` | 팀장 Mgmt. 강화 | 🔜 준비 중 | 성과 피드백 제안 AI, 리더십 Self 진단 |
| `[PJT] HR-operation/` | HR 운영 효율화 | 🔜 준비 중 | 의료비 판독 AI, 급여 이레귤러 검증 |

---

## 실행 방법

```bash
# survey-feedback 작업 시
cd "HR AX/[PJT] survey-feedback" && claude

# Leadership 작업 시
cd "HR AX/[PJT] Leadership" && claude

# HR-operation 작업 시
cd "HR AX/[PJT] HR-operation" && claude
```

---

## 공용 자산 (루트 수준)

- `harness-engineering-guide.md` — 하네스 구축 가이드 (전 프로젝트 공통)
- `databricks-harness-guide.md` — Databricks 환경 가이드
- `HR AX.md` — 전체 과제 로드맵 원본
- `.claude/settings.local.json` — Claude Code 권한 설정 (전 프로젝트 공통)

---

## 새 과제 시작 절차

1. 브리핑룸에서 `00-brief-{과제슬러그}-v1.md` 완성
2. 해당 프로젝트 폴더에 브리프 저장
3. 그 폴더에서 `claude` 실행
4. `"이 브리프로 하네스 구축해줘"` 입력

---

## 변경 이력

| 날짜 | 변경 내용 | 사유 |
|------|----------|------|
| 2026-04-18 | 단일 폴더 → 멀티 프로젝트 구조 전환 | Leadership, HR-operation 추가 대비 |
| 2026-04-18 | survey-feedback .claude/ 격리 | 프로젝트 간 에이전트 충돌 방지 |
