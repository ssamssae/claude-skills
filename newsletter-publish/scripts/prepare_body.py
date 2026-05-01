#!/usr/bin/env python3
"""Prepare a newsletter ep<N>-<DATE>.md for substack + naver paste.

Outputs:
- /tmp/nl_body.md   (transformed plain markdown, table→list, first h1 stripped, leading
                     HTML comment block stripped for backfill caches)
- /tmp/nl_body.html (HTML rendered, no nl2br extension)
- prints two lines on stdout:
    title: <captured h1 title>
    subtitle: <first italic line under title, if any>
"""
import re
import sys

import markdown


def table_to_list(md: str) -> str:
    lines = md.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if (
            re.match(r"^\s*\|.*\|\s*$", line)
            and i + 1 < len(lines)
            and re.match(r"^\s*\|[\s\-:|]+\|\s*$", lines[i + 1])
        ):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            if out and out[-1].strip() != "":
                out.append("")
            while i < len(lines) and re.match(r"^\s*\|.*\|\s*$", lines[i]):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                pairs = [f"**{h}**: {v}" for h, v in zip(header, row) if v]
                if pairs:
                    out.append("- " + " / ".join(pairs))
                i += 1
            out.append("")
        else:
            out.append(line)
            i += 1
    return "\n".join(out)


if len(sys.argv) < 2:
    sys.stderr.write("usage: prepare_body.py <md_path>\n")
    sys.exit(1)

with open(sys.argv[1], encoding="utf-8") as f:
    md = f.read()

md = re.sub(r"\A<!--.*?-->\s*\n+", "", md, count=1, flags=re.DOTALL)

title_match = re.match(r"\A\s*#\s+([^\n]+)\n", md)
title = title_match.group(1).strip() if title_match else ""

md = re.sub(r"\A\s*#\s+[^\n]*\n+", "", md, count=1)

subtitle_match = re.match(r"\A_([^_\n]+)_\s*\n+", md)
if subtitle_match:
    subtitle = subtitle_match.group(1).strip()
    md = md[subtitle_match.end():]
else:
    subtitle = ""

md_transformed = table_to_list(md)

with open("/tmp/nl_body.md", "w", encoding="utf-8") as f:
    f.write(md_transformed)

html = markdown.markdown(md_transformed, extensions=["fenced_code", "sane_lists"])
with open("/tmp/nl_body.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"title: {title}")
print(f"subtitle: {subtitle}")
