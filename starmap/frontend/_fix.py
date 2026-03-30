#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find the exact syntax error by scanning for problematic patterns"""

with open("index.html","r",encoding="utf-8") as f:
    html = f.read()

script_start = html.find("<script>") + 8
script_end = html.rfind("</script>")
script = html[script_start:script_end]
lines = script.split("\n")

print(f"Script has {len(lines)} lines")

# Check for unclosed template literals by tracking backtick state
bt_open = False
bt_line = 0
issues = []

for i, line in enumerate(lines, 1):
    j = 0
    while j < len(line):
        ch = line[j]
        # Skip escaped chars
        if ch == '\\':
            j += 2
            continue
        if ch == '`':
            if bt_open:
                bt_open = False
            else:
                bt_open = True
                bt_line = i
        j += 1

if bt_open:
    print(f"UNCLOSED TEMPLATE LITERAL starting at script line {bt_line}")
    print(f"  Content: {lines[bt_line-1][:100]}")
else:
    print("Template literals: OK")

# Check for unclosed strings
for i, line in enumerate(lines, 1):
    # Count unescaped single quotes (excluding template literals)
    sq = line.count("'") - line.count("\\'")
    if sq % 2 != 0:
        # Could be legitimate (apostrophe in comment etc), just flag
        if not line.strip().startswith("//"):
            issues.append((i, "odd single quotes", line[:80]))

if issues:
    print(f"\nPotential string issues ({len(issues)} lines):")
    for ln, typ, content in issues[:10]:
        print(f"  Line {ln}: {content}")
else:
    print("String quotes: OK")

# Show last 10 lines of script
print("\nLast 10 lines of script:")
for i, l in enumerate(lines[-10:], len(lines)-9):
    print(f"  {i}: {repr(l[:80])}")
