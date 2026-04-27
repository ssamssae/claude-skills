---
from: wsl
to: mac
sent_at: 2026-04-27T22:28:00+09:00
status: open
---

🪟 [WSL→MAC HANDOFF] hanjul push 사고 issue 정리 + settings.json KeyError 후속

배경. WSL 측에서 hanjul main push 가 default-branch classifier 에 막혀 issue 등록 진행했는데, 같은 시간에 Mac 본진도 별도 issue 2건 (`fe168ca`, `9e95d3b`) 박아둠. push 후 git pull 에서 양쪽 issue 발견. 강대종님 텔레그램 메시지 (msg 3459 "1, 2" + msg 3460 "2번은 맥 핸드오프") 로 두 옵션 모두 진행 결정 — 본 directive 가 그 두 작업 위임.

상태:
- WSL 측 issue 파일 `issues/2026-04-27-harness-default-branch-push-block.md` 끝에 "⚠️ 중복 알림" 섹션 박음 (canonical = Mac 의 wsl-hanjul-push-classifier-block.md). 이 commit 본 directive 와 함께 push 됨.
- WSL settings.json paste 룰 2개 (`Bash(cd ~/apps/hanjul && git push*)`, `Bash(cd /home/ssamssae/apps/hanjul && git push*)`) 정상 박힌 상태로 추정 — push 통과는 텔레그램 1회성 인가가 먼저 반응했어서 룰 매칭 자체는 다음 push 때 검증 가능 (`hanjul-push-retry-reply.md` 참고).

작업 1. issue 파일 정리 (Mac 측 canonical 에 reciprocal cross-link 추가):

- `issues/2026-04-27-wsl-hanjul-push-classifier-block.md` 본문 끝(또는 적절한 위치)에 한 줄 추가:
  > 보완 자료: `2026-04-27-harness-default-branch-push-block.md` (WSL 발신) — 재발방지 옵션 A/B/C 비교 정리.
- 본문 다른 부분 손대지 말 것 (Karpathy 룰 3 — 국소 변경).
- 두 파일 합치기·하나 삭제 하는 consolidation 은 **하지 말 것**. cross-link 만으로 중복 정리 충분, 양쪽 다 별개 perspective 갖고 있음.

작업 2. settings.json KeyError 후속 정리:

배경. Mac 세션이 첫 paste 명령 발송 시 WSL settings.json 에 `permissions.allow` 키 부재로 KeyError 발생 → defensive 형태(`setdefault`) 로 재발송 → 통과. Mac 측 issue update commit `9e95d3b` 에 sub-incident 기록됨.

확인할 거:
- WSL settings.json 의 현재 구조 검증 (강대종님이 SSH 로 직접 read 가능하면 했으면 함, 아니면 강대종님 직접 다음 세션 때 cat 로 확인 부탁). 두 룰이 정확히 어디(top-level `permissions.allow` 배열) 박혔는지 검증.
- 다음 신규 앱 추가 시 paste 명령 짜는 패턴: `setdefault('permissions',{}).setdefault('allow',[])` 형태로 항상 defensive — 새 앱 핸드오프 directive 에 패턴 명시.
- 이 패턴을 메모리 또는 issue 의 "예방" 섹션에 명문화.

저장 후:
1. claude-skills push.
2. 결과 텔레그램 reply 1줄 (Mac → 강대종님): "🍎 hanjul push 사고 issue cross-link 정리 + KeyError defensive 패턴 명문화 완료" 형태. 첫 글자 🍎 필수.
3. 답신 핸드오프 push (handoffs/2026-04-27-XXXX-mac-wsl-issue-cross-link-and-keyerror-followup-reply.md, frontmatter reply_to 본 파일, status done).

금지:
- 두 issue 파일 consolidation/삭제 금지. cross-link 만.
- WSL settings.json 직접 수정 금지 (paste 는 강대종님 영역).
- WSL apps 내 다른 repo 손대지 말 것.

종료 조건. (a) Mac 측 issue 파일에 cross-link 한 줄 추가됨 + push, (b) defensive paste 패턴이 메모리/issue 어딘가에 명문화됨 + push, (c) 텔레그램 결과 reply, (d) 답신 핸드오프 push.
