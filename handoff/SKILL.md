---
name: handoff
description: Mac↔WSL 크로스 디바이스 프롬프트 넘기기. 2026-04-25 부터 Primary 채널은 SSH+tmux send-keys METHOD A 무복붙(zero-touch) — 강대종님 손 0번. 텔레그램 peer-bot 발송과 fallback reply 는 보조. 강대종님이 "맥에 시켜 / 맥으로 넘겨 / WSL 로 넘겨 / 윈도우에 시켜 / 다른 기기에 보내 / handoff / /handoff / 쏴줘 / 맥도 알게 / 맥에 알려 / 맥에 보내 / WSL 도 알게 / 양방향 / 양쪽 다 알게 / 둘 다 알게 / 둘 다 인지 / 상대도 알아야 / 저쪽 Claude 한테 / 다른 Claude 한테" 같은 표현을 쓰거나, Claude 가 스스로 "이 작업·정보는 상대 기기 Claude 도 알아야 함" 판단 시 즉시 이 스킬을 실행. **함정**: "복붙용으로 보내줘 / 복사해서 줘" 식으로 reply 복붙 모드를 명시 요청한 게 아닌 한, "쏴줘 / 보내줘 / 알려" 는 모두 METHOD A 무복붙으로 해석 — "별도 reply 로 복붙해주세요" 답변으로 빠지면 어제 만든 zero-touch 인프라를 무시하는 셈.
allowed-tools: mcp__plugin_telegram_telegram__reply, Bash, Read
---

# handoff — 크로스 디바이스 프롬프트 넘기기

강대종님이 두 Claude 세션(Mac=`@MyClaude`, WSL=`@Myclaude2`) 을 운영한다. 디렉티브를 상대 기기로 넘기는 채널은 **3단 사다리**:

1. **Primary — `handoffs/` + SSH+send-keys ping** (2026-04-25 정착): directive 본문은 priv repo `ssamssae/claude-skills/handoffs/` 파일에 git 으로 운반, 짧은 1줄 핑은 SSH 로 상대 tmux 안 Claude 프롬프트에 자동 인젝션. 강대종님 손 0번 (단 text 와 Enter 를 `sleep 0.5` 끼워 별도 send-keys 로 분리 발사 필수 — bracketed paste 우회).
2. **Secondary — peer-bot `send.sh --peer`**: 텔레그램 상대 봇 챗에 directive 직접 POST. 짧은 인라인 directive 또는 `handoffs/` 영구 기록 불필요할 때.
3. **Fallback — 현재 봇 reply 별도 메시지**: peer 토큰 누락 또는 SSH 다운 시. 강대종님이 챗 전환 + long-press → paste.

텔레그램 봇끼리 자동 메시지 전달은 구조상 막혀있다 (getUpdates 는 user→bot 만 inbound 로 잡고 bot→user POST 는 폴링에 안 잡힘, 2026-04-25 검증, server.ts L903 `handleInbound`). 그래서 Secondary/Fallback 은 강대종님 수동 paste 가 트리거. Primary 만 진짜 무복붙.

## 호출 순서

### 1. 분석/근거 메시지 — 현재 봇으로 reply

분석·판단 근거·왜 상대 기기가 해야 하는지·맥락을 평소처럼 답한다. 끝에 한 줄 추가:

> **다음 메시지는 @Myclaude2(또는 @MyClaude) 챗에 이미 도착해 있어요. 그 챗 열어서 long-press → copy → paste 해주세요.**

(만약 peer 토큰 미설정이면 fallback 안내: "다음 reply 메시지가 복붙용이에요" — 같은 챗에 디렉티브 별도 reply.)

### 2. 디렉티브 운반 — 3단 사다리

**Primary — `handoffs/` git 운반 + SSH+send-keys ping**

1. `ssamssae/claude-skills/handoffs/YYYY-MM-DD-HHMM-{from}-{to}-{slug}.md` 작성 + commit + push. 본문 스키마는 `handoffs/README.md` (frontmatter from/to/sent_at/status, 본문 5섹션 컨텍스트/목표흐름/할일/금지/종료조건).
2. **활성 Claude 세션 동적 탐색** (2026-04-26 추가 — 이슈 `issues/2026-04-26-handoff-claude-main-empty-shell.md` 후 도입). `claude-main` 세션이 살아있어도 안에서 Claude Code 가 안 돌고 빈 bash 일 수 있음 (강대종님이 다른 터미널에서 `cc` 띄우면 새 세션이 활성, claude-main 은 빈 셸로 잔존). 송신 전 SSH 로 모든 tmux 세션 capture-pane 을 grep 해 Claude Code TUI 마커가 보이는 세션을 잡는다:

```bash
peer_session=$(ssh "$peer_user@$peer_host" '
  for s in $(tmux list-sessions -F "#{session_name}" 2>/dev/null); do
    tmux capture-pane -t "$s" -p 2>/dev/null \
      | grep -qE "auto mode \(shift|Bypass Permissions|Claude (Opus|Sonnet|Haiku|Code)" \
      && echo "$s" && break
  done
')
if [ -z "$peer_session" ]; then
  # 활성 Claude Code 세션 0개 → 텔레그램 Fallback 으로 우회 (강대종님 수동 paste).
  exit 1
fi
```

검사 마커: `auto mode \(shift` (footer mode 라인) | `Bypass Permissions` (footer) | `Claude (Opus|Sonnet|Haiku|Code)` (header). 셋 중 하나는 항상 떠있음.

3. SSH 로 그 세션 안 Claude 프롬프트에 짧은 1줄 핑 (sender 이모지 prefix 필수):

```bash
# Mac→WSL (보낸 기기 = Mac = 🍎)
ssh ssamssae@desktop-i4tr99i-1 "tmux send-keys -t '$peer_session' '🍎 [MAC→WSL HANDOFF] git pull 후 handoffs/YYYY-MM-DD-HHMM-...md 읽고 본문 directive 따라 진행'; sleep 0.5; tmux send-keys -t '$peer_session' Enter"

# WSL→Mac (보낸 기기 = WSL = 🪟). Mac 계정명 user 주의 (ssamssae 아님), tmux 절대경로 필수.
ssh user@user-macbookpro-1 "/opt/homebrew/bin/tmux send-keys -t '$peer_session' '🪟 [WSL→MAC HANDOFF] git pull 후 handoffs/YYYY-MM-DD-HHMM-...md 읽고 본문 directive 따라 진행'; sleep 0.5; /opt/homebrew/bin/tmux send-keys -t '$peer_session' Enter"
```

- **핑 첫 글자는 보낸 기기 이모지 필수** (WSL=🪟, Mac=🍎). 강대종님이 본인이 친 게 아님을 즉시 식별. 이 이모지는 §3 의 "이모지 금지" 규칙 예외 — §3 는 handoffs/ 파일 안 directive 본문 한정, 핑은 ephemeral chat injection 이라 별도.
- text 와 Enter 를 **별도 send-keys 호출**로 분리 + 사이에 `sleep 0.5` (2026-04-25 검증 완료, METHOD A PASS).
- 한 burst 로 보내면 (`'text' Enter` 또는 `'text' S-Enter`) 터미널이 통째로 bracketed paste 마커 (`\e[200~...\e[201~`) 로 감싸서, 안의 Enter 가 paste 콘텐츠 (= 줄바꿈) 로 흡수돼 submit 트리거 안 됨.
- sleep 끼우면 paste 종료 후 Enter 가 별도 keystroke 으로 도착해서 submit 됨.
- Mac→WSL: peer-user=`ssamssae`, peer-host=`desktop-i4tr99i-1` (Tailscale linux 노드 — windows 노드 `desktop-i4tr99i` 와 헷갈리지 말 것). 세션은 동적 탐색 (claude-main / claude / claude-NNNNN 등 어디든 활성 인스턴스).
- WSL→Mac: peer-user=`user` (macOS 계정명. Apple ID 표시이름인 ssamssae 아님 — 2026-04-25 검증), peer-host=`user-macbookpro-1`, IPv4 `100.74.85.37`, Mac sshd 활성·`authorized_keys` 에 WSL 키 "windows-wsl" 등록됨. 세션은 동적 탐색.
- WSL→Mac 방향 PATH 함정: Mac 비인터랙티브 SSH 셸은 `~/.zshrc` 안 로드 → tmux/grep 다 절대경로(`/opt/homebrew/bin/tmux`, `/usr/bin/grep`) 또는 `bash -lc 'tmux ...'` 로 인터랙티브 셸 강제.
- exit 0 + Claude 답변 도착 = end-to-end PASS. 핑 자체는 영구 기록 불필요 (handoffs/ 파일이 진짜 directive 운반체).

**Secondary — peer-bot `send.sh --peer` (짧은 인라인 directive)**

```bash
# WSL→Mac 방향 (보낸 기기 = WSL = 🪟)
~/.claude/channels/telegram/send.sh --peer 538806975 "🪟 [한 줄 제목]\n\n<본문>"

# Mac→WSL 방향 (보낸 기기 = Mac = 🍎)
~/.claude/channels/telegram/send.sh --peer 538806975 "🍎 [한 줄 제목]\n\n<본문>"
```

- **본문 첫 글자는 보낸 기기 이모지 필수** (WSL=🪟, Mac=🍎). Primary 핑 규칙과 동일 적용 — 강대종님이 받은 메시지가 본인 입력 아님 즉시 식별.
- handoffs/ 영구 기록 불필요한 짧은 directive (예: "PR #123 머지해", "포트 3000 죽여").
- chat_id `538806975` 는 강대종님 user_id (양 봇 같은 DM).
- send.sh `--peer` 시 `TELEGRAM_PEER_BOT_TOKEN` 사용 → 상대 봇 챗에 도착. 강대종님 수동 paste 가 트리거 (자동 처리 안 됨).

**Fallback — 현재 봇 reply 별도 메시지 (peer 토큰 누락 또는 SSH 다운)**

디렉티브를 `mcp__plugin_telegram_telegram__reply` 로 별도 메시지 발송 (현재 봇 챗에). 강대종님이 챗 전환해서 paste — 옛날 방식. **본문 첫 글자 sender 이모지(🪟/🍎)** Secondary 와 동일하게 필수.

### 3. 디렉티브 메시지 포맷 규칙

(handoffs/ 파일 본문 + secondary peer-bot Telegram directive 본문 + fallback reply directive 본문 모두 적용. **단 sender 이모지 첫 글자(🪟/🍎)는 §2 의 별도 규칙으로 모든 directive 메시지에 필수** — handoffs/ 파일 frontmatter 직후 본문 시작점에도, peer-bot 발송 본문 첫 글자에도, fallback reply 본문 첫 글자에도 동일 적용.)

- 인용 박스 (`>`) 사용 금지 — long-press 복사 영역 오염
- 이모지 사용 금지 (sender 이모지 첫 글자는 예외 — 핑/handoffs/secondary/fallback 전부)
- "다음은 디렉티브입니다" 류 프리픽스 금지 — 상대 Claude 가 명령 일부로 오해
- 코드 펜스 (```) 금지 — 동일 이유
- **자족적 (self-contained)**. 상대 Claude 가 새 세션 첫 입력으로 가정. 컨텍스트·repo URL·파일경로·제약·금지사항 전부 인라인. "아까 말한 그거" 금지
- **단일 메시지**. 4096자 초과 시 Gist/repo commit 후 URL 만 디렉티브에 포함

### 4. 여러 디렉티브는 각각 별도 send.sh 호출

독립된 디렉티브 2개 이상이면 send.sh 호출당 한 번씩 분리. 한 본문에 1/2/3 번호로 묶지 말 것 (long-press 는 메시지 단위).

## 전송 예

### 잘된 예 (peer 챗 발송 모드)

[reply 툴 — 분석]
"한줄일기는 toss-tone 폴리싱 끝났고, 다음 사이클은 감성 톤 전환입니다. docs/DESIGN_AUDIT_2026-04-22.md 에 prep 끝냈어요. 다음 메시지가 @Myclaude2 챗에 와있으니 거기 열어서 long-press → copy → paste 해주세요."

[Bash — send.sh --peer 538806975 "..."]
본문: "hanjul 디자인 업스케일 사이클 시작. cd ~/apps/hanjul && git pull 해서 docs/DESIGN_AUDIT_2026-04-22.md 읽은 다음, ~/design-lab/hanjul/ 폴더 만들어서 ZeroZ-lab/cc-design + bluzir/claude-code-design 을 -s project 스코프로 설치. 오디트 문서를 첫 컨텍스트로 넣고 A안(ZeroZ) 2개 + B안(bluzir) 2개 시안 HTML 로 뽑아줘. 제약: Pretendard 유지, Toss blue(#3182F6) CTA 유지, asset 300KB 이하, Flutter 이식 가능 수준."

### 잘못된 예 ❌ — 디렉티브가 분석 메시지 안에 인용 박스로 끼어 있음

reply 1: "분석 결과 이건 Mac 이 해야 합니다. 아래 내용을 @MyClaude 에 보내주세요:
> hanjul 디자인 시작. cd ~/apps/hanjul...
이거 붙여주시면 됩니다."

→ 폰 long-press 시 인용 박스만 따로 복사 어려움.

## 기기별 동작

| 출발 기기 | peer 봇 (디렉티브 도착지) | peer 토큰 키 | chat_id |
|-----------|---------|---------|---------|
| Mac (@MyClaude 세션) | @Myclaude2 | `TELEGRAM_PEER_BOT_TOKEN` | 538806975 |
| WSL (@Myclaude2 세션) | @MyClaude | `TELEGRAM_PEER_BOT_TOKEN` | 538806975 |

`.env` 위치: 양 기기 모두 `~/.claude/channels/telegram/.env` (mode 600, git 비추적).

각 봇은 **자기 호스트에서만 폴링**되므로 sendMessage POST 충돌(409)은 없음 (관련: `feedback_nested_claude_telegram_conflict.md` — 409 는 같은 토큰을 두 곳에서 폴링했을 때만).

## 왜 자동 전달이 아닌가 (2026-04-25 검증)

- Mac 이 @Myclaude2 토큰으로 sendMessage POST → @Myclaude2 챗에 메시지 도착 (강대종님 폰에선 보임)
- 그러나 그 메시지는 **bot → user outbound** 라서 @Myclaude2 의 getUpdates 폴링에 안 잡힘
- WSL Claude 는 자기 봇의 inbound 만 보므로 우리 POST 메시지를 못 봄 → 자동 처리 불가
- 진짜 자동화는 (a) Mac→WSL SSH + tmux send-keys, (b) 텔레그램 플러그인 fork (reply_to_text 노출), (c) Telegram userbot (MTProto) 셋 중 하나 필요. 비용/복잡도 vs 효과 안 맞아 채택 안 함

## 언제 자발적으로 실행하나

강대종님이 명시적 키워드 없어도 아래 상황엔 Claude 가 스스로 이 스킬 실행:

- 현재 세션에서 못 하는 작업이 상대 기기에 있음 (Mac=iOS 빌드·키체인·App Store, WSL=Android 빌드·adb)
- 상대 세션의 진행 중 작업의 후속 단계 필요
- 강대종님이 기기 옮겨가는 흐름에서 현재 세션이 막다른 길

## 실패 모드 / 주의

- **peer 토큰 누락**: send.sh 가 `TELEGRAM_PEER_BOT_TOKEN empty` 로 비0 종료 → 즉시 fallback (현재 봇 reply, 강대종님 챗 전환 + paste)
- **상대 Claude 세션 죽어있음**: 상관없음. 어차피 강대종님 수동 paste 가 트리거. 단, paste 전에 상대 세션 살아있는지 확인 필요
- **민감 정보 금지**: 디렉티브는 사실상 public 수준 (텔레그램 검색 캐시). API 키·비번·세션 토큰 절대 인라인 금지. "env 에서 읽어" 로 대체
- **메시지 길이 4096자 초과**: 분할 금지. Gist/repo commit 후 URL 만 디렉티브에 포함
- **handoff 의 handoff 금지**: 상대 Claude 가 받자마자 또 다른 기기로 handoff 던지는 무한루프 방지 — 디렉티브에 "이건 너 기기에서 끝내" 명시

## 향후 진화 옵션

옵션 — 플러그인 fork: `~/.claude/plugins/cache/.../telegram/0.0.6/server.ts` 의 `handleInbound` 에 `reply_to_message?.text` 를 meta 에 실어주는 패치. 사용자가 bot 메시지에 1글자 reply 만 해도 directive 컨텍스트 전달됨. 비용: 플러그인 버전업 시 fork 재적용. (Primary 정착 후 우선순위 낮음.)

## 알려진 한계

- Primary 흐름은 Claude Code 가 핑 도착 시점에 mid-task 인 경우 핑 본문이 user input 으로 끼어들 수 있음. 짧은 1줄(파일 경로 핑) 이라 본문 자체는 안 깨지지만, 세션 컨텍스트가 흐려질 수 있음. 발신측은 가능하면 수신측이 idle 일 때 핑.
- **claude-main 빈 셸 함정 (2026-04-26 검증, issues/2026-04-26-handoff-claude-main-empty-shell.md)**: ~/.bashrc / ~/.zshrc 가드는 `claude-main` 세션을 만들 뿐 안에서 cc 자동 실행은 안 시킴. 강대종님이 다른 터미널에서 cc 띄우면 새 세션 (claude-NNNNN) 이 활성, claude-main 은 빈 bash 로 잔존. 송신측이 claude-main 하드코딩하면 빈 셸이 받아 "command not found". → §2 Primary 의 동적 세션 탐색 패턴 필수 사용.
- tmux send-keys 의 `Enter` 또는 `S-Enter` 를 텍스트와 한 burst 로 보내면 Claude Code 가 submit 트리거 안 함. 원인: 빠른 burst 가 통째로 bracketed paste 마커 (`\e[200~ ... \e[201~`) 안에 감싸져서 안의 Enter/S-Enter 도 paste 콘텐츠 (= 줄바꿈) 로 흡수됨. 직접 손가락 Enter 는 paste 마커 밖에서 와서 submit 됨.
- **정답 (2026-04-25 검증 완료, METHOD A PASS, 양방향)**: 텍스트 send-keys → `sleep 0.5` → Enter send-keys (별도 호출) 로 분리 발사. sleep 동안 paste 모드 종료 → Enter 가 진짜 keystroke 으로 도착 → submit. 명령 형태는 §2 Primary 참조.
- **WSL→Mac 방향 PATH 함정**: Mac 비인터랙티브 SSH 셸은 `~/.zshrc` 안 로드해서 `/opt/homebrew/bin` PATH 빠짐 → `tmux: command not found` (exit=127). WSL→Mac SSH 명령에서는 `tmux` 를 `/opt/homebrew/bin/tmux` 절대경로로 사용 (memory `reference_ssh_mac_tools.md` 와 동일 함정). Mac→WSL 방향은 WSL 셸이 PATH 정상이라 영향 없음.

## 관련

- `feedback_mac_directive_separate_message.md` — 별도 메시지 규칙이 나온 2026-04-21 대화 기록
- `feedback_telegram_reply_tool_mandatory.md` — reply 는 MCP 툴 경유 (분석 메시지 한정)
- `feedback_nested_claude_telegram_conflict.md` — 409 발생 조건 (폴링만 충돌, POST 무관)
- `project_ship_pipeline.md` — SSH 자동 브릿지 차단 이력
- `reference_ssh_mac_tools.md` — 키체인 제약 원본
- `~/.claude/channels/telegram/send.sh` — peer 토큰 발송 구현체 (2026-04-25 `--peer` 플래그 추가)
- 2026-04-25 검증 메모: 자동 전달 가설 falsified, 옵션 1 (UX-only) 채택
