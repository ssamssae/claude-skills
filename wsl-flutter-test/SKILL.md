---
name: wsl-flutter-test
description: WSL bash 에서 Flutter 앱 테스트 호출 시 cmd.exe pushd UNC cwd 거부 함정을 우회하는 4단계 절차. 트리거 "/wsl-flutter-test", "WSL 에서 flutter test", "WSL 에서 lotto/단어요/한줄일기 테스트".
---

# /wsl-flutter-test — WSL Flutter test 우회 절차

## 함정 정리

WSL bash 에서 `flutter test` 를 호출하려면 다음 3가지 함정을 차례로 만난다:

1. **WSL bash → /mnt/c/src/flutter 직접 호출 X** — Windows 측 flutter 바이너리는 CRLF + Windows ELF 라 `exec format error`.
2. **powershell.exe Set-Location 'C:\path' + flutter test** — PowerShell 자체는 cwd 받는데 .bat 진입점 내부 cmd 가 UNC cwd 거부.
3. **/mnt/c 경로 cmd.exe pushd** — UNC 경로 거부 (`CMD does not support UNC paths as current directories`).

## 우회 4단계

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

## 안 되면

- powershell.exe 가 access 거부 → Windows 측 flutter PATH 확인 (`powershell.exe -Command 'flutter --version'`)
- 일부 패키지가 /mnt/c 임시 디렉토리에서 path resolution 실패 → flutter pub get 한 번 더
