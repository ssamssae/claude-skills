# Android Release Keystore SoT Registry

Each app's Android **release upload keystore** Source of Truth — which device owns the `.jks` and performs release signing + Play Console API upload.

Used by `/submit-app` guard: before building/uploading, read this file, find the app, compare SoT to current hostname. If mismatch, refuse and redirect.

## Format

One line per app:
```
<app-name>: <🍎 Mac | 🪟 WSL> (keystore: <relative path from repo root>, created: YYYY-MM-DD, play_sha: <SHA-256 or "?" or "MISMATCH (...)">)
```

`play_sha` 는 Play Console 패키지 이름 등록 페이지에서 본 등록 SHA-256. 우리 SoT keystore 의 SHA 와 일치해야 함. 첫 등록 시 `?` 로 두고 `/submit-app` Step 0.4 통과한 시점에 채워넣을 것. SoT SHA 와 다르면 `MISMATCH (Play=<...>, SoT=<...>)` 로 표기 + 출시 차단.

## Registry

<!-- Keep sorted by app name. Add via /create-play-app or manual edit. -->

- dutch_pay_calculator: 🍎 Mac (keystore: `android/dutchpay-upload-keystore.jks`, created: 2025 이전, play_sha: ?)
- hanjul: 🍎 Mac (keystore: `android/hanjul-upload-keystore.jks`, created: 2026-04-25, play_sha: **MISMATCH** (Play=`05:CF…`, SoT=`F4:A7:E2:AA:C0:93:CE:B5:D5:AE:59:95:C7:77:2C:6C:BB:1D:C0:C6:12:04:36:B1:CF:01:C9:43:EC:B3:04:A3`))
  - ⚠️ 2026-04-28 19:39 KST 발견. Play 등록 키(05:CF…) 출처 불명, 비공개 키 분실 추정. 옵션 A(키 복원)/B(패키지 이름 변경)/C(보류) 결정 미정. lessons/android-play-package-already-registered.md 참조
- hankeup: 🍎 Mac (keystore: `android/hankeup-upload-keystore.jks`, created: 2026-04-20, play_sha: ?)
- memoyo (simple_memo_app): 🍎 Mac (keystore: `android/memoyo-upload-keystore.jks`, created: 2025 이전, play_sha: ?)
- mini_expense: 🍎 Mac (keystore: `android/mini_expense-upload-keystore.jks`, created: 2026-04-20, play_sha: ?)
- pomodoro: 🍎 Mac (keystore: `android/pomodoro-upload-keystore.jks`, created: 2026-04-21, play_sha: ?)
- yakmukja: 🍎 Mac (keystore: `android/yakmukja-upload-keystore.jks`, created: 2025 이전, play_sha: ?)

## WSL 에도 keystore 가 있으면?

아래 앱은 WSL 쪽에도 `C:\src\<app>\android\*-upload-keystore.jks` 가 **남아있을 가능성** (2026-04-24 현재 미검증):
- pomodoro, hankeup, mini_expense (~/apps/ 계열은 원래 WSL 에서 시작)

권장 조치: WSL 에서 해당 파일을 **찾으면 rename** (`-obsolete-YYYYMMDD` suffix) 하고 절대 서명에 사용하지 말 것. 모든 release 서명은 이 registry 에 기재된 SoT 에서만 수행.

**⚠️ Keystore 교체는 Google Play 에서 허용 안 됨** (앱이 영구 락). 한 번 어느 keystore 로 업로드한 이상 그걸로만 이후 모든 업로드를 서명해야 함.

## 새 앱 등록

`/create-play-app <앱명>` 을 돌리면 자동으로 이 registry 에 append. 수동으로 append 할 수도 있음 (git push 로 양쪽 기기 동기화).

## 관련

- `/submit-app` §Step 0 — SoT 확인 가드
- `/submit-app` §Step 0.4 — Play 등록 SHA vs SoT SHA 비교 (2026-04-28 신설)
- `lessons/android-play-package-already-registered.md` — hanjul 19:00 출시 사고 회고
- 메모리 `multi_device_rules.md` 규칙 4 — Android 라우팅 nuance
