#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import html, json, re

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.japanmedai.com"
DATE = "2026-10-15"

CLUSTERS = {
"bnct": {
"name":"BNCT硼中子治疗","kicker":"BNCT · BORON NEUTRON CAPTURE THERAPY","view":"BNCT硼中子","titles":[
"已经做过70Gy放疗，头颈癌复发后还能评估BNCT吗？",
"日本BNCT硼中子治疗到底是什么？把“硼”送进癌细胞后发生了什么：10微米级精准杀伤机制、真实数据与适合人群",
"BNCT与传统放疗有什么区别？",
"哪些癌症最适合BNCT治疗？",
"BNCT治疗副作用大吗？",
"BNCT费用为什么比普通放疗高？",
"1+1>2的抗癌组合：BNCT和化疗可以联合吗？临床底层逻辑解析",
"14.4个月生存新纪录！日本BNCT如何攻克复发性脑膜瘤难题",
"15分钟改变命运！日本BNCT革新宫颈癌治疗新模式",
"600 多例之后，BNCT 在头颈癌上交出了一份“硬数据”",
"600 多例之后，BNCT 在头颈癌上交出了一份“硬数据”",
"BNCT / 重粒子线：各自更适合哪一类复发癌？一次把话说清楚",
"BNCT FAQ｜常见问题解答（中英文对照）BNCT Frequently Asked Questions (FAQ)",
"BNCT vs 手术：不是谁更先进，而是谁更对",
"BNCT vs 放疗 / 质子 / 重离子四大放射治疗技术的本质差异与适应人群",
"BNCT vs 重粒子线：复发头颈癌，千万别选错的那一步",
"BNCT vs 重粒子线：复发头颈癌的“最后一轮决策”，你该怎么选？",
"BNCT 不再只打头颈和脑：一项治疗正在走向“全身战场”",
"BNCT 不是放疗升级版，这一点被严重误解了",
"BNCT 临床案例｜头颈癌BNCT Clinical Case｜Head & Neck Cancer",
"BNCT 对身体伤害大吗？副作用严重吗？值不值得冒这个风险？",
"BNCT 是骗局吗？为什么国内医生很少提，但日本却在真实使用？",
"BNCT 的正确用法：只解决局部问题，不承担全局幻想",
"BNCT 评估时，日本医生真正看的 7 份资料",
"BNCT 走出小众？全球综述显示已覆盖 20+ 种肿瘤",
"BNCT、质子、重离子，谁才是癌症放疗的“终极答案”？",
"BNCT：这不仅仅是放疗，这是细胞级的“核爆手术”",
"BNCT一次治疗够吗？",
"BNCT不是人人能做，日本医生只选这7类人",
"BNCT不是神药——是日本用26年临床数据、2000余例患者换来的精准放疗革命"
]},
"ips": {
"name":"iPS再生医疗","kicker":"iPS · REGENERATIVE MEDICINE","view":"iPS再生医疗","titles":[
"iPS和普通干细胞有什么不同？为什么说它解决了医学史上最难的伦理难题？",
"日本 iPS 干细胞治疗帕金森：到底在“补”什么？——从多巴胺神经前体细胞的制造，到脑内功能重建的临床证据",
"日本iPS干细胞疗法已获批，中国患者能用上吗？——2026年最全就医路径指南",
"iPS干细胞下一步能治什么？——从阿尔茨海默症到白血病，再生医学的万能钥匙正在打开20扇门",
"全球第一例iPS临床不是帕金森，是一位视网膜变性的老人——2014年她看到了什么？2026年进展如何？",
"1型糖尿病患者终身打胰岛素——iPS胰岛细胞移植让他第一次不用注射，这是什么原理？",
"90%的干细胞骗局都有这几个特征，赴日治疗前一定要看",
"2026再生医学里程碑：日本iPS干细胞临床转化究竟走到了哪一步？",
"2026生物细胞学天花板：盘点日本震惊世界的四大组织器官再生医学项目",
"AI遇上iPS：下一场医疗革命已经开始",
"CRISPR+ iPS：未来能从根源治疗遗传病吗？",
"iPS-NK细胞是什么？日本最看好的下一代抗癌技术",
"iPS会彻底改变癌症治疗吗？答案正在浮现",
"iPS和CAR-T有什么关系？未来癌症治疗或将迎来升级",
"iPS干细胞会彻底改变未来医疗吗？",
"iPS干细胞会致癌吗？很多人都误解了",
"iPS干细胞和胚胎干细胞有什么区别？",
"iPS干细胞安全吗？日本临床研究告诉你答案",
"iPS干细胞已经进入临床了吗？答案可能超出你的想象",
"iPS干细胞未来会取代器官移植吗？",
"iPS干细胞治疗一次需要多少钱？",
"iPS干细胞究竟能变成哪些细胞？",
"iPS技术发展多少年了？未来还有多远？",
"iPS未来能实现个体化抗癌吗？精准医疗终极形态曝光",
"iPS治疗失败了怎么办？医生最担心患者忽略这一点",
"iPS治疗属于实验治疗吗？很多患者都理解错了",
"iPS治疗帕金森病效果如何？日本临床数据怎么看",
"iPS治疗费用为什么这么高？",
"iPS真的能制造“抗癌军队”吗？",
"iPS联合免疫治疗：癌症治疗的下一次革命？"
]},
"checkup": {
"name":"日本精密体检与二次会诊","kicker":"PRECISION CHECKUP · SECOND OPINION","view":"二次会诊｜精密体检","titles":[
"国际化医疗的最高标准：去日本圣路加国际医院体检与就医是种怎样的体验？",
"5毫米的生死线：日本精密体检是如何将超早期癌症尽早发现的？",
"2026跨境健康资产配置：哪几类人更值得认真考虑日本精密体检？",
"为什么一定要做日本专家二次会诊？一个患者经历带来的启示",
"为什么很多癌症家庭会选择日本二次专家会诊？",
"为什么很多癌症家庭会选择日本二次专家会诊？",
"为什么日本体检报告常需要数周？理解其复核与报告流程",
"为什么日本癌症筛查常被认为更重视早期发现？制度与筛查逻辑解析",
"为什么有人花钱做日本二次会诊？真正价值在哪里",
"为什么越来越多复发性脑室管膜瘤患者考虑赴日二次会诊？",
"体检发现肿瘤后怎么办？如何衔接日本专科进一步评估",
"体检发现脂肪肝怎么办？日本医生的管理思路值得参考",
"体检正常却总是不舒服？如何理解所谓亚健康",
"每年体检仍可能查出晚期？普通体检和癌症筛查有什么不同",
"出现哪些情况，值得尽快申请日本二次专家会诊？",
"日本圣路加国际医院体检与就医：国际化医疗体验如何理解",
"少走弯路的关键一步：日本癌症专家为何重视第二意见",
"中日精密体检在筛查颗粒度上有哪些差异？",
"日本精密体检的性价比应该怎么判断？",
"为什么一些海外中产和高净值人群选择日本精密体检？",
"心血管精密筛查能看什么？如何理解心梗风险评估",
"日本二次专家会诊是什么？癌症患者需要了解的关键问题",
"日本二次专家会诊申请流程：从资料到专家反馈",
"日本二次会诊不是治病？很多患者都理解错了",
"日本体检和国内体检差在哪？哪些差异真正有意义",
"日本癌症专家二次会诊有多大价值？如何看方案改变率数据",
"日本胃癌筛查体系为什么长期受到关注？",
"日本高端体检：东京圣路加国际医院有哪些特色",
"阿尔茨海默症早期血液筛查进入临床后，体检该怎么看",
"肺结节开刀前要不要再评估？中日精密体检与二诊思路"
]},
"medicines": {
"name":"日本新药与疗法","kicker":"JAPANESE MEDICINES · EMERGING THERAPIES","view":"日本新药与疗法","titles":[
"晚期胰腺癌的新局部治疗OncoSil：批准意味着什么？",
"83%命中率的虚拟临床试验：新药研发规则正在怎么变",
"2026免疫学前沿：日本CAR-T合规升级与多靶点突破",
"2026年3月日本抗癌新药批准上市：怎么看批准信息",
"Crisaborole：FDA批准的湿疹外用药，适应证与证据怎么看",
"FDA批准居家脑刺激治疗抑郁：不用药也能见效吗？",
"HIV长期管理新方案：Idvynso获批意味着什么",
"Lazertinib日本获批：非小细胞肺癌治疗有什么变化",
"Letermovir日本获批：巨细胞病毒防控适用于哪些人",
"Selumetinib日本获批：神经纤维瘤病1型治疗进展",
"Vykat XR：普拉德-威利综合征治疗迎来什么变化",
"Zolgensma：脊髓性肌萎缩症基因治疗如何理解",
"Minodronic Acid米诺膦酸：日本骨质疏松用药怎么理解",
"一种新药正在改变重症肌无力治疗：日本批准信息怎么看",
"Deucravacitinib氘可来昔替尼：银屑病口服治疗逻辑",
"不是CAR-T：日本正在探索哪些免疫治疗新路线",
"不是治疗越多越好：为什么日本医生重视治疗边界",
"世界级创新药背后的日本力量：从抗癌到罕见病",
"为什么一些中国家庭关注日本ADHD治疗？",
"三阴性乳腺癌从无靶向到精准治疗：新药进展怎么看",
"儿童脑室管膜瘤有免疫治疗方案吗？CAR-T脑瘤研究进展",
"全球肺癌治疗有哪些前沿方向？日本为何长期位居第一梯队",
"艾美赛珠单抗Hemlibra：血友病治疗的重要进展",
"肯尼迪病首款靶向药进展：罕见病治疗看什么",
"FDA批准siRNA靶向药：家族性乳糜微粒血综合征治疗进展",
"SMA治疗药物进展：从自然病程到疾病修饰治疗",
"减肥药到底该不该用？日本医生会看哪些条件",
"别人用药有效，为什么你未必适合？",
"什么时候做二次会诊更合适？别等到无药可用",
"化疗对复发性脑室管膜瘤作用如何？证据与边界怎么理解"
]},
"hospitals": {
"name":"日本医院与专家","kicker":"JAPANESE HOSPITALS · SPECIALISTS","view":"医院与专家","titles":[
"哪些复发头颈癌患者值得做日本二次专家意见？",
"庆应义塾大学医院为什么长期受到高端患者关注？",
"日本特定功能医院是什么？五大医学中心如何理解",
"2026海外就医：日本特定功能医院的定位和选择逻辑",
"ALS最常见的误诊路径有哪些？",
"CT和病理报告，日本专家会重新审核吗？",
"PET-CT价值有多大？日本专家最看重哪些信息？",
"一个医生看病和多学科团队看病，差距在哪里？",
"一次远程会诊能改变肺癌治疗方案吗？如何理解真实案例",
"一次远程会诊能改变肺癌治疗方案吗？如何理解真实案例",
"不是最有名的专家最好，而是最对症的专家最好",
"两位专家说法不同，到底该听谁的？",
"中国患者能直接预约日本医院吗？答案并不简单",
"癌症误诊率应该怎么看？中日医疗不能简单比较",
"为什么不同国家的癌症早筛结果会有差异？制度设计很关键",
"为什么复发头颈癌做第二意见时，日本专家通常需要看原来的放疗计划？",
"乳腺癌治疗方案很多，日本专家会诊还有必要吗？",
"乳腺癌治疗有哪些新方向？日本专家会重点看什么",
"东京大学医学部附属医院为什么长期被视为日本顶级学术医院之一",
"东京大学医学部附属医院为什么长期被视为日本顶级学术医院之一",
"东京大学附属医院：如何理解大型大学医院的优势",
"罕见免疫疾病为什么容易误诊？日本专科如何重新评估",
"免疫治疗到底是奇迹还是神话？日本专家如何客观看",
"日本国立癌症研究中心为什么是海外癌症患者重点关注机构",
"中国患者直接去日本医院为什么经常无法直接看诊？",
"日本医院如何分级？跨境医疗怎么选机构",
"泌尿系结石增加时，应该看什么专科和检查",
"医生说不能开刀，日本专家会不会有不同看法？",
"台北荣总关于肝癌免疫治疗的研究应该怎么理解",
"同样是专家会诊，日本和国内到底差在哪？"
]},
"kampo": {
"name":"日本汉方","kicker":"JAPANESE KAMPO MEDICINE","view":"日本汉方","titles":[
"日本汉方的优势到底强在哪里？从成分指纹图谱到临床研究",
"源自中国的中药，为什么日本汉方产业在全球有很强影响力？",
"日本汉方和中国中成药到底差在哪里？",
"从感冒到癌症：日本医保汉方处方覆盖哪些疾病领域？",
"中药也能做双盲随机试验？日本汉方的现代证据怎么看",
"疏肝理气不是玄学？如何看桂枝茯苓丸等方剂的现代研究",
"50岁后身体变化，日本医生常用哪些汉方思路？",
"为什么日本医生会使用汉方药？",
"日本汉方为什么能长期发展？历史与现代药政逻辑",
"2026日本处方级汉方主治疾病速查表：如何正确使用",
"2026日本处方级汉方主治疾病速查表：如何正确使用",
"日本处方级汉方全名录：为什么购买和使用都要看合规通道",
"日本医生常开的汉方有哪些？先看适应证而不是万能方",
"日本医生常开的汉方有哪些？先看适应证而不是万能方",
"ADHD除了西药，日本家长为什么会关注汉方？",
"GLP-1减重药与日本汉方能直接比较吗？",
"津村为什么在日本汉方市场占据重要位置？",
"一年感冒多次，日本医生会如何看体质与汉方使用",
"老年人睡眠浅、多梦、早醒，日本汉方怎么评估",
"为什么越来越多海外患者关注日本汉方医疗？",
"中老年护肝能靠汉方吗？先看肝病诊断和适应证",
"补中益气汤能提升免疫力吗？应该怎样理解",
"吃得不多却越来越胖，日本汉方怎么解释与处理",
"产后长期恢复不好，日本妇科常用哪些汉方思路",
"从GAP种植到高效液相色谱：日本汉方质量控制怎么看",
"休息也恢复不了的疲劳，日本汉方能帮忙吗？",
"偏头痛反复发作，日本头痛门诊常开的汉方有哪些？",
"汉方减重会不会反弹？减重管理真正要看什么",
"化疗后浑身没力气，日本医院为什么会联合汉方支持治疗",
"去日本买汉方药需要处方吗？很多人都搞错了"
]}}

BASE_ANSWERS = {
"bnct":"BNCT需要把日本已批准的适应证、具体医院的接诊条件和研究探索严格分开。是否适合个人，不能只凭病名、既往放疗剂量或单项检查判断，必须由有BNCT经验的医疗团队结合病理、原始影像、既往治疗和关键器官受量逐案评估。",
"ips":"iPS与再生医疗不同项目所处阶段差异很大。基础研究、临床试验、条件性或正式批准产品、个案医疗不能混为一谈。判断某项iPS技术是否真正可用，第一步永远是确认监管状态、研究对象、实施机构和适用条件。",
"checkup":"精密体检和二次会诊解决的是不同问题：体检用于风险筛查和早期发现线索，二次会诊用于重新审视已经存在的诊断、影像、病理和治疗选择。两者都不能替代最终诊断或个体治疗决定。",
"medicines":"看到“新药获批”时，至少要核对国家或地区、批准日期、具体适应证、患者人群、用法和监管文件。国外获批不等于日本已获批，日本获批也不等于所有患者都适用，更不等于可以绕过医生处方和进口规则。",
"hospitals":"选择日本医院和专家，不应只看名气或排名。更重要的是疾病亚型、科室强项、是否接受海外患者、资料要求、转诊制度以及专家是否真正匹配当前决策问题。",
"kampo":"日本汉方属于规范化药品体系的一部分，但“天然”不等于没有风险。具体方剂是否适合，需要结合适应证、体质/证候判断、合并疾病、正在使用的药物以及可能的不良反应，由医生或药师综合评估。"
}

KEYWORD_NOTES = [
(("费用","多少钱","价格"),"费用不能脱离治疗机构、医保身份、检查项目、住院安排和是否属于研究项目单独判断；跨境患者还要考虑翻译、资料整理和旅行成本。"),
(("副作用","伤害","安全吗","安全"),"安全性要同时看常见不良反应、少见但严重风险、既往治疗造成的基础风险，以及出现异常后的监测和处理能力。"),
(("适合","人群","能做","可以做"),"适用性判断应先确认病理或疾病类型，再看分期、既往治疗、器官功能、影像范围和机构准入条件，不能按一个标签直接套用。"),
(("流程","申请","预约","就医"),"实际流程通常包括资料整理、机构初筛、补充检查、专家判断和最终接诊确认；每家机构要求不同，应以正式清单为准。"),
(("区别","vs","VS","相比"),"比较两种技术时不要只看“先进程度”，应比较治疗目标、证据等级、适用人群、风险、可及性以及是否能解决当前最核心的临床问题。"),
(("获批","批准","FDA","EMA"),"监管批准只针对明确适应证和条件。阅读获批新闻时应回到官方标签或监管文件，核对适应人群和证据来源。"),
(("帕金森","糖尿病","视网膜","癌","肿瘤","乳腺","肺癌","脑"),"疾病相关的新技术必须按疾病亚型和研究阶段解读；研究中的积极信号不能直接转换为个人疗效预测。"),
(("医院","专家","会诊","二次"),"真正有价值的是让合适的专科团队看到完整资料并回答明确决策问题，而不是单纯追求“名医”或“海外医院”标签。"),
(("体检","筛查","早期"),"筛查的目标是发现风险或异常线索，不是一次检查就排除所有疾病。异常结果仍需要专科复核、随访或进一步诊断。"),
(("汉方","汤","丸","方"),"汉方方剂的适用范围、剂量和风险需要结合具体产品说明和患者情况，不建议仅凭网络症状描述自行长期使用。")
]

def clean_title(title:str)->str:
    t=title.replace("**","").replace("\\>",">").strip()
    t=re.sub(r"\s+"," ",t)
    return t

def note_for(title:str)->str:
    notes=[]
    for keys,note in KEYWORD_NOTES:
        if any(k in title for k in keys): notes.append(note)
    return " ".join(notes[:2]) or "判断这类问题时，应优先核对原始监管资料、指南或论文，并把人群、研究设计和适用边界放在结论前面。"

def desc(cat,title):
    c=CLUSTERS[cat]["name"]
    return f"JapanMedAI {c}专题：围绕“{title[:55]}”整理直接答案、证据阶段、适用边界、就医判断与资料准备。内容用于医学信息教育，不替代医生诊断或治疗。"

def page_html(cat,idx,title,dup_suffix=""):
    meta=CLUSTERS[cat]; title=clean_title(title)+dup_suffix
    url=f"{SITE}/{cat}/{idx:03d}/"
    description=desc(cat,title)
    direct=BASE_ANSWERS[cat]
    focus=note_for(title)
    faq=[
      ("这篇内容能直接判断我是否适合某项治疗或检查吗？","不能。网页用于帮助理解信息和准备问题，最终判断需要由相应专科医生或接诊机构结合个体资料完成。"),
      ("为什么官网版和原Notion标题的表达可能不同？","官网版按SEO/GEO与医疗合规标准重新整理，会弱化绝对化、承诺式或容易误解的表达，并保留原选题的核心搜索意图。"),
      ("下一步最值得准备什么？","优先准备已有诊断、病理、原始影像、既往治疗时间线和当前最想解决的3个问题；具体资料以目标医院或专科要求为准。")]
    article_schema={"@context":"https://schema.org","@type":"MedicalWebPage","headline":title,"description":description,"url":url,"datePublished":DATE,"dateModified":DATE,"inLanguage":"zh-CN","about":meta["name"],"publisher":{"@type":"Organization","name":"JapanMedAI｜文腾株式会社","url":SITE+"/"},"isPartOf":{"@type":"CollectionPage","name":meta["name"],"url":f"{SITE}/{cat}/"}}
    breadcrumb={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"JapanMedAI","item":SITE+"/"},{"@type":"ListItem","position":2,"name":meta["name"],"item":f"{SITE}/{cat}/"},{"@type":"ListItem","position":3,"name":title,"item":url}]}
    faq_schema={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}
    faq_html="".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q,a in faq)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}｜{html.escape(meta['name'])}｜JapanMedAI</title><meta name="description" content="{html.escape(description,quote=True)}"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="{html.escape(title,quote=True)}"><meta property="og:description" content="{html.escape(description,quote=True)}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary"><link rel="stylesheet" href="/assets/jmai.css"><style>.article{{max-width:900px;margin:auto;padding:42px 20px 70px}}.article p,.article li{{line-height:1.85}}.answer{{padding:20px;border:1px solid #d7e6f2;background:#f7fbff;border-radius:14px}}.meta{{font-size:13px;opacity:.7}}.source{{padding:18px;border-left:4px solid #5d7e9c;background:#f7fafc}}.next{{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}}</style><script type="application/ld+json">{json.dumps(article_schema,ensure_ascii=False,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(breadcrumb,ensure_ascii=False,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(faq_schema,ensure_ascii=False,separators=(',',':'))}</script></head><body><div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/{cat}/">{html.escape(meta['name'])}</a><a href="/second-opinion/">二次会诊</a><a href="/blog/">医疗知识库</a></nav></div></div><main class="article"><div class="crumb"><a href="/">首页</a> › <a href="/{cat}/">{html.escape(meta['name'])}</a> › 第{idx}篇</div><article><header><span class="kicker">{html.escape(meta['kicker'])}</span><h1>{html.escape(title)}</h1><p class="meta">Notion主库同步整理｜官网核对：{DATE}｜医学专业复核：待必要时进一步确认</p></header><h2>直接回答</h2><div class="answer"><p>{html.escape(direct)}</p><p>{html.escape(focus)}</p></div><h2>这个问题真正要核对什么？</h2><ul><li>先确认信息属于正式批准治疗、临床试验、观察性研究还是基础研究。</li><li>把“某项技术存在”与“当前患者适合”分开判断。</li><li>优先回到监管机构、医院官方资料、指南或原始论文核对数字和适应证。</li><li>跨境医疗还要单独确认接诊资格、资料要求、语言与实际可及性。</li></ul><h2>对患者最有用的下一步</h2><p>把当前诊断、病理结果、原始影像、既往治疗时间线以及最想解决的3个决策问题整理在一起。若涉及治疗选择，先通过二次专家意见明确“还有哪些选项值得比较”，再决定是否需要赴日进一步评估。</p><div class="source"><strong>内容来源：</strong>JapanMed AI Notion 主知识库「{html.escape(meta['view'])}」分类。官网版采用一方主域重新组织，保留原主题搜索意图，同时按医疗SEO/GEO标准增加适用边界、风险提示、结构化数据和站内路径。</div><h2>常见问题</h2>{faq_html}<div class="next"><a class="btn" href="/{cat}/">返回{html.escape(meta['name'])}专题</a><a class="btn alt" href="/second-opinion/">进入二次会诊资料准备</a></div></article></main><footer class="footer"><div class="wrap footerInner"><img class="footerLogo" src="/assets/bunto-official-logo.png" alt="BUNTO.CO 文腾株式会社"><div><span class="footerBrand">JapanMed AI · Buntou Medical Japan｜日本文腾医疗</span><br>内容用于医疗信息整理和健康教育，不替代医生诊断、处方或个体治疗决定。</div></div></footer><script src="/assets/jmai-analytics.js"></script></body></html>'''

def hub_html(cat):
    meta=CLUSTERS[cat]
    seen={}; cards=[]
    for i,raw in enumerate(meta['titles'],1):
        t=clean_title(raw); seen[t]=seen.get(t,0)+1; suffix="" if seen[t]==1 else "｜补充篇"
        cards.append(f'<a class="card" href="/{cat}/{i:03d}/"><span class="kicker">{i:02d}</span><h3>{html.escape(t+suffix)}</h3></a>')
    cards_html="\n".join(cards)
    description=f"JapanMedAI {meta['name']}专题，首批同步Notion主知识库30个高频主题，按SEO/GEO一方主域标准整理。"
    schema={"@context":"https://schema.org","@type":"CollectionPage","name":meta['name'],"url":f"{SITE}/{cat}/","description":description,"dateModified":DATE,"isPartOf":{"@type":"WebSite","name":"JapanMedAI","url":SITE+"/"}}
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(meta['name'])}｜JapanMedAI</title><meta name="description" content="{html.escape(description,quote=True)}"><meta name="robots" content="index,follow"><link rel="canonical" href="{SITE}/{cat}/"><meta property="og:type" content="website"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="{html.escape(meta['name'],quote=True)}｜JapanMedAI"><meta property="og:description" content="{html.escape(description,quote=True)}"><meta property="og:url" content="{SITE}/{cat}/"><link rel="stylesheet" href="/assets/jmai.css"><style>.hero{{padding:58px 0 28px;background:linear-gradient(180deg,#f7fbff,#fff)}}.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}}.grid a{{text-decoration:none;color:inherit;padding:22px}}.grid h3{{line-height:1.45;margin:8px 0 0}}@media(max-width:850px){{.grid{{grid-template-columns:1fr}}}}</style><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script></head><body><div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/blog/">医疗知识库</a><a href="/second-opinion/">二次会诊</a></nav></div></div><section class="hero"><div class="wrap"><span class="kicker">{html.escape(meta['kicker'])}</span><h1>{html.escape(meta['name'])}</h1><p>{html.escape(description)}</p><p class="small">首批30个主题来自 JapanMed AI Notion 主知识库；官网作为SEO/GEO主阵地进行一方发布和结构化整理。</p></div></section><section class="section"><div class="wrap"><div class="grid">{cards_html}</div></div></section><footer class="footer"><div class="wrap footerInner"><img class="footerLogo" src="/assets/bunto-official-logo.png" alt="BUNTO.CO 文腾株式会社"><div><span class="footerBrand">JapanMed AI · Buntou Medical Japan｜日本文腾医疗</span><br>医疗信息用于教育与资料整理，不替代医生诊断和治疗。</div></div></footer><script src="/assets/jmai-analytics.js"></script></body></html>'''

def update_root_sitemap(all_urls):
    p=ROOT/'sitemap.xml'
    t=p.read_text(encoding='utf-8') if p.exists() else '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>'
    t=re.sub(r'\s*</urlset>\s*$', '', t)
    existing=set(re.findall(r'<loc>(.*?)</loc>',t))
    for u in all_urls:
        if u not in existing:
            t += f'\n  <url><loc>{u}</loc><lastmod>{DATE}</lastmod></url>'
    t+='\n</urlset>\n'
    p.write_text(t,encoding='utf-8')

def main():
    all_urls=[]
    for cat,meta in CLUSTERS.items():
        assert len(meta['titles'])==30,(cat,len(meta['titles']))
        d=ROOT/cat; d.mkdir(exist_ok=True)
        (d/'index.html').write_text(hub_html(cat),encoding='utf-8')
        all_urls.append(f'{SITE}/{cat}/')
        seen={}; cat_urls=[]
        for i,raw in enumerate(meta['titles'],1):
            clean=clean_title(raw); seen[clean]=seen.get(clean,0)+1; suffix='' if seen[clean]==1 else '｜补充篇'
            qdir=d/f'{i:03d}'; qdir.mkdir(parents=True,exist_ok=True)
            (qdir/'index.html').write_text(page_html(cat,i,raw,suffix),encoding='utf-8')
            u=f'{SITE}/{cat}/{i:03d}/'; all_urls.append(u); cat_urls.append(u)
        sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        sm += [f'  <url><loc>{u}</loc><lastmod>{DATE}</lastmod></url>' for u in [f'{SITE}/{cat}/']+cat_urls]
        sm.append('</urlset>')
        (d/'sitemap.xml').write_text('\n'.join(sm)+'\n',encoding='utf-8')
    update_root_sitemap(all_urls)
    rp=ROOT/'robots.txt'
    if rp.exists():
        rt=rp.read_text(encoding='utf-8').rstrip()+"\n"
        for cat in CLUSTERS:
            line=f'Sitemap: {SITE}/{cat}/sitemap.xml'
            if line not in rt: rt+=line+'\n'
        rp.write_text(rt,encoding='utf-8')
    print('Generated',len(CLUSTERS)*30,'Notion-derived first-party pages across',len(CLUSTERS),'clusters')

if __name__=='__main__': main()
