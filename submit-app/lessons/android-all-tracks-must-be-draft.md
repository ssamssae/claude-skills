---
platform: android
severity: warning
category: release
first_hit: 2026-04-24
hits: 1
source: auto-from-session
---

# draft app 은 모든 트랙의 모든 릴리즈가 draft 여야 commit 통과

## 증상

포모도로(com.ssamssae.pomodoro) 1.0.0+6 을 alpha 트랙에 `--status draft` 로 올리는 흐름:

1. `edits.insert` ✅
2. `bundles.upload` ✅ (vc=6)
3. `edits.tracks().update(track="alpha", status="draft")` ✅ — 응답도 draft 로 echo
4. `edits.commit` ❌ 400 `"Only releases with status draft may be created on draft app."`

스크립트 auto-retry (`status=draft`) 도 동일 에러로 실패. 새 edit 을 열어도 같은 커밋 단계에서 막힘.

## 원인

해당 시점 Play Console 내부 트랙에 vc=3 status=**completed** 릴리즈가 남아있었음. 과거 업로드 시도들(beta precondition 실패, draft 상태 재시도 등) 중 어느 시점에 internal 로 vc=3 이 완료된 채 끼어있었음.

Play Developer API 의 `edits.commit` 은 **현재 edit 안의 모든 트랙/릴리즈 전체 상태를 validate**. "draft app" 상태의 앱은 하나의 non-draft 릴리즈도 허용하지 않음. 우리가 이번 edit 에서 건드리지 않은 internal 도 commit 단계에선 "현재 스냅샷의 일부"로 간주되어 같이 검사됨.

에러 메시지 "may be created" 는 오해 유발 — 실제로는 "may EXIST" 에 가까움.

## 해결

스크립트(`play-upload.py`) 의 기본 fallback 은 이 조합 케이스를 커버 못 함 (하나의 트랙·하나의 status 만 바꿈). 수동 파이썬으로 모든 non-draft 릴리즈를 draft 로 demote 한 뒤 commit 해야 통과:

```python
# 1. upload new aab (얻은 vc=N)
# 2. 기존에 completed 로 남아있는 release 를 전부 draft 로 demote:
service.edits().tracks().update(packageName=pkg, editId=eid, track='internal',
    body={"releases": [{"name": "3", "versionCodes": ["3"], "status": "draft"}]}).execute()
# 3. 새 릴리즈를 target 트랙에 draft 로:
service.edits().tracks().update(packageName=pkg, editId=eid, track='alpha',
    body={"releases": [{"name": str(vc), "versionCodes": [str(vc)], "status": "draft",
                        "releaseNotes": [{"language": "ko-KR", "text": "..."}]}]}).execute()
# 4. commit → OK
service.edits().commit(packageName=pkg, editId=eid).execute()
```

앱이 한 번 publish 된 이후부터는 이 제약 해제 (각 트랙 독립적으로 status 가질 수 있음).

## 재발 방지 체크리스트

- [ ] 신규 앱(= draft app) 업로드 시 `--status draft` 는 target 트랙 뿐 아니라 **기존 lingering completed 릴리즈도 전부 draft 로 demote** 해야 함
- [ ] 업로드 전 probe 에서 모든 트랙 순회(internal/alpha/beta/production) 해서 status≠draft 인 release 가 있으면 같이 demote 리스트에 추가
- [ ] `play-upload.py` 에 "draft app detected → all tracks demote" 옵션(`--demote-existing`) 추가 고려
- [ ] 앱이 publish 된 이후(최소 1개 트랙에 completed 로 라이브)부터는 이 로직 불필요 — 앱 publish 상태를 캐시해두면 편함

## 참고

- 관련 lesson: `android-draft-app-release-status.md` (단일 트랙 draft 재시도) + `android-beta-track-needs-testers.md` (testers 선행 조건) — 이 lesson 은 두 레슨의 조합 케이스
- 실패한 edit id: `08231519479274434153`, `07488784411631080250` (모두 discard)
- 성공한 edit id: `04724584959853325210` (vc=6 alpha draft commit)
