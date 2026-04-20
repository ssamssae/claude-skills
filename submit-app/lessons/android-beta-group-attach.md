---
platform: android
severity: blocking
category: metadata
first_hit: 2026-04-20
hits: 1
source: manual
---

# Play Console 베타 트랙에 memoyo-beta-testers 그룹 붙이기

## 증상
Play Console 에 새 앱을 올린 후 Closed Testing 으로 검토를 제출했지만, daejong-page 에서 "베타테스터 등록" 한 사람이 해당 앱의 테스트 트랙에 자동 포함되지 않음.

## 원인
daejong-page 의 베타테스터 등록 폼은 `memoyo-beta-testers@googlegroups.com` Google Group 하나로 모든 등록을 받지만, Play Console 의 테스터 목록은 **앱별로 따로** 설정. 새 앱을 올리면서 해당 그룹을 테스터로 명시적으로 추가하지 않으면 그룹 멤버는 이 앱의 베타에 접근 불가.

## 해결
앱 출시 직전에 Play Console 에서 아래 수동 단계 실행:

1. Play Console → [앱 선택] → Testing → **Closed testing** (또는 Open testing)
2. 기본 트랙 (alpha) → **Manage track**
3. **Testers** 탭 → **Add Google Group** 버튼
4. `memoyo-beta-testers@googlegroups.com` 입력 → 저장
5. 해당 그룹이 테스터 섹션에 `✓` 상태로 표시되는지 확인

## 재발 방지 체크리스트
- [ ] Play Console 의 Closed/Open testing 트랙에 `memoyo-beta-testers@googlegroups.com` 추가됨
- [ ] 그룹이 "Active" 상태로 표시 (pending 상태면 Google Groups 에서 해당 그룹이 public 설정인지 확인)
- [ ] 테스터 opt-in URL 이 Play Console 에서 발급됨 (발급되면 daejong-page 등록 이메일에 포함 가능)
- [ ] 첫 베타 릴리즈 전 최소 1명이 opt-in 해서 다운로드 가능한지 smoke test

## 참고
- 공통 그룹 URL: https://groups.google.com/g/memoyo-beta-testers
- `issues/2026-04-16-play-console-testers-google-group.md` — Play Console testers API 가 개별 이메일을 받지 않고 Google Group 배열만 받는 이유
- daejong-page 에서 이 그룹에 자동 추가하는 Playwright 워커: `daejong-page/beta-signup/worker/`
