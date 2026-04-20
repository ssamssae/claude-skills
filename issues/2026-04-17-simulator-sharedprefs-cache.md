---
prevention_deferred: null
---

# iOS 시뮬레이터 SharedPreferences 가 cfprefsd 캐시로 인해 갱신 안 됨

- **발생 일자:** 2026-04-17
- **해결 일자:** 2026-04-17
- **심각도:** medium (테스트 데이터 조작 자동화 블로킹)
- **재발 가능성:** medium (다른 앱 테스트 자동화에서도 같은 함정)
- **영향 범위:** 메모요 스크린샷·테스트 자동화 (iOS Simulator)

## 증상
시뮬레이터의 메모요 플러그인 plist 를 `PlistBuddy`/`plutil` 로 직접 수정해 메모 데이터를 주입했지만, 앱을 재실행해도 옛 데이터가 그대로 보이고 수정 내용이 반영되지 않음. 파일 자체는 바뀌어 있는데 앱 레벨에서는 보이지 않는 상태.

## 원인
iOS 는 **`cfprefsd`(Preferences Daemon) 가 plist 파일 내용을 메모리에 캐시** 함. 파일을 외부에서 바꿔도 cfprefsd 가 캐시를 invalidate 하지 않으면 앱이 옛 값을 계속 읽음. PlistBuddy 경로로 파일만 바꾸는 방식은 이 캐시를 건드리지 못함.

## 조치
- PlistBuddy/plutil 직접 수정 방식 포기
- 대신 plist 파일을 먼저 원하는 상태로 생성
- `xcrun simctl spawn <sim_id> defaults import <domain> <plist>` 로 시뮬레이터 내부의 `defaults` 커맨드를 실행해 cfprefsd 를 거쳐 값이 들어가게 함
- 이 경로는 cfprefsd 에 정상적으로 반영돼 앱 재실행 시 즉시 보임

## 예방 (Forcing function 우선)
- 앞으로 iOS 시뮬레이터 preferences 주입은 **`simctl spawn defaults import` 만** 쓴다. PlistBuddy 로 plist 파일 직접 수정은 금지.
- 메모요 스크린샷 자동화 스크립트 상단에 이 규칙 주석.
- 같은 함정은 다른 CFPreferences 기반 데이터(`NSUbiquitousKeyValueStore` 등) 에도 있을 가능성 → 새 자동화 작성 시 이 이슈 링크 확인.

## 재발 이력
_(없음)_

## 관련 링크
- 작업일지: docs/worklog/2026-04-17
