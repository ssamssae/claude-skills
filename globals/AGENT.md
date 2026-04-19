# AGENT.md — Claude Code 상세 규칙

`CLAUDE.md`(경량 포인터)에서 "자세한 규칙이 필요하다"고 판단될 때 이 파일을 Read 한다. 매 세션 자동 로드되지 않으므로, 구체 판단·실행 시점에만 참조.

---

## 1. 제품/UI 규칙

- 텍스트 콘텐츠 제공 시 **항상 복사 버튼 위젯**으로
- **앱 아이콘** 생성/변환 시 투명 채널 제거 (Apple 심사 리젝 방지)
- **모바일 앱 스플래시**: 다크 테마 + 노란색 아이콘 + 1.5초 페이드아웃 (더치페이 스타일)

---

## 2. 슬래시 커맨드 레퍼런스

| 커맨드 | 용도 |
|--------|------|
| `/irun` | Flutter 앱을 아이폰(기본 강대종의 iPhone)에 clean + release run |
| `/worklog [YYYY-MM-DD]` | `docs/worklog/YYYY-MM-DD_vX.Y.Z.md` 저장 후 git 커밋·푸시. 같은 날짜 여러 번 실행해도 이전 버전 유지, 새 스냅샷 추가 |
| `/todo` | 할일·사이드프로젝트 관리. `~/todo/todos.md` + 미리알림 앱 "Claude" 목록 연동 |
| `/ctx` | 세션 진행 상황 요약 (완료/진행중/블로커/다음액션/할일). "ctx" 한 단어도 호출됨 |
| `/merge-janitor N [close]` | WSL night-runner janitor PR 머지/닫기. 자세한 규칙은 3절 참조 |
| `/worklog`, `/done`, `/usage`, `/review-status-check` | 각 SKILL.md 참조 |

### /merge-janitor 자연어 트리거
- "PR #N 머지", "PR #N 닫아", "janitor PR 3 merge", "PR 5번 닫자" → `/merge-janitor N [close]` 자동 호출
- "머지"/"merge" 키워드 → 머지 모드
- "닫아"/"close" 키워드 → 닫기 모드

---

## 3. 할일 관리 자동 규칙 (최우선)

사용자가 다음과 같이 말하면 **`/todo` 스킬을 명시적으로 호출하지 않아도** 자동으로 처리한다.

| 발화 패턴 | 동작 |
|-----------|------|
| "오늘 OO 해야 해", "이번 주까지 OO 마감", "OO 추가해줘" | 할일 추가 |
| "OO 끝났어", "OO 완료", "OO 했어" | 완료 표시 |
| "할일 뭐야", "오늘 뭐해야 해", "사이드 프로젝트 뭐 있지" | 조회 |
| "그거 안 할래", "OO 취소" | 취소 (**하드삭제 금지** — 보류/취소 섹션 이동) |
| "이런 거 해보면 어떨까", "사이드 프로젝트 아이디어 있어" | 아이디어 추가 |

### 실행 순서
1. `~/todo/todos.md` Read
2. 해당 섹션 Edit
3. AppleScript 로 미리알림 앱 동기화 (iCloud 계정 **"Claude"** 목록 고정 — 다른 목록 섞지 말 것)
4. `~/todo/` 에서 git commit
5. **daejong-page 홈페이지 동기화**:
   - `cp todos.md ~/daejong-page/todos/YYYY-MM-DD.md`
   - `index.json` 업데이트
   - daejong-page git commit/push

상세 규칙: `~/.claude/skills/todo/SKILL.md`

---

## 4. 멀티 기기 운영 (Multi-device)

강대종님은 **Mac (MacBook Pro) + 윈도우 데스크탑 (3900X/2070S, WSL Ubuntu) + iPhone (Termius)** 3-way 환경에서 Claude Code 를 사용한다. 기기마다 역할이 다르므로 현재 호스트에 맞게 행동한다.

### 🍎 Mac = 본진 (Headquarter)
- **모든 launchd 자동화의 단일 진실 소스** (morning-briefing, todo-reminder, review-status-check 등)
- **Telegram MCP 메인 봇**: `@MyClaude` (1봇 1세션 원칙)
- **iOS 빌드** 전담 (Xcode/Flutter iOS — 윈도우 불가)
- 메인 git push 권한 (consistency)
- 일상 짧은 작업·실시간 대화

### 🪟 윈도우 데스크탑 = 전위 (Worker)
- **Telegram MCP 봇**: `@Myclaude2` (Mac 봇과 분리. 같은 봇 양쪽 폴링 시 getUpdates 409 충돌)
- **Android 빌드/에뮬레이터** 전담 (3900X + 2070S 활용)
- 무거운 작업 (장시간 리서치/리팩토링/배치)
- 실험적·파괴적 작업 (실패해도 본진 무영향)
- **launchd 잡 신규 추가 금지** (본진 충돌 방지)

### 📱 iPhone Termius = 원격 컨트롤러
- Tailscale 경유로 Mac (`100.74.85.37`, user@) 또는 데스크탑 (`100.80.253.65`, ssamssae@) SSH 접속
- 외부에서 가벼운 명령. 긴 세션은 본체 권장

### 공유 vs 분리
- ✅ **공유 (git: ssamssae/claude-skills)**: 스킬, 글로벌 CLAUDE.md/AGENT.md, 키바인딩
- ❌ **기기별 분리**: 메모리 (`~/.claude/projects/.../memory/`), 세션 히스토리, launchd plist (Mac 전용), 텔레그램 access.json (각자 봇)

### 함정 (절대 피할 것)
1. 같은 텔레그램 봇을 양쪽에서 폴링 → 409 Conflict 무한 충돌
2. 양쪽에서 같은 git repo 동시 push → conflict. 시작 전 `git pull`, 끝나면 즉시 `git push`
3. 양쪽에서 같은 launchd 잡 동시 실행 → 메시지 중복, 토큰 2배. launchd 는 Mac 전용
4. 메모리 강제 동기화 시도 → 컨텍스트 분기는 자연스러운 것, 강제 sync 시 혼란

### 현재 호스트 인지
작업 시작 전 `hostname` / `uname` 으로 확인. CLAUDE.md 의 역할에 어긋나는 작업이면 "이거 데스크탑 쪽이 더 적합한 것 같은데, 옮길까요?" 같이 제안.

---

## 5. 보안·안전 가드레일

- bypass 모드여도 `rm -rf`, force push, 크레덴셜 관련 작업은 사전 확인
- todos 하드삭제 금지 (보류/취소 섹션 이동)
- launchd 자식 claude 호출 시 `--settings settings-launchd.json` 으로 telegram 플러그인 disable (중첩 세션 충돌 방지)

---

## 6. 참고 경로

- `~/.claude/CLAUDE.md` — 경량 포인터 (매 세션 자동 로드)
- `~/.claude/skills/` — 개별 스킬 상세 규칙
- `~/.claude/projects/-Users-user/memory/MEMORY.md` — 자동 메모리 인덱스
- `~/todo/todos.md` — 할일 원본
- `~/daejong-page/` — 개인 홈페이지 (ssamssae.github.io/daejong-page)
