---
name: todo-reminder
description: 매일 밤 할일 리마인더. 오늘 뭐 했고 뭐 못 했나 정리, 내일 우선순위 제안. 텔레그램 전송.
allowed-tools: Bash, Read, Glob, Grep
---

# 할일 리마인더 — 저녁 체크

## 실행 흐름

### 1. 오늘 작업 체크

오늘(KST) 각 프로젝트 git 커밋 수집:
```bash
for repo in ~/simple_memo_app ~/daejong-page ~/todo ~/yakmukja ~/dutch_pay_calculator ~/babmeokja ~/apps/*/; do
  [ -d "$repo/.git" ] || continue
  echo "=== $(basename $repo) ==="
  git -C "$repo" log --since="today 00:00" --oneline --no-merges 2>/dev/null || echo "(no commits)"
done
```

### 2. 미완료 할일

`~/todo/todos.md` 의 `## 진행중` 에서 미완료(`- [ ]`) 항목 읽기.

미리알림 앱 "Claude" 목록 미완료 항목도 체크:
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

### 3. 내일 우선순위 제안

미완료 항목 중 긴급도/중요도 기준으로 상위 3개 추천.
기준:
- 마감 임박 (날짜 키워드 파싱)
- 외부 의존성 없는 것 우선 (심사 대기 등은 후순위)
- 연속 미완료 항목 (어제도 못 한 건 오늘 꼭)

### 4. 텔레그램 전송

`~/.claude/channels/telegram/send.sh 538806975 "<메시지>"` 로 전송.
(스케줄 잡에서 MCP 텔레그램 플러그인과 충돌 방지를 위해 curl 직접 호출)

포맷:
```
🌙 저녁 리마인더 (YYYY-MM-DD)

✅ 오늘 한 일:
  [커밋 요약]

📌 아직 안 한 것:
  [미완료 항목]

🎯 내일 우선순위 TOP 3:
  1. ...
  2. ...
  3. ...
```

send.sh 실패 시 터미널 출력만.

## 주의사항
- 한 줄 요약 위주, 길게 쓰지 말 것
- "잘했다" 류 멘트 금지 — 팩트만
- 할일 완료된 게 있으면 축하 한 줄 정도는 OK
