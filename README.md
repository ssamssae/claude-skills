# claude-skills

강대종(ssamssae)의 개인 Claude Code 스킬 모음.

각 폴더는 독립된 Claude Code 스킬이며, `SKILL.md` 파일에 프론트매터 + 실행 흐름이 정의돼 있다.

## 스킬 목록

| 이름 | 용도 |
|---|---|
| [ctx](ctx/SKILL.md) | 현재 세션 진행 상황 요약 (완료/진행중/블로커/다음액션/할일) |
| [done](done/SKILL.md) | 오늘 한 일 체크리스트 자동 수집 (한 줄 체크박스 포맷, daejong-page/done 페이지 연동) |
| [irun](irun/SKILL.md) | Flutter 앱을 iPhone 에 clean + release run |
| [morning-reporter](morning-reporter/SKILL.md) | 매일 아침 일일업무 브리핑 (어제 커밋 + 오늘 할일 + 뉴스 + 주식) |
| [side-project-briefing](side-project-briefing/SKILL.md) | 매일 아침 사이드 프로젝트 아이디어 브리핑 (웹 리서치 기반) |
| [todo](todo/SKILL.md) | 할일·사이드 프로젝트 관리 (todos.md + 미리알림 앱 양방향 연동) |
| [todo-reminder](todo-reminder/SKILL.md) | 매일 밤 할일 리마인더 (오늘 한 것/못 한 것/내일 우선순위) |
| [usage](usage/SKILL.md) | Claude Code 토큰 사용량 ASCII 그래프 (ccusage 기반) |
| [weather-dust](weather-dust/SKILL.md) | 매일 아침 서울 날씨 + 미세먼지 텔레그램 알림 |
| [worklog](worklog/SKILL.md) | 하루 작업 내용 수집·요약해서 docs/worklog/YYYY-MM-DD.md 로 저장 + git 커밋·푸시 |

## 사용 방법

각 스킬은 Claude Code 의 스킬 시스템을 따른다. 사용하려면:

1. `~/.claude/skills/<스킬이름>/SKILL.md` 에 파일을 복사
2. Claude Code 세션에서 `/<스킬이름>` 슬래시 커맨드로 호출 (또는 자연어 트리거)

## 참고

- 일부 스킬은 이 환경에 특화돼 있음 (예: 텔레그램 chat_id, iPhone device id, 특정 프로젝트 경로)
- 기반 인프라: macOS + Ghostty + Claude Code + Telegram 봇 채널
- 스킬 전송 헬퍼: `~/.claude/channels/telegram/send.sh` (curl 기반 Bot API 호출)

## 라이선스

MIT.
