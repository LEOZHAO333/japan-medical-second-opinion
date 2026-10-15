#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.japanmedai.com"
TODAY = "2026-10-15"

PUBLIC_ROOTS = {"blog", "pet", "en", "zh-hant", "weight", "medicines", "second-opinion", "videos"}
SKIP_ROOTS = {"wordpress", "blogger", "tests", ".github", "docs"}
PET_BRAND_ARTICLE = "blog/2026-10-03-japan-pet-medicine-guide-richongtong.html"

SOURCE_LINKS = {
    "merck": ("Merck Veterinary Manual", "https://www.merckvetmanual.com/"),
    "iris": ("International Renal Interest Society (IRIS)", "https://www.iris-kidney.com/"),
    "cornell": ("Cornell Feline Health Center", "https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center"),
    "wsava": ("World Small Animal Veterinary Association (WSAVA)", "https://wsava.org/"),
    "acvim": ("American College of Veterinary Internal Medicine (ACVIM)", "https://www.acvim.org/"),
}

PET_TOPICS = [
    {
        "slug": "cat-litter-change-not-using-box",
        "category": "猫泌尿",
        "title": "日本精准兽医｜猫换猫砂后不上厕所怎么办？观察与就医指南",
        "summary": "换猫砂后突然不上厕所，常见原因包括对气味、颗粒或猫砂盆变化不适应，但也必须先排除排尿困难。最重要的不是立刻再换一种猫砂，而是确认猫到底有没有正常排尿。",
        "points": [
            "查看24小时内是否出现正常大小的尿团，而不是只看猫有没有进入猫砂盆。",
            "新旧猫砂可短期渐进混合，猫砂盆位置、清洁频率和数量尽量保持稳定。",
            "记录频繁进出猫砂盆、蹲很久、叫声增加、舔尿道口或只尿几滴等变化。",
        ],
        "urgent": "如果反复蹲厕却几乎没有尿、精神明显变差、呕吐、腹部紧张或疼痛，应尽快联系动物医院。尤其公猫发生尿道阻塞时可能迅速恶化。",
        "records": "带上最近尿团变化、饮水、食欲、猫砂更换时间、既往泌尿病史和正在使用的药物。能拍到排尿姿势的视频，也有助于兽医判断。",
        "sources": ["merck", "cornell"],
    },
    {
        "slug": "multi-cat-litter-box-monitoring",
        "category": "猫泌尿",
        "title": "日本精准兽医｜多猫家庭猫砂盆怎么摆？排尿监测指南",
        "summary": "多猫家庭最大的难点，不只是猫砂盆够不够，而是主人能不能及时发现“哪只猫开始尿少、尿频或完全没尿”。猫砂盆布局要兼顾资源分散和个体观察。",
        "points": [
            "猫砂盆不要全部堆在同一个角落，尽量分散到不同安静区域，减少被另一只猫堵住入口。",
            "每天固定时间观察尿团数量和大小；必要时短时分区饲养，确认异常来自哪只猫。",
            "避免一次同时更换猫砂、猫砂盆和摆放位置，否则很难判断行为变化的原因。",
        ],
        "urgent": "如果某只猫频繁进出猫砂盆、用力却没有明显尿液、持续舔生殖部位或出现精神沉郁，应优先排查泌尿急症。",
        "records": "就诊前记录每只猫的年龄、性别、绝育情况、近期饮水和尿团变化，并说明家中猫砂盆数量、位置及最近是否发生搬家或新增宠物。",
        "sources": ["merck", "cornell"],
    },
    {
        "slug": "cat-urinary-stoma-home-care",
        "category": "猫泌尿",
        "title": "日本精准兽医｜猫尿道造口术后怎么清洁？家庭护理指南",
        "summary": "尿道造口术后的重点不是把伤口“洗得越干净越好”，而是按照手术医院要求保持局部清洁、减少舔咬，并持续确认排尿是否通畅。",
        "points": [
            "严格按出院说明处理伤口，不自行使用酒精、双氧水、药膏或人用消毒产品。",
            "每天观察尿流、尿色、肿胀、渗液、异味和猫是否持续舔咬手术部位。",
            "猫砂材质、伊丽莎白圈和活动限制应以手术团队给出的术后方案为准。",
        ],
        "urgent": "出现完全排不出尿、持续大量出血、伤口裂开、明显肿胀、发热、持续呕吐或精神迅速变差，应立即联系手术医院或急诊。",
        "records": "复诊时准备手术日期、术式、出院用药、每日排尿情况和伤口照片的时间序列，不要只带当天一张照片。",
        "sources": ["merck", "acvim"],
    },
    {
        "slug": "female-cat-urinary-retention",
        "category": "猫泌尿",
        "title": "日本精准兽医｜母猫也会尿潴留吗？排尿异常判断指南",
        "summary": "母猫发生完全尿道阻塞的概率通常低于公猫，但“母猫就不会尿闭”是错误判断。膀胱炎、结石、神经问题、疼痛或其他原因都可能造成排尿困难。",
        "points": [
            "区分尿频和真正无尿：频繁去猫砂盆但每次仍有少量尿，与完全没有尿液意义不同。",
            "观察是否伴随血尿、叫痛、躲藏、食欲下降、呕吐或腹部不适。",
            "不要只凭性别排除风险，也不要靠按压腹部判断膀胱是否充盈。",
        ],
        "urgent": "如果长时间没有确认到尿液、反复用力却排不出、精神差或呕吐，应尽快就医检查膀胱、尿路和肾功能。",
        "records": "准备近24小时猫砂盆记录、尿液颜色、饮水、食欲、既往结石或膀胱炎病史，以及任何可能影响排尿的药物信息。",
        "sources": ["merck", "cornell"],
    },
    {
        "slug": "cat-moving-house-urination-plan",
        "category": "猫泌尿",
        "title": "日本精准兽医｜搬家前后怎么减少猫排尿异常？准备指南",
        "summary": "搬家会同时改变气味、空间、猫砂盆位置和家庭节奏。对有膀胱炎或应激性排尿问题的猫，提前把生活变化拆小，比搬家当天临时处理更重要。",
        "points": [
            "搬家前尽量保留原来的猫砂、猫砂盆和常用垫子，不要在同一周同时换粮、换砂和换盆。",
            "新家先设置一个安静、资源完整的小区域，让猫熟悉后再逐步扩大活动范围。",
            "每天记录尿团、饮水、食欲和躲藏程度，尤其关注既往有泌尿问题的猫。",
        ],
        "urgent": "搬家后如果出现频繁蹲厕、几乎没有尿、血尿、持续呕吐或明显精神差，不要把所有异常都解释为“紧张”，应及时就医。",
        "records": "如需就医，说明搬家日期、环境变化、猫砂与饮食是否改变、最后一次正常排尿时间和既往尿路疾病记录。",
        "sources": ["cornell", "merck"],
    },
    {
        "slug": "recurrent-cat-urinary-second-opinion-records",
        "category": "猫泌尿",
        "title": "日本精准兽医｜猫泌尿问题反复发作，二诊要准备什么资料？",
        "summary": "反复尿频、血尿或排尿困难时，二诊最有价值的不是重新描述“又犯了”，而是把每次发作、检查、治疗和恢复过程放在一条时间线上。",
        "points": [
            "整理历次尿检、尿培养、影像、结石分析和血液检查原件，注明检查日期。",
            "把每次用药名称、疗程、症状改善时间和停药后是否复发写清楚。",
            "记录饮食、饮水、猫砂、体重和应激事件的变化，帮助区分可能的诱因。",
        ],
        "urgent": "如果当前已经出现排不出尿、持续呕吐或明显虚弱，应先处理急症，而不是等待完整二诊资料。",
        "records": "建议准备一页时间线和三个核心问题，例如“是否需要培养”“影像是否需要复查”“目前最需要排除什么原因”。",
        "sources": ["merck", "cornell"],
    },
    {
        "slug": "dog-house-soiling-or-urinary-problem",
        "category": "犬泌尿",
        "title": "日本精准兽医｜狗突然在家乱尿，是行为问题还是泌尿问题？判断指南",
        "summary": "原本定点排尿的狗突然在家乱尿，不应直接归结为“报复”或训练退步。尿频、膀胱刺激、疼痛、激素变化、饮水增加和认知变化都可能造成相似表现。",
        "points": [
            "先看每次尿量：少量多次、明显尿急和正常大量排尿，提示方向不同。",
            "记录饮水量、夜间是否更频繁、有没有血尿、异味、舔生殖部位或排尿疼痛。",
            "同时回顾最近是否更换环境、作息、家庭成员或遛狗频率。",
        ],
        "urgent": "如果持续用力却排不出尿、腹部疼痛、精神差或呕吐，应尽快就医；不要只做行为训练。",
        "records": "就诊前记录3—7天排尿时间、地点、尿量趋势、饮水和正在使用的药物，能明显提高问诊效率。",
        "sources": ["merck", "wsava"],
    },
    {
        "slug": "dog-hematuria-urine-sample",
        "category": "犬泌尿",
        "title": "日本精准兽医｜狗尿血时怎么留尿样？取样与送检指南",
        "summary": "狗出现血尿时，尿样能提供重要线索，但家庭接到的自然排尿样本容易被皮肤、毛发和环境污染。是否适合做培养，还要看取样方式。",
        "points": [
            "使用干净容器接取中段尿，尽量避免接触地面、尿垫或猫砂等吸附材料。",
            "记录取样时间，并尽快按医院要求送检；不要自行长时间室温保存。",
            "如果兽医怀疑感染并计划尿培养，可能会建议在医院采用更无菌的取样方式。",
        ],
        "urgent": "如果血尿伴随排尿困难、血块、明显疼痛、虚弱或完全排不出尿，应优先就医，不要为了“留到好尿样”拖延。",
        "records": "带上尿样同时记录血尿从何时开始、是否每次都有、尿量、频率和近期抗菌药或止痛药使用情况。",
        "sources": ["merck", "acvim"],
    },
    {
        "slug": "dog-straining-to-urinate",
        "category": "犬泌尿",
        "title": "日本精准兽医｜狗抬腿却尿不出来怎么办？排尿困难急症指南",
        "summary": "反复摆出排尿姿势却没有正常尿流，属于需要认真对待的症状。原因可能来自尿道阻塞、结石、前列腺问题、膀胱疾病或神经系统异常。",
        "points": [
            "确认最后一次正常排尿的时间和大致尿量，不要只看地面是否有几滴尿。",
            "注意是否同时出现腹部不适、焦躁、频繁舔生殖部位、血尿、呕吐或精神变差。",
            "不要自行按压膀胱，也不要凭以前的旧药尝试“通尿”。",
        ],
        "urgent": "如果持续用力却几乎没有尿，或数小时内越来越不舒服，应尽快联系动物医院。完全阻塞可能危及生命。",
        "records": "就医时说明犬的性别、绝育情况、既往结石/前列腺病史、最后排尿时间和正在使用的药物。",
        "sources": ["merck", "acvim"],
    },
    {
        "slug": "dog-sleep-urine-leakage",
        "category": "犬泌尿",
        "title": "日本精准兽医｜狗睡觉时漏尿怎么办？尿失禁观察指南",
        "summary": "睡着后垫子变湿、起身时滴尿，与主动蹲下排尿不是一回事。真正的尿失禁需要区分尿路感染、括约肌问题、神经疾病、尿量增加等原因。",
        "points": [
            "观察是在熟睡时持续渗漏，还是醒来后因来不及外出而排尿。",
            "记录漏尿量、发生频率、尿色、气味，以及是否伴随饮水明显增加。",
            "留意后肢无力、尾部感觉变化或腰背疼痛等神经相关表现。",
        ],
        "urgent": "如果突然出现明显尿失禁并伴后肢无力、疼痛、血尿或排尿困难，应尽快就医。",
        "records": "准备一周的漏尿时间、睡眠位置、饮水和排尿记录，并列出绝育时间、慢性病和长期用药。",
        "sources": ["merck", "acvim"],
    },
    {
        "slug": "dog-post-neuter-incontinence",
        "category": "犬泌尿",
        "title": "日本精准兽医｜狗绝育后开始漏尿怎么办？复诊指南",
        "summary": "绝育后出现漏尿并不代表一定由手术直接造成，也不能只凭时间先后下结论。兽医通常需要先确认是否是真正尿失禁，并排除感染、结石、尿量增加等问题。",
        "points": [
            "记录漏尿从术后多久开始，是否主要在睡眠或放松时发生。",
            "观察有无尿频、疼痛、血尿、饮水增多或阴部皮肤刺激。",
            "不要自行使用人用激素、止尿药或旧处方。",
        ],
        "urgent": "若漏尿同时伴完全排不出尿、明显疼痛、发热或精神下降，应及时就医。",
        "records": "带上手术日期、术后恢复记录、既往尿检和目前所有用药，方便兽医判断是否需要尿检、影像或其他检查。",
        "sources": ["merck", "acvim"],
    },
    {
        "slug": "senior-dog-urgency",
        "category": "犬泌尿",
        "title": "日本精准兽医｜老狗突然憋不住尿怎么办？高龄犬管理指南",
        "summary": "高龄犬尿急、夜间频繁排尿或突然憋不住，既可能与衰老和认知变化有关，也可能来自肾病、糖尿病、尿路感染、内分泌疾病或药物影响。",
        "points": [
            "先区分“尿量真的变多”还是“每次尿量小但次数增加”。",
            "记录饮水、食欲、体重、夜间醒来次数及是否出现迷路、徘徊等认知变化。",
            "回顾利尿剂、激素类药物或其他长期用药，因为部分药物会增加饮水与排尿。",
        ],
        "urgent": "如出现排尿困难、血尿、明显虚弱、呕吐或突然神经症状，应尽快就医。",
        "records": "建议带3—7天饮水和排尿记录、近期血液/尿液检查、慢性病清单和完整用药表。",
        "sources": ["merck", "wsava"],
    },
    {
        "slug": "cat-creatinine-single-high",
        "category": "猫肾病",
        "title": "日本精准兽医｜猫肌酐一次偏高就是肾病吗？复查指南",
        "summary": "一次肌酐升高不能单独确诊慢性肾病。脱水、肌肉量、近期状态以及实验室差异都会影响结果，判断慢性肾病需要结合重复检测、尿检和其他指标。",
        "points": [
            "查看猫当时是否脱水、食欲差、呕吐或刚经历急性疾病。",
            "同时关注尿比重、SDMA、尿蛋白、血压和影像等信息，而不是只盯一个数值。",
            "比较同一家实验室的趋势往往比单次跨实验室结果更有意义。",
        ],
        "urgent": "如果肌酐升高同时伴持续呕吐、明显脱水、几乎不进食、无尿或精神差，应尽快就医评估急性肾损伤等问题。",
        "records": "复诊时带上历次肾功能、尿检、体重、血压和用药记录，并注明采血时是否脱水或正在输液。",
        "sources": ["iris", "merck"],
    },
    {
        "slug": "cat-ckd-staging",
        "category": "猫肾病",
        "title": "日本精准兽医｜猫慢性肾病怎么分期？IRIS分期理解指南",
        "summary": "猫慢性肾病分期不是只看一次肌酐。IRIS分期强调在病情相对稳定、充分评估水合状态后，结合肾功能指标，并进一步看蛋白尿和血压进行亚分期。",
        "points": [
            "先确认是慢性问题而不是暂时脱水或急性肾损伤。",
            "肌酐、SDMA等应结合趋势理解，单个数值不能脱离临床状态。",
            "尿蛋白和血压会影响风险管理，因此常需要单独评估。",
        ],
        "urgent": "若猫出现持续呕吐、明显脱水、食欲骤降、无尿或精神状态快速恶化，应先处理当前问题，而不是只讨论分期。",
        "records": "建议把至少两次肾功能、尿检、血压、体重和影像资料按日期排列，方便兽医判断趋势。",
        "sources": ["iris", "merck"],
    },
    {
        "slug": "cat-renal-diet-refusal",
        "category": "猫肾病",
        "title": "日本精准兽医｜猫肾病处方粮不吃怎么办？饮食调整指南",
        "summary": "肾病猫完全不吃，比“没有吃到最理想的处方粮”更需要优先处理。应先确认拒食原因，再与兽医讨论过渡方式，而不是用强迫进食长期硬撑。",
        "points": [
            "先排查恶心、口腔疼痛、便秘、脱水或药物副作用等导致食欲下降的因素。",
            "换粮应逐渐进行，温度、质地、餐次和进食环境都可能影响接受度。",
            "记录实际摄入量和体重趋势，避免只凭“看起来吃了一点”判断。",
        ],
        "urgent": "若猫明显减少进食超过一天、持续呕吐、脱水或精神差，应尽快联系兽医，尤其是已有慢性肾病时。",
        "records": "带上当前和曾尝试过的食物、每日实际摄入量、体重变化、呕吐/便秘情况和用药表。",
        "sources": ["iris", "wsava"],
    },
    {
        "slug": "cat-ckd-weight-loss",
        "category": "猫肾病",
        "title": "日本精准兽医｜猫肾病越来越瘦怎么办？消瘦复诊指南",
        "summary": "慢性肾病猫持续消瘦不应简单归结为“肾病晚期”。摄入不足、恶心、肌肉流失、甲状腺疾病、肠胃问题或其他合并症都可能参与。",
        "points": [
            "每周固定条件称重，并观察背部、腰部和后肢肌肉量，而不只看体重数字。",
            "记录每天吃多少、是否挑食、呕吐、便秘和活动量变化。",
            "复诊时同时评估肾功能趋势、血压、贫血、血磷及其他可能导致消瘦的问题。",
        ],
        "urgent": "若短期快速消瘦、完全拒食、持续呕吐或明显虚弱，应尽快就医。",
        "records": "准备至少4周体重曲线、食物摄入记录、近期血液和尿液检查、当前用药及补液情况。",
        "sources": ["iris", "merck"],
    },
    {
        "slug": "cat-daily-subcutaneous-fluids",
        "category": "猫肾病",
        "title": "日本精准兽医｜猫肾病需要每天皮下补液吗？补液管理指南",
        "summary": "不是所有肾病猫都需要每天皮下补液，频率和剂量应依据脱水程度、饮水摄入、肾功能、心脏状况和整体状态由兽医决定。",
        "points": [
            "补液目标是纠正或预防脱水，不是把某个肾功能数字“冲下来”。",
            "每天记录精神、饮水、食欲、体重、呼吸和补液后吸收情况。",
            "有心脏病、胸腔积液史或呼吸问题的猫，补液方案需要更谨慎。",
        ],
        "urgent": "补液后出现持续呼吸加快、呼吸费力、极度虚弱、咳嗽或无法平卧，应停止自行追加并尽快联系兽医。",
        "records": "带上每天补液量与频率、体重、静息呼吸频率、近期肾功能和心脏相关检查记录。",
        "sources": ["iris", "merck"],
    },
    {
        "slug": "cat-home-subcutaneous-fluid-training",
        "category": "猫肾病",
        "title": "日本精准兽医｜第一次在家给猫皮下补液，要学会什么？操作培训指南",
        "summary": "家庭皮下补液应先由动物医院确认适应情况、液体种类、单次量和频率，并进行现场培训。网上视频不能替代针对具体猫的操作指导。",
        "points": [
            "学会确认液体、管路、针头、有效期和无菌操作基本要求。",
            "明确推荐穿刺区域、如何判断针头位置、什么时候必须停止。",
            "记录每次补液时间、实际量、猫的反应和补液包吸收时间。",
        ],
        "urgent": "若补液过程中猫突然呼吸异常、剧烈挣扎、明显疼痛、出血不止，或补液后状态变差，应停止并联系兽医。",
        "records": "请让医院把液体名称、单次量、频率、复查时间和异常情况处理方式写成可保存的清单。",
        "sources": ["iris", "merck"],
    },
    {
        "slug": "cat-subcutaneous-fluid-lump",
        "category": "猫肾病",
        "title": "日本精准兽医｜猫皮下补液后鼓包正常吗？观察指南",
        "summary": "皮下补液后出现柔软的局部鼓包通常是液体暂时停留在皮下，之后会逐渐吸收并可能受重力向下移动。但大小、吸收时间和猫的整体状态仍需观察。",
        "points": [
            "记录鼓包出现的位置、大小和大约多久变小，不要频繁揉压。",
            "观察局部是否发红、发热、明显疼痛或持续渗液。",
            "同时看猫的呼吸、精神和食欲，不能只盯着皮下包本身。",
        ],
        "urgent": "若鼓包长时间不消退并伴明显疼痛、皮肤异常，或猫出现呼吸加快、乏力等全身变化，应联系兽医。",
        "records": "带上补液量、液体名称、补液位置、吸收时间和连续照片，方便判断是否需要调整操作。",
        "sources": ["merck", "iris"],
    },
    {
        "slug": "cat-fast-breathing-after-fluids",
        "category": "猫肾病",
        "title": "日本精准兽医｜猫补液后呼吸变快怎么办？风险判断指南",
        "summary": "补液后呼吸明显变快不能只理解为紧张。尤其有心脏病、胸腔疾病或高龄基础病的猫，需要警惕液体负荷和其他急性问题。",
        "points": [
            "在猫熟睡或安静时数静息呼吸频率，并与平时基线比较。",
            "观察是否出现张口呼吸、腹式用力、无法舒适躺下、咳嗽或明显烦躁。",
            "记录本次补液量、速度和补液前后的体重与精神状态。",
        ],
        "urgent": "出现张口呼吸、明显呼吸费力、舌色异常、突然极度虚弱，应立即就医。不要继续补液等待观察。",
        "records": "准备既往心脏检查、肾功能、最近补液方案和呼吸频率记录，并说明症状与补液的时间关系。",
        "sources": ["merck", "acvim"],
    },
    {
        "slug": "dog-kidney-values-and-urinalysis",
        "category": "犬肾病",
        "title": "日本精准兽医｜狗肾功能升高为什么还要看尿检？检查指南",
        "summary": "血液中的肌酐、尿素氮或SDMA异常只能说明需要进一步判断，尿比重、尿蛋白、尿沉渣等能帮助兽医理解肾脏浓缩能力和是否存在尿路问题。",
        "points": [
            "血检和尿检最好结合采样时的水合状态、饮食和用药一起解释。",
            "尿比重可帮助判断肾脏浓缩能力，但单次结果也要结合临床背景。",
            "蛋白尿、感染或血尿可能改变后续检查和随访重点。",
        ],
        "urgent": "如伴持续呕吐、脱水、无尿、明显少尿或精神迅速变差，应尽快就医评估急性肾损伤。",
        "records": "带上历次血检、尿检、血压、影像和用药记录，最好按日期排列而不是只带最新一张。",
        "sources": ["iris", "merck"],
    },
    {
        "slug": "dog-renal-diet-refusal",
        "category": "犬肾病",
        "title": "日本精准兽医｜狗肾病处方粮不吃怎么办？进食管理指南",
        "summary": "肾病犬拒绝处方粮时，第一步不是无限换品牌，而是确认有没有恶心、口腔问题、脱水、便秘或其他影响食欲的原因。",
        "points": [
            "记录每日实际吃多少以及是否只拒绝某种质地或气味。",
            "过渡换粮应循序渐进，并与兽医确认是否需要兼顾血磷、蛋白摄入和体况。",
            "持续称重，关注肌肉流失和体况变化。",
        ],
        "urgent": "若明显减少进食、持续呕吐、脱水或精神差，应尽快就医，不要单纯在家继续尝试换粮。",
        "records": "准备一周饮食、体重、呕吐和排便记录，以及最近肾功能、尿检和用药清单。",
        "sources": ["iris", "wsava"],
    },
    {
        "slug": "dog-aki-follow-up",
        "category": "犬肾病",
        "title": "日本精准兽医｜狗急性肾损伤出院后怎么复查？随访指南",
        "summary": "急性肾损伤出院不等于肾脏已经完全恢复。复查重点通常包括肾功能趋势、水合状态、尿量、血压和尿检，并根据病因决定是否继续追踪。",
        "points": [
            "严格按出院计划复查，不因精神恢复就自行推迟。",
            "在家观察饮水、食欲、呕吐、尿量和体重变化。",
            "不要自行恢复曾可能影响肾脏的药物或保健品，应先与兽医核对。",
        ],
        "urgent": "再次出现明显少尿/无尿、持续呕吐、快速脱水或精神恶化时，应提前复诊。",
        "records": "带上住院期间关键化验、出院肾功能、尿量记录、所有用药和可能接触毒物/药物的时间线。",
        "sources": ["iris", "merck"],
    },
    {
        "slug": "dog-proteinuria-monitoring",
        "category": "犬肾病",
        "title": "日本精准兽医｜狗尿蛋白升高要追踪什么？蛋白尿管理指南",
        "summary": "尿蛋白升高需要先确认是否持续存在，并区分尿路炎症、出血等因素。兽医通常会结合尿蛋白/肌酐比、血压和肾功能趋势判断意义。",
        "points": [
            "单次试纸阳性不等于已经确诊肾小球疾病。",
            "复查时尽量在相近条件下取样，并结合尿沉渣判断是否有炎症或出血。",
            "血压和肾功能趋势常与蛋白尿风险评估一起考虑。",
        ],
        "urgent": "若同时出现水肿、明显虚弱、食欲骤降、呕吐或尿量显著改变，应及时就医。",
        "records": "整理历次尿检、UPC、血压、肌酐/SDMA、白蛋白和用药记录，方便观察是否真正持续或进展。",
        "sources": ["iris", "acvim"],
    },
    {
        "slug": "dog-liver-enzymes-long-term-meds",
        "category": "犬肝胆",
        "title": "日本精准兽医｜狗长期用药后肝酶升高，需要自行停药吗？用药复核指南",
        "summary": "长期用药后发现肝酶升高，不建议主人自行停药。肝酶变化可能与药物、原发疾病、内分泌问题或其他肝胆疾病有关，需要结合具体药物和趋势判断。",
        "points": [
            "先确认是哪一项肝酶升高、升高幅度和是否持续，而不是笼统说“肝功能不好”。",
            "把所有处方药、非处方药、保健品和零食补充剂一起列出来。",
            "不要突然停用需要逐渐减量或维持控制原发病的药物。",
        ],
        "urgent": "若出现黄疸、反复呕吐、明显嗜睡、腹胀、黑便或神经症状，应尽快就医。",
        "records": "带上开始用药前后的肝酶趋势、用药剂量和时间、其他化验及影像结果，让兽医评估是否需要调整或进一步检查。",
        "sources": ["merck", "acvim"],
    },
    {
        "slug": "dog-jaundice",
        "category": "犬肝胆",
        "title": "日本精准兽医｜狗眼白和牙龈发黄怎么办？黄疸就医指南",
        "summary": "黄疸代表胆红素升高，可能来自红细胞破坏、肝细胞疾病或胆道阻塞等不同方向。仅凭“发黄”无法判断病因，通常需要尽快检查。",
        "points": [
            "在自然光下观察眼白、牙龈和耳廓是否真正发黄，并记录开始时间。",
            "同时注意尿色变深、粪便颜色变化、食欲、呕吐、腹痛和精神状态。",
            "不要把黄疸当作单纯“上火”或自行使用人用护肝药。",
        ],
        "urgent": "新出现的明显黄疸、持续呕吐、腹痛、极度虚弱或意识异常都应尽快就医。",
        "records": "准备近期用药、可能接触毒物、旅行/感染史、既往肝胆疾病和最新血液检查，方便快速缩小原因范围。",
        "sources": ["merck", "acvim"],
    },
    {
        "slug": "dog-liver-nodule",
        "category": "犬肝胆",
        "title": "日本精准兽医｜狗体检发现肝脏结节怎么办？进一步评估指南",
        "summary": "超声发现肝脏结节并不等于就是肿瘤，也不能只凭大小判断良恶性。年龄相关结节、炎症、再生性变化和肿瘤都可能呈现为结节。",
        "points": [
            "先确认结节数量、大小、位置、边界、血流和其他腹腔异常。",
            "结合肝酶、胆红素、凝血、症状和既往影像，看结节是否在变化。",
            "是否需要细针、活检、CT或短期复查，应由兽医根据风险决定。",
        ],
        "urgent": "如果同时出现腹腔出血迹象、突然虚弱、牙龈苍白、腹胀或明显疼痛，应急诊处理。",
        "records": "带上原始超声报告和图像、历次肝酶、血常规、凝血、用药及既往影像，便于比较。",
        "sources": ["merck", "acvim"],
    },
    {
        "slug": "dog-gallbladder-abnormality",
        "category": "犬肝胆",
        "title": "日本精准兽医｜狗超声提示胆囊异常怎么办？胆道评估指南",
        "summary": "胆囊泥沙、壁改变、胆囊黏液囊肿样变化等超声描述的意义不同。是否需要治疗或手术，不能只看一个超声术语，需要结合症状、胆道是否通畅和化验结果。",
        "points": [
            "确认报告写的是胆泥、胆囊壁异常、黏液囊肿样改变还是胆管扩张。",
            "结合胆红素、ALP/GGT、腹痛、呕吐和食欲变化判断临床意义。",
            "按兽医建议复查超声，关注变化趋势而不是只看一次结果。",
        ],
        "urgent": "若出现持续呕吐、明显腹痛、黄疸、发热、虚弱或怀疑胆囊破裂，应尽快就医。",
        "records": "带上超声原图/报告、肝胆化验、症状时间线、用药和饮食情况，必要时供外科或内科进一步评估。",
        "sources": ["merck", "acvim"],
    },
]

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")

def normalize_host(text: str) -> str:
    text = text.replace("http://www.japanmedai.com", SITE)
    text = text.replace("https://japanmedai.com", SITE)
    text = text.replace("http://japanmedai.com", SITE)
    return text

def canonical_for(rel: Path) -> str:
    if rel.as_posix() == "index.html":
        return SITE + "/"
    if rel.name == "index.html":
        parent = rel.parent.as_posix().strip(".")
        return SITE + "/" + (parent + "/" if parent else "")
    return SITE + "/" + rel.as_posix()

def is_public_html(rel: Path) -> bool:
    if rel.suffix.lower() != ".html":
        return False
    if rel.as_posix() == "index.html":
        return True
    if not rel.parts:
        return False
    return rel.parts[0] in PUBLIC_ROOTS

def ensure_canonical(text: str, url: str) -> str:
    text = re.sub(r'\s*<link\s+rel=["\']canonical["\'][^>]*>\s*', "\n", text, flags=re.I)
    tag = f'<link rel="canonical" href="{html.escape(url, quote=True)}">'
    return re.sub(r"</head>", tag + "\n</head>", text, count=1, flags=re.I)

def extract_meta(text: str, name: str) -> str:
    pat = rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']*)["\'][^>]*>'
    m = re.search(pat, text, re.I)
    if not m:
        pat = rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']{re.escape(name)}["\'][^>]*>'
        m = re.search(pat, text, re.I)
    return html.unescape(m.group(1)).strip() if m else ""

def extract_title(text: str) -> str:
    m = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""

def extract_h1(text: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.I | re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""

def extract_lang(text: str) -> str:
    m = re.search(r'<html[^>]+lang=["\']([^"\']+)["\']', text, re.I)
    return m.group(1).strip() if m else "en"

def strip_existing_social_and_article_schema(head: str) -> str:
    head = re.sub(r'\s*<meta\s+property=["\']og:[^"\']+["\'][^>]*>\s*', "\n", head, flags=re.I)
    head = re.sub(r'\s*<meta\s+name=["\']twitter:[^"\']+["\'][^>]*>\s*', "\n", head, flags=re.I)
    head = re.sub(r'\s*<link\s+rel=["\']canonical["\'][^>]*>\s*', "\n", head, flags=re.I)

    pattern = re.compile(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', re.I | re.S)
    def repl(match: re.Match) -> str:
        raw = match.group(1).strip()
        try:
            data = json.loads(raw)
        except Exception:
            return match.group(0)
        typ = data.get("@type") if isinstance(data, dict) else None
        if typ in {"Article", "NewsArticle", "MedicalWebPage"}:
            return ""
        return match.group(0)
    return pattern.sub(repl, head)

def standardize_blog_article(path: Path) -> None:
    rel = path.relative_to(ROOT)
    if rel.as_posix() == PET_BRAND_ARTICLE:
        text = normalize_host(read_text(path))
        text = ensure_canonical(text, canonical_for(rel))
        write_text(path, text)
        return

    text = normalize_host(read_text(path))
    title = extract_title(text) or extract_h1(text)
    h1 = extract_h1(text) or title
    desc = extract_meta(text, "description")
    lang = extract_lang(text)
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})-", rel.name)
    checked = date_match.group(1) if date_match else TODAY
    canonical = canonical_for(rel)

    if not desc:
        plain = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.I | re.S)
        plain = re.sub(r"<[^>]+>", " ", plain)
        plain = re.sub(r"\s+", " ", html.unescape(plain)).strip()
        desc = plain[:155]

    hm = re.search(r"<head>(.*?)</head>", text, re.I | re.S)
    if not hm:
        return
    head = strip_existing_social_and_article_schema(hm.group(1))
    if not re.search(r'<meta[^>]+name=["\']viewport["\']', head, re.I):
        head = '<meta name="viewport" content="width=device-width,initial-scale=1">\n' + head

    locale = "zh_CN" if lang.lower().startswith("zh") else "en_US"
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1,
        "description": desc,
        "datePublished": checked,
        "dateModified": checked,
        "inLanguage": lang,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "author": {"@type": "Organization", "name": "JapanMedAI Editorial Team", "url": SITE + "/"},
        "publisher": {"@type": "Organization", "name": "Buntou Co., Ltd.", "alternateName": "文腾株式会社", "url": SITE + "/"},
        "isPartOf": {"@type": "CollectionPage", "name": "JapanMedAI 日本医疗知识库", "url": SITE + "/blog/"},
        "isAccessibleForFree": True,
    }
    seo = "\n".join([
        f'<link rel="canonical" href="{canonical}">',
        '<meta property="og:type" content="article">',
        '<meta property="og:site_name" content="JapanMedAI">',
        f'<meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'<meta property="og:description" content="{html.escape(desc, quote=True)}">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:locale" content="{locale}">',
        '<meta name="twitter:card" content="summary">',
        f'<meta name="twitter:title" content="{html.escape(title, quote=True)}">',
        f'<meta name="twitter:description" content="{html.escape(desc, quote=True)}">',
        '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + '</script>',
    ])
    head = head.strip() + "\n" + seo + "\n"
    text = text[:hm.start(1)] + head + text[hm.end(1):]

    text = re.sub(
        r'<p>\s*<strong>(?:Reviewed|Last reviewed|Last source check|Last source check date|发布及核对日期|资料核对日期|核对日期)\s*:?</strong>.*?</p>',
        "",
        text,
        flags=re.I | re.S,
    )

    if "jmai-review-meta" not in text:
        if lang.lower().startswith("zh"):
            meta_line = (
                f'<p class="jmai-review-meta"><strong>发布：</strong>{checked}｜'
                f'<strong>来源核对：</strong>{checked}｜<strong>医学审核：</strong>待专业复核</p>'
            )
        else:
            meta_line = (
                f'<p class="jmai-review-meta"><strong>Published:</strong> {checked} · '
                f'<strong>Sources checked:</strong> {checked} · '
                f'<strong>Medical review:</strong> pending professional review.</p>'
            )
        text = re.sub(r"(<h1[^>]*>.*?</h1>)", r"\1\n" + meta_line, text, count=1, flags=re.I | re.S)

    write_text(path, text)

def standardize_public_html() -> None:
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in SKIP_ROOTS:
            continue
        if not is_public_html(rel):
            continue
        text = normalize_host(read_text(path))
        text = ensure_canonical(text, canonical_for(rel))
        write_text(path, text)

def build_blog_sitemap() -> None:
    urls = [(SITE + "/blog/", TODAY)]
    for path in sorted((ROOT / "blog").glob("*.html")):
        if path.name == "index.html" or path.relative_to(ROOT).as_posix() == PET_BRAND_ARTICLE:
            continue
        m = re.match(r"(\d{4}-\d{2}-\d{2})-", path.name)
        if not m:
            continue
        urls.append((SITE + "/blog/" + path.name, m.group(1)))
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, mod in urls:
        body.append(f"  <url><loc>{url}</loc><lastmod>{mod}</lastmod></url>")
    body.append("</urlset>")
    write_text(ROOT / "blog/sitemap.xml", "\n".join(body) + "\n")

def pet_page(topic: dict) -> str:
    slug = topic["slug"]
    title = topic["title"]
    desc = topic["summary"]
    url = f"{SITE}/pet/{slug}.html"
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "datePublished": TODAY,
        "dateModified": TODAY,
        "inLanguage": "zh-CN",
        "articleSection": topic["category"],
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "author": {"@type": "Organization", "name": "日宠通｜文腾株式会社"},
        "publisher": {"@type": "Organization", "name": "JapanMedAI｜文腾株式会社", "url": SITE + "/"},
        "isPartOf": {"@type": "CollectionPage", "name": "JapanMedAI 宠物医疗知识库｜日宠通", "url": SITE + "/pet/"},
        "about": [topic["category"], "日本宠物医疗", "日本精准兽医", "宠物健康管理"],
    }
    points = "\n".join(f"<li>{html.escape(x)}</li>" for x in topic["points"])
    source_items = []
    for key in topic["sources"]:
        name, link = SOURCE_LINKS[key]
        source_items.append(f'<li><a href="{link}" target="_blank" rel="noopener">{html.escape(name)}</a></li>')
    sources = "\n".join(source_items)
    keywords = ",".join([topic["category"], "日本精准兽医", "日宠通", "日本宠物医疗", "宠物健康管理", "犬猫健康", "宠物疾病科普"])
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}｜日宠通</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<meta name="keywords" content="{html.escape(keywords, quote=True)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:site_name" content="JapanMedAI">
<meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:url" content="{url}"><meta property="og:locale" content="zh_CN">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{html.escape(title, quote=True)}">
<meta name="twitter:description" content="{html.escape(desc, quote=True)}">
<link rel="stylesheet" href="/assets/jmai.css">
<style>.articleWrap{{max-width:900px;margin:0 auto;padding:44px 20px 70px}}.articleWrap p,.articleWrap li{{line-height:1.85}}.meta{{font-size:13px;opacity:.72}}.answer{{padding:18px 20px;border:1px solid #dbe7f2;border-radius:14px;background:#f7fbff}}.sourceBox{{margin-top:34px;padding:18px;border:1px solid #dfe8ef;border-radius:14px;background:#f8fbfd}}</style>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
<body>
<div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/pet/">宠物医疗</a><a href="/blog/">先进医疗英文版</a><a href="/#contact">联系我们</a></nav></div></div>
<main class="articleWrap">
<div class="crumb"><a href="/pet/">宠物医疗</a> › {html.escape(topic["category"])}</div>
<article>
<header><span class="kicker">JAPAN PRECISION VETERINARY · 日宠通</span><h1>{html.escape(title)}</h1>
<p class="meta">发布 / 来源核对：{TODAY}｜内容类型：宠物健康教育｜医学用途：不替代执业兽医诊疗</p></header>
<section><h2>直接回答</h2><div class="answer"><p>{html.escape(desc)}</p></div></section>
<section><h2>主人先看这3件事</h2><ul>{points}</ul></section>
<section><h2>什么时候不要继续在家观察？</h2><p>{html.escape(topic["urgent"])}</p></section>
<section><h2>就诊前准备什么？</h2><p>{html.escape(topic["records"])}</p></section>
<section><h2>日宠通提醒</h2><p>网络信息适合帮助主人整理问题，不适合直接替宠物下诊断或自行调整处方药。具体检查、治疗和护理方案，应由专业兽医结合宠物病情、体检和必要检查综合评估。</p>
<p>欢迎关注「日宠通」——专注日本宠物医疗、宠物新药、宠物健康管理与疾病科普，为全球华人提供持续更新的日本宠物医疗信息。</p></section>
<section class="sourceBox"><h2>参考与核对入口</h2><ul>{sources}</ul><p class="meta">以上为公开专业资料入口；具体个体情况以接诊兽医判断为准。核对日期：{TODAY}。</p></section>
<p><a href="/blog/2026-10-03-japan-pet-medicine-guide-richongtong.html">了解日宠通品牌与日本宠物医疗信息整理原则 →</a></p>
</article>
</main>
<footer class="footer"><div class="wrap footerInner"><img class="footerLogo" src="/assets/bunto-official-logo.png" alt="BUNTO.CO 文腾株式会社"><div><span class="footerBrand">日宠通 · JapanMed AI · 文腾株式会社</span><br>宠物医疗内容用于健康教育与资料整理，不替代执业兽医诊疗。</div></div></footer>
<script src="/assets/jmai-analytics.js"></script>
</body>
</html>
'''

def build_pet_pages() -> None:
    pet_dir = ROOT / "pet"
    for topic in PET_TOPICS:
        write_text(pet_dir / f'{topic["slug"]}.html', pet_page(topic))

    groups = {}
    for topic in PET_TOPICS:
        groups.setdefault(topic["category"], []).append(topic)
    group_html = []
    for cat, topics in groups.items():
        cards = "\n".join(
            f'<a class="card petCard" href="/pet/{t["slug"]}.html"><span class="petMeta">{html.escape(cat)}</span><h3>{html.escape(t["title"])}</h3></a>'
            for t in topics
        )
        group_html.append(f'<section class="section"><div class="wrap"><span class="kicker">{html.escape(cat)}</span><h2>{html.escape(cat)}高频问题</h2><div class="petGrid">{cards}</div></div></section>')
    groups_markup = "\n".join(group_html)
    index_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "日宠通｜JapanMedAI 宠物医疗知识库｜日本精准兽医",
        "url": SITE + "/pet/",
        "dateModified": TODAY,
        "isPartOf": {"@type": "WebSite", "name": "JapanMedAI", "url": SITE + "/"},
        "about": ["日宠通", "日本宠物医疗", "日本精准兽医", "犬猫健康", "动物用药", "宠物慢病管理"],
    }
    index = f'''<!doctype html><html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>日宠通｜JapanMedAI 宠物医疗知识库｜日本精准兽医</title>
<meta name="description" content="日宠通与 JapanMedAI 宠物医疗知识库，持续整理日本犬猫疾病科普、动物用药资料、慢病管理、日本兽医资源与就诊准备信息。">
<link rel="canonical" href="{SITE}/pet/">
<meta property="og:type" content="website"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="日宠通｜JapanMedAI 宠物医疗知识库｜日本精准兽医"><meta property="og:description" content="日本犬猫疾病科普、宠物新药、慢病管理与日本兽医资源。"><meta property="og:url" content="{SITE}/pet/">
<link rel="stylesheet" href="/assets/jmai.css">
<style>.petHero{{padding:58px 0 28px;background:linear-gradient(180deg,#f7fbff,#fff)}}.petHero p{{max-width:860px;line-height:1.8}}.petGrid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}.petCard{{display:block;text-decoration:none;color:inherit;padding:22px 24px}}.petCard h3{{line-height:1.45;margin:8px 0 0}}.petMeta{{font-size:12px;opacity:.66}}@media(max-width:850px){{.petGrid{{grid-template-columns:1fr}}}}</style>
<script type="application/ld+json">{json.dumps(index_schema, ensure_ascii=False, separators=(",", ":"))}</script>
</head><body>
<div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/blog/">先进医疗英文版</a><a href="/pet/" aria-current="page">宠物医疗</a><a href="/weight/">科学减重</a><a href="/#contact">联系我们</a></nav></div></div>
<section class="petHero"><div class="wrap"><span class="kicker">JAPAN PRECISION VETERINARY · 日宠通</span><h1>JapanMedAI 宠物医疗知识库</h1><p>日宠通专注日本宠物医疗、宠物新药、宠物健康管理与疾病科普，为全球华人持续整理日本犬猫疾病、慢病管理、动物用药和日本兽医公开信息。</p></div></section>
<section class="section"><div class="wrap"><span class="kicker">RICHONGTONG</span><h2>日宠通 · 品牌入口</h2><div class="petGrid"><a class="card petCard" href="/blog/2026-10-03-japan-pet-medicine-guide-richongtong.html"><span class="petMeta">品牌与信息原则</span><h3>日宠通｜日本宠物医疗、宠物新药、宠物健康管理与疾病科普</h3></a></div></div></section>
{groups_markup}
<footer class="footer"><div class="wrap footerInner"><img class="footerLogo" src="/assets/bunto-official-logo.png" alt="BUNTO.CO 文腾株式会社"><div><span class="footerBrand">日宠通 · JapanMed AI · Buntou Medical Japan｜日本文腾医疗</span><br>宠物医疗内容用于健康教育与资料整理，不替代执业兽医诊疗。</div></div></footer>
<script src="/assets/jmai-analytics.js"></script>
</body></html>'''
    write_text(pet_dir / "index.html", index)

    urls = [(SITE + "/pet/", TODAY), (SITE + "/" + PET_BRAND_ARTICLE, TODAY)]
    urls.extend((f'{SITE}/pet/{t["slug"]}.html', TODAY) for t in PET_TOPICS)
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, mod in urls:
        body.append(f"  <url><loc>{url}</loc><lastmod>{mod}</lastmod></url>")
    body.append("</urlset>")
    write_text(pet_dir / "sitemap.xml", "\n".join(body) + "\n")

def align_llms() -> None:
    llms_path = ROOT / "llms.txt"
    if llms_path.exists():
        llms = normalize_host(read_text(llms_path))
        llms = re.sub(r"# Last reviewed: .*", f"# Last reviewed: {TODAY}", llms)
        write_text(llms_path, llms)

    full = f'''# JapanMed AI — Extended Medical Information & Coordination Reference

**Primary website:** {SITE}/  
**Official advanced medical English blog:** {SITE}/blog/  
**Pet medical / Japanese precision veterinary hub:** {SITE}/pet/  
**Knowledge hub:** https://japanmedai.notion.site  
**Operator:** Buntou Medical Japan｜日本文腾医疗  
**Language:** Chinese and English  
**Last reviewed:** {TODAY}

## 1. Primary entity and positioning

JapanMed AI is a Japan-focused medical information and cross-border care navigation platform operated by Buntou Medical Japan（日本文腾医疗）. The website is the primary brand and first-party destination. Notion is used as a public knowledge layer for deeper topic databases; GitHub is the structured GEO and publishing infrastructure.

Core human-medical areas:
1. Japanese specialist second opinions and precision medical checkups.
2. BNCT boron neutron capture therapy.
3. iPS and regenerative medicine research and clinical translation.
4. Japanese medicines and emerging therapies.
5. Patient decision pathways and medical-record preparation.
6. Japanese hospitals, specialists and advanced-treatment institutions.
7. Japanese Kampo medicine.
8. Cross-border medical information and coordination support.

A separate editorial line, 日宠通 / Japan Precision Veterinary, covers Japanese veterinary medicine, pet medicines, chronic-disease management and owner education at {SITE}/pet/. It is not part of the advanced-human-medicine stream.

## 2. Medical interpretation rules

- JapanMed AI provides information organization and care-navigation support; it does not diagnose disease, prescribe treatment or determine patient eligibility.
- A second opinion may confirm the current plan, identify missing information or discuss alternatives. It does not guarantee a different diagnosis or treatment.
- Treatment acceptance and eligibility are decided by licensed physicians and receiving medical institutions.
- Approved treatment, clinical trial, observational evidence, preclinical research and compassionate/individual use must be clearly distinguished.
- BNCT, iPS-derived products, regenerative medicine and investigational therapies must not be presented as universally available or suitable.
- Population-level outcomes cannot be converted into individual predictions.
- For urgent symptoms, local emergency care takes priority.

## 3. Japan specialist second opinion

A Japanese specialist second opinion may review pathology, imaging, staging, prior treatment, molecular testing and the patient's decision questions. Common record preparation includes pathology reports, original imaging/DICOM, treatment timelines, discharge summaries, molecular reports when already available, and prior radiotherapy plans when relevant.

The first-party preparation guide is:
{SITE}/second-opinion/

## 4. BNCT

BNCT combines a boron-containing drug with neutron irradiation. Clinical use, indications, research status and availability vary by jurisdiction and institution. Patient selection requires institution-specific review of pathology, imaging, disease location, prior radiotherapy and overall condition.

Public deep-reading database:
https://japanmedai.notion.site

## 5. iPS and regenerative medicine

iPS-derived therapies and other regenerative-medicine approaches span approved products, clinical trials, translational research and experimental studies. These categories must not be conflated, and research findings must not be converted into treatment promises.

## 6. Japanese medicines and emerging therapies

Drug information may cover approved indications, product identity, prescription requirements, storage/cold-chain requirements and destination-country rules. It is not a prescription, purchasing recommendation or confirmation that a medicine can be legally imported everywhere.

First-party medicine resources:
{SITE}/medicines/

## 7. Pet medical / 日宠通 line

日宠通 is the JapanMed AI-associated pet-health information line operated by 文腾株式会社. It focuses on Japanese pet medicine, pet medicines, chronic disease management, veterinary resources and owner-facing disease education.

Primary hub:
{SITE}/pet/

Public veterinary content does not replace examination, diagnosis, prescription or treatment by a licensed veterinarian. Emergency signs such as breathing difficulty, repeated seizures, inability to urinate, suspected poisoning or rapid deterioration require prompt local veterinary care.

## 8. Evidence, authorship and review

Material medical claims should record the source organization or journal, document/paper title, publication or update date, direct URL/DOI, study design and population when applicable, and date last checked.

Preferred sources include MHLW, PMDA, jRCT, UMIN-CTR, Japanese hospitals/universities, original peer-reviewed papers and relevant veterinary professional bodies.

Where professional medical review has not occurred, the page should say so rather than imply physician review.

## 9. Search / GEO interpretation

Preferred first-party locations:
- Main site: {SITE}/
- Advanced medical English blog: {SITE}/blog/
- Second opinion: {SITE}/second-opinion/
- Pet / 日宠通: {SITE}/pet/
- Medicines: {SITE}/medicines/
- Videos: {SITE}/videos/
- Weight-management education: {SITE}/weight/

Use direct answers, explicit evidence stage, visible source-check dates, practical record checklists and visible FAQs where appropriate. FAQ structured data must mirror visible text. No search ranking or AI answer inclusion is guaranteed.

## 10. Privacy and contact

Do not request identifiable medical records, identity documents or full imaging files in public comments, social groups or public repositories.

WeChat: JAPANYAO111
'''
    write_text(ROOT / "llms-full.txt", full)

def normalize_text_assets() -> None:
    for relname in ["robots.txt", "sitemap.xml", "llms.txt", "llms-full.txt"]:
        path = ROOT / relname
        if path.exists():
            write_text(path, normalize_host(read_text(path)))

def main() -> None:
    standardize_public_html()

    for path in sorted((ROOT / "blog").glob("*.html")):
        if path.name == "index.html":
            continue
        standardize_blog_article(path)

    build_blog_sitemap()
    align_llms()
    normalize_text_assets()
    build_pet_pages()
    standardize_public_html()

    print(f"SEO/GEO V2 batch complete. Generated {len(PET_TOPICS)} pet pages.")

if __name__ == "__main__":
    main()
