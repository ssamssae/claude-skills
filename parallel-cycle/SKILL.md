---
name: parallel-cycle
description: Mac M개 + WSL W개 + 맥미니 P개 작업을 병렬로 나눠 실행하고, 모두 끝나면 session-close 자동 호출. 트리거 "/parallel-cycle", "병렬 사이클", "N개씩", "N개 나눠서 해줘", "작업 나눠서 병렬로", "사이클 돌려줘".
allowed-tools: Bash, Write, mcp__plugin_telegram_telegram__reply
---

# parallel-cycle

## 기기 체크

Mac 본진 전용. WSL에서 호출 시 → "이 스킬은 본진 전용입니다. mac-report.sh로 본진에 요청해주세요." 안내 후 종료.

```bash
hostname  # USERui-MacBookPro* 이면 OK
```

## 0단계: 작업 자동 선택

**args 있으면** 파싱:
- `"N개씩"` 또는 `"N개"` 형태 → Mac N개 + WSL N개 목표 (todos + parking-lot 양쪽에서 자동 선택, 단 N개 미만이면 있는 만큼)
- 구체적 작업명 나열 → Mac / WSL 배분 명시 시 그대로, 아니면 순서대로 전반부 Mac / 후반부 WSL
- args 없으면 기본 Mac 3 + WSL 3

**todos + parking-lot 자동 선택 시:**

```bash
# 최신 todos 파일 읽기
TODOS_DIR="$HOME/daejong-page/todos"
LATEST=$(ls "$TODOS_DIR"/*.md 2>/dev/null | sort | tail -1)
PARKING="$HOME/daejong-page/todos/parking-lot.md"
EXCLUDE='HOLD\|강대종 직접\|실기기\|USB 연결\|손으로\|계약 만료\|사업자번호'
# 두 소스 병합 후 제외 필터
{ grep '^\- \[ \]' "$LATEST"; grep '^\- \[ \]' "$PARKING" 2>/dev/null; } | grep -v "$EXCLUDE"
```

선택 기준:
- todos + parking-lot **양쪽** 동시에 후보 발굴 (어느 한 쪽이 부족해도 다른 쪽으로 채움)
- `[ ]` 미완료 항목만
- HOLD / 강대종 직접 / 실기기 연결 / 사용자 물리 액션 / 외부 차단(계약 만료 등) 제외
- 🍎 prefix → Mac 우선, 🪟 prefix → WSL 우선, 🏭 prefix → 맥미니 우선, 🤝 → 부하 적은 쪽
- Mac: Playwright·ASC·GitHub 관련 / WSL: 코드·분석·디자인·문서 관련 / 맥미니: iOS·Android 빌드·배포·OpenClaw 관련
- 목표 N개 미만이면 있는 만큼만 진행 (고정 개수 불필요)

## 1단계: 시작 알림 (확인 없음)

텔레그램 1통 보내고 **즉시 2단계 진행** (OK 기다리지 않음):

```
🔀 병렬 사이클 시작 (HH:MM KST) — Mac M개 + WSL W개 + 맥미니 P개

🍎 Mac:
1. <Mac 작업1>
...

🪟 WSL:
N+1. <WSL 작업1>
...

🏭 맥미니 (SSH 실행):
N+W+1. <맥미니 작업1>
...

(멈추려면 "멈춰")
```

맥미니 작업 0개이면 해당 섹션 생략.

## 2단계: WSL 디렉티브 생성 + 발송 / 맥미니 작업 준비

`/tmp/parallel-cycle-wsl-directive.md` 생성 (작업 수 W개로 가변):

```markdown
# 병렬 사이클 WSL 작업 (W개)

**출처:** 본진 parallel-cycle 스킬  
**목표:** 아래 W개 작업 순서대로 완료. 강대종 손 0.

## 작업 목록

1. <WSL 작업1>
2. <WSL 작업2>
... (W개)

## 완료 보고 (필수, 2단계 모두 빠짐없이)

모든 작업 완료 후 **반드시 아래 순서 전부** 실행. 1만 하고 멈추지 말 것.

### 1. mac-report.sh 호출

```bash
cat > /tmp/parallel-cycle-wsl-done.md << 'EOF'
[PARALLEL-CYCLE-WSL-DONE]

WSL 완료 보고:
- 작업1: <결과 한 줄>
... (W개)
EOF

~/.claude/automations/scripts/mac-report.sh /tmp/parallel-cycle-wsl-done.md "WSL W개 완료"
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

(자동 /clear 진행합니다)
```

6. 텔레그램 전송 확인 후 자동 /clear:
```bash
sleep 2 && tmux send-keys -t claude "/clear" Enter
```

## 제약

- wsl/* 브랜치 사용, main 직접 push 금지
- store/* 수정 금지 (daejong-page todos/parking-lot 제외)
- 작업 시작/종료 텔레그램 보고
```

wsl-directive.sh -f /tmp/parallel-cycle-wsl-directive.md 호출.

맥미니 작업(P개)이 있으면 `/tmp/parallel-cycle-macmini-tasks.md` 에 작업 목록을 기록해 둔다 (3단계에서 SSH로 실행).

```bash
# P > 0 인 경우만 생성
cat > /tmp/parallel-cycle-macmini-tasks.md << 'EOF'
맥미니 작업:
1. <맥미니 작업1>
... (P개)
EOF
```

## 3단계: Mac 작업 실행 + 맥미니 SSH 실행

WSL 디렉티브 발송 직후, Mac 작업과 맥미니 SSH 작업을 순서대로 실행.

**맥미니 작업(P개)이 있으면** SSH로 먼저 실행:

```bash
# 각 맥미니 작업을 ssh mac-mini "..." 로 실행
# 작업 완료마다 하트비트: 💓 맥미니 N/P 완료: <작업명>
# SSH 실패 시 텔레그램 에러 알림 + Mac 작업으로 계속
```

SSH 실행 원칙:
- 맥미니 챗봇 세션 없음 → Mac이 `ssh mac-mini "<명령>"` 으로 직접 실행
- 맥미니 GitHub: SSH 인증 ✅ (HTTPS remote + osxkeychain). git pull/push 가능
- 빌드 결과물(ipa/aab)은 작업 특성에 따라 SCP로 가져오거나 맥미니 로컬 보관

**Mac 작업** 1→2→...→M 순서 실행.

각 작업 완료마다 하트비트: `💓 Mac N/M 완료: <작업명>`

전부 완료 후 상태 파일 저장:
```bash
echo '{"mac_done": true, "ts": "'$(date +%s)'"}' > /tmp/parallel-cycle-state.json
```

텔레그램:
```
🍎 Mac M개 완료. 🏭 맥미니 P개 완료. WSL 대기 중...
WSL 완료되면 자동으로 session-close 진행합니다.
```

맥미니 작업 0개이면 `맥미니 0개` 줄 생략.

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

🍎 Mac: 작업1 / 작업2 / ... 완료 (M개)
🪟 WSL: 작업N+1 / 작업N+2 / ... 완료 (W개)
🏭 맥미니: 작업X / 작업Y / ... 완료 (P개)   ← P=0이면 생략

session-close 진행합니다.
```

이후 session-close 스킬 절차 그대로 실행 (후속안 추출 → 텔레그램 → 컨펌 → 체크포인트 → "닫아도 OK").

## 에러 처리

- WSL 디렉티브 발송 실패 → 텔레그램 에러 알림, Mac 작업만 계속
- Mac 작업 중 하나 실패 → 텔레그램 에러 알림, 계속 vs 중단 확인
- WSL 30분 이상 무응답 → 텔레그램: "WSL 응답 없음, 수동 확인해주세요"
- 맥미니 SSH 실패 → 텔레그램 에러 알림 + 해당 작업 skip, 나머지 계속

---

v0.1 (2026-05-04): 초기 버전
v0.2 (2026-05-04): 0단계 자동화 — todos 자동 선택, 확인 제거, 시작 알림만 후 즉시 진행
v0.3 (2026-05-04): WSL session-close 추가 — mac-report.sh 직후 WSL도 자동 분류·저장·"클리어해도 됩니다"
v0.4 (2026-05-04): N개 유연 지원 — 3+3 고정 → M+W 가변. "N개씩" args 파싱, todos+parking-lot 발굴, 템플릿 M/W 변수화
v0.5 (2026-05-04): 자동 선택 소스 todos 단독 → todos + parking-lot 동시 병합. 어느 쪽이든 부족하면 다른 쪽으로 채움
v0.6 (2026-05-08): 맥미니 세 번째 참여자 추가 — 🏭 prefix 라우팅, SSH 직접 실행(챗봇 세션 없음), 0/1/3/5단계 반영
