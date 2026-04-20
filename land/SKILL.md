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

### 5. 의존성

```bash
fvm flutter pub get
cd ios && pod install --repo-update 2>&1 | tail -30; cd ..
```

pod install 실패 (CocoaPods 레포 문제) 시 `pod repo update && pod install` 한 번 더 시도. 그래도 실패면 에러 요약 후 중단.

### 6. 첫 실행 시그널 전송 (signing 체크)

`ios/Runner.xcworkspace` 를 한 번도 열지 않은 상태면 signing team 이 비어 있어 `/irun` 이 실패한다. 판정 기준:

```bash
grep -q 'DEVELOPMENT_TEAM = ""' ios/Runner.xcodeproj/project.pbxproj 2>/dev/null
```

비어 있으면 한 번만 Xcode 를 열어 signing 설정이 필요하다는 안내 후 중단:

```
⚠️ iOS signing team 미설정
  최초 1회: open ios/Runner.xcworkspace → Runner 타겟 → Signing & Capabilities 에서
           "Automatically manage signing" 체크 + Team 선택
  완료 후 /land 재호출하세요.
```

이미 team 이 박혀 있으면 통과.

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
- Bundle ID / 번들 org 변경 금지 — 한 번 정해진 `com.ssamssae.<name>` 고정
- signing team 자동 설정 금지 (사용자 수동 1회 요구)
- `--force` / `--no-verify` 금지
- 로그에 tokens/secrets 찍히지 않도록 환경 변수 노출 자제

## 첫 실행 기대 흐름 (hankeup 예)

1. WSL: `/to-iphone hankeup` — GitHub repo 생성 + push + Tailscale SSH 로 맥 트리거
2. Mac: `/land https://github.com/ssamssae/hankeup.git` 자동 수신
3. `~/apps/hankeup` 에 clone
4. iOS 폴더 없으므로 `flutter create --platforms=ios --org com.ssamssae --project-name hankeup .`
5. pub get + pod install
6. signing team 비어있음 → 사용자에게 Xcode 1회 여는 안내 후 중단
7. 사용자가 Xcode 에서 team 선택 후 `/land hankeup` 재호출
8. team 통과 → `/irun` → 아이폰에 hankeup 설치

두 번째 앱부터는 team 가 이미 선택된 경우가 많아 1회 중단 없이 곧바로 /irun 까지 이어진다 (Automatically manage signing 이면 `com.ssamssae.<새이름>` 프로비저닝 프로파일도 자동 생성).

## 기기 제약

- 맥 본진 전용. WSL·아이폰에서는 동작 불가.
- iOS signing 관련 수동 1회 액션은 자동화하지 않는다 — Apple 계정 보안상 명시 허용.
