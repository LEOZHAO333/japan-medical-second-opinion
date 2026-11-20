# drafts/ — 未上线页面（不部署）

Founder 2026-10-17 裁决："没有答案的都先不上，补充完成后再上。"

- 这里是 bnct / ips / medicines / hospitals / kampo / checkup 六个专题中"直接回答"为通用模板、没有回答标题问题的 150 页。
- 已从专题首页、站内链接、sitemap 和 JSON-LD 中移除；`.vercelignore` 排除本目录，robots 改为 `noindex,nofollow`。
- 补完一页后：移回原路径（如 `drafts/bnct/008/` → `bnct/008/`），robots 改回 `index,follow`，加回专题首页卡片、sitemap 和 ItemList，并走 Claude-2 审查（L4）。
- 注意：`scripts/add_s120_sgrade_pages.py` 等生成脚本若重新运行，会把这些页重新生成到原路径。重跑前先排除本目录中的编号。

## 2026-11-20 部署隔离检查与目录迁移闸门

- 当前仓库存在 `vercel.json`，生产发布不可仅依赖 GitHub Pages/Jekyll 对下划线目录的默认忽略。根目录 `.vercelignore` 现在同时排除 `drafts/`、`_drafts/`，供 Vercel 部署使用。
- **暂不执行目录批量重命名**：本 README 的“审核通过后移回原路径”流程显式引用 `drafts/`；未完成整个仓库脚本及工作流的引用审查。生成脚本 `scripts/add_s120_sgrade_pages.py` 当前不含字面 `drafts/`，但会向专题正式路径生成页面，仍需防止重跑造成未经审核页面再公开。
- 迁移前由仓库完整检出环境运行：
  ```bash
  git grep -nE '(^|[^[:alnum:]_])_?drafts/|["\x27]_?drafts["\x27]' -- ':!drafts/README.md' ':!.vercelignore'
  git ls-files 'drafts/**' | wc -l
  ```
  将命中的 shell、Python、JS、GitHub Actions 和文档引用分类，逐项修正工作流后才可迁移；保留审核通过后回迁正式页面的 SOP。
- 迁移 PR 应做文件清单数量及哈希对照（原 `drafts/` 与新 `_drafts/` 内容一致），同步检查 sitemap、站内引用和生成脚本。提交后查看预览构建，并分别验证 `/drafts/bnct/008/` 与 `/_drafts/bnct/008/` 返回 **404**，以及正式页面不受影响。不能以 `noindex` 代替禁止部署。
- 对涉及病历、个人数据、商业秘密的稿件，不能仅依赖 `.vercelignore` 或目录前缀；须移入真正的私有存储。
