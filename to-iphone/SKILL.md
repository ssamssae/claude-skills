---
name: to-iphone
description: Flutter 앱 하나를 git 커밋 → GitHub push → Mac 트리거까지 원샷으로 실행해서 최종적으로 아이폰에 /irun 까지 자동으로 닿게 한다. WSL 데스크탑 전용. Mac 쪽 /land 스킬과 페어로 동작. 호출 형태 `/to-iphone <앱명>` 또는 `/to-iphone --path <절대경로>`. 사용자가 "/to-iphone", "아이폰에 올려줘", "ship to iphone", "이 앱 폰으로 보내", "ship-to-iphone" 이라고 하면 이 스킬을 실행한다.
---

# /to-iphone — Ship Flutter app to iPhone (via Mac)

## 목적

WSL 데스크탑에서 만든 Flutter 앱 하나를 한 번의 호출로 깨끗하게 아이폰까지 보낸다. 과정:

1. 로컬 git 정리 + 커밋
2. GitHub remote 세팅 + push
3. 텔레그램으로 `/land <repo url>` 한 줄 전송 → Mac Claude 가 수신 → clone + iOS 빌드 + /irun
4. 전 과정 텔레그램 보고

Mac 쪽 `/land` 는 별도 스킬이며 입력은 **repo URL 한 개**. 이 스킬은 그 URL 만 깨끗이 만들어 넘긴다. iOS signing / 번들ID 는 건드리지 않는다 — 그건 `/land` 책임.

## 호출

```
/to-iphone hankeup
/to-iphone mini_expense
/to-iphone --path "/mnt/c/src/flutter-factory/apps/onedayfeel"
```

인자 해석:
- 앱명(첫 단어): 먼저 `/mnt/c/src/flutter-factory/apps/<name>`, 없으면 `/mnt/c/src/<name>` 순서로 탐색
- `--path <경로>`: 절대경로 직접 지정. 이 경우 이름은 디렉터리 basename 으로 자동 추출
- 인자 없거나 매치 실패: 강대종님에게 앱명 요구하고 종료

## 절차 (순서 준수)

### 1. 환경 체크 (stop 조건 포함)

- `hostname` 실행. `DESKTOP-*` 가 아니면 **"이 스킬은 WSL 데스크탑 전용"** 안내 후 종료.
- 대상 앱 경로 확인. 없으면 종료.
- `pubspec.yaml` 존재 확인. 없으면 "Flutter 프로젝트가 아닙니다" 로 종료.
- `gh auth status` 확인. 로그인 안 됐으면:
  - 텔레그램으로 알림
  - 안내: `gh auth login -h github.com --scopes repo,workflow`
  - 종료 (사용자 1회성 작업 필요)

### 2. 시크릿 가드 (필수)

- `.gitignore` 점검. 없으면 Flutter 표준 `.gitignore` 를 자동 생성 (build/, .dart_tool/, .flutter-plugins*, .pub-cache/, ios/Pods/, ios/.symlinks, android/.gradle/, *.iml, .idea/, .env, *.key, *.pem, *.p12, *.keystore, *.jks, google-services.json, GoogleService-Info.plist 포함)
- `git status --porcelain` 출력에서 아래 패턴 중 하나라도 **staged/modified/added** 로 나오면 즉시 중단 + 경고 + 종료:
  - `.env`, `*.key`, `*.pem`, `*.p12`, `*.keystore`, `*.jks`, `google-services.json`, `GoogleService-Info.plist`
- 첫 커밋 전 (or 큰 변경 시) 시크릿 스캔 1회:
  - `git diff --cached -U0 | grep -iE '(api[_-]?key|secret|token|password)\s*[:=]\s*["'"'"'`][^"'"'"'`]{8,}'`
  - 매치가 있으면 **경고만** 찍고 강대종님에게 텔레그램 확인 요청. 강제 중단 아님(false positive 많음).

### 3. git 상태 처리

- `.git/` 없으면:
  - `git init -b main`
  - 첫 커밋 메시지: `"feat: initial commit (flutter-factory MVP)"`  (이 이름은 스펙대로 고정)
- 변경사항 있으면 (`git status --porcelain` 비어있지 않으면):
  - 커밋 메시지: `"chore: ship to iphone $(date +%Y-%m-%d)"`
  - `git add -A` 후 `git commit -m "<위 메시지>"`
  - **주의:** `--no-verify` 금지, pre-commit hook 실패하면 그대로 중단
- clean + 이미 원격 push 최신 상태면 "이미 최신" 로그만 찍고 3단계 건너뜀
- `git push` 에는 `--force` / `--force-with-lease` **절대 금지**

### 4. GitHub remote 세팅

- `git remote get-url origin` 확인
- remote 없으면:
  - `gh repo create ssamssae/<앱명> --private --source=. --remote=origin --push`
  - 이미 같은 이름 repo 가 있으면 (409 conflict) `gh repo view ssamssae/<앱명> --json visibility,url` 로 확인:
    - public 이어도 **절대 --private 로 전환 말 것**. 상태 한 줄 보고 후 그대로 진행.
    - 안전 승인 없이 기존 repo 와 연결할지는 강대종님에게 텔레그램으로 물어봄.
- remote 있으면: `git push origin HEAD` (main 직푸시 허용 — 개인 repo)

### 5. 선택적 분석

- `cmd.exe /c "cd /d <windows경로> && C:\src\flutter\bin\flutter.bat analyze"` 실행.
- 실패해도 경고만 남기고 진행. `/land` 쪽에서 다시 pub get + analyze 할 것임.

### 6. Mac 트리거 (텔레그램)

- 강대종님 텔레그램(chat_id 538806975)으로 단 한 줄만 전송:
  ```
  /land https://github.com/ssamssae/<앱명>.git
  ```
- 그 **아래 안내 메시지**: "Mac Claude 창에 위 한 줄만 복붙해 주세요. 아이폰에 올려드릴게요."
- 자동으로 Mac 에 SMS / iMessage 같은 추가 경로는 쓰지 않는다. 텔레그램이 기본 경로.

> **SSH primary 를 쓰지 않는 이유 (설계 결정, 2026-04-20)**
> macOS 로그인 키체인은 비인터랙티브 SSH 세션에서 접근 불가. Claude CLI 가 OAuth 토큰을 키체인에 저장하기 때문에 `ssh user@mac "claude -p ..."` 는 항상 "Not logged in" 으로 실패한다.
> `launchctl asuser` 우회도 root 권한 필요해서 차단됨. Apple 보안 모델 자체의 제약이라 우회 불가.
> 따라서 이 스킬은 텔레그램 한 줄 전달 = default 로 간다. Mac Claude 가 살아있으면 그 메시지 1-click 처리.

### 7. 최종 보고 (텔레그램)

- chat_id: 538806975
- 단계별 상태를 짧게 (시작 / 커밋 / push / Mac 트리거 / 완료)
- 중간 실패 시 어느 단계에서 왜 실패했는지 + 복구 방법 1~2개

## 안전 원칙 (위반 시 중단)

- 개인 repo 에 main 직푸시는 허용. 그러나 **`--force` / `--force-with-lease` 금지**.
- **`--no-verify` 금지** — pre-commit hook 실패하면 원인 고친 뒤 다시 시도. 훅 무시하지 말 것.
- `.env`, `*.key`, `*.pem`, `*.p12`, keystore 류가 git diff 에 들어가면 **즉시 중단 + 경고 + 종료**. 사용자 명시 승인 없이는 재개 금지.
- 시크릿 추정(api_key / secret / token / password 값 패턴)이 잡히면 경고만 찍고 **텔레그램으로 확인 요청** 후 진행 여부 결정.
- 이미 존재하는 remote 의 **visibility 변경 금지** (public 이던 것을 private 로 내리지 말고, 그 반대도). 상태 1줄 보고만.
- 번들ID / 패키지명 변경 금지. iOS signing 세팅 변경 금지. → /land 책임.
- Mac SSH 실패했는데 "그냥 계속" 같은 침묵 스킵 금지. 반드시 Fallback 으로 전환하고 사용자에게 알린다.

## 외부 값 / 전제

| 항목 | 값 |
|------|-----|
| 맥 본진 SSH | `user@100.74.85.37` (Tailscale) |
| GitHub org | `ssamssae` |
| gh auth scopes | `repo`, `workflow` |
| 텔레그램 chat_id | `538806975` (MCP reply 또는 send.sh) |
| 대상 앱 기본 탐색 | `/mnt/c/src/flutter-factory/apps/<name>` → `/mnt/c/src/<name>` |

## 대응 스킬 /land (맥 본진)

- 위치: Mac `~/.claude/skills/land/SKILL.md` (별도 작성 예정)
- 입력: repo URL 한 개 (예: `https://github.com/ssamssae/hankeup.git`)
- 역할: clone (있으면 pull) → `flutter clean && pub get` → iOS signing 자동 처리 → `/irun` → 텔레그램 보고

이 스킬은 `/land` 의 입력만 깨끗이 만들어 넘긴다. 서로 역할이 겹치지 않도록 주의.

## 현재 대상 앱 (첫 실행 대기)

| 앱명 | 경로 | git 상태 | remote |
|------|------|---------|-------|
| `hankeup` | `/mnt/c/src/hankeup` | 로컬 git 있음 (master/main 커밋 1개) | 없음 — 이번에 생성 |
| `mini_expense` | `/mnt/c/src/flutter-factory/apps/mini_expense` | git 아님 | 이번에 init+생성 |

**첫 실행은 강대종님 승인 후에만**. 스킬 완성 직후 자동 실행 금지.
