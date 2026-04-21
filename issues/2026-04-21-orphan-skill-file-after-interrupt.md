---
prevention_deferred: null
---

# 세션 중단 직후 방금 만든 스킬 파일이 커밋/푸시 없이 로컬에만 남음

- **발생 일자:** 2026-04-21 14:32 KST (세션 중단), 2026-04-21 23:42 KST (9시간 10분 뒤 사용자 체감 보고)
- **해결 일자:** 2026-04-21 23:46 KST (다음 세션에서 `git add + commit + push`)
- **심각도:** medium (데이터 유실 가능성 — Mac 디스크 단일 장애점 의존, 단일 파일 규모)
- **재발 가능성:** high (인터럽트/컨텍스트 스위치가 일상적, 현재 가드 없음)
- **영향 범위:** `~/.claude/skills/**` 의 신규 파일 모두 (특히 `lessons/`, `issues/`, `SKILL.md` 수정)

## 증상

14:32:06 — `Write()` 로 `~/.claude/skills/submit-app/lessons/android-draft-app-release-status.md` 신규 생성.
14:32:09 — 파일 시스템 쓰기 완료.
14:32:12 — `[Request interrupted by user]`.

이 시점에 다음 일이 벌어져야 했지만 안 일어남:

- `git add` ❌
- `git commit` ❌
- `git push` ❌

14:42:08 — 사용자가 `/clear` 로 세션 초기화. 새 세션이 뜨지만 이전 세션의 "미처리 git 상태" 는 자동으로 감지되지 않음.

23:42 — 사용자가 "뭐가 꼬였나" 를 체감하고 재발 방지 요청. `git status` 로 untracked 파일 1개 확인:

```
$ git status --short
?? submit-app/lessons/android-draft-app-release-status.md
```

파일 내용은 무사했으나, Mac 이 사망했다면 해당 lesson 은 완전 유실. 홈페이지 `/skills` 에도 반영 안 됐음(rule: 새/수정 스킬은 GitHub + daejong-page 자동 반영).

## 원인

1. **인터럽트 = 작업 중단의 끝점 ≠ 세이브 포인트.** Claude Code 세션이 중단되면 그 직후에 돌려야 할 정리 단계(커밋·푸시·홈페이지 반영)가 그냥 누락됨. 복구할 메커니즘 없음.
2. **스킬 파일 쓰기 루틴이 "write-then-commit" 을 한 묶음으로 보장하지 않음.** 세션 로직상 Write() 이후 사용자 확인이나 다음 지시를 기다리는 게 일반적인 흐름이라, 인터럽트가 사이에 끼면 미커밋 상태로 정지.
3. **Stop/SessionEnd 훅이 "claude-skills repo 의 untracked/unstaged 변경" 을 감지 안 함.** `daily-sync-and-learn` 은 06:45 KST 에 돈다 — 그 사이에 세션 여러 번 열릴 수 있고, 그 시간대에 끄고 다시 켜면 구멍 발생.
4. **사용자 기준 가시성 제로.** 파일이 만들어졌는지조차 바로 알기 어려움 (git status 를 수동으로 쳐야 보임).

근본 원인은 **"쓰기(Write) 와 배포(commit+push) 가 트랜잭셔널하지 않다"**. 파일 시스템은 쓰였지만 git/GitHub/홈페이지 어디에도 반영 안 된 중간 상태가 장기간 눈에 안 띔.

## 조치

즉시:

1. `~/.claude/skills/` 에서 `git status --porcelain` 으로 untracked/unstaged 확인 → 1건(`submit-app/lessons/android-draft-app-release-status.md`) 식별
2. `git add` + 포스트모템 성격의 커밋 메시지로 `git commit` + `git push`
3. 이 이슈 파일 자체를 `/issue` 포맷으로 기록 + `regen_index.py` 로 INDEX.md 갱신
4. 텔레그램으로 사용자에게 복구 완료 보고

항구적 조치는 아래 예방 참조.

## 예방 (Forcing function 우선)

우선순위 순서:

### 1. Stop 훅에 "skills repo 미커밋 감지 + 텔레그램 경보" 추가 (최우선)

`~/.claude/hooks/` 혹은 `settings.json` 의 Stop 훅에 짧은 쉘 스니펫:

```bash
#!/bin/bash
cd ~/.claude/skills || exit 0
dirty=$(git status --porcelain)
if [ -n "$dirty" ]; then
  # untracked/unstaged 가 남은 채 세션이 끝나려는 상태
  curl -s -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TG_CHAT}" \
    -d "text=⚠️ claude-skills untracked/unstaged 감지 (세션 종료 직전):%0A%0A${dirty}%0A%0A다음 세션에서 정리 필요" \
    > /dev/null
fi
```

같은 로직을 `~/daejong-page/` 에도 확장 적용. "세션 끝났는데 홈페이지 반영 안 된 변경이 있다" 를 유저가 바로 인지.

### 2. "새 스킬 파일 = 즉시 push" 루틴 규칙화 (메모리)

메모리 `feedback_skill_write_commits_immediately.md` 신설:

> 스킬 관련 파일(`~/.claude/skills/**`) 을 Write/Edit 하면, 그 직후 같은 응답 안에서 `git add + commit + push` 까지 묶어서 실행. 사용자 확인 기다리지 않음(가역 + 규칙 명시).

이미 `feedback_skill_publishing.md` 가 "새 스킬은 GitHub + 홈페이지 자동 반영" 을 말하지만, "한 응답 안에서 끝낸다" 는 트랜잭션 단위를 명시적으로 못 박지는 않음 — 그걸 추가.

### 3. 세션 시작 시 자기 점검 (start-of-session safety net)

신규 세션 초기 작업 체크리스트에 `cd ~/.claude/skills && git status --short && cd ~/daejong-page && git status --short` 를 무조건 1회 돌려서 남아있는 미커밋을 발견 즉시 수습. `daily-sync-and-learn` 이 06:45 에 도는 것과 별개로 **매 세션** 이 자기 청소를 하게 만듬.

`~/.claude/CLAUDE.md` 에 "## 세션 워밍업" 섹션 신설하거나, 세션 워밍업 훅(UserPromptSubmit 아님 — SessionStart 훅) 으로 자동 `git status` → 결과 요약 주입.

### 4. daily-sync-and-learn 에 Mac 쪽 repo 훑기 추가

이미 WSL → Mac 동기화용으로 돌고 있으니, 거기서 `~/.claude/skills`, `~/daejong-page` 의 `git status --porcelain` 결과를 리포트. 하루 1회 건강검진 성격. 1·3번 있으면 백업 역할만 하면 충분.

### Deferred 결정

**1번(Stop 훅) 을 우선 설치하고, 2번 메모리도 같이 박음.** 3번은 2번과 상당히 겹쳐서 1·2 이후 상황 보고 결정. 4번은 이미 돌고 있는 잡 확장이라 당장 안 해도 됨.

## 재발 이력

_(없음 — 최초 발견)_

단, 과거 비슷한 "작업은 되었는데 외부 시스템에 반영 누락" 패턴은 있었음:
- 2026-04-20 `terminal-only-reply-missed-telegram` (reply 툴 호출 누락)
- 2026-04-21 `memoyo-signup-ghost-form` (홈페이지 반영 누락)

같은 계열 문제 — "여러 출력 채널 중 일부가 빠짐". 통합 관점에서 보면 **"write 후에 수반돼야 할 배포 동작이 빠지는 게 반복된다"** 이므로, 각 채널마다 Stop 훅 레벨 가드를 까는 방향이 일관된 대응.

## 관련 링크

- 커밋(orphan 수습): `claude-skills` `HEAD~1` (submit-app: add lesson — draft app 상태의 앱은 release status=draft 강제)
- 기존 메모리: `feedback_skill_publishing.md` ("새/수정된 스킬은 ssamssae/claude-skills GitHub + daejong-page /skills 페이지에 자동 반영")
- 예방 2 로 추가할 메모리(예정): `feedback_skill_write_commits_immediately.md`
- 예방 1 로 추가할 훅(예정): `~/.claude/hooks/stop-check-repos-dirty.sh`
