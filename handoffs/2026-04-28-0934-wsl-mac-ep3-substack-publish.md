---
from: wsl
to: mac
sent_at: 2026-04-28T09:34:00+09:00
status: open
---

🪟 바이브코딩 뉴스레터 Ep.3 Substack 발행

목표:
ep3-substack.md 본문을 daejongkang.substack.com 에 신규 newsletter post 로 자동 발행하고 공개 URL + 리치포맷 검증 카운트를 강대종님께 텔레그램 보고. Ep.1·Ep.2 와 동일 파이프라인 (`reference_substack_publish_pipeline.md`).

목표 흐름:
WSL 본진에서 ep3-substack.md 작성 + dcacb85 로 daejong-page main 푸시 완료 (276줄, ~20KB). 본문은 1~3막 원본 유지 + 4막 정리 + 5막 옵션 X 결말 (맥미니마저 박지 않기 + 데스크탑/노트북 동결 + trend-curator 폐기 = 빼기 두 번). 4-노드 LLM v4 결정(2026-04-27)이 글의 진짜 클로징으로 들어옴. 강대종님이 본문 사전 검토 없이 즉시 발행 옵션(A) 선택 → Mac 핸드오프 즉시 발사. Mac 에서만 발행 가능 (Playwright MCP + macOS NSPasteboard).

할일:
1. cd ~/daejong-page && git pull --rebase (dcacb85 가 최신 head 인지 확인. 그 위에 자동 activity 커밋 더 있을 수 있음)
2. newsletter/ep3-substack.md 의 마커 섹션 추출:
   - 📋 TITLE 다음 줄: "70만원짜리 인프라 사려다가 본가에서 0원으로 끝낸 1시간"
   - 📋 SUBTITLE 다음 줄: "바이브코딩 뉴스레터 Ep.3 — 1인 개발자의 인프라 빼기, 그리고 그 다음날 빼기가 한 번 더 일어난 이야기"
   - 📋 BODY (아래부터 끝까지 Substack 본문 복붙) 마커 다음 --- 부터 끝까지가 본문
3. 본문에 markdown 표 1개 (4막 비교표, 4행). `reference_substack_publish_pipeline.md` 의 Python transform 함수로 `- **헤더**: 값 / **헤더**: 값` 형식 리스트로 변환
4. python3 markdown 라이브러리 HTML 변환:
   `python3 -c "import markdown; print(markdown.markdown(open('/tmp/body.md').read(), extensions=['fenced_code','tables','sane_lists']))"` → /tmp/body.html
   (nl2br extension 절대 금지 — 빈 줄 블록 분리 깨짐)
5. NSPasteboard 에 HTML+plain 동시 set (pipeline 메모리의 osascript + AppKit 블록 그대로):
   - public.html ← /tmp/body.html
   - public.utf8-plain-text ← /tmp/body.md
   - encoding 4 (NSUTF8StringEncoding) 한글 안전
6. Playwright MCP 로 https://daejongkang.substack.com/publish/post?type=newsletter 진입
7. Title textarea (placeholder="Title") + Subtitle textarea (placeholder="Add a subtitle…") 채우기 — native value setter + input/change dispatch 또는 browser_type
8. 본문 에디터 클릭 포커스 → ControlOrMeta+a → Delete → ControlOrMeta+V (NSPasteboard 의 HTML 이 tiptap 으로 리치 포맷 그대로 들어감)
9. publish-button (data-testid) → 모달 → "Send to everyone now" 클릭 → /share-center?alreadyPublished=true 리다이렉트로 성공 확인
10. 공개 URL https://daejongkang.substack.com/p/<slug> 진입해서 article DOM 의 h2 / strong / blockquote / ul / li / table 카운트
11. 텔레그램 reply (chat_id 538806975) 로 결과 보고: 공개 URL + 검증 카운트(h2 N, strong M, blockquote K, ul P, li Q). 표는 리스트 변환됐으니 table 0 정상. 실패 시 막힌 step + 화면 스냅샷.

분기:
- /tmp/body.md 에 표가 그대로 남아있으면 (transform 함수 미적용) → step 3 부터 재시작
- Playwright Substack 로그인 세션 만료 시 → 로그인 후 재시도 (별도 directive 발생, 강대종님께 텔레그램으로 상태 보고)
- publish-button 모달이 "Send to everyone now" 가 아니라 "Publish without buttons" 만 있으면 → "Publish without buttons" 로 진행 (구독자 0 동작 안전)
- 검증 단계에서 h2 카운트 < 7 이면 → 본문 paste 가 mangled 됐을 가능성, 화면 스냅샷 + paste 직전 /tmp/body.html 일부 head 100줄 텔레그램 보고

금지사항:
- 본문 마크다운 임의 수정 금지. 5막 옵션 X 결말이 v4 결정 그대로 옮긴 거라 톤 보존이 중요. 강대종님이 사전 검토 안 한 상태에서 발행하기로 한 결정이라 Mac 측에서 임의로 문장 다듬으면 회귀 사고
- 표 → 리스트 변환은 OK (Substack table 노드 미지원, 검증된 회피책)
- 이미지 placeholder 4컷 (🖼 IMAGE 1~4) 은 그대로 두기. 강대종님이 발행 후 Substack 에디터에서 수동 업로드 예정
- SUBSCRIBE CTA 자리 (💌 SUBSCRIBE CTA 1, 2) 도 마크다운 텍스트로 그대로 두기. 강대종님이 Substack 에디터 안에서 Subscribe 블록 수동 삽입
- 사이드 박스 (Ep.2 Gmail OAuth 예고 정정) 한 단락도 그대로. 본문 흐름 깨면 빼도 된다는 주석은 발행 후 강대종님 본인 판단 영역
- nl2br extension 사용 금지
- 발행 도중 daejong-page repo 에 별도 commit 금지 (이번 발행 작업 자체는 ep3-substack.md 변경 없이 외부 발행만)
- "기존 글 update" 아니라 신규 newsletter post (ep3 가 daejongkang.substack.com 에 처음 올라가는 글)

종료 조건:
공개 URL 접근 가능 + h2 7개 이상 (1막~7막 + 메타 + 다음 이야기 = 9개 예상, 마진 7) + table 0 (전부 리스트 변환 확인) + 강대종님 텔레그램 reply 로 URL+카운트 보고 완료. 실패 시 막힌 step + 스냅샷 + 강대종님 판단 요청.
