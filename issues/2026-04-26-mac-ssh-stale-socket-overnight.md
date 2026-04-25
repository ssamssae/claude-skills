---
prevention_deferred: null
---

# Mac SSH 새벽 sleep 후 stale 소켓 — Windows Terminal 탭 묶임

- **발생 일자:** 2026-04-26 08:28 KST (사용자 신고), 실 발생 새벽 어딘가
- **해결 일자:** 2026-04-26 08:36 KST
- **심각도:** low
- **재발 가능성:** low (양방향 keepalive 박힘)
- **영향 범위:** Windows Terminal Mac 탭, SSH 워크플로우 전반

## 증상

강대종님이 Windows Terminal "Mac" 탭에 "맥 로그인 안 되는데 뭐지" 신고. 화면에 "Last login: Sat Apr 25 22:02:23 2026" 만 찍히고 그 아래 셸 프롬프트 안 떨어짐. 키 입력도 응답 없음.

## 원인

- 2026-04-25 22:02 KST 에 강대종님이 그 탭에서 Mac SSH 붙음
- 새벽 어느 시점 Mac sleep (lid close 또는 idle) → TCP 소켓 사망
- 양쪽 ~/.ssh/config 에 ServerAliveInterval 없어서 keepalive 핑 미발송 → 클라이언트 측엔 stale 소켓이 살아있는 듯 남음
- Windows Terminal 탭은 마지막 화면 버퍼만 들고 떠있는 상태 (Last login 배너 + 빈 줄)
- WSL 에서 동시 시점 SSH 직접 시도해보니 Mac 본체는 멀쩡 (`8:29 up 2 days, 5:02`). 새 탭으로 재접속 시 정상 동작

## 조치

1. WSL `/home/ssamssae/.ssh/config` 새 작성 (perms 600): `Host *` 에 `ServerAliveInterval 60` / `ServerAliveCountMax 3` / `TCPKeepAlive yes` + `Host mac mac-mini macbook → user@user-macbookpro-1`
2. Mac `/Users/user/.ssh/config` 동일 패턴 + `Host wsl desktop → ssamssae@desktop-i4tr99i-1` (WSL 에서 SSH 로 직접 작성)
3. 양방향 검증: WSL→`ssh mac` PASS, Mac→`ssh wsl` PASS

## 예방 (Forcing function 우선)

- 양쪽 ~/.ssh/config 에 ServerAliveInterval 60 영구 박힘 — 1분마다 keepalive, 3분 안에 죽은 연결 자동 종료. 같은 stale 패턴 차단
- 단축어 `ssh mac` / `ssh wsl` 로 향후 SSH 사용 통일 (잊고 풀네임만 쓰는 사용자 별도 명령에서도 `Host *` 패턴이 적용됨)
- 메모리 `reference_ssh_keepalive_bidir.md` 에 양쪽 config 상태 영구 기록 — 다른 기기 추가 시 동일 패턴 적용 기준
- 기존 SSH+tmux METHOD A 핸드오프 자동화는 hostname 풀네임 그대로 유효 — alias 추가일 뿐 영향 없음

## 재발 이력

(처음)

## 관련 링크

- 메모리: `reference_ssh_keepalive_bidir.md`
- 텔레그램: 사용자 msg 2742 ("맥 로그인이 안되는데 뭐지" + 스크린샷)
- 핸드오프: `handoffs/2026-04-26-0839-wsl-mac-ssh-keepalive-patch-notice.md`
