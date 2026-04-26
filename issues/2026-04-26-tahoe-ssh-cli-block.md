---
prevention_deferred: null
---

# macOS Tahoe 26.x: systemsetup -setremotelogin 이 Full Disk Access 부족으로 차단

- **발생 일자:** 2026-04-26 23:46 KST
- **해결 일자:** 2026-04-26 23:54 KST
- **심각도:** low
- **재발 가능성:** medium
- **영향 범위:** 24/7 자동화 허브 셋업, macOS 26.x 헤드리스 SSH 활성화

## 증상

M1 맥미니 (macOS Tahoe 26.4.1) 셋업 중 Ghostty 터미널에서:

```
sudo systemsetup -setremotelogin on
Password:
setremotelogin: Turning Remote Login on or off requires Full Disk Access privileges.
```

sudo 비번 통과 후에도 Full Disk Access (FDA) 권한 없는 터미널 앱은 SSH 데몬을 CLI 로 켤 수 없음. 24/7 자동화 허브 셋업 흐름에서 SSH 활성화 단계가 막힘.

## 원인

macOS Ventura (13+) 부터 강화된 권한 모델 — 시스템 변경 명령 일부가 호출 터미널 앱에 FDA 권한 요구. Ghostty 같은 새 설치 터미널은 FDA 미부여 상태로 출고. macOS Tahoe (26.x) 에서도 동일 또는 강화된 정책. CLI 자동화 차단됨.

근본 원인은 보안 정책 강화이며, 회피책은 (a) 터미널 앱에 FDA 부여 (시스템 설정 > 개인정보 보호 및 보안 > 전체 디스크 접근 → Ghostty 추가 → 토글 ON) 또는 (b) GUI 로 직접 SSH 켜기. 후자가 단계 적음.

## 조치

시스템 설정 > 일반 > 공유 > **원격 로그인** 토글 ON 으로 GUI 우회. 다이얼로그 자동 통과. SSH 데몬 정상 활성화. 본진 Mac → 맥미니 SSH 검증 PASS (`hostname`=mac-mini, `whoami`=user, arch=arm64, macOS=26.4.1).

## 예방 (Forcing function)

1. **메모리 reference 신규** — `reference_macos_setremotelogin_gui_only.md` 작성. 다음 24/7 자동화 머신 셋업 가이드 시 자동 참조.
2. 룰: macOS 26.x 헤드리스 SSH 활성화 = **GUI 토글 only**. CLI `systemsetup -setremotelogin` 시도 금지 (FDA 부여 절차 추가하느라 오히려 시간 더 듦, 새 터미널 앱 설치 후엔 항상 FDA 미부여 상태이기 때문).
3. 미래에 24/7 자동화 허브 셋업 스킬화 시 (`24-7-hub-setup` 또는 유사) 위 룰을 step 명시.

## 재발 이력

## 관련 링크

- 텔레그램 메시지: id 7820 (셋업 중 분석 + GUI 가이드)
- 메모리: `reference_macos_setremotelogin_gui_only.md` (신규)
- 본진 Mac → 맥미니 SSH 검증 PASS 시점: 2026-04-26 23:54 KST
- 셋업 컨텍스트: 진접 본가 → 공덕 픽업 후 M1 맥미니 16GB 24/7 자동화 허브 합류 (라파5 → M1 0원 대체)
