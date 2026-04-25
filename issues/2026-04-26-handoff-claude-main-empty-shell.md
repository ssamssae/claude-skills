---
date: 2026-04-26
slug: handoff-claude-main-empty-shell
status: resolved
device: mac
---

# /handoff Primary 첫 실전 — claude-main 세션은 살아있는데 안에서 Claude Code 가 안 돌고 있었음

## 증상

- 2026-04-26 00:42 KST. Mac /goodnight step 4.5 가 WSL 한테 `/insta-post 2026-04-25` 핸드오프를 SSH+tmux METHOD A 로 발사.
- 명령: `ssh ssamssae@desktop-i4tr99i-1 "tmux send-keys -t claude-main '/insta-post 2026-04-25'; sleep 0.5; tmux send-keys -t claude-main Enter"` → exit 0.
- 인스타에 카드가 안 올라옴. 강대종님 "왜 안오냐" (텔레그램 msg 7320).

## 진단

WSL 측 capture-pane 마지막 줄:

```
ssamssae@DESKTOP-I4TR99I:~/.claude/skills$ cc
ssamssae@DESKTOP-I4TR99I:~/.claude/skills$ /insta-post 2026-04-25
-bash: /insta-post: No such file or directory
```

`tmux ls` 결과:

```
claude:        1 windows (created Sat Apr 25 22:04:53 2026) (group claude)
claude-69156:  1 windows (created Sat Apr 25 22:04:53 2026) (group claude) (attached)
claude-main:   1 windows (created Sat Apr 25 21:13:05 2026)
```

활성 Claude Code 인스턴스는 `claude-69156` 였음. `claude-main` 은 빈 bash shell.

## 원인

2026-04-25 commit `f4f9cf7` 의 양방향 대칭 셋업 (~/.bashrc, ~/.zshrc 가드) 은 tmux 세션 `claude-main` 만 만들고, **그 안에서 Claude Code 자동 실행은 안 시킴**. 강대종님이 다른 터미널에서 `cc` 를 직접 띄우면 새 세션이 만들어지고 (예: claude-69156), `claude-main` 은 빈 bash 로 남는다. 또는 claude-main 안에서 한 번 `/exit` 하면 동일 상태.

Mac 의 핸드오프 SSH 명령은 `claude-main` 세션 이름을 하드코딩해서 보냈고, 빈 bash 가 받아서 명령어 경로로 해석 → "No such file or directory".

## 해결안

**대안 A (채택)** — 동적 세션 탐색:

송신 전에 SSH 로 상대 tmux 세션 전체를 훑고, 각 세션 capture-pane 에 Claude Code TUI 마커가 있는지 grep 검사. 첫 매치를 타겟. 0개면 텔레그램 fallback 으로 자동 우회.

검사 마커 (안정적 시그니처): `auto mode \(shift|Bypass Permissions|Claude (Opus|Sonnet|Haiku|Code)`. 헤더 또는 푸터 둘 중 한쪽엔 항상 떠있음.

송신측 헬퍼 패턴:

```bash
peer_session=$(ssh "$peer_user@$peer_host" '
  for s in $(tmux list-sessions -F "#{session_name}" 2>/dev/null); do
    tmux capture-pane -t "$s" -p 2>/dev/null \
      | grep -qE "auto mode \(shift|Bypass Permissions|Claude (Opus|Sonnet|Haiku|Code)" \
      && echo "$s" && break
  done
')
if [ -z "$peer_session" ]; then
  # 텔레그램 fallback
else
  ssh "$peer_user@$peer_host" "tmux send-keys -t '$peer_session' '<핑>'; sleep 0.5; tmux send-keys -t '$peer_session' Enter"
fi
```

**고려한 다른 안**:

- 대안 B (claude-main only + 헬스체크): claude-main 만 검사. 강대종님이 다른 세션에서 cc 돌리는 패턴은 못 따라감 → 오늘 케이스 그대로 재현.
- 대안 C (.bashrc 가드 강화): 세션 만들 때 안에서 cc 자동 실행. 이미 다른 곳에서 cc 돌고 있으면 중복 띄움. 강대종님과 합의 없이 가드 강제 변경 금지.

A 가 본질적 정답. C 는 "claude-main 을 정해진 자리로 쓰자" 의 컨벤션 강화안인데, 별건. 양립 가능하지만 둘 중 하나만 가야 한다면 A.

## 적용

- `~/.claude/skills/handoff/SKILL.md` §2 Primary 갱신 — claude-main 고정 → 동적 탐색 헬퍼 패턴.
- "알려진 한계" 항목에 오늘 케이스 박힘.
- WSL 측 `~/.bashrc` 는 안 건드림 (강대종님과 합의 후 별도 패치).

## 타임라인

- 2026-04-25 21:13:05 KST — claude-main 세션 생성 (~/.bashrc 가드).
- 2026-04-25 22:04:53 KST — claude / claude-69156 세션 추가 생성 (강대종님이 cc 직접 띄움).
- 2026-04-26 00:42 KST — Mac 송신 ssh+send-keys, claude-main 의 빈 bash 가 받음 → "command not found".
- 2026-04-26 00:43 KST — 강대종님 "핸드오프 안가는데?" 텔레그램.
- 2026-04-26 00:48 KST — WSL 진단 + 대안 A 추천 + Mac 한테 SKILL.md 갱신 핸드오프.
- 2026-04-26 00:55 KST — Mac 이 SKILL.md + issue 로그 적용 + commit + push.
- 인스타는 WSL 이 수동으로 `/insta-post 2026-04-25` 호출해서 마무리됐음 → https://www.instagram.com/p/DXj2_hoDoDM/

## 후속

- 다음 /goodnight 부터 새 동적 탐색 경로 사용.
- 강대종님과 .bashrc 가드 강화(대안 C) 별건 검토 — claude-main 을 항상 활성 세션으로 유지하는 컨벤션 도입할지.
