#!/usr/bin/env python3
"""Build /kampo/NNN/ long-form articles (051+) from content/kampo-articles/NNN.md.
Run: python3 scripts/build_kampo_articles.py [--check]
Each source: JSON header in <!--json ... --> then a Markdown-lite body
('## '/'### ' headings, '- ' lists, '1. ' lists, '> ' quotes, '|' tables, blank-line paragraphs).
Gate (S0): body >= 1500 chars, >= 3 specific https sources, >= 3 FAQs, verified date,
no internal/workflow words, related links resolve. Also keeps /kampo/ hub cards + ItemList,
root and /kampo/ sitemaps, and /kampo/llms*.txt entries in sync (idempotent).
"""
import html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = "https://www.japanmedai.com"
SRC = ROOT / "content/kampo-articles"
BAD = ("草稿", "待审核", "待医学", "复审", "GEO", "SEO", "Claude", "GPT", "主仓", "私库", "BLOCKED", "DRAFT",
       "知乎专栏", "德川在東京｜日本汉方专题", "日宠通")
LABEL = "日本汉方"
e = lambda x: html.escape(str(x), quote=True)
CARD_START, CARD_END = "<!--kampo-articles:start-->", "<!--kampo-articles:end-->"
LLMS_START, LLMS_END = "<!-- kampo-articles:start -->", "<!-- kampo-articles:end -->"


def ld(o):
    return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "</script>"


def parse(path):
    m = re.match(r"<!--json\n(.*?)\n-->\n(.*)", path.read_text(encoding="utf-8"), re.S)
    assert m, f"{path}: missing JSON header"
    return json.loads(m.group(1)), m.group(2).strip()


def inline(x):
    return e(x)


def body_html(body):
    out = []
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        if block.startswith("### "):
            out.append("<h3>" + inline(block[4:]) + "</h3>")
        elif block.startswith("## "):
            out.append("<h2>" + inline(block[3:]) + "</h2>")
        elif block.startswith("|") and re.search(r"\n\|[-| :]+\|", block):
            rows = [r.strip().strip("|").split("|") for r in lines if not re.match(r"^\|[-| :]+\|$", r.strip())]
            out.append('<div class="tableWrap"><table><thead><tr>' + "".join("<th>" + inline(c.strip()) + "</th>" for c in rows[0])
                       + "</tr></thead><tbody>" + "".join("<tr>" + "".join("<td>" + inline(c.strip()) + "</td>" for c in r) + "</tr>" for r in rows[1:])
                       + "</tbody></table></div>")
        elif all(l.startswith("> ") or l == ">" for l in lines):
            out.append("<blockquote><p>" + "<br>".join(inline(l[2:]) for l in lines) + "</p></blockquote>")
        elif all(l.startswith("- ") for l in lines):
            out.append("<ul>" + "".join("<li>" + inline(l[2:]) + "</li>" for l in lines) + "</ul>")
        elif all(re.match(r"^\d+\. ", l) for l in lines):
            out.append("<ol>" + "".join("<li>" + inline(re.sub(r"^\d+\. ", "", l)) + "</li>" for l in lines) + "</ol>")
        else:
            # paragraph possibly followed by a list (e.g. "说明：\n- a\n- b")
            para, items = [], []
            for l in lines:
                (items if l.startswith("- ") or items else para).append(l)
            if para:
                out.append("<p>" + "<br>".join(inline(x) for x in para) + "</p>")
            if items:
                out.append("<ul>" + "".join("<li>" + inline(x[2:]) + "</li>" for x in items) + "</ul>")
    return "".join(out)


def gate(meta, body, path):
    blob = json.dumps(meta, ensure_ascii=False) + body
    bad = [b for b in BAD if b in blob]
    assert not bad, (path.name, "internal words", bad)
    n = len(re.sub(r"[#\s]", "", body))
    assert n >= 1500, (path.name, "body under 1500 chars", n)
    assert len(meta["sources"]) >= 3, (path.name, "needs >=3 sources")
    for s in meta["sources"]:
        assert s["url"].startswith("https://") and s["url"].rstrip("/").count("/") >= 3, (path.name, s["url"])
        assert len(s["label"]) >= 10, (path.name, "source label too short", s["label"])
    assert len(meta["faqs"]) >= 3 and all(len(f["a"]) >= 20 for f in meta["faqs"]), (path.name, "FAQ")
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["verified"]), (path.name, "verified date")
    ids = {p.stem for p in SRC.glob("[0-9][0-9][0-9].md")}
    for r in meta["related"]:
        u = r["url"].split("#")[0].strip("/")
        ok = (ROOT / u / "index.html").is_file() or (u.startswith("kampo/") and u.split("/")[-1] in ids)
        assert ok, (path.name, "related link missing", r["url"])


def render(meta, body):
    gid = meta["id"]
    url = f"{SITE}/kampo/{gid}/"
    title, desc = meta["title"], meta["description"]
    T = e(title) + "｜JapanMedAI"
    art = {"@context": "https://schema.org", "@type": "MedicalWebPage", "headline": title, "description": desc, "url": url,
           "datePublished": meta["published"], "dateModified": meta["verified"], "lastReviewed": meta["verified"], "inLanguage": "zh-CN",
           "about": [LABEL, title], "author": {"@type": "Organization", "name": "JapanMedAI 编辑部｜文腾株式会社"},
           "publisher": {"@type": "Organization", "name": "JapanMedAI｜文腾株式会社", "url": SITE + "/"},
           "isPartOf": {"@type": "CollectionPage", "name": LABEL, "url": f"{SITE}/kampo/"},
           "citation": [s["url"] for s in meta["sources"]]}
    if meta.get("zhihu_url"):
        art["sameAs"] = meta["zhihu_url"]
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "JapanMedAI", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": LABEL, "item": f"{SITE}/kampo/"},
        {"@type": "ListItem", "position": 3, "name": title, "item": url}]}
    fq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in meta["faqs"]]}
    h = ['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         f'<title>{T}</title><meta name="description" content="{e(desc)}"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><link rel="canonical" href="{url}">',
         f'<meta property="og:type" content="article"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="{T}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary">',
         '<link rel="stylesheet" href="/assets/jmai.css">',
         '<style>main.article{max-width:860px;margin:0 auto;padding:0 16px 48px;box-sizing:border-box}.guide p,.guide li{line-height:1.9}.guide h2{margin-top:2em}.guide .meta{color:#5b6b7a;font-size:14px}.guide .faq h3{margin-top:1.2em}.guide .tableWrap{overflow-x:auto}.guide table{border-collapse:collapse;width:100%;font-size:15px}.guide th,.guide td{border:1px solid #d6e2ea;padding:8px;text-align:left}.guide blockquote{margin:1em 0;padding:8px 16px;border-left:4px solid #b9cfdc;background:#f5f9fb}</style>',
         ld(art), ld(bc), ld(fq), '</head><body>',
         '<div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本专家医疗决策平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/kampo/">日本汉方</a><a href="/kampo/qa/">汉方100问</a><a href="/second-opinion/">二次会诊</a></nav></div></div>',
         f'<main class="article guide"><div class="crumb"><a href="/">首页</a> › <a href="/kampo/">{LABEL}</a> › 第{int(gid)}篇</div><article><header><span class="kicker">JAPANESE KAMPO</span><h1>{e(title)}</h1>',
         f'<p class="meta">JapanMed AI 编辑部｜发布：{meta["published"]}｜资料核对：{meta["verified"]}｜编辑与医学合规审核，未经执业医师逐篇签署</p></header>',
         body_html(body),
         '<section class="faq"><h2>常见问题</h2>' + "".join("<h3>" + e(f["q"]) + "</h3><p>" + e(f["a"]) + "</p>" for f in meta["faqs"]) + "</section>",
         '<section class="evidencePanel"><h2>可以去哪里核对</h2><ul>' + "".join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["label"])}</a></li>' for s in meta["sources"])
         + f'</ul><p>资料核对日期：{meta["verified"]}。具体产品的效能、组成、禁忌和警示，请以该产品最新版说明书为准；标注“厂家示例”的链接仅用于说明说明书写法，不代表推荐某一厂家。</p></section>',
         '<section class="decisionPath"><h2>延伸阅读</h2><div class="relatedGrid">' + "".join(f'<a href="{e(r["url"])}">{e(r["text"])} →</a>' for r in meta["related"])
         + '<a href="/kampo/qa/">日本汉方100问 →</a><a href="/kampo/">查看日本汉方专题 →</a></div></section>',
         '<p class="small">本页为医学信息教育，不替代医生诊断、处方或用药建议；不推荐购买任何具体产品。</p>',
         '</article></main><footer class="footer"><div class="wrap"><span class="footerBrand">JapanMedAI · 文腾株式会社</span><br>内容用于医学信息教育与跨境医疗决策准备，不替代执业医疗团队诊疗。</div></footer><script src="/assets/jmai-analytics.js"></script></body></html>']
    return "".join(h) + "\n"


def sync_hub(text, items):
    cards = CARD_START + "".join(
        f'\n<a class="card" href="/kampo/{m["id"]}/" data-jmai-track="hub" data-jmai-id="hub_kampo_{m["id"]}" data-jmai-position="hub"><h3>{e(m["title"])}</h3></a>'
        for m in items) + "\n" + CARD_END
    if CARD_START in text:
        text = re.sub(re.escape(CARD_START) + ".*?" + re.escape(CARD_END), lambda _: cards, text, flags=re.S)
    else:
        anchor = 'data-jmai-id="hub_kampo_050" data-jmai-position="hub"><h3>怎么看一篇“日本汉方神方”文章是否可信？</h3></a>'
        assert anchor in text, "kampo hub anchor (050 card) not found"
        text = text.replace(anchor, anchor + "\n" + cards, 1)
    m = None
    for mm in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, re.S):
        if '"ItemList"' in mm.group(1):
            m = mm
            break
    assert m, "kampo hub ItemList JSON-LD not found"
    root = json.loads(m.group(1))

    def find(o):
        if isinstance(o, dict):
            if o.get("@type") == "ItemList":
                return o
            for v in o.values():
                r = find(v)
                if r:
                    return r
        elif isinstance(o, list):
            for v in o:
                r = find(v)
                if r:
                    return r
    obj = find(root)
    assert obj, "ItemList not found inside JSON-LD"
    ours = {f"{SITE}/kampo/{x['id']}/" for x in items}
    lst = [x for x in obj["itemListElement"] if x["url"] not in ours]
    for x in items:
        lst.append({"@type": "ListItem", "url": f"{SITE}/kampo/{x['id']}/", "name": x["title"]})
    obj["itemListElement"] = [{"@type": "ListItem", "position": i, "url": x["url"], "name": x["name"]} for i, x in enumerate(lst, 1)]
    if "numberOfItems" in obj:
        obj["numberOfItems"] = len(lst)
    return text[:m.start(1)] + json.dumps(root, ensure_ascii=False, separators=(",", ":")) + text[m.end(1):]


def sync_sitemap(text, items):
    for m in items:
        loc = f"<loc>{SITE}/kampo/{m['id']}/</loc>"
        line = f"  <url>{loc}<lastmod>{m['verified']}</lastmod></url>\n"
        if loc in text:
            text = re.sub(r"  <url>" + re.escape(loc) + r"<lastmod>[^<]*</lastmod></url>\n", line, text)
        else:
            text = text.replace("</urlset>", line + "</urlset>", 1)
    return text


def sync_llms(text, items):
    block = LLMS_START + "\n## 日本汉方长文（/kampo/051/ 起）\n\n" + "".join(
        f"- {m['title']}：{SITE}/kampo/{m['id']}/\n" for m in items) + LLMS_END
    if LLMS_START in text:
        return re.sub(re.escape(LLMS_START) + ".*?" + re.escape(LLMS_END), lambda _: block, text, flags=re.S)
    return text.rstrip("\n") + "\n\n" + block + "\n"


def main():
    check = "--check" in sys.argv
    stale, items = [], []
    for f in sorted(SRC.glob("[0-9][0-9][0-9].md")):
        meta, body = parse(f)
        assert meta["id"] == f.stem and int(meta["id"]) >= 51, f
        gate(meta, body, f)
        out = ROOT / "kampo" / meta["id"] / "index.html"
        html_ = render(meta, body)
        items.append(meta)
        if check:
            if not out.is_file() or out.read_text(encoding="utf-8") != html_:
                stale.append(str(out.relative_to(ROOT)))
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html_, encoding="utf-8")
    targets = [(ROOT / "kampo/index.html", sync_hub), (ROOT / "sitemap.xml", sync_sitemap), (ROOT / "kampo/sitemap.xml", sync_sitemap),
               (ROOT / "kampo/llms.txt", sync_llms), (ROOT / "kampo/llms-full.txt", sync_llms)]
    for p, fn in targets:
        old = p.read_text(encoding="utf-8")
        new = fn(old, items)
        if check:
            if new != old:
                stale.append(str(p.relative_to(ROOT)))
        elif new != old:
            p.write_text(new, encoding="utf-8")
    if check:
        if stale:
            sys.exit("Out of date: " + ", ".join(stale))
        print("PASS:", len(items), "kampo long-form pages up to date; >=1500 chars, >=3 sources, >=3 FAQ; hub/sitemaps/llms in sync")
        return
    print("Built", len(items), "kampo long-form pages; hub, sitemaps and llms synced")


if __name__ == "__main__":
    main()
