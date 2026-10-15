from pathlib import Path
import re, json, html

ROOT=Path(__file__).resolve().parents[1]
TODAY='2026-10-15'

PRIORITY=[
('bnct/001','已经做过70Gy放疗，头颈癌复发后还能评估BNCT吗？'),
('bnct/004','日本BNCT目前批准哪些适应证？哪些癌种仍处于研究阶段'),
('bnct/010','复发头颈癌BNCT疗效怎么看？ORR、OS与随访数据如何解读'),
('bnct/024','申请日本BNCT评估要准备哪些资料？病理、DICOM和放疗计划清单'),
('checkup/005','哪些癌症患者更值得做日本二次专家会诊'),
('checkup/006','申请日本二次会诊要准备哪些资料？病理、影像和治疗时间线清单'),
('checkup/023','日本二次专家会诊怎么申请？从资料整理到专家反馈'),
('hospitals/013','中国患者能直接预约日本医院吗？转诊、预审和介绍状怎么理解'),
('medicines/004','日本抗癌新药获批信息怎么看？批准日期、适应证和治疗线次三步核对'),
('ips/003','日本iPS疗法哪些已经进入临床？海外患者能否申请要看什么'),
]

HUB_S={
'bnct':['001','004','010','011','016','017','021','022','024','029'],
'checkup':['004','005','006','009','015','017','022','023'],
'hospitals':['001','004','013','020','025'],
'medicines':['004','017','029'],
'ips':['003','007'],
'kampo':['010','011'],
}

RELATED={
'bnct':[('/second-opinion/','二次专家会诊'),('/hospitals/','日本医院与专家')],
'checkup':[('/second-opinion/','二次专家会诊总入口'),('/hospitals/','日本医院与专家')],
'hospitals':[('/second-opinion/','二次专家会诊'),('/bnct/','BNCT硼中子治疗')],
'medicines':[('/second-opinion/','二次专家会诊'),('/hospitals/','日本医院与专家')],
'ips':[('/second-opinion/','二次专家会诊'),('/hospitals/','日本医院与专家')],
'kampo':[('/medicines/','日本新药与药品信息'),('/hospitals/','日本医院与专家')],
}

def read(p): return p.read_text(encoding='utf-8')
def write(p,s): p.write_text(s,encoding='utf-8',newline='\n')

def extract_title(path):
    t=read(path)
    m=re.search(r'<h1[^>]*>(.*?)</h1>',t,re.S|re.I)
    if m: return html.unescape(re.sub('<[^>]+>','',m.group(1))).strip()
    m=re.search(r'<title>(.*?)</title>',t,re.S|re.I)
    return html.unescape(m.group(1)).split('｜')[0].strip() if m else path.as_posix()

def update_home():
    p=ROOT/'index.html'; t=read(p)
    marker='<!-- JMAI_PRIORITY_ENTRY_START -->'
    if marker in t:
        t=re.sub(r'<!-- JMAI_PRIORITY_ENTRY_START -->.*?<!-- JMAI_PRIORITY_ENTRY_END -->','',t,flags=re.S)
    cards='\n'.join([f'<a class="card mini" href="/{path}/" data-jmai-track="priority" data-jmai-id="priority_{path.replace("/","_")}" data-jmai-position="home"><b>{html.escape(title)}</b><span>进入核心决策页 →</span></a>' for path,title in PRIORITY])
    block=f'''\n<!-- JMAI_PRIORITY_ENTRY_START -->\n<section class="section" id="priority-decisions"><div class="wrap"><span class="kicker">PRIORITY DECISION GUIDES</span><h2>优先阅读：最接近真实就医决策的10个问题</h2><p class="help">先看是否适合评估、需要哪些资料、证据如何理解，再决定是否进入医院接诊或二次会诊流程。</p><div class="grid3">{cards}</div></div></section>\n<!-- JMAI_PRIORITY_ENTRY_END -->\n'''
    anchor='<section class="section"><div class="wrap">\n<span class="kicker">WHY JAPANMEDAI</span>'
    if anchor in t:
        t=t.replace(anchor,block+anchor,1)
    else:
        t=t.replace('<section class="section" id="knowledge">',block+'<section class="section" id="knowledge">',1)
    # add ItemList in head
    script=json.dumps({"@context":"https://schema.org","@type":"ItemList","name":"JapanMedAI优先医疗决策指南","numberOfItems":len(PRIORITY),"itemListElement":[{"@type":"ListItem","position":i+1,"url":f"https://www.japanmedai.com/{path}/","name":title} for i,(path,title) in enumerate(PRIORITY)]},ensure_ascii=False,separators=(',',':'))
    t=re.sub(r'<script id="jmai-priority-itemlist" type="application/ld\+json">.*?</script>','',t,flags=re.S)
    t=t.replace('</head>',f'<script id="jmai-priority-itemlist" type="application/ld+json">{script}</script>\n</head>',1)
    write(p,t)

def update_hub(hub):
    p=ROOT/hub/'index.html'; t=read(p)
    titles=[]
    for n in HUB_S[hub]:
        page=ROOT/hub/n/'index.html'
        titles.append((n,extract_title(page)))
    links=''.join([f'<a href="/{hub}/{n}/" data-jmai-track="priority" data-jmai-id="priority_{hub}_{n}" data-jmai-position="hub-featured">{html.escape(title)}</a>' for n,title in titles])
    rel=''.join([f'<a class="topicPill" href="{u}">{html.escape(label)}</a>' for u,label in RELATED[hub]])
    block=f'''<!-- JMAI_HUB_PRIORITY_START --><section class="section hubPriority"><div class="wrap"><span class="kicker">START HERE</span><h2>优先阅读</h2><p>先从高决策价值问题进入，再浏览全部专题内容。</p><div class="priorityLinks">{links}</div><div class="topicGrid" style="margin-top:18px">{rel}</div></div></section><!-- JMAI_HUB_PRIORITY_END -->'''
    t=re.sub(r'<!-- JMAI_HUB_PRIORITY_START -->.*?<!-- JMAI_HUB_PRIORITY_END -->','',t,flags=re.S)
    insert='<section class="section"><div class="wrap"><div class="grid">'
    if insert in t:
        t=t.replace(insert,block+insert,1)
    style='.hubPriority{padding-top:18px}.priorityLinks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.priorityLinks a{display:block;padding:12px 14px;border:1px solid #dbe7f2;border-radius:12px;background:#fff;text-decoration:none;color:inherit;line-height:1.5}.priorityLinks a:hover{text-decoration:underline}@media(max-width:700px){.priorityLinks{grid-template-columns:1fr}}'
    t=t.replace('</style>',style+'</style>',1)
    write(p,t)

def write_intent_map():
    rows=['tier\tpath\tintent\ttitle']
    for path,title in PRIORITY:
        rows.append(f'P0\t{path}\tcore-decision\t{title}')
    for hub, nums in HUB_S.items():
        for n in nums:
            path=f'{hub}/{n}'
            if any(path==p for p,_ in PRIORITY): continue
            rows.append(f'P1\t{path}\tsupporting-decision\t{extract_title(ROOT/hub/n/"index.html")}')
    write(ROOT/'docs/index-weight-map.tsv','\n'.join(rows)+'\n')

def qa():
    home=read(ROOT/'index.html')
    assert home.count('data-jmai-position="home"')==10
    assert 'jmai-priority-itemlist' in home
    seen=set()
    for path,title in PRIORITY:
        assert path not in seen; seen.add(path)
        assert f'href="/{path}/"' in home
    for hub, nums in HUB_S.items():
        t=read(ROOT/hub/'index.html')
        assert 'JMAI_HUB_PRIORITY_START' in t
        for n in nums:
            assert f'href="/{hub}/{n}/"' in t
        for u,_ in RELATED[hub]: assert f'href="{u}"' in t
    # do not alter canonical/index status of 180 pages
    for hub in HUB_S:
        for n in range(1,31):
            p=ROOT/hub/f'{n:03d}'/'index.html'
            t=read(p)
            assert '<meta name="robots" content="index,follow' in t
            assert '<link rel="canonical" href="https://www.japanmedai.com/' in t
    print('index-weight QA OK')

for h in HUB_S: update_hub(h)
update_home()
write_intent_map()
qa()
