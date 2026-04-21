---
name: handoff
description: Mac↔WSL 크로스 디바이스 프롬프트 넘기기. 분석/근거 메시지와 분리해서 "상대 Claude 가 그대로 복붙할 수 있는 순수 디렉티브" 만 별도 텔레그램 메시지로 전송해 강대종님이 폰에서 long-press → copy 한 방에 상대방 세션에 꽂을 수 있게 한다. 강대종님이 "맥에 시켜 / 맥으로 넘겨 / WSL 로 넘겨 / 윈도우에 시켜 / 다른 기기에 보내 / handoff / /handoff" 라고 하거나, Claude 가 스스로 "이 작업은 상대 기기가 해야 함" 판단 시 이 스킬을 실행.
allowed-tools: mcp__plugin_telegram_telegram__reply, Read
---

# handoff — 크로스 디바이스 프롬프트 넘기기

강대종님이 두 Claude 세션(Mac=`@MyClaude`, WSL=`@Myclaude2`) 을 운영하는데 자동 브릿지가 전부 막혀 있음 (macOS 키체인 / 하네스 정책). 그래서 **사람이 텔레그램 메시지 한 개를 long-press → copy → 상대 봇에 paste** 하는 게 실질 전달 경로. 이 스킬은 그 "복붙용 메시지" 포맷을 강제한다.

## 왜 별도 메시지로 쏘나

폰에서 긴 메시지 안의 특정 블록만 드래그 선택해서 복사하는 게 iOS/Android 모두 어렵다. 메시지 **통째로** long-press → copy 하는 게 한 방이라, 디렉티브가 그 메시지의 **유일한 내용**이어야 한다.

## 호출 순서

### 1. 먼저 "일반 답변" 을 reply 로 보낸다

분석·판단 근거·왜 상대 기기가 해야 하는지·맥락을 평소처럼 답한다. 이 메시지 끝에 한 줄 넣는다:

> **다음 메시지가 맥(또는 WSL)에 복붙할 순수 프롬프트예요.**

### 2. 바로 이어서 "디렉티브만" 별도 reply 를 보낸다

**필수 포맷 규칙:**

- `reply_to` **미사용** (스레드 인용 없음 — long-press 복사 영역을 오염시킴)
- 인용 박스 (`>`) 사용 금지
- 이모지 사용 금지
- "다음은 디렉티브입니다" 류 프리픽스 금지
- 코드 펜스 (```) 는 상대 Claude 가 그걸 명령 일부로 오해할 수 있으니 **금지**
- 본문은 상대 Claude 가 **프롬프트 자체로 즉시 사용 가능한 형태** 여야 함
  - 예: "hanjul 디자인 업스케일 시작. `cd ~/apps/hanjul && git pull` 해서..."
  - 예: "/land https://github.com/ssamssae/hanjul.git"
- 길이: 상대 Claude 가 문맥 없이도 이해할 만큼 **자족적**. 파일 경로·repo URL·제약 조건 전부 인라인. "아까 말한 그거" 금지.

### 3. 여러 디렉티브는 각각 별도 메시지

2개 이상의 독립된 디렉티브를 상대에 넘겨야 하면 **각각 별도 reply**. 한 메시지에 1/2/3 번호로 묶지 말 것. (long-press 는 메시지 하나 단위)

## 전송 예

### 잘못된 예 ❌ — 디렉티브가 분석 메시지 안에 인용으로 끼어 있음

```
reply 1: "분석 결과 이건 Mac 이 해야 합니다. 아래 내용을 @MyClaude 에 보내주세요:
> hanjul 디자인 시작. cd ~/apps/hanjul...
이거 붙여주시면 됩니다."
```

→ 폰에서 `>` 박스만 선택 복사 어려움.

### 잘된 예 ✅

```
reply 1 (분석):
"현재 한줄일기는 이미 toss-tone 폴리싱된 상태라, 다음 사이클은 감성 톤 전환이 필요합니다.
docs/DESIGN_AUDIT_2026-04-22.md 에 prep 끝냈어요.
다음 메시지가 맥에 복붙할 순수 프롬프트예요."

reply 2 (디렉티브):
"hanjul 디자인 업스케일 사이클 시작. cd ~/apps/hanjul && git pull 해서 docs/DESIGN_AUDIT_2026-04-22.md 읽은 다음, ~/design-lab/hanjul/ 폴더 만들어서 ZeroZ-lab/cc-design + bluzir/claude-code-design 을 -s project 스코프로 설치. 오디트 문서를 첫 컨텍스트로 넣고 A안(ZeroZ) 2개 + B안(bluzir) 2개 시안 HTML 로 뽑아줘. 제약: Pretendard 유지, Toss blue(#3182F6) CTA 유지, asset 300KB 이하, Flutter 이식 가능 수준."
```

## 기기별 동작 차이

| 출발 기기 | 대상 봇 | chat_id |
|-----------|---------|---------|
| WSL (@Myclaude2 세션) | 상대는 @MyClaude | 538806975 (같은 DM) |
| Mac (@MyClaude 세션) | 상대는 @Myclaude2 | 538806975 (같은 DM) |

⚠️ 봇끼리는 서로의 메시지를 자동 수신하지 않는다. 강대종님이 long-press → 상대 봇 DM 에 paste 하는 수동 단계가 **필수**. 이걸 우회하려는 자율 브릿지 시도는 모두 블록됨 (`project_ship_pipeline.md`, `reference_ssh_mac_tools.md` 참조).

## 언제 자발적으로 실행하나

강대종님이 명시적으로 "handoff" 류 키워드를 안 써도, 아래 상황에 Claude 가 스스로 이 포맷을 쓴다:

- 현재 세션에서는 할 수 없는 작업이 상대 기기에 있음 (예: Mac 은 iOS 빌드·키체인·App Store, WSL 은 Android 빌드·adb)
- 상대 세션에서 이미 진행 중인 작업의 후속 단계를 요청해야 함
- 대종님이 기기를 옮겨 가면서 작업하는 흐름이라, 현재 세션에서 해결하기보다 상대에게 넘기는 게 정답

## 실패 모드 / 주의

- **디렉티브가 길어지면 메시지 분할되면 안 됨** — Telegram 한 메시지 최대 4096자. 그 이상이면 분할 대신 **"Gist/repo 에 프롬프트 commit → URL 만 디렉티브에 넣기"** 로 전환.
- **민감 정보 금지** — 디렉티브는 사실상 public 수준 (텔레그램 메시지 검색 캐시). API 키·비밀번호·세션 토큰 넣지 말 것. 필요하면 "env 에서 읽어" 로 대체.
- **상대 세션이 죽어 있을 수 있음** — 붙여도 바로 처리 안 될 수 있음. 일괄 복붙 후 대종님이 확인해야 함.

## 관련

- `feedback_mac_directive_separate_message.md` — 이 규칙이 나온 2026-04-21 대화 기록
- `feedback_telegram_reply_tool_mandatory.md` — 텔레그램 reply 는 반드시 MCP 툴로
- `project_ship_pipeline.md` — SSH 자동 브릿지 왜 불가능한지
- `reference_ssh_mac_tools.md` — 키체인 제약 원본
