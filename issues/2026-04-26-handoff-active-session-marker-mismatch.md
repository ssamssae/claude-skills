---
title: handoff 활성 Claude 세션 false-negative — auto mode 일 때 marker grep 안 잡힘
date: 2026-04-26
status: open
severity: medium
related:
  - 2026-04-26-handoff-claude-main-empty-shell.md  # 같은 detection 함수의 또 다른 false-negative
---

# 발생

2026-04-26 17:30 KST, Mac→WSL 자동 핸드오프 발사 시 SSH ping 단계에서 "활성 Claude 세션 0개" 로 잡혀 발사 안 됨. 실제로는 WSL 데스크탑에 활성 세션 2개 (`claude`, `claude-913`) + claude 프로세스 PID 916 살아있는 상태였음.

# 영향

- 핸드오프 SSH+tmux send-keys METHOD A 자동 인젝션 실패
- handoffs/2026-04-26-1730-mac-wsl-rasp5-to-m1-mini-pivot.md 파일은 git push 됐지만, WSL Claude 세션이 그 사실을 즉시 모름
- 강대종님이 텔레그램으로 "wsl 동기화 한번 해줘" 요청 → "ping 못 보냄, 다음 세션 켤 때 git pull 하면 됨" 으로 fallback 답변. zero-touch 핸드오프 인프라 깨짐
- 강대종님이 "핑 안 간 이유 이슈등록하고 재발방지대책" 요청 → 이 문서

# 원인 (확인됨)

handoff SKILL.md 의 detection 코드:

```bash
peer_session=$(ssh "$peer_user@$peer_host" '
  for s in $(tmux list-sessions -F "#{session_name}" 2>/dev/null); do
    tmux capture-pane -t "$s" -p 2>/dev/null \
      | grep -qE "auto mode \(shift|Bypass Permissions|Claude (Opus|Sonnet|Haiku|Code)" \
      && echo "$s" && break
  done
')
```

이 grep 패턴이 좁다.

| 마커 | 언제 보이는가 | 이번 케이스 결과 |
|---|---|---|
| `auto mode \(shift` | "shift+tab to cycle" 토글 안내가 떠있을 때만 | ❌ 안 보임 (auto mode on 정착 상태) |
| `Bypass Permissions` | bypass 모드 footer 일 때만 | ❌ auto mode 라 안 보임 |
| `Claude (Opus\|Sonnet\|Haiku\|Code)` | header 라인 (UI 위쪽) | ❌ capture-pane 기본 viewport 가 마지막 화면만 잡아서 missed |

**실제 footer 표시**: `⏵⏵ auto mode on · 4 shells · ↓ to manage`

이 문자열 어디에도 위 3개 마커가 없다 → grep 0 hit → 활성 세션 0개로 분류 → 핑 발사 skip.

# 재발 방지 대책

## 즉시 조치 (handoff SKILL.md 패치)

### 1. grep 마커 확장

기존 패턴에 다음을 추가:

```
auto mode (on|\(shift)         # 'auto mode (shift...' OR 'auto mode on'
⏵⏵                              # auto mode footer 의 double-arrow 마커 (BMP outside, 일관)
shells · ↓ to manage           # footer 의 manage 안내 (auto/bypass 둘 다 보임)
```

수정 후 패턴:

```bash
grep -qE "auto mode (on|\(shift)|Bypass Permissions|Claude (Opus|Sonnet|Haiku|Code)|⏵⏵|shells · ↓"
```

### 2. capture-pane viewport 확장

header 의 "Claude X.X" 라인도 잡히게 `-S -200` 옵션 추가:

```bash
tmux capture-pane -t "$s" -p -S -200 2>/dev/null
```

기본 capture 는 현재 viewport 만 잡음. -S 로 history buffer 거슬러 올라가면 header 까지 캡처돼서 fallback marker 도 잡힘.

### 3. fallback layer — process check

marker grep 0 hit 일 때 second pass:

```bash
if [ -z "$peer_session" ]; then
  # claude 프로세스 살아있고 attached tmux 세션 있으면 그걸 사용
  if ssh "$peer_user@$peer_host" 'pgrep -af "^claude " >/dev/null 2>&1'; then
    peer_session=$(ssh "$peer_user@$peer_host" \
      'tmux list-sessions -F "#{session_name}:#{session_attached}" 2>/dev/null \
       | awk -F: "$2==1{print $1; exit}"')
  fi
fi
```

이중 가드 — 시각 마커 + 프로세스/attach 상태 cross-check. 마커가 또 바뀌어도 process/attach layer 가 잡아줌.

## 검증 계획

1. SKILL.md 패치 PR 작성 (claude-skills repo)
2. 검증 시나리오 3종:
   - WSL 에 attached claude 세션 있는 상태에서 detection 동작 → expected: 세션 이름 반환
   - WSL 에 빈 bash tmux 만 있고 claude 프로세스 X → expected: 0
   - WSL 에 claude 프로세스 살아있는데 attach 안 된 상태 → expected: 가장 최근 created 세션 반환 (또는 process check fallback)
3. METHOD A end-to-end smoke 1회 (오늘 PASS 했던 자동 directive 시나리오 재현)

## 장기 대책

- detection 마커가 Claude Code UI 업데이트마다 바뀔 가능성 → handoff/ 안에 별도 `claude-detection.sh` 스크립트로 분리, 마커 변경 시 단일 파일만 수정
- 이번 이슈 + 기존 `claude-main-empty-shell` 이슈 = 같은 family. detection layer 통합 리팩터 기회. 우선순위 medium (긴급 아님, 다음 핸드오프 사이클에서 처리)

# Lessons

- **마커 grep 은 UI 의존성이 있어서 항상 깨질 위험**. UI 가 절대 안 바뀐다고 가정하면 안 됨
- **auto mode / bypass mode / 일반 모드 footer 가 다 다름** — 한 모드 가정 X, 모드 무관 마커("⏵⏵", "shells · ↓") 로 가는 게 안전
- **capture-pane 은 viewport 기본** — header 잡으려면 -S 명시 필수
- **fallback layer 가 검증 단축점** — 마커 grep 한 단계로 끝내지 말고 process/attach 상태 cross-check 한 단계 더 두기
