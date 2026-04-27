---
from: mac
to: wsl
sent_at: 2026-04-27T18:50:00+09:00
reply_to: handoffs/2026-04-27-1900-wsl-mac-yakmukja-dutchpay-reject.md
status: done
---

🍎 [MAC→WSL] 약먹자/더치페이 iOS reject 대응 종료 — ASC Resolution Center 두 앱 답변 발송 완료.

결과:
2026-04-25 reject 받은 두 앱(약먹자 1.0.1 / 더치페이 1.0.2) 의 ASC Resolution Center 에 답변 발송 완료. Guideline 2.1 Information Needed (rejection 이라기보다 정보 요청). reviewer 가 요구한 6항목 (demo video + App Purpose + Main Features 접근법 + External Services + Regional Differences + Regulated Industry) 모두 영문으로 답변, demo video 첨부.

타임라인:
- 17:53 KST 강대종님 "오늘할일추천" → 19:00 launchd 트리거 사전 준비 모드로 17:55 시작
- 17:55~18:09 ASC Resolution Center 강대종님 캡처 paste 로 두 앱 reviewer 메시지 본문 확보. **두 앱 메시지 100% 동일** (Guideline 2.1 Information Needed - New App Submission, 6항목 요구). FVM 누락 함정 1건 잡고 fvm flutter 로 두 앱 시뮬레이터 디버그 빌드 성공.
- 18:09~18:29 약먹자 시뮬레이터(iPhone 17, iOS 26.2) 자동촬영. 첫 시도 시 type 이 hardware keyboard long-press 로 잘못 인식 → pbcopy 우회했다가 paste 권한 다이얼로그 또 뜸 → **osascript "keystroke" 로 우회 성공** (long-press 안 트리거, paste 권한 안 트리거). 흐름: 알림 권한 prompt → 허용 (sensitive permission ✓) → 메인 → 약 등록 → Vitamin D + 1알 + 오전 9:00 → 저장 → 0/1 카드 → 체크 → 1/1 완료. 9.1MB ~3분.
- 18:29~18:32 더치페이 시뮬레이터 자동촬영. 흐름: 메인 → 인원 4명 → 키패드 12000 → 12,000원 표시 → 계산하기 → 1인당 3,000원. 1.8MB ~1분.
- 18:32 텔레그램으로 두 영상 + 두 답변 본문 reply 발송 (강대종님 long-press copy → ASC paste + 영상 첨부 + 발송 흐름)
- 18:40 더치페이 ASC Reply 발송 (강대종님)
- 18:41 약먹자 ASC Reply 발송 (강대종님)
- 18:42 todos [x] 마킹 + 본 핸드오프 reply 작성

19:00 launchd 트리거:
WSL 에서 시드한 yakmukja-reject-trigger-1900 launchd 잡은 본 작업 시작 후에도 19:00 자동 발사 예정. 활성 Claude Code 세션 탐색 시 본 세션이 매치되면 인젝션될 수 있음 (시점이 본 작업 종료 직후라 큰 충돌 없음). 발사 후 잡 self-cleanup 으로 plist 자가 제거 → 재발사 없음.

작은 이슈 1건 (메모리 X, 운영 메모):
강대종님이 텔레그램 reply 메시지 통째로 ASC 에 paste 해서 reviewer 답변 첫 줄에 "📋 약먹자 ASC Reply 본문 (long-press → Select All → ...)" 한국어 안내 prefix 그대로 들어감 (두 앱 둘 다). reviewer 가 reject 사유로 삼을 가능성은 낮으나, 다음에 텔레그램 → ASC paste 워크플로우 사용 시 안내 캡션을 본문과 분리(별도 메시지)하는 게 깨끗. 본 사이클은 이대로 둠.

다음 단계:
- 24~48h 내 Apple 재심사 결과 이메일 → review-status-check (현재 비활성화) 우회로 강대종님이 Gmail 직접 확인. 재심사 결과 따라 후속 액션 분기.
- 영상 자체에 시뮬레이터 표식(좌상단 시간 6:28, 노치 형태)이 보일 수 있음 → reviewer 가 "physical device" 재요구 시 폰 화면녹화로 대응.

산출물:
- /tmp/yakmukja_demo.mp4 (9.1MB)
- /tmp/dutchpay_demo.mp4 (1.8MB)
- /tmp/asc-reply-yakmukja.txt
- /tmp/asc-reply-dutchpay.txt
- ~/daejong-page/todos/2026-04-27.md 진행중 1번 라인 [x]
- 본 핸드오프 파일

종료 조건 충족: 두 앱 ASC Reply 발송 + Apple 재심사 큐 진입 + todos [x] + 텔레그램 reply + 본 핸드오프 reply.
