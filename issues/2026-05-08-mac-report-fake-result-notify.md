---
prevention_deferred: null
---

# mac-report.sh 래퍼가 자동으로 가짜 [결과] 알림 생성

- **발생 일자:** 2026-05-08 01:40 KST
- **해결 일자:** 2026-05-08 01:40 KST
- **심각도:** medium
- **재발 가능성:** low
- **영향 범위:** mac-mini → MacBook 왕복 테스트 워크플로우 / agent-msg-notify.sh 기반 기기 간 메시지

## 증상
mac-mini 가 mac-report.sh 로 MacBook tmux 에 명령을 붙여넣은 뒤, 래퍼 스크립트가 자동으로 `agent-msg-notify.sh macmini macbook 결과 ...` 를 실행. MacBook 화면에 [🏭→🍎] [결과] 메시지가 떴으나 실제 MacBook Claude 가 보낸 결과가 아님 — 방향도 반대처럼 보여 혼선 유발.

## 원인
mac-report.sh 끝부분에 자동 [결과] 알림 코드가 포함되어 있었음. 래퍼가 tmux paste 완료 후 스스로 결과 알림을 날려서, 진짜 MacBook 결과가 오기 전에 가짜 결과가 먼저 도착.

## 조치
- mac-report.sh 마지막 자동 [결과] 알림 코드 제거
- 회귀 테스트 추가 + PASS 확인
- 이제 MacBook 결과 알림은 Mac Claude 가 직접 `macbook → macmini` 방향으로 전송

## 예방 (Forcing function 우선)
래퍼 스크립트(mac-report.sh / wsl-directive.sh 류)는 자동 [결과] 알림 코드를 포함하지 않는 것을 코딩 규칙으로 고정. 결과 알림은 수신측 Claude 가 명시적으로 agent-msg-notify.sh 를 호출하는 것만 허용.

## 재발 이력

## 관련 링크
- 텔레그램 메시지: 2026-05-08 01:40 KST mac-mini 보고
