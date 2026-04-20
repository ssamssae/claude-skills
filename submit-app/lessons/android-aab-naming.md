---
platform: android
severity: warning
category: build
first_hit: 2026-02-10
hits: 1
source: auto-from-session
---

# Android aab 파일명은 영문·하이픈만

## 증상
`memoyo-1.0.2+19.aab` 같은 `+` 나 한글 포함 파일명은 Play Console 업로드 시 500 에러 또는 fastlane supply 실패.

## 원인
Play Console 내부 파서가 일부 특수문자(`+`, `한글`) 에서 파일 경로를 제대로 못 읽는 케이스가 있음. CI/CD 툴(fastlane, supply) 도 동일 제약.

## 해결
aab 파일명을 `<앱명>-<버전>-<빌드번호>.aab` 형식으로 rename 해서 업로드.

예:
- ❌ `memoyo-1.0.2+19.aab`
- ❌ `메모요-1.0.2-19.aab`
- ✅ `memoyo-1.0.2-19.aab`

## 재발 방지 체크리스트
- [ ] 파일명에 영문·숫자·하이픈(-) 만 사용
- [ ] `+`, 한글, 공백 포함 금지
- [ ] 빌드 직후 `mv build/app/outputs/bundle/release/app-release.aab build/<앱명>-<ver>-<build>.aab` 자동화
- [ ] 버전 포맷은 `1.0.2-19` 가 아닌 `1.0.2+19` 지만 **파일명에서만** `+` 를 `-` 로 치환

## 참고
- pubspec.yaml 의 version 은 그대로 `1.0.2+19` 유지 (Flutter 표준)
- rename 은 업로드 직전에만
