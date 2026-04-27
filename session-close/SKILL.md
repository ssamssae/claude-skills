---
name: session-close
description: 강대종님이 "세션초기화/세션 재시작/세션 클리어 해도 돼?" 류 발화로 현재 Claude Code 세션을 닫으려 할 때, 이번 세션의 진행 기록을 체크포인트로 남기고 답변에서 추가작업으로 제안만 했던(실행 안 한) 후속안들을 someday 로 박는 스킬. 다음 세션이 컨텍스트 끊김 없이 이어받을 수 있게 하는 게 목적. /clear 직전 마지막 step.
allowed-tools: Bash, Write, Edit, Read, Grep
---

# Session Close (세션 마무리 체크포인트)

## 핵심

강대종님 표현 그대로 — 세션 끝낼 때 **"어디까지 진행했다"** 기록 + **"이번 세션에서 제안만 한 후속안들"** 을 someday 로 빼두고 깔끔하게 닫기. 미완료 자체를 옮기는 게 아니라 진행 기록 + 후속안 캡처.

## 트리거 발화

다음 패턴 모두:

- "세션초기화해도 돼?" / "세션 초기화" / "세션초기화"
- "세션 재시작해도 돼?" / "세션 재시작"
- "세션 클리어해도 돼?" / "세션 클리어" / "세션클리어"
- "/session-close" / "/session-end"
- "이 세션 닫아도 돼?" / "/clear 해도 돼?"
- "오늘 세션 끝낼까?"

**"되?" / "돼?" 의문형이 핵심 시그널.** 그냥 "/clear" 만 친 거면 강대종님이 이미 닫기로 결심한 거니 발동하지 말고 통과.

## 0. 기기 라우팅

Mac/WSL/iPhone 어디서든 발동 가능. 단:
- 진행 기록(체크포인트)은 메모리 폴더에 직접 Write — `~/.claude/projects/-home-ssamssae/memory/` 가 양쪽 동기화돼있음
- someday 박기는 마스터 파일이 `~/todo/someday.md` (Mac 로컬) → WSL/iPhone 에서 발동되면 텔레그램 트리거로 Mac 에 위임

```bash
host=$(hostname)
case "$host" in
  *MacBook*|*MBP*) DEVICE=mac ;;
  DESKTOP-*) DEVICE=wsl ;;
  *) DEVICE=other ;;
esac
```

## 1. 진행 기록 수집

이번 세션에서 한 일을 4개 소스 cross-check:

1. **대화 맥락** — 이 세션 내내 어떤 작업을 했는지 기억
2. **git log 24h** — 작업한 repo 들의 최근 커밋
   ```bash
   for d in ~/claude-automations ~/claude-skills ~/daejong-page ~/trend-curator ~/.claude/projects/-home-ssamssae/memory; do
     [ -d "$d/.git" ] && (cd "$d" && echo "=== $d ===" && git log --since='24 hours ago' --oneline | head -10)
   done
   ```
3. **진행중 메모리** — `~/.claude/projects/-home-ssamssae/memory/project_*_in_progress.md` 패턴
   ```bash
   ls ~/.claude/projects/-home-ssamssae/memory/project_*_in_progress.md 2>/dev/null
   ```
4. **todos.md 24h diff** — `~/daejong-page/todos/` 최신 스냅샷에서 진행중 섹션 변화

각 작업에 대해 "어디까지 갔는지" 한 줄 정리. 다음 세션이 이 한 줄만 보고도 이어받을 수 있게.

## 2. 추가작업 제안 추출

이번 세션에서 강대종님이나 본인이 답변에서 **"다음에 X 도 할 수 있겠다"** / **"Y 도 고려해볼만함"** / **"Z 도 추가하면 좋겠다"** / **"v0.2 에서는 ..."** 같은 미실행 후속안을 식별.

이 후속안들이 todos 에 박힐 정도로 큰 건 아니지만 잊어버리긴 아까운 것 → **someday 후보**.

식별 신호:
- "추가로 ... 도 가능"
- "다음 단계로 ... 검토"
- "옵션으로 ... 도 고려"
- "v0.X 에서 ..."
- "TODO: ..."
- 메모리 파일 끝의 "## How to apply" 의 "다음 손볼 거리"

## 3. 텔레그램 후보 리스트

강대종님 폰으로 reply 한 메시지 1통:

```
💤 세션 닫기 체크포인트 후보 (YYYY-MM-DD HH:MM KST)

📌 진행 기록 (다음 세션이 이어받을 한 줄):
1. <repo/주제> — <어디까지 갔는지> ✅/⏸/🔄
2. ...

💭 someday 박을 후속안 (이번에 답변으로 제안만):
A. 🤝 <이모지> <제목> — <한 줄 설명>
B. ...

응답 포맷:
- 진행 기록 OK → "체크포인트 OK"
- 빠진 거/고칠 거 → "체크포인트 수정: <항목번호 또는 자유서술>"
- someday 후보 → "💤 A B" (박을 항목 알파벳 나열) 또는 "💤 X" (다 드롭)
- 다 OK → "닫아"
```

## 4. 강대종님 컨펌 처리

응답 발화 파싱:

| 응답 | 동작 |
|------|------|
| "체크포인트 OK" | 진행 기록 그대로 저장으로 |
| "체크포인트 수정: ..." | 해당 항목 다듬기 |
| "💤 A B C" | A, B, C 항목만 someday 트리거 발사 |
| "💤 X" / "💤 없어" | someday 박기 skip |
| "닫아" / "OK" | 5번으로 |
| "잠깐만 / 다시" | 발동 취소, 통상 응답으로 복귀 |

## 5. 저장

### 5-1. 진행 기록 → 메모리 파일

`~/.claude/projects/-home-ssamssae/memory/checkpoint_YYYY-MM-DD-HHMM.md` 형식 신규 파일. (in_progress 메모리와 다른 prefix `checkpoint_` 로 구분)

```markdown
---
name: 세션 체크포인트 YYYY-MM-DD HH:MM KST
description: <기기> 세션 마무리. <주제 키워드 N개> 작업 진행 기록. 다음 세션이 이어받기 위한 한 줄 요약.
type: project
---

## 세션 정보
- 기기: 🍎 Mac / 🪟 WSL / 📱 iPhone
- 시작 시각: HH:MM KST (대화 첫 turn ts)
- 종료 시각: HH:MM KST
- 발동 발화: "<강대종님 트리거 발화 그대로>"

## 진행 기록 (다음 세션 인계)

### 1. <repo/주제>
- 상태: ✅완료 / ⏸중단 / 🔄이어가기
- 어디까지: <한 줄>
- 관련 커밋: `<hash>` (있으면)
- 다음 step: <한 줄> (이어가기인 경우만)

### 2. ...

## 사이드 발견 (추가작업 someday 박은 것들)

- 💤 <항목 제목> → someday 추가 트리거 발사 완료 (HH:MM KST)
- 💤 ...

## 닫힘 후 청소

- [x] 진행중 메모리 정리: <삭제한 in_progress 파일들>
- [x] MEMORY.md 인덱스 갱신: <어떤 라인 더했/뺐>
```

저장 후 **MEMORY.md 인덱스에는 일부러 안 올림** (체크포인트는 1회용, 7일 후 자동 정리 가능). 단, 메모리 폴더에는 남겨서 다음 세션이 grep 으로 찾을 수 있게.

### 5-2. someday 후보 → 트리거

선택된 someday 후보들 각각에 대해 텔레그램 reply (별도 메시지):

```
💭 /someday 트리거
액션: 추가
항목: 🤝 <이모지> <제목> — <한 줄 설명>

Mac Claude 창에 아래 한 줄 복붙:
/someday 추가 🤝 <이모지> <제목>
```

WSL/iPhone 에서는 위 트리거만 보내고 종료. Mac 에서는 직접 someday 스킬 호출.

### 5-3. 진행중 메모리 정리

이번 세션에서 만든 `project_*_in_progress.md` 메모리 중 **완료된 것** 은 삭제 (룰 일관). MEMORY.md 인덱스에서도 빼기.

```bash
# in_progress 중 이번 세션 완료분 식별 후
rm ~/.claude/projects/-home-ssamssae/memory/project_<완료된주제>_in_progress.md
# MEMORY.md 인덱스 라인 제거 (Edit 툴로)
```

## 6. 그린라이트

체크포인트 저장 + someday 트리거 + 청소 완료 후 강대종님께 텔레그램 reply 1줄:

```
✅ 세션 닫기 OK
- 체크포인트: ~/.claude/projects/-home-ssamssae/memory/checkpoint_YYYY-MM-DD-HHMM.md
- someday 박힌 항목 N개 (트리거 발사됨)
- in_progress 메모리 M개 정리됨
- /clear 진행하셔도 됩니다.
```

## 자동 트리거 vs 명시 호출

- **자동 매칭**: 위 트리거 발화 들어오면 Claude 가 알아서 발동 (다른 스킬 호출보다 먼저)
- **명시 호출**: `/session-close` 슬래시 명령으로도 가능
- **No-op 케이스**: 이번 세션이 짧고 (5분 미만) 아무 작업 없었으면 "체크포인트 안 박을 만큼 가벼운 세션" 으로 판단, 그냥 "닫아도 OK" 한 줄로 응답

## 헷갈리지 말 것

- `/session-close` ≠ `/clear` — Claude Code 의 /clear 는 세션 메모리 비우기. 이 스킬은 그 직전 체크포인트 + someday 박기 단계.
- `/session-close` ≠ `/goodnight` — /goodnight 는 하루 마무리 (worklog + done + 체크리스트 + 홈페이지). 이 스킬은 세션 단위, 하루에 여러 번 호출 가능.
- `/session-close` ≠ `/handoff` — /handoff 는 다른 기기 Claude 에 작업 넘기기. 이 스킬은 같은 기기 다음 세션에 컨텍스트 넘기기.
- 진행중 메모리(`project_*_in_progress.md`) ≠ 체크포인트(`checkpoint_YYYY-MM-DD-HHMM.md`) — 전자는 작업 중인 동안만, 후자는 세션 닫을 때 1회 박는 스냅샷.

## 메모

- v0.1 시드: 2026-04-27 18:05 KST WSL 본진
- 첫 사용 시 강대종님 피드백 받아 v0.2 에서 다듬기 (체크포인트 위치, 트리거 정확도, 후보 추출 휴리스틱 등)
