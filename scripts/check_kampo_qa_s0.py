#!/usr/bin/env python3
"""Read-only quality gate for Kampo 100Q HTML pages. No network needed."""
from pathlib import Path
import re
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {"concepts":14, "quality":9, "indications":36, "safety":23, "evidence":18}
BANNED = re.compile(r"津村|ツムラ|クラシエ|コタロー|Tsumura|Kracie", re.I)

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.canonicals = []
        self.robots = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h2" and re.fullmatch(r"s-\d{3}", attrs.get("id", "")):
            self.ids.append(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        if tag == "meta" and attrs.get("name") == "robots":
            self.robots.append(attrs.get("content"))

def main():
    seen = []
    pages = ["kampo/qa/index.html"] + [f"kampo/qa/{name}/index.html" for name in TOPICS]
    for path in pages:
        file = ROOT / path
        assert file.is_file(), f"Missing page: {path}"
        source = file.read_text(encoding="utf-8")
        assert not BANNED.search(source), f"Brand term in {path}"
        assert "BreadcrumbList" in source, f"No breadcrumbs in {path}"
        assert '<div class="top"><div class="wrap nav navHome">' in source, f"Shared header missing: {path}"
        assert '<nav class="navMenu">' in source, f"Shared navigation missing: {path}"
        assert '<footer class="footer"><div class="wrap">' in source, f"Shared footer missing: {path}"
        assert '<span class="footerBrand">JapanMedAI · 文腾株式会社</span>' in source, f"Footer brand missing: {path}"
        assert 'qa-disclaimer' in source, f"Disclaimer missing: {path}"
        assert '<body class="kampo-qa-page">' in source, f"QA scope missing: {path}"
        assert 'body.kampo-qa-page .top .navMenu{display:flex' in source, f"Mobile navigation override missing: {path}"
        parsed = Page()
        parsed.feed(source)
        assert len(parsed.canonicals) == 1, f"Canonical missing/duplicate: {path}"
        assert parsed.robots == ["index,follow"], f"Unexpected robots: {path}"
        if path != "kampo/qa/index.html":
            name = path.split("/")[2]
            assert len(parsed.ids) == TOPICS[name], f"Count mismatch: {path}"
            seen.extend(parsed.ids)
            assert source.count("<strong>直接回答：</strong>") == TOPICS[name]
            assert source.count("<strong>核对要点：</strong>") == TOPICS[name]
            assert source.count("<strong>来源：</strong>") == TOPICS[name]
        if path != "kampo/qa/index.html":
            assert source.count('class="qa-feedback" data-qid=') == TOPICS[name], f"Feedback count mismatch: {path}"
            assert source.count('data-qa-helpful="true"') == TOPICS[name], f"Positive feedback missing: {path}"
            assert source.count('data-qa-helpful="false"') == TOPICS[name], f"Negative feedback missing: {path}"
            assert 'trackOnce("qa_feedback"' in source, f"Session dedupe missing: {path}"
        for href in parsed.links:
            if href.startswith("/kampo/qa/"):
                target = href.split("#")[0]
                assert (ROOT / target.lstrip("/") / "index.html").is_file(), f"Broken QA link: {href}"
    assert len(seen) == len(set(seen)) == 100, "Duplicate or missing question anchors"
    assert set(seen) == {f"s-{i:03}" for i in range(1,101)}, "Unexpected IDs"
    sitemap = (ROOT / "kampo/sitemap.xml").read_text(encoding="utf-8")
    for path in pages:
        url = "https://www.japanmedai.com/" + path.removesuffix("index.html")
        assert f"<loc>{url}</loc>" in sitemap, f"Sitemap missing {url}"
    index = (ROOT / "kampo/llms.txt").read_text(encoding="utf-8")
    assert len(re.findall(r"/kampo/qa/(?:concepts|quality|indications|safety|evidence)/#s-\d{3}", index)) == 100
    print("PASS: 6 pages, 100 unique anchors and feedback panels, QA links, sitemap + llms references OK")

if __name__ == "__main__":
    main()
