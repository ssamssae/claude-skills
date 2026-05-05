#!/usr/bin/env python3
"""Shared ASC REST API client — JWT auth + HTTP send().

Used by asc-territory-verify.py, asc-resubmit.py, asc-rc-reply.py.
Credentials: ~/.claude/secrets/asc-api-key.json + AuthKey_<KEY_ID>.p8
"""
import json
import sys
import time
from pathlib import Path

import jwt
import requests

ASC_BASE = "https://api.appstoreconnect.apple.com"
_SECRETS = Path.home() / ".claude" / "secrets"
_CREDS_FILE = _SECRETS / "asc-api-key.json"


def make_jwt() -> str:
    """Generate short-lived (20 min) ASC JWT."""
    if not _CREDS_FILE.exists():
        raise FileNotFoundError(
            f"ASC 자격증명 없음: {_CREDS_FILE}\n"
            "asc-api-key.json 형식: {\"key_id\": \"...\", \"issuer_id\": \"...\", \"key_path\": \"...\"}"
        )
    cfg = json.loads(_CREDS_FILE.read_text())
    key_id = cfg["key_id"]
    issuer_id = cfg["issuer_id"]
    p8_path = Path(cfg.get("key_path", str(_SECRETS / f"AuthKey_{key_id}.p8")))
    if not p8_path.exists():
        raise FileNotFoundError(f"ASC p8 키 없음: {p8_path}")
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
