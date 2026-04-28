---
platform: android
severity: blocking
category: signing
first_hit: 2026-04-28
hits: 1
source: auto-from-session
---

# Play 가 com.X.Y 패키지를 'already in use' 로 거부 (서명 키 미스매치)

## 증상
신규 앱 등록 시 Play Console 패키지 이름 등록 페이지에서:

> "com.ssamssae.hanjul 패키지는 이미 Android에서 사용 중. 기존 서명 키 소유권 증명 필요"

후보 SHA-256 1개 (`05:CF…`) 만 떠있고 우리 release upload keystore (`F4:A7…`) 와 다름. APK 업로드 다이얼로그까지 가도 비공개 키 매칭이 안 돼 차단. 한줄일기 1900원 유료 출시 19:00 KST 직전 발견 → 26분간 키 추적으로 헤맴.

## 원인
**Mac SoT keystore (2026-04-25 생성, F4:A7…) 보다 이전 시점**에 누군가 com.ssamssae.hanjul 을 Play 에 등록 (05:CF 출처 불명, 강대종님 과거 다른 기기/이전 keystore 추정). Play 는 패키지 이름 + 첫 등록 시 서명 키를 영구 바인딩하므로 비공개 키 분실 = 패키지 이름 영구 사망.

가능한 옵션:
- **A. 비공개 키 복원** — 거의 불가능 (출처 불명)
- **B. 패키지 이름 변경** — 다른 4개 앱 컨벤션 (com.daejongkang.* 또는 com.ssamssae.*) 따라 신규 이름 결정. AndroidManifest.xml + build.gradle.kts + ApplicationId + iOS Bundle ID(필요 시)까지 일괄 변경
- **C. 미루기** — 출시 자체 보류

## 해결
이번 회: 진행 중. (강대종님 결정 시점에 추가 기록)

S24 폰에 깔린 hanjul 의 서명 키는 옵션 G (`adb shell pm dump com.ssamssae.hanjul | grep -i sign`) 로 확인 가능 — 만약 폰 APK 가 05:CF 로 서명돼있으면 그 keystore 가 어딘가 강대종님 자산에 남아있을 가능성 1% 시사.

## 재발 방지 체크리스트
- [ ] **/submit-app Step 0.4 신설** — Android 빌드 전 Play 패키지 등록 사전 점검:
  1. `keytool -list -v -keystore <SoT.jks>` 로 보유 SoT SHA-256 추출
  2. Play Console 패키지 이름 등록 페이지 (또는 Play API `edits.insert` probe) 로 등록된 SHA-256 후보 확인
  3. SHA 매칭 안 되면 즉시 중단 + 옵션 A/B/C 제시. 출시일 직전이 아니라 빌드 전 단계에서 발견
- [ ] **출시 14일 전 사전 등록 권고** — Play 신규 패키지 정책(2026-03 시행) 따라 패키지 이름 등록은 빌드 직전이 아니라 **출시 사이클 시작 시점에 수행**. 충돌 시 14일 여유로 패키지 이름 변경 가능
- [ ] **keystore-sot.md 에 "Play 등록 SHA" 컬럼 추가** — SoT keystore 만이 아니라 "Play 가 인정하는 키" 도 같이 기록. 둘이 어긋나면 등록 시점 추적 가능
- [ ] **이전 keystore 자산 inventory** — 강대종님 과거 사용 기기/keystore 모두 검색해서 현존 보유 키 매트릭스 작성. 향후 같은 패키지 출시 시도 시 분실 키 후보 매칭
