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
- 인덱스: `issues/INDEX.md` — **자동 생성, 수동 편집 금지.** 매 /issue 저장 시 스킬이 전체 덮어쓰기로 재생성.

## 호출 방식

```
/issue
/issue <slug-or-free-text>
/issue $ARGUMENTS
/issue list [--recent N] [--tag X]   # 목록/검색 (쓰기 없음)
```

- **인자 없음**: 세션 맥락에서 내가 제목/증상/원인/조치 초안 작성 → 강대종님 컨펌 → 파일화
- **인자 있음**: 그 문구를 **제목 겸 slug 힌트** 로 사용. 나머지는 맥락에서 추출해서 초안 작성 → 컨펌 → 파일화
- **`list` 서브커맨드**: issues/ 디렉터리 스캔해 목록 출력 (새 파일 생성 안 함)

## 파일 네이밍

```
YYYY-MM-DD-<slug>.md
```

- 날짜: KST 기준 오늘
- slug: 소문자-케밥-케이스, 20자 이내. 예: `telegram-client-delivery-lag`, `mac-ssh-claude-keychain`
- 같은 날 같은 slug 중복이면 `-v2`, `-v3` 숫자 suffix

## 템플릿

`templates/issue.md` 복사해서 쓰되, 아래 구조 유지:

```md
---
prevention_deferred: null   # "YYYY-MM-DD" 를 넣으면 그 날짜까지 예방 미작성 허용. 기본 null.
---

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

## 재발 이력
<처음 생성 시 비워둠. 재발 발생 시 "- YYYY-MM-DD: 상황 한 줄" 로 한 줄 추가>

## 관련 링크
- 커밋: <sha or url>
- 메모리: `memory/xxx.md`
- PR: <url>
- 텔레그램 메시지: id <N>
```

## 절차 (/issue 호출 시)

### 1. 초안 단계

1. 날짜/시간 KST 로 픽스.
2. slug 결정 (인자 → kebab-case 변환; 없으면 세션 맥락에서 추출 + 사용자에게 제안).
3. 템플릿 복사해서 각 칸 채우기. 모르는 칸은 `(채울 것)` 으로 명시적 공란.

### 2. **재발 감지** (✨ 개선 2)

4. `issues/` 의 기존 `YYYY-MM-DD-*.md` 전체를 훑어 "증상" 섹션 본문을 추출.
5. 새 이슈의 "증상" 본문과 기존 증상들을 비교:
   - (a) 토큰(공백 분리, 3글자 이상) 겹침 수 ≥ 3, **또는**
   - (b) 짧은 문자열 편집거리 비율 ≥ 0.5 (정확도보다 recall 우선 — 후보 많이 뽑고 사람이 판단)
6. 매칭되는 이슈가 있으면 강대종님에게 텔레그램으로 물음:
   ```
   기존 이슈 <파일명> 과 비슷해 보입니다:
   <기존 제목>
   증상 요약: <1줄>

   [재발] 기존 파일 "재발 이력" 섹션에 추가
   [신규] 새 파일 생성 (주제가 달라 별건)
   ```
7. **[재발]** 선택 시:
   - 신규 파일 만들지 **말 것**.
   - 기존 파일의 `## 재발 이력` 섹션에 `- YYYY-MM-DD: <짧은 상황>` 한 줄 추가.
   - 기존 파일의 "예방" 섹션에 재발한 걸 근거로 **더 강한 forcing function** 이 있는지 사용자에게 제안: "이전 예방이 통하지 않았습니다. 이번 재발을 막을 더 센 forcing function 이 있나요?"
   - 사용자 답 받으면 "예방" 섹션 업데이트.
8. **[신규]** 선택 시 정상 새 파일 경로 진행.

### 3. **예방(Prevention) 강제 검증** (✨ 개선 1 — 최우선)

9. 초안의 "예방" 섹션을 검사. 아래 중 하나면 **저장 거절**:
   - 섹션 비어있음
   - 본문에 `TBD`, `미정`, `TODO`, `나중에`, `생각 중`, `생각중`, `검토 필요` 중 하나만 있음
   - 섹션이 `(채울 것)` 만 포함
10. 거절 시 사용자에게 강하게 요청:
    ```
    예방 한 줄이 없으면 이슈가 아닙니다 — 같은 일이 안 일어나게 하는
    forcing function 을 한 줄이라도 적어주세요.
    (강제 우회는 "나중에 채울게 — 2026-XX-XX 까지" 하고 명시적 날짜
     주시면 frontmatter 에 prevention_deferred 로 박아둡니다.)
    ```
11. 사용자가 예방 한 줄 주면 재검증 후 통과.
12. 사용자가 "deferred <YYYY-MM-DD>" 를 명시적으로 요구하면:
    - frontmatter `prevention_deferred: YYYY-MM-DD` 설정
    - "예방" 섹션에 `(deferred — 작성 마감 YYYY-MM-DD)` 로 표기
    - 통과
    - `/morning-briefing` 이나 리마인더에서 "예방 작성 미결 이슈" 섹션으로 별도 추적 대상.

### 4. 최종 컨펌 + 저장

13. 모든 검증 통과한 초안을 **강대종님에게 텔레그램으로 본문 그대로 전송** 후 OK/수정 지시 대기.
14. OK 받으면:
    a. `~/.claude/skills/issues/<파일>` 작성
    b. **INDEX.md 재생성** (✨ 개선 3):
       ```
       python3 ~/.claude/skills/issue/tools/regen_index.py
       ```
       → issues/ 디렉터리 스캔 후 INDEX.md 전체 덮어쓰기. 수동 편집 금지 상단 주석 포함.
    c. skills repo 에서 commit+push:
       ```
       cd ~/.claude/skills
       git pull --rebase origin main
       git add issues/
       git commit -m "issue: <제목 한 줄>"
       git push origin HEAD
       ```
    d. **daejong-page 공개본 동기화** (2026-04-20 추가 — 맥/데스크탑 공통):
       ```
       cp ~/.claude/skills/issues/<파일> ~/daejong-page/issues/
       # ~/daejong-page/issues/index.json 의 entries 배열에 해당 파일
       # entry 를 추가 또는 갱신. 필드:
       #   file, date, slug, title, severity, recurrence, scope,
       #   occurred_at, resolved_at, updated(ISO KST)
       # 같은 file 있으면 갱신(중복 추가 금지), 없으면 최상단 삽입.
       cd ~/daejong-page
       git pull --rebase origin main
       git add issues/<파일> issues/index.json
       git commit -m "issue: <제목 한 줄> 공개본 동기화"
       git push origin main
       ```
       - 본문에 민감 정보(개인키·토큰·내부 호스트명·사적 이름 등) 가 있으면 공개본에서는 해당 라인을 `(비공개)` 로 마스킹해서 복사. 원본(claude-skills) 은 그대로 유지.
       - daejong-page 동기화 실패는 **소프트 페일** — claude-skills push 는 이미 됐으므로 경고만 남기고 계속 진행.
15. 푸시 URL 두 개 텔레그램 최종 보고:
    - 내부: `https://github.com/ssamssae/claude-skills/blob/main/issues/<파일>`
    - 공개: `https://ssamssae.github.io/daejong-page/issues.html`

## 금지

- **임의로 파일 쓰고 커밋 금지.** 반드시 강대종님 컨펌 후에만 commit.
- feedback_* 메모리로 이미 저장된 패턴을 중복 생성하지 말 것. 있으면 issue 에서 해당 메모리 링크만 걸고 넘어가.
- **예방 섹션 비어있는데 `prevention_deferred` 플래그 없이 저장 절대 금지.**
- **INDEX.md 수동 편집 금지.** 반드시 regen 스크립트 통해서만 갱신.
- 이슈 내용을 외부(blog, public site)로 자동 발행 금지 — claude-skills repo 는 private. daejong-page 공개본 동기화는 14-d 경로로만(민감정보 마스킹 필수).

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
