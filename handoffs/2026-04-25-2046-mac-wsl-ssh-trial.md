---
from: mac
to: wsl
sent_at: 2026-04-25T20:46:00+09:00
status: open
---

[SSH+send-keys 트라이얼]

목표:
Mac→WSL 핸드오프 새 흐름 (priv repo handoffs/ + SSH+send-keys 핑) 의 종단간(end-to-end) 작동 검증. 이 파일을 WSL Claude 가 읽고 텔레그램에 한 메시지 답하면 트라이얼 성공.

할일:
1. 이 파일을 받았다는 사실 자체가 SSH+send-keys 핑이 도착한 증거. 추가 작업 없음.
2. 텔레그램 reply 한 메시지로 강대종님께 보고:
   - "TRIAL OK"
   - 받은 시각 (KST)
   - 핑이 프롬프트에 들어온 형태 그대로 한 줄 (Mac 이 어떻게 입력했는지 검증용)
   - 본인 tmux 세션명 (claude-60120 가 맞는지 재확인)

금지사항:
- handoffs/ 안에 새 파일 만들지 말 것 (이번엔 답신 파일 없이 텔레그램으로만)
- claude-60120 세션 kill / rename / 다른 세션으로 이동 금지
- claude-skills repo 에 새 commit 만들지 말 것 (read-only)

종료 조건:
텔레그램 reply 1통 보내면 끝. Mac 이 받으면 트라이얼 PASS 판정 → 다음 단계 (claude-main 이전 + handoff 스킬 SKILL.md 업데이트) 진행.
