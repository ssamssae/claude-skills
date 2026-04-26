---
prevention_deferred: null
---

# 복붙 메시지에 라벨/안내 텍스트 섞어 보냄 → PowerShell 명령 깨짐

- **발생 일자:** 2026-04-26 09:46 KST
- **해결 일자:** 2026-04-26 09:48 KST
- **심각도:** medium
- **재발 가능성:** high (이번이 3-4번째)
- **영향 범위:** 텔레그램 reply 워크플로우 전체 (모든 기기)

## 증상
WSL Claude 가 데스크탑 PC 로컬 LLM 부트스트랩 안내 중, PowerShell 한 줄 명령을 별도 메시지로 분리하긴 했는데 그 메시지 안에 `[관리자 PowerShell 창에 그대로 복붙 + 엔터]` 라벨을 함께 포함. 강대종님 폰 long-press copy = 메시지 통째 복사 → 라벨까지 PowerShell 에 붙여넣어져서 syntax error.

## 원인
기존 룰(`feedback_paste_blocks_as_separate_message.md`) 의 line 17 에 "한두 줄 컨텍스트는 OK" 예외 조항이 있었음. Claude 가 작성 시 이 예외에 기대서 라벨/괄호/안내 텍스트를 본능적으로 끼워넣음. 룰 본질("폰 long-press = 메시지 통째 카피") 와 충돌.

## 조치
1. 즉시 깨끗한 명령어만 든 새 reply 보내기 (Telegram msg 2810)
2. feedback 메모리 line 17 강화: "한두 줄 컨텍스트는 OK" → "0줄, 순수 블록만" (2026-04-26 commit)
3. 본 이슈 등록 (claude-skills repo)

## 예방 (Forcing function)
**PreToolUse hook 작성** — `mcp__plugin_telegram_telegram__reply` 호출 직전 text 본문 자동 검사:

- 라인별 분류 휴리스틱:
  - 명령형 라인 = `$`/`&`/`cd`/`Set-`/`Get-`/`Remove-`/`Invoke-`/`curl`/`git`/`sudo`/`python`/`pip`/`npm`/`node`/`flutter`/`adb` 등으로 시작
  - 일반 텍스트 라인 = 한글 포함 또는 5단어+ 영문 안내
  - **명령형 라인 1+ 와 일반 텍스트 라인 1+ 가 같은 메시지에 동시 존재** 시 → block
- block 메시지: `"복붙 블록은 별도 메시지. 명령어만 들어있는 깨끗한 reply 로 분리하세요"`
- fenced ```block``` 도 같은 패턴으로 검사
- 설치 위치: `~/.claude/hooks/telegram-reply-paste-purity.sh` 같은 별도 파일
- 이미 있는 `telegram-reply-check.sh` (Stop hook) 와 짝으로 운영

## 재발 이력
(처음 생성, 비워둠 — 메모리에는 2026-04-25 22:25 sudo pmset, 2026-04-25 11:12 claude plugin install 두 건의 동일 패턴 기록됨)

## 관련 링크
- 메모리: `feedback_paste_blocks_as_separate_message.md`
- 텔레그램: msg 2806 (강대종님 지적), msg 2810 (수정 후 재전송)
- 다음 작업: PreToolUse hook 구현 (별도 PR)
