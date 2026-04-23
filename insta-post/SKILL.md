---
name: insta-post
description: 오늘(또는 지정 날짜) worklog 를 1080×1350 인스타 텍스트 카드 PNG 로 렌더해 텔레그램으로 보낸다. 반자동 — 렌더·전송까지만 하고 업로드는 강대종님이 폰에서 수동. 사용자가 "인스타", "인스타 카드", "인스타 포스팅", "/insta-post" 라고 하면 이 스킬을 실행.
---

# /insta-post — worklog → 인스타 텍스트 카드 PNG → 텔레그램

## 목적

`~/daejong-page/worklog/<date>_v*.md` 의 H1·첫 `>` 블록을 파싱해 토스톤 인스타 카드 PNG 한 장을 만들고 텔레그램으로 보낸다. 강대종님이 폰에서 이미지 long-press → 인스타 앱 수동 업로드. API 제한·계정 정지 리스크를 회피하는 반자동 파이프라인.

## 언제 호출되는가

- 강대종님이 "인스타 뽑아줘", "오늘 인스타 카드", "/insta-post", "/insta-post 2026-04-20" 이라고 할 때
- 사이드 프로젝트·앱 출시 같은 하이라이트 데이가 있을 때
- `worklog` 스킬 실행 직후 이어서 호출 가능 (파일만 있으면 됨)

## 절차

1. `$ARGUMENTS` 가 `YYYY-MM-DD` 형식이면 그 날짜, 아니면 오늘(`date +%F`).
2. `~/daejong-page/worklog/<date>_v*.md` 파일이 있는지 확인. 없으면 "오늘 worklog 가 아직 없습니다 — `/worklog` 먼저 실행하세요" 로 중단.
3. 렌더:
   ```bash
   source ~/.claude/tools/venv/bin/activate
   python3 ~/insta-autopost/render.py --worklog --date <date>
   ```
   stdout 마지막 줄이 PNG 절대 경로.
4. 텔레그램 `reply` 툴로 해당 PNG 를 `files: [...]` 에 넣어 chat_id=538806975 로 전송. 본문은 한 줄 + "업로드 하실 때 인스타에 올리면 되는 카드입니다" 수준.
5. 같은 응답에서 `~/insta-autopost/out/` 의 이전 5일 이상 PNG 는 조용히 cleanup (용량 관리).

## 옵션 확장

- `$ARGUMENTS` 가 `"<title>|<hook>"` 형태면 worklog 파싱 우회하고 직접 렌더:
  ```bash
  python3 ~/insta-autopost/render.py --date <date> --title "<title>" --hook "<hook>"
  ```
- 앞으로 Graph API 완전 자동 업로드가 필요해지면 `project_instagram_autopost` 메모리의 A안(크리에이터 전환 + Meta Graph) 으로 전환. 현재 MVP 는 반자동.

## 디자인 규칙

- 폼팩터: 1080×1350 (4:5 세로, 피드·프로필 기본)
- 배경: 화이트 `#FFFFFF`, 본문 `#191F28`, 부텍스트 `#4E5968`
- 악센트: `#3182F6` (토스 블루)
- 폰트: Pretendard (CDN 자동 로드)
- 로고: 텍스트 풋터 `@ssamssae · daejong-page`

톤 변경은 `~/insta-autopost/templates/card.html` 직접 수정. 레퍼런스는 daejong-page 자체.

## 실패 시

- `playwright` import 실패: `source ~/.claude/tools/venv/bin/activate && playwright install chromium`
- 카드에 글자 깨짐: 폰트 로드 실패 — `wait_for_timeout` 을 1200 → 2500 으로 늘림
- 훅이 비어있음: worklog 에 `>` 블록이 없을 수 있음 — 강대종님에게 수동 `--title/--hook` 입력 요청

## 구조

```
~/insta-autopost/
├── render.py              # Playwright 렌더러
├── templates/card.html    # 토스톤 HTML 템플릿
└── out/                   # 생성 PNG (cleanup 대상)
```

스킬은 이 얇은 껍데기 — 실제 로직은 render.py 한 파일에.
