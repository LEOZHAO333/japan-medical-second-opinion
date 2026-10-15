#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

SRC_DIR = Path("wordpress")
DEST_DIR = Path("blog")
BASE_URL = "https://www.japanmedai.com/blog/"

# JapanMedicalBlog is the advanced-human-medicine English content stream.
# Veterinary material belongs to a separate editorial line and must not be mirrored here.
EXCLUDED_SOURCES = {
    "2026-10-03-japan-pet-medicine-guide-richongtong.html",
}

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
DESC_RE = re.compile(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>', re.I | re.S)
CANONICAL_RE = re.compile(r'<link\s+rel=["\']canonical["\'][^>]*>', re.I)
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_for_blog(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    canonical = f'{BASE_URL}{source.name}'
    canonical_tag = f'<link rel="canonical" href="{canonical}">'

    if CANONICAL_RE.search(text):
        text = CANONICAL_RE.sub(canonical_tag, text, count=1)
    elif "</head>" in text.lower():
        text = re.sub(r"</head>", canonical_tag + "\n</head>", text, count=1, flags=re.I)

    return text


def article_record(source: Path, text: str) -> dict[str, str]:
    title_match = TITLE_RE.search(text)
    desc_match = DESC_RE.search(text)
    date_match = DATE_RE.match(source.name)
    return {
        "date": date_match.group(1) if date_match else "",
        "title": clean_text(title_match.group(1)) if title_match else source.stem,
        "url": f"/blog/{source.name}",
        "category": "日本先进医疗英文版",
        "description": clean_text(desc_match.group(1)) if desc_match else "",
    }


def main() -> None:
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, str]] = []

    for source in sorted(SRC_DIR.glob("*.html")):
        if source.name in EXCLUDED_SOURCES:
            continue
        normalized = normalize_for_blog(source)
        target = DEST_DIR / source.name
        target.write_text(normalized, encoding="utf-8")
        records.append(article_record(source, normalized))

    records.sort(key=lambda item: (item["date"], item["title"]), reverse=True)
    (DEST_DIR / "articles.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Synced {len(records)} advanced-medical WordPress source files into {DEST_DIR}/")


if __name__ == "__main__":
    main()
