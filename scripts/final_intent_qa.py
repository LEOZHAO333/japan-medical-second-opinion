#!/usr/bin/env python3
from pathlib import Path
import html, json, re
from difflib import SequenceMatcher

ROOT=Path(__file__).resolve().parents[1]
TODAY='2026-10-15'
FOLDERS=['bnct','ips','checkup','medicines','hospitals','kampo']
INTENTS={
'bnct':['eligibility','definition','comparison','access','safety','cost','combination','evidence','evidence','evidence','access','comparison','workflow','comparison','comparison','comparison','retreatment','research','definition','evidence','safety','verification','scope','workflow','research','limitations','mechanism','workflow','eligibility','biomarker'],
'ips':['comparison','mechanism','access','research','evidence','research','verification','access','research','research','research','research','research','comparison','comparison','safety','comparison','safety','access','limitations','cost','definition','history','research','followup','access','evidence','cost','comparison','research'],
'checkup':['institution','screening','selection','second_opinion','eligibility','workflow','workflow','screening','cost','second_opinion','followup','followup','followup','screening','eligibility','workflow','second_opinion','comparison','cost','eligibility','screening','definition','workflow','scope','comparison','evidence','screening','institution','screening','second_opinion'],
'medicines':['regulatory','evidence','research','regulatory','drug','device','drug','drug','drug','drug','drug','drug','drug','drug','comparison','research','regulatory','research','drug','research','research','research','drug','research','drug','comparison','drug','personalization','access','evidence'],
'hospitals':['expert','institution','definition','institution','expert','workflow','diagnostics','mdt','second_opinion','workflow','expert','second_opinion','access','institution','institution','workflow','second_opinion','workflow','institution','access','comparison','expert','institution','institution','access','definition','expert','second_opinion','institution','comparison'],
'kampo':['evidence','industry','comparison','scope','evidence','drug','selection','scope','history','verification','comparison','verification','selection','verification','evidence','comparison','industry','selection','selection','access','safety','evidence','selection','selection','quality','selection','selection','weight','supportive','access']}
LABELS={'access':'实际可及性','comparison':'方案比较','selection':'选择判断','drug':'单个方剂/药物信息','scope':'适用范围','verification':'信息核验','eligibility':'适合人群','definition':'概念理解','safety':'安全性','cost':'费用','combination':'联合治疗','evidence':'证据解读','workflow':'流程与资料准备','retreatment':'再次治疗','research':'研究进展','limitations':'技术限制','mechanism':'作用机制','biomarker':'生物标志物','followup':'异常后的下一步','history':'技术发展','institution':'机构选择','screening':'筛查','second_opinion':'第二意见','regulatory':'监管与批准','device':'医疗设备','personalization':'个体化用药','expert':'专家匹配','diagnostics':'检查价值','mdt':'多学科会诊','industry':'产业与标准化','quality':'质量控制','weight':'体重管理','supportive':'支持治疗'}

O={
('hospitals','access'):{'lead':'海外患者能否进入某家日本医院，主要取决于该院国际患者政策、是否要求介绍状或转诊、资料预审结果、目标科室是否接收，以及语言和支付流程。医院有这个科室，不等于海外患者可以自行预约。','checks':['医院是否接受海外患者直接申请，还是必须经转诊或医疗协调','目标科室是否要求介绍状、原始影像、病理或其他资料预审','是否需要医学翻译、国际患者窗口、费用担保或预付款','当前需求适合远程第二意见、门诊面诊还是住院治疗'],'next':'先查目标医院国际患者与目标科室的官方要求，再按要求整理资料做预审；得到明确接诊反馈后，再安排赴日行程。'},
('bnct','access'):{'lead':'判断日本BNCT是否“能做”，要同时看日本正式适应证、具体机构是否开展、病灶与既往放疗是否符合评估条件，以及海外患者能否进入资料预审。不能把“日本有BNCT”直接等同于个人可治疗。','checks':['日本当前正式批准适应证与患者条件是什么','病灶位置、范围和既往放疗是否需要进一步剂量评估','目标BNCT机构目前是否开展该适应证并接受资料预审','海外患者需要提交哪些病理、DICOM和放疗计划资料'],'next':'先用官方适应证和目标机构要求做第一轮筛选，再提交病理、原始影像和既往放疗资料进行个体评估。'},
('ips','access'):{'lead':'iPS项目是否“进入临床”与海外患者现在是否能申请是两层问题。要先区分正式批准产品、临床试验、研究性医疗与商业自由诊疗，再看项目是否仍在招募及是否接受海外患者。','checks':['项目属于正式批准、临床试验还是研究探索','能否在监管机构或临床试验注册系统核对到项目状态','当前是否仍在招募，以及入组标准是什么','海外患者、年龄、疾病阶段和既往治疗是否符合申请条件'],'next':'先核对监管状态和试验注册，再看招募条件；只有明确可申请时，才进入病历预审和机构联系。'},
('medicines','access'):{'lead':'日本已经批准某种药，并不代表海外患者可以直接购买或使用。真正的可及性取决于批准适应证、医生处方与接诊、院内给药或冷链要求、供应状态，以及目的地国家或地区的进口规则。','checks':['日本说明书批准的疾病、患者人群和治疗线次是否匹配','是否必须由日本医生诊断并开具处方或在院内使用','药品当前供应、储存、冷链或给药条件是什么','跨境携带或邮寄是否符合目的地法律和海关要求'],'next':'先确认个人是否符合日本说明书适应证，再分别核对接诊处方路径和目的地合规要求，不要把“日本已上市”理解成可自由跨境购买。'},
('kampo','access'):{'lead':'日本汉方的获取方式取决于它是医用处方汉方还是药店OTC产品。即使方名相同，厂家、剂型、每日量、适应证和销售类别也可能不同，跨境携带或邮寄还要单独看目的地规则。','checks':['具体产品属于医用处方汉方还是OTC汉方','厂家、方剂编号、剂型、成分和每日用量是否一致','年龄、妊娠、基础疾病和合并用药是否存在限制','跨境携带或邮寄是否符合目的地药品监管要求'],'next':'先确认准确产品和销售类别，再核对说明书及个人用药风险；涉及处方汉方时，应按正规医疗路径评估。'},
('ips','comparison'):{'lead':'iPS相关比较最容易混淆的是“细胞来源”和“临床成熟度”。比较两种细胞或治疗路线时，应看多能性、制造方式、免疫排斥、质量控制、证据阶段和是否已经进入真实临床，而不是只看“干细胞”三个字。','checks':['两类细胞的来源、多能性和最终分化目标有什么不同','制造时间、标准化程度和批次质量控制如何','自体或异体使用时的免疫排斥和安全风险有什么差异','各自目前处于基础研究、临床试验还是批准应用阶段'],'next':'先把两种技术放到“细胞来源—制造—安全—证据—可及性”五个维度比较，再讨论是否与具体疾病相关。'},
('checkup','comparison'):{'lead':'比较不同体检体系或检查路径时，重点不是项目数量，而是筛查目标、风险分层、检查质量、报告复核和发现异常后的专科衔接。项目更多并不自动等于更精密。','checks':['两套方案针对的疾病风险和人群是否相同','关键影像、内镜或实验室项目的质量与复核机制有什么差异','是否存在重复检查、过度筛查或假阳性风险','发现异常后能否快速进入对应专科进一步诊断'],'next':'按年龄、家族史、既往异常和个人风险建立筛查目标，再比较哪些项目真正会改变后续决策。'},
('medicines','comparison'):{'lead':'比较两种药物或治疗路线时，应把作用机制、批准适应证、关键研究、治疗线次、安全性和给药条件放在一起看。不能因为某一种“更新”就直接判断它更适合。','checks':['两者批准适应证和目标患者是否真正重叠','关键研究的人群、对照组和主要终点是否可比较','疗效优势是否伴随不同的不良反应或监测要求','在指南或真实临床中分别处于什么治疗线次'],'next':'先确认个人疾病亚型和当前治疗阶段，再比较真正可选的方案，避免把不能互相替代的治疗放在同一张排行榜里。'},
('hospitals','comparison'):{'lead':'比较日本不同医院、专家或会诊模式时，最重要的是当前病例与机构能力是否匹配。医院名气、综合排名和专家头衔只是背景，不能替代专病经验、技术平台和实际接诊条件。','checks':['两家机构在目标疾病上的专病团队和技术能力有什么不同','当前病例需要的是诊断复核、手术、放疗、药物还是多学科决策','国际患者流程、资料预审和等待时间有什么差异','哪家机构最有可能解决当前最核心的决策问题'],'next':'把当前病例最需要解决的一个问题写在最前面，再据此比较机构和专家，而不是先按名气排序。'},
('kampo','comparison'):{'lead':'比较日本处方汉方、OTC汉方或不同方剂时，不能套用“谁更先进”的比较逻辑。真正要看的是药品类别、方剂组成、批准适应证、剂量、质量标准、适用人群和用药风险。','checks':['比较对象是同一方剂的处方/OTC版本，还是不同方剂','成分比例、剂型、厂家和每日剂量是否相同','官方适应证、目标症状和使用人群是否一致','甘草等成分重复、基础疾病和合并用药是否增加风险'],'next':'先确认准确方名和产品类别，再比较说明书与适用条件；不要只凭中文方名或网上功效列表判断。'},
('checkup','selection'):{'lead':'选择日本精密体检套餐时，原则不是“检查越多越好”，而是先按年龄、家族史、既往异常、生活方式和当前症状做风险分层，再选择能回答具体问题的项目。','checks':['个人年龄、家族史和既往异常提示哪些优先风险','基础套餐已经覆盖哪些项目，哪些追加检查真正有增量价值','有没有辐射、假阳性、侵入性或重复检查风险','异常结果出来后是否有明确的专科转诊和复查路径'],'next':'先列出个人前三位健康风险和已有检查，再据此选择套餐与追加项目，而不是从最高价套餐往下删。'},
('kampo','selection'):{'lead':'日本汉方的选择不是“一个症状对应一个万能方”。即便症状相似，也要结合官方适应证、症状组合、体质判断、年龄、基础疾病和合并用药来决定是否值得讨论某个方剂。','checks':['目标方剂在日本说明书中的适应证是什么','当前是单一症状还是有一组相互关联的症状与体征','年龄、肝肾功能、血压、电解质等基础情况是否影响安全性','是否与其他汉方或西药存在成分重复和相互作用风险'],'next':'把主要症状、持续时间、基础病和完整用药清单带给医生或药师，先判断是否适合汉方，再讨论具体方剂。'},
('kampo','drug'):{'lead':'看一个具体日本汉方方剂，不能只读“功效”。需要核对日本官方适应证、准确组成与剂量、研究对象、常见风险以及它是否适合当前人的症状组合和合并用药。','checks':['日本说明书中的正式适应证和用法是什么','具体厂家、方剂编号、组成和每日剂量是否明确','相关临床研究研究了哪些人群、用什么终点判断效果','是否存在甘草等成分重复、伪醛固酮症、肝损伤或其他已知风险'],'next':'确认准确产品后，以日本说明书和正规医疗判断为主；不要把传统用途或单项研究直接扩展成个人治疗建议。'},
('kampo','scope'):{'lead':'日本医保体系可以开具某些汉方，只说明它们在特定适应证和医疗场景中属于可使用药物，并不意味着“从感冒到癌症都能靠汉方治疗”。辅助治疗、症状管理和疾病本身的标准治疗必须分开。','checks':['具体方剂的正式适应证是什么','当前目标是改善症状、支持治疗还是治疗原发疾病','有没有更需要优先排除或治疗的明确疾病','汉方是否会与现有标准治疗或其他用药发生冲突'],'next':'先明确当前治疗目标和不能延误的标准治疗，再判断汉方是否有合适的辅助位置。'},
('kampo','verification'):{'lead':'核对日本汉方信息时，优先确认真实产品身份和官方资料。网上常把处方汉方、OTC产品、保健品和不同厂家的同名方剂混在一起，容易造成剂量与适应证误解。','checks':['产品属于处方药、OTC药还是其他类别','厂家、方剂编号、商品名和包装是否可核验','说明书中的组成、剂量、适应证和注意事项是什么','信息是否来自厂家、监管资料或正规医疗机构，而非仅来自电商宣传'],'next':'先用官方资料锁定“到底是哪一个产品”，再讨论功效、剂量或跨境获取问题。'}
}

def text(s): return re.sub(r'<[^>]+>','',html.unescape(s)).strip()
def get_h1(t):
    m=re.search(r'<h1>(.*?)</h1>',t,re.S); assert m; return text(m.group(1))
def clean_question(title): return title if title.endswith(('？','?')) else title+'？'
def repl_meta(t,name,value,prop=False):
    attr='property' if prop else 'name'; pat=rf'(<meta\s+{attr}="{re.escape(name)}"\s+content=")[^"]*(">)'
    return re.sub(pat,lambda m:m.group(1)+html.escape(value,quote=True)+m.group(2),t,count=1)
def direct_paras(t):
    m=re.search(r'<h2>直接回答</h2><div class="answer">(.*?)</div>',t,re.S); assert m
    ps=re.findall(r'<p>(.*?)</p>',m.group(1),re.S); return [text(x) for x in ps]
def update_json_scripts(t,title,desc,faq_q,faq_a):
    pat=re.compile(r'<script type="application/ld\+json">(.*?)</script>',re.S)
    def f(m):
        try: d=json.loads(m.group(1))
        except: return m.group(0)
        typ=d.get('@type') if isinstance(d,dict) else None
        if typ=='MedicalWebPage': d['description']=desc; d['dateModified']=TODAY
        if typ=='FAQPage' and d.get('mainEntity'):
            d['mainEntity'][0]['name']=faq_q; d['mainEntity'][0]['acceptedAnswer']['text']=faq_a
        return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False,separators=(',',':'))+'</script>'
    return pat.sub(f,t)
def focus_block(title,intent):
    label=LABELS.get(intent,intent)
    return f'<div class="intentFocus"><strong>本页搜索意图：</strong>{html.escape(label)}｜<strong>只解决：</strong>{html.escape(title)}</div>'

def process(folder,i,intent):
    p=ROOT/folder/f'{i:03d}'/'index.html'; t=p.read_text(encoding='utf-8'); title=get_h1(t)
    ov=O.get((folder,intent))
    if ov:
        # replace second direct-answer paragraph only; keep category safety baseline as first paragraph
        m=re.search(r'(<h2>直接回答</h2><div class="answer"><p>.*?</p>)<p>.*?</p>(</div>)',t,re.S)
        assert m,(folder,i,'answer')
        t=t[:m.start()]+m.group(1)+f'<p>{html.escape(ov["lead"])}</p>'+m.group(2)+t[m.end():]
        lis=''.join(f'<li>{html.escape(x)}</li>' for x in ov['checks'])
        t,n=re.subn(r'(<h2>这个问题真正要核对什么？</h2><ul>).*?(</ul>)',lambda m:m.group(1)+lis+m.group(2),t,count=1,flags=re.S); assert n==1
        t,n=re.subn(r'(<h2>对患者最有用的下一步</h2><p>).*?(</p>)',lambda m:m.group(1)+html.escape(ov['next'])+m.group(2),t,count=1,flags=re.S); assert n==1
    # unique, visible intent marker after metadata to make page purpose explicit
    t=re.sub(r'<div class="intentFocus">.*?</div>','',t,flags=re.S)
    t,n=re.subn(r'(<p class="meta">.*?</p>)',lambda m:m.group(1)+focus_block(title,intent),t,count=1,flags=re.S); assert n==1
    if '.intentFocus{' not in t:
        t=t.replace('.next{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}', '.next{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}.intentFocus{margin:12px 0 22px;padding:10px 12px;border-radius:10px;background:#f4f7f9;font-size:14px;line-height:1.6}')
    # cleaner intent-led meta description
    desc=f'JapanMedAI专题解答“{title}”。聚焦{LABELS.get(intent,intent)}：提供直接答案、关键核对项、适用边界和下一步准备。内容用于医学信息教育，不替代医生诊断或个体治疗。'
    t=repl_meta(t,'description',desc)
    t=repl_meta(t,'og:description',desc,prop=True)
    # FAQ #1 uses the actual user query and the page's direct answer rather than a generic disclaimer question
    ps=direct_paras(t); faq_q=clean_question(title); faq_a=' '.join(ps[:2])
    m=re.search(r'(<h2>常见问题</h2>)<h3>.*?</h3><p>.*?</p>',t,re.S); assert m,(folder,i,'faq visible')
    replacement=m.group(1)+f'<h3>{html.escape(faq_q)}</h3><p>{html.escape(faq_a)}</p>'
    t=t[:m.start()]+replacement+t[m.end():]
    t=update_json_scripts(t,title,desc,faq_q,faq_a)
    p.write_text(t,encoding='utf-8')

def validate():
    titles=[]; bodies={}
    for folder in FOLDERS:
        arr=[]
        for i,intent in enumerate(INTENTS[folder],1):
            p=ROOT/folder/f'{i:03d}'/'index.html'; t=p.read_text(encoding='utf-8'); title=get_h1(t); arr.append(title); titles.append((folder,i,title))
            for req in ['<div class="intentFocus">','"@type":"MedicalWebPage"','"@type":"FAQPage"','<h2>适用边界</h2>']:
                assert req in t,(folder,i,req)
            assert f'<h3>{html.escape(clean_question(title))}</h3>' in t,(folder,i,'faq1')
            bodies[(folder,i)]=text(re.search(r'<article>(.*?)</article>',t,re.S).group(1))
        assert len(arr)==30 and len(set(arr))==30
        for a in range(30):
            for b in range(a+1,30): assert SequenceMatcher(None,arr[a],arr[b]).ratio()<0.80,(folder,arr[a],arr[b])
    # known semantic anti-patterns must be gone from sensitive intent/category combinations
    for i in [13,20,25]: assert '当前监管状态和适应证写的是什么' not in (ROOT/'hospitals'/f'{i:03d}'/'index.html').read_text(encoding='utf-8')
    for i in [3,11,16]: assert '当前医院是否都具备实际实施条件' not in (ROOT/'kampo'/f'{i:03d}'/'index.html').read_text(encoding='utf-8')
    for i in [1,14,15,17,29]: assert '当前医院是否都具备实际实施条件' not in (ROOT/'ips'/f'{i:03d}'/'index.html').read_text(encoding='utf-8')
    # no exact duplicate article text after stripping HTML
    vals=list(bodies.values()); assert len(vals)==len(set(vals))==180
    print('QA PASS: 180 pages; unique titles; category-specific intent overrides; FAQ/meta aligned.')

def main():
    for folder in FOLDERS:
        for i,intent in enumerate(INTENTS[folder],1): process(folder,i,intent)
    validate()
if __name__=='__main__': main()
