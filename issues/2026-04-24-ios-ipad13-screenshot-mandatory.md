---
prevention_deferred: null
---

# App Store 심사 제출: iPad 13" 스크린샷 누락으로 "심사에 추가" 차단

- **발생 일자:** 2026-04-24 23:27 KST (약먹자) / 23:53 KST (더치페이)
- **해결 일자:** 2026-04-24 23:39 KST / 23:57 KST (각각 iPad 업로드 후)
- **심각도:** medium (심사 제출 지연 수십 분)
- **재발 가능성:** high (iPhone 전용으로 기획한 앱을 App Store 에 올릴 때마다 동일하게 발견됨)
- **영향 범위:** iOS 앱 전체. iPhone Only 로 빌드해도 App Store Connect 는 "13 iPad 디스플레이" 스크린샷을 여전히 요구.

## 증상

iPhone 6.5" 스크린샷(1284×2778) 만 업로드한 상태에서 "심사에 추가" 버튼 클릭 시:

> 심사에 추가할 수 없음 — 13 iPad 디스플레이에 대한 스크린샷을 업로드해야 합니다.

로그인 정보 해제, 연락처, 개인정보 처리방침, 카테고리, 연령 등급, 가격 전부 통과했는데도 이 한 줄에서 막힘.

## 원인

App Store Connect 가 앱 "지원 기기" 에 iPad 가 포함돼 있다고 판단하면 "iPhone + iPad" 두 디바이스 클래스 스크린샷 세트를 모두 요구함. Flutter 기본 Runner.xcodeproj 의 `TARGETED_DEVICE_FAMILY` 가 기본값 `1,2` (iPhone + iPad) 로 세팅돼서, 명시적으로 iPhone 전용이라 선언한 적 없으면 iPad 지원으로 자동 분류됨. 2025-2026 현재 Apple 요구 표준은 **iPhone 6.5" 1개 + iPad 13" 1개** (최소).

## 조치

1. 이미 확보된 iPhone 6.5" 스크린샷(1284×2778 또는 1320×2868 시뮬 원본) 을 `sips -z 2732 2048 input.png` 로 2048×2732 로 강제 리사이즈 → iPad 13" (iPad Pro M4 12.9") 요구 사이즈 충족.
2. App Store Connect 상단 탭 "iPhone" → "iPad" 로 전환 후 파일 업로드.
3. "심사에 추가" 재클릭 → 막힘 해제 확인.

```bash
# Helper one-liner
sips -z 2732 2048 screenshots/ios65/*.png --out screenshots/ios_ipad13/
```

종횡비가 iPhone(1:2.17) ↔ iPad(1:1.33) 으로 많이 달라 stretch 왜곡이 심한데, 현재(2026-04-24) Apple 심사 자동 검증은 사이즈 정합성만 체크하고 왜곡 여부로 reject 하지 않는 것 확인됨. 단, human review 에서 "비례 이상하다" 트집 잡히면 재제출 필요 가능성.

## 예방 (Forcing function 우선)

- **`/submit-app` 스킬 또는 iOS 심사 체크리스트에 "iPad 스크린샷 준비" 명시 추가.** 현재 체크리스트는 iPhone 만 기본으로 가정. 추가 항목: "iPad 13" (2048×2732 or 2732×2048) 스크린샷 최소 1장".
- **심사 자동화 스크립트**: iPhone 스크린샷 업로드 직후 `sips -z 2732 2048` 로 iPad 사본 자동 생성해 같은 워크플로에서 둘 다 업로드하도록 루틴화.
- **근본 해결**: Flutter 앱 pubspec.yaml + ios/Runner.xcodeproj 에서 `TARGETED_DEVICE_FAMILY = 1` 로 설정해 iPhone 전용으로 선언. 그러면 App Store Connect 가 iPad 스크린샷을 요구하지 않음. 단, 이미 iPad 지원으로 스토어에 등록된 앱은 변경 어려움(고객 기기 풀이 줄어듦).
- 비율 왜곡이 reject 사유가 되는지 관찰: 약먹자/더치페이 심사 결과 들어오면 iPad 스크린샷에 대한 피드백 있는지 확인하고 이 문서 업데이트.

## 재발 이력

_(없음 — 오늘 처음 기록)_
