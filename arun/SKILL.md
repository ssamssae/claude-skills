---
name: arun
description: Flutter 앱을 연결된 갤럭시 S24(기본 device id R3CX10GX1XR)에 clean + debug 로 재빌드·실행. WSL→Windows 브릿지로 동작. 이전 Gradle 데몬 정리(광범위 java kill 금지). irun 의 Android 버전.
allowed-tools: Bash, Monitor
---

# 안드로이드(S24) 디버그 재실행

WSL 셸에서 호출되는 스킬. 현재 Flutter 프로젝트를 Windows 측 `flutter` 와 `adb` 를 거쳐 갤럭시 S24 (또는 인자로 받은 Android 디바이스) 에 clean 빌드 후 **debug** 모드로 설치·실행한다.

> **2026-04-29 정책 변경**: Android **release aab 빌드 SoT = 🤖 Mac mini 단독**. WSL 에는 release upload keystore 가 없으므로 release 빌드 시 sign fail. arun 은 **dev/debug install 워크플로우** 전용이다. release 효과 폰 검증이 필요하면:
>
> 1. mac-mini night-build 산출물 받기: `scp mac-mini:apps/<app>/build/app/outputs/bundle/release/app-release.aab ./` (또는 launchd 잡 결과 파일)
> 2. aab → apks 변환: `bundletool build-apks --bundle=app-release.aab --output=app.apks --mode=universal`
> 3. `unzip -p app.apks universal.apk > app-release.apk && adb install -r app-release.apk`
>
> 자세한 SoT 정책은 `~/.claude/AGENT.md` "🪟 윈도우 데스크탑 = 전위" / "🤖 M1 Mac mini" 섹션 참조.

## 입력

`$ARGUMENTS` 형식:
- 비어있음 → 현재 PWD 가 Flutter 프로젝트 루트 가정 (pubspec.yaml 존재 확인)
- 한 단어 (예: `R3CX10GX1XR`) → device id 만 변경, PWD 사용
- 두 단어 (예: `C:\dev\hello R3CX10GX1XR`) → 첫 번째는 프로젝트 경로, 두 번째는 device id
- WSL 경로(`/mnt/c/...`) 가 들어오면 자동으로 Windows 경로(`C:\...`) 로 변환

## 고정값

- 기본 device id: `R3CX10GX1XR` (강대종님 갤럭시 S24, SM_S921N)
- 기본 device name 표기: `S24`
- adb 절대경로: `C:\Users\USER\AppData\Local\Android\sdk\platform-tools\adb.exe`
- Flutter 호출: `powershell.exe -NoProfile -Command "..."` (절대 cmd.exe 금지 — UNC cwd 거부)

## 절차

1. **인자 파싱 + 경로 해석**
   - `$ARGUMENTS` 토큰 수에 따라 PROJECT_DIR / DEVICE_ID 결정
   - 단일 토큰 디스앰비귀에이션: 토큰이 `/`, `\`, `:` 중 하나라도 포함하면 **경로**로 간주, 아니면 device id
   - PROJECT_DIR 가 비어있으면 `pwd` 사용
   - PROJECT_DIR 가 `/mnt/c/...` 이면 `C:\...` 로 변환: `sed 's|^/mnt/c|C:|; s|/|\\|g'`
   - PROJECT_DIR 가 `C:\...` 이면 WSL 경로 역변환도 준비 (pubspec 체크용): `sed 's|^C:|/mnt/c|; s|\\|/|g'`
   - PROJECT_DIR 안에 `pubspec.yaml` 없으면 즉시 에러 (`echo "Not a Flutter project: $PROJECT_DIR"; exit 1`)

2. **이전 빌드 잔여물 정리** (광범위 종료 금지!)
   - `pkill -f "flutter run" 2>/dev/null; sleep 1` (WSL 측 flutter run 모니터 프로세스만)
   - Gradle 데몬:
     ```
     powershell.exe -NoProfile -Command "$env:JAVA_HOME=[Environment]::GetEnvironmentVariable('JAVA_HOME','User'); cd $WIN_PROJECT_DIR\android; if (Test-Path .\gradlew.bat) { .\gradlew.bat --stop }"
     ```
   - **WSL→PowerShell 호출 시 JAVA_HOME 자동 전파 안 됨.** 항상 PS 명령 첫줄에 `$env:JAVA_HOME=[Environment]::GetEnvironmentVariable('JAVA_HOME','User')` 주입할 것 (gradlew, sdkmanager, avdmanager 모두 해당)
   - **NEVER** `Stop-Process java` 같은 광범위 명령

3. **디바이스 연결 확인**
   - `"$ADB" devices -l | grep "$DEVICE_ID"` 
   - 안 잡히면 사용자에게 안내: "S24 가 안 잡힘. 무선 디버깅 토글 ON/OFF 시도해보세요" + 종료

4. **clean + debug run (백그라운드)**
   - 로그 파일 준비: `mkdir -p /tmp/arun_logs; LOG=/tmp/arun_logs/run_$(date +%s).log; echo "$LOG" > /tmp/arun_logs/last_log`
   - 명령 (nohup 으로 분리, run_in_background=true):
     ```
     nohup powershell.exe -NoProfile -Command "$env:JAVA_HOME=[Environment]::GetEnvironmentVariable('JAVA_HOME','User'); cd $WIN_PROJECT_DIR; flutter clean; flutter run --debug -d $DEVICE_ID" > "$LOG" 2>&1 &
     ```
   - JAVA_HOME 주입 동일 (flutter 도 안전하게)
   - **release 모드 금지** (2026-04-29) — WSL 에 upload keystore 없음 → sign fail. release 효과 검증 필요하면 mac-mini night-build 산출물 다운로드 후 adb install (스킬 본문 상단 절차 참조).

5. **Monitor 로 빌드 이벤트 관찰**
   - BG_ID 의 stdout 을 Monitor 로 스트림
   - until 조건 패턴(grep -E):
     - 성공: `Installing build|Syncing files|Flutter run key commands|to quit|Hot reload`
     - 실패: `error:|Error:|FAILED|Exception|BUILD FAILED|Gradle task assemble.*FAILED`
   - timeout_ms: 600000 (10분 — Gradle warm-up 첫회 길 수 있음)

6. **완료 보고**
   - 성공 이벤트 잡히면: "S24 에 release APK 설치+실행 완료. 핫리로드 대기 중. (백그라운드 BG_ID 유지)"
   - 실패 이벤트 잡히면: 마지막 ~30줄 로그 발췌해서 사용자에게 요약

## 중요

- 첫 빌드는 Gradle 캐시 + NDK warm-up 때문에 5~7분 가능 (이미 한 번 돌렸으면 30~60초)
- `sleep` 으로 폴링 금지 — Monitor 이벤트 기반
- 빌드 끝난 뒤 BG 프로세스는 죽이지 말 것 (사용자가 Hot reload 쓸 수 있음). 필요하면 사용자가 직접 종료하거나 다음 arun 호출 시 자동 정리됨
- WSL 측 `pkill -f "flutter run"` 은 OK (정밀 패턴), Windows 측 `Stop-Process java` 는 금지 (공유 호스트의 다른 java 워크로드 영향)
- pubspec.yaml 가드 안 걸면 wrong-cwd 사고 자주 남 — 반드시 체크
