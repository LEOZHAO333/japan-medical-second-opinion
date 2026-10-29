#!/usr/bin/env python3
"""Read-only production smoke test for the 50 published weight articles.

No authentication, patient data, deployment, index submission, or mutation.
This checks public HTTP responses, not Google indexing.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.japanmedai.com"
ARTICLE_PREFIX = "/weight/articles/article-"
EXPECTED = [f"{ARTICLE_PREFIX}{i:03d}.html" for i in range(1, 51)]
PATHS = ["/", "/robots.txt", "/sitemap.xml", "/weight/library.html", *EXPECTED]
USER_AGENT = "JapanMedAI-public-URL-smoke-test/1.0"

def request_path(path: str) -> dict:
    url = BASE + path
    last_error = ""
    for attempt in range(2):
        try:
            req = Request(url, headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xml,text/plain,*/*",
                "Accept-Encoding": "identity",
            })
            with urlopen(req, timeout=20) as response:
                status = response.status
                final_url = response.geturl()
                body = response.read()
                content_type = response.headers.get("Content-Type", "")
                x_robots_tag = response.headers.get("X-Robots-Tag", "")
            if status != 200:
                return {"path": path, "status": status, "result": "FAIL", "reason": "not 200"}
            result = {
                "path": path, "status": status, "result": "PASS",
                "bytes": len(body), "final_url": final_url,
                "sha256": hashlib.sha256(body).hexdigest(),
            }
            if re.search(r"\\bnoindex\\b", x_robots_tag, re.I):
                result.update(result="FAIL", reason="live X-Robots-Tag noindex")
            if path.endswith(".html") and (path.startswith(ARTICLE_PREFIX) or path == "/weight/library.html"):
                html = body.decode("utf-8", errors="replace")
                match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', html, re.I)
                if not match or match.group(1) != url:
                    result.update(result="FAIL", reason="live canonical missing or unexpected")
                if re.search(r'<meta[^>]+(?:noindex|none)', html, re.I):
                    result.update(result="FAIL", reason="live noindex")
                if path.startswith(ARTICLE_PREFIX):
                    if "application/ld+json" not in html:
                        result.update(result="FAIL", reason="structured data missing")
                    local_path = ROOT / path.lstrip("/")
                    if local_path.exists():
                        result["same_bytes_as_b66c42de"] = body == local_path.read_bytes()
                    else:
                        result["same_bytes_as_b66c42de"] = None
            if path == "/sitemap.xml":
                try:
                    xml = ET.fromstring(body)
                    locs = {node.text for node in xml.findall(".//{*}loc") if node.text}
                    missing = [p for p in EXPECTED if BASE + p not in locs]
                    result["articles_in_sitemap"] = 50 - len(missing)
                    if missing:
                        result.update(result="FAIL", reason=f"sitemap missing {len(missing)} article URLs")
                except ET.ParseError as exc:
                    result.update(result="FAIL", reason=f"sitemap invalid XML: {exc}")
            return result
        except HTTPError as exc:
            return {"path": path, "status": exc.code, "result": "FAIL", "reason": str(exc)}
        except (URLError, TimeoutError, OSError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt == 0:
                time.sleep(1)
    return {"path": path, "status": None, "result": "FAIL", "reason": last_error}

def main() -> int:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(request_path, PATHS))
    failed = [r for r in results if r["result"] != "PASS"]
    articles = [r for r in results if r["path"].startswith(ARTICLE_PREFIX)]
    matches = [r for r in articles if r.get("same_bytes_as_b66c42de") is True]
    mismatches = [r for r in articles if r.get("same_bytes_as_b66c42de") is False]
    print(json.dumps({
        "source_commit": "b66c42de75c3a950be3b4b9159d6bd2650f2188a",
        "checks": len(results), "http_200": sum(r.get("status") == 200 for r in results),
        "article_200": sum(r.get("status") == 200 for r in articles),
        "matching_article_bytes": len(matches),
        "nonmatching_article_bytes": len(mismatches),
        "failed": len(failed),
        "failure_details": failed, "content_mismatch_paths": [r["path"] for r in mismatches],
    }, ensure_ascii=False, indent=2))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## 50 weight articles | live public HTTP test\n\n")
            f.write("Source: `b66c42de`. This does **not** confirm Google indexing.\n\n")
            f.write(f"- HTTP 200: **{sum(r.get('status') == 200 for r in results)}/{len(results)}**\n")
            f.write(f"- Article HTTP 200: **{sum(r.get('status') == 200 for r in articles)}/50**\n")
            f.write(f"- Article byte-for-byte matches: **{len(matches)}/50**\n")
            f.write(f"- Failing checks: **{len(failed)}**\n\n")
            if failed:
                f.write("| Path | Status | Reason |\n|---|---|---|\n")
                for r in failed[:55]:
                    f.write(f"| `{r['path']}` | {r.get('status')} | {str(r.get('reason', ''))[:180].replace('|', '/')} |\n")
            if mismatches:
                f.write("\nContent differs from checked-out production commit: " + ", ".join(r["path"] for r in mismatches) + "\n")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
