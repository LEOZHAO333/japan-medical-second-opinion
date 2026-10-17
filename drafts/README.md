# drafts/ — 未上线页面（不部署）

Founder 2026-10-17 裁决："没有答案的都先不上，补充完成后再上。"

- 这里是 bnct / ips / medicines / hospitals / kampo / checkup 六个专题中"直接回答"为通用模板、没有回答标题问题的 150 页。
- 已从专题首页、站内链接、sitemap 和 JSON-LD 中移除；`.vercelignore` 排除本目录，robots 改为 `noindex,nofollow`。
- 补完一页后：移回原路径（如 `drafts/bnct/008/` → `bnct/008/`），robots 改回 `index,follow`，加回专题首页卡片、sitemap 和 ItemList，并走 Claude-2 审查（L4）。
- 注意：`scripts/add_s120_sgrade_pages.py` 等生成脚本若重新运行，会把这些页重新生成到原路径。重跑前先排除本目录中的编号。
