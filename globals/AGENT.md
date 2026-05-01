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
| `/worklog`, `/done`, `/usage` | 각 SKILL.md 참조 |

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

강대종님은 **Mac 본진 (MacBook Pro) + Mac mini (M1, 빌드/배포 엔진) + 윈도우 데스크탑 (3900X/2070S, WSL Ubuntu) + iPhone (Termius)** 4-노드 환경에서 Claude Code 를 사용한다. 기기마다 역할이 다르므로 현재 호스트에 맞게 행동한다. SoT 통합본은 `~/.claude/skills/MACHINE_ROLES.md`.

### 🍎 Mac 본진 = 지휘관 (Headquarter)
- **모든 설계/판단/메인 세션** + 최종 결정 (App Store/Play 심사 제출 클릭, PR 머지 결정, 자산 발급)
- **Telegram MCP 메인 봇**: `@MyClaude` (1봇 1세션 원칙)
- todos / done / worklog 쓰기 SoT
- iOS 메타·스크린샷 입력 (브라우저)
- launchd 자동화 호스트 (todo-reminder 등 — 단 빌드/배포 워커는 Mac mini 로 이전됨)
- main git push 권한 (consistency)

### 🏭 Mac mini = 빌드/배포 엔진 (M1 arm64, 24/7 워커, 2026-05-01 역할 보강)
- **iOS ipa 빌드 + codesign** (xcodebuild/Flutter) — 본진/WSL 에 빌드 위임 X
- **Android aab 빌드 + 서명** — keystore SoT (`~/apps/<app>/android/{key.properties,*-upload-keystore.jks}`)
- **App Store Connect 업로드** (altool / fastlane pilot)
- **Play Console 업로드** (fastlane supply / Android Publisher API)
- **launchd 워커**: night-builder v2.0a (야간 자동 빌드), night-runner v1 (03:00 KST read-only 점검). mail-watcher v5 는 2026-05-01 드롭됨.
- **API key/Service Account/세션쿠키 SoT** (`~/.claude/secrets/`) — 본진 분산 X
- raw Playwright + chromium (MCP 의존 X, headless 자동화)
- **챗봇 세션 추가 금지** — 세 번째 챗봇으로 쓰지 않음. 설계 판단/다음작업 결정 금지. 정해진 시간에 정해진 스크립트만, 결과 md + 텔레그램 보고만.
- **사람 손이 필요한 부분은 X**: 메타·스크린샷 입력 / 심사 제출 버튼 / API key 최초 발급 → 본진 강대종님
- **Apple Silicon arm64 셋업 — Rosetta 1회 설치 필수**: `sudo softwareupdate --install-rosetta --agree-to-license` 1회. iOS debug 시 Flutter `iproxy` 가 x86_64 라 Rosetta 없으면 dart VM attach 실패. macOS 재설치 시 첫 단계로 진행. release ipa/aab 빌드는 영향 X. issue `2026-04-29-rosetta-iproxy-attach.md` 참조. 자동 검사: irun SKILL 의 3단계 `ssh mac-mini 'pgrep -x oahd'` 가드.

### 🪟 WSL = 낮 즉응 작업자 (Worker, 2026-05-01 역할 보강)
- **Telegram MCP 봇**: `@Myclaude2` (Mac 봇과 분리. 같은 봇 양쪽 폴링 시 getUpdates 409 충돌)
- **wsl/\* 브랜치 직접 개발자 OK**: 코드/문서 수정 + commit + `git push origin wsl/<slug>` 가능. main 머지는 Mac 본진이 결정 (PR 또는 직접 머지)
- **main 직접 push 금지**: 모든 main 반영은 본진 검토 후
- **Android dev/debug 빌드 + 갤럭시 S24 adb 실기** OK (3900X + 2070S 활용, 단발 폰 검증용)
- 코드/로그 분석, 보고서 초안, Windows ADB 게이트 (S24 무선 토글), WSL→Windows Chrome CDP (Playwright attach)
- 무거운 작업 (장시간 리서치/리팩토링/배치), 실험적·파괴적 작업 (실패해도 본진 무영향)
- **launchd 잡 신규 추가 금지** (Mac mini 가 워커 호스트 SoT — 충돌 방지)
- **iOS 빌드 금지** (Xcode/Flutter iOS — 윈도우 불가)
- **Android release aab 빌드 + Play 배포 금지** (2026-04-29) — Mac mini 전담. release 효과 폰 검증 필요하면 mac-mini night-builder 산출물 받아 `adb install`
- **App Store Connect / Play Console 배포 클릭 금지** (강대종님 본진)

### 📱 iPhone Termius = 원격 컨트롤러
- Tailscale 경유로 Mac 본진 (`100.74.85.37`, user@) 또는 Mac mini / WSL SSH 접속
- 외부에서 가벼운 명령. 긴 세션은 본체 권장

### 병렬 작업 + 충돌 방지 원칙 (2026-05-02, 「지휘관 1명 원칙」 폐기 후 교체)

> Mac 본진과 WSL 이 동시에 작업하면서도 충돌하지 않게 만드는 안전한 병렬 작업 체계. 상세 8항은 `~/.claude/CLAUDE.md` 의 동명 섹션 참조. 본 AGENT.md 는 운영 상세만.

**역할 분담 (운영 사실):**

- **Mac 본진**: 메인 챗봇 세션, 강대종 직접 대화 1차 수신자, 최종 결정 권한.
- **WSL 세션**: 자율 작업자. wsl/* 브랜치 코드/문서 수정·PR + 자율 제안·자율 스코프 확장 OK. 단 main 직접 push / iOS·Android 빌드·스토어 업로드 / store/* 수정 / 정책 자체 수정 금지.
- **Mac mini**: 빌드/배포 엔진. iOS ipa / Android aab 빌드 + 서명, ASC / Play Publisher API 업로드, 24/7 launchd 워커. 챗봇 세션 X. 심사 제출 클릭은 강대종 본진.

**브랜치 컨벤션 (정책 #3):**

- Mac 본진: `mac/<task-name>-YYYY-MM-DD`
- WSL: `wsl/<task-name>-YYYY-MM-DD`
- main 직접 push 금지. PR 흐름.

**파일 충돌 방지 (정책 #4):**

- 작업 시작 전 `git fetch` + `git pull --ff-only`.
- 텔레그램에 **수정 예정 파일 목록** 선언. 다른 작업자가 이미 선언한 파일은 수정 금지.
- 같은 파일을 건드려야 하면 **즉시 중단 + 강대종 확인**.

**핸드오프 방향성:**

- **Mac 본진→WSL = 작업 지시 directive**: 목표 / 수정 파일 / 금지 사항 / 성공 기준 / 보고 형식 명시.
- **Mac 본진→Mac mini = 빌드/배포 트리거 (SSH)**: `ssh mac-mini "<자동화 스크립트>"`. 인터랙티브 챗봇 세션 X.
- **WSL→Mac 본진 = 결과 보고 report + 자율 후속 제안 OK**: 수행 작업 / 수정 파일 / 테스트 결과 / 다음 방향 제안 (이전 "다음 방향 제안 금지" 조항 폐기).
- **Mac mini→Mac 본진 = mac-report.sh 운반체**: 빌드/배포 결과 본진 tmux 'claude' 세션 자동 paste.
- 의견 충돌 / 정책 판단 애매함 = 즉시 중단 + 강대종 결정 위임.

**자기 정책 수정 (정책 #8):**

- 본 정책 자체 수정은 강대종 명시 1회 권한 부여 시에만. SCOPE 한정.
- 예외 없이 임의 변경 금지.

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
