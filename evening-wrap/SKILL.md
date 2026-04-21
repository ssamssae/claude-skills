---
name: evening-wrap
description: 매일 밤 22:30 저녁 마무리 통합 스킬. todo-reminder + done 을 단일 Claude 세션으로 실행해 저녁 리마인드 1건 + 체크리스트 홈페이지 반영을 한 번에 처리한다. 기존 todo-reminder(22:00) + done-auto(23:30) 2개 launchd 잡을 통합한 버전. 수동 호출도 가능.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# 저녁 마무리 통합 브리핑 (evening-wrap)

하루 마감 시 필요한 두 축을 **단일 Claude 세션** 으로 처리한다. 기존 todo-reminder + done 이 각자 돌던 것을 합쳐 **세션 1회 / 텔레그램 메시지 1건** 으로 축약 — 토큰 절약 + 알림 피로도 감소.

## 실행 순서

### 1단계: done (체크리스트 생성)

`~/.claude/skills/done/SKILL.md` 의 로직을 그대로 따른다.

- 오늘 한 일을 체크리스트 형식으로 수집 (~/daejong-page 커밋 + todos 완료 항목 + 기타 작업)
- `~/daejong-page/done/YYYY-MM-DD.md` 저장
- `done/index.json` 업데이트
- daejong-page git push

### 2단계: todo-reminder (저녁 리마인드)

`~/.claude/skills/todo-reminder/SKILL.md` 의 로직을 그대로 따른다.

- 오늘 한 일 / 못 한 일 / 내일 우선순위 요약
- 블로커 체크
- 텔레그램으로 단일 메시지 전송

### 3단계: 단일 메시지로 합쳐 전송

두 축을 한 텔레그램 메시지로:

```
🌙 저녁 마무리 (YYYY-MM-DD)

✅ 오늘 완료 (N건)
- ...
- ...

📋 내일 우선순위
- ...

⚠️ 블로커
- ...

🔗 https://ssamssae.github.io/daejong-page/done.html
```

## 모드

- **cron 자동 실행** (launchd 22:30): 전체 흐름 자동 수행
- **수동 호출** (`/evening-wrap`): 동일, 언제든 실행 가능

## 주의

- done / todo-reminder 개별 스킬은 **수동 호출 용도로 유지** (특정 축만 따로 보고 싶을 때)
- 자동 실행은 이 스킬 하나로만 — 중복 실행 피할 것
- launchd 세션 1회 절약 = **매일 ~20-50k 토큰 절감**
