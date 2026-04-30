---
platform: ios
severity: blocking
category: review-workflow
first_hit: 2026-04-30
hits: 1
source: workflow-discovery
---

# Apple UNRESOLVED_ISSUES reject 후 ASC API 재제출 = 옛 submission cancel 우회 필요

## 증상

iOS 앱이 reject (state = UNRESOLVED_ISSUES) 된 뒤 ASC Resolution Center 에 답글만 보내고 기다리면 재심사 큐에 안 들어간다. 26시간 지나도 state 그대로. Apple 이 답글만으로 자동 재심사를 트리거하지 않음.

ASC 가 "새 reviewSubmission" 을 자동 생성해두기는 하지만 (state=READY_FOR_REVIEW), 그 안의 items 는 **0개** 인 빈 껍데기. 빌드/버전이 attach 안 돼있어서 submit 도 못 함.

## 원인

옛 (rejected) reviewSubmission 의 reviewSubmissionItem 이 **appStoreVersion 을 점유한 채 잠긴 상태**. UNRESOLVED_ISSUES 는 state 상 종결된 것 같지만 ASC 내부적으로는 아직 "active item" 으로 분류돼서 같은 version 을 새 submission 에 attach 시킬 수 없다.

- POST `/v1/reviewSubmissionItems` (새 sub 에 같은 version attach) → **409 STATE_ERROR.ENTITY_STATE_INVALID**: "appStoreVersions ... is not in valid state. ... Item is already present in another reviewSubmission"
- DELETE `/v1/reviewSubmissionItems/{old_item_id}` → **409**: "Item was already submitted" (제출된 item 은 직접 삭제 불가)

## 우회 (검증됨)

옛 submission 자체를 cancel 하면 그 안의 items 도 같이 풀려서 version 이 free 해진다.

```python
# 1. PATCH 옛 reviewSubmission canceled=true
PATCH /v1/reviewSubmissions/{OLD_SUB_ID}
{
  "data": {
    "type": "reviewSubmissions",
    "id": OLD_SUB_ID,
    "attributes": {"canceled": true}
  }
}
# → 200 OK, state: CANCELING

# 2. 폴링 ~30s 까지 state == COMPLETE 대기
# (CANCELING → COMPLETE 가 완료 신호. CANCELED 가 아니라 COMPLETE 로 끝남)

# 3. 새 reviewSubmission 에 appStoreVersion attach
POST /v1/reviewSubmissionItems
{
  "data": {
    "type": "reviewSubmissionItems",
    "relationships": {
      "reviewSubmission": {"data": {"type":"reviewSubmissions","id": NEW_SUB_ID}},
      "appStoreVersion":  {"data": {"type":"appStoreVersions","id": VERSION_ID}}
    }
  }
}
# → 201 Created

# 4. 새 submission submit
PATCH /v1/reviewSubmissions/{NEW_SUB_ID}
{
  "data": {
    "type": "reviewSubmissions",
    "id": NEW_SUB_ID,
    "attributes": {"submitted": true}
  }
}
# → 200 OK, state: WAITING_FOR_REVIEW
```

## 사전 조건

- Resolution Center 답글에서 약속한 변경(예: territory 제외)을 **API/UI 로 실제로 반영해둘 것**. 답글만 있고 변경이 없으면 또 reject 된다.
- territory 변경은 v2 `/territoryAvailabilities` 로 검증: `available=False` 인 territory id 가 reject 사유의 그 국가인지 확인.

## 첫 발생

- 2026-04-30 한줄일기 (com.daejongkang.hanjul). 4/28 23:05 제출 → 4/29 06:43 China Deep Synthesis 규정 reject (UNRESOLVED_ISSUES) → 4/29 08:05 강대종 Resolution Center 답글 + China availability 제외 → 4/30 11:06 이 우회 경로로 재심사 진입 PASS (reviewSubmission `e58db9c9-8a75-4835-9cd0-4f2ae0a0bc2e`, state=WAITING_FOR_REVIEW).
- 어제 세션이 "ASC API 재제출 불가 (사유 모름)" 으로 닫혔던 진짜 이유 = 잠금 패턴 미발견. canceled=true 한 줄로 해결.
