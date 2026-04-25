---
date: 2026-04-24
host: WSL → Mac mirror
status: resolved-2026-04-25
related: project_instagram_autopost_success
---

# 4/24 인스타 자동 포스팅 누락 — Mac 호출 시 시크릿/인프라 부재

## 발생

2026-04-24 일자 /insta-post 호출이 Mac 세션에서 시도됐을 때 가드 fail. 원인 분석 (Mac directive msg 2565 KST 12:23):

- `~/.claude/secrets/instagram.json` 만들어진 곳: WSL `/home/ssamssae/.claude/secrets/instagram.json` (Apr 24 06:57, 274 bytes, 0600).
- `~/insta-autopost/` repo: WSL `/home/ssamssae/insta-autopost/` (render.py, publish.py, posted.json, GET_TOKEN.md, out/, templates/, .git).
- Mac 본진은 둘 다 없음 (Mac 사전 점검에서 MISSING 확인).
- `/insta-post` SKILL.md 의 가드는 시크릿 존재 + worklog 존재 두 겹 → Mac 에서 시크릿 없으면 즉시 abort.

→ 이날 인스타 포스팅이 자동으로 안 올라갔음. 강대종님이 다음 날 발견.

## 해결 (2026-04-25 13:45 KST, WSL → Mac 미러링)

Mac directive (msg 2565) 기반 WSL `@Myclaude2` 가 SCP 로 미러링 수행:

### 1) 사전 검증

```
$ ls -la ~/.claude/secrets/instagram.json
-rw------- 1 ssamssae ssamssae 274 Apr 24 06:57 ...

$ ls -la ~/insta-autopost/
GET_TOKEN.md  out  posted.json  publish.py  render.py  templates  .git  .gitignore
```

WSL 양쪽 정상.

### 2) Mac 측 사전 점검

```
$ ssh user@100.74.85.37 'ls -la ~/.claude/secrets/instagram.json'
ls: /Users/user/.claude/secrets/instagram.json: No such file or directory

$ ssh user@100.74.85.37 'if [ -d ~/insta-autopost ]; then echo EXISTS; else echo MISSING; fi'
MISSING
```

둘 다 없으니 백업 불필요.

### 3) 시크릿 SCP

```
$ scp -p ~/.claude/secrets/instagram.json user@100.74.85.37:~/.claude/secrets/instagram.json
$ ssh user@100.74.85.37 'ls -la ~/.claude/secrets/instagram.json'
-rw------- 1 user staff 274 Apr 24 06:57 /Users/user/.claude/secrets/instagram.json
```

`-p` 옵션으로 0600 모드 보존됨. 별도 chmod 600 불필요. 시크릿 내용은 텔레그램·로그·터미널 stdout 어디에도 echo/cat 안 함.

### 4) insta-autopost 폴더 SCP

```
$ scp -rp ~/insta-autopost user@100.74.85.37:~/
$ ssh user@100.74.85.37 'ls ~/insta-autopost/'
GET_TOKEN.md
out
posted.json
publish.py
render.py
templates
```

posted.json 양쪽 동기화 시점: **2026-04-25 13:45 KST** (이 SCP 직후, WSL 의 4/24 마지막 상태 그대로 Mac 에 복사). 이후 양방향 동기화 정책은 다음 turn 결정 사항.

### 5) Mac 측 venv 체크

```
$ ssh user@100.74.85.37 'ls ~/.claude/tools/venv/bin/python 2>/dev/null && echo VENV_OK || echo VENV_MISSING'
VENV_MISSING
```

⚠️ **Mac 측 Pillow/requests venv 미설치** — `~/.claude/tools/venv/bin/python` 부재. /insta-post SKILL.md 가 이 절대경로를 호출하므로 Mac 에서 실행하려면 venv setup 필요. 다음 turn 후속 작업.

## 미러링 검증 상태

- ✅ Mac 시크릿 미러링 (0600 모드 보존)
- ✅ Mac insta-autopost 폴더 미러링 (.git 포함, 모든 핵심 파일 도착)
- ⚠️ Mac venv MISSING — Pillow + requests 설치 필요 (다음 turn)
- ⏸ posted.json 양방향 동기 정책 — 미정 (다음 turn)
- ⏸ 토큰 만료 ~2026-06-23 (60일) 알림 자동화 — 미정

## 다음 액션 후보

1. Mac 측 `~/.claude/tools/venv` 생성 + Pillow/requests/python-dateutil 설치
2. posted.json 동기화 정책: WSL 이 SoT 인가, 양쪽 commit 시 git push/pull 인가, ~/insta-autopost 자체를 git remote 로 묶을 것인가
3. 토큰 만료 D-7 알림 자동화 (현재 GET_TOKEN.md 수동 절차)
4. /insta-post SKILL.md 의 시크릿/folder 부재 가드 fail 시 텔레그램 즉시 보고 (그날 누락 모르고 지나가는 것 방지)

## Mac venv setup 진행 (2026-04-25 13:50 KST)

WSL → Mac 인계 directive (msg 6979) 기반 Mac `@MyClaude` 가 7단계 진행. 결과 부분 PASS + finding 1건.

### 사전 검증 (step 1-2)

- /sync exit=0, claude-skills b260ead 도착, issue 파일 받음
- `~/.claude/secrets/instagram.json` 274 bytes 0600 확정 (cat 안 함)
- `~/insta-autopost/` 6개 핵심 파일 + .git + .gitignore 모두 도착

### venv + 의존성 (step 3-4)

```
$ python3 -m venv ~/.claude/tools/venv
$ ~/.claude/tools/venv/bin/python -V
Python 3.13.5
$ ~/.claude/tools/venv/bin/pip install --upgrade pip
pip 25.1.1 → 26.0.1
$ ~/.claude/tools/venv/bin/pip install Pillow requests python-dateutil
$ ~/.claude/tools/venv/bin/python -c "import PIL, requests, dateutil; print(...)"
Pillow=12.2.0 requests=2.33.1 dateutil=2.9.0.post0
```

✅ directive 최소 세트 import 검증 PASS.

### dry-run SKIP — finding: render.py 추가 의존성 (step 5)

`~/.claude/tools/venv/bin/python render.py --help` 시도 결과:

```
ModuleNotFoundError: No module named 'playwright'
```

원인: render.py L21 `from playwright.async_api import async_playwright` — directive 가 명시한 최소 세트(Pillow/requests/dateutil)에 누락. 그 외 추가 발견:

- publish.py 는 stdlib 만 사용 (json + urllib.request + subprocess), 추가 패키지 불필요. WSL directive 가 명시한 `requests` 도 사실 publish.py 코드상 미사용
- chromium 번들은 Mac 표준 위치 `~/Library/Caches/ms-playwright/chromium-1217/` 에 이미 존재 (Playwright MCP 가 2026-04-16 깔아둠) → Python playwright 도 같은 번들 재사용 가능, 별도 다운로드 불필요

render.py 에 `--dry-run` 옵션 부재 (`--date / --title / --hook / --worklog / --output` 만). directive 룰 "render.py 가 dry-run 모드 미지원이면 step 4 import 검증 통과만으로 PASS 처리하고 publish.py 호출은 절대 하지 말 것" 에 따라 step 5 **SKIP**. publish.py 미호출.

### 현재 상태

- ✅ venv 생성 + pip 26.0.1
- ✅ Pillow/requests/python-dateutil import PASS
- ⚠️ render.py 추가 의존성 finding: `playwright` Python pkg 미설치 → 현재 상태로는 /insta-post 호출 시 또 ModuleNotFoundError
- ✅ chromium 번들 기존 활용 가능 (추가 다운로드 0)
- ⏸ /insta-post 양방향 호출 가능 여부: 강대종님 결정 후 추가 작업 1건 필요

### 강대종님 결정 대기

A) `~/.claude/tools/venv/bin/pip install playwright` 추가 설치 → render.py 실 dry 호출 (--title "smoke" --hook "test" --output ~/insta-autopost/out/dummy.png) 로 PNG 1080×1350 검증 → 정리 → /insta-post 양쪽 그린

B) /insta-post SKILL.md 의 의존성 정의 갱신 (Pillow/requests/dateutil + playwright) — WSL directive 보강 따로 필요

A 가 1단계로 끝남 (chromium 번들 재사용으로 다운로드 비용 0).
