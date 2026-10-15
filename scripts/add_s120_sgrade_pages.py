#!/usr/bin/env python3
from __future__ import annotations
import html, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE='https://www.japanmedai.com'
TODAY='2026-10-15'

CFG={
'bnct':{'label':'BNCT硼中子治疗','kicker':'BNCT · BORON NEUTRON CAPTURE THERAPY','sources':[('PMDA','https://www.pmda.go.jp/english/'),('MHLW','https://www.mhlw.go.jp/english/'),('jRCT','https://jrct.niph.go.jp/'),('PubMed','https://pubmed.ncbi.nlm.nih.gov/')],'p0':['/bnct/001/','/bnct/004/','/bnct/010/','/bnct/024/']},
'checkup':{'label':'二次会诊｜精密体检','kicker':'SECOND OPINION · PRECISION CHECKUP','sources':[('National Cancer Center Japan','https://www.ncc.go.jp/en/'),('The University of Tokyo Hospital','https://www.h.u-tokyo.ac.jp/english/'),('MHLW','https://www.mhlw.go.jp/english/'),('PMDA','https://www.pmda.go.jp/english/')],'p0':['/checkup/005/','/checkup/006/','/checkup/023/','/hospitals/013/']},
'hospitals':{'label':'日本医院与专家','kicker':'JAPAN HOSPITALS · SPECIALISTS','sources':[('National Cancer Center Japan','https://www.ncc.go.jp/en/'),('The University of Tokyo Hospital','https://www.h.u-tokyo.ac.jp/english/'),('MHLW','https://www.mhlw.go.jp/english/'),('Japan Medical Services Accreditation for International Patients','https://jmip.jme.or.jp/')],'p0':['/hospitals/013/','/checkup/006/','/checkup/023/','/bnct/024/']},
'ips':{'label':'iPS / 再生医疗','kicker':'iPS · REGENERATIVE MEDICINE','sources':[('PMDA','https://www.pmda.go.jp/english/'),('MHLW Regenerative Medicine','https://www.mhlw.go.jp/english/'),('jRCT','https://jrct.niph.go.jp/'),('CiRA Kyoto University','https://www.cira.kyoto-u.ac.jp/e/')],'p0':['/ips/003/','/ips/007/','/hospitals/013/','/checkup/006/']},
'medicines':{'label':'日本新药与疗法','kicker':'JAPAN MEDICINES · NEW THERAPIES','sources':[('PMDA Approved Products','https://www.pmda.go.jp/english/review-services/reviews/approved-information/0004.html'),('PMDA','https://www.pmda.go.jp/english/'),('MHLW','https://www.mhlw.go.jp/english/'),('jRCT','https://jrct.niph.go.jp/')],'p0':['/medicines/004/','/medicines/017/','/medicines/029/','/checkup/006/']},
'kampo':{'label':'日本汉方','kicker':'JAPANESE KAMPO','sources':[('MHLW','https://www.mhlw.go.jp/english/'),('PMDA','https://www.pmda.go.jp/english/'),('Japan Society for Oriental Medicine','https://www.jsom.or.jp/medical/ebm/'),('KEGG MEDICUS','https://www.kegg.jp/medicus-bin/search_drug')],'p0':['/kampo/010/','/kampo/011/','/medicines/004/','/hospitals/013/']},
}

# Two logical batches, one final production upload.
BATCH_A={
'bnct':[
('BNCT治疗前为什么必须看原始DICOM，而不是只看影像报告？','影像报告能总结所见，但BNCT评估还要看病灶真实位置、体积、与关键器官的空间关系以及既往照射区域。原始DICOM通常比截图或报告更适合做机构级预评估。','资料准备'),
('既往放疗计划找不到了，还能申请日本BNCT评估吗？','可以先评估，但资料缺失会降低判断精度。尤其既往高剂量放疗患者，原始放疗计划、剂量分布和关键器官累计受量常直接影响能否安全再次做局部照射。','资料准备'),
('BNCT前为什么要重新确认病理，而不是只看原来的诊断名称？','因为同一“头颈癌”标签下的病理类型、生物学行为和既往治疗可能不同。机构通常需要确认病理诊断与当前病灶是否一致，避免仅凭病名判断适用性。','适应性判断'),
('肿瘤离颈动脉很近，BNCT评估时最担心什么？','关键不是“离血管近”这一句话，而是肿瘤与大血管、皮肤、黏膜、神经等高风险结构的具体关系，以及既往治疗后的组织耐受性。需要由治疗机构做影像和剂量层面的评估。','风险判断'),
('BNCT前是否一定要做BPA-PET？什么时候更有参考价值？','BPA-PET可用于研究或部分机构的硼摄取评估，但并非所有BNCT流程都把它作为统一强制项目。是否需要应以接诊机构方案和当前证据为准。','检查判断'),
('头颈癌复发同时有远处转移，BNCT还有没有意义？','BNCT属于局部治疗，远处转移存在时必须同时考虑全身病情和系统治疗。局部症状控制可能仍有讨论价值，但不能把BNCT理解为控制全身转移的治疗。','治疗边界'),
('BNCT后多久能判断是否有效？为什么不能太早下结论？','局部反应需要结合影像、症状与随访时间判断。治疗后早期炎症、水肿或组织改变可能干扰影像，因此评估时间点应由接诊团队确定。','疗效判断'),
('BNCT后影像看起来变大，是进展还是治疗反应？','单次影像变大不能自动等同肿瘤进展。应结合检查时间、强化方式、症状变化和后续影像趋势判断，并排除治疗相关炎症或坏死。','随访判断'),
('高龄患者能不能做BNCT？年龄是不是主要门槛？','年龄本身通常不是唯一判断条件。更重要的是体能状态、合并症、病灶位置、既往治疗和能否承受治疗流程，最终由机构综合评估。','适应性判断'),
('BNCT后还能再做手术或其他放疗吗？','不能用固定顺序回答。后续是否还能手术、粒子治疗或其他局部治疗，需要重新看病灶范围、组织恢复、累计剂量和新的治疗目标。','治疗排序'),
('BNCT申请被一家医院拒绝，是否值得再找第二家评估？','不同机构设备、研究项目和接诊边界可能不同，但重复评估应建立在完整资料和明确原因上。若拒绝原因是病灶位置、全身状态或安全性限制，换医院不一定改变结论。','机构选择'),
('BNCT治疗前为什么要特别核对既往免疫治疗和靶向治疗？','既往系统治疗会影响病情阶段、当前治疗目标和不良反应判断，也可能影响BNCT与后续治疗的时序安排，因此应完整提供用药名称、时间和疗效。','资料准备'),
('复发口腔癌做BNCT前，为什么要评估皮肤和黏膜受量？','口腔和头颈部病灶附近常有皮肤、黏膜、唾液腺等敏感组织。治疗计划需要平衡肿瘤剂量与正常组织风险，不能只看肿瘤能否照到。','风险判断'),
('BNCT治疗是不是次数越多效果越好？','不是。BNCT是否单次、重复或不再重复，取决于既往剂量、正常组织耐受、病灶反应和研究证据，不能把次数当成疗效指标。','治疗边界'),
('BNCT治疗后疼痛减轻，能不能说明肿瘤已经缩小？','症状改善是重要临床信息，但不能替代影像和医生评估。疼痛变化可能受到炎症、止痛药和局部反应等多种因素影响。','疗效判断'),
('BNCT评估时为什么要问最后一次放疗是什么时候？','放疗时间会影响组织恢复、晚期损伤风险和再照射判断。除了总剂量，还要看分割方式、照射范围和距离上次治疗的时间。','风险判断'),
('脑肿瘤患者看到BNCT研究结果，怎么判断自己是否同一类患者？','要核对病理类型、分子分型、初发或复发、既往手术和放疗、研究入组标准与主要终点。仅凭“脑肿瘤”三个字不能直接套用研究结果。','证据解读'),
('BNCT的“选择性杀伤”是不是等于完全不伤正常组织？','不是。选择性来自硼药摄取差异和粒子作用范围，但正常组织仍可能摄取硼并受到中子场影响，因此治疗计划和器官剂量限制依然关键。','机制边界'),
('BNCT费用咨询为什么必须先做资料评估？','费用与是否进入正式治疗流程、需要哪些检查、住院安排和机构政策有关。在尚未确认可评估或可接诊前，单一价格通常不能代表最终费用。','费用判断'),
('准备BNCT二次意见时，最值得先问专家哪5个问题？','优先问：是否属于当前可评估范围、既往放疗是否构成主要限制、还缺哪些关键资料、预期治疗目标是什么、若不适合BNCT还有哪些下一步选择。','决策准备'),
],
'checkup':[
('日本二次会诊前，为什么要先把问题压缩到3到5个？','专家第二意见的价值在于解决关键决策点。把问题聚焦到诊断是否明确、现方案是否合理、是否还有替代选项和下一步资料缺口，通常比罗列几十个问题更有效。','问题准备'),
('只有中文病历，没有英文或日文翻译，能不能先申请日本二次会诊？','很多机构会要求日文或指定格式资料。可以先整理中文原始资料，但正式送审前应按接诊机构要求翻译，避免自行删减医学信息。','资料准备'),
('日本二次会诊一定需要本人到场吗？','不一定。部分第二意见可基于资料进行远程或书面评估，另一些医院要求本人到场。是否需要赴日取决于医院政策和问题性质。','流程判断'),
('病理切片和病理报告有什么区别？二次会诊时都要准备吗？','病理报告是文字结论，切片或数字病理可供重新阅片。是否必须提交切片取决于专家是否需要病理复核，但两者价值不同，不能互相替代。','资料准备'),
('癌症二次会诊为什么要提供完整治疗时间线？','时间线能帮助专家快速理解诊断、手术、放疗、化疗、靶向或免疫治疗的先后顺序及反应，避免从零散报告中重新拼接病程。','资料准备'),
('二次会诊前需要把所有检查都重新做一遍吗？','通常不应为了会诊盲目重复检查。先让专家看现有资料，确认真正缺失的关键项目，再决定是否需要补检查更合理。','检查判断'),
('肿瘤标志物正常，是否还有必要做二次会诊？','肿瘤标志物正常不能单独排除肿瘤进展或治疗问题。是否需要第二意见应看诊断复杂度、治疗选择和当前决策困难，而不是只看单项指标。','适用性判断'),
('已经在国内大医院看过专家，还需要日本二次会诊吗？','二次会诊不是因为原医生“不够好”，而是在重大决策、疑难病理、复发或治疗选择有限时增加一个独立视角。也可能最终确认原方案。','适用性判断'),
('二次会诊结果和原医院意见一样，还有价值吗？','有。独立确认可以降低重大治疗决策的不确定性，也可能明确目前不需要换方案，避免无效折腾或追逐尚不适用的新疗法。','价值判断'),
('日本二次会诊最适合在治疗前还是治疗后做？','最有价值的时间通常是存在真实决策点时，例如首次治疗方案选择、复发、疗效不佳、病理不确定或准备重大局部治疗前，而不是固定某个阶段。','时机判断'),
('只有CT或MRI截图，没有原始DICOM，会影响二次会诊吗？','会影响影像复核质量。截图无法完整浏览层面、序列和参数，尤其需要判断病灶范围或既往治疗影响时，原始DICOM更有价值。','资料准备'),
('二次会诊前为什么要把“已经做过什么治疗”写得很具体？','同一药物或放疗如果剂量、周期、疗效和停药原因不同，对后续选择影响很大。只写“做过化疗”通常不够支持专家判断。','资料准备'),
('精密体检是不是项目越多越好？','不是。筛查价值取决于年龄、家族史、症状、既往疾病和证据。无指征的大量检查可能增加假阳性、重复检查和不必要焦虑。','体检判断'),
('日本体检发现异常后，能否直接转入医院治疗？','取决于体检机构和医院合作模式。体检报告不等于完成诊断，异常项目通常还需要进一步专科检查或转诊。','流程判断'),
('有家族肿瘤史，去日本体检最该先补充什么信息？','应先整理亲属关系、癌种、确诊年龄、本人既往筛查与遗传检测情况，再由医生判断是否需要更有针对性的筛查或遗传咨询。','风险评估'),
('PET-CT适合作为所有人的常规体检项目吗？','不适合简单理解为“越高级越该做”。PET-CT有特定临床用途，也涉及辐射和假阳性问题，是否用于筛查应结合个人风险与专业建议。','体检判断'),
('日本精密体检前为什么要核对既往影像？','既往影像可帮助判断某个结节或异常是新出现、稳定还是变化，减少把长期稳定病灶误当成新问题。','资料准备'),
('二次会诊报告拿到后，下一步应该怎么用？','应把专家意见带回当前治疗团队，结合本人状态、当地可实施性和新的检查结果共同决策。第二意见本身不是处方，也不能自动替代主治团队。','结果使用'),
('二次会诊时可以直接问“我还能活多久”吗？','可以提出预后问题，但专家通常只能基于疾病阶段、治疗反应和群体数据给范围性判断，无法给出精确个人寿命预测。','预后边界'),
('日本二次会诊前，哪些资料最值得优先整理成一页摘要？','建议用一页写清诊断、病理、分期、关键分子检测、既往治疗及疗效、当前问题和3到5个核心提问，方便专家快速进入决策重点。','资料准备'),
],
'hospitals':[
('日本医院国际部和临床科室有什么区别？','国际部通常负责语言、预约、资料流转和费用流程，真正的诊疗判断仍由临床科室医生完成。联系国际部不等于已经获得接诊或治疗资格。','流程判断'),
('海外患者申请日本大学医院，为什么经常先要介绍状？','大型医院强调分级诊疗和专科筛选，介绍状可帮助确认转诊目的、既往诊疗和需要解决的问题。海外患者是否必须提供，以医院官方政策为准。','流程判断'),
('日本医院说“先资料预审”，是不是已经同意接诊？','不是。资料预审只是判断是否值得进入下一步，正式接诊还可能取决于专科意见、床位、治疗适应性、签证和付款流程。','接诊边界'),
('如何判断一家日本医院是否真正有国际患者接诊能力？','应看官方国际患者页面、语言与协调流程、是否接受海外资料预审、付款和医疗签证支持，而不是只看医院名气。','机构选择'),
('日本医院有某项先进技术，就一定会接海外患者吗？','不一定。技术存在、医保适应证、研究项目和海外接诊是不同问题，必须分别核对。','接诊边界'),
('日本医院预约为什么常要求先明确“就诊目的”？','因为体检、第二意见、确诊后治疗、临床试验咨询对应不同科室和流程。目的不清会增加转错科或被退回的概率。','流程判断'),
('海外患者去日本医院前为什么要确认支付方式？','国际患者可能涉及预付款、保证金、第三方协调或不同计费流程。提前确认可避免到院后因支付问题影响安排。','费用判断'),
('日本医院能不能接受微信里发来的病历照片？','正式医疗判断通常需要清晰、完整且可追溯的资料。聊天软件照片可用于初步沟通，但不能替代医院要求的正式影像、报告和翻译文件。','资料准备'),
('为什么日本医院会拒绝“只想找最有名教授看一下”的请求？','医院通常按疾病、科室和医疗需求分配专家，不以单纯名气作为预约依据。明确诊断和决策问题更有利于匹配合适专家。','专家匹配'),
('日本医院的“第二意见门诊”和“正式治疗门诊”有什么区别？','第二意见主要基于既有资料提供独立建议，通常不直接开始治疗；正式治疗门诊则需要重新建档、检查并由医院承担后续诊疗。','流程判断'),
('想去日本做手术，为什么医院还会要求重新检查？','医院需要对当前病情、麻醉风险和手术适应性负责。即使海外已有检查，也可能因时间、质量或项目要求重新完成部分检查。','接诊流程'),
('日本医院说“目前没有适合的临床试验”，是否等于没有治疗选择？','不等于。临床试验只是治疗路径之一，还应由专科医生结合已批准治疗、支持治疗和其他局部或系统方案评估。','治疗边界'),
('日本医院名单越多越好吗？如何缩小到2到3家？','应按疾病专长、具体技术、海外接诊政策和当前问题筛选，而不是按名气无限罗列。2到3家匹配机构通常更利于高质量预审。','机构选择'),
('如何核对日本医院官网上的医生是否仍在该院出诊？','以医院最新科室页、医生介绍和门诊安排为准。旧媒体报道或第三方医生名录可能已经过期。','信息核对'),
('日本癌症中心和大学医院怎么选？','没有统一优劣。癌症专科中心在肿瘤多学科和病例量上有优势，大学医院则可能在复杂合并症、研究和多学科资源上更广，需按具体问题匹配。','机构选择'),
('海外患者能否直接申请日本临床试验？','部分试验可能接受符合条件的海外患者，但入组标准、语言、居住和随访要求差异很大，应以jRCT/机构研究团队和正式入组流程为准。','研究申请'),
('日本医院为什么要求近期影像，而不是半年前的检查？','治疗决策需要反映当前病情。对于进展较快或正在治疗中的疾病，过旧影像可能不能代表现状，因此医院常要求近期资料。','资料准备'),
('国际患者协调机构可以替代医院做医学判断吗？','不能。协调机构可帮助预约、翻译和资料流转，但疾病诊断、治疗适应性和风险必须由医院医生判断。','角色边界'),
('日本医院接诊前要视频问诊，主要是在确认什么？','可能用于确认病史、沟通目标、语言支持和是否值得安排下一步，但视频问诊内容和法律边界取决于医院政策。','流程判断'),
('第一次联系日本医院时，最应该写清楚哪5项信息？','建议写清诊断、当前阶段、既往治疗、希望解决的问题、可提供的核心资料，并附联系方式和语言需求。','资料准备'),
],
}

BATCH_B={
'ips':[
('iPS治疗“获批”到底意味着什么？和临床试验有什么区别？','获批意味着特定产品在特定适应证和条件下通过监管审查；临床试验仍在验证安全性或有效性。两者不能混为“都能治疗”。','监管判断'),
('看到iPS研究进入I期或II期，患者现在能申请治疗吗？','进入临床试验不等于面向所有患者开放治疗。是否能申请取决于试验是否正在招募、入排标准、研究机构和随访要求。','研究申请'),
('iPS细胞治疗和普通干细胞治疗有什么本质区别？','iPS细胞来自重编程后的多能干细胞，可进一步分化为目标细胞；临床产品的制造、质量控制和监管路径与泛称“干细胞治疗”并不相同。','概念判断'),
('iPS帕金森治疗获批后，是不是所有帕金森患者都适合？','不是。监管批准会限定适应人群和使用条件，具体患者还要看疾病阶段、既往药物反应、手术风险和接诊机构标准。','适应性判断'),
('iPS心肌细胞片和细胞注射是一回事吗？','不是。细胞类型、递送方式、制造产品和临床证据可能完全不同。判断进展时应核对具体产品名称和研究方案。','概念判断'),
('iPS视网膜治疗已经能常规预约了吗？','不同眼病和不同iPS产品的证据阶段不同，不能用“iPS眼科”概括为已常规开放。应核对具体疾病、产品和当前研究或批准状态。','可及性判断'),
('海外患者想申请日本iPS临床试验，第一步查什么？','先查jRCT或机构官网确认试验状态、招募机构和入排标准，再决定是否值得准备病历资料联系研究团队。','研究申请'),
('iPS治疗为什么特别强调长期随访？','细胞产品可能涉及移植细胞存活、免疫反应、肿瘤风险和长期功能变化，因此监管和研究通常要求较长期的安全性观察。','风险判断'),
('iPS治疗需要免疫抑制吗？','取决于产品是否自体或异体、细胞类型和临床方案。不能用单一答案覆盖所有iPS治疗，应以具体产品方案为准。','治疗条件'),
('“自体iPS”是不是一定比“异体iPS”更安全？','不能这样推断。自体和异体方案在制造时间、成本、免疫风险和质量控制上各有取舍，安全性需看具体产品与临床数据。','证据解读'),
('iPS再生医疗的费用为什么差异很大？','费用取决于是否为批准产品、临床试验或自费医疗，以及制造、住院、手术和随访要求。研究项目与商业自费项目也不能混为一谈。','费用判断'),
('日本再生医疗广告说“iPS相关”，怎么判断是不是正规的iPS治疗？','应核对具体细胞来源、产品名称、监管类别、实施计划和临床证据。仅使用“iPS相关”宣传语不足以证明属于获批iPS产品。','合规判断'),
('iPS治疗失败后还能再治疗吗？','没有统一答案。是否可重复取决于产品机制、既往反应、安全性、试验方案和当前病情，不能自行推断。','治疗边界'),
('iPS临床试验中的“主要终点”为什么比新闻标题更重要？','主要终点决定研究真正验证什么，是安全性、症状改善还是功能恢复。只看新闻中的“患者改善”容易忽略研究设计和样本量。','证据解读'),
('iPS治疗出现“首例”“世界首个”新闻，患者最该核对什么？','先核对是研究启动、首例移植、阶段性结果还是监管获批，再看样本量和随访时间。新闻里“首个”不等于疗效已经确立。','证据解读'),
('iPS再生医疗和基因治疗是一回事吗？','不是。iPS主要涉及细胞重编程和分化，基因治疗则通过遗传物质或基因编辑实现治疗目标，两者可能结合但监管与风险不同。','概念判断'),
('日本iPS研究很多，为什么真正获批产品仍然很少？','从基础研究到获批要经历制造标准、非临床验证、分期临床试验和监管审查，细胞产品还涉及长期安全性，因此转化周期通常较长。','研发判断'),
('iPS治疗前为什么还要做常规标准治疗评估？','创新治疗通常不能脱离现有标准治疗背景。很多试验或批准条件会要求既往标准治疗效果不充分或符合特定阶段。','适应性判断'),
('iPS治疗的“细胞来源”为什么是患者必须问的问题？','细胞来源会影响免疫匹配、制造方式、质量控制和风险管理。患者应知道使用的具体细胞类型与产品，而不是只听“再生医疗”。','风险判断'),
('准备iPS第二意见时，最值得带哪些资料？','应准备明确诊断、疾病阶段、既往治疗、近期影像或功能评估、当前用药和希望确认的具体iPS产品或试验名称。','资料准备'),
],
'medicines':[
('日本新药“获批”后，为什么还要看最新添付文书？','批准新闻只能说明某次监管决定，最新添付文书才更具体地列出适应证、用法、警示和重要注意事项，后续也可能更新。','监管判断'),
('同一种抗癌药在日本和中国适应证不同，应该看哪一个？','患者在哪个国家实际接受治疗，就应以当地批准适应证和临床规范为基础；跨境比较可以参考，但不能直接套用另一国标签。','适应证判断'),
('日本药品已经上市，海外患者就一定能合法个人进口吗？','不一定。日本处方资格、出口流程和目的国个人进口规则是不同层面，必须分别核对。','合规判断'),
('新药新闻写“显著延长生存”，患者该先看哪3个数字？','应先看研究人群、主要终点和绝对效果大小，并结合随访时间和不良反应。单看相对风险下降容易高估实际收益。','证据解读'),
('日本新药的“最适使用推进指南”有什么用？','部分高成本或复杂药物会配套最适使用推进指南，对适用患者、医疗机构和使用条件做进一步说明，不能只看药品名称。','监管判断'),
('同一成分有多个商品名，怎么确认是不是同一种药？','应核对通用名、剂型、规格、给药途径和批准持有人。商品名不同不一定代表成分不同，也可能存在不同适应证或规格。','药品核对'),
('抗癌药换了一个新适应证，旧文章还能继续参考吗？','旧文章可能已过时。适应证、联合方案和治疗线次会更新，患者应优先查最新PMDA文件和当前指南。','信息更新'),
('日本儿童用药为什么不能直接按成人剂量缩小？','儿童药代动力学、体重和年龄阶段不同，且部分药物缺少儿童临床数据。是否可用及剂量必须依据正式儿科资料和医生判断。','用药边界'),
('日本药品说明书里写“慎重投与”或重要注意事项，患者怎么理解？','这些信息提示特定风险或需要额外监测，不等于绝对禁用。应由医生结合患者合并症、实验室指标和替代方案判断。','风险判断'),
('靶向药一定要有对应基因突变才能用吗？','很多靶向药确实依赖特定生物标志物，但具体要求因药物和适应证不同。必须核对当前批准标签和检测方法。','适应证判断'),
('免疫治疗PD-L1高就一定效果好吗？','不是。PD-L1只是部分癌种和药物中的一个生物标志物，疗效还受癌种、治疗线次、分子特征和整体状态影响。','证据边界'),
('日本孤儿药获批意味着疗效证据更弱吗？','不能简单这样说。罕见病试验常面临样本量限制，但仍需达到监管要求；应具体看研究设计、终点和批准条件。','证据解读'),
('新药进入“优先审评”是不是等于已经批准？','不是。优先审评只是监管流程加速机制之一，最终是否获批仍需完成正式审查。','监管判断'),
('日本临床试验用药能不能自己购买？','通常不能。试验药由研究方案和研究机构管理，获得途径受临床试验规定约束，不能按普通商品购买。','研究边界'),
('抗癌药发生严重副作用后，再挑战用药要看什么？','应看副作用类型、严重程度、恢复情况、药品说明书和是否有替代治疗。再挑战必须由治疗团队决定。','风险判断'),
('冷链药品跨境运输最容易出什么问题？','温度超限、运输时长、包装验证和海关延误都可能影响质量。是否还能使用不能凭肉眼判断，应依据产品储存要求和专业意见。','药品管理'),
('处方药在日本药局能直接买到吗？','大多数处方药需要日本医生处方。是否可调剂还取决于处方有效性、库存和药局规定，不能把“日本有售”理解为自由购买。','购药边界'),
('日本药品出现缺货，能不能随便换成同成分其他品牌？','同成分替换仍要核对剂型、规格、适应证、给药装置和医生处方要求，尤其生物制剂或特殊剂型不能自行替换。','用药安全'),
('药品说明书里没有写某个疾病，医生还能用吗？','是否存在超说明书使用要看当地法规、证据和医生责任，但患者不能据此自行使用。跨境信息平台更不能把研究用途写成已批准适应证。','合规边界'),
('判断一个“日本特效药”宣传是否靠谱，最少查哪4项？','至少核对通用名、PMDA批准状态、正式适应证、是否需要处方；若涉及癌症还应核对治疗线次和生物标志物。','信息核对'),
],
'kampo':[
('日本处方汉方和药妆店汉方，最大的区别是什么？','处方汉方属于医疗体系中的处方药，需医生根据适应证和患者情况开具；OTC汉方则按非处方药规则销售，产品规格和适应证可能不同。','药品分类'),
('同名汉方方剂，不同厂家成分一定一样吗？','不能只看方名。应核对生药组成、提取比例、每日用量和制剂规格，不同产品并非所有细节都相同。','药品核对'),
('日本汉方可以长期吃吗？','不能一概而论。长期使用需要看方剂、基础病、肝肾功能和潜在不良反应，尤其甘草等成分重复时更需要监测。','用药安全'),
('多个汉方一起吃，为什么要特别注意甘草重复？','多方并用可能叠加甘草摄入，增加假性醛固酮增多症等风险。是否合并使用应由医生或药师核对全部方剂组成。','用药安全'),
('汉方“对证”是不是等于不用看现代医学诊断？','不是。日本医疗中的汉方也建立在现代医学诊断和风险排查基础上，尤其出现报警症状时不能只靠体质判断。','诊疗边界'),
('日本汉方和中药汤剂是一回事吗？','不是完全相同。日本医疗用汉方多为标准化提取制剂，处方名称、原料标准、剂量和监管方式与个体化中药汤剂不同。','概念判断'),
('汉方颗粒写了某个适应证，是不是所有同症状的人都适合？','不是。说明书适应证提供使用范围，但具体患者还需考虑年龄、合并症、其他药物和症状原因。','适应性判断'),
('汉方吃了以后血压升高，要不要怀疑药物因素？','需要考虑，尤其含甘草方剂可能与低钾、血压升高和水肿相关。应停止自行加量并及时咨询医生或药师。','风险判断'),
('日本汉方为什么也会有肝损伤风险？','天然来源不等于没有不良反应。部分汉方存在药物性肝损伤报告，出现乏力、黄疸、尿色加深等情况应及时就医。','风险判断'),
('小柴胡汤是不是感冒或肝病都能长期吃？','不能这样使用。小柴胡汤有明确适应范围和重要安全注意事项，既往也有严重不良反应警示，应由医生判断。','用药边界'),
('防风通圣散是不是所有减肥人群都适合？','不是。其适应证和体质条件有限，也可能出现不良反应。不能把汉方减重宣传等同于普适性减肥药。','适应性判断'),
('葛根汤感冒初期什么时候更常被考虑？','葛根汤在日本有特定适应证，但发热、感染严重程度和基础病仍需判断。出现呼吸困难、高热不退等情况应优先就医。','适应性判断'),
('六君子汤适合所有胃口不好的人吗？','不适合一概而论。食欲差可能来自消化道、代谢、药物或肿瘤等原因，六君子汤是否适合需先明确基础问题。','适应性判断'),
('大建中汤在日本医院里主要怎么用？','大建中汤在日本临床常用于特定腹部症状和术后相关场景，但具体适应证、证据与患者状态需由医生判断。','临床使用'),
('芍药甘草汤腿抽筋时可以天天吃吗？','不建议自行长期频繁使用。该方含甘草，重复或长期使用时需关注低钾、血压和水肿等风险。','用药安全'),
('牛车肾气丸用于麻木或夜尿时要注意什么？','症状背后可能有糖尿病、神经病变、前列腺或泌尿系统疾病，应先排查原因；方剂本身也需结合合并症和其他用药。','适应性判断'),
('补中益气汤“补气”是不是身体虚就能吃？','“身体虚”不是足够的用药依据。应结合具体症状、基础病和现代医学检查，避免掩盖贫血、感染或其他器质性问题。','用药边界'),
('抑肝散用于老年人烦躁时，为什么要先排除其他原因？','谵妄、感染、疼痛、药物副作用和电解质异常都可能引起行为变化，不能把所有烦躁直接归为需要汉方。','诊疗边界'),
('日本汉方能和西药一起吃吗？','很多患者会合并使用，但必须核对成分重复、相互作用、肝肾功能和电解质风险，尤其多药并用的老年患者。','联合用药'),
('怎么看一篇“日本汉方神方”文章是否可信？','先查方剂是否为正规药品、正式适应证和安全警示，再看文章是否区分传统使用、临床研究和监管批准；绝对化疗效宣传应谨慎。','信息核对'),
],
}

def esc(x): return html.escape(x, quote=True)

def page(cat,idx,q,a,intent):
    c=CFG[cat]; url=f'{SITE}/{cat}/{idx:03d}/'; src=c['sources'][:3]
    checks={
      '资料准备':['原始报告和影像是否完整','既往治疗时间、剂量或用药是否清楚','当前最需要专家回答的问题是否明确'],
      '风险判断':['当前风险来自疾病还是治疗本身','既往治疗是否增加正常组织风险','是否有需要优先处理的急症或并发症'],
      '证据解读':['研究人群是否与自己相近','主要终点和随访时间是什么','研究阶段是否等于已批准临床应用'],
      '监管判断':['是否为正式监管批准','批准适应证和使用条件是什么','是否有后续指南或说明书更新'],
    }.get(intent,['这个问题的事实层面是什么','哪些条件会改变结论','下一步最需要核对什么资料'])
    faq1=a+' 具体到个人仍需结合完整资料由接诊医生或专业人员判断。'
    schema={'@context':'https://schema.org','@type':'MedicalWebPage','headline':q,'description':a,'url':url,'datePublished':TODAY,'dateModified':TODAY,'inLanguage':'zh-CN','about':[c['label'],q],'publisher':{'@type':'Organization','name':'JapanMedAI｜文腾株式会社','url':SITE+'/'},'isPartOf':{'@type':'CollectionPage','name':c['label'],'url':f'{SITE}/{cat}/'},'citation':[u for _,u in src],'abstract':faq1}
    faq={'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':faq1}},{'@type':'Question','name':'这个问题最需要核对哪几项信息？','acceptedAnswer':{'@type':'Answer','text':'；'.join(checks)+'。'}},{'@type':'Question','name':'下一步最值得做什么？','acceptedAnswer':{'@type':'Answer','text':'先把与本题直接相关的原始资料整理完整，再对照官方来源或接诊机构要求核对，不要仅凭病名、新闻标题或单个数字做个人治疗判断。'}}]}
    breadcrumb={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'JapanMedAI','item':SITE+'/'},{'@type':'ListItem','position':2,'name':c['label'],'item':f'{SITE}/{cat}/'},{'@type':'ListItem','position':3,'name':q,'item':url}]}
    related=''.join(f'<a href="{u}">优先决策参考 →</a>' for u in c['p0'][:4])
    sources=''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{esc(n)}</a></li>' for n,u in src)
    lis=''.join(f'<li>{esc(x)}</li>' for x in checks)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(q)}｜JapanMedAI</title><meta name="description" content="{esc(a)}"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="{esc(q)}｜JapanMedAI"><meta property="og:description" content="{esc(a)}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{esc(q)}｜JapanMedAI"><meta name="twitter:description" content="{esc(a)}"><link rel="stylesheet" href="/assets/jmai.css"><style>.article{{max-width:900px;margin:auto;padding:42px 20px 70px}}.article p,.article li{{line-height:1.85}}.answer{{padding:20px;border:1px solid #d7e6f2;background:#f7fbff;border-radius:14px}}.meta{{font-size:13px;opacity:.7}}.evidencePanel,.decisionPath{{margin:30px 0;padding:22px;border:1px solid #d7e6f2;border-radius:16px;background:#fbfdff}}.relatedGrid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}.relatedGrid a{{display:block;padding:14px 16px;border:1px solid #dbe7f2;border-radius:12px;text-decoration:none;color:inherit}}@media(max-width:700px){{.relatedGrid{{grid-template-columns:1fr}}}}</style><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(breadcrumb,ensure_ascii=False,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(faq,ensure_ascii=False,separators=(',',':'))}</script></head><body><div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/{cat}/">{esc(c['label'])}</a><a href="/second-opinion/">二次会诊</a><a href="/blog/">医疗知识库</a></nav></div></div><main class="article"><div class="crumb"><a href="/">首页</a> › <a href="/{cat}/">{esc(c['label'])}</a> › 第{idx}篇</div><article><header><span class="kicker">{esc(c['kicker'])}</span><h1>{esc(q)}</h1><p class="meta">JapanMedAI医学信息整理｜资料核对：{TODAY}｜医学专业复核：待必要时进一步确认</p><div><strong>本页搜索意图：</strong>{esc(intent)}｜<strong>只解决：</strong>{esc(q)}</div></header><h2>直接回答</h2><div class="answer"><p>{esc(a)}</p><p>判断边界：本页用于医学信息教育与决策准备，不替代医生诊断、处方、入组或接诊判断。</p></div><h2>这个问题真正要核对什么？</h2><ul>{lis}</ul><h2>适用边界</h2><p>涉及具体适应证、治疗风险、药品使用、医院接诊或研究入组时，应回到监管文件、接诊医院要求和原始研究核对；不能用专题页替代个体医疗判断。</p><h2>对患者最有用的下一步</h2><p>先把与本题直接相关的原始资料整理完整，再对照官方来源或接诊机构要求核对，不要仅凭病名、新闻标题或单个数字做个人治疗判断。</p><section class="evidencePanel"><h2>权威证据与官方核对</h2><p class="meta"><strong>证据核对日期：</strong>{TODAY}</p><ul>{sources}</ul><p>这些来源用于确认监管状态、机构规则或研究证据；个人是否适合仍需由相应专业团队判断。</p></section><h2>常见问题</h2><h3>{esc(q)}</h3><p>{esc(faq1)}</p><h3>这个问题最需要核对哪几项信息？</h3><p>{esc('；'.join(checks))}。</p><h3>下一步最值得做什么？</h3><p>先整理原始资料，再回到官方来源和接诊机构要求核对。</p><section class="decisionPath"><h2>下一步决策路径</h2><div class="relatedGrid">{related}</div></section></article></main><footer class="footer"><div class="wrap"><span class="footerBrand">JapanMedAI · 文腾株式会社</span><br>内容用于医学信息教育与跨境医疗决策准备，不替代执业医疗团队诊疗。</div></footer><script src="/assets/jmai-analytics.js"></script></body></html>'''

def add_to_hub(cat,topics):
    p=ROOT/cat/'index.html'; t=p.read_text(encoding='utf-8')
    cards='\n'.join(f'<a class="card" href="/{cat}/{i:03d}/" data-jmai-track="hub" data-jmai-id="hub_{cat}_{i:03d}" data-jmai-position="hub"><h3>{esc(q)}</h3></a>' for i,(q,_,_) in topics)
    # append before end of first grid
    m=re.search(r'(<div class="grid">)(.*?)(</div></div></section>)',t,re.S)
    if not m: raise RuntimeError(f'grid missing {cat}')
    t=t[:m.start(2)]+m.group(2)+'\n'+cards+t[m.end(2):]
    sm=re.search(r'<script id="jmai-itemlist" type="application/ld\+json">(.*?)</script>',t,re.S)
    if sm:
        d=json.loads(sm.group(1)); arr=d.get('itemListElement',[])
        pos=len(arr)
        for i,(q,_,_) in topics:
            pos+=1; arr.append({'@type':'ListItem','position':pos,'url':f'{SITE}/{cat}/{i:03d}/','name':q})
        d['numberOfItems']=len(arr); d['itemListElement']=arr
        t=t[:sm.start(1)]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+t[sm.end(1):]
    p.write_text(t,encoding='utf-8')

def update_sitemap(all_topics):
    p=ROOT/'sitemap.xml'; t=p.read_text(encoding='utf-8')
    additions=[]
    for cat,topics in all_topics.items():
        for i,_ in topics:
            url=f'{SITE}/{cat}/{i:03d}/'
            if url not in t: additions.append(f'  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url>')
    t=t.replace('</urlset>','\n'.join(additions)+'\n</urlset>')
    p.write_text(t,encoding='utf-8')

def build(batch):
    indexed={}
    for cat,items in batch.items():
        topics=[]
        for off,(q,a,intent) in enumerate(items,start=31):
            path=ROOT/cat/f'{off:03d}'/'index.html'; path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(page(cat,off,q,a,intent),encoding='utf-8')
            topics.append((off,(q,a,intent)))
        indexed[cat]=topics
    return indexed

def qa(all_topics):
    titles=[]; count=0
    for cat,topics in all_topics.items():
        assert len(topics)==20
        for i,(q,_,_) in topics:
            p=ROOT/cat/f'{i:03d}'/'index.html'; assert p.exists(); s=p.read_text(encoding='utf-8')
            assert f'<link rel="canonical" href="{SITE}/{cat}/{i:03d}/">' in s
            assert 'MedicalWebPage' in s and 'FAQPage' in s and '权威证据与官方核对' in s
            assert '<meta name="robots" content="index,follow' in s
            titles.append(q); count+=1
    assert count==120 and len(set(titles))==120
    sm=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
    for cat,topics in all_topics.items():
        for i,_ in topics: assert f'{SITE}/{cat}/{i:03d}/' in sm
    print('QA OK:',count,'new S-grade pages in two logical batches')

def main():
    a=build(BATCH_A); b=build(BATCH_B); all_topics={**a,**b}
    for cat,topics in all_topics.items(): add_to_hub(cat,topics)
    update_sitemap(all_topics)
    reg=['batch\tcategory\tid\ttitle\tintent']
    for name,batch in [('A',BATCH_A),('B',BATCH_B)]:
        for cat,items in batch.items():
            for off,(q,_,intent) in enumerate(items,start=31): reg.append(f'{name}\t{cat}\t{off:03d}\t{q}\t{intent}')
    (ROOT/'docs').mkdir(exist_ok=True); (ROOT/'docs/s120-sgrade-registry.tsv').write_text('\n'.join(reg)+'\n',encoding='utf-8')
    qa(all_topics)

if __name__=='__main__': main()
