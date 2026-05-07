# 3-way 에이전트 메시 양방향 통신 구조

## 개요
Mac 본진 · WSL · Codex(Mac mini) 3대가 서로 명령-결과를 주고받는 대칭 구조.
텔레그램 채팅방은 수신자 방에 표준 포맷으로 표시됨.

## 메시지 포맷
```
[발신이모지→수신이모지] [타입] 내용 (HH:MM KST)

이모지: 🍎=맥북 / 🪟=WSL / 🏭=Mac mini
타입: [명령] [결과] [알림] [상태]
```

## 스크립트 매핑

| 방향 | 명령 전송 | 결과 회신 |
|------|-----------|-----------|
| 🍎→🪟 | `wsl-directive.sh` | `mac-report.sh` (WSL에서 호출) |
| 🪟→🍎 | `mac-directive.sh` (WSL에서 호출) | `agent-msg-notify.sh macbook wsl 결과` |
| 🍎→🏭 | `codex-directive.sh` | `mac-report.sh` (MacMini에서 SSH 호출) |
| 🏭→🍎 | `mac-report.sh` (MacMini에서 SSH 호출) | `agent-msg-notify.sh macbook macmini 결과` |

모든 스크립트 위치: `~/.claude/automations/scripts/`

## 텔레그램 라우팅
- `agent-msg-notify.sh <from> <to> <type> <summary>`
- TO=로컬 기기 → BOT_TOKEN 사용
- TO=원격 기기 → PEER_BOT_TOKEN 사용
- 수신자 채팅방에 메시지 도착

## 핵심 환경변수 (.claude/channels/telegram/.env)
- `TELEGRAM_BOT_TOKEN` — 로컬 봇 토큰
- `TELEGRAM_PEER_BOT_TOKEN` — 상대 봇 토큰 (반드시 유효한 값인지 주기적 확인)
- `TELEGRAM_CHAT_ID` — 사용자 ID (538806975)

## 주의사항
- PEER_BOT_TOKEN 만료 시 라우팅 실패 (2026-05-07 WSL에서 발생). `getMe` API로 검증 가능
- mac-directive.sh: SSH ConnectTimeout 5초, Mac tmux 'claude' 세션 필요
- mac-report.sh: 非-Mac 호출 시 SCP+SSH 경유 (local paste 버그 2026-05-07 수정)
- codex-directive.sh: openclaw CLI + inject-gateway-url/token 파일 필요

## 구축 일자
2026-05-07 (포맷 표준화 + 양방향 완성)
