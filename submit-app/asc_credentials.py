#!/usr/bin/env python3
"""ASC credentials loader — env vars first, JSON file fallback.

Priority:
  1. Env vars: ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_P8_PATH
  2. JSON file: ~/.claude/secrets/asc-api-key.json

Usage:
    from asc_credentials import load_credentials
    creds = load_credentials()
    # creds.key_id, creds.issuer_id, creds.p8_path
"""
import os
from dataclasses import dataclass
from pathlib import Path

_SECRETS = Path.home() / ".claude" / "secrets"
_CREDS_JSON = _SECRETS / "asc-api-key.json"

_ENV_KEY_ID = "ASC_KEY_ID"
_ENV_ISSUER_ID = "ASC_ISSUER_ID"
_ENV_P8_PATH = "ASC_KEY_P8_PATH"


@dataclass(frozen=True)
class AscCredentials:
    key_id: str
    issuer_id: str
    p8_path: Path


def load_credentials() -> AscCredentials:
    """Return ASC credentials from env vars or JSON file.

    Raises FileNotFoundError if neither source has complete credentials.
    """
    key_id = os.environ.get(_ENV_KEY_ID)
    issuer_id = os.environ.get(_ENV_ISSUER_ID)
    p8_path_str = os.environ.get(_ENV_P8_PATH)

    if key_id and issuer_id and p8_path_str:
        return AscCredentials(
            key_id=key_id,
            issuer_id=issuer_id,
            p8_path=Path(p8_path_str),
        )

    # TODO: fallback to JSON file — call _load_from_json() when env vars absent
    return _load_from_json()


def _load_from_json() -> AscCredentials:
    """Load credentials from ~/.claude/secrets/asc-api-key.json.

    Expected JSON format:
      {"key_id": "XXXXXXXXXX", "issuer_id": "xxxxxxxx-xxxx-...", "key_path": "/abs/path/AuthKey_XXX.p8"}
    """
    if not _CREDS_JSON.exists():
        raise FileNotFoundError(
            f"ASC 자격증명 없음: {_CREDS_JSON}\n"
            f"환경변수 {_ENV_KEY_ID}/{_ENV_ISSUER_ID}/{_ENV_P8_PATH} 또는 JSON 파일 필요"
        )

    import json
    cfg = json.loads(_CREDS_JSON.read_text())
    key_id = cfg["key_id"]
    issuer_id = cfg["issuer_id"]
    p8_path = Path(cfg.get("key_path", str(_SECRETS / f"AuthKey_{key_id}.p8")))

    if not p8_path.exists():
        raise FileNotFoundError(f"ASC p8 키 없음: {p8_path}")

    return AscCredentials(key_id=key_id, issuer_id=issuer_id, p8_path=p8_path)


def credentials_available() -> bool:
    """Return True if ASC credentials are accessible (env or JSON file)."""
    if all(os.environ.get(k) for k in (_ENV_KEY_ID, _ENV_ISSUER_ID, _ENV_P8_PATH)):
        return True
    if _CREDS_JSON.exists():
        return True
    return False
