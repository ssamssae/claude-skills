---
name: stale
description: 추천·작업 시작 전 stale 검출 5단계 패스를 즉시 실행. 본인 컨텍스트가 낡았을 가능성을 가정하고 메모리·git·시스템 상태를 직접 확인해 "방금 끝낸 일 다시 추천" / "이미 정리된 잡을 살아있다 단정" 류 사고를 막는다. 사용자가 "/stale", "스테일", "stale 체크", "stale 패스", "낡았는지 확인" 이라고 하거나, Claude 가 "뭐할까/다음 뭐" 류 추천 만들기 직전에도 자동 호출.
---

# /stale — 추천·시작 전 stale 검출 패스

근거: `~/.claude/projects/-Users-user/memory/feedback_stale_check_before_recommend.md`. 그 룰의 5단계를 SKILL 한 번 호출로 일관되게 돌리기 위한 wrapper. 본 skill 의 단계는 그 메모리 룰과 강결합 — 메모리 룰이 갱신되면 이 SKILL 도 같이 갱신.

## 호출 패턴

- 사용자: `/stale` / "스테일" / "stale 체크" / "낡았는지 봐줘"
- 자동: Claude 가 "뭐할까/다음 뭐/새 작업/다음에 뭐할까" 류 추천 만들기 직전 (옵션 — 사용자가 명시 호출 안 해도 시도)
- 인자: 없음. 또는 `/stale <주제 키워드>` 로 step 4 의 grep 키워드 지정 가능.

## 5단계 절차

각 단계 결과를 그대로 stash 해두고, 마지막에 통합 보고.

### Step 0 — 메모리 폴더 refresh

```bash
cd ~/.claude/projects/-Users-user/memory && git pull --rebase --autostash
cd ~/.claude/projects/-Users-user/memory && git log --since="6 hours ago" --oneline | head -10
```

pull 후 변경된 파일 있으면 MEMORY.md + 관련 메모리 파일을 디스크에서 다시 Read. **본 세션 시작 시점 컨텍스트의 인덱스 위에서 추천 만들면 자기 함정.**

### Step 1 — 핵심 repo 24시간 git log

```bash
for repo in ~/todo ~/.claude/automations ~/.claude/skills ~/daejong-page ~/claude-automations; do
  [ -d "$repo/.git" ] && echo "=== $repo ===" && git -C "$repo" log --since="24 hours ago" --oneline 2>/dev/null | head -5
done
ls ~/apps/ 2>/dev/null | while read d; do [ -d ~/apps/$d/.git ] && echo "=== ~/apps/$d ===" && git -C ~/apps/$d log --since="24 hours ago" --oneline | head -3; done
```

### Step 2 — 최근 갱신된 메모리 키워드 grep

```bash
find ~/.claude/projects/-Users-user/memory -name "*.md" -mtime -1 -not -path "*/.git/*" | while read f; do
  grep -lE "발행|배포|완료|성공|PASS|도달|충족|발사|투입|머지|merged|폐기|decommission" "$f" 2>/dev/null
done
```

step 0 git log 의 **삭제 commit** 도 같이 cross-check (삭제된 in_progress 메모리 = "끝났다" 신호).

### Step 3 — 직전 텔레그램 reply 본문 매칭

현재 conversation 컨텍스트 또는 최근 transcript jsonl 에서 동일 키워드 ("발행/배포/완료/성공/머지" 등) 매칭. Claude 가 본 세션 컨텍스트로 직접 판단.

### Step 4 — (작업 시작 직전) off-repo 자산 + 주제 키워드 grep

`/stale <주제>` 로 호출됐거나 이미 추천 후보가 좁혀진 상태면:

```bash
# git repo 내 주제 cross-check
cd <관련 repo> && git log --all --since="7 days ago" --grep="<주제 키워드>"
# off-repo 자산 (plans/, skills/, docs/ 는 git repo 아닐 수 있음)
ls ~/.claude/plans/ 2>/dev/null | grep -i <주제>
ls ~/.claude/skills/ 2>/dev/null | grep -i <주제>
ls ~/docs/ 2>/dev/null | grep -i <주제>
```

매치 결과 있으면 **시작 멈추고** 기존 자산 목록 + 발행/완료 계획을 강대종님께 먼저 보고. 본인이 "그래도 새로 가" 하면 진행, "기존 거 흡수해" 하면 그쪽으로.

### Step 5 — 시스템 상태 직접 확인 (단정 금지)

"X 가 Y 시각에 자동으로 돈다 / Z 잡이 켜져있다 / 프로세스 W 가 실행 중이다" 류 단정은 SKILL 문서 description 만 보고 추론하면 안 됨. 직접 확인:

```bash
# macOS launchd
launchctl list | grep -iE "claude|<주제>"
ls ~/Library/LaunchAgents/ ~/Library/LaunchAgents/_disabled/ 2>/dev/null | grep -iE "claude|<주제>"

# Linux systemd (WSL — ssh 로)
ssh wsl "systemctl list-units --all | grep -iE 'claude|<주제>'; systemctl --user list-units --all | grep -iE 'claude|<주제>'"

# cron
crontab -l 2>/dev/null
ssh wsl "crontab -l 2>/dev/null"
```

## 통합 보고 형식

```
**🔍 stale 검출 결과 (YYYY-MM-DD HH:MM KST)**

📥 step 0 — 메모리 git pull
- N 커밋 받음 / Already up to date
- 6h 변경 commit: <oneline 요약 또는 "없음">

📜 step 1 — 핵심 repo 24h
- ~/todo: <oneline 또는 "없음">
- ~/.claude/skills: ...
- (변경 없음 repo 는 생략)

📂 step 2 — 메모리 mtime -1 키워드 매칭
- <파일> — <매칭 키워드>
- (없음)

💬 step 3 — 직전 텔레그램 본문
- (스스로 판단해 매칭 발견 시 한 줄)

🎯 step 4 — (호출 인자 있으면) 주제 cross-check
- git log --grep: ...
- plans/ skills/: ...

⚙️ step 5 — 시스템 상태
- launchd: ...
- systemd (WSL): ...
- cron: ...

🚨 **stale 매치된 todos / 추천 후보**
- (있다면) "X" 항목은 Y 에서 끝남 → 추천 후보 제외 + 사용자에 "닫을까?" 확인
- (없다면) "stale 매치 0건. 평소대로 추천 진행."
```

## 호출 시 반드시 텔레그램 reply 로

`<channel source="plugin:telegram:telegram">` 컨텍스트 안에서 호출됐으면 결과는 mcp__plugin_telegram_telegram__reply 로 보내야 함. 터미널 평문은 폰에 안 보임.

## 헷갈리지 말 것

- 이 SKILL 은 **검출만** 한다. todos.md 자동 마킹 X. 매치 발견되면 "닫을까?" confirm 후에만 [x] 처리.
- 매치가 0건이면 평소 흐름대로 추천/작업 진행. SKILL 이 무조건 차단하는 건 아님.
- step 4 의 키워드 grep 은 인자 없으면 생략 (지금 작업 주제가 명확하지 않은 상태라).
- /goodnight 의 todos sweep step 과 별개. /stale 은 즉시·소규모, /goodnight 은 일일 통합.
