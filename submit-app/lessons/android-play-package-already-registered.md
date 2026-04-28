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
**진짜 원인은 다른 사람 점유가 아니라 강대종님 본인의 Windows debug.keystore 잔재였음**.

1. WSL 에서 hanjul debug 빌드 시 Windows `/mnt/c/Users/USER/.android/debug.keystore` (4/19 자동 생성, SHA-256 `05:CF…`) 자동 사용
2. 그 debug 키로 서명된 APK 가 Pixel7 에뮬 또는 S24 에 한 번 깔림
3. Play Protect 가 그 SHA 를 com.ssamssae.hanjul 의 "기존 서명 키" 로 잡고 영구 바인딩
4. 강대종님이 신규로 com.ssamssae.hanjul 등록하려 할 때 Play 가 그 debug 키의 비공개 키 소유권 증명 요구 → release upload keystore (F4:A7) 와 미스매치

Play 는 패키지 이름 + 첫 등록 시 서명 키 (이번엔 debug 키) 를 영구 바인딩하므로, debug 키로 등록되어버린 패키지 이름은 사실상 회수 어려움.

## 해결 (강대종님 옵션 B 채택)

1. **com.ssamssae.hanjul 임시 등록은 보존** (삭제 안 함, 미래 재시도 가능성)
2. **com.daejongkang.hanjul 로 패키지 이름 전환** — 본명 도메인 (다른 4개 앱 컨벤션) 으로 충돌 0
3. Android `build.gradle.kts` namespace+applicationId, MainActivity.kt 디렉토리+package + iOS pbxproj 6군데 + store/launch-checklist + daejong-page todos 일괄 변경
4. com.daejongkang.hanjul Play Console 등록 → 깨끗한 패키지라 **SHA-256 직접 입력 폼** (APK 업로드 단계 없음) → F4:A7 입력 → "검토 중"
5. com.ssamssae.hanjul Apple Dev Portal Bundle ID 도 미사용 폐기 (강대종님 2026-04-28 11:31 KST 결정), com.daejongkang.hanjul 신규 등록

전체 사고 1시간 소요 (19:25~20:35 KST). 자세한 추적 과정은 메모리 `project_hanjul_wsl_build_artifact.md` 참조.

## 재발 방지 체크리스트
- [x] **/submit-app Step 0.4 신설** (2026-04-28 적용) — Android 빌드 전 Play 패키지 등록 사전 점검:
  1. `keytool -list -v -keystore <SoT.jks>` 로 보유 SoT SHA-256 추출
  2. Play Console 패키지 이름 등록 페이지 (또는 Play API `edits.insert` probe) 로 등록된 SHA-256 후보 확인
  3. SHA 매칭 안 되면 즉시 중단 + 옵션 A/B/C 제시. 출시일 직전이 아니라 빌드 전 단계에서 발견
- [x] **신규 패키지는 com.daejongkang.* 도메인 우선** (`feedback_new_package_use_daejongkang_domain.md`) — ssamssae 같은 일반 닉네임 도메인은 점유 충돌 위험. 본명 도메인은 사실상 충돌 0
- [ ] **WSL 에서 debug 빌드 시 Windows debug.keystore 자동 사용 주의** — `/mnt/c/Users/USER/.android/debug.keystore` 가 release upload keystore 와 다르므로 폰/에뮬에 깔린 적 있으면 신규 패키지 Play 등록 차단됨. 신규 패키지 등록 전 폰/에뮬에서 그 패키지 이름의 옛 빌드 삭제 또는 처음부터 release 키로만 빌드
- [x] **출시 14일 전 사전 등록 권고** — Play 신규 패키지 정책(2026-03 시행) 따라 패키지 이름 등록은 빌드 직전이 아니라 **출시 사이클 시작 시점에 수행**
- [x] **keystore-sot.md 에 "Play 등록 SHA" 컬럼 추가** (2026-04-28 적용)
- [ ] **이전 keystore 자산 inventory** — 강대종님 과거 사용 기기/keystore 모두 검색해서 현존 보유 키 매트릭스 작성
