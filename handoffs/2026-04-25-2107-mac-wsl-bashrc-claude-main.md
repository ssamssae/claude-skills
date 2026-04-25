---
from: mac
to: wsl
sent_at: 2026-04-25T21:07:00+09:00
status: open
---

[B1 — .bashrc 가드로 claude-main 세션 자동 유지]

배경:
강대종님이 옵션 B1 선택 (4개 옵션 중 .bashrc 한 줄 가드, 컴 켤 때 claude-main 자동 생성). Mac↔WSL 핸드오프 시 매번 세션 이름 동적 탐색 부담 제거하려는 목적.

목표:
~/.bashrc 끝에 idempotent 가드 한 줄 추가해서, 새 셸 열릴 때마다 claude-main detached tmux 세션이 살아있도록 보장. 이미 있으면 건드리지 않음.

할일:
1. ~/.bashrc 끝에 아래 두 줄 추가 (주석 + 가드):
```
# Mac↔WSL 핸드오프용: claude-main tmux 세션 자동 유지
tmux has-session -t claude-main 2>/dev/null || tmux new -d -s claude-main
```
2. 추가 후 `tail -3 ~/.bashrc` 결과 보여주기 (라인이 정확히 들어갔는지 확인용).
3. 즉시 `source ~/.bashrc` 또는 `tmux new -d -s claude-main` 한 번 실행해서 claude-main 세션이 지금 시점에 존재하게 만들기.
4. `tmux ls` 로 claude-main 이 목록에 있는지 확인.
5. 텔레그램 reply 1통으로 보고:
   - .bashrc 끝 3줄 그대로
   - tmux ls 결과 (claude-main 항목 포함된 줄)
   - "B1 셋업 완료" 한 줄

주의 — 강대종님 워크플로우 안내 (메시지에 함께 포함):
- claude-main 은 detached 세션으로 만들어졌지만 아직 그 안에 Claude 가 돌고 있지 않음.
- 다음에 새 Claude 시작할 때: `tmux attach -t claude-main` → 그 안에서 `claude` 실행. 그 시점부터 Mac→WSL 핑이 자연스럽게 claude-main 으로 도착.
- 지금 돌아가는 claude-60120 세션은 그대로 둬도 됨. 자연 종료될 때까지.

금지사항:
- claude-60120 (현재 본인 세션) kill / rename / 다른 세션으로 이동 절대 금지
- ~/.bashrc 의 다른 부분 수정 금지 (마지막에 추가만)
- 추가 환경 변경 (apt install, systemd 활성화 등) 금지

종료 조건:
위 5번 텔레그램 reply 1통 보내면 끝. 다음 단계는 강대종님 결정.
