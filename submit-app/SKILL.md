---
name: submit-app
description: Flutter 앱 App Store / Play Console 제출 루틴. 과거 실수·리젝 사례(lessons/) 먼저 읽어 재발 방지 체크리스트 후 빌드·업로드·심사 제출. 트리거 "앱 등록", "스토어 제출", "심사 보내", "aab 업로드", "ipa 업로드", "리뷰 제출", "/submit-app", "/submit", "Play Console 올려", "App Store 올려".
allowed-tools: Read, Edit, Write, Bash, Grep, Glob
---

# /submit-app — 앱 스토어 제출 루틴 + 실수 학습

앱 제출은 자주 하는 루틴이지만 플랫폼 정책(Apple 3.1.1, aab 파일명 등) 때문에 매번 같은 함정에 빠질 수 있다. 이 스킬은 **과거 실수를 먼저 읽고** 사용자에게 확인시킨 뒤 빌드·업로드·심사 제출을 진행한다.

## 기기 라우팅 (지휘관 1명 원칙)

🍎 Mac 본진 = 지휘관(설계·결정·메인 세션, main 머지 결정) / 🏭 Mac mini = 빌드·배포 워커(SSH 라우팅 수신) / 🪟 WSL = 작업자(`wsl/*` 브랜치 push, main 직접 push 금지). 운반체 = `wsl-directive.sh` / `mac-report.sh`.

**이 스킬**: 🍎 Mac 본진에서 호출 → 🏭 Mac mini SSH 라우팅으로 빌드/업로드 (자산 SoT = Mac mini). 🪟 WSL 호출 X (코드 SoT 도 Mac mini).

## 호출 패턴

- `/submit-app <앱명> --platform=ios` — App Store Connect 제출
- `/submit-app <앱명> --platform=android` — Play Console 제출
- `/submit-app <앱명>` — 플랫폼 미지정 시 먼저 물어봄
- `/submit-app <앱명> --dry-run` — 실제 업로드 없이 체크리스트만 돌려보기
- `/submit-app lessons` — 저장된 lessons 목록만 출력

## 전제

- **실행 SoT = Mac mini.** 이 스킬은 본진(MacBook) Claude Code 에서 호출하지만, 빌드·서명·업로드는 전부 `ssh mac-mini "..."` 라우팅으로 Mac mini 에서 수행 (2026-04-29 결정 — `feedback_android_build_deploy_mac_mini.md`).
- Flutter 프로젝트 루트가 **Mac mini** `~/apps/<앱명>/` 에 있음 (Mac mini 가 코드 SoT)
- iOS: Mac mini 에 Xcode + CocoaPods + fvm 세팅, signing team `46UH85U2B8` 주입
- Android: Mac mini 에 keystore 보관 (`~/apps/<app>/android/<app>-upload-keystore.jks`), `android/key.properties` 존재, release 서명 설정 완료
- Mac mini 에 `fastlane` 설치 (Phase A 셋업)
- App Store Connect / Google Play API key 가 Mac mini `~/.claude/secrets/` 에 보관
- 메타·스크린샷·심사 제출까지 자동화 default (2026-05-01 결정 — `feedback_default_to_automation.md`, 포모도로/한컵 iOS 풀자동 제출 PASS). ASC API + fastlane deliver + Playwright 클릭 사용. **단** 가격/territory/유료 전환 같은 위험 카테고리는 강대종님 컨펌 후 진행 (아래 Step 3 안전 원칙 참조)

## 절차

### Step 0 — Mac mini 라우팅 + Keystore 가드

**전 플랫폼(iOS/Android) 공통**. 빌드/서명/업로드는 전부 Mac mini 라우팅이므로 진입 시점에 Mac mini 도달 가능 + 산출물 위치 확인.

1. **Mac mini 도달 확인**:
   ```bash
   ssh -o ConnectTimeout=5 mac-mini 'echo OK' 2>&1
   ```
   실패 시 즉시 중단:
   ```
   🚨 Mac mini 도달 불가 (SSH timeout)
   배포는 Mac mini SoT 라 본진 단독 진행 불가. Tailscale/SSH 상태 확인 후 재시도.
   ```

2. **앱 디렉토리 확인** (Mac mini 위):
   ```bash
   ssh mac-mini "ls -d ~/apps/<앱명>/" 2>&1
   ```
   없으면 중단 — 코드 SoT 도 Mac mini 인 게 원칙. 본진에만 있으면 강대종님이 먼저 동기화 (또는 git push/pull) 필요.

3. **Android 만 — keystore 존재 확인 + SHA 추출**:
   ```bash
   ssh mac-mini "ls ~/apps/<앱명>/android/*-upload-keystore.jks && keytool -list -v -keystore ~/apps/<앱명>/android/<앱명>-upload-keystore.jks -alias upload 2>/dev/null | grep -i SHA256:"
   ```
   keystore 없으면 중단 + registry 확인 안내.

4. **registry 에 앱이 없으면** → 경고:
   ```
   ⚠️ <앱명> 이 keystore SoT registry 에 없습니다.
   keystore-sot.md "## Registry" 섹션에 먼저 한 줄 추가:
     <앱명>: 🏭 Mac mini (keystore: android/<file>.jks, created: YYYY-MM-DD)
   ```

5. 통과하면 Step 0.4 (Play 패키지 등록 사전 점검) 로.

**참고:** keystore-sot.md 의 `🍎 Mac` 표기는 2026-04-29 이전 표기. 현재 모든 release keystore 의 실제 SoT 는 Mac mini(`/Users/USER/apps/<app>/android/`). registry 의 emoji 는 점진적 마이그레이션 — 표기와 무관하게 라우팅은 Mac mini 로.

### Step 0.4 — Play 패키지 등록 사전 점검 (Android 만 해당)

**필수**. 출시일 직전 사고(2026-04-28 한줄일기 19:00 1900원 유료 출시, lesson `android-play-package-already-registered`) 재발 차단.

빌드·업로드 시작 전에 Play 가 com.X.Y 패키지를 이미 다른 keystore 로 영구 바인딩했는지 확인:

1. **SoT keystore SHA-256 추출**:
   ```bash
   keytool -list -v -keystore <keystore-sot.md 의 SoT 경로> -alias upload 2>/dev/null | grep -i "SHA256:"
   ```
   alias 가 'upload' 가 아니면 -alias 인자 빼고 전체 list. 출력은 `SHA256: F4:A7:...` 형식.

2. **Play Console 비교 (사용자 손)**:
   - URL: Play Console > 설정 > 개발자 계정 > Android 패키지 이름 > 신규 등록
   - 패키지 이름 입력 → 페이지 로드 후 "이미 등록됨" 메시지 + 후보 SHA-256 표시 여부 확인
   - 사용자에게 두 SHA 비교 요청, 결과 텔레그램 보고

3. **분기**:
   - **Play 에 미등록** → 정상 신규 등록 흐름 (Step 0.5 진행)
   - **등록됨 + SHA 매칭** → Play 가 우리 keystore 인정. 정상 (Step 0.5 진행)
   - **등록됨 + SHA 미스매치** → 즉시 중단:
     ```
     🚨 Play 패키지 이름 충돌
     com.X.Y 가 이미 Play 에 등록돼있고 보유 SoT keystore SHA-256 과 매칭되지 않습니다.
     Play 등록 키: <05:CF…>
     SoT 키: <F4:A7…>
     출시 차단됨. 옵션:
       (A) 비공개 키 복원 — 강대종님 과거 keystore 자산 검색 (분실 시 거의 불가능)
       (B) 패키지 이름 변경 — **신규 패키지 이름은 com.daejongkang.* 도메인 우선** (`feedback_new_package_use_daejongkang_domain.md`, ssamssae 같은 일반 닉네임은 점유 충돌 위험). AndroidManifest + build.gradle.kts + applicationId + MainActivity 디렉토리/package + iOS Bundle ID(pbxproj 6군데) + Apple Dev Portal 신규 등록 일괄
       (C) 출시 보류
     ```
     사용자 결정 전까지 Step 0.5 / 빌드 진행 금지. **2026-04-28 한줄일기 사고 = 옵션 B 채택 사례** (com.ssamssae.hanjul → com.daejongkang.hanjul, 1시간 소요).

4. **출시 14일 전 권고**: 이 점검은 **출시 사이클 시작 시점**(빌드 직전 X)에 1회 미리 수행. 충돌 시 14일 여유 확보 가능.

### Step 0.5 — Lessons 로드 & 체크리스트 생성

**필수**. 이걸 먼저 안 하면 과거 실수 학습 효과가 0.

```
~/.claude/skills/submit-app/lessons/*.md
```

- frontmatter 파싱 (platform, severity, category)
- `--platform` 과 일치하거나 `both` 인 것만 필터
- `severity: blocking` → **반드시 통과 확인**
- `severity: warning` → 통과 권장 (사용자 판단)
- `severity: info` → 참고용

체크리스트 출력 예:

```
📋 Submit-App 체크리스트 — <앱명> (<platform>)

🔴 BLOCKING (반드시 통과, 3건)
 [ ] 외부 결제 링크 없음? (Apple 3.1.1, 메모요 1.0 리젝 전례)
 [ ] Bundle ID 가 com.ssamssae.<name> 형식?
 [ ] 스크린샷 3장 이상 준비됨?

🟡 WARNING (권장, 2건)
 [ ] aab 파일명 영문·하이픈 (예: memoyo-1.0.2-19.aab)
 [ ] What's New 텍스트 작성됨?

🟢 INFO (참고, 1건)
 ℹ Pretendard 폰트 번들되어 있으면 용량 +3MB 예상
```

사용자가 체크리스트 통과 확인 (또는 명시적 "다 됐어" / "ㄱㄱ") 할 때까지 빌드 진행 금지. BLOCKING 항목 거부 시 중단.

### Step 1 — 버전 bump

- Mac mini 의 `~/apps/<앱명>/pubspec.yaml` 의 `version: X.Y.Z+N` 에서 N(build number) +1
- X.Y.Z 는 사용자에게 물어봄 (patch/minor/major 중 선택)
- bump 명령:
  ```bash
  ssh mac-mini "cd ~/apps/<앱명> && sed -i '' 's/^version: .*/version: X.Y.Z+N/' pubspec.yaml && git add pubspec.yaml && git commit -m 'chore: bump version to X.Y.Z+N'"
  ```

### Step 2 — 빌드 (Mac mini SSH 라우팅)

**iOS**:
```bash
ssh mac-mini "cd ~/apps/<앱명> && fvm flutter build ipa --release 2>&1 | tail -30"
```
산출물 (Mac mini 위): `~/apps/<앱명>/build/ios/ipa/*.ipa`

**Android**:
```bash
ssh mac-mini "cd ~/apps/<앱명> && fvm flutter build appbundle --release 2>&1 | tail -30"
```
산출물 (Mac mini 위): `~/apps/<앱명>/build/app/outputs/bundle/release/app-release.aab`

빌드 후 파일명 규칙 확인 (aab: 영문·하이픈). 어긋나면 Mac mini 에서:
```bash
ssh mac-mini "cd ~/apps/<앱명> && cp build/app/outputs/bundle/release/app-release.aab build/<app>-X.Y.Z-N.aab"
```

검증:
```bash
ssh mac-mini "ls -lh ~/apps/<앱명>/build/ios/ipa/*.ipa  ~/apps/<앱명>/build/app/outputs/bundle/release/*.aab 2>/dev/null"
```

### Step 3 — 업로드 (Mac mini SSH + fastlane)

**iOS** (App Store Connect API + altool):
```bash
ssh mac-mini "cd ~/apps/<앱명> && fastlane pilot upload --ipa build/ios/ipa/<file>.ipa --api_key_path ~/.claude/secrets/asc-api-key.json --skip_waiting_for_build_processing"
```
또는 단순 upload 만 (TestFlight 처리 대기 별도):
```bash
ssh mac-mini "xcrun altool --upload-app -f ~/apps/<앱명>/build/ios/ipa/<file>.ipa -t ios --apiKey <KEY_ID> --apiIssuer <ISSUER_ID>"
```
App Store Connect 프로세싱 대기 (보통 5~20분) — `mail-watcher v5` 가 결과 알림 수신.

**Android** (Google Play Publisher API + fastlane supply):
```bash
ssh mac-mini "cd ~/apps/<앱명> && fastlane supply --aab build/app/outputs/bundle/release/<file>.aab --json_key ~/.claude/secrets/play-service-account.json --track internal --skip_upload_metadata --skip_upload_changelogs --skip_upload_images --skip_upload_screenshots"
```
- `--track internal/alpha/beta/production` — 메모요처럼 Closed Testing 은 `internal` 또는 `beta`
- 메타·스크린샷·what's new = fastlane supply (Android) / fastlane deliver (iOS) 자동화 default (2026-05-01 자동화 룰). 위험 카테고리(가격/territory/유료 전환)만 사용자 컨펌

업로드 후 검증:
```bash
ssh mac-mini "fastlane supply --json_key ~/.claude/secrets/play-service-account.json --package_name com.daejongkang.<앱명> --validate_only=true" 2>&1 | tail -20
```

심사 제출 = `asc-deliver --submit` (iOS) / `fastlane supply --release_status completed` (Android) 자동화 default (2026-05-01). 가격/territory/유료 전환 같은 위험 카테고리만 사용자 컨펌 후 자동 트리거. (포모도로/한컵 5/1 풀자동 제출 PASS — reviewSubmission 77f1d8b5/69b71c26)

### Step 3.5 — ASC 가드 3종 (iOS, dry-run default)

자동 출시(AFTER_APPROVAL) quirk 우회 + reject 답글 자동화. 본 스킬 흐름에서 호출하는 dry-run 가드 3종. 위험 카테고리(territory/availability)이라 `--apply` 명시 + 강대종 컨펌 후에만 실 ASC API 호출. 미지정 시 dry-run, system-level 변경 0.

| 가드 | 트리거 | 스크립트 | 우회 대상 |
|------|--------|----------|-----------|
| W6 territory-verify | 자동 출시 직후 | `~/.claude/automations/scripts/asc-territory-verify.py --app-id <APP_ID>` | 174 territory record 누락 (2026-04-30 약먹자/더치페이 22분 unlist 사례) |

<!-- territory ID 캐시: skills/submit-app/data/asc_territories.json (174개 ISO 3166-1 alpha-3) -->
| W7 asc-resubmit | UNRESOLVED_ISSUES reject 수신 | `~/.claude/automations/scripts/asc-resubmit.py --app-id <APP_ID> --platform IOS` | reviewSubmission cancel→new sub→submit (2026-04-30 한줄일기 11:06 우회→13:29 승인) |
| W8 asc-rc-reply | territory/availability reject 답글 | `~/.claude/automations/scripts/asc-rc-reply.py --review-submission-id <SUB_ID> --message-template territory_fix` | reviewer 답글 자동화 (2026-04-29 강대종 손 친 답글 원본) |

호출 흐름:
1. Step 3 (업로드) 완료 후 mail-watcher v5 가 심사 결과 수신
2. **승인 + AFTER_APPROVAL 자동 출시** → W6 dry-run 1회 → 강대종 컨펌 후 `--apply`
3. **UNRESOLVED_ISSUES reject** → W7 dry-run 1회 → 강대종 컨펌 후 `--apply` → W8 dry-run + 컨펌 후 `--apply`
4. 가드 실패(스크립트 NotImplementedError 또는 API 변경) 시 즉시 강대종 텔레그램 보고 + 수동 fallback

### Step 4 — 심사 제출 후 모니터링 활성화

맥미니 mail-watcher v5 (4시간 폴링) 가 Gmail 모니터링하므로 별도 조치 불필요. 업로드 완료 시 텔레그램으로 "심사 제출 완료 — Gmail 상태 알림 대기" 공지.

### Step 5 — 회고 & Lesson 추가

제출 직후 물어봄:
> "이번 작업에서 새로 배운 게 있나요? (예: 리젝 사유, 스크린샷 요건 변경, Play Console UI 변화 등)"

답변이 있으면:
- `lessons/<YYYY-MM-DD>-<platform>-<slug>.md` 생성
- 사용자가 내용 불러주거나, 이 세션 중 일어난 이슈를 자동 요약해서 초안 작성 → 사용자 승인

Lesson 파일 포맷:

```markdown
---
platform: ios|android|both
severity: blocking|warning|info
category: signing|payment|privacy|metadata|build|screenshots|localization|version
first_hit: YYYY-MM-DD
hits: 1
source: manual | auto-from-session | reviewer-feedback
---

# 제목 (한줄 요약)

## 증상
관찰된 문제 또는 리젝 메시지 원문.

## 원인
근본 원인 분석.

## 해결
이번 회에서 어떻게 해결했는지.

## 재발 방지 체크리스트
- [ ] 체크리스트 항목 1
- [ ] 체크리스트 항목 2
```

기존 lesson 이 같은 category+platform 으로 존재하면 새 파일 만들지 말고 기존 파일의 `hits` +1 하고 맨 아래 "## 재발 히스토리" 섹션에 날짜 추가.

### Step 6 — 동기화

새 lesson 또는 SKILL.md 수정이 있으면:
- ssamssae/claude-skills repo 에 commit/push (맥·WSL 양쪽 동기화)
- 커밋 메시지: `docs(submit-app): add lesson <slug>`

## 텔레그램 보고

- 시작: "🚀 /submit-app 시작 — <앱명> (<platform>)"
- Step 0: 체크리스트 전체 전송, 사용자 응답 대기
- Step 2 완료: "📦 빌드 완료 (<file> <size>MB)"
- Step 3 완료: "⬆️ 업로드 명령 준비 — 복붙해서 실행해주세요:\n<명령어>"
- Step 5: 새 lesson 생성 시 "📚 새 lesson 저장: <title>"

## 안전 원칙

- BLOCKING 체크리스트 실패 시 중단, 강제 진행 금지
- aab/ipa 파일은 커밋하지 않음 (build 산출물은 `.gitignore` 확인)
- Play Console / App Store Connect 웹 UI 자동 조작 = ASC API + fastlane + Playwright MCP 사용 자동화 default (2026-05-01). 가격/territory/유료 전환 등 위험 카테고리는 사용자 컨펌 필수.
- ASC 가드 3종(W6/W7/W8) = dry-run default. `--apply` 는 강대종 컨펌 필수 (Step 3.5).
- 버전 bump 커밋은 push 금지 — 사용자가 확인 후 직접 push
- `--force` / `--no-verify` 금지

## 학습 루프

이 스킬의 핵심 가치는 "매 회 학습"이다.

- 각 제출 후 Step 5 에서 새 lesson 캡처
- 다음 제출 때 Step 0 에서 다시 로드 → 같은 실수 반복 X
- lessons 파일은 시간 지날수록 풍성해지고, 체크리스트도 자동으로 커짐

## 시드 Lessons (초기 등록)

- `apple-3-1-1-external-payment.md` — Apple 3.1.1 외부 결제/기부 링크 금지 (메모요 1.0 리젝)
- `android-aab-naming.md` — aab 파일명은 영문·하이픈 (`memoyo-1.0.2-19.aab`)
- `ios-bundle-id-convention.md` — `com.ssamssae.<name>` 고정
- `ios-signing-team.md` — DEVELOPMENT_TEAM = 46UH85U2B8 사전 주입 (submit-app 본체에서 처리)
- `both-pretendard-font-size.md` — Pretendard 번들 시 앱 용량 +~3MB

## 관련 스킬

- `/irun`, `/arun` — 빌드·실기기 설치 (제출 전 동작 확인, mac mini SSH 빌드)
- 맥미니 mail-watcher v5 — 제출 후 2시간 폴링 Gmail 심사·결제 알림 (스킬 아닌 백그라운드 자동화)
- ASC 가드 3종 (`~/.claude/automations/scripts/asc-{territory-verify,resubmit,rc-reply}.py`) — 자동 출시 quirk 우회 + reject 답글 자동화 (Step 3.5)
- `/issue` — 포괄적 이슈 로깅 (앱 제출 관련이면 이 스킬의 lessons/ 에도 저장)
- `/worklog` — 제출 작업 로그 기록
