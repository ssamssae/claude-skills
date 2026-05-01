---
name: ctx
description: 지금까지 한 작업 + 현재 상태 + 다음 액션 요약. 강대종님이 "어디까지 했지?" 빠르게 파악할 때 호출.
---

# /ctx — 진행 상황 요약 (오늘 KST · 양 기기)

호출되면 **오늘(KST 자정 이후) 양 기기(Mac/WSL)의 commit + 활동 + 진행중 todo** 를 다음 형식으로 정리해서 출력한다. 답변은 한국어. 텔레그램 세션이면 mcp__plugin_telegram_telegram__reply 로, 아니면 일반 텍스트로.

"이 세션", "이 세션 직전", "방금" 같은 모호한 시간 범위 표현 금지. 시간 기준은 항상 **"오늘 KST 자정 이후"**.

## 호출 시 무조건 fetch (추측 0)

ctx 호출되면 출력 작성 전에 다음 4개를 **실제로 실행해서** 데이터를 확보한다. fetch 결과가 비면 그 섹션은 비워둔다 (추측 X, "확인 필요" 도 데이터 기반으로만).

### 1. 양 기기 오늘 commit

주력 repo 들에서 KST 자정 이후 commit 만:

```bash
KST_TODAY="$(date -d 'today 00:00' +%FT%T) +0900"
for repo in ~/daejong-page ~/claude-skills ~/.claude/automations ~/ssamssae.github.io \
            ~/apps/hanjul ~/apps/hankeup ~/apps/pomodoro ~/wordyo ~/review_radar; do
  [[ -d "$repo/.git" ]] || continue
  out=$(cd "$repo" && git log --since="$KST_TODAY" --pretty='%h %s' --all 2>/dev/null)
  [[ -n "$out" ]] && printf '\n## %s\n%s\n' "$(basename "$repo")" "$out"
done
```

(작업 시작 전 `git fetch --all` 권장 — 다른 기기에서 push 한 commit 도 보이도록.)

### 2. 양 기기 활동 카드

- `cat ~/daejong-page/activity/mac.json`
- `cat ~/daejong-page/activity/wsl.json`

`last_active_ts` / `last_user_prompt` / `last_recent_edit` 추려서 ⏳ 또는 ✅ 섹션에 반영. 두 기기 last_active 비교로 어느 쪽이 최신인지 판단.

### 3. 진행중 todo + 메모리 stale 매칭 (✨ 2026-05-01 보강)

`~/todo/todos.md` 의 `## 진행중` 섹션 → `[ ]` 항목명만 (상세 X).

**그리고 stale 매칭 1번** — 진척이 메모리에 적혔는데 todos 엔 반영 안 된 케이스 검출. todo SKILL.md 0.5 절(Reality Preflight) step 3-4 와 동일 로직:

```bash
find ~/.claude/projects/-Users-user/memory -name "project_*.md" -mtime -7 \
  -exec awk '/^description:/{$1=""; print FILENAME":"$0}' {} \;
```

각 진행중 todo 의 토큰 vs (오늘 commit + 메모리 description) 토큰 매칭 ≥ 2개면 stale 후보. STOPWORDS 는 goodnight step 1.5 와 동일.

후보가 있으면 📝 섹션 항목 옆에 inline 표시 (자동 닫음 X — surface 만):

```
- 🤝 한줄일기 1900원 유료 출시 (Android 잔여)  ← stale? `project_hanjul_android_alpha_review_submitted` (alpha 큐 진입)
```

후보 0건이면 표시 없음.

### 4. 본 세션 진행 내역

현 Claude 세션에서 한 commit/edit/메시지 — 1·2 와 별도로 추가 (있을 때만, 없으면 빼기).

## 출력 형식

```
**현재 상황 (YYYY-MM-DD HH:MM KST · {hostname})**

✅ **오늘 한 일** (KST 자정 이후, 양 기기)
- 🍎 <hash> <repo>: <한 줄 요약>
- 🪟 <hash> <repo>: <한 줄 요약>
- 🤝 <hash> <repo>: <양쪽이 함께 다룬 작업>

⏳ **진행 중 / 대기 중**
- last_recent_edit, 외부 처리 대기, 사람 응답 대기.

🚧 **블로커** (있다면)
- 사람이 해야 할 액션, 빠진 권한, 결정 필요한 것.

🎯 **다음 액션**
- 강대종님이 멈추라고 안 하면 바로 할 다음 한 가지.

📝 **할일** (~/todo/todos.md 진행중)
- 항목명만 짧게.
```

## 작성 가이드

- **시간 범위 = 오늘 KST 자정 이후** 로 통일. "이 세션", "이 세션 직전", "어제 ~~" 같은 표현 금지. 어제 작업은 출력 안 함.
- **양 기기 prefix 필수** — 🍎(Mac 본진) / 🪟(WSL) / 🏭(Mac mini 빌드 워커) / 🤝(공통/공유). 어느 기기 작업인지 한눈에.
- **commit hash + repo 박기** — 예: `🪟 a0c32f9 daejong-page: portfolio 카드 위치 고정 + 강조 표시`.
- **결과 중심** — "X 했어요" 가 아니라 "X 완료, 결과는 Y".
- **숫자/ID/경로** 정확하게.
- **추측 금지** — fetch 결과 없으면 빈 섹션. 모르는 건 안 적기.
- **스크롤 안 해도 한 화면**.
- launchd 백그라운드 자동화(asc-deliver, night-builder 등) 결과는 **본인이 직접 트리거한 게 아니면 ✅ 섹션에 안 적기** — 추측 막기 위해 `git log` 데이터에 잡힌 commit 만 써라.

## 호출 패턴

- `ctx` / `/ctx` → 위 형식 (오늘 KST, 양 기기 전체)
- `ctx 짧게` → 위 형식의 절반 분량
- `ctx 메모요` / `ctx 한줄일기` 등 → 해당 키워드 관련 항목만 필터링 (commit message + 진행중 todo grep)
