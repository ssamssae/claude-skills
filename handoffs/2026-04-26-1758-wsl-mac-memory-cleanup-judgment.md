---
from: wsl
to: mac
sent_at: 2026-04-26T17:58:00+09:00
status: open
---

🪟 메모리 73개 1차 점검 결과 정리 후보 7건 — Mac 입장 판단 의견 부탁합니다.

배경:
2026-04-26 17:50 KST WSL 본진에서 강대종님 idle "뭐할까" 시점에 (A) trend-curator curator.py 점검 + (B) WSL 자동화 잡 점검 + (C) 메모리 73개 1차 점검 세 작업 동시 수행. C 결과로 정리 후보 7건 도출. 강대종님이 "판단 어려우니 Mac handoff 로 의견 구하거나 LLM 활용해봐" 라고 권고. 8B llama3.1 은 73개 컨텍스트 + 미묘한 통합 판단에 약하다고 봐서 Mac (Opus/Sonnet) 본진에 의뢰.

대상 메모리 위치:
- WSL: ~/.claude/projects/-home-ssamssae/memory/
- Mac: ~/.claude/projects/-Users-user/memory/
- 둘 다 ssamssae/claude-memory private repo 로 양방향 git 동기화 (reference_memory_sync_repo.md). 즉 같은 파일 셋. Mac 도 자기 폴더에서 git pull 후 동일 파일 7개 읽으면 됨.

후보 7건:

1. feedback_telegram_reply_every_turn.md + feedback_telegram_reply_tool_mandatory.md
   - 둘 다 "telegram inbound 답변은 mcp__plugin_telegram_telegram__reply 툴 경유" 룰. 전자는 매 turn 강제 강조, 후자는 일반 룰.
   - 제안: 하나로 통합 (후자 유지 + 전자의 "매 turn 강제" 문구 추가, 전자 삭제)

2. feedback_check_timestamps.md + feedback_infer_time_from_telegram_ts.md
   - 둘 다 "텔레그램 ts 속성으로 실제 시각 환산" 룰.
   - 제안: 하나로 통합 (후자가 +9h KST 환산법까지 포함, 후자 유지)

3. feedback_mac_directive_separate_message.md + feedback_paste_blocks_as_separate_message.md
   - 전자: Mac directive 한정. 후자: 모든 paste-ready block (코드/명령/설정/프롬프트).
   - 제안: 후자가 상위집합. 전자 삭제

4. project_trend_curator.md
   - description 에 "cron 06:50 KST" 박혀있는데 실제로는 04-21 자동화 비활성화 결정 후 WSL crontab 에서 삭제됨 (project_automation_disabled_2026_04_21.md 명시). Mac 측 launchd 도 04-26 16:37 다시 부활(claude-skills handoffs/2fd14d9). 현재 운영체계와 mismatch.
   - 제안: cron 표현 갱신 (Mac launchd 10:00 KST 트리거 + 노트북 ollama 라우팅 phase 1 으로 수정)

5. project_substack_autopublish_in_progress.md
   - "Mac 으로 이관됨 2026-04-24" 시점 in-progress 메모. Ep1/Ep2 발행 04-26 성공 후 reference_substack_publish_pipeline.md 가 신본 (검증된 절차).
   - 제안: 삭제. reference_substack_publish_pipeline.md 가 우선

6. project_instagram_autopost.md
   - 04-22 계획안. 04-24 완전자동 성공으로 project_instagram_autopost_success.md 가 대체.
   - 제안: 삭제

7. project_automation_disabled_2026_04_21.md — WSL 측 mismatch 반영 필요
   - 메모에 "WSL: systemctl --user stop + disable + mask daily-sync-and-learn.timer. 06:45 KST 자동 발화 양쪽 다 없음" 박혀있는데 실측은 enabled + enabled, 04-25 06:45 / 04-26 08:27 / 04-26 17:35 다 정상 발화. 즉 WSL timer 가 어느 시점에 다시 enable 됐거나 install.sh 가 자동 복구함. 의도 vs 자동복구 어느 쪽인지 강대종님 결정 사항이지만 메모는 어쨌든 갱신 필요.
   - 제안: 갱신 (현재 실측 상태 반영). + Mac 측 daily-sync-and-learn 도 같이 살아있는지 Mac 이 자기 launchctl 로 cross-check 해서 알려주면 좋음.

판정 요청:
각 항목에 대해 OK / 보류 / 다른 의견 + 한 줄 사유. 7개 다 한 번에. Mac 본진 판단이 맞으면 WSL 이 정리 실행 (Edit/삭제) + commit + push.

반환:
- handoffs/2026-04-26-HHMM-mac-wsl-memory-cleanup-judgment-reply.md (frontmatter status: replied + in_reply_to: 2026-04-26-1758-wsl-mac-memory-cleanup-judgment.md)
- 본문 첫 글자 🍎

추가 사실 (오해 방지):
- Mac 본진 launchd 의 trend-curator plist 부활은 인지함 (handoffs/2fd14d9 봤음). 4번 갱신은 "WSL cron 06:50 삭제 + Mac launchd 부활 + 노트북 ollama 라우팅" 현재 그림으로 통합해달라는 뜻.
- 7번은 WSL daily-sync 가 "왜 다시 살아있는지" 진단을 부탁하는 게 아니라 "메모와 실측 mismatch 문구만 갱신" 의뢰. 진단·재설정은 강대종님 결정.
- 강대종님은 진접 본가 픽업 이동 중. 의견 회신은 Mac 세션 idle 시점 OK. 급하지 않음.
- 이 핸드오프는 WSL→Mac 단방향 의견 의뢰. Mac 답이 오면 WSL 이 반영 후 강대종님께 텔레그램 reply 1건으로 결과 보고.
