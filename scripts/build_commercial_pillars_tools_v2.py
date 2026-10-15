from pathlib import Path
import json
R=Path('.'); D='2026-10-15'; B='https://www.japanmedai.com'
pillars=[
('bnct/recurrent-head-neck','复发头颈癌做日本BNCT前，先判断哪5件事？','适用于已经接受过治疗、正在评估日本BNCT或第二意见的人群。先核对适应证边界、原始DICOM、既往放疗计划、近期病理与全身病灶，再谈能否进入机构评估。',['/bnct/001/','/bnct/004/','/bnct/010/','/bnct/024/'],'/tools/bnct-records/'),
('bnct/gbm','复发胶质母细胞瘤考虑日本BNCT，先看研究阶段和资料条件','复发GBM的BNCT在日本仍需严格区分临床研究、注册试验与常规医疗。先核对分子病理、复发位置、既往放疗、近期MRI/DICOM和当前体能，再判断是否值得申请研究或专家第二意见。',['/bnct/021/','/bnct/022/','/bnct/024/','/bnct/047/'],'/tools/bnct-records/'),
('second-opinion/cancer','日本癌症二次专家会诊：什么时候值得做，资料怎么准备？','适合刚确诊、复发进展、治疗选择复杂或希望核对病理/影像/分子结果的人群。二次意见的价值不是保证找到新方案，而是把当前诊断、证据和下一步决策重新核对清楚。',['/checkup/005/','/checkup/006/','/checkup/023/','/checkup/048/'],'/tools/second-opinion-records/'),
('hospitals/international-patient','海外患者申请日本医院：从资料预审到接诊，先搞清这6步','日本医院是否接收海外患者，取决于科室、病种、资料完整度、是否需要介绍状、国际协调流程和费用支付安排。先做接诊准备，而不是先群发医院。',['/hospitals/013/','/hospitals/031/','/hospitals/033/','/hospitals/050/'],'/tools/hospital-readiness/'),
('medicines/indication-check','日本新药适应证怎么核对？别只看“日本已上市”','药物是否日本已上市与某位患者能否使用不是一回事。至少核对通用名、PMDA批准状态、正式适应证、治疗线次/生物标志物、最新添付文书和处方属性。',['/medicines/004/','/medicines/031/','/medicines/032/','/medicines/050/'],'/tools/medicine-indication/'),]
tools=[
('tools/bnct-records','BNCT资料完整度自查｜病理、DICOM、既往放疗计划',['病理报告或近期病理复核结果','近期CT/MRI/PET报告','原始DICOM影像文件','既往放疗计划/剂量资料（如做过放疗）','手术、化疗、免疫/靶向治疗时间线','当前症状、体能和主要问题'],'这不是BNCT适应证判断。资料是否足够、是否需要补充检查，应由接诊机构确认。'),
('tools/second-opinion-records','癌症二次会诊资料完整度自查｜一页时间线怎么准备',['病理报告及切片/蜡块调取信息','近期影像报告','原始DICOM','手术/出院记录','既往治疗时间线与停药原因','基因/分子检测（如已完成）','当前用药清单','最希望专家回答的3—5个问题'],'这只是资料准备工具，不判断是否有必要做二次会诊，也不替代主诊医生。'),
('tools/hospital-readiness','日本医院海外患者接诊准备自查｜首次联系前先核对',['明确就诊目的：第二意见/检查/手术/治疗','确认目标科室或疾病方向','准备可阅读的病情摘要','近期影像与原始文件可调取','确认是否需要介绍状或协调机构','准备预约所需身份信息并仅在正式渠道提交','了解费用支付/押金要求','确认是否需要翻译或医疗口译'],'完成清单不代表医院一定接诊；最终由医院和临床科室决定。'),
('tools/medicine-indication','日本新药适应证核对表｜批准、线次、生物标志物',['通用名与商品名是否对应','PMDA是否正式批准','正式适应证是什么','疾病阶段/治疗线次是否一致','是否要求特定生物标志物','是否规定联合方案','最新添付文书/重要注意事项','是否为处方药及当地合法获取路径'],'这不是用药建议。具体药物是否适合个人，应由具备处方资格的医生结合病情判断。')]
css='<link rel="stylesheet" href="/assets/jmai.css"><style>.article{max-width:940px;margin:auto;padding:42px 20px 70px}.article p,.article li{line-height:1.85}.panel{padding:22px;border:1px solid #d7e6f2;border-radius:16px;background:#fbfdff;margin:20px 0}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.grid a,.check{display:block;padding:14px 16px;border:1px solid #dbe7f2;border-radius:12px;text-decoration:none;color:inherit}.result{padding:16px;border-radius:12px;background:#f4f8fb;margin-top:16px}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style>'
def wrap(title,desc,url,body,typ='MedicalWebPage'):
 data={'@context':'https://schema.org','@type':typ,'headline':title,'description':desc,'url':url,'datePublished':D,'dateModified':D,'inLanguage':'zh-CN','publisher':{'@type':'Organization','name':'JapanMedAI｜文腾株式会社','url':B+'/'}}
 return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'｜JapanMedAI</title><meta name="description" content="'+desc+'"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><link rel="canonical" href="'+url+'"><meta property="og:type" content="article"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="'+title+'｜JapanMedAI"><meta property="og:description" content="'+desc+'"><meta property="og:url" content="'+url+'"><meta name="twitter:card" content="summary"><script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>'+css+'</head><body><div class="top"><div class="wrap nav"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a></div></div>'+body+'<footer class="footer"><div class="wrap">JapanMedAI · 文腾株式会社｜内容用于医学信息教育与跨境医疗决策准备，不替代医疗团队诊疗。</div></footer><script src="/assets/jmai-analytics.js"></script></body></html>'
for slug,title,desc,refs,tool in pillars:
 links=''.join('<a href="'+r+'">相关核心问题 →</a>' for r in refs)
 body='<main class="article"><div class="crumb"><a href="/">首页</a> › 专题入口</div><article><header><span class="kicker">DECISION HUB</span><h1>'+title+'</h1><p class="lead">'+desc+'</p></header><section class="panel"><h2>先做资料自查</h2><p>先把关键资料和当前决策问题整理完整，再进入机构评估或专家第二意见。</p><a class="btn" href="'+tool+'">开始资料自查 →</a></section><section class="panel"><h2>最常需要核对什么？</h2><ol><li>诊断和病理是否明确。</li><li>近期影像是否有原始DICOM。</li><li>既往治疗时间线是否完整。</li><li>当前真正需要解决的决策问题是什么。</li><li>哪些属于获批/常规医疗，哪些仍是研究。</li></ol></section><section class="panel"><h2>优先阅读</h2><div class="grid">'+links+'</div></section><section class="panel"><h2>下一步</h2><p><a class="btn" href="'+tool+'">资料自查</a> <a class="btn alt" href="/second-opinion/">二次会诊预评估</a></p></section></article></main>'
 p=R/slug/'index.html'; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(wrap(title,desc,B+'/'+slug+'/',body),encoding='utf-8')
for slug,title,items,boundary in tools:
 checks=''.join('<label class="check"><input type="checkbox" class="jmaiCheck">'+x+'</label>' for x in items)
 js="<script>const cs=[...document.querySelectorAll('.jmaiCheck')],s=document.getElementById('score');cs.forEach(c=>c.addEventListener('change',()=>s.textContent=cs.filter(x=>x.checked).length));</script>"
 body='<main class="article"><div class="crumb"><a href="/">首页</a> › 资料自查工具</div><article><header><span class="kicker">SELF-CHECK TOOL</span><h1>'+title+'</h1><p class="lead">不上传病历、不留联系方式，只检查目前手上的资料是否齐全。</p></header><section class="panel"><div class="grid">'+checks+'</div><div class="result">已准备 <b id="score">0</b> / '+str(len(items))+' 项</div><p class="small">'+boundary+'</p></section><section class="panel"><h2>怎么用结果？</h2><p>先补最基础资料，再整理一页治疗时间线和3—5个核心问题；不要为了凑齐清单自行追加医学检查。</p><p><a class="btn" href="/second-opinion/">进入二次会诊预评估</a></p></section></article></main>'+js
 p=R/slug/'index.html'; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(wrap(title,'JapanMedAI资料准备自查工具：不上传病历、不判断诊断或治疗资格，仅帮助整理跨境医疗所需资料。',B+'/'+slug+'/',body,'WebPage'),encoding='utf-8')
hubs={'bnct/index.html':[('/bnct/recurrent-head-neck/','复发头颈癌 × BNCT'),('/bnct/gbm/','复发胶质母细胞瘤 × BNCT')],'second-opinion/index.html':[('/second-opinion/cancer/','癌症二次专家会诊'),('/tools/second-opinion-records/','资料自查')],'hospitals/index.html':[('/hospitals/international-patient/','海外患者申请日本医院'),('/tools/hospital-readiness/','接诊准备自查')],'medicines/index.html':[('/medicines/indication-check/','日本新药适应证核对'),('/tools/medicine-indication/','新药核对表')]}
for fn,ls in hubs.items():
 p=R/fn; t=p.read_text(encoding='utf-8'); block='<section class="section"><div class="wrap"><span class="kicker">DECISION ENTRY</span><h2>高价值决策入口</h2><div class="grid3">'+''.join('<a class="card mini" href="'+u+'"><b>'+n+'</b><span>进入 →</span></a>' for u,n in ls)+'</div></div></section>'
 if 'DECISION ENTRY' not in t: p.write_text(t.replace('<footer',block+'<footer',1),encoding='utf-8')
p=R/'index.html'; t=p.read_text(encoding='utf-8'); block='<section class="section" id="decision-hubs"><div class="wrap"><span class="kicker">DECISION HUBS</span><h2>从疾病与决策场景进入</h2><div class="topicGrid"><a class="topicPill" href="/bnct/recurrent-head-neck/">复发头颈癌 × BNCT</a><a class="topicPill" href="/bnct/gbm/">复发胶质母细胞瘤 × BNCT</a><a class="topicPill" href="/second-opinion/cancer/">癌症二次专家会诊</a><a class="topicPill" href="/hospitals/international-patient/">日本医院海外患者申请</a><a class="topicPill" href="/medicines/indication-check/">日本新药适应证核对</a></div></div></section>'
if 'id="decision-hubs"' not in t: p.write_text(t.replace('<section class="section" id="homeFaq">',block+'<section class="section" id="homeFaq">',1),encoding='utf-8')
sp=R/'sitemap.xml'; st=sp.read_text(encoding='utf-8'); slugs=[x[0] for x in pillars]+[x[0] for x in tools]
for slug in slugs:
 loc=B+'/'+slug+'/'
 if loc not in st: st=st.replace('</urlset>','  <url><loc>'+loc+'</loc><lastmod>'+D+'</lastmod></url>\n</urlset>')
sp.write_text(st,encoding='utf-8')
reg=R/'docs/commercial-pillar-registry.tsv'; reg.write_text('type\tslug\ttitle\n'+''.join('pillar\t'+x[0]+'\t'+x[1]+'\n' for x in pillars)+''.join('tool\t'+x[0]+'\t'+x[1]+'\n' for x in tools),encoding='utf-8')
for slug in slugs:
 txt=(R/slug/'index.html').read_text(encoding='utf-8'); assert '<link rel="canonical"' in txt and B+'/'+slug+'/' in st
print('OK',len(pillars),len(tools))
