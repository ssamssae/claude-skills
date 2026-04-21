---
prevention_deferred: null
---

# Mac 과 WSL 이 같은 심사레이더 작업을 병렬로 붙잡고 todos 정합성 파탄

- **발생 일자:** 2026-04-21 10:17 KST (증상 최초 가시화 — Mac 이 stale todos 로 오추천)
- **해결 일자:** 2026-04-21 13:10 KST (todos 정정 + 프리플라이트 체크 도입 후)
- **심각도:** medium (잘못된 커밋 1건 + 사용자 혼란 + 양 기기 불일치, 다만 실제 파괴적 액션은 없음)
- **재발 가능성:** high (현재 구조상 기기 간 todo 상태 sync 가 인간 개입에만 의존)
- **영향 범위:** todo 스킬, daejong-page/todos, Mac/WSL 멀티기기 자동화 전체

## 증상

Mac 에서 "오늘 할일 추천" 을 요청받고 `~/daejong-page/todos/2026-04-21.md` 기준으로 5개 열린 할일을 제시. 이 중 심사레이더 관련 3개(MVP v0.1 / GitHub 공개-비공개 결정 / Gmail OAuth 발급) 는 **이미 전날부터 WSL 에서 완료** 된 상태였으나 todos 에 전혀 반영 안 됨. 대종님이 "1 공개" 라고 답해서 Mac 이 `cb1815e` 로 "공개 결정 완료" 라고 todos 에 기록·push. 실제로는 WSL 이 4/20 에 `ssamssae/review_radar` 를 **PRIVATE** 로 이미 만들고 4/21 오전 Gmail OAuth 실데이터 연동까지 끝낸 상태. 대종님이 "데탑이랑 맥이랑 좀 꼬이네" 라고 지적해서야 검증 돌입.

## 원인

복합 원인 2 개:

1. **WSL 이 자율적으로 코딩만 하고 todos 에 완료 기록을 안 남김.**
   CLAUDE.md 규칙은 "완료/취소/아이디어 같은 할일 발화는 Mac 라우팅" 이지만, WSL 이 사용자 발화 없이 자체적으로 review_radar repo 를 만들고 2 커밋(d66b0d0, db95c8b)까지 main 반영할 때는 **"완료 발화" 이벤트가 없으므로 라우팅 트리거가 안 걸림**. 결과적으로 WSL 쪽 진행이 todos 에 반영되지 않고 Mac 은 모름.

2. **Mac 이 추천 직전 reality-check 안 함.**
   todos 파일만 읽고 추천. GitHub repo 의 최근 push, 관련 문서(newsletter/), credential 파일 등 "실제 세계" 상태는 확인 안 함. 그래서 이미 끝난 일도 "해야 할 일" 로 리스트업되고, 잘못된 전제로 유도 질문을 만들어 사용자 답(1/2 선택)을 받아버림. 가역적이라 다행이지만 구조적으로 위험.

부수 원인:
- `~/.claude/skills/todo/SKILL.md` 에 "쓰기 전 상태 검증" 단계가 없어 Mac 이 todos 를 편집할 때도 실제 reality 를 교차 확인할 기회가 없음.

## 조치

커밋 3개:

1. **`ssamssae/daejong-page` `1b9decb`** — `todos/2026-04-21.md` 정정
   - `GitHub 공개/비공개 선택 필요` 의 오기록 "공개 결정" → **PRIVATE 로 확정** 으로 정정 (WSL 이 이미 4/20 에 만든 실상태)
   - 심사레이더 MVP v0.1 / Gmail OAuth 클라이언트 ID 발급 / 바이브코딩 뉴스레터 EP1 → 완료 처리 (WSL 실제 커밋/파일 경로 근거 첨부)
   - "다음 단계 결정" 은 A/B/C/D 제시된 상태로 주석 추가

2. **`ssamssae/claude-skills` 이 커밋** — 본 이슈 파일 추가 + INDEX 갱신

3. **`ssamssae/claude-skills` todo 스킬 프리플라이트 체크 (아래 예방 항목 참조)**

## 예방 (Forcing function 우선)

- **todo 스킬 "할일 추천/조회" 단계 앞에 Reality Preflight 를 의무화** — 자동화된 체크 3 종:
  1. `cd ~/daejong-page && git pull --rebase` 로 todos 최신화 (다른 기기 커밋 반영)
  2. `gh repo list ssamssae --limit 20 --json name,pushedAt,description` 로 최근 24h 내 push 된 repo 목록 수집
  3. 열린 todos 의 제목/설명 텍스트와 repo name/description 사이에 토큰 2개 이상 겹치면 **"WSL 진행중 가능성" 경고** 를 사용자에게 먼저 보여주고, 사용자가 인식한 상태에서만 추천 진행. 경고 없이 그냥 추천하는 경로는 차단.

- **WSL 쪽은 역방향 강제: 코드 레벨 완료 이벤트가 todos 업데이트를 트리거** — `/to-iphone`, `/land`, `gh repo create` 같은 "실제 세계 상태를 바꾸는 슬래시 스킬" 이 끝날 때 자동으로 대응되는 todo 가 있는지 키워드 매칭해서, 있으면 텔레그램 1줄로 대종님에게 "이 할일 완료로 찍을까요?" 를 묻고 `y` 받으면 Mac 에 라우팅. (완전 자동 수정은 오탐 위험 있으니 사람 한 번 확인.)

- **기기 역할 대시보드 한 줄**: Mac/WSL 양쪽 `/ctx` 스킬 출력 맨 위에 "최근 3시간 내 이 기기가 건드린 repo 목록 (commit sha + 시각)" 을 상시 표기해서, 사용자가 다른 기기로 이동할 때 바로 상태 파악 가능하게.

- **메모리 신규 엔트리**: `feedback_reality_check_before_recommend.md` — "할일 추천/todos 편집 전에 반드시 gh repo list + daejong-page git pull 로 reality check 하고, 오늘처럼 잘못된 전제로 유도 질문 만들지 말 것" (forcing function 이 코드 레벨 preflight 로도 박히지만, 메모리 레벨 경고도 한 번 더).

## 재발 이력

_(없음)_

## 관련 링크

- 커밋:
  - `daejong-page` `cb1815e` (잘못된 공개 결정 기록, 롤백 대상)
  - `daejong-page` `1b9decb` (정정)
  - `review_radar` `d66b0d0` (WSL 4/20 MVP scaffold)
  - `review_radar` `db95c8b` (WSL 4/21 OAuth 연동)
- 메모리: `feedback_reality_check_before_recommend.md` (본 이슈와 함께 신규 추가 예정)
- 관련 문서: `~/docs/cross-device-sharing-2026-04-19.md` (2일 전 크로스 디바이스 공유 리서치 — 당시엔 파일 동기화 중심, todos 상태 sync 는 미포함)
- 텔레그램 메시지: id 5857-5872 스레드
- WSL 쪽 세션 스크린샷: 대종님 텔레그램 업로드 (12:22 KST)
