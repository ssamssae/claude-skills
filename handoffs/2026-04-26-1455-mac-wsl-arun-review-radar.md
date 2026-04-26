---
from: mac
to: wsl
sent_at: 2026-04-26T14:55:00+09:00
status: open
---

🍎 review_radar v0.2 UX 검증 — S24 release 빌드 + 헤더/알림 변화 확인

목표:
방금 Mac 에서 review_radar v0.2 UX 잔여 두 항목 마무리 + main 푸시 (bfd1d64). 같은 빌드를 강대종님 갤럭시 S24 (R3CX10GX1XR) 에 release 모드로 올려서 헤더 변화·알림 분기 확인.

컨텍스트:
- repo: ssamssae/review_radar, main bfd1d64 가 최신
- WSL 로컬에 ~/apps/review_radar 가 있을 것 (없으면 pull-apps 또는 git clone). 시작 전 git pull --rebase --autostash 필수
- 변경된 파일: lib/screens/home_screen.dart (헤더), lib/services/notification_service.dart (알림), lib/services/radar_controller.dart (latestEmailDate getter), test/widget_test.dart (정정)
- 동일 빌드를 Mac 에서 아이폰에 /irun 으로 올리는 중 — 양쪽 모두 같은 v0.2 검증

할일:
1. cd ~/apps/review_radar && git pull --rebase --autostash 로 main bfd1d64 까지 받기
2. /arun 으로 갤럭시 S24 (기본 device id R3CX10GX1XR) 에 clean + release 빌드·실행
3. 빌드 성공하면 강대종님께 텔레그램 보고 — "S24 빌드/설치 완료, 다음 화면 확인 부탁드립니다" + 확인 포인트 안내
4. 확인 포인트:
   (a) 홈 헤더 첫 줄에 "마지막 스캔 · HH:mm · 메일 N분 전" 두 정보가 같이 보이는지 (스캔 시각과 메일 도착 시각 분리)
   (b) 메일 N분 전 텍스트가 ink2 + w600 으로 살짝 강조됐는지
   (c) 시간이 지나도 자연스러운지 (1분 이내=방금, 60분 미만=N분 전, 24시간 미만=N시간 전, 7일 미만=N일 전, 그 외=M/d)
5. 알림 분기는 실제 메일 도착해야 검증 가능 — 다음 상태 변경 메일 도착 시점에 자동 검증, 즉시 보장 안 됨

금지사항:
- review_radar 코드에 추가 변경 금지. 단순 재빌드/검증 한정. 추가 다듬기 필요하면 별도 todo 로 등록 후 다음 라운드
- adb kill-server / Gradle 강제 종료 같은 광범위 process kill 금지 — feedback_no_broad_kill.md 참조
- main 에 추가 푸시 금지 — Mac 에서 이미 푸시함

종료 조건:
S24 에 v0.2 빌드 설치 + 강대종님께 텔레그램 보고 + 확인 포인트 안내까지. 시각 검증은 강대종님 손에서 — Claude 가 직접 확인 안 됨. 보고 후 이 핸드오프 종료 (status: done 으로 frontmatter 업데이트 + commit).
