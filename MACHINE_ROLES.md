# 머신 역할표 + 위험 작업 블랙리스트

마지막 갱신: 2026-05-01 (KST) — WSL wsl/\* 브랜치 정책 + mail-watcher v5 드롭 반영
SoT(Source of Truth): 이 파일 자체 — 흩어진 룰의 통합본

## 1. 역할표 (한 줄 요약)

> **맥북은 운전대, Mac mini는 엔진.** 맥북에서 명령하고, Mac mini 에서 빌드·서명·자동배포 실행한다. WSL 은 낮 분석/Windows 게이트, iPhone 은 외출용 원격 헤드, 3060/3060Ti 는 온디맨드 GPU 실습/연구 노드.

| 머신 | 호스트 | 역할 | 가동 | 봇 |
|------|--------|------|------|----|
| 🍎 **Mac 본진** | `USERui-MacBookPro` | 운전대 / 지휘관 / SoT / 최종 결정 | 사실상 24/7 (집 데스크톱화) | `@MyClaude` |
| 🏭 **Mac mini** | `mac-mini` (M1, arm64) | 엔진 / 24/7 워커 / 빌드·서명·자동배포 | 진짜 24/7 | (워커, 챗봇 X) |
| 🪟 **WSL** | `DESKTOP-*` | 낮 즉응 작업자 + Windows 게이트웨이 | 낮 ON / 밤 OFF | `@Myclaude2` |
| 📱 **iPhone Termius** | (원격) | 외출용 원격 헤드 | 강대종님 동행 | — |
| 🎨 **데스크탑 3060Ti** | (SSH 원격) | 온디맨드 GPU 연구소 (LLM/SD/Whisper 실험) | 필요 시만 | — |
| 🧪 **노트북 3060** | (SSH 원격) | 온디맨드 실습실/샌드박스 (위험 자동화 실험, GPU 보조) | 필요 시만 | — |

**핵심 배제 규칙:**
- 3060Ti / 3060 노트북은 **상시 빌드/배포 역할 X.** 온디맨드 호출만.
- 인증서·키스토어·결제 키·App Store/Play 배포 권한은 **3060 류에 절대 X.**
- 본진(맥북) 이 SSH 로 호출할 때만 깨워서 GPU/실험 작업 수행.

### Mac 본진 (지휘관)

**한다:**
- Claude Code 메인 세션 (모든 설계/판단)
- 앱 방향/스코프 결정
- todos.md / done.md / worklog 쓰기 (SoT)
- App Store Connect / Play Console **최종 배포 버튼**
- GitHub PR 머지 결정
- 인증서/프로비저닝 프로파일 발급 (Apple Developer 포털)
- 위험 작업 사전 확인 응답

**안 한다:**
- 야간 자동 작업 (Mac mini 가 함)
- 무거운 빌드 반복 (Mac mini 가 함)

### Mac mini (엔진)

**한다:**
- iOS ipa 빌드 + codesign (`/submit-app` iOS 분기, ssh 라우팅 수신)
- Android aab 빌드 + 서명 + Play 배포 (2026-04-29 전담 결정)
- **자동 신규 앱 등록** (`/create-play-app` raw playwright 호출 수신, 2026-04-30 정비)
- **fastlane 자동 업로드** (App Store Connect / Play Publisher API)
- night-runner v1 (read-only 점검, 03:00 KST launchd)
- night-builder v2.0a (야간 자동 빌드)
- mac-report.sh / wsl-directive.sh 운반체 받는 쪽
- 키스토어 보관 (`~/apps/<app>/android/*-upload-keystore.jks`)
- **API key/Service Account/세션쿠키 보관** (`~/.claude/secrets/`, 2026-04-30 추가)
- raw Playwright + chromium (Mac mini 단독 자동화, MCP 의존 X)

**안 한다:**
- Claude Code 챗봇 세션 추가 (지휘관 1명 원칙)
- 앱 방향/스코프 결정
- 새 인프라 설계 판단
- 메타데이터/스크린샷 입력 (사람 클릭 — 강대종님 본진)
- 심사 제출 버튼 클릭 (사람 결정 — 강대종님 본진)

### WSL (낮 즉응 작업자)

**한다:**
- 낮 시간 즉응 작업 (강대종님이 WSL 머신 앞에 있을 때)
- **wsl/\* 브랜치 직접 개발자**: 코드/문서 수정 + commit + `git push origin wsl/<slug>` (2026-05-01 명시)
- 코드/로그 분석, 보고서 초안
- Windows ADB 게이트웨이 (Galaxy S24 무선 토글)
- WSL→Windows Chrome CDP (Playwright attach)
- 보고는 mac-report.sh 로 본진 라우팅

**안 한다:**
- **main 직접 push** (모든 main 반영은 Mac 본진이 검토·머지, 2026-05-01 명시)
- 야간 자동 작업 (밤 OFF)
- todos 직접 쓰기 (Mac 라우팅)
- 설계 변경/방향 변경/새 인프라 추가 제안 (지휘관 1명 원칙)
- 옵션 메뉴 surface ("뭐할래 1/2/3?" 금지)
- iOS 빌드 (Mac mini)
- Android aab 빌드/Play 배포 (Mac mini, 2026-04-29 결정)
- App Store Connect / Play Console 배포 클릭 (강대종님 본진)

### iPhone Termius (원격 헤드)

**한다:**
- 외출 시 SSH 로 본진/맥미니 원격 트리거
- 텔레그램 답변 receive

**안 한다:**
- 직접 빌드/배포 (트리거만, 실행은 항상 Mac 류)

---

## 2. 앱 배포 책임 분담

> **결정 (2026-04-29 23:42 KST):** "빌드도 배포도 Mac mini". 키스토어가 Mac mini 에 있고, 24/7 워커이며, night-builder v2.0a 풀그린이라 서명 일관성·자동화 SoT 모두 거기.

| 단계 | 자동화 (헤드리스) | 사람 클릭 (GUI) |
|------|-----------------|---------------|
| 코드 작성 / 버전 bump | — | 🍎 Mac 본진 (or 🪟 낮 WSL) |
| iOS ipa 빌드 + codesign | 🏭 Mac mini | — |
| Android aab 빌드 + 서명 | 🏭 Mac mini (keystore SoT) | — |
| 산출물 검증/리포트 | 🏭 Mac mini → 🍎 본진 (mac-report.sh) | — |
| App Store Connect 업로드 (Transporter/altool) | 🏭 Mac mini | 강대종님 (필요시 본진 GUI) |
| Play Console aab 업로드 (Publisher API) | 🏭 Mac mini | 강대종님 (필요시 본진 GUI) |
| 스크린샷/메타데이터 입력 | — | 🍎 Mac 본진 + 강대종님 |
| 심사 제출 버튼 | — (자동화 X, 책임 명확화) | 🍎 Mac 본진 + 강대종님 |
| 심사 결과 알림 receive | — (mail-watcher v5 2026-05-01 드롭) | 🍎 Mac 본진 ASC/Play 직접 모니터링 |
| 승인 후 출시 결정 | — | 🍎 Mac 본진 + 강대종님 |

**핵심 분리:** 
- 헤드리스 자동화 가능한 모든 빌드/업로드 = **Mac mini** (키스토어 SoT, 24/7)
- 사람 손이 필요한 GUI (메타·스크린샷·심사제출) = **강대종님** (대개 본진 앞에서)
- WSL/3060 류 머신에 빌드/배포 권한 절대 X
- **본진에 keystore 복사 X** — 자산 분산 = 노출 리스크 2배. Mac mini 만 SoT.

**기술적 근거:** 서명된 aab/ipa 는 self-contained. 빌드 시점에 keystore/codesign 으로 봉인되고 그 후엔 단순 파일 업로드. 즉 "Mac mini 가 빌드+업로드 하고, 본진은 GUI 클릭만" 이 자연스러운 분리.

---

## 3. 위험 작업 블랙리스트

### 🚫 절대 자동화 X (강대종님 사전 확인 필수)

- `rm -rf` 광역 (홈/repo 루트)
- `git push --force` to `main`/`master`
- `git reset --hard` (uncommitted 있을 때)
- `launchctl bootstrap` / `bootout` / `plist 이동` ([feedback_confirm_before_launchctl](projects/-Users-user/memory/feedback_confirm_before_launchctl.md))
- 광범위 `Stop-Process` / `pkill -9` ([feedback_no_broad_kill](projects/-Users-user/memory/feedback_no_broad_kill.md))
- `--no-verify` / `--no-gpg-sign` 훅 우회
- `App Store Connect` / `Play Console` 배포 버튼 자동 클릭
- IAP/결제 API key 노출/이동
- 운영 서버 (`prod-*`) 직접 수정
- 키스토어(`*.jks`) / `.p12` / `.p8` 파일 외부 송신
- `.env` / `credentials.json` git 커밋
- todos.md **하드 삭제** (취소/보류 섹션 이동만)
- 사용자 명시 없는 settings.json 수정 ([feedback_harness_self_modification_gate](projects/-Users-user/memory/feedback_harness_self_modification_gate.md))
- `Allow` 1회성 클릭으로 영구룰 만들었다고 주장 ([feedback_auto_mode_no_allow_prompt](projects/-Users-user/memory/feedback_auto_mode_no_allow_prompt.md))

### 🟡 사전 확인 권장 (저위험이지만 영향 큼)

- 새 launchd 잡 추가
- 새 자동화 스킬 추가 (먼저 폐지·드롭 grep 1번 — [feedback_check_existing_decisions](projects/-Users-user/memory/feedback_check_existing_decisions.md))
- 새 인프라 (LLM/SD/Whisper/Vision) 설치 — workflow 매핑 먼저 ([feedback_check_workflow_before_infra](projects/-Users-user/memory/feedback_check_workflow_before_infra.md))
- `git rebase` 공유 브랜치
- 큰 의존성 다운그레이드/제거
- `tmux kill-session` (강대종님 작업 세션 가능성)

### ✅ 자유 진행 OK (가역적, 로컬)

- 파일 편집/생성 (가역)
- `git pull` (로컬 fetch+merge)
- 테스트 실행
- 로그/메모리 grep
- 텔레그램 reply / mac-report / wsl-directive (운반체)
- 새 commit (push 는 별개 — 강대종님 룰: 끝나면 즉시 push 는 OK)

---

## 4. 라우팅 결정 트리

```
요청 들어옴
  │
  ├─ 🍎 태그 OR 본진 전용(배포/결정/메인 세션)? → Mac 본진
  ├─ 🪟 태그 OR Windows 게이트(ADB/CDP)? → WSL
  ├─ 🤝 태그? → 현재 머신
  └─ 태그 없음? → 본진 디폴트
  
빌드 작업?
  ├─ iOS → Mac mini (`/submit-app`)
  ├─ Android aab → Mac mini (`create-play-app` + `/submit-app`)
  └─ 단순 debug run → 현재 머신 (`/irun` `/arun` 으로 mac-mini SSH)

야간 자동 작업?
  └─ Mac mini 만 (launchd). WSL/본진 NO.
```

---

## 4.5 자동배포 라우팅 규칙 (2026-04-30 추가)

> **배포 명령은 맥북에서 시작하지만, 실행은 Mac mini 가 담당한다.**

### 호출 경로

```
🍎 본진 Claude Code 세션 (사람 트리거)
  ├─ /submit-app <앱명> --platform=android  → ssh mac-mini "fastlane supply ..."
  ├─ /submit-app <앱명> --platform=ios      → ssh mac-mini "fastlane pilot upload ..." or altool
  └─ /create-play-app <앱명>                → ssh mac-mini "node ~/.claude/automations/scripts/create-play-app.js ..."
```

스킬 SKILL.md 내부에서 모든 빌드/업로드/Playwright 단계는 `ssh mac-mini "..."` 로 라우팅. 본진 로컬에서 직접 fastlane/playwright 실행 X.

### 자산 배치

| 자산 | 보관 위치 | 본진 복사 X 이유 |
|------|---------|-----------------|
| Android keystore (`*.jks`) | Mac mini `~/apps/<app>/android/` | 분산 = 노출 리스크 2배. SoT 한 곳. |
| App Store Connect API key (`.p8`) | Mac mini `~/.claude/secrets/` | 위와 동일 |
| Google Play Service Account JSON | Mac mini `~/.claude/secrets/` | 위와 동일 |
| Google 세션 쿠키 (Playwright 용) | Mac mini `~/.claude/secrets/google-session.json` | 위와 동일 |

본진은 자산 0개. SSH 로 명령만 던지고 결과 받음.

### 사람 손이 필요한 부분 (자동화 X)

- App Store Connect / Play Console **신규 메타데이터/스크린샷 입력** → 강대종님 본진 브라우저
- **심사 제출 버튼** → 강대종님 본진 브라우저 (책임 명확화)
- 출시 결정/롤아웃 비율 → 강대종님 본진 브라우저
- API key/Service Account/세션 쿠키 **최초 발급** → 강대종님 본진 브라우저 → scp 로 Mac mini 전송

### 헤드리스 가능 / Playwright 필요 매트릭스

| 작업 | iOS | Android |
|------|-----|---------|
| 신규 앱 등록 | App Store Connect API (`POST /v1/apps`) — Playwright 불필요 | 공식 API 없음 → **Mac mini raw Playwright** |
| 빌드/서명 | xcodebuild/codesign — 헤드리스 OK | gradle + keystore — 헤드리스 OK |
| 업로드 | altool / fastlane pilot — 헤드리스 OK | fastlane supply (Publisher API) — 헤드리스 OK |
| 심사 메타·스크린샷 입력 | API 일부 + GUI 일부 → 강대종님 본진 | API 없음 → 강대종님 본진 |
| 심사 제출 | 자동화 X (책임) | 자동화 X (책임) |

### 3060Ti / 3060 노트북 — 온디맨드만

- 정기 잡 라우팅 X (launchd/cron 0)
- 본진이 SSH 로 호출 시에만 사용 (LLM/SD/Whisper/실험 빌드)
- 배포·서명·키스토어 권한 영구 X

## 5. 변경 시 갱신 규칙

이 파일은 **메모리/스킬/자동화 결정 변경 시 같이 갱신**. 흩어지면 의미 없음.

- 새 머신 편입 / 머신 드롭
- 빌드 라우팅 변경
- 배포 책임 이동
- 위험 작업 신규 발견

갱신할 때는 `마지막 갱신` 날짜도 같이 업데이트.

---

## 6. 참조

- `~/.claude/CLAUDE.md` — 빠른 컨텍스트
- `~/.claude/AGENT.md` — 상세 룰 (참고용)
- `~/.claude/projects/-Users-user/memory/MEMORY.md` — 자동 메모리 인덱스
- `~/.claude/projects/-Users-user/memory/multi_device_rules.md` — 3-way 운영 8개 규칙
- `~/.claude/projects/-Users-user/memory/project_commander_one_principle.md` — 지휘관 1명 원칙
