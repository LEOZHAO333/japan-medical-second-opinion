#!/usr/bin/env python3
from pathlib import Path
import html,json,re
ROOT=Path(__file__).resolve().parents[1]
FOLDERS=['bnct','ips','checkup','medicines','hospitals','kampo']

def plain(s): return re.sub(r'<[^>]+>','',html.unescape(s)).strip()
def faq_schema_update(t,q2,a2,q3,a3):
    pat=re.compile(r'<script type="application/ld\+json">(.*?)</script>',re.S)
    def f(m):
        try:d=json.loads(m.group(1))
        except:return m.group(0)
        if isinstance(d,dict) and d.get('@type')=='FAQPage':
            es=d.get('mainEntity',[]); assert len(es)>=3
            es[1]['name']=q2; es[1]['acceptedAnswer']['text']=a2
            es[2]['name']=q3; es[2]['acceptedAnswer']['text']=a3
        return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False,separators=(',',':'))+'</script>'
    return pat.sub(f,t)

def process(p):
    t=p.read_text(encoding='utf-8')
    cm=re.search(r'<h2>这个问题真正要核对什么？</h2><ul>(.*?)</ul>',t,re.S); assert cm,p
    checks=[plain(x) for x in re.findall(r'<li>(.*?)</li>',cm.group(1),re.S)]; assert checks,p
    nm=re.search(r'<h2>对患者最有用的下一步</h2><p>(.*?)</p>',t,re.S); assert nm,p
    nxt=plain(nm.group(1))
    q2='这个问题最需要核对哪几项信息？'; a2='重点核对：'+'；'.join(checks)+'。'
    q3='下一步最值得做什么？'; a3=nxt
    fm=re.search(r'(<h2>常见问题</h2>)(.*?)(<div class="next">)',t,re.S); assert fm,p
    pairs=re.findall(r'<h3>(.*?)</h3><p>(.*?)</p>',fm.group(2),re.S); assert len(pairs)==3,(p,len(pairs))
    first='<h3>'+pairs[0][0]+'</h3><p>'+pairs[0][1]+'</p>'
    body=first+f'<h3>{html.escape(q2)}</h3><p>{html.escape(a2)}</p><h3>{html.escape(q3)}</h3><p>{html.escape(a3)}</p>'
    t=t[:fm.start()]+fm.group(1)+body+fm.group(3)+t[fm.end():]
    t=faq_schema_update(t,q2,a2,q3,a3)
    p.write_text(t,encoding='utf-8')

def validate(p):
    t=p.read_text(encoding='utf-8')
    vis=re.search(r'<h2>常见问题</h2>(.*?)<div class="next">',t,re.S); assert vis,p
    vp=[(plain(q),plain(a)) for q,a in re.findall(r'<h3>(.*?)</h3><p>(.*?)</p>',vis.group(1),re.S)]; assert len(vp)==3
    schemas=re.findall(r'<script type="application/ld\+json">(.*?)</script>',t,re.S)
    faq=None
    for raw in schemas:
        d=json.loads(raw)
        if isinstance(d,dict) and d.get('@type')=='FAQPage':faq=d
    assert faq and len(faq['mainEntity'])==3
    sp=[(x['name'],x['acceptedAnswer']['text']) for x in faq['mainEntity']]
    assert vp==sp,(p,vp,sp)
    assert vp[1][0]=='这个问题最需要核对哪几项信息？'
    assert vp[2][0]=='下一步最值得做什么？'

def main():
    pages=[]
    for f in FOLDERS:
        for i in range(1,31):
            p=ROOT/f/f'{i:03d}'/'index.html';process(p);pages.append(p)
    for p in pages:validate(p)
    print('FAQ alignment PASS: visible FAQ and FAQPage schema synchronized across 180 pages.')
if __name__=='__main__':main()
