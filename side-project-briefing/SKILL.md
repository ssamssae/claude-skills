---
name: side-project-briefing
description: (수동 호출 전용) 사이드 프로젝트 아이디어 브리핑만 따로 받고 싶을 때 사용. 상세 파일(~/Documents/side-project-briefings/YYYY-MM-DD.md) 저장 포함. 자동 실행은 /morning-briefing 통합 스킬로 2026-04-18 이전됨.
allowed-tools: WebSearch, WebFetch, Bash, Write, Read
---

# 사이드 프로젝트 데일리 브리핑

## 실행 흐름

### 1. 웹 리서치 (최소 5회 검색)

다음 검색어들을 **오늘 날짜 기준**으로 실행:
- `"trending side project ideas ${YEAR} ${MONTH}"`
- `"ProductHunt launches today ${YEAR}"`
- `"indie hacker profitable apps ${YEAR}"`
- `"micro SaaS ideas solo developer ${YEAR}"`
- `"AI app ideas trending ${MONTH} ${YEAR}"`

### 2. 아이디어 큐레이션 (3~5개)

각 아이디어에 포함할 항목:
- **이름** + 한 줄 설명 (한국어)
- **왜 지금 뜨는지** — 트렌드 근거 (한국어)
- **빌드 시간** — 혼자 몇 주 (1~4주 범위)
- **수익화** — SaaS, 프리미엄, 원타임 등
- **추천 기술스택** — 강대종님 스택 고려: Flutter(모바일), Swift(iOS 네이티브), Next.js/React(웹), Python(백엔드/AI), Claude API
- **참고 링크** — 출처 URL

필터 기준:
- 솔로 개발자가 1~4주 내 빌드 가능
- 명확한 수익화 가능성
- 과포화 시장 제외
- AI/자동화/개발자도구 등 현재 트렌드 활용

### 3. 오늘의 픽 (1개)

가장 해볼 만한 아이디어 1개를 골라 상세 분석:
- 왜 이걸 골랐는지
- MVP 범위 제안
- 첫 주 액션 플랜
- 경쟁 상황

### 4. 파일 저장

```
~/Documents/side-project-briefings/YYYY-MM-DD.md
```

마크다운 형식, 한국어. 날짜는 KST 기준.

### 5. 텔레그램 전송

`~/.claude/channels/telegram/send.sh 538806975 "<요약>"` 로 전송.
(스케줄 잡에서 MCP 텔레그램 플러그인과 충돌 방지를 위해 curl 직접 호출)
텔레그램 메시지는 **요약본** (오늘의 픽 + 나머지 아이디어 제목만). 전문은 파일 참조.

send.sh 실패 시 파일 저장만 하고 스킵.

### 6. Git 커밋 (선택)

`~/Documents/side-project-briefings/` 가 git repo 면 자동 커밋.
아니면 스킵.

## 주의사항

- 이전 브리핑과 겹치지 않게 다양한 검색어 활용
- 구체적이고 실행 가능한 아이디어만 — 에세이 금지
- 스캔하기 쉽게: 짧은 문단, 명확한 헤딩
- 웹 리서치 실패 시 에러 메시지 출력 후 종료 (빈 브리핑 생성 금지)
