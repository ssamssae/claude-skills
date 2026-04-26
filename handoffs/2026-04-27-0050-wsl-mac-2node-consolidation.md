---
from: wsl
to: mac
sent_at: 2026-04-27T00:50:00+09:00
status: open
---

[4-노드 → 2-노드 슬림화 + trend-curator routing v2 마무리]

목표:
어제(2026-04-26) 박은 데스크탑·노트북 LLM 노드가 day-1 활용도 0 으로 확인되어 강대종님이 v3 운영 정책 결정 — 2-노드 운영(Mac mini 24/7 + WSL본진 dual-purpose) + 데스크탑·노트북 OFF 평소(필요 시 power-on, SSH/schtasks 그대로 보존). 이에 맞춰 trend-curator 라우팅도 노트북 SSH hop 제거 → WSL본진 localhost 실행으로 단순화. WSL 쪽 작업은 끝났고, Mac 쪽 잔여 정리(launchd plist 검증·선택적 rename·미push commit 결정)만 남음.

목표 흐름:
- WSL 본진(이 세션 발신처) 에서 완료된 일:
  - `~/claude-automations/scripts/run-trend-curator-on-notebook.sh` 수정: 노트북 SSH hop 제거 → `cd ~/trend-curator && exec python3 curator.py --telegram` 로컬 실행. 파일명은 그대로 둠 (Mac launchd plist 가 이 경로 참조).
  - Smoke test PASS: `python3 curator.py --print` → HN+GitHub top 10 정상 생성, 2026-04-27T00:44:49 KST 리포트.
  - 데스크탑(100.70.173.66)·노트북(100.89.67.22) Tailscale 5분+ offline 확인 → 셧다운 명령 불필요(이미 OFF). SSH 키·schtasks·방화벽 그대로 보존.
  - 메모리 v3 반영: `project_4node_local_llm_infra.md`(v3 운영 정책 섹션 추가), `project_trend_curator_sonnet_routing.md`(v2 routing 으로 전면 개정), `MEMORY.md` 인덱스 두 줄 갱신. memory auto-push hook 이 fired 됐을 가능성 → Mac 쪽 메모리 폴더 git pull 로 sync 확인 필요.
  - 로컬 commit `7f0daa0` (claude-automations) — `git push origin main` 이 harness 거부됨(직접 main push 차단). 강대종님 승인 대기 상태로 텔레그램에 보고함.

할일:
1. **메모리 sync 확인 (필수)**:
   ```bash
   cd ~/.claude/projects/-Users-user/memory && git pull --rebase --autostash 2>&1 | tail -5
   ```
   - `project_4node_local_llm_infra.md` 끝에 "## 운영 정책 v3 (2026-04-27 00:40 KST 결정 — 강대종님)" 섹션이 들어왔는지 확인.
   - `project_trend_curator_sonnet_routing.md` frontmatter `name` 필드가 "trend-curator Sonnet routing (WSL master local, v2 2026-04-27)" 로 바뀌었는지 확인.
   - `MEMORY.md` 의 "4-node 로컬 LLM 인프라 가동" 라인이 "LLM 인프라: 2-노드 v3 (2026-04-27)" 로, "trend-curator Sonnet 라우팅 Phase 1" 라인이 "trend-curator routing v2 (WSL본진 localhost)" 로 갱신됐는지 확인.
   - 만약 sync 누락이면 (auto-push hook 이 안 돌았을 수 있음) WSL 본진에 SSH 들어가 원인 진단 후 수동 push 요청. 절대 Mac 에서 같은 메모리를 다시 작성해서 충돌 만들지 말 것.

2. **claude-automations 7f0daa0 처리 결정 (강대종님 답 받은 후)**:
   - 옵션 A — 강대종님이 "WSL 에서 그냥 push 해" 라고 하면: WSL 세션에 텔레그램으로 답 도착 시 WSL Claude 가 처리. Mac 은 이 옵션이면 그냥 `cd ~/claude-automations && git pull --rebase` 후 `git log -1 --oneline` 으로 7f0daa0 확인하면 끝.
   - 옵션 B — 강대종님이 "Mac 에서 처리" 라고 하면: Mac 에서 동일 변경 직접 적용:
     - 현재 WSL 본진 파일 내용은 아래 (claude-automations/scripts/run-trend-curator-on-notebook.sh):
       ```bash
       #!/usr/bin/env bash
       # Trigger trend-curator run on WSL master (this host).
       # Called by Mac launchd at 10:00 KST daily.
       # Topology: Mac -> ssh wsl -> this script -> python3 curator.py (localhost).
       # Previously hopped further to notebook (100.89.67.22). Removed 2026-04-27 KST
       # after day-1 utilization review: 2-node ops (Mac mini 24/7 + WSL master),
       # desktop/notebook shut down. TODO: rename file to run-trend-curator.sh and
       # update Mac launchd plist (com.claude.trend-curator) to match.
       set -euo pipefail

       cd "${HOME}/trend-curator"
       exec python3 curator.py --telegram
       ```
     - Mac 에서 같은 내용으로 덮어쓰고 commit 메시지는 "trend-curator Phase 1: drop notebook SSH hop, run on WSL master locally" + co-author 라인. push 후 WSL 에서 pull 받아 7f0daa0(또는 새 SHA)으로 정렬.
   - 옵션 결정 전엔 Mac 쪽에서 임의로 자동화 만지지 말 것.

3. **launchd plist 검증 (필수, 잡 깨지지 않았는지)**:
   ```bash
   launchctl print gui/$(id -u)/com.claude.trend-curator 2>&1 | head -20
   plutil -p ~/Library/LaunchAgents/com.claude.trend-curator.plist | head -30
   ```
   - plist 가 여전히 `ssh wsl /home/ssamssae/claude-automations/scripts/run-trend-curator-on-notebook.sh` 호출하는지 확인.
   - 변경 불필요(파일명 그대로). 단 1회 검증 실행:
     ```bash
     launchctl kickstart -k gui/$(id -u)/com.claude.trend-curator
     sleep 90
     tail -40 ~/Library/Logs/claude.trend-curator.log
     tail -40 ~/Library/Logs/claude.trend-curator.err.log
     ```
   - 강대종님 폰에 trend-curator 텔레그램 1통 도달하면 v2 라우팅 launchd 경로 PASS. (단 옵션 B 진행 중이면 Mac 의 push 가 끝난 후 검증.)

4. **launcher 파일명 정리 (선택, 강대종님 명시 요청 시에만)**:
   - 현재 파일명에 `-on-notebook` 잔재. 강대종님이 "정리해" 라고 하면:
     - WSL 에서 `git mv scripts/run-trend-curator-on-notebook.sh scripts/run-trend-curator.sh` + commit + push.
     - Mac plist 의 `<string>...run-trend-curator-on-notebook.sh</string>` 부분을 새 이름으로 교체.
     - `launchctl bootout gui/$(id -u)/com.claude.trend-curator || true` → `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude.trend-curator.plist` 재등록.
     - kickstart 검증 1회.
   - 강대종님 명시 요청 없으면 이번 세션에선 건드리지 말 것.

5. **Phase 2 (LLM 실호출) 는 이번 directive 범위 밖**:
   - WSL본진 ollama 에 모델 재설치(qwen2.5 는 2026-04-26 17:25 KST 삭제됨, 현재 nomic 만 남음) → curator.py `OLLAMA_URL=localhost:11434` 변경 + LLM 요약 단계 추가는 별도 WSL 세션에서 처리. Mac 에서 SSH 로 미리 만지지 말 것.

금지사항:
- 데스크탑(100.70.173.66)·노트북(100.89.67.22) SSH 키·schtasks·Tailscale 등록·방화벽 룰 제거 금지. v3 정책의 핵심은 "필요 시 power-on 으로 자동 복귀". dismantle 하면 다시 셋업 비용 큼.
- WSL본진 ollama 모델 재설치를 Mac 에서 SSH 로 시도하지 말 것 — 강대종님이 "다른 세션에서" 처리한다고 명시함.
- claude-automations / claude-skills / claude-memory 직접 force push 금지.
- 옵션 A/B 결정 전에 7f0daa0 commit 을 Mac 에서 임의로 cherry-pick / rebase / 새로 만들지 말 것.
- 메모리 충돌 발생 시 임의 resolve 하지 말고 강대종님께 보고 후 진행.
- 06:50 launchd 시간 되돌리지 말 것(10:00 KST 유지).

종료 조건:
- 메모리 v3 sync 확인 PASS + launchd plist 검증 PASS + (옵션 결정 시) 7f0daa0 처리 완료
- 텔레그램 reply 1통: "MAC: 2-노드 v3 동기화 완료. (메모리 sync OK / launchd 검증 OK / push 처리 [A or B or 보류])"
- 실패 시 정확한 실패 지점 + 관련 로그 일부를 같은 reply 로. 추측·임시방편 금지.
