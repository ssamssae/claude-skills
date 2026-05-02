---
prevention_deferred: null
---

# Playwright MCP server cwd 가 `/` 일 때 `/.playwright-mcp` mkdir ENOENT

- **발생 일자:** 2026-05-02
- **해결 일자:** 2026-05-02
- **심각도:** medium (Playwright MCP 도구 호출 100% 실패 → Substack republish · Play Console 자동화 등 차단)
- **재발 가능성:** high (plugin update / cache 재생성 시 .mcp.json 원복되면서 재현)
- **영향 범위:** Track D Substack republish (Ep.1 / Ep.2 IMAGE N 노출 패치 사이클), `/create-play-app`, save-google-session, naver-blog-publish 등 Playwright MCP 의존 모든 흐름

## 증상

Mac 본진 세션에서 `mcp__plugin_playwright_playwright__browser_navigate` 호출 시:

```
Error: ENOENT: no such file or directory, mkdir '/.playwright-mcp'
```

Playwright MCP server (`npx @playwright/mcp@latest`) 가 cwd 상대 경로로 `.playwright-mcp` 디렉터리를 생성하려고 함. Claude Code CLI 가 cwd `/` 로 시작하면 root 쓰기 권한이 없어 mkdir 실패.

## 원인

- `npx @playwright/mcp@latest` 는 `--output-dir` 미지정 시 cwd 를 출력 베이스로 사용
- Claude Code 의 MCP server 프로세스 cwd 는 부모 (Claude CLI) 에서 상속
- Claude CLI 가 root 또는 권한 없는 디렉터리에서 시작되면 모든 MCP tool call 이 ENOENT 로 실패
- 본 세션은 환경 metadata 의 "Primary working directory: /" 로 시작됨 → 100% 재현

## 조치

`~/.claude/plugins/cache/claude-plugins-official/playwright/unknown/.mcp.json` 의 args 에 절대 경로 `--output-dir` 박음:

```json
// before
{ "playwright": { "command": "npx", "args": ["@playwright/mcp@latest"] } }

// after
{ "playwright": { "command": "npx",
  "args": ["@playwright/mcp@latest", "--output-dir", "/Users/user/.playwright-mcp"] } }
```

부수 작업
- `mkdir -p ~/.playwright-mcp` (1780+ 기존 artifact 가 이미 누적된 상태였음 = 과거 다른 cwd 환경에서는 동작했다는 증거)
- 백업 `~/.claude/plugins/cache/claude-plugins-official/playwright/unknown/.mcp.json.bak-2026-05-02`
- **본인 Claude 재시작 필수** (running MCP server 는 잘못된 cwd 로 떠있어 변경 미반영)

## 예방 (Forcing function 우선)

- **재발 트리거**: plugin update (`/plugin update playwright` 또는 `~/.claude/plugins/cache/...` 재생성 작업) → cache 위치 .mcp.json 이 upstream 으로 덮어써지면서 `--output-dir` 인자 사라짐
- 매 plugin update 후 본 issue 의 fix 를 1줄 재적용 필요
- 영구 fix 후보 (deferred):
  - `~/.claude/settings.json` 에 mcpServers override 가능하면 거기 박기 (Claude Code 문서 확인 필요)
  - claude-skills repo 에 plugin update 후 자동 재패치 hook 박기
  - upstream `@playwright/mcp` 에 cwd-fallback 패치 PR 보내기 (`/.playwright-mcp` mkdir 실패 시 `~/.playwright-mcp` fallback)
- 본 issue 를 INDEX.md 에 등록하면 재발 시 `grep playwright-mcp-cwd ~/.claude/skills/issues/INDEX.md` 로 바로 연결

## 관련 메모리 / 히스토리

- 2026-04-16 [playwright-chrome-google-login-blocked](2026-04-16-playwright-chrome-google-login-blocked.md) — Playwright 자체 환경 fix 의 다른 결
- 본 fix 는 Track D 하이브리드 사이클 (PR ssamssae/daejong-page#18) 의 4단계 Substack republish 잠금 해제용
