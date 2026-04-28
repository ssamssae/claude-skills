---
prevention_deferred: null
---

# CF colo region-block 으로 친구 wifi 에서만 OpenAI 호출 거부

- **발생 일자:** 2026-04-28 (친구 카톡 알림 17시 전)
- **해결 일자:** 2026-04-28 17:20 KST (친구 카톡 "와파로도 이제 된다!!")
- **심각도:** high (1900원 유료 출시 블로커)
- **재발 가능성:** medium (CF Workers 에서 OpenAI/Anthropic 등 region-block 권역 API 를 직접 호출하는 모든 앱)
- **영향 범위:** hanjul worker, 향후 LLM 연동 신규 앱 전체

## 증상
친구폰 wifi (잠실 KT 라우터 IP) 에서 한줄일기 AI 호출 시 502 `upstream_failed` → 디버그 결과 OpenAI 가 403 `unsupported_country_region_territory` 반환. 본인 IP·친구 LTE 는 정상. 이전엔 "강대종 될 때 친구도 됨" 처럼 동기화돼 보였음. 1900원 유료 출시 직전 발견.

## 원인
Cloudflare colo 라우팅이 한국 wifi 라우터 IP 를 한국 colo 로 매핑 → 그 colo 의 outbound IP 가 OpenAI region-block 권역. 본인 / 친구 LTE 는 다른 colo 로 통과해서 그동안 안 보였던 것. budget 한도 문제 아님 (1a 결정사항 RESOLVED).

## 조치
- `worker.js` 의 `api.openai.com` 직접 호출 → CF AI Gateway (`hanjul-ai`) 경유로 교체. AI Gateway 는 자체 outbound colo 풀 사용해 한국 colo 의존 회피.
- compat URL 은 모델명 prefix 등 schema 차이로 400 (code:2019) 떴고, openai provider URL 로 가니 100% 호환 PASS.
- 진단 console.log 한 줄 유지 → 다음에 비슷한 region 거부 시 `wrangler tail` 만 켜면 IP+device+detail 즉시 잡힘.
- 커밋 `a188ed3` (2026-04-28 17:23 KST).

## 예방 (Forcing function 우선)
- **default 룰: CF Workers 에서 OpenAI/Anthropic 등 외부 LLM API 호출은 항상 CF AI Gateway 경유**. `api.openai.com` 직접 호출 금지. 신규 앱 worker 부트스트랩 시 이 규칙을 SKILL.md / 템플릿에 명시.
- 신규 LLM 연동 앱 출시 전 사전 점검 체크리스트에 "친구 wifi (다른 ISP) 또는 LTE 둘 다에서 1회 호출 PASS" 라인 추가. 본인 IP 한 곳에서만 확인하면 못 잡음.
- worker 진단 console.log (IP+device+detail 한 줄) 표준 패턴화 → `wrangler tail` 디버그 즉시성 확보.

## 재발 이력
<없음>

## 관련 링크
- 커밋: `a188ed3`
- 체크리스트: `~/apps/hanjul/store/launch-checklist-2026-04-28.md` (1a RESOLVED)
- 텔레그램: id 3730
