---
prevention_deferred: null
---

# 메모리에 스킬 파일로 유도 가능한 내용을 중복 저장

- **발생 일자:** 2026-04-21 09:56 KST
- **해결 일자:** 2026-04-21 09:58 KST
- **심각도:** low (메모리 오염, 토큰 낭비)
- **재발 가능성:** high (가드 없음)
- **영향 범위:** auto-memory 시스템 전체 (모든 기기)

## 증상

대종님이 `/sync` 가 양 기기 동시 실행 안전하다고 말하자, 해당 사실을 `project_automation_disabled_2026_04_21.md` 메모리에 새 줄로 추가. 그런데 같은 내용이 이미 `~/.claude/skills/sync/SKILL.md` 에 명시돼 있었음. 대종님 "내가 기록 안해도 스킬에 적혀있지 않나?" (텔레그램 id 1551) 지적으로 발견. 뒤이어 "근데 왜 또적었어?" (id 1553) 로 남은 메모리 파일 자체의 존재 이유까지 재검토 요청.

## 원인

auto-memory 쓰기 전 **기존 skill 파일 / CLAUDE.md / AGENT.md 에 같은 사실이 있는지 grep 체크 안 함**. 시스템 프롬프트 auto-memory 섹션에 "Anything already documented in CLAUDE.md files" 저장 금지 룰은 있지만:

1. skill SKILL.md 파일까지 명시 안 됨 (CLAUDE.md 만 언급).
2. 실제로 "유도 가능한지" 를 grep 없이 감으로 판단 → 놓침.

부수 원인: 메모리 파일이 decision context 와 sync 가능한 fact 를 섞어 저장하다 보니 추가 줄의 성격(결정 맥락 vs 단순 사실)을 분별 못 하고 습관적으로 append.

## 조치

1. 중복 라인 Edit 로 되돌림 (`project_automation_disabled_2026_04_21.md` 원복).
2. 남긴 메모리 자체는 **결정 맥락 + 현재 비활성/활성 스냅샷** 이라 skill 에서 유도 불가한 정보이므로 유지 결정.
3. 대종님에게 "기준 더 타이트하게 잡겠다" 메타 피드백.

## 예방 (Forcing function 우선)

auto-memory 에 새 줄 쓰기 직전 아래 3-step preflight 를 **시스템 프롬프트/훅 레벨로 박는다**:

1. 저장 내용에서 핵심 키워드 2~3개 추출.
2. `rg <키워드> ~/.claude/skills/*/SKILL.md ~/.claude/CLAUDE.md ~/.claude/AGENT.md` 로 grep (대소문자 무시).
3. hit 나오면 **저장 취소** + "이미 <경로> 에 있습니다" 콘솔 로그, hit 없을 때만 저장 진행.

구현 옵션:
- **A. PreToolUse hook** (`~/.claude/settings.json`) — `Write|Edit` 호출 + 경로가 `memory/*.md` 이면 컨텐츠를 stdin 으로 받아 keyword grep 해주는 훅. hit 시 exit 2 로 블록.
- **B. 프롬프트 레벨 룰 추가** — 시스템 프롬프트 auto-memory 섹션의 "What NOT to save" 에 `~/.claude/skills/*/SKILL.md` 도 포함 + "Before writing, grep keywords in those files" 의무화.
- **C. 하이브리드** (권장) — A 훅이 기본 가드, B 룰이 의식적 체크. A 실패 시 B 가 catch.

재발 이력 쌓이면 forcing function 을 더 센 쪽 (훅 강제 차단) 으로 승격.

## 재발 이력

_(없음)_

## 관련 링크

- 원인 세션: `~/.claude/projects/-home-ssamssae/3739a5cc-86ff-451e-971a-c88b8ae5afd0.jsonl` (09:56~10:03 KST)
- 텔레그램 메시지: id 1549, 1551, 1553
- 유지된 메모리: `~/.claude/projects/-home-ssamssae/memory/project_automation_disabled_2026_04_21.md`
- 되돌린 변경: 같은 파일의 "daily-sync Mac+WSL 동시 실행 안전" 추가 라인 (Edit 으로 원복)
- 관련 시스템 룰: 시스템 프롬프트 auto-memory 섹션 "What NOT to save in memory" (현재 CLAUDE.md 만 언급, skill SKILL.md 확장 필요)
