---
platform: android
severity: warning
category: build
first_hit: 2026-04-23
hits: 1
source: auto-from-session
---

# macOS Python PermissionError: ~/Downloads 접근 차단

## 증상

`play-upload.py --aab ~/Downloads/<name>-<ver>-<build>.aab` 실행 시 aab 파일을 열지 못하고 `PermissionError: [Errno 1] Operation not permitted` 로 즉시 터짐.

```
File "...googleapiclient/http.py", line 594, in __init__
    self._fd = open(self._filename, "rb")
PermissionError: [Errno 1] Operation not permitted: '/Users/user/Downloads/pomodoro-1.0.0-1.aab'
```

stat/ls 로는 파일이 보이고 권한도 `-rw-r--r--` 로 정상인데, Python (또는 임의 비-GUI 프로세스) 가 open 하려고 하면 OS 가 차단.

## 원인

macOS 14+ 의 **TCC (Transparency, Consent, and Control)** 가 `~/Downloads` 를 **보호된 디렉터리** 로 지정. Finder/Safari 같이 명시적으로 허용된 프로세스는 접근 가능하지만, Terminal 에서 실행한 임의 Python 프로세스는 TCC 권한 부여 필요.

Claude Code 세션에서 돌리는 Python 은 기본적으로 이 권한이 없음. Finder 로 파일을 더블클릭해서 열면 TCC 가 자동 승인 prompt 띄우지만, CLI 스크립트는 silent deny 됨.

## 해결

**Workaround (즉시)**: aab 파일을 샌드박스 대상이 아닌 경로로 복사 후 사용.

```bash
cp ~/Downloads/pomodoro-1.0.0-1.aab /tmp/
python3 play-upload.py --aab /tmp/pomodoro-1.0.0-1.aab ...
```

`/tmp`, `~/apps/*/build/`, `~/.claude/` 등은 TCC 보호 대상 아님.

**Root cause fix**: `play-upload.py` 에 `--aab` 가 `~/Downloads/` 하위면 자동으로 `/tmp` 로 복사 후 사용하도록 fallback 로직 추가.

## 재발 방지 체크리스트

- [ ] aab 산출물을 애초에 `~/Downloads` 대신 `~/apps/<app>/build/dist/` 나 `/tmp` 에 저장 (morning Claude 가 `~/Downloads` 저장한 건 브라우저 다운로드 습관 잔재)
- [ ] `play-upload.py` 가 `~/Downloads` 경로를 받으면 자동 복사+경고 출력 (스크립트 패치 대상)
- [ ] 시스템 설정 → 개인정보 보호 및 보안 → 파일 및 폴더 → Terminal/Python 에 Downloads 폴더 권한 부여 (수동 해결, 재발 방지 위해 권장)
- [ ] Claude Code 세션에서 자동으로 이 권한 prompt 뜨지 않음 — 미리 설정하거나 경로 회피

## 참고

- 같은 이슈: `~/Desktop`, `~/Documents`, `~/Pictures`, `~/Movies` 도 동일 TCC 보호 대상
- 허용 폴더: `/tmp`, `/var/tmp`, `~/.claude/`, `~/Library/Caches/`, `~/apps/*/build/`, 기타 유저 custom 폴더 (대부분)
- 우회 시도 시 `open`, `cat` 도 같이 실패 — Finder 나 이미 권한 받은 앱만 접근 가능
- 관련 Apple 문서: https://support.apple.com/guide/mac-help/control-access-to-files-and-folders-on-mac-mchld5a35146/mac
