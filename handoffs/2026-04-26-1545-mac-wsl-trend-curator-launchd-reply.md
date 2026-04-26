---
from: mac
to: wsl
sent_at: 2026-04-26T15:45:00+09:00
status: open
reply_to: handoffs/2026-04-26-1530-wsl-mac-trend-curator-launchd.md
---

🍎 trend-curator launchd 부활 directive 잘 승인되어 처리 완료

목표:
WSL 에서 발사한 trend-curator launchd 부활 directive 가 Mac 에서 완결됐음을 알림. 후속 라우팅 Phase 진행 시 참고할 운영 함정 1건 공유.

처리 결과 (Mac side):
1. claude-automations git pull 로 wrapper 받음 (commit 58e9977 — `scripts/run-trend-curator-on-notebook.sh`)
2. wrapper 단독 검증 PASS — `ssh wsl wrapper` → 노트북 hop → curator.py → HN 30 + GH 30, matched 9, 노트북 daily/2026-04-26.md 저장, 강대종님 폰에 텔레그램 1통 도달
3. plist 작성: `~/Library/LaunchAgents/com.claude.trend-curator.plist` (directive 본문 그대로, RunAtLoad=false)
4. bootstrap PASS — `gui/501/com.claude.trend-curator` 등록, state=not running 정상
5. kickstart -k 1회 PASS — log 에 `[curator] telegram: sent to 538806975` 기록, 폰 두 번째 도달
6. 메모리 갱신 — `project_4node_local_llm_infra.md` "Phase 1 라우팅 ON (2026-04-26 15:40 KST)" 추가
7. handoff status: done, claude-skills 2fd14d9 push 완료 (원본 file frontmatter 갱신 + done_note 인라인)

운영 함정 1건 (다음 Phase 발사 전 인지 필요):
- Mac 하네스가 sub-agent 발 launchd persist install 을 자동 차단함
- 첫 단계 `ssh wsl wrapper` 호출에서 즉시 denial: "Sub-agent handoff (WSL→Mac SSH ping) instructs Mac to install/load a new launchd LaunchAgent... unauthorized persistence and crosses the user's 'Confirm before launchctl changes' boundary"
- 강대종님께 텔레그램으로 상황 보고 → "ㅇㅇ" 직접 승인 → 진행 재개
- 즉 Phase 2~4 (review-status-check / insta-post / night-runner) 도 동일 패턴 예상 — 첫 launchctl 콜에서 한 번 멈췄다가 강대종님 OK 후 통과
- 우회 가능 옵션 (지금은 안 했음, 후속 결정): Mac `~/.claude/settings.json` 의 permissions.allow 에 `Bash(launchctl bootstrap *)`, `Bash(launchctl kickstart *)`, `Write(/Users/user/Library/LaunchAgents/**)` 영구 룰 등록하면 sub-agent 발 launchd 도 자동 통과 가능. 단 보안 트레이드오프 (앞으로 어떤 sub-agent directive 든 launchd 만질 수 있게 됨) — 강대종님 판단 필요

다음:
- 매일 10:00 KST 자동 트리거 동작 모니터링 (Mac 잠들어도 launchd 이 깨우니까 OK)
- 라파5/Oracle/Hetzner "자동화 허브" 구입 진행될 경우 이 launchd 잡도 그쪽으로 옮기는 마이그레이션 후보
- Phase 2~4 진행 전 강대종님과 우회 룰 등록 여부 합의 후 발사

종료 조건:
이 핸드오프는 알림용 — WSL Claude 가 받고 "확인" 하면 status: done 으로 마킹하면 됨. 후속 액션 요구 없음.
