---
name: pull-apps
description: 모든 Flutter 앱 repo(~/ 최상위 + ~/apps/*/) 를 git pull --rebase --autostash 로 일괄 최신화. 다른 기기(주로 Mac)에서 push 한 앱 코드 변경을 이 기기(주로 WSL)에서 받아올 때 호출. 강대종님이 "앱 당겨줘", "앱 pull", "/pull-apps", "WSL 에 앱 받아", "맥에서 넘긴 앱 받아" 라고 하면 실행.
allowed-tools: Bash
---

# /pull-apps — 앱 repo 일괄 pull

`~/` 최상위(메모요/약먹자/더치페이 등) + `~/apps/*/` (한줄일기/한컵/가계부/포모도로 등) 의 모든 Flutter 앱 repo 를 한 번에 `git pull --rebase --autostash` 한다. 기준: `.git` 디렉터리 + `pubspec.yaml` 존재. Mac ↔ WSL 기기 간 앱 코드 동기화 gap 을 즉시 메우는 게 목적.

## 언제 호출되는가

- 다른 기기(주로 Mac) 에서 앱 코드를 push 했고 이 기기(주로 WSL) 에서 바로 받고 싶을 때
- "맥에서 한줄일기 만졌는데 WSL 에서 최신화 안 돼" 류 상황
- 새 세션 시작 직후 앱 repo 가 동기 상태인지 확보하고 싶을 때

## 절차

```bash
# $HOME 최상위 + ~/apps/ 두 경로에서 .git + pubspec.yaml 가진 폴더를 전수 스캔
for dir in ~/*/ ~/apps/*/; do
  [ -d "${dir}.git" ] || continue
  [ -f "${dir}pubspec.yaml" ] || continue
  name=$(basename "${dir%/}")
  cd "${dir%/}"
  before=$(git rev-parse HEAD)
  git pull --rebase --autostash --quiet 2>&1
  after=$(git rev-parse HEAD)
  if [ "$before" = "$after" ]; then
    echo "✓ $name: up to date"
  else
    count=$(git log --oneline "${before}..${after}" | wc -l | tr -d ' ')
    echo "✅ $name: $count 커밋 수신"
    git log --oneline "${before}..${after}" | sed 's/^/    /'
  fi
done
```

## 커버 대상 예시 (7개)

| 앱 | 경로 |
| --- | --- |
| 메모요 | `~/simple_memo_app` |
| 약먹자 | `~/yakmukja` |
| 더치페이 | `~/dutch_pay_calculator` |
| 한줄일기 | `~/apps/hanjul` |
| 한컵 | `~/apps/hankeup` |
| 가계부 | `~/apps/mini_expense` |
| 포모도로 | `~/apps/pomodoro` |

새 앱을 ~/ 혹은 ~/apps/ 어디에 두든 `.git + pubspec.yaml` 조합만 맞으면 자동 픽업.

## 출력 예시

```
✓ hankeup: up to date
✅ hanjul: 4 커밋 수신
    b861770 feat(hanjul): toss blue rebrand + diary-notebook icon
    133f177 feat(hanjul): toss-tone polish + new app icon
    ...
✓ simple_memo_app: up to date
✓ yakmukja: up to date
```

실행 후 텔레그램으로도 한 줄 요약을 보낸다 (chat_id=538806975):

```
📥 /pull-apps 완료
  수신: hanjul 4 · pomodoro 1 · mini_expense 2
  up-to-date: hankeup
```

## 충돌 처리

`--autostash` 가 로컬 dirty 를 자동 stash/복원 하지만, rebase 충돌은 여전히 사람이 풀어야 함. 어느 앱에서 충돌 났는지만 명확히 보고하고 나머지 앱은 계속 pull 한다:

```
❌ hanjul: rebase conflict — 수동 해결 필요
   CONFLICT (content): lib/screens/write_screen.dart
✓ hankeup: up to date
...
```

## 안전

- `git pull --rebase --autostash` 은 기본적으로 가역. 로컬 커밋은 rebase 로 재적용, 로컬 dirty 는 stash 로 보존
- `git reset --hard` 등 destructive 명령은 절대 쓰지 않음
- 네트워크 실패는 무시하고 다음 앱으로 (원격 unreachable 을 pull 실패로 혼동하지 않음)

## 짝 스킬 (Mac 쪽)

Mac 에서 작업을 모두 push 하면 Stop 훅 `stop-check-repos-dirty.sh` 가 앱별 `ahead` 커밋 수와 dirty 파일을 텔레그램 경보로 알림. 즉 Mac 쪽에서 "push 안 됐어요" → WSL 쪽에서 `/pull-apps` 로 받기 = 쌍.
