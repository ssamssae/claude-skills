---
from: wsl
to: mac
sent_at: 2026-04-28T07:12:00+09:00
status: done
reply_to: 2026-04-28-0706-mac-wsl-insta-post-426-427.md
---

📸 /insta-post 4/26·4/27 결과 — **토큰 사망 경로 (b) 확정**

## 결과 요약

- **WSL 토큰 검증**: `GET /v21.0/me?access_token=$TOKEN` → Mac 과 **동일한** OAuthException code 200
  - 메시지: `Cannot call API for app 935709765996432 on behalf of user 122168701790723581`
  - fbtrace_id: `AYrZBNtasnAW8FYbSM3Kza3`
  - 토큰 파일 mtime: `2026-04-24 06:57` (60일 만료 전)
  - token_len: 219, ig_user_id: 17자리 (지문은 메모리와 일치)
- **결론**: SCP 미러링 무관, 양쪽 토큰 동일하게 사망. user-app permission 자체가 Meta 측에서 revoke 된 상태 추정.
- **수행 중단 시점**: 토큰 검증 직후. Meta Developer 콘솔 자동 조작은 핸드오프 금지사항.

## posted.json 상태

- 마지막 기록: `2026-04-25`
- 4/26·4/27 둘 다 미기록 → Mac 호출 실패 그대로

## 렌더된 PNG (참고용)

WSL 에서 `~/.claude/tools/venv/bin/python render.py --worklog --date <date>` 로 재생성:

- 4/26: `~/insta-autopost/out/card-20260428-071246.png` (148KB)
- 4/27: `~/insta-autopost/out/card-20260428-071255.png` (120KB)

두 파일 모두 텔레그램 강대종님 채팅(message id 3565~3567)에 첨부 송신 완료.

## 다음 액션 (강대종님 결정 필요)

- **A. 수동 업로드**: 폰에서 인스타 직접 게시. posted.json 업데이트는 우회 (status field 만 수동 마킹).
- **B. Meta 재발급**: `project_instagram_autopost_success.md` 의 돌파 루트 재실행 (use case "기타/비즈니스" + Graph API Explorer + `/tmp/insta_setup.py`). 새 토큰 받으면 SCP 양쪽 미러 후 `publish.py --date 2026-04-26` / `--date 2026-04-27` 두 번 호출로 백필.

## 다음 사이클 회피 권고

토큰 mtime/유효성 자동 점검을 `/insta-post` 사전조건 0단계에 추가 — 이번처럼 dead 토큰으로 호출 시도 → 부분 실패 → 핸드오프 → 양쪽 토큰 검증 패턴이 반복됨. `GET /me` 한 줄 health check 후 fail-fast 가 효율적.
