#!/usr/bin/env python3
"""
Generates assets/clock (1).svg showing the current time in IST.
Meant to be run on a schedule by .github/workflows/clock.yml,
which commits the regenerated file back to the repo. GitHub
strips <script> from README-rendered SVGs, so this is the only
way to get a genuinely "live" (auto-refreshing) clock in a
profile README rather than a static or purely decorative one.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
now = datetime.now(IST)

time_str = now.strftime("%H:%M")
date_str = now.strftime("%A, %d %b %Y")
synced_str = now.strftime("%H:%M:%S IST")

svg = f'''<svg viewBox="0 0 420 150" width="420" height="150" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="clockBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#12172A"/>
      <stop offset="100%" stop-color="#0D1117"/>
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="416" height="146" rx="12" fill="url(#clockBg)" stroke="#C9A24B" stroke-width="1.4"/>
  <text x="30" y="40" font-family="Courier New, monospace" font-size="13" fill="#8B93A7" letter-spacing="2">LOCAL TIME · NEEMRANA, IN</text>
  <text x="30" y="98" font-family="Courier New, monospace" font-size="52" fill="#F5EFE6" letter-spacing="4">{time_str}</text>
  <text x="30" y="126" font-family="Courier New, monospace" font-size="14" fill="#C9A24B">{date_str}</text>
  <circle cx="388" cy="30" r="4" fill="#C9A24B"/>
  <text x="374" y="118" font-family="Courier New, monospace" font-size="10" fill="#8B93A7" text-anchor="end">synced {synced_str}</text>
</svg>
'''

with open("assets/clock-img.svg", "w") as f:
    f.write(svg)

print(f"clock-img.svg written for {synced_str}")
