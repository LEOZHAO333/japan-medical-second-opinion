#!/usr/bin/env python3
"""Verify that published topic URLs in the root sitemap occur in topic sitemaps.

Only checks repository files; it does not crawl the public website or imply
that Google has crawled or indexed any URL.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "www.japanmedai.com"
TOPICS = ("checkup", "bnct", "ips", "medicines", "hospitals")
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def sitemap_urls(path: Path) -> set[str]:
    tree = ET.parse(path)
    result: set[str] = set()
    for node in tree.findall(".//sm:url", NS):
        link = node.findtext("sm:loc", default="", namespaces=NS).strip()
        if not link:
            raise ValueError(f"Empty sitemap URL: {path}")
        u = urlsplit(link)
        if u.scheme != "https" or u.hostname != DOMAIN or u.query or u.fragment:
            raise ValueError(f"Unexpected sitemap URL: {link}")
        if link in result:
            raise ValueError(f"Duplicate sitemap URL: {link}")
        result.add(link)
    return result


def redirect_ids_for(section: str, redirects: list[dict]) -> set[str]:
    ids: set[str] = set()
    prefix = f"/{section}/:id("
    for entry in redirects:
        src = entry.get("source", "")
        if not src.startswith(prefix) or ")/" not in src and not src.endswith(")"):
            continue
        group = src.split(":id(", 1)[1].split(")", 1)[0]
        ids.update(group.split("|"))
    return ids


def main() -> int:
    root = sitemap_urls(ROOT / "sitemap.xml")
    redirects = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8")).get("redirects", [])
    errors: list[str] = []
    for section in TOPICS:
        subset = sitemap_urls(ROOT / section / "sitemap.xml")
        required = {u for u in root if urlsplit(u).path.startswith(f"/{section}/")}
        missing = sorted(required - subset)
        retired = redirect_ids_for(section, redirects)
        obsolete = [
            u for u in subset
            if (lambda segments: len(segments) == 2 and segments[1] in retired)(
                [x for x in urlsplit(u).path.split("/") if x]
            )
        ]
        if missing:
            errors.append(f"{section}: {len(missing)} root sitemap URLs absent from child: " + ", ".join(missing[:4]))
        if obsolete:
            errors.append(f"{section}: redirected/retired URLs must not be submitted: " + ", ".join(obsolete[:4]))
        print(f"{section}: root {len(required)}, child {len(subset)}, missing {len(missing)}, retired {len(obsolete)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Topic sitemap alignment: PASS. This is NOT a Google indexing or HTTP status test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
