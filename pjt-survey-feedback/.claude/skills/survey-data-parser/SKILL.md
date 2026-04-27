---
name: survey-data-parser
description: "리더십 설문 엑셀(dummy_leadership_survey.xlsx)을 파싱하여 팀장별 집계 JSON을 생성하는 스킬. 응답원본/문항목록/README 시트 파싱, Q01~Q10 통계 집계, 강점/개선 Top 3 계산, Q11·Q12 익명화까지 포함. 이 설문 데이터를 다루거나, 팀장별 집계 데이터가 필요하거나, 엑셀 파싱 후 JSON을 만들어야 할 때 반드시 이 스킬을 사용."
---

# Survey Data Parser

`dummy_leadership_survey.xlsx`를 파싱하여 팀장 10명의 피드백 집계 JSON을 생성한다.

## config 로딩 (필수 — 스킬 시작 전 실행)

익명화 설정과 집계 기준을 `_workspace/config.json`에서 읽는다. 파일이 없으면 오케스트레이터에게 알리고 중단한다.

```python
import json

with open("_workspace/config.json", encoding="utf-8") as f:
    cfg = json.load(f)

anon   = cfg["anonymization"]
layout = cfg["layout"]

SHUFFLE_RESPONSES      = anon["shuffle_responses"]
MASK_PROPER_NOUNS      = anon["mask_proper_nouns"]
HIDE_RESPONSE_ID       = anon["hide_response_id"]
TOP_N                  = layout["top_n"]
MIN_RESP_QUALITATIVE   = layout["min_responses_for_qualitative"]
```

## 파일 구조

| 시트명 | 내용 |
|--------|------|
| `응답원본` | 응답 53건. 컬럼: 응답ID, 팀장ID, 팀장명, 팀명, 응답일시, Q01~Q10(1~5 정수), Q11(텍스트), Q12(텍스트) |
| `문항목록` | Q01~Q12 문항 전문 |
| `README` | 데이터 구조 안내 |

## 파싱 절차

```python
import pandas as pd
from datetime import datetime

# 1. 시트 로드
df_raw = pd.read_excel("dummy_leadership_survey.xlsx", sheet_name="응답원본")
df_q   = pd.read_excel("dummy_leadership_survey.xlsx", sheet_name="문항목록")

# 2. 문항 텍스트 딕셔너리 생성
# df_q 컬럼: 문항ID, 문항텍스트
questions = dict(zip(df_q["문항ID"], df_q["문항텍스트"]))

# 3. 팀장별 그룹핑
for leader_id, group in df_raw.groupby("팀장ID"):
    build_leader_json(leader_id, group, questions)
```

## 집계 로직

### Q01~Q10 척도 집계

```python
score_cols = [f"Q{i:02d}" for i in range(1, 11)]

scores = {}
for col in score_cols:
    vals = group[col].dropna().tolist()
    scores[col] = {
        "question": questions.get(col, col),
        "mean": round(group[col].mean(), 2),
        "std": round(group[col].std(), 2),
        "distribution": {str(i): int((group[col] == i).sum()) for i in range(1, 6)},
        "n": len(vals)
    }
```

### 강점 / 개선 필요 Top 3

```python
sorted_by_mean = sorted(scores.items(), key=lambda x: x[1]["mean"], reverse=True)
strengths     = [k for k, _ in sorted_by_mean[:TOP_N]]    # config.layout.top_n
improvements  = [k for k, _ in sorted_by_mean[-TOP_N:]]   # config.layout.top_n (역순)
```

### 응답 기간 (날짜 범위만)

```python
dates = pd.to_datetime(group["응답일시"])
date_range = {
    "from": dates.min().strftime("%Y-%m-%d"),
    "to":   dates.max().strftime("%Y-%m-%d")
}
```

### Q11·Q12 익명화

서술형 응답은 아래 규칙을 적용하여 저장한다:
- 응답자 번호·순서 표시 금지 (R001, 1번째 응답자 등)
- 고유명사(사람 이름, 팀 이름)가 포함된 경우 `[이름]` `[팀명]`으로 치환
- 응답 목록은 순서를 섞어(shuffle) 저장하여 순서로 응답자를 추적할 수 없게 한다

```python
import random

def anonymize_qualitative(responses: list[str]) -> list[str]:
    cleaned = [r.strip() for r in responses if r and str(r).strip()]
    if SHUFFLE_RESPONSES:        # config.anonymization.shuffle_responses
        random.shuffle(cleaned)
    return cleaned

q11_responses = anonymize_qualitative(group["Q11"].dropna().tolist())
q12_responses = anonymize_qualitative(group["Q12"].dropna().tolist())
```

## 출력 JSON 스키마

```json
{
  "leader_id": "L001",
  "leader_name": "홍길동",
  "team_name": "전략팀",
  "response_count": 5,
  "date_range": { "from": "2026-03-01", "to": "2026-03-15" },
  "scores": {
    "Q01": {
      "question": "명확한 방향성과 목표를 제시한다",
      "mean": 4.2,
      "std": 0.75,
      "distribution": {"1": 0, "2": 0, "3": 1, "4": 2, "5": 2},
      "n": 5
    }
  },
  "strengths": ["Q03", "Q07", "Q01"],
  "improvements": ["Q09", "Q05", "Q10"],
  "qualitative": {
    "Q11": ["잘하는 점 응답1(익명화)", "잘하는 점 응답2(익명화)"],
    "Q12": ["개선 점 응답1(익명화)", "개선 점 응답2(익명화)"]
  }
}
```

## 주의사항

- `leader_name`, `team_name`은 JSON에 포함하나 리포트 생성 외 용도로 사용 금지
- `qualitative` 응답에 익명화가 불완전한 것으로 의심되면 해당 응답 전체를 `[익명화 검토 필요]`로 표시
- 응답 수가 3건 미만인 팀장은 서술형 응답을 리포트에 표시하지 않음 (역익명화 위험)
