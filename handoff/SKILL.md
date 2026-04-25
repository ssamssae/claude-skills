---
name: handoff
description: Mac↔WSL 크로스 디바이스 프롬프트 넘기기. 분석 메시지는 현재 봇으로 reply, **순수 디렉티브 메시지는 상대 봇 챗에 직접 발송**해서 강대종님이 챗 전환 없이 한 챗에서 long-press → copy → paste → send 로 끝낼 수 있게 한다. 진짜 무복붙은 텔레그램 봇 구조상 불가능 (봇끼리 user 매개 없이 못 만남). 이 스킬은 "챗 전환 1회 제거" UX 개선만 한다. 강대종님이 "맥에 시켜 / 맥으로 넘겨 / WSL 로 넘겨 / 윈도우에 시켜 / 다른 기기에 보내 / handoff / /handoff" 라고 하거나, Claude 가 스스로 "이 작업은 상대 기기가 해야 함" 판단 시 이 스킬을 실행.
allowed-tools: mcp__plugin_telegram_telegram__reply, Bash, Read
---

# handoff — 크로스 디바이스 프롬프트 넘기기

강대종님이 두 Claude 세션(Mac=`@MyClaude`, WSL=`@Myclaude2`) 을 운영한다. **자동 전달은 텔레그램 봇 구조상 안 됨** — getUpdates 는 user→bot 메시지만 inbound 로 잡고 bot→user POST 는 폴링에 안 잡힌다 (2026-04-25 검증, server.ts L903 `handleInbound` 참조). 그래서 디렉티브 자동 처리 같은 건 못 한다.

이 스킬이 하는 것: **챗 전환 1회 제거**. 디렉티브를 상대 봇 챗에 직접 발송해서, 강대종님이 그 챗만 열면 directive 가 거기 이미 와있게 한다. 상대 봇 챗 안에서 long-press → copy → paste → send 로 끝.

## 호출 순서

### 1. 분석/근거 메시지 — 현재 봇으로 reply

분석·판단 근거·왜 상대 기기가 해야 하는지·맥락을 평소처럼 답한다. 끝에 한 줄 추가:

> **다음 메시지는 @Myclaude2(또는 @MyClaude) 챗에 이미 도착해 있어요. 그 챗 열어서 long-press → copy → paste 해주세요.**

(만약 peer 토큰 미설정이면 fallback 안내: "다음 reply 메시지가 복붙용이에요" — 같은 챗에 디렉티브 별도 reply.)

### 2. 디렉티브 — 상대 봇 챗에 send.sh 로 직접 발송

```bash
~/.claude/channels/telegram/send.sh --peer 538806975 "<디렉티브 본문>"
```

- chat_id `538806975` 는 강대종님 user_id (양 봇 같은 DM)
- send.sh 는 `--peer` 시 `TELEGRAM_PEER_BOT_TOKEN` 사용 → 상대 봇 챗에 도착
- exit 0 = 도착 OK. 비0 = 토큰 누락 등 → fallback (아래)
- **이 메시지는 상대 Claude 가 자동 처리하지 않음**. 강대종님 수동 paste 가 트리거.

**Fallback (peer 토큰 누락 또는 send.sh 실패):**
디렉티브를 `mcp__plugin_telegram_telegram__reply` 로 **별도 메시지** 발송 (현재 봇 챗에). 강대종님이 챗 전환해서 paste — 옛날 방식.

### 3. 디렉티브 메시지 포맷 규칙

- 인용 박스 (`>`) 사용 금지 — long-press 복사 영역 오염
- 이모지 사용 금지
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

## 향후 진화 옵션 (현재 미구현, 메모용)

옵션 2 — Mac↔WSL SSH + tmux send-keys: WSL Claude 를 약속된 tmux 세션에서 띄우고, Mac 이 SSH 로 send-keys 인젝션. 진짜 무복붙. 비용: SSH 키 양방향 셋업 + tmux 디시플린 + Claude 작업 중 인젝션 충돌 위험.

옵션 3 — 플러그인 fork: `~/.claude/plugins/cache/.../telegram/0.0.6/server.ts` 의 `handleInbound` 에 `reply_to_message?.text` 를 meta 에 실어주는 패치. 사용자가 bot 메시지에 1글자 reply 만 해도 directive 컨텍스트 전달됨. 비용: 플러그인 버전업 시 fork 재적용.

## 관련

- `feedback_mac_directive_separate_message.md` — 별도 메시지 규칙이 나온 2026-04-21 대화 기록
- `feedback_telegram_reply_tool_mandatory.md` — reply 는 MCP 툴 경유 (분석 메시지 한정)
- `feedback_nested_claude_telegram_conflict.md` — 409 발생 조건 (폴링만 충돌, POST 무관)
- `project_ship_pipeline.md` — SSH 자동 브릿지 차단 이력
- `reference_ssh_mac_tools.md` — 키체인 제약 원본
- `~/.claude/channels/telegram/send.sh` — peer 토큰 발송 구현체 (2026-04-25 `--peer` 플래그 추가)
- 2026-04-25 검증 메모: 자동 전달 가설 falsified, 옵션 1 (UX-only) 채택
