#!/usr/bin/env python3
"""Read-only S0 QA gate for staged /checkup/qa/ content. No deploy."""
from pathlib import Path
from html.parser import HTMLParser
import json,re
ROOT=Path(__file__).resolve().parents[1]
class Parse(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.hrefs=[];self.canonical=[];self.robots=[];self.buttons=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="h3" and re.fullmatch(r"so-\d{3}",a.get("id","")):self.ids.append(a["id"])
        if tag=="a":self.hrefs.append(a.get("href",""))
        if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
        if tag=="meta" and a.get("name")=="robots":self.robots.append(a.get("content"))
        if tag=="button" and a.get("data-vote") in ("helpful","needs_work"):self.buttons+=1
def main():
    data=json.loads((ROOT/"content/checkup-qa/first-release-25.json").read_text(encoding="utf-8"))
    questions=data["questions"];assert len(questions)==40
    assert len({q["id"] for q in questions})==40
    src=(ROOT/"checkup/qa/index.html").read_text(encoding="utf-8")
    p=Parse();p.feed(src)
    assert len(p.ids)==len(set(p.ids))==40
    assert set(p.ids)=={q["id"].lower() for q in questions}
    assert p.buttons==80 and src.count("<strong>直接回答：</strong>")==40
    assert src.count("<strong>核对要点：</strong>")==40
    assert src.count("<strong>来源：</strong>")==40
    assert p.canonical==["https://www.japanmedai.com/checkup/qa/"]
    assert p.robots==["index,follow"],"Release page must be indexable"
    assert "BreadcrumbList" in src
    assert "jmai-analytics.js" in src and "checkup-qa-feedback.js" in src
    assert (ROOT/"assets/checkup-qa-feedback.js").is_file()
    for href in p.hrefs:
        if re.fullmatch(r"/checkup/\d{3}/",href):
            assert (ROOT/href.lstrip("/")/"index.html").is_file(),href
    assert '/checkup/qa/' in (ROOT/"checkup/index.html").read_text(encoding="utf-8")
    assert "<loc>https://www.japanmedai.com/checkup/qa/</loc>" in (ROOT/"checkup/sitemap.xml").read_text(encoding="utf-8")
    page=(ROOT/"checkup/qa/index.html").read_text(encoding="utf-8")
    for bad in ("草稿","复审","专业审核待完成","待审核"):
        assert bad not in page, "Draft wording on public page: "+bad
    print("PASS: 40 unique QA, 80 feedback buttons, fields, internal links, canonical, index,follow, hub, sitemap")
if __name__=="__main__":main()
