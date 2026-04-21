---
platform: android
severity: warning
category: release
first_hit: 2026-04-21
hits: 1
source: auto-from-session
---

# beta/alpha (Closed Testing) 트랙은 testers 그룹이 붙어있어야 release 생성됨

## 증상

메모요(com.daejongkang.simple_memo_app) 에 1.0.4+21 을 `play-upload.py --track beta` 로 업로드 시도. 흐름:

1. `edits.insert` ✅
2. `bundles.upload` ✅ (versionCode 21 생성)
3. `edits.tracks().update(track="beta", ...)` ❌ 400 `"Precondition check failed"`

"draft app" 케이스(`status=draft` 로 재시도)가 아니므로 자동 fallback 도 해결 못 함 — 이 앱은 alpha/internal 에 completed 릴리즈가 이미 존재하는 정식 앱.

## 원인

해당 시점 beta 트랙에 **testers 그룹이 하나도 설정돼있지 않았음**. 구성 상태(read-only API probe):

```
production:  releases=0
beta:        releases=0   ← 여기에 push 시도
alpha:       releases=1 (1.0.3+20 completed)
internal:    releases=1 (1.0.0 vc 7 completed)
```

Google Play Developer API 는 closed testing 트랙(alpha/beta/custom closed track)에 release 생성을 하려면:

- 해당 트랙에 최소 1개의 tester group(Google Groups URL) 혹은 이메일 리스트가 enrolled 돼 있어야 함
- 그렇지 않으면 `tracks.update` 가 400 Precondition check failed 로 거부

Play Console 웹 UI 는 이 단계를 강제로 통과시켜주지만 API 는 그 사전조건이 미충족이면 그냥 precondition 으로 튕김. 에러 메시지가 구체적이지 않아서 debugging 이 까다로움.

## 해결

3가지 선택:

1. **Play Console 웹에서 beta 트랙에 testers 추가** (testers → email list 또는 Google Group 연결) → 이후 API 호출 성공
2. **이미 testers 설정된 다른 트랙 사용** (예: 해당 앱에서 alpha 가 이미 활성이면 alpha 로 전환) — 단 이건 **유저 인지 없이 스크립트 레벨에서 자동 전환 금지**. 사용자 명시적 승인 필요.
3. **Internal 트랙으로 먼저 올리고 Play Console 에서 promote** — internal 은 가장 덜 까다로움

스크립트 레벨에서 자동 복구는 불가능 — Play Console 웹 구성이 필요.

## 재발 방지 체크리스트

- [ ] 신규 앱이든 기존 앱이든 **beta/alpha 처음 사용 전**에 Play Console 웹에서 해당 트랙 Testers 섹션 확인 → 최소 1개 그룹/이메일 리스트 assigned 된 상태로 만들어놓기
- [ ] API 업로드 실패 시 확인 순서: (1) "draft app" 이면 `status=draft` fallback (자동, 이미 반영), (2) closed testing 트랙이면 테스터 그룹 유무 확인 (수동)
- [ ] 업로드 전 현재 트랙 상태를 한 번 조회하는 read-only probe 를 스크립트 `--check` 옵션으로 추가 고려 (tracks.list + 해당 트랙 testersGroup 여부 리포트)

## 참고

- 실패한 edit id 들: `13927638567206975897`, `05944931482355980367` (둘 다 discard 됨, 영구 영향 없음)
- 관련 스크립트: `~/.claude/automations/scripts/play-upload.py`
- 해당 스크립트의 `tracks.update` 400 "Precondition check failed" → `status=draft` 재시도 fallback 은 이 케이스에는 안 맞지만, 실제 draft app + closed track 조합에는 유효하므로 유지
