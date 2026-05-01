---
name: night-runner
description: 야간 사이드 프로젝트 러너 v1 안전모드 — projects.yaml 기반 라운드로빈으로 enabled repo 1개 골라 read-only 점검 5개(BACKLOG/TODO grep, TODO·FIXME·HACK, 7일 commit silence, test, lint) 수행 후 markdown 보고서 + 텔레그램 1통. 코드 수정/commit/push/PR 0. Mac mini launchd 매일 03:00 KST 자동 실행 + 수동 호출 동일. 트리거 "/night-runner".
allowed-tools: Bash, Read, Write
---

# 야간 사이드 프로젝트 러너 (v1 안전모드)

**v1 = read-only 점검만, 코드 수정 0.** ~/claude-automations/scripts/night-runner-check.sh 를 진입점으로 호출하고 결과를 텔레그램으로 보고한다.

## 기기 라우팅 (지휘관 1명 원칙)

🍎 Mac 본진 = 지휘관(설계·결정·메인 세션, main 머지 결정) / 🏭 Mac mini = 빌드·배포 워커(SSH 라우팅 수신) / 🪟 WSL = 작업자(`wsl/*` 브랜치 push, main 직접 push 금지). 운반체 = `wsl-directive.sh` / `mac-report.sh`.

**이 스킬**: 🏭 Mac mini launchd 03:00 KST 자동 실행 + 양 기기 수동 호출 OK. read-only 점검만이라 commit/push 0 (룰 충돌 가능성 없음).

## 호출 패턴

- `/night-runner` — `bash ~/claude-automations/scripts/night-runner-check.sh` 호출
- 자동 실행: Mac mini launchd `com.claude.night-runner-check` 매일 03:00 KST (RunAtLoad false)

## 절차

1. **사전 체크**
   - `~/.claude/runner/projects.yaml` 존재 + enabled=true 항목 1개 이상
   - `git`, `python3` (+pyyaml) 설치 확인
   - Mac/Mac mini/WSL 어디서나 호출 가능 (단 자동 실행은 Mac mini launchd 만)

2. **점검 5개 (read-only)**
   - 라운드로빈으로 `enabled=true` repo 1개 선택 (`projects[date.day % count]`)
   - **BACKLOG.md / TODO.md 미해결 항목 grep** — `[ ]` 체크박스 unchecked 또는 plain `-` bullet
   - **TODO / FIXME / HACK grep** — lib / src / app / source 디렉토리 한정 (없으면 `.`), node_modules / .dart_tool / build/ 제외
   - **마지막 commit N일 경과 여부** — default N=7 (`COMMIT_SILENT_DAYS`). 임계 초과 시 ⚠️
   - **test 호출** — pubspec.yaml → `flutter test` / package.json → `npm test` / requirements.txt 또는 pyproject.toml → `pytest -q`. timeout 5분 (`PER_REPO_TEST_TIMEOUT_SEC`)
   - **lint 호출** — pubspec.yaml → `flutter analyze` / package.json with lint script → `npm run lint` / pyproject.toml + ruff → `ruff check .`

3. **보고서 + 알림**
   - 출력: `~/claude-automations/reports/night-runner/$(date +%F).md` (같은 날 재실행 시 suffix `-2`, `-3`)
   - 위험도 라벨: low / med / high (commit silence ⚠️ 또는 test/lint 의 fail/error/exception 발견 시 med)
   - 텔레그램 1통 (완료 시): `[야간 점검 - YYYY-MM-DD] <repo-name> 점검 완료 (위험도 X). 보고서: <path>`
   - 시작 알림 없음 (새벽 노이즈 제거)

## 다음날 흐름

- Mac 지휘관이 보고서 검토
- 수정 필요 시 별도 directive 로 작업자(WSL 또는 Mac 본진) 에게 지시
- Mac mini 는 수정 판단 / 작업 지시 / PR 생성 0. 정해진 launchd 잡만 실행

## 안전장치 (v1)

- 코드 파일 수정 0
- git commit 0, push 0, branch 생성 0, gh pr create 0
- claude headless 0 (예산 $0)
- `--dangerously-skip-permissions` 0
- 전체 timeout 1200초 (`TOTAL_TIMEOUT_SEC`)
- 실패 시 재시도 0 (보고서에 FAILED 라벨만)
- enabled=true 는 강대종님이 명시 승인한 것만 (projects.yaml 수동 편집)
- main/master 직접 push 금지는 의미 없음 — git push 자체 안 함

## v1 금지사항 (hard rule)

다음 중 하나라도 위반하면 v1 안전모드 아님:

- claude headless 호출 (claude -p, --agent 등)
- `--dangerously-skip-permissions` 사용
- git branch 생성
- git commit
- git push
- gh pr create
- 실패 시 재시도
- 코드 파일 수정
- 1회 실행에 repo 2개 이상 점검

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `PROJECTS_YAML` | `~/.claude/runner/projects.yaml` | enabled repo 명세 |
| `REPORTS_DIR` | `~/claude-automations/reports/night-runner` | 보고서 출력 |
| `COMMIT_SILENT_DAYS` | 7 | commit silence 임계일 |
| `PER_REPO_TEST_TIMEOUT_SEC` | 300 | test/lint 명령 timeout |
| `TOTAL_TIMEOUT_SEC` | 1200 | 전체 timeout |
| `TG_SEND` | `~/.claude/channels/telegram/send.sh` | 텔레그램 송신 스크립트 |

## projects.yaml 위치

각 기기 로컬 `~/.claude/runner/projects.yaml` (path 필드가 기기마다 다르므로 git 동기화 부적합). Mac/Mac mini 배포 시 WSL 사본을 SCP 로 받은 후 path 필드만 해당 기기 경로로 수정.

## 비활성화

- Mac mini launchd 끄기: `launchctl bootout gui/$(id -u)/com.claude.night-runner-check`
- 또는 `mv ~/claude-automations/scripts/night-runner-check.sh{,.disabled}`
- WSL 측 옛 run.sh: 이미 `~/.claude/runner/run.sh.disabled` 로 mv (v1 도입 시 비활성화)

## 이전 버전 (v0 = janitor 자동 코드 수정 모드, 폐기)

v0 = WSL 측 `~/.claude/runner/run.sh` (claude headless --agent repo-janitor + --dangerously-skip-permissions + janitor/YYYY-MM-DD 브랜치 + git push + gh pr create + 2시간 timeout + $5 예산). v1 도입 시 `run.sh.disabled` 로 보존, 폐기 X. 향후 v2 (제한적 PR 모드) 검토 시 참고용.
