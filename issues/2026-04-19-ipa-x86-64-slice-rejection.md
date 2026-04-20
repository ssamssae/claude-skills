---
prevention_deferred: null
---

# 약먹자 IPA 에 x86_64 슬라이스가 섞여 App Store 검증 실패

- **발생 일자:** 2026-04-19
- **해결 일자:** 2026-04-19
- **심각도:** high (App Store 제출 블로킹)
- **재발 가능성:** medium (Flutter + Pods 빌드 설정 회귀 가능)
- **영향 범위:** 약먹자 iOS 릴리즈 빌드

## 증상
약먹자 IPA 를 App Store Connect 로 올렸더니 검증 단계에서 **불필요한 x86_64 아키텍처 슬라이스가 포함돼 있다** 는 사유로 reject. 실제 배포 타겟은 arm64 디바이스만이라 x86_64 는 불필요한 용량만 차지하고 정책상 허용되지 않음.

## 원인
일부 Pod 또는 Flutter 엔진 아티팩트가 **시뮬레이터용 x86_64 슬라이스** 를 포함한 채 릴리즈 빌드에 섞여 들어갔음. Xcode `Valid Architectures` 혹은 `Excluded Architectures` 설정이 시뮬레이터와 디바이스 빌드에서 완전히 분리되지 않은 상태.

## 조치
- Xcode 프로젝트의 `Excluded Architectures` 에 시뮬레이터 SDK 에 대해서만 x86_64 를 남기고, 디바이스 SDK 에서는 arm64 만 포함하도록 정리
- Pods 쪽 빌드 설정도 동일하게 맞춤
- clean build 후 IPA 재생성 → `lipo -info` 로 arm64 만 들어있는지 확인
- App Store Connect 재업로드 성공

## 예방 (Forcing function 우선)
- iOS 릴리즈 빌드 전에 `lipo -info <실행파일>` 로 아키텍처 확인을 **배포 스크립트의 고정 단계** 로 박아둠. arm64 이외 슬라이스가 보이면 에러로 중단.
- 이 체크를 약먹자 배포 스크립트에 우선 반영하고, 이후 다른 iOS 앱(메모요·더치페이 등) 배포 스크립트에도 확산.
- 관련 메모리 한 줄: "iOS 릴리즈 IPA 는 arm64-only, 배포 직전 lipo 검증 필수".

## 재발 이력
_(없음)_

## 관련 링크
- 작업일지: docs/worklog/2026-04-19
