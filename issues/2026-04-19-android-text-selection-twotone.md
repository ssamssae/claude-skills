---
prevention_deferred: null
---

# Android 텍스트 선택 블록이 2가지 톤으로 표시됨

- **발생 일자:** 2026-04-19
- **해결 일자:** 2026-04-19
- **심각도:** low (시각적 문제, 기능 정상)
- **재발 가능성:** low (Flutter TextField BoxHeightStyle 정책 이슈로 고정)
- **영향 범위:** 메모요 Android 빌드 텍스트 선택 UX

## 증상
Android 에서 메모 본문 텍스트를 드래그 선택하면 **선택 블록이 두 가지 톤** 으로 나뉘어 표시됨. 문자 자체 영역과 line-spacing 여백 영역의 배경색이 달라 블록이 계단식으로 끊긴 것처럼 보임. iOS 에서는 정상이라 Android 만 해당.

## 원인
TextField 의 `selectionHeightStyle` 로 `BoxHeightStyle.max` 를 쓰면 line-spacing 을 포함한 영역까지 선택 박스가 채워지는데, Android 쪽 렌더러가 이 영역을 다른 톤으로 페인트함. iOS 는 같은 스타일이어도 균일 톤으로 렌더해서 이 문제가 안 보였음. 즉 플랫폼별 렌더링 차이.

## 조치
- `selectionHeightStyle` 을 `BoxHeightStyle.max` 에서 `BoxHeightStyle.includeLineSpacingMiddle` 로 교체
- 이 스타일은 양쪽 플랫폼에서 균일한 높이로 렌더링됨
- Android/iOS 둘 다에서 선택 블록이 단일 톤으로 표시되는 것을 확인 후 릴리즈

## 예방 (Forcing function 우선)
- Flutter TextField `BoxHeightStyle` 선택은 **플랫폼별 렌더링 차이가 크므로, 양쪽 시뮬레이터에서 동시 확인** 하는 것을 기본 체크리스트에 포함. Android 에서만 이상한 스타일이 나오면 이 이슈 링크로 연결.
- `max` 대신 `includeLineSpacingMiddle` 을 플랫폼 통일 기본값으로 메모요 프로젝트에 박아둠. 다른 Flutter 앱 생성 시 flutter-factory 템플릿에도 반영 검토.

## 재발 이력
_(없음)_

## 관련 링크
- 작업일지: docs/worklog/2026-04-19
