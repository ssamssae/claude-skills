---
prevention_deferred: null
---

# 텔레그램 typing 표시가 채팅 중 "한번 쏘고" 완전 정지

- **발생 일자:** 2026-04-20 23:30 KST
- **해결 일자:** 2026-04-21 00:28 KST
- **심각도:** low (UX, 응답 중 상태 불투명)
- **재발 가능성:** medium
- **영향 범위:** 플러그인 telegram typing 데몬, 병렬 Claude 세션 전체

## 증상
Claude 가 긴 작업 중일 때, 텔레그램 "입력 중..." 표시가 턴 시작 직후 1회만 나오고 이후 4초가 지나도 다시 안 나타남. 사용자 입장에서 Claude 가 멈췄는지 계속 일하는지 판별 불가. 초기 가설이었던 "메시지 전송 시 깜빡임" 은 사용자 재현으로 기각됨 — 실제로는 daemon 이 죽어서 완전 정지.

## 원인
드림팀 서브에이전트 3명 병렬 분석 결과 2:1 합의로 아래 2개 복합 원인 확정:

1. **전역 pkill 패턴 매칭으로 병렬 세션 간 상호 격추.** `telegram-typing-start.sh`, `telegram-typing-stop.sh` 양쪽 모두 `pkill -f 'telegram-typing-daemon\.sh'` 를 세션 구분 없이 호출. 같은 Mac 위에서 돌아가는 다른 Claude 세션(또는 과거 턴의 Stop 훅)이 현재 세션의 활성 daemon 을 패턴만 보고 SIGTERM.
2. **daemon 의 `set -e` + 미완전 detach 조합으로 silent 조기 종료.** `nohup bash ...daemon.sh &` 는 했지만 `</dev/null` 과 `disown` 이 없어서 부모 TTY 에 묶여 있었고, `.env` source 실패 등 부수 오류로 조용히 exit(1) 해도 로그 없이 사라짐.

2026-04-15 오펀 청소 이슈에서 도입한 "전역 pkill 로 확실히 정리" 패턴이 역방향으로 작용해 이번 이슈를 유발 — 하나의 forcing function 이 다른 바운더리를 무너뜨린 케이스.

> Telegram Bot API rate-limit 가설(Agent 3)은 문서상 근거 약해 기각. `sendChatAction` 의 5초는 typing 지속 시간이지 요청 주기 제한이 아님.

## 조치
commit `0c62bab` — `claude-automations` repo

1. `telegram-typing-start.sh`
   - 전역 pkill 제거
   - `CLAUDE_SESSION_ID` 별 PID 파일 `/tmp/claude-telegram-typing-<sess>.pid` 도입
   - 같은 세션 daemon 살아있으면 재스폰 대신 typing 1회만 refresh
   - `nohup bash ...daemon.sh </dev/null >/dev/null 2>&1 &` + `disown` 으로 TTY 완전 분리
2. `telegram-typing-stop.sh`
   - 전역 pkill 제거 → 세션별 PID 파일만 kill
3. `telegram-typing-daemon.sh`
   - `set -e` 제거
   - `curl -w '%{http_code}'` 로 HTTP 상태 캡처 → 200 아니면 로그
   - 60초마다 heartbeat `/tmp/claude-telegram-typing-heartbeat.log`

Mac push 완료, WSL 은 `cd ~/.claude/automations && git pull --rebase origin main` 한 줄로 반영 (심링크 구조 ~/.claude/hooks → automations/hooks).

## 예방 (Forcing function 우선)
- **세션 격리 PID 파일이 앞으로의 표준.** 어떤 장시간 daemon 이든 `pkill -f <pattern>` 을 전역으로 쓰지 말고 `CLAUDE_SESSION_ID` 키로 PID 파일 분리. 오펀 청소는 SessionStart 훅이나 별도 cron 에서 "부모 없는 PID" 만 골라 처리.
- **daemon 기본 템플릿 3종 세트**: `set -e 금지` + `</dev/null >/dev/null 2>&1 &` + `disown` + heartbeat 로그. 이 네 가지 없이 daemon 만들면 같은 silent-death 반복.
- **heartbeat 로그가 재발 감지 forcing function.** 다음에 "끊김" 신고 들어오면 `/tmp/claude-telegram-typing-heartbeat.log` 의 마지막 로그 시각 + HTTP 코드로 원인이 pkill 인지 API 오류인지 즉시 구분 가능.

## 재발 이력
_(없음)_

## 관련 링크
- 커밋: `claude-automations` 0c62bab (hooks 3종 수정)
- 관련 이슈: `2026-04-15-telegram-typing-daemon-orphan.md` (반대 방향 — 이번 이슈를 유발한 원 forcing function)
- 드림팀 분석 텔레그램 메시지: id 5657
- 메모리: (없음 — forcing function 이 코드/훅 레벨에서 자동화됐으므로 메모리 중복 불필요)
