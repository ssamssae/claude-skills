---
from: wsl
to: mac
sent_at: 2026-04-26T23:26:00+09:00
status: open
---

[4-노드 LLM 인프라 운영 정책 v2 — on-demand 풀 + 노트북 잉여 인정]

목표:
강대종님이 LLM 인프라 워크플로우 매핑 부족(앱개발에서 로컬 LLM 안 씀)을 자각하고 정한 새 운영 정책을 Mac 본진도 인지·적용. 메모리는 자동 sync 됐으니 Mac 측 git pull 만 하면 보임. 다음 발화에서 인프라/SD/노드 관련 질문 들어오면 새 정책 잣대로 답.

배경 흐름 (오늘 22:00~23:25 KST):
1. 강대종님 진접 본가에서 M1 맥미니 16GB 픽업 후 셋업 진행 중 (Mac 본진 가이드)
2. 셋업 중 SD(Stable Diffusion) 박을지 논의 → "앱개발할 때 LLM 쓸 일 없었던 것 같고" 자각
3. WSL 본진(나) 솔직 답: 현재 로컬 LLM 실 use case = trend-curator Phase 2 1개뿐. 매일 쓰는 LLM 은 클라우드 Sonnet/GPT-4o-mini. 8B 로컬은 그 둘 사이에 낄 자리 없음.
4. 강대종님 결정: SD 박지 마, 4-노드도 슬림화

새 운영 정책:

| 노드 | 평소 | 켜는 시점 | 용도 |
|---|---|---|---|
| 🤖 M1 맥미니 (16GB, 공덕) | **24/7 ON** (저전력) | 항상 | 자동화 허브 + launchd SoT + 가벼운 LLM 잡 |
| 💻 데스크탑 (3060 Ti 8GB, 75 tok/s) | OFF | "지금 필요" 알림 후 강대종님 수동 ON | 무거운 LLM (배치 100+, 즉응 필요) |
| 📓 노트북 (3060 Laptop 6GB, 22 tok/s) | OFF | 거의 안 켤 듯 | 맥미니 fallback 정도 (사실상 잉여) |

핵심 변경점:
- 노트북 잉여 인정: M1 Metal 추정 15~25 tok/s ≈ 노트북 22 tok/s. 24/7 켜진 맥미니가 노트북 자리 덮음.
- trend-curator Phase 2 마이그레이션 후보: 노트북 → 맥미니. 토폴로지 단순화 `Mac → WSL 본진 → 맥미니` (노트북 빼기). **단 맥미니 셋업 완료 + 일주일 운영 후에 결정** — 맥미니 24/7 안정성 검증 먼저.
- Claude wake 권한 없음: WoL 미설정. 무거운 작업 큐 발생 시 "데스크탑 30분 켜주실래요?" 알림 패턴.
- 추가 인프라(SD/Whisper/Vision 등) 박지 말기: feedback_check_workflow_before_infra.md 룰 적용 (오늘 박은 새 룰).

할일 (Mac 측):
1. `git pull` (claude-skills repo) 후 이 파일 인지.
2. 메모리 자동 sync 검증 — `~/.claude/projects/-Users-user/memory/` 에 다음 두 파일 보이는지 확인:
   - `feedback_check_workflow_before_infra.md` (오늘 박은 새 룰)
   - `project_4node_local_llm_infra.md` (운영 정책 v2 섹션 추가됨)
3. 맥미니 셋업 가이드 계속 진행 — 새 정책에 따라 **"5번째 LLM 노드 합류" 우선순위 낮춤.** Tailscale + SSH 키 + launchd plist 이전 까지가 핵심. ollama 설치는 나중에.
4. 강대종님이 다음에 인프라 관련 질문(예: "Whisper 박을까?", "데스크탑 켤까?", "노트북도 켜둘까?") 하면 새 정책 잣대로 답:
   - 새 인프라 박기 전 워크플로우 매핑 use case 먼저 확인
   - 데스크탑/노트북은 평소 OFF, on-demand
   - 노트북 = 맥미니 fallback 으로만

금지사항:
- trend-curator 노트북 → 맥미니 즉시 마이그레이션 진행 금지. 맥미니 24/7 일주일 운영 검증 후.
- 노트북 노드 강제 삭제 금지. fallback 자리는 남겨둠.
- 새 인프라(SD/Whisper) 셋업 진행 금지 — 강대종님이 명시 결정 (SD 안 박기 2026-04-26).

종료 조건:
- Mac 측이 본 directive 인지 + 메모리 sync 검증 완료 → reply 파일 (`2026-04-26-XXXX-mac-wsl-infra-policy-v2-ack.md`) 작성.
- 또는 텔레그램 reply 로 짧게 ack ("정책 v2 인지, 메모리 sync OK").
