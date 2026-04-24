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

## 텔레그램 답변 철칙 (hard rule)

- `<channel source="plugin:telegram:telegram">` 에서 온 메시지 답변은 **반드시** `mcp__plugin_telegram_telegram__reply` 툴로 전송. 터미널 평문은 강대종님 폰에 안 보임.
- Stop 훅 `telegram-reply-check.sh` 가 이 규칙을 강제함 (telegram 입력 + reply 0회 = block).
- 답변 포맷이 "exploratory 2-3 sentences" 일 때도 **예외 없음**. 짧든 길든 reply 툴 경유.

## 크로스 디바이스 핸드오프 철칙 (hard rule)

다른 기기 Claude 세션(WSL↔Mac)에 전달할 지시문은 **반드시 별도 텔레그램 메시지**로 보낸다.

- **복붙 단위 1개 = 텔레그램 메시지 1개** (분석/근거/답변과 절대 섞지 말 것)
- 각 directive 메시지는 **self-contained** — 새 채팅 첫 메시지로 가정하고 컨텍스트·판정결과·할일·금지사항 모두 포함
- 분석 답변 끝에 "다음 directive" 섹션으로 내장하는 것 = 위반
- 시그널 키워드 (본인 답변에서): "WSL Claude 용 복붙 directive", "Mac 세션에 넘겨", "복붙해서 전달", "넘겨줘" → 이 순간 즉시 `reply` 툴 호출을 **별도 메시지**로 분리
- 위반 감지 시 바로 찢어서 재전송

## 빠른 자동 트리거 (상세는 AGENT.md)

- 할일: "OO 해야 해 / 끝났어 / 완료 / 취소 / 아이디어" → **WSL 에선 Mac 로 라우팅** (todo SKILL.md 0단계). 조회는 `~/daejong-page/todos/YYYY-MM-DD.md` 스냅샷으로 가능, 쓰기는 텔레그램 트리거로 Mac 에 위임.
- PR: "PR #N 머지/닫아" → `/merge-janitor N [close]` 자동 호출

## 현재 기기 빠른 식별

작업 시작 전 `hostname` 확인:

| hostname | 역할 | 봇 | 주 빌드 타겟 |
|----------|------|----|----|
| `Daejongs-MacBook-Pro` 류 | 🍎 Mac 본진 (launchd SoT) | `@MyClaude` | iOS |
| `DESKTOP-*` (WSL) | 🪟 윈도우 전위 | `@Myclaude2` | Android |
| 그 외 | 📱 iPhone Termius 원격 | — | — |

역할 어긋나면 "이거 OO 쪽이 더 적합한 것 같은데, 옮길까요?" 제안.

## Reference

- `~/.claude/AGENT.md` — 상세 규칙 (제품/슬래시/할일 자동화/멀티기기/가드레일)
- `~/.claude/projects/-Users-user/memory/MEMORY.md` — 자동 메모리 인덱스
- `~/.claude/skills/` — 개별 스킬 상세
