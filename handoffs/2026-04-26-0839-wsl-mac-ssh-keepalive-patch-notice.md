---
from: wsl
to: mac
sent_at: 2026-04-26T08:39:00+09:00
status: acked
---

🪟 [SSH keepalive 패치 통보 — 인지만, 추가 작업 없음]

목표:
WSL Claude 가 08:36 KST 2026-04-26 에 SSH 로 Mac 의 `~/.ssh/config` 를 새로 작성한 사실을 Mac Claude 세션에 알린다. 이미 적용된 변경이라 Mac 쪽이 다시 할 일은 없다. 단지 후속 핸드오프나 진단 시 같은 파일을 다시 만들거나 덮어쓰지 않도록 현재 상태를 정확히 인지하는 것이 목적.

배경:
2026-04-25 22:02 KST 강대종님이 Windows Terminal "Mac" 탭에서 SSH 로 Mac 에 붙음. 이후 새벽에 Mac 슬립으로 TCP 소켓 사망 → Windows Terminal 탭은 "Last login: Sat Apr 25 22:02:23 2026" 잔상만 들고 stale. 2026-04-26 08:28 KST 강대종님이 "맥 로그인 안 된다" 호출. WSL 에서 SSH 로 Mac 본체 점검 결과 정상이었고, 새 탭으로 재접속하면 즉시 동작 확인. 재발 방지로 양방향 SSH keepalive 박음.

박힌 변경 (Mac 측 `/Users/user/.ssh/config`, perms 600, mtime 2026-04-26 08:36:40):

Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes

Host wsl desktop
    HostName desktop-i4tr99i-1
    User ssamssae

WSL 측 동일 keepaliveconfig + `Host mac/mac-mini/macbook` alias 도 같이 박혀있음 (`/home/ssamssae/.ssh/config`).

검증 완료 (2026-04-26 08:36):
- WSL → ssh mac → "OK / USERui-MacBookPro.local" PASS
- Mac → ssh wsl → "OK from wsl / DESKTOP-I4TR99I" PASS

할일:
1. 이 메시지 인지했음을 텔레그램 chat 538806975 (강대종님 DM, MyClaude 봇) 으로 reply 한 줄 — "🍎 SSH keepalive 패치 인지함, Mac→WSL `ssh wsl` 단축어 확인."
2. handoffs/ 의 본 파일 frontmatter `status: open` → `status: acked` 로 변경 후 commit + push.
3. 끝.

금지사항:
- 같은 `~/.ssh/config` 다시 만들거나 덮어쓰기 금지 (덮어써도 동일 내용이라 무해하지만 의미 없음)
- ServerAliveInterval 값 멋대로 바꾸지 말 것 (60초 = 강대종님과 합의된 값)
- 핸드오프 자동화(SSH+tmux METHOD A) 의 hostname 풀네임은 그대로 유효 — alias 추가일 뿐 기존 코드 영향 없음. 다른 스크립트의 `desktop-i4tr99i-1` / `user-macbookpro-1` 풀네임 참조를 alias 로 일괄 치환 같은 짓 금지.

종료 조건:
- 텔레그램 chat 538806975 로 인지 reply 1건 도착 + handoffs 파일 status: acked 커밋 push 완료 시 종료. WSL Claude 가 git pull 로 status 변경 확인.
