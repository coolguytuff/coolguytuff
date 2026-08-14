#!/usr/bin/env python3
from __future__ import annotations

import collections
import datetime as dt
import html
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "coolguytuff")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = Path(os.environ.get("TELEMETRY_OUT", "assets/telemetry.svg"))
API = "https://api.github.com"
PALETTE = ["#7ff0ff", "#4a7bff", "#a78bfa", "#f472d0", "#6ee7b7"]


def request_json(path: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "coolguytuff-profile-telemetry",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(API + path, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def short_date(value: str | None) -> str:
    if not value:
        return "UNKNOWN"
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.strftime("%b %d").upper()
    except ValueError:
        return "UNKNOWN"


def collect():
    user = request_json(f"/users/{OWNER}")
    repos = request_json(f"/users/{OWNER}/repos?per_page=100&type=owner&sort=pushed")
    public = [repo for repo in repos if not repo.get("private")]
    originals = [repo for repo in public if not repo.get("fork") and repo.get("name") != OWNER]
    forks = [repo for repo in public if repo.get("fork")]

    language_bytes = collections.Counter()
    for repo in public:
        name = repo.get("name")
        if not name:
            continue
        try:
            languages = request_json(f"/repos/{OWNER}/{name}/languages")
            for language, size in languages.items():
                language_bytes[language] += int(size)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, OSError):
            fallback_language = repo.get("language")
            if fallback_language:
                language_bytes[fallback_language] += 1

    latest = max((repo.get("pushed_at") or "" for repo in public), default="")
    return {
        "public_repos": int(user.get("public_repos", len(public))),
        "originals": len(originals),
        "forks": len(forks),
        "latest": short_date(latest),
        "top_langs": language_bytes.most_common(4),
        "ok": True,
    }


def fallback():
    return {
        "public_repos": "—",
        "originals": "—",
        "forks": "—",
        "latest": "UNAVAILABLE",
        "top_langs": [],
        "ok": False,
    }


def render(data) -> str:
    languages = data["top_langs"]
    language_total = sum(count for _, count in languages) or 1
    metric_boxes = [
        ("PUBLIC REPOS", data["public_repos"], "VISIBLE BUILDS"),
        ("ORIGINAL", data["originals"], "NON-FORK REPOS"),
        ("FORKED LABS", data["forks"], "EXPLORATION"),
        ("LAST PUSH", data["latest"], "PUBLIC ACTIVITY"),
    ]

    boxes = []
    for index, (label, value, subtitle) in enumerate(metric_boxes):
        x = 40 + index * 278
        accent = PALETTE[index % len(PALETTE)]
        boxes.append(f'''<g transform="translate({x} 104)">
  <rect width="260" height="132" rx="15" fill="#07111f" fill-opacity=".86" stroke="{accent}" stroke-opacity=".32"/>
  <path d="M0 35H260" stroke="{accent}" stroke-opacity=".10"/>
  <text x="18" y="24" fill="#7f91a8" font-size="10" letter-spacing="2">{esc(label)}</text>
  <text x="18" y="82" fill="{accent}" font-size="35" font-weight="700">{esc(value)}</text>
  <text x="18" y="110" fill="#5f7288" font-size="9.5" letter-spacing="1.4">{esc(subtitle)}</text>
</g>''')

    rows = []
    if languages:
        for index, (language, count) in enumerate(languages):
            y = 306 + index * 42
            fraction = count / language_total
            width = max(55, round(fraction * 650))
            percent = round(fraction * 100)
            color = PALETTE[index % len(PALETTE)]
            rows.append(f'''<g>
  <text x="42" y="{y}" fill="#bac7d8" font-size="11.5">{esc(language.upper())}</text>
  <rect x="190" y="{y - 12}" width="650" height="12" rx="6" fill="#0c1725"/>
  <rect x="190" y="{y - 12}" width="{width}" height="12" rx="6" fill="{color}" fill-opacity=".72"/>
  <text x="868" y="{y}" fill="#71849a" font-size="10">{percent}%</text>
</g>''')
    else:
        rows.append('<text x="42" y="320" fill="#71849a" font-size="12">LANGUAGE MIX // DATA UNAVAILABLE</text>')

    health = "PUBLIC API OK" if data["ok"] else "PUBLIC API DEGRADED"
    health_color = "#6ee7b7" if data["ok"] else "#f0c66a"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 510" role="img" aria-label="GitHub telemetry for {esc(OWNER)}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#020617"/><stop offset=".5" stop-color="#07111f"/><stop offset="1" stop-color="#02040b"/></linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7ff0ff" stop-opacity=".08"/><stop offset=".5" stop-color="#7ff0ff" stop-opacity=".65"/><stop offset="1" stop-color="#a78bfa" stop-opacity=".08"/></linearGradient>
  <pattern id="grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="#6d8cff" stroke-opacity=".055"/></pattern>
</defs>
<rect width="1200" height="510" rx="26" fill="url(#bg)"/>
<rect width="1200" height="510" rx="26" fill="url(#grid)"/>
<g font-family="IBM Plex Mono,JetBrains Mono,ui-monospace,monospace">
  <text x="42" y="52" fill="#d8faff" font-size="18" font-weight="700" letter-spacing="3">GITHUB // TELEMETRY</text>
  <text x="42" y="75" fill="#64748b" font-size="9.5" letter-spacing="1.8">SELF-HOSTED PROFILE DATA • REFRESHED BY GITHUB ACTIONS</text>
  <text x="1158" y="52" text-anchor="end" fill="{health_color}" font-size="10" letter-spacing="1.8">● {health}</text>
  {''.join(boxes)}
  <text x="42" y="272" fill="#7ff0ff" font-size="10.5" letter-spacing="2.2">LANGUAGE SIGNAL // PUBLIC REPO CONTENT</text>
  {''.join(rows)}
  <rect x="914" y="286" width="244" height="160" rx="14" fill="#07111f" fill-opacity=".78" stroke="#315b7e" stroke-opacity=".38"/>
  <text x="934" y="314" fill="#7f91a8" font-size="9.5" letter-spacing="1.7">CURRENT VECTOR</text>
  <text x="934" y="346" fill="#d8faff" font-size="14" font-weight="700">AI SYSTEMS</text>
  <text x="934" y="372" fill="#7ff0ff" font-size="10">AGENTS / AUTOMATION</text>
  <text x="934" y="398" fill="#a78bfa" font-size="10">ORCHESTRATION / EVALS</text>
  <text x="934" y="424" fill="#6ee7b7" font-size="10">BUILDING / ITERATING</text>
  <text x="42" y="482" fill="#53657a" font-size="9.5" letter-spacing="1.4">NO THIRD-PARTY STATS CARD REQUIRED // IF THE API FAILS, THIS PANEL DEGRADES INTENTIONALLY</text>
</g>
<rect x="1" y="1" width="1198" height="508" rx="25" fill="none" stroke="url(#edge)" stroke-opacity=".48"/>
</svg>'''


def main():
    try:
        data = collect()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, OSError) as error:
        print(f"telemetry: API unavailable: {error}")
        data = fallback()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(data), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
