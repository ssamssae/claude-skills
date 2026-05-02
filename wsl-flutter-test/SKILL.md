---
name: wsl-flutter-test
description: WSL bash 에서 Flutter 앱 analyze/test 호출 시 cmd.exe pushd UNC cwd 거부 함정을 우회. run.sh 1줄 호출 권장 (4단계 자동화), 수동 4단계는 fallback. 트리거 "/wsl-flutter-test", "WSL 에서 flutter test", "WSL 에서 lotto/단어요/한줄일기 테스트".
---

# /wsl-flutter-test — WSL Flutter analyze/test 우회 절차

## 함정 정리

WSL bash 에서 `flutter test` 를 호출하려면 다음 3가지 함정을 차례로 만난다:

1. **WSL bash → /mnt/c/src/flutter 직접 호출 X** — Windows 측 flutter 바이너리는 CRLF + Windows ELF 라 `exec format error`.
2. **powershell.exe Set-Location 'C:\path' + flutter test** — PowerShell 자체는 cwd 받는데 .bat 진입점 내부 cmd 가 UNC cwd 거부.
3. **/mnt/c 경로 cmd.exe pushd** — UNC 경로 거부 (`CMD does not support UNC paths as current directories`).

## 권장 호출 (1줄, run.sh)

```bash
~/.claude/skills/wsl-flutter-test/run.sh <repo_path> [--analyze | --test | --both]
```

기본 모드 = `--both` (analyze 후 test, analyze 실패 시 test 스킵).

내부적으로 4단계를 자동 처리:
1. rsync `<repo>` → `/mnt/c/tmp/wsl-ft-<basename>-<timestamp>` (`.dart_tool` / `build` / `.git` 제외)
2. `powershell.exe -Command "Set-Location '<win_path>'; flutter analyze"` (또는 `flutter test`)
3. exit code 보존
4. trap EXIT 으로 임시 디렉토리 정리

exit 코드:
- `0` = 모든 단계 PASS
- `2` = repo 경로 디렉토리 아님
- `3` = `pubspec.yaml` 없음
- `4` = 모드 인자 잘못
- `5` / `6` = `rsync` / `powershell.exe` 부재
- 그 외 = 첫 실패 단계의 flutter exit code

예시:
```bash
~/.claude/skills/wsl-flutter-test/run.sh ~/apps/wordyo --analyze
# [1/4] rsync ... → /mnt/c/tmp/wsl-ft-wordyo-20260502-230705
# [2/4] flutter analyze
# No issues found! (ran in 3.1s)
# [done] exit=0
# [4/4] cleanup /mnt/c/tmp/wsl-ft-wordyo-20260502-230705
```

## 수동 4단계 (fallback / 디버깅용)

run.sh 가 어떤 이유로든 안 통할 때 (예: rsync 비호환, 별도 flag 필요) 수동 호출:

```bash
# 1. WSL 측 앱 소스를 Win 측 임시 디렉토리로 복제 (UNC 회피)
cp -r ~/apps/lottocalc /mnt/c/tmp/lottocalc_test

# 2. powershell.exe Set-Location 으로 Win 본체 cwd 진입 후 flutter test
powershell.exe -Command "Set-Location 'C:\tmp\lottocalc_test'; flutter test"

# 3. exit code + 결과 확인
echo "exit=$?"

# 4. 정리
rm -rf /mnt/c/tmp/lottocalc_test
```

## 출처

- 2026-05-02 lotto-calc PR #2 작업 검증 (knowhow `wsl-flutter-test` 진입점)
- daejong-page commit b074e3d — knowhow 신규 카테고리에 박혀있음
- 2026-05-02 wordyo step 4d (PR #12) 검증 사이클에서 4단계 손 가는 비용 실증 → run.sh 자동화

## 안 되면

- powershell.exe 가 access 거부 → Windows 측 flutter PATH 확인 (`powershell.exe -Command 'flutter --version'`)
- 일부 패키지가 /mnt/c 임시 디렉토리에서 path resolution 실패 → flutter pub get 한 번 더
- run.sh 가 첫 실행 시 `flutter pub get` 다운로드 시간 ~30초 추가 (Win 측 .dart_tool 새로 생성)
