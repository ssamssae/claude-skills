---
date: 2026-05-04
slug: lottocalc-irun-white-screen
status: open
---

# lottocalc irun 흰화면 버그

## 증상

- iOS 26.3.1 (iPhone17, device 00008150-0018459C2161401C) 실기기에서 debug/release 모두 흰화면
- debug 모드: "The Dart VM Service was not discovered after 60 seconds" → iproxy Dart VM attach 실패
- release 모드: `flutter run --release` 가 빌드를 `build/ios/Release-iphoneos/`에 생성하지만 Flutter가 `build/ios/iphoneos/`를 기대 → 코드서명 없는 아티팩트 설치 시도 → "No code signature found" 설치 실패

## 시도한 것

1. `flutter run --debug` → Dart VM 60초 타임아웃, 흰화면
2. `flutter run --release` (background) → 경로 불일치로 코드서명 없는 빌드 설치 → 흰화면 후 크래시
3. Flutter 3.41.8 → 3.41.9 업그레이드 후 재시도
4. `flutter build ios --release` + `devicectl install + launch` → 설치 성공, 프로세스 살아있음, 그래도 흰화면

## 환경

- Flutter: 3.41.9 (stable, 2026-04-29)
- Xcode: 26.4.1
- iOS: 26.3.1 (23D8133)
- Device: iPhone17 (강대종의 iPhone (2))

## 원인 가설

iOS 26 + Flutter 3.41.9 Metal 렌더링 호환 문제. flutter doctor에서 CocoaPods 미설치 경고도 있음.

## 다음 시도

- `flutter doctor` 전체 출력 확인 및 CocoaPods 이슈 해결
- Flutter stable 최신 채널 재확인
- iOS 26 Flutter 이슈 트래커 검색
- 다른 앱(hanjul 등)도 같은 증상인지 확인 → 기기 수준 문제인지 판별
