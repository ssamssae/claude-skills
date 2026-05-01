---
prevention_deferred: null
---

# Substack backfill 이 Ep5 원본 prose 를 덮어씀 — 컨벤션 두 갈래 공존

- **발생 일자:** 2026-04-30 23:45 KST (50c5ad4 커밋 시점)
- **해결 일자:** 2026-05-01 20:50 KST (이슈 등록 시점, 데이터 원복 X)
- **심각도:** medium
- **재발 가능성:** high (다음 ep 도 substack-first 면 같은 사고)
- **영향 범위:** daejong-page newsletter 파이프라인 / naver-blog-publish / ep<N> 원본 prose 보존

## 증상

2026-05-01 20:39 KST 강대종님이 네이버 블로그에 EP1~5 일괄 발행을 시도하던 중, EP4·EP5 가 `ep<N>-<DATE>.md` 원본 파일이 없고 `ep<N>-substack.md` 만 있는 걸 발견. EP5 의 경우 15:59 KST 에 `ep5-substack.md` 에 ~3500자 본문이 commit (6eacc7f) 됐었지만, 23:45 KST 에 sync_from_substack.py 가 같은 파일에 backfill 결과를 덮어써 원본 prose 가 substack→markdownify 변환본으로 치환됨. 결과적으로 git history 에는 두 버전이 남았지만 working tree 의 "원본"은 사라짐.

## 원인

ep<N> 파일 컨벤션이 두 갈래로 공존:

- Ep1~3: `ep<N>-<DATE>.md` (로컬 원본, 외부 발행 sync 가 안 건드림)
- Ep4~5: `ep<N>-substack.md` (substack-first 편집본 = 원본인데, sync_from_substack.py 가 cacheFile 로 같은 이름을 쓰고 덮어씀)

sync_from_substack.py 가 cacheFile 위치를 분리하지 않은 채 도입되면서, "편집본 파일명 = 캐시 파일명" 충돌이 발생.

## 조치

이번 사이클에서는 데이터 원복 안 함 (git history 에 6eacc7f 로 원본 보존돼 있어서 필요 시 cherry-pick 가능). 강대종님이 추천 A+C 동시 채택 → 후속 PR 로 마이그레이션 + 룰 박기.

## 예방 (Forcing function 우선)

1. **컨벤션 통일** — 모든 ep 는 `ep<N>-<DATE>.md` 로. Ep4/5 의 `ep<N>-substack.md` 는 `ep<N>-<DATE>.md` 로 git mv 1회 마이그레이션.
2. **sync_from_substack.py 손질** — backfill 결과는 별도 파일 (`ep<N>-cache.md` 같은) 에 저장. **원본 격 파일 (`ep<N>-<DATE>.md` / `ep<N>-substack.md`) 절대 덮어쓰기 금지** assert 추가.
3. **feedback memory 추가** — "외부 발행 (substack/naver) 전 로컬 원본 commit 필수, backfill 은 캐시 파일에만". 매 세션 로드.

## 재발 이력

## 관련 링크

- 커밋: 6eacc7f (ep5-substack 원본), 50c5ad4 (덮어쓰기 backfill)
- 메모리: `reference_substack_publish_pipeline.md`, `project_naver_blog_skill_v1_deployed.md`
- 텔레그램: id 10449
