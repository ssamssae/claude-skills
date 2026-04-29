---
name: create-play-app
description: Google Play Console 에 Flutter 앱을 **웹 UI 자동 클릭 + API probe** 조합으로 등록한다. Playwright MCP 로 "앱 만들기" 폼 입력까지 자동화하고, 성공 후 Android Publisher API 로 `edits.insert` 403→200 전환 검증. 이어지는 테스터 연결·AAB 업로드까지 한 번에 이어지려면 `/submit-app` 과 조합해서 호출.
---

# /create-play-app — Play Console 새 앱 등록 자동화

`/submit-app` 은 기존 앱에 새 빌드를 올리는 루틴. 하지만 **Play Console 에 앱이 아직 없을 때** 는 먼저 "앱 만들기" 를 해야 하는데, 이게 수동 웹 UI 단계라 자주 병목. 이 스킬은 그 장벽을 Playwright MCP 로 넘긴다.

## 호출 패턴

- `/create-play-app <앱명>` — `~/apps/<앱명>/` 에서 메타데이터 읽어서 자동 등록
- `/create-play-app <앱명> --name "<한글 이름>"` — 앱 이름 override
- `/create-play-app <앱명> --package com.ssamssae.<name>` — 패키지 override (기본은 build.gradle.kts 에서 자동 감지)
- `/create-play-app <앱명> --dry-run` — 실제 클릭 없이 입력값만 미리 보여줌

## 전제

- **실행 SoT = Mac mini** (2026-04-29 결정). 본진에서 호출하면 SSH 로 Mac mini 의 raw Playwright 스크립트 트리거.
- Mac mini 에 `node` + `playwright` + `chromium` 설치 (Phase A 셋업)
- 저장된 Google 로그인 세션 쿠키: `~/.claude/secrets/google-session.json` (1회 헤드풀 로그인 후 저장)
- Mac mini 의 `~/apps/<name>/android/app/build.gradle.kts` 에 `applicationId` 있음
- Mac mini 의 `~/apps/<name>/store_metadata.md` 에 앱 이름/언어 설정 (옵션)
- Play Console Service Account JSON: `~/.claude/secrets/play-service-account.json` (API probe 용)

## 플로우

### Step 1 — 사전 체크 (Mac mini SSH 라우팅)

이미 등록된 앱인지 확인 — `edits.insert` 가 200 이면 존재, 404 면 신규:

```bash
ssh mac-mini "python3 ~/.claude/automations/scripts/play-upload.py --check <name>"
```

스크립트가 없으면 inline python (Mac mini 에서):

```bash
ssh mac-mini bash -lc "'python3 -c \"
from google.oauth2 import service_account
from googleapiclient.discovery import build
creds = service_account.Credentials.from_service_account_file(\\\"/Users/USER/.claude/secrets/play-service-account.json\\\", scopes=[\\\"https://www.googleapis.com/auth/androidpublisher\\\"])
svc = build(\\\"androidpublisher\\\", \\\"v3\\\", credentials=creds, cache_discovery=False)
try:
    edit = svc.edits().insert(packageName=\\\"<pkg>\\\", body={}).execute()
    print(\\\"ALREADY REGISTERED\\\")
    svc.edits().delete(packageName=\\\"<pkg>\\\", editId=edit[\\\"id\\\"]).execute()
except Exception as e:
    if \\\"404\\\" in str(e):
        print(\\\"NEEDS REGISTRATION\\\")
\"'"
```

(실제로는 별도 `.py` 파일에 저장하고 호출하는 게 깔끔.)

이미 등록됐으면 `/submit-app <name>` 으로 바로 가라고 안내하고 종료.

### Step 2 — 메타데이터 수집

- **앱 이름** (Korean preferred): `store_metadata.md` 의 `## 공통` 블록 `- 이름:` 줄 → 없으면 `--name` 인자 → 없으면 에러
- **패키지**: `android/app/build.gradle.kts` 의 `applicationId` (grep) → 없으면 `--package` 인자 → 없으면 에러
- **언어**: 기본 `한국어 - ko-KR` (override: `--lang en-US` 등)
- **앱/게임**: 기본 `앱` (override: `--game`)
- **무료/유료**: 기본 `무료` (override 불가 — 유료 앱은 Play Console 정책상 출시 후 변경 불가라 수동 진행 권장)

### Step 3 — Mac mini Raw Playwright 호출

본진에서 Playwright MCP 직접 클릭하지 않고 Mac mini 의 headless playwright 스크립트 호출:

```bash
ssh mac-mini "node ~/.claude/automations/scripts/create-play-app.js \
  --name '<한글이름>' \
  --package <com.daejongkang.XXX> \
  --lang ko-KR \
  --type app \
  --pricing free \
  --session ~/.claude/secrets/google-session.json"
```

스크립트(`create-play-app.js`)는 다음 시퀀스를 자동 실행:
1. `chromium.launch({ headless: true })`
2. 저장된 Google 세션 쿠키 로드 → `play.google.com/console` 접근
3. `/console/u/0/developers/6982984193099657371/create-new-app` 이동
4. 폼 입력: 앱 이름, 패키지, 앱/게임=앱, 무료/유료=무료, 정책 체크 2개
5. 기본 언어 dropdown click → ko-KR option click (1-step fill 안 먹음, 2026-04-23 검증)
6. `page.screenshot()` 으로 검증용 스샷 저장 (`/tmp/create-play-app-<timestamp>.png`)
7. "앱 만들기" submit click
8. URL 이 `/app/<id>/app-dashboard` 로 리다이렉트되면 성공
9. JSON 출력: `{"new_app_id": "...", "package_name": "...", "dashboard_url": "..."}`

세션 쿠키가 만료되면 (보통 수개월) 재로그인 필요:
- 강대종님 본진에서 헤드풀로 1회 로그인 → 쿠키 export → Mac mini `~/.claude/secrets/google-session.json` 으로 scp.

### Step 4 — 성공 검증 (Mac mini)

```bash
ssh mac-mini "python3 ~/.claude/automations/scripts/play-upload.py --check <name>"
```

- 위 ssh 결과의 `new_app_id`, `package_name`, `dashboard_url` 파싱
- API probe 재실행 → 200 이면 success
- 검증 스크린샷은 `scp mac-mini:/tmp/create-play-app-*.png .` 으로 본진으로 가져와서 텔레그램 첨부

### Step 4.5 — Keystore SoT 기록

등록 직후 `~/.claude/skills/submit-app/keystore-sot.md` 의 "## Registry" 섹션에 현재 기기 기준으로 한 줄 append:

```
<앱명>: 🍎 Mac (keystore: android/<name>-upload-keystore.jks, created: YYYY-MM-DD)
```
(hostname 이 `*MacBook*`/`*MBP*` 면 🍎 Mac, `DESKTOP-*` 면 🪟 WSL)

이어서 커밋:
```bash
cd ~/.claude/skills && git add submit-app/keystore-sot.md && git commit -m "keystore-sot: <앱명> 등록 (<🍎 Mac|🪟 WSL>)" && git push
```

Registry 에 이미 해당 앱이 있으면 skip (중복 등록 방지). SoT 가 다른 기기로 기재돼 있으면 경고 + "이 앱은 이미 OO 에 keystore 가 있습니다" 로 step 1 실패로 처리.

### Step 5 — 이어서 할 일 제시

```
✅ 포모도로 등록 완료 (app_id=4975840183826223287)

다음 단계:
  1. 테스터 그룹 연결: .../tracks/internal-testing?tab=testers 에서 Google Group 또는 이메일 리스트 추가
  2. `/submit-app <앱명> --platform=android` 로 AAB 업로드
  3. App content 설문 (선택, internal testing 만이면 건너뛰어도 됨)
```

사용자 명시 승인 있으면 (2)(3) 자동 진행; 기본값은 멈춰서 사용자 확인.

## 텔레그램 보고

- 시작: "🚀 /create-play-app 시작 — <앱명>"
- Step 3 완료: "📝 폼 입력 완료, 제출 직전 — 스크린샷 첨부 확인 요청"
- 제출 전 사용자 OK 신호 대기 (auto mode 여도 이 단계는 hold — 비가역)
- 성공: "✅ 등록 완료 — app_id=<id>, dashboard=<url>"

## 안전 원칙

- 앱 생성은 **비가역** (삭제해도 패키지 이름 재사용 불가, 삭제 전 deactivate 필요) → 제출 전 사용자 확인 필수
- **유료 앱 자동 생성 금지** — 정책상 이후 무료로 변경 불가, 수동만
- 가능하면 Playwright 스크린샷 전송해서 최종 확인 단계 제공
- 로그인 실패 / 2FA 화면 뜨면 즉시 중단, 사용자에게 수동 로그인 요청

## Lessons 반영

- `apple-3-1-1-external-payment.md` 는 Apple 전용 — Play 등록 흐름에는 미적용
- `android-aab-naming.md` 는 업로드 단계 (등록 후)
- `android-beta-group-attach.md`, `android-beta-track-needs-testers.md` 는 테스터 연결 단계 (등록 후) → 이 스킬 Step 5 안내에 포함

## 실전 검증

**2026-04-23 (첫 검증)** — 포모도로 (com.ssamssae.pomodoro) 등록 성공
- 입력: 포모도로, com.ssamssae.pomodoro, ko-KR, 앱, 무료
- 소요: 약 1분 (폼 입력 + 제출 + 대시보드 로드)
- 결과: app_id=4975840183826223287, API probe 404→200 전환 확인
- 교훈: 기본 언어 combobox 는 한 번에 `fill_form` 안 먹고 click → option click 2-step 필요

## 관련 스킬

- `/submit-app` — 등록 이후 AAB 업로드·심사 제출
- `/land` — iOS 실기 배포
- 맥미니 mail-watcher v5 — 제출 후 4시간 폴링 Gmail 심사 알림 (스킬 아닌 백그라운드 자동화)

## Lessons 생성 가이드

이 스킬 실행 중 새 장애물 발견하면 `~/.claude/skills/submit-app/lessons/play-console-create-<slug>.md` 에 저장. 포맷은 submit-app 의 lessons 와 동일 (frontmatter: platform/severity/category/first_hit/hits/source).
