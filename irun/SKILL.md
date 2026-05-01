---
name: irun
description: Flutter 앱을 mac mini 에 직접 USB 연결된 아이폰17(기본 device id 00008150-0018459C2161401C)에 clean + debug 로 재빌드·실행. SSH 로 mac mini 호출, 본진 Mac/WSL 어디서 호출해도 동일.
allowed-tools: Bash, Monitor
---

# 아이폰 디버그 재실행 (mac mini SSH 빌드)

현재 Flutter 프로젝트를 **mac mini 에 USB 연결된 iPhone17** 에 clean 빌드 후 **debug** 모드로 실행한다. 본진 Mac, WSL, 어디서 호출해도 동일하게 mac mini 가 빌드 SoT.

> **2026-04-29 정책 변경**: iPhone/Galaxy 실기기 빌드 SoT = 🤖 mac mini 단독. 본진 Mac/WSL 은 시뮬레이터 빌드만 (그 경우 일반 `flutter run` 로컬 사용, irun 호출 X). irun = 실기기 debug install/run 전용, mac mini SSH 로 위임.

## 기기 라우팅 (지휘관 1명 원칙)

🍎 Mac 본진 = 지휘관(설계·결정·메인 세션, main 머지 결정) / 🏭 Mac mini = 빌드·배포 워커(SSH 라우팅 수신) / 🪟 WSL = 작업자(`wsl/*` 브랜치 push, main 직접 push 금지). 운반체 = `wsl-directive.sh` / `mac-report.sh`.

**이 스킬**: 어느 기기에서 호출해도 🏭 Mac mini SSH 경유 (iPhone17 USB 직결 mac mini 단독). 본진/WSL 직접 빌드 X.

## 입력

`$ARGUMENTS`:
- 비어있음 → 현재 PWD 가 Flutter 프로젝트 루트 가정 (pubspec.yaml 존재 확인)
- device id 1개 → device id 만 변경, 호출 측 PWD basename 사용

## 고정값

- 기본 device id: `00008150-0018459C2161401C` (강대종님 iPhone17, mac mini USB 연결)
- mac mini SSH alias: `mac-mini` (Tailscale)
- mac mini Flutter: `/opt/homebrew/bin/flutter`
- mac mini 프로젝트 위치: `~/apps/<repo-name>`

## 절차

1. **호출 측 git push** (코드 동기화)
   - 현재 cwd 가 git repo 인지 확인 (`git rev-parse --show-toplevel`)
   - `git status --porcelain` 출력 비어있지 않으면: 사용자에게 commit 필요한지 확인 (자동 커밋 X — 사용자 의도 모호)
   - 커밋된 변경사항 있으면: `git push` (실패 시 즉시 보고하고 중단)
   - repo 가 아니면 1단계 skip (사용자가 mac mini 에 동일 경로로 이미 sync 했다고 가정)

2. **repo 이름 추출**
   - `REPO=$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")`
   - mac mini 측 경로: `~/apps/$REPO`

3. **Rosetta 사전체크** (M1 mac mini iOS debug 필수 — 빌드 시작 전)
   - `ssh mac-mini 'pgrep -x oahd >/dev/null 2>&1 && echo OK || echo MISSING'`
   - 응답이 `MISSING` 이면 즉시 abort + 다음 1줄 안내:
     "Rosetta 미설치. mac mini 에 1회 직접 실행 필요: `ssh -t mac-mini 'sudo softwareupdate --install-rosetta --agree-to-license'`. 설치 후 irun 재시도."
   - 근거: iOS debug 시 Flutter 가 묶어 보내는 `iproxy` 가 x86_64 빌드 → arm64 mac mini 에서 Rosetta 없으면 dart VM attach 실패. release ipa 빌드는 영향 X (codesign 만). issue 2026-04-29-rosetta-iproxy-attach.md 참조.

4. **mac mini 측 빌드 + 실행** (run_in_background=true)
   - 명령:
     ```
     ssh mac-mini "cd ~/apps/$REPO && git pull --rebase --autostash && /opt/homebrew/bin/flutter clean && /opt/homebrew/bin/flutter run --debug -d $DEVICE_ID"
     ```
   - **release 모드 금지** — release ipa SoT 는 mac mini night-build (launchd) 또는 별도 /submit-app 흐름

5. **Monitor 로 빌드 이벤트 관찰**
   - 성공 패턴: `Installing and launching|Xcode build done|Syncing files|to quit|Flutter run key commands`
   - 실패 패턴: `error:|Error:|FAILED|Exception|BUILD FAILED|No devices`
   - timeout_ms: 600000 (iOS clean 빌드 첫회 5~10분 가능)

6. **완료 보고**
   - 성공: "iPhone17 ($DEVICE_ID) 에 debug install+launch 완료. (mac mini BG 프로세스 유지)"
   - 실패: 마지막 ~30줄 SSH 출력 발췌
   - hot reload 가 필요하면 강대종님이 직접 mac mini SSH attach: `ssh mac-mini` → tmux 또는 해당 터미널 찾아서 키 입력

## 중요

- iOS clean 첫회는 Xcode build + signing 때문에 5~10분 가능
- `sleep` 폴링 X — Monitor 이벤트 기반
- mac mini 측 ~/apps/<repo> 가 없으면 사용자에게 안내: "mac mini 에 ~/apps/<repo> clone 필요 (`git clone <url> ~/apps/<repo>`)"
- 광범위 `pkill flutter` 등 금지 — mac mini 의 다른 빌드 프로세스 영향 가능. 필요 시 정밀 패턴 (`pkill -f "flutter run.*$REPO"`)
