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
- 2026-04-26 09:55:03~10:10:02: daemon PID 24413 이 `start` + `iter=0 http=200` 만 찍고 silent death. 이후 15분간 새 daemon 시작 흔적 없음 (사용자 turn 안에서 죽었음). `/tmp/claude-telegram-typing-heartbeat.log` 확인. 동시에 Claude 측 5분 reply 하트비트도 누락되어 사용자에게는 "12분 완전 침묵" 으로 인지됨 → 별건 이슈 `2026-04-26-heartbeat-rule-soft-enforcement.md` 와 동시 발생.
- **2026-04-26 12:33 KST 세 번째 재발**: /clear 직후 새 세션(20372e1a) 첫 telegram prompt 에 데몬이 안 뜸. 04-26 오전의 두 번째 forcing function(stdin .session_id 파싱)으로 sess UUID 8자 prefix(c458df1d)는 살아있었지만, 새 세션 20372e1a 에는 heartbeat-log 가 0줄. start.sh 수동 invoke 는 성공 → 진단: hook fires before Claude flushes prompt to transcript, `grep -q 'source=...' "$transcript"` 가 빈 파일 만나서 exit 0 → daemon 안 뜸. 사용자가 turn 전체 동안 입력중 표시 못 봄.

### 2026-04-26 12:33 KST 세 번째 forcing function (claude-automations commit 9094e88)
- **확정 원인 (3차)**: UserPromptSubmit hook 이 발화하는 시점에 `transcript_path` 파일에는 아직 새 prompt 가 flush 되지 않음 (race). start.sh 의 `grep -q 'source=...' "$transcript"` 가 false → 데몬 spawn 단계 도달 못 하고 exit 0. 새 세션 첫 telegram prompt 에서 일관 재현.
- **검증**: 12:43 에 동일 transcript 로 start.sh 수동 invoke → daemon spawn 성공, heartbeat log 에 `sess=20372e1a` 정상 기록. 결국 transcript 가 비어있는 그 한 순간만 grep 이 헛도는 게 원인.
- **세 번째 forcing function**: UserPromptSubmit hook stdin JSON 의 `.prompt` 필드를 읽어 거기에 `source="plugin:telegram:telegram"` 가 있으면 transcript grep 실패와 무관하게 spawn. transcript 그rep 은 1차 path 로 유지 (legacy/이상 케이스 대응), prompt 검사가 fallback.
- **e2e 검증 (commit 9094e88)**: synthetic JSON `transcript_path:/dev/null` + `.prompt` 안에 telegram channel 태그만 있을 때 daemon spawn OK. 일반 문자열 prompt 는 spawn 안 함.

### 2026-04-26 09:50 KST 재조사 — 두 번째 forcing function 추가 (commit 3f4d2d1)
- **확정 원인:** `CLAUDE_SESSION_ID` 환경변수가 hook 프로세스에 주입되지 않음. start.sh / stop.sh 모두 `${CLAUDE_SESSION_ID:-default}` 로 떨어지고 daemon.sh 는 `unknown` 으로 떨어져, **모든 병렬 세션이 단일 PID 파일 `/tmp/claude-telegram-typing-default.pid` 를 공유**. 04-20 의 세션별 PID 격리 forcing function 자체는 살아있었으나, "세션 ID 가 항상 동일 fallback" 이라는 함정 때문에 격리가 무력화됨.
- **외부 kill 증거:** `/tmp/claude-stop-hook.log` 에 09:55:44 sess `663444…` 의 Stop 발생 → 그 직전 09:55:03 에 시작한 [24413] 이 iter=15 (예상 09:56:03) 도 못 찍고 사라짐. silent exit 아니고 sibling Stop 이 `default.pid` 의 24413 을 kill.
- **두 번째 forcing function:** Claude Code 가 Stop / UserPromptSubmit hook 에 JSON stdin 으로 `session_id` 를 넘겨줌 (env 가 아니라). 이걸 `jq -r '.session_id'` 로 파싱해 PID 파일 키로 사용. fallback 도 `default` 같은 단일 리터럴이 아니라 transcript 파일명 또는 hostname+pid 같은 고유값으로 변경.
- **stop.sh 의 안전 가드:** 만약 session_id 도, transcript 도 모두 비면 SESSION_ID="MISSING" 으로 두고 **아무것도 안 함** (sibling 데몬 nuke 방지 — 누설이 차라리 안전).
- **e2e 검증:** synthetic JSON 으로 다른 session_id 두 개 만들어서 한 세션의 Stop 이 다른 세션의 daemon 을 안 죽이는 것 확인. heartbeat-log 에 `sess=e2e-test` 로 실제 세션 prefix 가 찍힘 (이전엔 `sess=unknown`).
- **실데이터 확인 신호:** 다음 세션부터 heartbeat-log 의 `sess=` 부분이 `unknown` / `default` 가 아니라 진짜 UUID 8자 prefix 가 찍혀야 정상. 다시 `unknown` 이 보이면 stdin 파싱 실패 — fallback (transcript basename) 으로 떨어졌어야 함.

## 관련 링크
- 커밋: `claude-automations` 0c62bab (hooks 3종 수정)
- 관련 이슈: `2026-04-15-telegram-typing-daemon-orphan.md` (반대 방향 — 이번 이슈를 유발한 원 forcing function)
- 드림팀 분석 텔레그램 메시지: id 5657
- 메모리: (없음 — forcing function 이 코드/훅 레벨에서 자동화됐으므로 메모리 중복 불필요)
