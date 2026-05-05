#!/usr/bin/env python3
"""ASC resubmit — W7 가드 (dry-run default, --apply 로 실 API 호출).

Apple UNRESOLVED_ISSUES reject 시:
  옛 reviewSubmission canceled=true → 새 sub 생성 → appStoreVersion attach → submitted=true

Usage:
    asc-resubmit.py --app-id <APP_ID> [--platform IOS] [--apply]

참고 lesson: ~/claude-skills/submit-app/lessons/apple-reject-resubmit-via-cancel.md
2026-04-30 한줄일기 사례 (11:06 우회 → 13:29 승인 PASS).
"""
import argparse
import sys
from pathlib import Path

_here = Path(__file__).parent
sys.path.insert(0, str(_here))
from asc_client import send, confirm_apply


def main() -> int:
    p = argparse.ArgumentParser(description="ASC resubmit (W7 가드)")
    p.add_argument("--app-id", required=True, help="App Store Connect App ID (숫자)")
    p.add_argument(
        "--platform",
        default="IOS",
        choices=["IOS", "MAC_OS", "TV_OS"],
    )
    p.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="실제 ASC API 호출. 미지정 시 dry-run.",
    )
    args = p.parse_args()
    dry_run = not args.apply

    print(
        f"[asc-resubmit] app_id={args.app_id} platform={args.platform} "
        f"dry_run={dry_run}"
    )

    if not dry_run and not confirm_apply("asc-resubmit", args.app_id):
        print("[ABORT] 사용자 취소")
        return 1

    # Step 1: 현재 WAITING_FOR_REVIEW / IN_REVIEW sub 조회
    result = send(
        "GET",
        f"/v1/reviewSubmissions"
        f"?filter[app]={args.app_id}"
        f"&filter[platform]={args.platform}"
        f"&filter[state]=IN_REVIEW,WAITING_FOR_REVIEW",
        dry_run=dry_run,
    )

    # --apply 시 실제 sub ID 사용, dry-run 시 placeholder
    old_sub_id = (
        result["data"][0]["id"]
        if result and result.get("data")
        else "PLACEHOLDER_OLD_SUB_ID"
    )

    # Step 2: 기존 sub 취소
    cancel_body = {
        "data": {
            "type": "reviewSubmissions",
            "id": old_sub_id,
            "attributes": {"canceled": True},
        }
    }
    send("PATCH", f"/v1/reviewSubmissions/{old_sub_id}", body=cancel_body, dry_run=dry_run)

    # Step 3: 새 sub 생성
    new_body = {
        "data": {
            "type": "reviewSubmissions",
            "attributes": {"platform": args.platform},
            "relationships": {"app": {"data": {"id": args.app_id, "type": "apps"}}},
        }
    }
    new_result = send("POST", "/v1/reviewSubmissions", body=new_body, dry_run=dry_run)
    new_sub_id = (
        new_result["data"]["id"] if new_result else "PLACEHOLDER_NEW_SUB_ID"
    )

    # Step 4: 최신 appStoreVersion attach
    asv_result = send(
        "GET",
        f"/v1/appStoreVersions?filter[app]={args.app_id}"
        f"&filter[platform]={args.platform}"
        f"&filter[appStoreState]=PREPARE_FOR_SUBMISSION,WAITING_FOR_REVIEW",
        dry_run=dry_run,
    )
    asv_id = (
        asv_result["data"][0]["id"] if asv_result and asv_result.get("data")
        else "PLACEHOLDER_LATEST_APP_STORE_VERSION_ID"
    )

    attach_body = {
        "data": {
            "type": "reviewSubmissionItems",
            "relationships": {
                "appStoreVersion": {"data": {"type": "appStoreVersions", "id": asv_id}},
                "reviewSubmission": {"data": {"type": "reviewSubmissions", "id": new_sub_id}},
            },
        }
    }
    send("POST", "/v1/reviewSubmissionItems", body=attach_body, dry_run=dry_run)

    # Step 5: 새 sub 제출
    submit_body = {
        "data": {
            "type": "reviewSubmissions",
            "id": new_sub_id,
            "attributes": {"submitted": True},
        }
    }
    send("PATCH", f"/v1/reviewSubmissions/{new_sub_id}", body=submit_body, dry_run=dry_run)

    if dry_run:
        print("[asc-resubmit] dry-run complete (no API call)")
    else:
        print(f"[asc-resubmit] ✅ 재제출 완료 — new_sub_id={new_sub_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
