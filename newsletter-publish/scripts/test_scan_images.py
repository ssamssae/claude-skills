#!/usr/bin/env python3
"""Unit tests for scan_images.py — stdlib unittest, no external deps.

Run: `python3 -m unittest test_scan_images.py`
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SELF_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(SELF_DIR, "scan_images.py")

sys.path.insert(0, SELF_DIR)
from scan_images import parse_ep_num, resolve_asset, scan  # noqa: E402


class ParseEpNum(unittest.TestCase):
    def test_dash_form(self):
        self.assertEqual(parse_ep_num("/x/ep3-2026-04-28.md"), 3)

    def test_substack_form(self):
        self.assertEqual(parse_ep_num("/x/ep3-substack.md"), 3)

    def test_two_digit_ep(self):
        self.assertEqual(parse_ep_num("/x/ep12-2027-01-01.md"), 12)

    def test_unparseable(self):
        with self.assertRaises(ValueError):
            parse_ep_num("/x/random.md")


class ResolveAsset(unittest.TestCase):
    def test_missing_dir_returns_none(self):
        self.assertIsNone(resolve_asset("/no/such/dir", 1))

    def test_zero_padded_match(self):
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "01-hero.png"), "w"):
                pass
            with open(os.path.join(td, "10-late.png"), "w"):
                pass
            r = resolve_asset(td, 1)
            self.assertIsNotNone(r)
            self.assertTrue(r.endswith("01-hero.png"))
            r10 = resolve_asset(td, 10)
            self.assertTrue(r10.endswith("10-late.png"))

    def test_non_match_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "01-hero.png"), "w"):
                pass
            self.assertIsNone(resolve_asset(td, 2))

    def test_ext_filter(self):
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "01-notes.txt"), "w"):
                pass
            self.assertIsNone(resolve_asset(td, 1))


def _write_ep(td: str, ep_num: int, body: str, asset_files: list[str]) -> str:
    md_path = os.path.join(td, f"ep{ep_num}-2026-04-28.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(body)
    asset_dir = os.path.join(td, "assets", f"ep{ep_num}")
    os.makedirs(asset_dir, exist_ok=True)
    for name in asset_files:
        with open(os.path.join(asset_dir, name), "w"):
            pass
    return md_path


class ScanFixture(unittest.TestCase):
    def test_ep3_fixture_4_images_all_resolved(self):
        with tempfile.TemporaryDirectory() as td:
            body = (
                "# Title\n\n"
                "intro text\n\n"
                "> 🖼 IMAGE 1 (Hero) — first image caption\n\n"
                "section 1\n\n"
                "> 🖼 IMAGE 2 (Table) — second image caption\n\n"
                "section 2\n\n"
                "> 🖼 IMAGE 3 (Timeline) — third image caption\n\n"
                "section 3\n\n"
                "> 🖼 IMAGE 4 (Mirror) — fourth image caption\n\n"
                "outro\n"
            )
            assets = ["01-hero.png", "02-price-table.png",
                      "03-timeline.png", "04-claude-mirror.png"]
            md = _write_ep(td, 3, body, assets)

            entries = scan(md)
            self.assertEqual(len(entries), 4)
            self.assertEqual([e["index"] for e in entries], [1, 2, 3, 4])
            for e in entries:
                self.assertIsNotNone(
                    e["asset_path"], f"index {e['index']} unresolved")
                self.assertTrue(os.path.isabs(e["asset_path"]))
            self.assertTrue(entries[0]["asset_path"].endswith("01-hero.png"))
            self.assertTrue(entries[3]["asset_path"].endswith("04-claude-mirror.png"))

    def test_missing_asset_emits_null(self):
        with tempfile.TemporaryDirectory() as td:
            body = ("> 🖼 IMAGE 1 (Hero) — caption\n\n"
                    "> 🖼 IMAGE 2 (Missing) — no asset for this one\n")
            md = _write_ep(td, 3, body, ["01-hero.png"])

            entries = scan(md)
            self.assertEqual(len(entries), 2)
            self.assertIsNotNone(entries[0]["asset_path"])
            self.assertIsNone(entries[1]["asset_path"])

    def test_no_placeholders_returns_empty(self):
        with tempfile.TemporaryDirectory() as td:
            md = _write_ep(td, 4, "# title\n\nplain body\n", [])
            self.assertEqual(scan(md), [])

    def test_duplicate_index_dedupes_keeping_first(self):
        with tempfile.TemporaryDirectory() as td:
            body = ("> 🖼 IMAGE 1 (Hero) — first\n\n"
                    "later in body\n\n"
                    "> 🖼 IMAGE 1 (Re-use) — same index reappears\n")
            md = _write_ep(td, 5, body, ["01-hero.png"])

            entries = scan(md)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["index"], 1)
            self.assertIn("first", entries[0]["caption_line"])


class CliSmoke(unittest.TestCase):
    def test_cli_emits_valid_json_to_stdout(self):
        with tempfile.TemporaryDirectory() as td:
            md = _write_ep(td, 3,
                           "> 🖼 IMAGE 1 (Hero) — cap\n",
                           ["01-hero.png"])
            res = subprocess.run([sys.executable, SCRIPT, md],
                                 capture_output=True, text=True, check=True)
            payload = json.loads(res.stdout)
            self.assertEqual(len(payload), 1)
            self.assertEqual(payload[0]["index"], 1)


if __name__ == "__main__":
    unittest.main()
