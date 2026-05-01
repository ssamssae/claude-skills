---
prevention_deferred: null
---

# Mac 본진 push 직후 WSL 가 stale base 로 같은 repo 작업 시작 — race 자동 merge

- **발생 일자:** 2026-05-01 13:49 KST (본진 push) → 13:52 KST (WSL merge, race 인지)
- **해결 일자:** 2026-05-01 13:52 KST (3-way merge 자동)
- **심각도:** low (이번엔 충돌 라인 안 겹쳐 git 이 자동 해결)
- **재발 가능성:** medium (handoff 패턴 + 본진 동시작업이 일상)
- **영향 범위:** claude-skills repo, Mac↔WSL handoff 흐름

## 증상

5/1 13:49 KST 본진이 `7452fcd` "fix(stale-match): NEGATION_DESC_KEYWORDS 추가" 를 main 에 push. 그로부터 3분 안에 WSL 이 base `e328dbf` 에서 시작한 wsl/skills-policy-docs-2026-05-01 브랜치를 main 으로 머지(`8cbc611`, 13:52 KST). 머지 시점 main 은 이미 본진 패치가 들어간 7452fcd 였고, WSL 브랜치는 그 직전 base 에서 분기됨 → 잠재적 race.

## 원인

1. **WSL 가 stale base 로 작업 시작** — directive 받은 시점의 main HEAD 와 작업 시작 시점의 main HEAD 가 어긋남. WSL 이 `git pull --rebase` 후 분기하라는 강제 안내 없었고, wsl-directive.sh 도 main HEAD SHA 를 본문에 첨부하지 않음.
2. **본진이 directive 발송 직후 같은 repo 동시 수정** — directive 보낸 뒤 같은 claude-skills repo 의 stale-match 파이썬 파일을 본진이 직접 수정. 본진 측 "같은 파일 동시 수정 금지" 룰 (AGENT.md 126 라인) 은 있지만 "같은 repo 동시 수정" 으로는 확장 안 돼있음.
3. **3-way merge 가 운으로 자동 해결** — 본진 패치는 `night-builder/stale_match.py` 류 파이썬 파일, WSL 패치는 `arun/SKILL.md` 등 8개 마크다운. 디렉토리 자체가 안 겹쳐 conflict 0. 만약 본진이 SKILL.md 도 같이 만졌으면 WSL 머지 시 manual conflict 해결 필요했음.

## 조치

이번 사이클은 추가 조치 없이 자동 해결. `8cbc611` merge commit 으로 main 통합. 후속 손실 없음.

## 예방 (Forcing function 우선)

forcing function 후보 3개 (someday todos 항목 10번 본문):

1. **(a) directive 본문에 "최신 main 위에서 시작" 명시 강제** — wsl-directive.sh 또는 directive 작성 단계에서 본문에 "WSL 측: 작업 시작 전 `git pull --rebase` 후 분기" 한 줄 의무화. 사람 룰 + 자동화 양쪽 한 번에 박는 게 효과.
2. **(b) 본진은 directive 발송 직후 같은 repo 동시 수정 자제** — AGENT.md 126 라인 "같은 파일 동시 수정 금지" 를 "같은 repo 동시 수정 금지 (WSL 작업 종료 보고 받기 전까지)" 로 확장. 단 본진 작업 정체 비용 발생.
3. **(c) wsl-directive.sh 에 main HEAD SHA 자동 첨부** — 디렉티브 발송 시점 main HEAD 를 운반체가 본문에 한 줄 자동 박아 보냄. WSL 측이 그 SHA 와 본인 작업 base 가 다르면 경고. `mac-report.sh` 의 거울 구조에 추가.

**적용 결정:** (c) 가 자동화 가벼움 + 가시성 + (a) 보완 효과 모두 충족. 다음 race 발생 시 (a) 도 추가. (b) 는 본진 정체 비용이 커서 후순위.

## 재발 이력

<생성 시 비어있음. 다음 race 발생 시 한 줄 추가>

## 관련 링크

- 커밋: 본진 `7452fcd` (13:49 KST), WSL 머지 `8cbc611` (13:52 KST), WSL 브랜치 끝 `375afdc`
- 메모리: `feedback_check_existing_decisions.md`, `project_handoff_bidirectional_zero_touch.md`
- todos: `~/todo/todos.md` 진행중 "10 wsl-mac-race-skill-edit 이슈 기록"
- 텔레그램: 2026-05-01 14:48 KST someday batch 분류 결과 (id 10256)
