---
prevention_deferred: null
---

# flutter 명령 PATH 누락으로 APK 빌드 초기 실패

- **발생 일자:** 2026-04-20 20:29 KST
- **해결 일자:** 2026-04-20 20:31 KST
- **심각도:** medium
- **재발 가능성:** high
- **영향 범위:** Claude Code Bash 도구로 실행되는 모든 Flutter 빌드(한컵·가계부·포모도로 등). `/irun`·`/land`·APK 빌드 스크립트 전반.

## 증상

사용자가 "한컵 apk 보내줘" 요청 → `flutter build apk --release` 백그라운드 실행 → exit 0 으로 끝났는데 APK 가 생성되지 않음. 출력 파일을 열어 보니 `(eval):1: command not found: flutter`.

## 원인

Claude Code 의 Bash 도구는 비대화형 zsh 를 띄우는데, 이 세션은 `~/.zprofile` / `~/.zshrc` 가 로드되지 않아 `/Users/user/fvm/default/bin` 같은 fvm PATH 가 잡히지 않는다. `zsh -i -c 'which flutter'` 도 여전히 not found — fvm 가 `~/.zshenv` 가 아니라 interactive rc 에서만 PATH 를 추가하도록 설정돼 있어, 비대화형 shell 에서는 결코 잡히지 않는 것이 근본 원인이다.

## 조치

- 실제 fvm 바이너리 위치 확인: `/Users/user/fvm/versions/3.41.7/bin/flutter`
- 절대 경로로 재호출: `FLUTTER=/Users/user/fvm/versions/3.41.7/bin/flutter; cd <앱> && $FLUTTER build apk --release`
- 이후 모든 flutter 호출은 절대 경로 또는 `fvm flutter` 로 통일.

## 예방 (Forcing function 우선)

- `/irun`·`/land`·이 세션의 다른 Flutter 스킬에 **flutter 바이너리 resolver 헤더** 를 박는다:
  ```bash
  FLUTTER_BIN="$(command -v flutter 2>/dev/null || ls /Users/user/fvm/versions/*/bin/flutter 2>/dev/null | head -1 || echo flutter)"
  ```
  이후 `$FLUTTER_BIN build apk --release` 식으로 호출.
- 즉시 적용 지점: `~/.claude/skills/irun/SKILL.md`, `~/.claude/skills/land/SKILL.md` (둘 다 현재 `fvm flutter` 로 호출하는데, 비대화형 shell 에서 `fvm` 자체도 못 찾을 수 있으므로 fvm 바이너리도 같은 resolver 적용).
- 추가 안전장치로 `~/.zshenv` 에 fvm 경로를 넣는 방법이 있으나, 전역 환경 변경은 범위가 커서 스킬 레벨 resolver 가 우선.

## 재발 이력

## 관련 링크

- 메모리: 해당 없음 (새 패턴)
- 텔레그램 메시지: id 5336 (첫 빌드 실패 보고), id 5338/5340 (절대 경로 재실행 후 APK 전송)
