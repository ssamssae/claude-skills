---
platform: android
severity: blocking
category: privacy
first_hit: 2026-04-26
hits: 1
source: auto-from-session
---

# 광고 ID 선언이 별도 블로커 — 광고 선언과 다른 항목

## 증상
앱 콘텐츠 → 주의 필요 탭에 "광고 ID" 선언이 미완료로 표시. 본문: "이 섹션을 작성하지 않으면 Android 13을 타겟팅하는 버전을 제출할 수 없습니다." 검토를 위해 앱 전송 버튼이 비활성 상태. 광고 선언(앱에 광고 포함 여부)을 이미 "아니요" 로 답변했음에도 별개로 막힘.

## 원인
Play Console 의 두 가지 광고 관련 선언이 이름은 비슷하지만 별개 폼:
- **광고 선언 (Ads in app)**: 앱이 광고를 보여주는지 — 사용자 경험 관점
- **광고 ID (Advertising ID, AAID)**: 앱이 com.google.android.gms.permission.AD_ID 권한을 사용하는 SDK 를 포함하는지 — 시스템 권한 관점

광고 SDK 가 없는 앱이라도 후자에는 명시적 "아니요" 선언이 강제됨 (Android 13 정책). 작년·재작년 워크시트는 첫 번째만 다루고 두 번째를 빠뜨리는 경우가 흔함.

## 해결
앱 콘텐츠 → 광고 ID → "앱에서 광고 ID를 사용하나요?" → **아니요** → 저장.
포모도로처럼 pubspec 에 google_mobile_ads / firebase_analytics / sentry / amplitude 등이 전혀 없으면 즉시 "아니요". 있으면 SDK 매니페스트 자동 병합 가능성 점검 필요.

## 재발 방지 체크리스트
- [ ] /submit-app §0.5 체크리스트에 "광고 ID 선언(별건) 처리됐는지" 항목 추가
- [ ] 포모도로 워크시트 같은 사전 작성 워크시트에서 "광고 선언" 섹션 옆에 "광고 ID 선언(별건)" 도 함께 적기
- [ ] 신규 앱 첫 제출 시 앱 콘텐츠 페이지의 "주의 필요" 탭을 반드시 확인 — 워크시트가 모르는 신규 정책 항목이 거기 잡힘
