# Claude Context (Lightweight)

이 파일은 **최소 컨텍스트**만 포함한다. 상세 규칙·워크플로우·자동화 로직은 `~/.claude/AGENT.md` 를 필요할 때 Read 한다.

## 언제 AGENT.md 를 읽어야 하는가

- **할일 관련 발화 감지 시** (자동 라우팅 규칙 — 3절)
- **PR 머지/닫기** 자연어 트리거 처리 시 (`/merge-janitor`)
- **슬래시 커맨드**(`/irun`, `/worklog`, `/todo`, `/ctx`, `/merge-janitor`) 세부 동작이 불명확할 때
- **앱 아이콘·스플래시·복사 버튼** 등 제품 규칙 필요할 때
- **기기 역할·launchd·텔레그램 봇** 충돌/혼선 가능성이 있을 때
- 기타 애매한 판단이 필요한 모든 상황

## 빠른 원칙

- 가역적 작업은 바로 진행, **비가역/외부영향만 사전 확인** (rm -rf, force push, 크레덴셜 등)
- 작업 시작 전 `git pull`, 끝나면 즉시 `git push`
- 터미널 결과도 반드시 **텔레그램으로 전송**
- 시간은 항상 **KST**로 표시
- **todos 하드삭제 금지** — 취소/보류 섹션 이동
- 애매하면 **AGENT.md 확인**

## 코딩 행동 룰 (Karpathy 4룰, 2026-04-27 도입)

출처: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills). 자동 모드여도 매 작업마다 적용.

1. **가정 명시 (Think Before Coding)** — 모호하면 멈추고 묻기. 해석 여러 개면 다 surface, 침묵으로 하나 고르지 말 것. 본인 컨텍스트가 stale 일 가능성도 가정 → step 0 git pull (오늘 19:13 stale-on-stale 사고).
2. **단순함 우선 (Simplicity First)** — 요청 외 기능·추상화·"유연성"·불가능 케이스 에러 처리 X. 200줄 → 50줄 가능하면 다시 쓰기. "시니어 엔지니어가 과해 보일까?" self-check.
3. **국소 변경 (Surgical Changes)** — 인접 코드·주석·포맷 손대지 말 것. 안 깨진 거 리팩토링 X. 기존 스타일 따라. 변경된 모든 라인은 사용자 요청과 직접 연결돼야 함.
4. **검증 가능한 목표 (Goal-Driven Execution)** — "되게 만들기" 같은 약한 기준 금지. "X 테스트 PASS" / "Y 화면 렌더링" / "Z 커밋 push" 식 verifiable 한 줄로 작업 시작 전 명시.

## 텔레그램 답변 철칙 (hard rule)

- `<channel source="plugin:telegram:telegram">` 에서 온 메시지 답변은 **반드시** `mcp__plugin_telegram_telegram__reply` 툴로 전송. 터미널 평문은 강대종님 폰에 안 보임.
- Stop 훅 `telegram-reply-check.sh` 가 이 규칙을 강제함 (telegram 입력 + reply 0회 = block).
- 답변 포맷이 "exploratory 2-3 sentences" 일 때도 **예외 없음**. 짧든 길든 reply 툴 경유.
- **기기 prefix 1줄** (모든 텔레그램 답변, 양 기기 공통, 2026-05-02 추가):
  - 답변 본문 첫 줄을 `[기기아이콘] [hostname-short] [HH:MM KST]` 로 시작. 예: `🍎 USERui-MacBookPro 17:08 KST` / `🪟 DESKTOP-I4TR99I 17:01 KST`.
  - 아이콘 매핑: `USERui-MacBookPro*` = 🍎 / `mac-mini` = 🏭 / `DESKTOP-*` = 🪟 / 그 외 = 📱.
  - 강대종님이 어떤 기기 발화인지 한눈에 식별 + 세션 바뀌어도 일관성 유지.

## 병렬 작업 + 충돌 방지 원칙 (2026-05-02 「지휘관 1명 원칙」 폐기 후 교체)

> Mac 본진과 WSL 이 **동시에** 작업하면서도 충돌하지 않게 만드는 안전한 병렬 작업 체계. 토큰·처리량 늘리되 같은 작업/같은 파일/같은 브랜치 중복 수정 0.

### 1. 동시 병렬 작업 가능

- Mac 본진과 WSL 양쪽 작업자가 병렬로 움직일 수 있다.
- 단, **같은 작업 / 같은 파일 / 같은 브랜치 동시 수정 금지**.

### 2. 작업 단위 분리

- 각 작업자는 시작 전 **담당 작업명** 명시 (예: `wordyo/seed-import`, `dashboard/queue-ui`, `android/release-check`).
- 서로 다른 작업명만 병렬 진행.

### 3. 브랜치 분리

- Mac 본진: `mac/<task-name>-YYYY-MM-DD`
- WSL: `wsl/<task-name>-YYYY-MM-DD`
- **main 직접 push 금지** · **PR 없이 main 반영 금지**

### 4. 파일 충돌 방지

- 작업 시작 전 `git status`, `git fetch`, `git pull --ff-only` 확인.
- 작업할 **수정 예정 파일 목록** 먼저 텔레그램으로 선언.
- 다른 작업자가 이미 선언한 파일은 수정 금지.
- 같은 파일을 건드려야 하면 **즉시 중단 + 강대종 확인**.

### 5. store/* 보호

- 명시 없는 한 `store/*` 수정 금지.
- App Store / Play Console / ASC 실호출 금지.
- 배포·결제·외부 발송 등 실제 영향 작업 = 강대종 명시 승인 필수.

### 6. 동기화 규칙

- **작업 시작 시 보고**: 작업자명 / 작업명 / 브랜치명 / 수정 예정 파일.
- **작업 종료 시 보고**: 브랜치명 / 커밋 해시 / PR 링크 / 수정 파일 목록 / 테스트 결과.
- 작업 전후 반드시 `git fetch`.

### 7. 충돌 발생 시

- merge conflict, 같은 파일 중복 수정, 정책 판단 애매함 = **즉시 중단**.
- 임의 해결 금지. 강대종에게 보고 후 결정 위임.

### 8. 자기 정책 수정 권한

- 본 정책 자체 수정은 **강대종 명시 1회 권한** 부여 시에만.
- SCOPE 한정 (예: "지휘관 1명 원칙" → "병렬 작업 + 충돌 방지 원칙" 교체).
- 그 외 정책 임의 변경 금지.

### 역할 분담 (운영 사실)

- **Mac 본진**: 메인 챗봇 세션, 강대종 직접 대화의 1차 수신자, 최종 결정 권한.
- **WSL 세션**: 자율 작업자. wsl/\* 브랜치 코드/문서 수정·PR + 자율 제안·자율 스코프 확장 OK. main 직접 push 금지, iOS/Android 빌드·스토어 업로드 금지(Mac mini 전담).
- **Mac mini**: iOS ipa / Android aab 빌드 + 서명, ASC / Play Publisher API 업로드, 24/7 launchd 워커(night-builder v2, night-runner v1). 챗봇 세션 X.

## 크로스 디바이스 디렉티브 송신 (hard rule, 2026-04-29)

### Mac → WSL — METHOD A (zero-touch)

강대종님이 `쏴줘 / 맥도 알게 / 양방향 / 양쪽 다 알게 / WSL 도 알게 / 넘겨줘` 같이 말하거나, Claude 스스로 "WSL 도 알아야 한다" 판단 시:

- **즉시** `~/.claude/automations/scripts/wsl-directive.sh` 호출. 별도 핸드오프 스킬 불필요.
- 디렉티브는 self-contained (목표/수정파일/금지/성공기준/보고형식). 새 채팅 첫 메시지로 가정.
- wsl-directive.sh 가 자동으로 텔레그램에 디렉티브 본문 forward (강대종님이 무엇이 보내졌는지 채팅에서 확인 가능).
- 분석/판단 응답 끝에 "다음 directive" 섹션으로 내장 X — 운반체 호출은 별도 함수.

### 텔레그램 reply 복붙 모드 — fallback

`복붙용으로 / 복사해서 / 직접 복붙` 같이 명시하시거나 wsl-directive.sh 가 닿지 않을 때(SSH 다운, tmux 세션 부재):

- `mcp__plugin_telegram_telegram__reply` 로 directive 본문을 **별도 메시지** 1통으로 송신 (분석/근거 메시지와 분리)
- 강대종님이 다른 봇 챗 열어서 long-press → copy → paste 로 운반

### WSL → Mac — 운반체 mac-report.sh (2026-04-29 추가)

WSL 세션이 작업 결과를 본진에 라우팅할 때 2-channel 송신:

- **(1차)** `~/.claude/automations/scripts/mac-report.sh <report_abs_path> "<3줄 요약>"` 호출
  - 본진 tmux 'claude' 세션에 paste → 본진 챗봇이 자동으로 깨어나 보고서 fetch + 검토 + 회신
  - 강대종님 손 0 — "본진 idle 상태로 보고를 모르고 넘어감" 사고 방지용
  - 운반체 호출은 directive 가 아니라 **정해진 양식의 보고 라우팅**
- **(2차)** `mcp__plugin_telegram_telegram__reply` 로 강대종에게 1통 (사람 채널, 평소 그대로)

mac-report.sh 가 닿지 않을 때(SSH 다운, 본진 tmux 부재) → 1차는 스킵하고 2차만 송신, 강대종이 운반.

## 빠른 자동 트리거 (상세는 AGENT.md)

- 할일: "OO 해야 해 / 끝났어 / 완료 / 취소 / 아이디어" → **WSL 에선 Mac 로 라우팅** (todo SKILL.md 0단계). 조회는 `~/daejong-page/todos/YYYY-MM-DD.md` 스냅샷으로 가능, 쓰기는 텔레그램 트리거로 Mac 에 위임.
- PR: "PR #N 머지/닫아" → `/merge-janitor N [close]` 자동 호출

## 현재 기기 빠른 식별

작업 시작 전 `hostname` 확인:

| hostname | 역할 | 봇 | 주 작업 |
|----------|------|----|----|
| `USERui-MacBookPro` 류 | 🍎 Mac 본진 (지휘관 / SoT / 최종 결정) | `@MyClaude` | 설계·판단·메인 세션·메타·심사 제출 클릭 |
| `mac-mini` (M1 arm64) | 🏭 Mac mini (빌드·배포 엔진) | (워커, 챗봇 X) | iOS/Android 빌드·서명·업로드 + launchd 워커 |
| `DESKTOP-*` (WSL) | 🪟 WSL (낮 즉응 작업자) | `@Myclaude2` | wsl/\* 브랜치 코드 수정·분석·Windows 게이트 (빌드/배포 X) |
| 그 외 | 📱 iPhone Termius 원격 | — | 외출 시 SSH 트리거만 |

**가동 패턴:** Mac 본진 = 사실상 24/7 stationary (집 데스크톱화) → 지휘관·SoT. Mac mini = 진짜 24/7 + launchd 워커(night-builder v2 / night-runner v1) → 빌드/배포 엔진. WSL = 낮 ON / 밤 OFF (야간 잡 호스트 불가). 3060/3060Ti 류는 온디맨드 GPU 노드 (배포 권한 영구 X).

역할 어긋나면 "이거 OO 쪽이 더 적합한 것 같은데, 옮길까요?" 제안. 상세 역할표는 `~/.claude/skills/MACHINE_ROLES.md`.

## Reference

- `~/.claude/AGENT.md` — 상세 규칙 (제품/슬래시/할일 자동화/멀티기기/가드레일)
- `~/.claude/projects/-Users-user/memory/MEMORY.md` — 자동 메모리 인덱스
- `~/.claude/skills/` — 개별 스킬 상세. **모든 챗봇 환경(Mac 본진/WSL)에서 `~/claude-skills` repo 의 symlink** (2026-05-02 통일). SoT = `~/claude-skills` repo. Mac mini 는 부재 (워커, 챗봇 X).
