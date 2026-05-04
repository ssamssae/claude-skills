# /session-clear — 텔레그램에서 현재 세션 클리어

## 용도

텔레그램 채팅에서 현재 Claude Code 세션을 `/clear` 하는 스킬.  
원래 텔레그램 창에서 `/clear` 를 직접 보낼 수 없어서 이 스킬로 대신한다.

**트리거:** "세션 클리어", "클리어 해줘", "세션 초기화", "/session-clear"

## 절차

1. 텔레그램 reply 전송 (chat_id 538806975):
   ```
   🔄 [기기아이콘] [hostname] [HH:MM KST]
   세션 클리어합니다
   ```

2. sleep 2 후 tmux send-keys:
   ```bash
   TMUX_BIN=/opt/homebrew/bin/tmux  # Mac
   # WSL: /usr/bin/tmux
   sleep 2 && $TMUX_BIN send-keys -t claude "/clear" Enter
   ```

## 실행 코드

```python
import subprocess, time

host = subprocess.check_output("hostname", shell=True).decode().strip()
is_mac = "MacBook" in host or "MBP" in host or "mac" in host.lower()
tmux = "/opt/homebrew/bin/tmux" if is_mac else "/usr/bin/tmux"

# 텔레그램 reply는 스킬 실행 직전 Claude가 먼저 전송
time.sleep(2)
subprocess.run([tmux, "send-keys", "-t", "claude", "/clear", "Enter"])
```

## 주의

- tmux 'claude' 세션이 없으면 조용히 실패 (에러 없음)
- `/clear` 가 전송되면 이 대화 컨텍스트가 초기화됨 — 진행 중인 작업 있으면 먼저 확인
- parallel-cycle 끝에 session-close 가 자동 호출할 때와 동일한 메커니즘

## 버전

- v0.1 (2026-05-04): 초기 버전 — session-close 의 /clear 부분만 독립 분리
