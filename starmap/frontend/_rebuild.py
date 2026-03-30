#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Move panel to left side using CSS order + fix borders"""

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

changes = 0

# 1. Add order:1 to sidePanel and order:2 to map via CSS
# Find the #sidePanel CSS rule and add order:1
old_side = "display:flex;flex-direction:column;overflow:hidden;flex-shrink:0;"
new_side = "display:flex;flex-direction:column;overflow:hidden;flex-shrink:0;order:1;"
if old_side in html and "order:1" not in html.split("#sidePanel")[1][:500]:
    html = html.replace(old_side, new_side, 1)
    changes += 1
    print("1. Added order:1 to sidePanel")

# 2. Add order:2 to #map
old_map = "#map{flex:1;height:100%;min-width:0}"
new_map = "#map{flex:1;height:100%;min-width:0;order:2}"
if old_map in html:
    html = html.replace(old_map, new_map)
    changes += 1
    print("2. Added order:2 to map")

# 3. Change border-left to border-right on sidePanel
html = html.replace(
    "border-left:1px solid rgba(255,255,255,.06);display:flex;flex-direction:column",
    "border-right:1px solid rgba(255,255,255,.06);display:flex;flex-direction:column"
)
# Also fix the border in collapsed state
html = html.replace(
    "#sidePanel.collapsed{width:0;border-left:none}",
    "#sidePanel.collapsed{width:0;border-right:none}"
)
changes += 1
print("3. Changed border-left to border-right")

# 4. Fix shadow direction
html = html.replace(
    "box-shadow:-8px 0 32px rgba(0,0,0,.3)}",
    "box-shadow:8px 0 32px rgba(0,0,0,.3)}"
)
changes += 1
print("4. Fixed shadow direction")

# 5. Move panelTab to right side
html = html.replace(
    "left:-26px;top:50%;transform:translateY(-50%);width:26px;height:56px;",
    "right:-26px;top:50%;transform:translateY(-50%);width:26px;height:56px;"
)
html = html.replace(
    "left:-28px;top:50%;transform:translateY(-50%);width:28px;height:60px;",
    "right:-28px;top:50%;transform:translateY(-50%);width:28px;height:60px;"
)
# Fix border radius
html = html.replace(
    "border-right:none;border-radius:10px 0 0 10px;",
    "border-left:none;border-radius:0 10px 10px 0;"
)
html = html.replace(
    "border-right:none;border-radius:12px 0 0 12px;",
    "border-left:none;border-radius:0 12px 12px 0;"
)
changes += 1
print("5. Moved panelTab to right side")

# 6. Fix panelTab arrow
html = html.replace(
    '<div id="panelTab">\u25c0</div>',  # ◀
    '<div id="panelTab">\u25b6</div>'   # ▶
)
# Fix toggle direction
html = html.replace(
    'p.classList.contains("collapsed")?"\u25b6":"\u25c0"',
    'p.classList.contains("collapsed")?"\u25c0":"\u25b6"'
)
changes += 1
print("6. Fixed panelTab arrows")

# 7. Rename "右侧面板" comment to "左侧面板"
html = html.replace("右侧面板：iOS 风格", "左侧面板")
changes += 1
print("7. Updated comment")

print(f"\nTotal changes: {changes}")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Done!")
