#!/usr/bin/env python3
"""Conservative read-only outbound source-link audit for public weight articles.

This is link reachability only, not a medical content review. 403, 429,
CAPTCHA, and network failures are never labeled as proof a source is dead.
"""
import concurrent.futures
from collections import Counter, defaultdict
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "weight" / "articles"
OUTPUT = ROOT / "weight-source-audit"
UA = "JapanMedAI-public-editorial-link-check/1.0"
HOST_LIMIT = defaultdict(lambda: threading.BoundedSemaphore(2))

class ExternalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href", "")
        parsed = urlparse(href)
        if parsed.scheme in ("http","https") and parsed.hostname and not parsed.hostname.endswith("japanmedai.com"):
            self.urls.append(href)

def crawl(url):
    hostname = urlparse(url).hostname or ""
    attempts = 2
    with HOST_LIMIT[hostname]:
        for attempt in range(attempts):
            try:
                req = Request(url, headers={"User-Agent":UA,"Accept":"text/html,application/pdf,*/*","Accept-Encoding":"identity"})
                with urlopen(req, timeout=14) as resp:
                    code = resp.status
                    final = resp.geturl()
                    snippet = resp.read(8192).decode("utf-8", "ignore").lower()
                if "recaptcha" in snippet or "verify you are human" in snippet:
                    return {"url":url,"code":code,"state":"challenge","final_url":final}
                state = "reachable" if 200 <= code < 300 else "other_response"
                return {"url":url,"code":code,"state":state,"final_url":final}
            except HTTPError as e:
                if e.code in (403,401,429,503):
                    return {"url":url,"code":e.code,"state":"restricted_or_rate_limited","reason":str(e)}
                if e.code in (404,410):
                    return {"url":url,"code":e.code,"state":"potential_not_found","reason":str(e)}
                return {"url":url,"code":e.code,"state":"other_http_error","reason":str(e)}
            except (URLError, TimeoutError, OSError) as e:
                if attempt == attempts - 1:
                    return {"url":url,"code":None,"state":"network_inconclusive","reason":str(e)[:180]}
                time.sleep(1.0)

refs = defaultdict(set)
occurrences = 0
for i in range(1,51):
    number = f"{i:03d}"
    file = ARTICLES / f"article-{number}.html"
    html = file.read_text(encoding="utf-8")
    parser=ExternalLinks()
    parser.feed(html)
    occurrences += len(parser.urls)
    for url in parser.urls:
        refs[url].add(number)
distinct = sorted(refs)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    checks=list(pool.map(crawl,distinct))
for obj in checks:
    obj["cited_by"]=sorted(refs[obj["url"]])
counters=Counter(x["state"] for x in checks)
OUTPUT.mkdir(exist_ok=True)
report={
    "source_commit":"b66c42de75c3a950be3b4b9159d6bd2650f2188a",
    "purpose":"External reference URL reachability. No medical claim or source validity is reviewed.",
    "articles_checked":50,
    "source_links_total":occurrences,
    "unique_external_urls":len(distinct),
    "status_counts":dict(counters),
    "checks":checks,
}
(OUTPUT / "report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
lines=[
 "# Weight 50｜外部来源链接只读访问核验",
 "",
 "此处只测网络可达性，不证明医学主张正确，不更换审核稿来源。挑战页/403/429/超时不等于404。",
 "",
 f"- 文章：50/50；外链引用去重数：{len(distinct)}；每种状态：{dict(counters)}",
 "",
 "| 网络状态 | HTTP | 引用篇目 | URL |",
 "|---|---|---|---|",
]
for r in sorted(checks,key=lambda a:(a["state"]=="reachable",a["state"],a["url"])):
    url=r["url"]
    lines.append(f'| {r["state"]} | {r["code"]} | {",".join(r["cited_by"])} | {url.replace("|","%7C")} |')
(OUTPUT / "report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
if os.getenv("GITHUB_STEP_SUMMARY"):
    with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as s:
        s.write("## Weight 50 | External source URL read-only audit\n\n")
        s.write(f"- Unique external URLs: **{len(distinct)}**; states: **{dict(counters)}**\n")
        s.write("- No content edits, no medical claim validation. 403/429/captcha are not proof of 404.\n")
        flagged=[c for c in checks if c["state"]!="reachable"]
        s.write(f"- URLs requiring follow-up: **{len(flagged)}**\n\n")
        for row in flagged[:80]:
            s.write(f'- {row["state"]} ({row["code"]}): {row["url"]} (article {",".join(row["cited_by"])})\n')
print(json.dumps({k:v for k,v in report.items() if k!="checks"},ensure_ascii=False,indent=2))
# Always report observations instead of claiming the referenced page is invalid.
