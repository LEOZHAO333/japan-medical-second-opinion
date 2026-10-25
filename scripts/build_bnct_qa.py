#!/usr/bin/env python3
"""Generate /bnct/qa/ and BNCT llms files from content/bnct-qa/published.json.
Run: python3 scripts/build_bnct_qa.py [--check]
"""
import json, html, pathlib, re, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"content/bnct-qa/published.json"
OUT=ROOT/"bnct/qa/index.html"
TOPICS=["原理与监管","医保诊疗","临床研究","自由诊疗","预审、海外受理与随访"]
BASE="https://www.japanmedai.com/bnct/qa/"
BAD=("草稿","复审","待审核","待Claude","Claude","GPT","主仓","私库","BLOCKED","DRAFT")
def esc(v): return html.escape(str(v),quote=True)
def anchor(i): return i.lower()
def load():
    rows=json.loads(DATA.read_text(encoding="utf-8"))["questions"]
    ids=[r["id"] for r in rows]
    assert len(ids)==len(set(ids)) and all(re.fullmatch(r"BNCT-\d{3}",i) for i in ids)
    for r in rows:
        assert r["topic"] in TOPICS, r["id"]
        assert all(r.get(k) for k in ("question","answer","check","source","source_note")), r["id"]
        assert r["source"].startswith("https://"), r["id"]
        assert not any(b in json.dumps(r,ensure_ascii=False) for b in BAD), r["id"]
    return rows
def page(rows):
    n=len(rows)
    out=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
    '<title>BNCT硼中子治疗'+str(n)+'问｜医保、研究与自由诊疗｜JapanMed AI</title>',
    '<meta name="description" content="日本BNCT常见问题：原理与监管、医保诊疗条件、临床研究、自由诊疗风险告知、资料预审与回国随访。每题附官方来源。">',
    '<meta name="robots" content="index,follow"><link rel="canonical" href="'+BASE+'">',
    '<link rel="stylesheet" href="/assets/jmai.css">',
    '<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"首页","item":"https://www.japanmedai.com/"},{"@type":"ListItem","position":2,"name":"BNCT硼中子治疗","item":"https://www.japanmedai.com/bnct/"},{"@type":"ListItem","position":3,"name":"BNCT问答","item":BASE}]},ensure_ascii=False,separators=(",",":"))+'</script>',
    '<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":r["question"],"acceptedAnswer":{"@type":"Answer","text":r["answer"]}} for r in rows]},ensure_ascii=False,separators=(",",":"))+'</script>',
    '<style>main{max-width:1000px;margin:auto;padding:30px 18px}.qa{padding:18px 0;border-bottom:1px solid #dce6ee}.qa h3{scroll-margin-top:18px}.qa p{line-height:1.8}.qa button{margin-right:10px;padding:7px 12px;cursor:pointer}.topicNav{display:flex;flex-wrap:wrap;gap:12px}.qa-disclaimer{margin:24px 0;padding:16px;background:#f4f7fa}.feedbackStatus{font-size:13px}</style>',
    '</head><body class="bnct-qa-page" data-qa-version="bnct-qa-v1"><div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/bnct/">BNCT</a><a href="/checkup/">二次会诊</a><a href="/blog/">医疗知识库</a></nav></div></div>',
    '<main><p><a href="/bnct/">返回BNCT专题</a></p><h1>BNCT硼中子治疗'+str(n)+'问</h1><p>按医保诊疗、临床研究、自由诊疗三条路径整理常见问题。本页为医学信息科普，不提供诊断或治疗建议，不承诺任何机构接诊。</p>',
    '<nav class="topicNav" aria-label="问答主题">']
    used=[t for t in TOPICS if any(r["topic"]==t for r in rows)]
    for i,t in enumerate(used): out.append('<a href="#topic-'+str(i+1)+'">'+esc(t)+'</a>')
    out.append('</nav>')
    for i,t in enumerate(used):
        sub=[r for r in rows if r["topic"]==t]
        out.append('<section><h2 id="topic-'+str(i+1)+'">'+esc(t)+'（'+str(len(sub))+'题）</h2>')
        for r in sub:
            a=anchor(r["id"])
            out.extend(['<article class="qa"><h3 id="'+a+'">'+esc(r["question"])+'</h3>',
            '<p><strong>直接回答：</strong>'+esc(r["answer"])+'</p>',
            '<p><strong>核对要点：</strong>'+esc(r["check"])+'</p>',
            '<p><strong>来源：</strong><a href="'+esc(r["source"])+'" rel="noopener noreferrer">'+esc(r["source_note"])+'</a></p>'])
            if r.get("related"): out.append('<p>延伸阅读：<a href="'+esc(r["related"])+'" data-jmai-track="qa_related" data-jmai-id="qa_'+a.replace("-","_")+'" data-jmai-position="faq">查看相关专题</a></p>')
            out.append('<div class="qaFeedback" data-qa-id="'+a+'"><button type="button" data-vote="helpful">有帮助</button><button type="button" data-vote="needs_work">需改进</button><span class="feedbackStatus" role="status" aria-live="polite"></span></div></article>')
        out.append('</section>')
    out.extend(['<section class="qa-disclaimer"><p>医学信息用于教育与资料整理，不替代医生诊断或治疗；是否适合BNCT及能否受理，以实施机构的正式评估为准。</p></section></main>',
    '<footer class="footer"><div class="wrap"><span class="footerBrand">JapanMedAI · 文腾株式会社</span><br>内容用于医学信息教育与跨境医疗决策准备，不替代执业医疗团队诊疗。</div></footer>',
    '<script src="/assets/jmai-analytics.js"></script><script src="/assets/checkup-qa-feedback.js"></script></body></html>'])
    return "".join(out)+"\n"
def llms(rows):
    n=len(rows)
    brief=["# BNCT硼中子治疗｜已发布"+str(n)+"问","","> 本索引由已发布JSON自动生成，只含已上线问答。","",
           "- [BNCT专题](https://www.japanmedai.com/bnct/)","- [已发布问答]("+BASE+")","- [完整问答](https://www.japanmedai.com/bnct/llms-full.txt)",""]
    full=["# BNCT硼中子治疗｜已发布"+str(n)+"问完整正文","","> 本文件由已发布JSON自动生成。医学信息仅供教育，不代替诊断或治疗，不保证接诊。",""]
    for r in rows:
        link=BASE+"#"+anchor(r["id"])
        brief.append("- ["+r["question"]+"]("+link+")")
        full.extend(["## "+r["question"],"",r["answer"],"","核对要点："+r["check"],"","来源："+r["source"],"来源说明："+r["source_note"],"","[网页入口]("+link+")",""])
    return "\n".join(brief)+"\n","\n".join(full)+"\n"
def main():
    rows=load()
    files={OUT:page(rows)}
    b,f=llms(rows); files[ROOT/"bnct/llms.txt"]=b; files[ROOT/"bnct/llms-full.txt"]=f
    if "--check" in sys.argv:
        stale=[str(p.relative_to(ROOT)) for p,c in files.items() if not p.is_file() or p.read_text(encoding="utf-8")!=c]
        if stale: sys.exit("Out of date: "+", ".join(stale))
        for href in re.findall(r'href="(/bnct/\d{3}/)"',files[OUT]): assert (ROOT/href.lstrip("/")/"index.html").is_file(),href
        assert "https://www.japanmedai.com/bnct/llms.txt" in (ROOT/"llms.txt").read_text(encoding="utf-8")
        assert "<loc>"+BASE+"</loc>" in (ROOT/"bnct/sitemap.xml").read_text(encoding="utf-8")
        assert 'href="/bnct/qa/"' in (ROOT/"bnct/index.html").read_text(encoding="utf-8")
        print("PASS:",len(rows),"BNCT QA; page/llms up to date; links, sitemap, hub, root llms OK"); return
    for p,c in files.items(): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(c,encoding="utf-8")
    print("Generated /bnct/qa/ and BNCT llms from",len(rows),"FAQs")
if __name__=="__main__": main()
