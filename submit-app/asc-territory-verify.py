#!/usr/bin/env python3
"""ASC territory-verify — W6 가드 (dry-run default, --apply 로 실 API 호출).

자동 출시(AFTER_APPROVAL) 가 territory record 를 만들지 않는 quirk 우회.
출시 직후 호출하여 174 territory + CHN 1 unavailable 자동 등록.

Usage:
    asc-territory-verify.py --app-id <APP_ID> [--apply]

참고 사례: 2026-04-30 약먹자·더치페이 약 22분 unlist 사고.
"""
import argparse
import json
import sys
from pathlib import Path

# Allow running from the script's own directory or from claude-skills/submit-app/
_here = Path(__file__).parent
sys.path.insert(0, str(_here))
from asc_client import send, confirm_apply

_TERRITORIES_CACHE = _here / "territory_ids.json"


def load_territories() -> list[str]:
    if not _TERRITORIES_CACHE.exists():
        print(f"[WARN] territory cache 없음: {_TERRITORIES_CACHE}", file=sys.stderr)
        return ["PLACEHOLDER_174_ITEMS"]
    data = json.loads(_TERRITORIES_CACHE.read_text())
    if isinstance(data, list):
        return [t if isinstance(t, str) else t["id"] for t in data]
    return data.get("ids", ["PLACEHOLDER_174_ITEMS"])


def main() -> int:
    p = argparse.ArgumentParser(description="ASC territory-verify (W6 가드)")
    p.add_argument("--app-id", required=True, help="App Store Connect App ID (숫자)")
    p.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="실제 ASC API 호출. 미지정 시 dry-run (system-level 변경 0).",
    )
    args = p.parse_args()
    dry_run = not args.apply

    print(f"[asc-territory-verify] app_id={args.app_id} dry_run={dry_run}")

    if not dry_run and not confirm_apply("asc-territory-verify", args.app_id):
        print("[ABORT] 사용자 취소")
        return 1

    # Step 1: 현재 availability 조회
    send("GET", f"/v2/appAvailabilities/{args.app_id}", dry_run=dry_run)

    # Step 2: 174 territory + CHN 제외 POST
    territories = load_territories()
    territory_data = [{"type": "territories", "id": t} for t in territories if t != "CHN"]

    body = {
        "data": {
            "type": "appAvailabilities",
            "relationships": {
                "app": {"data": {"id": args.app_id, "type": "apps"}},
                "availableTerritories": {"data": territory_data},
            },
            "attributes": {
                "availableInNewTerritories": True,
            },
        }
    }
    send("POST", "/v2/appAvailabilities", body=body, dry_run=dry_run)

    if dry_run:
        print(
            f"[asc-territory-verify] dry-run complete — "
            f"{len(territory_data)} territory records would be set, CHN excluded"
        )
    else:
        print(f"[asc-territory-verify] ✅ {len(territory_data)} territories 등록 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
