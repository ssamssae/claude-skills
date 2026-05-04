---
name: session-close
description: 강대종님이 "세션 클리어/초기화/재시작 해도 돼?" 류 의문형으로 세션 끝낼지 물을 때, 이번 세션에서 답변으로 제안만 하고 안 한 후속안을 todos/parking-lot/drop 분류 후보로 추려 텔레그램 1통으로 던지고 OK 받으면 체크포인트 메모리 파일 1개 추가하고 닫음. v0.4 (2026-05-02 someday 폐지 반영).
allowed-tools: Bash, Write, mcp__plugin_telegram_telegram__reply
---

# Session Close (lean)

## 기기 라우팅 (지휘관 1명 원칙)

🍎 Mac 본진 = 지휘관(설계·결정·메인 세션, main 머지 결정) / 🏭 Mac mini = 빌드·배포 워커(SSH 라우팅 수신) / 🪟 WSL = 작업자(`wsl/*` 브랜치 push, main 직접 push 금지). 운반체 = `wsl-directive.sh` / `mac-report.sh`.

**이 스킬**: 🍎 Mac 본진 전용 — 체크포인트 메모리 SoT 가 본진이라 WSL 에서 호출 X.

## 발동

"세션 클리어/초기화/재시작 해도 돼?" / "이 세션 닫아도 돼?" / "/clear 해도 돼?" / "/session-close" — **의문형**이 시그널. 그냥 `/clear` 만 친 거면 발동 X.

## 0. 메모리 경로 (호스트별)

```bash
case "$(hostname)" in
  *MacBook*|*MBP*) MEMORY_DIR="$HOME/.claude/projects/-Users-user/memory" ;;
  *)               MEMORY_DIR="$HOME/.claude/projects/-home-ssamssae/memory" ;;
esac
```

## 1. 후보 추출 (대화 컨텍스트만)

이 세션 turn 들에서 본인이나 강대종님이 답변으로 던졌지만 실행 안 한 후속안 식별. 패턴: "다음에 X 도 가능" · "v0.X 에서 ..." · "옵션으로 ..." · "TODO: ...".

**외부 grep / git log / 메모리 스캔 없음.** 대화 기억만 사용. 후보 0개면 4번으로 점프.

## 2. 자동 분류 + 저장

후보가 있으면 **확인 없이** 바로 분류해서 저장:

- **활성 작업/트리거 박힌 것** → `todos.md` `## 진행중` 상단 추가
- **사이드 프로젝트/언젠가/여유 되면 류 아이디어** → `parking-lot.md` 끝에 추가
- **인프라 후속·운영 튜닝/재발 시 재기소** → drop (저장 X)
- 분류 기준: 트리거·마감·ASC·PR 관련이면 todos, 막연한 개선이면 parking-lot, 일회성이면 drop

저장 후 daejong-page repo commit + push.

후보 0건이면 저장 단계 스킵.

## 3. 컨펌 없음

확인 메시지 보내지 않음. 저장까지 자동 완료 후 5단계로.

## 4. 체크포인트 저장 (선택)

진행 한 줄이 의미 있을 때만 (반나절+ 작업 / 미완 작업 인계 필요) `$MEMORY_DIR/checkpoint_YYYY-MM-DD-HHMM.md`:

```markdown
---
name: 세션 체크포인트 YYYY-MM-DD HH:MM KST
description: <기기> 세션 마무리. <주제>. 다음 세션 인계.
type: project
---

- 기기: 🍎/🪟/📱
- 진행: <한 줄>
- 다음 step: <한 줄> (이어가기일 때만)
- 추가한 후속안: <todos/parking-lot/drop 분류로 <항목들> 또는 없음>
```

MEMORY.md 인덱스에는 안 올림 (1회용). 5분 미만 짧은 세션이면 skip.

## 5. 종료

텔레그램 reply 후 **2초 대기 → tmux send-keys로 자동 /clear**:

```bash
# 1. 텔레그램 reply (아래 형식)
# 2. 전송 확인 후:
sleep 2 && tmux send-keys -t claude "/clear" Enter
```

reply 형식:
```
💤 세션 마무리 (HH:MM KST)

박힌 것:
- todos → <항목 한 줄> (있을 때만)
- parking-lot → <항목 한 줄> (있을 때만)
- 후속안 없음 (0건일 때)

(자동 /clear 진행합니다)
```

## 헷갈리지 말 것

`/session-close` ≠ `/goodnight`(하루 마무리) ≠ `/clear`(세션 메모리 비우기). 타기기 인계는 `wsl-directive.sh` (Mac→WSL) 또는 텔레그램 reply (WSL→Mac).

## 메모

- v0.1 (2026-04-27 18:05 KST): 초기 버전 (4-source cross-check + 다턴 컨펌)
- v0.2 (2026-04-27 20:10 KST): host-aware MEMORY_DIR + METHOD A handoff + takeover 처리 추가 → 280줄로 비대해짐
- v0.3 (2026-04-27 22:50 KST): 강대종님 "토큰 1/5 으로" 지시. git log 루프 / in_progress 스캔 / takeover 라이프사이클 / no-op 휴리스틱 모두 제거. host-aware path 만 유지. ~60줄
- v0.4 (2026-05-02): someday 폐지 반영. "someday 후보" → "후속안 (todos/parking-lot/drop 분류)". someday 직접 호출 흐름 제거.
- v0.5 (2026-05-02): parking-lot 정의 확장 — 「사이드 프로젝트」 한정에서 「사이드 프로젝트 + 언젠가/여유 되면 류 아이디어」 통합 한 통으로. someday 컨셉 자체를 parking-lot 에 흡수.
