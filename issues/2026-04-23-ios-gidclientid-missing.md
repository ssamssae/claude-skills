---
prevention_deferred: null
---

# iOS GoogleSignIn GIDClientID 누락 크래시 (심사레이더)

- **발생 일자:** 2026-04-23 23:40 KST
- **해결 일자:** 2026-04-24 00:05 KST
- **심각도:** high (앱 첫 화면 전 강제 종료)
- **재발 가능성:** high (google_sign_in 쓰는 신규 Flutter 앱 iOS 첫 빌드에서 동일하게 재현)
- **영향 범위:** 심사레이더(review_radar) iOS 빌드. 확대 리스크: flutter-factory 로 찍어내는 모든 앱 중 google_sign_in 의존하는 것 전체.

## 증상
심사레이더 앱 첫 iOS 시뮬 런치 시 첫 프레임 뜨기 전 강제 종료. Xcode/Mac 크래시 리포트:

```
NSInvalidArgumentException: 'No active configuration. Make sure GIDClientID is set in Info.plist.'
```

스택: `GIDSignIn signInWithOptions` → `FLTGoogleSignInPlugin signInWithHint:additionalScopes:completion:` → Flutter PlatformMessageHandler → HomeScreen initState 의 자동 refresh.

## 원인
RealGmailService 구현이 **Android 만 염두에 두고 쓰여짐**. 해당 파일 주석 그대로 "Android 는 package name + SHA-1 매칭이라 Client ID 코드에 넣을 필요 없음". iOS 는 bundle ID 매칭이 아니라 Info.plist 의 `GIDClientID` 키로 OAuth 설정을 읽는데 이 키가 한 번도 추가된 적 없음. 그간 테스트는 Galaxy S24 에서만 진행돼서 iOS 경로가 런타임에 발견되지 않음.

## 조치
1. GCP `review-radar-493922` 프로젝트에 iOS OAuth Client 신규 생성 (bundle `com.ssamssae.reviewRadar`)
2. `ios/Runner/Info.plist` 에 2개 키 추가:
   - `GIDClientID` = `1056684831781-2680sm18t1lhnusu5ooh200j122de6mh.apps.googleusercontent.com`
   - `CFBundleURLTypes` → `CFBundleURLSchemes` 에 reversed client ID `com.googleusercontent.apps.1056684831781-2680sm18t1lhnusu5ooh200j122de6mh`
3. 첫 iOS 빌드 부산물(CocoaPods integration: project.pbxproj Pods refs, workspace entry, Podfile.lock) 같이 커밋
4. iPhone 17 시뮬(iOS 26.2) 재설치 후 Google 로그인 consent 다이얼로그 정상 노출 확인

## 예방 (Forcing function 우선)
- **flutter-factory 템플릿에 iOS OAuth 체크 스크립트 추가.** `tools/check_ios_oauth.sh`: `pubspec.yaml` 에 `google_sign_in` 또는 다른 OAuth 의존성이 있으면 `ios/Runner/Info.plist` 에 `GIDClientID` 키 존재 여부 검사. `flutter build ios` 전 pre-build 단계 or new_app.sh 마지막 검증 단계에 자동 실행. 키 없으면 빨간 경고 + "iOS OAuth Client 만들고 Info.plist 설정 필수" 링크.
- Dart 레벨 fail-fast 추가: `RealGmailService._ensureSignedIn()` 시작 부분에 `if (Platform.isIOS)` 일 때 GIDClientID 누락 감지 시 네이티브 크래시 전에 Dart `StateError` 로 친절하게 터지도록. Obj-C NSException 보다 디버깅 훨씬 쉬움.
- flutter-factory README 의 "OAuth 붙일 때" 섹션에 **iOS/Android 별 OAuth Client 각각 필요** 를 첫 문장으로 명시.

## 재발 이력
_(없음)_

## 관련 링크
- 커밋: https://github.com/ssamssae/review_radar/commit/41aabea
- 메모리: `project_review_radar.md` (Android SHA-1 기록 있음, iOS 는 누락 상태였음)
- 텔레그램 트리거: id 6438 ("앱 실행이 안되 시뮬레이터 돌려보고 디버그")
