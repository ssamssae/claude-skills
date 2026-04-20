---
platform: ios
severity: blocking
category: payment
first_hit: 2026-01-15
hits: 1
source: reviewer-feedback
---

# Apple App Store Guideline 3.1.1 — 외부 결제/기부 링크 금지

## 증상
Apple 리뷰팀이 앱 내 "후원/응원하기" 버튼이 외부 웹(카카오페이 송금 링크)으로 이동하는 것을 3.1.1 위반으로 지적. 메모요 1.0 리젝됨.

## 원인
iOS 앱은 디지털 구매·구독뿐 아니라 기부·팁·후원성 결제까지 전부 In-App Purchase(IAP) 로만 처리해야 한다. 외부 웹 결제·송금 링크는 가이드라인 위반.

## 해결
- 해당 기능을 iOS 빌드에서만 비활성화 (플랫폼 분기)
- 또는 IAP Consumable 로 전환 (수수료 30% 수용)
- 또는 완전히 기능 제거
- daejong-page(외부 포트폴리오) 의 응원 링크는 **앱 번들 내에서만** 금지 — 웹브라우저에서는 OK

## 재발 방지 체크리스트
- [ ] 앱 내 "응원/후원/기부/팁" 문구와 버튼 없는지 검토
- [ ] WebView 나 url_launcher 로 카카오페이/토스페이 송금 링크 호출 여부 확인
- [ ] 디지털 콘텐츠·기능 해금은 IAP 로만 처리
- [ ] "프리미엄 기능 업그레이드" 링크를 외부 결제 페이지로 보내지 않음
- [ ] 리뷰어가 테스트 가능하도록 IAP 상품 Sandbox 등록 완료

## 참고
- https://developer.apple.com/app-store/review/guidelines/#payments
- 메모요 케이스: daejong-page/worklog/2026-01-15.md 참조
