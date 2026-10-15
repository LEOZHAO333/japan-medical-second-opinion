#!/usr/bin/env python3
from pathlib import Path
import html, json, re, sys
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.japanmedai.com"
TODAY = "2026-10-15"

TITLES = {
  "bnct": [
    "已经做过70Gy放疗，头颈癌复发后还能评估BNCT吗？",
    "BNCT硼中子治疗是什么？原理、硼药与中子照射怎么配合",
    "BNCT与普通放疗有什么区别？作用机制、剂量与适用场景比较",
    "日本BNCT目前批准哪些适应证？哪些癌种仍处于研究阶段",
    "BNCT常见副作用有哪些？急性反应与恢复期风险怎么判断",
    "日本BNCT治疗费用由哪些部分构成？评估、硼药与照射怎么计算",
    "BNCT能和化疗或免疫治疗联合吗？证据阶段与治疗时序怎么判断",
    "复发性脑膜瘤做BNCT效果如何？PFS、OS和研究数据怎么读",
    "宫颈癌可以做BNCT吗？日本研究进展与适用边界",
    "复发头颈癌BNCT疗效怎么看？ORR、OS与随访数据如何解读",
    "日本BNCT治疗哪些复发头颈癌已进入临床应用？适应证与接诊边界",
    "BNCT和重粒子线怎么选？复发癌评估时要比较哪些条件",
    "BNCT治疗流程是什么？从资料评估、硼药到中子照射",
    "BNCT和手术怎么选？局部治疗目标与风险比较",
    "BNCT、质子、重粒子和普通放疗有什么本质区别",
    "复发头颈癌既往放疗后，BNCT与重粒子评估分别看什么",
    "BNCT可以做第二次吗？再次治疗需要重新评估哪些风险",
    "BNCT除了头颈癌和脑肿瘤还能治什么？研究癌种与证据阶段",
    "BNCT属于放疗吗？为什么不能简单理解为“放疗升级版”",
    "BNCT真实病例应该怎么看？个案、队列研究与疗效证据有什么区别",
    "BNCT有哪些严重或长期风险？关键器官受量为什么重要",
    "BNCT靠谱吗？日本临床应用、批准状态与研究范围怎么核对",
    "BNCT能控制全身转移吗？局部治疗与系统治疗的边界",
    "申请日本BNCT评估要准备哪些资料？病理、DICOM和放疗计划清单",
    "BNCT已研究20多种肿瘤意味着什么？“研究过”不等于“可治疗”",
    "BNCT能治疗深部肿瘤吗？中子穿透、硼分布与剂量限制",
    "BNCT为什么能做到微米级杀伤？α粒子和锂核的作用范围",
    "BNCT一次治疗够吗？单次照射、重复治疗与随访怎么理解",
    "哪些患者更值得评估BNCT？病理、位置、既往治疗等7项条件",
    "BPA-PET和LAT1能预测BNCT效果吗？硼摄取评估怎么理解"
  ],
  "ips": [
    "iPS细胞和间充质干细胞有什么不同？来源、能力与临床阶段比较",
    "iPS治疗帕金森病是在补什么？多巴胺神经前体细胞原理",
    "日本iPS疗法哪些已经进入临床？海外患者能否申请要看什么",
    "iPS未来可能用于哪些疾病？神经、眼科、心脏和免疫方向一览",
    "全球首例iPS视网膜临床研究做了什么？眼科再生证据怎么读",
    "iPS胰岛细胞能治疗1型糖尿病吗？原理与临床研究阶段",
    "如何识别“赴日干细胞治疗”骗局？正规研究与商业项目的7个区别",
    "2026日本iPS临床转化走到哪一步？批准、试验与研究要分开",
    "日本iPS器官再生有哪些重点方向？心肌、角膜、血液与神经系统",
    "AI如何用于iPS研究？细胞筛选、质量控制与药物研发场景",
    "CRISPR与iPS为什么常被一起研究？遗传病模型与治疗潜力",
    "iPS-NK细胞是什么？抗癌机制与临床研究阶段",
    "iPS可以用于癌症治疗吗？免疫细胞、模型与药物筛选三条路线",
    "iPS和CAR-T有什么关系？通用型免疫细胞为什么受关注",
    "iPS细胞和胚胎干细胞有什么区别？来源、伦理与应用比较",
    "iPS细胞会致癌吗？肿瘤形成风险来自哪里",
    "自体iPS和异体iPS有什么区别？成本、时间与免疫排斥怎么比较",
    "iPS治疗安全吗？日本如何做细胞质量和长期随访",
    "iPS已经进入临床了吗？临床试验和获批治疗有什么区别",
    "iPS未来能替代器官移植吗？真正难点在血管、结构与免疫",
    "iPS治疗一次多少钱？先分清临床试验、获批产品和商业项目",
    "iPS细胞能变成哪些细胞？多能性意味着什么",
    "iPS技术发展到第几年了？从山中伸弥发现到临床转化",
    "iPS能做个体化抗癌吗？患者来源细胞和精准药物筛选怎么用",
    "iPS治疗没有达到预期怎么办？疗效终点、随访与后续方案怎么判断",
    "iPS治疗属于实验治疗吗？看监管状态、试验阶段和适应证",
    "iPS治疗帕金森病效果如何？日本临床数据应该怎么看",
    "iPS疗法为什么贵？细胞制造、质控和长期随访成本",
    "iPS来源T细胞和NK细胞有什么区别？抗癌应用怎么比较",
    "iPS联合免疫治疗到了哪一步？研究证据与临床可及性"
  ],
  "checkup": [
    "东京圣路加国际医院体检适合哪些人？项目定位与选择逻辑",
    "日本精密体检真能更早发现癌症吗？早筛能力与局限怎么理解",
    "第一次去日本做精密体检，套餐应该怎么选",
    "日本二次会诊可能改变什么？病理、分期和治疗方案三种结果",
    "哪些癌症患者更值得做日本二次专家会诊",
    "申请日本二次会诊要准备哪些资料？病理、影像和治疗时间线清单",
    "日本体检报告为什么常需要数周？复核、读片与报告流程",
    "日本癌症筛查为什么强调早期发现？筛查项目与风险分层怎么理解",
    "日本二次会诊值不值得做？费用、时间和决策价值怎么衡量",
    "复发性脑室管膜瘤为什么值得考虑日本二次会诊",
    "体检发现肿瘤或可疑结节后，下一步应该怎么衔接日本专科",
    "体检发现脂肪肝后怎么办？哪些情况需要进一步检查",
    "体检都正常却一直不舒服，还需要进一步专科评估吗",
    "每年体检为什么仍可能发现晚期癌症？普通体检与癌症筛查的区别",
    "出现哪些情况，值得尽快申请日本二次专家会诊",
    "圣路加国际医院体检怎么预约？国际患者常见流程与资料",
    "两位专家意见不同怎么办？如何利用二次会诊解决真正的分歧",
    "中日精密体检在筛查项目和检查深度上有什么差异",
    "日本精密体检性价比怎么判断？不要只看套餐价格",
    "哪些年龄和风险人群更适合做日本精密体检",
    "心血管精密筛查能看什么？冠心病和心梗风险怎么评估",
    "日本二次专家会诊是什么？和转院、远程问诊有什么区别",
    "日本二次专家会诊怎么申请？从资料整理到专家反馈",
    "日本二次会诊能直接治病吗？第二意见的作用边界",
    "日本体检和国内体检差在哪？重点看报告、复核和后续转诊",
    "日本癌症二次会诊“方案改变率”应该怎么解读",
    "日本胃癌筛查为什么重视胃镜和风险分层",
    "日本精密体检怎么选医院？综合医院、癌症中心与专科机构区别",
    "阿尔茨海默病血液标志物进入临床后，体检筛查应该怎么看",
    "肺结节准备手术前要不要再评估？影像复核和二次会诊思路"
  ],
  "medicines": [
    "OncoSil用于晚期胰腺癌意味着什么？批准状态、适应证与证据怎么核对",
    "虚拟临床试验能替代真实试验吗？83%命中率类研究应该怎么看",
    "日本CAR-T治疗2026有哪些新进展？适应证、多靶点与研究路线",
    "日本抗癌新药获批信息怎么看？批准日期、适应证和治疗线次三步核对",
    "Crisaborole治疗特应性皮炎：批准适应证、证据与使用边界",
    "居家脑刺激治疗抑郁是什么？FDA批准设备与“不用药”并不是一回事",
    "Idvynso用于HIV长期管理意味着什么？适用人群和用药逻辑",
    "Lazertinib在肺癌治疗中处于什么位置？日本获批信息怎么核对",
    "Letermovir用于CMV预防适合哪些人？日本适应证怎么理解",
    "Selumetinib治疗NF1相关丛状神经纤维瘤：日本获批信息怎么看",
    "Vykat XR用于Prader-Willi综合征：改善什么、不能解决什么",
    "Zolgensma治疗SMA：一次性基因治疗的适应证与长期随访",
    "Minodronic Acid米诺膦酸用于骨质疏松：日本用药特点与注意点",
    "日本重症肌无力新药怎么判断价值？机制、适应证和治疗位置",
    "Deucravacitinib治疗银屑病：口服TYK2抑制剂与JAK药有何不同",
    "日本正在探索哪些非CAR-T免疫治疗？TCR、NK等路线怎么区分",
    "日本新药获批不等于适合所有患者：适应证、线次和生物标志物怎么看",
    "日本创新药为什么值得关注？抗癌、罕见病和再生疗法三条主线",
    "日本ADHD治疗有哪些正规路径？药物、适应证与跨境用药边界",
    "三阴性乳腺癌有哪些新药方向？ADC、免疫治疗与精准分型",
    "儿童脑室管膜瘤有CAR-T研究吗？临床研究阶段和可及性",
    "肺癌治疗有哪些前沿方向？靶向、ADC、免疫和细胞治疗怎么区分",
    "Hemlibra艾美赛珠单抗治疗血友病：适合谁、和凝血因子有什么不同",
    "肯尼迪病首款靶向药进展怎么看？罕见病新药最该核对什么",
    "siRNA用于家族性乳糜微粒血综合征：获批意味着什么",
    "SMA药物有哪些？基因治疗、反义寡核苷酸和口服药怎么比较",
    "日本减重药怎么判断是否适合？BMI、合并症和处方条件",
    "同一种药别人有效，为什么你未必适合？生物标志物和个体差异",
    "日本获批新药，海外患者能直接使用吗？处方、接诊与跨境规则",
    "复发性脑室管膜瘤化疗作用有多大？证据与治疗边界"
  ],
  "hospitals": [
    "复发头颈癌想做日本二次会诊，应该找什么类型的专家",
    "庆应义塾大学医院有哪些优势？海外患者选院时该看什么",
    "日本“特定功能病院”是什么？和普通综合医院有什么不同",
    "海外就医怎么选日本医院？大学医院、癌症中心与专科医院区别",
    "ALS疑难诊断在日本该看什么科？神经内科与专病中心怎么选",
    "CT、MRI和病理报告到日本会重新审核吗？为什么原始资料很重要",
    "PET-CT在癌症会诊中有什么价值？日本专家主要看哪些信息",
    "MDT多学科会诊和单个专家看诊有什么区别",
    "远程二次会诊真的可能改变肺癌治疗方案吗？看哪些条件",
    "日本远程会诊和赴日面诊怎么选？哪些情况必须本人到场",
    "日本名医越有名越好吗？选专家最重要的是疾病匹配度",
    "两位日本专家意见不同怎么办？如何处理医学分歧",
    "中国患者能直接预约日本医院吗？转诊、预审和介绍状怎么理解",
    "日本医院排名靠谱吗？海外患者更应该看哪些公开指标",
    "选择日本癌症医院时，应看手术量、专病团队还是研究能力",
    "复发头颈癌二次会诊为什么一定要带原放疗计划",
    "乳腺癌已经有治疗方案，还值得做日本二次会诊吗",
    "乳腺癌赴日会诊，日本专家通常会重新核对哪些信息",
    "东京大学医学部附属医院的优势是什么？学术型医院适合哪些复杂病例",
    "东京大学附属医院国际患者怎么申请？转诊和资料预审怎么准备",
    "大学医院、癌症中心和专科医院怎么选？不要只看名气",
    "罕见免疫疾病为什么容易误诊？日本专科会怎样重新评估",
    "想做免疫治疗，应该怎样选择真正有经验的日本医院",
    "日本国立癌症研究中心适合哪些海外癌症患者关注",
    "为什么很多日本医院要求海外患者先做资料预审再决定是否接诊",
    "日本医院如何分级？特定功能病院、大学医院和专科中心怎么理解",
    "泌尿系结石去日本应该看什么科？哪些检查最常见",
    "国内医生说不能手术，日本外科二次意见还能看什么",
    "癌研有明医院为什么受癌症患者关注？选院前要核对什么",
    "日本专家会诊和国内会诊有什么差异？重点看流程而不是国家标签"
  ],
  "kampo": [
    "日本汉方的优势是什么？质量控制、标准化与临床使用怎么理解",
    "日本汉方为什么形成成熟产业？从中药来源到现代药政体系",
    "日本汉方和中国中成药有什么区别？处方体系、标准与使用场景比较",
    "日本医保汉方主要用于哪些诊疗场景？“可开方”不等于“万能治疗”",
    "日本汉方也做随机对照试验吗？证据质量应该怎么读",
    "桂枝茯苓丸在日本主要用于什么？传统用途与现代研究怎么区分",
    "更年期和中老年常见不适，日本医生为什么会考虑汉方",
    "为什么日本西医也会开汉方？处方逻辑和使用边界",
    "日本汉方为什么能长期进入现代医疗体系？历史与监管逻辑",
    "日本处方级汉方怎么查适应证？别只看“主治疾病速查表”",
    "日本医保汉方和药店OTC汉方有什么区别",
    "日本处方级汉方有哪些？看名录时先分清处方药与OTC",
    "日本医生常开的汉方有哪些？先看适应证和体质判断",
    "日本汉方编号是什么意思？同一方剂不同厂家的差异怎么理解",
    "ADHD可以用日本汉方吗？证据、适应证与儿童用药边界",
    "GLP-1减重药和日本汉方能直接比较吗？作用目标完全不同",
    "津村为什么在日本汉方市场占重要位置？医院用药体系怎么理解",
    "一年反复感冒多次，日本汉方会怎么评估？先排除哪些问题",
    "老年人睡眠浅、多梦、早醒，日本汉方怎么评估是否适合",
    "海外患者为什么关注日本汉方？标准化、处方与可及性怎么判断",
    "肝功能异常能靠汉方调理吗？先看诊断、药物性肝损伤和适应证",
    "补中益气汤能“提升免疫力”吗？研究证据应该怎么理解",
    "吃得不多却容易胖，日本汉方会怎么评估？先排除代谢问题",
    "产后长期恢复不好，日本妇科为什么会考虑汉方",
    "日本汉方如何做质量控制？GAP种植、指纹图谱与成分标准",
    "总是疲劳但检查没大问题，日本汉方能帮到什么程度",
    "偏头痛反复发作，日本头痛门诊会在什么情况下考虑汉方",
    "用汉方减重会不会反弹？体重管理不能只看一味药",
    "化疗后乏力，日本医院为什么有时会联合汉方做支持治疗",
    "去日本买汉方需要处方吗？处方汉方与OTC汉方怎么区分"
  ]
}
INTENTS = {
  "bnct": ["eligibility","definition","comparison","access","safety","cost","combination","evidence","evidence","evidence","access","comparison","workflow","comparison","comparison","comparison","retreatment","research","definition","evidence","safety","verification","scope","workflow","research","limitations","mechanism","workflow","eligibility","biomarker"],
  "ips": ["comparison","mechanism","access","research","evidence","research","verification","access","research","research","research","research","research","comparison","comparison","safety","comparison","safety","access","limitations","cost","definition","history","research","followup","access","evidence","cost","comparison","research"],
  "checkup": ["institution","screening","selection","second_opinion","eligibility","workflow","workflow","screening","cost","second_opinion","followup","followup","followup","screening","eligibility","workflow","second_opinion","comparison","cost","eligibility","screening","definition","workflow","scope","comparison","evidence","screening","institution","screening","second_opinion"],
  "medicines": ["regulatory","evidence","research","regulatory","drug","device","drug","drug","drug","drug","drug","drug","drug","drug","comparison","research","regulatory","research","drug","research","research","research","drug","research","drug","comparison","drug","personalization","access","evidence"],
  "hospitals": ["expert","institution","definition","institution","expert","workflow","diagnostics","mdt","second_opinion","workflow","expert","second_opinion","access","institution","institution","workflow","second_opinion","workflow","institution","access","comparison","expert","institution","institution","access","definition","expert","second_opinion","institution","comparison"],
  "kampo": ["evidence","industry","comparison","scope","evidence","drug","selection","scope","history","verification","comparison","verification","selection","verification","evidence","comparison","industry","selection","selection","access","safety","evidence","selection","selection","quality","selection","selection","weight","supportive","access"]
}
CATEGORY = {
  "bnct": {"name":"BNCT硼中子治疗","kicker":"BNCT · BORON NEUTRON CAPTURE THERAPY","hub_desc":"围绕BNCT原理、适应证、复发头颈癌、既往放疗、疗效证据、副作用、费用、资料准备与研究边界，按单一搜索意图整理30个核心问题。","baseline":"BNCT相关判断必须把日本已批准的临床应用、具体机构接诊条件和研究探索分开。是否适合个人，不能只凭病名或单项检查，需要结合病理、原始影像、既往治疗、关键器官受量和目标机构要求评估。"},
  "ips": {"name":"iPS再生医疗","kicker":"iPS · REGENERATIVE MEDICINE","hub_desc":"围绕iPS细胞原理、帕金森病、眼科、糖尿病、免疫细胞、临床转化、安全性、费用与监管状态，按单一搜索意图整理30个核心问题。","baseline":"iPS与再生医疗必须区分基础研究、临床试验、条件性或正式批准产品以及商业项目。某项技术“已经有人做”不等于已成为常规治疗，更不等于海外患者一定可以申请。"},
  "checkup": {"name":"日本精密体检与二次会诊","kicker":"PRECISION CHECKUP · SECOND OPINION","hub_desc":"围绕日本精密体检、癌症筛查、圣路加国际医院、二次专家会诊、资料准备、费用与异常结果衔接，按单一搜索意图整理30个核心问题。","baseline":"精密体检和二次会诊解决的是不同问题：前者用于风险筛查与健康评估，后者用于既有诊断或治疗方案的再判断。筛查不能替代诊断，第二意见也不等于直接治疗。"},
  "medicines": {"name":"日本新药与疗法","kicker":"JAPANESE MEDICINES · EMERGING THERAPIES","hub_desc":"围绕日本新药、抗癌药、罕见病药物、细胞与基因疗法、跨境可及性和证据解读，按单一搜索意图整理30个核心问题。","baseline":"新药与新疗法首先要核对监管地区、批准日期、具体适应证、疾病亚型、治疗线次和证据阶段。国外获批不等于日本已获批，日本获批也不等于所有患者都适用或可以绕过医生处方与接诊规则。"},
  "hospitals": {"name":"日本医院与专家","kicker":"JAPANESE HOSPITALS · SPECIALISTS","hub_desc":"围绕日本医院分级、大学医院、癌症中心、专家匹配、远程二次会诊、资料预审与国际患者接诊，按单一搜索意图整理30个核心问题。","baseline":"选择日本医院和专家时，核心不是“排名最高”，而是疾病亚型、当前治疗阶段、所需技术、专家专长和医院是否实际接诊相匹配。海外患者还要额外确认转诊、资料预审和国际患者流程。"},
  "kampo": {"name":"日本汉方","kicker":"JAPANESE KAMPO MEDICINE","hub_desc":"围绕日本汉方标准化、医保处方、常见方剂、适应证、质量控制、安全性、OTC与跨境使用，按单一搜索意图整理30个核心问题。","baseline":"日本汉方进入现代医疗体系，并不意味着可以按一个症状自行选方。具体处方仍要结合适应证、体质判断、基础疾病、合并用药和不良反应风险；处方汉方与OTC产品也应分开理解。"}
}
INTENT_GUIDES = {
  "eligibility": {"lead":"这类问题的重点不是先得到一个“能不能”的二元答案，而是确认当前患者是否进入值得进一步评估的范围。病名相同，既往治疗、病灶位置、全身状态和关键检查不同，结论可能完全不同。","checks":["当前诊断和疾病阶段是否已经明确","既往治疗是否改变了后续治疗的可行性或风险","有没有原始影像、病理或关键检查可以支持个体判断","目标机构是否有明确的接诊或筛选条件"],"next":"先把诊断、原始影像、病理、既往治疗时间线和当前最想解决的决策问题整理好，再做针对性的专科评估。"},
  "definition": {"lead":"先把概念本身弄清楚，往往比直接讨论“效果好不好”更重要。需要区分它的作用对象、实施方式、证据阶段和它真正能解决的问题，避免把相邻技术或商业宣传混在一起。","checks":["这个术语的医学定义和核心机制是什么","它和名称相近的技术有哪些本质区别","目前属于常规临床、临床试验还是研究探索","它不能解决哪些问题"],"next":"先建立正确概念，再去看具体适应证、证据和机构要求，能显著减少被标题和营销词带偏。"},
  "comparison": {"lead":"比较两种技术或路径时，不能只问“谁更先进”。真正有意义的是比较治疗目标、适用人群、证据成熟度、风险、可及性以及对当前患者资料的要求。","checks":["两种方案解决的是不是同一个临床问题","适应证和排除条件是否重叠","风险与既往治疗之间是否存在冲突","当前医院是否都具备实际实施条件"],"next":"把两种方案放进同一张比较表，至少列出适应证、证据、风险、资料要求和可及性，再请相应专科医生做个体化判断。"},
  "access": {"lead":"“技术存在”与“现在能不能真正用上”是两件事。需要依次确认监管状态、机构是否开展、是否接收该类患者、是否接受海外患者，以及个人资料是否达到预审要求。","checks":["当前监管状态和适应证写的是什么","哪些机构实际开展或招募","海外患者是否需要转诊或资料预审","是否存在年龄、既往治疗或其他接诊限制"],"next":"优先核对官方监管和医院资料，再准备完整病历做预审，不要只凭媒体报道判断可及性。"},
  "safety": {"lead":"风险不能只看一张“副作用列表”。更重要的是区分常见反应、严重但少见风险、既往治疗叠加风险，以及发生后是否可监测和处理。","checks":["常见短期反应和严重风险分别是什么","既往治疗或基础疾病是否会放大风险","需要监测哪些实验室、影像或临床指标","出现什么情况需要暂停或紧急就医"],"next":"把个人既往治疗、合并症和当前用药带入风险评估，而不是用总体发生率替代个人判断。"},
  "cost": {"lead":"费用问题要拆成项目，而不是只看一个总价。评估费、检查费、治疗或产品费用、住院、随访以及跨境交通住宿的计费方式可能完全不同。","checks":["报价包含哪些医疗项目、不包含哪些项目","是否还需要额外影像、病理复核或实验室检查","治疗后随访和可能的追加治疗是否另计","商业项目和临床研究的费用规则是否不同"],"next":"要求拿到书面费用构成和可能追加项目，再比较不同机构，避免只比较一个宣传总价。"},
  "combination": {"lead":"联合治疗的核心不是简单做“1+1”，而是看两种治疗的作用机制、先后顺序、毒性叠加和已有临床证据。没有成熟证据时，理论上可联合并不等于临床上应联合。","checks":["联合方案有没有同疾病、同阶段的人体证据","治疗先后顺序是否影响安全性或疗效","毒性是否可能叠加","当前机构是否把它作为标准治疗还是研究方案"],"next":"如果考虑联合方案，应让负责整体治疗的医生统一评估时序和风险，避免不同机构各自推进而缺少全局管理。"},
  "evidence": {"lead":"读疗效数据时，最容易出错的是把不同研究类型、不同患者人群和不同终点放在一起比较。ORR、PFS、OS、病例报告和单臂研究回答的问题并不相同。","checks":["研究是病例、回顾性队列、前瞻性试验还是随机研究","纳入的患者疾病阶段和既往治疗是否与自己相近","主要终点是缓解率、无进展生存还是总生存","随访时间和样本量是否足以支持结论"],"next":"把最吸引人的数字放回原始研究的人群和终点中解读，再判断它对当前患者有没有参考价值。"},
  "workflow": {"lead":"这类问题本质上是流程问题。把资料准备、预审、检查、专家判断和后续步骤按顺序拆开，通常比反复询问一个结果更高效。","checks":["第一步需要提交哪些资料","哪些资料必须提供原始文件而不是截图或报告","医院何时决定是否接诊或进入下一步","结果出来后谁负责解释和后续衔接"],"next":"先做一页时间线和一份资料清单，缺什么就补什么，避免在流程中反复来回。"},
  "retreatment": {"lead":"再次治疗不能因为第一次做过、有效过或耐受过，就自动推断第二次也可以。需要重新看病灶变化、累计剂量、器官耐受、间隔时间和全身病情。","checks":["第一次治疗的完整剂量和范围是什么","两次治疗之间间隔多久、病灶位置是否变化","关键器官累计受量是否仍有安全空间","有没有更合适的替代方案"],"next":"准备第一次治疗的完整计划和后续影像，让有再治疗经验的团队重新计算风险，而不是沿用第一次结论。"},
  "research": {"lead":"研究方向值得关注，但必须把“科学上有前景”与“患者现在可获得的治疗”分开。实验室结果、动物研究、早期人体试验和正式临床应用之间存在明显距离。","checks":["目前证据处在哪个研究阶段","有没有正式的人体试验和清晰的入组标准","研究终点主要看安全性还是已经看疗效","是否存在被媒体放大的早期结果"],"next":"关注研究注册、原始论文和机构官方更新；如果考虑参加研究，应先核对入组条件，而不是根据新闻标题做决定。"},
  "verification": {"lead":"面对真假混杂的信息，最有效的方法不是看宣传语，而是核对可验证事实：监管记录、试验注册、医院官方页面、研究论文和收费主体是否一致。","checks":["有没有明确的监管或伦理信息","项目名称能否在官方注册系统中找到","实施机构和负责医生是否真实可核验","是否出现保证疗效、包治或要求绕过正规流程的表述"],"next":"把任何高价或高承诺项目先做一次独立核验，再决定是否提交个人资料或付款。"},
  "scope": {"lead":"关键是明确这项服务或治疗的能力边界。局部治疗、系统治疗、筛查、诊断和第二意见各自解决的问题不同，不能互相替代。","checks":["它解决的是局部问题还是全身性问题","主要目标是筛查、诊断、控制疾病还是帮助决策","哪些情况明确超出它的能力范围","是否仍需要其他专科或系统治疗配合"],"next":"先定义当前最需要解决的临床问题，再选择对应工具，避免让单一技术承担它做不到的任务。"},
  "limitations": {"lead":"理解限制条件和理解优势同样重要。技术效果往往受解剖位置、深度、剂量、制造条件、免疫环境或其他客观约束影响。","checks":["物理或生物学限制是什么","患者个体差异会改变哪些关键参数","有没有明确的排除或不适合条件","是否存在理论可行但临床不可及的情况"],"next":"在咨询时主动问“什么情况下做不了、效果会打折或风险会增加”，通常比只问优势更有价值。"},
  "mechanism": {"lead":"机制问题要回答的是“它为什么可能有效”，而不是直接证明“它对某个人一定有效”。机制可以解释技术逻辑，但临床价值还需要人体研究和适应证来确认。","checks":["关键细胞或物理过程是什么","作用发生在什么时间和空间尺度","机制优势是否已经在人体现实场景得到验证","哪些临床结果不能仅由机制推导"],"next":"先用机制理解技术，再回到人体证据和适应证，避免把漂亮的机制图当成疗效证明。"},
  "biomarker": {"lead":"生物标志物或影像指标通常用于提高筛选和预测精度，但很少能单独决定治疗。检测方法、阈值、重复性和与最终临床结果的相关性都需要核对。","checks":["这个指标测的到底是什么","是否有统一阈值和标准化检测方法","它与治疗反应之间的证据强度如何","结果是否还需要结合影像、病理和临床状态"],"next":"把标志物当作综合评估的一部分，而不是把一个阳性或阴性结果直接等同于能治或不能治。"},
  "followup": {"lead":"异常结果之后真正重要的是“下一步怎么确认”。筛查异常、症状持续或治疗后变化，都需要把复查时间、专科方向和需要排除的高风险情况说清楚。","checks":["异常是否可能由暂时状态或技术因素造成","需要复查同一项目还是增加更针对性的检查","应该转到什么专科","什么症状或变化意味着不能继续等待"],"next":"把异常结果、既往检查和症状时间线带给对应专科，建立明确的复查节点，而不是只重复做同一套体检。"},
  "history": {"lead":"看发展历史的意义不是“越久越可靠”，而是理解关键突破、监管节点和临床转化速度。不同阶段解决的问题不同。","checks":["最初的科学突破是什么","什么时候开始人体研究","哪些节点真正改变了临床可及性","目前仍有哪些关键问题没有解决"],"next":"用时间线判断一项技术已经走到哪一步，比只看“研究了很多年”或“刚刚突破”更可靠。"},
  "institution": {"lead":"选机构要把“医院名气”拆成可验证的能力：专病团队、病例量、技术平台、研究能力、国际患者流程和是否真的接收当前病情。","checks":["医院是否有对应疾病的专病团队","所需技术是否由该院实际开展","国际患者是否需要转诊、预审或中介协调","医院优势是否与当前诊疗目标一致"],"next":"先明确诊疗目标，再用医院官方专科和接诊信息做匹配，避免先选名院再硬套病情。"},
  "screening": {"lead":"筛查的目标是在无症状或高风险人群中尽早发现可能的问题，它不是“把全身所有癌症都查一遍”。检查越多并不一定越好，年龄、家族史和风险分层更重要。","checks":["这个项目针对哪类疾病和风险人群","是否有明确的筛查收益和假阳性风险","发现异常后有没有后续诊断路径","检查频率是否与年龄和个人风险匹配"],"next":"先做个人风险分层，再选择筛查项目；出现异常后应进入专科诊断流程，而不是继续堆叠体检套餐。"},
  "selection": {"lead":"选择套餐、方剂或路径时，不应该从“最贵、最多、最热门”出发，而应先确定目标、风险和真正需要解决的问题。","checks":["当前最主要的目标是什么","哪些项目或选择与个人风险真正相关","有没有重复、低价值或不必要的内容","结果出来后有没有明确的解释和后续路径"],"next":"先列出必须解决的3个问题，再根据问题选择项目或方案，通常比从完整清单倒推更有效率。"},
  "second_opinion": {"lead":"第二意见的价值在于重新核对关键事实和决策，而不是为了得到一个“完全不同”的答案。最常见的价值包括确认原方案、发现缺失信息、调整优先级或提出可比较的替代方案。","checks":["病理、分期和原始影像是否需要复核","目前治疗目标和关键分歧是什么","原方案有没有明确的替代方案值得比较","第二意见出来后谁负责执行和衔接"],"next":"把最想解决的3个决策问题写清楚，并准备原始资料；问题越具体，第二意见越容易产生实际价值。"},
  "regulatory": {"lead":"“获批”必须带着地区、日期、适应证和患者人群一起读。一个国家的批准不能自动外推到另一个国家，同一种药在不同疾病或治疗线次的监管状态也可能不同。","checks":["由哪个监管机构在什么时间批准","批准的具体适应证、年龄和疾病阶段是什么","批准依据来自哪项关键研究","当地是否已经商业供应并进入实际临床使用"],"next":"优先查看监管机构说明书和正式审评文件，再用医院或指南资料理解它在真实诊疗中的位置。"},
  "drug": {"lead":"药物信息不能只看“药名+效果”。需要同时核对适应证、作用机制、关键研究、用药方式、安全性和它在现有治疗序列中的位置。","checks":["批准适应证和目标人群是什么","关键研究比较了什么、主要终点是什么","常见和严重不良反应如何监测","它是替代现有治疗还是只适合特定人群"],"next":"把药物说明书、关键研究和患者当前病情放在一起看，由专业医生判断是否真正匹配。"},
  "device": {"lead":"医疗设备或非药物治疗同样需要看监管状态和证据，不能因为“不用药”就理解为无风险、无禁忌或可以自行使用。","checks":["设备获批的是哪种具体适应证","治疗需要什么专业人员或监测","关键研究的比较组和效果大小如何","有哪些禁忌证、风险或需要停止的情况"],"next":"把它当作正规医疗干预来核对，而不是当作普通消费电子产品。"},
  "personalization": {"lead":"同一种治疗在不同人身上效果不同，并不奇怪。疾病分子特征、器官功能、合并症、既往治疗和药物相互作用都会改变获益与风险。","checks":["有没有可用的生物标志物或分子分型","患者是否符合关键研究的人群特征","合并症和用药会不会改变风险","如果无效，下一步替代方案是什么"],"next":"不要复制别人的处方或治疗经验，先把个人诊断和关键生物学信息补齐，再讨论药物选择。"},
  "expert": {"lead":"找专家最重要的是“对症”，而不是头衔或知名度。疾病亚型、需要解决的技术问题和专家近期主要临床方向必须匹配。","checks":["专家长期主要处理哪类疾病和技术","当前病例的关键问题是否属于其专长","是否需要病理、影像或多学科团队共同参与","医院是否接受当前患者和海外就诊流程"],"next":"先定义病例的关键决策问题，再匹配专家，而不是先找最有名的人再让他回答所有问题。"},
  "diagnostics": {"lead":"影像检查的价值取决于“为什么做、要回答什么”。同一项检查在筛查、分期、疗效评估和复发判断中的意义并不相同。","checks":["这项检查当前要回答的临床问题是什么","是否需要原始影像而不只是报告","有没有更合适或需要互补的检查","结果会不会真正改变下一步决策"],"next":"让接诊医生先明确检查目的，再决定是否需要追加或重新检查，能减少重复和无效检查。"},
  "mdt": {"lead":"多学科会诊的优势不是“医生更多”，而是让不同专科在同一时间围绕一个决策整合信息，尤其适合治疗路径复杂或多方案都可行的病例。","checks":["是否真的有相关专科共同参与","会诊前资料是否完整","最终意见有没有明确主次和执行顺序","如果意见不一致，谁负责整合"],"next":"复杂病例可优先选择有成熟MDT机制的中心，但仍要确认参与科室是否与当前问题相关。"},
  "industry": {"lead":"看一个产业或企业的意义，不是把市场份额当成疗效证明，而是理解标准化生产、供应链、质量控制和医疗体系采用程度。","checks":["行业优势来自研发、生产还是渠道","产品是否有统一质量标准","医院使用和商业销售之间如何区分","市场规模能不能真正说明临床价值"],"next":"把产业信息和临床证据分开读，避免用“卖得多”替代“疗效好”。"},
  "quality": {"lead":"质量控制是汉方和天然来源药物能否进入现代医疗体系的关键环节。原料、种植、鉴别、提取、成分一致性和污染物控制都需要标准化。","checks":["原料来源和基原是否明确","生产过程有没有批次一致性控制","是否使用指纹图谱或关键成分检测","重金属、农残和微生物等风险如何控制"],"next":"选择正规产品时优先看批准类别、厂家和质量标准，不要只看“天然”或产地宣传。"},
  "weight": {"lead":"体重管理不是靠某一种药或方剂单独完成。真正影响反弹的是长期能量平衡、饮食结构、活动、睡眠、基础疾病以及停药后的管理方案。","checks":["当前体重问题是否需要先排除内分泌或药物因素","治疗目标是减重还是改善代谢风险","药物或汉方在整体计划中承担什么角色","停止治疗后如何维持"],"next":"把体重管理做成长期方案，不要用短期体重变化判断某一种产品是否“根治”。"},
  "supportive": {"lead":"支持治疗的目标通常是改善症状、帮助耐受主要治疗或提高生活质量，而不是替代抗肿瘤治疗本身。评价效果时也应使用与目标一致的终点。","checks":["目标症状是什么、严重程度如何","是否已经排除需要紧急处理的原因","与主要治疗有没有相互作用或安全风险","效果用什么指标和时间点判断"],"next":"把支持治疗纳入主治疗团队的整体管理，尤其是化疗、放疗或多药联合期间。"}
}

def esc(s): return html.escape(str(s), quote=True)
def topic_keyword(title): return re.split(r"[？?：:]", title, maxsplit=1)[0].strip()
def category_boundary(folder):
    return {
        "bnct":"涉及具体适应证、疗效数字、再照射风险或机构接诊条件时，应以日本监管文件、接诊医院要求和原始研究为准；不能用专题页替代个体治疗评估。",
        "ips":"涉及iPS或再生医疗时，必须确认是正式批准、临床试验还是研究探索；不得把研究项目、自由诊疗或商业项目自动等同于标准治疗。",
        "checkup":"筛查异常不等于确诊，体检正常也不能排除所有疾病；有持续症状或已知病变时，应进入相应专科诊疗或第二意见流程。",
        "medicines":"处方药、基因治疗、细胞治疗和医疗设备是否适合个人，应由专业医生依据说明书、疾病阶段、既往治疗和当地监管规则判断。",
        "hospitals":"医院或专家的知名度不能替代病例匹配。接诊资格、转诊要求、资料预审和实际可提供的技术应以机构官方信息为准。",
        "kampo":"汉方也可能有禁忌、不良反应和药物相互作用。出现明确疾病、异常化验或持续症状时，不应只靠自我辨证或自行购药。"}[folder]

def faq_for(title,intent):
    g=INTENT_GUIDES[intent]
    q1=f"“{title}”能只凭网上资料直接下结论吗？"
    a1="不能。网页用于帮助理解关键判断点；涉及个人诊断、治疗、用药、筛查异常或接诊资格时，需要由相应专业医生或机构结合个体资料确认。"
    q2_map={"eligibility":"判断是否适合时，最应该先准备什么？","definition":"理解这个概念时，最容易混淆什么？","comparison":"比较两种方案时，最应该避免什么误区？","access":"判断自己能否实际获得这项医疗服务，要核对什么？","safety":"看风险时，为什么不能只看副作用发生率？","cost":"比较费用时，为什么不能只看总价？","combination":"联合治疗为什么不能自己拼方案？","evidence":"看疗效数据时，最重要的第一步是什么？","workflow":"流程类问题，最值得先整理什么？","retreatment":"再次治疗为什么一定要重新评估？","research":"研究有积极结果，为什么不等于现在就能治疗？","verification":"如何快速判断一个医疗项目是否值得继续核实？","scope":"为什么先明确治疗或服务边界很重要？","limitations":"了解一项技术时，为什么要主动问限制条件？","mechanism":"机制听起来很先进，为什么还不能等同于疗效？","biomarker":"一个生物标志物阳性，能直接决定治疗吗？","followup":"出现异常结果后，最重要的下一步是什么？","history":"技术发展多年，能说明已经成熟吗？","institution":"选医院时最重要的是排名吗？","screening":"筛查项目越多越好吗？","selection":"套餐或方案是不是越贵越全面越好？","second_opinion":"第二意见一定会推翻原方案吗？","regulatory":"看到“获批”两个字，第一步应该核对什么？","drug":"看一种新药时，最关键的不是药名而是什么？","device":"非药物治疗是不是就更安全？","personalization":"为什么别人的有效方案不能直接照搬？","expert":"选专家是不是名气越大越好？","diagnostics":"检查做得越多，诊断就越准确吗？","mdt":"MDT是不是参与医生越多越好？","industry":"市场规模大能证明临床疗效好吗？","quality":"天然来源的药物为什么仍需要严格质量控制？","weight":"体重下降后为什么还需要长期管理？","supportive":"支持治疗能替代主要疾病治疗吗？"}
    return [(q1,a1),(q2_map[intent],g["lead"]),("下一步最值得做什么？",g["next"])]

def page(folder,idx,title,intent):
    c=CATEGORY[folder]; g=INTENT_GUIDES[intent]; url=f"{SITE}/{folder}/{idx:03d}/"; keyword=topic_keyword(title)
    desc=f"JapanMedAI {c['name']}专题：{title}。聚焦{keyword}相关的直接答案、判断条件、证据或监管边界及下一步资料准备。内容用于医学信息教育，不替代医生诊断或个体治疗。"
    checks="".join(f"<li>{esc(x)}</li>" for x in g["checks"]); faqs=faq_for(title,intent)
    faq_schema={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    schema={"@context":"https://schema.org","@type":"MedicalWebPage","headline":title,"description":desc,"url":url,"datePublished":"2026-10-15","dateModified":TODAY,"inLanguage":"zh-CN","about":[c["name"],keyword],"publisher":{"@type":"Organization","name":"JapanMedAI｜文腾株式会社","url":SITE+"/"},"isPartOf":{"@type":"CollectionPage","name":c["name"],"url":f"{SITE}/{folder}/"}}
    breadcrumbs={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"JapanMedAI","item":SITE+"/"},{"@type":"ListItem","position":2,"name":c["name"],"item":f"{SITE}/{folder}/"},{"@type":"ListItem","position":3,"name":title,"item":url}]}
    faq_html="".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q,a in faqs)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}｜{esc(c['name'])}｜JapanMedAI</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary"><link rel="stylesheet" href="/assets/jmai.css"><style>.article{{max-width:900px;margin:auto;padding:42px 20px 70px}}.article p,.article li{{line-height:1.85}}.answer{{padding:20px;border:1px solid #d7e6f2;background:#f7fbff;border-radius:14px}}.meta{{font-size:13px;opacity:.7}}.source{{padding:18px;border-left:4px solid #5d7e9c;background:#f7fafc}}.next{{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}}</style><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(breadcrumbs,ensure_ascii=False,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(faq_schema,ensure_ascii=False,separators=(',',':'))}</script></head><body><div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/{folder}/">{esc(c['name'])}</a><a href="/second-opinion/">二次会诊</a><a href="/blog/">医疗知识库</a></nav></div></div><main class="article"><div class="crumb"><a href="/">首页</a> › <a href="/{folder}/">{esc(c['name'])}</a> › 第{idx}篇</div><article><header><span class="kicker">{esc(c['kicker'])}</span><h1>{esc(title)}</h1><p class="meta">JapanMedAI医学信息整理｜资料核对：{TODAY}｜医学专业复核：待必要时进一步确认</p></header><h2>直接回答</h2><div class="answer"><p>{esc(c['baseline'])}</p><p>{esc(g['lead'])}</p></div><h2>这个问题真正要核对什么？</h2><ul>{checks}</ul><h2>适用边界</h2><p>{esc(category_boundary(folder))}</p><h2>对患者最有用的下一步</h2><p>{esc(g['next'])}</p><div class="source"><strong>核对原则：</strong>涉及具体批准状态、疗效数字、适应证、医院接诊要求或药品信息时，优先回到监管机构、医院官方资料、指南、试验注册或原始论文核对；不使用单篇网页替代个体医疗判断。</div><h2>常见问题</h2>{faq_html}<div class="next"><a class="btn" href="/{folder}/">返回{esc(c['name'])}专题</a><a class="btn alt" href="/second-opinion/">进入二次会诊资料准备</a></div></article></main><footer class="footer"><div class="wrap footerInner"><img class="footerLogo" src="/assets/bunto-official-logo.png" alt="BUNTO.CO 文腾株式会社"><div><span class="footerBrand">JapanMed AI · Buntou Medical Japan｜日本文腾医疗</span><br>内容用于医疗信息整理和健康教育，不替代医生诊断、处方或个体治疗决定。</div></div></footer><script src="/assets/jmai-analytics.js"></script></body></html>'''

def hub(folder):
    c=CATEGORY[folder]; links="\n".join(f'<a class="card" href="/{folder}/{i:03d}/"><h3>{esc(t)}</h3></a>' for i,t in enumerate(TITLES[folder],1)); schema={"@context":"https://schema.org","@type":"CollectionPage","name":c["name"],"url":f"{SITE}/{folder}/","description":c["hub_desc"],"dateModified":TODAY,"isPartOf":{"@type":"WebSite","name":"JapanMedAI","url":SITE+"/"}}
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(c['name'])}｜JapanMedAI</title><meta name="description" content="{esc(c['hub_desc'])}"><meta name="robots" content="index,follow"><link rel="canonical" href="{SITE}/{folder}/"><meta property="og:type" content="website"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="{esc(c['name'])}｜JapanMedAI"><meta property="og:description" content="{esc(c['hub_desc'])}"><meta property="og:url" content="{SITE}/{folder}/"><link rel="stylesheet" href="/assets/jmai.css"><style>.hero{{padding:58px 0 28px;background:linear-gradient(180deg,#f7fbff,#fff)}}.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}}.grid a{{text-decoration:none;color:inherit;padding:22px}}.grid h3{{line-height:1.45;margin:8px 0 0}}@media(max-width:850px){{.grid{{grid-template-columns:1fr}}}}</style><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script></head><body><div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/blog/">医疗知识库</a><a href="/second-opinion/">二次会诊</a></nav></div></div><section class="hero"><div class="wrap"><span class="kicker">{esc(c['kicker'])}</span><h1>{esc(c['name'])}</h1><p>{esc(c['hub_desc'])}</p><p class="small">每个页面只解决一个主要问题，减少关键词互相竞争；涉及医疗判断时明确证据、监管与适用边界。</p></div></section><section class="section"><div class="wrap"><div class="grid">{links}</div></div></section><footer class="footer"><div class="wrap footerInner"><img class="footerLogo" src="/assets/bunto-official-logo.png" alt="BUNTO.CO 文腾株式会社"><div><span class="footerBrand">JapanMed AI · Buntou Medical Japan｜日本文腾医疗</span><br>医疗信息用于教育与资料整理，不替代医生诊断和治疗。</div></div></footer><script src="/assets/jmai-analytics.js"></script></body></html>'''

def sitemap(folder):
    rows=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',f'  <url><loc>{SITE}/{folder}/</loc><lastmod>{TODAY}</lastmod></url>']
    rows += [f'  <url><loc>{SITE}/{folder}/{i:03d}/</loc><lastmod>{TODAY}</lastmod></url>' for i in range(1,31)]
    rows.append('</urlset>'); return "\n".join(rows)+"\n"

def main():
    banned=["｜补充篇","改变命运","核爆手术","终极答案"]
    for folder,arr in TITLES.items():
        assert len(arr)==30 and len(set(arr))==30
        assert not any(x in t for t in arr for x in banned)
        for i,a in enumerate(arr):
            for b in arr[i+1:]: assert SequenceMatcher(None,a,b).ratio()<0.80,(folder,a,b)
    for folder in TITLES:
        for i,(title,intent) in enumerate(zip(TITLES[folder],INTENTS[folder]),1):
            p=ROOT/folder/f"{i:03d}"/"index.html"; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(page(folder,i,title,intent),encoding="utf-8")
        (ROOT/folder/"index.html").write_text(hub(folder),encoding="utf-8")
        (ROOT/folder/"sitemap.xml").write_text(sitemap(folder),encoding="utf-8")
    normalized={}
    for folder,arr in TITLES.items():
        for t in arr:
            n=re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+","",t).lower()
            assert n not in normalized,(normalized.get(n),folder,t); normalized[n]=(folder,t)
    for folder in TITLES:
        for i in range(1,31):
            txt=(ROOT/folder/f"{i:03d}"/"index.html").read_text(encoding="utf-8")
            required=[f'{SITE}/{folder}/{i:03d}/','"@type":"MedicalWebPage"','"@type":"FAQPage"','<h2>直接回答</h2>','<h2>适用边界</h2>']
            assert all(x in txt for x in required),(folder,i)
    print("Refined 180 pages: titles deduped, search intents separated, page copy aligned.")

if __name__=="__main__": main()
