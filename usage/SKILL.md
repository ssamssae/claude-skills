---
name: usage
description: Claude Code 토큰 사용량을 ccusage 기반으로 ASCII 바 그래프로 보여준다. 현재 5시간 블록 진행률, 최근 블록 히스토리, 모델별 분포, 주/일별 합계를 한눈에 렌더링. 사용자가 "usage", "사용량", "토큰", "남은 한도", "블록", "번 레이트" 등을 이야기하거나 `/usage` 를 호출하면 이 스킬을 실행한다.
allowed-tools: Bash
---

# 토큰 사용량 그래프

## 데이터 소스

- `npx -y ccusage@latest blocks --json` : 5시간 빌링 블록 단위 집계 (JSON)
- `npx -y ccusage@latest weekly --json` : 주간 합계 (선택)
- `npx -y ccusage@latest daily --json` : 일별 합계 (선택)

## 호출 시 동작

1. **한 번의 Bash 호출로 모두 처리**. `ccusage blocks --json` 을 돌리고, 아래 파이썬 스크립트로 파싱·렌더링해서 stdout 으로 바로 출력한다. 중간 파일 만들지 말 것.

2. **출력 영역 (순서대로)**

   ### (A) 현재 활성 블록
   - `isActive: true` 인 블록 찾기. 없으면 "활성 블록 없음" 표시.
   - `totalTokens` / `limitRef` × 100 = 사용률 %. `limitRef` 는 "지금까지 관찰된 최대 블록 토큰"을 기준값으로 사용 (모든 non-gap 블록 중 max).
   - 경과 시간, 남은 시간, burn rate(분당 토큰), projection(전체 블록 예상치) 표시
   - ASCII 20칸 바: 사용분 `█`, 남은분 `░`

   ### (B) 최근 5시간 블록 히스토리 (최근 10개, gap 제외)
   - 각 블록 한 줄씩: `날짜 시간 | 바(20칸) | %  $비용  모델약칭`
   - 100% 는 ⚠️ 이모지 붙이기
   - 모델 약칭: opus-4-6→O, sonnet-4-6→S, haiku-4-5→H. 여러 개면 조합 (예: "OH")

   ### (C) 오늘 / 이번주 합계
   - 오늘: 오늘 날짜(KST, Asia/Seoul) 의 블록 합. 토큰 총량과 비용.
   - 이번주: ISO week 기준, 이번 주 월요일 00:00 부터 지금까지 블록 합.
   - 지난주 대비 증감 % 도 같이.

   ### (D) 모델별 분포 (이번주)
   - 이번 주 블록들에서 각 모델이 등장한 블록 수 및 추정 비용 비중을 ASCII 바로.

3. **주의**
   - ccusage 가 설치돼 있지 않을 수 있으니 항상 `npx -y ccusage@latest` 사용.
   - JSON 이 비어있거나 파싱 실패하면 명확한 에러 메시지 출력 후 종료.
   - 구독 한도(weekly quota) % 는 Anthropic 이 공개 API 로 안 뿌리므로 **절대 단정 짓지 말 것**. 5시간 블록 % 만 "관찰 최대값 대비 상대 사용률" 이라고 명시.
   - 터미널 색상: ANSI 사용 가능 (녹색 = 여유, 노랑 = 50%+, 빨강 = 80%+).

## 구현 템플릿

아래 한 방 Bash 명령으로 실행한다. 파이썬 스크립트는 heredoc 으로 직접 주입.

```bash
npx -y ccusage@latest blocks --json > /tmp/ccu_blocks.json 2>/dev/null && python3 <<'PY'
import json, datetime as dt, zoneinfo

data = json.load(open("/tmp/ccu_blocks.json"))
blocks = [b for b in data.get("blocks", []) if not b.get("isGap")]
if not blocks:
    print("사용 데이터 없음"); sys.exit(0)

KST = zoneinfo.ZoneInfo("Asia/Seoul")
limit_ref = max(b["totalTokens"] for b in blocks)  # 관찰된 최대 블록

def bar(pct, width=20):
    filled = int(round(pct/100 * width))
    filled = min(max(filled, 0), width)
    return "█"*filled + "░"*(width-filled)

def color(pct):
    if pct >= 80: return "\033[31m"   # red
    if pct >= 50: return "\033[33m"   # yellow
    return "\033[32m"                  # green
RESET = "\033[0m"

# (A) 활성 블록
active = next((b for b in blocks if b.get("isActive")), None)
print("\n📊 Claude Code 토큰 사용량\n")
if active:
    pct = active["totalTokens"] / limit_ref * 100
    start = dt.datetime.fromisoformat(active["startTime"].replace("Z","+00:00")).astimezone(KST)
    end = dt.datetime.fromisoformat(active["endTime"].replace("Z","+00:00")).astimezone(KST)
    now = dt.datetime.now(KST)
    elapsed = now - start
    remaining = end - now
    br = active.get("burnRate") or {}
    proj = active.get("projection") or {}
    print(f"⏰ 현재 블록 ({start:%H:%M}~{end:%H:%M} KST)")
    print(f"   {color(pct)}{bar(pct)}{RESET} {pct:5.1f}%  "
          f"({active['totalTokens']:>12,} / {limit_ref:,} 토큰)")
    print(f"   💰 ${active['costUSD']:.2f}   "
          f"경과 {elapsed.seconds//3600}h {(elapsed.seconds//60)%60}m / "
          f"남음 {remaining.seconds//3600}h {(remaining.seconds//60)%60}m")
    if br:
        print(f"   🔥 번 레이트: {br.get('tokensPerMinute',0):,.0f} tok/min")
    if proj:
        proj_pct = proj.get("totalTokens",0) / limit_ref * 100
        print(f"   📈 블록 종료시 예상: {proj_pct:.1f}%  (${proj.get('totalCost',0):.2f})")
else:
    print("⏰ 현재 활성 블록 없음")

# (B) 최근 10개 블록 히스토리
print("\n📅 최근 5시간 블록 (최근 10개)")
MODEL_ABBR = {"claude-opus-4-6":"O", "claude-sonnet-4-6":"S",
              "claude-haiku-4-5-20251001":"H", "claude-haiku-4-5":"H"}
recent = [b for b in blocks if not b.get("isActive")][-10:]
for b in recent:
    pct = b["totalTokens"] / limit_ref * 100
    start = dt.datetime.fromisoformat(b["startTime"].replace("Z","+00:00")).astimezone(KST)
    warn = " ⚠️" if pct >= 100 else ""
    mods = "".join(sorted({MODEL_ABBR.get(m,"?") for m in b.get("models",[])}))
    print(f"   {start:%m-%d %H:%M} {color(pct)}{bar(pct)}{RESET} "
          f"{pct:5.1f}%  ${b['costUSD']:6.2f}  [{mods}]{warn}")

# (C) 오늘/이번주 합계
today = dt.datetime.now(KST).date()
monday = today - dt.timedelta(days=today.weekday())
last_monday = monday - dt.timedelta(days=7)

def in_range(b, start_date, end_date):
    bd = dt.datetime.fromisoformat(b["startTime"].replace("Z","+00:00")).astimezone(KST).date()
    return start_date <= bd < end_date

today_blocks = [b for b in blocks if in_range(b, today, today + dt.timedelta(days=1))]
week_blocks = [b for b in blocks if in_range(b, monday, monday + dt.timedelta(days=7))]
last_week_blocks = [b for b in blocks if in_range(b, last_monday, monday)]

t_tok = sum(b["totalTokens"] for b in today_blocks)
t_cost = sum(b["costUSD"] for b in today_blocks)
w_tok = sum(b["totalTokens"] for b in week_blocks)
w_cost = sum(b["costUSD"] for b in week_blocks)
lw_tok = sum(b["totalTokens"] for b in last_week_blocks)
lw_cost = sum(b["costUSD"] for b in last_week_blocks)

def diff(cur, prev):
    if prev == 0: return "N/A"
    d = (cur-prev)/prev*100
    arrow = "▲" if d >= 0 else "▼"
    return f"{arrow}{abs(d):.0f}%"

print(f"\n📈 오늘 ({today})")
print(f"   토큰: {t_tok:>14,}   비용: ${t_cost:6.2f}   블록: {len(today_blocks)}개")
print(f"\n📈 이번주 ({monday} ~)")
print(f"   토큰: {w_tok:>14,}   비용: ${w_cost:6.2f}   블록: {len(week_blocks)}개")
print(f"   vs 지난주: 토큰 {diff(w_tok,lw_tok)}  비용 {diff(w_cost,lw_cost)}")

# (D) 모델별 분포 (이번주)
print(f"\n🤖 이번주 모델 분포")
model_cost = {}
for b in week_blocks:
    for m in b.get("models", []):
        model_cost[m] = model_cost.get(m,0) + b["costUSD"]/max(len(b["models"]),1)
total_c = sum(model_cost.values()) or 1
for m, c in sorted(model_cost.items(), key=lambda x:-x[1]):
    pct = c/total_c*100
    short = m.replace("claude-","").replace("-20251001","")
    print(f"   {short:<18} {bar(pct)} {pct:5.1f}%  (~${c:.2f})")

# (E) 플랜 한도 — claude.ai/settings/usage 스크레이핑
import subprocess, socket
host = socket.gethostname()
is_wsl = host.startswith("DESKTOP-") or host.startswith("WSL-")
try:
    if is_wsl:
        # WSL: SSH to Mac 본진 (Tailscale) — Mac 쪽 scrape.ts 가 profile/ 에 저장된 세션으로 실행
        plan_raw = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
             "user@100.74.85.37",
             "cd ~/.claude/scripts/claude-usage-scraper && ~/.bun/bin/bun run scrape.ts"],
            capture_output=True, text=True, timeout=90,
        )
    else:
        plan_raw = subprocess.run(
            ["/Users/user/.bun/bin/bun", "run", "/Users/user/.claude/scripts/claude-usage-scraper/scrape.ts"],
            capture_output=True, text=True, timeout=60,
            cwd="/Users/user/.claude/scripts/claude-usage-scraper",
        )
    if plan_raw.returncode == 0 and plan_raw.stdout.strip():
        plan_data = json.loads(plan_raw.stdout.strip())
        print(f"\n🎯 플랜 한도 ({plan_data.get('plan','?')})" + (" [via Mac SSH]" if is_wsl else ""))
        sess = plan_data.get("session") or {}
        wa = plan_data.get("week_all") or {}
        ws = plan_data.get("week_sonnet") or {}
        if sess.get("pct") is not None:
            p = sess["pct"]
            print(f"   현재 세션   {color(p)}{bar(p)}{RESET} {p:>3}%   ({sess.get('reset','')})")
        if wa.get("pct") is not None:
            p = wa["pct"]
            print(f"   주간 전체   {color(p)}{bar(p)}{RESET} {p:>3}%   ({wa.get('reset','')})")
        if ws.get("pct") is not None:
            p = ws["pct"]
            print(f"   주간 Sonnet {color(p)}{bar(p)}{RESET} {p:>3}%   ({ws.get('reset','')})")
    elif plan_raw.returncode == 2:
        print(f"\n🎯 플랜 한도: 스크레이퍼 미로그인. 한 번 수동 로그인 필요 (Mac):")
        print(f"   cd ~/.claude/scripts/claude-usage-scraper && HEADFUL=1 bun run scrape.ts")
    else:
        print(f"\n🎯 플랜 한도: 스크레이퍼 실패 (exit={plan_raw.returncode}). 상세: {plan_raw.stderr[:200]}")
except FileNotFoundError:
    if is_wsl:
        print(f"\n🎯 플랜 한도: ssh 미설치/경로 실패 — WSL 에서 'ssh user@100.74.85.37' 확인")
    else:
        print(f"\n🎯 플랜 한도: bun 미설치 — claude.ai Settings → Usage 수동 확인")
except subprocess.TimeoutExpired:
    print(f"\n🎯 플랜 한도: 타임아웃 (Mac 잠자는 중?) — Mac 깨우고 재시도")
except Exception as e:
    print(f"\n🎯 플랜 한도: 스크레이퍼 예외 {type(e).__name__}: {str(e)[:100]}")

print(f"\n⚠️  블록 % 는 '관찰된 최대 블록({limit_ref:,} tok)' 기준 상대값이고,")
print(f"    플랜 한도 % 는 claude.ai/settings/usage 실제 값입니다.\n")
PY
```

## 에러 핸들링

- `npx ccusage` 가 네트워크 문제로 실패하면 stderr 에 힌트 남기고 종료코드 1.
- 파이썬 `json.load` 실패 시: "ccusage 출력 파싱 실패" 안내.

## 출력 직후 할 일

- 추가 분석이나 조언은 사용자가 요청하지 않는 한 하지 말 것. 그래프만 그리고 끝.
- 사용자가 텔레그램 등 원격 채널에서 호출한 경우, 결과를 그대로 전달하면 된다 (이모지와 ASCII 바는 모바일에서도 잘 보임).
