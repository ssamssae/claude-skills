---
prevention_deferred: null
---

# codex-session-relay가 Codex 응답을 본진 채팅에 중복 미러링

- **발생 일자:** 2026-05-07 21:58 KST (생성 추정)
- **해결 일자:** 2026-05-08 00:55 KST
- **심각도:** medium
- **재발 가능성:** low
- **영향 범위:** 본진(@MyClaude) 텔레그램 채팅

## 증상
Codex가 텔레그램으로 응답할 때마다 `🏭 Codex→Claude: "..."` 형태로 본진 채팅에 동일 내용이 중복 전송됨.

## 원인
Mac mini의 `com.user.codex-session-relay` launchd job(Python)이 `~/.openclaw/logs/gateway.log`를 tail -f로 감시하다가 Codex 응답 감지 시 SSH mac 경유 → 본진 텔레그램에 재전송. 2026-05-07 21:58경 생성된 것으로 추정.

## 조치
Mac mini에서 `launchctl bootout + disable gui/$(id -u)/com.user.codex-session-relay` 실행.
`com.user.codex-relay-daemon`도 동시에 disable (당시 이미 멈춰있었음).

## 예방 (Forcing function 우선)
Mac mini에 `com.user.codex-*` 패턴 신규 launchd job 생성 시 본진 텔레그램 채널 영향 여부 강대종 명시 승인 후 등록. 생성 전 `launchctl list | grep codex` 로 기존 job 목록 확인 필수.

## 재발 이력
<처음 생성>

## 관련 링크
- 텔레그램: 2026-05-08 00:53~00:55 KST 사이 스크린샷 포함 보고
