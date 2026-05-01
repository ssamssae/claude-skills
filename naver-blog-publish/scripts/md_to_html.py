#!/usr/bin/env python3
"""Convert markdown to HTML for naver-blog-publish.

Naver SmartEditor 의 제목 셀은 별도이므로, md 의 첫 `# h1` 라인은 제목으로
사용되고 본문 paste 에는 들어가면 안 됨 (h1 듀플 회피). 기본 동작으로 첫 h1
라인을 제거 후 HTML 변환. nl2br extension 금지 (Substack 패턴).
"""
import re
import sys
import markdown

if len(sys.argv) < 2:
    sys.stderr.write("usage: md_to_html.py <md_path>\n")
    sys.exit(1)

with open(sys.argv[1], encoding="utf-8") as f:
    md = f.read()

md_no_h1 = re.sub(r"\A\s*#\s+[^\n]*\n+", "", md, count=1)

html = markdown.markdown(md_no_h1, extensions=["fenced_code", "tables", "sane_lists"])
sys.stdout.write(html)
