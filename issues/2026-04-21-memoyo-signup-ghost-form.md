---
prevention_deferred: null
---

# 메모요 스토어 드롭 후 2주 동안 홈페이지 사전예약 폼이 살아있어서 이메일 계속 수집

- **발생 일자:** 2026-04-07 전후 (사전예약 폼이 의미 없어진 시점, 추정). 실제로는 2026-04-19 스토어 드롭 결정 이후 최소 2일.
- **해결 일자:** 2026-04-21 18:30 KST (`e80d213` 커밋, portfolio.html showSignup 제거)
- **심각도:** low (개인 데이터 소규모 + 악의적 수집은 아님). 단 사용자 기대 이탈 위험은 있음.
- **재발 가능성:** medium (다른 앱/스킬 드롭 시 동일 구조 — 백엔드만 끄고 입력 채널 남김 — 재현 가능)
- **영향 범위:** daejong-page portfolio.html, 메모요 Apps Script endpoint, 사전예약자 기대치

## 증상

저녁 세션(18:27 KST) 에 대종님이 "메모요 배터워커는 뭐야" 라고 물어서 점검 중 발견:

- `com.memoyo.beta-worker.plist` 는 `~/Library/LaunchAgents/_disabled/` 에 격리됨 (4/19 드롭 결정 후 처리됨)
- 하지만 `portfolio.html` Hero 영역의 `showSignup` 플래그는 `true`
- 메모요 카드 status 문자열이 "TestFlight / 비공개 테스트 중" 으로 2주 전 상태 그대로 stale
- 사용자가 홈페이지에서 이메일을 입력하면 여전히 Apps Script 엔드포인트로 전송되고 시트에 append 됨
- 워커는 죽어있으니 Google Groups 자동 초대는 안 일어남 — **사용자는 등록됐다고 믿지만 실제로는 아무 일도 안 일어남**

## 원인

서비스 드롭을 "백엔드 정리" 로만 이해하고 넘어간 것. 4/19 에 드롭 결정할 때:

- ✅ 워커 launchd 비활성
- ✅ todos.md 에 "메모요 스토어 출시 드롭" 기록
- ❌ 홈페이지 입력 폼 차단 누락
- ❌ 홈페이지 상태 문자열 갱신 누락
- ❌ 이미 저장된 사전예약자들에게 "드롭 결정" 고지 안 함

드롭 체크리스트가 없어서 어디까지가 "완료" 인지 기준이 없음. 결과적으로 입력 채널이 2주간 방치.

## 조치

커밋 1개:

- **`daejong-page` `e80d213`** — portfolio.html 7줄 변경
  - Hero 영역 `showSignup` 플래그 제거 → 사전예약 폼 DOM 제거
  - 메모요 카드 status 문자열: "TestFlight / 비공개 테스트 중" → "스토어 제출 보류 중"
  - Apps Script 엔드포인트는 **보존** (이미 받은 30여 건 데이터 유지 목적)

기존 등록자 대상 고지는 **미조치** — 현재 확인 필요 사항으로 남김.

## 예방 (Forcing function 우선)

- **서비스 드롭 체크리스트 스킬 신설**: `/drop-service <name>` 스킬을 만들어서 인자로 앱/기능 이름을 받으면 아래 3단을 순서대로 확인·안내:
  1. **백엔드** — launchd/cron/systemd 잡, 워커 스크립트, 환경변수, 토큰
  2. **입력 채널** — 프론트 폼, API endpoint (공개 여부), CLI 트리거
  3. **상태 표시** — 홈페이지 status 문자열, README, 포트폴리오 카드, todos.md 메타
  각 단계 체크리스트 통과해야만 "드롭 완료" 로 기록하고 todos.md 에 반영. 수동 호출 시에도 개별 앱 단위로 누락 없이 처리됨.
- **대안(가벼움)**: `/drop-service` 까지 안 만들고, 메모리 파일 `feedback_service_drop_checklist.md` 로 3단 체크리스트만 박아서 드롭 발화 감지 시 자동 로드되게. forcing function 강도는 떨어지지만 비용 낮음.
- **정기 감사**: 한 달에 한 번 `/morning-briefing` 섹션에 "포트폴리오 카드 status ↔ 현실 일치 감사" 한 줄 추가 — portfolio.html status 문자열과 실제 서비스 상태(워커 활성/스토어 등재 상태) 가 일치하는지 확인.

## 재발 이력

_(없음)_

## 관련 링크

- 커밋: `daejong-page` `e80d213`
- 작업일지: `~/daejong-page/worklog-source/2026-04-21_v1.0.3.md` (## 메모요 베타테스터 모집 전면 드롭 섹션)
- 메모리(예정): `feedback_service_drop_checklist.md`
- 관련 기존 메모리: `project_memoyo_beta_auto_add.md` (DROP 2026-04-21 마커 반영 완료)
