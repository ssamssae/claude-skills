---
name: goodnight
description: 하루 마무리 종합 스킬. 오늘 한 일을 **worklog(산문체 작업일지) + done(체크리스트) + 미기록 이슈 점검** 세 축으로 한 번에 최신화하고, claude-automations·claude-skills·daejong-page 3개 repo 상태를 점검해 홈페이지까지 반영한다. 사용자가 "굿나잇", "잘자", "/goodnight", "오늘 마무리", "하루 마무리", "종합 동기화", "오늘 정리해줘", "오늘 끝", "하루 정리" 라고 말하면 이 스킬을 실행.
daejong_device: mac
daejong_tag: 하루 마무리
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill
---

# /goodnight — 하루 마무리 종합 동기화

## 컨셉

- 강대종님이 자기 직전 한 줄로 하루를 닫는 스킬
- 기존 `/worklog`(산문체 상세) · `/done`(체크리스트) · `/issue`(포스트모템) 를 **개별로 부르지 않고 한 번에** 최신화
- 끝나면 홈페이지(`ssamssae.github.io/daejong-page`) 에 오늘치가 세 축(worklog·done·issues) 전부 반영돼 있어야 성공
- `/todo-reminder` 와는 역할이 다름 — todo-reminder 는 "내일 뭐 할지" 알림, goodnight 은 "오늘 뭐 했는지" 기록 마감

## 기기 라우팅 (Mac 본진 집중)

worklog·done·이슈 동기화 모두 Mac 이 SoT. Mac 이 아닌 기기에서 호출되면 텔레그램 트리거 1줄 보내고 종료:

```bash
host=$(hostname)
if [[ "$host" != *MacBook* && "$host" != *MBP* ]]; then
  # 텔레그램 reply 로 chat_id 538806975 에 전송 후 종료:
  #   🌙 /goodnight 트리거
  #   Mac Claude 창에 아래 한 줄 복붙:
  #   /goodnight
  exit 0
fi
```

## 절차

### 1. 오늘 맥락 수집 (읽기 전용)

아래를 조용히 수집해서 머릿속에 요약본 만든 후 강대종님에게 3~5줄로 미리보기:

- 이번 세션의 주요 작업 (내 입장에서 요약)
- `~/.claude/projects/-Users-user/*.jsonl` 중 오늘 날짜 세션 로그 존재 여부 (worklog 가 참조할 것)
- 오늘 날짜 기준 각 주요 repo 의 커밋 (`git log --since="today 00:00" --oneline`)
  - `~/simple_memo_app`
  - `~/daejong-page`
  - `~/.claude/automations`
  - `~/.claude/skills`
  - `~/apps/*` (Flutter 앱들)
- 오늘치 이미 있는 산출물:
  - `~/daejong-page/worklog/$(date +%F)_*.md`
  - `~/daejong-page/worklog-source/$(date +%F)_*.md`
  - `~/daejong-page/done/$(date +%F).md`
  - `~/.claude/skills/issues/$(date +%F)-*.md`

요약 미리보기 형식:

```
🌙 오늘 마무리 미리보기
- 이번 세션: <1~2줄>
- 오늘 커밋: N개 (repo별 숫자)
- 기존 산출물: worklog ✅/❌, done ✅/❌, 이슈 N건
- 하고 싶은 것: worklog 작성/갱신, done 갱신, 이슈 점검
OK 하면 진행합니다.
```

사용자 OK 받으면 2단계로.

### 2. 미기록 이슈 점검 (✨ 핵심)

오늘 세션에서 **버그·혼선·해결된 문제** 패턴이 나왔는데 `issues/` 에 안 찍힌 게 있으면 먼저 /issue 로 빠진 것부터 기록한다. 감지 기준:

- "끊김", "에러", "실패", "멈춤", "안 됨", "리젝", "충돌", "오동작" 같은 단어가 이번 세션 사용자 메시지에 등장했는가
- 내가 bug-fix 커밋을 오늘 만들었는가 (`git log --since="today 00:00" --oneline | grep -iE 'fix|bug|버그|오류|픽스'`)
- 해당 이슈가 `~/.claude/skills/issues/$(date +%F)-*.md` 중 하나에 이미 대응되는가

매칭되는 게 있는데 이슈 파일이 없으면 사용자에게 텔레그램으로 물음:

```
📋 미기록 이슈 후보
<1줄 요약>
→ [기록] /issue 로 지금 바로 기록
→ [패스] 이번 goodnight 에선 기록 없이 진행
```

[기록] 선택 시 Skill tool 로 `issue` 스킬 호출. 기록 끝나면 2.5 단계로.
[패스] 또는 후보 없음이면 바로 2.5 단계로.

### 2.5. 중요 결정 박제 점검 (✨ 2026-04-24 추가)

오늘 세션에서 **다른 세션/디바이스가 몰라도 이상한 결정·방향 전환·제거·추가**가 있었는지 사용자에게 물음. 이유: worklog 에만 남으면 다른 Claude 세션이 모름 (다른 스킬이 worklog 를 안 읽음).

감지 기준:
- 디자인 방향 결정 ("A2+B1 채택", "blue rebrand" 같은 것)
- 플랫폼·툴 선정 ("Substack 확정", "ollama qwen2.5 로 교체")
- 스킬 추가·제거 ("/toss-tone 삭제", "/insta-post 신설")
- 중요한 지표·수치·ID ("alpha 트랙 edit_id", "IG 앱 ID", "API quota 숫자")
- 프로젝트 상태 전환 ("기억이 드롭", "심사레이더 v0.2 로 진입")

사용자에게:

```
🧠 오늘 기억할 결정 있나요?
후보(감지된 것):
  • <후보 1>
  • <후보 2>
없으면 "없음", 추가 있으면 한 줄씩 입력 → 알맞은 memory 파일로 저장합니다.
```

응답 처리:
- **새 항목**: `project_<name>.md` 또는 `feedback_<name>.md` 로 적절히 분류, Write 로 저장 + `MEMORY.md` 인덱스 1줄 추가
- **기존 메모리 갱신**: 해당 파일 Edit
- 모든 변경은 memory auto-push hook 이 알아서 commit+push
- **"없음"**: skip, 3단계로

이 단계가 고비용(사용자 입력 대기) 이라 후보가 명확히 0개면 사용자에게 안 물어봐도 됨. 다만 감지 애매하면 반드시 질문.

### 3. worklog 실행

```
Skill tool → worklog 호출
```

worklog 스킬이 알아서:
- `~/daejong-page/worklog-source/` 에 마크다운 원본 저장
- `~/daejong-page/worklog/` 에 산문체 공개본 저장
- daejong-page repo commit + push

에러 나면 강대종님에게 알리고 4단계는 건너뛰지 말고 계속 시도 (done 은 독립적으로 실행 가능).

### 4. done 실행

```
Skill tool → done 호출 (인자 없음, 오늘 날짜 사용)
```

done 스킬이 알아서:
- `~/daejong-page/done/$(date +%F).md` 저장/갱신
- daejong-page push

### 5. 3 repo 상태 점검

```bash
for repo in ~/.claude/automations ~/.claude/skills ~/daejong-page; do
  cd "$repo" || continue
  dirty=$(git status --porcelain | wc -l | xargs)
  unpushed=$(git log @{u}.. --oneline 2>/dev/null | wc -l | xargs)
  echo "$(basename $repo): dirty=$dirty unpushed=$unpushed"
done
```

- dirty > 0 이면 → 안 커밋된 변경이 있음. 강대종님에게 diff 요약 보여주고 commit 여부 확인
- unpushed > 0 이면 → commit 은 됐는데 push 안 됨. 즉시 push 시도

### 6. 최종 보고 (텔레그램)

chat_id 538806975 로 한 메시지:

```
🌙 굿나잇 — 하루 마무리 완료

**오늘 한 일**
- worklog: <파일명> (커밋 SHA)
- done: <체크리스트 N개 항목>
- 이슈: <신규/갱신 M건> or "없음"
- 코드 커밋: <repo별 개수>

**홈페이지 반영**
- https://ssamssae.github.io/daejong-page/worklog.html
- https://ssamssae.github.io/daejong-page/done.html
- https://ssamssae.github.io/daejong-page/issues.html

**상태**
- 3 repo clean + pushed ✅
- GitHub Pages 빌드 1-2분 후 반영

잘자요 🌙
```

실패가 끼면 해당 축만 "⚠️ 실패: <사유>" 로 표시하고 나머지는 성공으로 보고.

## 금지

- **내일 할일 제안 금지** — todo-reminder 의 영역. 여기선 과거형만.
- **이슈 없는데 억지로 만들기 금지** — 후보 감지 안 되면 이슈 단계는 스킵.
- **홈페이지 커밋 생략 금지** — worklog·done 은 각 스킬이 자체 push 까지 해주지만, 혹시 빠졌으면 5단계에서 잡아서 push.
- **다른 날짜 소급 금지** — 기본은 오늘. 과거 날짜가 필요하면 `/worklog <date>` 나 `/done <date>` 를 개별 호출.

## 메모리 연계

- 완료 시 메모리 저장 불필요 (매일 돌리는 루틴)
- 예외적 실패(예: repo push 실패가 반복되면) 는 `/issue` 로 포스트모템 기록
