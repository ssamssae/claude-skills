---
name: session-clear
description: 텔레그램에서 현재 세션을 클리어. 트리거: "세션 클리어", "세션클리어", "세션클리어하자", "클리어 해줘", "클리어하자", "세션 초기화", "세션 닫자", "세션 지워줘", "/session-clear", "/reset". 후속안 저장 후 /clear 자동 실행. ⚠️ 이 트리거에서 /goodnight 절대 금지 — /session-clear 만 호출.
---

# /session-clear — 텔레그램에서 현재 세션 클리어

## 용도

텔레그램 채팅에서 현재 Claude Code 세션을 `/clear` 하는 스킬.  
원래 텔레그램 창에서 `/clear` 를 직접 보낼 수 없어서 이 스킬로 대신한다.

**트리거:** "세션 클리어", "세션클리어", "세션클리어하자", "클리어 해줘", "클리어하자", "세션 초기화", "세션 닫자", "세션 지워줘", "/session-clear", "/reset"

**⚠️ 절대 금지**: 이 트리거로 /goodnight 호출 금지. "세션" + "클리어/초기화/닫자/지워" 조합은 무조건 이 스킬만. worklog/done/insta-post 실행 안 함.

## 절차

### 1. 후속안 추출 (대화 컨텍스트만)

이 세션 turn 들에서 제안만 하고 실행 안 한 후속안 식별. 패턴: "다음에 X 도 가능" · "나중에 ..." · "v0.X 에서 ..." · "옵션으로 ..." · "TODO: ...".

**외부 grep / git log / 메모리 스캔 없음.** 대화 기억만 사용. 후보 0개면 2번 스킵.

### 2. 자동 분류 + 저장 (후보 있을 때만)

- **활성 작업/마감/트리거 박힌 것** → `~/todo/todos.md` `## 진행중` 상단 추가
- **사이드 프로젝트/언젠가/아이디어 류** → `~/todo/parking-lot.md` 끝에 추가 + `~/daejong-page/parking-lot.md` mirror
- **일회성/인프라 후속** → drop (저장 X)

저장 후 `~/daejong-page` commit + push.

### 3. 텔레그램 reply 전송

```
🔄 [기기아이콘] [hostname] [HH:MM KST]

박힌 것:
- todos → <항목> (있을 때만)
- parking-lot → <항목> (있을 때만)
- 후속안 없음 (0건일 때)

(자동 /clear 진행합니다)
```

### 4. /clear 실행

```bash
TMUX_BIN=/opt/homebrew/bin/tmux  # Mac
# WSL: /usr/bin/tmux
$TMUX_BIN send-keys -t claude "/clear" Enter
```

## 주의

- tmux 'claude' 세션이 없으면 조용히 실패 (에러 없음)
- `/clear` 가 전송되면 이 대화 컨텍스트가 초기화됨

## 버전

- v0.1 (2026-05-04): 초기 버전 — session-close 의 /clear 부분만 독립 분리
- v0.2 (2026-05-04): 후속안 박기 + 보고 추가 (session-close 흐름 일부 이식)
- v0.3 (2026-05-05): 트리거 확장 ("세션클리어하자" 포함) + /goodnight 발화 금지 명시 (이슈 2026-05-05-session-clear-triggered-goodnight)
- v0.4 (2026-05-06): "/reset" 트리거 추가 (강대종 요청)
- v0.5 (2026-05-06): /clear 실행 전 대기 2초 → 10초로 변경 (강대종 요청)
- v0.6 (2026-05-06): /clear 실행 전 sleep 10 제거 — 딜레이 없이 즉시 실행 (강대종 요청)
