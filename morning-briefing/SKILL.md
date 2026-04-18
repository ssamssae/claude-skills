---
name: morning-briefing
description: 매일 아침 07:15 통합 브리핑. 날씨·미세먼지 + 어제 커밋·오늘 할일·블로커 + 뉴스·주식 + 사이드 프로젝트 픽을 한 번에 조사해 텔레그램으로 단일 메시지 전송. 기존 morning-reporter·weather-dust·side-project-briefing 3개 스킬을 통합(각 스킬은 수동 호출용으로 유지). 저녁 todo-reminder(22:00)는 별도 운영.
allowed-tools: WebSearch, WebFetch, Bash, Read, Write, Glob, Grep
---

# 아침 통합 브리핑 (morning-briefing)

하루 시작 시 필요한 모든 정보를 **단일 Claude 세션 + 단일 텔레그램 메시지** 로 전달.
세션 3회 → 1회, 알림 3건 → 1건으로 축약되어 토큰 절약 + 알림 피로도 감소.

> 저녁 `todo-reminder` (22:00 KST) 는 별도 운영. 이 스킬에 포함하지 말 것.

## 실행 흐름

### 1. 로컬 데이터 수집 (네트워크 전 먼저 실행)

**1-A. 어제 git 커밋 요약 (KST 기준)**

```bash
for repo in ~/simple_memo_app ~/daejong-page ~/todo; do
  echo "=== $(basename $repo) ==="
  git -C "$repo" log --since="yesterday 00:00" --until="today 00:00" --oneline --no-merges 2>/dev/null || echo "(no commits)"
done
```

프로젝트별로 제목만 한 줄씩. 커밋 없으면 "작업 없음".

**1-B. 오늘 할일 (todos.md)**

`~/todo/todos.md` 의 `## 진행중` 섹션에서 미완료(`- [ ]`) 항목 중 **상위 5개** 만 추출.
선정 기준: ⭐ 최우선순위 먼저, 다음은 마감 임박, 최근 추가 순.

**1-C. 미리알림 앱 "Claude" 목록 미완료**

```bash
osascript -e 'tell application "Reminders"
  set targetList to list "Claude"
  set output to ""
  repeat with r in (every reminder in targetList whose completed is false)
    set output to output & "- " & name of r & "\n"
  end repeat
  return output
end tell'
```

todos.md 미완료와 합쳐 중복 제거.

**1-D. 블로커 탐지**

진행중 항목 중 `블로커`·`대기`·`심사` 키워드 포함 항목 별도 리스트.

### 2. 웹 검색 (병렬 가능, 실패는 섹션별 격리)

최소 4개 쿼리:
- `"서울 오늘 날씨 YYYY-MM-DD"` + `"서울 미세먼지 초미세먼지 오늘"` (2개로 분리 OK)
- `"한국 IT 테크 뉴스 오늘"` / `"오늘 주요뉴스 YYYY-MM-DD"`
- `"코스피 코스닥 오늘"` + `"나스닥 S&P500 어제 종가"` (합쳐도 OK)
- `"trending side project ideas YEAR MONTH"` + `"indie hacker profitable apps YEAR"` (2~3개)

### 3. 사이드 프로젝트 파일 저장

기존 형식 유지: `~/Documents/side-project-briefings/YYYY-MM-DD.md`
- 마크다운, 한국어
- 3~5개 아이디어 상세 + 오늘의 픽 1개 분석
- 포맷은 기존 `/side-project-briefing` 스킬과 동일

텔레그램 메시지에는 **오늘의 픽 1개만** 한 줄로.

### 4. 외출·날씨 판단

기준:
- 미세먼지 "나쁨" 이상 → 😷 마스크
- 비 확률 50%+ → ☂️ 우산
- 기온 5°C 이하 → 🧥 두꺼운 옷
- 기온 30°C 이상 → 🥵 더위 주의

### 5. 통합 텔레그램 메시지 (단일 전송)

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
  1. ⭐ [우선순위 항목]
  2. ...
  (미완료 5개)

⚠️ 블로커 (있을 때만 섹션 생성)
  • [대기/심사중 항목]

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

### 6. 전송

```bash
~/.claude/channels/telegram/send.sh 538806975 "<메시지>"
```

(스케줄 잡에서 MCP 텔레그램 플러그인과 충돌 방지를 위해 curl 직접 호출)

send.sh 실패 시 터미널 stdout 에만 출력.

## 에러 처리

- 웹 검색 하나 실패해도 **나머지는 계속 진행**. 실패 섹션은 `— (정보 없음)` 으로 표기.
- 로컬 데이터 실패(git, osascript) 는 해당 섹션만 스킵.
- 전체 실패 시 최소한 `🌅 모닝 브리핑 (YYYY-MM-DD)\n(데이터 수집 실패)` 이라도 전송.

## 주의

- **단일 세션·단일 메시지**가 이 스킬의 존재 이유. 여러 번 send.sh 호출 금지.
- 메시지 길이는 Telegram 한도(4096자) 내. 각 섹션 장황하지 않게.
- 기존 `/morning-reporter`·`/weather-dust`·`/side-project-briefing` 은 수동 호출용으로 유지. 자동 실행은 이 스킬로 단일화.
- 날짜는 KST 기준. bash `TZ=Asia/Seoul date +%Y-%m-%d` 로 계산.
- "잘했다" 류 멘트 금지 — 팩트·정보 위주.
