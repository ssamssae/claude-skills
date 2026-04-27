---
from: wsl
to: mac
sent_at: 2026-04-27T18:15:00+09:00
status: open
---

🪟 [WSL→MAC] 새 스킬 `/session-close` 시드됨 — Mac 에서도 인지하고 사용할 수 있게 sync 부탁해요.

목표:
강대종님이 "세션초기화 / 세션 재시작 / 세션 클리어 해도 돼?" 류 발화로 Claude Code 세션을 닫으려 할 때 자동 발동되는 신규 스킬 `/session-close` 가 WSL 본진(2026-04-27 18:05 KST 시드 + push, 커밋 c95c449)에서 만들어졌음. Mac claude-skills clone 에 git pull 로 받아서 harness 가 자동 인식하도록 맞춰주면 됨.

컨텍스트:
- 강대종님 요청 시점: 2026-04-27 17:59 KST WSL chat
- 결정사항 4가지 (강대종님 픽):
  1. 트리거 = "세션초기화 / 세션 재시작 / 세션 클리어 해도 돼?" + "/session-close" + "/session-end"
  2. 후보 = 미완료가 아니라 "어디까지 진행했다 기록" (다음 세션 인계용)
  3. someday 박을 후보 = 이번 세션에서 답변에 추가작업으로 제안만 한 후속안들
  4. 시점 = 지금 (이 스킬 먼저 시드 → 그다음 심사레이더 v0.2 S24 시각검증)
- 스킬 파일: `session-close/SKILL.md` (claude-skills repo 루트 직속)
- harness 자동 매칭됨 (frontmatter description 경유). WSL 에서는 sync 후 사용 가능 목록에 정상 등록 확인됨.

목표 흐름:
1. claude-skills repo 에서 `git pull --rebase --autostash origin main` (커밋 c95c449 받기)
2. `~/.claude/skills/session-close/SKILL.md` 도착 확인 (양쪽 폴더 동기화)
3. SKILL.md 본문 한 번 훑고 동작 흐름 인지 (6단계: 진행 기록 수집 → 후속안 추출 → 텔레그램 후보 리스트 → 강대종님 컨펌 → 저장(메모리 + someday 트리거) → 그린라이트)
4. ack — 강대종님께 텔레그램 reply 1줄 ("session-close 스킬 인지 OK, /clear 직전 사용 가능")

할일:
- (a) `cd /Users/user/claude-skills && git pull --rebase --autostash origin main` (또는 Mac 측의 claude-skills 절대경로)
- (b) `cd ~/.claude/skills && git pull --rebase --autostash origin main` (harness 가 읽는 clone)
- (c) `ls ~/.claude/skills/session-close/SKILL.md` 으로 도착 확인
- (d) SKILL.md 한 번 Read (분량 약 200줄, 6단계 동작 명세)
- (e) ack 답신 핸드오프 파일 1개 push: `handoffs/2026-04-27-XXXX-mac-wsl-session-close-skill-reply.md` (frontmatter `reply_to: handoffs/2026-04-27-1815-wsl-mac-session-close-skill.md`, status `acked`, 본문은 도착 확인 + 세션 인지 결과 1-2 paragraph)
- (f) 강대종님 텔레그램 reply 1줄 (chat_id 538806975)

금지사항:
- session-close/SKILL.md 본문 직접 수정 금지 (v0.2 다듬기는 강대종님 첫 사용 후 별건 작업으로)
- session-close 디렉토리 새 파일 추가 금지 (스킬 표면 깨끗하게 유지, v0.1 시드 그대로 평가 받기)
- 강대종님 reject 대응 흐름 침범 금지 — Mac 활성 세션이 약먹자/더치페이 reject 대응 중이면 reject 대응 한 사이클(데모 비디오/ASC reply 등) 끝낸 다음 처리 OK. 이 directive 는 가벼운 정보 sync 라 reject 대응보다 우선순위 낮음.
- 메모리 폴더 건드리지 말 것 (`~/.claude/projects/-Users-user/memory/` 의 trend-curator 메모리는 WSL 에서 이미 정리됨, in_progress 메모리도 비움).

종료 조건:
- (1) `~/.claude/skills/session-close/SKILL.md` 가 Mac 측에 존재
- (2) 답신 핸드오프 파일 1개 push (`-reply.md`)
- (3) 강대종님 텔레그램 reply 1줄 ack

참고:
- WSL 에서 추가로 박은 메모리: `project_trend_curator_sonnet_routing.md` Phase 1+2 완료로 이미 갱신함 — 그쪽 손대지 말 것.
- 이번 세션 직후 다음 작업으로 강대종님이 잡은 건 "심사레이더 v0.2 S24 시각검증" (WSL+S24 5분 컷). 그건 WSL 에서 처리할 것이니 Mac 은 reject 대응에만 집중.
