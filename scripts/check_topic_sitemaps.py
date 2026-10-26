#!/usr/bin/env python3
"""Prevent drift between published root and topic XML sitemaps.

This is a repository-only test. It does NOT prove HTTP reachability or that
Google has crawled, accepted, or indexed the listed URLs.
"""
from __future__ import annotations

from datetime import date, datetime
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "www.japanmedai.com"
TOPICS = ("checkup", "bnct", "ips", "medicines", "hospitals", "kampo")
XMLNS = "http://www.sitemaps.org/schemas/sitemap/0.9"
NS = {"sm": XMLNS}


def check_lastmod(value: str, path: Path) -> None:
    """Accept W3C-style ISO dates or timezone-aware ISO date-times."""
    try:
        if "T" in value:
            timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                raise ValueError("timezone is required for date-time values")
        else:
            date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid sitemap <lastmod> {value!r} in {path}") from exc


def sitemap_entries(path: Path) -> dict[str, str | None]:
    tree = ET.parse(path)
    if tree.getroot().tag != f"{{{XMLNS}}}urlset":
        raise ValueError(f"Not a sitemap <urlset>: {path}")
    entries: dict[str, str | None] = {}
    for node in tree.findall("sm:url", NS):
        link = node.findtext("sm:loc", default="", namespaces=NS).strip()
        if not link:
            raise ValueError(f"Empty sitemap URL: {path}")
        u = urlsplit(link)
        if u.scheme != "https" or u.netloc != DOMAIN or u.query or u.fragment:
            raise ValueError(f"Unexpected sitemap URL: {link}")
        if link in entries:
            raise ValueError(f"Duplicate sitemap URL: {link}")
        lastmod = node.findtext("sm:lastmod", default=None, namespaces=NS)
        if lastmod is not None:
            lastmod = lastmod.strip()
            check_lastmod(lastmod, path)
        entries[link] = lastmod
    return entries


def redirect_ids_for(section: str, redirects: list[dict]) -> set[str]:
    ids: set[str] = set()
    prefix = f"/{section}/:id("
    for entry in redirects:
        src = entry.get("source", "")
        if not src.startswith(prefix):
            continue
        suffix = src.split(":id(", 1)[1]
        if ")" not in suffix:
            continue
        group = suffix.split(")", 1)[0]
        ids.update(group.split("|"))
    return ids


def main() -> int:
    root = sitemap_entries(ROOT / "sitemap.xml")
    redirects = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8")).get("redirects", [])
    errors: list[str] = []
    for section in TOPICS:
        subset = sitemap_entries(ROOT / section / "sitemap.xml")
        required = {u: d for u, d in root.items() if urlsplit(u).path.startswith(f"/{section}/")}
        missing = sorted(required.keys() - subset.keys())
        different_lastmod = sorted(
            u for u in required.keys() & subset.keys()
            if required[u] != subset[u]
        )
        retired = redirect_ids_for(section, redirects)
        obsolete = sorted(
            u for u in subset
            if (lambda segments: len(segments) == 2 and segments[1] in retired)(
                [x for x in urlsplit(u).path.split("/") if x]
            )
        )
        if missing:
            errors.append(
                f"{section}: {len(missing)} root URLs absent from child: " + ", ".join(missing[:4])
            )
        if different_lastmod:
            errors.append(
                f"{section}: {len(different_lastmod)} root/child lastmod mismatches: "
                + ", ".join(different_lastmod[:4])
            )
        if obsolete:
            errors.append(
                f"{section}: redirected/retired URLs must not be submitted: "
                + ", ".join(obsolete[:4])
            )
        print(
            f"{section}: root {len(required)}, child {len(subset)}, "
            f"missing {len(missing)}, date_mismatch {len(different_lastmod)}, retired {len(obsolete)}"
        )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Topic sitemap alignment and lastmod: PASS. Not an HTTP or Google indexing test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
