#!/usr/bin/env python3
"""Build the 3 core pillar guides (Simplified + Traditional Chinese) from content/pillars/*.md.

Run: python3 scripts/build_pillars.py [--check]
Needs: pip install opencc-python-reimplemented==0.1.7 (Traditional conversion, s2twp).

Each pillar page = hand-written guide body + FAQ + sources + an auto-generated directory that links every
matching article on the site (grouped by regex on the URL path). Also keeps in sync (idempotent markers):
root sitemap + section sitemaps, root llms.txt, the section hub callout, and /zh-hant/ links.
"""
import html, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from expert_opinion_module import module_html  # noqa: E402
import pillar_links  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = "https://www.japanmedai.com"
SRC = ROOT / "content/pillars"
SKIP_DIRS = ("drafts", "wordpress", "blogger", "node_modules", ".git", "content", "scripts", "assets")
e = lambda x: html.escape(str(x), quote=True)
_cc = None


def hant(text):
    global _cc
    if _cc is None:
        import opencc
        _cc = opencc.OpenCC("s2twp")
    return _cc.convert(text).replace("釋出", "發布")


def ld(o):
    return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "</script>"


def parse(p):
    m = re.match(r"<!--json\n(.*?)\n-->\n(.*)", p.read_text(encoding="utf-8"), re.S)
    assert m, p
    return json.loads(m.group(1)), m.group(2).strip()


def site_pages():
    pages = {}
    for f in ROOT.rglob("index.html"):
        rel = f.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS:
            continue
        path = "/" + "/".join(rel.parts[:-1]) + ("/" if len(rel.parts) > 1 else "")
        m = re.search(r"<title>([^<]*)</title>", f.read_text(encoding="utf-8", errors="ignore"))
        if m:
            t = re.split(r"｜JapanMed ?AI|\|JapanMed ?AI", m.group(1))[0].strip()
            pages[path] = html.unescape(t)
    return pages


def body_html(body):
    out = []
    for block in re.split(r"\n\s*\n", body.strip()):
        lines = block.strip().split("\n")
        if block.startswith("## "):
            out.append("<h2>" + e(block[3:]) + "</h2>")
        elif all(l.startswith("- ") for l in lines):
            out.append("<ul>" + "".join("<li>" + e(l[2:]).replace("**", "") + "</li>" for l in lines) + "</ul>")
        elif all(re.match(r"^\d+\. ", l) for l in lines):
            out.append("<ol>" + "".join("<li>" + e(re.sub(r"^\d+\. ", "", l)).replace("**", "") + "</li>" for l in lines) + "</ol>")
        else:
            out.append("<p>" + "<br>".join(e(l) for l in lines).replace("**", "") + "</p>")
    # bold markers -> <strong>
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", "".join(out))


def directory(meta, pages):
    groups, used = [], set()
    for g in meta["directory"]:
        rx = re.compile(g["match"])
        items = sorted((p, t) for p, t in pages.items() if rx.search(p) and p not in used and p not in (meta["path"],))
        used.update(p for p, _ in items)
        if items:
            groups.append((g["title"], items))
    return groups


def gate(meta, body, groups):
    n = len(re.sub(r"[#\s*]", "", body))
    assert n >= 1200, (meta["id"], "pillar body under 1200 chars", n)
    assert len(meta["sources"]) >= 4 and all(s["url"].startswith("https://") and s["url"].rstrip("/").count("/") >= 3 for s in meta["sources"]), meta["id"]
    assert len(meta["faqs"]) >= 5, meta["id"]
    total = sum(len(i) for _, i in groups)
    assert total >= 20, (meta["id"], "directory too small", total)
    bad = [w for w in ("Claude", "GPT", "草稿", "待审核", "日宠通", "唯一", "最好", "保证", "治愈", "根治") if w in re.sub(r"不能保证|不保证", "", body + json.dumps(meta, ensure_ascii=False))]
    assert not bad, (meta["id"], bad)


def render(meta, body, groups, lang):
    tr = (lambda s: s) if lang == "zh-CN" else hant
    path = meta["path"] if lang == "zh-CN" else meta["path_hant"]
    url = SITE + path
    alt = {"zh-CN": SITE + meta["path"], "zh-TW": SITE + meta["path_hant"]}
    title, desc = tr(meta["title"]), tr(meta["description"])
    T = e(title) + "｜JapanMedAI"
    total = sum(len(i) for _, i in groups)
    sec = meta["section"]
    hub = "/" + sec + "/"
    art = {"@context": "https://schema.org", "@type": "MedicalWebPage", "headline": title, "description": desc, "url": url,
           "inLanguage": lang if lang == "zh-CN" else "zh-Hant", "datePublished": meta["published"], "dateModified": meta["verified"],
           "lastReviewed": meta["verified"], "author": {"@type": "Organization", "name": "JapanMedAI 编辑部｜文腾株式会社"},
           "publisher": {"@type": "Organization", "name": "JapanMedAI｜文腾株式会社 Bunto Co., Ltd.", "url": SITE + "/"},
           "citation": [s["url"] for s in meta["sources"]],
           "hasPart": [{"@type": "WebPage", "url": SITE + p, "name": tr(t)} for _, items in groups for p, t in items][:200]}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "JapanMedAI", "item": SITE + ("/" if lang == "zh-CN" else "/zh-hant/")},
        {"@type": "ListItem", "position": 2, "name": tr(meta["label"]), "item": SITE + hub},
        {"@type": "ListItem", "position": 3, "name": title, "item": url}]}
    fq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": tr(f["q"]), "acceptedAnswer": {"@type": "Answer", "text": tr(f["a"])}} for f in meta["faqs"]]}
    a2 = ""
    if sec in ("bnct", "second-opinion"):
        a2 = module_html("bnct" if sec == "bnct" else "default")
        a2 = a2 if lang == "zh-CN" else hant(a2)
    note = "" if lang == "zh-CN" else '<p class="small">下方目錄中的文章為簡體中文頁面。</p>'
    dir_html = ('<section class="pillarDir"><h2>' + tr("全部相关文章目录") + f'（{total}）</h2>' + note
                + "".join('<h3>' + e(tr(gt)) + f'（{len(items)}）</h3><ul>' + "".join(f'<li><a href="{p}">{e(tr(t))}</a></li>' for p, t in items) + "</ul>" for gt, items in groups)
                + "</section>")
    nav_home = "/" if lang == "zh-CN" else "/zh-hant/"
    h = ['<!doctype html><html lang="' + ("zh-CN" if lang == "zh-CN" else "zh-Hant") + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         f'<title>{T}</title><meta name="description" content="{e(desc)}"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><link rel="canonical" href="{url}">',
         f'<link rel="alternate" hreflang="zh-CN" href="{alt["zh-CN"]}"><link rel="alternate" hreflang="zh-TW" href="{alt["zh-TW"]}"><link rel="alternate" hreflang="x-default" href="{alt["zh-CN"]}">',
         f'<meta property="og:type" content="article"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="{T}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:locale" content="{"zh_CN" if lang == "zh-CN" else "zh_TW"}"><meta name="twitter:card" content="summary">',
         '<link rel="stylesheet" href="/assets/jmai.css">',
         '<style>main.article{max-width:860px;margin:0 auto;padding:0 16px 48px;box-sizing:border-box}.guide p,.guide li{line-height:1.9}.guide h2{margin-top:2em}.guide .meta{color:#5b6b7a;font-size:14px}.pillarDir h3{margin-top:1.4em}.pillarDir li{line-height:1.7}.langSwitch{font-size:14px}</style>',
         ld(art), ld(bc), ld(fq), "</head><body>",
         f'<div class="top"><div class="wrap nav navHome"><a class="brand" href="{nav_home}">JapanMed AI<small>{e(tr("日本专家医疗决策平台"))}</small></a><nav class="navMenu"><a href="{nav_home}">{e(tr("首页"))}</a><a href="/second-opinion/guide/">{e(tr("第二意见指南"))}</a><a href="/bnct/guide/">{e(tr("BNCT评估指南"))}</a><a href="/kampo/guide/">{e(tr("汉方用药指南"))}</a></nav></div></div>',
         f'<main class="article guide"><div class="crumb"><a href="{nav_home}">{e(tr("首页"))}</a> › <a href="{hub}">{e(tr(meta["label"]))}</a> › {e(tr("指南"))}</div>',
         '<p class="langSwitch">' + (f'<a href="{meta["path_hant"]}">繁體中文</a>' if lang == "zh-CN" else f'<a href="{meta["path"]}">简体中文</a>') + "</p>",
         f'<article><header><span class="kicker">PILLAR GUIDE</span><h1>{e(title)}</h1><p class="meta">{e(tr("JapanMed AI 编辑部"))}｜{e(tr("发布"))}：{meta["published"]}｜{e(tr("资料核对"))}：{meta["verified"]}｜{e(tr("编辑与医学合规审核，未经执业医师逐篇签署"))}</p></header>',
         body_html(tr(body)),
         '<section class="faq"><h2>' + e(tr("常见问题")) + "</h2>" + "".join("<h3>" + e(tr(f["q"])) + "</h3><p>" + e(tr(f["a"])) + "</p>" for f in meta["faqs"]) + "</section>",
         '<section class="evidencePanel"><h2>' + e(tr("可以去哪里核对")) + "</h2><ul>" + "".join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(tr(s["label"]))}</a></li>' for s in meta["sources"])
         + "</ul><p>" + e(tr("资料核对日期：")) + meta["verified"] + "</p></section>",
         a2, dir_html,
         '<p class="small">' + e(tr("本页为医学信息教育，不替代医生诊断、处方或治疗决定。")) + "</p>",
         '</article></main><footer class="footer"><div class="wrap"><span class="footerBrand">JapanMedAI · ' + e(tr("文腾株式会社")) + ' Bunto Co., Ltd.</span></div></footer><script src="/assets/jmai-analytics.js"></script></body></html>']
    s = "".join(h)
    return s + "\n"


def marker_sync(text, key, block, anchor_fn):
    a, b = f"<!--{key}:start-->", f"<!--{key}:end-->"
    full = a + block + b
    if a in text:
        return re.sub(re.escape(a) + ".*?" + re.escape(b), lambda _: full, text, flags=re.S)
    return anchor_fn(text, full)


def sync_sitemap(text, path, lastmod):
    loc = f"<loc>{SITE}{path}</loc>"
    line = f"  <url>{loc}<lastmod>{lastmod}</lastmod></url>\n"
    if loc in text:
        return re.sub(r"  <url>" + re.escape(loc) + r"<lastmod>[^<]*</lastmod></url>\n", line, text)
    return text.replace("</urlset>", line + "</urlset>", 1)


def main():
    check = "--check" in sys.argv
    pages = site_pages()
    metas, outs, stale = [], {}, []
    for f in sorted(SRC.glob("*.md")):
        meta, body = parse(f)
        groups = directory(meta, pages)
        gate(meta, body, groups)
        metas.append((meta, groups))
        outs[meta["path"]] = render(meta, body, groups, "zh-CN")
        outs[meta["path_hant"]] = render(meta, body, groups, "zh-TW")
    for path, html_ in outs.items():
        p = ROOT / path.strip("/") / "index.html"
        if check:
            if not p.is_file() or p.read_text(encoding="utf-8") != html_:
                stale.append(path)
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(html_, encoding="utf-8")
    # side files
    edits = {}

    def edit(rel, fn):
        p = ROOT / rel
        cur = edits.get(rel, p.read_text(encoding="utf-8"))
        edits[rel] = fn(cur)

    for meta, groups in metas:
        edit("sitemap.xml", lambda t, m=meta: sync_sitemap(sync_sitemap(t, m["path"], m["verified"]), m["path_hant"], m["verified"]))
        sm = f'{meta["section"]}/sitemap.xml'
        if (ROOT / sm).is_file():
            edit(sm, lambda t, m=meta: sync_sitemap(t, m["path"], m["verified"]))
        total = sum(len(i) for _, i in groups)
        callout = (f'<section class="evidencePanel pillarCallout"><h2>先读这一页：{e(meta["title"].split("：")[0])}</h2>'
                   f'<p>{e(meta["description"])}</p><p><a class="btn" href="{meta["path"]}">阅读指南（含 {total} 篇文章目录）→</a> '
                   f'<a href="{meta["path_hant"]}">繁體中文版</a></p></section>')

        def hub_anchor(t, full):
            m = re.search(r"</h1>.*?</(p|header|section)>", t, re.S)
            assert m, "hub anchor"
            return t[:m.end()] + full + t[m.end():]
        edit(f'{meta["section"]}/index.html', lambda t, c=callout: marker_sync(t, "pillar-callout", c, hub_anchor))
    llms_block = "\n## 核心主题指南（Pillar）\n\n" + "".join(
        f'- {m["title"]}：{SITE}{m["path"]}（繁體：{SITE}{m["path_hant"]}）\n' for m, _ in metas)
    edit("llms.txt", lambda t: marker_sync(t, "pillars", llms_block, lambda tt, full: tt.rstrip("\n") + "\n\n" + full + "\n"))
    hant_links = ('<section class="guide pillarLinks"><div class="wrap"><h2>核心主題指南</h2><ul>'
                  + "".join(f'<li><a href="{m["path_hant"]}">{e(hant(m["title"]))}</a></li>' for m, _ in metas) + "</ul></div></section>")

    def zh_anchor(t, full):
        i = t.find("<footer")
        assert i > 0
        return t[:i] + full + t[i:]
    edit("zh-hant/index.html", lambda t: marker_sync(t, "pillars", hant_links, zh_anchor))
    # back-links on every article listed in a pillar directory (hubs carry the callout instead)
    hubs = {"/" + m["section"] + "/" for m, _ in metas}
    for meta, groups in metas:
        for _, items in groups:
            for path, _t in items:
                if path in hubs:
                    continue
                trad = "/zh-tw/" in path or path.startswith("/zh-hant/")
                href = meta["path_hant"] if trad else meta["path"]
                name = meta["title"].split("：")[0]
                txt = (f'本文屬於「{hant(name)}」專題。<a href="{href}">先讀指南，查看全部相關文章 →</a>' if trad
                       else f'本文属于“{name}”专题。<a href="{href}">先读指南，查看全部相关文章 →</a>')
                block = (pillar_links.START + '<aside class="pillarBack" style="margin:24px 0;padding:12px 16px;border-left:4px solid #1f6feb;background:#f3f7ff">'
                         + f'<p style="margin:0">{txt}</p></aside>' + pillar_links.END)
                rel = path.strip("/") + "/index.html"
                edit(rel, lambda t, b=block: pillar_links.insert(t, b))
    for rel, new in edits.items():
        p = ROOT / rel
        if p.read_text(encoding="utf-8") != new:
            if check:
                stale.append(rel)
            else:
                p.write_text(new, encoding="utf-8")
    if check:
        if stale:
            sys.exit("Out of date: " + ", ".join(stale))
        print("PASS: pillars up to date", {m["id"]: sum(len(i) for _, i in g) for m, g in metas})
        return
    print("Built pillars", {m["id"]: sum(len(i) for _, i in g) for m, g in metas})


if __name__ == "__main__":
    main()
