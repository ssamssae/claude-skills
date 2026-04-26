---
prevention_deferred: null
---

# review-status-check _disabled 이동 후 17h 동안 Apple issue 메일 누락

- **발생 일자:** 2026-04-25 00:44 KST (Apple 메일 도착) ~ 2026-04-26 17:55 KST (Mac Claude 가 Gmail 검색으로 발견)
- **해결 일자:** 2026-04-26 17:55 KST (발견·강대종님 알림). 실제 fix(ASC 사유 확인 + 재제출) 는 강대종님 ASC 콘솔 확인 후 별건
- **심각도:** high (App Store 제출 일정 + 사용자 신뢰 영향, 2개 앱 동시 영향)
- **재발 가능성:** high (forcing function 없음, _disabled/ 폴더의 다른 모니터링·알림 잡들 다 같은 위험)
- **영향 범위:** Mac 본진 launchd `com.claude.review-status-check`, 약먹자 1.0.1 (iOS), 더치페이 계산기 1.0.2 (iOS)

## 증상

Apple "There's an issue with your submission" 메일이 약먹자 + 더치페이 둘 다 2026-04-25 00:44 KST 에 도착했는데 강대종님이 17h 동안 모름. 자동 텔레그램 알림이 와야 했는데 안 옴. 17h 후 Mac Claude 가 이 세션에서 다른 작업("머하까" 발화에 옵션 #3 심사 메일함 점검) 으로 Gmail MCP 검색 돌렸을 때 비로소 가시화.

```
"During our review, we noticed an issue with your submission.
You can also view this information on the App Review page
in App Store Connect."
```

메일 본문은 보일러플레이트만 — 상세 사유는 ASC 콘솔의 App Review 페이지에서만 확인 가능.

## 원인

2026-04-21 토큰 절감 차원에서 `com.claude.review-status-check.plist` 가 `~/Library/LaunchAgents/_disabled/` 폴더로 이동된 채 그대로 비활성. 이동 자체는 의도적(memory `project_automation_disabled_2026_04_21.md` 명시)이지만 **비활성화의 영향**(메일 모니터링 멈춤 → Apple/Google 메일 시점 누락 가능성)을 추적하는 메커니즘이 없었음.

이동 후 며칠 동안 심사 메일이 한 건도 안 와서 누락 자체가 가시화되지 않았고, 첫 실 데이터(약먹자/더치페이 issue 메일 2건)가 와서야 "이거 알림 안 왔네" 인지 가능. 즉 "비활성화 → 침묵 모드 → 첫 알림 손실 시점에 비로소 가시화" 의 늦은 피드백 루프.

근본 원인은 **모니터링·알림 잡과 토큰 소비 잡을 같은 _disabled/ 바스켓에 넣은 것**. 이 둘은 비활성화 영향이 다른데 분류 갭이 없었음.

## 조치

즉시 (2026-04-26 17:55 KST):

1. Mac 본진 Gmail MCP 로 `(from:apple.com OR from:itunes.com) newer_than:3d` 검색해서 Apple issue 메일 2건 발견 (thread 19dc029ccd949d22 약먹자, 19dc02a354f22278 더치페이)
2. 메일 본문 FULL_CONTENT 로 fetch — 보일러플레이트만 있음 확인 (상세는 ASC 콘솔)
3. 텔레그램 reply 7685 로 강대종님께 보고
4. Task #6 (issue 사유 확인 + 재제출) + Task #7 (review-status-check 가벼운 모드 부활) 등록
5. 메모리 갱신 권고 (project_automation_disabled_2026_04_21.md 에 "Cost: review-status-check 끈 결과 17h 메일 누락" 한 줄) 를 WSL 핸드오프 reply 에 포함 (handoffs/2026-04-26-1801-mac-wsl-memory-cleanup-judgment-reply.md)

## 예방 (Forcing function 우선)

1. **맥미니 launchd 이전 시 review-status-check 가벼운 모드로 부활 강제** — Claude API 호출 0, Gmail grep + 키워드 매치 + 텔레그램 알림만. 토큰 비용 0 이라 토큰 절감 핑계로 다시 끄지 않게. Task #7 로 묶음, 맥미니 셋업과 짝. 24/7 가동 보장으로 폴링 누락 위험도 동시 해결.
2. **`_disabled/` 폴더 분류 게이트** — 모니터링·알림·헬스체크 잡은 `_disabled/` 가 아니라 별도 `_lite/` 폴더에 가벼운 모드 plist 형태로 보관. 이동 시 "이 잡이 외부 신호 모니터링이면 lite 모드 변환 필수, 단순 비활성화 금지" 룰 강제. (현재는 분류 없이 다 _disabled/ 에 들어감)
3. **morning-briefing 1-X 섹션에 "_disabled 폴더 + 마지막 활성 시점 + 재활성 검토" 행 추가** — 매일 아침 강대종님 폰에 비활성화 잡 목록 노출. 잊을 수 없게. 모니터링 잡이 며칠째 disabled 면 대시보드에서 빨갛게 보임.
4. **stop-check-repos-dirty.sh 훅에 _disabled/ 모니터링 잡 비교 추가** — 세션 끝날 때마다 review-status-check, morning-briefing 같은 알림성 잡이 disabled 상태면 경고. 기존 NOT LOADED 경고와 같은 자리에 새 줄.

## 재발 이력

(처음 생성 시 비워둠)

## 관련 링크

- 메일 thread: gmail `19dc029ccd949d22` (약먹자), `19dc02a354f22278` (더치페이)
- 비활성 plist: `~/Library/LaunchAgents/_disabled/com.claude.review-status-check.plist`
- 메모리: `project_automation_disabled_2026_04_21.md` (배경)
- 텔레그램 reply: id 7685 (보고), id 7687 (/issue 컨펌 요청)
- WSL 핸드오프 reply: `claude-skills/handoffs/2026-04-26-1801-mac-wsl-memory-cleanup-judgment-reply.md` (메모리 갱신 권고 포함)
- 관련 기존 이슈: `2026-04-21-launchd-silent-job-dropout.md` (메커니즘 다름 — 그건 launchctl silent fail, 이건 휴먼 의사결정 후속)
- Task: #6 (issue 사유 확인+재제출), #7 (가벼운 모드 부활)
