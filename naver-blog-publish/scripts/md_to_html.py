#!/usr/bin/env python3
"""Convert markdown to HTML (Substack-pattern, no nl2br)."""
import sys
import markdown

if len(sys.argv) < 2:
    sys.stderr.write("usage: md_to_html.py <md_path>\n")
    sys.exit(1)

with open(sys.argv[1], encoding="utf-8") as f:
    md = f.read()

html = markdown.markdown(md, extensions=["fenced_code", "tables", "sane_lists"])
sys.stdout.write(html)
