---
name: morning-reporter
description: (수동 호출 전용) 어제 git 커밋 요약 + 오늘 할일 + 블로커 체크만 따로 보고 싶을 때 사용. 자동 실행은 /morning-briefing 통합 스킬로 2026-04-18 이전됨.
allowed-tools: Bash, Read, Glob, Grep, WebSearch
---

# 모닝리포터 — 일일업무 브리핑

## 실행 흐름

### 1. 어제 작업 요약

아래 프로젝트들의 **어제(KST 기준) git 커밋**을 수집:
```bash
for repo in ~/simple_memo_app ~/daejong-page ~/todo; do
  echo "=== $(basename $repo) ==="
  git -C "$repo" log --since="yesterday 00:00" --until="today 00:00" --oneline --no-merges 2>/dev/null || echo "(no commits)"
done
```

각 프로젝트별 커밋 1줄씩 요약. 커밋 없으면 "작업 없음".

### 2. 오늘 할일

`~/todo/todos.md` 의 `## 진행중` 섹션에서 미완료 항목 읽기.

추가로 미리알림 앱 "Claude" 목록의 미완료 항목도 체크:
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

### 3. 주요 뉴스 TOP 3

웹 검색: `"오늘 주요뉴스 ${YYYY-MM-DD}"` 또는 `"한국 뉴스 헤드라인 오늘"`
- IT/테크/스타트업 위주로 3개 선별
- 각 뉴스: 제목 + 한 줄 요약 (출처 포함)

### 4. 주식/투자 TOP 3

웹 검색: `"코스피 코스닥 오늘 ${YYYY-MM-DD}"`, `"미국 주식 나스닥 어제"`
- 코스피/코스닥 전일 종가 또는 현재 시세
- 나스닥/S&P500 전일 종가
- 주목할 종목이나 이슈 1개 (AI/테크 관련 우선)

### 5. 블로커/대기 항목

할일 중 "심사 대기", "대기중", "블로커" 키워드가 있으면 별도 표시.

### 6. 텔레그램 전송

`~/.claude/channels/telegram/send.sh 538806975 "<메시지>"` 로 전송.
(스케줄 잡에서 MCP 텔레그램 플러그인과 충돌 방지를 위해 curl 직접 호출)

포맷:
```
🌅 모닝 리포트 (YYYY-MM-DD)

📋 어제 한 일:
  [프로젝트별 커밋 요약]

📌 오늘 할일:
  [todos.md 진행중 항목]

📰 주요 뉴스:
  1. [제목] — [한 줄 요약]
  2. ...
  3. ...

📈 주식/투자:
  • 코스피 X,XXX (+X.X%) | 코스닥 XXX (+X.X%)
  • 나스닥 XX,XXX (+X.X%) | S&P500 X,XXX
  • [주목 종목/이슈 1개]

⚠️ 블로커:
  [대기/블로커 항목]
```

send.sh 실패 시 터미널 출력만.

## 주의사항
- KST 기준으로 "어제" 계산
- 길어지면 핵심만 (커밋 메시지 전문 X, 제목만)
- 할일이 없으면 "할일 없음 — 새 작업 추가하세요" 안내
