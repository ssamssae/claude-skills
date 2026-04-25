---
prevention_deferred: null
---

# /handoff METHOD A 회귀 — 무복붙 인프라 두고 복붙 폴백으로 빠짐

- **발생 일자:** 2026-04-26 08:38 KST
- **해결 일자:** 2026-04-26 08:43 KST
- **심각도:** medium
- **재발 가능성:** medium
- **영향 범위:** handoff 스킬, 크로스 디바이스 워크플로우

## 증상

강대종님이 "쏴줘 그래도 알고는 있어야지 맥도" 라며 SSH keepalive 패치 사실을 Mac Claude 에게 통보 요청. WSL Claude 가 답변에 "📨 MyClaude(맥) 챗에 복붙해서 보내주세요 ↓" 라며 fallback reply 모드로 빠짐. 강대종님 직접 지적: "무슨소리하는거야 직접 쏴주기로 어제 약속했잖아 양방향 그래서 만든거아니야 어제 하루종일".

## 원인

- 어제(2026-04-25) METHOD A (SSH+tmux send-keys 무복붙) e2e PASS 후 메모리(`project_handoff_bidirectional_zero_touch.md`)에는 박아뒀지만 행동 강제로 안 이어짐
- handoff SKILL.md description 의 트리거 키워드가 "/handoff", "맥에 시켜", "맥으로 넘겨" 등 구체적 표현 위주 → "쏴줘 / 알게" 같은 짧은 발화에서 미발화
- 답변에 "복붙" 단어 자동 등장 → reply 모드로 흘러감

## 조치

1. handoff/SKILL.md description 트리거 키워드 확장 + 함정 경고 추가 (커밋 2267a18 push 됨)
2. 메모리 추가: `feedback_handoff_method_a_default.md` (감지→메서드 선택 5단계 체크리스트)
3. METHOD A 실제 실행으로 e2e PASS 검증: handoffs/2026-04-26-0839-wsl-mac-ssh-keepalive-patch-notice.md (commit 28e9e9a) → Mac ack (d6acc91, status: open→acked)

## 예방 (Forcing function 우선)

- handoff SKILL.md description 키워드 확장 박힘 ("쏴줘 / 맥도 알게 / 양방향 / 둘 다 알게" 등). 짧은 발화에서도 스킬 발화 강제
- description 본문에 함정 경고 명시: "복붙해서 보내주세요" reply 폴백 회귀 = 어제 인프라 무시. 매 description 로드 시 자기점검 강화
- 메모리 `feedback_handoff_method_a_default.md` 의 "How to apply" 5단계: (1) 발화 패턴 감지 → (2) "복붙해서/paste" 가 답변에 들어가려 하면 STOP → (3) METHOD A 가능 여부 검토 (SSH/peer 세션 살아있나) → (4) 명시 "복붙용으로 만들어줘" 만 fallback 허용 → (5) 표준 흐름 (handoffs/ 작성→commit→push→SSH+tmux ping)
- 행동 강제: "복붙해서" 가 답변 draft 에 들어가는 순간을 Stop hook 으로 잡는 건 후속 검토 (오탐 위험 있어 보류)

## 재발 이력

(처음)

## 관련 링크

- 커밋: 2267a18 (skill description), 28e9e9a (handoff dispatch), d6acc91 (mac ack)
- 메모리: `feedback_handoff_method_a_default.md`, `project_handoff_bidirectional_zero_touch.md`
- 텔레그램: 사용자 msg 2754 ("무슨소리하는거야 직접 쏴주기로 어제 약속했잖아")
