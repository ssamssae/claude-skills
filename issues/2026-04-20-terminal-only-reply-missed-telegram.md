---
prevention_deferred: null
---

# Telegram-origin 질문에 터미널로만 답하고 reply 툴 호출 누락

- **발생 일자:** 2026-04-20 09:10 KST (추정)
- **해결 일자:** 2026-04-20 09:13 KST
- **심각도:** high (사용자 의사소통 차단)
- **재발 가능성:** high (같은 세션에서 여러 번 반복 확인됨)
- **영향 범위:** WSL Claude Code 세션 전반 (telegram-origin 대화 시)

## 증상
사용자가 텔레그램으로 `/to-iphone` 스킬 설계 질문을 보냄. WSL Claude 가 설계안을 터미널에 길게 출력한 뒤 reply 툴 호출 없이 응답 종료. 사용자 화면(텔레그램)에는 아무것도 뜨지 않아 "또 텔레그램 답변이 안오는데?" 로 인지.

## 원인
긴/구조적 답변을 작성할 때 "대화 턴" 으로 인식해 기본 출력 경로(터미널 텍스트)로 빠짐. reply 툴 호출은 **override 단계**라서 매번 의식적으로 걸어야 하는데, 답변의 길이/복잡도가 올라갈수록 마지막 단계에서 빼먹는 패턴이 반복. 시스템 프롬프트 상단의 "The sender reads Telegram, not this session" 지시를 머리로는 알지만 손이 먼저 터미널로 감.

## 조치
- 즉시 같은 내용을 `mcp__plugin_telegram_telegram__reply` 로 재전송
- 원인 자가분석 (길이 트랩, 질문 모드 방심, forcing function 부재) 텔레그램으로 공유
- 메모리 저장: `feedback_telegram_reply_tool_mandatory.md`
- **Stop 훅 설치**: `~/.claude/hooks/telegram-reply-check.sh`
  - transcript JSONL 파싱 → 마지막 real user prompt (content=string) 검사
  - telegram-origin 이고 이번 turn 에 reply 툴 호출 0회면 `{"decision":"block","reason":"..."}` 반환
  - `stop_hook_active` 플래그로 무한 루프 방지
  - 6개 시나리오 전부 pipe-test 통과
- `~/.claude/settings.json` `hooks.Stop` 배열 첫 entry 로 추가 (기존 훅 3개 보존)

## 예방 (Forcing function 우선)
- **Forcing function 설치 완료.** 다음 세션부터 동일 실수 시 Stop 훅이 자동 감지 → 모델이 다시 깨어나서 reply 툴 호출하게 함.
- 훅은 `exit 0` 기본값이라 오작동해도 세션 안 깨짐.
- 훅 로그: `/tmp/claude-telegram-reply-check.log` — 여기서 재발 여부 관찰 가능.
- **추가 검증(Mac 피드백, 2026-04-20):** 기존 `telegram-stop-ping.sh` 의 race retry 루프(0.5s × 6회)가 유지되는지, Stop 훅 exit 감지 로직에 failure path 로그가 제대로 찍히고 있는지 한 번 점검. 새 훅이 충돌하거나 막지 않도록.

## 재발 이력
_(없음)_

## 관련 링크
- 훅 파일: `~/.claude/hooks/telegram-reply-check.sh`
- 설정 변경: `~/.claude/settings.json` `hooks.Stop` 첫 번째 entry
- 메모리: `feedback_telegram_reply_tool_mandatory.md`
- 텔레그램 메시지 id: 931 (사용자 지적), 932 (재전송), 933 (원인 요청), 935 (자가분석), 942 (훅 설치 완료)
