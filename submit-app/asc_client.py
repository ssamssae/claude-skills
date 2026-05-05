#!/usr/bin/env python3
"""Shared ASC REST API client — JWT auth + HTTP send().

Used by asc-territory-verify.py, asc-resubmit.py, asc-rc-reply.py.
Credentials: env vars (ASC_KEY_ID / ASC_ISSUER_ID / ASC_KEY_P8_PATH)
             or ~/.claude/secrets/asc-api-key.json (fallback).
"""
import sys
import time
from pathlib import Path

import jwt
import requests

from asc_credentials import load_credentials

ASC_BASE = "https://api.appstoreconnect.apple.com"


def make_jwt() -> str:
    """Generate short-lived (20 min) ASC JWT."""
    creds = load_credentials()
    key_id = creds.key_id
    issuer_id = creds.issuer_id
    p8_path = creds.p8_path
    p8 = p8_path.read_text()
    now = int(time.time())
    return jwt.encode(
        {"iss": issuer_id, "iat": now, "exp": now + 1200, "aud": "appstoreconnect-v1"},
        p8,
        algorithm="ES256",
        headers={"alg": "ES256", "kid": key_id, "typ": "JWT"},
    )


def send(method: str, path: str, body: dict | None = None, dry_run: bool = True) -> dict | None:
    """HTTP call to ASC API. dry_run=True → print only, no network call."""
    url = ASC_BASE + path
    if dry_run:
        print(f"[DRY-RUN] {method} {url}")
        if body is not None:
            print(json.dumps(body, indent=2))
        return None

    token = make_jwt()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    resp = requests.request(
        method,
        url,
        headers=headers,
        json=body,
        timeout=30,
    )
    if resp.status_code >= 400:
        print(f"[ERROR] {method} {url} → {resp.status_code}", file=sys.stderr)
        try:
            print(json.dumps(resp.json(), indent=2), file=sys.stderr)
        except Exception:
            print(resp.text[:500], file=sys.stderr)
        resp.raise_for_status()
    if resp.content:
        return resp.json()
    return None


def confirm_apply(script_name: str, app_id: str) -> bool:
    """Interactive --apply 진행 전 사용자 확인 프롬프트.
    non-interactive(파이프/CI) 환경에서는 --apply 에도 True 반환 (강대종 컨펌 이미 완료 가정).
    """
    if not sys.stdin.isatty():
        return True
    ans = input(
        f"\n⚠️  [{script_name}] 실제 ASC API 호출 예정 (app_id={app_id}).\n"
        "   계속하려면 'yes' 입력: "
    ).strip()
    return ans.lower() == "yes"
