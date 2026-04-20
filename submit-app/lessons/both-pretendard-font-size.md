---
platform: both
severity: info
category: build
first_hit: 2026-04-10
hits: 1
source: manual
---

# Pretendard 폰트 번들 시 앱 용량 +~3MB

## 증상
Toss 톤 디자인(Pretendard 폰트) 적용된 앱은 `pubspec.yaml` 의 `fonts:` 섹션에 Pretendard 9 weights 등록하면 앱 용량이 base 대비 약 3MB 증가. iOS 용량 제한(200MB over-the-air) 이나 Android Dynamic Feature 분할에 영향 가능.

## 원인
Pretendard-Regular.otf ≈ 350KB, 9 weights 전부 번들하면 3MB+. Flutter 는 사용하는 weight 만 tree-shake 하지 않으므로 `pubspec.yaml` 에 선언된 weight 는 전부 들어감.

## 해결
- **추천**: Pretendard 의 Regular / Medium / SemiBold / Bold 4개만 번들. ExtraBold / Black 등은 제거.
- 또는 Variable Font(.ttf) 버전 사용 — 1MB 미만으로 줄어듦 (Pretendard Variable: https://github.com/orioncactus/pretendard/releases)
- 시스템 폰트 fallback 이 충분하면 번들 생략

## 재발 방지 체크리스트
- [ ] `flutter build appbundle --analyze-size` 로 앱 용량 확인
- [ ] 번들하는 weight 가 실제 코드에서 쓰이는 것뿐인지 검토
- [ ] Variable font 사용 가능한지 확인 (Pretendard-Variable.ttf)
- [ ] 첫 빌드 후 aab/ipa 용량을 lesson 하단에 기록

## 사이즈 히스토리
- hankeup 1.0.0: aab 8.1MB (weights 4개 번들)
- 메모요 1.0.0: aab 12.4MB (9 weights 번들, 이후 축소 권장)
