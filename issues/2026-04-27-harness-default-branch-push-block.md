---
prevention_deferred: null
date: 2026-04-27
host: DESKTOP-I4TR99I (WSL)
status: open
related: feedback_respect_harness_denial, feedback_auto_mode_no_allow_prompt
---

# `git push origin main` 하네스 차단 — default branch 직접 push

- **발생 일자:** 2026-04-27 22:04 KST
- **해결 일자:** (미해결, 재발방지 작업 중)
- **심각도:** medium
- **재발 가능성:** high — repo 마다 분류기 판단이 다르고, 작업 끝마다 같은 패턴 반복
- **영향 범위:** 모든 default branch 직접 push 워크플로우 (hanjul 등 앱 repo)

## 증상

hanjul UX 작업(에러 분기 5종 세분화 + AI 카드에 디버그 코드) 끝내고 commit 까지 완료 → `git push origin main` 시 하네스 denial:

> Permission for this action has been denied. Reason: Pushing directly to the default branch `main` bypasses PR review; CLAUDE.md's general "끝나면 즉시 git push" guidance does not specifically authorize bypassing review on the default branch.

근데 흥미로운 비대칭: 같은 세션에서 직전에 `claude-skills` repo 의 default branch (main) 에 push 한 건 통과 (handoff reply 답신, .md 1개). hanjul 은 .dart 코드 2개 + production 영향 → 분류기가 더 엄격하게 본 것으로 추정.

## 원인

1. 하네스가 default branch 직접 push 를 PR review 우회로 분류, 추가 명시 승인 요구.
2. CLAUDE.md 의 "끝나면 즉시 git push" 룰은 일반 가이드로 인식 — "default branch 직접 push" 명시 인가가 아님.
3. settings.json 의 `permissions.allow` 에 `Bash(git push:*)` 같은 명시 룰 없음.
4. 자동 모드라 1회성 Allow 프롬프트도 안 뜸 (`feedback_auto_mode_no_allow_prompt.md` 메모리 확인 — auto mode 에선 영구 룰만 통함).
5. agent 가 자기 settings.json 수정도 일관 거부 (`feedback_harness_self_modification_gate.md`) — 즉 셀프 해결 불가.

## 조치 (재발방지 — 강대종님 결정 필요)

세 옵션:

**A. settings.json `permissions.allow` 에 영구 룰 추가** (강대종님이 `/update-config` 또는 직접 편집)
- 좁게: `Bash(git push origin main)` (정확 매칭)
- 넓게: `Bash(git -C * push origin main:*)`, `Bash(git push origin main:*)` 패턴
- 위험: force push (`git push --force`) 류 다른 위험 명령은 별도 차단 유지해야 — 반드시 좁은 패턴.

**B. CLAUDE.md "빠른 원칙" 섹션의 git push 라인 강화**
- 현재: `작업 시작 전 git pull, 끝나면 즉시 git push`
- 제안: `작업 시작 전 git pull, 끝나면 즉시 git push origin main (default branch 직접 push 도 OK — solo dev repo, PR review 없음)`
- 하네스 분류기가 "specifically authorize" 키워드를 본다면 이 표현이 통과시킬 가능성. 단 검증 필요.

**C. 항상 PR 분기 거치기**
- `git checkout -b ...; git push origin <branch>; gh pr create ...` 후 강대종님 머지
- 안전하지만 solo dev repo 에선 과한 오버헤드. 하루 작업이 PR 6~8개씩 늘어남.

권장: **A + B 병행**. A 는 즉시 효과, B 는 향후 분류기 판단 변경 시도 보강.

## 관련

- `feedback_respect_harness_denial.md` — denial 나오면 우회 안 하고 즉시 사용자에게 알림 (오늘 룰 그대로 따름)
- `feedback_auto_mode_no_allow_prompt.md` — auto mode 영구 룰만이 답
- `feedback_harness_self_modification_gate.md` — agent 가 자기 settings.json 수정 불가
