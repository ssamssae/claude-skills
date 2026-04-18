---
name: review-status-check
description: 매 시간 Gmail 에서 Google Play Console + App Store Connect 심사 상태 이메일을 모니터링하고, 상태 변경 감지 시 텔레그램으로 알림. launchd 로 매시간 자동 실행되며 수동 호출도 가능. 최초 실행 시 Gmail OAuth 인증 필요.
allowed-tools: Bash, Read, Write, mcp__claude_ai_Gmail__authenticate, mcp__claude_ai_Gmail__complete_authentication
---

# 앱 심사 상태 체크 봇

Google/Apple 이 보내는 **공식 심사 상태 이메일**을 Gmail MCP 로 감시해서 상태 변경 시 텔레그램으로 전달.
이메일 알림을 별도로 체크할 필요 없게 만드는 용도.

## 모니터링 대상

- **메모요 Android** (Google Play Closed Testing → Production)
  - applicationId: `com.daejongkang.simple_memo_app`
- **메모요 iOS** (Apple App Store)
  - bundle ID: `com.daejongkang.simpleMemoApp`

## 실행 흐름

### 1. 이전 상태 읽기

```bash
cat ~/.claude/review-state.json 2>/dev/null || echo '{}'
```

파일 구조:
```json
{
  "memoyo_android": {
    "subject": "...",
    "from": "...",
    "date": "ISO8601",
    "messageId": "..."
  },
  "memoyo_ios": { ... },
  "lastChecked": "ISO8601"
}
```

### 2. Gmail 검색

Gmail MCP 로 최근 **7일** 이메일 검색. 두 쿼리 병렬 실행:

**Android 쿼리:**
```
from:(googleplay-noreply@google.com OR noreply-play-console@google.com OR play-console-noreply@google.com) newer_than:7d
```

**iOS 쿼리:**
```
from:(no_reply@email.apple.com OR noreply@email.apple.com OR itunesconnect@apple.com) newer_than:7d
```

각 쿼리 결과에서 "memoyo" / "메모요" / "Memoyo" 본문·제목 포함 것만 필터링.

### 3. 가장 최근 이메일 선정

각 플랫폼별로 **date 내림차순** 첫 번째 이메일을 현재 상태로 간주.

### 4. 상태 변경 감지

이전 상태의 `messageId` 와 비교:
- 다르면 → **상태 변경** (텔레그램 전송)
- 같으면 → 변경 없음 (스킵)
- 이전 상태 `{}` (최초 실행) → 알림 없이 현재 상태만 저장 (sliient seed)

### 5. 텔레그램 알림 포맷 (변경 있을 때만)

```
🔔 앱 심사 상태 변경

📱 메모요 Android
  제목: [이메일 제목]
  출처: Google Play Console
  시간: YYYY-MM-DD HH:MM KST

📱 메모요 iOS
  제목: [이메일 제목]
  출처: App Store Connect
  시간: YYYY-MM-DD HH:MM KST

💡 Gmail 에서 원문 확인하세요.
```

전송:
```bash
~/.claude/channels/telegram/send.sh 538806975 "<메시지>"
```

### 6. 상태 저장

`~/.claude/review-state.json` 덮어쓰기. `lastChecked` 항상 갱신.

## Gmail 인증

최초 실행 시 Gmail MCP 가 OAuth 플로우 요구:
1. `mcp__claude_ai_Gmail__authenticate` 호출
2. 사용자에게 반환된 URL 을 브라우저에서 열어 인증하도록 텔레그램으로 안내
3. 사용자가 인증 후 반환된 코드를 붙여넣으면 `complete_authentication` 호출
4. 이후 리프레시 토큰으로 자동 갱신

launchd 세션에서 인증이 만료된 경우:
- 에러를 텔레그램으로 알림 ("Gmail 재인증 필요")
- 사용자가 `/review-status-check` 수동 실행해서 재인증

## 에러 처리

- Gmail MCP 실패: 텔레그램으로 에러 메시지 1줄 전송 후 종료
- 메일 0건: `"심사 이메일 없음 (정상)"` 로그만, 알림 X
- send.sh 실패: stdout 로만 출력

## 주의

- **조용한 시드** 원칙: 최초 실행 시 "상태 변경됨" 오해 안 나도록 알림 X
- 스팸 방지: 동일 messageId 재검출 시 알림 X (idempotent)
- 노이즈 방지: Google/Apple 의 일반 마케팅·청구 메일은 "memoyo" 키워드로 필터링됨
- 타임스탬프는 KST 로 변환해서 표시
- 메시지 한국어, 이메일 제목은 원문 그대로
