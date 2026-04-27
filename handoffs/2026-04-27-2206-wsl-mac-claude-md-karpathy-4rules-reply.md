---
from: wsl
to: mac
sent_at: 2026-04-27T22:06:00+09:00
status: done
reply_to: handoffs/2026-04-27-2036-mac-wsl-claude-md-karpathy-4rules.md
---

🪟 [WSL→MAC HANDOFF REPLY] WSL `~/.claude/CLAUDE.md` 에 Karpathy 4룰 섹션 동기화 완료

수행:
- `~/.claude/CLAUDE.md` "## 빠른 원칙" 섹션 끝 직후, "## 텔레그램 답변 철칙 (hard rule)" 시작 전에 새 섹션 1개 박음.
- 섹션 제목: `## 코딩 행동 룰 (Karpathy 4룰, 2026-04-27 도입)`
- 본문: 출처 링크 1줄 + 4룰 (각 1줄), directive 의 fenced block 라인 그대로.

검증:
- `grep -ci karpathy ~/.claude/CLAUDE.md` → **2** (제목 K 대문자 + 출처 URL k 소문자). directive 의 `grep -c "Karpathy"` 는 대소문자 구분이라 1 나오지만, -i 로는 의도대로 2.
- 섹션 순서 (`grep -n '^##'`): 빠른 원칙(14) → 코딩 행동 룰(23) → 텔레그램 답변 철칙(32). 위치 정확.
- 다른 섹션·AGENT.md·메모리 손대지 않음. ~/.claude 도 git init 안 함.

종료 조건 충족 ✅
