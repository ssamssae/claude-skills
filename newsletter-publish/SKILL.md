---
name: 뉴스레터 통합 발행 (Substack + 홈페이지 + 네이버 블로그)
description: 뉴스레터 ep 1개를 Substack / daejong-page 홈페이지 / 네이버 블로그 3채널에 한 번에 발행. Mac 본진 한정. 트리거 "/newsletter-publish <N>", "뉴스레터 발행 EpN", "EpN 셋다 올려", "EpN 다 올려줘".
---

# 뉴스레터 통합 발행 v0

뉴스레터 ep 1개의 마크다운 (`~/daejong-page/newsletter/ep<N>-<DATE>.md`) 을 다음 3채널에 자동 발행한다:

1. **Substack** (`daejongkang.substack.com`) — Playwright MCP 내장 Chromium 으로 publish/post 진입 → 본문 paste → publish-button → "Send to everyone now"
2. **홈페이지 뉴스레터** (`https://ssamssae.github.io/daejong-page/newsletter.html`) — Substack URL 로 `sync_from_substack.py` 실행 → cache + index.json → daejong-page commit + push
3. **네이버 블로그** (`blog.naver.com/ssamssae`) — SmartEditor ONE, OS-level Cmd+V (naver-blog-publish v1 절차)

각 채널 독립적으로 진행. 한 채널 실패해도 나머지는 계속 (B+C 페일 모드).

## 0. 사전 가드

1. `hostname` = `USERui-MacBookPro*` 인지 확인. 아니면 즉시 중단.
2. 4조건 inherited (네이버):
   - 본인 계정 + 본인 블로그 / 본인 자동로그인 세션
   - 1일 1~2건 (강대종 directive 로 override 가능, surface 후 진행)
   - 기본 전체공개 (all)
3. 입력 인자:
   - `<ep_num>` (필수) — 1, 2, 3, 5 등 정수
   - `--md <path>` (옵션, 없으면 `~/daejong-page/newsletter/ep<N>-2*.md` 패턴으로 lookup. `outline`/`cache`/`bak-` 파일 제외)
   - `--subtitle <text>` (옵션, 없으면 md 본문 첫 italic 라인)
   - `--skip-substack` / `--skip-homepage` / `--skip-naver` (개별 채널 스킵)

## 1. 본문 준비

```bash
python3 ~/.claude/skills/newsletter-publish/scripts/prepare_body.py "$MD" 
# stdout 2 lines:
#   title: <captured h1>
#   subtitle: <first italic line under title, if any>
# 출력 파일:
#   /tmp/nl_body.md   plain markdown (table→list, h1·HTML 주석 제거)
#   /tmp/nl_body.html HTML (fenced_code+sane_lists, no nl2br)
```

`--subtitle` 인자 우선. 없고 md 첫 italic 도 없으면 빈 문자열.

## 2. Substack 발행

(`reference_substack_publish_pipeline.md` 의 검증된 절차)

### 2-1. Playwright 세션 점검 + 글쓰기 페이지

```javascript
mcp__plugin_playwright_playwright__browser_tabs(action='new', url='https://daejongkang.substack.com/publish/post?type=newsletter')
```

페이지가 publish/post UI 로 정상 진입. 로그인 안 됐으면 substack.com 탭에서 로그인 닉네임 확인 후 강대종에게 1회 로그인 요청 + 작업 중단.

### 2-2. 제목 + 부제 입력

```javascript
() => {
  const title = '<TITLE>';
  const subtitle = '<SUBTITLE>';
  const titleEl = document.querySelector('textarea[placeholder="Title"]');
  const subEl = document.querySelector('textarea[placeholder="Add a subtitle…"]');
  const setNative = (el, val) => {
    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    setter.call(el, val);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };
  setNative(titleEl, title);
  if (subtitle) setNative(subEl, subtitle);
  return { titleVal: titleEl.value, subVal: subEl.value };
}
```

### 2-3. 본문 paste (Substack tiptap = Playwright synthetic Cmd+V OK)

```bash
~/.claude/skills/newsletter-publish/scripts/pb_set_html.sh /tmp/nl_body.html /tmp/nl_body.md
```

```javascript
// Click body editor
mcp__plugin_playwright_playwright__browser_click(target='div[role="textbox"][contenteditable="true"]')
mcp__plugin_playwright_playwright__browser_press_key(key='ControlOrMeta+a')
mcp__plugin_playwright_playwright__browser_press_key(key='Delete')
mcp__plugin_playwright_playwright__browser_press_key(key='ControlOrMeta+v')
```

(2-3 초 대기) — Substack 의 tiptap 은 CDP synthetic paste 를 받아 HTML 해석.

### 2-4. 발행 + Send to everyone now

```javascript
// Step 1: Continue / Publish
mcp__plugin_playwright_playwright__browser_click(target='button[data-testid="publish-button"]')
// Step 2: 모달의 "Send to everyone now" 클릭
() => {
  const btns = Array.from(document.querySelectorAll('button')).filter(b => b.offsetParent && /Send to everyone now|Publish/.test(b.innerText));
  if (btns[0]) btns[0].click();
  return { clicked: !!btns[0], text: btns[0]?.innerText };
}
```

5~8초 대기 → `/share-center?alreadyPublished=true` redirect 또는 `/p/<slug>` URL 캡처.

### 2-5. URL + 검증

```javascript
() => ({ url: location.href });
```

slug 추출: `https://daejongkang.substack.com/p/<slug>`. 공개 URL fetch 로 article DOM 의 h1/h3 매치 (선택, 검증 단계 8 에서).

## 3. 홈페이지 sync

```bash
python3 ~/daejong-page/scripts/sync_from_substack.py --url "$SUBSTACK_URL" --ep $N
```

→ `~/daejong-page/newsletter/ep<N>-cache.md` (2026-05-01 패치 후 분리 캐시 파일) + `index.json` 갱신.

```bash
cd ~/daejong-page
git pull --rebase origin main
git add newsletter/
git commit -m "newsletter(ep<N>): substack 발행 후 cache + index.json 갱신"
git push origin main
```

GitHub Pages 1~2분 후 https://ssamssae.github.io/daejong-page/newsletter.html 카드 + view.html 본문 반영.

## 4. 네이버 블로그 발행

(`naver-blog-publish` v1 절차 inline)

### 4-1. NSPasteboard 재set (substack 발행 도중 클립보드 변경됐을 가능성)

```bash
~/.claude/skills/newsletter-publish/scripts/pb_set_html.sh /tmp/nl_body.html /tmp/nl_body.md
```

### 4-2. 글쓰기 페이지 + 임시저장 팝업 처리

```javascript
mcp__plugin_playwright_playwright__browser_tabs(action='new', url='https://blog.naver.com/GoBlogWrite.naver')
```

(4초 대기) → snapshot 으로 임시저장 팝업 (`작성 중인 글이 있습니다`) 확인. 떠있으면 강대종 결정 대기 (취소/확인). 없으면 진행.

### 4-3. 제목 set (SmartEditor 내부 API)

```javascript
() => {
  const title = '<NAVER_TITLE>';  // Substack title 그대로 또는 "바이브코딩 뉴스레터 Ep.<N> — <substack title>"
  const main = document.querySelector('iframe#mainFrame');
  const editor = main.contentWindow.SmartEditor._editors.blogpc001;
  editor._documentService.setDocumentTitle(title);
  return { match: editor._documentService.getDocumentTitle() === title };
}
```

**제목 형식 룰**: 기존 Ep1~3 처럼 "바이브코딩 뉴스레터 Ep.N — <substack title>" 형식. md 의 첫 h1 이 이미 이 형식이면 그대로, Substack 캐시본처럼 짧으면 prefix 추가.

### 4-4. 본문 placeholder 클릭 (Playwright real click)

snapshot 으로 placeholder paragraph (`글감과 함께 나의 일상을 기록해보세요!`) ref 캡처 → `browser_click` 으로 클릭.

### 4-5. OS-level Cmd+V

```bash
osascript <<'OSAEOF'
tell application "Google Chrome"
  activate
  set index of (first window whose title contains "강대종") to 1
end tell
delay 0.5
tell application "System Events"
  keystroke "v" using command down
end tell
delay 2
OSAEOF
```

### 4-6. 발행 모달

```javascript
// Step 1: 발행 버튼
() => doc.querySelector('[data-click-area="tpb.publish"]').click();
// (2초 대기 — 모달 open)
// Step 2: 모달 내 발행
() => doc.querySelector('[data-testid="seOnePublishBtn"]').click();
// (5~8초 대기 — redirect)
```

### 4-7. URL 캡처

`https://blog.naver.com/ssamssae/<postNo>` redirect 후 `location.href` 로 캡처.

## 5. 검증 (verifiable goal)

각 채널의 공개 URL fetch 로 OG title 매치:

```bash
# Substack
curl -s -A "Mozilla/5.0" "$SUBSTACK_URL" | grep -o 'og:title.*content="[^"]*"' | head -1

# Homepage (GitHub Pages 1~2분 지연 가능, 즉시 검증 안 되면 Skip 후 보고)
curl -s "https://ssamssae.github.io/daejong-page/newsletter.html" | grep -c "ep$N"

# Naver
curl -s -A "Mozilla/5.0" "$NAVER_URL" | grep -o 'og:title" content="[^"]*"' | head -1
```

3개 다 매치 → PASS. 일부만 매치 → 실패 채널 surface.

## 6. 텔레그램 보고

PASS 시 강대종 (chat_id=538806975) 에게 1통:

```
✅ 뉴스레터 Ep.<N> 통합 발행 PASS
• Substack: <substack_url>
• 홈페이지: https://ssamssae.github.io/daejong-page/newsletter.html (1~2분 후 반영)
• 네이버: <naver_url>
호스트: USERui-MacBookPro · HH:MM KST
```

부분 PASS / 실패 시 채널별 결과 + 1줄 사유 + 후속 단계 surface.

## 7. 페일 모드 (B+C)

- **2 (Substack) 실패** → 3 (홈페이지) skip + 4 (네이버) 진행 여부 강대종 결정 대기
- **2 OK, 3 (홈페이지) 실패** → 4 (네이버) 진행 + 홈페이지 수동 복구 surface
- **2/3 OK, 4 (네이버) 실패** → 다른 채널 그대로 두고 네이버만 다음 사이클 재시도 surface

각 채널 try/except 격리. abort 후에는 후속 채널 자동 진행 X (로그·텔레그램 surface 후 강대종 GO 결정 대기).

## 금지 / 주의 (hard rules)

- Mac 본진 한정. WSL/Mac mini 에서 호출 금지.
- 자동 로그인 자동화 X. 강대종 본인 세션만.
- 4조건 (네이버) 깨질 가능성 surface, override 는 강대종 명시 directive 필요.
- substack tiptap = Playwright synthetic paste OK. naver SmartEditor = OS-level keystroke 필수. 두 채널 paste 메커니즘 절대 섞지 말 것.
- substack 발행 → sync 사이 시간차 = GitHub Pages 빌드 (~1-2분). 즉시 검증 실패해도 abort 안 함.
- 본문 첨부 이미지 / 외부 CTA 블록은 v0 미지원. v1+ 후속.

## 미해결 / 후속

- 임시저장 팝업 자동 처리 (현재 surface 후 강대종 결정 대기)
- Substack 발행 모달 옵션 (Send to everyone vs Publish without buttons) 선택 정책
- 발행 실패 시 자동 재시도 룰
- 이미지·CTA 블록 자동화 (v1+)

## 검증 PASS 기록

(첫 PASS 시 채워질 자리)

## 트리거 → 동작 매핑

- `/newsletter-publish 4` → ep4 셋다
- `/newsletter-publish 4 --skip-substack` → 홈페이지 sync + 네이버만 (substack 이미 발행된 경우)
- "뉴스레터 발행 Ep.4" → 동일
- "Ep.4 셋다 올려" → 동일
- "Ep.4 다 올려줘" → 동일
