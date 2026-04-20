---
prevention_deferred: null
---

# /irun 재배포 시 "Could not run Runner.app" 반복 — 실제 원인은 아이폰 잠금

- **발생 일자:** 2026-04-20 20:48 KST
- **해결 일자:** 2026-04-20 20:51 KST
- **심각도:** medium
- **재발 가능성:** high
- **영향 범위:** `/irun` · `/land` 연쇄 호출 시 아이폰이 잠긴 상태로 책상에 있을 때 전부 재현됨.

## 증상

포모도로 앱 디자인 리팩 후 /irun 으로 재배포 → Xcode 빌드는 완료됐으나 "Installing and launching" 단계에서 실패:

```
Could not run build/ios/iphoneos/Runner.app on 00008150-0018459C2161401C.
Try launching Xcode and selecting "Product > Run" to fix the problem:
  open ios/Runner.xcworkspace

Error running application on 강대종의 iPhone (2).
```

기존 앱 uninstall → 재시도했는데도 같은 에러. Flutter 의 조언대로 Xcode 를 열어야 하나 의심하며 두 번 낭비.

## 원인

Flutter 가 출력한 메시지는 오탐이었다. 실제 원인은 **아이폰이 잠금 화면 상태였고**, devicectl 의 launch API 가 다음 에러로 거부됨:

```
The request was denied by service delegate (SBMainWorkspace) for reason:
Locked ("Unable to launch com.ssamssae.pomodoro because the device was not,
or could not be, unlocked").
FBSOpenApplicationErrorDomain error 7
```

- `xcrun devicectl device install app` 자체는 정상 성공 (앱은 폰에 올라감)
- `xcrun devicectl device process launch` 단계에서 잠금 거부
- Flutter 는 launch 실패를 "Could not run Runner.app — Xcode 에서 열어봐" 로 번역해 버려, 원인 규명이 어려움.

## 조치

1. `ls ~/apps/pomodoro/build/ios/iphoneos/Runner.app` 로 빌드 산출물은 정상 확인
2. `xcrun devicectl device install app ...` 직접 호출 → "App installed." 성공
3. `xcrun devicectl device process launch ... com.ssamssae.pomodoro` → 잠금 에러로 원인 확정
4. 사용자에게 텔레그램으로 "폰 잠금 풀고 아이콘 탭하면 새 디자인 보임" 안내
5. 이후 사용자가 폰 잠금 풀자 재 /irun 한 번에 Installing and launching 2.1초로 성공.

## 예방 (Forcing function 우선)

- `/irun` 스킬 Monitor grep 에 `"Could not run"` 패턴이 잡히면 **자동으로 devicectl launch 를 직접 호출** 하도록 폴백 추가:
  ```bash
  xcrun devicectl device process launch --device <uuid> <bundle-id> 2>&1 | tee /tmp/devicectl-launch.log
  ```
  stderr 에 `Locked` 포함이면 텔레그램으로 "폰 잠금 해제 필요" 알림을 즉시 보내고, 그렇지 않으면 실제 에러 내용을 그대로 전달.
- 추가 안전: /irun 실행 직전에 `xcrun devicectl device info connected --device <uuid>` 로 `unlocked` 상태도 함께 확인해 미리 안내.
- 즉시 적용 지점: `~/.claude/skills/irun/SKILL.md` 4~5 단계 사이에 "launch 실패 시 devicectl 직접 호출 + 잠금 감지" 분기 추가.

## 재발 이력

## 관련 링크

- 커밋: 없음 (/irun 스킬 개선은 별도 PR 예정)
- 메모리: 해당 없음
- 텔레그램 메시지: id 5361 (첫 실패 보고), id 5364 (원인 규명 보고), id 5373 (재시도 성공)
