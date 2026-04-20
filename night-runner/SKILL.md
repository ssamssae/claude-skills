---
name: night-runner
description: 야간 사이드 프로젝트 러너 — projects.yaml 기반 라운드로빈으로 매일 밤 1개 repo 골라 repo-janitor 에이전트로 1~2개 TODO 처리, janitor/YYYY-MM-DD 브랜치에 push, 텔레그램 보고. 수동 호출과 cron 호출 동일.
allowed-tools: Bash, Read, Write
---

# 야간 사이드 프로젝트 러너

`~/.claude/runner/run.sh` 를 호출하고 결과를 텔레그램으로 보고하는 진입점.

## 호출 패턴

- `/night-runner` — 정상 실행
- `/night-runner --dry-run` — 실행 안 하고 어떤 repo 가 선택될지만 시뮬레이션
- cron 호출 시: `0 23 * * * /home/ssamssae/.claude/runner/run.sh && <텔레그램 보고>`

## 절차

1. **사전 체크**
   - `~/.claude/runner/projects.yaml` 존재 + enabled=true 항목 1개 이상
   - `git`, `python3`, `claude` (Claude Code CLI) 설치 확인
   - 현재 시각이 22:00~02:00 KST 가 아니면 강대종님께 한번 더 확인 ("야간 러너인데 지금 호출하시는 거 맞아요?")

2. **dry-run 모드**
   - `$ARGUMENTS` 에 `--dry-run` 포함 시 `DRY_RUN=true ~/.claude/runner/run.sh` 호출
   - 출력만 보고 종료, 텔레그램 보고 안 함

3. **정상 실행**
   - `~/.claude/runner/run.sh` 호출 (run_in_background=true 권장 — claude -p 가 1~2시간 걸릴 수 있음)
   - 시작 텔레그램: `[야간 러너 - $(date +%H:%M)] <repo-name> 작업 시작. 2시간 후 결과 보고 예정.`
   - Monitor 로 로그 파일 (`~/.claude/runner/logs/$(date +%Y-%m-%d).log`) 의 주요 이벤트 추적
     - 패턴: `에러|ERROR|FAIL|커밋|commit|push|종료`

4. **종료 후 보고**
   - 로그 파일에서 마지막 50줄 추출
   - claude -p 가 만든 변경사항 (git log janitor/YYYY-MM-DD --oneline) 요약
   - 텔레그램으로 단일 메시지:
     ```
     [야간 러너 결과 - YYYY-MM-DD]
     repo: <name>
     상태: 성공/실패/타임아웃
     커밋: N개
       - <commit msg 1>
       - <commit msg 2>
     푸시 브랜치: janitor/YYYY-MM-DD
     로그: ~/.claude/runner/logs/YYYY-MM-DD.log
     ```

## 안전장치

- main/master 직접 push 금지 (run.sh 가 항상 janitor/YYYY-MM-DD 브랜치 사용)
- 2시간 타임아웃 (run.sh 의 `timeout 7200`)
- 3번 연속 실패 시 정지 (repo-janitor 에이전트 자체 룰)
- DRY_RUN 모드 권장: 처음 셋업 후 며칠은 dry-run 으로 동작 검증
- enabled=true 인 repo 는 강대종님이 명시 승인한 것만 (projects.yaml 수동 편집 필요)

## 비활성화

cron 끄기:
- `crontab -e` 에서 해당 줄 주석
- 또는 `mv ~/.claude/runner/run.sh ~/.claude/runner/run.sh.disabled`
