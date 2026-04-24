---
name: sync
description: 맥과 WSL 의 자동화·이슈 히스토리·앱 코드·디자인 시안을 즉시 최신 상태로 끌어오는 수동 스킬. 강대종님이 "동기화", "최신화", "sync", "/sync", "pull", "복습", "이슈 복기" 이라고 말하거나 데스크탑에서 방금 push 한 내용을 맥에서 바로 받고 싶을 때 호출. 내부적으로 claude-automations/scripts/daily-sync-and-learn.py 를 실행해 06:45 KST 자동 동기화와 동일한 작업을 즉시 수행. 2026-04-22 부터 ~/apps/*/ 앱 repo 도 자동 커버, 2026-04-24 부터 ~/design-lab 시안도 커버.
allowed-tools: Bash
---

# /sync — 자동화·이슈 히스토리·앱 repo 즉시 최신화

맥과 WSL 에서 각 기기의 claude-skills + claude-automations + daejong-page + design-lab + `~/apps/*/` 모든 repo 를 pull 하고, 이슈 히스토리 메모리를 재생성하고, 과거 이슈 3건을 복기하는 작업을 즉시 실행한다. 자동 실행판(launchd/systemd, 매일 06:45 KST) 과 동일한 스크립트를 공유한다.

## 언제 호출되는가

- 강대종님이 "동기화", "최신화", "sync", "/sync", "pull 받아" 라고 말할 때
- 데스크탑(WSL) 에서 방금 스킬·자동화·이슈·**앱 코드**를 push 했고 맥에서 바로 반영받고 싶을 때 (반대 방향도 동일)
- 새 세션 시작 직후 현재 시점 기준으로 이슈·스킬 메모리를 최신 상태로 올리고 싶을 때
- 아침 06:45 자동 실행이 누락됐다는 신호가 있을 때 (맥 잠자기 등)

## 절차

기기 모드에 상관없이 한 줄로 끝난다. claude-automations 가 clone 돼 있어야 함.

```bash
python3 ~/.claude/automations/scripts/daily-sync-and-learn.py
```

스크립트 내부 동작:

1. `~/.claude/skills` 를 `git pull --rebase --quiet` — 실패하면 경고만 찍고 계속
2. `~/.claude/automations` 도 동일하게 pull
3. `~/daejong-page` 가 있으면 pull
4. `~/design-lab` 이 있으면 pull (2026-04-24 추가, 앱 UI 시안·audit·theme 공유용)
5. **`~/apps/*/` 전수 순회 → `git pull --rebase --autostash --quiet`** (2026-04-22 추가). 한 앱 실패해도 다른 앱은 계속. 로컬 dirty 는 autostash 로 보존.
6. `~/.claude/automations/install.sh` 재실행 (idempotent — 새 plist/timer 있으면 자동 설치)
7. `~/.claude/skills/issues/*.md` 를 스캔해 `~/.claude/projects/-Users-user/memory/reference_issue_history.md` 메모리 파일 재생성 + MEMORY.md 인덱스 링크 보장
8. 최근 30일 이슈 중 랜덤 3건을 "오늘의 복기" 로 선정
9. 변경 요약(📚 skills / ⚙️ automations / 🌐 daejong-page / 🎨 design-lab / **📱 apps**) + 복기 3건을 묶어 텔레그램 chat 538806975 에 단일 메시지 전송

## 실행 결과 보고

스크립트가 이미 텔레그램으로 결과를 보내지만, /sync 스킬 호출 시에는 추가로 현재 세션(맥이든 WSL 이든) 에 스크립트 exit code + 변경된 커밋 수 요약 한 줄을 응답한다:

```
✅ /sync 완료
  skills: <변경 커밋 수> · automations: <변경 커밋 수>
  issue 메모리 갱신 · 오늘의 복기 N건 전송됨
```

실패 시:
```
⚠️ /sync 일부 실패
  상세: <에러 한 줄>
  (git pull 충돌·네트워크 등은 텔레그램 경고로 가 있음)
```

## 자동 실행판과의 관계

- 자동: claude-automations/launchd/com.claude.daily-sync-and-learn.plist (맥) + systemd/daily-sync-and-learn.{timer,service} (WSL). 매일 06:45 KST.
- 수동: 이 /sync 스킬. 언제든 호출.

둘 다 같은 `daily-sync-and-learn.py` 를 호출하므로 동작 일관성이 보장된다. 로직 업데이트는 파이썬 스크립트 한 곳만 수정.

## 안전

- `git pull --rebase --quiet` 이므로 로컬 커밋이 있을 때 자동 충돌 해결을 시도한다. 해결 실패하면 pull 을 포기하고 경고만 남기고 계속 진행 — 강제 덮어쓰기 절대 금지.
- install.sh 는 idempotent. 여러 번 실행해도 `launchctl load` 가 이미 로드된 것에 대해서는 무해하게 실패한다.
- 메모리 파일 재생성은 전체 덮어쓰기. 손으로 편집한 내용이 있으면 덮어씀(이 파일은 자동 관리 대상이므로 수동 편집 금지).
