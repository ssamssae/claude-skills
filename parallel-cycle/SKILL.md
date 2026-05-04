---
name: parallel-cycle
description: Mac 3개 + WSL 3개 작업을 병렬로 나눠 실행하고, 둘 다 끝나면 session-close 자동 호출. 트리거 "/parallel-cycle", "병렬 사이클", "6개 나눠서 해줘", "작업 나눠서 병렬로", "사이클 돌려줘".
allowed-tools: Bash, Write, mcp__plugin_telegram_telegram__reply
---

# parallel-cycle

## 기기 체크

Mac 본진 전용. WSL에서 호출 시 → "이 스킬은 본진 전용입니다. mac-report.sh로 본진에 요청해주세요." 안내 후 종료.

```bash
hostname  # USERui-MacBookPro* 이면 OK
```

## 0단계: 작업 자동 선택

**args 있으면** 그대로 파싱 (순서대로 Mac 1-3 / WSL 4-6, 또는 사용자 배분 명시 시 그대로).

**args 없으면** todos에서 자동 선택:

```bash
# 최신 todos 파일 읽기
TODOS_DIR="$HOME/daejong-page/todos"
LATEST=$(ls "$TODOS_DIR"/*.md 2>/dev/null | sort | tail -1)
# [ ] 항목 중 HOLD 아닌 것 grep
grep '^\- \[ \]' "$LATEST" | grep -v 'HOLD\|강대종 직접\|실기기\|USB 연결\|손으로'
```

선택 기준:
- `[ ]` 미완료 항목만
- HOLD / 강대종 직접 / 실기기 연결 / 사용자 물리 액션 필요 항목 제외
- 🍎 prefix → Mac 우선, 🪟 prefix → WSL 우선, 🤝 → 부하 적은 쪽
- Mac: Playwright·ASC·GitHub 관련 / WSL: 코드·분석·디자인·문서 관련
- 적합한 항목이 6개 미만이면 있는 만큼만 진행 (3+3 고정 불필요)

## 1단계: 시작 알림 (확인 없음)

텔레그램 1통 보내고 **즉시 2단계 진행** (OK 기다리지 않음):

```
🔀 병렬 사이클 시작 (HH:MM KST)

🍎 Mac:
1. <Mac 작업1>
2. <Mac 작업2>
3. <Mac 작업3>

🪟 WSL:
4. <WSL 작업1>
5. <WSL 작업2>
6. <WSL 작업3>

(수정하려면 "멈춰" → 즉시 중단)
```

## 2단계: WSL 디렉티브 생성 + 발송

`/tmp/parallel-cycle-wsl-directive.md` 생성:

```markdown
# 병렬 사이클 WSL 작업

**출처:** 본진 parallel-cycle 스킬  
**목표:** 아래 3개 작업 순서대로 완료

## 작업 목록

1. <WSL 작업1>
2. <WSL 작업2>
3. <WSL 작업3>

## 완료 보고 (필수)

모든 작업 완료 후 순서대로:

### 1. mac-report.sh 호출

```bash
cat > /tmp/parallel-cycle-wsl-done.md << 'EOF'
[PARALLEL-CYCLE-WSL-DONE]

WSL 완료 보고:
- 작업1: <결과 한 줄>
- 작업2: <결과 한 줄>
- 작업3: <결과 한 줄>
EOF

~/.claude/automations/scripts/mac-report.sh /tmp/parallel-cycle-wsl-done.md "WSL 3개 완료"
```

### 2. WSL session-close (자동)

mac-report.sh 직후 바로 실행. 확인 없이 자동 진행:

1. 이번 WSL 작업에서 나온 후속안 식별 (대화 컨텍스트만)
2. daejong-page 최신화: `cd ~/daejong-page && git pull --ff-only`
3. 후속안 자동 분류·저장:
   - 활성 작업/트리거 → `todos.md` `## 진행중` 상단에 추가 (🪟 prefix)
   - 사이드 아이디어/언젠가 → `parking-lot.md` 끝에 추가
   - 일회성/인프라 튜닝 → drop (저장 X)
4. 변경 있으면: `git add -p && git commit -m "chore: WSL session-close 후속안" && git push`
5. 텔레그램 1통:

```
🪟 [hostname] [HH:MM KST] 세션 마무리

박힌 것:
- todos → <항목> (없으면 생략)
- parking-lot → <항목> (없으면 생략)
- 후속안 없음 (0건일 때)

/clear 진행하셔도 됩니다.
```

## 제약

- wsl/* 브랜치 사용, main 직접 push 금지
- store/* 수정 금지 (daejong-page todos/parking-lot 제외)
- 작업 시작/종료 텔레그램 보고
```

wsl-directive.sh -f /tmp/parallel-cycle-wsl-directive.md 호출.

## 3단계: Mac 작업 실행

WSL 디렉티브 발송 직후, Mac 작업 1→2→3 순서 실행.

각 작업 완료마다 하트비트: `💓 Mac N/3 완료: <작업명>`

전부 완료 후 상태 파일 저장:
```bash
echo '{"mac_done": true, "ts": "'$(date +%s)'"}' > /tmp/parallel-cycle-state.json
```

텔레그램:
```
🍎 Mac 3개 완료. WSL 대기 중...
WSL 완료되면 자동으로 session-close 진행합니다.
```

## 4단계: WSL 완료 감지 (새 턴에서)

mac-report.sh 신호가 이 세션에 들어오면 새 turn이 시작됨.

새 turn 입력에 `[PARALLEL-CYCLE-WSL-DONE]` 포함 여부 확인:
- 포함 → 5단계 진행
- 미포함 + `/tmp/parallel-cycle-state.json` 존재 → "아직 WSL 대기 중입니다." 안내 후 대기

상태 파일 정리:
```bash
rm -f /tmp/parallel-cycle-state.json /tmp/parallel-cycle-wsl-directive.md /tmp/parallel-cycle-wsl-done.md
```

## 5단계: 전체 완료 → session-close 자동 호출

텔레그램 1통:
```
✅ 병렬 사이클 완료 (HH:MM KST)

🍎 Mac: 작업1 / 작업2 / 작업3 완료
🪟 WSL: 작업4 / 작업5 / 작업6 완료

session-close 진행합니다.
```

이후 session-close 스킬 절차 그대로 실행 (후속안 추출 → 텔레그램 → 컨펌 → 체크포인트 → "닫아도 OK").

## 에러 처리

- WSL 디렉티브 발송 실패 → 텔레그램 에러 알림, Mac 작업만 계속
- Mac 작업 중 하나 실패 → 텔레그램 에러 알림, 계속 vs 중단 확인
- WSL 30분 이상 무응답 → 텔레그램: "WSL 응답 없음, 수동 확인해주세요"

---

v0.1 (2026-05-04): 초기 버전
v0.2 (2026-05-04): 0단계 자동화 — todos 자동 선택, 확인 제거, 시작 알림만 후 즉시 진행
v0.3 (2026-05-04): WSL session-close 추가 — mac-report.sh 직후 WSL도 자동 분류·저장·"클리어해도 됩니다"
