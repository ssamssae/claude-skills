#!/usr/bin/env python3
"""Regenerate issues/INDEX.md by scanning YYYY-MM-DD-*.md files.

Usage:
    python3 ~/.claude/skills/issue/tools/regen_index.py

Overwrites INDEX.md every run — do NOT edit INDEX.md manually.
Parses each issue's frontmatter (if present) + top-level heading + metadata block
to build a glanceable table.
"""
from __future__ import annotations

import datetime as dt
import pathlib
import re
import sys

SKILLS_DIR = pathlib.Path.home() / ".claude" / "skills"
ISSUES_DIR = SKILLS_DIR / "issues"
INDEX_PATH = ISSUES_DIR / "INDEX.md"

HEADER = (
    "# Issues Index\n"
    "\n"
    "_자동 생성됨. 이 파일은 수동 편집 금지 — `python3 "
    "~/.claude/skills/issue/tools/regen_index.py` 로만 갱신._\n"
    "_마지막 생성: {ts} KST_\n"
    "\n"
    "| 날짜 | slug | 제목 | 심각도 | 재발 가능성 | 재발 이력 | 예방 deferred |\n"
    "| --- | --- | --- | --- | --- | --- | --- |\n"
)

FOOTER = (
    "\n"
    "## 룰\n"
    "\n"
    "- 매 이슈는 자기 파일 하나. `YYYY-MM-DD-<slug>.md`\n"
    "- 이 INDEX 는 `/issue` 스킬이 저장할 때마다 전체 덮어쓰기로 재생성됨.\n"
    "- 재발 가능성 high 인데 forcing function 없으면 적극적으로 설치. "
    "이 index 가 \"손 안 댄 debt\" 추적판 역할도 겸함.\n"
)


_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")
_FRONT_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_META_RE = re.compile(r"^-\s*\*\*(.+?):\*\*\s*(.+?)\s*$", re.MULTILINE)
_RECUR_SECTION_RE = re.compile(
    r"^##\s*재발\s*이력\s*$\n(.*?)(?=^##\s|\Z)", re.MULTILINE | re.DOTALL
)
_RECUR_ITEM_RE = re.compile(r"^\s*-\s+", re.MULTILINE)


def parse_issue(path: pathlib.Path) -> dict | None:
    m = _DATE_RE.match(path.name)
    if not m:
        return None
    date, slug = m.group(1), m.group(2)

    text = path.read_text(encoding="utf-8")

    frontmatter: dict[str, str] = {}
    fm = _FRONT_RE.match(text)
    if fm:
        body = text[fm.end():]
        for line in fm.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                frontmatter[k.strip()] = v.strip().strip('"').strip("'")
    else:
        body = text

    title_m = _TITLE_RE.search(body)
    title = title_m.group(1).strip() if title_m else slug

    meta: dict[str, str] = {}
    for mm in _META_RE.finditer(body):
        meta[mm.group(1).strip()] = mm.group(2).strip()
    severity = meta.get("심각도", "?")
    recurrence = meta.get("재발 가능성", "?")

    recur_count = 0
    rm = _RECUR_SECTION_RE.search(body)
    if rm:
        section_body = rm.group(1)
        recur_count = sum(1 for _ in _RECUR_ITEM_RE.finditer(section_body))

    deferred = frontmatter.get("prevention_deferred", "").strip()
    if deferred in ("", "null", "None"):
        deferred = "—"

    return {
        "date": date,
        "slug": slug,
        "filename": path.name,
        "title": title,
        "severity": severity,
        "recurrence": recurrence,
        "recur_count": recur_count,
        "deferred": deferred,
    }


def main() -> int:
    if not ISSUES_DIR.is_dir():
        print(f"[regen_index] not a directory: {ISSUES_DIR}", file=sys.stderr)
        return 1

    issues = []
    for md in sorted(ISSUES_DIR.glob("*.md")):
        if md.name == "INDEX.md":
            continue
        parsed = parse_issue(md)
        if parsed:
            issues.append(parsed)

    # 최신 날짜 + 같은 날이면 slug 역순
    issues.sort(key=lambda d: (d["date"], d["slug"]), reverse=True)

    now_kst = dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))
    out = HEADER.format(ts=now_kst.strftime("%Y-%m-%d %H:%M"))

    if not issues:
        out += "| _(아직 없음)_ | | | | | | |\n"
    else:
        for it in issues:
            recur_cell = "—" if it["recur_count"] == 0 else f"{it['recur_count']}회"
            title = it["title"].replace("|", "\\|")
            out += (
                f"| {it['date']} | [{it['slug']}]({it['filename']}) | "
                f"{title} | {it['severity']} | {it['recurrence']} | "
                f"{recur_cell} | {it['deferred']} |\n"
            )

    out += FOOTER
    INDEX_PATH.write_text(out, encoding="utf-8")
    print(f"[regen_index] wrote {INDEX_PATH} ({len(issues)} issues)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
