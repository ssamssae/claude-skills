---
name: trend
description: Dev Trend Curator 실행. Hacker News + GitHub 최신 트렌드에서 Flutter/indie/Claude 키워드 매칭 결과를 ~/trend-curator/daily/YYYY-MM-DD.md 에 누적 저장하고 텔레그램으로 요약 전송. 사용자가 "트렌드", "오늘 뭐 핫함", "dev trend", "/trend" 라고 하면 이 스킬을 실행한다.
---

# /trend — Dev Trend Curator

매일 돌려도 되고, 필요할 때 수동으로 호출해도 되는 **자동 생산형 큐레이터**.

## 실행 규칙

1. 기본 실행:
   ```bash
   python3 ~/trend-curator/curator.py --telegram
   ```
   - Hacker News top 30 + GitHub 신규 레포(최근 2일, stars 정렬 30건) 수집
   - `~/trend-curator/config.json` 의 keywords 로 필터
   - `~/trend-curator/daily/YYYY-MM-DD.md` 저장 (날짜별 누적)
   - `~/trend-curator/raw/YYYY-MM-DD.json` 원본 저장
   - `~/trend-curator/INDEX.md` 업데이트
   - 텔레그램 요약 전송

2. 실행 후 **완료 보고** (터미널 출력 + 텔레그램 별도 reply 불필요 — 스크립트가 이미 보냄):
   - HN/GH 매칭 건수
   - 저장된 파일 경로
   - 총 누적 리포트 개수 (`ls ~/trend-curator/daily/*.md | wc -l`)

3. `$ARGUMENTS` 처리:
   - `--no-telegram` 포함 시: `--telegram` 플래그 생략 (파일만 저장)
   - `--summary` 포함 시: 요약을 stdout에도 출력
   - `--print` 포함 시: 전체 리포트를 stdout에 출력
   - 날짜 문자열(YYYY-MM-DD) 포함 시: `--date <날짜>` 로 전달

## 금지

- curator.py 수정은 이 스킬에서 하지 마라. 사용자가 명시적으로 요청할 때만.
- 텔레그램 전송은 curator.py 내장 경로만 쓴다 (중복 전송 금지).
- config.json 의 keywords 를 자동으로 바꾸지 마라. 사용자가 "트렌드에 OO 추가" 라고 해야 수정.

## 구조 요약

```
~/trend-curator/
├── curator.py       # 메인
├── config.json      # keywords, 수집 개수
├── daily/           # YYYY-MM-DD.md (날짜별 누적)
├── raw/             # YYYY-MM-DD.json (원본)
└── INDEX.md         # 날짜별 링크
```

## 다음 개선 포인트

- `stderr.log` 에 실패 기록 (API rate limit, 네트워크 오류)
- Claude API 로 하루치 리포트 압축 요약 (1-paragraph TL;DR)
- Product Hunt / dev.to 소스 추가
