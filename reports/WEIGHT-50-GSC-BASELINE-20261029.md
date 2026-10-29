# WEIGHT-50 | Google Search Console 索引核验基线（2026-10-29）

> 作用：已上线减重50篇页面的 **GSC 待核验清单**。只记录已证实数据。未连接有权限的 Search Console，所有 Google 索引状态均为 **未知**，不是“未收录”。
>
> 发布版本：主站 PR #204，正式 commit `b66c42de75c3a950be3b4b9159d6bd2650f2188a`。私有 Preview PR #114 closed/unmerged，不再作为待上线版本。

## 已证实事实（GitHub Actions 公网实测）
- 2026-10-29 UTC, [只读测试 run #40836058752](https://github.com/LEOZHAO333/japan-medical-second-opinion/actions/runs/40836058752) 成功：`www.japanmedai.com` 下的 50 篇 article + 首页 + robots.txt + 总 Sitemap + 目录，共 **54/54 HTTP 200**。
- 50 篇线上 HTML 与正式代码文件 **50/50 字节一致**；live canonical、HTML noindex 和 HTTP X-Robots-Tag 的基础阻断检测通过。
- 不带 `www` 的根域名首页、目录、article-034 共 **3/3** 最终返回 HTTP 200，最终 URL 统一指向 `www`。总计 **57/57** 通过。
- `https://www.japanmedai.com/sitemap.xml` 的正式源文件含 50/50 篇文章，并记录 `lastmod=2026-10-29`；`robots.txt` 声明该 Sitemap。
- **不能据此宣称 Google 已读取 Sitemap、已抓取 50 篇、或已收录。** 公网探测来自通用 GitHub Runner，不是 Googlebot 实际抓取。

## Search Console 需提取的权威证据
1. 确认 GSC 中选择的是覆盖 `https://www.japanmedai.com/` 的已验证资源（域名资源或正确的 HTTPS www URL 前缀资源）；只读检查是否曾提交 `https://www.japanmedai.com/sitemap.xml`，记录**提交时间、上次读取、状态**。未提交时由持有网站 Owner 权限的人提交；不重复提交已有成功记录。
2. 进入 **网页索引** 报告，按 `sitemap.xml` 查看已发现/已编入/未编入的总量。注意此根 Sitemap 还有其他栏目，**总收录数不可当作减重50篇的收录数**。
3. 对重点 URL `001`、`008`、`034`、`050` 使用 **URL 检查**，记录 `网址是否在 Google 上`、上次抓取、是否允许抓取、网页获取、Google 选择的规范网址；其中 `034` 为含药品名的重要医学页面。
4. 50 篇全量状态可按配额逐步通过 GSC 的 URL Inspection API 或有授权的人工检查记录。**不要把 site: 搜索无结果视为未收录**；“可编入索引”也不等于“已被编入索引”。
5. 若 GSC 明确列出 `404/5xx`、`noindex`、robots 阻断、canonical 异常，先与当前公网证据核对，再决定是否修复。仅“已发现但尚未索引”不触发批量重写或重发。
6. 当前未调用 GSC API、未申请配额、未提交 Sitemap/索引请求，也未编辑正式内容。

官方资料：
- https://support.google.com/webmasters/answer/7451001
- https://support.google.com/webmasters/answer/9012289
- https://support.google.com/webmasters/answer/7440203

## 50 篇状态台账

状态 `待 GSC 核实` 意味着没有获得 Search Console 的真实数据。HTTP 和字节一致性来自上述成功测试，不是搜索收录结果。

| 编号 | 正式 URL | HTTP | 线上与 b66c42de 一致 | GSC 收录状态 | Google 选择 canonical | 上次抓取 |
|---|---|---|---|---|---|---|
| 001 | https://www.japanmedai.com/weight/articles/article-001.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 002 | https://www.japanmedai.com/weight/articles/article-002.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 003 | https://www.japanmedai.com/weight/articles/article-003.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 004 | https://www.japanmedai.com/weight/articles/article-004.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 005 | https://www.japanmedai.com/weight/articles/article-005.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 006 | https://www.japanmedai.com/weight/articles/article-006.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 007 | https://www.japanmedai.com/weight/articles/article-007.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 008 | https://www.japanmedai.com/weight/articles/article-008.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 009 | https://www.japanmedai.com/weight/articles/article-009.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 010 | https://www.japanmedai.com/weight/articles/article-010.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 011 | https://www.japanmedai.com/weight/articles/article-011.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 012 | https://www.japanmedai.com/weight/articles/article-012.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 013 | https://www.japanmedai.com/weight/articles/article-013.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 014 | https://www.japanmedai.com/weight/articles/article-014.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 015 | https://www.japanmedai.com/weight/articles/article-015.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 016 | https://www.japanmedai.com/weight/articles/article-016.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 017 | https://www.japanmedai.com/weight/articles/article-017.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 018 | https://www.japanmedai.com/weight/articles/article-018.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 019 | https://www.japanmedai.com/weight/articles/article-019.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 020 | https://www.japanmedai.com/weight/articles/article-020.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 021 | https://www.japanmedai.com/weight/articles/article-021.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 022 | https://www.japanmedai.com/weight/articles/article-022.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 023 | https://www.japanmedai.com/weight/articles/article-023.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 024 | https://www.japanmedai.com/weight/articles/article-024.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 025 | https://www.japanmedai.com/weight/articles/article-025.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 026 | https://www.japanmedai.com/weight/articles/article-026.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 027 | https://www.japanmedai.com/weight/articles/article-027.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 028 | https://www.japanmedai.com/weight/articles/article-028.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 029 | https://www.japanmedai.com/weight/articles/article-029.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 030 | https://www.japanmedai.com/weight/articles/article-030.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 031 | https://www.japanmedai.com/weight/articles/article-031.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 032 | https://www.japanmedai.com/weight/articles/article-032.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 033 | https://www.japanmedai.com/weight/articles/article-033.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 034 | https://www.japanmedai.com/weight/articles/article-034.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 035 | https://www.japanmedai.com/weight/articles/article-035.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 036 | https://www.japanmedai.com/weight/articles/article-036.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 037 | https://www.japanmedai.com/weight/articles/article-037.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 038 | https://www.japanmedai.com/weight/articles/article-038.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 039 | https://www.japanmedai.com/weight/articles/article-039.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 040 | https://www.japanmedai.com/weight/articles/article-040.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 041 | https://www.japanmedai.com/weight/articles/article-041.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 042 | https://www.japanmedai.com/weight/articles/article-042.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 043 | https://www.japanmedai.com/weight/articles/article-043.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 044 | https://www.japanmedai.com/weight/articles/article-044.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 045 | https://www.japanmedai.com/weight/articles/article-045.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 046 | https://www.japanmedai.com/weight/articles/article-046.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 047 | https://www.japanmedai.com/weight/articles/article-047.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 048 | https://www.japanmedai.com/weight/articles/article-048.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 049 | https://www.japanmedai.com/weight/articles/article-049.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |
| 050 | https://www.japanmedai.com/weight/articles/article-050.html | 200 | 是 | 待 GSC 核实 | 待 GSC 核实 | 待 GSC 核实 |

## 后续事实更新原则
- 只有通过 Search Console 实际报告或 API 返回，才把 `待 GSC 核实` 改成真实状态。
- 公网 200、Sitemap inclusion、Google 已抓取、Google 已编入索引，是四项不同证据；每项分别存日期和来源。
- 如需要公开操作，必须保留既有医学审核与发布闸门；**本文件不授权新部署、DNS 改动或索引接口批量提交**。
