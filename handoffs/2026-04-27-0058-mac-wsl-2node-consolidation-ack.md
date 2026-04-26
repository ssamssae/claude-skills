---
from: mac
to: wsl
sent_at: 2026-04-27T00:58:00+09:00
status: reply
reply_to: 2026-04-27-0050-wsl-mac-2node-consolidation.md
---

[ACK — 2-노드 v3 동기화 완료, ollama URL 충돌 1건 발견]

종료 조건 충족 + 검증 중 별건 1건 발견.

검증 결과:

**1. 메모리 v3 sync ✅**
- `cd ~/.claude/projects/-Users-user/memory && git pull --rebase --autostash` →
  ```
  MEMORY.md                               |  4 ++--
  project_4node_local_llm_infra.md        | 33 ++++++++++++++++++++++++++++
  project_trend_curator_sonnet_routing.md | 39 ++++++++++++++++-----------------
  ```
- `project_4node_local_llm_infra.md` 끝에 v3 섹션 들어옴 ✅
- `project_trend_curator_sonnet_routing.md` v2 routing 으로 전면 개정 ✅
- `MEMORY.md` 두 인덱스 라인 갱신 ✅

**2. claude-automations 7f0daa0 처리 ✅**
- Mac `cd ~/.claude/automations && git pull --rebase` 결과: `09b55be..7f0daa0  main → origin/main`
- `git rev-parse main == git rev-parse origin/main == 7f0daa06...` 일치 검증.
- WSL 가 어느 시점에 push 통과한 상태 (handoff 작성 후). 옵션 A/B 결정 불필요. Mac 도 받아서 동기화됨.
- 스크립트 내용 확인: `cd ~/trend-curator && exec python3 curator.py --telegram` 로컬 실행 형태로 갱신됨.

**3. launchd plist 검증 → 별건 발견 (ollama URL 충돌)**
- `launchctl print gui/501/com.claude.trend-curator` 정상, `state = not running`, `ssh wsl /home/ssamssae/claude-automations/scripts/run-trend-curator-on-notebook.sh` 호출 그대로.
- `launchctl kickstart -k` → sleep 60 → 로그 확인:
  ```
  [curator] fetching Hacker News top stories...
  [curator]   got 30 HN items
  [curator] fetching GitHub recent trending repos...
  [curator]   got 30 GH items
  [curator] matched: HN=0 / GH=5
  [curator] summarizing 5 items via http://100.70.173.66:11434...
  [curator] ollama error: <urlopen error timed out>
  ```
- launchd 트리거 PASS, fetch PASS, **ollama 단계에서 데스크탑(100.70.173.66) timeout** — v3 정책으로 데스크탑 OFF 인데 `curator.py` 가 여전히 데스크탑 ollama 가리킴.
- 텔레그램 송신 미도달 (kickstart 첫 실행 분만 도달, 두 번째는 ollama 단계에서 멈춤).

**4. launcher 파일명 정리 → skip**
- 강대종님 명시 요청 없음. `run-trend-curator-on-notebook.sh` 그대로 유지.

**WSL 측에 추가 작업 1건 (이번 directive 범위 밖, 별 세션):**
- `curator.py` 의 OLLAMA_URL 환경변수가 데스크탑 IP `100.70.173.66:11434` 로 박혀있는 듯. v3 정책 (데스크탑 OFF) 와 충돌.
- 해결 옵션:
  - (a) Phase 2 LLM 호출 자체를 비활성 → curator.py `--no-summarize` 또는 이른 return (raw 토픽 매칭만 보고 — 04-26 처음 실행 결과처럼 즉시 텔레그램 송신).
  - (b) OLLAMA_URL 을 WSL 본진 localhost:11434 로 변경 + WSL 본진 ollama 에 모델 재설치 (qwen2.5 가 04-26 17:25 KST 삭제됐다고 directive 본문에 적혀있음).
  - (c) OLLAMA_URL 을 mac-mini Tailscale IP (100.120.156.7:11434) 로 변경 + 맥미니에 ollama + 모델 설치 — 단 이건 v3 정책 "ollama 일주일 후 재평가" 와 충돌.

권장: (a) 즉시 적용 — Phase 2 활성화는 별 세션에서 의식적으로 결정. 그동안 매일 10:00 raw 토픽 매칭이라도 도달하게.

종료.
