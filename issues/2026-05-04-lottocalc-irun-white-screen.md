---
date: 2026-05-04
slug: lottocalc-irun-white-screen
status: resolved
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

## 해결 (2026-05-04)

실제 원인: 이전 `flutter run` 프로세스가 mac-mini에 좀비로 남아 기기 포트를 점유 → 새 세션이 Dart VM attach 실패.

해결 방법:
```bash
ssh mac-mini "pkill -f 'flutter run.*lottocalc'; pkill -f 'iproxy'"
```
이후 `flutter run --debug` 재실행 → Dart VM 연결 성공, 앱 정상 실행.

**실제 흰화면 원인은 iOS 26 렌더링 문제가 아니라 좀비 프로세스 점유였음.**

## 예방

irun 재시도 시 먼저 mac-mini 에서 이전 flutter/iproxy 프로세스 kill 후 실행.
