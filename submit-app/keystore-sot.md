# Android Release Keystore SoT Registry

Each app's Android **release upload keystore** Source of Truth — which device owns the `.jks` and performs release signing + Play Console API upload.

Used by `/submit-app` guard: before building/uploading, read this file, find the app, compare SoT to current hostname. If mismatch, refuse and redirect.

## Format

One line per app:
```
<app-name>: <🍎 Mac | 🪟 WSL> (keystore: <relative path from repo root>, created: YYYY-MM-DD)
```

## Registry

<!-- Keep sorted by app name. Add via /create-play-app or manual edit. -->

- dutch_pay_calculator: 🍎 Mac (keystore: `android/dutchpay-upload-keystore.jks`, created: 2025 이전)
- hanjul: 🍎 Mac (keystore: `android/hanjul-upload-keystore.jks`, created: 2026-04-25)
- hankeup: 🍎 Mac (keystore: `android/hankeup-upload-keystore.jks`, created: 2026-04-20)
- memoyo (simple_memo_app): 🍎 Mac (keystore: `android/memoyo-upload-keystore.jks`, created: 2025 이전)
- mini_expense: 🍎 Mac (keystore: `android/mini_expense-upload-keystore.jks`, created: 2026-04-20)
- pomodoro: 🍎 Mac (keystore: `android/pomodoro-upload-keystore.jks`, created: 2026-04-21)
- yakmukja: 🍎 Mac (keystore: `android/yakmukja-upload-keystore.jks`, created: 2025 이전)

## WSL 에도 keystore 가 있으면?

아래 앱은 WSL 쪽에도 `C:\src\<app>\android\*-upload-keystore.jks` 가 **남아있을 가능성** (2026-04-24 현재 미검증):
- pomodoro, hankeup, mini_expense (~/apps/ 계열은 원래 WSL 에서 시작)

권장 조치: WSL 에서 해당 파일을 **찾으면 rename** (`-obsolete-YYYYMMDD` suffix) 하고 절대 서명에 사용하지 말 것. 모든 release 서명은 이 registry 에 기재된 SoT 에서만 수행.

**⚠️ Keystore 교체는 Google Play 에서 허용 안 됨** (앱이 영구 락). 한 번 어느 keystore 로 업로드한 이상 그걸로만 이후 모든 업로드를 서명해야 함.

## 새 앱 등록

`/create-play-app <앱명>` 을 돌리면 자동으로 이 registry 에 append. 수동으로 append 할 수도 있음 (git push 로 양쪽 기기 동기화).

## 관련

- `/submit-app` §Step 0.5 — SoT 확인 가드
- 메모리 `multi_device_rules.md` 규칙 4 — Android 라우팅 nuance
