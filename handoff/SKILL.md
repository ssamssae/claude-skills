---
name: handoff
description: Mac↔WSL 크로스 디바이스 프롬프트 넘기기. 분석 메시지는 현재 봇으로 reply, "상대 Claude 가 그대로 받아 실행할 순수 디렉티브"는 **상대 봇 토큰으로 직접 POST** 해서 자동 전달. 강대종님이 폰에서 long-press → copy → paste 안 해도 되는 무복붙 플로우. 강대종님이 "맥에 시켜 / 맥으로 넘겨 / WSL 로 넘겨 / 윈도우에 시켜 / 다른 기기에 보내 / handoff / /handoff" 라고 하거나, Claude 가 스스로 "이 작업은 상대 기기가 해야 함" 판단 시 이 스킬을 실행.
allowed-tools: mcp__plugin_telegram_telegram__reply, Bash, Read
---

# handoff — 크로스 디바이스 프롬프트 넘기기

강대종님이 두 Claude 세션(Mac=`@MyClaude`, WSL=`@Myclaude2`) 을 운영한다. 자동 전달 메커니즘:

- 현재 세션은 **자기 봇만 폴링** (각각 @MyClaude, @Myclaude2)
- 디렉티브 발송은 `~/.claude/channels/telegram/send.sh --peer` 로 **상대 봇 토큰을 써서 직접 sendMessage POST**
- → 디렉티브가 처음부터 상대 봇 챗에 도착 → 상대 Claude 가 인바운드로 받아 처리
- 강대종님은 **복붙 0회**. 상대 봇 챗만 열어보면 됨

(과거에는 long-press → 상대 봇 DM paste 가 필수였으나 2026-04-25 peer-token 메커니즘으로 자동화됨. 토큰 미설정 / 전송 실패 시 자동 fallback 으로 reply 툴 사용 — 이 경우 강대종님 수동 복붙 필요.)

## 호출 순서

### 1. 먼저 "분석/근거" 를 reply 툴로 보낸다 (현재 봇)

분석·판단 근거·왜 상대 기기가 해야 하는지·맥락을 평소처럼 답한다. 이 메시지 끝에 한 줄 넣는다:

> **다음 메시지가 @Myclaude2(또는 @MyClaude) 챗에 자동으로 도착해 있을 거예요.**

만약 fallback 모드(아래 참조)면 다음과 같이 안내:

> **peer 토큰 미설정/전송실패 — 다음 메시지가 복붙용입니다.**

### 2. 디렉티브를 상대 봇으로 직접 발송 (Bash + send.sh)

1차 시도: peer 봇 토큰으로 자동 발송.

```bash
~/.claude/channels/telegram/send.sh --peer 538806975 "<디렉티브 본문 그대로>"
```

- chat_id `538806975` 는 강대종님 user_id (양 봇 모두 같은 DM)
- 본문은 **상대 Claude 의 첫 입력 프롬프트로 즉시 사용 가능한 형태**
- send.sh 가 0 반환 = 도착. 비0 = 토큰 누락 등 → fallback

**Fallback (peer 토큰 미설정 또는 send.sh 실패):**
기존 방식대로 `mcp__plugin_telegram_telegram__reply` 로 **별도 메시지** 발송. 강대종님이 long-press → 상대 봇 챗에 paste.

### 3. 디렉티브 메시지 포맷 규칙 (양쪽 경로 공통)

- **인용 박스 (`>`) 사용 금지** — fallback 시 long-press 복사 영역을 오염
- **이모지 사용 금지**
- **"다음은 디렉티브입니다" 류 프리픽스 금지** — 상대 Claude 가 그걸 명령 일부로 오해
- **코드 펜스 (```) 금지** — 동일 이유
- 본문은 **자족적** (self-contained). 상대 Claude 가 새 세션 첫 입력으로 가정하고 컨텍스트·repo URL·파일경로·제약·금지사항 전부 인라인. "아까 말한 그거" 금지
- 자동 발송 모드에서도 디렉티브는 **단일 메시지**. 4096자 초과 시 Gist/repo 에 commit 후 URL 만 디렉티브에 넣음

### 4. 여러 디렉티브는 각각 별도 send.sh 호출

2개 이상의 독립된 디렉티브면 send.sh 를 **호출당 한 번** 으로 분리. 한 본문에 1/2/3 번호로 묶지 말 것 (상대 Claude 가 한 입력으로 처리하면 컨텍스트 섞임).

## 전송 예

### 잘된 예 ✅ (자동 전달 모드)

```
[reply 툴] 분석:
"한줄일기는 toss-tone 폴리싱 끝났고, 다음 사이클은 감성 톤 전환입니다.
docs/DESIGN_AUDIT_2026-04-22.md 에 prep 끝냈어요.
다음 메시지가 @Myclaude2 챗에 자동 도착했을 거예요."

[Bash] send.sh --peer 538806975 "..."
본문: "hanjul 디자인 업스케일 사이클 시작. cd ~/apps/hanjul && git pull 해서 docs/DESIGN_AUDIT_2026-04-22.md 읽은 다음, ~/design-lab/hanjul/ 폴더 만들어서 ZeroZ-lab/cc-design + bluzir/claude-code-design 을 -s project 스코프로 설치. 오디트 문서를 첫 컨텍스트로 넣고 A안(ZeroZ) 2개 + B안(bluzir) 2개 시안 HTML 로 뽑아줘. 제약: Pretendard 유지, Toss blue(#3182F6) CTA 유지, asset 300KB 이하, Flutter 이식 가능 수준."
```

### 잘못된 예 ❌

```
reply 1: "분석 결과 이건 Mac 이 해야 합니다. 아래 내용을 @MyClaude 에 보내주세요:
> hanjul 디자인 시작. cd ~/apps/hanjul...
이거 붙여주시면 됩니다."
```

→ 디렉티브가 분석 안에 인용으로 끼어 있어 fallback 시에도 복사 어렵고, 자동 모드면 send.sh 호출 자체가 누락됨.

## 기기별 동작

| 출발 기기 | peer 봇 | peer 토큰 위치 (`.env` 키) | chat_id |
|-----------|---------|---------|---------|
| Mac (@MyClaude 세션) | @Myclaude2 | `TELEGRAM_PEER_BOT_TOKEN` | 538806975 |
| WSL (@Myclaude2 세션) | @MyClaude | `TELEGRAM_PEER_BOT_TOKEN` | 538806975 |

`.env` 위치: 양 기기 모두 `~/.claude/channels/telegram/.env` (mode 600, git 비추적).

각 봇은 **자기 호스트에서만 폴링**되므로 sendMessage POST 충돌(409)은 발생하지 않음. (관련: `feedback_nested_claude_telegram_conflict.md` 의 409 는 같은 토큰을 두 곳에서 폴링했을 때만 발생)

## 언제 자발적으로 실행하나

강대종님이 명시적 키워드 없어도 아래 상황엔 Claude 가 스스로 이 스킬 실행:

- 현재 세션에서 못 하는 작업이 상대 기기에 있음 (Mac=iOS 빌드·키체인·App Store, WSL=Android 빌드·adb)
- 상대 세션의 진행 중 작업의 후속 단계 필요
- 강대종님이 기기 옮겨가는 흐름에서 현재 세션이 막다른 길

## 실패 모드 / 주의

- **peer 토큰 누락**: send.sh 가 `TELEGRAM_PEER_BOT_TOKEN empty` 로 비0 종료 → 즉시 fallback (reply 툴 + 강대종님 복붙 안내)
- **상대 Claude 세션 죽어있음**: 메시지는 상대 봇 챗에 도착하지만 처리 안 됨. 강대종님이 상대 기기 Claude 살리거나 폰에서 그대로 처리. send.sh 성공이 곧 처리 보장은 아님 — 분석 메시지에 "도착 시 자동 처리 / 미처리면 알려주세요" 한 줄 권장
- **민감 정보 금지**: 디렉티브는 사실상 public 수준 (텔레그램 검색 캐시). API 키·비번·세션 토큰 절대 인라인 금지. "env 에서 읽어" 로 대체
- **메시지 길이 4096자 초과**: 자동 모드에서도 분할 금지. Gist/repo commit 후 URL 만 디렉티브에 포함
- **handoff 의 handoff 금지**: 상대 Claude 가 받자마자 또 다른 기기로 handoff 하는 무한루프 발생 가능 — 디렉티브에 "이건 너 기기에서 끝내" 명시

## 관련

- `feedback_mac_directive_separate_message.md` — 별도 메시지 규칙이 나온 2026-04-21 대화 기록
- `feedback_telegram_reply_tool_mandatory.md` — reply 는 MCP 툴 경유 (분석 메시지 한정)
- `feedback_nested_claude_telegram_conflict.md` — 409 발생 조건 (폴링만 충돌, POST 무관)
- `project_ship_pipeline.md` — SSH 자동 브릿지 차단 이력 (peer-token 우회 와는 별개)
- `reference_ssh_mac_tools.md` — 키체인 제약 원본
- `~/.claude/channels/telegram/send.sh` — peer 토큰 발송 구현체 (2026-04-25 `--peer` 플래그 추가)
