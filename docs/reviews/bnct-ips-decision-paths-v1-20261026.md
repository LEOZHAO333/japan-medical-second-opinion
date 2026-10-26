# BNCT / iPS 专题下一步分流 V1｜2026-10-26

## 范围
仅编辑 `bnct/index.html` 和 `ips/index.html` 两个已上线专题页的首屏静态入口，不触动已审核正文、适应证描述、FAQ Schema、canonical 或现有医疗数据。

## BNCT 路径
1. 先看 /bnct/#bnctPathways 中既有获批、研究、非医保路径说明。
2. 已有资料，进入 /tools/bnct-records/ 自查病理、影像DICOM及既往放疗计划。
3. 对目前治疗方案有疑问的患者，了解 /second-opinion/#contact 的专家第二意见服务。**这不是BNCT治疗预约，且不保证任何实际医院受理。**

## iPS 路径
1. 先读 /ips/qa/ 已批准制品与研究区别。
2. 关注研究者读 /ips/037/，先核对正式研究登记、参加条件及海外居民资格。
3. 有现有诊疗方案疑问的用户阅读 /second-opinion/。**现有第二意见服务的受理范围仍须另行确认，不代表开通iPS移植预约。**
4. 辅助内链 /ips/050/ 梳理现有医疗资料。

## 隐私与统计
- 使用站点既有 data-jmai-track 和固定 data-jmai-id 共6个，无病情问卷、身份和健康档案采集，无新表单、上传或第三方依赖。
- 固定CTA ID：bnct_eligibility_info、bnct_records_check、bnct_second_opinion、ips_approved_vs_research、ips_trial_eligibility_info、ips_second_opinion_info。
- 点击仅代表导航意向，不代表医疗咨询、临床资格、研究入组或成交。

## 已通过的静态测试
- 远端分支两个HTML均成功回读。
- 10项静态检查PASS：6个CTA/6个固定ID、全部目标链接有效路径、医学边界文字、移动端单栏CSS、无上传字段、canonical不变。
- 未进行浏览器渲染验收；CI、医疗审查与业务批准仍需在Draft PR执行并记录。

## 医学与审批门槛
- Claude-2审核：BNCT日本批准适应证≠其它适应证/研究；不同医院境外接诊不同；iPS获批药械并不等于所有再生医疗疗法已经批准。第二意见不替代正式医疗。
- Claude-3审核：同主题不新增薄页；UI、可访问性、390px手机首屏无溢出；固定CTA统计只传合法标签。
- 跑 page-rewrites-s0、checkup-qa-s0及Vercel Preview，不将Preview ready当生产上线。
- 保持Draft，待Founder明确批准后方可合并部署。
