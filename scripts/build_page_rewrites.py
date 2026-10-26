#!/usr/bin/env python3
"""Rebuild formerly thin topic pages from reviewed JSON in content/page-rewrites/*.json.
Run: python3 scripts/build_page_rewrites.py [--check]
Each JSON: {section,label,kicker,cta:{href,text},updated,pages:[{id,title,direct,explanations[],checks[],faqs[{q,a}],sources[{url,purpose}],related[{url,text}]}]}
"""
import html, json, pathlib, re, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
SITE="https://www.japanmedai.com"
PLACEHOLDER=("这个问题的事实层面是什么","哪些条件会改变结论","优先决策参考")
BAD=("草稿","待审核","Claude","GPT","主仓","私库","BLOCKED","DRAFT")
e=lambda x: html.escape(str(x),quote=True)
def ld(o): return '<script type="application/ld+json">'+json.dumps(o,ensure_ascii=False,separators=(",",":"))+'</script>'
def render(cfg,p,old):
    sec=cfg["section"]; url=f"{SITE}/{sec}/{p['id']}/"; title=p["title"]
    style=re.search(r"<style>.*?</style>",old,re.S); style=style.group(0) if style else ""
    pub=re.search(r'"datePublished":"([^"]+)"',old); pub=pub.group(1) if pub else cfg["updated"]
    desc=p["direct"][:150]
    mw={"@context":"https://schema.org","@type":"MedicalWebPage","headline":title,"description":desc,"url":url,"datePublished":pub,"dateModified":cfg["updated"],"inLanguage":"zh-CN","about":[cfg["label"],title],"publisher":{"@type":"Organization","name":"JapanMedAI｜文腾株式会社","url":SITE+"/"},"isPartOf":{"@type":"CollectionPage","name":cfg["label"],"url":f"{SITE}/{sec}/"},"citation":[s["url"] for s in p["sources"]],"abstract":p["direct"]}
    bc={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"JapanMedAI","item":SITE+"/"},{"@type":"ListItem","position":2,"name":cfg["label"],"item":f"{SITE}/{sec}/"},{"@type":"ListItem","position":3,"name":title,"item":url}]}
    fq={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f["q"],"acceptedAnswer":{"@type":"Answer","text":f["a"]}} for f in p["faqs"]]}
    T=e(title)+"｜JapanMedAI"
    h=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
       f'<title>{T}</title><meta name="description" content="{e(desc)}"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><link rel="canonical" href="{url}">',
       f'<meta property="og:type" content="article"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="{T}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{T}"><meta name="twitter:description" content="{e(desc)}">',
       '<link rel="stylesheet" href="/assets/jmai.css">',style,ld(mw),ld(bc),ld(fq),'</head><body>',
       f'<div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/{sec}/">{e(cfg["label"])}</a><a href="/second-opinion/">二次会诊</a><a href="/blog/">医疗知识库</a></nav></div></div>',
       f'<main class="article"><div class="crumb"><a href="/">首页</a> › <a href="/{sec}/">{e(cfg["label"])}</a> › 第{int(p["id"])}篇</div><article><header><span class="kicker">{e(cfg["kicker"])}</span><h1>{e(title)}</h1><p class="meta">JapanMedAI医学信息整理｜首次发布：{pub}｜资料核对：{cfg["updated"]}</p></header>',
       '<h2>直接回答</h2><div class="answer"><p>'+e(p["direct"])+'</p></div>',
       '<h2>为什么这样判断</h2>'+"".join('<p>'+e(x)+'</p>' for x in p["explanations"]),
       '<h2>这个问题真正要核对什么？</h2><ol>'+"".join('<li>'+e(x)+'</li>' for x in p["checks"])+'</ol>',
       '<section class="evidencePanel"><h2>可以去哪里核对</h2><ul>'+"".join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["purpose"])}</a></li>' for s in p["sources"])+'</ul><p>来源用于核对一般医学信息；个人情况仍需由接诊医生或专业人员判断。</p></section>',
       '<h2>常见问题</h2>'+"".join('<h3>'+e(f["q"])+'</h3><p>'+e(f["a"])+'</p>' for f in p["faqs"]),
       '<section class="decisionPath"><h2>下一步</h2><div class="relatedGrid">'+"".join(f'<a href="{e(r["url"])}">{e(r["text"])} →</a>' for r in p["related"])+f'<a href="{e(cfg["cta"]["href"])}">{e(cfg["cta"]["text"])} →</a></div></section>',
       '<p class="small">本页为医学信息教育，不替代医生诊断、处方或治疗决定；不承诺任何机构接诊或检查结果。</p>',
       '</article></main><footer class="footer"><div class="wrap"><span class="footerBrand">JapanMedAI · 文腾株式会社</span><br>内容用于医学信息教育与跨境医疗决策准备，不替代执业医疗团队诊疗。</div></footer><script src="/assets/jmai-analytics.js"></script></body></html>']
    return "".join(h)+"\n"
def main():
    check="--check" in sys.argv; stale=[]; n=0
    sm=(ROOT/"sitemap.xml").read_text(encoding="utf-8"); sm0=sm
    for f in sorted((ROOT/"content/page-rewrites").glob("*.json")):
        cfg=json.loads(f.read_text(encoding="utf-8"))
        for p in cfg["pages"]:
            blob=json.dumps(p,ensure_ascii=False)
            assert not any(b in blob for b in BAD+PLACEHOLDER),(p["id"],[b for b in BAD+PLACEHOLDER if b in blob])
            assert len(p["explanations"])>=2 and len(p["checks"])>=3 and len(p["faqs"])>=2 and p["sources"], p["id"]
            assert all(s["url"].startswith("https://") and s["url"].rstrip("/").count("/")>=3 for s in p["sources"]), p["id"]
            path=ROOT/cfg["section"]/p["id"]/"index.html"
            assert path.is_file(), path
            old=path.read_text(encoding="utf-8")
            new=render(cfg,p,old) if not check else render(cfg,p,old)
            for r in p["related"]:
                u=r["url"].split("#")[0]; assert (ROOT/u.lstrip("/")/"index.html").is_file(), u
            loc=f"<loc>{SITE}/{cfg['section']}/{p['id']}/</loc><lastmod>"
            sm=re.sub(re.escape(loc)+r"[0-9-]+",loc+cfg["updated"],sm)
            if check:
                if old!=new: stale.append(str(path.relative_to(ROOT)))
                assert not any(x in old for x in PLACEHOLDER), path
            else: path.write_text(new,encoding="utf-8")
            n+=1
    if check:
        if stale: sys.exit("Out of date: "+", ".join(stale))
        if sm!=sm0: sys.exit("sitemap lastmod out of date")
        print("PASS:",n,"rewritten pages up to date, no placeholders, sources specific, links OK"); return
    (ROOT/"sitemap.xml").write_text(sm,encoding="utf-8"); print("Rebuilt",n,"pages")
if __name__=="__main__": main()
