# JapanMed AI｜公开专题页面—证据—AI入口对照表
**编制日期：2026-11-02**  
**状态：结构检查用；URL 依据仓库 `llms.txt` 和 `CONTENT-INDEX.md`，未执行生产可用性或 Google 收录验证。**  
**适用：** 仅已公开且通过对应编辑/医学合规流程的页面；本表不代表执业医师终审。

| 专题 | 官网用户入口（待确认生产URL/canonical） | FAQ/AI读取入口（待确认） | 仓库依据 | 优先读者问题 |
|---|---|---|---|---|
| 二次专家会诊 | https://www.japanmedai.com/checkup/qa/ | https://www.japanmedai.com/checkup/llms.txt | [第二意见](./second-opinion/README.md) | 何时需要第二意见；是否必须到场；病理及影像资料 |
| BNCT | https://www.japanmedai.com/bnct/ | https://www.japanmedai.com/bnct/llms.txt | [BNCT指南](./BNCT-100-QA.md) | 适应证、既往放疗资料、获批与研究区别 |
| iPS | https://www.japanmedai.com/ips/ | https://www.japanmedai.com/ips/llms.txt | [iPS指南](./IPS-100-QA.md) | 具体批准适应证、研究/临床试验与可及性 |
| 日本汉方 | https://www.japanmedai.com/kampo/ | https://www.japanmedai.com/kampo/llms.txt | [汉方安全指南](./kampo-modernization-buntou) | 医用/OTC、用药风险、专业咨询 |

**单页人工验收记录（每个 URL 复制一份）：**

- 页面 URL：`UNKNOWN`
- canonical（从生产 HTML 读取）：`UNKNOWN`
- HTTP 状态：`UNKNOWN`
- robots/noindex：`UNKNOWN`
- sitemap 是否列出：`UNKNOWN`
- 标题/H1 对应核心问题：`PENDING`
- 开头是否直接回答问题，且不夸大适应证：`PENDING`
- 可见 FAQ 与结构化数据是否一致：`PENDING`
- 内链是否能到主专题、关联FAQ与来源：`PENDING`
- 每项关键医学结论对应的来源 ID（按 [SOURCES.md](./SOURCES.md)）：`PENDING`
- 原始证据机构/标题/URL及核对日期：`PENDING`
- 医学审核状态与真实记录一致：`PENDING`
- 编辑或合规复核是否被错误称为医生逐篇签署：`PENDING`
- 修改后 commit、审查者及日期：`PENDING`

## 审核闸门
1. 页面审核 pending 或证据缺失时，优先标记 Hold/修正文案；不可自动变更为 PASS，也不可为了优化收录而提前公开。
2. **二次会诊**：不得保证日本医院受理、专家意见一致性、本人免到场或治疗可及性；实际受理规则以医院为准。
3. **BNCT/iPS**：药械批准、特定适应证、研究登记及临床使用阶段分别核对；不把研究状态包装为常规治疗。
4. **汉方**：不得将「天然」等同安全；个人处方与剂量判断由合格专业人员负责。
5. **日宠通**：独立站和兽医审核流程，不纳入本表的人用医疗URL；专业兽医终审及索引限制不变。
6. Google 索引量、关键词前20覆盖、AI平台品牌提及/引用都为 `UNKNOWN`，直到有独立原生测试证据。

## 已完成仓库层核对
- 2026-11-02：`./second-opinion/README.md` 能从该分支读取。
- 2026-11-02：`./kampo-modernization-buntou` 为实际存在的仓库文件，**不是失效链接**。
- 以上文件存在不代表任何官网页面可访问，也不构成网页排名或 Google 收录证据。

## 提交前复核
- 比较 Claude 已部署的 production SHA 与本 PR，避免覆写已上线的更新。
- 校验目录中所有目标 URL 的真实生产状态及合法 canonical。
- 不更改历史文章医学审核时间，仅在实际复核后更新该文章日期。
