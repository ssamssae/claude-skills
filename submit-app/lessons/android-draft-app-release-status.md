---
platform: android
severity: warning
category: build
first_hit: 2026-04-21
hits: 1
source: auto-from-session
---

# "앱 초안" 상태의 앱은 release status 도 draft 여야 함

## 증상

약먹자 1.0.1+2 를 Play Developer API 로 internal 트랙에 업로드 시도 — aab 업로드는 성공하지만 `edits.commit` 단계에서 400 에러:

```
Only releases with status draft may be created on draft app.
```

요청 바디의 `releases[0].status` 를 기본값 `"completed"` 로 보냈던 게 원인.

## 원인

Play Console 에 등록된 앱이 아직 **"앱 초안 (draft app)"** 상태. 이 상태에서는 모든 릴리즈가 `draft` 상태로만 생성 가능 — 콘텐츠 등급·스토어 등록정보·데이터 보안 설문 등 필수 페이지가 아직 완료되지 않았기 때문.

앱이 한 번 publish 된 뒤(Internal 이라도 완료된 릴리즈 1개 있으면) 부터는 `"completed"` 가 정상 동작.

## 해결

`~/.claude/automations/scripts/play-upload.py` 에 자동 재시도 로직 내장:

```python
if "Only releases with status draft may be created on draft app" in msg and status != "draft":
    print(f"retrying with status=draft (app is in draft state)...")
    return upload_aab(service, package_name, aab_path, track, notes, status="draft")
```

결과적으로 스크립트 호출자는 앱 상태를 의식할 필요 없음. 첫 호출에서 `completed` 로 보내고, 400 뜨면 같은 edit 세션을 버리고 재시도하면서 `draft` 로 바꿔 성공.

## 재발 방지 체크리스트

- [ ] 신규 앱 업로드 시 `--status` 플래그 추가로 강제 지정하고 싶으면 `--status draft` 명시
- [ ] 스크립트에 자동 fallback 이 있으므로 기본적으로 사용자 개입 불필요
- [ ] 앱이 한 번 publish 되면 `completed` 로 다시 전환됨 (자동 복구)
- [ ] Play Console 웹에서 앱 초안 졸업(콘텐츠 등급·개인정보 등 설문 완료) 후 publish 되면 이 lesson 무효

## 참고

- `~/.claude/automations/scripts/play-upload.py` 의 `upload_aab()` 함수 안에 fallback 로직 있음
- 관련 API 문서: https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks (status enum)
- 첫 발견 시점: 2026-04-21 약먹자 1.0.1+2 업로드 (유일한 "앱 초안" 상태 앱이었음)
