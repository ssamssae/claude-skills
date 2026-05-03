# submit-app/asc-cache

`asc-territory-verify.py` 가 사용하는 정적 territory 캐시.

ASC API `GET /v1/territories` 결과(174건 + CHN unavailable 1건)를
정적 JSON 으로 미리 박아두고, dry-run/실호출 시 외부 호출 없이 로딩한다.

## 파일

- `territories.json` — 캐시 본체. `version` / `fetched_at` / `source` /
  `territories` (string id 배열) / `unavailable` (string id 배열).
- `README.md` — 본 문서.

## 역할 분리 (hard rule)

- **본진(Mac) 전담** — ASC p8 key 보유. `GET /v1/territories` 호출 +
  `territories.json` 채우기 + commit.
- **WSL** — 캐시 인프라(JSON skeleton + loader) 만 관리.
  ASC API 직접 호출 X. `territories.json` 의 territories 배열 채우기 X.

## 채우기 절차 (본진 사이클)

1. `~/.appstoreconnect/private_keys/AuthKey_RU7URQ5453.p8` 로 JWT 발급.
2. `GET /v1/territories` 호출 → 174 territory id 추출.
3. `territories.json` 의 `territories` 배열에 string id 만 박음 (객체 X).
   `fetched_at` 을 ISO8601 로 갱신.
4. commit + push (main 직접 또는 mac/asc-territory-cache-fill-YYYY-MM-DD 브랜치).

## 검증

```bash
~/claude-automations/scripts/asc-territory-verify.py --app-id 0000000000
```

dry-run 출력의 `availableTerritories.data` 에 N 항목이 들어있어야 한다.
캐시가 비어있으면 stderr 에 `WARN cache empty` 가 나오고 N=0 으로 떨어진다.
캐시 파일이 없으면 `SystemExit("territory cache missing: ...")` 로 즉시 종료.

검증 편의용 환경변수: `ASC_TERRITORY_CACHE_PATH=/path/to/sandbox.json` 으로
캐시 경로 override 가능 (read-only path).

## 관련

- 사고 이력: 2026-04-30 약먹자·더치페이 약 22분 unlist.
  자동 출시(AFTER_APPROVAL) 가 territory record 를 만들지 않는 quirk 우회용.
