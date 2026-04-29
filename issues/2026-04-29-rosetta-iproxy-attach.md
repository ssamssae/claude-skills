---
prevention_deferred: null
---

# Apple Silicon mac mini 에서 Flutter iOS debug attach 가 Rosetta 없이는 실패

- **발생 일자:** 2026-04-29 22:30 KST
- **해결 일자:** 2026-04-29 23:24 KST
- **심각도:** medium (debug 빌드 막힘, release ipa 는 영향 없음)
- **재발 가능성:** low (1회 설치하면 영구 해결, 단 macOS 재설치 시 재발)
- **영향 범위:** mac mini (M1, arm64) SSH 빌드 — irun/arun 워크플로우

## 증상
`ssh mac-mini 'flutter run --debug -d <iPhone udid>'` 실행 시 Xcode build/install 까지 정상 진행 (5.3s + 14.9s). 직후 정확히 다음 메시지로 멈춤:

```
Error: Flutter failed to run "/opt/homebrew/share/flutter/bin/cache/artifacts/libusbmuxd/iproxy <port>:<port> --udid <udid>".
The binary was built with the incorrect architecture to run on this machine.
If you are on an ARM Apple Silicon Mac, Flutter requires the Rosetta translation environment.
```

앱은 디바이스에 설치는 됐지만 splash 에서 멈추고 dart VM 에 attach 못 함. 이전 세션에서 "mac mini Xcode 가 떠있어서 lldb 충돌" 가설 세웠는데 오답 — Xcode 종료해도 동일 에러.

## 원인
flutter (3.41.8 stable) 가 함께 묶어 보내는 `iproxy` 바이너리(libusbmuxd, USB↔호스트 포트 포워딩 데몬) 가 x86_64 빌드. mac mini 는 M1 (arm64) 라 Rosetta 없이는 x86 바이너리 실행 불가. release ipa 빌드는 codesign 만 하므로 영향 없고, debug 모드의 dart VM 어태치 단계에서만 막힘.

## 조치
mac mini 에서 sudo 1회:

```
sudo softwareupdate --install-rosetta --agree-to-license
```

출력에 "Package Authoring Error: 122-28065: Package reference com.apple.pkg.RosettaUpdateAuto is missing installKBytes attribute" 경고 떠도 무해. 마지막 줄 "Install of Rosetta 2 finished successfully" 확인 후 `flutter run --debug` 재시도 → 정상 attach 확인:

- Syncing files 312ms
- Flutter run key commands prompt (r/R/h/d/c/q)
- Dart VM Service URL emit
- iPhone17 (00008150-0018459C2161401C) 한줄일기 메인 화면 렌더링 확인 ("켜졌어" 회신)

## 예방 (Forcing function 우선)
- `irun` / `arun` SKILL.md 에 "M1 mac mini 사전체크" 단계 추가 — flutter run 호출 전에 `ssh mac-mini 'pgrep oahd >/dev/null'` 검사. 실패 시 즉시 중단하고 `sudo softwareupdate --install-rosetta --agree-to-license` 안내. (oahd = Rosetta 데몬, 미설치 시 미실행)
- Apple Silicon 빌드 호스트 셋업 체크리스트에 Rosetta 항목 명시 — Xcode/flutter 셋업보다 우선 순서.
- 관련 메모리 추가: `project_mac_mini_ios_debug_rosetta.md`.

## 재발 이력
_(없음)_

## 관련 링크
- 메모리: `memory/project_mac_mini_ios_debug_rosetta.md`, `memory/project_mac_mini_ios_ipa_recovery.md`
- 텔레그램 메시지: 9448 (세션 핸드오프 시작) → 9466 ("켜졌어" 확인)
- 디바이스: 강대종의 iPhone (2), udid 00008150-0018459C2161401C
- 앱: 한줄일기 (com.daejongkang.hanjul) 1.1.0+4
