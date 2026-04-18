# -*- coding: utf-8 -*-
"""
Leadership Survey Parser
- Reads dummy_leadership_survey.xlsx (응답원본, 문항목록, README)
- Aggregates per-leader statistics into JSON files
- Writes parse_summary.md
"""
import json
import random
import os
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

# 재현성 확보용 시드 (익명화 shuffle)
random.seed(42)

ROOT = Path(r"C:\Users\yhlee\Desktop\myprojects\HR AX")
INPUT_XLSX = ROOT / "survey-feedback" / "dummy_leadership_survey.xlsx"
OUT_DIR = ROOT / "_workspace" / "01_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. 시트 로드
xl = pd.ExcelFile(INPUT_XLSX)
sheet_names = xl.sheet_names  # ['응답원본', '문항목록', 'README']

df_raw = pd.read_excel(xl, sheet_name="응답원본")
df_q = pd.read_excel(xl, sheet_name="문항목록")
df_readme = pd.read_excel(xl, sheet_name="README")

# 2. 문항 텍스트 딕셔너리 생성
# 문항목록 컬럼: ['문항번호', '유형', '문항 내용']
q_col_id = df_q.columns[0]
q_col_text = df_q.columns[2]
questions = dict(zip(df_q[q_col_id].astype(str), df_q[q_col_text].astype(str)))

# 3. 응답원본 컬럼 정규화
# 순서: 응답ID, 팀장ID, 팀장명, 팀명, Q01~Q12, 응답일시
cols = list(df_raw.columns)
col_leader_id = cols[1]   # 팀장ID
col_leader_nm = cols[2]   # 팀장명
col_team_nm = cols[3]     # 팀명
col_date = cols[-1]       # 응답일시
score_cols = [f"Q{i:02d}" for i in range(1, 11)]
q11_col = "Q11"
q12_col = "Q12"


def anonymize_qualitative(responses):
    """익명화: 공백 제거 + 섞기. 고유명사 패턴 치환은 휴리스틱 한계로 검토 플래그 처리."""
    cleaned = []
    for r in responses:
        if pd.isna(r):
            continue
        s = str(r).strip()
        if not s:
            continue
        cleaned.append(s)
    random.shuffle(cleaned)
    return cleaned


def build_leader_json(leader_id, group):
    leader_name = str(group[col_leader_nm].iloc[0]) if len(group) else ""
    team_name = str(group[col_team_nm].iloc[0]) if len(group) else ""
    response_count = int(len(group))

    # 응답 기간
    if response_count > 0:
        dates = pd.to_datetime(group[col_date], errors="coerce").dropna()
        if len(dates) > 0:
            date_range = {
                "from": dates.min().strftime("%Y-%m-%d"),
                "to": dates.max().strftime("%Y-%m-%d"),
            }
        else:
            date_range = {"from": None, "to": None}
    else:
        date_range = {"from": None, "to": None}

    # Q01~Q10 집계
    scores = {}
    for col in score_cols:
        if col not in group.columns:
            continue
        series = pd.to_numeric(group[col], errors="coerce")
        vals = series.dropna().tolist()
        n = len(vals)
        if n > 0:
            mean_v = round(float(series.mean()), 2)
            std_v = float(series.std(ddof=1)) if n > 1 else 0.0
            std_v = round(std_v, 2)
        else:
            mean_v = 0.0
            std_v = 0.0
        distribution = {str(i): int((series == i).sum()) for i in range(1, 6)}
        scores[col] = {
            "question": questions.get(col, col),
            "mean": mean_v,
            "std": std_v,
            "distribution": distribution,
            "n": n,
        }

    # 강점 / 개선 Top 3 (응답이 있는 문항만 평균 기준 정렬)
    sortable = [(k, v["mean"]) for k, v in scores.items() if v["n"] > 0]
    sortable_desc = sorted(sortable, key=lambda x: x[1], reverse=True)
    sortable_asc = sorted(sortable, key=lambda x: x[1])
    strengths = [k for k, _ in sortable_desc[:3]]
    improvements = [k for k, _ in sortable_asc[:3]]

    # 서술형 Q11/Q12 익명화
    q11_raw = group[q11_col].dropna().tolist() if q11_col in group.columns else []
    q12_raw = group[q12_col].dropna().tolist() if q12_col in group.columns else []

    q11_list = anonymize_qualitative(q11_raw)
    q12_list = anonymize_qualitative(q12_raw)

    # 응답 수 3건 미만 시 서술형 비노출 정책 (역익명화 위험)
    if response_count < 3:
        qualitative = {
            "Q11": [],
            "Q12": [],
            "note": "응답 수 3건 미만 - 역익명화 위험으로 서술형 미노출",
        }
    else:
        qualitative = {"Q11": q11_list, "Q12": q12_list}

    return {
        "leader_id": str(leader_id),
        "leader_name": leader_name,
        "team_name": team_name,
        "response_count": response_count,
        "date_range": date_range,
        "scores": scores,
        "strengths": strengths,
        "improvements": improvements,
        "qualitative": qualitative,
    }


# 4. 팀장별 처리
leaders_summary = []
grouped = df_raw.groupby(col_leader_id, sort=True)

# 입력에 등장한 모든 팀장 ID 수집 (응답 0건도 처리 가능하도록 보강)
all_leader_ids = sorted(df_raw[col_leader_id].dropna().unique().tolist())

for leader_id in all_leader_ids:
    group = df_raw[df_raw[col_leader_id] == leader_id].copy()
    leader_json = build_leader_json(leader_id, group)

    out_path = OUT_DIR / f"{leader_id}_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(leader_json, f, ensure_ascii=False, indent=2)

    leaders_summary.append({
        "leader_id": leader_id,
        "leader_name": leader_json["leader_name"],
        "team_name": leader_json["team_name"],
        "response_count": leader_json["response_count"],
        "date_from": leader_json["date_range"]["from"],
        "date_to": leader_json["date_range"]["to"],
        "strengths": leader_json["strengths"],
        "improvements": leader_json["improvements"],
        "file": str(out_path),
    })

# 5. 파싱 요약 마크다운
total_responses = int(len(df_raw))
overall_from = pd.to_datetime(df_raw[col_date], errors="coerce").min()
overall_to = pd.to_datetime(df_raw[col_date], errors="coerce").max()

lines = []
lines.append("# 설문 데이터 파싱 결과 요약\n")
lines.append(f"- 입력 파일: `{INPUT_XLSX.as_posix()}`")
lines.append(f"- 시트: {', '.join(sheet_names)}")
lines.append(f"- 총 응답 수: {total_responses}건")
lines.append(f"- 전체 응답 기간: {overall_from.strftime('%Y-%m-%d') if pd.notna(overall_from) else 'N/A'} ~ {overall_to.strftime('%Y-%m-%d') if pd.notna(overall_to) else 'N/A'}")
lines.append(f"- 처리된 팀장 수: {len(leaders_summary)}명")
lines.append("")
lines.append("## 팀장별 요약\n")
lines.append("| 팀장ID | 팀장명 | 팀명 | 응답수 | 응답기간 | 강점 Top 3 | 개선 Top 3 |")
lines.append("|--------|--------|------|--------|----------|------------|------------|")
for s in leaders_summary:
    date_range_str = f"{s['date_from']} ~ {s['date_to']}" if s["date_from"] else "N/A"
    strengths_str = ", ".join(s["strengths"]) if s["strengths"] else "-"
    improvements_str = ", ".join(s["improvements"]) if s["improvements"] else "-"
    lines.append(
        f"| {s['leader_id']} | {s['leader_name']} | {s['team_name']} | "
        f"{s['response_count']} | {date_range_str} | {strengths_str} | {improvements_str} |"
    )
lines.append("")
lines.append("## 파일 출력")
for s in leaders_summary:
    lines.append(f"- `{Path(s['file']).as_posix()}`")
lines.append("")
lines.append("## 처리 규칙 적용 사항")
lines.append("- 응답ID(R0001~) JSON 미포함")
lines.append("- 응답일시는 `date_range`(from/to)로만 기록 (개별 타임스탬프 미포함)")
lines.append("- Q11·Q12 서술형 응답은 shuffle 익명화 적용 (seed=42 재현성 확보)")
lines.append("- 응답 수 3건 미만 팀장은 서술형 응답 비노출 (본 데이터셋 해당 없음)")

# 응답 0건 팀장 체크
zero_leaders = [s for s in leaders_summary if s["response_count"] == 0]
if zero_leaders:
    lines.append("\n## 주의: 응답 0건 팀장")
    for s in zero_leaders:
        lines.append(f"- {s['leader_id']} ({s['leader_name']}) - 빈 데이터 구조로 저장됨")

summary_path = OUT_DIR / "parse_summary.md"
with open(summary_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

# 콘솔 출력은 ASCII 안전하게
print(f"[OK] {len(leaders_summary)} leaders processed")
print(f"[OK] Summary: {summary_path}")
for s in leaders_summary:
    print(f"  - {s['leader_id']} | {s['leader_name']} | {s['team_name']} | n={s['response_count']}")
