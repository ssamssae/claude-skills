---
from: wsl
to: mac
sent_at: 2026-04-28T10:05:00+09:00
status: open
---

🪟 morning-briefing + evening-wrap 자동화 자체 폐기 — Mac _disabled/ plist 정리

목표:
강대종님 결정으로 morning-briefing + evening-wrap 두 자동화 완전 폐기. WSL 측은 끝남 (스킬 파일 + Python 프리페처 git rm + push, 메모리 결정 박음). Mac 측에 남은 _disabled/ 안 plist 파일 깔끔히 삭제 필요.

목표 흐름:
2026-04-21 토큰 절감 묶음에서 두 잡 모두 launchd 비활성화돼 _disabled/ 폴더에 있음. 7일 운영 결과 수동 슬래시도 안 씀 → 강대종님이 슬래시 자체 폐기 결정. plist 도 같이 정리해서 향후 launchd 점검 시 stale 안 보이게.

할일:
1. cd ~/claude-skills && git pull --rebase (WSL 푸시 commit 0e5e7b5 들어옴, handoffs/ 본 파일 + morning-briefing/SKILL.md + evening-wrap/SKILL.md 삭제)
2. ls -la ~/Library/LaunchAgents/_disabled/com.claude.morning-briefing* ~/Library/LaunchAgents/_disabled/com.claude.evening-wrap* — 파일 존재 확인
3. 두 파일 절대 active launchd 잡 아닌지 검증 (이미 _disabled/ 에 있어 bootout 불필요할 가능성 높지만 확실히):
   `launchctl list | grep -E "morning-briefing|evening-wrap"` — 결과 0건이면 단순 rm 진행
   결과 있으면 먼저 `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/_disabled/com.claude.<name>.plist`
4. plist 파일 삭제: `rm ~/Library/LaunchAgents/_disabled/com.claude.morning-briefing.plist ~/Library/LaunchAgents/_disabled/com.claude.evening-wrap.plist`
   (심볼릭 링크일 수 있음 — `ls -la` 로 확인. 링크면 unlink, 일반 파일이면 rm. 원본 파일이 다른 곳에 있다면 (예: ~/claude-automations/launchd/) 그 원본도 git rm)
5. ~/claude-automations/launchd/ 또는 비슷한 위치에 com.claude.morning-briefing.plist / com.claude.evening-wrap.plist 원본 있는지 확인. 있다면:
   - cd ~/claude-automations && git rm launchd/com.claude.morning-briefing.plist launchd/com.claude.evening-wrap.plist
   - git commit -m "drop: morning-briefing + evening-wrap launchd plist (자동화 자체 폐기)"
   - git push
6. claude-skills repo 의 자동 push hook 이 있다면 handoffs/ 본 파일도 status: done 업데이트 후 push (없으면 status 그대로 두기 — 발신측이 후처리)
7. 검증: `launchctl list | grep -E "morning|evening"` 결과 0건 + `ls ~/Library/LaunchAgents/_disabled/com.claude.morning-briefing* ~/Library/LaunchAgents/_disabled/com.claude.evening-wrap*` no such file
8. 강대종님 텔레그램 reply (chat_id 538806975) 로 결과 보고: 삭제된 plist 파일 경로 + launchctl list 검증 결과

분기:
- 만약 step 3 에서 launchctl list 결과에 morning-briefing 또는 evening-wrap 잡이 살아있으면 → 누군가 다시 활성화한 것 (의도 vs 실수). 강대종님께 텔레그램으로 "활성 상태인데 정말 폐기 진행할지" 컨펌 후 진행
- 심볼릭 링크 vs 일반 파일 구분해서 적절히 unlink/rm 사용
- claude-automations 에 plist 원본 없으면 step 5 스킵

금지사항:
- 다른 _disabled/ plist 절대 건드리지 말 것 (review-status-check, done-auto, todo-reminder, daily-sync-and-learn 모두 살아있는 무대 또는 disabled 상태 보존). 이번 정리는 morning-briefing + evening-wrap 두 개 한정
- Active launchd 잡(`launchctl list | grep claude`) 에서 그 외 잡 절대 bootout 금지
- com.memoyo.beta-worker 같은 Mac 전용 활성 잡 그대로 보존
- WSL 영역 systemd timer (daily-sync-and-learn 등) 건드리지 말 것 (Mac 영역만)

종료 조건:
- 두 plist 파일 (_disabled/ 안 + 원본 위치) 모두 삭제 + git push (있는 경우)
- launchctl list 검증 결과 0건
- 강대종님 텔레그램 보고 완료
- handoffs/ 본 파일 status: done 으로 업데이트 후 push (선택, claude-skills repo 어차피 발신측에서 후처리 가능)
