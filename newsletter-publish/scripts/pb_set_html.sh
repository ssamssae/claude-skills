#!/usr/bin/env bash
# Set NSPasteboard with both HTML and plain-text content.
# Usage: pb_set_html.sh <html_path> <plain_path>
set -euo pipefail
HTML="$1"
PLAIN="$2"

osascript <<OSAEOF
use framework "Foundation"
use framework "AppKit"
set pb to current application's NSPasteboard's generalPasteboard()
pb's clearContents()
set htmlNSString to (current application's NSString's stringWithContentsOfFile:"$HTML" encoding:4 |error|:(missing value))
set plainNSString to (current application's NSString's stringWithContentsOfFile:"$PLAIN" encoding:4 |error|:(missing value))
pb's setString:htmlNSString forType:"public.html"
pb's setString:plainNSString forType:"public.utf8-plain-text"
OSAEOF
