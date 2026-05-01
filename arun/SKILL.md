---
name: arun
description: Flutter 앱을 mac mini 에 직접 USB 연결된 갤럭시 S24(기본 device id R3CX10GX1XR)에 clean + debug 로 재빌드·실행. SSH 로 mac mini 호출, 본진 Mac/WSL 어디서 호출해도 동일.
allowed-tools: Bash, Monitor
---

# 안드로이드(S24) 디버그 재실행 (mac mini SSH 빌드)

현재 Flutter 프로젝트를 **mac mini 에 USB 연결된 갤럭시 S24** 에 clean 빌드 후 **debug** 모드로 설치·실행한다. 본진 Mac, WSL, 어디서 호출해도 동일하게 mac mini 가 빌드 SoT.

> **2026-04-29 정책 변경**: 실기기 빌드 SoT = 🤖 mac mini 단독. 본진 Mac/WSL 은 시뮬레이터/에뮬레이터 빌드만 (그 경우 일반 `flutter run` 로컬 사용, arun 호출 X). arun = 실기기 debug install/run 전용, mac mini SSH 위임. release aab SoT 도 mac mini night-build (launchd) 단독.

## 기기 라우팅 (지휘관 1명 원칙)

🍎 Mac 본진 = 지휘관(설계·결정·메인 세션, main 머지 결정) / 🏭 Mac mini = 빌드·배포 워커(SSH 라우팅 수신) / 🪟 WSL = 작업자(`wsl/*` 브랜치 push, main 직접 push 금지). 운반체 = `wsl-directive.sh` / `mac-report.sh`.

**이 스킬**: 어느 기기에서 호출해도 🏭 Mac mini SSH 경유 (S24 USB 직결 mac mini 단독). 본진/WSL 직접 빌드 X.

## 입력

`$ARGUMENTS`:
- 비어있음 → 현재 PWD 가 Flutter 프로젝트 루트 가정 (pubspec.yaml 존재 확인)
- device id 1개 (예: `R3CX10GX1XR`) → device id 만 변경, 호출 측 PWD basename 사용

## 고정값

- 기본 device id: `R3CX10GX1XR` (강대종님 갤럭시 S24, SM_S921N, mac mini USB 연결)
- 기본 device name 표기: `S24`
- mac mini SSH alias: `mac-mini` (Tailscale)
- mac mini Flutter: `/opt/homebrew/bin/flutter`
- mac mini adb: `/opt/homebrew/share/android-commandlinetools/platform-tools/adb`
- mac mini 프로젝트 위치: `~/apps/<repo-name>`
- **SSH 비대화형 세션 환경변수 주입** (필수, ~/.zshrc 자동 source 안 됨):
  ```
  export JAVA_HOME=/opt/homebrew/opt/openjdk@17
  export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools
  export PATH=$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:/opt/homebrew/bin:$PATH
  ```
  (mac mini night-build launchd plist 와 동일 변수 셋)

## 절차

1. **호출 측 git push** (코드 동기화)
   - 현재 cwd 가 git repo 인지 확인 (`git rev-parse --show-toplevel`)
   - `git status --porcelain` 출력 비어있지 않으면: 사용자에게 commit 필요한지 확인 (자동 커밋 X)
   - 커밋된 변경사항 있으면: `git push` (실패 시 즉시 보고하고 중단)
   - repo 가 아니면 1단계 skip (사용자가 mac mini 에 동일 경로로 이미 sync 했다고 가정)

2. **repo 이름 추출**
   - `REPO=$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")`
   - mac mini 측 경로: `~/apps/$REPO`

3. **디바이스 연결 확인** (선제)
   - `ssh mac-mini "/opt/homebrew/share/android-commandlinetools/platform-tools/adb devices -l | grep $DEVICE_ID"`
   - 안 잡히면: "S24 가 mac mini 에 안 잡힘. USB 케이블/무선 디버깅 토글 확인" 알리고 종료

4. **mac mini 측 빌드 + 실행** (run_in_background=true)
   - 명령:
     ```
     ssh mac-mini 'export JAVA_HOME=/opt/homebrew/opt/openjdk@17; export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools; export PATH=$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:/opt/homebrew/bin:$PATH; cd ~/apps/'$REPO' && git pull --rebase --autostash && /opt/homebrew/bin/flutter clean && /opt/homebrew/bin/flutter run --debug -d '$DEVICE_ID
     ```
   - **release 모드 금지** — release aab SoT 는 mac mini night-build (launchd, 02:00 KST)

5. **Monitor 로 빌드 이벤트 관찰**
   - 성공 패턴: `Installing build|Syncing files|Flutter run key commands|to quit|Hot reload`
   - 실패 패턴: `error:|Error:|FAILED|Exception|BUILD FAILED|Gradle task assemble.*FAILED`
   - timeout_ms: 600000 (Gradle warm-up 첫회 5~7분 가능)

6. **완료 보고**
   - 성공: "S24 ($DEVICE_ID) 에 debug install+launch 완료. (mac mini BG 프로세스 유지)"
   - 실패: 마지막 ~30줄 SSH 출력 발췌
   - hot reload 필요하면 강대종님이 mac mini SSH attach 직접

## 중요

- 첫 빌드는 Gradle 캐시 + NDK warm-up 때문에 5~7분 (이후는 30~60초)
- `sleep` 폴링 X — Monitor 이벤트 기반
- mac mini 측 `~/apps/<repo>` 가 없으면 사용자에게 안내: clone 필요
- 광범위 `pkill java` 또는 `Stop-Process java` 금지 — mac mini 의 다른 Gradle/launchd 빌드 영향 가능. 정밀 패턴만 (`pkill -f "flutter run.*$REPO"`)
- pubspec.yaml 가드: 호출 측 PWD 에 pubspec.yaml 없으면 즉시 에러
