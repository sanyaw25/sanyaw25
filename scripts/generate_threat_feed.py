#!/usr/bin/env python3
"""
Generates assets/threat-feed.svg: a scrolling ticker of the most
recently published CVEs, pulled from NIST's public NVD API 2.0
(no key required for this volume of requests). Meant to run daily
via .github/workflows/threat-feed.yml. Falls back to a placeholder
row if the API is unreachable so the README never breaks.
"""
import json
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://services.nvd.nist.gov/rest/json/cves/2.0"

def fetch_recent_cves(n=6):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=3)
    fmt = "%Y-%m-%dT%H:%M:%S.000"
    url = (f"{API}?pubStartDate={start.strftime(fmt)}"
           f"&pubEndDate={end.strftime(fmt)}&resultsPerPage=20")
    req = urllib.request.Request(url, headers={"User-Agent": "readme-threat-feed/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)

    items = []
    for v in data.get("vulnerabilities", []):
        cve = v["cve"]
        cid = cve["id"]
        desc = next((d["value"] for d in cve.get("descriptions", []) if d["lang"] == "en"), "")
        desc = " ".join(desc.split())[:90]
        items.append((cid, desc))

    items.sort(key=lambda x: x[0], reverse=True)
    return items[:n]

def build_svg(items):
    row_texts = []
    x = 40
    for cid, desc in items:
        entry = f"{cid} — {desc}"
        row_texts.append((x, cid, desc))
        x += len(entry) * 8 + 90

    tspans = "".join(
        f'<text x="{pos}" y="34" font-family="Courier New, monospace" font-size="14" fill="#F5EFE6">'
        f'<tspan fill="#B76E79">\u25cf</tspan> <tspan fill="#C9A24B">{cid}</tspan> '
        f'<tspan fill="#F5EFE6">{desc}</tspan></text>'
        for pos, cid, desc in row_texts
    )

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f'''<svg viewBox="0 0 1200 70" width="100%" height="70" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="feedBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#12172A"/>
      <stop offset="100%" stop-color="#0D1117"/>
    </linearGradient>
    <linearGradient id="fadeMask" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="white" stop-opacity="0"/>
      <stop offset="6%" stop-color="white" stop-opacity="1"/>
      <stop offset="94%" stop-color="white" stop-opacity="1"/>
      <stop offset="100%" stop-color="white" stop-opacity="0"/>
    </linearGradient>
    <mask id="edgeFade">
      <rect x="0" y="0" width="1200" height="70" fill="url(#fadeMask)"/>
    </mask>
  </defs>

  <rect x="0" y="0" width="1200" height="70" rx="8" fill="url(#feedBg)" stroke="#C9A24B" stroke-width="1"/>
  <text x="16" y="16" font-family="Courier New, monospace" font-size="10" fill="#8B93A7" letter-spacing="2">LIVE THREAT FEED · NVD · UPDATED {stamp}</text>

  <g mask="url(#edgeFade)">
    <g>
      <animateTransform attributeName="transform" type="translate" from="0,0" to="-{x},0" dur="{max(28, x // 40)}s" repeatCount="indefinite"/>
      {tspans}
      <g transform="translate({x},0)">
        {tspans}
      </g>
    </g>
  </g>
</svg>
'''

def main():
    try:
        items = fetch_recent_cves()
        if not items:
            raise ValueError("no results")
    except Exception as e:
        items = [("FEED-OFFLINE", "Could not reach NVD right now — will retry on next scheduled run.")]

    svg = build_svg(items)
    with open("assets/threat-feed.svg", "w") as f:
        f.write(svg)
    print(f"threat-feed.svg written with {len(items)} entries")

if __name__ == "__main__":
    main()
