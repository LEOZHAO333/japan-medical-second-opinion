#!/usr/bin/env python3
"""Generate private-review second-opinion QA page from approved-schema JSON.
Run: python3 scripts/build_checkup_qa.py
No publication, no data mutation beyond checkup/qa/index.html.
"""
import json, html, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"content/checkup-qa/first-release-25.json"
OUT=ROOT/"checkup/qa/index.html"
TOPICS=["概念与边界","资料准备","申请与流程","诊疗决策","结果使用"]
def esc(v): return html.escape(str(v),quote=True)
def render():
    data=json.loads(DATA.read_text(encoding="utf-8"))
    rows=data["questions"]
    assert len(rows)==25 and len({r["id"] for r in rows})==25
    assert all(r["topic"] in TOPICS and r["source"].startswith("https://ganjoho.jp/") for r in rows)
    for r in rows:
        assert all(r.get(k) for k in ("question","answer","check","source","source_note"))
    base="https://www.japanmedai.com/checkup/qa/"
    out=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
    '<title>癌症第二意见25问｜申请流程、资料与结果使用｜JapanMed AI</title>',
    '<meta name="description" content="日本癌症第二意见常见问题：定义、资料准备、申请流程、费用和结果使用。每题附官方来源。">',
    '<meta name="robots" content="index,follow"><link rel="canonical" href="'+base+'">',
    '<link rel="stylesheet" href="/assets/jmai.css">',
    '<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"首页","item":"https://www.japanmedai.com/"},{"@type":"ListItem","position":2,"name":"二次会诊","item":"https://www.japanmedai.com/checkup/"},{"@type":"ListItem","position":3,"name":"二次会诊问答","item":base}]},ensure_ascii=False,separators=(",",":"))+'</script>',
    '<style>main{max-width:1000px;margin:auto;padding:30px 18px}.qa{padding:18px 0;border-bottom:1px solid #dce6ee}.qa h3{scroll-margin-top:18px}.qa p{line-height:1.8}.qa button{margin-right:10px;padding:7px 12px;cursor:pointer}.topicNav{display:flex;flex-wrap:wrap;gap:12px}.qa-disclaimer{margin:24px 0;padding:16px;background:#f4f7fa}.feedbackStatus{font-size:13px}@media(max-width:900px){body.checkup-qa-page .top .navMenu{display:flex;flex-wrap:wrap;gap:8px 14px;justify-content:center}body.checkup-qa-page .top .nav{flex-direction:column;align-items:center;gap:10px}body.checkup-qa-page .top{position:relative}}</style>',
    '</head><body class="checkup-qa-page"><div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/checkup/">二次会诊</a><a href="/hospitals/">日本医院</a><a href="/blog/">医疗知识库</a></nav></div></div>',
    '<main><p><a href="/checkup/">返回二次会诊专题</a></p><h1>癌症第二意见25问</h1><p>按五大主题整理常见问题，帮助理解日本第二意见门诊的流程与边界。本页为医学信息科普，不提供诊断或治疗建议。</p>',
    '<nav class="topicNav" aria-label="问答主题">']
    for i,topic in enumerate(TOPICS):out.append('<a href="#topic-'+str(i+1)+'">'+esc(topic)+'</a>')
    out.append('</nav>')
    for i,topic in enumerate(TOPICS):
        subset=[r for r in rows if r["topic"]==topic]
        out.append('<section><h2 id="topic-'+str(i+1)+'">'+esc(topic)+'（'+str(len(subset))+'题）</h2>')
        for r in subset:
            rid=r["id"].lower()
            out.extend(['<article class="qa"><h3 id="'+esc(rid)+'">'+esc(r["question"])+'</h3>',
            '<p><strong>直接回答：</strong>'+esc(r["answer"])+'</p>',
            '<p><strong>核对要点：</strong>'+esc(r["check"])+'</p>',
            '<p><strong>来源：</strong><a href="'+esc(r["source"])+'" rel="noopener noreferrer">'+esc(r["source_note"])+'</a></p>'])
            if r.get("related"):out.append('<p>延伸阅读：<a href="'+esc(r["related"])+'" data-jmai-track="qa_related" data-jmai-id="qa_'+esc(rid.replace("-","_"))+'" data-jmai-position="faq">查看相关专题</a></p>')
            out.append('<div class="qaFeedback" data-qa-id="'+esc(rid)+'"><button type="button" data-vote="helpful">有帮助</button><button type="button" data-vote="needs_work">需改进</button><span class="feedbackStatus" role="status" aria-live="polite"></span></div></article>')
        out.append('</section>')
    out.extend(['<section class="qa-disclaimer"><p>医学信息用于教育与资料整理，不替代医生诊断、处方或治疗；具体受理要求请咨询医院。</p></section></main>',
    '<footer class="footer"><div class="wrap"><span class="footerBrand">JapanMedAI · 文腾株式会社</span><br>内容用于医学信息教育与跨境医疗决策准备，不替代执业医疗团队诊疗。</div></footer>',
    '<script src="/assets/jmai-analytics.js"></script><script src="/assets/checkup-qa-feedback.js"></script></body></html>'])
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text("".join(out)+"\n",encoding="utf-8")
    print("Generated",OUT.relative_to(ROOT),len(rows),"FAQ")
if __name__=="__main__":render()
