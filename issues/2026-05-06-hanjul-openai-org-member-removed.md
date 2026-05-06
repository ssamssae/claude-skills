---
prevention_deferred: null
---

# 한줄일기 AI 응원 기능 중단 — OpenAI Organization 멤버 remove로 API 키 접근 차단

- **발생 일자:** 2026-05-06 (정확한 중단 시점 불명, 20:47 KST 최초 발견)
- **해결 일자:** 2026-05-06 20:50 KST
- **심각도:** high (유료 앱 핵심 기능 전체 중단)
- **재발 가능성:** medium
- **영향 범위:** 한줄일기 iOS/Android — AI 응원 버튼 (Cloudflare Worker → OpenAI GPT-4o-mini)

## 증상
AI 응원 버튼 클릭 시 무응답. Cloudflare Worker curl 직접 테스트 결과:
```
HTTP 502 {"error":"upstream_failed","status":401,"detail":"You do not have access to the organization tied to the API key."}
```

## 원인
사업자 OpenAI 계정 설정 과정에서 **API 키를 만든 개인 계정을 Organization에서 remove**함.

OpenAI API 키는 키 문자열만으로 인증하는 것처럼 보이지만, 실제로는 **키가 귀속된 Organization + 키를 만든 멤버의 org 접근권한**을 함께 검증함. 멤버가 org에서 제거되는 순간 해당 멤버가 만든 모든 키가 차단됨.

함께 있었던 Organization name 변경(Personal → hanjul)은 표시명만 바뀌는 것으로 직접 원인 아님.

## 조치
1. 개인 계정을 Organization에 재초대 (invite)
2. Organization name을 hanjul → Personal로 복구 (이름 자체는 원인 아니지만 원복)
→ API 정상 동작 확인

## 예방
1. **OpenAI org 멤버 변경 전 Worker 테스트 필수**: org에서 멤버 add/remove 전에 반드시 `curl https://hanjul-proxy.ssamssae.workers.dev/reply -X POST -H "Content-Type: application/json" -d '{"text":"테스트"}'` 로 현재 정상 확인 후 변경 진행.
2. **외부 uptime monitor 등록**: UptimeRobot(무료) 또는 유사 서비스로 /reply 엔드포인트를 5분 주기 ping → 중단 시 즉시 알림. 유료 앱 무증상 중단 방지.

## 재발 이력
<처음 생성>

## 관련 링크
- Worker endpoint: https://hanjul-proxy.ssamssae.workers.dev/reply
- 앱 코드: `lib/services/ai_service.dart`
- 텔레그램 메시지: id 13167
