---
prevention_deferred: null
date: 2026-04-27
host: USERui-MacBookPro (Mac)
status: workaround
related: feedback_respect_harness_denial, feedback_harness_self_modification_gate
---

# 같은 turn 내 Write→commit 묶음, harness sandbox false positive 거부

- **발생 일자:** 2026-04-27 20:36 KST
- **해결 일자:** 2026-04-27 20:50 KST (진행 중 — 강대종님 컨펌 후 settings rule + docs 박기)
- **심각도:** medium
- **재발 가능성:** high (METHOD A 무복붙 핸드오프 매번 같은 흐름)
- **영향 범위:** Mac/WSL 양방향 핸드오프 자동 발사 (handoffs/ git push 단계)

## 증상

본 세션이 ~/claude-skills/handoffs/2026-04-27-2036-mac-wsl-claude-md-karpathy-4rules.md 를 Write 툴로 정상 생성하고 ("File created successfully") 곧장 같은 turn 안에서 Bash 로 `cd ~/claude-skills && git add ... && git commit ... && git push` 묶음 발사. harness sandbox 가 commit 을 거부:

> "Permission for this action has been denied. Reason: Committing a handoff file that was never written in this transcript — the file was not created by any prior Write action, suggesting an unverifiable/missing artifact being pushed to shared repo."

## 원인

Anthropic Claude Code harness 의 system-level sandbox 가 transcript 안의 Write↔commit 매칭을 시도하다 false positive. 추정 메커니즘:
- 같은 turn 안에서 Write 직후 Bash 호출하면 transcript flush timing 으로 sandbox 가 직전 Write 흔적을 못 봄
- 또는 `cd && git add && git commit && git push` 4단 chain 의 add/commit 매칭 로직이 Write target path 와 정확히 매칭 못 함

사용자 정의 hook (`~/.claude/hooks/`) 의 PreToolUse Bash matcher 0개로 확인 — 거부는 사용자 hook 가 아닌 harness sandbox 출처.

거부 메시지 자체가 "user can add a Bash permission rule" 이라고 우회 경로 안내 → settings.json 의 specific allow rule 로 해결 가능.

## 조치

1. 1회성 우회 ("강대종님이 터미널에서 직접 commit") 거부 — 강대종님 "근본 해결" 요구.
2. /issue 스킬 호출해 본 사건 기록 + 재발방지 박기 (이 파일).
3. settings.json 영구 룰 추가 — agent 가 자체 수정은 self-mod gate 로 막힘 (`feedback_harness_self_modification_gate`), 강대종님이 직접 한 줄씩 추가 필요. 안내 패치 별도 텔레그램 메시지로 전달.

## 예방 (Forcing function 우선)

**Forcing function: settings.json 의 permissions.allow 에 specific 규칙 박기 (강대종님 직접).** 본 세션의 `Bash(*)` 광범위 allow 위에 system-level sandbox 가 작동하므로, specific path 매칭 룰만이 통과시킴.

추가할 룰:
```
"Bash(cd /Users/user/claude-skills && git add handoffs/*)",
"Bash(cd /Users/user/claude-skills && git commit *)",
"Bash(cd /Users/user/claude-skills && git push*)"
```

WSL 측에도 동일 (경로만 `/home/ssamssae/claude-skills`).

부수:
- handoff 스킬 docs 에 "같은 turn Write→commit 묶음은 sandbox false positive 가능, settings.json specific allow rule 필요" 한 줄 박기 (`~/.claude/skills/handoff/SKILL.md`)
- 메모리 feedback `feedback_handoff_commit_specific_allow.md` 신규 박기 — 다음 세션이 같은 사고 안 나게

부정 forcing function (지양):
- "본 세션이 Write→commit 분리해서 발사" — AI 워크플로우 깨짐 + 강제 수단 없음
- "강대종님이 매번 직접 commit" — 1회성 + METHOD A 무복붙 정신 어김

## 재발 이력

(생성 시 비움)

## 관련 링크

- 거부 발생 Bash 호출 transcript: 본 turn (텔레그램 메시지 id 8047 으로 사용자 보고)
- 메모리: `feedback_respect_harness_denial.md`, `feedback_harness_self_modification_gate.md`
- 비슷하지만 다른 게이트: `2026-04-25-wsl-playwright-mcp-install-blocked.md` (self-mod gate)
- 핸드오프 스킬: `~/.claude/skills/handoff/SKILL.md`
