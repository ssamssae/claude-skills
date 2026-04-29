---
name: irun
description: Flutter 앱을 연결된 아이폰(기본 device id 00008150-0018459C2161401C)에 clean + debug 로 재빌드·실행. 이전 flutter run 프로세스 자동 종료.
allowed-tools: Bash, Monitor
---

# 아이폰 디버그 재실행

현재 Flutter 프로젝트를 연결된 iPhone에 clean 빌드 후 **debug** 모드로 실행합니다.

> **2026-04-29 정책**: iOS release ipa 빌드 SoT = 🤖 Mac mini (v1.1 도입 시점부터). irun 은 **dev/debug install 워크플로우** 전용. release 효과 폰 검증이 필요하면 Mac mini night-build 산출물(.ipa) 받아 별도 install. arun(Android) 과 같은 패턴.

## 절차

1. **device id 결정**
   - `$ARGUMENTS`로 device id가 주어지면 그 값 사용
   - 없으면 기본값: `00008150-0018459C2161401C` (강대종의 iPhone)

2. **기존 flutter run 프로세스 종료**
   - `pkill -f "flutter run" 2>/dev/null; sleep 1`

3. **clean + debug run (백그라운드)**
   - `fvm flutter clean && fvm flutter run --debug -d <device-id>`
   - `run_in_background: true` 로 Bash 도구 호출
   - **release 모드 금지** (2026-04-29) — release ipa 검증 필요하면 mac-mini night-build 산출물 다운로드 후 별도 install 절차

4. **Monitor로 빌드 이벤트 관찰**
   - 출력 파일을 `tail -f` + `grep -E --line-buffered "Xcode build done|Installing and launching|error:|Error:|FAILED|Exception"` 로 감시
   - `timeout_ms: 600000`

5. **완료 보고**
   - "Installing and launching" 이벤트가 오면 설치·실행 완료로 간주
   - 에러 이벤트가 오면 원인 로그를 사용자에게 요약 전달

## 중요
- iOS clean 빌드는 2~3분 걸릴 수 있음 — 기다리지 말고 Monitor 이벤트 기반으로 진행
- `sleep` 으로 폴링하지 말 것
