# Issues Index

_자동 생성됨. 이 파일은 수동 편집 금지 — `python3 ~/.claude/skills/issue/tools/regen_index.py` 로만 갱신._
_마지막 생성: 2026-04-21 21:15 KST_

| 날짜 | slug | 제목 | 심각도 | 재발 가능성 | 재발 이력 | 예방 deferred |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-04-21 | [memoyo-signup-ghost-form](2026-04-21-memoyo-signup-ghost-form.md) | 메모요 스토어 드롭 후 2주 동안 홈페이지 사전예약 폼이 살아있어서 이메일 계속 수집 | low (개인 데이터 소규모 + 악의적 수집은 아님). 단 사용자 기대 이탈 위험은 있음. | medium (다른 앱/스킬 드롭 시 동일 구조 — 백엔드만 끄고 입력 채널 남김 — 재현 가능) | — | — |
| 2026-04-21 | [memory-skill-duplication](2026-04-21-memory-skill-duplication.md) | 메모리에 스킬 파일로 유도 가능한 내용을 중복 저장 | low (메모리 오염, 토큰 낭비) | high (가드 없음) | — | — |
| 2026-04-21 | [mac-wsl-todos-desync](2026-04-21-mac-wsl-todos-desync.md) | Mac 과 WSL 이 같은 심사레이더 작업을 병렬로 붙잡고 todos 정합성 파탄 | medium (잘못된 커밋 1건 + 사용자 혼란 + 양 기기 불일치, 다만 실제 파괴적 액션은 없음) | high (현재 구조상 기기 간 todo 상태 sync 가 인간 개입에만 의존) | — | — |
| 2026-04-21 | [launchd-silent-job-dropout](2026-04-21-launchd-silent-job-dropout.md) | launchd 가 등록된 잡을 소리 없이 떨궈서 수 주 동안 자동 스케줄 유실 | medium (자동화 잡 2개가 몇 주간 침묵 실행 실패 가능성) | medium (launchd 수동 편집 시마다 동일 현상 가능) | — | — |
| 2026-04-20 | [terminal-only-reply-missed-telegram](2026-04-20-terminal-only-reply-missed-telegram.md) | Telegram-origin 질문에 터미널로만 답하고 reply 툴 호출 누락 | high (사용자 의사소통 차단) | high (같은 세션에서 여러 번 반복 확인됨) | 6회 | — |
| 2026-04-20 | [telegram-typing-midsession-drop](2026-04-20-telegram-typing-midsession-drop.md) | 텔레그램 typing 표시가 채팅 중 "한번 쏘고" 완전 정지 | low (UX, 응답 중 상태 불투명) | medium | — | — |
| 2026-04-20 | [telegram-client-delivery-lag](2026-04-20-telegram-client-delivery-lag.md) | 텔레그램 답변이 "안 오는 것처럼" 보인 지연 현상 | medium | medium | — | — |
| 2026-04-20 | [irun-locked-iphone](2026-04-20-irun-locked-iphone.md) | /irun 재배포 시 "Could not run Runner.app" 반복 — 실제 원인은 아이폰 잠금 | medium | high | — | — |
| 2026-04-20 | [flutter-not-in-path](2026-04-20-flutter-not-in-path.md) | flutter 명령 PATH 누락으로 APK 빌드 초기 실패 | medium | high | — | — |
| 2026-04-19 | [ipa-x86-64-slice-rejection](2026-04-19-ipa-x86-64-slice-rejection.md) | 약먹자 IPA 에 x86_64 슬라이스가 섞여 App Store 검증 실패 | high (App Store 제출 블로킹) | medium (Flutter + Pods 빌드 설정 회귀 가능) | — | — |
| 2026-04-19 | [android-text-selection-twotone](2026-04-19-android-text-selection-twotone.md) | Android 텍스트 선택 블록이 2가지 톤으로 표시됨 | low (시각적 문제, 기능 정상) | low (Flutter TextField BoxHeightStyle 정책 이슈로 고정) | — | — |
| 2026-04-17 | [simulator-tap-coordinate-drift](2026-04-17-simulator-tap-coordinate-drift.md) | iOS 시뮬레이터에서 메모 탭 좌표가 한 칸씩 어긋남 | low (스크린샷 자동화 흐름 지연) | medium (시뮬레이터 해상도/스케일 변경 시 재현 가능) | — | — |
| 2026-04-17 | [simulator-sharedprefs-cache](2026-04-17-simulator-sharedprefs-cache.md) | iOS 시뮬레이터 SharedPreferences 가 cfprefsd 캐시로 인해 갱신 안 됨 | medium (테스트 데이터 조작 자동화 블로킹) | medium (다른 앱 테스트 자동화에서도 같은 함정) | — | — |
| 2026-04-16 | [playwright-chrome-google-login-blocked](2026-04-16-playwright-chrome-google-login-blocked.md) | Playwright Chromium 으로 Google 로그인 시 "안전하지 않은 브라우저" 차단 | medium (자동화 블로킹) | medium (Google 보안 정책 변경 시 재현 가능) | — | — |
| 2026-04-16 | [play-console-testers-google-group](2026-04-16-play-console-testers-google-group.md) | Play Console testers API 가 개별 이메일을 받지 않음 | medium (베타 테스터 자동 추가 블로킹) | low (Google 정책 변경 없으면 고정) | — | — |
| 2026-04-15 | [telegram-typing-daemon-orphan](2026-04-15-telegram-typing-daemon-orphan.md) | 텔레그램 typing-start 데몬이 세션 종료 후에도 살아남아 누적 | medium (리소스 누수, 다음 세션 혼선) | medium (다른 장시간 데몬에 같은 패턴 재현 가능) | — | — |
| 2026-04-15 | [aab-40mb-applescript-chunking](2026-04-15-aab-40mb-applescript-chunking.md) | AAB 40MB 파일을 AppleScript 로 직접 못 넣어서 막힘 | medium (업로드 자동화 블로킹) | medium (다른 대용량 업로드 경로 재현 가능) | — | — |
| 2026-04-12 | [ios-relaunch-crash](2026-04-12-ios-relaunch-crash.md) | iOS 재실행 시 SharedPreferencesPlugin 크래시 | high (앱 사용 불가) | medium (Flutter 메이저 업데이트 시 lifecycle 관련 회귀 가능) | — | — |

## 룰

- 매 이슈는 자기 파일 하나. `YYYY-MM-DD-<slug>.md`
- 이 INDEX 는 `/issue` 스킬이 저장할 때마다 전체 덮어쓰기로 재생성됨.
- 재발 가능성 high 인데 forcing function 없으면 적극적으로 설치. 이 index 가 "손 안 댄 debt" 추적판 역할도 겸함.
