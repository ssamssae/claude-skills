---
name: 네이버 블로그 자동 발행 (본진 한정)
description: 마크다운 파일을 네이버 블로그(SmartEditor ONE)에 자동 발행. Mac 본진 Playwright MCP 내장 Chromium + 강대종 본인 자동로그인 세션 활용. 기본 전체공개(all). 트리거 "/naver-publish <md_path>", "네이버에 올려", "/naver-publish".
---

# 네이버 블로그 자동 발행 v1

마크다운 1개를 강대종 본인 네이버 블로그(`ssamssae`)에 자동 발행한다. 본진 Mac 한정. 사람 빈도(1일 1~2건) + 본인 계정 + 기본 전체공개. 4조건 중 하나라도 깨지는 요청이 오면 NO GO 회귀.

## 0. 사전 가드 (skip 금지)

1. `hostname` 출력이 `USERui-MacBookPro*` 가 맞는지 확인. 아니면 즉시 중단 (`Mac mini` / WSL 에서 호출 금지).
2. 메모리 `project_naver_blog_auto_publish_dropped.md` + `feedback_no_login_automation_for_terminated_apis.md` 4조건 떠올리기:
   - 본인 계정 + 본인 블로그
   - 본인 자동로그인 세션 (자동 로그인 자동화 X)
   - 1일 1~2건 (대량 X)
   - 기본 공개설정 = 전체공개 (all). **2026-05-01 강대종 directive 로 closed → all 변경.** Substack/GitHub Pages/daejong-page 와 일관성 + verifiable goal 의 공개 URL fetch 모순 해소.
3. 입력 인자 파싱:
   - `--md <path>` (필수)
   - `--title <text>` (옵션, 없으면 md 의 첫 `# h1` 줄 사용. 둘 다 없으면 파일명 stem)
   - `--category <name>` (옵션)
   - `--open all|closed|neighbor` (옵션, **기본 `all`**)

## 1. 마크다운 → HTML

```bash
python3 ~/.claude/skills/naver-blog-publish/scripts/md_to_html.py "$MD" > /tmp/naver_body.html
cp "$MD" /tmp/naver_body.md
```

표(table) 가 들어가는 글이면 Substack 패턴(`reference_substack_publish_pipeline.md`)의 표→리스트 변환 함수를 먼저 적용한 뒤 HTML 변환. **nl2br extension 절대 쓰지 말 것.**

## 2. Playwright MCP 세션 점검

`mcp__plugin_playwright_playwright__browser_tabs(action=list)` 로 탭 목록 조회.

```javascript
() => {
  return { url: location.href, hasNickname: !!document.querySelector('.MyView-module__profile_box___QKPGA, [class*="profile_box"]') };
}
```

`https://www.naver.com` 탭에서 `MyView-module__profile_box` 등으로 닉네임이 나타나면 로그인 OK. 안 나오면 텔레그램으로 강대종에게 "1회 네이버 로그인 부탁" 한 통 + 작업 중단.

## 3. 글쓰기 페이지 진입

새 탭에서:
```
https://blog.naver.com/GoBlogWrite.naver
```

→ 자동 redirect: `https://blog.naver.com/ssamssae?Redirect=Write&categoryNo=<n>`

페이지 안에 `iframe#mainFrame` 이 있고, 같은 origin(`blog.naver.com`)이라 `contentDocument` 직접 접근 가능.

3초 대기 후 임시저장 팝업 점검:
```javascript
() => {
  const doc = document.querySelector('iframe#mainFrame').contentDocument;
  const layers = Array.from(doc.querySelectorAll('[class*="layer_popup"], [class*="modal"]'))
    .filter(p => p.offsetParent !== null);
  return layers.map(p => ({ cls: p.className, text: (p.innerText || '').slice(0, 200) }));
}
```

임시저장 팝업이 떠있으면 (예: "이전에 작성하던 글이 있어요"), `취소` / `새로 쓰기` 버튼을 evaluate 로 찾아 클릭. 패턴은 발견 시 surface 후 강대종 결정 대기 (자동 우회 X).

## 4. 제목 입력 — SmartEditor 내부 API 호출 (검증됨 2026-05-01)

SmartEditor ONE 은 표준 paste/click 이벤트로 title 셀에 글자를 넣는 게 안 통한다(가상 contenteditable 사용). 내부 store 에 박힌 `_documentService.setDocumentTitle(text)` 가 정공법:

```javascript
(title) => {
  const main = document.querySelector('iframe#mainFrame');
  const editor = main.contentWindow.SmartEditor._editors.blogpc001;
  editor._documentService.setDocumentTitle(title);
  return { current: editor._documentService.getDocumentTitle() };
}
```

이 한 호출로 (a) 내부 model 갱신 (b) DOM `.se-section-documentTitle` 의 `span.__se-node.textContent` 채워짐 (c) `se-is-empty` class 제거. 검증 = `getDocumentTitle()` 반환값이 입력값과 동일.

**editor key**: `_editors.blogpc001` 가 v1 시점 발견된 키. 다른 키이면 `Object.keys(SmartEditor._editors)[0]` 로 찾아.

(deprecated: span.textContent 직접 설정 + InputEvent dispatch — SmartEditor 가 내부 model 안 업데이트해서 발행 시 빈 제목으로 가는 사고가 있었다. 위 API 호출로 대체. v1 검증 시점)

```javascript
(title) => {
  const doc = document.querySelector('iframe#mainFrame').contentDocument;
  const titleSect = doc.querySelector('.se-section-documentTitle');
  const node = titleSect.querySelector('span.__se-node');
  const ph = titleSect.querySelector('.se-placeholder');
  // Focus container
  const editable = titleSect.closest('[contenteditable]') || titleSect.querySelector('[contenteditable]');
  if (editable) editable.focus();
  // Set text
  node.textContent = title;
  if (ph) ph.style.display = 'none';
  // Notify
  const ev = new InputEvent('input', { bubbles: true, cancelable: true });
  (editable || node).dispatchEvent(ev);
  return { ok: true, currentTitle: node.textContent };
}
```

검증: `node.textContent === title` 인지 evaluate 로 재확인.

직접 텍스트 set 이 SmartEditor 의 내부 모델과 어긋나서 발행 시 빈 제목으로 가는 경우, 폴백:
- `mcp__plugin_playwright_playwright__browser_click` 으로 title section 클릭 → focus
- `mcp__plugin_playwright_playwright__browser_type` 으로 직접 타이핑

(이 폴백 패턴은 v1 풀그린 검증 시 한 번 확인하고 SKILL.md 에 결과 기록)

## 5. 본문 입력 (NSPasteboard + Mac 시스템 keystroke)

본문 컴포넌트: `iframe#mainFrame` 안의 `.se-component.se-text` → `.se-section.se-section-text` → `.se-module.se-module-text`.

**중요한 사실 (v1 검증 시점 발견):** Playwright `browser_press_key('ControlOrMeta+v')` 는 SmartEditor 의 paste handler 를 트리거하지 못한다 (CDP synthetic event 가 SmartEditor 의 가상 입력 시스템을 우회). OS-level 실제 키스트로크(`osascript ... keystroke "v" using command down`) 만 SmartEditor 에 전달된다. 단, 이 경로는 **Mac frontmost = Playwright Chromium** 이어야 작동.

### 5-1. NSPasteboard 에 HTML+plain 동시 set
```bash
~/.claude/skills/naver-blog-publish/scripts/pb_set_html.sh /tmp/naver_body.html /tmp/naver_body.md
```

### 5-2. 본문 영역 focus + 셀렉션 set

evaluate 로 본문 컴포넌트 마지막 paragraph 에 caret 위치:
```javascript
() => {
  const main = document.querySelector('iframe#mainFrame');
  const doc = main.contentDocument;
  const bodyComps = Array.from(doc.querySelectorAll('.se-component.se-text'));
  const target = bodyComps[bodyComps.length - 1];
  const para = target.querySelector('.se-text-paragraph');
  para.scrollIntoView({ block: 'center' });
  main.contentWindow.focus();
  para.click();
  const range = doc.createRange();
  range.selectNodeContents(para);
  range.collapse(false);
  const sel = doc.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
  return { ok: true };
}
```

### 5-3. OS-level Cmd+V

```bash
osascript -e 'tell application "Google Chrome" to activate'
osascript -e 'tell application "System Events" to keystroke "v" using command down'
```

SmartEditor 가 OS-level paste 를 받아 자체 구조로 변환 (heading / list / blockquote / code / link 모두 검증됨 — h1 → fs24 bold, h2 → fs19 bold, ul → se-text-list, blockquote → 따옴표 인용 컴포넌트). 이후 1~2초 대기.

**주의:** osascript activate 가 강대종님 Mac 포커스를 빼앗는다. 새 자동 발행 사이클마다 한 번씩만. 강대종님이 다른 작업 중일 때는 사전 양해 필요.

### 5-4. 검증
```javascript
() => {
  const doc = document.querySelector('iframe#mainFrame').contentDocument;
  const body = doc.querySelector('.se-content');
  return { textHead: (body?.innerText || '').slice(0, 200) };
}
```
md 의 첫 30자가 들어가있어야 OK. 안 들어갔으면 폴백:
- `browser_click` 으로 본문 영역 클릭 → `browser_press_key("ControlOrMeta+a")` → `Delete` → 다시 `ControlOrMeta+v`

## 6. 발행 모달

> **harness 권한:** v1 검증 시 `_documentService.setDocumentTitle()` 호출 후 발행 버튼 evaluate-click 이 harness 에 의해 거부되었다(외부 시스템 쓰기 + 공개설정 modal-radio 가 아직 검증 안 됨). 정상적인 안전 가드. 강대종님이 .claude/settings.json 에 permission rule 추가하거나, 첫 1회는 강대종님이 직접 모달까지 수동 클릭해 selector 확정 후 SKILL.md update.

### 6-1. 발행 버튼 클릭

iframe 안의 `[data-click-area="tpb.publish"]` 버튼 (또는 `.publish_btn__*`). evaluate:
```javascript
() => {
  const doc = document.querySelector('iframe#mainFrame').contentDocument;
  const btn = doc.querySelector('[data-click-area="tpb.publish"]');
  btn.click();
  return { clicked: !!btn };
}
```

### 6-2. 공개설정 (기본 all = 전체공개)

발행 모달이 뜨면 카테고리/태그/공개설정 옵션 노출. **기본은 `전체공개`** 라디오 — 인자 `--open` 미지정 시 그대로 둠 (네이버 모달의 default 가 전체공개).

`--open closed` (비공개) 또는 `--open neighbor` (이웃공개) 명시된 경우만 라디오 변경. 모달 selector 는 첫 1회 풀그린 시 inspect 후 update.
- `--open all` 일 땐 클릭 자체를 생략 (default 그대로).
- `--open closed`: 비공개 라디오 → `Array.from(doc.querySelectorAll('label, input[type=radio]')).find(l => /비공개/.test(l.innerText || l.value))`
- `--open neighbor`: 이웃공개 라디오 → 위 패턴에 `/이웃공개/`

### 6-3. 카테고리 (옵션)

`--category` 인자 들어왔으면 모달의 카테고리 select / dropdown 에서 매칭. 없으면 default 둠.

### 6-4. 최종 발행

모달 안의 `발행` 버튼 (모달 안에 별도 발행 버튼 있음, top-bar 발행과 다름) 클릭 → redirect 대기.

## 7. 결과 URL 캡쳐

발행 후 redirect 되는 URL 또는 `https://blog.naver.com/ssamssae/<postNo>` 패턴 capture.

```javascript
() => {
  return { url: location.href, mainFrameUrl: document.querySelector('iframe#mainFrame')?.src };
}
```

postNo 는 mainFrame URL 에 `logNo=` 또는 redirect URL path 로 노출.

## 8. 검증 (verifiable goal)

기본 `--open all` 이면 인증 없이 공개 URL fetch 가능 — directive 그대로:

1. `https://blog.naver.com/ssamssae/<postNo>` curl/WebFetch (인증 X)
2. article DOM 의 제목/본문 첫 30자 파싱 + 매치 검사
3. 제목 정확 일치 + 본문 첫 30자 일치 → **PASS**

`--open closed` 명시된 경우만 fetch 가 막히므로 Playwright 같은 세션 안에서 진입해 DOM 매치로 검증.

## 9. 텔레그램 보고

PASS 시 강대종 (chat_id=538806975) 에게 1통:

```
✅ 네이버 블로그 자동 발행 v1 PASS
발행 URL: <url>
호출: /naver-publish <md_path>
공개설정: all (전체공개)
호스트: USERui-MacBookPro · HH:MM KST
```

차단/실패 시 1줄 사유 + 다음 단계 후보 surface 없이 대기.

## 금지/주의 (hard rules)

- Playwright **시스템 Chrome `--remote-debugging-port` attach 금지** (Chrome 136+ default user-data-dir 거부). MCP 내장 Chromium 만 사용.
- 자동 로그인 자동화 금지. 강대종 본인 자동로그인 세션을 그대로 활용.
- 4조건 (본인계정/본인세션/사람빈도/`기본 전체공개 all`) 중 1개라도 깨지는 요청이 오면 즉시 NO GO 회귀. 2026-05-01 강대종 directive 로 #4 = closed → all 변경.
- 캡차/2FA 발견 시 우회 시도 X. 강대종 결정 대기.
- 첫 풀그린 검증 글은 강대종이 보고 받은 직후 공개/비공개/삭제 결정.
- 다른 탭(ASC, etc.) 건드리지 말 것 — 새 탭 1개에서만 작업.

## 미해결 / 후속 (v1 검증 시 update)

- 임시저장 팝업 정확한 selector
- 발행 모달 공개설정 라디오 정확한 selector
- 카테고리 dropdown 패턴
- 표/이미지 첨부 패턴 (본문 paste 만 검증, 이미지·파일 첨부는 v2)
