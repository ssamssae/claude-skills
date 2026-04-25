---
from: mac
to: wsl
sent_at: 2026-04-25T21:41:00+09:00
status: open
---

[양방향 핸드오프 end-to-end 검증]

목표:
오늘 정착한 새 흐름 (handoffs/ + SSH+send-keys + sleep 분리) 의 WSL→Mac 방향 종단간 검증. 양방향 무손이면 강대종님 손 0번 확정.

할일:
이 directive 를 받자마자 Mac 한테 SSH+send-keys 핑 1발만 쏴라. 내용은 "Mac Claude 가 자동 submit 후 텔레그램으로 'WSL→MAC PASS' 한 줄만 보고" 하라는 짧은 트리거.

명령 형태 (그대로 사용):
```
ssh user@user-macbookpro-1 "tmux send-keys -t claude-39509 '[WSL HANDOFF] 자동 submit 됐으면 텔레그램으로 WSL→MAC PASS 한 줄만 보고'; sleep 0.5; tmux send-keys -t claude-39509 Enter"
```

매개변수 메모:
- Mac SSH 호스트: `user-macbookpro-1` (Tailscale, IPv4 100.74.85.37)
- Mac SSH 사용자: `user`
- Mac tmux 세션: `claude-39509` (Mac Claude 가 지금 들어있는 attached 세션. PID suffix 임시명)
- WSL→Mac 키 인증: WSL ed25519 코멘트 "windows-wsl" 이 Mac authorized_keys 에 등록됨, 비번 없이 통과

직후 WSL 이 할 일은 없음. 텔레그램 reply 자체도 Mac 이 보냄. Mac 답신이 오면 양방향 PASS.

금지사항:
- ssh 명령 변형 금지 — sleep 분리 형태 그대로 (변형은 다음 trial 에서)
- 추가 핸드오프 파일 생성 금지 (검증은 Mac 텔레그램 답신으로 완료)
- Mac 시스템 점검·sshd 설정 변경 금지 (이미 완료)

종료 조건:
SSH 명령 exit=0 보고 한 줄 텔레그램으로 강대종님께. 그 후 Mac 답신 오는지는 강대종님이 확인 (Mac 답신은 Mac Claude 가 텔레그램으로 보냄, 별도 reply).
