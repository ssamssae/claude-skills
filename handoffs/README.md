# handoffs/

Mac↔WSL Claude 직통 핸드오프 채널. 긴 directive 본문을 텔레그램 메시지로 복붙하지 않고 git 으로 운반한다.

## 기기 역할 (2026-05-01 보강)

- **Mac 본진 (지휘관)** — directive 발신 / 결과 검토 / main 머지 결정. SoT.
- **WSL (작업자)** — directive 수신 후 wsl/\* 브랜치에서 코드 수정 + `git push origin wsl/<slug>`. main 직접 push 금지. 빌드/배포 일체 금지.
- **Mac mini (빌드/배포 엔진)** — handoffs/ 채널 사용 X. 본진이 SSH 로 직접 트리거(`/submit-app` 등). 결과는 mac-report.sh 운반체로 본진 tmux 'claude' 세션에 자동 paste.

상세: `~/.claude/skills/MACHINE_ROLES.md`, `~/.claude/CLAUDE.md` 지휘관 1명 원칙.

## 흐름

1. 발신측 Claude 가 `handoffs/YYYY-MM-DD-HHMM-{from}-{to}-{slug}.md` 작성 후 push
2. 발신측이 수신측 tmux 안 Claude 프롬프트에 짧은 핑 1줄 입력 (수단은 무관 — 보통 SSH+`tmux send-keys`)
3. 수신측 Claude 가 `git pull && cat handoffs/...md` 으로 본문 읽고 진행
4. 종료 조건 충족 시 텔레그램으로 결과 보고 (WSL→Mac 은 mac-report.sh 도 함께)

## 파일명 규칙

```
YYYY-MM-DD-HHMM-{from}-{to}-{slug}.md
```

- `YYYY-MM-DD-HHMM`: KST 기준 발신 시각
- `from` / `to`: `mac` 또는 `wsl`
- `slug`: 짧은 영문 케밥 케이스 (예: `env-check`, `ssh-trial`, `flag-cleanup`)
- 답신: 같은 base 이름 끝에 `-reply.md` 접미 (예: `2026-04-25-1130-mac-wsl-env-check-reply.md`). frontmatter `reply_to:` 로 원본 파일 경로 명시.

## 본문 스키마

```markdown
---
from: mac
to: wsl
sent_at: 2026-04-25T11:30:00+09:00
status: open  # open | acked | done | cancelled
---

[제목]

목표:
이 핸드오프가 무엇을 달성하려는지 1-3줄.

목표 흐름 (선택):
큰 그림이 필요하면 명시. 단발 작업이면 생략.

할일:
구체적 단계 + 결과 보고 방법. 분기 조건이 있으면 명시 (예: "(1) 일치하면 (2) 진행, 불일치면 (3) 진행").

금지사항:
파괴적/외부영향 액션 명시. 승인 없이 만지면 안 되는 것 나열.

종료 조건:
무엇을 하면 이 핸드오프가 끝나는지. 보고 채널 명시 (텔레그램 reply / handoffs/ 답신 파일 등).
```

## frontmatter 필드

| 필드 | 필수 | 설명 |
|------|------|------|
| `from` | ✓ | `mac` / `wsl` |
| `to` | ✓ | `mac` / `wsl` |
| `sent_at` | ✓ | KST ISO8601 (`+09:00` 명시) |
| `status` | ✓ | `open` 발신 직후 / `acked` 수신측이 받음 / `done` 종료 조건 충족 / `cancelled` 취소 |
| `reply_to` | 선택 | 답신일 때 원본 파일 경로 (`handoffs/...md`) |

## 보존

영구. git history 자체가 핸드오프 로그. 종료 후 파일 삭제 금지.

## 운영 메모

- 본문에 토큰/패스워드/공개키 본문 등 민감정보 절대 금지 (priv repo 라도 leak 위험 있는 정보는 제외)
- 텔레그램에는 짧은 핑 (파일 경로) 만 보내고 본문은 git 로 운반
- 양쪽 기기 모두 `claude-skills` repo 의 `main` 브랜치 sync 필수
