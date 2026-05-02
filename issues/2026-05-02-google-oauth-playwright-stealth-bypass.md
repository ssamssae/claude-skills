---
prevention_deferred: null
---

# Playwright 로 띄운 Chrome 에서 Google OAuth 로그인 차단 — stealth args 3종 우회 성공

- **발생 일자:** 2026-05-02 12:53 KST (1차 차단 화면)
- **해결 일자:** 2026-05-02 13:00 KST (3차 stealth args 우회 통과)
- **심각도:** medium (`/create-play-app` 자동화 + Play Console 신규 등록 자동화 전체가 차단되는 함정)
- **재발 가능성:** high (Google 자동화 차단 정책 상시 강화 추세, 규칙 변경 시 또 깨질 수 있음)
- **영향 범위:** `/create-play-app` 스킬, PHASE-B-SETUP.md §3 (Google 세션 쿠키 export), 향후 Play Console / ASC / Google Cloud Console / Gmail OAuth Playwright 자동화 전부

## 증상

본진 Mac 에서 Playwright headful Chromium 으로 `https://play.google.com/console` 접속 → Google 계정 로그인 시도하면 즉시 차단 화면:

> 🚫 **로그인할 수 없음**
> 브라우저 또는 앱이 안전하지 않을 수 있습니다. 자세히 알아보기
> 다른 브라우저를 사용해 보세요. 이미 지원되는 브라우저를 사용 중이라면 로그인을 다시 시도해 보시기 바랍니다.

URL: `accounts.google.com/v3/signin/rejected?continue=...`

이메일/비밀번호 입력 단계 도달조차 못 함 = OAuth flow 진입 자체 차단.

## 원인

Google 이 브라우저의 자동화 시그니처 감지:

1. **`--enable-automation` 플래그**: Playwright 가 Chrome/Chromium launch 시 디폴트로 켜는 플래그. Google 의 client-side detector 가 즉시 발견.
2. **`navigator.webdriver === true`**: Blink 엔진의 자동화 표시. JS 한 줄로 Google 이 감지 가능.
3. **Chrome for Testing 식별**: `playwright install chromium` 으로 받는 chromium 빌드는 메뉴바에 "Chrome for Testing" 표시. Google 이 user-agent 또는 binary 시그니처로 식별.
4. **추가 시그니처**: process iframe 격리 패턴 등.

`channel: 'chrome'` 으로 실제 Chrome 사용해도 위 1~2 (`--enable-automation` + `navigator.webdriver`) 가 그대로 남아 차단 통과 X. **2차 시도에서 실증 — 메뉴바는 "Chrome" 으로 나왔지만 같은 차단 화면**.

## 조치

3차 시도에서 stealth args 3종 적용 후 통과:

```js
const browser = await chromium.launch({
  headless: false,
  channel: 'chrome',                                    // 실제 Chrome (chromium 아님)
  args: [
    '--disable-blink-features=AutomationControlled',    // navigator.webdriver=false 강제
    '--disable-features=IsolateOrigins,site-per-process', // 일부 격리 시그니처 제거
  ],
  ignoreDefaultArgs: ['--enable-automation'],           // Playwright 디폴트 자동화 플래그 제거
});
```

핵심은 3개가 **동시에** 적용돼야 함. 어느 하나 빠지면 차단:
- `channel: 'chrome'` 만 (2차 시도) → 차단
- `channel: 'chrome'` + 일부 args 만 → 미검증, 차단 가능성
- 3종 동시 → 통과

추가 검증 — 강대종 본진 Mac 에서 실제 로그인 + 2FA 정상 진행, "로그인 성공" 텔레그램 보고 (msg 10935 "로그인성공! 와 이 노하우 기록해놓자 대박이다").

## 예방 (Forcing function 우선)

1. **`/tmp/save-google-session.js` 표준 템플릿화** — `~/.claude/skills/create-play-app/templates/save-google-session.js` 또는 `~/.claude/automations/scripts/save-google-session.js` 로 박고 stealth args 3종 디폴트 포함. 매번 작성 X, 1회 호출.

2. **PHASE-B-SETUP.md §3.1 정정** — 현재 가이드는 `chromium.launch({ headless: false })` 만. stealth args 3종 + `channel: 'chrome'` 추가 필수 표기. 3차 시도 비용 회피 (사고 시점에 30분 소비).

3. **`/create-play-app` SKILL.md / `create-play-app.js` 점검** — Mac mini raw Playwright 스크립트도 같은 함정 가능성. 같은 stealth args 디폴트 적용 + headful/headless 모두 검증.

4. **Google OAuth Playwright 패턴 = stealth 필수 룰 메모리** — `feedback_google_oauth_playwright_stealth.md` 박아서 향후 Gmail / Google Cloud Console / ASC (Apple OAuth 는 무관) 자동화 시도 시 0차 reflex 로 stealth args 적용.

5. **Google 정책 강화 모니터링** — stealth args 우회는 Google 의 detection 강화에 따라 깨질 수 있음. 다음 차단 발생 시 추가 우회 (puppeteer-extra-plugin-stealth 류) 검토.

## 참고

- 시도 순서:
  - 1차 (chromium-only, no channel): mac-mini SSH 에서 path 실수 + 본진 글로벌 playwright 미설치 = 실행 자체 실패
  - 2차 (NODE_PATH 우회 + chromium-only): Chromium 띄워짐, Google 차단 화면
  - 2.5차 (channel: 'chrome'): Chrome 띄워짐, 같은 차단 화면 (자동화 시그니처 감지)
  - 3차 (channel: 'chrome' + stealth args 3종): 통과 ✅
- 총 소요: 약 30분 (12:30 KST 시작 → 13:00 KST 통과)
- 강대종 손: Chrome 창에서 Google 로그인 + 2FA + Play Console 진입 (본인 디바이스로 인증된 세션)
- chromium 바이너리 캐시: `~/Library/Caches/ms-playwright/` (chromium-1217 + chrome 별도)
- playwright 모듈: `~/daejong-page/beta-signup/worker/node_modules/playwright` (NODE_PATH 우회 사용)

## 관련 작업

- 강대종 결정 옵션 A (PHASE-B-SETUP §3) = Google 세션 쿠키 1회 export → mac-mini 영구 자동화 사이클의 일환
- 차단 후 옵션 결정 트리: A-1 (launchPersistentContext, 강대종 본인 Chrome 데이터) / A-2 (stealth args, 0 손) / A-3 (CDP attach) / C (수동 Play Console 등록 폴백)
- A-2 (stealth args) 가 0 손 + 5분 우회 = winner
