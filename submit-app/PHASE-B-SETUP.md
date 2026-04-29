# Phase B — 자동배포 1회 셋업 가이드 (강대종님 본진 작업)

마지막 갱신: 2026-04-30

이 단계는 **본진(MacBook Pro) 브라우저** 에서 강대종님이 직접 클릭으로 진행. 끝나면 Mac mini 가 자동배포 가능.

소요 시간: 약 15~25분 (3개 자료 발급 + scp 4번).

---

## 0. 사전 체크

- Mac mini SSH 도달 확인:
  ```bash
  ssh -o ConnectTimeout=5 mac-mini 'echo OK'
  ```
- secrets 디렉토리 존재 확인:
  ```bash
  ssh mac-mini 'ls -ld ~/.claude/secrets/'
  ```
  없으면: `ssh mac-mini 'mkdir -p ~/.claude/secrets && chmod 700 ~/.claude/secrets'`

---

## 1. iOS — App Store Connect API key 발급

### 1.1 발급

1. 본진 브라우저로 이동: <https://appstoreconnect.apple.com/access/users>
2. 상단 탭: **Integrations** (또는 한국어: 통합) → **App Store Connect API** → **Team Keys** 탭
3. **Generate API Key** (또는 한국어 "API 키 생성") 버튼 클릭
4. 폼 입력:
   - Name: `mac-mini-fastlane`
   - Access: **Admin** (App Manager 도 가능하지만 fastlane 호환성은 Admin 가장 안전)
5. 발급 후 다음 정보를 메모장에 복사:
   - **Issuer ID** (페이지 상단, UUID 형식 — 모든 키 공통)
   - **Key ID** (10자 영문/숫자, 예: `ABC1234XYZ`)
   - **Private Key (.p8 파일)** — 한 번만 다운로드 가능. 다운로드 → Finder 의 `~/Downloads/AuthKey_<KeyID>.p8` 위치 확인.

### 1.2 Mac mini 로 전송

본진 터미널:
```bash
KEY_ID=ABC1234XYZ          # 위에서 메모한 값
ISSUER_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx   # 위에서 메모한 값

# .p8 파일 전송
scp ~/Downloads/AuthKey_${KEY_ID}.p8 mac-mini:/Users/USER/.claude/secrets/

# fastlane 이 읽을 수 있도록 권한 조정
ssh mac-mini "chmod 600 ~/.claude/secrets/AuthKey_${KEY_ID}.p8"

# fastlane 호환 JSON 형식 metadata 도 같이 보관 (편의용)
ssh mac-mini "cat > ~/.claude/secrets/asc-api-key.json <<EOF
{
  \"key_id\": \"${KEY_ID}\",
  \"issuer_id\": \"${ISSUER_ID}\",
  \"key\": \"\$(cat ~/.claude/secrets/AuthKey_${KEY_ID}.p8 | sed 's/\$/\\\\n/' | tr -d '\\n')\",
  \"in_house\": false
}
EOF"
```

### 1.3 검증

```bash
ssh mac-mini "ls -l ~/.claude/secrets/AuthKey_*.p8 ~/.claude/secrets/asc-api-key.json"
ssh mac-mini "fastlane pilot list --api_key_path ~/.claude/secrets/asc-api-key.json --app_identifier com.daejongkang.hanjul" 2>&1 | tail -10
```

마지막 명령이 한줄일기 빌드 목록을 출력하면 성공. (TestFlight 빌드 없으면 빈 목록 OK — 인증 통과 확인.)

---

## 2. Android — Google Play Service Account JSON 발급

### 2.1 발급

1. 본진 브라우저로 이동: <https://play.google.com/console>
2. 좌측 메뉴: **설정 → API 액세스** (또는 영어 Settings → API access)
3. 처음이면: "**새 서비스 계정 만들기**" 클릭 → Google Cloud Console 새 탭으로 이동
4. Google Cloud Console 에서:
   - 프로젝트 선택 (없으면 새로 생성, 이름 예: `daejong-play-deploy`)
   - **서비스 계정 만들기** 클릭
   - 이름: `mac-mini-supply`
   - 역할: 선택 안 함 (Play Console 에서 부여)
   - **만들기 + 계속 + 완료**
5. 만든 서비스 계정 클릭 → **키** 탭 → **키 추가 → 새 키 만들기 → JSON** → 다운로드
6. Google Cloud Console 에서 JSON 받은 파일은 `~/Downloads/<프로젝트명>-<해시>.json` 형식
7. **Play Console 로 돌아와서**:
   - API 액세스 페이지 새로고침
   - 새로 만든 서비스 계정이 목록에 보임 → **권한 부여**
   - 앱별 권한: 한줄일기/메모요/포모도로 등 자동배포 대상 앱 모두 체크
   - 권한:
     - **앱 정보 보기**: ✅
     - **버전 관리**: ✅ (production/internal/beta 트랙 모두)
     - **앱 액세스 관리**: 필요 X (상세 권한 그대로)
   - **변경사항 적용**

### 2.2 Mac mini 로 전송

본진 터미널:
```bash
# 다운받은 JSON 파일 경로 확인
ls ~/Downloads/*.json

# 전송 (파일명을 표준 이름으로 변경)
scp ~/Downloads/<발급-받은-파일>.json mac-mini:/Users/USER/.claude/secrets/play-service-account.json

# 권한
ssh mac-mini "chmod 600 ~/.claude/secrets/play-service-account.json"
```

### 2.3 검증

```bash
ssh mac-mini "python3 -c \"
from google.oauth2 import service_account
from googleapiclient.discovery import build
creds = service_account.Credentials.from_service_account_file(
    '/Users/USER/.claude/secrets/play-service-account.json',
    scopes=['https://www.googleapis.com/auth/androidpublisher'],
)
svc = build('androidpublisher', 'v3', credentials=creds, cache_discovery=False)
edit = svc.edits().insert(packageName='com.daejongkang.hanjul', body={}).execute()
print('OK editId=', edit['id'])
svc.edits().delete(packageName='com.daejongkang.hanjul', editId=edit['id']).execute()
\""
```

`OK editId= ...` 출력되면 성공. **403 Forbidden** 이 나오면 Play Console 의 서비스 계정 권한 부여가 아직 안 된 상태 — 위 2.1 마지막 단계 다시 확인.

Mac mini 에 google-api 패키지 없으면:
```bash
ssh mac-mini "pip3 install --user google-api-python-client google-auth"
```

---

## 3. (옵션) Android 자동 신규 앱 등록용 Google 세션 쿠키

> **이 단계는 `/create-play-app` 자동화를 원할 때만 필요.** 신규 앱 등록 자동화가 필요 없으면 (예: 강대종님이 새 앱 등록은 본진에서 직접 하시면) **스킵 가능**.

### 3.1 본진에서 헤드풀 Playwright 1회 로그인

```bash
# 본진에 playwright 없으면 한 번만:
npm install -g playwright
npx playwright install chromium

# 로그인 + 쿠키 저장 스크립트 (본진에서 1회 실행)
cat > /tmp/save-google-session.js <<'EOF'
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: false });
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await page.goto('https://play.google.com/console');
  console.log('🔓 브라우저에서 Google 계정으로 로그인 + 2FA 까지 완료한 뒤');
  console.log('   터미널에서 Enter 누르세요...');
  process.stdin.once('data', async () => {
    await ctx.storageState({ path: '/tmp/google-session.json' });
    console.log('✅ /tmp/google-session.json 저장됨');
    await browser.close();
    process.exit(0);
  });
})();
EOF

node /tmp/save-google-session.js
```

브라우저 열리면 → Google 로그인 + 2FA → Play Console 정상 진입 확인 → 본진 터미널로 돌아와 **Enter 한 번** → 쿠키 자동 저장.

### 3.2 Mac mini 로 전송

```bash
scp /tmp/google-session.json mac-mini:/Users/USER/.claude/secrets/google-session.json
ssh mac-mini "chmod 600 ~/.claude/secrets/google-session.json"
rm /tmp/google-session.json   # 본진엔 둘 필요 X
```

### 3.3 검증

```bash
ssh mac-mini "node -e \"
const { chromium } = require('/Users/USER/.claude/automations/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ storageState: '/Users/USER/.claude/secrets/google-session.json' });
  const page = await ctx.newPage();
  await page.goto('https://play.google.com/console');
  await page.waitForTimeout(3000);
  console.log('TITLE:', await page.title());
  await browser.close();
})();
\""
```

`TITLE: Google Play Console` 비슷하게 나오면 성공. `로그인` 류 타이틀이면 쿠키 만료 — 3.1 다시 진행.

**참고:** Google 세션 쿠키는 보통 수개월~1년 유효. 만료되면 위 3.1 다시 1회.

---

## 4. 최종 점검 — secrets 디렉토리

```bash
ssh mac-mini "ls -la ~/.claude/secrets/"
```

기대 결과 (3개 핵심 파일):
```
-rw------- AuthKey_XXXXXXXXXX.p8       (iOS API key)
-rw------- asc-api-key.json            (iOS metadata, 편의용)
-rw------- play-service-account.json   (Android API)
-rw------- google-session.json         (옵션, 신규 앱 등록 자동화 시)
```

**모든 파일 권한 = `-rw-------` (600)** 인지 확인. 다르면:
```bash
ssh mac-mini "chmod 600 ~/.claude/secrets/*"
```

---

## 5. 완료 후 다음 액션

본진 Claude Code 세션에 다음 메시지:

> "Phase B 셋업 끝났음. 검증 명령 결과 OK."

→ Claude 가 raw Playwright 스크립트(`create-play-app.js`) + `play-upload.py` 작성 + 다음 release 사이클부터 자동배포 적용 진행.

---

## 6. 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| iOS `pilot` 인증 실패 | `.p8` 권한 644 | `chmod 600` |
| iOS `Invalid issuer` | issuer_id 오타 | App Store Connect Integrations 페이지 재확인 |
| Android `403 Forbidden` | 권한 부여 안 됨 | Play Console API access > 서비스 계정 > 앱 권한 추가 |
| Android `Package not found` | applicationId 매칭 X | `com.daejongkang.<app>` 정확히 입력 |
| Playwright `로그인` 타이틀 | 세션 만료 | 본진에서 3.1 다시 실행 |

## 7. 자산 분실 시

- `.p8` 파일 분실 → App Store Connect 에서 폐기 + 재발급 (Mac mini 에 새 파일 scp)
- Service Account JSON 분실 → Google Cloud 에서 키 폐기 + 새 키 생성 (Play Console 권한 부여 다시)
- Google 세션 쿠키 분실 → 단순 재로그인 (3.1)

**모든 자산은 Mac mini SoT.** 본진에 절대 복사 X (자산 분산 = 노출 리스크 2배).
