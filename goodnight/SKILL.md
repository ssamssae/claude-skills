---
name: goodnight
description: 하루 마무리 종합 스킬. worklog(산문) + done(체크리스트) + 미기록 이슈 점검을 한 번에 최신화하고 claude-automations·claude-skills·daejong-page 3개 repo 점검 후 홈페이지 반영. 트리거 "굿나잇", "잘자", "/goodnight", "오늘 마무리", "하루 마무리", "종합 동기화", "오늘 정리해줘", "오늘 끝", "하루 정리".
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

사용자 OK 받으면 1.5 단계로.

### 1.5. 자동 완료 todos 매칭 (✨ 2026-04-26 추가)

오늘 끝낸 일과 todos.md 의 열린 항목을 토큰 매칭해 "이미 끝났는데 todo 만 안 옮긴" 항목을 자동 검출.

배경: 강대종님 패턴 — 작업이 자연스럽게 끝나도 진행중 [ ] 마킹을 안 옮기는 일이 자주 발생 (예: 4/24 iOS 심사 제출 완료 → 4/26 아침에야 발견). 진행중 섹션이 부풀어서 오늘 우선순위 안 보임.

**입력**:
- 열린 todos: `grep "^- \[ \]" ~/todo/todos.md`
- 오늘 증거 (step 1 에서 수집된 것 + 추가):
  - 오늘 커밋 메시지
  - 오늘 done 항목
  - 오늘 worklog 본문
  - **오늘 갱신된 메모리** (✨ 2026-04-26 추가): `find ~/.claude/projects/-Users-user/memory -name "*.md" -mtime -1` → 각 파일에서 "발행/배포/완료/성공/PASS/도달/충족/투입" 키워드 grep
  - **오늘 텔레그램 reply 본문** (✨ 2026-04-26 추가): 현재 conversation 의 직전 reply 들 또는 transcript jsonl 의 오늘분 — `assistant` role 중 `mcp__plugin_telegram_telegram__reply` tool_use 의 `text` 인자에 동일 키워드 grep

**매칭 알고리즘**:

```python
import re

# 토큰 추출 — 3글자+, 한/영/숫자, 흔한 stopword 제외
STOPWORDS = {"오늘","내일","어제","처리","작업","완료","마무리","수정","변경","추가","제거","업데이트","검증","해결","진행","제출","빌드","배포"}

def tokens(text):
    raw = re.findall(r'[가-힣A-Za-z0-9_]{3,}', text)
    return {w.lower() for w in raw if w.lower() not in STOPWORDS}

evidence_tokens = tokens(today_commits + today_done + today_worklog)
for todo_line in open_todos:
    title = todo_line.split('  (')[0]  # 메타 빼고 본문만
    overlap = tokens(title) & evidence_tokens
    if len(overlap) >= 2:
        candidates.append((title, overlap))
```

매칭 임계값 2개 — 1개는 false positive 너무 많음, 3개는 너무 빡빡.

**텔레그램 질문 포맷**:

```
✅ 자동 완료 후보 N건 — 오늘 한 일이랑 매칭됨:
1. <todo 한 줄 제목> (매칭: 단어1, 단어2, ...)
2. ...

처리: "1,2" 박을 번호 / "전부" / "없음" / "확인 필요" (자세히 보고 싶음)
```

**응답 처리**:
- **번호** / **"전부"**: `/todo` 스킬에 위임. 항목별로 `/todo 완료 <제목>` 호출. 완료 메모는 "✨ 자동 매칭 완료 (오늘 커밋·done·메모리 매칭)" 로 표기 — 나중에 본인이 "왜 완료됐지?" 확인할 수 있게.
  - **메모리 status 동시 갱신** (✨ 2026-04-26 추가): 닫힌 todo 와 매칭된 메모리 파일이 있으면 (evidence 출처가 메모리인 경우), 그 메모리 파일의 status/decision 필드를 "완료"로 갱신 또는 description 한 줄 보강. 갱신 끝난 메모리는 auto-push hook 이 알아서 commit + push.
- **"확인 필요"**: 후보별로 매칭된 단어 + 어디서 매칭됐는지(커밋 hash / done 줄 / worklog 섹션 / 메모리 파일명 / 텔레그램 reply 시각) 상세 표시.
- **"없음"**: skip, 2단계로.
- 후보 0개 / 임계값 미달: 사용자에게 안 물어봄. 조용히 다음 단계.

**오작동 방지**:
- 토큰이 너무 일반적이면 false positive 위험. STOPWORDS 에 "심사", "iOS", "Android" 같은 자주 나오는 단어 추가 검토.
- "검토 필요" 대답이 자주 나오면 임계값 3개로 올리거나, 오늘 commit 의 본문 (제목 외) 도 evidence 에 포함.
- 매칭은 후보 제시일 뿐, 자동 완료 처리 금지. 반드시 사용자 confirm.

이 단계가 끝나면 2단계(미기록 이슈 점검)로.

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

### 2.7. someday 후보 점검 (✨ 2026-04-26 추가)

오늘 세션에서 "지금 할 건 아닌데 언젠가 해보면 좋을 것 같다" 류 아이디어가 떠올랐는지 점검. todo 가 아닌 someday 로 박을 후보들.

감지 기준:
- 사용자 발화에 "나중에" / "언젠가" / "여유 되면" / "이런 거 있으면 좋겠다" 같은 표현
- 이번 세션에서 검토했지만 채택 안 한 대안 (오늘 케이스: 핸드오프 가드 강화 대안 C)
- "아 이런 옵션도 있구나" 식의 미해결 가능성

매칭되는 게 있으면 텔레그램으로 묻음:

```
💭 someday 후보 N건:
1. <후보 1 — 한 줄>
2. <후보 2 — 한 줄>
박을 번호 / "전부" / "없음"
```

응답 처리:
- **번호** / **"전부"**: Skill tool 로 `someday` 스킬 호출, 해당 항목 추가.
- **"없음"** 또는 후보 0개: skip, 3단계로.

이 단계도 고비용이라 후보 0개면 사용자에게 안 물어봄. 결정 박제(2.5) 와 다른 점: 2.5 는 "박아둘 결정", 2.7 은 "박아둘 옵션/아이디어".

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

### 4.5. insta-post 실행 (2026-04-24 추가, 2026-04-29 단순화 — Mac 직접 호출만)

worklog 가 성공적으로 push 된 상태(3단계) 라는 전제 하에 인스타 카드 자동 업로드. **2026-04-29 부터 hostname 분기·WSL 핸드오프 폐기** — 어느 기기든 무조건 직접 호출.

```
Skill tool → insta-post 호출 (인자 없음, 오늘 날짜 사용)
```

insta-post 스킬이 worklog 파싱 → 카드 PNG 렌더 → posted.json dedup → Instagram Graph API 자동 업로드 → permalink. 최종 보고에 permalink.

**왜 단순화했나 (2026-04-29):** 이전엔 Mac 에서 호출되면 WSL 로 텔레그램 핸드오프했음. 그러나 (1) WSL = 야간 OFF 라 야간 /goodnight 핸드오프는 사일런트 실패, (2) Mac=SoT 지휘관 1명 원칙과도 정렬 안 됨. Mac 에 IG 시크릿·venv·posted.json 미러링이 이미 돼있어 직접 호출이 안전.

실패 케이스 처리:
- worklog 가 없으면 insta-post 내부 가드가 "worklog 없음" 으로 중단 + 텔레그램 알림 → goodnight 은 **계속 진행**, 최종 보고에 "⚠️ 인스타 스킵: worklog 없음"
- 이미 올렸으면 dedup 가드로 중단 → 기존 permalink 를 최종 보고에 넣음
- API 에러 또는 토큰 만료 → "⚠️ 인스타 실패: <사유>" 로 보고, 5단계로 계속
- **publish.py wait_public timeout** → publish.py 자체에 300s + 120s retry 박혀있음 (2026-04-28 도입). 그래도 timeout 나면 "⚠️ 인스타 발행 실패 (GH Pages 빌드 timeout): 내일 `/insta-post <date>` 로 백필 권장" 텔레그램 알림. 다음 날 첫 호출 시 강대종님이 인지

**미발행 사후 점검 (2026-04-28 추가)**: insta-post 호출 후 `~/insta-autopost/posted.json` 에 `<date>` entry 박혔는지 확인. 안 박혔으면 publish 단계가 죽은 거 → 위 "발행 실패" 알림 송신. 알림:

```
⚠️ 인스타 미발행: <date> posted.json 에 entry 없음
사유: <publish.py 마지막 stderr>
백필: 내일 /insta-post <date> 호출
```

**중요**: 인스타 업로드가 실패해도 goodnight 전체를 중단하지 말 것. worklog/done 이 홈페이지에 올라갔으면 하루 마감은 이미 성공. 다만 미발행 사실이 텔레그램에 명시적으로 떠야 다음 날 백필 가능.

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
- 인스타: <permalink> or "⚠️ 스킵/실패: 사유"

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
