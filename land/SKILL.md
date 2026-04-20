---
name: land
description: WSL /to-iphone 에서 넘어온 GitHub repo URL 을 맥에 clone-or-pull 하고, iOS 플랫폼 자동 세팅 + pub get + pod install 을 거쳐 /irun 으로 아이폰에 릴리즈 설치한다. WSL → Mac → iPhone 으로 이어지는 ship-to-iphone 파이프라인의 맥 쪽 종단. 호출: "/land https://github.com/ssamssae/<앱명>.git".
allowed-tools: Bash, Read, Edit, Monitor, Skill
---

# /land — ship 된 앱을 아이폰까지 내려 앉히기

WSL 데스크탑 `/to-iphone` 이 앱 코드를 GitHub 에 푸시하고 이 스킬을 호출하면, 맥 본진이 코드를 받아 iOS 빌드를 거쳐 아이폰까지 실행시킨다. 페어 스킬 관계:

- WSL: `/to-iphone <앱명>` — git push + 맥 트리거
- Mac: `/land <repo-url>` (이 스킬) — clone/pull + iOS 세팅 + /irun

## 호출 패턴

- `/land https://github.com/ssamssae/<앱명>.git`
- `/land https://github.com/ssamssae/<앱명>` (`.git` 생략 허용)
- `/land <앱명>` (owner 생략 시 ssamssae 기본)
- Tailscale SSH 로 들어온 원격 호출도 동일 시그니처:
  `ssh user@100.74.85.37 "cc -p '/land https://github.com/ssamssae/<앱명>.git'"`

## 전제

- hostname 이 `.local` 로 끝나는 맥 본진에서만 실행. 아니면 "맥 본진에서 실행해주세요" 후 종료.
- `~/apps/` 를 작업 루트로 사용 (없으면 mkdir).
- Xcode Command Line Tools, CocoaPods, flutter, fvm 설치 가정 (irun 과 동일 환경).
- 아이폰(기본 device id `00008150-0018459C2161401C`) USB 연결 상태. 없으면 /irun 직전에 안내 후 대기.

## 절차

### 1. 입력 파싱

`$ARGUMENTS` 에서 repo URL 추출:
- `https://github.com/<owner>/<name>.git` 또는 `.git` 없는 형태 허용
- `<name>` 단독 토큰이면 `https://github.com/ssamssae/<name>.git` 로 재구성
- `<name>` = repo URL 의 마지막 경로 컴포넌트 (`.git` 제거)

### 2. 호스트 체크

```bash
hostname | grep -q '\.local$' || { echo "맥 본진에서 실행해주세요"; exit 1; }
```

### 3. clone-or-pull

```bash
APP_DIR="$HOME/apps/<name>"
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" fetch --all --prune
  git -C "$APP_DIR" checkout main 2>/dev/null || git -C "$APP_DIR" checkout master
  git -C "$APP_DIR" pull --ff-only
else
  mkdir -p "$HOME/apps"
  git clone "<repo-url>" "$APP_DIR"
fi
cd "$APP_DIR"
```

pull 이 fast-forward 로 안 되면 (divergence) 중단하고 "맥에서 로컬 변경이 있습니다. 수동으로 정리해주세요" 리포트.

### 4. iOS 플랫폼 자동 세팅

```bash
if [ ! -d "ios" ]; then
  fvm flutter create --platforms=ios --org com.ssamssae --project-name <name> .
fi
```

- `ios/` 폴더가 없으면 iOS 플랫폼만 추가 생성 (기존 lib/, pubspec.yaml 유지)
- org 는 `com.ssamssae` 고정 → Bundle ID 는 `com.ssamssae.<name>` 로 결정됨
- 최초 실행 시에만 동작. 이후엔 스킵.

### 4-1. Bundle ID 자동 교정 (com.example → com.ssamssae)

repo 가 다른 기기에서 `--org com.example` 로 create 된 경우 `com.example.<name>` 으로 박혀 있다.
pbxproj 에서 찾아서 `com.ssamssae.<name>` 으로 치환:

```bash
PBXPROJ="ios/Runner.xcodeproj/project.pbxproj"
if [ -f "$PBXPROJ" ] && grep -q 'PRODUCT_BUNDLE_IDENTIFIER = com\.example\.' "$PBXPROJ"; then
  # com.example.<anything> → com.ssamssae.<name> 로 통일
  sed -i '' "s|PRODUCT_BUNDLE_IDENTIFIER = com\\.example\\.[A-Za-z0-9_]*|PRODUCT_BUNDLE_IDENTIFIER = com.ssamssae.<name>|g" "$PBXPROJ"
  echo "🔧 Bundle ID 교정: com.example.* → com.ssamssae.<name>"
fi
```

- `com.ssamssae.*` 이미 박혀 있으면 그대로 두고 스킵
- `com.example.*` 패턴만 매칭 → 의도적으로 다른 org 쓰는 앱에는 영향 없음
- Test / RunnerTests 타겟까지 세 블록 전부 일괄 치환됨

### 5. 의존성

```bash
fvm flutter pub get
cd ios && pod install --repo-update 2>&1 | tail -30; cd ..
```

pod install 실패 (CocoaPods 레포 문제) 시 `pod repo update && pod install` 한 번 더 시도. 그래도 실패면 에러 요약 후 중단.

### 6. signing team 자동 주입

강대종님 Apple Developer 팀 ID `46UH85U2B8` 를 pbxproj 에 자동 삽입한다. Flutter 가 create 단계에서 만드는 기본 pbxproj 는 `DEVELOPMENT_TEAM` 라인 자체가 없거나 `""` 로 비어 있어, 그대로 두면 `/irun` 의 release 빌드가 signing 오류로 죽는다.

판정 & 치환 전략:

```bash
PBXPROJ="ios/Runner.xcodeproj/project.pbxproj"
TEAM_ID="46UH85U2B8"

if [ -f "$PBXPROJ" ]; then
  # 케이스 A: DEVELOPMENT_TEAM = ""  → TEAM_ID 로 치환
  sed -i '' "s|DEVELOPMENT_TEAM = \"\";|DEVELOPMENT_TEAM = ${TEAM_ID};|g" "$PBXPROJ"

  # 케이스 B: DEVELOPMENT_TEAM 라인이 아예 없음 → CODE_SIGN_STYLE = Automatic; 바로 뒤에 추가
  if ! grep -q 'DEVELOPMENT_TEAM = ' "$PBXPROJ"; then
    sed -i '' "s|CODE_SIGN_STYLE = Automatic;|CODE_SIGN_STYLE = Automatic;\\
				DEVELOPMENT_TEAM = ${TEAM_ID};|g" "$PBXPROJ"
  fi

  echo "🔏 signing team 주입: ${TEAM_ID}"
fi
```

- `CODE_SIGN_STYLE = Automatic;` 은 Flutter 기본값이라 모든 타겟(Runner / RunnerTests) 블록에 존재
- sed 의 개행 삽입은 macOS BSD sed 문법(`\` + 실제 개행)을 사용
- 이미 다른 team ID 가 박혀있으면 덮어쓰지 않는다 (케이스 B 조건이 막아줌) — 다른 Apple 계정으로 사이닝하는 앱에는 영향 없음
- 기존 `46UH85U2B8` 이 이미 박힌 repo 는 케이스 A/B 모두 no-op

### 7. /irun 호출

위 단계가 전부 성공했으면 `/irun` 스킬을 연쇄 호출:

```
Skill(irun, args="")  # 기본 device id 사용
```

/irun 이 clean + release 빌드 + 아이폰 설치까지 담당한다.

### 8. 텔레그램 보고

각 단계 시작·완료 이벤트를 텔레그램 chat 538806975 로 보고:

- 시작: "🛬 /land 시작 — <repo-url>"
- clone/pull 완료: "📥 코드 수신 (HEAD: <short-sha>)"
- iOS 세팅 (필요 시): "🍎 iOS 플랫폼 추가 완료"
- pod install 완료: "📦 pods 설치 완료"
- /irun 기동: "▶️ /irun 실행, Xcode 빌드 대기"
- 최종 아이폰 설치: "✅ 아이폰 설치·실행 완료 (<name>)"

실패 단계에서는 원인 한 줄 + 다음 액션 (복구 방법) 첨부.

## 안전 원칙

- 맥 로컬 변경과 원격 충돌 시 강제 덮어쓰기 금지 (`git pull --ff-only` 만 사용, `git reset --hard` 금지)
- `sudo` 사용 금지
- Bundle ID 는 `com.ssamssae.<name>` 규약 고정. 자동 교정은 `com.example.*` 패턴에만 적용 — 의도적으로 다른 org 쓰는 앱은 건드리지 않는다
- signing team 자동 주입은 `46UH85U2B8` 기본값 + `DEVELOPMENT_TEAM` 이 비어있거나 없는 경우만 동작. 이미 다른 team ID 박혀 있으면 덮어쓰지 않는다
- `--force` / `--no-verify` 금지
- 로그에 tokens/secrets 찍히지 않도록 환경 변수 노출 자제

## 첫 실행 기대 흐름 (hankeup 예)

1. WSL: `/to-iphone hankeup` — GitHub repo 생성 + push + Tailscale SSH 로 맥 트리거
2. Mac: `/land https://github.com/ssamssae/hankeup.git` 자동 수신
3. `~/apps/hankeup` 에 clone
4. iOS 폴더 없으므로 `flutter create --platforms=ios --org com.ssamssae --project-name hankeup .`
4-1. Bundle ID `com.example.*` 흔적이 남아있으면 `com.ssamssae.hankeup` 으로 자동 교정
5. pub get + pod install
6. signing team 자동 주입 (`DEVELOPMENT_TEAM = 46UH85U2B8`)
7. `/irun` → 아이폰에 hankeup 설치

세 번째 앱부터는 중단 없이 `/to-iphone` 한 줄로 아이폰까지 완전 무인 배달된다 (Automatically manage signing + team ID 박혀 있음 → `com.ssamssae.<새이름>` 프로비저닝 프로파일 Apple 이 자동 생성).

## 기기 제약

- 맥 본진 전용. WSL·아이폰에서는 동작 불가.
- signing team 자동 주입은 `46UH85U2B8` (강대종님 개인 Apple Developer 계정) 기본값 기준. 다른 계정으로 사이닝하려면 해당 repo pbxproj 를 수동 선점 편집해둘 것 — 이 스킬은 이미 박힌 team ID 를 덮어쓰지 않는다.
