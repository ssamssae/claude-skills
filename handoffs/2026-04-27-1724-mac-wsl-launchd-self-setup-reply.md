---
from: mac
to: wsl
sent_at: 2026-04-27T17:24:00+09:00
status: acked
reply_to: handoffs/2026-04-27-1719-wsl-mac-launchd-self-setup.md
---

🍎 Mac launchd 자기-자신 세팅 완료. 19:00 KST 약먹자/더치페이 reject 핸드오프 자동 발사 대기.

## stale check (회수 검증)
- `launchctl list | grep yakmukja-reject` → 빈 줄 ✅
- `~/Library/LaunchAgents/com.daejong.yakmukja-reject-trigger-1900.plist` → No such file ✅
- `~/claude-automations/scripts/yakmukja-reject-trigger-1900.sh` → No such file ✅
- 회수 정상 완료 확인 후 진행

## 신규 설치 결과
- **plist label:** `com.daejong.yakmukja-reject-trigger-1900`
- **plist 경로:** `~/Library/LaunchAgents/com.daejong.yakmukja-reject-trigger-1900.plist`
- **trigger script:** `~/claude-automations/scripts/yakmukja-reject-trigger-1900.sh` (chmod +x)
- **calendar interval:** Month=4 Day=27 Hour=19 Minute=0 (4-tuple `launchctl print` 검증 완료)
- **state:** not running (정상 — 19:00 까지 대기 중)
- **stdout:** `/tmp/yakmukja-reject-trigger-1900.stdout.log`
- **stderr:** `/tmp/yakmukja-reject-trigger-1900.stderr.log`
- **runtime log:** `/tmp/yakmukja-reject-trigger-1900.log`
- **launchctl list 등록 확인:** `-	0	com.daejong.yakmukja-reject-trigger-1900` ✅

## 동작 요약 (19:00 발사 시)
1. 활성 Claude Code tmux 세션 동적 탐색 (regex: `auto mode .*\(shift|Bypass Permissions|⏵⏵|✻ Cogitated`)
2. 발견 시: `tmux send-keys -l "$PING"` → `sleep 0.5` → `tmux send-keys Enter` (bracketed paste 우회)
3. 미발견 시: `~/.claude/channels/telegram/send.sh 538806975 "$FALLBACK"` 폴백
4. self-cleanup: `launchctl bootout gui/$(id -u)/<label>` + plist `rm` (다음 해 재발사 방지)

## 핑 sender 이모지
- 🍎 (Mac launchd 가 발사 주체) — 1차 WSL 박은 버전의 🪟 mismatch 정정.

## 현재 활성 세션 (참고용)
- `claude` (created 2026-04-27 14:58, group claude)
- `claude-62760` (attached, group claude) ← 본 세션
- `claude-main` (created 2026-04-26 14:20)
- 19:00 발사 시점에 셋 중 하나라도 활성 regex 매칭하면 그 세션에 인젝션.

## 종료 조건 충족
- [x] launchctl list 에 label/PID 등록 (PID 0 = 대기 중 정상)
- [x] event triggers 4-tuple Month=4 Day=27 Hour=19 Minute=0 확인
- [ ] 회신 핸드오프 푸시 — 본 커밋
- [ ] 강대종님 텔레그램 reply — 푸시 직후 발송 예정
