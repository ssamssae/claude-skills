# Issues Index

_자동 생성됨. 이 파일은 수동 편집 금지 — `python3 ~/.claude/skills/issue/tools/regen_index.py` 로만 갱신._
_마지막 생성: 2026-05-08 01:41 KST_

| 날짜 | slug | 제목 | 심각도 | 재발 가능성 | 재발 이력 | 예방 deferred |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-08 | [mac-report-fake-result-notify](2026-05-08-mac-report-fake-result-notify.md) | mac-report.sh 래퍼가 자동으로 가짜 [결과] 알림 생성 | medium | low | — | — |
| 2026-05-08 | [codex-session-relay-telegram-mirror](2026-05-08-codex-session-relay-telegram-mirror.md) | codex-session-relay가 Codex 응답을 본진 채팅에 중복 미러링 | medium | low | — | — |
| 2026-05-06 | [hanjul-openai-org-member-removed](2026-05-06-hanjul-openai-org-member-removed.md) | 한줄일기 AI 응원 기능 중단 — OpenAI Organization 멤버 remove로 API 키 접근 차단 | high (유료 앱 핵심 기능 전체 중단) | medium | — | — |
| 2026-05-05 | [session-clear-triggered-goodnight](2026-05-05-session-clear-triggered-goodnight.md) | "세션클리어하자" → /goodnight 잘못 발화 사고 | ? | ? | — | — |
| 2026-05-04 | [lottocalc-irun-white-screen](2026-05-04-lottocalc-irun-white-screen.md) | lottocalc irun 흰화면 버그 | ? | ? | — | — |
| 2026-05-02 | [policy-race-mac-wsl](2026-05-02-policy-race-mac-wsl.md) | 본진·WSL 가 globals/CLAUDE.md 를 stale-on-stale 로 동시 수정 — 「지휘관 1명 원칙」 폐기 사이클의 race | medium (정책 파일 → 잘못 통합되면 두 작업자 행동 룰 자체가 깨짐) | medium (정책 갱신 사이클 또는 같은 파일 동시 작업 발생 시 동일 패턴) | — | — |
| 2026-05-02 | [playwright-mcp-cwd-output-dir](2026-05-02-playwright-mcp-cwd-output-dir.md) | Playwright MCP server cwd 가 `/` 일 때 `/.playwright-mcp` mkdir ENOENT | medium (Playwright MCP 도구 호출 100% 실패 → Substack republish · Play Console 자동화 등 차단) | high (plugin update / cache 재생성 시 .mcp.json 원복되면서 재현) | — | — |
| 2026-05-02 | [google-oauth-playwright-stealth-bypass](2026-05-02-google-oauth-playwright-stealth-bypass.md) | Playwright 로 띄운 Chrome 에서 Google OAuth 로그인 차단 — stealth args 3종 우회 성공 | medium (`/create-play-app` 자동화 + Play Console 신규 등록 자동화 전체가 차단되는 함정) | high (Google 자동화 차단 정책 상시 강화 추세, 규칙 변경 시 또 깨질 수 있음) | — | — |
| 2026-05-01 | [wsl-mac-race-skill-edit](2026-05-01-wsl-mac-race-skill-edit.md) | Mac 본진 push 직후 WSL 가 stale base 로 같은 repo 작업 시작 — race 자동 merge | low (이번엔 충돌 라인 안 겹쳐 git 이 자동 해결) | medium (handoff 패턴 + 본진 동시작업이 일상) | — | — |
| 2026-05-01 | [ep5-backfill-overwrite](2026-05-01-ep5-backfill-overwrite.md) | Substack backfill 이 Ep5 원본 prose 를 덮어씀 — 컨벤션 두 갈래 공존 | medium | high (다음 ep 도 substack-first 면 같은 사고) | — | — |
| 2026-04-28 | [cf-colo-region-block](2026-04-28-cf-colo-region-block.md) | CF colo region-block 으로 친구 wifi 에서만 OpenAI 호출 거부 | high (1900원 유료 출시 블로커) | medium (CF Workers 에서 OpenAI/Anthropic 등 region-block 권역 API 를 직접 호출하는 모든 앱) | — | — |
| 2026-04-27 | [wsl-hanjul-push-classifier-block](2026-04-27-wsl-hanjul-push-classifier-block.md) | WSL 측 hanjul main push 가 auto-mode classifier 에 막힘 + Mac SSH 우회도 동일 룰로 막힘 | medium | high (다른 앱·다른 기기에도 동일 발생 가능) | 3회 | — |
| 2026-04-27 | [telegram-msg-id-leak](2026-04-27-telegram-msg-id-leak.md) | 텔레그램 답장에 Bot API raw msg ID 인용해서 사용자 혼선 | low | high (이번이 첫 기록이지만 매 reply 마다 발생 가능한 패턴) | — | — |
| 2026-04-27 | [same-turn-commit-fp](2026-04-27-same-turn-commit-fp.md) | 같은 turn 내 Write→commit 묶음, harness sandbox false positive 거부 | medium | high (METHOD A 무복붙 핸드오프 매번 같은 흐름) | — | — |
| 2026-04-27 | [paste-block-mixed-r6](2026-04-27-paste-block-mixed-r6.md) | 복붙 블록 별도 메시지 룰 6번째 재발 (오늘만 4번) | medium | high (메모리·CLAUDE.md 룰만으론 6번째까지 어김) | 3회 | — |
| 2026-04-27 | [harness-default-branch-push-block](2026-04-27-harness-default-branch-push-block.md) | `git push origin main` 하네스 차단 — default branch 직접 push | medium | high — repo 마다 분류기 판단이 다르고, 작업 끝마다 같은 패턴 반복 | — | — |
| 2026-04-26 | [tahoe-ssh-cli-block](2026-04-26-tahoe-ssh-cli-block.md) | macOS Tahoe 26.x: systemsetup -setremotelogin 이 Full Disk Access 부족으로 차단 | low | medium | — | — |
| 2026-04-26 | [review-status-disabled-blind-spot](2026-04-26-review-status-disabled-blind-spot.md) | review-status-check _disabled 이동 후 17h 동안 Apple issue 메일 누락 | high (App Store 제출 일정 + 사용자 신뢰 영향, 2개 앱 동시 영향) | high (forcing function 없음, _disabled/ 폴더의 다른 모니터링·알림 잡들 다 같은 위험) | — | — |
| 2026-04-26 | [paste-block-label-leak](2026-04-26-paste-block-label-leak.md) | 복붙 메시지에 라벨/안내 텍스트 섞어 보냄 → PowerShell 명령 깨짐 | medium | high (이번이 3-4번째) | — | — |
| 2026-04-26 | [heartbeat-rule-soft-enforcement](2026-04-26-heartbeat-rule-soft-enforcement.md) | 작업 중 5분 하트비트 룰 강제력 부재로 12분간 침묵 | medium (UX, 사용자가 진행 상태 파악 못 함) | high (메모리 룰 만으로는 강제력 없음 — 작업 몰입 시 timestamp 추적 실패가 일상) | 3회 | — |
| 2026-04-26 | [handoff-method-a-fallback-regression](2026-04-26-handoff-method-a-fallback-regression.md) | /handoff METHOD A 회귀 — 무복붙 인프라 두고 복붙 폴백으로 빠짐 | medium | medium | — | — |
| 2026-04-26 | [handoff-claude-main-empty-shell](2026-04-26-handoff-claude-main-empty-shell.md) | /handoff Primary 첫 실전 — claude-main 세션은 살아있는데 안에서 Claude Code 가 안 돌고 있었음 | ? | ? | — | — |
| 2026-04-26 | [handoff-active-session-marker-mismatch](2026-04-26-handoff-active-session-marker-mismatch.md) | 발생 | ? | ? | — | — |
| 2026-04-25 | [wsl-playwright-mcp-install-blocked](2026-04-25-wsl-playwright-mcp-install-blocked.md) | WSL Playwright MCP 플러그인 설치 — 하네스 자기수정 게이트로 차단 | ? | ? | — | — |
| 2026-04-24 | [ios-ipad13-screenshot-mandatory](2026-04-24-ios-ipad13-screenshot-mandatory.md) | App Store 심사 제출: iPad 13" 스크린샷 누락으로 "심사에 추가" 차단 | medium (심사 제출 지연 수십 분) | high (iPhone 전용으로 기획한 앱을 App Store 에 올릴 때마다 동일하게 발견됨) | — | — |
| 2026-04-24 | [insta-autopost-mac-mirror-missing](2026-04-24-insta-autopost-mac-mirror-missing.md) | 4/24 인스타 자동 포스팅 누락 — Mac 호출 시 시크릿/인프라 부재 | ? | ? | — | — |
| 2026-04-23 | [ios-gidclientid-missing](2026-04-23-ios-gidclientid-missing.md) | iOS GoogleSignIn GIDClientID 누락 크래시 (심사레이더) | high (앱 첫 화면 전 강제 종료) | high (google_sign_in 쓰는 신규 Flutter 앱 iOS 첫 빌드에서 동일하게 재현) | — | — |
| 2026-04-21 | [orphan-skill-file-after-interrupt](2026-04-21-orphan-skill-file-after-interrupt.md) | 세션 중단 직후 방금 만든 스킬 파일이 커밋/푸시 없이 로컬에만 남음 | medium (데이터 유실 가능성 — Mac 디스크 단일 장애점 의존, 단일 파일 규모) | high (인터럽트/컨텍스트 스위치가 일상적, 현재 가드 없음) | 2회 | — |
| 2026-04-21 | [memoyo-signup-ghost-form](2026-04-21-memoyo-signup-ghost-form.md) | 메모요 스토어 드롭 후 2주 동안 홈페이지 사전예약 폼이 살아있어서 이메일 계속 수집 | low (개인 데이터 소규모 + 악의적 수집은 아님). 단 사용자 기대 이탈 위험은 있음. | medium (다른 앱/스킬 드롭 시 동일 구조 — 백엔드만 끄고 입력 채널 남김 — 재현 가능) | — | — |
| 2026-04-21 | [memory-skill-duplication](2026-04-21-memory-skill-duplication.md) | 메모리에 스킬 파일로 유도 가능한 내용을 중복 저장 | low (메모리 오염, 토큰 낭비) | high (가드 없음) | — | — |
| 2026-04-21 | [mac-wsl-todos-desync](2026-04-21-mac-wsl-todos-desync.md) | Mac 과 WSL 이 같은 심사레이더 작업을 병렬로 붙잡고 todos 정합성 파탄 | medium (잘못된 커밋 1건 + 사용자 혼란 + 양 기기 불일치, 다만 실제 파괴적 액션은 없음) | high (현재 구조상 기기 간 todo 상태 sync 가 인간 개입에만 의존) | — | — |
| 2026-04-21 | [launchd-silent-job-dropout](2026-04-21-launchd-silent-job-dropout.md) | launchd 가 등록된 잡을 소리 없이 떨궈서 수 주 동안 자동 스케줄 유실 | medium (자동화 잡 2개가 몇 주간 침묵 실행 실패 가능성) | medium (launchd 수동 편집 시마다 동일 현상 가능) | 1회 | — |
| 2026-04-20 | [terminal-only-reply-missed-telegram](2026-04-20-terminal-only-reply-missed-telegram.md) | Telegram-origin 질문에 터미널로만 답하고 reply 툴 호출 누락 | high (사용자 의사소통 차단) | high (같은 세션에서 여러 번 반복 확인됨) | 6회 | — |
| 2026-04-20 | [telegram-typing-midsession-drop](2026-04-20-telegram-typing-midsession-drop.md) | 텔레그램 typing 표시가 채팅 중 "한번 쏘고" 완전 정지 | low (UX, 응답 중 상태 불투명) | medium | 12회 | — |
| 2026-04-20 | [telegram-client-delivery-lag](2026-04-20-telegram-client-delivery-lag.md) | 텔레그램 답변이 "안 오는 것처럼" 보인 지연 현상 | medium | medium | — | — |
| 2026-04-20 | [irun-locked-iphone](2026-04-20-irun-locked-iphone.md) | /irun 재배포 시 "Could not run Runner.app" 반복 — 실제 원인은 아이폰 잠금 | medium | high | — | — |
| 2026-04-19 | [android-text-selection-twotone](2026-04-19-android-text-selection-twotone.md) | Android 텍스트 선택 블록이 2가지 톤으로 표시됨 | low (시각적 문제, 기능 정상) | low (Flutter TextField BoxHeightStyle 정책 이슈로 고정) | — | — |
| 2026-04-16 | [playwright-chrome-google-login-blocked](2026-04-16-playwright-chrome-google-login-blocked.md) | Playwright Chromium 으로 Google 로그인 시 "안전하지 않은 브라우저" 차단 | medium (자동화 블로킹) | medium (Google 보안 정책 변경 시 재현 가능) | — | — |
| 2026-04-16 | [play-console-testers-google-group](2026-04-16-play-console-testers-google-group.md) | Play Console testers API 가 개별 이메일을 받지 않음 | medium (베타 테스터 자동 추가 블로킹) | low (Google 정책 변경 없으면 고정) | — | — |
| 2026-04-12 | [ios-relaunch-crash](2026-04-12-ios-relaunch-crash.md) | iOS 재실행 시 SharedPreferencesPlugin 크래시 | high (앱 사용 불가) | medium (Flutter 메이저 업데이트 시 lifecycle 관련 회귀 가능) | — | — |

## 룰

- 매 이슈는 자기 파일 하나. `YYYY-MM-DD-<slug>.md`
- 이 INDEX 는 `/issue` 스킬이 저장할 때마다 전체 덮어쓰기로 재생성됨.
- 재발 가능성 high 인데 forcing function 없으면 적극적으로 설치. 이 index 가 "손 안 댄 debt" 추적판 역할도 겸함.
