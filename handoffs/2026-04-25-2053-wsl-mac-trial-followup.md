---
from: wsl
to: mac
sent_at: 2026-04-25T20:53:00+09:00
status: open
---

[트라이얼 후속]

목표:
직전 SSH+send-keys 트라이얼(handoffs/2026-04-25-2046-mac-wsl-ssh-trial.md, WSL 텔레그램 보고 message_id 2645) 결과 받았으니 후속 4개 — 핑 전달 경로 확정 / WSL→Mac 역방향 점검 / handoff/SKILL.md 정리 / WSL 세션명 마이그레이션 결정.

할일:

(1) 트라이얼 핑 전달 경로 확정 — 직전 핑 본문 "[MAC HANDOFF] git pull 후 handoffs/2026-04-25-2046-mac-wsl-ssh-trial.md 읽고 본문 directive 따라 진행" 이 WSL Claude 프롬프트에 들어왔다. 이게 Mac 이 SSH+tmux send-keys 로 자동 인젝션한 건지, 강대종님이 직접 WSL CLI 에 타이핑한 건지 강대종님께 명시 보고. 전자면 Mac→WSL 자동 핑 end-to-end PASS, 후자면 WSL 수신측만 PASS 이고 SSH 자동 인젝션은 미검증 — 다음 셋업 작업 필요.

(2) WSL→Mac 역방향 SSH 점검 — WSL 에 ed25519 키쌍 있음 (코멘트 "windows-wsl"). Mac 의 ~/.ssh/authorized_keys 에 마지막 필드(코멘트) 가 "windows-wsl" 인 키가 등록돼 있는지 grep 으로 확인. Mac sshd 가 active 인지 (Mac 은 시스템 설정 > 일반 > 공유 > 원격 로그인 또는 sudo systemsetup -getremotelogin). Mac Tailscale 호스트명 + IPv4 (tailscale ip -4 + tailscale status 자기 줄). 이 3개만 사실 보고. WSL→Mac SSH 가 보안/필요성 측면에서 강대종님이 원하지 않을 수도 있으니 점검만 하고 임의로 authorized_keys 추가 또는 sshd 활성화 절대 금지.

(3) handoff/SKILL.md 정리 — 현재 SKILL.md L102~106 가 "옵션 2 — SSH+tmux send-keys" 를 "현재 미구현, 메모용" 으로 표기. 트라이얼 PASS (최소 WSL 수신측) 했으니 메인 플로우로 승격. 구조 제안: Primary = handoffs/ git 운반 + ping (SSH+send-keys 또는 수동 paste 둘 다 허용) / Secondary = peer-bot send.sh --peer (긴 directive 인라인 필요할 때) / Fallback = 현재 봇 reply (peer 토큰 누락). 이미 push 된 handoffs/README.md 와 일관되게. 변경 초안 git diff 만 강대종님께 보여주고 승인 받은 후에 commit+push.

(4) WSL 세션명 claude-main 마이그레이션 옵션 강대종님께 제안 — 현재 WSL Claude 는 claude-60120 (PID suffix) 세션. send-keys 타겟으로 매번 tmux ls 검색 부담. 옵션 A: 강대종님이 WSL 다음 부팅/재시작 시점에 tmux new -s claude-main 후 거기서 claude 실행 (수동, 1회). 옵션 B: WSL 부팅 자동화 — ~/.bashrc 또는 systemd user service 로 claude-main 세션 자동 생성 (자동, 셋업 후 영구). 옵션 비교만 텔레그램으로 보내고 강대종님 결정 받기. WSL 측 변경은 Mac 이 직접 못 함 — 결정 받고 강대종님이 WSL 에서 실행하거나 다음 WSL handoff 로 위임.

금지사항:
- Mac authorized_keys 임의 추가/제거 (강대종님 승인 필수)
- Mac sshd 임의 활성화 (강대종님 승인 필수)
- handoff/SKILL.md 사전 승인 없이 commit+push
- 한 번에 4개 다 끝내려고 묶어서 보고 — (1)+(2) 사실 보고는 묶어도 되지만 (3)/(4) 변경 수반은 각각 따로 승인 받고 진행

종료 조건:
(1)+(2) 사실 보고 텔레그램 reply 1통 → (3) SKILL.md 초안 diff 보고 1통 → (4) 세션 마이그레이션 옵션 비교 보고 1통 = 최대 3통. 각 통마다 강대종님 결정 받고 다음 단계.
