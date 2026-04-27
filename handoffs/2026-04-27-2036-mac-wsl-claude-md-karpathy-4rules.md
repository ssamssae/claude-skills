---
from: mac
to: wsl
sent_at: 2026-04-27T20:36:00+09:00
status: open
---

🍎 [MAC→WSL HANDOFF] WSL `~/.claude/CLAUDE.md` 에 Karpathy 4룰 섹션 동기화

배경: 강대종님 결정으로 forrestchang/andrej-karpathy-skills 의 4 코딩 행동 룰을 강대종님 본인 CLAUDE.md 에 박기로 함. Mac 본진(이 핸드오프 발신측) 은 방금 박음. ~/.claude/CLAUDE.md 가 git repo 아니라 Mac/WSL 로컬 파일이라 양쪽 따로 박아야 일관성 유지.

작업: WSL 의 `~/.claude/CLAUDE.md` 의 "빠른 원칙" 섹션 바로 다음에, "텔레그램 답변 철칙" 섹션 직전에 아래 섹션 통째로 삽입.

```
## 코딩 행동 룰 (Karpathy 4룰, 2026-04-27 도입)

출처: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills). 자동 모드여도 매 작업마다 적용.

1. **가정 명시 (Think Before Coding)** — 모호하면 멈추고 묻기. 해석 여러 개면 다 surface, 침묵으로 하나 고르지 말 것. 본인 컨텍스트가 stale 일 가능성도 가정 → step 0 git pull (오늘 19:13 stale-on-stale 사고).
2. **단순함 우선 (Simplicity First)** — 요청 외 기능·추상화·"유연성"·불가능 케이스 에러 처리 X. 200줄 → 50줄 가능하면 다시 쓰기. "시니어 엔지니어가 과해 보일까?" self-check.
3. **국소 변경 (Surgical Changes)** — 인접 코드·주석·포맷 손대지 말 것. 안 깨진 거 리팩토링 X. 기존 스타일 따라. 변경된 모든 라인은 사용자 요청과 직접 연결돼야 함.
4. **검증 가능한 목표 (Goal-Driven Execution)** — "되게 만들기" 같은 약한 기준 금지. "X 테스트 PASS" / "Y 화면 렌더링" / "Z 커밋 push" 식 verifiable 한 줄로 작업 시작 전 명시.
```

위 섹션 본문 위 fenced block 안 라인 그대로. 한 줄도 빠뜨리지 말 것.

확인:
- 섹션 위치: "## 빠른 원칙" 끝 직후, "## 텔레그램 답변 철칙 (hard rule)" 시작 전
- 섹션 제목: `## 코딩 행동 룰 (Karpathy 4룰, 2026-04-27 도입)`
- 본문: 출처 링크 1줄 + 4룰 (각 1줄)

저장 후:
1. `cat ~/.claude/CLAUDE.md | grep -c "Karpathy"` 가 2 이상 (제목 + 출처) 인지 확인
2. 결과 텔레그램 reply 1줄: "🪟 WSL ~/.claude/CLAUDE.md 에 Karpathy 4룰 섹션 동기화 완료"

답신 핸드오프 파일 1개 push (handoffs/2026-04-27-XXXX-wsl-mac-claude-md-karpathy-4rules-reply.md, frontmatter reply_to: handoffs/2026-04-27-2036-mac-wsl-claude-md-karpathy-4rules.md, status: done).

금지:
- ~/.claude/CLAUDE.md 의 다른 섹션 손대지 말 것 (룰 3 적용: 인접 코드 손대지 말 것)
- ~/.claude/AGENT.md 또는 메모리에 추가 박지 말 것 — 이 핸드오프는 CLAUDE.md 본체만 동기화
- 새 git repo 만들거나 ~/.claude 를 git init 하지 말 것 — 의도적으로 local 파일

종료 조건: WSL 측 ~/.claude/CLAUDE.md 에 위 4줄짜리 섹션 1개 + 답신 핸드오프 push.
