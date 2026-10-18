# 日宠通历史路径迁移核验清单（2026-10-18）

## 检查范围

- 原站：`https://www.japanmedai.com/pet/`
- 新品牌入口：`https://pet.japanmedai.com/`
- 原主站 `vercel.json`：28 条旧HTML→`/pet/qa/` 重定向；此外 `/pet/index.html` 一条首页跳转和旧代理rewrites。
- 当前新站运行时源代码：`LEOZHAO333/wenteng-medical-knowledge/pet-site/api/pet.js`（main）共有 12 个Article slug，不包含下表的旧目标slug。缺少运行时slug意味着当前API的`qa/<slug>`路由会返回404。
- **迁移禁止条件：** 只要新站目标页404、内容缺失、医学状态未经审核或canonical不正确，不将旧路径统一301到该目标。不可将所有老文章指向首页掩盖404。
- **下表为静态代码核对，不是生产HTTP逐URL实测。** 部署前应执行真实HTTP检查，包括状态码、响应头、location、移动端可用性、noindex和内部链接。

| 旧主站路径 | 拟定新站路径（待恢复） | 新站运行时文章slug存在 |
|---|---|---|
| `/pet/cat-ckd-staging.html` | `https://pet.japanmedai.com/qa/cat-ckd-staging/` | **否 / HOLD** |
| `/pet/cat-ckd-weight-loss.html` | `https://pet.japanmedai.com/qa/cat-ckd-weight-loss/` | **否 / HOLD** |
| `/pet/cat-creatinine-single-high.html` | `https://pet.japanmedai.com/qa/cat-creatinine-single-high/` | **否 / HOLD** |
| `/pet/cat-daily-subcutaneous-fluids.html` | `https://pet.japanmedai.com/qa/cat-daily-subcutaneous-fluids/` | **否 / HOLD** |
| `/pet/cat-fast-breathing-after-fluids.html` | `https://pet.japanmedai.com/qa/cat-fast-breathing-after-fluids/` | **否 / HOLD** |
| `/pet/cat-home-subcutaneous-fluid-training.html` | `https://pet.japanmedai.com/qa/cat-home-subcutaneous-fluid-training/` | **否 / HOLD** |
| `/pet/cat-litter-change-not-using-box.html` | `https://pet.japanmedai.com/qa/cat-litter-change-not-using-box/` | **否 / HOLD** |
| `/pet/cat-moving-house-urination-plan.html` | `https://pet.japanmedai.com/qa/cat-moving-house-urination-plan/` | **否 / HOLD** |
| `/pet/cat-renal-diet-refusal.html` | `https://pet.japanmedai.com/qa/cat-renal-diet-refusal/` | **否 / HOLD** |
| `/pet/cat-subcutaneous-fluid-lump.html` | `https://pet.japanmedai.com/qa/cat-subcutaneous-fluid-lump/` | **否 / HOLD** |
| `/pet/cat-urinary-stoma-home-care.html` | `https://pet.japanmedai.com/qa/cat-urinary-stoma-home-care/` | **否 / HOLD** |
| `/pet/dog-aki-follow-up.html` | `https://pet.japanmedai.com/qa/dog-aki-follow-up/` | **否 / HOLD** |
| `/pet/dog-gallbladder-abnormality.html` | `https://pet.japanmedai.com/qa/dog-gallbladder-abnormality/` | **否 / HOLD** |
| `/pet/dog-hematuria-urine-sample.html` | `https://pet.japanmedai.com/qa/dog-hematuria-urine-sample/` | **否 / HOLD** |
| `/pet/dog-house-soiling-or-urinary-problem.html` | `https://pet.japanmedai.com/qa/dog-house-soiling-or-urinary-problem/` | **否 / HOLD** |
| `/pet/dog-jaundice.html` | `https://pet.japanmedai.com/qa/dog-jaundice/` | **否 / HOLD** |
| `/pet/dog-kidney-values-and-urinalysis.html` | `https://pet.japanmedai.com/qa/dog-kidney-values-and-urinalysis/` | **否 / HOLD** |
| `/pet/dog-liver-enzymes-long-term-meds.html` | `https://pet.japanmedai.com/qa/dog-liver-enzymes-long-term-meds/` | **否 / HOLD** |
| `/pet/dog-liver-nodule.html` | `https://pet.japanmedai.com/qa/dog-liver-nodule/` | **否 / HOLD** |
| `/pet/dog-post-neuter-incontinence.html` | `https://pet.japanmedai.com/qa/dog-post-neuter-incontinence/` | **否 / HOLD** |
| `/pet/dog-proteinuria-monitoring.html` | `https://pet.japanmedai.com/qa/dog-proteinuria-monitoring/` | **否 / HOLD** |
| `/pet/dog-renal-diet-refusal.html` | `https://pet.japanmedai.com/qa/dog-renal-diet-refusal/` | **否 / HOLD** |
| `/pet/dog-sleep-urine-leakage.html` | `https://pet.japanmedai.com/qa/dog-sleep-urine-leakage/` | **否 / HOLD** |
| `/pet/dog-straining-to-urinate.html` | `https://pet.japanmedai.com/qa/dog-straining-to-urinate/` | **否 / HOLD** |
| `/pet/female-cat-urinary-retention.html` | `https://pet.japanmedai.com/qa/female-cat-urinary-retention/` | **否 / HOLD** |
| `/pet/multi-cat-litter-box-monitoring.html` | `https://pet.japanmedai.com/qa/multi-cat-litter-box-monitoring/` | **否 / HOLD** |
| `/pet/recurrent-cat-urinary-second-opinion-records.html` | `https://pet.japanmedai.com/qa/recurrent-cat-urinary-second-opinion-records/` | **否 / HOLD** |
| `/pet/senior-dog-urgency.html` | `https://pet.japanmedai.com/qa/senior-dog-urgency/` | **否 / HOLD** |

## 经核验可采用的安全路径

1. 先完成日宠通新域名首页根路径验收（DNS/Vercel verified不等于所有HTTP页面均可用）。
2. 为旧文章恢复真实内容，逐条匹配 slug、原问题意图、正文、医学风险、原始引用、canonical；若不适合恢复应保留404/410或返回明确说明，切勿虚构相近替代页面。
3. 逐条在新域名验收 HTTP 200，保持文章 `noindex` 直到专业医学审核与Founder索引批准（域名迁移不代表自动解除noindex）。
4. 在变更 `vercel.json` 时设置单跳301：老HTML→真正的新文章页面；老主站`/pet/qa/<slug>/`→新站`/qa/<slug>/`；主站`/pet/`→新品牌首页。注意原宠物素材仍挂 `/pet/assets/`，不得错误重定向到新域名的 `/assets/`。
5. 单独检查旧query与锚点、UA不同、robots、CSS/图片、Search Console及迁移后的404监测。
6. 在获得生产部署批准后才切换；当前主站旧rewrites与redirects继续保留原状，避免未经核查造成大量新404。
