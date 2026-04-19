---
name: merge-janitor
description: WSL night-runner 가 janitor 브랜치로 만든 PR 을 머지하거나 닫는다. morning-briefing 1-E 섹션에서 보여준 PR 에 대해 사용자가 "PR #3 머지", "PR #5 닫아", "/merge-janitor 3", "janitor PR 3번 merge" 같은 자연어·명시 호출로 실행. gh CLI 기반, 크로스 repo 자동 탐색.
allowed-tools: Bash, Read
---

# /merge-janitor — 야간 러너 PR 머지/닫기

WSL `/night-runner` 가 밤사이 janitor/YYYY-MM-DD 브랜치로 밀어 올린 PR 을 맥 본진에서 머지·닫는다. morning-briefing 이 매일 07:15 에 해당 PR 목록을 텔레그램으로 보여주고, 사용자는 "PR #N 머지" 또는 "PR #N 닫아" 라고 답장해 이 스킬을 실행시킨다.

## 호출 패턴

전부 이 스킬을 호출해야 함:
- `/merge-janitor 3` — PR #3 을 머지 (default: `--merge`, 히스토리 보존)
- `/merge-janitor 3 squash` — PR #3 을 squash 머지
- `/merge-janitor 3 --squash` — 동일
- `/merge-janitor 3 close` — PR #3 을 닫기
- `/merge-janitor 3 --close` — 동일
- 자연어 (repo 별칭 포함, morning-briefing 1-E 섹션의 답장 포맷):
  - "더치페이 #1 머지" · "메모요 #1 닫아" · "약묵자 #3 squash 머지" · "밥먹자 #2 머지해"
  - 별칭 없는 형태도 여전히 지원: "PR #3 머지", "PR 5번 머지해", "PR #7 닫아", "janitor PR 3 merge"

### repo 별칭 테이블

morning-briefing 과 동일한 테이블 유지 (양쪽 스킬이 같은 별칭을 써야 매칭 성공):

| 별칭 | repo nameWithOwner |
|---|---|
| `더치페이` | `ssamssae/dutch_pay_calculator` |
| `메모요` | `ssamssae/simple-memo-app` |
| `약묵자` | `ssamssae/yakmukja` |
| `밥먹자` | `ssamssae/babmeokja` |
| `daejong-page` | `ssamssae/daejong-page` |
| (그 외) | repo 이름의 `/` 뒤 부분 그대로 |

파이썬 딕셔너리로 내장:
```python
ALIASES = {
    '더치페이': 'ssamssae/dutch_pay_calculator',
    '메모요': 'ssamssae/simple-memo-app',
    '약묵자': 'ssamssae/yakmukja',
    '밥먹자': 'ssamssae/babmeokja',
    'daejong-page': 'ssamssae/daejong-page',
}
```

### 파싱 규칙

`$ARGUMENTS` (또는 사용자 자연어) 에서:
- 별칭 토큰이 하나 포함되면 해당 repo 로 필터링 (1단계 검색 결과에서 `repository.nameWithOwner == ALIASES[별칭]` 인 것만)
- 별칭이 없으면 모든 janitor PR 중 번호 일치로 찾음 (기존 동작)
- 숫자: `#` 뒤 숫자, 또는 `N번` 패턴, 또는 단순 정수 토큰 → PR 번호
- "close"·"닫아"·"--close" → **닫기 모드**
- "squash"·"--squash" → **머지 모드 (strategy=squash)**
- 그 외 기본 → **머지 모드 (strategy=merge)**

여러 repo 에 같은 번호 PR 이 있을 때: 별칭 없이 호출되면 repo 목록을 제시하고 되묻기. 별칭이 있으면 바로 진행.

## 실행 절차

### 1. PR 식별 (크로스 repo 탐색)

`gh search prs` 는 `additions/deletions/files` 필드 미지원. 2단계로 분리한다.

**1-a. 목록 조회 (search)**:
```bash
gh search prs author:@me is:open is:pr janitor \
  --json number,url,repository,title \
  --limit 20
```

결과에서 `number == N` 이고 `title` 이 `[janitor]` 로 시작하는 PR 필터링.

**호출에 repo 별칭이 포함됐으면** 1차 필터에 `repository.nameWithOwner == ALIASES[별칭]` 조건 추가.

- **0개**: "해당 번호의 open janitor PR 이 없습니다. 이미 머지·닫혔거나 번호 오타" 리포트 후 종료 (별칭이 잘못된 경우도 여기 포함, 에러 메시지에 "별칭 '<X>' 에 해당하는 repo 에 PR #N 없음" 으로 힌트)
- **1개**: 1-b 로 진행
- **2개 이상 (다른 repo 에 같은 PR 번호)**: 각 repo 이름과 URL 을 보여주고 "어느 repo 인지, 또는 별칭으로 다시 불러주세요" 물어보고 대기. 별칭이 이미 주어졌다면 이 분기는 발생 안 함.

**1-b. 상세 조회 (pr view)**: 1-a 의 URL 로 diff 메타 확보
```bash
gh pr view <URL> --json additions,deletions,files,body
```

여기서 `additions`, `deletions`, `files[]` 로 3번 안전 체크 수행.

### 2. 닫기 모드

```bash
gh pr close <URL> --delete-branch --comment "janitor 자동 생성 PR 닫기 (merge-janitor 스킬)"
```

성공 시 리포트:
```
🗑 janitor PR 닫힘
  repo: owner/name
  PR #N: 제목
  브랜치 삭제됨: janitor/YYYY-MM-DD
```

종료.

### 3. 머지 모드 — 안전 체크

PR 메타데이터에서 판정:

- **대형 변경 경고**: `additions + deletions > 300`
- **의존성 변경 경고**: 파일 목록에 `pubspec.yaml`, `Podfile`, `Gemfile`, `package.json`, `pyproject.toml`, `Cargo.toml` 포함
- **민감 파일 경고**: 파일 경로/이름에 `.env`, `key`, `token`, `secret`, `credential`, `.pem`, `.p12`, `.keystore` 포함
- **CI/설정 위험 경고**: `.github/workflows/`, `.launchd/`, `fastlane/`, `Fastfile`, `android/key.properties` 변경

### 4. 경고 분기

**경고 0건**: 곧바로 5번으로 머지 실행.

**경고 1건 이상**: 사용자에게 경고 목록을 표시하고 명시 확인 요구:
```
⚠️ 머지 전 확인 필요
  repo: owner/name
  PR #N: 제목
  +X/-Y lines (F files)
  경고:
    • [대형 변경] +320 lines
    • [의존성 변경] pubspec.yaml 수정
  계속 머지하려면 "예" 또는 "강제 머지" 로 답장해주세요.
```

사용자가 긍정(예/응/진행/강제 머지/go) 답장 → 5번. 부정(아니/취소/stop/no) → 종료.

### 5. 머지 실행

**기본 전략: `--merge` (히스토리 보존).**
이유: janitor 커밋은 conventional commits (docs:/chore:/test:/fix:) 규칙으로 atomic 하게 쪼개져 있어 보존 가치가 있고, 개인 repo 의 git log 는 그 자체가 기억 보조장치. squash 하면 bisect/blame 해상도가 떨어짐.

`$ARGUMENTS` 에 `squash`/`--squash` 가 있을 때만 squash 전략 사용.

```bash
# default (merge)
gh pr merge <URL> --merge --delete-branch

# squash 명시 시
gh pr merge <URL> --squash --delete-branch
```

옵션:
- `--merge` (default): 정규 merge commit + 각 janitor 커밋이 main 에 그대로 반영됨
- `--squash` (명시 요청 시): janitor 커밋 여러 개를 하나로 합침. 나중에 WIP 반복 커밋 패턴 생기면 default 로 전환 고려.
- `--delete-branch`: 머지 성공 시 원격 브랜치 자동 삭제
- `--auto` 는 기본 사용 안 함 (required check 없는 개인 repo 가 대부분이라 불필요. check 가 걸려 있으면 사용자에게 먼저 확인.)

### 6. 최종 리포트 (텔레그램 세션이면 reply 도구로 전송)

성공:
```
✅ 머지 완료
  repo: owner/name
  PR #N: 제목
  +X/-Y lines (F files)
  merge SHA: abc1234
  janitor/YYYY-MM-DD 브랜치 삭제됨
```

실패 (check 미통과, conflict 등):
```
❌ 머지 실패
  사유: <gh 에러 한 줄>
  PR URL: <URL>
  수동 확인 필요
```

## 원칙

- **main 직접 푸시 금지** — PR 을 통해서만 merge
- **--force / --force-with-lease 금지**
- **--no-verify 같은 hook bypass 금지**
- **여러 PR 동시 머지 요청 불가** — 한 번에 한 PR
- 안전 체크 경고 상태에서 사용자 확인 없이 머지하지 말 것
- 비-janitor PR (제목이 `[janitor]` 안 시작하는 것) 은 이 스킬로 다루지 않는다. 실수 방지.

## 기기 제약

- 맥 본진에서만 실행. WSL·iPhone 에서는 gh auth 와 repo clone 상태가 달라 오동작 가능.
- `hostname` 체크해서 `.local` (맥) 이 아니면 "맥 본진에서 실행해주세요" 안내 후 종료.
