# JapanMedAI /blog｜2026-10-16 十篇长文暂存清单

**状态：STAGED / NOT PUBLISHED**  
**生产分支：main 未修改**  
**目的：先登记进入 `/blog/` 内容数据库，待统一同步发布时再生成正式页面、更新 sitemap/索引并合并到 main。**

## 发布原则

1. 这10篇以 2026-10-16 已确认并发布公众号的约1200字最终长文为正式正文来源。
2. `articles/2026-10-16-*.md` 为当前仓库内的结构化专题/患者问题配套稿，可用于标题、主题、链接和医学边界核对，但**不得在同步发布时自动替代公众号最终长文正文**。
3. 同步发布前统一完成：正文核对 → `/blog/*.html` 页面生成 → canonical/description/schema/citation → 对应 patient-question 双向内链 → `blog/articles.json` 状态由 staged 转为 published → sitemap/CONTENT-INDEX/llms 必要更新 → 合并 main。
4. 在正式页面生成前，不合并本分支，不触发 JapanMedAI.com 上线。

## 10篇登记记录

1. **晚期胃癌已经出现转移，为什么日本专家还会重新判断能不能手术？**  
   Target: `/blog/2026-10-16-stomach-cancer-surgery-after-metastasis.html`  
   Patient question: `/patient-questions/stomach-cancer-surgery-after-metastasis/`

2. **低位直肠癌被告知不能保肛，第二意见最值得重新核对哪5项？**  
   Target: `/blog/2026-10-16-rectal-cancer-sphincter-preservation.html`  
   Patient question: `/patient-questions/rectal-cancer-sphincter-preservation/`

3. **复发头颈癌看到“光免疫治疗”，先别问能不能做，先核对这4件事**  
   Target: `/blog/2026-10-16-head-neck-cancer-photoimmunotherapy.html`  
   Patient question: `/patient-questions/head-neck-cancer-photoimmunotherapy/`

4. **脑胶质瘤治疗陷入瓶颈，什么时候应该重新做一次专家第二意见？**  
   Target: `/blog/2026-10-16-glioma-second-opinion-timing.html`  
   Patient question: `/patient-questions/glioma-second-opinion-timing/`

5. **胃癌化疗效果不好，第二意见最先重新核对的是方案还是病理？**  
   Target: `/blog/2026-10-16-gastric-cancer-chemo-pathology-review.html`  
   Patient question: `/patient-questions/gastric-cancer-chemo-pathology-review/`

6. **晚期癌症还有必要做第二意见吗？真正价值不只是“找新疗法”**  
   Target: `/blog/2026-10-16-advanced-cancer-second-opinion-value.html`  
   Patient question: `/patient-questions/advanced-cancer-second-opinion-value/`

7. **每年体检都正常，为什么癌症仍可能发现得很晚？**  
   Target: `/blog/2026-10-16-annual-checkup-late-cancer-detection.html`  
   Patient question: `/patient-questions/annual-checkup-late-cancer-detection/`

8. **体检查出结节，真正需要判断的不是“是不是癌”这一个问题**  
   Target: `/blog/2026-10-16-nodule-after-health-check.html`  
   Patient question: `/patient-questions/nodule-after-health-check/`

9. **PET-CT越高级越适合体检吗？为什么多数人不需要把它当常规筛查？**  
   Target: `/blog/2026-10-16-pet-ct-cancer-screening.html`  
   Patient question: `/patient-questions/pet-ct-cancer-screening/`

10. **癌症筛查不是项目越多越好：真正有证据的筛查怎么选？**  
    Target: `/blog/2026-10-16-evidence-based-cancer-screening.html`  
    Patient question: `/patient-questions/evidence-based-cancer-screening/`

## 当前数据库动作

上述10条已加入本暂存分支的 `blog/articles.json`，并标记 `status: staged`。正式同步时再生成页面并切换为 published。
