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
