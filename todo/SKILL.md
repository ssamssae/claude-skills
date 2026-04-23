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

### 0. 기기 라우팅 (맥 본진 집중 실행)

/todo 는 `~/todo/todos.md` (Mac 로컬) + macOS Reminders AppleScript + `/Users/user/daejong-page/...` 하드코딩 경로를 쓰므로 **맥 전용**.  맥 아닌 기기(WSL/iPhone)에서 호출되면 아래 규칙 적용:

1. **조회 (read-only)** — `~/daejong-page/todos/YYYY-MM-DD.md` 스냅샷이 git 으로 동기화돼 있음. WSL 에서도 Read 해서 응답 가능. 마감일/오늘 진행중 조회까지는 여기서 끝.
2. **쓰기 (추가/완료/취소/이동/수정)** — 맥에서만 가능. 텔레그램 reply 로 chat_id 538806975 에 아래 본문 전송하고 종료 (/to-iphone → /land 패턴):

```
✅ /todo 트리거
액션: <추가|완료|취소|이동|수정>
항목: <제목>
Mac Claude 창에 아래 한 줄 복붙:
/todo <액션> <제목>
```

```bash
host=$(hostname)
if [[ "$host" != *MacBook* && "$host" != *MBP* ]]; then
  # 조회면 daejong-page 스냅샷 읽고 답변, 쓰기면 위 트리거 전송 후 종료
  :
fi
```

텔레그램 전송 실패 시엔 "Mac 세션 깨어있으면 Mac 에서 /todo 로 처리해달라" 안내로 fallback.

### 0.5. Reality Preflight (쓰기·추천 직전 의무)

**목적**: 다른 기기(WSL 등)가 먼저 일을 끝내고 todos 에 반영 안 했을 때, Mac 이 stale todos 만 보고 "아직 남은 할일" 로 추천하거나 잘못 편집하는 것을 차단. (근거: `issues/2026-04-21-mac-wsl-todos-desync.md`)

아래 상황에서 **반드시** 프리플라이트 실행:
- "오늘 할일 추천" / "오늘 뭐 해야 해" 류 **추천 요청**
- `[x]` 완료 처리 / 보류·취소 이동 등 **상태 변경 쓰기**
- `Edit`/`Write` 로 todos 파일 수정 직전

절차 (3단계):

1. **git pull --rebase**
   ```bash
   cd ~/daejong-page && git pull --rebase origin main 2>&1 | tail -3
   ```
   다른 기기가 todos 를 이미 업데이트했으면 여기서 반영됨.

2. **최근 24h GitHub 활동 스캔**
   ```bash
   gh repo list ssamssae --limit 20 \
     --json name,pushedAt,description,visibility \
     | python3 -c 'import sys,json,datetime as dt; data=json.load(sys.stdin); now=dt.datetime.now(dt.timezone.utc); [print(f"{r[\"name\"]:20} {r[\"pushedAt\"]} {r.get(\"description\",\"\")[:60]}") for r in data if (now-dt.datetime.fromisoformat(r["pushedAt"].replace("Z","+00:00"))).total_seconds() < 86400]'
   ```

3. **열린 todos × 최근 repo 교차검사**
   - 열린 todos 항목의 제목/설명에서 3글자 이상 토큰 추출
   - 2번의 최근 repo name/description 토큰과 **2개 이상 겹치면 매칭 후보**
   - 매칭 후보 있으면 추천/편집 전에 텔레그램으로 먼저 경고:
     ```
     ⚠️ Reality Preflight 경고
     열린 할일 "<제목>" 이 최근 24h 내 push 된 repo <name> 과 겹칩니다.
     WSL 등 다른 기기에서 이미 진행중/완료일 수 있습니다.
     확인 방법: gh api repos/ssamssae/<name>/commits
     그대로 추천/편집 진행할까요? (y/수정)
     ```
   - 사용자 `y` 받으면 계속, 다른 답이면 사용자 지시대로.

4. 매칭 없으면 바로 step 1 로 진행. 조용히 다음 단계로.

**원칙**:
- **조회만** 하는 경우(단순 "할일 리스트 뭐야")엔 step 1 만 해도 OK. Step 2-3 은 추천/편집 때 의무.
- 프리플라이트 실패(네트워크 오류, gh 미인증 등)면 soft-fail — 사용자에게 "프리플라이트 스킵했음, 수동 교차검증 권장" 한 줄 보고 후 진행.
- 프리플라이트는 리드온리(git pull 은 merge conflict 없으면 가역). 파괴적 작업 아님.

### 0.6. Device Affinity Tag (추가·재활성화 시 필수)

**규칙**: 새 todo 추가 시(또는 취소된 항목 재활성화 시) 제목 맨 앞에 디바이스 태그 1글자를 붙인다. 기존 이모지(✍️🎨📸🛰️ 등)보다 **먼저** 놓는다.

- `🍎` — Mac 전용 (iOS 빌드, App Store Connect, macOS GUI 자동화, xcodebuild 의존 작업)
- `🪟` — WSL 전용 (Android 네이티브 빌드, Windows 전용 툴, 갤럭시 실기 연결)
- `🤝` — 어디서든 (Flutter 코드 편집, 문서 작성, Python 스크립트, 웹 툴)

**판정 가이드**:
- "iOS", "App Store", "altool", "Xcode", "xcrun" → 🍎
- "Android", "aab", "Play Console", "갤럭시", "adb" → 🪟
- 그 외 코드/문서/스크립트 → 🤝

**`🤝` 시작 시 클레임 규칙** (코드 편집 충돌 방지):
1. 작업 시작 직전 해당 repo(들) `git pull` 먼저
2. `~/todo/todos.md` 해당 라인을 `- [ ] 🤝 [🍎진행중]` 또는 `[🪟진행중]` 로 Edit + commit+push
3. 작업 완료 처리 시 진행중 마커 제거 (완료 섹션으로 이동할 때 자동)

**기존 항목 소급 태깅**: 태그 없는 열린 항목을 다음 번 터치(수정·조회 확인) 시 태그 추가. 일괄 수정은 하지 않음(diff 노이즈 방지).

**기기 미스매치 시**: `🍎` 를 WSL 세션이 잡거나 `🪟` 를 Mac 세션이 잡으면 "이거 OO 쪽이 더 적합한 것 같은데 옮길까요?" 먼저 제안 (CLAUDE.md 의 '역할 어긋나면 제안' 규칙 구체화).

예시:
```
- [ ] 🍎 🎯 더치페이/약먹자 iOS 심사 제출 마무리 ...
- [ ] 🪟 🍅 포모도로 Android AAB Play Console 업로드 ...
- [ ] 🤝 ✍️ 바이브코딩 뉴스레터 Ep.1 원고 작성 ...
```

### 1. 로컬 실행 (맥 본진)

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

### 삭제 (delete / cancel / archive)
사용자: "그거 취소해" / "필요없어졌어" / "지우자" / "빼자" / "삭제" / "TODO 에서 빼" / "정리해"

**중요: 절대 하드 삭제 금지.** 사용자가 "지우자"·"삭제해"라고 해도 todos.md 라인을 제거하지 말 것. 반드시 **보류/취소 섹션으로 이동**하여 이력 보존 + daejong-page `/cancelled.html` 에 자동 반영되게 한다. 사용자가 보는 "취소한 할일 무덤" 페이지가 이 섹션에서 파싱된다.

1. todos.md 의 해당 항목을 보류/취소 섹션으로 이동:
   - 형식: `- [-] ~~<제목>~~ (취소: YYYY-MM-DD) — <사유>`
   - 사유: 사용자가 말한 이유를 한 줄로. 사용자가 "머리속에 있음"·"외움"·"사유 생략" 같이 말해 사유 기록을 거부하면 → `(사유 비공개, 강대종님 메모)` 로 표기 (라인 자체는 유지).
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
- 파일명은 무조건 `YYYY-MM-DD.md` (버전 번호·시간 접미사 금지). 하루에 여러 번 수정해도 같은 파일을 덮어쓴다. 이력은 git commit 로그로 본다.
- 과거 `YYYY-MM-DD_vX.Y.Z.md` 형식 파일은 이미 정리 완료. 혹시 발견되면 `YYYY-MM-DD.md` 로 rename + index.json 의 version 필드 제거.
- index.json 는 `entries` 배열(신규 포맷). 구 `versions` 필드가 남아 있으면 마이그레이션해서 entries 로 통일.
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

- 절대 완료·취소된 항목을 하드 삭제하지 말 것. 반드시 완료/보류 섹션으로 이동해서 이력 보존. 보류/취소 섹션은 daejong-page `/cancelled.html` 에 자동 파싱되어 공개된다.
- 사용자가 "지우자"·"삭제"라고 해도 todos.md 라인을 제거하는 것이 아니라 **취소로 아카이브**(보류/취소 섹션으로 이동)한다는 뜻으로 해석. 하드 삭제를 원하면 사용자가 "완전 삭제"·"라인 제거"처럼 명시적으로 말해야 함.
- todos.md 전체를 매번 덮어쓰지 말고, Edit 으로 필요한 라인만 변경 (이력 diff 가 깨끗해짐)
- 민감 정보(비밀번호, API 키 등) 절대 저장 금지
