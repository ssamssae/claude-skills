---
from: wsl
to: mac
sent_at: 2026-04-27T17:19:00+09:00
status: open
---

🪟 [META] launchd SoT 정정 — 너(Mac)가 직접 launchd 박아서 19:00 KST handoff 발사하기

목표:
WSL 세션이 SSH 로 Mac launchd plist + trigger script 박은 게 SoT 위반(CLAUDE.md "launchd SoT는 Mac"). WSL 쪽에서 그 자산 회수했으니, 이제 Mac Claude(너) 가 동일 기능을 자기 자신 책임으로 다시 세팅한다. 결과적으로 19:00 KST 약먹자/더치페이 iOS reject 핸드오프가 변함없이 자동 발사돼야 함.

목표 흐름:
WSL 17:19 KST 에 (1) 이 메타-디렉티브 푸시 → (2) WSL 이 박았던 Mac 자산 bootout/rm 으로 회수 → (3) WSL 이 너한테 METHOD A 핑. 너는 이 파일 읽고 launchd 새로 박는다. 19:00 KST 까지 1h 41m 버퍼.

컨텍스트:
- 발사할 핸드오프(원본): handoffs/2026-04-27-1900-wsl-mac-yakmukja-dutchpay-reject.md (이미 main 에 푸시됨, 강대종님 약먹자/더치페이 ASC reject 대응 디렉티브 본문)
- WSL 이 박았다 회수한 자산:
  - LaunchAgent label: `com.daejong.yakmukja-reject-trigger-1900`
  - plist 경로: `~/Library/LaunchAgents/com.daejong.yakmukja-reject-trigger-1900.plist`
  - trigger script: `~/claude-automations/scripts/yakmukja-reject-trigger-1900.sh`
  - 회수 명령: `launchctl bootout gui/$(id -u)/com.daejong.yakmukja-reject-trigger-1900` + `rm` plist + `rm` script
  - WSL 핑 도착 시점에 회수가 이미 끝나 있어야 함. 도착 후 너가 `launchctl list | grep yakmukja-reject` 결과 빈 줄 + plist/script 파일 부재 확인 먼저.

할일:
1. **stale check**: `launchctl list | grep yakmukja-reject` 와 `ls ~/Library/LaunchAgents/com.daejong.yakmukja-reject-trigger-1900.plist 2>&1` 와 `ls ~/claude-automations/scripts/yakmukja-reject-trigger-1900.sh 2>&1` — 셋 다 "비어있음/No such file" 나오면 회수 정상 완료. 하나라도 잔존하면 강대종님께 텔레그램 reply 로 보고 후 진행 보류.
2. **trigger script 작성**: `~/claude-automations/scripts/yakmukja-reject-trigger-1900.sh` 새로 작성. 본질 동작:
   - 활성 Claude Code tmux 세션 동적 탐색 (regex: `auto mode .*\(shift|Bypass Permissions|⏵⏵|✻ Cogitated`). claude-main/claude/claude-NNNNN 등 어디든 활성이면 잡기.
   - 활성 세션 발견 시 핑 1줄 발사: `🍎 [SCHEDULED 19:00 KST · MAC LAUNCHD] 약먹자/더치페이 iOS reject 대응 시작. cd ~/claude-skills && git pull && cat handoffs/2026-04-27-1900-wsl-mac-yakmukja-dutchpay-reject.md 으로 본문 읽고 진행. 종료조건: 두 앱 ASC Reply + todos [x] + 텔레그램 보고.`
   - send-keys 텍스트 + `sleep 0.5` + send-keys Enter 분리 (bracketed paste 우회 — 2026-04-25 검증)
   - 활성 세션 0개면 텔레그램 send.sh 폴백: `~/.claude/channels/telegram/send.sh 538806975 "<안내메시지>"`
   - 마지막에 self-cleanup: `launchctl bootout gui/$(id -u)/com.daejong.yakmukja-reject-trigger-1900` + `rm $PLIST` (다음 해 재발사 방지)
   - 로그: `/tmp/yakmukja-reject-trigger-1900.log`
   - **핑 sender 이모지는 🍎** (이번엔 Mac launchd 가 발사 주체이므로). WSL 이 박은 1차 버전은 🪟 였는데 그게 mismatch 의 원인. 이제 🍎 로 정정.
   - chmod +x 잊지 말 것.
3. **plist 작성**: `~/Library/LaunchAgents/com.daejong.yakmukja-reject-trigger-1900.plist`. StartCalendarInterval `Month=4 Day=27 Hour=19 Minute=0`, RunAtLoad=false, ProgramArguments 에 trigger script 절대경로, StandardOut/StandardError 로그 경로 `/tmp/yakmukja-reject-trigger-1900.{stdout,stderr}.log`.
4. **bootstrap**: `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.daejong.yakmukja-reject-trigger-1900.plist` → `launchctl print gui/$(id -u)/com.daejong.yakmukja-reject-trigger-1900` 으로 calendar interval 4-tuple (Month=4, Day=27, Hour=19, Minute=0) 확인.
5. **회신 핸드오프 파일**: `handoffs/2026-04-27-HHMM-mac-wsl-launchd-self-setup-reply.md` (frontmatter `from: mac, to: wsl, status: acked, reply_to: handoffs/2026-04-27-1719-wsl-mac-launchd-self-setup.md`) 작성 + commit + push. 본문에 설치 결과(plist label, calendar interval, log paths, active session 탐지 결과) 요약.
6. **강대종님께 텔레그램 reply 보고**: "Mac launchd 자기-자신 세팅 완료, 19:00 KST 약먹자/더치페이 핸드오프 자동 발사 대기. SoT mismatch 정정됨." (chat_id 538806975).

금지사항:
- 19:00 KST 핸드오프 본문(handoffs/2026-04-27-1900-wsl-mac-yakmukja-dutchpay-reject.md)은 **건드리지 말 것**. 그건 19:00 에 Mac 본인이 받을 디렉티브이고 frontmatter `from: wsl, to: mac` 그대로 유지. 메타-회수 작업과 별개.
- WSL 이 박았던 자산이 회수 완료된 줄 알았는데 잔존하면 즉시 멈춤. 강대종님 텔레그램 reply 로 보고. 임의로 덮어쓰기 X.
- launchd plist 레이블은 `com.daejong.yakmukja-reject-trigger-1900` 그대로 재사용. 새 레이블 만들지 말 것 (파편화 방지).
- self-cleanup 단계에서 `rm -rf` 같은 광범위 삭제 금지. plist 경로만 정확히 `rm`.
- "생성됨 by Claude" 같은 메타 주석 plist 에 박지 말 것.

종료 조건:
- `launchctl list | grep yakmukja-reject` 가 새 plist 의 label/PID 보여줌
- `launchctl print gui/$(id -u)/com.daejong.yakmukja-reject-trigger-1900` 의 event triggers 가 Month=4 Day=27 Hour=19 Minute=0 4-tuple 로 출력
- 회신 핸드오프 파일 푸시 완료
- 강대종님 텔레그램 reply 1건 발송
이 4개 다 충족되면 본 메타 핸드오프 status `done`.
