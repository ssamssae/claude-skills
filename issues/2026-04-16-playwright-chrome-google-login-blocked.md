---
prevention_deferred: null
---

# Playwright Chromium 으로 Google 로그인 시 "안전하지 않은 브라우저" 차단

- **발생 일자:** 2026-04-16
- **해결 일자:** 2026-04-16
- **심각도:** medium (자동화 블로킹)
- **재발 가능성:** medium (Google 보안 정책 변경 시 재현 가능)
- **영향 범위:** 메모요 사전예약 자동 등록용 Playwright 워크플로우

## 증상
Playwright 기본 Chromium(for Testing) 으로 Google 계정 로그인 페이지에 진입하면 "이 브라우저는 안전하지 않을 수 있습니다" 경고가 뜨면서 로그인 폼 자체가 비활성화됨. Google Groups 멤버 추가 자동화가 로그인 단계에서 멈춤.

## 원인
Google 로그인 시스템이 **WebDriver/자동화 시그니처를 감지**해서 차단. `navigator.webdriver` 플래그, Chromium for Testing 특유의 User-Agent, 일부 헤더가 주요 힌트로 사용됨. Playwright 기본 설정은 이 시그니처를 숨기지 않음.

## 조치
- Chromium for Testing 대신 **시스템에 설치된 실제 Chrome 채널** 사용 (`channel: 'chrome'`)
- `disable-blink-features=AutomationControlled` 플래그 추가
- `navigator.webdriver = undefined` 오버라이드 스크립트를 각 페이지 진입 시 `addInitScript` 로 주입
- User-Agent 를 실제 Chrome 과 동일하게 유지
- 위 3가지를 모두 적용하니 Google 로그인 폼이 정상 활성화됨

## 예방 (Forcing function 우선)
- Google/네이버 등 bot detection 이 강한 사이트 자동화는 **처음부터 stealth 기본 설정** 으로 시작. Playwright 래퍼에 `stealth=true` 옵션 같은 공용 함수 두고 신규 자동화 스크립트가 이걸 디폴트로 쓰도록.
- 메모요 자동 등록 스크립트 상단에 "Google 로그인 경로는 반드시 system Chrome + stealth" 주석.
- 다른 자동화가 재발 시 이 이슈 파일로 바로 연결되도록 INDEX.md 에 태깅.

## 재발 이력
_(없음)_

## 관련 링크
- 메모리: project_memoyo_beta_auto_add.md
- 작업일지: docs/worklog/2026-04-16
