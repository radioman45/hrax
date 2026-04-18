# 설문 데이터 파싱 결과 요약

- 입력 파일: `C:/Users/yhlee/Desktop/myprojects/HR AX/survey-feedback/dummy_leadership_survey.xlsx`
- 시트: 응답원본, 문항목록, README
- 총 응답 수: 53건
- 전체 응답 기간: 2026-04-01 ~ 2026-04-17
- 처리된 팀장 수: 10명

## 팀장별 요약

| 팀장ID | 팀장명 | 팀명 | 응답수 | 응답기간 | 강점 Top 3 | 개선 Top 3 |
|--------|--------|------|--------|----------|------------|------------|
| L001 | 김민수 | 운영1팀 | 4 | 2026-04-04 ~ 2026-04-07 | Q01, Q05, Q10 | Q09, Q02, Q07 |
| L002 | 이지영 | 운영2팀 | 6 | 2026-04-02 ~ 2026-04-17 | Q01, Q03, Q04 | Q07, Q02, Q03 |
| L003 | 박성호 | 기술1팀 | 5 | 2026-04-01 ~ 2026-04-07 | Q10, Q08, Q06 | Q02, Q05, Q09 |
| L004 | 최유진 | 기술2팀 | 4 | 2026-04-02 ~ 2026-04-13 | Q10, Q01, Q05 | Q07, Q03, Q04 |
| L005 | 정현우 | 안전환경팀 | 7 | 2026-04-01 ~ 2026-04-16 | Q03, Q04, Q01 | Q06, Q07, Q08 |
| L006 | 한소연 | 공정기술팀 | 5 | 2026-04-03 ~ 2026-04-11 | Q05, Q02, Q06 | Q04, Q07, Q01 |
| L007 | 오재철 | 생산관리팀 | 7 | 2026-04-07 ~ 2026-04-15 | Q03, Q01, Q08 | Q07, Q09, Q04 |
| L008 | 신혜원 | 품질팀 | 7 | 2026-04-01 ~ 2026-04-15 | Q06, Q03, Q09 | Q01, Q05, Q04 |
| L009 | 윤태경 | 설비관리팀 | 4 | 2026-04-09 ~ 2026-04-10 | Q10, Q04, Q02 | Q03, Q09, Q05 |
| L010 | 강서진 | 인사기획팀 | 4 | 2026-04-01 ~ 2026-04-14 | Q04, Q05, Q08 | Q03, Q01, Q07 |

## 파일 출력
- `C:/Users/yhlee/Desktop/myprojects/HR AX/_workspace/01_data/L001_data.json`
- `C:/Users/yhlee/Desktop/myprojects/HR AX/_workspace/01_data/L002_data.json`
- `C:/Users/yhlee/Desktop/myprojects/HR AX/_workspace/01_data/L003_data.json`
- `C:/Users/yhlee/Desktop/myprojects/HR AX/_workspace/01_data/L004_data.json`
- `C:/Users/yhlee/Desktop/myprojects/HR AX/_workspace/01_data/L005_data.json`
- `C:/Users/yhlee/Desktop/myprojects/HR AX/_workspace/01_data/L006_data.json`
- `C:/Users/yhlee/Desktop/myprojects/HR AX/_workspace/01_data/L007_data.json`
- `C:/Users/yhlee/Desktop/myprojects/HR AX/_workspace/01_data/L008_data.json`
- `C:/Users/yhlee/Desktop/myprojects/HR AX/_workspace/01_data/L009_data.json`
- `C:/Users/yhlee/Desktop/myprojects/HR AX/_workspace/01_data/L010_data.json`

## 처리 규칙 적용 사항
- 응답ID(R0001~) JSON 미포함
- 응답일시는 `date_range`(from/to)로만 기록 (개별 타임스탬프 미포함)
- Q11·Q12 서술형 응답은 shuffle 익명화 적용 (seed=42 재현성 확보)
- 응답 수 3건 미만 팀장은 서술형 응답 비노출 (본 데이터셋 해당 없음)