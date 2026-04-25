---
name: insta-post
description: 오늘(또는 지정 날짜) worklog 를 1080×1350 인스타 텍스트 카드 PNG 로 렌더해 Instagram Graph API 로 개인 인스타 피드에 완전 자동 업로드한다. 사용자가 "인스타", "인스타 올려", "인스타 카드", "인스타 포스팅", "/insta-post" 라고 하거나, 텔레그램 채팅에 "📸 /insta-post 핸드오프" 메시지가 들어오면 (Mac→WSL 자동 라우팅) 이 스킬을 실행.
---

# /insta-post — worklog → 토스톤 카드 PNG → 인스타 피드 (완전 자동)

## 목적

`~/daejong-page/worklog/<date>_v*.md` 의 H1·첫 `>` 블록을 파싱해 토스톤 인스타 카드 PNG 를 만들고, daejong-page GitHub Pages 로 호스팅한 뒤 Instagram Graph API 로 개인 계정(크리에이터) 에 자동 포스팅한다.

## 언제 호출되는가

- 강대종님이 "인스타 올려줘", "인스타 뽑아줘", "오늘 인스타 카드", "/insta-post", "/insta-post 2026-04-20" 이라고 할 때
- 사이드 프로젝트·앱 출시 같은 하이라이트 데이가 있을 때
- `worklog` 스킬 실행 직후 이어서 호출 가능
- **Mac→WSL 자동 핸드오프**: WSL 채널에 "📸 /insta-post 핸드오프" 로 시작하는 메시지가 들어오면 (Mac /goodnight step 4.5 가 송신) WSL Claude 가 메시지의 "날짜:" 라인을 파싱해 `/insta-post <YYYY-MM-DD>` 호출. 강대종님 발화 없어도 인식

## 사전 조건

### 기기 정책 (2026-04-25 결정, A 옵션)

**🪟 WSL 만 평소 호출 경로.** Mac 은 비상용으로만 살림 (WSL 멈춤 / 강대종님 Mac 에 있을 때). 이유는 posted.json 동기화 충돌 막기 위함 — 한 쪽이 SoT 고 다른 쪽은 잠자는 백업.

- 일상 호출: WSL `@Myclaude2` 가 받음
- **/goodnight step 4.5**: WSL hostname 이면 Skill tool → insta-post 직접 호출. Mac hostname 이면 텔레그램으로 WSL 한테 자동 핸드오프 directive 송신. WSL Claude 가 그 메시지 인식하고 `/insta-post <date>` 호출. 강대종님이 Mac 만 켜도 인스타 올라가는 흐름 유지 (정책 A 의 핵심)
- Mac 에서 강대종님이 "맥에서 인스타 올려" 라고 직접 발화하면 Mac 직접 호출도 가능. 이 경우 호출 직후 WSL 에 SCP 로 posted.json 회수 (수동)

### 기기 가드 (가장 먼저)

시크릿(`~/.claude/secrets/instagram.json`) 은 **git 동기화 제외**. WSL + Mac 양쪽에 동일 사본 (2026-04-25 SCP 미러링). Mac 에서 호출되면:

1. `test -f ~/.claude/secrets/instagram.json` 로 확인
2. 없으면 🍎 Mac 에 시크릿 미러링이 깨진 것 — 텔레그램으로 안내:
   ```
   📸 /insta-post Mac 시크릿 사본이 없습니다. WSL 에 호출 넘기는 게 정답.
   ```
3. 사용자가 "WSL 로 옮겨" 라고 하면 `/handoff` 스타일로 WSL 에 "/insta-post <date>" 트리거 directive 송신 후 종료.
4. 있으면(→ WSL 이거나 대종님이 이미 복사) 아래 절차로 진행.

### 토큰 (완전 자동 경로)

`~/.claude/secrets/instagram.json` 에 장기 토큰 + IG Business Account ID 가 있어야 함:

```json
{"access_token": "<60일 장기 토큰>", "ig_user_id": "<17자리 IG biz id>"}
```

없으면 "토큰이 없습니다 — project_instagram_autopost_success 메모리의 돌파 루트 먼저 끝내야 완전 자동 가능" 로 중단하고 **임시 폴백**으로 PNG 만 렌더 후 텔레그램 첨부 전송(구 반자동 모드).

### 의존성 (Python venv)

`~/.claude/tools/venv/bin/python` 가 실 호출 경로. publish.py 는 stdlib(json/urllib/subprocess) 만 쓰고 render.py 가 Pillow + playwright 를 씀. **최소 세트:**

```bash
~/.claude/tools/venv/bin/pip install Pillow playwright
~/.claude/tools/venv/bin/playwright install chromium
```

- Pillow: 카드 PNG 후처리 (리사이즈/포맷 변환)
- playwright: 토스톤 HTML → PNG 렌더 (chromium 번들 필요)
- requests / python-dateutil: **불필요** (publish.py 가 urllib 으로 직접 호출)

새 기기에 미러링 시 위 두 줄만 돌리면 됨. SCP 직후 가드 #0 에서 자동 점검.

검증 명령 (설치 직후 또는 의심날 때):

```bash
~/.claude/tools/venv/bin/python -c "import PIL; from playwright.async_api import async_playwright; from importlib.metadata import version; print(f'PIL={PIL.__version__} playwright={version(\"playwright\")}')"
```

⚠️ playwright Python pkg 는 `__version__` 속성을 노출하지 않음. `importlib.metadata.version()` 으로 우회 (2026-04-25 Mac 검증에서 발견).

## 절차

1. `$ARGUMENTS` 가 `YYYY-MM-DD` 형식이면 그 날짜, 아니면 오늘(`date +%F`).
2. **가드 #0 — venv 점검**: `~/.claude/tools/venv/bin/python` 존재 확인. 없으면 즉시 텔레그램으로 알림 후 중단:
   ```
   ⚠️ /insta-post 중단 — ~/.claude/tools/venv 없음. 위의 "의존성 (Python venv)" 두 줄로 설치해주세요.
   ```
   자동 호출(/goodnight step 4.5 등)에서도 이 알림이 채팅에 떠야 그날 인스타 누락을 바로 알 수 있음.
3. **가드 #1 — worklog 존재 체크**: `~/daejong-page/worklog/<date>_v*.md` 파일 확인. 없으면 텔레그램으로 알림 후 중단:
   ```
   📭 /insta-post 중단 — <date> worklog 가 없습니다. /worklog 먼저 돌려주세요.
   ```
   사용자 호출이면 같은 메시지로 회신, 자동 호출이면 텔레그램 reply 1회 송신. 어느 쪽이든 그날 누락 사실이 채팅에 남게 함 (4/24 사례 재발 방지).
4. **가드 #2 — 시크릿 점검**: `~/.claude/secrets/instagram.json` 존재 확인. 없으면 위의 "기기 가드" 흐름으로 분기 (Mac/WSL 안내). 자동 호출이면 텔레그램에 "🔐 /insta-post 중단 — 시크릿 없음, [기기명] 에서는 호출 불가" 송신.
5. **가드 #3 — 중복 포스트 체크**: `~/insta-autopost/posted.json` 에 같은 `<date>` 가 있으면 기존 permalink 출력하고 중단. 사용자가 "그래도 다시 올려" 라고 하면 `--force` 플래그로 재실행. (이건 누락이 아니라 정상 — 텔레그램 알림 불필요, 채팅 회신만)
6. 카드 렌더:
   ```bash
   ~/.claude/tools/venv/bin/python ~/insta-autopost/render.py --worklog --date <date>
   ```
7. 캡션 준비: H1 title + 첫 hook 한 줄 + 해시태그(`#바이브코딩 #클로드코드 #Flutter #1인개발자 #앱개발`). 필요 시 편집.
8. 인스타 발행 (`--date` 는 publish.py 내부 dedup 가드용 — 중복 방지 레일 두 겹):
   ```bash
   URL=$(python3 ~/insta-autopost/publish.py --png "$PNG" --caption "$CAPTION" --date "<date>" | tail -1)
   ```
   publish.py 가 자동으로:
   - posted.json 에 `<date>` 있으면 즉시 중단 (가드 #3 와 중복 보호 layer)
   - daejong-page/insta-host/ 에 PNG 커밋·푸시
   - GitHub Pages 퍼블릭 URL 200 대기
   - Graph API `/media` 컨테이너 생성 → status_code=FINISHED 대기
   - `/media_publish` 로 최종 게시 → permalink 반환
   - posted.json 에 `{date, permalink, published_at}` append
9. 텔레그램 `reply` 로 결과 전송:
   - 성공: "인스타 업로드 완료 → `<permalink>`" + PNG 썸네일 첨부
   - 실패: 에러 메시지 + PNG 첨부(수동 업로드 폴백 가능하게)
10. `~/insta-autopost/out/` 의 5일 이상 PNG cleanup.

## 옵션 확장

- `$ARGUMENTS` 가 `"<title>|<hook>"` 형태면 worklog 파싱 우회:
  ```bash
  python3 ~/insta-autopost/render.py --date <date> --title "<title>" --hook "<hook>"
  ```
- 드라이런(렌더만, 업로드 없이): `/insta-post --dry` — render.py 만 실행하고 텔레그램에 첨부만 전송.

## 디자인 규칙

- 폼팩터: 1080×1350 (4:5 세로, 피드·프로필 기본)
- 배경: 화이트 `#FFFFFF`, 본문 `#191F28`, 부텍스트 `#4E5968`
- 악센트: `#3182F6` (토스 블루)
- 폰트: Pretendard (CDN 자동 로드)
- 로고: 텍스트 풋터 `@ssamssae · daejong-page`

톤 변경은 `~/insta-autopost/templates/card.html` 직접 수정. 레퍼런스는 daejong-page 자체.

## 실패 시

- `playwright` import 실패: `source ~/.claude/tools/venv/bin/activate && playwright install chromium`
- 카드 글자 깨짐: 폰트 로드 실패 — `wait_for_timeout` 1200 → 2500 으로 늘림
- 훅 비어있음: worklog 에 `>` 블록 없음 — 수동 `--title/--hook` 입력 요청
- Graph API 403 `OAuthException`: 토큰 만료(60일) — 재발급 후 `~/.claude/secrets/instagram.json` 갱신
- Graph API `(#100)` image_url not reachable: GitHub Pages 배포 지연 — `wait_public` 타임아웃 180s 에서 안 되면 수동으로 URL HEAD 확인
- `media` status_code=ERROR: 이미지 비율(4:5) 또는 크기(최대 8MB) 위반 — render.py 가 1080×1350 으로 이미 맞추지만 포맷 문제면 PNG → JPG 변환 고려

## 구조

```
~/insta-autopost/
├── render.py              # Playwright 렌더러 (PNG 생성)
├── publish.py             # 호스팅 + Graph API 2-step publish
├── templates/card.html    # 토스톤 HTML 템플릿
└── out/                   # 생성 PNG (cleanup 대상)

~/daejong-page/insta-host/ # GitHub Pages 호스팅 폴더 (publish.py 가 커밋)
~/.claude/secrets/instagram.json  # 장기 토큰 + IG biz id
```

스킬은 얇은 껍데기 — 실제 로직은 render.py + publish.py 에.
