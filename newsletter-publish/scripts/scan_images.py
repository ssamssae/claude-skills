#!/usr/bin/env python3
"""Scan a newsletter ep markdown for `🖼 IMAGE N` placeholders and
resolve each to an asset file under `<repo>/newsletter/assets/ep<N>/`.

Convention (locked 2026-05-02):
- Body lines like `> 🖼 IMAGE 1 (Hero) — caption text` declare an image slot.
- Asset files live in `<md_dir>/assets/ep<N>/<NN>-*.{png,jpg,jpeg,webp}`
  where `<NN>` is the zero-padded slot index (`01`, `02`, ...).
- `<N>` (the ep number) is parsed from the md filename: `ep<N>-*.md`.

Output (stdout, one JSON per line on a single line):
[
  {"index": 1, "asset_path": "/abs/.../assets/ep3/01-hero.png", "caption_line": "..."},
  {"index": 2, "asset_path": null, "caption_line": "..."},
  ...
]

`asset_path` is null when no matching file exists. The publisher should
surface those (don't silently skip — Ep.3 lost 4 images that way).

Exit codes:
0 success (any number of placeholders, including 0)
1 input error (missing file, unparseable filename)
"""
import json
import os
import re
import sys

PLACEHOLDER = re.compile(r"^>?\s*🖼\s*IMAGE\s+(\d+)\b.*$", re.MULTILINE)
EP_FROM_NAME = re.compile(r"\bep(\d+)[-_.]", re.IGNORECASE)
ASSET_EXTS = (".png", ".jpg", ".jpeg", ".webp")


def parse_ep_num(md_path: str) -> int:
    name = os.path.basename(md_path)
    m = EP_FROM_NAME.search(name)
    if not m:
        raise ValueError(f"cannot parse ep number from filename: {name}")
    return int(m.group(1))


def resolve_asset(asset_dir: str, index: int) -> str | None:
    if not os.path.isdir(asset_dir):
        return None
    prefix = f"{index:02d}-"
    for entry in sorted(os.listdir(asset_dir)):
        if entry.startswith(prefix) and entry.lower().endswith(ASSET_EXTS):
            return os.path.abspath(os.path.join(asset_dir, entry))
    return None


def scan(md_path: str) -> list[dict]:
    with open(md_path, encoding="utf-8") as f:
        body = f.read()
    ep_num = parse_ep_num(md_path)
    asset_dir = os.path.join(os.path.dirname(md_path), "assets", f"ep{ep_num}")

    out: list[dict] = []
    seen: set[int] = set()
    for m in PLACEHOLDER.finditer(body):
        index = int(m.group(1))
        if index in seen:
            continue
        seen.add(index)
        out.append({
            "index": index,
            "asset_path": resolve_asset(asset_dir, index),
            "caption_line": m.group(0).strip(),
        })
    out.sort(key=lambda e: e["index"])
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        sys.stderr.write("usage: scan_images.py <md_path>\n")
        return 1
    md_path = argv[1]
    if not os.path.isfile(md_path):
        sys.stderr.write(f"file not found: {md_path}\n")
        return 1
    try:
        entries = scan(md_path)
    except ValueError as e:
        sys.stderr.write(f"{e}\n")
        return 1
    print(json.dumps(entries, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
