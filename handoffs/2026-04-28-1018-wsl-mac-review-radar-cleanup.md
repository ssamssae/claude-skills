---
from: wsl
to: mac
sent_at: 2026-04-28T10:18:00+09:00
status: open
---

🪟 심사레이더 + review-status-check 일괄 폐기 — Mac 잔여 정리

목표:
강대종님 D 옵션 컨펌으로 심사레이더 흔적 일괄 폐기. WSL 측은 끝남 — 스킬 git rm + push (commit af32726), S24 (R3CX10GX1XR) 에서 com.ssamssae.review_radar uninstall, GitHub repo `ssamssae/review_radar` archived. Mac 측 잔여 정리 부탁.

목표 흐름:
앞선 morning-briefing/evening-wrap 폐기 (commit 0e5e7b5 + 47b150a) 와 같은 결의 이번 폐기. 심사레이더는 앱 자체 + review-status-check launchd 잡 두 갈래라 양쪽 다 정리. 4/25 17h Apple 메일 누락 사고 인지하고 강대종님이 폐기 결정 — 본인 앱 출시 알림은 Gmail 직접 확인 또는 ASC/Play Console 공식 푸시로 대체 의지.

할일:
1. cd ~/claude-skills && git pull --rebase (handoffs/ 본 파일 + review-status-check/SKILL.md 삭제 commit af32726 들어옴)
2. **review-status-check launchd 정리:**
   - `launchctl list | grep review-status` — active 면 bootout 먼저
     `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.claude.review-status-check.plist` (있는 경로로)
   - plist 위치 확인: `ls -la ~/Library/LaunchAgents/_disabled/com.claude.review-status-check* ~/Library/LaunchAgents/com.claude.review-status-check*`
   - 양쪽 다 발견되면 둘 다 삭제. 심볼릭 링크면 unlink, 일반 파일이면 rm
   - ~/claude-automations 안에 plist 원본/래퍼 스크립트 있는지: `find ~/claude-automations -iname "*review-status*"` — 있으면 git rm + commit + push
3. **심사레이더 앱 코드 잔여:**
   - `ls -la ~/apps/review_radar/` — 있으면 강대종님께 텔레그램으로 "디렉토리 삭제할까요?" 컨펌 (강대종님 작업 중일 수 있어 함부로 rm 금지)
   - 강대종님이 OK 하면 `rm -rf ~/apps/review_radar/` (단 git status 깨끗한지 먼저 확인 — uncommitted 변경분 있으면 손실 방지 stash)
4. **Gmail OAuth 안내:**
   - 강대종님께 텔레그램으로 안내 — "심사레이더 Gmail OAuth 토큰은 https://myaccount.google.com/permissions 에서 직접 revoke 부탁드려요. 본인 인증 필요해서 자동 처리 불가"
   - 단 강대종님이 이미 알고 있을 가능성 높음 — 안내만 한 줄
5. **검증:**
   - `launchctl list | grep -E "review-status|review_radar"` 결과 0건
   - `ls ~/Library/LaunchAgents/_disabled/com.claude.review-status-check* ~/Library/LaunchAgents/com.claude.review-status-check*` no such file
   - `find ~/claude-automations -iname "*review-status*"` 결과 0건
   - `ls ~/apps/review_radar/` no such file (또는 강대종님이 보존 결정한 경우 명시)
6. **보고:**
   - 강대종님 텔레그램 reply (chat_id 538806975) 로 결과: 삭제된 plist 경로 + ~/apps/review_radar 처리 결과 + Gmail OAuth 안내 + handoffs/ 본 파일 status: done 업데이트

분기:
- step 2 launchctl list 에 review-status-check 가 active 상태면 누군가 부활시킨 것 — `project_automation_disabled_2026_04_21.md` "가벼운 모드 부활 검토" 라인 확인. 부활 후 일괄 폐기 결정 (D) 이라 그대로 bootout + 삭제 진행
- step 3 ~/apps/review_radar 안에 uncommitted 변경분 있으면 강대종님께 보고 후 OK 받고 진행 (git status 깨끗하면 바로 rm 가능 — repo 가 이미 archived 라 GitHub 에 다 보존됨)
- 만약 review-status-check 가 ~/.claude/runner/settings-launchd.json 같은 공유 설정에 등록돼있으면 그 항목도 삭제 (`feedback_nested_claude_telegram_conflict.md` 참조)

금지사항:
- 다른 _disabled/ plist 절대 건드리지 말 것 (done-auto, todo-reminder, daily-sync-and-learn 등 보존)
- com.memoyo.beta-worker 같은 활성 잡 그대로
- ~/apps/ 안 다른 앱 (hanjul, mini_expense, pomodoro, yakmukja, dutchpay 등) 절대 건드리지 말 것 — review_radar 한정
- GitHub `ssamssae/review_radar` repo 는 이미 archived 됨 (gh repo archive 완료) — delete 금지 (archive = 가역, delete = 비가역)
- Gmail OAuth 자동 revoke 시도 금지 — 강대종님 본인 Google account 인증 필요

종료 조건:
- launchctl 에 review-status-check 흔적 0건
- ~/Library/LaunchAgents/{,_disabled/} 에 review-status-check.plist 0건
- ~/claude-automations 에 review-status 관련 파일 0건
- ~/apps/review_radar 처리 결과 명시 (삭제 또는 보존 + 사유)
- Gmail OAuth 안내 + handoffs/ 본 파일 status: done 업데이트
- 강대종님 텔레그램 보고 완료
