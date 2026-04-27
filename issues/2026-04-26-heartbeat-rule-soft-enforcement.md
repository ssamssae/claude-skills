---
prevention_deferred: null
---

# 작업 중 5분 하트비트 룰 강제력 부재로 12분간 침묵

- **발생 일자:** 2026-04-26 09:58~10:10 KST
- **해결 일자:** 2026-04-26 10:15 KST (이슈 등록 + nudge hook 설계 결정)
- **심각도:** medium (UX, 사용자가 진행 상태 파악 못 함)
- **재발 가능성:** high (메모리 룰 만으로는 강제력 없음 — 작업 몰입 시 timestamp 추적 실패가 일상)
- **영향 범위:** 모든 장시간 텔레그램 inbound 작업 세션. 이번엔 Substack 마크다운 fix 작업.

## 증상
강대종님이 09:55 KST 에 보낸 directive 로 Mac 새 세션이 Substack Ep1/Ep2 포맷 픽스 작업 시작. 하트비트 1 (09:56), 하트비트 2 (09:58) 까지는 정상 발송. 그 후 12분간 작업하면서 하트비트 3 (10:03 예정) 누락. 10:10:03 에 강대종님이 "하트비트 3 또 안 보냈고 입력중도 안쏴짐 이슈등록하고 조치해줘" 텔레그램 도착. 같은 시간대에 typing daemon 도 죽어 (별건 이슈) 사용자 폰에는 "Claude 가 멈춤" 처럼 보임.

## 원인
1. **메모리 룰 `feedback_heartbeat_during_work.md` 의 강제력 한계.** Claude 가 작업 몰입 상태에서 마지막 reply 시각을 추적 안 함. 매 도구 호출마다 wall clock 비교를 하지 않으므로 "지금 5분 지났나?" 판단이 자동으로 들지 않음.
2. **시간 추적 메커니즘 부재.** 텔레그램 inbound `<channel>` 태그의 `ts` 는 받지만, 그 이후 경과 시간을 매 도구 호출 직전에 검사하는 구조가 없음.
3. **부수: typing daemon 도 silent death** (별건 이슈 — `2026-04-20-telegram-typing-midsession-drop.md` 의 재발). typing 이라도 살아있었으면 강대종님이 "작동 중" 으로 보고 12분 침묵을 덜 심각하게 받았을 것. 두 layer 의 fallback 이 동시에 무너진 게 결정적.

## 조치
1. (이번 세션) 누락 즉시 인정. 강대종님에게 reply 보내고 이슈 등록 시작.
2. (구조적, 작성 마감 2026-04-27) **PreToolUse hook 기반 5분 nudge** 설계:
   - `hooks/heartbeat-reminder.sh` 신규 추가
   - `/tmp/claude-last-tg-reply-${CLAUDE_SESSION_ID}.ts` 파일에 마지막 reply timestamp 기록
   - PostToolUse hook 이 `mcp__plugin_telegram_telegram__reply` 호출 후 timestamp 갱신
   - PreToolUse hook 이 매 도구 호출 직전 `now - last > 300` 검사, 초과 시 stderr 로 `⏰ 마지막 reply 이후 N초 경과. 5분 하트비트 보낼 시간` nudge 출력 (차단 X, 알림 O)
   - 텔레그램 inbound 가 활성인 세션 한정 (`/tmp/claude-tg-active-${SESSION}.flag` 같은 indicator)
3. 04-20 typing daemon silent death 이슈에 재발 이력 한 줄 추가 (이번 09:55:03 ~ 10:10:02 구간 daemon 24413 silent death).

## 예방 (Forcing function 우선)
- **PreToolUse hook 의 5분 timestamp 비교 nudge** — 이게 메인 forcing function. 메모리 룰의 약한 권고를 hook stderr 경고로 끌어올림. **2026-04-27 19:30 KST 구현 완료** (commit 별도 — claude-automations `hooks/heartbeat-reminder.sh` + `hooks/typing-keepalive.sh` + settings.json wire-up).
- **typing indicator 채널은 메시지 채널과 별도로 강제 시작.** 2026-04-27 재발 시점 사용자 의도 명확화 — "쏜다는 게 입력 중 표시" (메시지 폭탄 아님). PreToolUse hook 이 텔레그램 inbound 활성 세션 검출하면 typing daemon 자동 spawn (4초 sendChatAction 루프). 메시지(💓 하트비트 N) 트랙과 분리 운영. 두 트랙 모두 죽으면 폰에 침묵.
- **이중 침묵 자동 검출**: typing daemon heartbeat log 가 끊긴 시점에 reply hook 의 last-reply ts 도 5분 이상 stale 이면 morning-briefing 에 "이중 침묵 N분" 항목 추가. 두 layer 가 동시에 무너지는 패턴이 가장 위험하므로 별도 추적.
- **claim 마커가 아닌 시간 마커**: hook 이 nudge 띄울 때 단순 경고 외에 도구 호출명/파일명도 함께 출력 → 무엇 하다가 침묵했는지 자동 라벨.

## 재발 이력
- **2026-04-26 12:47~13:33 KST (46분 침묵)** — WSL 본진 세션, 데스크탑·노트북 로컬 LLM 부트스트랩. 텔레그램 첫 inbound 12:47 받고 이후 작업 들어가면서 하트비트 0회 발송. 13:33 KST 강대종님이 "왜 하트비트 없어" 지적 → 즉시 하트비트 1 reply. **이번엔 12분이 아니라 46분 침묵** — 첫 발생 (09:58~10:10) 보다 4배 길어짐. 메모리 룰 강제력 부재 재확인. 같은 날 두 번 재발 = forcing function hook 구현을 다음 날(04-27) 까지 미루지 말고 **오늘 안에 wire-up** 해야 함.

- **2026-04-26 18:14 ~ 19:05 KST (51분 침묵)**: 약먹자/더치페이 ASC Information Needed 대응 작업 흐름. 18:14 reply (id 7703) 에 "진행 단계마다 한 줄씩 보고할게요" 명시 약속까지 했는데, 그 후 약먹자 pub get → 빌드 23초 → 시뮬 install/launch → 더치페이 pub get → 빌드 15초 → computer-use request_access 까지 도구만 6단계 쌓이고 reply 0번. 강대종님이 7704 (19:05 "하는중이야? 입력중 하트비트 안나옴 이슈등록후 재발방지") + 7705 (19:07 "mcp 끊김?") 로 지적. 09:55 12분 침묵 대비 **4배 길어진 51분**. 원인: PreToolUse hook 미구현(prevention_deferred 2026-04-27) 상태 그대로 + 명시 약속 위반(self-binding 도 fail) — 메모리 룰 + 자기 약속 둘 다 강제력 0 재확인. 2026-04-27 마감 forcing function 우선순위 high 격상 권고.

- **2026-04-27 19:21 KST (typing indicator 채널 자체 미작동)**: WSL 본진 세션, 심사레이더 v0.2 emulator 검증 → /arun review_radar 빌드 흐름. 강대종님 텔레그램 "왜 핑 4초마다 안 쏴주지 작업중인데" (id 3349). Claude 가 처음에 "메시지 폭탄 의미" 로 잘못 받음 → 강대종님 정정 "쏜다는 게 입력 중 ... 표시를 말하는 거야" (id 3352). **핵심 발견**: 메시지(💓 하트비트) 트랙은 milestone 단위 발송 OK 였지만 **typing indicator 트랙은 한 번도 안 띄움**. 즉 두 트랙이 별도여야 한다는 룰 자체가 메모리·이슈에 없었음. 이번 시점에 (1) 메모리 `feedback_heartbeat_during_work.md` 두 트랙 분리 룰 박음 + (2) 04-26 prevention_deferred 마감일 도래로 forcing function (`heartbeat-reminder.sh` PreToolUse hook + `typing-keepalive.sh` daemon wrapper) 진짜 구현 + settings.json wire-up 진행. 강대종님 직접 지적 "미작동 이슈 올리고 재발방지 조치" (id 3355).

## 관련 링크
- 메모리: `feedback_heartbeat_during_work.md` (룰 정의)
- 관련 이슈: `2026-04-20-telegram-typing-midsession-drop.md` (typing daemon 측 silent death — 같은 시간대 재발, 분리 추적)
- 텔레그램 메시지: id 7393 (강대종님 지적), id 7395 (인정 reply)
- 이번 세션 작업: Substack Ep1/Ep2 마크다운 → 리치포맷 변환 (별건, 성공)
