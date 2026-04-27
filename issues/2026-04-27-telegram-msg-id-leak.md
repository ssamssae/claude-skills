---
prevention_deferred: null
---

# 텔레그램 답장에 Bot API raw msg ID 인용해서 사용자 혼선

- **발생 일자:** 2026-04-27 17:09 KST
- **해결 일자:** 2026-04-27 17:14 KST
- **심각도:** low
- **재발 가능성:** high (이번이 첫 기록이지만 매 reply 마다 발생 가능한 패턴)
- **영향 범위:** 텔레그램 reply 워크플로우 전체 (모든 기기)

## 증상
review_radar v0.3 outline 보고가 한 번 도달 실패한 듯한 정황 (15:30 KST 보고 사용자 미수신 보고). 디버깅 시도하면서 답장에 "id 7930 못 받으셨어요?", "id 7932 는 도착" 같이 Bot API 가 sent 후 돌려준 raw msg ID 를 그대로 인용. 사용자: "7930이 누군데". 폰 텔레그램 UI 엔 이 ID 가 보이지 않으므로 사용자에게 무의미한 식별자였음.

## 원인
- `mcp__plugin_telegram_telegram__reply` 툴이 호출 후 `sent (id: NNNN)` 을 반환 — 디버깅 컨텍스트에 살아있다 보니 답장 텍스트에 그대로 새어 들어감
- 이 ID 는 Bot API 내부 message_id 일 뿐 사용자 폰 채팅 UI 에는 노출되지 않음 (텔레그램은 클라이언트에 raw msg id 를 보여주지 않음)
- 메모리/룰 없었음

## 조치
- 사용자에게 사과 + 무의미한 정보였음 설명 (17:09 KST 사과 답장)
- 메모리 추가: `feedback_no_raw_telegram_msg_ids.md`
- MEMORY.md 인덱스 업데이트
- PreToolUse hook 신설 (예방 섹션 참조)

## 예방 (Forcing function)
**PreToolUse hook 신설** — `mcp__plugin_telegram_telegram__reply` 호출 직전 text 본문에서 raw msg ID 패턴 자동 차단:

- 정규식 (OR):
  - `\(\s*id\s*[:=]\s*\d{3,6}\s*\)` — `(id: 7930)`, `(id 7930)`
  - `\bid\s+\d{4,6}\b` — `id 7930`
  - `\bmsg\s+\d{4,6}\b` — `msg 7930`
  - `\bmessage\s*id\s*[:=]?\s*\d{4,6}\b` — `message id 7930`
- 매칭 시 PreToolUse decision="block" + reason: "Bot API raw msg ID 는 사용자 폰 UI 에 안 보입니다. 시각(KST)+키워드로 가리키세요"
- 설치 위치: `~/.claude/hooks/telegram-reply-no-raw-id.sh` (PreToolUse, 기존 telegram-reply-check.sh Stop hook 의 짝)
- false positive 우회: fenced ```block``` 안의 라인은 검사 제외
- 자기참조 케이스(이슈 doc 자체에 매칭 패턴이 있는 등)는 reply 텍스트에 들어갈 일이 거의 없으므로 미고려

## 재발 이력
_(없음, 첫 기록)_

## 관련 링크
- 메모리: `feedback_no_raw_telegram_msg_ids.md`
- 훅: `~/.claude/hooks/telegram-reply-no-raw-id.sh`
- 텔레그램: 17:09 KST "7930이 누군데" 사용자 지적
