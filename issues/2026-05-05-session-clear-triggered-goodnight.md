---
date: 2026-05-05
slug: session-clear-triggered-goodnight
status: open
---

# "세션클리어하자" → /goodnight 잘못 발화 사고

## 증상

강대종님이 "세션클리어하자" 입력 → /session-clear 대신 /goodnight 가 실행됨.
worklog 작성 + done 갱신 + insta-post + 텔레그램 최종 보고까지 전체 굿나잇 파이프라인 동작.

## 원인

session-clear 스킬(SKILL.md) 트리거 목록:
```
"세션 클리어", "클리어 해줘", "세션 초기화", "세션 지워줘", "/session-clear"
```

"세션클리어하자" 는 한 단어로 붙어 있고 "하자" 어미가 붙어 있어 목록에 없음.
→ Claude 가 트리거 매칭 실패 후 "자정 넘어 작업량 많음 = 하루를 닫는다" 로 오판해 /goodnight 발화.

## 영향

- 의도치 않게 worklog v1.0.1 + done 갱신 + 텔레그램 굿나잇 보고가 실행됨
- 결과물 자체는 유효하지만, 강대종님이 원한 건 그냥 /clear 였음
- /goodnight 가 굿나잇 기록 겸 세션 종료를 모두 해버려 "대형사고"로 인식됨

## 재발 방지

1. session-clear SKILL.md 트리거에 추가 필요:
   - "세션클리어하자", "클리어하자", "세션클리어", "클리어 해줘", "세션 닫자"
2. 자연어 발화 시 Claude 가 /session-clear vs /goodnight 를 구분하는 기준 명시:
   - "세션클리어" 류 → 무조건 /session-clear (/goodnight 절대 금지)
   - "굿나잇", "자야겠다", "오늘 마무리" 류 → /goodnight
3. 혼선 방지 원칙: "세션" + "클리어/지우기/초기화" 조합이 들어오면 /goodnight 우선순위 0, /session-clear 우선.

## 수정 필요 파일

- `~/.claude/skills/session-clear/SKILL.md` — 트리거 확장 + goodnight 발화 금지 명시
