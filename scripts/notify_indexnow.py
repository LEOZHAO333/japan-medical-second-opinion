#!/usr/bin/env python3
"""Fail-closed IndexNow for specifically approved, changed and live HTML."""
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

HOST = "www.japanmedai.com"
ORIGIN = "https://" + HOST
KEY = "2314dd35f50668e36564dfd274329af5"
MAX_URLS = 20

class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = None
        self.noindex = False
    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "meta" and data.get("name", "").lower() in ("robots", "bingbot"):
            self.noindex |= "noindex" in data.get("content", "").lower()
        if tag == "link" and "canonical" in data.get("rel", "").lower().split():
            self.canonical = data.get("href")

def parse_head(body):
    parser = Head()
    parser.feed(body.decode("utf-8"))
    return parser

def sitemap_urls():
    urls = set()
    for path in Path(".").rglob("sitemap.xml"):
        if any(part in (".git", "node_modules", ".venv") for part in path.parts):
            continue
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root.iter():
            if node.tag.rsplit("}", 1)[-1] == "loc" and node.text:
                urls.add(node.text.strip())
    return urls

def changed_html(before, after):
    if not all(re.fullmatch(r"[0-9a-f]{40}", x or "") for x in (before, after)) or before == "0" * 40:
        print("SKIP: invalid commit range")
        return []
    parts = subprocess.check_output(["git", "diff", "--name-status", "-z", before, after]).decode().split("\0")
    return [parts[i+1] for i in range(0, len(parts)-1, 2)
            if parts[i] in ("A", "M") and parts[i+1].endswith(".html")]

def url_for(path):
    if path == "index.html":
        return ORIGIN + "/"
    if path.endswith("/index.html"):
        return ORIGIN + "/" + path[:-len("index.html")]
    return ORIGIN + "/" + path

def live_matches(url, content):
    request = urllib.request.Request(url, headers={"User-Agent": "JapanMedAI-IndexNow/1.0"})
    with urllib.request.urlopen(request, timeout=15) as response:
        if response.status != 200 or response.geturl() != url or "text/html" not in response.headers.get("Content-Type", ""):
            return False
        production = response.read()
    head = parse_head(production)
    return (hashlib.sha256(production).digest() == hashlib.sha256(content).digest()
            and not head.noindex and head.canonical == url)

def main():
    approved = {s.strip() for s in Path(".github/indexnow-approved-urls.txt").read_text().splitlines()
                if s.strip() and not s.lstrip().startswith("#")}
    listed = sitemap_urls()
    eligible = []
    for path in changed_html(os.getenv("BEFORE_SHA"), os.getenv("AFTER_SHA")):
        url = url_for(path)
        if url not in approved or url not in listed or not Path(path).is_file():
            print("SKIP not approved/published:", url)
            continue
        local = Path(path).read_bytes()
        head = parse_head(local)
        if head.noindex or head.canonical != url:
            print("SKIP noindex or canonical mismatch:", url)
            continue
        eligible.append((url, local))
    if not eligible:
        print("No eligible changed HTML; nothing sent.")
        return
    if len(eligible) > MAX_URLS:
        raise SystemExit("SAFETY HOLD: too many eligible URLs in one release")
    urls = []
    for url, local in eligible:
        for attempt in range(6):
            try:
                if live_matches(url, local):
                    urls.append(url)
                    break
            except Exception as error:
                print("Production not ready:", url, type(error).__name__, str(error))
            if attempt < 5:
                time.sleep(20)
        else:
            print("HOLD: production HTML did not match this release:", url)
    if not urls:
        print("No verified production URL; nothing sent.")
        return
    payload = json.dumps({"host": HOST, "key": KEY, "urlList": urls}).encode("utf-8")
    request = urllib.request.Request(
        "https://api.indexnow.org/indexnow", data=payload, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = response.status
    except urllib.error.HTTPError as error:
        status = error.code
    print("IndexNow HTTP:", status, "submitted:", urls)
    if status not in (200, 202):
        raise SystemExit("IndexNow API did not accept notification")

if __name__ == "__main__":
    main()
