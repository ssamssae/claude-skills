---
name: someday
description: Someday/Maybe 리스트(`~/todo/someday.md`) 관리. 해야 할 일은 아니지만 언젠가 해도 좋을 것들 — todos.md 와 분리해 우선순위 노이즈 없이 모음. 트리거 "someday", "언젠가", "/someday", "써뎀이", "야 이거 someday 에 박아줘", "이건 todo 말고 someday". 실제 할 일 되면 todos.md 로 promote.
allowed-tools: Bash, Write, Edit, Read
---

# Someday/Maybe 관리

## 데이터 소스

- **마스터 파일**: `~/todo/someday.md` (모아둠/승격됨/드롭 3개 섹션)
- **공개 미러**: `~/daejong-page/someday.md` (홈페이지 someday.html 가 fetch 해서 렌더)
- **버전 관리**: `~/todo/` 와 `~/daejong-page/` 둘 다 git. 모든 수정은 두 repo 동시 commit + push.
- **미리알림 앱 연동 안 함** — todos 와 달리 "지금 알림 받을 일" 이 아니므로.

## 호출 시 항상 먼저 할 일

### 0. 기기 라우팅 (맥 본진 집중)

`~/todo/someday.md` 와 `~/daejong-page/someday.md` 둘 다 Mac 로컬 마스터. 맥 아닌 기기에서 호출되면:

1. **조회 (read-only)** — `~/daejong-page/someday.md` 가 git 으로 동기화돼 있음. WSL/iPhone 에서도 Read 해서 응답 가능.
2. **쓰기 (추가/승격/드롭/수정)** — 맥에서만. 텔레그램 reply 로 chat_id 538806975 에 트리거 1줄 보내고 종료:

```
💭 /someday 트리거
액션: <추가|승격|드롭|수정>
항목: <제목>
Mac Claude 창에 아래 한 줄 복붙:
/someday <액션> <제목>
```

```bash
host=$(hostname)
if [[ "$host" != *MacBook* && "$host" != *MBP* ]]; then
  # 위 트리거 전송 후 종료
  exit 0
fi
```

### 1. 의도 파악

사용자 발화에서 액션 추출:
- "**추가**" / "박아줘" / "넣어줘" / "이건 someday" → 모아둠 섹션 항목 추가
- "**승격**" / "todo 로 올려" / "진짜 할거됐어" → 모아둠 → 승격됨 섹션 이동 + todos.md 의 진행중 섹션에 추가
- "**드롭**" / "취소" / "안 할 거야" → 모아둠 → 드롭 섹션 이동
- "**수정**" / "내용 바꿔" → 항목 본문 갱신
- 액션 명시 없이 "someday 보여줘" / "리스트" → 조회 모드로 모아둠 섹션 출력

### 2. Device Affinity Tag (추가 시 필수)

todos 와 동일 — 새 someday 항목 추가 시 제목 맨 앞에 디바이스 태그 1글자.

- `🍎` Mac 전용 / `🪟` WSL 전용 / `🤝` 어디서든

다음에 도메인 이모지 (🛠️ 인프라 / ✍️ 글쓰기 / 🎨 디자인 / 🛰️ 심사레이더 / 📸 인스타 / 🔧 자동화 등) 가 있으면 같이.

### 3. 수정 적용 (양쪽 파일 동시)

마스터 + 공개 미러 동시 갱신. 형식 차이 주의:

**`~/todo/someday.md` (마스터, 체크박스 포맷)**:
```
- [ ] 🤝 🛠️ 항목 제목 — 본문 설명. 배경, 트레이드오프, 진행 시 합의 사항 등.  (추가: YYYY-MM-DD)
```

- `[ ]` 빈 체크박스로 추가
- 승격 시 → 모아둠에서 제거 + 승격됨 섹션에 `(승격: YYYY-MM-DD → todos.md)` 표기로 이동
- 드롭 시 → 모아둠에서 제거 + 드롭 섹션에 `~~취소선~~ (드롭: YYYY-MM-DD) — 사유` 형식으로 이동

**`~/daejong-page/someday.md` (공개 미러, 마크다운 본문)**:
```
- 🤝 🛠️ **항목 제목** — 본문 설명.  *(추가: YYYY-MM-DD)*
```

- 체크박스 없음, 항목 제목 볼드, 메타 이탤릭
- 승격/드롭은 같은 섹션 이동 + 메타 형식 동일

### 4. 승격 시 todos.md 동시 갱신

"승격" 액션이면 `~/todo/todos.md` 의 `## 진행중` 섹션 맨 위에 추가 (디바이스 태그·도메인 이모지 유지). todos 의 0.5 reality preflight 룰 적용 — git pull --rebase 먼저, 그 후 추가.

### 5. 미리알림 동기화 안 함

todos 와 다르게 someday 는 reminders 앱 등록 X. "지금 알림" 이 아니라 "언젠가 후보" 라.

### 6. 양쪽 commit + push

```bash
# 1) ~/todo
cd ~/todo && git pull --rebase origin main 2>&1 | tail -3
git add someday.md
git commit -m "someday: <액션> <제목 짧게>"
git push origin main

# 2) ~/daejong-page
cd ~/daejong-page && git pull --rebase origin main 2>&1 | tail -3
git add someday.md
git commit -m "someday: <액션> <제목 짧게>"
git push origin main
```

승격 케이스면 todos.md 도 같이.

### 7. 응답

- 텔레그램 발화면 reply 로 한 줄 보고: "💭 someday 추가/승격/드롭 완료. <제목>". 홈페이지 링크 1줄 (https://ssamssae.github.io/daejong-page/someday.html).
- 동시에 현재 someday 모아둠 섹션 항목 수 표기.

## 조회 모드 (단순 listing)

"someday 보여줘" 류 발화엔 마스터 파일 읽어서 모아둠 섹션만 출력:

```
💭 Someday/Maybe (N개)
1. 🤝 🛠️ 핸드오프 가드 강화 (대안 C) — ... (추가: 2026-04-26)
2. ...
```

승격됨/드롭 섹션은 `/someday 전체` 같은 명시 요청 시에만 같이.

## /goodnight 연계

`/goodnight` step 5 에서 someday 변경사항 점검 단계가 있음 (skill `goodnight` SKILL.md 참조). 굿나잇 마무리할 때 "오늘 새로 떠오른 언젠가-할까-말까 거 있어요?" 묻고, 있으면 이 스킬 호출.

## 금지

- todos.md 의 진행중 섹션에 "언젠가" 항목 박지 말 것 — 우선순위 노이즈 만듦. someday 가 따로 있는 이유.
- 일상생활(병원/약속/쇼핑) 박지 말 것 — todos 와 동일 룰 적용.
- "남는 시간에" 같은 모호한 시점 표현 OK, 구체 마감일 박는 거 금지 (마감 있으면 그건 todo).

## 메모리 연계

- someday 항목 수가 많아지면(예: 30개+) MEMORY.md 인덱스 다이어트와 같은 결의 정리 필요 → 그땐 `/someday 다이어트` 별건으로.
