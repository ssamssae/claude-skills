---
name: night-someday
description: someday 큐 자동 소진 v0 안전모드 — ~/todo/someday.md 항목 N개(기본 3, Week 2~ 5) 라운드로빈 선택 → 각 항목 stale check (메모리 grep) → markdown 보고서 + 텔레그램 1통. v0 = surface only, 자동 DROP/PR/commit/push 0. Mac mini launchd 매일 03:30 KST 자동 실행 + 수동 호출 동일. 트리거 "/night-someday".
allowed-tools: Bash, Read, Write
---

# Night Someday (v0 안전모드)

**v0 = surface only, 자동 DROP/PR/commit/push 0.** ~/claude-automations/scripts/night-someday.sh 를 진입점으로 호출하고 결과를 텔레그램으로 보고한다.

## 배경

- ~/todo/someday.md 가 35개+ 누적 → 묘지화. 저장은 잘 되는데 꺼내서 처리하는 로직 부재가 진짜 문제 (2026-05-01 강대종님 진단).
- night-runner v1 (read-only 점검) 과 분리해 별도 잡으로 격리. v1 안전모드 hard rule 깨지 않음.
- 매일 N개 라운드로빈 surface → 강대종님이 새벽 보고서 보고 처리/승격/드롭 결정.

## 기기 라우팅

🏭 Mac mini launchd 03:30 KST 자동 실행 (night-runner-check 03:00 직후) + Mac/Mac mini/WSL 어디서나 수동 호출 OK. v0 = read/write reports only, ~/todo/someday.md 수정 0.

## 호출 패턴

- `/night-someday` — `bash ~/claude-automations/scripts/night-someday.sh` 호출
- 자동 실행: Mac mini launchd `com.claude.night-someday` 매일 03:30 KST (RunAtLoad false)

## 절차

1. **사전 체크**
   - `~/todo/someday.md` 존재
   - `python3` 설치 확인
   - `~/.claude/projects/-Users-user/memory/` 메모리 디렉토리 존재 (stale grep 대상)

2. **라운드로빈 선택**
   - someday.md "## 모아둠" 섹션의 `- [ ]` 항목 파싱
   - 시작 인덱스 = `(day_of_month - 1) % len(items)`
   - `SOMEDAY_DAILY_LIMIT` 개 슬라이싱 (wrap-around)

3. **각 항목 stale check**
   - 키워드 추출: 한글 4글자+ 또는 영문 5글자+, NOISE_TOKENS/STOPWORDS 제외, 시간/날짜 제외, 최대 6개
   - `grep -l -r` 메모리 디렉토리에서 키워드 매치 파일 수집
   - 매치 파일이 8개+ → 키워드가 noise → stale check skip
   - 매치 파일에서 **같은 라인** 에 키워드 + stale signal (완료/LIVE/승격/폐지/드롭/끝남/done/merged/fixed/shipped/출시/PASS) 동시 등장 시 STALE 신호 기록

4. **분류**
   - STALE-CANDIDATE: stale 신호 있음 → DROP 권고 (강대종님 verify 후)
   - OLD: 추가 14일+ → 유효성 컨펌 권고
   - ACTIVE: 그 외 → 처리/승격/유지 결정

5. **보고서 + 알림**
   - 출력: `~/claude-automations/reports/night-someday/$(date +%F).md` (같은 날 재실행 시 suffix `-2`, `-3`)
   - 텔레그램 1통: `[Night Someday - YYYY-MM-DD] 검토 N (STALE 후보 X / OLD Y / ACTIVE Z). 보고서: <path>`

## ramp-up 계획

- **Week 1 (신뢰 구축)**: `SOMEDAY_DAILY_LIMIT=3`. 보고서 정확도 + false positive 비율 검증.
- **Week 2~ (정상 운영)**: `SOMEDAY_DAILY_LIMIT=5` 로 환경변수 변경 (plist 또는 wrapper).
- **v1 ramp-up (조건부)**: stale check 정확도 입증되면 STALE-CANDIDATE 자동 DROP (someday.md "드롭" 섹션 이동 + commit + push). 강대종님 합의 필수.
- **v2 ramp-up (조건부)**: 자동 코드 패치 PR 생성 (예: install.sh hostname, settings.json wildcard 류 simple patch). 가드 한 단계 더 필요.

## 안전장치 (v0)

- ~/todo/someday.md 수정 0
- git commit 0, push 0, branch 0, PR 0
- claude headless 0, `--dangerously-skip-permissions` 0
- 보고서 외 파일 수정 0
- 실패 시 재시도 0

## v0 금지사항 (hard rule)

- ~/todo/someday.md 자동 수정
- git commit / push / branch / PR
- claude headless 호출
- `--dangerously-skip-permissions`
- 1회 실행에 SOMEDAY_DAILY_LIMIT 초과 처리

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `SOMEDAY_FILE` | `~/todo/someday.md` | 입력 someday |
| `SOMEDAY_DAILY_LIMIT` | 3 | 검토 항목 수 (Week 2~ 5) |
| `MEMORY_DIR` | `~/.claude/projects/-Users-user/memory` | grep 대상 |
| `REPORTS_DIR` | `~/claude-automations/reports/night-someday` | 보고서 출력 |
| `TG_SEND` | `~/.claude/channels/telegram/send.sh` | 텔레그램 송신 |

## 다음날 흐름

- Mac 지휘관이 보고서 검토
- 항목별 결정 (DROP / 승격 → todos.md / 유지)
- ~/todo/someday.md 직접 수정 또는 다음 세션에서 처리
- v1 ramp-up 박히면 STALE-CANDIDATE 는 자동 DROP, ACTIVE 만 결정 필요
