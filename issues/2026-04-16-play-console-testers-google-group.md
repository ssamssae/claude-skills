---
prevention_deferred: null
---

# Play Console testers API 가 개별 이메일을 받지 않음

- **발생 일자:** 2026-04-16
- **해결 일자:** 2026-04-16
- **심각도:** medium (베타 테스터 자동 추가 블로킹)
- **재발 가능성:** low (Google 정책 변경 없으면 고정)
- **영향 범위:** 메모요 사전예약 자동 등록 파이프라인

## 증상
Play Console REST API 의 `edits.testers` 에 이메일 배열을 넣어 개별 테스터를 추가하려 했는데, API 가 해당 형식을 받지 않고 400 으로 내려침. 문서에는 ""emails": ["..."]" 가 있어 보였지만 실제 엔드포인트에서는 수용되지 않는 필드였음.

## 원인
해당 REST API 는 설계상 **Google Group 배열만 받음**. 개별 이메일을 받으려면 Play Console UI 에서 수동으로 넣어야 하고, API 자동화 경로로는 그룹을 통해 간접 추가하는 것이 의도된 흐름.

## 조치
- Google Groups 에 전용 그룹(`memoyo-testers`) 생성
- API 는 그룹 이메일만 `edits.testers.googleGroups` 로 전달
- 개별 사전예약자는 Google Group 멤버 추가(Playwright) 를 거쳐 자동으로 테스트 트랙에 포함되는 흐름으로 재설계
- 이 흐름을 `project_memoyo_beta_auto_add` 메모리로 박아 재발 방지

## 예방 (Forcing function 우선)
- Play Console/Firebase 쪽 Google API 는 "개별 이메일" 입력을 기본으로 기대하지 말고 **그룹 경유 설계** 를 디폴트로 간주. 새로운 자동화 시작 전에 "이 API 는 그룹만 받는가?" 질문을 체크리스트에 포함.
- 메모리에 "Play Console testers API = googleGroups 배열만" 규칙 고정. 관련 자동화 스크립트 상단 주석으로도 표기.

## 재발 이력
_(없음)_

## 관련 링크
- 메모리: project_memoyo_beta_auto_add.md
- 작업일지: docs/worklog/2026-04-16
