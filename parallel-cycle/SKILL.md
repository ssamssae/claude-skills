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

## 0단계: 작업 파싱

args에서 작업 목록 추출. 없으면 텔레그램으로 요청:

```
작업 6개를 알려주세요:
Mac 1:
Mac 2:
Mac 3:
WSL 1:
WSL 2:
WSL 3:
```

6개 미만이면 동일하게 요청. args로 왔으면 순서대로 Mac 1-3 / WSL 4-6 분리.

사용자가 직접 Mac/WSL 배분 명시하면 그대로 따름.

## 1단계: 플랜 공유 + 확인

텔레그램으로 1통:

```
🔀 병렬 사이클 플랜

🍎 Mac (내가 실행):
1. <Mac 작업1>
2. <Mac 작업2>
3. <Mac 작업3>

🪟 WSL (디렉티브 송신):
4. <WSL 작업1>
5. <WSL 작업2>
6. <WSL 작업3>

시작할까요? (OK / 수정: ...)
```

"OK" / "응" / "ㅇㅇ" → 2단계 진행. 수정 있으면 반영 후 재확인.

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

모든 작업 완료 후 mac-report.sh 반드시 호출:

```bash
# 보고서 파일 생성
cat > /tmp/parallel-cycle-wsl-done.md << 'EOF'
[PARALLEL-CYCLE-WSL-DONE]

WSL 완료 보고:
- 작업1: <결과 한 줄>
- 작업2: <결과 한 줄>
- 작업3: <결과 한 줄>
EOF

~/.claude/automations/scripts/mac-report.sh /tmp/parallel-cycle-wsl-done.md "WSL 3개 완료"
```

## 제약

- wsl/* 브랜치 사용, main 직접 push 금지
- store/* 수정 금지
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
