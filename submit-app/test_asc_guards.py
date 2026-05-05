#!/usr/bin/env python3
"""Dry-run tests for ASC guard scripts — no network calls, no credentials needed."""
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).parent


def run(script: str, args: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(_here / script)] + args,
        capture_output=True, text=True
    )
    return result.returncode, result.stdout + result.stderr


def test_territory_verify_dry_run():
    code, out = run("asc-territory-verify.py", ["--app-id", "12345678"])
    assert code == 0, f"exit {code}\n{out}"
    assert "[DRY-RUN]" in out
    assert "dry_run=True" in out
    print("PASS: territory-verify dry-run")


def test_resubmit_dry_run():
    code, out = run("asc-resubmit.py", ["--app-id", "12345678"])
    assert code == 0, f"exit {code}\n{out}"
    assert "[DRY-RUN]" in out
    assert "dry_run=True" in out
    print("PASS: resubmit dry-run")


def test_rc_reply_dry_run():
    code, out = run("asc-rc-reply.py", ["--review-submission-id", "abc-123"])
    assert code == 0, f"exit {code}\n{out}"
    assert "[DRY-RUN]" in out
    assert "dry_run=True" in out
    print("PASS: rc-reply dry-run")


def test_rc_reply_templates():
    for tmpl in ["territory_fix", "generic"]:
        code, out = run("asc-rc-reply.py", [
            "--review-submission-id", "abc-123",
            "--message-template", tmpl,
        ])
        assert code == 0, f"exit {code}\n{out}"
        assert tmpl in out
        print(f"PASS: rc-reply template={tmpl}")


def test_territory_verify_missing_app_id():
    code, out = run("asc-territory-verify.py", [])
    assert code != 0
    print("PASS: territory-verify exits non-zero without --app-id")


if __name__ == "__main__":
    test_territory_verify_dry_run()
    test_resubmit_dry_run()
    test_rc_reply_dry_run()
    test_rc_reply_templates()
    test_territory_verify_missing_app_id()
    print("\n✅ All tests passed")
