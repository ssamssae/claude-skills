#!/usr/bin/env python3
"""ASC rc-reply — W8 가드 (dry-run default, --apply 로 실 API 호출).

territory/availability 변경 케이스 reject 답글 자동화.
ASC reviewSubmissionMessages 엔드포인트 사용.
2026-04-29 강대종님이 손으로 친 답글이 원본.

Usage:
    asc-rc-reply.py --review-submission-id <SUB_ID> [--message-template territory_fix] [--apply]
"""
import argparse
import sys
from pathlib import Path

_here = Path(__file__).parent
sys.path.insert(0, str(_here))
from asc_client import send, confirm_apply

TEMPLATES = {
    "territory_fix": (
        "Hi reviewer, the previous availability issue has been resolved on "
        "our side. We've also added the missing territory records. Please "
        "retry the review. Thanks."
    ),
    "generic": (
        "Hi reviewer, we have addressed the issue raised in the previous "
        "review. Please retry the review. Thanks."
    ),
}


def main() -> int:
    p = argparse.ArgumentParser(description="ASC rc-reply (W8 가드)")
    p.add_argument("--review-submission-id", required=True)
    p.add_argument(
        "--message-template",
        choices=list(TEMPLATES.keys()),
        default="territory_fix",
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
        f"[asc-rc-reply] review_sub_id={args.review_submission_id} "
        f"template={args.message_template} dry_run={dry_run}"
    )

    if not dry_run and not confirm_apply("asc-rc-reply", args.review_submission_id):
        print("[ABORT] 사용자 취소")
        return 1

    # Step 1: 기존 메시지 조회 (중복 방지)
    send(
        "GET",
        f"/v1/reviewSubmissionMessages"
        f"?filter[reviewSubmission]={args.review_submission_id}",
        dry_run=dry_run,
    )

    # Step 2: 답글 POST
    text = TEMPLATES[args.message_template]
    print(f"[asc-rc-reply] template '{args.message_template}' ({len(text)} chars)")

    reply_body = {
        "data": {
            "type": "reviewSubmissionMessages",
            "attributes": {"text": text},
            "relationships": {
                "reviewSubmission": {
                    "data": {
                        "type": "reviewSubmissions",
                        "id": args.review_submission_id,
                    }
                }
            },
        }
    }
    send("POST", "/v1/reviewSubmissionMessages", body=reply_body, dry_run=dry_run)

    if dry_run:
        print("[asc-rc-reply] dry-run complete (no API call)")
    else:
        print("[asc-rc-reply] ✅ 답글 전송 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
