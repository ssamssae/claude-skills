---
name: issue
description: 이슈/사건/버그/혼선이 생겼다가 해결된 상황을 구조적으로 기록한다. `~/.claude/skills/issues/YYYY-MM-DD-<slug>.md` 에 마크다운으로 저장하고 ssamssae/claude-skills repo 에 자동 commit+push. WSL / Mac 어디서 호출해도 동일 포맷으로 쌓여서 기기 간 공유된다. 사용자가 "/issue", "이 이슈 기록해줘", "이거 포스트모템", "이슈로그", "트러블슈팅 기록" 이라고 하면 이 스킬을 실행한다.
---

# /issue — 이슈 포스트모템 기록

## 목적

문제가 생겼다가 해결됐을 때, **증상/원인/조치/예방** 네 칸을 간결하게 남긴다. 기기에 관계없이 같은 형식으로 누적되어 나중에 검색/참고/재발방지의 근거가 된다.

- 저장 위치: `~/.claude/skills/issues/YYYY-MM-DD-<slug>.md`
- 동기화: `ssamssae/claude-skills` repo 를 통한 git push/pull. 양쪽 기기가 자동으로 같은 디렉터리 공유.
- 폰에서 보기: GitHub 모바일 앱에서 `ssamssae/claude-skills/issues/` 경로로 접근.

## 호출 방식

```
/issue
/issue <slug-or-free-text>
/issue $ARGUMENTS
```

- **인자 없음**: 세션 맥락에서 내가 제목/증상/원인/조치 초안 작성 → 강대종님 컨펌 → 파일화
- **인자 있음**: 그 문구를 **제목 겸 slug 힌트** 로 사용. 나머지는 맥락에서 추출해서 초안 작성 → 컨펌 → 파일화

## 파일 네이밍

```
YYYY-MM-DD-<slug>.md
```

- 날짜: KST 기준 오늘
- slug: 소문자-케밥-케이스, 20자 이내. 예: `telegram-client-delivery-lag`, `mac-ssh-claude-keychain`
- 같은 날 같은 slug 중복이면 `-v2`, `-v3` 숫자 suffix

## 템플릿 (`templates/issue.md` 를 복사해서 쓰되, 아래 구조 유지)

```md
# <제목 한 줄>

- **발생 일자:** YYYY-MM-DD HH:MM KST
- **해결 일자:** YYYY-MM-DD HH:MM KST
- **심각도:** low / medium / high
- **재발 가능성:** low / medium / high
- **영향 범위:** 어떤 기기/스킬/워크플로우

## 증상
사용자가 직접 본 현상. 1~3줄.

## 원인
진짜 근본 원인. 추측이면 "추정" 표기.

## 조치
이번에 뭐 했는지. 코드/커밋/설정 변경 레벨까지.

## 예방 (Forcing function 우선)
같은 상황이 또 오면 어떻게 막거나 자동으로 감지할지. 가능하면 코드/스킬/훅 레벨의 자동화. 사람 의지에만 의존하는 항목은 지양.

## 관련 링크
- 커밋: <sha or url>
- 메모리: `memory/xxx.md`
- PR: <url>
- 텔레그램 메시지: id <N> (회고용)
```

## 절차 (/issue 호출 시)

1. 날짜/시간 KST 로 픽스.
2. slug 결정 (인자 → kebab-case 변환; 없으면 세션 맥락에서 추출 + 사용자에게 제안).
3. 위 템플릿 복사해서 각 칸 채우기. 모르는 칸은 `(채울 것)` 으로 명시적 공란.
4. 초안 완성하면 **강대종님에게 텔레그램으로 본문 그대로 전송** 후 OK/수정 지시 대기.
5. OK 받으면:
   - `~/.claude/skills/issues/<파일>` 작성
   - `~/.claude/skills/issues/INDEX.md` 맨 위에 한 줄 entry 추가
   - skills repo 에서 `git add issues/ && git commit -m "issue: <제목>" && git pull --rebase && git push`
6. 푸시 URL (예: `https://github.com/ssamssae/claude-skills/blob/main/issues/<파일>`) 을 텔레그램으로 최종 보고.

## 금지

- **임의로 파일 쓰고 커밋 금지.** 반드시 강대종님 컨펌 후에만 commit.
- feedback_* 메모리로 이미 저장된 패턴을 중복 생성하지 말 것. 있으면 issue 에서 해당 메모리 링크만 걸고 넘어가.
- 이슈 내용을 외부(blog, public site)로 자동 발행 금지 — 이 repo 는 private.

## 메모리 연계

- **재발 가능성 high + forcing function 있는 이슈** 는 `feedback_*.md` 메모리로도 동시 저장 권장. (쌓이는 이슈 파일은 아카이브용, 메모리는 매 세션 로드용.)
- 이미 있는 memory 파일은 issue 의 "관련 링크" 섹션에서 인용.

## 예시 (오늘)

- `2026-04-20-telegram-client-delivery-lag.md` — 텔레그램 답이 안 오는 줄 알았는데 클라이언트가 pull 을 못 해서 뒤늦게 받은 건
- `2026-04-20-terminal-only-reply-missed-telegram.md` — 답변을 터미널에만 찍고 reply 툴로 안 보낸 실수

## 다른 기기에서 보기

- Mac: `cat ~/.claude/skills/issues/2026-04-20-*.md`
- 폰: GitHub 앱 → `ssamssae/claude-skills` → `issues/` 디렉터리
- WSL: 이 파일 편집 후 재푸시
