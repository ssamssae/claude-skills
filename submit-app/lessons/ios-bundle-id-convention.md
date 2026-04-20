---
platform: ios
severity: blocking
category: signing
first_hit: 2026-03-20
hits: 1
source: auto-from-session
---

# iOS Bundle ID 는 com.ssamssae.<name> 고정

## 증상
Flutter 가 다른 기기(WSL 등)에서 `--org com.example` 로 create 된 경우 `com.example.<name>` 으로 박혀있어 `/irun` release 빌드가 provisioning profile 매칭 실패로 죽음.

## 원인
강대종님 Apple Developer 계정(Team 46UH85U2B8) 에는 `com.ssamssae.*` prefix 의 App ID 만 자동 생성 가능하게 세팅됨. 다른 Bundle ID prefix 는 수동 App ID 생성 필요.

## 해결
- `/land` 스킬의 Step 4-1 이 자동으로 `com.example.*` → `com.ssamssae.<name>` 치환
- 이미 `com.ssamssae.*` 박혀있으면 no-op
- 의도적으로 다른 org 쓰는 앱은 건드리지 않음 (com.example.* 패턴만 매칭)

## 재발 방지 체크리스트
- [ ] `ios/Runner.xcodeproj/project.pbxproj` 의 PRODUCT_BUNDLE_IDENTIFIER 가 `com.ssamssae.<name>` 인지 확인
- [ ] Runner + RunnerTests 블록 3개 모두 일괄 치환됐는지 (테스트 타겟 누락 주의)
- [ ] Flutter create 시 `--org com.ssamssae` 명시
- [ ] 새 앱 생성 시 Bundle ID 충돌 없는지 App Store Connect 에서 확인

## 참고
- `/land` SKILL.md Step 4-1
