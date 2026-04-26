---
from: wsl
to: mac
sent_at: 2026-04-26T15:30:00+09:00
status: open
---

[trend-curator launchd 부활 — 노트북 외곽 워커 라우팅]

목표:
오늘 결정된 4-노드 라우팅의 Phase 1 마무리. trend-curator 를 매일 10:00 KST 에 노트북(Sonnet 외곽 워커, Tailscale 100.89.67.22) 에서 자동 실행하도록 Mac launchd plist 를 새로 작성한다. 이전 06:50 launchd 잡은 2026-04-21 자동화 비활성화 때 죽었으니 새 plist 부활이 맞음.

목표 흐름:
- WSL 본진: trend-curator 를 ssamssae/trend-curator private repo 로 분리, 노트북에 clone, .env(텔레그램 token) chmod 600 으로 복사, 시범 실행 → 강대종님 폰 텔레그램 도달 검증 PASS (15:25 KST). 추가로 wrapper `~/claude-automations/scripts/run-trend-curator-on-notebook.sh` 작성·push 됨 (commit 58e9977 또는 그 이후 main).
- Mac: 그 wrapper 를 호출하는 launchd plist 만 만들면 끝.

할일:
1. `cd ~/claude-automations && git pull --rebase` 로 wrapper 스크립트 받기. `ls scripts/run-trend-curator-on-notebook.sh` 확인 (실행권한 +x).

2. wrapper 동작 확인:
   ```bash
   ssh wsl /home/ssamssae/claude-automations/scripts/run-trend-curator-on-notebook.sh
   ```
   - 끝까지 실행되고 강대종님 폰에 트렌드 텔레그램 1통 도달하면 PASS.
   - 실패 시 ssh wsl 키 인증 + WSL→노트북 키 인증 둘 다 살아있는지부터 확인.

3. launchd plist 작성: `~/Library/LaunchAgents/com.claude.trend-curator.plist`
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
     <key>Label</key>
     <string>com.claude.trend-curator</string>
     <key>ProgramArguments</key>
     <array>
       <string>/usr/bin/ssh</string>
       <string>wsl</string>
       <string>/home/ssamssae/claude-automations/scripts/run-trend-curator-on-notebook.sh</string>
     </array>
     <key>StartCalendarInterval</key>
     <dict>
       <key>Hour</key>
       <integer>10</integer>
       <key>Minute</key>
       <integer>0</integer>
     </dict>
     <key>StandardOutPath</key>
     <string>/Users/user/Library/Logs/claude.trend-curator.log</string>
     <key>StandardErrorPath</key>
     <string>/Users/user/Library/Logs/claude.trend-curator.err.log</string>
     <key>RunAtLoad</key>
     <false/>
   </dict>
   </plist>
   ```
   - launchd 환경은 사용자 셸과 달라서 `ssh-agent`/키체인 키를 못 잡을 수 있음. 만약 ssh wsl 가 키 인증 실패하면 plist 의 ProgramArguments 첫 단계를 `/bin/bash -lc 'ssh wsl ...'` 로 감싸서 인터랙티브 셸을 강제하든가, `<key>EnvironmentVariables</key>` 로 SSH_AUTH_SOCK 명시.

4. plist 등록:
   ```bash
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude.trend-curator.plist
   launchctl print gui/$(id -u)/com.claude.trend-curator | head -10
   ```

5. 즉시 1회 실행으로 launchd 경로 검증 (강대종님 폰에 또 1통 도달):
   ```bash
   launchctl kickstart -k gui/$(id -u)/com.claude.trend-curator
   sleep 60
   tail -30 ~/Library/Logs/claude.trend-curator.log
   tail -30 ~/Library/Logs/claude.trend-curator.err.log
   ```

6. 완료 후 메모리 갱신 (양쪽 다):
   - `project_4node_local_llm_infra.md` 의 "라우팅·결과 수거 파이프라인은 아직 0" 표현을 "Phase 1 완료: trend-curator → 노트북 (10:00 KST launchd)" 로 업데이트.
   - 만약 새 메모리 만든다면 `project_routing_phase1_done.md` 같은 이름.

금지사항:
- launchd plist 의 ProgramArguments 안에서 `python3 /Users/.../curator.py` 같은 Mac 로컬 직접 호출 금지. trend-curator 는 노트북에 있어야 라우팅 의미가 있음 (Sonnet 외곽 워커 시나리오의 핵심).
- 06:50 으로 시간 되돌리지 말 것 — 강대종님이 명시적으로 10:00 으로 옮겼음.
- claude-skills 또는 trend-curator repo 직접 force push 금지.
- Phase 2~4 (review-status-check / insta-post / night-runner) 는 이번 directive 범위 밖. 손대지 말 것.

종료 조건:
- launchd plist 등록 완료 + kickstart 1회 텔레그램 도달 확인 + log 정상 + 메모리 갱신
- 텔레그램 reply 1통: "MAC: trend-curator launchd 부활 완료 (10:00 KST). 검증 1통 도달 확인."
- 또는 실패 시 같은 reply 로 정확한 실패 지점 + log 일부 보고. 추측·임시방편 금지.
