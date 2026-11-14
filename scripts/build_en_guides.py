#!/usr/bin/env python3
"""English summaries of the BNCT and second-opinion pillar guides (/en/bnct-guide/, /en/second-opinion-guide/).

Run: python3 scripts/build_en_guides.py [--check]
Source: content/pillars-en/*.md (JSON header + markdown body). Pages carry hreflang to the zh-CN / zh-TW guides;
the Chinese guides get the matching en alternate via the "path_en" field read by build_pillars.py.
"""
import html, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_pillars import body_html, ld, sync_sitemap, marker_sync, SITE  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "content/pillars-en"
e = lambda x: html.escape(str(x), quote=True)
BAD = ("best", "guarantee", "cure", "miracle", "breakthrough", "only provider", "No.1")


def parse(p):
    m = re.match(r"<!--json\n(.*?)\n-->\n(.*)", p.read_text(encoding="utf-8"), re.S)
    return json.loads(m.group(1)), m.group(2).strip()


def gate(meta, body):
    words = len(re.findall(r"[A-Za-z]+", body))
    assert words >= 500, (meta["id"], "English body under 500 words", words)
    assert len(meta["sources"]) >= 4 and len(meta["faqs"]) >= 5, meta["id"]
    low = (body + json.dumps(meta)).lower()
    bad = [w for w in BAD if re.search(r"\b" + re.escape(w.lower()) + r"\b", low) and not re.search(r"(not|no|cannot|does not|without)\s+(\w+\s+){0,3}" + re.escape(w.lower()), low)]
    assert not bad, (meta["id"], bad)


def render(meta, body):
    url = SITE + meta["path"]
    title = meta["title"]
    T = e(title) + " | JapanMed AI"
    art = {"@context": "https://schema.org", "@type": "MedicalWebPage", "headline": title, "description": meta["description"], "url": url,
           "inLanguage": "en", "datePublished": meta["published"], "dateModified": meta["verified"], "lastReviewed": meta["verified"],
           "author": {"@type": "Organization", "name": "JapanMed AI editorial team, Bunto Co., Ltd."},
           "publisher": {"@id": SITE + "/#organization"}, "citation": [s["url"] for s in meta["sources"]]}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "JapanMed AI", "item": SITE + "/en/"},
        {"@type": "ListItem", "position": 2, "name": title, "item": url}]}
    fq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in meta["faqs"]]}
    alt = (f'<link rel="alternate" hreflang="zh-CN" href="{SITE}{meta["zh"]}"><link rel="alternate" hreflang="zh-TW" href="{SITE}{meta["zh_hant"]}">'
           f'<link rel="alternate" hreflang="en" href="{url}"><link rel="alternate" hreflang="x-default" href="{SITE}{meta["zh"]}">')
    h = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         f'<title>{T}</title><meta name="description" content="{e(meta["description"])}"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><link rel="canonical" href="{url}">', alt,
         f'<meta property="og:type" content="article"><meta property="og:site_name" content="JapanMed AI"><meta property="og:title" content="{T}"><meta property="og:description" content="{e(meta["description"])}"><meta property="og:url" content="{url}"><meta property="og:locale" content="en_US"><meta name="twitter:card" content="summary">',
         '<link rel="stylesheet" href="/assets/jmai.css">',
         '<style>main.article{max-width:860px;margin:0 auto;padding:0 16px 48px;box-sizing:border-box}.guide p,.guide li{line-height:1.75}.guide h2{margin-top:2em}.guide .meta{color:#5b6b7a;font-size:14px}.langSwitch{font-size:14px}</style>',
         ld(art), ld(bc), ld(fq), "</head><body>",
         '<div class="top"><div class="wrap nav navHome"><a class="brand" href="/en/">JapanMed AI<small>Japanese specialist decision support</small></a><nav class="navMenu"><a href="/en/">Home</a><a href="/en/second-opinion-guide/">Second opinion guide</a><a href="/en/bnct-guide/">BNCT guide</a></nav></div></div>',
         f'<main class="article guide"><div class="crumb"><a href="/en/">Home</a> › Guide</div>',
         f'<p class="langSwitch">Also in <a href="{meta["zh"]}">简体中文</a> · <a href="{meta["zh_hant"]}">繁體中文</a> (full article directory in Chinese)</p>',
         f'<article><header><span class="kicker">GUIDE</span><h1>{e(title)}</h1><p class="meta">JapanMed AI editorial team | Published {meta["published"]} | Sources checked {meta["verified"]} | Editorial and medical-compliance review; not individually signed by a licensed physician</p></header>',
         body_html(body),
         '<section class="faq"><h2>Frequently asked questions</h2>' + "".join(f'<h3>{e(f["q"])}</h3><p>{e(f["a"])}</p>' for f in meta["faqs"]) + "</section>",
         '<section class="evidencePanel"><h2>Where to verify</h2><ul>' + "".join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["label"])}</a></li>' for s in meta["sources"]) + f'</ul><p>Sources checked: {meta["verified"]}</p></section>',
         '<p class="small">This page is medical information for education. It does not replace diagnosis, prescription or treatment decisions by your doctors. If symptoms are urgent or worsening quickly, seek local care first.</p>',
         '</article></main><footer class="footer"><div class="wrap"><span class="footerBrand">JapanMed AI · Bunto Co., Ltd. (文腾株式会社)</span></div></footer><script src="/assets/jmai-analytics.js"></script></body></html>']
    return "".join(h) + "\n"


def main():
    check = "--check" in sys.argv
    stale, edits, metas = [], {}, []

    def edit(rel, fn):
        edits[rel] = fn(edits.get(rel, (ROOT / rel).read_text(encoding="utf-8")))

    for f in sorted(SRC.glob("*.md")):
        meta, body = parse(f)
        gate(meta, body)
        metas.append(meta)
        edits[meta["path"].strip("/") + "/index.html"] = render(meta, body)
        edit("sitemap.xml", lambda t, m=meta: sync_sitemap(t, m["path"], m["verified"]))
    llms = "\n## English guides\n\n" + "".join(f'- {m["title"]}: {SITE}{m["path"]}\n' for m in metas)
    edit("llms.txt", lambda t: marker_sync(t, "en-guides", llms, lambda tt, full: tt.rstrip("\n") + "\n\n" + full + "\n"))
    links = ('<section class="guide pillarLinks" style="max-width:860px;margin:24px auto;padding:0 16px"><h2>Guides</h2><ul>'
             + "".join(f'<li><a href="{m["path"]}">{e(m["title"])}</a></li>' for m in metas) + "</ul></section>")

    def anchor(t, full):
        i = t.find("<footer")
        return t[:i] + full + t[i:]
    edit("en/index.html", lambda t: marker_sync(t, "en-guides", links, anchor))
    for rel, new in edits.items():
        p = ROOT / rel
        if not p.is_file() or p.read_text(encoding="utf-8") != new:
            if check:
                stale.append(rel)
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(new, encoding="utf-8")
    if check:
        if stale:
            sys.exit("Out of date: " + ", ".join(stale))
        print("PASS: English guides up to date", [m["path"] for m in metas])
    else:
        print("Built", [m["path"] for m in metas])


if __name__ == "__main__":
    main()
