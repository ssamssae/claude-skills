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

## 빠른 자동 트리거 (상세는 AGENT.md)

- 할일: "OO 해야 해 / 끝났어 / 완료 / 취소 / 아이디어" → `~/todo/todos.md` + 미리알림 "Claude" 목록 + daejong-page 동기화
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
