---
prevention_deferred: null
---

# 텔레그램 typing 표시 4초 주기 신호가 채팅 중에 끊김

- **발생 일자:** 2026-04-20 23:30 KST
- **해결 일자:** (진행 중 — 이슈 기록 + 원인 조사 먼저)
- **심각도:** low (UX, 응답 중 상태 불투명)
- **재발 가능성:** medium
- **영향 범위:** 플러그인 telegram typing 데몬

## 증상
Claude 가 긴 작업 중일 때, 텔레그램에 "입력 중..." 을 4초 주기로 쏴주는 신호가 채팅 중간에 사라짐. 사용자가 Claude 가 멈췄는지 계속 일하는지 판별 불가.

## 원인
(추정) 4초 주기 typing 데몬이 세션 활성 중 조기 종료 또는 Bot API sendChatAction 이 rate limit 에 걸려 silent drop. 2026-04-15 오펀 청소 조치(`pkill -f`)가 역으로 너무 일찍 죽이는 방향으로 작용했을 가능성. 로그 확인 필요.

## 조치
(미정 — 이 이슈 기록 후 로그 분석부터)

## 예방 (Forcing function 우선)
- typing 데몬을 heartbeat 로그로 30초마다 stderr 찍게 추가 → 언제 끊기는지 근거 확보
- 데몬 프로세스가 예상 수명 이전에 종료되면 텔레그램 reply 로 경보 발사 (현재 silent fail)
- sendChatAction 4xx 응답 시에도 동일 경보
- 데몬 wrapper 에 `while true; do send_typing; sleep 4; done` 패턴으로 자가 respawn — 현재 구조 확인 후 결정

## 재발 이력
_(없음)_

## 관련 링크
- 관련 이슈: `2026-04-15-telegram-typing-daemon-orphan.md` (반대 방향 문제 — 세션 종료 후 오펀 누적)
