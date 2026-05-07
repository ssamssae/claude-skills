---
name: worklog
description: 하루 전체 작업(현재 세션 + 그날 모든 Claude 세션 로그 + 모든 프로젝트 git 커밋) 수집·요약해 작업일지 저장 + GitHub·홈페이지 반영. 마크다운 원본(worklog-source/) + 뉴스레터 공개본(worklog/) 동시 생성. 트리거 "작업일지", "일지", "일지 써줘", "오늘 일지", "일지 기록", "/worklog".
allowed-tools: Bash, Write, Edit, Read, Glob, Grep
---

# 작업일지 작성 & 깃허브 푸시

**지정 날짜에 수행한 모든 작업**(현재 프로젝트 + 다른 프로젝트 + 다른 Claude Code 세션)을 수집해 작업일지를 작성하고 GitHub·홈페이지에 올립니다. 단일 프로젝트만 기록하던 과거 동작과 다르게, 그날 하루 전체 궤적을 한 문서에 합칩니다.

## 기기 라우팅 (지휘관 1명 원칙)

🍎 Mac 본진 = 지휘관(설계·결정·메인 세션, main 머지 결정) / 🏭 Mac mini = 빌드·배포 워커(SSH 라우팅 수신) / 🪟 WSL = 작업자(`wsl/*` 브랜치 push, main 직접 push 금지). 운반체 = `wsl-directive.sh` / `mac-report.sh`.

**이 스킬**: 양 기기 호출 가능. WSL 에서 호출 시 commit/push 가 `wsl/*` 브랜치 정책 따라야 함 (이번 docs PR 은 본문 가이드만, 코드 분기는 별도 PR 예정).

## 출력 파일 2종 (이원화)

- **마크다운 원본 (강대종님 본인 기록용)** — `~/daejong-page/worklog-source/YYYY-MM-DD_vX.Y.Z.md`
  - 헤딩(##), 불릿, 링크, 코드블록, 강조, 표 등 마크다운 풀 사용
  - 본인이 훑어 보기 편하도록 **섹션·리스트·표 구조화**. 사실 기록 중심.
  - 홈페이지는 이 파일을 렌더링하지 않음 (공개 렌더링은 공개본 쪽).
- **뉴스레터 스타일 공개본 (홈페이지·구독자용)** — `~/daejong-page/worklog/YYYY-MM-DD_vX.Y.Z.md`
  - 같은 사실을 **스토리 서사**로 풀어 쓴 뉴스레터 본. 마크다운 풀 사용.
  - `~/daejong-page/newsletter/ep1-2026-04-20.md` 와 같은 톤·구조: 시간 기반 블록쿼트 훅 → 번호 매긴 evocative 섹션 → story arc(setup → 복잡해진 지점 → 반전/해결 → 배운 것) → 다음 예고 → 서명.
  - 홈페이지 `worklog.html` 과 `worklog/view.html` 이 이 파일을 **마크다운 렌더러(marked.js)** 로 파싱해서 보여줌.

두 파일은 같은 사실·시간대·맥락을 다른 톤으로 서술한다. 원본을 먼저 작성해 사실 구조를 잡고, 그걸 바탕으로 공개본을 뉴스레터 서사로 풀어 쓴다.

> **카페 붙여넣기 용도는 2026-04-21 부로 드롭.** 과거 공개본은 네이버 카페 모바일 앱 붙여넣기 호환을 위해 마크다운 기호를 전면 금지하던 규칙이 있었으나, 뉴스레터 스타일 전환과 함께 폐지. 공개 배포 경로는 홈페이지 렌더링 일원화.

## 절차

### 0. 기기 라우팅 (맥 본진 집중 실행, 텔레그램 트리거 방식)

맥이 이 파이프라인의 SoT 다 (launchd·iOS·daejong-page 편집 전부 맥). /worklog 는 맥에서 실행해야 양쪽 세션 데이터가 통합되므로, **맥이 아닌 기기에서 호출되면 텔레그램 트리거로 맥에 위임한다.** SSH 자동 실행 아님, 강대종님이 맥 창에 한 줄 복붙하는 명시적 승인 단계가 들어감.

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

### 3b. 맥미니 Obsidian 작업일지 수집 (소프트 페일)

맥미니 `~/Documents/openclaw_macmini/Worklog/` 에 날짜별 옵시디언 작업일지가 쌓인다. TARGET_DATE 에 해당하는 파일을 SSH 로 읽어 내용을 병합한다.

```bash
# TARGET_DATE 형식: YYYY-MM-DD
OBS_FILES=$(ssh -o ConnectTimeout=5 mac-mini \
  "ls ~/Documents/openclaw_macmini/Worklog/${TARGET_DATE}*.md 2>/dev/null" 2>/dev/null)

if [[ -n "$OBS_FILES" ]]; then
  for f in $OBS_FILES; do
    ssh mac-mini "cat '$f'" 2>/dev/null
  done
fi
```

- SSH 실패 / 파일 없음 → **소프트 페일**: 에러 없이 건너뜀. 나머지 수집은 계속.
- 파일이 있으면 내용을 그대로 읽어 5단계(요약) 입력에 포함. 맥미니 Obsidian 일지에만 있는 활동(OpenClaw·Codex 관련 맥미니 작업 등)이 worklog 에 반영된다.
- **중복 제거**: 같은 사건이 git 커밋 + Obsidian 양쪽에 기록된 경우 한 번만 서술.

### 4. 사용자가 수동 보강한 내용 병합

- 현재 대화 컨텍스트에서 사용자가 "오늘 OO도 했어", "어제 웹에서 OO 했어" 같은 내용을 얘기했으면 포함
- `~/.claude/projects/-Users-user/memory/` 의 project 타입 메모리 중 TARGET_DATE 관련 항목이 있으면 참고
- Claude 웹(claude.ai), 외부 서비스 활동 등 **로컬에 로그가 없는 활동**은 자동 수집 불가. 사용자가 명시적으로 알려준 경우에만 포함.

### 5. 작업 내용 요약 (사실 구조 → 서사 구조)

- 2~4단계에서 모은 자료를 **사실 단위로 정리**: 어느 프로젝트에서 무엇이 언제 시작돼 언제 끝났고, 막힌 지점은 어디였고, 어떻게 풀렸는지.
- 이 단계에서 먼저 **원본용(사실 구조)** 을 만들고, 그걸 바탕으로 **공개본용 story arc(서사 구조)** 을 뽑는다.
- Story arc 재료 뽑을 때 질문:
  - **훅**: 오늘의 결정적 전환 순간(한두 개 타임스탬프). 블록쿼트로 뽑을 재료.
  - **복잡해진 지점**: 설계 오판·에러 메시지·막힘 구간.
  - **반전/해결**: 원인 파악 순간, 한 줄 고침, 드림팀 합의 등.
  - **배운 것**: 일반화 가능한 교훈(도구의 함정, 에러 메시지의 오도, 원인 파악 방법론).
- 단순 질문·잡담은 "학습·상담" 섹션에 한두 문장.
- 커밋 메시지만이 아니라 대화에서 드러난 맥락/의도·실패한 시도까지 포함.
- 절대 비밀번호/토큰/API key 포함 금지. `~/.claude` 하위 세션 ID 제외.
- **픽션 금지**: ep1 수준의 스토리텔링은 하되 실제로 일어난 일만. 각색·과장·심리 묘사 추가 금지. 시간대·명령어·에러 메시지는 사실 그대로.

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
- 마크다운 원본과 공개본은 **같은 버전 번호** 를 공유한다. 짝을 맞춰야 함.
- 2026-04-20 이전 파일은 그대로 둔다 (레거시 "산문체 금지 마크다운" 규칙이 박힌 버전들). 소급 재작성 금지.

#### 6-b. 마크다운 원본 작성 (사실 구조, 강대종님 본인용)

- 파일: `~/daejong-page/worklog-source/TARGET_DATE_vX.Y.Z.md`
- 포맷: **자유 마크다운**. 템플릿 뼈대:
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
  ## 학습·상담
  ## 남은 작업

  ## 관련 커밋
  | repo | SHA | 메시지 |
  |---|---|---|
  | daejong-page | `abc1234` | feat: ... |
  ```
- 사실 중심, 표/불릿 자유. 본인이 찾아보기 쉽게 구조화.
- 민감 정보 금지 (비밀번호/토큰/API key/세션 ID/사적 호스트명).

#### 6-c. 뉴스레터 스타일 공개본 작성 (서사 구조, 홈페이지 렌더링 대상)

- 파일: `~/daejong-page/worklog/TARGET_DATE_vX.Y.Z.md`
- 레퍼런스: `~/daejong-page/newsletter/ep1-2026-04-20.md` (있으면 참고), `ep2-*` 가 생기면 그것도.
- **필수 구조**:
  1. `# YYYY.MM.DD 작업일지 vX.Y.Z — <한 줄 부제목>` (emdash 로 연결, 부제는 그 버전의 핵심 임팩트를 5~10단어로)
  2. 블록쿼트 시간 기반 훅 2~3줄
     ```markdown
     > HH:MM, 나는 X 를 하고 있었다.
     > HH:MM, Y 가 터졌다.
     > HH:MM, 결국 Z 로 결론이 났다.
     ```
     (타임스탬프는 실제 세션 로그·커밋 시각에서 정확히 뽑을 것)
  3. 도입 문단 — 이 에피소드가 무엇을 다루는 이야기인지 2~4문장. 결말 스포일러는 괜찮지만 **픽션 추가 금지**.
  4. 번호 매긴 evocative 섹션 헤딩 `## 1. <한 줄 제목>` — 섹션 제목 자체가 이야기 조각이 되도록 ("## 3. systemd 가 거절한 이유", "## 5. 봇이 자기 자신과 싸우고 있었다" 같은 패턴). 단순 "배포" 같은 명사형 지양.
  5. 본문 섹션은 3~6개. Story arc 흐름: 도입·스택결정 → 실행 → 막힌 지점 → 해결 → 마지막 함정 → 결과.
  6. 핵심 교훈 자리엔 `> **배운 것** — <일반화된 통찰 한 줄>` 블록쿼트.
  7. **표·코드블록·볼드** 는 필요하면 자유. 스택 테이블, 에러 메시지 코드블록, 커밋 해시 볼드 같은 패턴 환영.
  8. 마지막 섹션 "## N. 그래서 뭐가 남았나" 또는 유사 — 결과물·들어간 비용(시간/돈)·다음 예고.
  9. 구분선 `---` 아래에 다음 에피소드 예고 한 줄(있으면) + 서명.
  10. **서명 자동 삽입** (공개본 마지막 줄):
      ```markdown
      ---

      *다음 이야기는 <N> 이야기.* *(예고 없으면 이 줄 생략)*

      — 강대종 / [@ssamssae](https://github.com/ssamssae)
      ```
- **사실 제약**: ep1 스토리텔링 수준을 흉내내되 실제 일어난 일만. 시간대·명령어·에러 메시지·커밋 해시는 사실 그대로. 심리 묘사·각색·없던 대화 창작 금지.
- **민감 정보 금지** 는 원본과 동일.
- 길이: 800~3000자 (ep1 기준 ≈2800자). 하루 임팩트가 크면 길어도 OK, 잔잔한 날은 짧게.

### 7. 커밋 & 푸시 (daejong-page 단일 저장소)

- 두 파일 모두 stage:
  ```
  git -C ~/daejong-page add worklog-source/TARGET_DATE_vX.Y.Z.md worklog-source/index.json \
                           worklog/TARGET_DATE_vX.Y.Z.md worklog/index.json
  ```
- 커밋 메시지: `docs: 작업일지 TARGET_DATE vX.Y.Z (원본+뉴스레터 공개본)`
- push: `git -C ~/daejong-page push origin main`

### 7b. 인덱스 파일 갱신 (양쪽 각각)

각 폴더마다 독립된 `index.json` 을 유지한다.

#### 7b-1. worklog/ (공개본 인덱스) — 홈페이지가 읽는 쪽

- 위치: `~/daejong-page/worklog/index.json`
- entry 형식:
  ```json
  {
    "file": "YYYY-MM-DD_vX.Y.Z.md",
    "date": "YYYY-MM-DD",
    "version": "vX.Y.Z",
    "title": "<뉴스레터 부제목 또는 블록쿼트 훅 1줄 요약, 20~60자>",
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

### 7d. 결정 박제 (✨ 2026-04-24 추가 — 근본해결 핵심)

worklog 는 산문 기록이라 다른 스킬이 안 읽음. 오늘의 **decision-level 사실** 은 반드시 memory 로 박제해야 교차세션 전파됨.

**자동 추출 단계**:

1. 이번 worklog 산출물(`worklog-source/<date>_vX.Y.Z.md`) 의 본문을 스캔하면서 다음 패턴 매칭:
   - `"<X> 로 확정|채택|선정|결정"`
   - `"<Y> 제거|삭제|드롭|폐기"`
   - `"<Z> 신설|추가|도입|진입"`
   - `"플랫폼 <P> (으)로"`
   - 표 / 체크리스트에 **새 도메인 개념** 도입 (예: 태그 체계, SoT registry 등)

2. 각 후보에 대해 해당 memory 파일 존재 여부 확인:
   - 있으면 → Edit 로 frontmatter `decided_date` 갱신 + 본문에 "2026-04-24 업데이트" 섹션 append
   - 없으면 → 새 파일 Write. 분류 규칙:
     - 프로젝트 상태/방향 → `project_<slug>.md`
     - 작업 방식 / 규칙 → `feedback_<slug>.md`
     - 외부 시스템 좌표 → `reference_<slug>.md`
   - 모든 새/갱신 파일 frontmatter 에 **반드시 필요**: `decided_date: YYYY-MM-DD`, `decision: <한 줄 요약>`

3. **사용자 확인 단계 (CRITICAL)** — 자동 실행 금지. Memory 쓰기 전에 텔레그램 diff 미리보기:

```
🧠 오늘 decision-level 추출 N건:
1. 📄 project_<foo>.md (신규) — <decision 한 줄>
2. ✏️ feedback_<bar>.md (갱신) — <decision 한 줄>
...
확정 → "박제" / 보류 → "스킵" / 개별 수정 → "X번 빼" 같이
```

사용자 "박제" 응답 받으면 Write/Edit 실행 → memory auto-push hook 이 자동 render_recent_decisions.py 호출해서 MEMORY.md 상단 최근결정 블록 갱신 + commit+push.

4. 결과 보고 (8 단계와 머지 가능):
   ```
   🧠 결정 박제 N건 완료 → MEMORY.md 상단 "최근 결정 7일" 블록에 반영됨
      다른 Claude 세션이 시작 시 자동 인지.
   ```

**패턴 감지 가이드**: 애매할 땐 사용자에게 "이거 decision 맞아요?" 먼저 물음. false positive 는 노이즈, false negative 는 근본해결 실패 → **false negative 가 더 나쁨**. 의심되면 일단 추출.

### 7c. 실패 처리

- 원본(6-b) 만 작성되고 공개본(6-c) 에서 에러 나면: 공개본 생성 재시도. 여전히 실패하면 원본 커밋 후 사용자에게 "공개본 생성 실패, 원본은 저장됨" 보고.
- daejong-page push 실패 시 이미 local commit 은 있으므로 재시도만 권고.

### 8. 결과 보고

- 텔레그램/채팅 응답에 다음을 보고:
  - 공개본 파일 URL: `https://ssamssae.github.io/daejong-page/worklog/view.html?file=TARGET_DATE_vX.Y.Z.md`
  - 원본 GitHub URL: `https://github.com/ssamssae/daejong-page/blob/main/worklog-source/TARGET_DATE_vX.Y.Z.md`
  - 새 파일 2종 파일명 + 해당 커밋 해시 1줄 요약
  - 공개본 블록쿼트 훅(첫 2~3줄) 을 미리보기로 인용
- **공개본 전문을 텔레그램 본문으로 쏟아붓지 말 것** — 홈페이지 렌더링이 공식 공개 경로다. 텔레그램은 진입점만 안내.

## 뉴스레터 스타일 체크리스트 (공개본 Write 직전 자가 점검)

공개본을 `Write` 하기 직전 아래 항목을 속으로 순회하고, 하나라도 빠지면 보강한다.

1. 1행 제목에 emdash(`—`) + 한 줄 부제 있는가?
2. 블록쿼트 시간 기반 훅이 2~3줄 있는가? 타임스탬프는 실제 기록 기반인가?
3. 섹션 헤딩이 `## N. <evocative 한 줄>` 형식인가? 최소 3개 섹션?
4. Story arc 가 보이는가? (setup → 막힘 → 반전/해결 → 결과)
5. 핵심 교훈 자리에 `> **배운 것** — ...` 블록쿼트 있는가? (최소 1개, 최대 3개)
6. 표·코드블록·볼드가 의미 있게 쓰였는가? (단순 장식 금지)
7. 마지막에 결과물·비용·예고 섹션 있는가?
8. 구분선 `---` + 서명 `— 강대종 / [@ssamssae](https://github.com/ssamssae)` 있는가?
9. 사실 검증: 언급한 타임스탬프·명령어·에러·커밋 해시가 실제 로그/커밋과 일치하는가?
10. 픽션·각색·창작 대화 없는가? 심리 묘사가 과하지 않은가?

## 핵심 원칙 재확인

- 작업일지는 **두 파일**: 마크다운 원본(`worklog-source/`, 사실 중심) + 뉴스레터 공개본(`worklog/`, 서사 중심). 둘 다 마크다운 풀 사용.
- 홈페이지 `worklog.html` + `worklog/view.html` 은 공개본을 **marked.js 마크다운 렌더러**로 파싱해서 보여준다. 평문 렌더링이 아니다.
- 버전 번호는 쌍으로 맞춘다 (`v1.0.3` 원본이 있으면 같은 날 `v1.0.3` 공개본도 필수)
- 한 번 push 한 버전 파일은 수정하지 않는다 (새 버전으로 append)
