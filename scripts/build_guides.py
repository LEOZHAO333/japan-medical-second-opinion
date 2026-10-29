#!/usr/bin/env python3
"""Build /guide/ long-form pages (日本医疗决策指南) from reviewed sources in content/guide/NNN.md.
Run: python3 scripts/build_guides.py [--check]
Each source file: a JSON header in <!--json ... --> followed by the article body (Markdown-lite:
'## ' and '### ' headings, blank-line separated paragraphs, single newlines kept as line breaks).
Gate (S0): body >= 1500 chars, >= 3 https sources with specific labels, >= 3 FAQs,
verified date present, no internal/workflow words, related links resolve to repository files.
"""
import html, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = "https://www.japanmedai.com"
SRC = ROOT / "content/guide"
BAD = ("草稿", "待审核", "待医学", "复审", "归档说明", "编辑版", "未发布", "GEO", "SEO", "Claude", "GPT",
       "主仓", "私库", "BLOCKED", "DRAFT", "知乎专栏系列草稿", "发布前须")
SERIES = "日本医疗决策指南"
e = lambda x: html.escape(str(x), quote=True)


def ld(o):
    return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "</script>"


def parse(path):
    t = path.read_text(encoding="utf-8")
    m = re.match(r"<!--json\n(.*?)\n-->\n(.*)", t, re.S)
    assert m, f"{path}: missing JSON header"
    meta = json.loads(m.group(1))
    return meta, m.group(2).strip()


def body_html(body):
    out = []
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block:
            continue
        if block.startswith("### "):
            out.append("<h3>" + e(block[4:].strip()) + "</h3>")
        elif block.startswith("## "):
            out.append("<h2>" + e(block[3:].strip()) + "</h2>")
        elif block.startswith("|") and "\n|---" in block:
            rows = [r.strip().strip("|").split("|") for r in block.split("\n") if not re.match(r"^\|[-| ]+\|$", r.strip())]
            head, rest = rows[0], rows[1:]
            out.append('<div class="tableWrap"><table><thead><tr>' + "".join("<th>" + e(c.strip()) + "</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join("<td>" + e(c.strip()) + "</td>" for c in r) + "</tr>" for r in rest) + "</tbody></table></div>")
        else:
            out.append("<p>" + "<br>".join(e(x) for x in block.split("\n")) + "</p>")
    return "".join(out)


def description(meta, body):
    if meta.get("description"):
        return meta["description"]
    paras = [p.strip().replace("\n", "") for p in re.split(r"\n\s*\n", body) if p.strip() and not p.startswith("#")]
    d = ""
    for p in paras:
        d += p
        if len(d) >= 90:
            break
    return d[:150]


def gate(meta, body, path):
    blob = json.dumps(meta, ensure_ascii=False) + body
    bad = [b for b in BAD if b in blob]
    assert not bad, (path.name, "internal words", bad)
    n = len(re.sub(r"[#\s]", "", body))
    assert n >= 1500, (path.name, "body under 1500 chars", n)
    src = meta["sources"]
    assert len(src) >= 3, (path.name, "needs >=3 sources")
    for s in src:
        assert s["url"].startswith("https://") and s["url"].rstrip("/").count("/") >= 3, (path.name, s["url"])
        assert len(s["label"]) >= 10, (path.name, "source label too short", s["label"])
    assert len(meta["faqs"]) >= 3 and all(len(f["a"]) >= 20 for f in meta["faqs"]), (path.name, "FAQ")
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["verified"]), (path.name, "verified date")
    for r in meta["related"]:
        u = r["url"].split("#")[0].lstrip("/")
        assert (ROOT / u / "index.html").is_file() or (ROOT / u).is_file() or u.startswith("guide/"), (path.name, r["url"])


def render(meta, body):
    gid = meta["id"]
    url = f"{SITE}/guide/{gid}/"
    title = meta["title"]
    desc = description(meta, body)
    T = e(title) + "｜日本医疗决策指南｜JapanMedAI"
    art = {"@context": "https://schema.org", "@type": "MedicalWebPage", "headline": title, "description": desc, "url": url,
           "datePublished": meta["published"], "dateModified": meta["verified"], "lastReviewed": meta["verified"], "inLanguage": "zh-CN",
           "author": {"@type": "Organization", "name": "德川在東京｜文腾株式会社"},
           "publisher": {"@type": "Organization", "name": "JapanMedAI｜文腾株式会社", "url": SITE + "/"},
           "isPartOf": {"@type": "CollectionPage", "name": SERIES, "url": f"{SITE}/guide/"},
           "citation": [s["url"] for s in meta["sources"]], "sameAs": meta.get("zhihu_url")}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "JapanMedAI", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": SERIES, "item": f"{SITE}/guide/"},
        {"@type": "ListItem", "position": 3, "name": title, "item": url}]}
    fq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in meta["faqs"]]}
    h = ['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         f'<title>{T}</title><meta name="description" content="{e(desc)}"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><link rel="canonical" href="{url}">',
         f'<meta property="og:type" content="article"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="{T}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary">',
         '<link rel="stylesheet" href="/assets/jmai.css">',
         '<style>.guide p{line-height:1.9}.guide h2{margin-top:2em}.guide .meta{color:#5b6b7a;font-size:14px}.guide .faq h3{margin-top:1.2em}.guide .tableWrap{overflow-x:auto}.guide table{border-collapse:collapse;width:100%;font-size:15px}.guide th,.guide td{border:1px solid #d6e2ea;padding:8px;text-align:left}</style>',
         ld(art), ld(bc), ld(fq), '</head><body>',
         '<div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本专家医疗决策平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/guide/">决策指南</a><a href="/second-opinion/">二次会诊</a><a href="/checkup/qa/">二次会诊问答</a></nav></div></div>',
         f'<main class="article guide"><div class="crumb"><a href="/">首页</a> › <a href="/guide/">{SERIES}</a> › 第{int(gid)}篇</div><article><header><span class="kicker">{SERIES}</span><h1>{e(title)}</h1>',
         f'<p class="meta">德川在東京｜JapanMedAI｜官网发布：{meta["published"]}｜资料核对：{meta["verified"]}</p></header>',
         body_html(body),
         '<section class="faq"><h2>常见问题</h2>' + "".join("<h3>" + e(f["q"]) + "</h3><p>" + e(f["a"]) + "</p>" for f in meta["faqs"]) + "</section>",
         '<section class="evidencePanel"><h2>参考资料</h2><ul>' + "".join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["label"])}</a></li>' for s in meta["sources"]) + f'</ul><p>资料核对日期：{meta["verified"]}。医院流程与费用可能调整，申请前请以各机构最新公开信息为准。</p></section>',
         '<section class="decisionPath"><h2>延伸阅读</h2><div class="relatedGrid">' + "".join(f'<a href="{e(r["url"])}">{e(r["text"])} →</a>' for r in meta["related"]) + '<a href="/second-opinion/">了解日本癌症第二意见服务 →</a></div></section>',
         ('<p class="small">本文首发于“德川在東京”知乎专栏，官网版补充了来源核对与常见问题。本页为医学信息教育，不替代医生诊断、处方或治疗决定；不承诺任何医疗机构接诊。</p>' if meta.get("zhihu_url") else '<p class="small">本文为JapanMedAI原创医学科普。内容基于公开医学与监管资料，不替代医生诊断、处方或治疗决定，也不承诺任何医疗机构接诊。</p>'),
         '</article></main><footer class="footer"><div class="wrap"><span class="footerBrand">JapanMedAI · 文腾株式会社</span><br>内容用于医学信息教育与跨境医疗决策准备，不替代执业医疗团队诊疗。</div></footer><script src="/assets/jmai-analytics.js"></script></body></html>']
    return "".join(h) + "\n", desc


def render_index(items):
    url = f"{SITE}/guide/"
    T = f"{SERIES}｜癌症第二意见与日本医疗决策长文｜JapanMedAI"
    desc = "日本医疗决策指南：围绕癌症第二诊疗意见、资料准备、复发转移后的治疗决策等问题的长文，每篇附官方来源与核对日期。"
    col = {"@context": "https://schema.org", "@type": "CollectionPage", "name": SERIES, "url": url, "description": desc, "inLanguage": "zh-CN",
           "hasPart": [{"@type": "MedicalWebPage", "name": m["title"], "url": f"{SITE}/guide/{m['id']}/"} for m, _ in items]}
    li = "".join(f'<li><a href="/guide/{m["id"]}/">第{int(m["id"])}篇｜{e(m["title"])}</a><br><span class="small">{e(d)}</span></li>' for m, d in items)
    return ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{T}</title><meta name="description" content="{e(desc)}"><meta name="robots" content="index,follow"><link rel="canonical" href="{url}">'
            '<link rel="stylesheet" href="/assets/jmai.css"><style>.guideList li{margin:18px 0;line-height:1.7}</style>' + ld(col) + '</head><body>'
            '<div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本专家医疗决策平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/second-opinion/">二次会诊</a><a href="/checkup/qa/">二次会诊问答</a><a href="/bnct/">BNCT</a></nav></div></div>'
            f'<main class="article"><div class="crumb"><a href="/">首页</a> › {SERIES}</div><h1>{SERIES}</h1><p>{e(desc)}短问题可查看<a href="/checkup/qa/">癌症第二意见100问</a>。</p>'
            f'<ol class="guideList">{li}</ol><p class="small">本栏目为医学信息教育，不替代医生诊断或治疗决定。</p></main>'
            '<footer class="footer"><div class="wrap"><span class="footerBrand">JapanMedAI · 文腾株式会社</span></div></footer><script src="/assets/jmai-analytics.js"></script></body></html>\n')


def main():
    check = "--check" in sys.argv
    stale, items = [], []
    for f in sorted(SRC.glob("[0-9][0-9][0-9].md")):
        meta, body = parse(f)
        assert meta["id"] == f.stem, f
        gate(meta, body, f)
        html_, desc = render(meta, body)
        items.append((meta, desc))
        out = ROOT / "guide" / meta["id"] / "index.html"
        if check:
            if not out.is_file() or out.read_text(encoding="utf-8") != html_:
                stale.append(str(out.relative_to(ROOT)))
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html_, encoding="utf-8")
    idx = ROOT / "guide/index.html"
    ih = render_index(items)
    if check:
        if not idx.is_file() or idx.read_text(encoding="utf-8") != ih:
            stale.append("guide/index.html")
        sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        missing = [m["id"] for m, _ in items if f"{SITE}/guide/{m['id']}/" not in sm]
        assert f"<loc>{SITE}/guide/</loc>" in sm and not missing, ("sitemap missing guide URLs", missing)
        if stale:
            sys.exit("Out of date: " + ", ".join(stale))
        print("PASS:", len(items), "guide pages up to date; >=1500 chars, >=3 sources, >=3 FAQ, no internal words, in sitemap")
        return
    idx.write_text(ih, encoding="utf-8")
    print("Built", len(items), "guide pages + index")


if __name__ == "__main__":
    main()
