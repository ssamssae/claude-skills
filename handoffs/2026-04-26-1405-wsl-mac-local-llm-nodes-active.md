---
from: wsl
to: mac
sent_at: 2026-04-26T14:05:00+09:00
status: done
---

🪟 [4-노드 로컬 LLM 인프라 가동 — 데스크탑·노트북 신입 합류]

목표:
강대종님 인프라가 4-노드로 확장됨을 맥(오케스트레이터) Claude 가 알게 한다. 직접 액션 할 일은 없고 컨텍스트 등록 + 메모리 갱신만 진행하면 끝.

배경:
오늘 14:00 KST 이전까지 WSL 본진에서 새 데스크탑·노트북 두 대 셋업 진행. 양쪽 다 Windows 네이티브 ollama (llama3.1:8b-instruct-q4_K_M Q4_K_M, 4.92GB 모델 적재) + Tailscale 합류 + WSL 본진 SSH 키 등록 완료. 한국어 추론 양쪽 다 검증 통과.

새 노드 정보:
- 🪟 데스크탑 호스트명 DESKTOP-0VAB3QC, Tailscale 100.70.173.66, RTX 3060 Ti 8GB, ollama 75 tok/s, ollama 트레이앱 자동시동
- 💻 노트북 호스트명 DESKTOP-4MNJ1C0 (리전5), Tailscale 100.89.67.22, RTX 3060 Laptop 6GB, ollama 22 tok/s, schtasks ONLOGON + VBS hidden 모드 자동시동
- 양쪽 SSH: ssh user@100.70.173.66 / ssh user@100.89.67.22 (계정명 user, 키 인증, administrators_authorized_keys)
- 양쪽 ollama API: http://100.70.173.66:11434 / http://100.89.67.22:11434 (LAN 전용, 인증 없음)

4-노드 전체 그림:
- 🍎 맥 = 본진 오케스트레이터 (이 세션), 봇 @MyClaude, iOS 빌드, Opus
- 🪟 WSL 본진 = 핸드오프/Android, 봇 @Myclaude2
- 🪟 데스크탑 = 로컬 LLM 75 tok/s (속도 우위, 즉응 작업)
- 💻 노트북 = 로컬 LLM 22 tok/s (밤새 배치 작업 적합)

신입(데스크탑·노트북) 능력 한계:
- 한국어 텍스트 생성·번역·간단 코딩 OK
- 산수/논리 추론 ❌ (8B 한계, 단순 사칙연산도 헛소리)
- 도구 호출(파일·git·웹) ❌ (텍스트 in/out 만 가능)
- 긴 컨텍스트 추론 ❌ (Claude 압승)
- 본진/맥에서 던지는 curl 한 번이 호출 단위. 라우팅·결과 수거 파이프라인은 아직 0

테스트 결과 요약 (참고만):
- 한국어 자기소개: 둘 다 자연스러움
- 사과 5개 친구 3명 분배 산수: 둘 다 실패 (15개·45-30 헛소리)
- 파이썬 리스트 dedup: 둘 다 정답 (set vs dict.fromkeys)
- lazy dog 영한: 노트북이 더 정확 ("게으른" vs "느려진")
- 속도: 데스크탑 ~75 tok/s, 노트북 ~22 tok/s

운영 함정:
- 노트북 11434 포트가 winnat 자동 제외 범위(11361-11460) 에 잡혀서 일회성 트릭(net stop winnat → ollama 시동 → net start winnat) 으로 풀어둔 상태. 재부팅 시 재발 가능성 50:50. WSL 본진은 재부팅 직후 새 세션으로 검증 예정.
- 노트북 ollama 콘솔창은 VBS 래퍼(C:\Users\user\ollama-hidden.vbs) + schtasks 로 hidden. 데스크탑은 트레이앱이라 함정 무관.

할일:
1. 위 정보를 맥 메모리(`~/.claude/projects/-Users-user/memory/`) 에 새 메모 또는 기존 `multi_device_rules.md` 갱신으로 등록. 핵심: 4-노드 IP/모델/토큰속도 + 능력 한계.
2. 강대종님께 텔레그램(@MyClaude 챗) 으로 reply 1건 — "맥 입장에서 받은 신입 두 명 인지함, 메모리 갱신 끝, 다음 세션부터 라우팅 짤 수 있음" 정도.
3. (선택) 라우팅 파이프라인 첫 시범 케이스를 한두 줄 제안. 추천 후보:
   - 트렌드 큐레이터 보조 (HN/GitHub 매칭 → 노트북 한국어 1차 요약 → 아침 브리핑은 Claude)
   - 메모리 의미검색 임베딩 (Claude 컨텍스트 절약)
4. 종료 조건 충족 시 이 파일 frontmatter status `done` 으로 갱신 + 같은 폴더 `-reply.md` 답신 파일 1개 작성 (간단 한 단락 + push).

금지사항:
- 데스크탑·노트북 SSH·ollama 셋업 자체는 건드리지 말 것 (본진에서 도는 게 끝). 검증 차원에서 curl 한 방씩 찔러보는 건 OK.
- 본진(WSL) 새 세션이 노트북 재부팅 검증 진행 중일 수 있음. 양쪽이 동시에 노트북 만지면 충돌 — 검증은 본진에 맡기고 맥은 인지·메모리만.
- settings.json 자가편집 금지 (양쪽 다 일관 거부됨, /update-config 로 우회).

종료 조건:
- 메모리 갱신 + 강대종님 텔레그램 reply 1건 완료 + 이 파일 status=done 으로 commit+push.
- 강대종님 텔레그램 reply 는 chat_id 538806975, 봇 @MyClaude. 본문 첫 글자는 🍎 (sender 이모지) 필수.
