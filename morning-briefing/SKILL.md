---
name: morning-briefing
description: 매일 아침 07:15 통합 브리핑. 날씨·미세먼지 + 어제 커밋·오늘 할일·블로커 + 뉴스·주식 + 사이드 프로젝트 픽을 한 번에 조사해 텔레그램으로 단일 메시지 전송. 기존 morning-reporter·weather-dust·side-project-briefing 3개 스킬을 통합·대체(2026-04-21 기존 3개 삭제). 2026-04-21 Python 프리페처 분리로 토큰 절감. 저녁 마무리는 /evening-wrap(22:30)로 별도 운영.
allowed-tools: WebSearch, WebFetch, Bash, Read, Write, Glob, Grep
---

# 아침 통합 브리핑 (morning-briefing)

하루 시작 시 필요한 모든 정보를 **단일 Claude 세션 + 단일 텔레그램 메시지** 로 전달.
세션 3회 → 1회, 알림 3건 → 1건으로 축약되어 토큰 절약 + 알림 피로도 감소.

> **2026-04-21 업데이트**: 기계적 데이터 수집(git/todos/Reminders/PR/날씨/시장) 을 Python 프리페처로 분리. Claude 는 미세먼지·뉴스·사이드 픽·합성만 담당 → 토큰 약 70% 절감.

> 저녁 `todo-reminder` (22:00 KST) 는 별도 운영. 이 스킬에 포함하지 말 것.

## 실행 흐름

### 1. Python 프리페처 실행 (네트워크·로컬 데이터 모두)

```bash
~/.claude/automations/scripts/morning-prefetch.py
```

출력: `/tmp/morning-briefing-prefetch-YYYY-MM-DD.json`

수집 내용:
- `git_commits`: simple_memo_app · daejong-page · todo 3개 repo 의 어제 커밋 제목
- `todos`: `~/todo/todos.md` 진행중 섹션 미완료 TOP 5 + 블로커 후보
- `reminders`: macOS Reminders "Claude" 리스트 미완료
- `janitor_prs`: 야간 러너 janitor PR + diff·민감파일 안전 체크 (별칭 포함)
- `weather`: 서울 기온·최저·최고·하늘·강수%·습도 (wttr.in 무료)
- `market`: 코스피·코스닥·나스닥·S&P500 종가·등락률 (Yahoo Finance)

섹션별 실패 격리. 한쪽 실패해도 나머지는 JSON 에 저장됨.
프리페처 전체 실패 시 Claude 가 기존 방식으로 fallback 하지 말고 **"데이터 수집 실패" 메시지**만 전송.

### 2. JSON 읽고 합성에 필요한 항목만 꺼내기

```
Read /tmp/morning-briefing-prefetch-YYYY-MM-DD.json
```

todos 중복 제거: `todos.top5` 와 `reminders` 합쳐서 중복 제거 후 상위 5개.

### 3. Claude 가 직접 해야 할 것 (웹 검색·합성만)

**3-A. 미세먼지·초미세먼지** (Python 으로 무료 수집 어려움)

```
WebSearch: "서울 미세먼지 초미세먼지 오늘 YYYY-MM-DD"
```

결과에서 PM10·PM2.5 수치·등급 추출. 실패 시 `— (정보 없음)`.

**3-B. 주요 뉴스** (창의적 선별 필요)

```
WebSearch: "한국 IT 테크 뉴스 오늘" 또는 "오늘 주요뉴스 YYYY-MM-DD"
```

3개 골라 한 줄 요약.

**3-C. 사이드 프로젝트 픽** (창의·분석 필요)

기존 형식 유지: `~/Documents/side-project-briefings/YYYY-MM-DD.md`
- 마크다운, 한국어, 3~5개 아이디어 상세 + 오늘의 픽 1개 분석
- 텔레그램 메시지에는 **오늘의 픽 1개만** 한 줄로

간단히 가고 싶으면 WebSearch 1회 (`"trending side project ideas YEAR MONTH"`) 만 하고 1개 픽. 최근 아이디어와 중복 피하기.

**3-D. 외출·날씨 한줄평**

프리페처 `weather` 값 기반:
- 미세먼지 "나쁨" 이상 → 😷 마스크 (3-A 결과 사용)
- 강수% ≥ 50 → ☂️ 우산
- min_c ≤ 5 → 🧥 두꺼운 옷
- max_c ≥ 30 → 🥵 더위 주의
- 그 외 → 가벼운 한 줄

### 4. 통합 텔레그램 메시지 (단일 전송)

```
🌅 모닝 브리핑 (YYYY-MM-DD 요일)

🌤 서울 날씨
  기온 X°C (최저 Y / 최고 Z) · 하늘 ___ · 강수 X%
  미세 XX (등급) · 초미세 XX (등급)
  💡 [한줄평]

📋 어제 한 일
  • simple_memo_app: [커밋 제목들]
  • daejong-page: ...
  • todo: ...
  (없으면 "작업 없음")

📌 오늘 할일 TOP 5
  1. ⭐ 🍎/🪟/🤝 [우선순위 항목]  ← 디바이스 태그 필수
  2. ...
  (미완료 5개. 🍎=Mac, 🪟=WSL, 🤝=어디서든. todos 원본 태그 그대로 유지, 없으면 제목에서 추정 — iOS/ASC/xcodebuild → 🍎, Android/Play Console/갤럭시 → 🪟, 그 외 → 🤝)

⚠️ 블로커 (있을 때만 섹션 생성)
  • [대기/심사중 항목]

🤖 야간 러너 PR (있을 때만 섹션 생성)
  • [repo] #N — [제목 핵심만] (+X/-Y줄)
    ✅ 안전 머지 가능 · 🔗 [URL]
    💬 답장: "[별칭] #N 머지"
  • [repo] #N — [제목] (+X/-Y줄)
    ⚠️ [warnings], 수동 리뷰 권장 · 🔗 [URL]
    💬 답장: "[별칭] #N 머지" (확인 후 머지)
  👉 닫으려면 "[별칭] #N 닫아"

📰 주요 뉴스
  1. [제목] — [한 줄]
  2. ...
  3. ...

📈 시장
  코스피 X,XXX (+X.X%) · 코스닥 XXX (+X.X%)
  나스닥 XX,XXX · S&P500 X,XXX
  📍 [AI/테크 주목 이슈 1개]

💡 오늘의 사이드 픽
  [이름] — [한 줄 설명]
  예상 빌드: X주 · 수익화: [방식]
  🔗 상세: ~/Documents/side-project-briefings/YYYY-MM-DD.md
```

**별칭 테이블** (PR 섹션 복붙용 — 프리페처가 이미 alias 필드에 채워줌):

| repo nameWithOwner | 별칭 |
|---|---|
| `ssamssae/dutch_pay_calculator` | `더치페이` |
| `ssamssae/simple-memo-app` | `메모요` |
| `ssamssae/yakmukja` | `약묵자` |
| `ssamssae/babmeokja` | `밥먹자` |
| `ssamssae/daejong-page` | `daejong-page` |
| (그 외) | repo 이름의 `/` 뒤 부분 |

/merge-janitor 가 자연어로 `<별칭> #N 머지` 를 받으면 repo 매칭해 해당 PR 을 처리한다. (매칭 실패 시 /merge-janitor 가 되묻기)

### 5. 전송

```bash
~/.claude/channels/telegram/send.sh 538806975 "<메시지>"
```

(스케줄 잡에서 MCP 텔레그램 플러그인과 충돌 방지를 위해 curl 직접 호출)

send.sh 실패 시 터미널 stdout 에만 출력.

## 에러 처리

- 프리페처 비정상 종료 → `🌅 모닝 브리핑 (YYYY-MM-DD)\n(데이터 수집 실패 — morning-prefetch.py 확인 필요)` 만 전송
- 프리페처 JSON 섹션이 `{}` 또는 `[]` → 해당 섹션만 스킵, 다른 섹션은 정상 표시
- WebSearch 하나 실패해도 나머지 섹션 계속 진행. 실패 섹션은 `— (정보 없음)`

## 주의

- **단일 세션·단일 메시지**가 이 스킬의 존재 이유. 여러 번 send.sh 호출 금지
- 메시지 길이는 Telegram 한도(4096자) 내. 각 섹션 장황하지 않게
- 기존 `/morning-reporter`·`/weather-dust`·`/side-project-briefing` 은 수동 호출용으로 유지. 자동 실행은 이 스킬로 단일화
- 날짜는 KST 기준. 프리페처 파일명이 이미 KST 기준으로 생성됨
- "잘했다" 류 멘트 금지 — 팩트·정보 위주
- 프리페처가 실패할 경우 fallback 으로 Claude 가 git/gh/osascript 를 직접 호출하지 말 것 (원래 목표가 토큰 절감이므로 오히려 본말전도). 실패 알림만.
