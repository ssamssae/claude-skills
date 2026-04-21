---
prevention_deferred: null
---

# launchd 가 등록된 잡을 소리 없이 떨궈서 수 주 동안 자동 스케줄 유실

- **발생 일자:** 불명 (2026-04-21 15:30 KST 에 우연히 가시화). 실제 유실 시점은 추정 불가.
- **해결 일자:** 2026-04-21 15:39 KST (`launchctl load` 로 두 잡 복구)
- **심각도:** medium (자동화 잡 2개가 몇 주간 침묵 실행 실패 가능성)
- **재발 가능성:** medium (launchd 수동 편집 시마다 동일 현상 가능)
- **영향 범위:** Mac 본진 launchd (`com.claude.morning-briefing`, `com.claude.daily-sync-and-learn`), 아침 루틴 전반

## 증상

v1.0.2 토큰 절약 작업 중 새 `/evening-wrap` 잡을 load 하면서 `launchctl list | grep com.claude` 로 현재 등록 상태를 점검. 결과에 `morning-briefing` + `daily-sync-and-learn` 2개 잡이 빠져있음.

- plist 파일은 `~/Library/LaunchAgents/` 에 정상 존재
- 문법 오류 없음 (`plutil -lint` 통과 추정)
- 그냥 등록이 안 된 상태. 언제부터인지 전혀 알 수 없음.

실제 영향 확인은 `/tmp/claude-*-wrapper.log` 로 교차 검증 가능했을 텐데, 오늘 가시화 직전까지는 누구도 확인하지 않음 = "조용히 실패" 가 며칠~몇 주 지속됐을 가능성.

## 원인

추정 2가지 (확증 불가):

1. **과거 unload 튕김** — 이전에 다른 `com.claude.*` 잡 unload 작업이 옆 잡까지 영향을 주는 tcc/tmp 조건에서 실행됐을 가능성. launchd 는 실패를 조용히 삼키는 성향이라 로그에도 안 남음.
2. **재부팅 후 로그인 세션 재로드 실패** — `RunAtLoad=true` 인데 파일이 LoginItem 이 아니라 수동 load 에 의존할 경우, 맥 재시작 후 자동 재등록이 없음. (이건 plist 문법/설치 위치 재검토 필요.)

근본 원인은 **등록 상태를 누구도 모니터링 안 함**. plist 파일 존재 ≠ 잡 활성. 이 갭이 진짜 원인.

## 조치

즉시:

1. `launchctl load ~/Library/LaunchAgents/com.claude.morning-briefing.plist`
2. `launchctl load ~/Library/LaunchAgents/com.claude.daily-sync-and-learn.plist`
3. `launchctl list | grep com.claude` 로 4개(morning-briefing + evening-wrap + daily-sync-and-learn + memoyo-beta-worker) 모두 등록 확인

항구적 조치는 아래 예방 참조.

## 예방 (Forcing function 우선)

### 구현됨 (2026-04-22 재발 후 강화)

- **install.sh 를 bootstrap API + 등록 검증으로 교체** — `launchctl unload/load` 가 silent-fail 하는 문제를 `launchctl bootout/bootstrap` 으로 교체. bootstrap 성공 후에도 `launchctl list` 로 재확인해서 drop 감지. 실패 시 stderr 에 명시적 에러 + exit 1. commit: automations `85d7af9`.
- **Stop 훅 LaunchAgent 로드 감지** — `~/.claude/hooks/stop-check-repos-dirty.sh` 가 매 세션 종료 시 `~/Library/LaunchAgents/com.claude.*.plist` 파일 목록과 `launchctl list` 등록 목록을 대조. 미등록 항목 있으면 텔레그램으로 "launchd NOT LOADED" 섹션과 함께 경고. commit: automations `85d7af9`.

### 미구현 — 어제 계획 중 아직 안 한 것

- **launchd 헬스체크 데일리 스크립트** — Stop 훅이 "세션이 한 번이라도 돌면" 감지하는 구조라, 며칠간 세션 없이 지나가는 상황은 여전히 침묵 가능. 추가 필요.
- **수동 편집 전/후 스냅샷 규칙 + feedback_launchd_snapshot_before_edit 메모리** — bootstrap 전환으로 동일 문제 대부분 예방되지만, 사람 손 편집 시 스냅샷은 여전히 가치 있음.
- ~~KeepAlive 재검토~~ — `StartCalendarInterval` 타입엔 부적합 확인돼 드롭.

## 재발 이력

- **2026-04-22 07:02 KST**: `com.claude.daily-sync-and-learn` 등록 누락 재발. 어제 예방 3개가 모두 미이행 상태에서 06:45 자동 발동 실패. 원인 심층 분석 결과 install.sh 의 `launchctl load` 가 silent fail 해서 plist symlink 만 갱신되고 등록은 빠진 상태가 유지됨. 조치: (1) 수동 bootstrap 재등록, (2) 오늘치 동기화 수동 보충 (`2026-04-22-mac.json` 07:02 갱신), (3) install.sh bootout/bootstrap + list 검증으로 교체, (4) Stop 훅 LaunchAgent 로드 감지 추가. commit: automations `85d7af9`.

## 관련 링크

- 커밋: `claude-skills` `c8c967e` (evening-wrap 추가 중 발견)
- 작업일지: `~/daejong-page/worklog-source/2026-04-21_v1.0.2.md` (## A. launchd 세션 통합 섹션 "부수 발견" 부분)
- 메모리(예정): `feedback_launchd_snapshot_before_edit.md`
