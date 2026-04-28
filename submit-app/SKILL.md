---
name: submit-app
description: Flutter 앱 App Store / Play Console 제출 루틴. 과거 실수·리젝 사례(lessons/) 먼저 읽어 재발 방지 체크리스트 후 빌드·업로드·심사 제출. 트리거 "앱 등록", "스토어 제출", "심사 보내", "aab 업로드", "ipa 업로드", "리뷰 제출", "/submit-app", "/submit", "Play Console 올려", "App Store 올려".
allowed-tools: Read, Edit, Write, Bash, Grep, Glob
---

# /submit-app — 앱 스토어 제출 루틴 + 실수 학습

앱 제출은 자주 하는 루틴이지만 플랫폼 정책(Apple 3.1.1, aab 파일명 등) 때문에 매번 같은 함정에 빠질 수 있다. 이 스킬은 **과거 실수를 먼저 읽고** 사용자에게 확인시킨 뒤 빌드·업로드·심사 제출을 진행한다.

## 호출 패턴

- `/submit-app <앱명> --platform=ios` — App Store Connect 제출
- `/submit-app <앱명> --platform=android` — Play Console 제출
- `/submit-app <앱명>` — 플랫폼 미지정 시 먼저 물어봄
- `/submit-app <앱명> --dry-run` — 실제 업로드 없이 체크리스트만 돌려보기
- `/submit-app lessons` — 저장된 lessons 목록만 출력

## 전제

- Flutter 프로젝트 루트가 `~/apps/<앱명>/` 에 있거나 `pwd` 가 Flutter 프로젝트
- iOS: Xcode Command Line Tools + CocoaPods + fvm 세팅 완료, signing team `46UH85U2B8` 주입돼있음
- Android: keystore 준비, `android/key.properties` 존재, release 서명 설정 완료
- Play Console / App Store Connect 는 사용자가 수동으로 웹 UI 접속 (이 스킬은 aab·ipa 파일 생성과 업로드 지시까지)

## 절차

### Step 0 — Keystore SoT 가드 (Android 만 해당)

`--platform=android` 일 때 **반드시 먼저** 실행. iOS 는 스킵.

1. `~/.claude/skills/submit-app/keystore-sot.md` 의 "## Registry" 섹션에서 해당 앱 라인 찾기
2. SoT 가 `🍎 Mac` 인데 현재 hostname 이 `*MacBook*`/`*MBP*` 가 아니면 → 즉시 중단:
   ```
   🚨 keystore SoT 불일치
   <앱명> 의 release keystore SoT 는 🍎 Mac 입니다.
   현재 기기: 🪟 WSL
   이 기기에서 서명·업로드 시 Play Store 가 "서명 불일치" 로 영구 거부할 수 있어요.
   → Mac 세션에서 /submit-app <앱명> --platform=android 호출해주세요.
   ```
3. SoT 가 `🪟 WSL` 인데 현재 hostname 이 `DESKTOP-*` 가 아니면 → 동일한 방식으로 중단 + WSL 로 안내
4. registry 에 앱이 없으면 → 경고:
   ```
   ⚠️ <앱명> 이 keystore SoT registry 에 없습니다.
   keystore-sot.md "## Registry" 섹션에 먼저 한 줄 추가해주세요:
     <앱명>: 🍎 Mac | 🪟 WSL (keystore: android/<file>.jks, created: YYYY-MM-DD)
   ```
   사용자가 "일단 진행" 이라고 하면 warning 만 남기고 계속.
5. 통과하면 Step 0.5 (Lessons) 로.

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

- `pubspec.yaml` 의 `version: X.Y.Z+N` 에서 N(build number) +1
- X.Y.Z 는 사용자에게 물어봄 (patch/minor/major 중 선택)
- 커밋: `chore: bump version to X.Y.Z+N`

### Step 2 — 빌드

**iOS**:
```bash
cd <app> && fvm flutter build ipa --release
```
산출물: `build/ios/ipa/*.ipa`

**Android**:
```bash
cd <app> && fvm flutter build appbundle --release
```
산출물: `build/app/outputs/bundle/release/app-release.aab`

빌드 후 파일명 규칙 확인 (aab: 영문·하이픈). 어긋나면 `build/<app>-X.Y.Z-N.aab` 로 복사.

### Step 3 — 업로드

**iOS**:
- Transporter.app 또는 `xcrun altool --upload-app -f <ipa> -t ios` 사용
- App Store Connect 프로세싱 대기 (보통 5~20분)

**Android**:
- `fastlane supply --aab <aab>` 또는 수동 업로드 링크 안내
- 메모요처럼 Closed Testing 트랙 별도 관리 시 `--track=beta`

이 스킬은 업로드 **명령어와 경로만 출력**하고 실제 웹 업로드는 사용자가 제어 (프로덕션 계정 조작은 항상 수동 확인).

### Step 4 — 심사 제출 후 모니터링 활성화

`/review-status-check` 스킬이 이미 Gmail 모니터링하므로 별도 조치 불필요. 업로드 완료 시 텔레그램으로 "심사 제출 완료 — Gmail 상태 알림 대기" 공지.

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
- Play Console / App Store Connect 웹 UI 자동 조작은 이 스킬에서 하지 않음 (계정 리스크). 사용자가 직접.
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
- `ios-signing-team.md` — DEVELOPMENT_TEAM = 46UH85U2B8 사전 주입 (/land 가 처리)
- `both-pretendard-font-size.md` — Pretendard 번들 시 앱 용량 +~3MB

## 관련 스킬

- `/irun`, `/land` — 빌드·아이폰 설치 (제출 전 동작 확인)
- `/review-status-check` — 제출 후 심사 상태 Gmail 모니터링
- `/issue` — 포괄적 이슈 로깅 (앱 제출 관련이면 이 스킬의 lessons/ 에도 저장)
- `/worklog` — 제출 작업 로그 기록
