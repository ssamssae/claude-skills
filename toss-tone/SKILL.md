---
name: toss-tone
description: Flutter 앱의 디자인을 Toss 톤으로 고도화. 레퍼런스 theme.dart(~/apps/hankeup/lib/theme.dart) 를 기준으로 타겟 앱의 theme.dart 를 머지하고, 화면 코드에서 토스 톤 위배 패턴(Colors.red/blue 등 하드코딩, 매직 넘버 패딩·반경, fontFamily 누락 TextStyle) 을 스캔·리포트한다. 강대종님이 "토스톤 입혀줘", "디자인 고도화", "toss-tone", "toss tone", "/toss-tone", "/toss-up" 이라고 하면 이 스킬을 실행.
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

# /toss-tone — Flutter 앱 Toss 톤 고도화

Pretendard + Toss 색상·반경·스페이싱 토큰 체계를 타겟 앱에 입힌다. 공장 템플릿 `~/apps/hankeup/lib/theme.dart` 를 Single Source of Truth 로 삼고, 타겟 앱의 부족한 토큰을 비파괴적으로 머지 + 리팩토링 포인트를 리포트한다.

## 호출 패턴

- `/toss-tone` — 현재 작업 디렉토리가 Flutter 프로젝트면 그 앱에 적용
- `/toss-tone <앱명>` — `~/apps/<앱명>` 대상으로 적용
- `/toss-tone <앱명> --check` — 수정 없이 진단만 (리포트만 출력)
- `/toss-tone <앱명> --apply-all` — 리포트된 자동 치환 가능한 항목 일괄 적용 (위험, 일반적으로 `--check` 후 선택적으로 수동 적용 권장)

## 전제

- 레퍼런스: `~/apps/hankeup/lib/theme.dart` (Pretendard + Toss 톤 + ColorScheme + TextTheme + ButtonTheme + BottomSheetTheme)
- Pretendard 폰트 에셋은 타겟 `pubspec.yaml` 에 등록돼 있거나, 플랫폼 기본 폰트로 fallback 되는 상황을 허용

## 절차

### 1. 타겟 해석

- args 없으면 `pwd` 를 확인 → `pubspec.yaml` + `lib/main.dart` 가 있으면 그 디렉토리 사용
- args 가 앱명이면 `~/apps/<앱명>` 사용
- `--check` 플래그 감지 → 쓰기 금지 모드
- `--apply-all` 플래그 감지 → 자동 치환 허용 모드

### 2. theme.dart 머지

```
REF="$HOME/apps/hankeup/lib/theme.dart"
TGT="<app>/lib/theme.dart"
```

- `$TGT` 없으면: `$REF` 내용을 복사해서 생성 (주석의 앱이름만 교체)
- `$TGT` 있으면: 토큰 단위로 diff
  - **AppColors**: 레퍼런스에 있는데 타겟에 없는 상수 → 타겟 AppColors 블록에 추가. 타겟의 기존 색상은 덮어쓰지 않음 (앱별 브랜드 컬러 보존).
  - **AppRadius / AppSpacing**: 레퍼런스와 동일 이름의 상수가 없으면 추가. 기존 값 유지.
  - **AppShadows** (선택): `ref` 에 존재하면 동일 규칙으로 머지
  - **buildTheme()**: 타겟에 없으면 레퍼런스 버전 통째로 추가. 있으면 손대지 않음 (앱별 커스텀 존중).
- 머지는 "추가만" — 기존 코드 라인을 바꾸지 않는다.

### 3. main.dart 배선 확인

`lib/main.dart` 에서:

- `import 'theme.dart';` (또는 `package:<app>/theme.dart`) 가 없으면 추가
- `MaterialApp(` 호출부에 `theme: buildTheme(),` 가 없으면 삽입 (`home:` 앞 라인)

이미 있으면 no-op.

### 4. 화면 코드 스캔 (lib/**/*.dart, theme.dart 제외)

Grep 으로 아래 패턴 찾아서 파일+라인 리스트 수집:

| 패턴 | 제안 |
|------|------|
| `Colors\.(red\|blue\|green\|grey\|gray\|black\|white)(?!.*Colors\.white)` | `AppColors.*` |
| `Color\(0x[0-9A-Fa-f]{8}\)` (theme.dart 외부) | 토큰 매칭 제안 |
| `BorderRadius\.circular\(\d+(\.\d+)?\)` | `AppRadius.*` |
| `EdgeInsets\.(all\|symmetric\|only)\([^)]*\b\d+(\.\d+)?\b` | `AppSpacing.*` |
| `SizedBox\((height\|width):\s*\d+` | `AppSpacing.*` |
| `TextStyle\(` without `fontFamily:` in same parenthesis block | `fontFamily: 'Pretendard'` 또는 `Theme.of(context).textTheme.*` |

`Colors.white` / `Colors.transparent` / `Colors.black26` 같은 의도적 사용은 허용 (경고 X).

### 5. 진단 리포트

모든 발견 항목을 카테고리별로 정리해서 출력:

```
📋 /toss-tone 진단 리포트 — <app>

✅ theme.dart: 머지 3개 토큰 추가 (AppShadows, labelXLarge, ...)
✅ main.dart: theme 배선 완료

⚠️ 수동 리팩토링 권장 (12건)
  · lib/screens/home_screen.dart:42  Color(0xFFEEEEEE) → AppColors.surface
  · lib/screens/home_screen.dart:58  BorderRadius.circular(16) → AppRadius.md
  · lib/screens/write_screen.dart:121 TextStyle 에 fontFamily 누락
  ...
```

### 6. 자동 치환 (--apply-all)

리포트된 항목 중 **안전한 것만** 치환:

- `Color(0xAABBCCDD)` 가 AppColors 토큰 16진값과 정확히 같으면 토큰으로 대체
- `BorderRadius.circular(8/12/16/20/24)` 는 `AppRadius.xs/sm/md/lg/xl` 로 대체
- `EdgeInsets.all(4/8/12/16/24/32)` 는 `AppSpacing.*` 로 대체
- `SizedBox(height/width: 4/8/12/16/24/32)` 도 동일

**치환 안 함**:
- `Colors.red` 류 (어느 톤으로 매핑할지 의도가 애매)
- 매직 넘버가 딱 AppSpacing 값과 안 맞는 경우 (예: `EdgeInsets.all(10)`)
- `TextStyle` 의 자동 재구조화 (깨질 위험)

### 7. 검증

```bash
cd <app> && fvm flutter analyze
```

분석 에러 발생 시 이전 상태로 롤백하고 원인 리포트.

### 8. 완료 보고

텔레그램 chat `538806975` 으로:
- 추가된 토큰 수
- 자동 치환 건수
- 수동 리팩토링 권장 건수 (상위 10건 나열)
- analyze 결과

## 안전 원칙

- 기존 AppColors 값 덮어쓰기 금지 (앱별 브랜드 컬러 보존)
- 기존 buildTheme() 덮어쓰기 금지 (앱별 커스텀 존중)
- `--apply-all` 없이 자동 치환 금지
- 치환 후 `flutter analyze` 실패면 자동 롤백
- theme.dart 자체는 스캔 대상에서 제외 (토큰 정의부는 원래 하드코딩)
- 커밋·푸시는 이 스킬에서 하지 않음 — 사용자가 결과 확인 후 별도 커맨드로 지시

## 확장 아이디어 (v2)

- 이모지/FontAwesome 외 토스가 쓰는 아이콘 세트 권장
- 다크 모드 ColorScheme 자동 생성
- `--haptic` 옵션: 모든 버튼/IconButton 에 HapticFeedback.lightImpact 자동 주입
- `--shadow` 옵션: 카드(Container with BoxDecoration)에 AppShadows.soft 자동 래핑
