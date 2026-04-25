---
from: mac
to: wsl
sent_at: 2026-04-25T21:46:00+09:00
status: open
reply_to: handoffs/2026-04-25-2141-mac-wsl-bidir-verify.md
---

[양방향 검증 재시도 — tmux 절대경로]

배경:
직전 핸드오프 (handoffs/2026-04-25-2141-...md) 의 SSH 명령이 Mac 측에서 `zsh:1: command not found: tmux` (exit=127) 로 실패. Mac 비인터랙티브 SSH 셸은 PATH 에 /opt/homebrew/bin 이 없음 (memory `reference_ssh_mac_tools.md` — bun/flutter 절대경로 필수와 동일 함정).

수정 사항:
원격 명령에서 `tmux` 를 절대경로 `/opt/homebrew/bin/tmux` 로 교체.

할일:
정확한 명령 (그대로 사용):
```
ssh user@user-macbookpro-1 "/opt/homebrew/bin/tmux send-keys -t claude-39509 '[WSL HANDOFF] 자동 submit 됐으면 텔레그램으로 WSL→MAC PASS 한 줄만 보고'; sleep 0.5; /opt/homebrew/bin/tmux send-keys -t claude-39509 Enter"
```

기대 동작:
- exit=0
- Mac claude-39509 세션의 Claude 프롬프트에 텍스트 도착 + 자동 submit
- Mac Claude 가 텔레그램으로 "WSL→MAC PASS" 한 줄 답신
- 강대종님이 답신 받으면 양방향 PASS 확정

금지사항:
- 다른 곳 임의 변경 금지 (오늘 마지막 검증, 변형은 다음 trial)
- 추가 핸드오프 파일 생성 금지

종료 조건:
SSH 명령 exit=0 한 줄 텔레그램 보고 → 끝. Mac 답신은 Mac Claude 가 별도로 보냄.
