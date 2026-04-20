---
name: worklog
description: 하루 전체 작업 내용(현재 세션 + 그날의 모든 Claude Code 세션 로그 + 모든 프로젝트의 git 커밋)을 수집·요약해서 작업일지로 저장하고 GitHub·홈페이지에 반영한다. 마크다운 원본(worklog-source/)과 산문체 공개본(worklog/) 을 동시에 생성해 push 한다. 사용자가 "작업일지", "일지", "일지 써줘", "오늘 일지", "일지 기록", "/worklog" 등을 말하면 이 스킬 호출.
allowed-tools: Bash, Write, Edit, Read, Glob, Grep
---

# 작업일지 작성 & 깃허브 푸시

**지정 날짜에 수행한 모든 작업**(현재 프로젝트 + 다른 프로젝트 + 다른 Claude Code 세션)을 수집해 작업일지를 작성하고 GitHub·홈페이지에 올립니다. 단일 프로젝트만 기록하던 과거 동작과 다르게, 그날 하루 전체 궤적을 한 문서에 합칩니다.

## 출력 파일 2종 (이원화)

- **마크다운 원본 (메인 본문)** — `~/daejong-page/worklog-source/YYYY-MM-DD_vX.Y.Z.md`
  - 헤딩(##), 불릿, 링크, 코드블록, 강조 등 마크다운 풀 사용
  - 강대종님 본인이 훑어 보기 편하도록 섹션·리스트 구조화
  - 홈페이지 `/worklog.html` 페이지는 이 파일을 렌더링하지 않음 (공개 렌더링은 산문체 공개본 쪽)
- **산문체 공개본 (카페·홈페이지용)** — `~/daejong-page/worklog/YYYY-MM-DD_vX.Y.Z.md`
  - 기존 산문체 규칙 그대로 (8번 참조)
  - 홈페이지 `worklog.html` 이 이 파일을 렌더링
  - 네이버 카페 모바일 앱 붙여넣기 호환 (불릿·헤딩·이모지·백틱 금지)

두 파일은 같은 내용을 다른 톤으로 서술한다. 마크다운 원본을 먼저 쓰고, 그걸 산문체로 풀어 공개본을 만든다.

## 절차

### 0. 기기 라우팅 (맥 본진 집중 실행, 텔레그램 트리거 방식)

맥이 이 파이프라인의 SoT 다 (launchd·iOS·daejong-page 편집 전부 맥). /worklog 는 맥에서 실행해야 양쪽 세션 데이터가 통합되므로, **맥이 아닌 기기에서 호출되면 텔레그램 트리거로 맥에 위임한다.** (/to-iphone → /land 와 동일 패턴 — SSH 자동 실행 아님, 강대종님이 맥 창에 한 줄 복붙하는 명시적 승인 단계가 들어감.)

판별 + 트리거:

```bash
host=$(hostname)
if [[ "$host" != *MacBook* && "$host" != *MBP* ]]; then
  # 맥이 아님 → 텔레그램으로 트리거 1줄 전송 후 여기서 종료
  # reply 툴을 통해 chat_id 538806975 에 아래 본문 전송:
  #
  #   📋 /worklog 트리거
  #   날짜: ${ARGS:-오늘}
  #   Mac Claude 창에 아래 한 줄 복붙:
  #   /worklog ${ARGS:-}
  #   (맥에서 실행 완료되면 이 기기는 다음 /sync 또는 06:45 자동 sync 때 git 으로 내려받음)
  exit 0
fi
```

**라우팅 실패 fallback**: 텔레그램이 끊긴 상태거나 전송 실패면 아래 1번부터 로컬에서라도 계속 돌린다 (기존 동작 유지, 소프트 페일).

맥 본진이면 라우팅 건너뛰고 바로 1번부터 실행.

### 1. 날짜 결정

- `$ARGUMENTS`로 날짜(`YYYY-MM-DD`)가 주어졌으면 그 날짜 사용
- 없으면 오늘 날짜 (KST): `date +%Y-%m-%d`
- 이후 단계에서 이 날짜를 `TARGET_DATE` 로 지칭

### 1b. 데스크탑 세션 동기화 (Tailscale rsync, 소프트 페일)

멀티 기기 운영 구조상 윈도우 데스크탑 WSL 에서도 Claude Code 세션이 생성된다. /worklog 는 맥에서 주로 실행하므로, 데스크탑 세션 로그를 맥으로 미리 당겨와야 통합 일지 작성이 가능하다.

- 동기화 명령:
  ```
  mkdir -p ~/.claude/projects-desktop
  rsync -az --timeout=15 ssamssae@100.80.253.65:~/.claude/projects/ ~/.claude/projects-desktop/ 2>&1
  ```
- **소프트 페일 원칙**: 데스크탑이 꺼져 있거나 Tailscale 단절이면 rsync 실패 → 에러 메시지 한 줄만 출력하고 **절대 실패로 중단하지 말 것**. 맥 세션만으로 일지 작성 계속 진행.
- 데스크탑에서 맥 방향으로 /worklog 를 돌릴 때(역방향 드물지만)는 출발지를 맥(user@100.74.85.37) 으로 바꿔 실행. 호스트 판별은 `hostname` 으로.
- **충돌 방지**: 데스크탑 세션 폴더명이 `-home-ssamssae-...` 형태로 맥의 `-Users-user-...` 와 달라 세션 ID 충돌 없음.

### 2. 해당 날짜의 모든 Claude Code 세션 수집 (크로스 세션, 맥+데스크탑)

- 세션 저장 루트: `~/.claude/projects/*/` (맥 본진 세션) + `~/.claude/projects-desktop/*/` (1b 에서 동기화한 데스크탑 세션)
- `TARGET_DATE` 에 **활동이 있었던** 세션 파일 찾기 (두 경로 모두 탐색):
  ```
  find ~/.claude/projects ~/.claude/projects-desktop -maxdepth 2 -name "*.jsonl" -newermt "TARGET_DATE 00:00" ! -newermt "TARGET_DATE 23:59:59" 2>/dev/null
  ```
  또는 파일 내부 `timestamp` 필드(UTC ISO)가 TARGET_DATE(KST) 에 해당하는 라인만 골라도 됨. mtime 과 실제 대화 시간이 어긋날 수 있으면 후자가 더 정확.
- 각 `.jsonl` 은 한 줄당 하나의 이벤트(JSON). 주요 타입: `user`, `assistant`, `tool_use`, `tool_result`.
- 추출 대상:
  - `type == "user"` 의 사용자 입력 텍스트(슬래시 커맨드 포함) — **"무엇을 요청했는지"**
  - `type == "assistant"` 의 응답 요약 — **"무엇을 답/실행했는지"** (툴콜 인자에서 파일 경로, Bash 명령 등 실제 작업의 증거)
- 프로젝트 폴더 이름(`-Users-user-dutch-pay-calculator` 등) 을 보면 어느 프로젝트/어느 위치(`cwd`)에서 작업했는지 파악 가능. 이벤트 내부 `cwd` 필드도 참고.
- 구분하여 수집: 앱 개발(예: dutch_pay_calculator, yakmukja, simple_memo_app), 홈 세션(`-Users-user`, 일반 질문/설정/텔레그램/도우미 성격), 기타.
- 용량이 큰 세션은 `head`/`tail` 로 샘플링하지 말고 필요한 필드만 파이썬 원라이너로 파싱해 요약 추출(토큰 절약).

### 3. 모든 프로젝트의 그 날짜 git 커밋 수집

- 관심 프로젝트 후보: 2단계에서 잡힌 각 프로젝트 폴더의 실제 경로들(`~/dutch_pay_calculator`, `~/yakmukja`, `~/simple_memo_app`, `~/babmeokja`, `~/daejong-page`, `~/apps/*` 등) + 현재 cwd
- 각 프로젝트에서:
  ```
  git -C <repo> log --since="TARGET_DATE 00:00" --until="TARGET_DATE 23:59" --pretty=format:"%h %s" --all
  git -C <repo> branch --show-current
  ```
- git 저장소가 아닌 폴더는 건너뜀(오류 무시)

### 4. 사용자가 수동 보강한 내용 병합

- 현재 대화 컨텍스트에서 사용자가 "오늘 OO도 했어", "어제 웹에서 OO 했어" 같은 내용을 얘기했으면 포함
- `~/.claude/projects/-Users-user/memory/` 의 project 타입 메모리 중 TARGET_DATE 관련 항목이 있으면 참고
- Claude 웹(claude.ai), 외부 서비스 활동 등 **로컬에 로그가 없는 활동**은 자동 수집 불가. 사용자가 명시적으로 알려준 경우에만 포함.

### 5. 작업 내용 요약

- 2~4단계에서 모은 모든 자료를 합쳐 주제별로 정리 (앱 단위로 묶어도 되고, 영역별—UI/기능/버그/최적화/배포/설정/학습·대화—로 묶어도 됨. 그날 성격에 맞게 판단)
- 단순 질문·잡담은 의미 있는 것만 추려 "학습/상담" 단락으로 간단히
- 커밋 메시지만이 아니라 대화에서 드러난 맥락/의도까지 포함
- 절대 비밀번호/토큰/API key 포함 금지. 내부 경로 중 `~/.claude` 하위의 세션 ID 같은 건 쓰지 않기.

### 6. 파일 작성 (버전 스냅샷 방식, 이원화)

#### 6-a. 버전 결정 + 공통 규칙

- **버전 결정 기준 경로**: `~/daejong-page/worklog-source/` (원본 쪽이 기준. 공개본은 같은 버전으로 쌍을 맞춘다).
  ```bash
  LATEST=$(ls ~/daejong-page/worklog-source/ 2>/dev/null | grep "^TARGET_DATE_v" | sort -V | tail -1)
  ```
  - 없으면 `v1.0.0` 으로 시작
  - 있으면(예: `_v1.0.2.md`) 패치 버전 +1 한 **새 파일** `_v1.0.3.md`
- **절대 기존 버전 파일을 Edit 하지 말 것.** 항상 Write 로 새 파일을 만든다. 기존 스냅샷은 보존.
- 이전 버전이 있으면 Read 로 맥락 파악 후, **직전 버전 이후 달라진 작업을 중심으로** 새 스냅샷 작성.
- 마크다운 원본과 산문체 공개본은 **같은 버전 번호** 를 공유한다. 짝을 맞춰야 함.
- 마크다운 원본이 없던 과거 날짜(2026-04-20 이전) 는 산문체 공개본만 존재. 소급 작성은 선택.

#### 6-b. 마크다운 원본 작성 (메인 본문)

- 파일: `~/daejong-page/worklog-source/TARGET_DATE_vX.Y.Z.md`
- 포맷: **자유 마크다운**. 아래 표준 뼈대를 기본 템플릿으로 쓰되 그날 성격에 따라 유연하게.
  ```markdown
  # YYYY.MM.DD 작업일지 vX.Y.Z

  > 한 줄 요약 (이 버전에서 달라진 핵심 1-2문장)

  ## 오늘의 궤적
  (하루 전체 맥락. 어느 프로젝트 몇 개 오갔는지, 주제 흐름은 뭐였는지.)

  ## <프로젝트 또는 영역 1>
  - 불릿 OK
  - 커밋 해시·경로·링크 모두 마크다운으로 자유롭게 표기
  - 코드/명령어도 인라인 `backtick` 이나 코드블록 허용

  ## <프로젝트 또는 영역 2>
  ...

  ## 인프라·스킬·자동화
  - /worklog 이원화 반영, /issue 재발 감지 추가 같은 항목

  ## 학습·상담
  - 이번 일지에 남길 만한 대화나 결정이 있었다면

  ## 남은 작업
  - 다음 버전 또는 내일로 이월되는 항목

  ## 관련 커밋
  | repo | SHA | 메시지 |
  |---|---|---|
  | daejong-page | `abc1234` | feat: ... |
  ```
- **민감 정보는 여기서도 금지.** 비밀번호/토큰/API key/세션 ID/사적 호스트명 제외.
- 이 파일이 "강대종님 본인이 읽고 검색하는 용도" 이므로, 카페용 금지 문자(이모지·화살표 등) 는 자유롭게 써도 된다.

#### 6-c. 산문체 공개본 작성 (홈페이지·카페용)

- 파일: `~/daejong-page/worklog/TARGET_DATE_vX.Y.Z.md`
- 6-b 의 마크다운 원본을 읽어 들인 뒤, **8번 "포맷 원칙" 규칙을 적용한 산문체 문단** 으로 풀어 쓴다.
- 구조·내용은 동일하지만 헤딩·불릿·백틱·이모지·화살표 금지. 불릿은 문장으로 풀고, 코드/경로는 공백 양옆에 평문처럼.
- 첫 줄: `YYYY.MM.DD 작업일지 vX.Y.Z`
- 마지막 줄: 해당 공개본 파일의 GitHub blob URL 한 줄. `https://github.com/ssamssae/daejong-page/blob/main/worklog/TARGET_DATE_vX.Y.Z.md`

### 7. 커밋 & 푸시 (daejong-page 단일 저장소)

- 두 파일 모두 stage:
  ```
  git -C ~/daejong-page add worklog-source/TARGET_DATE_vX.Y.Z.md worklog-source/index.json \
                           worklog/TARGET_DATE_vX.Y.Z.md worklog/index.json
  ```
- 커밋 메시지: `docs: 작업일지 TARGET_DATE vX.Y.Z (원본+공개본)`
- push: `git -C ~/daejong-page push origin main`

### 7b. 인덱스 파일 갱신 (양쪽 각각)

각 폴더마다 독립된 `index.json` 을 유지한다.

#### 7b-1. worklog/ (산문체 공개본 인덱스) — 홈페이지가 읽는 쪽

- 위치: `~/daejong-page/worklog/index.json`
- entry 형식:
  ```json
  {
    "file": "YYYY-MM-DD_vX.Y.Z.md",
    "date": "YYYY-MM-DD",
    "version": "vX.Y.Z",
    "title": "<작업일지 첫 문단 요약 1문장, 20~40자>",
    "updated": "<ISO 8601 KST>"
  }
  ```
- 중복 방지: 같은 `file` 이 이미 있으면 갱신만(중복 추가 금지). entries 는 `date` 내림차순.

#### 7b-2. worklog-source/ (마크다운 원본 인덱스) — 강대종님 본인용

- 위치: `~/daejong-page/worklog-source/index.json`
- entry 형식:
  ```json
  {
    "file": "YYYY-MM-DD_vX.Y.Z.md",
    "date": "YYYY-MM-DD",
    "version": "vX.Y.Z",
    "summary": "<이 버전에서 달라진 핵심 1줄>",
    "updated": "<ISO 8601 KST>"
  }
  ```
- 같은 구조. entries 내림차순.

### 7c. 실패 처리

- 원본(6-b) 만 작성되고 공개본(6-c) 에서 에러 나면: 공개본 생성 재시도. 여전히 실패하면 원본 커밋 후 사용자에게 "공개본 생성 실패, 원본은 저장됨" 보고.
- daejong-page push 실패 시 이미 local commit 은 있으므로 재시도만 권고.

### 8. 결과 보고 (산문체 공개본 기준)

- 작업일지 **공개본(산문체) 전체 본문** 을 텔레그램/채팅 응답으로 전송. 사용자가 바로 복사해 네이버 카페 모바일 앱에 붙여넣어도 에러 없이 들어가야 함.
- 추가로 한 줄: "마크다운 원본은 worklog-source/ 에 별도 저장됨"
- 텔레그램 세션이면 reply 도구로 전송.

#### 포맷 원칙: "그날 일기처럼, 산문체로" (공개본 전용)

- 불릿 나열 금지. 문장을 자연스럽게 이어 쓸 것
- 섹션은 한 문장 또는 짧은 한 줄로 시작
- 섹션 사이는 빈 줄 1줄
- 전체 길이는 대략 800~1500자 내
- 담담한 평서체 선호 ("~했다", "~만들었다", "~마쳤다")

#### 금지 문자/기호 (공개본 전용, 원본에는 적용 X)

- 이모지/이모티콘 전부 금지
- 대괄호 `[]`, 꺾쇠 `<>`, 중괄호 `{}` 금지
- 화살표 `→`, `->` 금지. "에서", "로", "후" 같은 말로 풀어쓸 것
- 긴 대시 `—`, 중점 `·`, 말줄임 `…` 금지. 하이픈 `-` 도 글머리로 쓰지 말 것
- 수평선 `━━━`, `───`, `====` 등 장식선 금지
- 백틱 `` ` ``, 트리플 백틱 금지. 코드/경로/명령어는 그냥 공백 양옆에 두고 평문처럼 적기
- 마크다운 헤딩 `#`, `##` 금지
- 볼드/이탤릭 `**`, `*`, `_` 금지
- 마크다운 링크 `[text](url)` 금지
- URL은 맨 마지막 한 줄에 작업일지 GitHub blob URL 하나만 허용
- **커밋 해시 목록 금지**. 필요하면 "최신 커밋은 5800aea로 원격 반영 완료" 한 줄만

#### 본문 구조 예시 (공개본, 산문체)

```
YYYY.MM.DD 작업일지 vX.Y.Z

오늘은 (하루 전체 맥락 한 단락. 여러 프로젝트를 오갔다면 그 흐름도 한두 문장으로.)

더치페이 계산기 쪽에서는
(해당 프로젝트에서 한 작업을 이어지는 문장으로)

약먹자에서는
(다음 프로젝트 작업)

기타 설정과 도구 쪽 작업도 있었다.
(텔레그램 봇, 클로드 설정, 스킬 수정, 메모리 업데이트 등 프로젝트 소속이 아닌 작업)

학습과 상담도 몇 건 있었다.
(질문/상담성 대화 중 의미 있는 것만 한두 문장)

남은 작업은
(짧게 한 단락 또는 한 줄)

오늘 기준 주요 저장소의 최신 커밋은 <해시>이고 원격 반영까지 끝난 상태다.

https://github.com/ssamssae/daejong-page/blob/main/worklog/YYYY-MM-DD_vX.Y.Z.md
```

**중요**: 공개본은 위 산문체 규칙을 반드시 지킨다. 원본(worklog-source/)은 마크다운 자유. 두 파일의 본문은 서로 완전 동일할 필요 없지만 **같은 사실·시간대·맥락** 을 담아야 한다. 공개본은 원본을 읽은 다음 규칙에 맞춰 풀어 쓴 결과물.

## 핵심 원칙 재확인

- 작업일지는 **두 파일**: 마크다운 원본(`worklog-source/`) + 산문체 공개본(`worklog/`)
- 홈페이지 `worklog.html` 은 공개본만 렌더링
- 버전 번호는 쌍으로 맞춘다 (`v1.0.3` 원본이 있으면 같은 날 `v1.0.3` 공개본도 필수)
- 한 번 push 한 버전 파일은 수정하지 않는다 (새 버전으로 append)
- 2026-04-20 이전 산문체 파일만 있는 날은 그대로 둔다. 소급 마크다운 원본은 선택 사항.
