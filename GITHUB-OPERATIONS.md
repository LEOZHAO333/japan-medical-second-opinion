# GitHub Operations Guide

This repository manages public medical content and draft publishing. It must
never be used for patient records, identity documents, imaging, contact details,
payment data or private consultation notes.

## Operating flow

1. Create an Issue with the appropriate form.
2. Move it through the project statuses: `情报池` → `待核实` → `待写` →
   `待审核` → `草稿箱` → `已发布` → `复盘`.
3. Work on an `automation/*` or editorial branch.
4. Open a pull request. Medical validation must pass before merge.
5. Merge only verified public content. WordPress and Blogger jobs create or
   update drafts; they do not authorize public publication.
6. The operator reviews the draft in the platform dashboard and publishes it
   manually.

## Project fields

| Field | Values |
|---|---|
| 市场 | 国内；欧美及海外华人 |
| 内容方向 | 二次会诊；BNCT／精准放疗；iPS；新药；减重；医疗流程 |
| 证据阶段 | 已获批；临床试验；观察研究；临床前；个案；待核实 |
| 合规风险 | 低；中；高 |
| 目标平台 | 公众号；官网／WordPress；Blogger；Facebook；X |
| 发布日期 | Date |
| 转化目标 | 公开阅读；问卷完成；有效咨询；资料准备 |

Domestic and overseas work must use separate items, copy and metrics. Do not
use domestic WeChat results as evidence of overseas acquisition performance.

## Manual action buttons

- **Validate medical content**: run a changed-file or full repository scan.
- **Check public medical links**: verify source links; 403, 429 and transient
  network errors require human review, while 404 and 410 fail the run.
- **Publish WordPress draft**: optionally provide one exact `wordpress/*.html`
  path. The workflow enforces `WP_POST_STATUS=draft`.
- **Upload Blogger drafts**: provide one exact `blogger/*.html` path. The
  uploader verifies that the remote post remains a draft.

Never paste Actions secrets or full environment-variable output into an Issue.

## Failure priority

1. Privacy or secret exposure: stop the workflow and rotate affected secrets.
2. Medical evidence or compliance failure: correct the content before merge.
3. Draft upload failure: keep the public platform unchanged, record the run
   link, fix the cause and retry manually.
4. Source link warning: verify with the source organization before changing or
   withdrawing a medical claim.
