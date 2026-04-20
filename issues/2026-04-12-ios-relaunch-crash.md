---
prevention_deferred: null
---

# iOS 재실행 시 SharedPreferencesPlugin 크래시

- **발생 일자:** 2026-04-11 (첫 증상 관측)
- **해결 일자:** 2026-04-12 (근본 원인 제거 완료)
- **심각도:** high (앱 사용 불가)
- **재발 가능성:** medium (Flutter 메이저 업데이트 시 lifecycle 관련 회귀 가능)
- **영향 범위:** 메모요(simple_memo_app) iOS 빌드

## 증상
앱을 처음 설치하고 실행한 직후에는 정상. 사용자가 앱을 한 번 종료한 뒤 다시 열면 곧바로 `EXC_BAD_ACCESS` 크래시가 발생하며 홈 화면으로 떨어짐. 재현 조건: 메모 1건 이상 저장 후 앱 완전 종료 → 재실행.

## 원인
Flutter 3.38 부터 도입된 **UIScene lifecycle** 로의 마이그레이션이 AppDelegate/Info.plist/Podfile 에 일관되게 들어가지 않아, iOS가 엔진 초기화 전에 Scene 복원을 먼저 시도함. 이 시점에 SharedPreferencesPlugin 이 등록되기 전인 채 복원 데이터를 읽으려다 댕글링 포인터에 접근. 추가로 메모 ID 가 `millisecondsSinceEpoch` 기반이라 같은 밀리초에 두 건 생성되면 ID 충돌이 나서 상태 복원이 망가지는 잠재 버그도 함께 있었음.

## 조치
- iOS UIScene 관련 설정 제거 (AppDelegate 기반 lifecycle 로 되돌림)
- AppDelegate, Info.plist, Podfile 의 Flutter 관련 항목 정렬
- `runZonedGuarded` 로 메인 영역을 감싸 uncaught exception 시 크래시 대신 로그가 남게 보강
- 메모 ID 생성을 `UUID v4` 로 교체해 충돌 가능성 제거
- 재실행 10회 연속 정상 동작 확인 후 릴리즈

## 예방 (Forcing function 우선)
- 앞으로 Flutter 메이저/마이너 업데이트 후에는 iOS 빌드에서 **앱 종료 후 재실행** 시나리오를 기본 smoke test 에 포함. simple_memo_app 의 CI/수동 체크리스트에 "clean install → 메모 1건 저장 → 앱 강제종료 → 재실행 → 메모 유지 확인" 3단계 명시.
- ID 생성 타임스탬프 방식은 **금지**, 새 Flutter 앱 스캐폴드(flutter-factory) 의 local_store 템플릿에 UUID v4 기본값을 박아둠.

## 재발 이력
_(없음)_

## 관련 링크
- 복구 커밋: simple_memo_app 4/12 스토리
- 작업일지: docs/worklog/2026-04-11, 2026-04-12
- 메모리: project_memoyo_build_naming.md
