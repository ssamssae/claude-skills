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

- **launchd 헬스체크 스크립트 + 데일리 실행**: `~/.claude/automations/scripts/launchd-health-check.sh` 신설해서
  1. `~/Library/LaunchAgents/com.claude.*.plist` 파일 목록 수집
  2. `launchctl list | grep com.claude` 등록 목록 수집
  3. 두 집합의 차이(파일 존재 but 미등록) 를 찾아 텔레그램 알림
  4. `daily-sync-and-learn` Python 스크립트 안에 이 체크를 inline 으로 태우면 매일 06:45 자동 실행되므로 별도 cron 필요 없음
- **launchd 수동 편집 전/후 스냅샷 규칙**: 어떤 `load`/`unload` 작업 전에 `launchctl list | grep com.claude > /tmp/launchd-before` 로 저장, 작업 후 `> /tmp/launchd-after` 로 저장, `diff` 로 의도한 잡만 변경됐는지 확인. 이 규칙을 `feedback_launchd_snapshot_before_edit.md` 메모리로 박기.
- **plist 설치 시 RunAtLoad 외에 KeepAlive 고려**: 주기 실행 타입 잡에 `KeepAlive` 설정이 맞는지 재검토. (단, `StartCalendarInterval` 잡은 KeepAlive 적용 부적합 — 타입별 판단 필요.)

## 재발 이력

_(없음)_

## 관련 링크

- 커밋: `claude-skills` `c8c967e` (evening-wrap 추가 중 발견)
- 작업일지: `~/daejong-page/worklog-source/2026-04-21_v1.0.2.md` (## A. launchd 세션 통합 섹션 "부수 발견" 부분)
- 메모리(예정): `feedback_launchd_snapshot_before_edit.md`
