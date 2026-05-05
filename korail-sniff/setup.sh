#!/usr/bin/env bash
# korail-sniff/setup.sh
# 코레일 iOS 앱 API 스니핑용 mitmproxy 설정 스크립트
# 목표: 코레일 앱의 예약 API 엔드포인트 및 요청 파라미터 캡처
#
# 사용법:
#   ./setup.sh [--filter] [--dump] [--replay <har_file>]
#
#   --filter  : 코레일 관련 요청만 필터링해서 터미널에 표시 (기본)
#   --dump    : 모든 요청을 korail-capture-YYYY-MM-DD.har 로 저장
#   --replay  : HAR 파일에서 예약 요청만 추출해서 재전송

set -euo pipefail

# mitmproxy 경로 — brew(M1/Intel Mac) 또는 pip3 Python 3.13 framework
for _p in \
    /opt/homebrew/bin \
    /usr/local/bin \
    "/Library/Frameworks/Python.framework/Versions/3.13/bin" \
    "$HOME/Library/Python/3.13/bin" \
    "$HOME/Library/Python/3.12/bin"; do
  [[ -x "${_p}/mitmproxy" ]] && export PATH="${_p}:${PATH}" && break
done
unset _p

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAPTURE_DIR="${SCRIPT_DIR}/captures"
ADDON_FILTER="${SCRIPT_DIR}/addon_filter.py"
ADDON_REPLAY="${SCRIPT_DIR}/addon_replay.py"
DATE=$(date +%Y-%m-%d)
CAPTURE_FILE="${CAPTURE_DIR}/korail-capture-${DATE}.har"

# macOS / Linux 호환 로컬 IP 검출
if [[ "$(uname)" == "Darwin" ]]; then
  PROXY_HOST="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")"
else
  PROXY_HOST="$(hostname -I | awk '{print $1}')"
fi
PROXY_PORT=8080

# ── 의존성 확인 ──────────────────────────────────────────────

check_deps() {
  if ! command -v mitmproxy &>/dev/null; then
    echo "[setup] mitmproxy가 없습니다. 설치 중..."
    if command -v pip3 &>/dev/null; then
      pip3 install --user mitmproxy
    elif command -v brew &>/dev/null; then
      brew install mitmproxy
    else
      echo "[ERROR] pip3 또는 brew가 필요합니다." >&2
      exit 1
    fi
  fi

  MITM_VER=$(mitmproxy --version 2>&1 | head -1)
  echo "[setup] ${MITM_VER}"
  mkdir -p "${CAPTURE_DIR}"
}

# ── iPhone 프록시 설정 안내 ───────────────────────────────────

print_iphone_guide() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  iPhone 프록시 설정 (Wi-Fi 동일 네트워크 필수)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "1. iPhone → 설정 → Wi-Fi → 현재 네트워크 (i) 버튼"
  echo "   → 프록시 구성 → 수동"
  echo "   서버: ${PROXY_HOST}"
  echo "   포트: ${PROXY_PORT}"
  echo ""
  echo "2. iPhone Safari에서 http://mitm.it 접속"
  echo "   → iOS 클릭 → 구성 프로파일 설치 허용"
  echo ""
  echo "3. 설정 → 일반 → VPN 및 기기 관리"
  echo "   → mitmproxy 인증서 → 신뢰"
  echo ""
  echo "4. 설정 → 일반 → 정보 → 인증서 신뢰 설정"
  echo "   → mitmproxy 루트 인증서 → 활성화"
  echo ""
  echo "5. 코레일 앱 실행 → 로그인 → 승차권 예매 시도"
  echo ""
  echo "스니핑 완료 후: iPhone Wi-Fi 프록시 → '없음' 으로 복원"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
}

# ── 코레일 필터 애드온 생성 ──────────────────────────────────

write_addon_filter() {
  cat > "${ADDON_FILTER}" << 'PYEOF'
"""
코레일 API 필터 애드온
- 코레일 관련 요청만 터미널에 출력
- captures/ 디렉토리에 JSON으로 저장
"""
import json
import os
import re
from datetime import datetime
from mitmproxy import http

KORAIL_HOSTS = (
    "www.letskorail.com",
    "smart.letskorail.com",
    "app.letskorail.com",
    "railgate.korail.com",
    "m.korail.com",
    "openapi.korail.go.kr",
)

RESERVATION_KEYWORDS = (
    "train", "reserve", "ticket", "booking",
    "schedule", "search", "seat",
    "기차", "예매", "좌석", "조회",
)

CAPTURE_DIR = os.path.join(os.path.dirname(__file__), "captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)

captured = []


def is_korail(flow: http.HTTPFlow) -> bool:
    host = flow.request.pretty_host.lower()
    return any(h in host for h in KORAIL_HOSTS)


def is_reservation_related(flow: http.HTTPFlow) -> bool:
    url = flow.request.pretty_url.lower()
    body = flow.request.text.lower() if flow.request.text else ""
    return any(kw in url or kw in body for kw in RESERVATION_KEYWORDS)


def response(flow: http.HTTPFlow):
    if not is_korail(flow):
        return

    entry = {
        "ts": datetime.now().isoformat(),
        "method": flow.request.method,
        "url": flow.request.pretty_url,
        "status": flow.response.status_code if flow.response else None,
        "req_headers": dict(flow.request.headers),
        "req_body": flow.request.text or "",
        "resp_body": flow.response.text if flow.response else "",
        "is_reservation": is_reservation_related(flow),
    }
    captured.append(entry)

    tag = "🎯 예매" if entry["is_reservation"] else "   "
    print(f"{tag} [{entry['status']}] {entry['method']} {entry['url'][:80]}")

    # 즉시 파일로 저장 (중간에 ctrl+c 해도 유실 없음)
    date = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join(CAPTURE_DIR, f"korail-capture-{date}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(captured, f, ensure_ascii=False, indent=2)
PYEOF
  echo "[setup] 필터 애드온 생성: ${ADDON_FILTER}"
}

# ── 재전송 애드온 생성 ───────────────────────────────────────

write_addon_replay() {
  cat > "${ADDON_REPLAY}" << 'PYEOF'
"""
캡처된 코레일 예매 요청 재전송 스크립트
사용: python3 addon_replay.py <capture_json> [--dry-run]
"""
import json
import sys
import time
import urllib.request
import urllib.error
import urllib.parse


def replay(capture_file: str, dry_run: bool = False):
    with open(capture_file, encoding="utf-8") as f:
        entries = json.load(f)

    reservation_entries = [e for e in entries if e.get("is_reservation")]
    print(f"[replay] 전체 {len(entries)}건 중 예매 관련 {len(reservation_entries)}건")

    for i, entry in enumerate(reservation_entries, 1):
        print(f"\n[{i}/{len(reservation_entries)}] {entry['method']} {entry['url'][:80]}")
        if dry_run:
            print("  → dry-run: 실제 전송 생략")
            continue

        try:
            body = entry["req_body"].encode() if entry["req_body"] else None
            req = urllib.request.Request(
                entry["url"],
                data=body,
                method=entry["method"],
            )
            # 원본 헤더 복원 (일부 헤더는 urllib이 자동 처리)
            skip_headers = {"content-length", "transfer-encoding", "connection"}
            for k, v in entry["req_headers"].items():
                if k.lower() not in skip_headers:
                    req.add_header(k, v)

            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"  → {resp.status} {resp.reason}")
                respbody = resp.read().decode(errors="replace")
                print(f"  → {respbody[:200]}")
        except urllib.error.HTTPError as e:
            print(f"  → HTTP {e.code}: {e.reason}")
        except Exception as ex:
            print(f"  → ERROR: {ex}")

        time.sleep(0.5)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용: python3 addon_replay.py <capture.json> [--dry-run]")
        sys.exit(1)
    dry = "--dry-run" in sys.argv
    replay(sys.argv[1], dry_run=dry)
PYEOF
  echo "[setup] 재전송 스크립트 생성: ${ADDON_REPLAY}"
}

# ── 메인 ────────────────────────────────────────────────────

MODE="${1:---filter}"

check_deps
write_addon_filter
write_addon_replay
print_iphone_guide

case "${MODE}" in
  --filter)
    echo "[setup] 필터 모드 시작 (코레일 요청만 표시 + captures/ 저장)"
    echo "[setup] 종료: Ctrl+C"
    echo ""
    mitmproxy \
      --listen-host 0.0.0.0 \
      --listen-port "${PROXY_PORT}" \
      -s "${ADDON_FILTER}"
    ;;
  --dump)
    echo "[setup] 덤프 모드 시작 → ${CAPTURE_FILE}"
    mitmdump \
      --listen-host 0.0.0.0 \
      --listen-port "${PROXY_PORT}" \
      -s "${ADDON_FILTER}" \
      -w "${CAPTURE_FILE}"
    ;;
  --replay)
    REPLAY_FILE="${2:-}"
    if [[ -z "${REPLAY_FILE}" ]]; then
      # 가장 최신 캡처 파일 자동 선택
      REPLAY_FILE=$(ls -t "${CAPTURE_DIR}"/korail-capture-*.json 2>/dev/null | head -1)
      if [[ -z "${REPLAY_FILE}" ]]; then
        echo "[ERROR] 재전송할 캡처 파일이 없습니다. --dump 로 먼저 캡처하세요." >&2
        exit 1
      fi
      echo "[setup] 자동 선택: ${REPLAY_FILE}"
    fi
    python3 "${ADDON_REPLAY}" "${REPLAY_FILE}"
    ;;
  *)
    echo "사용: $0 [--filter|--dump|--replay [파일]]" >&2
    exit 1
    ;;
esac
