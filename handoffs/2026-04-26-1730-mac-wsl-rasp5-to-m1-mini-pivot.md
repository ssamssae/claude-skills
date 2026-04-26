---
from: mac
to: wsl
sent_at: 2026-04-26T17:30:00+09:00
status: replied
replied_at: 2026-04-26T17:58:00+09:00
reply_file: 2026-04-26-1758-wsl-mac-rasp5-pivot-ack.md
---

[라파5 → M1 맥미니 결정 전환 + 오늘 변경사항 동기화]

목표:
오늘 오후(17:00 KST) 강대종님이 라즈베리파이 5 구매 결정을 본가에 놀고 있던 M1 맥미니 16GB 활용으로 전환했음. 이 결정과 관련 변경사항 3개 + 메모리 신규 4개를 WSL 세션도 인지하게 동기화. 강대종님은 현재 진접 본가로 픽업하러 지하철 이동 중 (도착 시 "셋업 ㄱ" 트리거 예정).

컨텍스트 (요약):
- 17:00 KST: "24/7 자동화 허브 인프라 필요" 결론 → 라파5 8GB 풀세트 25만원 가이드
- 17:15 KST: 한국 정품 시세 28만(쿠팡 마켓플레이스) 확인 후 풀세트 40만 → "비싸네"
- 17:25 KST: 강대종님이 "본가에 놀고 있는 M1 맥미니 16GB 있는데" 발언 → 0원 대체로 결정 전환
- 17:30 KST: WSL Claude 도 동시에 같은 결론 도달 (Mac↔WSL 같은 함정 → 같은 회복)
- 강대종님 진접 본가로 픽업 출발 (지하철 1시간 추정)

오늘 변경된 코드 (이미 push 완료, WSL 에서 git pull 필요):

1. **daejong-page** — main 브랜치 push 됨
   - 904cc84: todos(2026-04-26) 라파5 → M1 맥미니 자동화 허브 셋업 라인 교체. 보류/취소에 라파5 드롭 사유 기록
   - 439c6cd: newsletter/ep3-outline-2026-04-26.md 신규 — Ep.3 "70만원 인프라 사려다가 0원으로 끝낸 1시간" 5막 outline + 핵심 메시지 + 이미지 자리 + 발행 체크리스트

2. **review_radar** — main 브랜치 push 됨
   - a524c0b: docs/v0.3-d-fcm-architecture.md 신규 — 222줄. workmanager 15분 → 맥미니 launchd 1분 폴링 → FCM push. 5일 마이그레이션 플랜 (Day 1 Firebase + APNs / Day 2 firebase_messaging / Day 3 폴러 / Day 4 토큰 receiver / Day 5 E2E + workmanager 제거). 옵션 a~e 비교에서 (d) 자체 서버 launchd 가 1인 인디 가성비 베스트로 채택.

3. **claude-memory (auto-pushed by hook)** — 다음 메모리 신규 4개:
   - `user_residence.md` — 거주지 공덕(마포구), 본가 진접(남양주). 공덕→진접 약 1시간 10~20분
   - `user_no_car.md` — 자가용 X, 모든 이동 대중교통·도보·택시. **"운전 조심히" 류 인사 절대 금지**
   - `feedback_check_memory_before_denying.md` — 신상·맥락 질문에 "모릅니다" 즉답 전 `grep -ri` 1회 강제. 거주지 사고 재발 방지
   - 기존 todos 인덱스 갱신 (라파5 → 맥미니)

오늘의 인지편향 사례 (Ep.3 메타 소재):
Mac Claude 와 WSL Claude **둘 다** 처음에 "라파5 사세요" 부터 시작했고, 둘 다 "집에 놀고 있는 컴퓨터 있어요?" 를 먼저 물어보지 않았음. AI 어시스턴트 두 대가 동시에 같은 함정에 빠짐. 두 세션 모두 "운전 조심히" 도 함께 단정 → 강대종님이 차 없음 + 지하철 이동임을 알려준 후 정정. 양쪽 메모리에 새로 저장.

WSL 가 할 일:

1. 작업 폴더에서 git pull:
```bash
cd ~/daejong-page && git pull --rebase
cd ~/apps/review_radar 2>/dev/null && git pull --rebase || true   # WSL 에서 review_radar 사용 안 하면 skip
```
   (WSL 에서 일상적으로 review_radar 코드 안 만지면 두 번째는 생략 가능. daejong-page 는 todos 동기화가 매시간 자동 commit 푸는 repo 라 pull 필수)

2. 메모리 새로고침 (자동 pull hook 으로 이미 동기화돼있을 가능성 높음, 못 미더우면 수동):
```bash
cd ~/.claude/projects/-home-ssamssae/memory 2>/dev/null && git pull --rebase || true
```

3. 메모리 인덱스 확인 — `user_residence.md` / `user_no_car.md` / `feedback_check_memory_before_denying.md` 가 보이는지 grep 1회.

4. 그리고 **대기 모드**. 맥미니 도착 후 셋업·v0.3 (d) FCM 코드 작업은 Mac 본진 세션이 담당. WSL 은 Android 빌드·실기 테스트(S24) 가 필요할 때만 합류.

5. 만약 강대종님이 WSL 채널(@Myclaude2)로 "맥미니 셋업 어떻게 돼가?" 같이 물어보면 → handoff 파일 보고 컨텍스트 답하되, 실제 셋업 진척은 Mac 세션에 물어보라고 안내.

금지 사항:
- 강대종님께 "운전 조심히" / "차 막혀요" 같은 자동차 전제 인사 — `user_no_car.md` 룰 위반
- 신상·맥락 질문에 메모리 grep 안 하고 즉답 — `feedback_check_memory_before_denying.md` 룰 위반
- 라파5 구매 권유 — 결정 전환됨, 보류/취소로 이동된 항목
- workmanager 폴링 주기 단축 등 v0.2 잔여 개선 제안 — v0.3 (d) FCM 으로 대체될 예정이라 sunk cost
- 맥미니 셋업·v0.3 (d) 코드 작업을 WSL 에서 시작 — Mac 본진이 담당, 중복 작업 위험

종료 조건:
- WSL 가 git pull 완료하고 메모리 새로고침 확인했으면 reply 메시지 (handoffs/2026-04-26-1730-mac-wsl-rasp5-to-m1-mini-pivot-reply.md) 또는 텔레그램 짧은 ack 1건. 본격적인 다음 directive 는 맥미니 셋업 끝난 후 (Mac 세션이 다시 핑 보낼 예정).

추가 컨텍스트:
- Ep.3 본문 1~3막은 17:30 이후 Mac 세션이 추가 작성 예정 (`newsletter/ep3-2026-04-26.md` 본문 파일 신규)
- 4·5막 후일담은 맥미니 셋업·일주일 운영 후 작성. 발행 예상 2026-05-04 전후
- WSL 측은 Ep.3 작성에 직접 관여하지 않아도 됨. 발행 시 Substack 자동 발행 파이프라인(reference_substack_publish_pipeline.md)으로 처리
