# korail-sniff — 코레일 iOS 앱 API 스니핑 방법론

## 목표

코레일 공식 iOS 앱의 예매 API를 mitmproxy로 가로채어, **서울→진영 05-23 09:04 KTX** 자동 예약 자동화의 기반을 마련한다.

## 왜 Playwright 경로가 막혀있나

코레일 웹사이트(letkorail.com)는 PerimeterX v1~v4 봇 탐지를 적용한다:
- 마우스 움직임·클릭 속도 패턴 분석
- Canvas fingerprinting
- JS 난독화 + 동적 토큰 로테이션
- Headless 브라우저 감지 (`navigator.webdriver` 등)

Playwright stealth 플러그인으로 일부 우회 가능하나, v4 기준으로 지속적인 실패가 보고된다. **iOS 앱은 이 레이어가 없어** mitmproxy MITM이 훨씬 안정적이다.

## 준비물

| 항목 | 내용 |
|------|------|
| iPhone | 코레일 앱 설치 + 로그인 완료 |
| PC/Mac | mitmproxy 설치, iPhone과 동일 Wi-Fi |
| mitmproxy | `pip3 install mitmproxy` 또는 `brew install mitmproxy` |

## 스니핑 3단계

### 1단계: 스크립트 실행

```bash
cd ~/.claude/skills/korail-sniff
chmod +x setup.sh
./setup.sh --filter
```

iPhone 프록시 설정 안내가 터미널에 출력된다.

### 2단계: iPhone 설정

1. **Wi-Fi 프록시** 설정 (스크립트가 IP/포트 출력)
2. **인증서 설치**: Safari에서 `http://mitm.it` 접속 → iOS 프로파일 설치
3. **인증서 신뢰**: 설정 → 일반 → 정보 → 인증서 신뢰 설정 → mitmproxy 활성화

### 3단계: API 캡처

코레일 앱에서:
1. 로그인
2. 승차권 예매 → 출발역(서울) / 도착역(진영) / 날짜 입력
3. 열차 조회 → 열차 선택 → 좌석 선택 → 결제 직전까지

터미널에 `🎯 예매` 태그가 붙은 요청들이 핵심이다.

캡처 파일: `captures/korail-capture-YYYY-MM-DD.json`

## 캡처 후 분석 포인트

```json
{
  "url": "https://smart.letskorail.com/...",
  "req_body": "...",
  "is_reservation": true
}
```

확인해야 할 것:
- **세션 토큰**: 요청 헤더의 `Authorization` 또는 쿠키
- **열차 조회 API**: URL + 파라미터 (출발역 코드, 도착역 코드, 날짜, 시각)
- **예약 API**: POST body 구조 (열차 ID, 좌석 등급, 인원)
- **결제 분기점**: 예약 확정 vs 결제 요청 분리 여부

## 재전송 (dry-run 먼저)

```bash
# 먼저 dry-run으로 확인
python3 addon_replay.py captures/korail-capture-2026-05-23.json --dry-run

# 실제 재전송 (세션 토큰 유효한 상태에서)
python3 addon_replay.py captures/korail-capture-2026-05-23.json
```

## 자동화 로드맵

```
스니핑 완료
  → API 구조 분석 (엔드포인트, 헤더, 파라미터)
  → 파이썬 예약 스크립트 작성
     ├── 로그인 (세션 토큰 발급)
     ├── 열차 조회 (서울→진영, 05-23, 09:04 이후 첫 KTX)
     ├── 좌석 선택 (일반실 창측 우선)
     └── 예약 확정 (결제는 수동 또는 카드 자동)
  → crontab / launchd 로 예매 오픈 시각(보통 1개월 전 00:00) 스케줄
```

## 주의사항

- mitmproxy 인증서는 스니핑 후 iPhone에서 **반드시 삭제** 또는 신뢰 해제
- Wi-Fi 프록시도 스니핑 후 **없음** 으로 복원
- 캡처된 세션 토큰은 `captures/` 디렉토리에 로컬 저장됨 — 외부 업로드 금지
- 코레일 앱 SSL Pinning 여부: 앱 버전마다 다름. 핀닝이 있으면 요청이 막힘 → `mitmproxy SSL error` 확인

## SSL Pinning 우회 (핀닝 감지 시)

코레일 앱이 SSL Pinning을 적용한 경우 mitmproxy에서 연결 오류가 발생한다.

대안:
1. **Frida** (탈옥 없이 sideload) + `ssl-kill-switch` 스크립트
2. **objection** (Frida 기반 CLI): `objection --gadget korail explore` → `ios sslpinning disable`
3. iOS 구버전 앱 sideload (핀닝 없는 이전 버전)

Frida 방식은 별도 설정이 필요하므로 먼저 핀닝 없이 동작하는지 테스트한다.
