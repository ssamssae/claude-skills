---
name: todo
description: 할일(todo)과 사이드 프로젝트를 ~/todo/todos.md 에 기록하고 미리알림 앱 "Claude" 목록과 연동한다. 사용자가 "할일", "해야할거", "미리알림", "todo", "할거", "사이드프로젝트" 등을 이야기하면 이 스킬의 규칙대로 처리한다.
allowed-tools: Bash, Write, Edit, Read
---

# 할일 관리 & 미리알림 연동

## 데이터 소스

- **파일**: `~/todo/todos.md` (진행중/완료/보류/사이드프로젝트 4개 섹션)
- **버전 관리**: `~/todo/` 가 git 저장소. 모든 수정은 커밋으로 남겨 이력 추적.
- **미리알림 앱**: macOS Reminders 의 `"Claude"` 목록과 연동 (AppleScript 경유)

## 호출 시 항상 먼저 할 일

1. `Read ~/todo/todos.md` 로 현재 상태 파악 (이전 커밋 의존 X, 항상 파일 재읽기)
2. 사용자 요청 분류: 추가 / 완료 / 삭제 / 조회 / 이동 / 수정 / 사이드프로젝트

## 기본 동작

### 추가 (add)
사용자: "오늘 더치페이 아이콘 앱스토어 업로드"
1. todos.md 진행중 섹션에 한 줄 추가:
   `- [ ] 더치페이 아이콘 앱스토어 업로드  (추가: YYYY-MM-DD, 마감: YYYY-MM-DD 또는 없음)`
2. 미리알림 앱에 같은 이름으로 reminder 생성:
   ```
   osascript -e 'tell application "Reminders"
       tell list "Claude"
           make new reminder with properties {name:"<제목>"}
       end tell
   end tell'
   ```
   (마감일 있으면 `due date:date "..."` 도 추가)
3. git add + commit: `todo: 추가 - <제목>` + 가능하면 push (원격 있을 때)

### 완료 (done)
사용자: "더치페이 아이콘 완료"
1. todos.md 진행중 섹션에서 해당 항목 찾기
2. 완료 섹션으로 이동하며 `(완료: YYYY-MM-DD)` 추가
3. 미리알림 앱에서 완료 체크:
   ```
   osascript -e 'tell application "Reminders"
       tell list "Claude"
           set r to first reminder whose name is "<제목>"
           set completed of r to true
       end tell
   end tell'
   ```
4. git commit: `todo: 완료 - <제목>`

### 삭제 (delete)
사용자: "그거 취소해" / "필요없어졌어"
1. todos.md 의 해당 항목을 보류/취소 섹션으로 이동, 취소 날짜 기록
2. 미리알림 앱에서 해당 reminder 삭제:
   ```
   osascript -e 'tell application "Reminders"
       tell list "Claude"
           set r to first reminder whose name is "<제목>"
           delete r
       end tell
   end tell'
   ```
3. git commit: `todo: 취소 - <제목>`

### 조회 (list)
사용자: "오늘 할일 뭐야" / "할일 불러와" / "사이드프로젝트 뭐 있지"
1. Read 로 todos.md 읽기
2. 요청 범위에 맞는 섹션만 필터링해서 응답:
   - "할일" / "진행중" → 진행중 섹션
   - "사이드 프로젝트" → 사이드프로젝트 섹션
   - "오늘" / "이번주" → 진행중 중 마감일 기준 필터
   - "완료" → 최근 완료 10건
3. 텔레그램 세션이면 reply 로 전송

### 수정
- 제목 변경·마감일 변경 등은 todos.md 해당 라인 Edit + 미리알림 앱에서도 해당 항목 update

### 사이드 프로젝트
- `## 사이드 프로젝트 아이디어` 섹션에 추가
- 미리알림 앱엔 **기본적으로 추가하지 않음** (할일 아님)
- 사용자가 명시적으로 "이거 이번 주에 시작할게" 같이 말하면 진행중 섹션으로 승격

## 항목 매칭 규칙

사용자가 정확한 제목을 말하지 않는 경우(예: "아이콘 그거 끝났어"):
1. todos.md 진행중 섹션에서 부분 일치 검색
2. 후보가 1개면 바로 진행
3. 후보가 여러 개면 어느 것인지 한 줄로 확인 요청

## AppleScript 안전 수칙

- 제목에 큰따옴표(`"`), 백슬래시(`\`), 작은따옴표가 포함되면 쉘에서 깨질 수 있으므로 heredoc 또는 임시 파일로 넘기기
- 한글은 UTF-8 로 그대로 가능
- 실패 시(권한 거부 등) todos.md 업데이트는 진행하되 사용자에게 미리알림 동기화 실패를 한 줄로 보고

## git 커밋 메시지 규칙

- 추가: `todo: 추가 - <제목>`
- 완료: `todo: 완료 - <제목>`
- 취소: `todo: 취소 - <제목>`
- 이동: `todo: 이동 - <제목> (진행중 → 사이드)`
- 일괄: `todo: <N>건 업데이트` (3건 이상 묶을 때)

원격 저장소가 있으면 push. 없으면 로컬 커밋만.

## 홈페이지(daejong-page) 자동 동기화

todos.md 를 수정한 후에는 항상 개인 홈페이지(`ssamssae.github.io/daejong-page/todos.html`)에도 동일 내용 스냅샷을 반영해야 한다. 사용자는 이걸 수동으로 할 필요가 없도록 기대함.

**위치**: `/Users/user/daejong-page/todos/`
- 스냅샷 파일명: `YYYY-MM-DD.md` (하루 1파일, 버전 없이 날짜만)
- 인덱스: `/Users/user/daejong-page/todos/index.json`

**절차 (todos.md 커밋 완료 후):**

1. 스냅샷 작성 (덮어쓰기): `cp ~/todo/todos.md /Users/user/daejong-page/todos/YYYY-MM-DD.md`
   - 같은 날 이미 파일이 있으면 **덮어쓴다**. 이력은 git commit 히스토리에 남는다.
2. `Read /Users/user/daejong-page/todos/index.json` 으로 현재 상태 확인
3. index.json 업데이트: `entries` 배열에 해당 entry 추가·갱신
   ```json
   {
     "file": "YYYY-MM-DD.md",
     "date": "YYYY-MM-DD",
     "updated": "YYYY-MM-DDTHH:MM:SS+09:00"
   }
   ```
   - 같은 `file` 이 이미 있으면 `updated` 만 갱신. 중복 추가 금지.
   - `entries` 는 `date` 내림차순(최신이 먼저).
4. `cd /Users/user/daejong-page && git add todos/ && git commit -m "todos: YYYY-MM-DD — <요약>" && git push`

**커밋 메시지 요약**은 이번 변경의 핵심만 한줄:
- 추가 1건: `todos: YYYY-MM-DD — 추가: <제목>`
- 완료 1건: `todos: YYYY-MM-DD — 완료: <제목>`
- 여러 건: `todos: YYYY-MM-DD — N건 업데이트`

**주의:**
- 구 형식 버전 파일(`YYYY-MM-DD_vX.Y.Z.md`)이 과거에 남아 있어도 건드리지 않음. 새로 쓰는 건 무조건 버전 없는 `YYYY-MM-DD.md`.
- 홈페이지 동기화 실패해도 todos.md 업데이트는 유지. 동기화 실패는 사용자에게 한 줄로만 보고하고 계속 진행.

## 응답 포맷

**텔레그램**: 간결한 평문. 체크박스는 `[ ]` `[x]` 평문으로.
**터미널**: 마크다운 리스트 그대로 OK.

조회 응답 예시:
```
오늘 진행중 할일 3건:
1. 더치페이 아이콘 앱스토어 업로드 (마감 내일)
2. 메모요 위젯 기획 (마감 없음)
3. worklog 스킬 테스트 (마감 없음)

사이드 프로젝트 2건:
- 카페 추천 봇
- 영어회화 카톡봇
```

## 주의

- 절대 완료·취소된 항목을 삭제하지 말 것. 반드시 완료/보류 섹션으로 이동해서 이력 보존
- todos.md 전체를 매번 덮어쓰지 말고, Edit 으로 필요한 라인만 변경 (이력 diff 가 깨끗해짐)
- 민감 정보(비밀번호, API 키 등) 절대 저장 금지
