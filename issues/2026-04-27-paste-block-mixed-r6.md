---
prevention_deferred: null
date: 2026-04-27
host: USERui-MacBookPro (Mac)
status: workaround
related: feedback_paste_blocks_as_separate_message
---

# 복붙 블록 별도 메시지 룰 6번째 재발 (오늘만 4번)

- **발생 일자:** 2026-04-27 19:34 ~ 21:01 KST (한 세션 내 4회 연속)
- **해결 일자:** 2026-04-27 21:05 KST (hook 보강 + 메모리 갱신)
- **심각도:** medium
- **재발 가능성:** high (메모리·CLAUDE.md 룰만으론 6번째까지 어김)
- **영향 범위:** 모든 텔레그램 reply 워크플로우 (Mac/WSL 양 기기)

## 증상

본 세션이 텔레그램 reply 안에 `복붙용 fenced block` + `한국어 분석/안내 sentence` 를 한 메시지에 같이 박음. 강대종님 폰에서 long-press → copy 가 제대로 안 됨.

오늘만 4회 연속:
1. 19:34 (msg 8047) — handoff commit 옵션 A 안내문에 git commit 명령어 fenced block 포함
2. 19:43 (msg 8051) — settings.json patch 3줄 fenced block 을 issue 컨펌 본문 안에 포함
3. 20:00 (msg 8061) — nano 명령 + nano 안 절차를 한 메시지에 (강대종님 8064 지적: "터미널에 입력하는거 따로줘야지")
4. (동일 패턴 — fenced 안 명령어 + 외부 한글 안내 sentence)

기존 메모리 (`feedback_paste_blocks_as_separate_message.md`) 의 재발 카운트는 18:32 (msg 18a5b30) 3번째 까지 박혀있었음. 오늘 4번째~6번째 추가.

## 원인

- 본 세션이 "분석/근거를 자연스럽게 + 함께 복붙 본문도 같이" 구조로 reply 생성하는 디폴트 패턴 — 사람 친화적 서술 흐름이라 무의식적으로 섞음.
- 룰이 메모리·CLAUDE.md 룰만 — 매 reply 호출 직전 자동 차단 forcing function 부재. 시스템 프롬프트도 이 룰 명시 X.
- raw msg ID leak (2026-04-27 17:09 사고) 는 PreToolUse hook 신설로 차단됐지만, 복붙 mixed 패턴은 같은 패턴이 아니라 detection 못 함.

## 조치

1. 본 issue 등록.
2. 기존 PreToolUse hook `~/.claude/hooks/telegram-reply-no-raw-id.sh` 본체에 추가 검사 블록 — fenced ```block``` 안에 명령어/config 패턴 + fenced 외 영역에 한국어 자연어 sentence 동시 존재 시 block.
3. 메모리 `feedback_paste_blocks_as_separate_message.md` 의 Recurrences 섹션에 4·5·6번째 재발 추가 + hook reference 박기.

## 예방 (Forcing function)

**PreToolUse hook 보강** (`~/.claude/hooks/telegram-reply-no-raw-id.sh` 안에 추가 검사):

```python
# fenced ```block``` 추출
blocks = re.findall(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
# 각 block 본문 첫 라인에 명령어/config 시그널?
cmd_signal = any(
    re.match(r"^\s*(nano|sudo|git|cd|cp|mv|rm|ls|brew|npm|npx|python3?|Edit|Write|Bash|open|code)\b", b.split("\n", 1)[0])
    or re.match(r"^\s*[\{\[]", b.split("\n", 1)[0])
    or re.match(r"^\s*\"[A-Za-z_]+\(", b.split("\n", 1)[0])  # JSON allow rule
    for b in blocks
)
# fenced 외 영역에 한글 sentence?
outside = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
ko_sentence = bool(re.search(r"[가-힣]{4,}", outside))

if cmd_signal and ko_sentence:
    block_with_reason("fenced block 안 명령어/config + 외부 한글 sentence — 별도 reply 메시지로 분리하라")
```

매칭 시 PreToolUse decision=block + reason 안내. 본 세션이 다시 reply 호출할 때 fenced block 만 따로, 한글 안내는 따로 보내는 흐름 강제.

False positive (정상 인용 케이스) 트레이드오프 감수 — 6번째 재발이라 strict 우선. 본 세션이 막히면 분리해서 재전송하면 됨.

부수:
- 메모리 `feedback_paste_blocks_as_separate_message.md` 의 Recurrences 섹션에 4·5·6번째 사례 추가, "hook 보강 2026-04-27" 메모.
- 본 issue 자체는 fenced block 인용 포함 — 본 issue commit 통과는 issue 파일이 텔레그램 reply 가 아니므로 hook 무관 (PreToolUse Bash 매처 아님).

## 재발 이력

- 2026-04-27 19:34: msg 8047 (4번째 — 오늘만 1번째)
- 2026-04-27 19:43: msg 8051 (5번째 — 오늘만 2번째)
- 2026-04-27 20:00: msg 8061 (6번째 — 오늘만 3번째, 강대종님 직접 지적)

## 관련 링크

- 메모리: `feedback_paste_blocks_as_separate_message.md`
- hook: `~/.claude/hooks/telegram-reply-no-raw-id.sh` (보강 대상)
- 강대종님 지적 텔레그램: msg 8054, msg 8064, msg 8069
- 비슷한 패턴 hook: `2026-04-27-telegram-msg-id-leak.md` (raw msg ID leak — 같은 hook 의 1번째 검사)
