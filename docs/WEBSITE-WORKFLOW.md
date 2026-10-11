# japanmedai.com 网站代码工作规则（Founder 锁定，2026-10-11）

本仓库的 `main` 分支就是线上生产环境：Vercel 会自动部署 `main`，**合并 = 上线**。

## 分工
| 角色 | 负责 |
|---|---|
| **Claude** | 修改网站代码：在新分支提交，开 PR 或更新 PR，并写清楚改了什么、怎么测的 |
| **GPT** | 审查 Claude 的改动，在 PR 评论里用 P0/P1/P2 格式回执 |
| **Founder（Leo）** | 决定是否合并。每一次合并都由 Founder 本人点按钮，或明确批准 |

## 硬性规则
1. 两个 AI 都**不合并 PR**，也**不直接推送 `main`**。
2. 不新增带写权限的 GitHub Actions workflow，不新增任何权限、密钥或第三方应用。如确实需要，必须先由 Founder 批准。
3. 密钥（API Key / Secret）一律不写进仓库，也不出现在 PR 评论里。
4. 锁定内容不改：前台联系方式只用微信（不显示 WhatsApp）；许可证只写名称，不写编号；Logo 只用原图 `assets/bunto-official-logo.png`（Canva `MAHXfZgfP08`，SHA-256 `1922ef92…c982`）；网站不在线卖药。
5. 医学内容、价格、品牌方面的改动，属于 Founder 的重大决定。
6. 每个 PR 都要说明测试结果：至少用手机尺寸逐页加载一次，确认没有 JS 报错，且 Logo 和联系区显示正常。

## 例外
其他仓库（Review Hub、内容生产）仍按原分工：GPT 执行，Claude 审查。
