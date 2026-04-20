---
platform: ios
severity: blocking
category: signing
first_hit: 2026-03-20
hits: 2
source: auto-from-session
---

# iOS DEVELOPMENT_TEAM 자동 주입 필수

## 증상
Flutter 가 새로 create 한 iOS 프로젝트는 `DEVELOPMENT_TEAM` 라인이 비어있거나(`""`) 아예 없음. 그대로 `/irun` 의 release 빌드 돌리면 signing 에러로 즉사:
> Signing for "Runner" requires a development team. Select a development team in the Signing & Capabilities editor.

## 원인
Xcode GUI 에서 팀을 선택하면 자동 주입되지만 CLI 에서 flutter run 만 돌리는 워크플로우에선 GUI 를 안 타므로 수동 주입 필요.

## 해결
`/land` 스킬 Step 6 이 자동으로 pbxproj 에 `DEVELOPMENT_TEAM = 46UH85U2B8;` 을 주입.
- 케이스 A: `DEVELOPMENT_TEAM = "";` → team ID 로 치환
- 케이스 B: `DEVELOPMENT_TEAM` 라인 자체가 없음 → `CODE_SIGN_STYLE = Automatic;` 바로 뒤에 추가
- 이미 다른 team ID 박혀 있으면 덮어쓰지 않음

## 재발 방지 체크리스트
- [ ] `/land` 스킬로 clone 후 세팅할 것 (수동으로 git clone → flutter run 금지)
- [ ] `grep DEVELOPMENT_TEAM ios/Runner.xcodeproj/project.pbxproj` 로 Team ID 확인
- [ ] Runner + RunnerTests(2개 config) 전부 = 46UH85U2B8 인지
- [ ] 다른 Apple 계정 쓸 거면 해당 repo pbxproj 수동 선점 편집 (이 스킬은 기존 team ID 덮어쓰지 않음)

## 참고
- `/land` SKILL.md Step 6
- Team ID `46UH85U2B8` = 강대종 개인 Apple Developer
