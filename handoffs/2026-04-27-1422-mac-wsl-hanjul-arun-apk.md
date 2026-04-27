---
from: mac
to: wsl
sent_at: 2026-04-27T14:22:00+09:00
status: open
---

[hanjul /arun + apk 강대종님께 전달]

목표:
강대종님이 오늘 아침 Mac 에서 push 한 hanjul UI 폴리시 6개(커밋 2021fee — 날짜 라벨 정리, soft route, stats heat 5단계 등)를 S24 에서 시각 확인하고 싶어함. 동시에 친구폰에 줄 APK 가 필요. WSL 에서 /arun 흐름으로 release 빌드 + S24 설치 + APK 강대종님 텔레그램 전달까지 한 번에 처리.

할일:
1. cd ~/apps/hanjul && git pull --rebase --autostash 으로 최신 (커밋 2021fee 포함) 받기
2. fvm flutter pub get + analyze (오늘 Mac 에서 아무 이슈 없었지만 WSL 환경 재확인)
3. /arun 실행 — 갤럭시 S24 (R3CX10GX1XR) 에 clean + release 빌드 + 설치
4. 빌드된 APK 경로 확인 — 보통 build/app/outputs/flutter-apk/app-release.apk
5. 강대종님 텔레그램(@Myclaude2 챗) 으로 APK 파일 첨부 reply.
   - reply tool 의 files 파라미터에 절대경로 넣으면 document 로 도착
   - 캡션: "🪟 hanjul v1.1.0+3 release APK (커밋 2021fee 반영, /arun 설치 완료)"
6. 핵심 검증 포인트 짧게 함께 보고 (build 성공/실패, 설치 성공/실패, APK 크기)

금지사항:
- Stop-Process 광범위 java kill 금지 (메모리 feedback_no_broad_kill.md). 필요하면 PID/path 타겟팅.
- 새 기능 추가나 코드 변경 금지. 빌드+설치+APK 전달만.
- APK 가 50MB 초과면 텔레그램 attach 실패 가능 — 그 경우 GitHub release artifact 또는 Tailscale 임시 파일 공유로 우회 알림.

종료 조건:
강대종님 텔레그램(@Myclaude2 챗) 에 APK 파일 + 한 줄 보고 도착하면 종료. handoff 답신 파일 만들 필요 없음.
